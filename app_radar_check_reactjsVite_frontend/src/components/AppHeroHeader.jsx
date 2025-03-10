
        const AppHeroHeader = () => {
          return (
            <>
                     {/* App hero header starts */}
        <div className="app-hero-header d-flex align-items-center">
          {/* Breadcrumb starts */}
          <ol className="breadcrumb">
            <li className="breadcrumb-item">
              <i className="ri-home-8-line lh-1 pe-3 me-3 border-end" />
              <a href="index.html">Home</a>
            </li>
            <li className="breadcrumb-item text-primary" aria-current="page">
              Add Room
            </li>
          </ol>
          {/* Breadcrumb ends */}
          {/* Sales stats starts */}
          <div className="ms-auto d-lg-flex d-none flex-row">
            <div className="d-flex flex-row gap-1 day-sorting">
              <button className="btn btn-sm btn-primary">Today</button>
              <button className="btn btn-sm">7d</button>
              <button className="btn btn-sm">2w</button>
              <button className="btn btn-sm">1m</button>
              <button className="btn btn-sm">3m</button>
              <button className="btn btn-sm">6m</button>
              <button className="btn btn-sm">1y</button>
            </div>
          </div>
          {/* Sales stats ends */}
        </div>
        {/* App Hero header ends */}



            </>
          );
        };
        
        export default AppHeroHeader;
        