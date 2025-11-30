import React from "react";

const pricingTerms = [
  {
    title: "Fair Share",
    desc: "It pertains to equitable distribution of revenue across all retailers or manufacturers within a category, without using specific filters.",
    icon: "fa-scale-balanced",
    accent: "linear-gradient(135deg, #f9f5ff, #e6dfff)",
  },
  {
    title: "Price Elasticity",
    desc: "Price elasticity measures the responsiveness of consumers to changes in price. E.g., A price elasticity = -2.0,for example, is considered more price elastic and 5% price increase will result in roughly 10% volume loss.",
    icon: "fa-chart-line",
    accent: "linear-gradient(135deg, #bddbf6ff, #b8f5cdff)",
  },
  {
    title: "Cross Price Elasticity",
    desc: "Cross price elasticity refers to how the demand for one product changes in response to a change in the price of another related product. It quantifies the percentage change in the quantity demanded of one product when the price of another product changes by one percent. E.g A Cross Price Elasticty = 1 , for example, is considered less elastic and 5% price increase in competitor price will result in 5% gain in own volume.",
    icon: "fa-arrows-left-right",
    accent: "linear-gradient(135deg, #f2f7ff, #d6e7ff)",
  },
  {
    title: "Distribution Elasticity",
    desc: "Distribution elasticity provide insights on impact of products distribution on the volume. For every 1%-point increase in product’s ACV weighted distribution (Wtd. %ACV ) or Total Distribution Points (TDP) , distribution elasticity of 0.6 results in 0.6% increase in product’s volume.",
    icon: "fa-route",
    accent: "linear-gradient(135deg, #fef8f5, #fde5da)",
  },
  {
    title: "Current Price",
    desc: "It shows last year average price.",
    icon: "fa-tag",
    accent: "linear-gradient(135deg, #f7fff8, #e0f7e6)",
  },
  {
    title: "Current Distribution",
    desc: "It shows last year average distribution.",
    icon: "fa-store",
    accent: "linear-gradient(135deg, #feeeffff, #e9ddecff)",
  },
  {
    title: "Current Competitor Price",
    desc: "It shows last year average competitor price",
    icon: "fa-handshake",
    accent: "linear-gradient(135deg, #fbdcd0ff, #e0f2ff)",
  },
];

const PricingGlossary = () => {
  return (
    <section className="py-5" style={{ background: "white" }}>
      <div className="container">
        <div className="text-center mb-5">
          <p className="text-uppercase text-primary fw-bold mb-1 small">
            Pricing glossary
          </p>
          <h2 className="fw-bold text-dark">
            Key definitions for Smart Pricing
          </h2>
        </div>
        <div className="row g-4">
          {pricingTerms.map((term) => (
            <div className="col-lg-6 col-md-12" key={term.title}>
              <div
                className="card h-100 shadow-sm border-0 p-3"
                style={{ background: term.accent, borderRadius: "14px" }}
              >
                <div className="card-body d-flex flex-column">
                  <div className="d-flex align-items-center mb-3">
                    <span className="badge bg-white text-primary shadow-sm me-3 p-3 rounded-circle">
                      <i className={`fa-solid ${term.icon}`}></i>
                    </span>
                    <h4 className="mb-0 fw-bold text-dark">{term.title}</h4>
                  </div>
                  <p className="text-muted mb-0">{term.desc}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default PricingGlossary;
