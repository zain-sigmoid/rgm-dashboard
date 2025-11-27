import React, {
  useContext,
  useEffect,
  useMemo,
  useState,
  useCallback,
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
} from "recharts";
import { userContext } from "../../../context/userContext";

const Simulation = ({ filters }) => {
  const { simulation, runSimulation } = useContext(userContext);
  const [priceChange, setPriceChange] = useState(0);
  const [newPrice, setNewPrice] = useState("");
  const [compChange, setCompChange] = useState(0);
  const [newCompPrice, setNewCompPrice] = useState("");
  const [newDistribution, setNewDistribution] = useState("");

  const cards = simulation.data?.summary_cards ?? [];
  const volumeBars = simulation.data?.volume_bars;
  const revenueBars = simulation.data?.revenue_bars;
  const context = simulation.data?.context || {};

  const basePrice = context.base_price || 0;
  const baseCompPrice = context.base_comp_price || 0;
  const baseDistribution = context.base_distribution || 0;

  console.log(simulation);

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

  useEffect(() => {
    runSimulation({ filters: mappedFilters });
  }, [mappedFilters, runSimulation]);

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
    setCompChange(value);
    if (baseCompPrice != null) {
      const updated = baseCompPrice * (1 + value / 100);
      setNewCompPrice(updated.toFixed(2));
    }
  };

  const handleNewCompPriceInputChange = (value) => {
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
    setNewPrice(basePrice != null ? basePrice.toFixed(2) : "");
    setCompChange(0);
    setNewCompPrice(baseCompPrice != null ? baseCompPrice.toFixed(2) : "");
    setNewDistribution(
      baseDistribution != null ? baseDistribution.toFixed(0) : ""
    );

    // Run simulation with baseline values
    runSimulation({
      filters: mappedFilters,
      price_change_pct: 0,
      new_price: null,
      competitor_price_change_pct: 0,
      new_competitor_price: null,
      new_distribution: null,
    });
  }, [
    basePrice,
    baseCompPrice,
    baseDistribution,
    mappedFilters,
    runSimulation,
  ]);

  // When filters change and new base values arrive, default the sliders/inputs to current values
  useEffect(() => {
    handleReset();
  }, [handleReset]);

  const handleNewDistributionInputChange = (value) => {
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

      const manualPrice =
        Number.isFinite(parseFloat(newPrice)) && parseFloat(newPrice) > 0;
      const manualComp =
        Number.isFinite(parseFloat(newCompPrice)) &&
        parseFloat(newCompPrice) > 0;
      const manualDist =
        Number.isFinite(parseFloat(newDistribution)) &&
        parseFloat(newDistribution) >= 0;

      const payload = {
        filters: mappedFilters,
        price_change_pct: priceChange,
        new_price: manualPrice ? parseFloat(newPrice) : null,
        competitor_price_change_pct: compChange,
        new_competitor_price: manualComp ? parseFloat(newCompPrice) : null,
        new_distribution: manualDist ? parseFloat(newDistribution) : null,
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

  return (
    <div className="container py-4">
      <div className="d-flex justify-content-between align-items-center mb-3">
        <h4 className="fw-bold text-muted mb-0">Simulation</h4>
        {simulation.loading && (
          <span className="badge bg-info text-dark">Loading...</span>
        )}
        {simulation.error && (
          <span className="badge bg-danger">{simulation.error}</span>
        )}
      </div>
      <form className="row g-4 mb-4 mt-3" onSubmit={handleSubmit} noValidate>
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
                      ? baseDistribution.toFixed(0)
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
          ? cards.map((card) => (
              <div className="col-md-4 col-lg-3" key={card.label}>
                <div className="card border shadow-sm h-100">
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
            <div className="card shadow-sm border h-100 pe-4 py-2">
              <div className="card-body">
                <h6 className="fw-bold mb-3">{volumeBars?.title}</h6>
                <div style={{ height: 320 }}>
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={volumeChartData} layout="vertical">
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis
                        type="number"
                        tickFormatter={(v) =>
                          (v / 1_000_000_000).toFixed(1) + "B"
                        }
                      />
                      <YAxis type="category" dataKey="label" width={120} />
                      <Tooltip
                        formatter={(v) => (v / 1_000_000_000).toFixed(5) + "B"}
                      />
                      <Legend />
                      <Bar
                        dataKey="value"
                        name="Volume"
                        fill="#0f62c2"
                        barSize={40}
                      >
                        <LabelList
                          dataKey="value"
                          position="insideRight"
                          formatter={(v) =>
                            (v / 1_000_000_000).toFixed(2) + "B"
                          }
                          fill="white"
                        />
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>
            </div>
          </div>
        ) : null}

        {revenueChartData.length ? (
          <div className="col-lg-6">
            <div className="card shadow-sm border h-100 pe-4 py-2">
              <div className="card-body">
                <h6 className="fw-bold mb-3">{revenueBars?.title}</h6>
                <div style={{ height: 320 }}>
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={revenueChartData} layout="vertical">
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis
                        type="number"
                        tickFormatter={(v) =>
                          (v / 1_000_000_000).toFixed(1) + "B"
                        }
                      />
                      <YAxis type="category" dataKey="label" width={120} />

                      <Tooltip
                        formatter={(v) => (v / 1_000_000_000).toFixed(5) + "B"}
                      />
                      <Legend />

                      <Bar
                        dataKey="value"
                        name="Revenue"
                        fill="#1e3d7d"
                        barSize={40}
                      >
                        <LabelList
                          dataKey="value"
                          position="insideRight"
                          formatter={(v) =>
                            (v / 1_000_000_000).toFixed(2) + "B"
                          }
                          fill="white"
                        />
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>
            </div>
          </div>
        ) : null}
      </div>
    </div>
  );
};

Simulation.propTypes = {
  filters: PropTypes.object.isRequired,
};

export default Simulation;
