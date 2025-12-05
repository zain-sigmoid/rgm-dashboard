import React, {
  useEffect,
  useMemo,
  useContext,
  useCallback,
  useState,
} from "react";
import PropTypes from "prop-types";
import { userContext } from "../../../context/userContext";
import {
  Bar,
  CartesianGrid,
  Legend,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
  LabelList,
  BarChart,
  PieChart,
  Pie,
  Cell,
  Label,
} from "recharts";
import "../styling/promo.css";
import { simulationEventFields } from "../../config/promoFields";
import { buildFields } from "../../config/buildFields";
import FilterBar from "../../pricing/components/FilterBar";
import BarLabel from "../../pricing/components/BarLabel";
import { formatVolume } from "../../config/labelFormatter";
import Spinner from "../../../components/Spinner";

const Simulation = ({ globalFilter, options, showAlert }) => {
  const {
    promoSimulation,
    runPromotionSimulation,
    promoSimState,
    setPromoSimulationState,
    resetPromotionSimulation,
  } = useContext(userContext);
  const [numEvents, setNumEvents] = useState(promoSimState.numEvents || 0);
  const [eventVal, setEventVal] = useState(
    promoSimState.numEvents ? String(promoSimState.numEvents) : ""
  );
  const [activeEvent, setActiveEvent] = useState(0);
  const [globalFilters, setGlobalFilters] = useState(
    promoSimState.globalFilters &&
      Object.keys(promoSimState.globalFilters).length
      ? promoSimState.globalFilters
      : globalFilter || {}
  );
  const emptyEvent = {
    promo_tactics: [],
    offer_type: [],
    offer_mechanic: [],
    start_date: null,
    duration: null,
    discount: null,
    redemption_rate: null,
  };
  const [eventFilters, setEventFilters] = useState(
    Array.isArray(promoSimState.eventFilters) ? promoSimState.eventFilters : []
  );

  const handleEventChange = useCallback((idx, updated) => {
    setEventFilters((prev) => {
      const next = [...prev];
      next[idx] = { ...(next[idx] || {}), ...updated };
      return next;
    });
  }, []);

  // When user sets number of events, initialize empty filter objects
  useEffect(() => {
    if (numEvents > 0) {
      setEventFilters((prev) => {
        const next = Array.isArray(prev) ? [...prev] : [];
        while (next.length < numEvents) {
          next.push({ ...emptyEvent });
        }
        return next.slice(0, numEvents);
      });
    } else {
      setEventFilters([]);
    }
  }, [numEvents]);

  // Keep global filters in sync with incoming prop when not set in state
  useEffect(() => {
    if (
      !promoSimState.globalFilters ||
      !Object.keys(promoSimState.globalFilters).length
    ) {
      setGlobalFilters(globalFilter || {});
    }
  }, [globalFilter, promoSimState.globalFilters]);

  // Persist current simulation state in context
  useEffect(() => {
    setPromoSimulationState({
      numEvents,
      eventFilters,
      globalFilters,
    });
  }, [numEvents, eventFilters, globalFilters, setPromoSimulationState]);

  const optionFields = useMemo(() => {
    const opt = options || {};
    return buildFields(simulationEventFields, opt);
  }, [options]);

  const baselineVsPromo = promoSimulation.data?.baseline_vs_promo || [];
  const pieChart = promoSimulation.data?.pie_chart;
  const table = promoSimulation.data?.df_table;
  const eventsROI = promoSimulation.data?.events || [];

  const handleSimulation = () => {
    const requiredFields = ["start_date", "duration"];

    for (let i = 0; i < eventFilters.length; i++) {
      const evt = eventFilters[i] || {};
      const eventLabel = `Event ${i + 1}`;

      // 1️⃣ Required fields: start_date, duration
      for (const field of requiredFields) {
        const val = evt[field];
        if (val === null || val === undefined || val === "") {
          const pretty = field.replace(/_/g, " ").toUpperCase();
          showAlert(`${eventLabel}: ${pretty} cannot be empty`, "danger");
          setActiveEvent(i); // jump user to the invalid event
          return;
        }
      }

      // 2️⃣ Discount: 0 <= discount <= 50
      if (
        evt.discount !== null &&
        evt.discount !== undefined &&
        evt.discount !== ""
      ) {
        const d = Number(evt.discount);
        if (Number.isNaN(d)) {
          showAlert(`${eventLabel}: Discount must be a valid number`, "danger");
          setActiveEvent(i);
          return;
        }
        if (d < 0) {
          showAlert(`${eventLabel}: Discount cannot be negative`, "danger");
          setActiveEvent(i);
          return;
        }
        if (d > 50) {
          showAlert(`${eventLabel}: Discount cannot exceed 50%`, "danger");
          setActiveEvent(i);
          return;
        }
      }

      // 3️⃣ Redemption Rate: 0 <= redemption_rate <= 100
      if (
        evt.redemption_rate !== null &&
        evt.redemption_rate !== undefined &&
        evt.redemption_rate !== ""
      ) {
        const r = Number(evt.redemption_rate);
        if (Number.isNaN(r)) {
          showAlert(
            `${eventLabel}: Redemption Rate must be a valid number`,
            "danger"
          );
          setActiveEvent(i);
          return;
        }
        if (r < 0 || r > 100) {
          showAlert(
            `${eventLabel}: Redemption Rate must be between 0 and 100`,
            "danger"
          );
          setActiveEvent(i);
          return;
        }
      }
    }
    runPromotionSimulation({
      filters: globalFilters,
      event_filters: eventFilters,
    });
  };

  return (
    <div
      className={`py-4 pe-4 ${numEvents === 0 ? "abstract-bg" : ""}`}
      id="sim"
      style={{ minHeight: "70vh" }}
    >
      <div className="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h4 className="mb-1">Simulation</h4>
        </div>
        {promoSimulation.loading && (
          <span className="badge bg-info text-dark">Loading...</span>
        )}
        {promoSimulation.error && (
          <span className="badge bg-danger">{promoSimulation.error}</span>
        )}
      </div>

      {/* Centered div when numEvents === 0 */}
      {numEvents === 0 && (
        <div
          className="d-flex justify-content-center align-items-center flex-column g-2"
          style={{
            height: "50vh",
            width: "100%",
          }}
        >
          <div className="shape-1"></div>
          <div className="shape-2"></div>
          <div className="shape-3"></div>
          <h5 className="text-muted">
            Number of events required to start simulation, atleast One
          </h5>
          <div className="d-flex flex-column gap-2 justify-content-center align-items-center my-2">
            <div
              className="input-group shadow-sm border"
              style={{
                width: "500px",
                borderRadius: "10px",
                overflow: "hidden",
              }}
            >
              <input
                type="number"
                className="form-control border-0 py-3"
                placeholder="Enter number of events..."
                min={"1"}
                style={{ fontSize: "15px" }}
                value={eventVal}
                onChange={(e) => setEventVal(Number(e.target.value))}
              />
            </div>
            <button
              className="btn btn-outline-secondary mt-3"
              onClick={() => {
                setNumEvents(eventVal);
                setActiveEvent(0);
              }}
              style={{ width: "200px" }}
              disabled={eventVal == 0}
            >
              <i
                class={`fa-solid ${
                  eventVal === 0 || eventVal === ""
                    ? "fa-circle-arrow-up"
                    : "fa-circle-check"
                } me-2`}
              ></i>
              {eventVal === 0 || eventVal === ""
                ? "Enter Events"
                : `Proceed with ${eventVal}`}
            </button>
            <div className="d-flex justify-content-between mt-2"></div>
          </div>
        </div>
      )}

      {numEvents > 0 && (
        <div>
          <div className="d-flex flex-row justify-content-between align-items-center">
            <div className="d-flex gap-3">
              {numEvents < 5 ? (
                Array.from({ length: numEvents }).map((_, idx) => (
                  <button
                    key={idx}
                    type="button"
                    className={`btn btn-sm shadow-sm ${
                      idx === activeEvent
                        ? "btn-primary"
                        : "btn-outline-secondary"
                    }`}
                    onClick={() => setActiveEvent(idx)}
                  >
                    Event Filter {idx + 1}
                  </button>
                ))
              ) : (
                <nav
                  aria-label="Event filter pagination"
                  className="p-0 m-0"
                  style={{ lineHeight: 1 }}
                >
                  <ul className="pagination mb-0">
                    {/* Previous */}
                    <li
                      className={`page-item ${
                        activeEvent <= 0 ? "disabled" : ""
                      }`}
                    >
                      <button
                        className="page-link"
                        onClick={() => {
                          if (activeEvent > 0) setActiveEvent(activeEvent - 1);
                        }}
                      >
                        Previous
                      </button>
                    </li>

                    {/* Pages */}
                    {Array.from({ length: numEvents }).map((_, idx) => (
                      <li
                        key={idx}
                        className={`page-item ${
                          idx === activeEvent ? "active" : ""
                        }`}
                      >
                        <button
                          className="page-link"
                          onClick={() => setActiveEvent(idx)}
                        >
                          {idx + 1}
                        </button>
                      </li>
                    ))}

                    {/* Next */}
                    <li
                      className={`page-item ${
                        activeEvent >= numEvents - 1 ? "disabled" : ""
                      }`}
                    >
                      <button
                        className="page-link"
                        onClick={() => {
                          if (activeEvent < numEvents - 1) {
                            setActiveEvent(activeEvent + 1);
                          }
                        }}
                      >
                        Next
                      </button>
                    </li>
                  </ul>
                </nav>
              )}
            </div>
            <div className="d-flex flex-row gap-2">
              <button
                type="button"
                className="btn btn-sm btn-outline-primary btn-sm shadow-sm"
                onClick={() => setActiveEvent(-1)}
              >
                Collapse All
              </button>
              <button
                type="button"
                className="btn btn-sm btn-outline-success btn-sm shadow-sm"
                onClick={() => {
                  setNumEvents(0);
                  setEventVal("");
                  setEventFilters([]);
                  resetPromotionSimulation();
                }}
              >
                New Simulation
              </button>
            </div>
          </div>
          {activeEvent >= 0 && (
            <div className="mt-4">
              <div className="mt-3">
                <FilterBar
                  filters={eventFilters[activeEvent] || {}}
                  onChange={(name, values) =>
                    handleEventChange(activeEvent, { [name]: values })
                  }
                  fields={optionFields}
                  eventNumber={activeEvent + 1}
                />
              </div>
              <div className="mt-3 d-flex justify-content-between">
                <button
                  type="button"
                  className="btn btn-primary"
                  disabled={promoSimulation.loading}
                  onClick={handleSimulation}
                >
                  <i className="fa-solid fa-play me-2"></i>
                  Run Simulation
                </button>
                {promoSimulation.loading && <Spinner className="me-2" />}
              </div>
            </div>
          )}
        </div>
      )}

      {numEvents > 0 && promoSimulation.data && (
        <>
          <div className="row g-3 mt-3">
            {eventsROI.map((evt) => (
              <div className="col-md-3" key={evt.promo_index}>
                <div
                  className={`glass-card d-flex flex-column justify-content-between h-100 grad-${
                    (evt.promo_index % 6) + 1
                  }`}
                >
                  <div className="fw-semibold small">
                    Event {evt.promo_index} ROI
                  </div>
                  <div className="fw-bold fs-5">{evt.roi}</div>
                </div>
              </div>
            ))}
          </div>
          <div className="row g-4 mt-4">
            <div className="col-md-6">
              <div className="card shadow-sm border h-100">
                <div className="card-body">
                  <div className="d-flex justify-content-between align-items-center mb-2">
                    <h6 className="mb-0">Baseline vs Promo Sales</h6>
                    <span className="badge bg-light text-secondary">Bar</span>
                  </div>
                  <div style={{ height: 320 }}>
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart
                        data={baselineVsPromo}
                        barGap={150}
                        barSize={60}
                        className="px-4"
                      >
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis
                          dataKey="label"
                          domain={[0, (dataMax) => dataMax * 1.1]}
                        >
                          <Label
                            value="label"
                            angle={0}
                            position="insideBottom"
                            offset={0}
                            style={{ textAnchor: "middle", fontSize: "12px" }}
                          />
                        </XAxis>
                        <YAxis
                          tickFormatter={(v) => formatVolume(v, 1)}
                          tick={{ fontSize: "12px" }}
                          domain={[0, (dataMax) => dataMax * 1.1]}
                        >
                          <Label
                            value="Volume"
                            angle={-90}
                            position="left"
                            offset={0}
                            style={{ textAnchor: "middle", fontSize: "12px" }}
                          />
                        </YAxis>
                        <Tooltip formatter={formatVolume} />
                        <Legend />

                        <Bar
                          dataKey="baseline_sales"
                          name="Baseline"
                          fill="#1E3D7D"
                          radius={[6, 6, 0, 0]}
                        >
                          <LabelList
                            dataKey="baseline_sales"
                            content={<BarLabel formatter={formatVolume} />}
                          />
                        </Bar>
                        <Bar
                          dataKey="promo_sales"
                          name="Promo Sales"
                          fill="#06C480"
                          radius={[6, 6, 0, 0]}
                        >
                          <LabelList
                            dataKey="promo_sales"
                            content={<BarLabel formatter={formatVolume} />}
                          />
                        </Bar>
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                </div>
              </div>
            </div>
            <div className="col-md-6">
              <div className="card shadow-sm border h-100">
                <div className="card-body">
                  <div className="d-flex justify-content-between align-items-center mb-2">
                    <h6 className="mb-0">Total Sales Split</h6>
                    <span className="badge bg-light text-secondary">Pie</span>
                  </div>
                  <div style={{ height: 320 }}>
                    <ResponsiveContainer width="100%" height="100%">
                      <PieChart>
                        <Pie
                          data={pieChart?.segments || []}
                          dataKey="value"
                          nameKey="name"
                          cx="50%"
                          cy="50%"
                          outerRadius={110}
                          label={({ name, value }) => formatVolume(value, 2)}
                          fontSize={12}
                        >
                          {(pieChart?.segments || []).map((entry, idx) => (
                            <Cell
                              key={`cell-${idx}`}
                              fill={idx === 0 ? "#1E3D7D" : "#06C480"}
                            />
                          ))}
                        </Pie>
                        <Legend />
                        <Tooltip formatter={(v) => formatVolume(v, 3)} />
                      </PieChart>
                    </ResponsiveContainer>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div style={{ margin: "60px 0" }}>
            <div
              className="table-responsive shadow-sm  rounded"
              style={{ maxHeight: "500px" }}
            >
              <table className="table table-sm table-striped-columns table-sticky-header">
                <thead style={{ fontSize: "15px", paddingLeft: "10px" }}>
                  <tr className="table-warning">
                    <th scope="col">#</th>
                    {(table?.columns || []).map((col) => (
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
                  {(table?.rows || []).map((row, idx) => (
                    <tr
                      key={idx}
                      className={`align-middle border border-top border-start-0 border-end-0 border-warning border-2 border-opacity-50`}
                    >
                      <th scope="row">{idx + 1}</th>
                      {(table?.columns || []).map((col) => (
                        <td key={col}>{row[col]}</td>
                      ))}
                    </tr>
                  ))}
                  {!table?.rows?.length && (
                    <tr>
                      <td colSpan={table?.columns?.length || 1}>No data</td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
            <p
              className="text-muted font-monospace mt-4"
              style={{ fontSize: "14px" }}
            >
              Total Rows: {table?.rows.length}
            </p>
          </div>
        </>
      )}
    </div>
  );
};

export default Simulation;

Simulation.defaultProps = {
  globalFilter: {},
  options: {},
};

Simulation.propTypes = {
  globalFilter: PropTypes.object,
  options: PropTypes.object,
};
