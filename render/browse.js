// Row visibility in the browse table is driven by two independent filters -
// the data-set switch ("hp:scope", see scope.js) and the sunburst selection
// ("hp:select") - plus pagination on top. All three are held as state here and
// applied together. Letting each event set row.style.display on its own would
// make whichever fired last silently undo the others.
//
// Pagination runs over the rows that pass the filters, not over every row, so
// the page count tracks the current data set rather than the full catalogue.
//
// Wrapped in an IIFE: this is a classic script sharing one global scope with
// sunburst.js, and a bare top-level `function render()` here silently replaced
// the sunburst's own render() - which is called asynchronously, so the only
// symptom was a chart that never appeared.

(() => {
  const PAGE_SIZE = 10;

  let scopeFilter = HPScope.current();
  let selection = { category: null, dimension: null, observation: null };
  let currentPage = 1;

  const table = document.getElementById("browse-table");
  const statusEl = document.getElementById("pager-status");
  const prevBtn = document.getElementById("pager-prev");
  const nextBtn = document.getElementById("pager-next");

  function allRows() {
    return table ? Array.from(table.querySelectorAll("tbody tr")) : [];
  }

  function matchingRows() {
    const { category, dimension, observation } = selection;
    return allRows().filter(row =>
      (scopeFilter === "combined" || row.dataset.scope === scopeFilter) &&
      (!category    || row.dataset.category    === category) &&
      (!dimension   || row.dataset.dimension   === dimension) &&
      (!observation || row.dataset.observation === observation)
    );
  }

  function render() {
    const matching = matchingRows();
    const pageCount = Math.max(1, Math.ceil(matching.length / PAGE_SIZE));
    // clamp rather than reset: paging to the end and then narrowing the filter
    // would otherwise leave us on a page that no longer exists
    if (currentPage > pageCount) currentPage = pageCount;

    const start = (currentPage - 1) * PAGE_SIZE;
    const onPage = new Set(matching.slice(start, start + PAGE_SIZE));
    allRows().forEach(row => { row.style.display = onPage.has(row) ? "" : "none"; });

    if (statusEl) {
      statusEl.textContent = matching.length === 0
        ? statusEl.dataset.empty
        : statusEl.dataset.format
            .replace("{from}", String(start + 1))
            .replace("{to}", String(Math.min(start + PAGE_SIZE, matching.length)))
            .replace("{total}", String(matching.length));
    }
    if (prevBtn) prevBtn.disabled = currentPage <= 1;
    if (nextBtn) nextBtn.disabled = currentPage >= pageCount;
  }

  function goToPage(page) {
    currentPage = page;
    render();
  }

  if (prevBtn) prevBtn.addEventListener("click", () => goToPage(currentPage - 1));
  if (nextBtn) nextBtn.addEventListener("click", () => goToPage(currentPage + 1));

  document.addEventListener("hp:select", event => {
    selection = event.detail;
    currentPage = 1;
    render();
  });

  document.addEventListener("hp:scope", event => {
    scopeFilter = event.detail.scope;
    // The sunburst rebuilds from scratch on a scope change and returns to its
    // root, so the selection it had dispatched no longer applies.
    selection = { category: null, dimension: null, observation: null };
    currentPage = 1;
    render();
  });

  // The table is rendered with every row present, so the starting data set (the
  // default pressed segment, or an incoming ?set=) has to be applied once on
  // load - there is no event to wait for.
  render();
})();
