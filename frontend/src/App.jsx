import { useEffect, useState } from "react";
import "./App.css";
import "bootstrap-icons/font/bootstrap-icons.css";

import Navbar from "./components/Navbar.jsx";
import Slider from "./components/Slider.jsx";
import About from "./components/About.jsx";
import Chairman from "./components/Chairman.jsx";
import Services from "./components/Services.jsx";
import ContentSection from "./components/ContentSection.jsx";
import Popup from "./components/Popup.jsx";
import Footer from "./components/Footer.jsx";
import PremiumCalculator from "./components/PremiumCalculator.jsx";

import { readSiteContent } from "./utils/siteContent.js";
import { fetchSiteContent } from "./services/siteContentService.js";
import { addSeoSchema } from "./utils/seoSchema.js";

import { Routes, Route, Link } from "react-router-dom";

function TopBar() {
  return (
    <div className="top-bar">
      <div className="container-fluid">
        <div className="contact-info">
          <div className="contact-item">
            <strong>
              <i className="bi bi-telephone"></i> +977 9744360267
            </strong>
          </div>

          <div className="contact-item">
            <strong>
              <i className="bi bi-clock"></i> 9:00am-5:00pm (Monday-Friday)
            </strong>
          </div>

          <div className="contact-item">
            <strong>
              <i className="bi bi-envelope"></i> info@nanuinvestment.com
            </strong>
          </div>

          <div className="contact-item">
            <strong>
              <i className="bi bi-geo-alt"></i> Barahathawa-12, Sarlahi
            </strong>
          </div>
        </div>
      </div>
    </div>
  );
}

function WebsiteLayout({ children, showCalculatorButton = false }) {
  return (
    <div className="app-shell">
      <TopBar />

      <Navbar />

      {children}

      {showCalculatorButton && (
        <Link
          to="/premium-calculator/"
          className="premium-calculator-float"
          aria-label="Premium Calculator"
          title="Premium Calculator"
        >
          <span className="calculator-icon" aria-hidden="true">
            <i class="bi-calculator fs-lg"></i>
          </span>

          <span className="calculator-text">Premium Calculator</span>
        </Link>
      )}

      <Footer />
    </div>
  );
}

function Home() {
  const [siteContent, setSiteContent] = useState(readSiteContent);

  const [showPopup, setShowPopup] = useState(Boolean(siteContent.popup));

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

  useEffect(() => {
    return addSeoSchema();
  }, []);

  const closePopup = () => {
    setShowPopup(false);
  };

  return (
    <WebsiteLayout showCalculatorButton={true}>
      {showPopup && siteContent.popup && (
        <Popup popup={siteContent.popup} onClose={closePopup} />
      )}

      <Slider slides={siteContent.banners} />

      <main className="main-container">
        {/* ABOUT */}

        <About />

        {/* CHAIRMAN */}

        <Chairman />

        {/* SERVICES */}

        <Services />

        {/* NEWS */}

        <ContentSection
          id="news"
          title="News & Activities"
          items={siteContent.news}
          actionLabel="View document"
        />

        {/* NOTICES */}

        <ContentSection
          id="notices"
          title="Notice"
          items={siteContent.notices}
          actionLabel="Open notice"
          compact
        />

        {/* DOWNLOADS */}

        <ContentSection
          id="downloads"
          title="Downloads"
          items={siteContent.downloads}
          actionLabel="Download"
          compact
        />
      </main>
    </WebsiteLayout>
  );
}

function PremiumCalculatorPage() {
  return (
    <WebsiteLayout showCalculatorButton={false}>
      <main className="premium-calculator-page">
        <PremiumCalculator />
      </main>
    </WebsiteLayout>
  );
}

function App() {
  return (
    <Routes>
      <Route path="/" element={<Home />} />

      <Route path="/premium-calculator/" element={<PremiumCalculatorPage />} />
    </Routes>
  );
}

export default App;
