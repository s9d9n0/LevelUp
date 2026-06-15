(function() {
    function initSort() {
        const state = {};

        document.querySelectorAll("#results-table th[data-col]").forEach(th => {
            th.style.cursor = "pointer";
            th.addEventListener("click", () => {
                const col = th.dataset.col;
                state[col] = state[col] === "asc" ? "desc" : "asc";
                const dir = state[col];

                document.querySelectorAll("#results-table th[data-col]").forEach(h => {
                    h.textContent = h.textContent.replace(" ▲", "").replace(" ▼", "").replace(" ⇅", "") + " ⇅";
                });
                th.textContent = th.textContent.replace(" ⇅", "") + (dir === "asc" ? " ▲" : " ▼");

                const tbody = document.getElementById("results-body");
                const rows = Array.from(tbody.querySelectorAll("tr"));

                rows.sort((a, b) => {
                    let va = a.dataset[col];
                    let vb = b.dataset[col];
                    const na = parseFloat(va);
                    const nb = parseFloat(vb);
                    if (!isNaN(na) && !isNaN(nb)) {
                        return dir === "asc" ? na - nb : nb - na;
                    }
                    return dir === "asc" ? va.localeCompare(vb) : vb.localeCompare(va);
                });

                rows.forEach(row => tbody.appendChild(row));
            });
        });
    }

    // Initialise au chargement et après chaque mise à jour HTMX
    document.addEventListener("DOMContentLoaded", initSort);
    document.addEventListener("htmx:afterSwap", initSort);
})();