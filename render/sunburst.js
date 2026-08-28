const SIZE = 740;

// Radial scale: a small fixed hole for the back-button circle, then a thin
// fixed gap up to the first data ring (kept separate from ring thickness so
// it can stay thin regardless of how thick the data rings themselves are —
// otherwise, with a small hole and a chunky ring thickness, that gap reads
// as a mismatched blank/white ring around the hole, especially once the
// hole itself gets colored on category focus), then ring thickness
// stretched to use the rest of the canvas — set once the data is loaded and
// the hierarchy's actual depth (root.height) is known, so the outermost
// ring's outer edge always lands exactly on the chart boundary instead of a
// hardcoded constant clipping it (or leaving it too small).
const HOLE_RADIUS = SIZE * 0.065;
const CENTER_GAP  = SIZE * 0.022;
let ringThickness;
function radiusAt(y) {
  if (y <= 0) return HOLE_RADIUS;
  return HOLE_RADIUS + CENTER_GAP + (y - 1) * ringThickness;
}

const chartWrap   = document.getElementById("chart-wrap");
const embedLocale = chartWrap ? chartWrap.dataset.locale : null;
const profileSrc  = (chartWrap && chartWrap.dataset.profileSrc) || "health-profile.json";
// health-profile.json stores category icons as a site-root-absolute path
// (e.g. "/media/apple.png"), which is wrong once the site itself lives under
// a sub-path (GitHub Pages project sites) — reuse the same relative prefix
// already worked out for profileSrc ("" embedded, "../" standalone) instead.
const mediaBase   = profileSrc.replace(/health-profile\.json$/, "");

let currentLocale = embedLocale || "de";
let labelSel;          // D3 selection — updated on locale switch
let focusNode;         // currently focused node — for center label update
let centerCircle;      // D3 selection — recolored to the focused category

// ── i18n strings ──────────────────────────────────────────────────────────

const I18N = {
  de: {
    hint:  "Klick auf ein Segment zum Vergrößern · Klick auf die Mitte zum Zurücknavigieren",
    back:  "← zurück",
  },
  en: {
    hint:  "Click a segment to zoom in · Click the center to navigate back",
    back:  "← back",
  },
};

// shown in the center hub at the root — replaces the "PreNUDGE Health Profile"
// text label with the actual logo.
const ROOT_LOGO = {
  de: "media/PN_Gesundheitsprofil_Logo.png",
  en: "media/PN_health_profile_Logo.png",
};

// ── helpers ────────────────────────────────────────────────────────────────

function nodeName(d) {
  return d.data[`name_${currentLocale}`] || d.data.name_de || "";
}

function catColor(d) {
  const anc = d.ancestors().find(a => a.depth === 1);
  return anc ? (anc.data.color || "#bbb") : "#ddd";
}

function fillColor(d) {
  const base = catColor(d);
  if (d.depth === 1) return base;
  if (d.depth === 2) return d3.interpolateRgb(base, "#ffffff")(0.38);
  return d3.interpolateRgb(base, "#ffffff")(0.68);
}

function arcVisible(d) {
  return d.y1 <= 4 && d.y0 >= 1 && d.x1 > d.x0;
}

function labelVisible(d) {
  return d.y1 <= 4 && d.y0 >= 1 && (d.y1 - d.y0) * (d.x1 - d.x0) > 0.032;
}

// horizontal (unrotated) label's screen position — at the wedge's centroid.
// Category labels (biasOutward) sit further toward the ring's outer edge
// instead, leaving the inner part of the ring free for the category icon
// (iconCenter) — both computed along the wedge's own radial line, so
// (unlike a fixed screen-space offset) they're guaranteed to stay within
// the wedge's radial band regardless of where it sits on the circle.
function labelXY(d, arcGen, biasOutward) {
  if (biasOutward) {
    const angle = (d.x0 + d.x1) / 2 - Math.PI / 2;
    const r     = radiusAt(d.y0) + (radiusAt(d.y1) - radiusAt(d.y0)) * 0.58;
    return { x: Math.cos(angle) * r, y: Math.sin(angle) * r };
  }
  const [x, y] = arcGen.centroid(d);
  return { x, y };
}

function labelPosition(d, arcGen, biasOutward) {
  const { x, y } = labelXY(d, arcGen, biasOutward);
  return `translate(${x},${y})`;
}

