function Chairman() {
  return (
    <section
      className="row owner-section py-5"
      aria-label="Chairperson message"
    >
      <div className="col-12">
        <div className="owner-container">
          <div className="row align-items-center">
            <div className="col-lg-4 col-md-5 col-sm-12 mb-4 mb-lg-0">
              <div className="owner-photo-box">
                <img
                  src="/static/owner.png"
                  alt="Chairman / Founder"
                  className="owner-photo img-fluid rounded"
                />
              </div>
            </div>

            <div className="col-lg-8 col-md-7 col-sm-12">
              <div className="owner-info">
                <h3>Mr. Krishna Ray</h3>

                <p className="owner-title">Founder Chairman / President</p>

                <p className="owner-message">
                  Our journey continues with a vision to uplift communities
                  through mutual trust, strong cooperation, and reliable
                  financial support.
                </p>

                <div className="owner-details-grid">
                  <span>
                    <strong>Experience:</strong> 5+ Years in Co-operative Sector
                  </span>

                  <span>
                    <strong>Email:</strong> ka1234yad@gmail.com
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

export default Chairman;
