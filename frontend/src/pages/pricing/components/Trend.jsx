import React, { useState, useEffect, useContext } from "react";
import { UserStateContext } from "../../context/UserState"; 
import FilterBar from "./components/FilterBar"; 
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  ResponsiveContainer,
  CartesianGrid
} from "recharts";

export default function Trend() {
  const userCtx = useContext(UserStateContext || {});

  // Filters
  const [ppg, setPpg] = useState([]); // array of strings
  const [retailer, setRetailer] = useState([]);
  const [year, setYear] = useState([]);
  const [month, setMonth] = useState([]);
  const [freq, setFreq] = useState("M"); // 'M' or 'D'

  // Data & UI state
  const [chartData, setChartData] = useState(null);
  const [topTable, setTopTable] = useState([]);
  const [rowCount, setRowCount] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Build API payload from current filters
  const buildPayload = () => ({
    ppg: ppg && ppg.length ? ppg : null,
    retailer: retailer && retailer.length ? retailer : null,
    year: year && year.length ? year : null,
    month: month && month.length ? month : null,
    date_freq: freq,
    top_n: 10
  });

  // Primary fetch function: tries context first, then fallback
  const fetchTrend = async () => {
    setLoading(true);
    setError(null);

    try {
      const payload = buildPayload();
      let resp = null;

      // 1) Preferred: context method fetchTrend
      if (userCtx && typeof userCtx.fetchTrend === "function") {
        resp = await userCtx.fetchTrend(payload);
      }
      // 2) Alternate: context.api.computeTrend or computeDescriptive
      else if (userCtx && userCtx.api && typeof userCtx.api.computeTrend === "function") {
        resp = await userCtx.api.computeTrend(payload);
      } else if (userCtx && userCtx.api && typeof userCtx.api.computeDescriptive === "function") {
        resp = await userCtx.api.computeDescriptive(payload);
      }
      // 3) Fallback: direct fetch to backend endpoint (trend)
      else {
        const base = process.env.REACT_APP_API_BASE || import.meta.env.VITE_API_BASE || "http://localhost:8000/api";
        const res = await fetch(`${base}/trend/compute`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        });
        if (!res.ok) {
          const text = await res.text();
          throw new Error(`API error ${res.status}: ${text}`);
        }
        resp = await res.json();
      }

      // Normalize timeseries structure for recharts:
      // Ensure each row has date, volume (numeric), revenue (numeric)
      const timeseries = (resp && resp.timeseries) ? resp.timeseries.map((r) => ({
        ...r,
        volume: r.volume !== undefined ? Number(r.volume) : 0,
        revenue: r.revenue !== undefined ? Number(r.revenue) : 0,
        date: r.date // expect ISO string like 'YYYY-MM-DD'
      })) : [];

      setChartData(timeseries);
      setTopTable(resp?.top_table || []);
      setRowCount(resp?.row_count || 0);
    } catch (err) {
      console.error("Trend fetch error:", err);
      setError(err.message || "Failed to fetch trend");
      setChartData(null);
      setTopTable([]);
      setRowCount(0);
    } finally {
      setLoading(false);
    }
  };

  // Optional: run once on mount (comment/uncomment based on preference)
  // useEffect(() => { fetchTrend(); }, []);

  return (
    <div className="container-fluid py-3">
      {/* Header */}
      <div className="row mb-2">
        <div className="col-12 d-flex justify-content-between align-items-center">
          <h3 className="text-primary">Trend Analysis</h3>
          <div><small className="text-muted">Rows: {rowCount}</small></div>
        </div>
      </div>

      {/* Filters */}
      <div className="row mb-3">
        <div className="col-lg-9">
          {/* FILTER BAR - adapt props if your FilterBar API differs */}
          <FilterBar
            ppgValue={ppg}
            onPpgChange={setPpg}
            retailerValue={retailer}
            onRetailerChange={setRetailer}
            yearValue={year}
            onYearChange={setYear}
            monthValue={month}
            onMonthChange={setMonth}
            // FilterBar can trigger apply; we forward fetchTrend as onApply
            onApply={() => fetchTrend()}
            showApplyButton={true}
            showResetButton={true}
          />
        </div>

        <div className="col-lg-3 d-flex align-items-end">
          <div className="w-100">
            <label className="form-label">Frequency</label>
            <select className="form-select mb-2" value={freq} onChange={(e) => setFreq(e.target.value)}>
              <option value="M">Monthly</option>
              <option value="D">Daily</option>
            </select>

            <button className="btn btn-primary w-100" onClick={fetchTrend} disabled={loading}>
              {loading ? (
                <>
                  <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                  Running...
                </>
              ) : (
                "Run"
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Chart + Top table */}
      <div className="row">
        {/* Chart column */}
        <div className="col-lg-8 mb-3">
          <div className="card h-100">
            <div className="card-body">
              <h5 className="card-title">Volume & Revenue</h5>

              {error && <div className="alert alert-danger">{error}</div>}

              {!chartData && !loading && !error && (
                <div className="text-muted">No data — select filters and click Run</div>
              )}

              {loading && (
                <div className="d-flex justify-content-center align-items-center" style={{ minHeight: 240 }}>
                  <div className="spinner-border text-primary" role="status">
                    <span className="visually-hidden">Loading...</span>
                  </div>
                </div>
              )}

              {chartData && !loading && (
                <div style={{ width: "100%", height: 420 }}>
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={chartData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="date" tick={{ fontSize: 12 }} />
                      {/* Left axis for volume */}
                      <YAxis yAxisId="left" tick={{ fontSize: 12 }} />
                      {/* Right axis for revenue */}
                      <YAxis yAxisId="right" orientation="right" tick={{ fontSize: 12 }} />
                      <Tooltip />
                      <Legend />
                      <Line yAxisId="left" type="monotone" dataKey="volume" stroke="#0d6efd" dot={false} strokeWidth={2} name="Volume" />
                      <Line yAxisId="right" type="monotone" dataKey="revenue" stroke="#198754" dot={false} strokeWidth={2} name="Revenue" />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Table column */}
        <div className="col-lg-4 mb-3">
          <div className="card h-100">
            <div className="card-body">
              <h5 className="card-title">Top Table</h5>
              {topTable && topTable.length > 0 ? (
                <div style={{ maxHeight: 380, overflowY: "auto" }}>
                  <table className="table table-sm table-striped">
                    <thead>
                      <tr>
                        {Object.keys(topTable[0]).map((h) => (
                          <th key={h}>{h}</th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {topTable.map((row, idx) => (
                        <tr key={idx}>
                          {Object.keys(row).map((k) => (
                            <td key={k}>{String(row[k])}</td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <div className="text-muted">No top table data</div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