// widest a horizontal label may render without spilling past its wedge —
// the chord length at the label's radius, with a safety margin since a
// horizontal line across a wedge can run wider than the wedge itself away
// from the top/bottom of the circle.
function chordWidth(d) {
  const r    = radiusAt((d.y0 + d.y1) / 2);
  const span = Math.min(d.x1 - d.x0, Math.PI);
  return Math.max(0, 2 * r * Math.sin(span / 2) - 6) * 0.85;
}

// category icon sits directly above its label — same x as the (screen-space,
// unrotated) label position, offset upward by roughly half the label's
// (possibly 2-line) text block plus the icon's own height and a small gap.
// Note: this is a fixed screen-space offset, not a radial one, so "above"
// only reliably stays within the wedge for wedges near the top of the
// circle — for wedges elsewhere, up on screen isn't the same direction as
// toward the ring's inner edge, so the icon can drift outside the wedge.
const ICON_SIZE = 20;
const ICON_LABEL_GAP = 26;
function iconCenter(d, arcGen) {
  const { x, y } = labelXY(d, arcGen, true);
  return { x, y: y - ICON_LABEL_GAP };
}

const SVG_NS         = "http://www.w3.org/2000/svg";
const MAX_LABEL_LINES = 3;
const LINE_HEIGHT_EM  = 1.05;

// binary-search a string down to fit maxWidth (plus ellipsis), measured via
// the supplied measure() callback (real rendered glyph widths — avoids
// fixed-character-count guessing across languages).
function truncateToWidth(text, maxWidth, measure) {
  if (measure(text) <= maxWidth) return text;
  let lo = 0, hi = text.length;
  while (lo < hi) {
    const mid = Math.ceil((lo + hi) / 2);
    if (measure(text.slice(0, mid) + "…") <= maxWidth) lo = mid; else hi = mid - 1;
  }
  return lo > 0 ? text.slice(0, lo) + "…" : "";
}

// greedy word-wrap into at most maxLines lines that each fit maxWidth;
// leftover words are folded into the last line and ellipsized if needed.
// Used as a fallback when an evenly-split line (see layoutLines) still
// doesn't fit — packs as much as possible per line instead of by count.
function wrapIntoLines(fullText, maxWidth, maxLines, measure) {
  const words = fullText.split(/\s+/).filter(Boolean);
  const lines = [];
  let current = "";
  let i = 0;
  while (i < words.length && lines.length < maxLines - 1) {
    const word      = words[i];
    const candidate = current ? `${current} ${word}` : word;
    if (!current || measure(candidate) <= maxWidth) {
      current = candidate;
      i++;
    } else {
      lines.push(current);
      current = "";
    }
  }
  const rest = words.slice(i).join(" ");
  let lastLine = current ? (rest ? `${current} ${rest}` : current) : rest;
  if (lastLine && measure(lastLine) > maxWidth) {
    lastLine = truncateToWidth(lastLine, maxWidth, measure);
  }
  if (lastLine) lines.push(lastLine);
  return lines;
}

// multi-word titles are always split across (at least) two lines, evenly by
// word count, even when the full title would already fit on one line — a
// deliberate readability choice, not just an overflow fallback. Only when
// that even split still doesn't fit does this fall back to greedy
// width-based wrapping/truncation. Single-word titles are never split.
function layoutLines(fullText, maxWidth, maxLines, measure) {
  const words = fullText.split(/\s+/).filter(Boolean);
  if (words.length <= 1) {
    return measure(fullText) <= maxWidth ? [fullText] : [truncateToWidth(fullText, maxWidth, measure)];
  }

  const mid = Math.ceil(words.length / 2);
  const evenSplit = [words.slice(0, mid).join(" "), words.slice(mid).join(" ")];
  if (evenSplit.every(line => measure(line) <= maxWidth)) return evenSplit;

  return wrapIntoLines(fullText, maxWidth, maxLines, measure);
}

// renders fullText into el (a <text>) as one or more centered <tspan> lines
// (see layoutLines), measured via the element's own rendered width, so it
// works for both locales without guessing at character counts.
function fitLabel(el, fullText, maxWidth) {
  while (el.firstChild) el.removeChild(el.firstChild);
  if (!fullText || maxWidth <= 4) return;

  const measure = text => { el.textContent = text; return el.getComputedTextLength(); };

  const lines = layoutLines(fullText, maxWidth, MAX_LABEL_LINES, measure);

  el.textContent = "";
  lines.forEach((line, i) => {
    const tspan = document.createElementNS(SVG_NS, "tspan");
    tspan.setAttribute("x", 0);
    tspan.setAttribute("dy", i === 0
      ? `${-(lines.length - 1) * LINE_HEIGHT_EM / 2 + 0.32}em`
      : `${LINE_HEIGHT_EM}em`);
    tspan.textContent = line;
    el.appendChild(tspan);
  });
}

