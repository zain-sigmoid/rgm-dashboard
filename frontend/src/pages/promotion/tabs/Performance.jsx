import React, { useEffect, useMemo, useState } from "react";
import PropTypes from "prop-types";
import { useContext } from "react";
import { userContext } from "../../../context/userContext";
import "../styling/promo.css";

const Performance = ({ filters }) => {
  const { performance, fetchPerformance } = useContext(userContext);
  const [activeTab, setActiveTab] = useState("offer_mechanics");

  useEffect(() => {
    fetchPerformance(filters);
  }, [filters, fetchPerformance]);

  const grads = ["grad-1", "grad-2", "grad-3", "grad-4", "grad-5", "grad-6"];
  const PROMOTION_API =
    import.meta.env.VITE_PROMOTION_API?.replace(/\/$/, "") ||
    "http://127.0.0.1:8000/api/promotion";

  const cards = useMemo(
    () => performance.data?.metrics ?? [],
    [performance.data]
  );
  const mechanics = performance.data?.mechanics ?? [];
  const ppgs = performance.data?.ppg ?? [];
  const retailer = performance.data?.retailer ?? [];
  const subsegment = performance.data?.subsegment ?? [];
  const tabsConfig = {
    offer_mechanics: {
      key: "offer_mechanics",
      title: "Mechanics",
      icon: "fa-solid fa-gear",
      data: mechanics,
      bg: "success",
    },
    ppgs: {
      key: "ppgs",
      title: "PPG",
      icon: "fa-solid fa-box",
      data: ppgs,
      bg: "info",
    },
    retailer: {
      key: "retailer",
      title: "Retailer",
      icon: "fa-solid fa-shop",
      data: retailer,
      bg: "primary",
    },
    subsegment: {
      key: "subsegment",
      title: "Subsegment",
      icon: "fa-solid fa-sliders",
      data: subsegment,
      bg: "danger",
    },
  };
  const handleDownload = async (activeTab) => {
    try {
      const res = await fetch(`${PROMOTION_API}/export/${activeTab}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(filters),
      });

      if (!res.ok) {
        // optional: handle error
        const text = await res.text();
        console.error("Download error:", text);
        return;
      }

      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = `${activeTab}.csv`;
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error("Download failed:", err);
    }
  };
  const tabs = Object.values(tabsConfig);
  const DFTableView = ({ table, bg }) => {
    if (!table || !table.columns || table.columns.length === 0) {
      return (
        <div className="card p-3 shadow-sm">
          <h6 className="fw-bold mb-3">Loading Data...</h6>

          <div className="table-responsive">
            <table className="table align-middle">
              <thead>
                <tr>
                  {["Col 1", "Col 2", "Col 3", "Col 4", "Col 5", "Col 6"].map(
                    (_, i) => (
                      <th key={i}>
                        <span className="placeholder col-6"></span>
                      </th>
                    )
                  )}
                </tr>
              </thead>

              <tbody className="placeholder-glow">
                {[...Array(6)].map((_, idx) => (
                  <tr key={idx}>
                    <td>
                      <span className="placeholder col-8"></span>
                    </td>
                    <td>
                      <span className="placeholder col-6"></span>
                    </td>
                    <td>
                      <span className="placeholder col-5"></span>
                    </td>
                    <td>
                      <span className="placeholder col-8"></span>
                    </td>
                    <td>
                      <span className="placeholder col-6"></span>
                    </td>
                    <td>
                      <span className="placeholder col-5"></span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      );
    }

    const { columns, rows } = table;

    return (
      <div
        className="table-responsive shadow-sm"
        style={{ maxHeight: "500px" }}
      >
        <table className="table table-sm table-striped-columns table-sticky-header">
          <thead style={{ fontSize: "15px", paddingLeft: "10px" }}>
            <tr className={`table-${bg}`}>
              <th scope="col">#</th>
              {columns.map((col) => (
                <th key={col}>{col}</th>
              ))}
            </tr>
          </thead>
          <tbody
            style={{ fontSize: "12px", paddingLeft: "10px" }}
            className="table-group-divider"
          >
            {rows.map((row, idx) => (
              <tr
                key={idx}
                className={`align-middle border border-top border-start-0 border-end-0 border-${bg} border-2 border-opacity-50`}
              >
                <th scope="row">{idx + 1}</th>
                {columns.map((col) => (
                  <td key={col}>{row[col]}</td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
  };

  return (
    <div className="py-4 pe-4" id="promo">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h4 className="mb-1">Performance Analysis</h4>
        </div>
        {performance.loading && (
          <span className="badge bg-info text-dark">Loading...</span>
        )}
        {performance.error && (
          <span className="badge bg-danger">{performance.error}</span>
        )}
      </div>
      <div className="row g-3 mb-4">
        {cards.length > 0
          ? cards.map((card, idx) => (
              <div className="col-md-2" key={card.label}>
                <div
                  className={`glass-card d-flex flex-column justify-content-between h-100 ${
                    grads[idx % grads.length]
                  }`}
                >
                  <div className="fw-semibold small">{card.label}</div>
                  <div className="fw-bold fs-5">{card.value}</div>
                </div>
              </div>
            ))
          : [...Array(6)].map((_, idx) => (
              <div className="col-md-2" key={idx}>
                <div
                  className={`glass-card h-100 ${grads[idx % grads.length]}`}
                >
                  <div className="placeholder-glow">
                    <div className="placeholder placeholder-sm col-6 mb-2 d-block"></div>
                    <div className="placeholder placeholder-xs col-4 d-block"></div>
                  </div>
                </div>
              </div>
            ))}
      </div>
      <div
        className="d-flex flex-row justify-content-between"
        style={{ margin: "50px 0" }}
      >
        <div className="d-flex flex-wrap gap-3">
          {tabs.map((tab, idx) => (
            <button
              key={idx}
              type="button"
              className={`btn ${
                tab.key === activeTab ? "btn-primary" : "btn-outline-secondary"
              } shadow-sm`}
              onClick={() => {
                setActiveTab(tab.key);
              }}
            >
              {tab.icon && <i className={`${tab.icon} me-2 `}></i>}
              {tab.title}
            </button>
          ))}
        </div>
        <button
          type="button"
          className="btn btn-sm btn-outline-secondary shadow-sm"
          onClick={() => {
            handleDownload(activeTab);
          }}
        >
          <i className="fa-solid fa-download me-1" />
          Download CSV
        </button>
      </div>
      <div style={{ margin: "20px 0" }}>
        <DFTableView
          table={tabsConfig[activeTab]?.data}
          bg={tabsConfig[activeTab]?.bg}
        />
        <p
          className="text-muted font-monospace mt-4"
          style={{ fontSize: "14px" }}
        >
          Total Rows: {tabsConfig[activeTab]?.data?.rows?.length}
        </p>
      </div>
    </div>
  );
};

Performance.propTypes = {
  filters: PropTypes.shape({
    categories: PropTypes.arrayOf(PropTypes.string),
    manufacturers: PropTypes.arrayOf(PropTypes.string),
    brands: PropTypes.arrayOf(PropTypes.string),
    ppgs: PropTypes.arrayOf(PropTypes.string),
    retailers: PropTypes.arrayOf(PropTypes.string),
  }),
};

Performance.defaultProps = {
  filters: {
    categories: [],
    manufacturers: [],
    brands: [],
    ppgs: [],
    retailers: [],
  },
};

export default Performance;
