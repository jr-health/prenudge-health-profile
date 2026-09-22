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
let ringTitleSel;      // D3 selection — updated on locale switch and zoom
let currentMaxDepth;   // root.height of the last render — ring-title row count

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

// ring-level axis titles, curved along the top (12 o'clock) of each ring —
// one per semantic depth (1 = Category, matching hierarchy depth). Same
// wording as the browse table's column headers (render/templates/
// _browse_table.{de,en}.html.j2), for consistency.
const LEVEL_LABELS = {
  de: ["Kategorie", "Gesundheitsindikator", "Messinstrument"],
  en: ["Category", "Health Indicator", "Measurement Instrument"],
};

// half the angular span (radians) the label's arc may curve across — same
// for every ring, so wider outer rings give the text more linear room
// (arc length = r * RING_TITLE_HALF_ANGLE * 2) than the tight inner ring,
// where long labels fall back to truncation.
const RING_TITLE_HALF_ANGLE = 0.5;

// centered on 11 o'clock rather than 12 — at RING_TITLE_RADIAL_BIAS 1 the
// outermost title sits exactly on the chart's outer edge, and at 12 o'clock
// that point touches the (square) SVG viewBox with zero clearance, clipping
// the text; off-center, the nearest viewBox edge is comfortably farther away.
const RING_TITLE_CENTER_ANGLE = -Math.PI / 6;

// endpoints of a ring-title's arc at radius r — same clockwise-from-12
// convention as labelXY/iconCenter (angle - PI/2 feeds cos/sin directly).
function ringTitleArcPath(r) {
  const a0 = RING_TITLE_CENTER_ANGLE - RING_TITLE_HALF_ANGLE - Math.PI / 2;
  const a1 = RING_TITLE_CENTER_ANGLE + RING_TITLE_HALF_ANGLE - Math.PI / 2;
  const x0 = Math.cos(a0) * r, y0 = Math.sin(a0) * r;
  const x1 = Math.cos(a1) * r, y1 = Math.sin(a1) * r;
  return `M${x0},${y0} A${r},${r} 0 0 1 ${x1},${y1}`;
}

// fraction from a ring's inner (0) to outer (1) edge where its title sits —
// biased toward the outer edge, away from the ring's own wedge labels
// (positioned near the centroid by labelXY/arcGen.centroid, see below), so
// the two stop competing for the same space.
const RING_TITLE_RADIAL_BIAS = 1;

function ringTitleRadius(depth, focus) {
  return radiusAt(Math.max(depth - focus.depth, 0) + RING_TITLE_RADIAL_BIAS);
}

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

// fades each ring-title in/out and re-curves its arc path against the
// ring's *current* radius — d.r is the mutable per-datum radius (mirrors
// the d.current pattern the arcs/labels already use), tweened smoothly
// across a zoom transition via attrTween since an SVG path's "d" can't be
// interpolated directly. Only ever called with a transition (the zoom
// click handler) — the initial/locale-switch render sets "d" directly
// instead, since attrTween only applies to transitions. onSettled, if
// given, runs once the radius tween finishes (re-fit the text — see
// updateRingTitleText); chained onto this same transition rather than a
// second .transition(t) on the same elements, which would compete with
// this one instead of sharing its schedule.
function updateRingTitleGeometry(sel, focus, onSettled) {
  sel.attr("opacity", d => (d.depth - focus.depth >= 1 ? 1 : 0));
  const pathSel = sel.select(".ring-title-path")
    .attrTween("d", function(d) {
      const target = ringTitleRadius(d.depth, focus);
      const interpolateR = d3.interpolate(d.r, target);
      return t => {
        d.r = interpolateR(t);
        return ringTitleArcPath(d.r);
      };
    });
  if (onSettled) pathSel.on("end", onSettled);
}

