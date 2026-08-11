import { useEffect, useRef, useState } from "react";

function Navbar() {
    const [isMenuOpen, setIsMenuOpen] = useState(false);

    const navbarRef = useRef(null);

    /* =========================================
       TOGGLE MOBILE MENU
    ========================================= */
    const toggleMenu = () => {
        setIsMenuOpen((current) => !current);
    };

    /* =========================================
       CLOSE MOBILE MENU
    ========================================= */
    const closeMenu = () => {
        setIsMenuOpen(false);
    };

    /* =========================================
       CLOSE WHEN CLICKING OUTSIDE NAVBAR
    ========================================= */
    useEffect(() => {
        const handleOutsideClick = (event) => {
            if (
                navbarRef.current &&
                !navbarRef.current.contains(event.target)
            ) {
                setIsMenuOpen(false);
            }
        };

        document.addEventListener(
            "pointerdown",
            handleOutsideClick
        );

        return () => {
            document.removeEventListener(
                "pointerdown",
                handleOutsideClick
            );
        };
    }, []);

    /* =========================================
       CLOSE WITH ESCAPE KEY
    ========================================= */
    useEffect(() => {
        const handleEscape = (event) => {
            if (event.key === "Escape") {
                setIsMenuOpen(false);
            }
        };

        document.addEventListener(
            "keydown",
            handleEscape
        );

        return () => {
            document.removeEventListener(
                "keydown",
                handleEscape
            );
        };
    }, []);

    /* =========================================
       PREVENT PAGE SCROLL WHEN MOBILE MENU
       IS OPEN
    ========================================= */
    useEffect(() => {
        const isMobile =
            window.innerWidth <= 1199;

        if (isMenuOpen && isMobile) {
            document.body.style.overflow = "hidden";
        } else {
            document.body.style.overflow = "";
        }

        return () => {
            document.body.style.overflow = "";
        };
    }, [isMenuOpen]);

    return (
        <nav
            ref={navbarRef}
            className="navbar-custom"
        >
            <div className="navbar-inner">

                {/* =====================================
                    LOGO
                ===================================== */}
                <a
                    href="/"
                    className="navbar-brand"
                    onClick={closeMenu}
                    aria-label="Nanu Investment Home"
                >
                    <img
                        src="/static/company_logo.png"
                        alt="Nanu Investment"
                        className="navbar-logo"
                    />
                </a>


                {/* =====================================
                    HAMBURGER BUTTON
                ===================================== */}
                <button
                    type="button"
                    className={`navbar-toggler ${
                        isMenuOpen ? "active" : ""
                    }`}
                    onClick={toggleMenu}
                    aria-controls="navbarNav"
                    aria-expanded={isMenuOpen}
                    aria-label={
                        isMenuOpen
                            ? "Close navigation"
                            : "Open navigation"
                    }
                >
                    <span></span>
                    <span></span>
                    <span></span>
                </button>


                {/* =====================================
                    NAVIGATION MENU
                ===================================== */}
                <div
                    id="navbarNav"
                    className={`navbar-menu ${
                        isMenuOpen ? "show" : ""
                    }`}
                >
                    <ul className="navbar-nav">

                        {/* HOME */}
                        <li className="nav-item">
                            <a
                                className="nav-link"
                                href="#home"
                                onClick={closeMenu}
                            >
                                HOME
                            </a>
                        </li>


                        {/* ABOUT */}
                        <li className="nav-item">
                            <a
                                className="nav-link"
                                href="#about"
                                onClick={closeMenu}
                            >
                                ABOUT US
                            </a>
                        </li>


                        {/* SERVICES */}
                        <li className="nav-item">
                            <a
                                className="nav-link"
                                href="#services"
                                onClick={closeMenu}
                            >
                                SERVICES
                            </a>
                        </li>


                        {/* NEWS */}
                        <li className="nav-item">
                            <a
                                className="nav-link"
                                href="#news"
                                onClick={closeMenu}
                            >
                                NEWS &amp; ACTIVITIES
                            </a>
                        </li>


                        {/* NOTICE */}
                        <li className="nav-item">
                            <a
                                className="nav-link"
                                href="#notices"
                                onClick={closeMenu}
                            >
                                NOTICE
                            </a>
                        </li>


                        {/* DOWNLOADS */}
                        <li className="nav-item">
                            <a
                                className="nav-link"
                                href="#downloads"
                                onClick={closeMenu}
                            >
                                DOWNLOADS
                            </a>
                        </li>


                        {/* CONTACT */}
                        <li className="nav-item">
                            <a
                                className="nav-link"
                                href="#contact"
                                onClick={closeMenu}
                            >
                                CONTACT US
                            </a>
                        </li>


                        {/* =================================
                            LOGIN / USER ICON
                        ================================= */}
                        <li className="nav-item login-item">
                            <a
                                className="nav-link login-link"
                                href="/login/"
                                aria-label="Login"
                                data-tooltip="Login"
                                onClick={closeMenu}
                            >
                                <svg
                                    className="login-icon"
                                    viewBox="0 0 24 24"
                                    aria-hidden="true"
                                >
                                    <path
                                        d="M20 21a8 8 0 0 0-16 0"
                                    />

                                    <circle
                                        cx="12"
                                        cy="7"
                                        r="4"
                                    />
                                </svg>
                            </a>
                        </li>

                    </ul>
                </div>

            </div>
        </nav>
    );
}

export default Navbar;