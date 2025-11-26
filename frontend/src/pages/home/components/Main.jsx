import React from "react";
import "../styling/home.css";
import { Link } from "react-router-dom";

const Main = () => {
  return (
    <div className="hero-page">
      <main className="hero-content">
        <div className="container text-center">
          <div className="logo-row">
            <img
              src="https://i.im.ge/2024/05/30/KLEPIh.Screenshot-2024-05-30-at-10-20-29AM.png"
              alt="Retailer logo"
              className="hero-logo-left"
            />
            <img
              src="https://i.im.ge/2024/03/21/RKWdrM.Sigmoid-Logo.png"
              alt="Sigmoid logo"
              className="hero-logo-right"
            />
          </div>

          <p className="hero-kicker mb-2">Sigmoid&apos;s</p>
          <h1 className="hero-title mb-3">
            <span className="gradient-text">Pricing</span> and{" "}
            <span className="gradient-text">Promotion</span>
            <br />
          </h1>
          <h3 className="hero-sub-title">Optimization Tool</h3>
          <p className="hero-subtitle mx-auto">
            Navigate smart pricing and optimal promotions with an immersive,
            data-forward experience.
          </p>

          <div className="d-flex justify-content-center gap-3 flex-wrap mt-5">
            <Link className="btn cta-btn" to="/smart-pricing">
              SMART PRICING
            </Link>
            <Link className="btn cta-btn" to="/optimal-promotion">
              OPTIMAL PROMOTION
            </Link>
          </div>
        </div>
      </main>
    </div>
  );
};

export default Main;
