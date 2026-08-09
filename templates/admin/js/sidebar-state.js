'use strict';
{
    const key = "nanu-admin-sidebar-scroll";

    function initSidebarState() {
        const sidebar = document.querySelector(".custom-admin-sidebar");

        if (!sidebar) {
            return;
        }

        const savedScroll = sessionStorage.getItem(key);
        if (savedScroll !== null) {
            sidebar.scrollTop = Number(savedScroll) || 0;
        }

        sidebar.addEventListener("scroll", function() {
            sessionStorage.setItem(key, String(sidebar.scrollTop));
        }, { passive: true });

        sidebar.querySelectorAll("a").forEach((link) => {
            link.addEventListener("click", function() {
                sessionStorage.setItem(key, String(sidebar.scrollTop));
            });
        });
    }

    window.addEventListener("DOMContentLoaded", initSidebarState);
}