// re-fits each ring-title's curved text against its *current* arc length —
// called once per render/locale-switch and again after a zoom's radius
// settles (its available arc length can shrink or grow a lot when a level
// moves between an inner and outer ring), not on every animation frame,
// since re-measuring text via getComputedTextLength() mid-tween would be
// wasted work the eye can't follow anyway.
function updateRingTitleText(sel) {
  const labels = LEVEL_LABELS[currentLocale] || LEVEL_LABELS.de;
  sel.each(function(d) {
    const textPath = d3.select(this).select("textPath");
    const arcLength = Math.max(0, d.r * RING_TITLE_HALF_ANGLE * 2 - 12);
    const measure = text => { textPath.text(text); return textPath.node().getComputedTextLength(); };
    textPath.text(truncateToWidth(labels[d.depth - 1] || "", arcLength, measure));
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
  // source-type (admin/config.yml) only ever holds one of two full option
  // strings ("Questionnaire · manual (self-reported)" / "Wearable device /
  // sensor · automated") - shortened here since the full text doesn't fit a
  // ring segment. The questionnaire/device name itself lives in the sibling
  // `device` field, appended in parens so e.g. "Questionnaire (WHOQOL-BREF)"
  // distinguishes instruments that would otherwise share a label.
  function instrumentNode(instr) {
    const sourceType = instr["source-type"] || "";
    const isQuestionnaire = sourceType.startsWith("Questionnaire");
    const base = isQuestionnaire ? "Questionnaire"
      : sourceType.startsWith("Wearable") ? "Wearable device"
      : sourceType;
    const label = isQuestionnaire && instr.device ? `${base} (${instr.device})` : base;
    return {
      key: null,
      name_de: label,
      name_en: label,
      value: 1,
    };
  }
  function obsNode(obs) {
    const instruments = (obs.de || {})["measurement-instrument"]
      || (obs.en || {})["measurement-instrument"]
      || [];
    return {
      key: (obs.de || obs.en || {}).key,
      name_de: (obs.de || {}).title || "",
      name_en: (obs.en || {}).title || (obs.de || {}).title || "",
      value: 1,
      children: instruments.length > 0 ? instruments.map(instrumentNode) : null,
    };
  }
  return {
    key: null,
    name_de: "PreNUDGE",
    name_en: "PreNUDGE",
    // dimensions still exist in the source data (categories -> dimensions ->
    // observations) but no longer get their own ring here - observations sit
    // directly under their category, flattened across all of its dimensions.
    children: profile.categories.map(cat => {
      const observations = cat.dimensions.flatMap(dim => dim.observations || []);
      return {
        key: (cat.de || cat.en || {}).key,
        name_de: (cat.de || {}).title || "",
        name_en: (cat.en || {}).title || (cat.de || {}).title || "",
        color:   (cat.de || cat.en || {}).color || "#bbb",
        icon:    (cat.de || cat.en || {}).icon_upload || null,
        children: observations.length > 0
          ? observations.map(obsNode)
          : null,
      };
    }),
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

  // update ring titles (text changed — re-fit against the current arcs)
  if (ringTitleSel) {
    updateRingTitleText(ringTitleSel);
  }
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
      observation: byDepth(2),
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
      detail: { category: null, observation: null },
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

  // ── ring-level axis titles ───────────────────────────────────────────
  // curved along the top of each ring, on top of the wedge color — a white
  // text halo (CSS paint-order/stroke) keeps them legible over any color.

  currentMaxDepth = root.height;

  const ringTitleData = d3.range(1, currentMaxDepth + 1)
    .map(depth => ({ depth, r: ringTitleRadius(depth, root) }));

  const ringTitleG = svg.append("g").attr("class", "ring-titles");
  ringTitleSel = ringTitleG.selectAll("g.ring-title")
    .data(ringTitleData, d => d.depth)
    .join(enter => {
      const g = enter.append("g").attr("class", "ring-title");
      g.append("path").attr("class", "ring-title-path").attr("id", d => `ring-title-path-${d.depth}`);
      g.append("text").attr("class", "ring-title-text").attr("dy", "0.32em")
        .append("textPath")
          .attr("href", d => `#ring-title-path-${d.depth}`)
          .attr("startOffset", "50%")
          .attr("text-anchor", "middle");
      return g;
    });

  ringTitleSel.attr("opacity", d => (d.depth - root.depth >= 1 ? 1 : 0));
  ringTitleSel.select(".ring-title-path").attr("d", d => ringTitleArcPath(d.r));
  updateRingTitleText(ringTitleSel);

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

    updateRingTitleGeometry(ringTitleSel.transition(t), p, () => updateRingTitleText(ringTitleSel));

    setCenterLabel(p);
    dispatchSelect(p);
  }

}

// ── PNG export ──────────────────────────────────────────────────────────
// exports the current view (zoom depth, scope, locale — whatever's on
// screen right now) as a flat PNG: rasterizes the live <svg id="chart"> via
// an offscreen <canvas>, then redraws the HTML #center overlay (icon/title/
// hint — a CSS-positioned sibling <div>, not part of the SVG) on top by
// hand. A <foreignObject> would be the obvious way to fold that overlay
// into the SVG before rasterizing, and it briefly was implemented that way,
// but Chrome taints the canvas for *any* SVG-to-image draw whose source SVG
// contains a foreignObject, even once every resource inside it is inlined
// — there's no way to read the pixels back out afterwards. Redrawing by
// hand avoids that entirely, at the cost of only approximating (not
// pixel-matching) the live DOM's text layout — good enough for a title/hint
// that's usually one or two short words.

// converts a same-origin image URL to a data: URL so the rasterized SVG
// doesn't depend on loading external files at draw time — avoids canvas
// tainting and load-order races with the synchronous draw below.
function toDataURL(url) {
  return fetch(url)
    .then(r => r.blob())
    .then(blob => new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload  = () => resolve(reader.result);
      reader.onerror = reject;
      reader.readAsDataURL(blob);
    }));
}

// inlines every SVG <image>/HTML <img> found under root as a data: URL, in place.
async function inlineImages(root) {
  const nodes = [...root.querySelectorAll("image"), ...root.querySelectorAll("img")];
  await Promise.all(nodes.map(async el => {
    const attr = el.tagName.toLowerCase() === "img" ? "src" : "href";
    const url  = el.getAttribute(attr);
    if (!url || url.startsWith("data:")) return;
    try {
      el.setAttribute(attr, await toDataURL(url));
    } catch (err) {
      console.error("PNG export: failed to inline image", url, err);
    }
  }));
}

