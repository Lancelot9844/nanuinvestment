import { useEffect, useState } from 'react'
import './App.css'

const fallbackSlides = [
  { title: 'Trusted Financial Growth', image: '/static/banner1.png' },
  { title: 'Member First Approach', image: '/static/banner2.png' },
  { title: 'Reliable Partnership', image: '/static/banner3.png' },
  { title: 'Community Financial Support', image: '/static/banner4.png' },
  { title: 'Secure Savings Services', image: '/static/banner5.png' },
  { title: 'Growing Together', image: '/static/banner6.png' },
]

const services = [
  {
    title: 'बचत सेवा (Saving Services)',
    description: 'विभिन्न प्रकारका बचत योजनाहरुमा सुरक्षित बचत गर्ने सुविधा ।',
    image: '/static/Saving Services1.png',
  },
  {
    title: 'मुद्रती निक्षेप (Fixed Deposit)',
    description: 'आकर्षक ब्याजदरमा निश्चित अवधिका लागि निक्षेप राख्ने सुविधा ।',
    image: '/static/fixed deposit2.png',
  },
  {
    title: 'कर्जा सेवा (Loan Services)',
    description: 'व्यवसाय, शिक्षा, घर, उपभोग लगायतका आवश्यकताका लागि कर्जा सुविधा ।',
    image: '/static/loan services3.png',
  },
  {
    title: 'समूह बचत (Group Saving)',
    description: 'समूहमा आबद्ध भई संयुक्त रुपमा बचत गर्ने सुविधा तथा प्रोत्साहन ।',
    image: '/static/group serivces4.png',
  },
]

const fallbackContent = {
  banners: fallbackSlides,
  news: [
    {
      title: 'Latest cooperative updates will appear here',
      description: 'Add news and activity posts from Django admin to show them on the homepage.',
      published_at: 'Latest',
    },
  ],
  notices: [
    {
      title: 'Member notices will appear here',
      description: 'Add active notices from Django admin with optional documents.',
      published_at: 'Notice',
    },
  ],
  downloads: [
    {
      title: 'Download documents will appear here',
      description: 'Upload forms, policies, reports, or other files from Django admin.',
      published_at: 'Download',
    },
  ],
  popup: null,
}

function normalizeSiteContent(content) {
  return {
    banners: content.banners?.length ? content.banners : fallbackContent.banners,
    news: content.news?.length ? content.news : fallbackContent.news,
    notices: content.notices?.length ? content.notices : fallbackContent.notices,
    downloads: content.downloads?.length ? content.downloads : fallbackContent.downloads,
    popup: content.popup || null,
  }
}

function readSiteContent() {
  const node = document.getElementById('site-content')
  if (!node?.textContent) {
    return fallbackContent
  }

  try {
    return normalizeSiteContent(JSON.parse(node.textContent))
  } catch {
    return fallbackContent
  }
}

function ContentCard({ item, actionLabel }) {
  return (
    <article className="content-card">
      <span className="content-date">{item.published_at}</span>
      {item.image_url && <img src={item.image_url} alt={item.title} className="content-image" />}
      <h3>{item.title}</h3>
      {item.description && <p>{item.description}</p>}
      {item.document_url && (
        <a className="content-link" href={item.document_url} target="_blank" rel="noreferrer">
          {actionLabel}
        </a>
      )}
    </article>
  )
}

function PopupMedia({ popup }) {
  const [pdfPreviewUrl, setPdfPreviewUrl] = useState('')
  const [pdfPreviewFailed, setPdfPreviewFailed] = useState(false)

  useEffect(() => {
    if (popup.file_type !== 'pdf' || !popup.pdf_url) {
      return undefined
    }

    let ignore = false
    let objectUrl = ''

    async function loadPdfPreview() {
      try {
        const response = await fetch(popup.pdf_url)
        if (!response.ok) {
          throw new Error('PDF preview failed')
        }

        const blob = await response.blob()
        objectUrl = URL.createObjectURL(new Blob([blob], { type: 'application/pdf' }))
        if (!ignore) {
          setPdfPreviewUrl(objectUrl)
          setPdfPreviewFailed(false)
        }
      } catch {
        if (!ignore) {
          setPdfPreviewFailed(true)
        }
      }
    }

    loadPdfPreview()

    return () => {
      ignore = true
      if (objectUrl) {
        URL.revokeObjectURL(objectUrl)
      }
    }
  }, [popup.file_type, popup.pdf_url])

  if (popup.file_type === 'image' && popup.image_url) {
    return <img src={popup.image_url} alt={popup.title} className="website-popup-media website-popup-image" />
  }

  if (popup.file_type === 'pdf' && popup.pdf_url) {
    return (
      <div className="website-popup-media website-popup-pdf">
        {pdfPreviewUrl && !pdfPreviewFailed ? (
          <iframe src={pdfPreviewUrl} title={popup.title} />
        ) : (
          <div className="website-popup-pdf-fallback">
            <strong>{popup.file_name || 'PDF notice'}</strong>
            <a href={popup.pdf_url} target="_blank" rel="noreferrer">
              Open PDF
            </a>
          </div>
        )}
      </div>
    )
  }

  if (popup.document_url) {
    return (
      <div className="website-popup-media website-popup-document">
        <strong>{popup.file_name || 'Uploaded file'}</strong>
        <a href={popup.document_url} target="_blank" rel="noreferrer">
          Open uploaded file
        </a>
      </div>
    )
  }

  return null
}

