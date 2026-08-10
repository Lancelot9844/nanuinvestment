import { useEffect, useRef, useState } from 'react'

function Navbar() {
  const [isMenuOpen, setIsMenuOpen] = useState(false)

  const navbarRef = useRef(null)

  // Toggle mobile menu
  const toggleMenu = () => {
    setIsMenuOpen((current) => !current)
  }

  // Close menu
  const closeMenu = () => {
    setIsMenuOpen(false)
  }

  // Close menu when clicking outside navbar
  useEffect(() => {
    const handleOutsideClick = (event) => {
      if (
        navbarRef.current &&
        !navbarRef.current.contains(event.target)
      ) {
        setIsMenuOpen(false)
      }
    }

    document.addEventListener('mousedown', handleOutsideClick)

    return () => {
      document.removeEventListener(
        'mousedown',
        handleOutsideClick
      )
    }
  }, [])

  // Close menu when pressing Escape
  useEffect(() => {
    const handleEscape = (event) => {
      if (event.key === 'Escape') {
        setIsMenuOpen(false)
      }
    }

    document.addEventListener('keydown', handleEscape)

    return () => {
      document.removeEventListener(
        'keydown',
        handleEscape
      )
    }
  }, [])

  return (
    <nav
      ref={navbarRef}
      className="navbar navbar-expand-lg navbar-dark navbar-custom"
    >
      <div className="container-fluid">

        {/* Brand */}
        <a
          className="navbar-brand"
          href="#home"
          onClick={closeMenu}
        >
          NANU INVESTMENT
        </a>

        {/* Mobile Hamburger */}
        <button
          className="navbar-toggler"
          type="button"
          onClick={toggleMenu}
          aria-controls="navbarNav"
          aria-expanded={isMenuOpen}
          aria-label="Toggle navigation"
        >
          <span className="navbar-toggler-icon"></span>
        </button>

        {/* Navigation Menu */}
        <div
          id="navbarNav"
          className={`collapse navbar-collapse ${
            isMenuOpen ? 'show' : ''
          }`}
        >
          <ul className="navbar-nav ms-auto">

            <li className="nav-item">
              <a
                className="nav-link"
                href="#home"
                onClick={closeMenu}
              >
                HOME
              </a>
            </li>

            <li className="nav-item">
              <a
                className="nav-link"
                href="#about"
                onClick={closeMenu}
              >
                ABOUT US
              </a>
            </li>

            <li className="nav-item">
              <a
                className="nav-link"
                href="#services"
                onClick={closeMenu}
              >
                SERVICES
              </a>
            </li>

            <li className="nav-item">
              <a
                className="nav-link"
                href="#news"
                onClick={closeMenu}
              >
                NEWS & ACTIVITIES
              </a>
            </li>

            <li className="nav-item">
              <a
                className="nav-link"
                href="#notices"
                onClick={closeMenu}
              >
                NOTICE
              </a>
            </li>

            <li className="nav-item">
              <a
                className="nav-link"
                href="#downloads"
                onClick={closeMenu}
              >
                DOWNLOADS
              </a>
            </li>

            <li className="nav-item">
              <a
                className="nav-link"
                href="#contact"
                onClick={closeMenu}
              >
                CONTACT US
              </a>
            </li>

            {/* Login */}
            <li className="nav-item">
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
                  <path d="M20 21a8 8 0 0 0-16 0" />
                  <circle cx="12" cy="7" r="4" />
                </svg>
              </a>
            </li>

          </ul>
        </div>

      </div>
    </nav>
  )
}

export default Navbar