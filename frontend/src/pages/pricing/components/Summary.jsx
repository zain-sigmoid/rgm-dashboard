import React, { useEffect, useMemo } from "react";
import PropTypes from "prop-types";
import { useContext } from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
  LabelList,
} from "recharts";
import { userContext } from "../../../context/userContext";
import BarLabel from "./BarLabel";
import { formatPercent } from "../config/labelFormatter";
import "../styling/style.css";

const Summary = ({ filters }) => {
  const { summary, fetchSummary } = useContext(userContext);
  const grads = ["grad-1", "grad-2", "grad-3", "grad-4"];

  useEffect(() => {
    fetchSummary(filters);
  }, [filters, fetchSummary]);

  const cards = useMemo(() => summary.data?.kpis ?? [], [summary.data]);
  const fairShare = summary.data?.fair_share_vs_revenue ?? [];
  const revenueSeries = summary.data?.revenue_by_manufacturer ?? [];
  const revenueTable = summary.data?.revenue_table ?? [];
  const revenueRetailerTable = summary.data?.revenue_by_retailer_table ?? [];
  const revenueRetailer = summary.data?.revenue_by_retailer ?? [];
  const revenueRetailerChart = summary.data?.revenue_by_retailer_chart ?? [];

  console.log(summary);

  const revenueChartData = useMemo(
    () =>
      revenueSeries.flatMap((serie) =>
        serie.points.map((p) => ({
          manufacturer: serie.manufacturer,
          period: p.period,
          revenue: p.value,
        }))
      ),
    [revenueSeries]
  );

  const manufacturers = Array.from(
    new Set(revenueChartData.map((d) => d.manufacturer))
  );

  const retailers = Array.from(
    new Set(revenueRetailerChart?.rows?.map((d) => d.retailer_id))
  );

  const stackedData = useMemo(() => {
    const map = {};

    revenueChartData.forEach(({ period, manufacturer, revenue }) => {
      if (!map[period]) map[period] = { period };
      map[period][manufacturer] = revenue;
    });

    return Object.values(map);
  }, [revenueChartData]);

  const retailerPeriods = useMemo(
    () =>
      revenueRetailerChart?.columns?.filter(
        (c) => c !== "retailer_id" && c !== "%Change"
      ) ?? [],
    [revenueRetailerChart?.columns]
  );

  const chartData = useMemo(() => {
    if (!retailerPeriods.length) return [];
    return retailerPeriods.map((period) => {
      const row = { period };
      revenueRetailerChart?.rows?.forEach((r) => {
        row[r.retailer_id] = r[period];
      });
      return row;
    });
  }, [retailerPeriods, revenueRetailerChart?.rows]);

  const colors = ["#e53935", "#fb8c00", "#43a047", "#1e88e5", "#6d4c41"];
  return (
    <div className="py-4 pe-4">
      <div className="d-flex justify-content-between align-items-center mb-3">
        <div>
          <h4 className="mb-1">Summary</h4>
          <div className="text-muted small">
            Assessment Period: {summary.data?.assessment_period || "–"}
          </div>
        </div>
        {summary.loading && (
          <span className="badge bg-info text-dark">Loading...</span>
        )}
        {summary.error && (
          <span className="badge bg-danger">{summary.error}</span>
        )}
      </div>

      {/* KPIs Cards */}
      <div className="row g-3 mb-4">
        {cards.map((card, idx) => (
          <div className="col-md-3" key={card.label}>
            <div className={`glass-card h-100 ${grads[idx % grads.length]}`}>
              <div className="fw-semibold small">{card.label}</div>
              <div className="fw-bold fs-1">{card.value}</div>
            </div>
          </div>
        ))}
      </div>

      <div className="card shadow-sm border p-4 my-5 abstract-curtain-bg">
        <div className="card-body">
          <div className="row g-4">
            <div className="col-lg-5">
              <div className="h-100 p-4 abstract-curtain-content">
                <div
                  className="rounded-circle d-flex justify-content-center align-items-center mb-3"
                  style={{
                    width: "70px",
                    height: "70px",
                    background: "rgba(255,255,255,0.2)",
                    backdropFilter: "blur(6px)",
                    boxShadow: "0 4px 12px rgba(0,0,0,0.2)",
                  }}
                >
                  <i className="fa-solid fa-chart-pie fs-3"></i>
                </div>

                {/* HEADING */}
                <h2 className="fw-bold mb-2 text-white">
                  Manufacturer Revenue Share
                </h2>

                {/* DESCRIPTION */}
                <p className="mb-4 text-dark" style={{ opacity: 0.9 }}>
                  Compare actual revenue share against fair share to identify
                  over- and under-performing manufacturers.
                </p>

                {/* INSIGHT BADGES */}
                <div className="d-flex flex-column gap-3">
                  <span
                    className="badge rounded-pill px-3 py-2"
                    style={{
                      background: "rgba(3, 31, 109, 0.39)",
                      backdropFilter: "blur(1px)",
                      fontSize: "0.9rem",
                    }}
                  >
                    <strong>Revenue Share</strong>
                  </span>

                  <span
                    className="badge rounded-pill px-3 py-2"
                    style={{
                      background: "rgba(3, 31, 109, 0.39)",
                      backdropFilter: "blur(1px)",
                      fontSize: "0.9rem",
                    }}
                  >
                    <strong>Fair Share</strong>
                  </span>
                </div>
              </div>
            </div>
            <div className="col-lg-7 p-2">
              <div className="card shadow-sm border h-100 pe-4 py-2">
                <div className="card-body">
                  <div style={{ height: 320 }}>
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart data={fairShare} layout="vertical">
                        <CartesianGrid strokeDasharray="3 3" />
                        <YAxis
                          dataKey="manufacturer"
                          type="category"
                          width={70}
                          tick={{ fontSize: 12 }}
                          textAnchor="end"
                        />
                        <XAxis type="number" />
                        <Tooltip />
                        <Legend />
                        <Bar
                          dataKey="revenue_share"
                          name="Revenue Share %"
                          fill="#0f62c2"
                        >
                          <LabelList
                            dataKey="revenue_share"
                            content={
                              <BarLabel
                                formatter={formatPercent}
                                orientation="horizontal"
                              />
                            }
                          />
                        </Bar>
                        <Bar
                          dataKey="fair_share"
                          name="Fair Share %"
                          fill="#6aa6ff"
                        >
                          <LabelList
                            dataKey="fair_share"
                            content={
                              <BarLabel
                                formatter={formatPercent}
                                orientation="horizontal"
                              />
                            }
                          />
                        </Bar>
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="row g-4">
        <div className="col-lg-6">
          <div className="card shadow-sm border h-100 pe-4 py-2">
            <div className="card-body">
              <h6 className="fw-bold mb-3 text-center">
                Manufacturer Wise Revenue
              </h6>
              <div style={{ height: 320 }}>
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={stackedData} barSize={50}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="period" tick={{ fontSize: 12 }} />
                    <YAxis tick={{ fontSize: 12 }} />
                    <Tooltip />
                    <Legend wrapperStyle={{ fontSize: 12 }} />

                    {manufacturers.map((m, idx) => (
                      <Bar
                        key={m}
                        dataKey={m}
                        name={m}
                        stackId="a"
                        fill={colors[idx % colors.length]}
                      />
                    ))}
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>
        </div>
        <div className="col-lg-6">
          <div className="card shadow-sm border h-100 px-4 py-2">
            <div className="card-body">
              <h6 className="fw-bold mb-3 text-center">
                Manufacturer Revenue Comparison
              </h6>
              <div style={{ height: 320, overflow: "auto" }}>
                <table className="table table-striped-columns mt-4">
                  <thead>
                    <tr>
                      {revenueTable?.columns?.map((col) => (
                        <th key={col} className="table-success ">
                          {col}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {revenueTable?.rows?.map((row, rowIdx) => (
                      <tr key={rowIdx}>
                        {revenueTable?.columns?.map((col) => (
                          <td key={col} style={{ fontSize: "14px" }}>
                            {col === "%Change 2023"
                              ? `${row[col].toFixed(2)}%`
                              : row[col]}
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div className="card shadow-sm border p-4 my-5 abstract-curtain-bg-retailer">
        <div className="card-body">
          <div className="row g-4">
            <div className="col-lg-7 p-2">
              <div className="card shadow-sm border h-100 pe-4 py-2">
                <div className="card-body">
                  <div style={{ height: 320 }}>
                    <ResponsiveContainer width="100%" height={300}>
                      <BarChart
                        data={revenueRetailer}
                        layout="vertical"
                        barSize={18}
                        margin={{ right: 40 }}
                      >
                        <CartesianGrid strokeDasharray="3 3" />
                        <YAxis
                          dataKey="retailer_id"
                          type="category"
                          width={70}
                          tick={{ fontSize: 12 }}
                        />
                        <XAxis
                          type="number"
                          tickFormatter={(v) => v + "%"}
                          tick={{ fontSize: 12 }}
                        />

                        <Tooltip formatter={(v) => v.toFixed(2) + "%"} />
                        <Legend wrapperStyle={{ fontSize: 12 }} />

                        <Bar
                          dataKey="revenue_share"
                          name="Revenue Share"
                          fill="#f64915ff"
                        >
                          <LabelList
                            dataKey="revenue_share_label"
                            content={
                              <BarLabel
                                formatter={formatPercent}
                                orientation="horizontal"
                              />
                            }
                          />
                        </Bar>

                        <Bar
                          dataKey="rev_share_retailer_fair_share"
                          name="Fair Share"
                          fill="#ffa726"
                        >
                          <LabelList
                            dataKey="rev_share_retailer_fair_share"
                            content={
                              <BarLabel
                                formatter={formatPercent}
                                orientation="horizontal"
                              />
                            }
                          />
                        </Bar>
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                </div>
              </div>
            </div>
            <div className="col-lg-5">
              <div className="h-100 p-4 abstract-curtain-content text-end">
                <div
                  className="rounded-circle d-flex justify-content-center align-items-center mb-3 ms-auto"
                  style={{
                    width: "70px",
                    height: "70px",
                    background: "rgba(255,255,255,0.2)",
                    backdropFilter: "blur(6px)",
                    boxShadow: "0 4px 12px rgba(0,0,0,0.2)",
                    right: "0",
                  }}
                >
                  <i className="fa-solid fa-store fs-3"></i>
                </div>

                {/* HEADING */}
                <h2 className="fw-bold mb-2 text-white">
                  Retailer Revenue Share
                </h2>

                {/* DESCRIPTION */}
                <p className="mb-4 text-dark" style={{ opacity: 0.9 }}>
                  See how each retailer’s revenue share compares with its fair
                  share to spot over and under performers.
                </p>

                {/* INSIGHT BADGES */}
                <div className="d-flex flex-column gap-3">
                  <span
                    className="badge rounded-pill px-3 py-2"
                    style={{
                      background: "rgba(109, 54, 3, 0.39)",
                      backdropFilter: "blur(1px)",
                      fontSize: "0.9rem",
                    }}
                  >
                    <strong>Revenue Share</strong>
                  </span>

                  <span
                    className="badge rounded-pill px-3 py-2"
                    style={{
                      background: "rgba(109, 44, 3, 0.39)",
                      backdropFilter: "blur(1px)",
                      fontSize: "0.9rem",
                    }}
                  >
                    <strong>Fair Share</strong>
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div className="row g-4">
        <div className="col-lg-6">
          <div className="card shadow-sm border h-100 pe-4 py-2">
            <div className="card-body">
              <h6 className="fw-bold text-center">Retailers Wise Revenue</h6>
              <div style={{ height: 320 }}>
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={chartData} barSize={50}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="period" tick={{ fontSize: 12 }} />
                    <YAxis
                      tickFormatter={(v) => (v / 1_000_000).toFixed(1) + "M"}
                      width={70}
                      tick={{ fontSize: 12 }}
                    />
                    <Tooltip
                      formatter={(v) => (v / 1_000_000).toFixed(1) + "M"}
                    />
                    <Legend wrapperStyle={{ fontSize: 12 }} />

                    {retailers.map((m, idx) => (
                      <Bar
                        key={m}
                        dataKey={m}
                        name={m}
                        stackId="a"
                        fill={colors[idx % colors.length]}
                      ></Bar>
                    ))}
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>
        </div>
        <div className="col-lg-6">
          <div className="card shadow-sm border h-100 px-4 py-2">
            <div className="card-body">
              <h6 className="fw-bold text-center">
                Retailer Revenue Comparison
              </h6>
              <div style={{ height: 320, overflow: "auto" }}>
                <table
                  className="table table-striped-columns mt-2"
                  style={{ borderCollapse: "collapse", width: "100%" }}
                >
                  <thead>
                    <tr>
                      {revenueRetailerTable?.columns?.map((col) => (
                        <th key={col} scope="col" className="table-info">
                          {col}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {revenueRetailerTable?.rows?.map((row, rowIdx) => (
                      <tr key={rowIdx}>
                        {revenueRetailerTable?.columns?.map((col) => (
                          <td key={col} style={{ fontSize: "14px" }}>
                            {row[col]}
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

Summary.propTypes = {
  filters: PropTypes.object.isRequired,
};

export default Summary;
