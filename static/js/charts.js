(() => {
    const canvas = document.getElementById("website-count-chart");
    const dataNode = document.getElementById("overview-chart-data");
    const fallback = document.getElementById("overview-chart-fallback");
    if (!canvas || !dataNode || !fallback) return;

    if (typeof Chart === "undefined") {
        fallback.textContent = "Interactive chart unavailable; the source counts are listed below.";
        canvas.setAttribute("aria-hidden", "true");
        return;
    }

    const chartData = JSON.parse(dataNode.textContent);
    const colors = ["#71a7ff", "#55c9a5", "#edb95e", "#b68af1", "#f27e91", "#55bfd3"];
    const textColor = getComputedStyle(document.documentElement).getPropertyValue("--muted").trim();

    new Chart(canvas, {
        type: "doughnut",
        data: {
            labels: chartData.labels,
            datasets: [{
                data: chartData.values,
                backgroundColor: chartData.labels.map((_, index) => colors[index % colors.length]),
                borderColor: getComputedStyle(document.documentElement).getPropertyValue("--surface").trim(),
                borderWidth: 3,
                hoverOffset: 5
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: "67%",
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        label(context) {
                            const total = context.dataset.data.reduce((sum, value) => sum + value, 0);
                            const percent = total ? (context.parsed / total * 100).toFixed(1) : "0.0";
                            return ` ${context.label}: ${context.parsed.toLocaleString()} products (${percent}%)`;
                        }
                    }
                }
            }
        }
    });
    fallback.hidden = true;
    canvas.parentElement.setAttribute("aria-busy", "false");
    canvas.setAttribute("aria-hidden", "false");
})();