// re-fits every label's text against the given geometry ("current" while at
// rest, "target" right after a zoom, matching how fill-opacity/visibility
// are already decided off d.target without waiting for the transition tween).
function updateLabelText(selection, geomKey) {
  selection.each(function(d) {
    const geom = d[geomKey];
    if (!labelVisible(geom)) { while (this.firstChild) this.removeChild(this.firstChild); return; }
    fitLabel(this, nodeName(d), chordWidth(geom));
  });
}

function breadcrumb(d) {
  return d.ancestors()
    .filter(a => a.depth > 0)
    .reverse()
    .map(a => nodeName(a))
    .join(" > ");
}

// ── build D3 hierarchy — stores both locales + key in each node ───────────

function buildHierarchy(profile) {
  function obsNode(obs) {
    return {
      key: (obs.de || obs.en || {}).key,
      name_de: (obs.de || {}).title || "",
      name_en: (obs.en || {}).title || (obs.de || {}).title || "",
      value: 1,
    };
  }
  function dimNode(dim) {
    return {
      key: (dim.de || dim.en || {}).key,
      name_de: (dim.de || {}).title || "",
      name_en: (dim.en || {}).title || (dim.de || {}).title || "",
      children: dim.observations.length > 0
        ? dim.observations.map(obsNode)
        : null,
    };
  }
  return {
    key: null,
    name_de: "PreNUDGE",
    name_en: "PreNUDGE",
    children: profile.categories.map(cat => ({
      key: (cat.de || cat.en || {}).key,
      name_de: (cat.de || {}).title || "",
      name_en: (cat.en || {}).title || (cat.de || {}).title || "",
      color:   (cat.de || cat.en || {}).color || "#bbb",
      icon:    (cat.de || cat.en || {}).icon_upload || null,
      children: cat.dimensions.length > 0
        ? cat.dimensions.map(dimNode)
        : null,
    })),
  };
}

// ── locale switch ──────────────────────────────────────────────────────────

function switchLocale(locale) {
  currentLocale = locale;

  const btnDe = document.getElementById("btn-de");
  const btnEn = document.getElementById("btn-en");
  if (btnDe) btnDe.classList.toggle("active", locale === "de");
  if (btnEn) btnEn.classList.toggle("active", locale === "en");

  const hintEl = document.getElementById("hint");
  if (hintEl) hintEl.textContent = I18N[locale].hint;

  // update arc labels in place — no re-render needed
  if (labelSel) {
    updateLabelText(labelSel, "current");
  }

  // update center label
  if (focusNode !== undefined) setCenterLabel(focusNode);
}

// ── center label ──────────────────────────────────────────────────────────

