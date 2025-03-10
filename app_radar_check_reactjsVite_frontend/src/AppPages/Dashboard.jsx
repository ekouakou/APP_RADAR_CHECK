

function Dashboard() {
  // const [count, setCount] = useState(0)

  return (
    <>
      <div className="app-body">
        {/* Row starts */}
        <div className="row gx-3">
          <div className="col-xxl-9 col-sm-12">
            <div className="card mb-3 bg-3">
              <div className="card-body">
                <div className="mh-230">
                  <div className="py-4 px-3 text-white">
                    <h6>Good Morning,</h6>
                    <h2>Dr. Smith White</h2>
                    <h5>Your schedule today.</h5>
                    <div className="mt-4 d-flex gap-3">
                      <div className="d-flex align-items-center">
                        <div className="icon-box lg bg-arctic rounded-2 me-3">
                          <i className="ri-surgical-mask-line fs-4" />
                        </div>
                        <div className="d-flex flex-column">
                          <h2 className="m-0 lh-1">9</h2>
                          <p className="m-0">Appointments</p>
                        </div>
                      </div>
                      <div className="d-flex align-items-center">
                        <div className="icon-box lg bg-lime rounded-2 me-3">
                          <i className="ri-lungs-line fs-4" />
                        </div>
                        <div className="d-flex flex-column">
                          <h2 className="m-0 lh-1">3</h2>
                          <p className="m-0">Surgeries</p>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div className="col-xxl-3 col-sm-12">
            <div className="card mb-3 bg-lime">
              <div className="card-body">
                <div className="mh-230 text-white">
                  <h5>Activity</h5>
                  <div className="text-body chart-height-md">
                    <div id="docActivity" />
                  </div>
                  <div className="text-center">
                    <span className="badge bg-danger">60%</span> patients are
                    higher
                    <br />
                    than last week.
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        {/* Row ends */}
        {/* Row starts */}
        <div className="row gx-3">
          <div className="col-xxl-6 col-sm-12">
            <div className="card mb-3">
              <div className="card-header">
                <h5 className="card-title">Available Doctors</h5>
              </div>
              <div className="card-body">
                <div
                  id="carouselAvailableDocs"
                  className="carousel slide carousel-fade"
                  data-bs-ride="carousel"
                >
                  <div className="carousel-inner">
                    <div
                      className="carousel-item active"
                      data-bs-interval={4000}
                    >
                      <div className="grid gap-2 p-1">
                        <div className="g-col-6">
                          <div className="border rounded-2 p-3 mh-100">
                            <div className="d-flex align-items-start">
                              <img
                                src="assets/images/user1.png"
                                className="img-4x rounded-5"
                                alt="Doctor Dashboard"
                              />
                              <div className="ms-3">
                                <h6 className="mb-1">Gilbert Sandoval</h6>
                                <p className="mb-1">Neurologist</p>
                                <div className="d-flex align-items-center">
                                  <div className="rating-stars-sm">
                                    <div className="readonly5" />
                                  </div>
                                  <span className="ms-1 lh-1">5</span>
                                </div>
                              </div>
                            </div>
                          </div>
                        </div>
                        <div className="g-col-6">
                          <div className="border rounded-2 p-3 mh-100">
                            <div className="d-flex align-items-start">
                              <img
                                src="assets/images/user2.png"
                                className="img-4x rounded-5"
                                alt="Doctor Dashboard"
                              />
                              <div className="ms-3">
                                <h6 className="mb-1">Gilbert Sandoval</h6>
                                <p className="mb-1">Radiologist</p>
                                <div className="d-flex align-items-center">
                                  <div className="rating-stars-sm">
                                    <div className="readonly4" />
                                  </div>
                                  <span className="ms-1 lh-1">4</span>
                                </div>
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                    <div className="carousel-item" data-bs-interval={4000}>
                      <div className="grid gap-2 p-1">
                        <div className="g-col-6">
                          <div className="border rounded-2 p-3 mh-100">
                            <div className="d-flex align-items-start">
                              <img
                                src="assets/images/user.png"
                                className="img-4x rounded-5"
                                alt="Doctor Dashboard"
                              />
                              <div className="ms-3">
                                <h6 className="mb-1">George Bailey</h6>
                                <p className="mb-1">Dentist</p>
                                <div className="d-flex align-items-center">
                                  <div className="rating-stars-sm">
                                    <div className="readonly4" />
                                  </div>
                                  <span className="ms-1 lh-1">4</span>
                                </div>
                              </div>
                            </div>
                          </div>
                        </div>
                        <div className="g-col-6">
                          <div className="border rounded-2 p-3 mh-100">
                            <div className="d-flex align-items-start">
                              <img
                                src="assets/images/user3.png"
                                className="img-4x rounded-5"
                                alt="Doctor Dashboard"
                              />
                              <div className="ms-3">
                                <h6 className="mb-1">Amelia Bruklin</h6>
                                <p className="mb-1">Therapist</p>
                                <div className="d-flex align-items-center">
                                  <div className="rating-stars-sm">
                                    <div className="readonly3" />
                                  </div>
                                  <span className="ms-1 lh-1">3.5</span>
                                </div>
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                    <div className="carousel-item" data-bs-interval={4000}>
                      <div className="grid gap-2 p-1">
                        <div className="g-col-6">
                          <div className="border rounded-2 p-3 mh-100">
                            <div className="d-flex align-items-start">
                              <img
                                src="assets/images/user4.png"
                                className="img-4x rounded-5"
                                alt="Doctor Dashboard"
                              />
                              <div className="ms-3">
                                <h6 className="mb-1">Bernardo James</h6>
                                <p className="mb-1">Pediatrics</p>
                                <div className="d-flex align-items-center">
                                  <div className="rating-stars-sm">
                                    <div className="readonly4" />
                                  </div>
                                  <span className="ms-1 lh-1">4</span>
                                </div>
                              </div>
                            </div>
                          </div>
                        </div>
                        <div className="g-col-6">
                          <div className="border rounded-2 p-3 mh-100">
                            <div className="d-flex align-items-start">
                              <img
                                src="assets/images/user5.png"
                                className="img-4x rounded-5"
                                alt="Doctor Dashboard"
                              />
                              <div className="ms-3">
                                <h6 className="mb-1">Bshton Cozei</h6>
                                <p className="mb-1">Gynecologist</p>
                                <div className="d-flex align-items-center">
                                  <div className="rating-stars-sm">
                                    <div className="readonly5" />
                                  </div>
                                  <span className="ms-1 lh-1">5</span>
                                </div>
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                  <div className="carousel-custom-btns">
                    <button
                      className="carousel-control-prev btn text-danger"
                      type="button"
                      data-bs-target="#carouselAvailableDocs"
                      data-bs-slide="prev"
                    >
                      <i className="ri-arrow-left-s-line fs-2 lh-1" />
                    </button>
                    <button
                      className="carousel-control-next btn text-danger"
                      type="button"
                      data-bs-target="#carouselAvailableDocs"
                      data-bs-slide="next"
                    >
                      <i className="ri-arrow-right-s-line fs-2 lh-1" />
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div className="col-xxl-6 col-sm-12">
            <div className="card mb-3">
              <div className="card-header">
                <h5 className="card-title">Upcoming Surgeries</h5>
              </div>
              <div className="card-body">
                <div
                  id="carouselSurgeries"
                  className="carousel slide carousel-fade"
                  data-bs-ride="carousel"
                >
                  <div className="carousel-inner">
                    <div
                      className="carousel-item active"
                      data-bs-interval={3000}
                    >
                      <div className="grid gap-2 p-1">
                        <div className="g-col-6">
                          <div className="border rounded-2 p-3 mh-100">
                            <div className="d-flex align-items-start">
                              <div className="icon-box lg rounded-3 bg-primary-subtle text-primary">
                                <div className="d-flex flex-column text-center">
                                  <p className="m-0">Thu</p>
                                  <h3 className="m-0">23</h3>
                                </div>
                              </div>
                              <div className="ms-3">
                                <h6 className="mb-1">Amelia Bruklin</h6>
                                <p className="mb-1">Neurologist</p>
                                <span className="badge bg-primary">
                                  2:30 PM
                                </span>
                              </div>
                            </div>
                          </div>
                        </div>
                        <div className="g-col-6">
                          <div className="border rounded-2 p-3 mh-100">
                            <div className="d-flex align-items-start">
                              <div className="icon-box lg rounded-3 bg-success-subtle text-success">
                                <div className="d-flex flex-column text-center">
                                  <p className="m-0">Sat</p>
                                  <h3 className="m-0">25</h3>
                                </div>
                              </div>
                              <div className="ms-3">
                                <h6 className="mb-1">Bshton Cozei</h6>
                                <p className="mb-1">Surgen</p>
                                <span className="badge bg-success">
                                  5:00 PM
                                </span>
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                    <div className="carousel-item" data-bs-interval={3000}>
                      <div className="grid gap-2 p-1">
                        <div className="g-col-6">
                          <div className="border rounded-2 p-3 mh-100">
                            <div className="d-flex align-items-start">
                              <div className="icon-box lg rounded-3 bg-danger-subtle text-danger">
                                <div className="d-flex flex-column text-center">
                                  <p className="m-0">Mon</p>
                                  <h3 className="m-0">27</h3>
                                </div>
                              </div>
                              <div className="ms-3">
                                <h6 className="mb-1">Smith White</h6>
                                <p className="mb-1">Oncologist</p>
                                <span className="badge bg-danger">
                                  10:30 AM
                                </span>
                              </div>
                            </div>
                          </div>
                        </div>
                        <div className="g-col-6">
                          <div className="border rounded-2 p-3 mh-100">
                            <div className="d-flex align-items-start">
                              <div className="icon-box lg rounded-3 bg-info-subtle text-info">
                                <div className="d-flex flex-column text-center">
                                  <p className="m-0">Tue</p>
                                  <h3 className="m-0">28</h3>
                                </div>
                              </div>
                              <div className="ms-3">
                                <h6 className="mb-1">Bernardo James</h6>
                                <p className="mb-1">Radiologist</p>
                                <span className="badge bg-info">3:30 PM</span>
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                    <div className="carousel-item" data-bs-interval={3000}>
                      <div className="grid gap-2 p-1">
                        <div className="g-col-6">
                          <div className="border rounded-2 p-3 mh-100">
                            <div className="d-flex align-items-start">
                              <div className="icon-box lg rounded-3 bg-warning-subtle text-warning">
                                <div className="d-flex flex-column text-center">
                                  <p className="m-0">Fri</p>
                                  <h3 className="m-0">29</h3>
                                </div>
                              </div>
                              <div className="ms-3">
                                <h6 className="mb-1">George Bailey</h6>
                                <p className="mb-1">Cardiologist</p>
                                <span className="badge bg-warning">
                                  6:30 AM
                                </span>
                              </div>
                            </div>
                          </div>
                        </div>
                        <div className="g-col-6">
                          <div className="border rounded-2 p-3 mh-100">
                            <div className="d-flex align-items-start">
                              <div className="icon-box lg rounded-3 bg-primary-subtle text-primary">
                                <div className="d-flex flex-column text-center">
                                  <p className="m-0">Sat</p>
                                  <h3 className="m-0">30</h3>
                                </div>
                              </div>
                              <div className="ms-3">
                                <h6 className="mb-1">Taylor Melon</h6>
                                <p className="mb-1">Gynecologist</p>
                                <span className="badge bg-primary">
                                  4:30 PM
                                </span>
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                  <div className="carousel-custom-btns">
                    <button
                      className="carousel-control-prev btn text-danger"
                      type="button"
                      data-bs-target="#carouselSurgeries"
                      data-bs-slide="prev"
                    >
                      <i className="ri-arrow-left-s-line fs-2 lh-1" />
                    </button>
                    <button
                      className="carousel-control-next btn text-danger"
                      type="button"
                      data-bs-target="#carouselSurgeries"
                      data-bs-slide="next"
                    >
                      <i className="ri-arrow-right-s-line fs-2 lh-1" />
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        {/* Row ends */}
        {/* Row starts */}
        <div className="row gx-3">
          <div className="col-sm-12">
            <div className="card mb-3">
              <div className="card-header">
                <h5 className="card-title">Appointments</h5>
              </div>
              <div className="card-body">
                {/* Table starts */}
                <div className="table-outer">
                  <div className="table-responsive">
                    <table className="table m-0 align-middle">
                      <thead>
                        <tr>
                          <th>#</th>
                          <th>Patient Name</th>
                          <th>Age</th>
                          <th>Consulting Doctor</th>
                          <th>Department</th>
                          <th>Date</th>
                          <th>Time</th>
                          <th>Disease</th>
                          <th>Actions</th>
                        </tr>
                      </thead>
                      <tbody>
                        <tr>
                          <td>001</td>
                          <td>Deena Cooley</td>
                          <td>65</td>
                          <td>
                            <img
                              src="assets/images/user.png"
                              className="img-shadow img-2x rounded-5 me-1"
                              alt="Hospital Admin Template"
                            />
                            Vicki Walsh
                          </td>
                          <td>Surgeon</td>
                          <td>05/23/2024</td>
                          <td>9:30AM</td>
                          <td>Diabeties</td>
                          <td>
                            <div className="d-inline-flex gap-1">
                              <button
                                className="btn btn-success btn-sm"
                                data-bs-toggle="tooltip"
                                data-bs-placement="top"
                                data-bs-title="Accepted"
                              >
                                <i className="ri-checkbox-circle-line" />
                              </button>
                              <button
                                className="btn btn-outline-danger btn-sm"
                                data-bs-toggle="tooltip"
                                data-bs-placement="top"
                                data-bs-title="Reject"
                                disabled=""
                              >
                                <i className="ri-close-circle-line" />
                              </button>
                              <a
                                href="edit-appointment.html"
                                className="btn btn-outline-info btn-sm"
                                data-bs-toggle="tooltip"
                                data-bs-placement="top"
                                data-bs-title="Edit Appointment"
                              >
                                <i className="ri-edit-box-line" />
                              </a>
                            </div>
                          </td>
                        </tr>
                        <tr>
                          <td>002</td>
                          <td>Jerry Wilcox</td>
                          <td>73</td>
                          <td>
                            <img
                              src="assets/images/user1.png"
                              className="img-shadow img-2x rounded-5 me-1"
                              alt="Hospital Admin Template"
                            />
                            April Gallegos
                          </td>
                          <td>Gynecologist</td>
                          <td>05/23/2024</td>
                          <td>9:45AM</td>
                          <td>Fever</td>
                          <td>
                            <div className="d-inline-flex gap-1">
                              <button
                                className="btn btn-outline-success btn-sm"
                                data-bs-toggle="tooltip"
                                data-bs-placement="top"
                                data-bs-title="Accept"
                                disabled=""
                              >
                                <i className="ri-checkbox-circle-line" />
                              </button>
                              <button
                                className="btn btn-danger btn-sm"
                                data-bs-toggle="tooltip"
                                data-bs-placement="top"
                                data-bs-title="Rejected"
                              >
                                <i className="ri-close-circle-line" />
                              </button>
                              <a
                                href="edit-appointment.html"
                                className="btn btn-outline-info btn-sm"
                                data-bs-toggle="tooltip"
                                data-bs-placement="top"
                                data-bs-title="Edit Appointment"
                              >
                                <i className="ri-edit-box-line" />
                              </a>
                            </div>
                          </td>
                        </tr>
                        <tr>
                          <td>003</td>
                          <td>Eduardo Kramer</td>
                          <td>84</td>
                          <td>
                            <img
                              src="assets/images/user2.png"
                              className="img-shadow img-2x rounded-5 me-1"
                              alt="Hospital Admin Template"
                            />
                            Basil Frost
                          </td>
                          <td>Psychiatrists</td>
                          <td>05/23/2024</td>
                          <td>10:00AM</td>
                          <td>Cold</td>
                          <td>
                            <div className="d-inline-flex gap-1">
                              <button
                                className="btn btn-outline-success btn-sm"
                                data-bs-toggle="tooltip"
                                data-bs-placement="top"
                                data-bs-title="Accept"
                              >
                                <i className="ri-checkbox-circle-line" />
                              </button>
                              <button
                                className="btn btn-outline-danger btn-sm"
                                data-bs-toggle="tooltip"
                                data-bs-placement="top"
                                data-bs-title="Reject"
                              >
                                <i className="ri-close-circle-line" />
                              </button>
                              <a
                                href="edit-appointment.html"
                                className="btn btn-outline-info btn-sm"
                                data-bs-toggle="tooltip"
                                data-bs-placement="top"
                                data-bs-title="Edit Appointment"
                              >
                                <i className="ri-edit-box-line" />
                              </a>
                            </div>
                          </td>
                        </tr>
                        <tr>
                          <td>004</td>
                          <td>Jason Compton</td>
                          <td>56</td>
                          <td>
                            <img
                              src="assets/images/user4.png"
                              className="img-shadow img-2x rounded-5 me-1"
                              alt="Hospital Admin Template"
                            />
                            Nannie Guerrero
                          </td>
                          <td>Urologist</td>
                          <td>05/23/2024</td>
                          <td>10:15AM</td>
                          <td>Prostate</td>
                          <td>
                            <div className="d-inline-flex gap-1">
                              <button
                                className="btn btn-outline-success btn-sm"
                                data-bs-toggle="tooltip"
                                data-bs-placement="top"
                                data-bs-title="Accept"
                              >
                                <i className="ri-checkbox-circle-line" />
                              </button>
                              <button
                                className="btn btn-outline-danger btn-sm"
                                data-bs-toggle="tooltip"
                                data-bs-placement="top"
                                data-bs-title="Reject"
                              >
                                <i className="ri-close-circle-line" />
                              </button>
                              <a
                                href="edit-appointment.html"
                                className="btn btn-outline-info btn-sm"
                                data-bs-toggle="tooltip"
                                data-bs-placement="top"
                                data-bs-title="Edit Appointment"
                              >
                                <i className="ri-edit-box-line" />
                              </a>
                            </div>
                          </td>
                        </tr>
                        <tr>
                          <td>005</td>
                          <td>Emmitt Bryan</td>
                          <td>49</td>
                          <td>
                            <img
                              src="assets/images/user5.png"
                              className="img-shadow img-2x rounded-5 me-1"
                              alt="Hospital Admin Template"
                            />
                            Daren Andrade
                          </td>
                          <td>Cardiology</td>
                          <td>05/23/2024</td>
                          <td>10:30AM</td>
                          <td>Asthma</td>
                          <td>
                            <div className="d-inline-flex gap-1">
                              <button
                                className="btn btn-outline-success btn-sm"
                                data-bs-toggle="tooltip"
                                data-bs-placement="top"
                                data-bs-title="Accept"
                              >
                                <i className="ri-checkbox-circle-line" />
                              </button>
                              <button
                                className="btn btn-outline-danger btn-sm"
                                data-bs-toggle="tooltip"
                                data-bs-placement="top"
                                data-bs-title="Reject"
                              >
                                <i className="ri-close-circle-line" />
                              </button>
                              <a
                                href="edit-appointment.html"
                                className="btn btn-outline-info btn-sm"
                                data-bs-toggle="tooltip"
                                data-bs-placement="top"
                                data-bs-title="Edit Appointment"
                              >
                                <i className="ri-edit-box-line" />
                              </a>
                            </div>
                          </td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                </div>
                {/* Table ends */}
              </div>
            </div>
          </div>
          <div className="col-xxl-6 col-sm-12">
            <div className="card mb-3">
              <div className="card-header">
                <h5 className="card-title">Income</h5>
              </div>
              <div className="card-body">
                <div id="income" />
              </div>
            </div>
          </div>
          <div className="col-xxl-6 col-sm-12">
            <div className="card mb-3">
              <div className="card-header">
                <h5 className="card-title">Pharmacy Orders</h5>
              </div>
              <div className="card-body">
                <div id="orders" />
              </div>
            </div>
          </div>
        </div>
        {/* Row ends */}
      </div>
    </>
  );
}

export default Dashboard;
