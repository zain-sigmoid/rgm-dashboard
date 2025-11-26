import React from "react";

const promotionTerms = [
  {
    title: "TPR (Temporary Price Reduction)",
    desc: "A temporary discount on the regular price of a product to stimulate sales and attract customers. TPRs are often used to boost short-term revenue or clear out inventory.",
    icon: "fa-bolt",
    accent: "linear-gradient(135deg, #f9f5ff, #e6dfff)",
  },
  {
    title: "Feature",
    desc: "A type of promotion where a product is highlighted in marketing materials, such as flyers, catalogs, or online banners. Features increase product visibility and awareness, driving consumer interest and sales.",
    icon: "fa-bullhorn",
    accent: "linear-gradient(135deg, #f5fbff, #dff0ff)",
  },
  {
    title: "Display",
    desc: "A promotional strategy where products are prominently showcased in physical. Special displays, end caps, or eye-catching arrangements draw attention to the promoted items, encouraging impulse purchases and increasing sales.",
    icon: "fa-store",
    accent: "linear-gradient(135deg, #bddbf6ff, #b8f5cdff)",
  },
  {
    title: "Redemption Rate",
    desc: "The percentage of customers who take advantage of a promotional offer out of the total number of customers who were exposed to the offer. It measures the effectiveness of the promotion in converting potential customers into actual buyers.",
    icon: "fa-ticket",
    accent: "linear-gradient(135deg, #fef8f5, #fde5da)",
  },
  {
    title: "ROI (Return on Investment)",
    desc: "A performance measure used to evaluate the efficiency or profitability of an investment. In promotions, ROI calculates the gain or loss generated relative to the amount invested in the promotional activity. It helps to determine the financial return of marketing efforts..",
    icon: "fa-sack-dollar",
    accent: "linear-gradient(135deg, #f7fff8, #e0f7e6)",
  },
  {
    title: "Uplift",
    desc: "The increase in sales or customer engagement attributed to a specific promotion or marketing activity. Uplift measures the positive impact of the promotion by comparing sales or engagement levels before and during the promotion period. It helps assess the effectiveness of the promotional strategy in driving additional business.",
    icon: "fa-arrow-trend-up",
    accent: "linear-gradient(135deg, #d0d2fbff, #e0f2ff)",
  },
];

const PromotionGlossary = () => {
  return (
    <section className="py-5" style={{ background: "white" }}>
      <div className="container p-4">
        <div className="text-center mb-4">
          <p className="text-uppercase text-primary fw-bold mb-1 small">
            Promotion glossary
          </p>
          <h2 className="fw-bold text-dark">
            Key definitions for Optimal Promotion
          </h2>
        </div>
        <div className="row g-4 mt-2">
          {promotionTerms.map((term) => (
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
                    <h5 className="mb-0 fw-bold text-dark">{term.title}</h5>
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

export default PromotionGlossary;
