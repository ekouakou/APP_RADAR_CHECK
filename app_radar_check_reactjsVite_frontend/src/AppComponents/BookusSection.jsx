import React from "react";

const BookusSection = () => {
  return (
    <section className="bookus-section bg-dark">
      <div className="container">
        <div className="row align-items-center row-gap-4">
          <div className="col-lg-6">
            <div className="bookus-img">
              <div className="row g-3">
                <div
                  className="col-md-12 aos aos-init aos-animate"
                  data-aos="fade-up"
                >
                  <img
                    src="assets/img/book-01.jpg"
                    alt="img"
                    className="img-fluid"
                  />
                </div>
                <div
                  className="col-sm-6 aos aos-init aos-animate"
                  data-aos="fade-up"
                >
                  <img
                    src="assets/img/book-02.jpg"
                    alt="img"
                    className="img-fluid"
                  />
                </div>
                <div
                  className="col-sm-6 aos aos-init aos-animate"
                  data-aos="fade-up"
                >
                  <img
                    src="assets/img/book-03.jpg"
                    alt="img"
                    className="img-fluid"
                  />
                </div>
              </div>
            </div>
          </div>
          <div className="col-lg-6">
            <div
              className="section-header sec-header-one mb-2 aos aos-init aos-animate"
              data-aos="fade-up"
            >
              <span className="badge badge-primary">Why Book With Us</span>
              <h2 className="text-white mb-3">
                We are committed to understanding your{" "}
                <span className="text-primary-gradient">
                  unique needs and delivering care.
                </span>
              </h2>
            </div>
            <p className="text-light mb-4">
              As a trusted healthAs a trusted healthcare provider in our
              community, we are passionate about promoting health and wellness
              beyond the clinic. We actively engage in community outreach
              programs, health fairs, and educational workshop.
            </p>
            <div
              className="faq-info aos aos-init aos-animate"
              data-aos="fade-up"
            >
              <div className="accordion" id="faq-details">
                {/* FAQ Item */}
                <div className="accordion-item">
                  <h2 className="accordion-header" id="headingOne">
                    <a
                      href="javascript:void(0);"
                      className="accordion-button"
                      data-bs-toggle="collapse"
                      data-bs-target="#collapseOne"
                      aria-expanded="true"
                      aria-controls="collapseOne"
                    >
                      01 . Our Vision
                    </a>
                  </h2>
                  <div
                    id="collapseOne"
                    className="accordion-collapse collapse show"
                    aria-labelledby="headingOne"
                    data-bs-parent="#faq-details"
                  >
                    <div className="accordion-body">
                      <div className="accordion-content">
                        <p>
                          We envision a community where everyone has access to
                          high-quality healthcare and the resources they need to
                          lead healthy, fulfilling lives.
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
                {/* /FAQ Item */}
                {/* FAQ Item */}
                <div className="accordion-item">
                  <h2 className="accordion-header" id="headingTwo">
                    <a
                      href="javascript:void(0);"
                      className="accordion-button collapsed"
                      data-bs-toggle="collapse"
                      data-bs-target="#collapseTwo"
                      aria-controls="collapseTwo"
                    >
                      02 . Our Mission
                    </a>
                  </h2>
                  <div
                    id="collapseTwo"
                    className="accordion-collapse collapse"
                    aria-labelledby="headingTwo"
                    data-bs-parent="#faq-details"
                  >
                    <div className="accordion-body">
                      <div className="accordion-content">
                        <p>
                          We envision a community where everyone has access to
                          high-quality healthcare and the resources they need to
                          lead healthy, fulfilling lives.
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
                {/* /FAQ Item */}
              </div>
            </div>
          </div>
        </div>
        <div className="bookus-sec">
          <div className="row g-4">
            <div className="col-lg-3">
              <div className="book-item">
                <div className="book-icon bg-primary">
                  <i className="isax isax-search-normal5" />
                </div>
                <div className="book-info">
                  <h6 className="text-white mb-2">Search For Doctors</h6>
                  <p className="fs-14 text-light">
                    Search for a doctor based on specialization, location, or
                    availability for your Treatements
                  </p>
                </div>
                <div className="way-icon">
                  <img src="assets/img/icons/way-icon.svg" alt="img" />
                </div>
              </div>
            </div>
            <div className="col-lg-3">
              <div className="book-item">
                <div className="book-icon bg-orange">
                  <i className="isax isax-security-user5" />
                </div>
                <div className="book-info">
                  <h6 className="text-white mb-2">Check Doctor Profile</h6>
                  <p className="fs-14 text-light">
                    Explore detailed doctor profiles on our platform to make
                    informed healthcare decisions.
                  </p>
                </div>
                <div className="way-icon">
                  <img src="assets/img/icons/way-icon.svg" alt="img" />
                </div>
              </div>
            </div>
            <div className="col-lg-3">
              <div className="book-item">
                <div className="book-icon bg-cyan">
                  <i className="isax isax-calendar5" />
                </div>
                <div className="book-info">
                  <h6 className="text-white mb-2">Schedule Appointment</h6>
                  <p className="fs-14 text-light">
                    After choose your preferred doctor, select a convenient time
                    slot, &amp; confirm your appointment.
                  </p>
                </div>
                <div className="way-icon">
                  <img src="assets/img/icons/way-icon.svg" alt="img" />
                </div>
              </div>
            </div>
            <div className="col-lg-3">
              <div className="book-item">
                <div className="book-icon bg-indigo">
                  <i className="isax isax-blend5" />
                </div>
                <div className="book-info">
                  <h6 className="text-white mb-2">Get Your Solution</h6>
                  <p className="fs-14 text-light">
                    Discuss your health concerns with the doctor and receive the
                    personalized advice &amp; with solution.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default BookusSection;
