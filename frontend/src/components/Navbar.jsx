import { Link, useLocation } from "react-router-dom";

const Navbar = () => {
  const location = useLocation();

  return (
    <nav className="navbar navbar-expand-lg navbar-light bg-white shadow-sm sticky-top">
      <div className="container">
        <Link className="navbar-brand fw-bold fs-5 text-primary" to="/">
          RGM
        </Link>
        <button
          className="navbar-toggler"
          type="button"
          data-bs-toggle="collapse"
          data-bs-target="#navbarSupportedContent"
          aria-controls="navbarSupportedContent"
          aria-expanded="false"
          aria-label="Toggle navigation"
        >
          <span className="navbar-toggler-icon"></span>
        </button>
        <div className="collapse navbar-collapse" id="navbarSupportedContent">
          <ul className="navbar-nav me-auto mb-2 mb-lg-0">
            <li className="nav-item me-2 fs-5">
              <Link
                className={`nav-link ${
                  location.pathname === "/" ? "active" : ""
                }`}
                aria-current="page"
                to="/"
              >
                Home
              </Link>
            </li>
            <li className="nav-item dropdown me-2 fs-5">
              <a
                className={`nav-link dropdown-toggle ${
                  location.pathname === "/smart-pricing" ? "active" : ""
                }`}
                href="#"
                role="button"
                data-bs-toggle="dropdown"
                aria-expanded="false"
              >
                Tools
              </a>
              <ul className="dropdown-menu">
                <li>
                  <Link className="dropdown-item" to="/smart-pricing">
                    Smart Pricing
                  </Link>
                </li>
                <li>
                  <Link className="dropdown-item" to="/optimal-promotion">
                    Optimal Promotion
                  </Link>
                </li>
              </ul>
            </li>
            <li className="nav-item dropdown me-2 fs-5">
              <a
                className={`nav-link dropdown-toggle ${
                  location.pathname.startsWith("/glossary") ? "active" : ""
                }`}
                href="#"
                role="button"
                data-bs-toggle="dropdown"
                aria-expanded="false"
              >
                Glossary
              </a>
              <ul className="dropdown-menu">
                <li>
                  <Link className="dropdown-item" to="/glossary/pricing">
                    Pricing Glossary
                  </Link>
                </li>
                <li>
                  <Link className="dropdown-item" to="/glossary/promotion">
                    Promotion Glossary
                  </Link>
                </li>
              </ul>
            </li>
          </ul>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
