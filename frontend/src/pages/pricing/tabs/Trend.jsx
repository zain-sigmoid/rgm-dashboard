import React, {
  useCallback,
  useEffect,
  useMemo,
  useState,
  useContext,
} from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  Label,
  ResponsiveContainer,
  CartesianGrid,
} from "recharts";
import { userContext } from "../../../context/userContext";
import PlaceholderChart from "../components/PlaceholderChart";
import MechanicsTick from "../../../components/charts/MechanicTick";
import {
  formatNumber,
  formatPercent,
  formatVolume,
} from "../../config/labelFormatter";

const Trend = ({ filters }) => {
  const { trend, fetchTrend } = useContext(userContext);
  const [dateFreq, setDateFreq] = useState("M");
  const [activeTab, setActiveTab] = useState("kpi");
  const [activeSubTab, setActiveSubTab] = useState("volume_vs_revenue");

  const payload = useMemo(
    () => ({
      categories: filters.categories || [],
      manufacturers: filters.manufacturers || [],
      brands: filters.brands || [],
      ppgs: filters.ppgs || [],
      retailers: filters.retailers || [],
      years: filters.years || [],
      months: null,
      date_freq: dateFreq,
      include_competitor:
        (filters.competitor_manufacturers?.length ||
          filters.competitor_brands?.length ||
          filters.competitor_ppgs?.length ||
          filters.competitor_retailers?.length) > 0,
      competitor_manufacturers: filters.competitor_manufacturers || [],
      competitor_brands: filters.competitor_brands || [],
      competitor_ppgs: filters.competitor_ppgs || [],
      competitor_retailers: filters.competitor_retailers || [],
      top_n: 10,
    }),
    [filters, dateFreq]
  );

  const run = useCallback(() => {
    fetchTrend(payload);
  }, [fetchTrend, payload]);

  useEffect(() => {
    run();
  }, [run]);

  const formatters = {
    volume: (v) => formatVolume(v, 1),
    revenue: (v) => formatVolume(v, 1),
    price: (v) => formatNumber(v, 2),
    distribution: (v) => formatNumber(v, 0),
    competitor_price: (v) => formatNumber(v, 2),
    competitor_distribution: (v) => formatNumber(v, 0),
  };

  const seriesByTab = useMemo(() => {
    switch (activeTab) {
      case "kpi":
        if (activeSubTab === "volume_vs_price") {
          return {
            data: trend.data?.volume_vs_price || [],
            leftKey: "volume",
            rightKey: "price",
            leftLabel: "Volume",
            rightLabel: "Price",
            title: "Volume Vs Price",
          };
        }
        if (activeSubTab === "volume_vs_distribution") {
          return {
            data: trend.data?.volume_vs_distribution || [],
            leftKey: "volume",
            rightKey: "distribution",
            leftLabel: "Volume",
            rightLabel: "Distribution",
            title: "Volume Vs Distribution",
          };
        }
        return {
          data: trend.data?.volume_vs_revenue || [],
          leftKey: "volume",
          rightKey: "revenue",
          leftLabel: "Volume",
          rightLabel: "Revenue",
          title: "Volume Vs Revenue",
        };
      case "competition":
        if (activeSubTab === "own_comp_distribution") {
          return {
            data: trend.data?.competitor_distribution || [],
            leftKey: "distribution",
            rightKey: "competitor_distribution",
            leftLabel: "Distribution",
            rightLabel: "Competitor Distribution",
            title: "Own Distribution Vs Competitor Distribution",
          };
        }
        return {
          data: trend.data?.competitor_price || [],
          leftKey: "price",
          rightKey: "competitor_price",
          leftLabel: "Price",
          rightLabel: "Competitor Price",
          title: "Own Price Vs Competitor Price",
        };
      default:
        return {
          data: [],
          leftKey: "volume",
          rightKey: "revenue",
          leftLabel: "",
          rightLabel: "",
          title: "",
        };
    }
  }, [activeSubTab, activeTab, trend.data]);

  const renderLineChart = () => {
    const d = seriesByTab.data || [];
    const leftLabel = seriesByTab.leftLabel || "";
    const rightLabel = seriesByTab.rightLabel || "";
    const leftKey = seriesByTab.leftKey || "";
    const rightKey = seriesByTab.rightKey || "";
    const leftValues = d.map((item) => item[seriesByTab.leftKey]);
    const rightValues = d.map((item) => item[seriesByTab.rightKey]);

    const minLeft = Math.min(...leftValues);
    const maxLeft = Math.max(...leftValues);

    const minRight = Math.min(...rightValues);
    const maxRight = Math.max(...rightValues);

    // Add visual padding (10% margin)
    const pad = 0.6;

    const leftDomain = [
      minLeft - (maxLeft - minLeft) * pad,
      maxLeft + (maxLeft - minLeft) * pad,
    ];

    const rightDomain = [
      minRight - (maxRight - minRight) * pad,
      maxRight + (maxRight - minRight) * pad,
    ];

    if (!d.length) {
      return <PlaceholderChart />;
    }
    return (
      <div style={{ width: "100%", height: 420 }}>
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={d}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" tick={<MechanicsTick />} />
            <YAxis
              yAxisId="left"
              tick={{ fontSize: 12 }}
              tickFormatter={formatters[leftKey]}
              domain={leftDomain}
            >
              <Label
                value={leftLabel}
                angle={-90}
                position="insideLeft"
                offset={0}
                style={{ textAnchor: "middle", fontSize: "12px" }}
              />
            </YAxis>
            <YAxis
              yAxisId="right"
              orientation="right"
              domain={rightDomain}
              tick={{ fontSize: 12 }}
              tickFormatter={formatters[rightKey]}
            >
              <Label
                value={rightLabel}
                angle={90}
                position="insideRight"
                offset={0}
                style={{ textAnchor: "middle", fontSize: "12px" }}
              />
            </YAxis>
            <Tooltip
              formatter={(value, name, props) => {
                const fmt = formatters[props.dataKey] || ((v) => v);
                return [fmt(value), name];
              }}
            />
            <Legend />
            <Line
              yAxisId="left"
              type="monotone"
              dataKey={seriesByTab.leftKey}
              stroke="#0d6efd"
              dot={false}
              strokeWidth={2}
              name={seriesByTab.leftLabel}
            />
            <Line
              yAxisId="right"
              type="monotone"
              dataKey={seriesByTab.rightKey}
              stroke="#198754"
              dot={false}
              strokeWidth={2}
              name={seriesByTab.rightLabel}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    );
  };

  const topTable = trend.data?.top_table || [];
  const formatTitle = (str) => {
    let result = str.replace(/_/g, " ");
    result = result.replace(/\b\w/g, (c) => c.toUpperCase());
    return result.replace("Vs", "vs"); // fix casing for vs
  };

  return (
    <div className="py-4 pe-4">
      <div className="d-flex justify-content-between align-items-center mb-3">
        <h4 className="mb-1">Trend Analysis</h4>
        {trend.loading && (
          <span className="badge bg-info text-dark">Loading...</span>
        )}
        {trend.error && <span className="badge bg-danger">{trend.error}</span>}
      </div>

      <div className="d-flex justify-content-between flex-row mb-3">
        <div className="d-flex gap-2 mb-3">
          <button
            type="button"
            className={`btn ${
              activeTab === "kpi" ? "btn-primary" : "btn-outline-secondary"
            }`}
            onClick={() => {
              setActiveTab("kpi");
              setActiveSubTab("volume_vs_revenue");
            }}
          >
            KPI Trend
          </button>
          <button
            className={`btn ${
              activeTab === "competition"
                ? "btn-primary"
                : "btn-outline-secondary"
            }`}
            onClick={() => {
              setActiveTab("competition");
              setActiveSubTab("own_comp_price");
            }}
            disabled={
              !payload.include_competitor ||
              (!payload.competitor_manufacturers.length &&
                !payload.competitor_brands.length &&
                !payload.competitor_ppgs.length &&
                !payload.competitor_retailers.length)
            }
          >
            Comparison VS Competition
          </button>
        </div>

        <div className="mb-4">
          {activeTab === "kpi" ? (
            <>
              <div class="btn-group">
                <button
                  type="button"
                  class="btn btn-outline-primary dropdown-toggle"
                  data-bs-toggle="dropdown"
                  aria-expanded="false"
                >
                  {formatTitle(activeSubTab)}
                </button>
                <ul class="dropdown-menu">
                  <li>
                    <a
                      class="dropdown-item"
                      href="#"
                      onClick={() => setActiveSubTab("volume_vs_revenue")}
                    >
                      Volume vs Revenue
                    </a>
                  </li>
                  <li>
                    <a
                      class="dropdown-item"
                      href="#"
                      onClick={() => setActiveSubTab("volume_vs_price")}
                    >
                      Volume vs price
                    </a>
                  </li>
                  <li>
                    <a
                      class="dropdown-item"
                      href="#"
                      onClick={() => setActiveSubTab("volume_vs_distribution")}
                    >
                      Volume vs Distribution
                    </a>
                  </li>
                </ul>
              </div>
            </>
          ) : (
            <>
              <div class="btn-group">
                <button
                  type="button"
                  class="btn btn-outline-primary dropdown-toggle"
                  data-bs-toggle="dropdown"
                  aria-expanded="false"
                >
                  {formatTitle(activeSubTab)}
                </button>
                <ul class="dropdown-menu">
                  <li>
                    <a
                      class="dropdown-item"
                      href="#"
                      onClick={() => setActiveSubTab("own_comp_price")}
                    >
                      Own Price Vs Competitor Price
                    </a>
                  </li>
                  <li>
                    <a
                      class="dropdown-item"
                      href="#"
                      onClick={() => setActiveSubTab("own_comp_distribution")}
                    >
                      Own Distribution Vs Competitor Distribution
                    </a>
                  </li>
                </ul>
              </div>
            </>
          )}
        </div>
      </div>

      <div className="row g-4">
        <div className="col-lg-12">
          <div className="card shadow-sm border h-100">
            <div className="card-body">
              <h6 className="fw-bold mb-3">{seriesByTab.title}</h6>
              {renderLineChart()}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Trend;
