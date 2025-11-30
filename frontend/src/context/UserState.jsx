import React, { useCallback, useMemo, useReducer } from "react";
import PropTypes from "prop-types";
import { userContext } from "./userContext";

const API_BASE =
  import.meta.env.VITE_API_BASE?.replace(/\/$/, "") ||
  "http://127.0.0.1:8000/api/pricing";

const initialState = {
  options: { data: null, loading: false, error: null, fetched: false },
  summary: { data: null, loading: false, error: null, fetched: false },
  simulation: { data: null, loading: false, error: null, fetched: false },
  trend: { data: null, loading: false, error: null, fetched: false },
  trendOptions: { data: null, loading: false, error: null, fetched: false },
  contribution: { data: null, loading: false, error: null, fetched: false },
};

function reducer(state, action) {
  switch (action.type) {
    case "FETCH_START": {
      const key = action.key;
      return {
        ...state,
        [key]: {
          // keep previous data (same as your *_START cases)
          data: state[key]?.data ?? null,
          loading: true,
          error: null,
          fetched: true,
        },
      };
    }

    case "FETCH_SUCCESS": {
      const key = action.key;
      return {
        ...state,
        [key]: {
          data: action.payload,
          loading: false,
          error: null,
          fetched: true,
        },
      };
    }

    case "FETCH_ERROR": {
      const key = action.key;
      return {
        ...state,
        [key]: {
          data: null,
          loading: false,
          error: action.payload,
          fetched: true,
        },
      };
    }

    default:
      return state;
  }
}

const UserState = ({ children }) => {
  const [state, dispatch] = useReducer(reducer, initialState);

  // generic helper (optional but keeps code DRY)
  const createFetcher = useCallback(
    (key, url) =>
      async (payload = {}) => {
        dispatch({ type: "FETCH_START", key });
        try {
          const res = await fetch(url, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload || {}),
          });

          if (!res.ok)
            throw new Error(`${key} request failed: ${res.statusText}`);

          const data = await res.json();
          dispatch({ type: "FETCH_SUCCESS", key, payload: data });
          return data;
        } catch (err) {
          dispatch({
            type: "FETCH_ERROR",
            key,
            payload: err.message || "Unknown error",
          });
          return null;
        }
      },
    []
  );

  // OPTIONS (special because endpoint depends on tab)
  const fetchOptions = useCallback(async (payload = {}, tab = "summary") => {
    const key = "options";
    dispatch({ type: "FETCH_START", key });

    const endpointMap = {
      summary: "options",
      simulation: "simulation/options",
      contribution: "contribution/options",
    };

    const endpoint = endpointMap[tab] || "options";

    try {
      const res = await fetch(`${API_BASE}/${endpoint}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload || {}),
      });

      if (!res.ok) throw new Error(`Options request failed: ${res.statusText}`);

      const data = await res.json();
      dispatch({ type: "FETCH_SUCCESS", key, payload: data });
      return data;
    } catch (err) {
      dispatch({
        type: "FETCH_ERROR",
        key,
        payload: err.message || "Unknown error",
      });
      return null;
    }
  }, []);

  // SUMMARY
  const fetchSummary = useCallback(
    createFetcher("summary", `${API_BASE}/summary`),
    [createFetcher]
  );

  // SIMULATION
  const runSimulation = useCallback(
    createFetcher("simulation", `${API_BASE}/simulation`),
    [createFetcher]
  );

  // TREND
  const fetchTrend = useCallback(createFetcher("trend", `${API_BASE}/trend`), [
    createFetcher,
  ]);

  // TREND OPTIONS
  const fetchTrendOptions = useCallback(
    createFetcher("trendOptions", `${API_BASE}/trend/options`),
    [createFetcher]
  );

  const getContribution = useCallback(
    createFetcher("contribution", `${API_BASE}/contribution`),
    [createFetcher]
  );

  const value = useMemo(
    () => ({
      options: state.options,
      summary: state.summary,
      simulation: state.simulation,
      trend: state.trend,
      trendOptions: state.trendOptions,
      contribution: state.contribution,
      fetchOptions,
      fetchSummary,
      runSimulation,
      fetchTrend,
      fetchTrendOptions,
      getContribution,
    }),
    [
      state,
      fetchOptions,
      fetchSummary,
      runSimulation,
      fetchTrend,
      fetchTrendOptions,
      getContribution,
    ]
  );

  return <userContext.Provider value={value}>{children}</userContext.Provider>;
};

UserState.propTypes = {
  children: PropTypes.node.isRequired,
};

export default UserState;
