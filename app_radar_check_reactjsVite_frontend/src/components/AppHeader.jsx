const AppHeader = () => {
  return (

    <>
            <div className="app-header d-flex align-items-center">
      {/* Toggle buttons */}
      <div className="d-flex">
        <button className="toggle-sidebar">
          <i className="ri-menu-line" />
        </button>
        <button className="pin-sidebar">
          <i className="ri-menu-line" />
        </button>
      </div>

      {/* App brand */}
      <div className="app-brand ms-3">
        <a href="index.html" className="d-lg-block d-none">
          <img src="assets/images/logo.svg" className="logo" alt="Medicare Admin Template" />
        </a>
        <a href="index.html" className="d-lg-none d-md-block">
          <img src="assets/images/logo-sm.svg" className="logo" alt="Medicare Admin Template" />
        </a>
      </div>

      {/* App header actions */}
      <div className="header-actions">
        {/* Search */}
        <div className="search-container d-lg-block d-none mx-3">
          <input type="text" className="form-control" placeholder="Search" />
          <i className="ri-search-line" />
        </div>

        {/* Notifications */}
        <div className="dropdown">
          <a className="dropdown-toggle header-icon" href="#!" role="button" data-bs-toggle="dropdown">
            <i className="ri-list-check-3" />
            <span className="count-label warning" />
          </a>
          <div className="dropdown-menu dropdown-menu-end dropdown-300">
            <h5 className="fw-semibold px-3 py-2 text-primary">Activity</h5>
            <div className="scroll300 p-3">
              <ul className="p-0 activity-list2">
                <li className="activity-item pb-3 mb-3">
                  <a href="#!">
                    <h5 className="fw-regular">
                      <i className="ri-circle-fill text-danger me-1" />
                      Invoices.
                    </h5>
                    <p className="small">10:20AM Today</p>
                  </a>
                </li>
                <li className="activity-item">
                  <a href="#!">
                    <h5 className="fw-regular">
                      <i className="ri-circle-fill text-success me-1" />
                      Appointed.
                    </h5>
                    <p className="small">06:50PM Today</p>
                  </a>
                </li>
              </ul>
            </div>
          </div>
        </div>

        {/* User Profile */}
        <div className="dropdown ms-2">
          <a id="userSettings" className="dropdown-toggle d-flex align-items-center" href="#!" role="button" data-bs-toggle="dropdown">
            <div className="avatar-box">
              JB
              <span className="status busy" />
            </div>
          </a>
          <div className="dropdown-menu dropdown-menu-end shadow-lg">
            <div className="px-3 py-2">
              <span className="small">Admin</span>
              <h6 className="m-0">James Bruton</h6>
            </div>
            <div className="mx-3 my-2 d-grid">
              <a href="login.html" className="btn btn-danger">Logout</a>
            </div>
          </div>
        </div>
      </div>
    </div>
    </>

  );
};

export default AppHeader;
