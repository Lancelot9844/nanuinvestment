'use strict';

{
    const key = "nanu-admin-sidebar-scroll";

    /* =========================================
       SIDEBAR SCROLL POSITION
       ========================================= */

    function initSidebarState() {
        const sidebar = document.querySelector(".custom-admin-sidebar");

        if (!sidebar) {
            return;
        }

        const savedScroll = sessionStorage.getItem(key);

        if (savedScroll !== null) {
            sidebar.scrollTop = Number(savedScroll) || 0;
        }

        sidebar.addEventListener(
            "scroll",
            function () {
                sessionStorage.setItem(
                    key,
                    String(sidebar.scrollTop)
                );
            },
            { passive: true }
        );

        sidebar.querySelectorAll("a").forEach(function (link) {
            link.addEventListener("click", function () {
                sessionStorage.setItem(
                    key,
                    String(sidebar.scrollTop)
                );
            });
        });
    }


    /* =========================================
       ADMIN PROFILE DROPDOWN
       CLOSE WHEN CLICKING OUTSIDE
       ========================================= */

    function initProfileMenu() {
        const profileMenu = document.querySelector(".admin-profile-menu");

        if (!profileMenu) {
            return;
        }

        /*
         * Close menu when clicking outside
         */
        document.addEventListener("click", function (event) {
            if (!profileMenu.contains(event.target)) {
                profileMenu.removeAttribute("open");
            }
        });

        /*
         * Close menu when pressing Escape
         */
        document.addEventListener("keydown", function (event) {
            if (event.key === "Escape") {
                profileMenu.removeAttribute("open");
            }
        });
    }


    /* =========================================
       INITIALIZE
       ========================================= */

    document.addEventListener("DOMContentLoaded", function () {
        initSidebarState();
        initProfileMenu();
    });
}