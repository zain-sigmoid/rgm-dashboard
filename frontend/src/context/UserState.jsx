import React, { useCallback, useMemo, useReducer } from "react";
import PropTypes from "prop-types";
import { userContext } from "./userContext";

const API_BASE =
  import.meta.env.VITE_API_BASE?.replace(/\/$/, "") || "http://127.0.0.1:8000";

const initialState = {
  options: { data: null, loading: false, error: null, fetched: false },
  summary: { data: null, loading: false, error: null, fetched: false },
  simulation: { data: null, loading: false, error: null, fetched: false },
};

function reducer(state, action) {
  switch (action.type) {
    case "OPTIONS_START":
      return { ...state, options: { data: state.options.data, loading: true, error: null, fetched: true } };
    case "OPTIONS_SUCCESS":
      return { ...state, options: { data: action.payload, loading: false, error: null, fetched: true } };
    case "OPTIONS_ERROR":
      return { ...state, options: { data: null, loading: false, error: action.payload, fetched: true } };
    case "SUMMARY_START":
      return {
        ...state,
        summary: { data: state.summary.data, loading: true, error: null, fetched: true },
      };
    case "SUMMARY_SUCCESS":
      return { ...state, summary: { data: action.payload, loading: false, error: null, fetched: true } };
    case "SUMMARY_ERROR":
      return { ...state, summary: { data: null, loading: false, error: action.payload, fetched: true } };
    case "SIM_START":
      return {
        ...state,
        simulation: { data: state.simulation.data, loading: true, error: null, fetched: true },
      };
    case "SIM_SUCCESS":
      return { ...state, simulation: { data: action.payload, loading: false, error: null, fetched: true } };
    case "SIM_ERROR":
      return { ...state, simulation: { data: null, loading: false, error: action.payload, fetched: true } };
    default:
      return state;
  }
}

const UserState = ({ children }) => {
  const [state, dispatch] = useReducer(reducer, initialState);

  const fetchOptions = useCallback(async () => {
    dispatch({ type: "OPTIONS_START" });
    try {
      const res = await fetch(`${API_BASE}/api/pricing/options`);
      if (!res.ok) throw new Error(`Options request failed: ${res.statusText}`);
      const data = await res.json();
      dispatch({ type: "OPTIONS_SUCCESS", payload: data });
      return data;
    } catch (err) {
      dispatch({ type: "OPTIONS_ERROR", payload: err.message });
      return null;
    }
  }, []);

  const fetchSummary = useCallback(async (filters = {}) => {
    dispatch({ type: "SUMMARY_START" });
    try {
      const res = await fetch(`${API_BASE}/api/pricing/summary`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(filters || {}),
      });
      if (!res.ok) throw new Error(`Summary request failed: ${res.statusText}`);
      const data = await res.json();
      dispatch({ type: "SUMMARY_SUCCESS", payload: data });
      return data;
    } catch (err) {
      dispatch({ type: "SUMMARY_ERROR", payload: err.message });
      return null;
    }
  }, []);

  const runSimulation = useCallback(async (payload = {}) => {
    dispatch({ type: "SIM_START" });
    try {
      const res = await fetch(`${API_BASE}/api/pricing/simulation`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload || {}),
      });
      if (!res.ok) throw new Error(`Simulation request failed: ${res.statusText}`);
      const data = await res.json();
      dispatch({ type: "SIM_SUCCESS", payload: data });
      return data;
    } catch (err) {
      dispatch({ type: "SIM_ERROR", payload: err.message });
      return null;
    }
  }, []);

  const value = useMemo(
    () => ({
      options: state.options,
      summary: state.summary,
      simulation: state.simulation,
      fetchOptions,
      fetchSummary,
      runSimulation,
    }),
    [state, fetchOptions, fetchSummary, runSimulation]
  );

  return <userContext.Provider value={value}>{children}</userContext.Provider>;
};

UserState.propTypes = {
  children: PropTypes.node.isRequired,
};

export default UserState;
