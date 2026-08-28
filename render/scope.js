// Shared data-set filtering for the sunburst chart and the browse table.
//
// Mirrors filter_tree() in scripts/consolidate.py so that switching the
// dropdown on a page shows exactly what the correspondingly-scoped .docx
// export contains. Keep the two in sync when the rule changes.
//
// Loaded before sunburst.js / browse.js, which both react to the "hp:scope"
// event dispatched here.

const HPScope = (() => {
  const COMBINED = "combined";

  // CMS option strings (admin/config.yml, field `dataset-scope`) -> scope ids.
  const SCOPE_VALUES = { "Minimalset": "minimalset", "Extension": "extended" };

  // `dataset-scope` is an i18n: duplicate field, so de and en always hold the
  // same value and either may be read.
  function scopeOf(entry) {
    const raw = (entry.de || {})["dataset-scope"] || (entry.en || {})["dataset-scope"];
    return SCOPE_VALUES[raw] || null;
  }

  function inScope(entry, scope) {
    return scope === COMBINED || scopeOf(entry) === scope;
  }

  // Every level is selected by its own `dataset-scope`, and an entry is kept
  // as well when any of its descendants was selected - so a category or
  // dimension belongs to the set it is flagged for even while all of its
  // observations still sit in the other set, and a selected observation is
  // never orphaned by an ancestor flagged the other way.
  function filterProfile(profile, scope) {
    if (scope === COMBINED) return profile;

    const categories = [];
    for (const cat of profile.categories) {
      const dimensions = [];
      for (const dim of cat.dimensions) {
        const observations = dim.observations.filter(o => inScope(o, scope));
        if (observations.length > 0 || inScope(dim, scope)) {
          dimensions.push({ ...dim, observations });
        }
      }

      if (dimensions.length > 0 || inScope(cat, scope)) {
        categories.push({ ...cat, dimensions });
      }
    }

    return { ...profile, categories };
  }

  const switchEl = document.getElementById("scope-switch");

  // Read from the pressed button rather than tracking state, so a view
  // rendering for the first time picks up the current selection even if it
  // missed the event (the sunburst renders asynchronously, after its profile
  // JSON arrives).
  function current() {
    if (!switchEl) return COMBINED;
    const pressed = switchEl.querySelector('button[aria-pressed="true"]');
    return pressed ? pressed.dataset.scope : COMBINED;
  }

  function setPressed(scope) {
    if (!switchEl) return;
    // aria-pressed is the state, not just a label: current() and the
    // active-segment styling both read it.
    switchEl.querySelectorAll("button[data-scope]").forEach(b => {
      b.setAttribute("aria-pressed", String(b.dataset.scope === scope));
    });
  }

  // Carry the selection across page navigation (Explore <-> full-page
  // Sunburst/Table, and the language switch) as ?set=<scope>, so following a
  // link doesn't silently reset the chart and table to a different data set.
  function syncLinks() {
    const scope = current();
    document.querySelectorAll("a[data-keep-scope]").forEach(a => {
      a.search = `?set=${scope}`;
    });
  }

  if (switchEl) {
    // An incoming ?set= wins over the button marked pressed in the markup.
    const requested = new URLSearchParams(window.location.search).get("set");
    if (requested && switchEl.querySelector(`button[data-scope="${requested}"]`)) {
      setPressed(requested);
    }
    syncLinks();

    switchEl.addEventListener("click", event => {
      const button = event.target.closest("button[data-scope]");
      if (!button || button.getAttribute("aria-pressed") === "true") return;

      setPressed(button.dataset.scope);
      syncLinks();
      document.dispatchEvent(new CustomEvent("hp:scope", { detail: { scope: button.dataset.scope } }));
    });
  }

  return { COMBINED, scopeOf, inScope, filterProfile, current };
})();
