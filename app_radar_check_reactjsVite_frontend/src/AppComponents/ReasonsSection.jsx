import React from "react";

const ReasonsSection = () => {
  return (
    <section className="reason-section">
  <div className="container">
    <div
      className="section-header sec-header-one text-center aos aos-init aos-animate"
      data-aos="fade-up"
    >
      <span className="badge badge-primary">Why Book With Us</span>
      <h2>Compelling Reasons to Choose</h2>
    </div>
    <div className="row row-gap-4 justify-content-center">
      <div className="col-lg-4 col-md-6">
        <div
          className="reason-item aos aos-init aos-animate"
          data-aos="fade-up"
        >
          <h6 className="mb-2">
            <i className="isax isax-tag-user5 text-orange me-2" />
            Follow-Up Care
          </h6>
          <p className="fs-14 mb-0">
            We ensure continuity of care through regular follow-ups and
            communication, helping you stay on track with health goals.
          </p>
        </div>
      </div>
      <div className="col-lg-4 col-md-6">
        <div
          className="reason-item aos aos-init aos-animate"
          data-aos="fade-up"
        >
          <h6 className="mb-2">
            <i className="isax isax-voice-cricle text-purple me-2" />
            Patient-Centered Approach
          </h6>
          <p className="fs-14 mb-0">
            We prioritize your comfort and preferences, tailoring our services
            to meet your individual needs and Care from Our Experts
          </p>
        </div>
      </div>
      <div className="col-lg-4 col-md-6">
        <div
          className="reason-item aos aos-init aos-animate"
          data-aos="fade-up"
        >
          <h6 className="mb-2">
            <i className="isax isax-wallet-add-15 text-cyan me-2" />
            Convenient Access
          </h6>
          <p className="fs-14 mb-0">
            Easily book appointments online or through our dedicated customer
            service team, with flexible hours to fit your schedule.
          </p>
        </div>
      </div>
    </div>
  </div>
</section>

  );
};

export default ReasonsSection;
