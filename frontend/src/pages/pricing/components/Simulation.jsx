import React, { useContext, useEffect, useMemo } from "react";
import PropTypes from "prop-types";
import { BarChart, Bar, CartesianGrid, Legend, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { userContext } from "../../../context/userContext";

const Simulation = ({ filters }) => {
  const { simulation, runSimulation } = useContext(userContext);

  useEffect(() => {
    runSimulation({ filters });
  }, [filters, runSimulation]);

  const cards = simulation.data?.summary_cards ?? [];
  const volumeBars = simulation.data?.volume_bars;
  const revenueBars = simulation.data?.revenue_bars;
  const table = simulation.data?.table;

  const volumeChartData = useMemo(() => volumeBars?.bars ?? [], [volumeBars]);
  const revenueChartData = useMemo(() => revenueBars?.bars ?? [], [revenueBars]);

  return (
    <div className="container py-4">
      <div className="d-flex justify-content-between align-items-center mb-3">
        <h4 className="mb-0">Simulation</h4>
        {simulation.loading && <span className="badge bg-info text-dark">Loading...</span>}
        {simulation.error && <span className="badge bg-danger">{simulation.error}</span>}
      </div>

      <div className="row g-3 mb-4">
        {cards.map((card) => (
          <div className="col-md-4 col-lg-3" key={card.label}>
            <div className="card border-0 shadow-sm h-100">
              <div className="card-body">
                <div className="text-muted small">{card.label}</div>
                <div className="fs-5 fw-bold">{card.value}</div>
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="row g-4 mb-4">
        {volumeChartData.length ? (
          <div className="col-lg-6">
            <div className="card shadow-sm border-0 h-100">
              <div className="card-body">
                <h6 className="fw-bold mb-3">{volumeBars?.title}</h6>
                <div style={{ height: 280 }}>
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={volumeChartData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="label" />
                      <YAxis />
                      <Tooltip />
                      <Legend />
                      <Bar dataKey="value" name="Volume" fill="#0f62c2" />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>
            </div>
          </div>
        ) : null}

        {revenueChartData.length ? (
          <div className="col-lg-6">
            <div className="card shadow-sm border-0 h-100">
              <div className="card-body">
                <h6 className="fw-bold mb-3">{revenueBars?.title}</h6>
                <div style={{ height: 280 }}>
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={revenueChartData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="label" />
                      <YAxis />
                      <Tooltip />
                      <Legend />
                      <Bar dataKey="value" name="Revenue" fill="#1e3d7d" />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>
            </div>
          </div>
        ) : null}
      </div>

      {table?.rows?.length ? (
        <div className="card shadow-sm border-0">
          <div className="card-body">
            <h6 className="fw-bold mb-3">Detailed View</h6>
            <div className="table-responsive" style={{ maxHeight: "450px" }}>
              <table className="table table-sm table-hover mb-0">
                <thead className="table-light">
                  <tr>
                    {table.columns.map((col) => (
                      <th key={col}>{col}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {table.rows.map((row, idx) => (
                    <tr key={idx}>
                      {table.columns.map((col) => (
                        <td key={col}>{row[col]}</td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      ) : null}
    </div>
  );
};

Simulation.propTypes = {
  filters: PropTypes.object.isRequired,
};

export default Simulation;
