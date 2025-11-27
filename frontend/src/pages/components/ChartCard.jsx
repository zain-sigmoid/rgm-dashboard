// ChartCard.tsx
import React from "react";

export const ChartCard = ({ title, loading, height = 320, children }) => {
  return (
    <div className="col-lg-4">
      <div className="card shadow-sm border h-100 pe-4 py-2">
        <div className="card-body">
          {title ? (
            <h6 className="fw-bold mb-3">{title}</h6>
          ) : (
            <div className="placeholder-glow mb-3">
              <span className="placeholder col-6"></span>
            </div>
          )}

          <div style={{ height }}>
            {loading ? (
              <div className="placeholder-glow h-100 w-100 d-flex align-items-center justify-content-center">
                <div className="placeholder rounded w-75 h-75" />
              </div>
            ) : (
              children
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
