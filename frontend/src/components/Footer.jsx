import ContactForm from './ContactForm'

function Footer() {
  return (
    <footer className="footer" id="contact">

      <div className="container-fluid">

        <div className="row footer-grid">

          {/* About */}
          <div className="col-lg-3 col-md-6 col-sm-12 mb-4">

            <h4>About Us</h4>

            <p>
              Our Saving and Credit Co-operative Society Ltd.
              has been operating with financial opportunities
              for its needy members and society.
            </p>

          </div>

          {/* Useful Links */}
          <div className="col-lg-3 col-md-6 col-sm-12 mb-4">

            <h4>Useful Links</h4>

            <ul className="list-unstyled footer-list">

              <li>
                <a href="#home">Home</a>
              </li>

              <li>
                <a href="#about">About Us</a>
              </li>

              <li>
                <a href="#services">Services</a>
              </li>

              <li>
                <a href="#news">
                  News & Activities
                </a>
              </li>

              <li>
                <a href="#notices">Notice</a>
              </li>

              <li>
                <a href="#downloads">Downloads</a>
              </li>

            </ul>

          </div>

          {/* Contact */}
          <div className="col-lg-3 col-md-6 col-sm-12 mb-4">

            <h4>Contact Us</h4>

            <ul className="list-unstyled footer-list">

              <li>
                📌 Barahathawa-12, Sarlahi, Nepal
              </li>

              <li>
                ✆ +977 9744360267
              </li>

              <li>
                ✉ info@nanuinvestment.com
              </li>

            </ul>

          </div>

          {/* Contact Form */}
          <div className="col-lg-3 col-md-6 col-sm-12">

            <h4>Send Us a Message</h4>

            <ContactForm />

          </div>

        </div>

        <div className="footer-bottom text-center">
          &copy; 2026 Copyright NanuInvestment Pvt. Ltd.
          All Rights Reserved.
        </div>

      </div>

    </footer>
  )
}

export default Footer