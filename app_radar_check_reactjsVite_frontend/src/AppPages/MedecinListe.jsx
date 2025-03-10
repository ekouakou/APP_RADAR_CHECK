// import { useState } from 'react'

function MedecinListe() {
  // const [count, setCount] = useState(0)

  return (
    <>
      <div className="app-body">
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

export default MedecinListe;
