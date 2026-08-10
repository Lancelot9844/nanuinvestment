import { useEffect, useState } from 'react'
import './App.css'

import Navbar from './components/Navbar.jsx'
import Slider from './components/Slider.jsx'
import About from './components/About.jsx'
import Chairman from './components/Chairman.jsx'
import Services from './components/Services.jsx'
import ContentSection from './components/ContentSection.jsx'
import Popup from './components/Popup.jsx'
import Footer from './components/Footer.jsx'

import { readSiteContent } from './utils/siteContent.js'
import { fetchSiteContent } from './services/siteContentService.js'
import { addSeoSchema } from './utils/seoSchema.js'

function App() {
  const [siteContent, setSiteContent] = useState(readSiteContent)

  const [showPopup, setShowPopup] = useState(
    Boolean(siteContent.popup)
  )

  // Load dynamic Django content
  useEffect(() => {
    let ignore = false

    async function loadContent() {
      try {
        const nextContent = await fetchSiteContent()

        if (!ignore) {
          setSiteContent(nextContent)
          setShowPopup(Boolean(nextContent.popup))
        }
      } catch (error) {
        console.error('Failed to load site content:', error)
      }
    }

    loadContent()

    return () => {
      ignore = true
    }
  }, [])

  // SEO Schema
  useEffect(() => {
    return addSeoSchema()
  }, [])

  const closePopup = () => {
    setShowPopup(false)
  }

  return (
    <div className="app-shell">

      {/* Popup */}
      {showPopup && siteContent.popup && (
        <Popup
          popup={siteContent.popup}
          onClose={closePopup}
        />
      )}

      {/* Navigation */}
      <Navbar />

      {/* Hero Slider */}
      <Slider
        slides={siteContent.banners}
      />

      {/* Main Content */}
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

      {/* Footer */}
      <Footer />

    </div>
  )
}

export default App