// redraws the #center overlay (icon/title/hint) onto ctx by hand, in place
// of the foreignObject that would otherwise taint the canvas (see above).
// toCanvas() maps a point in *live page* CSS-pixel space (from
// getBoundingClientRect(), same coordinate space the browser already laid
// the overlay out in) to canvas-pixel space, so this lines up whether the
// chart is the large standalone page or the smaller embedded panel.
function drawCenterOverlay(ctx, canvas) {
  const svgEl    = document.getElementById("chart");
  const centerEl = document.getElementById("center");
  const titleEl  = document.getElementById("center-title");
  const hintEl   = document.getElementById("center-hint");
  const iconEl   = document.getElementById("center-icon");
  if (!svgEl || !centerEl) return;

  const svgRect = svgEl.getBoundingClientRect();
  const k       = canvas.width / svgRect.width; // canvas px per live CSS px
  const originX = svgRect.left + svgRect.width  / 2;
  const originY = svgRect.top  + svgRect.height / 2;
  const toCanvas = (clientX, clientY) => ({
    x: canvas.width  / 2 + (clientX - originX) * k,
    y: canvas.height / 2 + (clientY - originY) * k,
  });

  if (iconEl && iconEl.style.display !== "none" && iconEl.complete && iconEl.naturalWidth) {
    const r  = iconEl.getBoundingClientRect();
    const tl = toCanvas(r.left, r.top);
    ctx.drawImage(iconEl, tl.x, tl.y, r.width * k, r.height * k);
  }

  const isTinted = centerEl.classList.contains("center-tinted");

  const drawText = (el, color) => {
    const text = el && el.textContent.trim();
    if (!el || !text) return;
    const style  = getComputedStyle(el);
    const fontPx = parseFloat(style.fontSize) * k;
    ctx.font         = `${style.fontWeight} ${fontPx}px ${style.fontFamily}`;
    ctx.fillStyle    = color;
    ctx.textAlign    = "center";
    ctx.textBaseline = "alphabetic";

    const r          = el.getBoundingClientRect();
    const top        = toCanvas(r.left + r.width / 2, r.top);
    const maxWidth   = r.width * k;
    const lines      = layoutLines(text, maxWidth, MAX_LABEL_LINES, t => ctx.measureText(t).width);
    const lineHeight = fontPx * LINE_HEIGHT_EM;
    lines.forEach((line, i) => ctx.fillText(line, top.x, top.y + (i + 0.8) * lineHeight));
  };

  drawText(titleEl, isTinted ? "#ffffff" : "#222222");
  drawText(hintEl,  isTinted ? "rgba(255,255,255,0.85)" : "#bbbbbb");
}

const PNG_EXPORT_SCALE = 2; // rasterize at 2x SIZE for a crisp download

async function exportChartPNG() {
  const svgEl = document.getElementById("chart");
  if (!svgEl) return;

  const clone = svgEl.cloneNode(true);
  clone.setAttribute("xmlns", "http://www.w3.org/2000/svg");
  // .arc-label/.ring-title-text don't set their own font-family, relying on
  // inheriting the page's `body { font-family: Verdana, ... }` — which a
  // standalone SVG document has no <body> to match, so without this it
  // silently falls back to the browser's default (serif) font.
  clone.setAttribute("font-family", "Verdana, Geneva, sans-serif");

  // classed styles (.arc path, .arc-label, .ring-title-text, ...) live in
  // the page's <style> block, which a standalone serialized SVG can't see —
  // embed it directly so the export doesn't fall back to unstyled shapes.
  const styleEl = document.createElementNS(SVG_NS, "style");
  styleEl.textContent = Array.from(document.querySelectorAll("style")).map(s => s.textContent).join("\n");
  clone.insertBefore(styleEl, clone.firstChild);

  await inlineImages(clone);

  const svgString = new XMLSerializer().serializeToString(clone);
  const svgUrl    = URL.createObjectURL(new Blob([svgString], { type: "image/svg+xml;charset=utf-8" }));

  const img = new Image();
  img.src = svgUrl;
  await img.decode();

  const canvas = document.createElement("canvas");
  canvas.width  = SIZE * PNG_EXPORT_SCALE;
  canvas.height = SIZE * PNG_EXPORT_SCALE;
  const ctx = canvas.getContext("2d");
  ctx.fillStyle = "#ffffff"; // canvas is transparent by default; the page behind it isn't
  ctx.fillRect(0, 0, canvas.width, canvas.height);
  ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
  URL.revokeObjectURL(svgUrl);

  drawCenterOverlay(ctx, canvas);

  canvas.toBlob(blob => {
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = `prenudge-health-profile-sunburst-${currentLocale}.png`;
    a.click();
    URL.revokeObjectURL(a.href);
  }, "image/png");
}

const downloadPngBtn = document.getElementById("btn-download-png");
if (downloadPngBtn) {
  downloadPngBtn.addEventListener("click", () => {
    exportChartPNG().catch(err => console.error("PNG export failed", err));
  });
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
