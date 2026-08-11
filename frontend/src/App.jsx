import { useEffect, useState } from "react";
import "./App.css";

import Navbar from "./components/Navbar.jsx";
import Slider from "./components/Slider.jsx";
import About from "./components/About.jsx";
import Chairman from "./components/Chairman.jsx";
import Services from "./components/Services.jsx";
import ContentSection from "./components/ContentSection.jsx";
import Popup from "./components/Popup.jsx";
import Footer from "./components/Footer.jsx";

import { readSiteContent } from "./utils/siteContent.js";
import { fetchSiteContent } from "./services/siteContentService.js";
import { addSeoSchema } from "./utils/seoSchema.js";

function App() {
  const [siteContent, setSiteContent] = useState(readSiteContent);

  const [showPopup, setShowPopup] = useState(
    Boolean(siteContent.popup)
  );

  // Load dynamic Django content
  useEffect(() => {
    let ignore = false;

    async function loadContent() {
      try {
        const nextContent = await fetchSiteContent();

        if (!ignore) {
          setSiteContent(nextContent);
          setShowPopup(Boolean(nextContent.popup));
        }
      } catch (error) {
        console.error("Failed to load site content:", error);
      }
    }

    loadContent();

    return () => {
      ignore = true;
    };
  }, []);

  // SEO Schema
  useEffect(() => {
    return addSeoSchema();
  }, []);

  const closePopup = () => {
    setShowPopup(false);
  };

  return (
    <div className="app-shell">

      {/* =========================================
          TOP BAR
          This is normal document content.
          It will scroll away.
      ========================================= */}
      <div className="top-bar">
        <div className="container-fluid">
          <div className="contact-info">

            <div className="contact-item">
              <strong>📞 +977 9744360267</strong>
            </div>

            <div className="contact-item">
              <strong>🕘 9:00am-5:00pm (Monday-Friday)</strong>
            </div>

            <div className="contact-item">
              <strong>✉ info@nanuinvestment.com</strong>
            </div>

            <div className="contact-item">
              <strong>📍 Barahathawa-12, Sarlahi</strong>
            </div>

          </div>
        </div>
      </div>

      {/* =========================================
          NAVBAR
          Sticky navbar stays at top after scrolling.
      ========================================= */}
      <Navbar />

      {/* =========================================
          POPUP
      ========================================= */}
      {showPopup && siteContent.popup && (
        <Popup
          popup={siteContent.popup}
          onClose={closePopup}
        />
      )}

      {/* =========================================
          HERO SLIDER
      ========================================= */}
      <Slider slides={siteContent.banners} />

      {/* =========================================
          MAIN CONTENT
      ========================================= */}
      <main className="main-container">

        {/* About */}
        <About />

        {/* Chairman */}
        <Chairman />

        {/* Services */}
        <Services />

        {/* News */}
        <ContentSection
          id="news"
          title="News & Activities"
          items={siteContent.news}
          actionLabel="View document"
        />

        {/* Notices */}
        <ContentSection
          id="notices"
          title="Notice"
          items={siteContent.notices}
          actionLabel="Open notice"
          compact
        />

        {/* Downloads */}
        <ContentSection
          id="downloads"
          title="Downloads"
          items={siteContent.downloads}
          actionLabel="Download"
          compact
        />

      </main>

      {/* =========================================
          FOOTER
      ========================================= */}
      <Footer />

    </div>
  );
}

export default App;