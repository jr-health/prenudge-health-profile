document.addEventListener("hp:select", event => {
  const table = document.getElementById("browse-table");
  if (!table) return;

  const { category, dimension, observation } = event.detail;

  table.querySelectorAll("tbody tr").forEach(row => {
    const matches =
      (!category    || row.dataset.category    === category) &&
      (!dimension   || row.dataset.dimension   === dimension) &&
      (!observation || row.dataset.observation === observation);
    row.style.display = matches ? "" : "none";
  });
});
