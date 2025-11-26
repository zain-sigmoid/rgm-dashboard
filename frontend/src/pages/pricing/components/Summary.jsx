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

const Summary = ({ filters }) => {
  const { summary, fetchSummary } = useContext(userContext);

  useEffect(() => {
    fetchSummary(filters);
  }, [filters, fetchSummary]);

  const cards = useMemo(() => summary.data?.kpis ?? [], [summary.data]);
  const fairShare = summary.data?.fair_share_vs_revenue ?? [];
  const revenueSeries = summary.data?.revenue_by_manufacturer ?? [];
  const revenueTable = summary.data?.revenue_table?.rows ?? [];
  const revenueColumns = summary.data?.revenue_table?.columns ?? [];
  const revenueRetailer = summary.data?.revenue_by_retailer?.items ?? [];

  console.log(summary, revenueRetailer);
  console.log(fairShare);

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

  const stackedData = useMemo(() => {
    const map = {};

    revenueChartData.forEach(({ period, manufacturer, revenue }) => {
      if (!map[period]) map[period] = { period };
      map[period][manufacturer] = revenue;
    });

    return Object.values(map);
  }, [revenueChartData]);
  const colors = ["#e53935", "#fb8c00", "#43a047", "#1e88e5", "#6d4c41"];

  return (
    <div className="container py-4">
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

      <div className="row g-3 mb-4">
        {cards.map((card) => (
          <div className="col-md-3" key={card.label}>
            <div className="card shadow-sm border-0 h-100">
              <div className="card-body">
                <div className="text-muted small">{card.label}</div>
                <div className="fs-4 fw-bold">{card.value}</div>
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="row g-4">
        <div className="col-lg-4">
          <div className="card shadow-sm border-0 h-100">
            <div className="card-body">
              <h6 className="fw-bold mb-3">Revenue Share vs Fair Share</h6>
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
                        position="insideRight"
                        fill="#ffffff"
                        formatter={(value) => `${value.toFixed(2)}%`}
                        fontSize={12}
                      />
                    </Bar>
                    <Bar
                      dataKey="fair_share"
                      name="Fair Share %"
                      fill="#6aa6ff"
                    >
                      <LabelList
                        dataKey="fair_share"
                        position="insideRight"
                        fill="#ffffff"
                        formatter={(value) => `${value.toFixed(2)}%`}
                        fontSize={12}
                      />
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>
        </div>

        <div className="col-lg-4">
          <div className="card shadow-sm border-0 h-100">
            <div className="card-body">
              <h6 className="fw-bold mb-3">Revenue by Manufacturer</h6>
              <div style={{ height: 320 }}>
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={stackedData} barSize={50}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="period" tick={{ fontSize: 12 }} />
                    <YAxis />
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
        <div className="col-lg-4">
          <div className="card shadow-sm border h-100">
            <div className="card-body">
              <h6>Manufacturer Revenue Comparison</h6>
              <div style={{ height: 320 }}>
                <table style={{ borderCollapse: "collapse", width: "100%" }}>
                  <thead>
                    <tr>
                      {revenueColumns.map((col) => (
                        <th
                          key={col}
                          style={{
                            border: "1px solid #ddd",
                            padding: "8px",
                            textAlign: "left",
                            backgroundColor: "#f5f5f5",
                            fontWeight: "600",
                          }}
                        >
                          {col}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {revenueTable.map((row, rowIdx) => (
                      <tr key={rowIdx}>
                        {revenueColumns.map((col) => (
                          <td
                            key={col}
                            style={{ border: "1px solid #ddd", padding: "8px" }}
                          >
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
      <div className="row g-4 mt-3">
        <div className="col-lg-4">
          <div className="card shadow-sm border-0 h-100">
            <div className="card-body">
              <h6 className="fw-bold mb-3">Retailer Revenue Share</h6>
              <div style={{ height: 320 }}>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart
                    data={revenueRetailer}
                    layout="vertical"
                    barSize={18}
                  >
                    <CartesianGrid strokeDasharray="3 3" />

                    {/* Y-axis: retailers */}
                    <YAxis
                      dataKey="retailer_id"
                      type="category"
                      width={100}
                      tick={{ fontSize: 12 }}
                    />

                    {/* X-axis: revenue */}
                    <XAxis
                      type="number"
                      tickFormatter={(v) => (v / 1_000_000).toFixed(0) + "M"}
                    />

                    <Tooltip
                      formatter={(v) => (v / 1_000_000).toFixed(2) + "M"}
                    />
                    <Legend wrapperStyle={{ fontSize: 12 }} />

                    <Bar dataKey="2022" name="2022" fill="#ff7043">
                      <LabelList
                        dataKey="2022"
                        position="insideRight"
                        fill="#ffffff"
                        formatter={(v) => (v / 1_000_000).toFixed(1) + "M"}
                        fontSize={12}
                      />
                    </Bar>

                    <Bar dataKey="2023" name="2023" fill="#ffa726">
                      <LabelList
                        dataKey="2023"
                        position="insideRight"
                        fill="#ffffff"
                        formatter={(v) => (v / 1_000_000).toFixed(1) + "M"}
                        fontSize={12}
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
  );
};

Summary.propTypes = {
  filters: PropTypes.object.isRequired,
};

export default Summary;