function setCenterLabel(p) {
  focusNode = p;
  const t = I18N[currentLocale];
  const titleEl  = document.getElementById("center-title");
  const hintEl   = document.getElementById("center-hint");
  const iconEl   = document.getElementById("center-icon");
  const centerEl = document.getElementById("center");

  // whichever category we're currently inside (itself, if p is a category;
  // an ancestor, if we've zoomed further into one of its dimensions) — null
  // at the root, where the center stays its default white/no-icon state.
  const category = p.depth === 0 ? null : p.ancestors().find(a => a.depth === 1);

  if (p.depth === 0) {
    // root: the logo already carries "PreNUDGE"/"Health Profile" visually —
    // no separate title/hint text needed alongside it.
    if (titleEl) titleEl.textContent = "";
    if (hintEl)  hintEl.textContent  = "";
    if (iconEl) {
      iconEl.style.display = "block";
      iconEl.src = mediaBase + ROOT_LOGO[currentLocale];
    }
  } else {
    if (titleEl) titleEl.textContent = nodeName(p);
    if (hintEl)  hintEl.textContent  = t.back;
    if (iconEl) {
      const iconPath = category && category.data.icon;
      iconEl.style.display = iconPath ? "block" : "none";
      if (iconPath) iconEl.src = mediaBase + category.data.icon.replace(/^\//, "");
    }
  }
  if (centerEl) {
    centerEl.classList.toggle("center-tinted", !!category);
    centerEl.classList.toggle("center-root", p.depth === 0);
  }
  if (centerCircle) {
    centerCircle
      .attr("fill", category ? category.data.color : "white")
      .attr("fill-opacity", category ? 1 : 0.92);
  }
}

// ── selection event — lets a table on the same page react to clicks ───────

function dispatchSelect(p) {
  const ancestors = p.ancestors();
  const byDepth = depth => {
    const node = ancestors.find(a => a.depth === depth);
    return node ? node.data.key : null;
  };
  document.dispatchEvent(new CustomEvent("hp:select", {
    detail: {
      category:    byDepth(1),
      dimension:   byDepth(2),
      observation: byDepth(3),
    },
  }));
}

// ── main ──────────────────────────────────────────────────────────────────

// Kept so the chart can be rebuilt against a different data set without
// re-fetching (see the "hp:scope" listener at the bottom).
let fullProfile = null;

// Not just "render": this is a classic script sharing one global scope with
// scope.js and browse.js, so a generic name here is a collision waiting to
// happen - and the call below is async, so the clash would only surface at
// runtime as a chart that never draws.
function renderSunburst(profile) {

  const hintEl = document.getElementById("hint");
  if (hintEl) hintEl.textContent = I18N[currentLocale].hint;

  // rebuilt from scratch on every scope change - drop the previous chart's
  // arcs/labels/icons/center circle rather than layering new <g>s over them.
  d3.select("#chart").selectAll("*").remove();
  const emptyEl = document.getElementById("chart-empty");
  if (emptyEl) emptyEl.style.display = profile.categories.length ? "none" : "";
  if (!profile.categories.length) {
    document.dispatchEvent(new CustomEvent("hp:select", {
      detail: { category: null, dimension: null, observation: null },
    }));
    return;
  }

  const root = d3.hierarchy(buildHierarchy(profile))
    .sum(d => d.children ? 0 : d.value || 1)
    .sort((a, b) => b.value - a.value);

  // ring thickness fills exactly the space between the (hole + center gap)
  // and the chart edge, split across the actual number of data rings
  // (root.height), however many levels deep this particular hierarchy turns
  // out to be — so the outermost ring's outer edge always lands on SIZE/2,
  // never beyond it (a hardcoded per-ring radius clipped the leaf ring
  // before).
  // clamped: a filtered data set can leave the tree shallower than the usual
  // three levels (a category whose dimensions are all in the other set keeps
  // no children), and root.height would be 0 for a single-level tree.
  ringThickness = (SIZE / 2 - HOLE_RADIUS - CENTER_GAP) / Math.max(root.height, 1);

  d3.partition().size([2 * Math.PI, root.height + 1])(root);
  root.each(d => d.current = { x0: d.x0, x1: d.x1, y0: d.y0, y1: d.y1 });

  // ── arc generator ─────────────────────────────────────────────────────

  const arc = d3.arc()
    .startAngle(d => d.x0)
    .endAngle(d => d.x1)
    .padAngle(d => Math.min((d.x1 - d.x0) / 2, 0.004))
    .padRadius(HOLE_RADIUS * 1.5)
    .innerRadius(d => radiusAt(d.y0))
    .outerRadius(d => Math.max(radiusAt(d.y0), radiusAt(d.y1) - 1));

  const svg = d3.select("#chart")
    .attr("viewBox", [-SIZE / 2, -SIZE / 2, SIZE, SIZE])
    .attr("width",  SIZE)
    .attr("height", SIZE);

  // ── arcs ──────────────────────────────────────────────────────────────

  const path = svg.append("g").attr("class", "arc")
    .selectAll("path")
    .data(root.descendants().slice(1))
    .join("path")
      .attr("fill",          d => fillColor(d))
      .attr("fill-opacity",  d => arcVisible(d.current) ? 1 : 0)
      .attr("pointer-events",d => arcVisible(d.current) ? "auto" : "none")
      .attr("d",             d => arc(d.current));

  // ── labels — stored in module-level var for locale updates ────────────

  labelSel = svg.append("g")
    .attr("text-anchor", "middle")
    .selectAll("text")
    .data(root.descendants().slice(1))
    .join("text")
      .attr("class",        "arc-label")
      .attr("fill-opacity", d => +labelVisible(d.current))
      .attr("transform",    d => labelPosition(d.current, arc, d.depth === 1));

  updateLabelText(labelSel, "current");

  // ── category icons ──────────────────────────────────────────────────────

  const iconSel = svg.append("g")
    .selectAll("image")
    .data(root.descendants().filter(d => d.depth === 1 && d.data.icon))
    .join("image")
      .attr("class",         "category-icon")
      .attr("href",          d => mediaBase + d.data.icon.replace(/^\//, ""))
      .attr("width",         ICON_SIZE)
      .attr("height",        ICON_SIZE)
      .attr("pointer-events","none")
      .attr("opacity",       d => +arcVisible(d.current))
      .attr("x",             d => iconCenter(d.current, arc).x - ICON_SIZE / 2)
      .attr("y",             d => iconCenter(d.current, arc).y - ICON_SIZE / 2);

  // ── center circle (back button) ───────────────────────────────────────

  const parent = svg.append("circle")
    .datum(root)
    .attr("r", radiusAt(1))
    .attr("fill", "white")
    .attr("fill-opacity", 0.92)
    .attr("cursor", "pointer")
    .on("click", clicked);
  centerCircle = parent;

  setCenterLabel(root);

  // ── tooltip ───────────────────────────────────────────────────────────

  const tooltip = d3.select("#tooltip");

  path
    .on("mousemove", (event, d) => {
      tooltip
        .style("opacity", 1)
        .style("left", (event.clientX + 14) + "px")
        .style("top",  (event.clientY - 10) + "px")
        .html(`<strong>${nodeName(d)}</strong><br>
               <span class="path">${breadcrumb(d)}</span>`);
    })
    .on("mouseleave", () => tooltip.style("opacity", 0))
    .on("click", clicked);

  // ── zoom / click ──────────────────────────────────────────────────────

  function clicked(event, p) {
    tooltip.style("opacity", 0);
    parent.datum(p.parent || root);

    root.each(d => {
      d.target = {
        x0: Math.max(0, Math.min(1, (d.x0 - p.x0) / (p.x1 - p.x0))) * 2 * Math.PI,
        x1: Math.max(0, Math.min(1, (d.x1 - p.x0) / (p.x1 - p.x0))) * 2 * Math.PI,
        y0: Math.max(0, d.y0 - p.depth),
        y1: Math.max(0, d.y1 - p.depth),
      };
    });

    const t = svg.transition().duration(700).ease(d3.easeCubicInOut);

    path.transition(t)
      .tween("data", d => {
        const i = d3.interpolate(d.current, d.target);
        return t => d.current = i(t);
      })
      .filter(function(d) {
        return +this.getAttribute("fill-opacity") || arcVisible(d.target);
      })
      .attr("fill-opacity",   d => arcVisible(d.target) ? 1 : 0)
      .attr("pointer-events", d => arcVisible(d.target) ? "auto" : "none")
      .attrTween("d", d => () => arc(d.current));

    labelSel
      .filter(function(d) {
        return +this.getAttribute("fill-opacity") || labelVisible(d.target);
      })
      .transition(t)
      .attr("fill-opacity", d => +labelVisible(d.target))
      .attrTween("transform", d => () => labelPosition(d.current, arc, d.depth === 1));

    updateLabelText(labelSel, "target");

    iconSel
      .filter(function(d) {
        return +this.getAttribute("opacity") || arcVisible(d.target);
      })
      .transition(t)
      .attr("opacity", d => +arcVisible(d.target))
      .attrTween("x", d => () => iconCenter(d.current, arc).x - ICON_SIZE / 2)
      .attrTween("y", d => () => iconCenter(d.current, arc).y - ICON_SIZE / 2);

    setCenterLabel(p);
    dispatchSelect(p);
  }

}

d3.json(profileSrc).then(profile => {
  fullProfile = profile;

  const metaEl = document.getElementById("meta");
  if (metaEl) {
    metaEl.textContent = `Version ${profile.version} · ${profile.generated.slice(0, 10)}`;
  }

  // current() rather than a plain "combined": the switch may already have
  // been changed while the profile JSON was still in flight.
  renderSunburst(HPScope.filterProfile(profile, HPScope.current()));
}).catch(err => {
  document.body.innerHTML =
    `<p style="color:red;padding:2rem">Fehler beim Laden von ${profileSrc}:<br>
     <code>${err}</code><br><br>
     Bitte den Server aus dem Projektroot starten:<br>
     <code>py -m http.server</code></p>`;
});

document.addEventListener("hp:scope", event => {
  if (!fullProfile) return;
  renderSunburst(HPScope.filterProfile(fullProfile, event.detail.scope));
});
