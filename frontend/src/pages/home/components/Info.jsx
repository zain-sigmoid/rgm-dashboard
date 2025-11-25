import React from "react";
import "../styling/home.css";

const highlightCards = [
  {
    id: "smart-pricing",
    title: "Smart Pricing",
    icon: "fa-solid fa-tags",
    description:
      "Simulate price changes, forecast revenue impact, and identify optimal price points across products and channels.",
    bullets: [
      "Elasticity-driven simulations with historical uplift",
      "Scenario planning with competitor and distribution inputs",
      "Instant visuals for revenue, margin, and volume shifts",
    ],
    gradient: "linear-gradient(135deg, #e1f2ff 0%, #b9dcff 55%, #8dbfff 100%)",
  },
  {
    id: "optimal-promotion",
    title: "Optimal Promotion",
    icon: "fa-solid fa-bullseye",
    description:
      "Design and evaluate promotion mechanics with lift factors, ROI visibility, and guardrails on spend.",
    bullets: [
      "Promotion mix optimization with contribution analysis",
      "Cross- and self-elasticity baked into outcomes",
      "Guardrails for spend, frequency, and depth of discount",
    ],
    gradient: "linear-gradient(135deg, #e9f9ff 0%, #c2ebff 55%, #8edcff 100%)",
  },
  {
    id: "insights",
    title: "Insights & Drill Through",
    icon: "fa-solid fa-chart-line",
    description:
      "Track performance by category, retailer, and time horizon with drill-through views for rapid decisioning.",
    bullets: [
      "Contribution analysis across key levers",
      "Distribution and price corridor visuals",
      "Health checks with responsive KPIs",
    ],
    gradient: "linear-gradient(135deg, #eef5ff 0%, #d6e6ff 50%, #b3d1ff 100%)",
  },
];

const Info = () => {
  return (
    <section className="info-section">
      <div className="container pt-4 px-3">
        <div className="text-center mb-4">
          <p className="hero-kicker text-uppercase fw-bold mb-1">
            Navigate smarter
          </p>
          <h2 className="fw-bold fs-1 text-primary-emphasis">
            Everything you need for Pricing &amp; Promotion decisions
          </h2>
          {/* <p className="text-secondary">
            Built from the Streamlit experience—now with cards for the key
            workflows.
          </p> */}
        </div>

        <div className="row g-5 pt-3">
          {highlightCards.map((card) => (
            <div className="col-lg-4 col-md-6" key={card.id} id={card.id}>
              <div
                className="card h-100 shadow border-0 info-card p-4"
                style={{ background: card.gradient }}
              >
                <div className="card-body d-flex flex-column">
                  <div className="d-flex align-items-center mb-3">
                    {/* <span className="badge rounded-pill bg-white text-primary me-2 shadow-sm">
                      <i className={card.icon}></i>
                    </span> */}
                    <h5 className="card-title mb-0 text-dark fw-bold fs-3">
                      {card.title}
                    </h5>
                  </div>
                  <p className="card-text text-dark mb-3">{card.description}</p>
                  <ul className="list-unstyled text-dark mb-0">
                    {card.bullets.map((item) => (
                      <li className="d-flex align-items-start mb-2" key={item}>
                        <i className="fa-solid fa-check text-primary me-2 mt-1"></i>
                        <span>{item}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default Info;
