import React from "react";

const Footer = () => {
  return (
    <footer className="bg-dark text-light py-4 mt-5">
      <div className="container d-flex flex-column flex-md-row justify-content-between align-items-center gap-3">
        <div className="d-flex align-items-center gap-3">
          <img
            src="https://i.im.ge/2024/03/21/RKWdrM.Sigmoid-Logo.png"
            alt="Sigmoid"
            style={{ height: "40px", width: "auto" }}
          />
          <div>
            <div className="fw-semibold">Sigmoid Pricing &amp; Promotion</div>
            <small className="text-secondary">
              Data-forward insights for smart pricing and optimal promotions.
            </small>
          </div>
        </div>
        <div className="d-flex align-items-center gap-3 text-secondary">
          <i className="fa-brands fa-linkedin fs-5"></i>
          <i className="fa-brands fa-github fs-5"></i>
          <i className="fa-solid fa-envelope fs-5"></i>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
