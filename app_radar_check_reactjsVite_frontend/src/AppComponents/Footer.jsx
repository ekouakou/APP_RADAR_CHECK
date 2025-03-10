import React from "react";

const Footer = () => {
  return (
    <footer className="footer inner-footer">
  <div className="footer-top">
    <div className="container">
      <div className="row">
        <div className="col-lg-8">
          <div className="row">
            <div className="col-lg-3 col-md-3">
              <div className="footer-widget footer-menu">
                <h6 className="footer-title">Company</h6>
                <ul>
                  <li>
                    <a href="about-us.html">About</a>
                  </li>
                  <li>
                    <a href="search.html">Features</a>
                  </li>
                  <li>
                    <a href="javascript:void(0);">Works</a>
                  </li>
                  <li>
                    <a href="javascript:void(0);">Careers</a>
                  </li>
                  <li>
                    <a href="javascript:void(0);">Locations</a>
                  </li>
                </ul>
              </div>
            </div>
            <div className="col-lg-3 col-md-3">
              <div className="footer-widget footer-menu">
                <h6 className="footer-title">Treatments</h6>
                <ul>
                  <li>
                    <a href="search.html">Dental</a>
                  </li>
                  <li>
                    <a href="search.html">Cardiac</a>
                  </li>
                  <li>
                    <a href="search.html">Spinal Cord</a>
                  </li>
                  <li>
                    <a href="search.html">Hair Growth</a>
                  </li>
                  <li>
                    <a href="search.html">Anemia &amp; Disorder</a>
                  </li>
                </ul>
              </div>
            </div>
            <div className="col-lg-3 col-md-3">
              <div className="footer-widget footer-menu">
                <h6 className="footer-title">Specialities</h6>
                <ul>
                  <li>
                    <a href="search.html">Transplant</a>
                  </li>
                  <li>
                    <a href="search.html">Cardiologist</a>
                  </li>
                  <li>
                    <a href="search.html">Oncology</a>
                  </li>
                  <li>
                    <a href="search.html">Pediatrics</a>
                  </li>
                  <li>
                    <a href="search.html">Gynacology</a>
                  </li>
                </ul>
              </div>
            </div>
            <div className="col-lg-3 col-md-3">
              <div className="footer-widget footer-menu">
                <h6 className="footer-title">Utilites</h6>
                <ul>
                  <li>
                    <a href="pricing.html">Pricing</a>
                  </li>
                  <li>
                    <a href="contact-us.html">Contact</a>
                  </li>
                  <li>
                    <a href="contact-us.html">Request A Quote</a>
                  </li>
                  <li>
                    <a href="javascript:void(0);">Premium Membership</a>
                  </li>
                  <li>
                    <a href="javascript:void(0);">Integrations</a>
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </div>
        <div className="col-lg-4 col-md-7">
          <div className="footer-widget">
            <h6 className="footer-title">Newsletter</h6>
            <p className="mb-2">
              Subscribe &amp; Stay Updated from the Doccure
            </p>
            <div className="subscribe-input">
              <form action="#">
                <input
                  type="email"
                  className="form-control"
                  placeholder="Enter Email Address"
                />
                <button
                  type="submit"
                  className="btn btn-md btn-primary-gradient d-inline-flex align-items-center"
                >
                  <i className="isax isax-send-25 me-1" />
                  Send
                </button>
              </form>
            </div>
            <div className="social-icon">
              <h6 className="mb-3">Connect With Us</h6>
              <ul>
                <li>
                  <a href="javascript:void(0);">
                    <i className="fa-brands fa-facebook" />
                  </a>
                </li>
                <li>
                  <a href="javascript:void(0);">
                    <i className="fa-brands fa-x-twitter" />
                  </a>
                </li>
                <li>
                  <a href="javascript:void(0);">
                    <i className="fa-brands fa-instagram" />
                  </a>
                </li>
                <li>
                  <a href="javascript:void(0);">
                    <i className="fa-brands fa-linkedin" />
                  </a>
                </li>
                <li>
                  <a href="javascript:void(0);">
                    <i className="fa-brands fa-pinterest" />
                  </a>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
    <div className="footer-bg">
      <img
        src="assets/img/bg/footer-bg-01.png"
        alt="img"
        className="footer-bg-01"
      />
      <img
        src="assets/img/bg/footer-bg-02.png"
        alt="img"
        className="footer-bg-02"
      />
      <img
        src="assets/img/bg/footer-bg-03.png"
        alt="img"
        className="footer-bg-03"
      />
      <img
        src="assets/img/bg/footer-bg-04.png"
        alt="img"
        className="footer-bg-04"
      />
      <img
        src="assets/img/bg/footer-bg-05.png"
        alt="img"
        className="footer-bg-05"
      />
    </div>
  </div>
  <div className="footer-bottom">
    <div className="container">
      {/* Copyright */}
      <div className="copyright">
        <div className="copyright-text">
          <p className="mb-0">Copyright © 2025 Doccure. All Rights Reserved</p>
        </div>
        {/* Copyright Menu */}
        <div className="copyright-menu">
          <ul className="policy-menu">
            <li>
              <a href="javascript:void(0);">Legal Notice</a>
            </li>
            <li>
              <a href="privacy-policy.html">Privacy Policy</a>
            </li>
            <li>
              <a href="javascript:void(0);">Refund Policy</a>
            </li>
          </ul>
        </div>
        {/* /Copyright Menu */}
        <ul className="payment-method">
          <li>
            <a href="javascript:void(0);">
              <img src="assets/img/icons/card-01.svg" alt="Img" />
            </a>
          </li>
          <li>
            <a href="javascript:void(0);">
              <img src="assets/img/icons/card-02.svg" alt="Img" />
            </a>
          </li>
          <li>
            <a href="javascript:void(0);">
              <img src="assets/img/icons/card-03.svg" alt="Img" />
            </a>
          </li>
          <li>
            <a href="javascript:void(0);">
              <img src="assets/img/icons/card-04.svg" alt="Img" />
            </a>
          </li>
          <li>
            <a href="javascript:void(0);">
              <img src="assets/img/icons/card-05.svg" alt="Img" />
            </a>
          </li>
          <li>
            <a href="javascript:void(0);">
              <img src="assets/img/icons/card-06.svg" alt="Img" />
            </a>
          </li>
        </ul>
      </div>
      {/* /Copyright */}
    </div>
  </div>
</footer>

  );
};

export default Footer;
