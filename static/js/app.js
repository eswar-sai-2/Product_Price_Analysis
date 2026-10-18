(() => {
    const root = document.documentElement;
    const button = document.getElementById("theme-toggle");
    const preferenceKey = "product-price-analysis-theme";

    function applyTheme(theme) {
        const isLight = theme === "light";
        root.dataset.bsTheme = isLight ? "light" : "dark";
        root.style.colorScheme = isLight ? "light" : "dark";
        if (button) {
            const nextTheme = isLight ? "dark" : "light";
            button.setAttribute("aria-label", `Switch to ${nextTheme} theme`);
            button.setAttribute("aria-pressed", String(isLight));
            const label = button.querySelector(".theme-label");
            const icon = button.querySelector(".theme-icon");
            if (label) label.textContent = `${nextTheme[0].toUpperCase()}${nextTheme.slice(1)} theme`;
            if (icon) icon.textContent = isLight ? "☾" : "☼";
        }
    }

    const savedTheme = window.localStorage.getItem(preferenceKey);
    applyTheme(savedTheme === "light" ? "light" : "dark");
    if (button) {
        button.addEventListener("click", () => {
            const theme = root.dataset.bsTheme === "dark" ? "light" : "dark";
            window.localStorage.setItem(preferenceKey, theme);
            applyTheme(theme);
        });
    }

    document.querySelectorAll(".image-frame img").forEach((image) => {
        image.addEventListener("error", () => {
            image.hidden = true;
            const fallback = document.createElement("p");
            fallback.className = "image-fallback";
            fallback.textContent = "This chart image is currently unavailable.";
            image.parentElement.appendChild(fallback);
        }, { once: true });
    });
})();
