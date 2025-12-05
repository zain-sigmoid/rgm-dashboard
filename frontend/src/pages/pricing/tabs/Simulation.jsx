import React, {
  useContext,
  useEffect,
  useMemo,
  useState,
  useCallback,
  useRef,
} from "react";
import PropTypes from "prop-types";
import {
  BarChart,
  Bar,
  CartesianGrid,
  Legend,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
  LabelList,
  Label,
} from "recharts";
import { userContext } from "../../../context/userContext";
import BarLabel from "../../pricing/components/BarLabel";
import { formatVolume } from "../../config/labelFormatter";
import "../styling/style.css";

const Simulation = ({ filters }) => {
  const grads = ["grad-1", "grad-2", "grad-3", "grad-4", "grad-5", "grad-6"];
  const { simulation, runSimulation } = useContext(userContext);
  const [priceChange, setPriceChange] = useState(0);
  const [newPrice, setNewPrice] = useState(0.0);
  const [compChange, setCompChange] = useState(0);
  const [newCompPrice, setNewCompPrice] = useState(0.0);
  const [newDistribution, setNewDistribution] = useState(0.0);

  console.log(newPrice, newCompPrice, newDistribution);

  const cards = simulation.data?.summary_cards ?? [];
  const volumeBars = simulation.data?.volume_bars;
  const revenueBars = simulation.data?.revenue_bars;
  const table = simulation.data?.table;
  const contextTable = simulation.data?.context_table;
  const context = simulation.data?.context || {};

  const basePrice = context.base_price || 0;
  const baseCompPrice = context.base_comp_price || 0;
  const baseDistribution = context.base_distribution || 0;
  const lastFiltersRef = useRef("");

  const mappedFilters = useMemo(
    () => ({
      categories: filters?.categories || [],
      manufacturers: filters?.manufacturers || [],
      brands: filters?.brands || [],
      ppgs: filters?.ppgs || [],
      retailers: filters?.retailers || [],
    }),
    [
      filters?.categories,
      filters?.manufacturers,
      filters?.brands,
      filters?.ppgs,
      filters?.retailers,
    ]
  );

  const mappedFiltersKey = useMemo(
    () => JSON.stringify(mappedFilters),
    [mappedFilters]
  );

  useEffect(() => {
    if (mappedFiltersKey !== lastFiltersRef.current) {
      lastFiltersRef.current = mappedFiltersKey;
      runSimulation({
        filters: mappedFilters,
        price_change_pct: 0,
        new_price: 0.0,
        competitor_price_change_pct: 0,
        new_competitor_price: 0.0,
        new_distribution: 0.0,
      });
    }
  }, [mappedFiltersKey, mappedFilters, runSimulation]);

  const volumeChartData = useMemo(() => volumeBars?.bars ?? [], [volumeBars]);
  const revenueChartData = useMemo(
    () => revenueBars?.bars ?? [],
    [revenueBars]
  );
  const handlePriceSliderChange = (value) => {
    setPriceChange(value);
    if (basePrice != null) {
      const updated = basePrice * (1 + value / 100);
      setNewPrice(updated.toFixed(2));
    }
  };

  const handleNewPriceInputChange = (value) => {
    setNewPrice(value);
    if (basePrice != null && value !== "") {
      const numeric = parseFloat(value);
      if (!isNaN(numeric) && basePrice !== 0) {
        const pct = ((numeric - basePrice) / basePrice) * 100;
        setPriceChange(parseFloat(pct.toFixed(2)));
      }
    }
  };

  // -------- Competitor card logic --------
  const handleCompSliderChange = (value) => {
    console.log("new price", value);
    setCompChange(value);
    if (baseCompPrice != null) {
      const updated = baseCompPrice * (1 + value / 100);
      setNewCompPrice(updated.toFixed(2));
    }
  };

  const handleNewCompPriceInputChange = (value) => {
    console.log("new comp price", value);
    setNewCompPrice(value);
    if (baseCompPrice != null && value !== "") {
      const numeric = parseFloat(value);
      if (!isNaN(numeric) && baseCompPrice !== 0) {
        const pct = ((numeric - baseCompPrice) / baseCompPrice) * 100;
        setCompChange(parseFloat(pct.toFixed(2)));
      }
    }
  };

  const handleReset = useCallback(() => {
    setPriceChange(0);
    setNewPrice(basePrice != null ? basePrice.toFixed(2) : 0.0);
    setCompChange(0);
    setNewCompPrice(baseCompPrice != null ? baseCompPrice.toFixed(2) : 0.0);
    setNewDistribution(
      baseDistribution != null ? baseDistribution.toFixed(2) : 0.0
    );
  }, [
    basePrice,
    baseCompPrice,
    baseDistribution,
    mappedFilters,
  ]);

  // When filters change and new base values arrive, default the sliders/inputs to current values
  useEffect(() => {
    handleReset();
  }, [handleReset]);

  const handleNewDistributionInputChange = (value) => {
    console.log("new dist value", value);
    setNewDistribution(value);
  };

  const handleSubmit = useCallback(
    (e) => {
      if (e) e.preventDefault();
      const mappedFilters = {
        manufacturers: filters?.manufacturers || [],
        brands: filters?.brands || [],
        ppgs: filters?.ppgs || [],
        retailers: filters?.retailers || [],
      };
      const numericPrice = Number.parseFloat(newPrice);
      const numericComp = Number.parseFloat(newCompPrice);
      const numericDist = Number.parseFloat(newDistribution);

      const payload = {
        filters: mappedFilters,
        price_change_pct: priceChange,
        new_price: Number.isFinite(numericPrice) ? numericPrice : 0.0,
        competitor_price_change_pct: compChange,
        new_competitor_price: Number.isFinite(numericComp) ? numericComp : 0.0,
        new_distribution: Number.isFinite(numericDist) ? numericDist : 0.0,
      };

      runSimulation(payload);
    },
    [
      compChange,
      filters?.brands,
      filters?.manufacturers,
      filters?.ppgs,
      filters?.retailers,
      newCompPrice,
      newDistribution,
      newPrice,
      priceChange,
      runSimulation,
    ]
  );

  const renderBarCard = useCallback((data, title, color) => {
    if (!data?.length) return null;
    return (
      <div className="card shadow-sm border h-100 pe-4 py-2">
        <div className="card-body">
          <h6 className="fw-bold mb-3">{title}</h6>
          <div style={{ height: 320 }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis
                  type="number"
                  tickFormatter={(v) => formatVolume(v, 0)}
                  tick={{ fontSize: "12px" }}
                >
                  <Label
                    value="volume"
                    angle={0}
                    position="insideBottom"
                    offset={0}
                    style={{ textAnchor: "middle", fontSize: "12px" }}
                  />
                </XAxis>
                <YAxis
                  type="category"
                  dataKey="label"
                  width={120}
                  tick={{ fontSize: "12px" }}
                />
                <Tooltip formatter={(v) => formatVolume(v, 5)} />
                <Legend />
                <Bar
                  dataKey="value"
                  fill={color}
                  barSize={40}
                  radius={[0, 6, 6, 0]}
                >
                  <LabelList
                    dataKey="value"
                    content={
                      <BarLabel
                        fontSize={14}
                        formatter={(v) => formatVolume(v, 2)}
                      />
                    }
                  />
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    );
  }, []);

  const renderTable = (tableData, title, bg = "info") => {
    if (!tableData?.columns?.length) return null;
    return (
      // <div className="card shadow-sm border h-100 p-3">
      //   <div className="card-body">
      //     <div className="d-flex justify-content-between align-items-center mb-2">
      //       <h6 className="mb-0">{title}</h6>
      //       <span className="badge bg-light text-secondary">Table</span>
      //     </div>

      //   </div>
      // </div>
      <div
        className="table-responsive shadow-sm rounded"
        style={{ maxHeight: "500px" }}
      >
        <table className="table table-sm table-striped-columns table-sticky-header">
          <thead style={{ fontSize: "15px", paddingLeft: "10px" }}>
            <tr className={`table-${bg}`}>
              <th scope="col">#</th>
              {tableData.columns.map((col) => (
                <th key={col} className="text-capitalize">
                  {col.replace(/_/g, " ")}
                </th>
              ))}
            </tr>
          </thead>
          <tbody
            style={{ fontSize: "12px", paddingLeft: "10px" }}
            className="table-group-divider"
          >
            {tableData.rows?.length ? (
              tableData.rows.map((row, idx) => (
                <tr
                  key={idx}
                  className={`align-middle border border-top border-start-0 border-end-0 border-${bg} border-2 border-opacity-50`}
                >
                  <th scope="row">{idx + 1}</th>
                  {tableData.columns.map((col) => (
                    <td key={col}>{row[col]}</td>
                  ))}
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan={tableData.columns.length}>No data</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    );
  };

  return (
    <div className="py-4 pe-4">
      <div className="d-flex justify-content-between align-items-center mb-3">
        <h4 className="mb-1">Simulation</h4>
        {simulation.loading && (
          <span className="badge bg-info text-dark">Loading...</span>
        )}
        {simulation.error && (
          <span className="badge bg-danger">{simulation.error}</span>
        )}
      </div>
      <form className="row g-4 mb-4" onSubmit={handleSubmit} noValidate>
        {/* Price Change Card */}
        <div className="col-lg-4 col-md-6">
          <div className="card shadow-sm border h-100">
            <div className="card-body">
              <div className="d-flex align-items-center justify-content-between mb-3">
                <i class="fa-solid fa-hand-holding-dollar fa-lg me-2 text-warning"></i>
                <div className="d-flex align-items-center">
                  <h6 className="fw-semibold text-secondary mb-0">
                    Price Change
                  </h6>
                </div>
              </div>

              {/* Current vs New */}
              <div className="d-flex justify-content-between align-items-end mb-2">
                <div>
                  <div className="text-muted small">Current</div>
                  <div className="fs-5 fw-bold">
                    {basePrice != null ? basePrice.toFixed(2) : "–"}
                  </div>
                </div>
                <div className="text-end">
                  <div className="text-muted small">New</div>
                  <div className="fs-5 fw-bold text-primary">
                    {newPrice || "—"}
                  </div>
                </div>
              </div>

              {/* Slider + % */}
              <div className="d-flex justify-content-between align-items-center mb-1">
                <span className="text-muted small">Change (%)</span>
                <span className="fw-bold">{priceChange.toFixed(2)}%</span>
              </div>
              <input
                type="range"
                className="form-range"
                min={-20}
                max={20}
                step={0.5}
                value={priceChange}
                onChange={(e) =>
                  handlePriceSliderChange(parseFloat(e.target.value))
                }
              />

              {/* New price input (small) */}
              <label className="form-label mt-2 small fw-semibold mb-1">
                Override Price (optional)
              </label>
              <input
                type="number"
                className="form-control form-control-sm w-75"
                placeholder="Enter new price"
                value={newPrice}
                onChange={(e) => handleNewPriceInputChange(e.target.value)}
                min={0}
                step={0.1}
                inputMode="decimal"
              />
            </div>
          </div>
        </div>

        {/* Competitor Price Change Card */}
        <div className="col-lg-4 col-md-6">
          <div className="card shadow-sm border h-100">
            <div className="card-body">
              <div className="d-flex justify-content-between align-items-center mb-3">
                <i class="fa-solid fa-people-arrows-left-right fa-lg me-3 text-danger"></i>
                <div className="d-flex align-items-center">
                  <h6 className="fw-semibold text-secondary mb-0">
                    Competitor Price
                  </h6>
                </div>
              </div>

              {/* Current vs New */}
              <div className="d-flex justify-content-between align-items-end mb-2">
                <div>
                  <div className="text-muted small">Current</div>
                  <div className="fs-5 fw-bold">
                    {baseCompPrice != null ? baseCompPrice.toFixed(2) : "–"}
                  </div>
                </div>
                <div className="text-end">
                  <div className="text-muted small">New</div>
                  <div className="fs-5 fw-bold text-primary">
                    {newCompPrice || "—"}
                  </div>
                </div>
              </div>

              {/* Slider + % */}
              <div className="d-flex justify-content-between align-items-center mb-1">
                <span className="text-muted small">Change (%)</span>
                <span className="fw-bold">{compChange.toFixed(2)}%</span>
              </div>
              <input
                type="range"
                className="form-range"
                min={-20}
                max={20}
                step={0.5}
                value={compChange}
                onChange={(e) =>
                  handleCompSliderChange(parseFloat(e.target.value))
                }
              />

              {/* New competitor price input (small) */}
              <label className="form-label mt-2 small fw-semibold mb-1">
                Override Competitor Price (optional)
              </label>
              <input
                type="number"
                className="form-control form-control-sm w-75"
                placeholder="Enter competitor price"
                value={newCompPrice}
                onChange={(e) => handleNewCompPriceInputChange(e.target.value)}
                min={0}
                step={0.1}
              />
            </div>
          </div>
        </div>

        {/* Distribution Card */}
        <div className="col-lg-4 col-md-6">
          <div className="card shadow-sm border h-100">
            <div className="card-body">
              <div className="d-flex justify-content-between align-items-center mb-3">
                <i className="fa-solid fa-diagram-project fa-lg me-3 text-success "></i>
                <div className="d-flex align-items-center">
                  <h6 className="fw-semibold text-secondary mb-0">
                    Distribution
                  </h6>
                </div>
              </div>

              {/* Current vs New */}
              <div className="d-flex justify-content-between align-items-end mb-2">
                <div>
                  <div className="text-muted small">Current</div>
                  <div className="fs-5 fw-bold">
                    {baseDistribution != null
                      ? baseDistribution.toFixed(2)
                      : "–"}
                  </div>
                </div>
                <div className="text-end">
                  <div className="text-muted small">New</div>
                  <div className="fs-5 fw-bold text-primary">
                    {newDistribution ? `${newDistribution}` : "—"}
                  </div>
                </div>
              </div>
              <label className="form-label small fw-semibold mb-1">
                New Distribution
              </label>
              <input
                type="number"
                className="form-control form-control-sm w-50"
                placeholder="Leave blank to keep current"
                value={newDistribution}
                onChange={(e) =>
                  handleNewDistributionInputChange(e.target.value)
                }
                min={0}
                max={100}
                step={1}
              />

              <div className="d-flex flex-row gap-2">
                <button
                  type="submit"
                  className="btn btn-primary w-100 mt-4 fw-bold"
                >
                  Run Simulation
                </button>
                <button
                  type="button"
                  className="btn btn-outline-secondary w-100 mt-4 fw-bold"
                  onClick={handleReset}
                >
                  Reset
                </button>
              </div>
            </div>
          </div>
        </div>
      </form>

      <div className="row g-3 mb-4 mt-4">
        {cards.length > 0
          ? cards.map((card, idx) => (
              <div className="col-md-4 col-lg-3" key={card.label}>
                <div
                  className={`glass-card border shadow-sm h-100 ${
                    grads[idx % grads.length]
                  }`}
                >
                  <div className="card-body">
                    <div className="text-muted small">{card.label}</div>
                    <div className="fs-5 fw-bold">{card.value}</div>
                  </div>
                </div>
              </div>
            ))
          : [...Array(7)].map((_, idx) => (
              <div className="col-md-4 col-lg-3" key={idx}>
                <div className="card border shadow-sm h-100">
                  <div className="card-body placeholder-glow">
                    <div className="placeholder placeholder-sm col-6 mb-2 d-block"></div>
                    <div className="placeholder placeholder-xs col-4 d-block"></div>
                  </div>
                </div>
              </div>
            ))}
      </div>

      <div className="row g-4 mb-4 mt-4">
        {volumeChartData.length ? (
          <div className="col-lg-6">
            {renderBarCard(volumeChartData, volumeBars?.title, "#0f62c2")}
          </div>
        ) : null}
        {revenueChartData.length ? (
          <div className="col-lg-6">
            {renderBarCard(revenueChartData, revenueBars?.title, "#1e3d7d")}
          </div>
        ) : null}
      </div>

      <div className="row g-4 mt-4">
        <h3 className="fw-bold text-muted text-center">Tables</h3>
        <div className="col-md-12">
          {renderTable(contextTable, "Context", "success")}
        </div>
        <div className="col-md-12">
          {renderTable(table, "Simulation Results", "danger")}
        </div>
      </div>
    </div>
  );
};

Simulation.propTypes = {
  filters: PropTypes.object.isRequired,
};

export default Simulation;
