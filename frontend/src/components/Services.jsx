import { services } from '../data/siteData'

function Services() {
  return (
    <section
      className="row services-section py-5 w-100"
      id="services"
    >
      <div className="col-12">

        <div className="services-header mb-5">
          <h2 className="services-title-nepali">
            इन्भेष्टमेन्ट प्रा. लि. का सेवाहरु
          </h2>

          <h2 className="services-title-english">
            SERVICES OF INVESTMENT
          </h2>
        </div>

        <div className="row g-4">
          {services.map((service) => (
            <div
              key={service.title}
              className="col-lg-3 col-md-6 col-sm-12"
            >
              <article className="service-card h-100">

                <div className="service-icon">
                  <img
                    src={service.image}
                    alt={service.title}
                    className="service-image"
                  />
                </div>

                <h3 className="service-title">
                  {service.title}
                </h3>

                <p className="service-description">
                  {service.description}
                </p>

              </article>
            </div>
          ))}
        </div>

      </div>
    </section>
  )
}

export default Services