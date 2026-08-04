'use strict';
{
    function setTheme(mode) {
        if (mode !== "light" && mode !== "dark") {
            mode = "light";
        }
        document.documentElement.dataset.theme = mode;
        localStorage.setItem("theme", mode);
    }

    function cycleTheme() {
        const currentTheme = localStorage.getItem("theme") || "light";
        setTheme(currentTheme === "dark" ? "light" : "dark");
    }

    function initTheme() {
        const currentTheme = localStorage.getItem("theme");
        setTheme(currentTheme === "dark" ? "dark" : "light");
    }

    window.addEventListener("load", function() {
        const buttons = document.getElementsByClassName("theme-toggle");
        Array.from(buttons).forEach((btn) => {
            btn.addEventListener("click", cycleTheme);
        });
    });

    initTheme();
}
