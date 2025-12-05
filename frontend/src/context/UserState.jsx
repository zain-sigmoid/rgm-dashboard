import React, { useCallback, useMemo, useReducer } from "react";
import PropTypes from "prop-types";
import { userContext } from "./userContext";

const PRICING_API =
  import.meta.env.VITE_PRICING_API?.replace(/\/$/, "") ||
  "http://127.0.0.1:8000/api/pricing";

const PROMOTION_API =
  import.meta.env.VITE_PROMOTION_API?.replace(/\/$/, "") ||
  "http://127.0.0.1:8000/api/promotion";

const initialState = {
  options: { data: null, loading: false, error: null, fetched: false },
  summary: { data: null, loading: false, error: null, fetched: false },
  simulation: { data: null, loading: false, error: null, fetched: false },
  trend: { data: null, loading: false, error: null, fetched: false },
  trendOptions: { data: null, loading: false, error: null, fetched: false },
  contribution: { data: null, loading: false, error: null, fetched: false },
  performance: { data: null, loading: false, error: null, fetched: false },
  promoOptions: { data: null, loading: false, error: null, fetched: false },
  pastPromotion: { data: null, loading: false, error: null, fetched: false },
  promoSimulation: { data: null, loading: false, error: null, fetched: false },
  promoSimState: {
    numEvents: 0,
    eventFilters: [],
    globalFilters: {},
  },
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

    case "SET_PROMO_SIM_STATE": {
      return {
        ...state,
        promoSimState: {
          ...state.promoSimState,
          ...(action.payload || {}),
        },
      };
    }

    case "RESET_PROMO_SIMULATION": {
      return {
        ...state,
        promoSimulation: {
          data: null,
          loading: false,
          error: null,
          fetched: false,
        },
        promoSimState: {
          numEvents: 0,
          eventFilters: [],
          globalFilters: {},
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
        console.log("simulation userstate", payload);
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

  const runPromotionSimulation = useCallback(async (payload = {}) => {
    const key = "promoSimulation";
    dispatch({ type: "FETCH_START", key });
    try {
      const res = await fetch(`${PROMOTION_API}/simulation`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload || {}),
      });

      if (!res.ok) throw new Error(`${key} request failed: ${res.statusText}`);

      console.log("promo simulation response recived", res);
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

  const setPromoSimulationState = useCallback((payload) => {
    dispatch({ type: "SET_PROMO_SIM_STATE", payload });
  }, []);

  const resetPromotionSimulation = useCallback(() => {
    dispatch({ type: "RESET_PROMO_SIMULATION" });
  }, []);

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
      const res = await fetch(`${PRICING_API}/${endpoint}`, {
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

  const fetchPromoOptions = useCallback(
    async (payload = {}, tab = "summary") => {
      const key = "promoOptions";
      dispatch({ type: "FETCH_START", key });
      console.log("fetching promot options for", tab);
      const endpointMap = {
        past_promotion: "past-promotion/options",
        simulation: "simulation/options",
        performance: "performance/options",
      };

      const endpoint = endpointMap[tab] || "past-promotion/options";

      try {
        const res = await fetch(`${PROMOTION_API}/${endpoint}`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload || {}),
        });

        if (!res.ok)
          throw new Error(`Options request failed: ${res.statusText}`);

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

  // SUMMARY
  const fetchSummary = useCallback(
    createFetcher("summary", `${PRICING_API}/summary`),
    [createFetcher]
  );

  // SIMULATION
  const runSimulation = useCallback(
    createFetcher("simulation", `${PRICING_API}/simulation`),
    [createFetcher]
  );

  // TREND
  const fetchTrend = useCallback(
    createFetcher("trend", `${PRICING_API}/trend`),
    [createFetcher]
  );

  // TREND OPTIONS
  const fetchTrendOptions = useCallback(
    createFetcher("trendOptions", `${PRICING_API}/trend/options`),
    [createFetcher]
  );

  const getContribution = useCallback(
    createFetcher("contribution", `${PRICING_API}/contribution`),
    [createFetcher]
  );

  // ================================================================
  // Promotion Context
  // ================================================================

  const fetchPerformance = useCallback(
    createFetcher("performance", `${PROMOTION_API}/performance`),
    [createFetcher]
  );

  const fetchPastPromotion = useCallback(
    createFetcher("pastPromotion", `${PROMOTION_API}/past-promotion`),
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
      performance: state.performance,
      promoOptions: state.promoOptions,
      pastPromotion: state.pastPromotion,
      promoSimulation: state.promoSimulation,
      promoSimState: state.promoSimState,
      fetchOptions,
      fetchSummary,
      runSimulation,
      fetchTrend,
      fetchTrendOptions,
      getContribution,
      fetchPerformance,
      fetchPromoOptions,
      fetchPastPromotion,
      runPromotionSimulation,
      setPromoSimulationState,
      resetPromotionSimulation,
    }),
    [
      state,
      fetchOptions,
      fetchSummary,
      runSimulation,
      fetchTrend,
      fetchTrendOptions,
      getContribution,
      fetchPerformance,
      fetchPromoOptions,
      fetchPastPromotion,
      runPromotionSimulation,
      setPromoSimulationState,
      resetPromotionSimulation,
    ]
  );

  return <userContext.Provider value={value}>{children}</userContext.Provider>;
};

UserState.propTypes = {
  children: PropTypes.node.isRequired,
};

export default UserState;