function App() {
  const [activeSlide, setActiveSlide] = useState(0)
  const [siteContent, setSiteContent] = useState(readSiteContent)
  const slides = siteContent.banners
  const [showPopup, setShowPopup] = useState(Boolean(siteContent.popup))
  const [isMenuOpen, setIsMenuOpen] = useState(false)
  const [dragStartX, setDragStartX] = useState(null)
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    phone: '',
    message: '',
  })
  const [formStatus, setFormStatus] = useState('')

  useEffect(() => {
    let ignore = false

    async function loadSiteContent() {
      try {
        const response = await fetch('/api/site-content/')
        if (!response.ok) {
          return
        }

        const nextContent = normalizeSiteContent(await response.json())
        if (!ignore) {
          setSiteContent(nextContent)
          setShowPopup(Boolean(nextContent.popup))
        }
      } catch {
        // The Django-rendered page already has embedded content, so a failed dev fetch can be ignored.
      }
    }

    loadSiteContent()

    return () => {
      ignore = true
    }
  }, [])

  useEffect(() => {
    const timer = window.setInterval(() => {
      setActiveSlide((current) => (current + 1) % slides.length)
    }, 4000)

    const schema = {
      '@context': 'https://schema.org',
      '@type': 'LocalBusiness',
      name: 'Nanu Investment',
      description: 'Saving and Credit Co-operative Society Ltd.',
      address: {
        '@type': 'PostalAddress',
        streetAddress: 'Barahathawa-12',
        addressLocality: 'Sarlahi',
        addressRegion: 'Sarlahi',
        addressCountry: 'NP',
      },
      telephone: '+977-9744360267',
      email: 'info@nanuinvestment.com',
      image: 'https://nanuinvestment.com/static/logo.jpeg',
      url: 'https://nanuinvestment.com',
      areaServed: 'NP',
    }

    const script = document.createElement('script')
    script.type = 'application/ld+json'
    script.text = JSON.stringify(schema)
    document.head.appendChild(script)

    return () => {
      window.clearInterval(timer)
      document.head.removeChild(script)
    }
  }, [slides.length])

  const handleFormChange = (e) => {
    const { name, value } = e.target
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }))
  }

  const handleFormSubmit = async (e) => {
    e.preventDefault()
    setFormStatus('Sending...')

    try {
      const response = await fetch('https://api.web3forms.com/submit', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          access_key: '03f4e679-af8a-4138-967e-5a5ec32dde40',
          subject: 'New Contact Inquiry from Nanu Investment',
          name: formData.name,
          email: formData.email,
          phone: formData.phone,
          message: formData.message,
        }),
      })

      const data = await response.json()

      if (data.success) {
        setFormStatus('Message sent successfully.')
        setFormData({ name: '', email: '', phone: '', message: '' })
        setTimeout(() => setFormStatus(''), 3000)
      } else {
        setFormStatus('Error sending message. Please try again.')
      }
    } catch {
      setFormStatus('Error sending message. Please try again.')
    }
  }

  const closeMenu = () => {
    setIsMenuOpen(false)
  }

  const showPreviousSlide = () => {
    setActiveSlide((current) => (current - 1 + slides.length) % slides.length)
  }

  const showNextSlide = () => {
    setActiveSlide((current) => (current + 1) % slides.length)
  }

  const handleSlideStart = (clientX) => {
    setDragStartX(clientX)
  }

  const handleSlideEnd = (clientX) => {
    if (dragStartX === null) {
      return
    }

    const distance = clientX - dragStartX
    const minimumSwipeDistance = 50

    if (Math.abs(distance) >= minimumSwipeDistance) {
      if (distance > 0) {
        showPreviousSlide()
      } else {
        showNextSlide()
      }
    }

    setDragStartX(null)
  }

  const closePopup = () => {
    setShowPopup(false)
  }

  return (
    <div className="app-shell">
      {showPopup && siteContent.popup && (
        <div
          className="website-popup-backdrop"
          role="dialog"
          aria-modal="true"
          aria-labelledby="website-popup-title"
          onClick={closePopup}
        >
          <article className="website-popup" onClick={(event) => event.stopPropagation()}>
            <button type="button" className="website-popup-close" onClick={closePopup} aria-label="Close popup">
              &times;
            </button>
            <PopupMedia popup={siteContent.popup} />
            <div className="website-popup-content">
              <h2 id="website-popup-title">{siteContent.popup.title}</h2>
            </div>
          </article>
        </div>
      )}
      <header className="top-bar" id="home">
        <div className="container-fluid">
          <div className="row align-items-center justify-content-center">
            <div className="col-12 text-center mb-3 mb-md-0">
              <div className="logo-area">
                <img src="/static/logo.jpeg" alt="Nanu Investment logo" className="brand-logo" />
              </div>
            </div>
            <div className="col-12">
              <div className="contact-info">
                <div className="contact-item">
                  <strong>✆ +977 9744360267</strong>
                </div>
                <div className="contact-item">
                  <strong>📌 Barahathawa-12, Sarlahi, Nepal</strong>
                </div>
              </div>
            </div>
          </div>
        </div>
      </header>

      <nav className="navbar navbar-expand-lg navbar-dark navbar-custom sticky-top">
        <div className="container-fluid">
          <a className="navbar-brand" href="#home">NANU INVESTMENT</a>
          <button
            className="navbar-toggler"
            type="button"
            aria-controls="navbarNav"
            aria-expanded={isMenuOpen}
            aria-label="Toggle navigation"
            onClick={() => setIsMenuOpen((current) => !current)}
          >
            <span className="navbar-toggler-icon"></span>
          </button>
          <div className={`collapse navbar-collapse${isMenuOpen ? ' show' : ''}`} id="navbarNav">
            <ul className="navbar-nav ms-auto">
              <li className="nav-item"><a className="nav-link" href="#home" onClick={closeMenu}>HOME</a></li>
              <li className="nav-item"><a className="nav-link" href="#about" onClick={closeMenu}>ABOUT US</a></li>
              <li className="nav-item"><a className="nav-link" href="#services" onClick={closeMenu}>SERVICES</a></li>
              <li className="nav-item"><a className="nav-link" href="#news" onClick={closeMenu}>NEWS & ACTIVITIES</a></li>
              <li className="nav-item"><a className="nav-link" href="#notices" onClick={closeMenu}>NOTICE</a></li>
              <li className="nav-item"><a className="nav-link" href="#downloads" onClick={closeMenu}>DOWNLOADS</a></li>
              <li className="nav-item"><a className="nav-link" href="#contact" onClick={closeMenu}>CONTACT US</a></li>
              <li className="nav-item">
                <a className="nav-link login-link" href="/login/" aria-label="Login" data-tooltip="Login" onClick={closeMenu}>
                  <svg className="login-icon" viewBox="0 0 24 24" aria-hidden="true">
                    <path d="M20 21a8 8 0 0 0-16 0" />
                    <circle cx="12" cy="7" r="4" />
                  </svg>
                </a>
              </li>
            </ul>
          </div>
        </div>
      </nav>

      <div className="accent-line" />

      <section className="slider-container" aria-label="Nanu Investment highlights">
        <div
          className="slides"
          onMouseDown={(event) => handleSlideStart(event.clientX)}
          onMouseUp={(event) => handleSlideEnd(event.clientX)}
          onMouseLeave={() => setDragStartX(null)}
          onTouchStart={(event) => handleSlideStart(event.touches[0].clientX)}
          onTouchEnd={(event) => handleSlideEnd(event.changedTouches[0].clientX)}
        >
          <div className="slide active">
            <img src={slides[activeSlide].image} alt={slides[activeSlide].title} className="img-fluid w-100" />
          </div>
        </div>
        <div className="slider-dots">
          {slides.map((slide, index) => (
            <button
              key={slide.title}
              className={index === activeSlide ? 'dot active' : 'dot'}
              onClick={() => setActiveSlide(index)}
              aria-label={`Show ${slide.title}`}
              type="button"
            />
          ))}
        </div>
      </section>

      <main className="main-container">
        <section className="row welcome-section py-5" id="about">
          <div className="col-12">
            <h1 className="welcome-title">Welcome To Our Co-operative</h1>
            <p className="subtitle">"सहकारीको विकास सँगै सामाजिक बिकासमा समर्पित" <br /> Since 2025</p>
            <p className="welcome-text">
              Respecting the true spirit of cooperative revolution, our Saving and Credit
              Co-operative Society Ltd. is established with the mission of serving members
              with trust, transparency, and dependable financial support.
            </p>
          </div>
        </section>

        <section className="row owner-section py-5" aria-label="Chairperson message">
          <div className="col-12">
            <div className="owner-container">
              <div className="row align-items-center">
                <div className="col-lg-4 col-md-5 col-sm-12 mb-4 mb-lg-0">
                  <div className="owner-photo-box">
                    <img src="/static/owner.png" alt="Chairman / Founder" className="owner-photo img-fluid rounded" />
                  </div>
                </div>
                <div className="col-lg-8 col-md-7 col-sm-12">
                  <div className="owner-info">
                    <h3>Mr. Krishna Ray</h3>
                    <p className="owner-title">Founder Chairman / President</p>
                    <p className="owner-message">
                      Our journey continues with a vision to uplift communities through mutual trust,
                      strong cooperation, and reliable financial support.
                    </p>
                    <div className="owner-details-grid">
                      <span><strong>Experience:</strong> 5+ Years in Co-operative Sector</span>
                      <span><strong>Email:</strong> ka1234yad@gmail.com</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        <section className="row services-section py-5 w-100" id="services">
          <div className="col-12">
            <div className="services-header mb-5">
              <h2 className="services-title-nepali">इन्भेष्टमेन्ट प्रा. लि. का सेवाहरु</h2>
              <h2 className="services-title-english">SERVICES OF INVESTMENT</h2>
            </div>
            <div className="row g-4">
              {services.map((service) => (
                <div key={service.title} className="col-lg-3 col-md-6 col-sm-12">
                  <article className="service-card h-100">
                    <div className="service-icon">
                      <img src={service.image} alt={service.title} className="service-image" />
                    </div>
                    <h3 className="service-title">{service.title}</h3>
                    <p className="service-description">{service.description}</p>
                  </article>
                </div>
              ))}
            </div>
          </div>
        </section>

        <section className="content-section" id="news">
          <div className="section-heading">
            <h2>News & Activities</h2>
          </div>
          <div className="content-grid">
            {siteContent.news.map((item) => (
              <ContentCard key={`${item.title}-${item.published_at}`} item={item} actionLabel="View document" />
            ))}
          </div>
        </section>

        <section className="content-section compact-section" id="notices">
          <div className="section-heading">
            <h2>Notice</h2>
          </div>
          <div className="content-grid">
            {siteContent.notices.map((item) => (
              <ContentCard key={`${item.title}-${item.published_at}`} item={item} actionLabel="Open notice" />
            ))}
          </div>
        </section>

        <section className="content-section compact-section" id="downloads">
          <div className="section-heading">
            <h2>Downloads</h2>
          </div>
          <div className="content-grid">
            {siteContent.downloads.map((item) => (
              <ContentCard key={`${item.title}-${item.published_at}`} item={item} actionLabel="Download" />
            ))}
          </div>
        </section>
      </main>

      <footer className="footer" id="contact">
        <div className="container-fluid">
          <div className="row footer-grid">
            <div className="col-lg-3 col-md-6 col-sm-12 mb-4">
              <h4>About Us</h4>
              <p>Our Saving and Credit Co-operative Society Ltd. has been operating with financial opportunities for its needy members and society.</p>
            </div>
            <div className="col-lg-3 col-md-6 col-sm-12 mb-4">
              <h4>Useful Links</h4>
              <ul className="list-unstyled footer-list">
                <li><a href="#home">Home</a></li>
                <li><a href="#about">About Us</a></li>
                <li><a href="#services">Services</a></li>
                <li><a href="#news">News & Activities</a></li>
                <li><a href="#notices">Notice</a></li>
                <li><a href="#downloads">Downloads</a></li>
              </ul>
            </div>
            <div className="col-lg-3 col-md-6 col-sm-12 mb-4">
              <h4>Contact Us</h4>
              <ul className="list-unstyled footer-list">
                <li>📌 Barahathawa-12, Sarlahi, Nepal</li>
                <li>✆ +977 9744360267</li>
                <li>✉ info@nanuinvestment.com</li>
              </ul>
            </div>
            <div className="col-lg-3 col-md-6 col-sm-12">
              <h4>Send Us a Message</h4>
              <form onSubmit={handleFormSubmit} className="contact-form">
                <input type="text" className="form-control" name="name" placeholder="Your name" value={formData.name} onChange={handleFormChange} required />
                <input type="email" className="form-control" name="email" placeholder="Your email" value={formData.email} onChange={handleFormChange} required />
                <input type="tel" className="form-control" name="phone" placeholder="Your phone number" value={formData.phone} onChange={handleFormChange} required />
                <textarea className="form-control" name="message" rows="4" placeholder="Your message" value={formData.message} onChange={handleFormChange} required />
                <button type="submit" className="btn btn-custom w-100">Send Message</button>
                {formStatus && (
                  <p className="form-message mt-2 text-center fw-bold" aria-live="polite">
                    {formStatus}
                  </p>
                )}
              </form>
            </div>
          </div>
          <div className="footer-bottom text-center">
            &copy; 2026 Copyright NanuInvestment Pvt. Ltd. All Rights Reserved.
          </div>
        </div>
      </footer>
    </div>
  )
}

export default App
