import React, { useState } from "react";
import Plot from "react-plotly.js";
import { computeDescriptive } from "../api/descriptive";

export default function DescriptivePage(){
  const [ppg, setPpg] = useState([]);
  const [retailer, setRetailer] = useState([]);
  const [year, setYear] = useState([]);
  const [fig, setFig] = useState(null);
  const [rows, setRows] = useState([]);
  const [loading, setLoading] = useState(false);

  async function run() {
    setLoading(true);
    const payload = {
      ppg: ppg.length ? ppg : null,
      retailer: retailer.length ? retailer : null,
      year: year.length ? year : null,
      top_n: 10,
      date_freq: "M"
    };
    try {
      const data = await computeDescriptive(payload);
      setFig(data.fig);
      setRows(data.top_table);
    } catch (e) {
      console.error(e);
      alert("API error");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={{padding:20}}>
      <h2>Descriptive Analysis</h2>
      {/* Replace the inputs below with multiselect components */}
      <div>
        <input placeholder="ppg comma separated" onBlur={(e)=>setPpg(e.target.value.split(',').map(s=>s.trim()))}/>
        <input placeholder="retailer comma separated" onBlur={(e)=>setRetailer(e.target.value.split(',').map(s=>s.trim()))}/>
        <input placeholder="year comma separated" onBlur={(e)=>setYear(e.target.value.split(',').map(s=>s.trim()))}/>
        <button onClick={run} disabled={loading}>{loading? "Running..." : "Run"}</button>
      </div>
      {fig && <Plot data={fig.data} layout={fig.layout} />}
      <pre>{JSON.stringify(rows,null,2)}</pre>
    </div>
  );
}
