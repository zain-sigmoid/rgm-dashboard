import React, {
  useState,
  useMemo,
  useCallback,
  useEffect,
  useContext,
  useRef,
} from "react";
import Summary from "./components/Summary";
import Simulation from "./components/Simulation";
import Trend from "./components/Trend";
import Contribution from "./components/Contribution";
import FilterSidebar from "./components/FilterSideBar";
import { userContext } from "../../context/userContext";
import {
  summaryFields,
  trendFields,
  simulationFields,
  contributionFields,
} from "./config/fields";
import { buildFields } from "./config/buildFields";
import "./styling/pricing.css";

const Pricing = () => {
  const { options, fetchOptions, trendOptions, fetchTrendOptions } =
    useContext(userContext);
  const [activeTab, setActiveTab] = useState("summary");
  const prevKeyRef = useRef(null);
  const initialFilters = {
    categories: ["SurfaceCare"],
    manufacturers: [],
    retailers: [],
    time_periods: [],
    brands: [],
    ppgs: [],
    competitor_manufacturers: [],
    competitor_brands: [],
    competitor_ppgs: [],
    competitor_retailers: [],
  };
  const [filters, setFilters] = useState(initialFilters);

  useEffect(() => {
    if (!options.fetched && !options.loading) {
      fetchOptions(filters);
      fetchTrendOptions();
    }
    // If categories empty and backend provides options, set default category
    if (filters.categories.length === 0 && options.data?.categories?.length) {
      const preferred = options.data.categories.includes("SurfaceCare")
        ? ["SurfaceCare"]
        : [options.data.categories[0]];
      setFilters((prev) => ({ ...prev, categories: preferred }));
    }
  }, [
    filters.categories.length,
    options.data,
    options.fetched,
    options.loading,
    fetchOptions,
  ]);
  const filtersKey = JSON.stringify(filters);
  useEffect(() => {
    const key = `${activeTab}-${filtersKey}`;

    if (prevKeyRef.current === key) return;
    prevKeyRef.current = key;

    if (activeTab === "trend") {
      fetchTrendOptions(filters);
    } else if (
      activeTab === "summary" ||
      activeTab === "simulation" ||
      activeTab === "contribution"
    ) {
      fetchOptions(filters, activeTab);
    }
  }, [filtersKey, activeTab]);

  const handleFilterChange = useCallback((name, values) => {
    setFilters((prev) => ({ ...prev, [name]: values }));
  }, []);
  const handleClearAll = useCallback(() => {
    setFilters((prev) => ({
      ...initialFilters,
      categories:
        options.data?.categories && options.data.categories.length
          ? [options.data.categories[0]]
          : ["SurfaceCare"],
    }));
  }, [options.data]);

  const filterPayload = useMemo(() => {
    const base = { ...filters };
    Object.entries(base).forEach(([k, v]) => {
      if (Array.isArray(v) && v.length === 0) {
        base[k] = null;
      }
    });

    if (activeTab === "simulation") {
      const { categories, manufacturers, retailers, brands, ppgs } = base;
      return { categories, manufacturers, retailers, brands, ppgs };
    }
    if (activeTab === "trend") {
      const {
        categories,
        manufacturers,
        brands,
        ppgs,
        retailers,
        time_periods,
        competitor_manufacturers,
        competitor_brands,
        competitor_ppgs,
        competitor_retailers,
      } = base;
      return {
        categories,
        manufacturers,
        brands,
        ppgs,
        retailers,
        time_periods,
        competitor_manufacturers,
        competitor_brands,
        competitor_ppgs,
        competitor_retailers,
      };
    }
    if (activeTab === "contribution") {
      const { categories, manufacturers, retailers, brands, ppgs } = base;
      return { categories, manufacturers, retailers, brands, ppgs };
    }
    const { categories, manufacturers, brands, ppgs, retailers } = base;
    return { categories, manufacturers, brands, ppgs, retailers };
  }, [filters, activeTab]);

  let fields = "";
  activeTab === "summary"
    ? (fields = buildFields(summaryFields, options))
    : activeTab === "simulation"
    ? (fields = buildFields(simulationFields, options))
    : activeTab === "trend"
    ? (fields = buildFields(trendFields, trendOptions))
    : (fields = buildFields(contributionFields, options));

  return (
    <div className="container-fluid">
      <div className="row">
        {/* SIDEBAR */}
        <div className="col-12 col-md-3 mb-4">
          <FilterSidebar
            title={
              activeTab === "summary"
                ? "Summary Filters"
                : activeTab === "simulation"
                ? "Simulation Filters"
                : "Trend Filters"
            }
            filters={filters}
            onChange={handleFilterChange}
            onClearAll={handleClearAll}
            fields={fields}
            clear={handleClearAll}
          />
        </div>

        {/* CONTENT */}
        <div className="col-12 col-md-9 p-4">
          {/* Tabs */}
          <div className="d-flex flex-row justify-content-between align-items-center tabs me-4">
            <div style={{ paddingBottom: "0" }}>
              <h4 className="tab-head fw-bold" style={{ paddingBottom: "0" }}>
                Smart Pricing
              </h4>
            </div>
            <div className="tabs-wrapper d-flex gap-5">
              <div
                className={`tab-item ${
                  activeTab === "summary" ? "active" : ""
                }`}
                onClick={() => {
                  setActiveTab("summary");
                  handleClearAll();
                }}
              >
                Summary
              </div>

              <div
                className={`tab-item ${activeTab === "trend" ? "active" : ""}`}
                onClick={() => {
                  setActiveTab("trend");
                  handleClearAll();
                }}
              >
                Trend
              </div>

              <div
                className={`tab-item ${
                  activeTab === "contribution" ? "active" : ""
                }`}
                onClick={() => {
                  setActiveTab("contribution");
                  handleClearAll();
                }}
              >
                Contribution
              </div>

              <div
                className={`tab-item ${
                  activeTab === "simulation" ? "active" : ""
                }`}
                onClick={() => {
                  setActiveTab("simulation");
                  handleClearAll();
                }}
              >
                Simulation
              </div>
            </div>
          </div>

          {/* Tab Content */}
          {activeTab === "summary" && <Summary filters={filterPayload} />}
          {activeTab === "simulation" && <Simulation filters={filterPayload} />}
          {activeTab === "trend" && (
            <Trend
              filters={filterPayload}
              onFilterChange={handleFilterChange}
            />
          )}
          {activeTab === "contribution" && (
            <Contribution filters={filterPayload} />
          )}
        </div>
      </div>
    </div>
  );
};

export default Pricing;
