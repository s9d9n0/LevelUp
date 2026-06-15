document.addEventListener("htmx:afterSwap", () => {
    const form = document.querySelector(".scan-form");
    const bar = document.getElementById("export-bar");
    const link = document.getElementById("export-link");

    if (!form || !bar || !link) return;

    const rsi_min = form.querySelector("[name=rsi_min]").value;
    const rsi_max = form.querySelector("[name=rsi_max]").value;
    const macd_signal = form.querySelector("[name=macd_signal]").checked;
    const above_ema = form.querySelector("[name=above_ema]").checked;

    const params = new URLSearchParams({ rsi_min, rsi_max, macd_signal, above_ema });
    link.href = `/export?${params}`;
    bar.style.display = "block";
});