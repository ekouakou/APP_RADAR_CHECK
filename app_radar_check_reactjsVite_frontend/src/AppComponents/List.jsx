import React from "react";

const List = () => {
  return (
    <div className="list-section">
  <div className="container">
    <div className="list-card card mb-0">
      <div className="card-body">
        <div className="d-flex align-items-center justify-content-center justify-content-xl-between flex-wrap gap-4 list-wraps">
          <a href="booking.html" className="list-item aos" data-aos="fade-up">
            <div className="list-icon bg-secondary">
              <img src="assets/img/icons/list-icon-01.svg" alt="img" />
            </div>
            <h6>Book Appointment</h6>
          </a>
          <a
            href="doctor-grid.html"
            className="list-item aos"
            data-aos="fade-up"
          >
            <div className="list-icon bg-primary">
              <img src="assets/img/icons/list-icon-02.svg" alt="img" />
            </div>
            <h6>Talk to Doctors</h6>
          </a>
          <a href="hospitals.html" className="list-item aos" data-aos="fade-up">
            <div className="list-icon bg-pink">
              <img src="assets/img/icons/list-icon-03.svg" alt="img" />
            </div>
            <h6>Hospitals &amp; Clinics</h6>
          </a>
          <a href="index-3.html" className="list-item aos" data-aos="fade-up">
            <div className="list-icon bg-cyan">
              <img src="assets/img/icons/list-icon-04.svg" alt="img" />
            </div>
            <h6>Healthcare</h6>
          </a>
          <a href="index-13.html" className="list-item aos" data-aos="fade-up">
            <div className="list-icon bg-purple">
              <img src="assets/img/icons/list-icon-05.svg" alt="img" />
            </div>
            <h6>Medicine &amp; Supplies</h6>
          </a>
          <a href="index-12.html" className="list-item aos" data-aos="fade-up">
            <div className="list-icon bg-orange">
              <img src="assets/img/icons/list-icon-06.svg" alt="img" />
            </div>
            <h6>Lab Testing</h6>
          </a>
          <a href="index-13.html" className="list-item aos" data-aos="fade-up">
            <div className="list-icon bg-teal">
              <img src="assets/img/icons/list-icon-07.svg" alt="img" />
            </div>
            <h6>Home Care</h6>
          </a>
        </div>
      </div>
    </div>
  </div>
</div>

  );
};

export default List;
