import React, {
  useState,
  useMemo,
  useCallback,
  useEffect,
  useContext,
} from "react";
import Summary from "./components/Summary";
import Simulation from "./components/Simulation";
import Trend from "./components/Trend";
import FilterBar from "./components/FilterBar";
import { userContext } from "../../context/userContext";

const Pricing = () => {
  const { options } = useContext(userContext);
  const [activeTab, setActiveTab] = useState("summary");
  const [filters, setFilters] = useState({
    categories: ["SurfaceCare"],
    manufacturers: [],
    retailers: [],
    time_periods: [],
    brands: [],
    ppgs: [],
  });

  useEffect(() => {
    // If categories empty and backend provides options, set default category to first or SurfaceCare if present
    if (filters.categories.length === 0 && options.data?.categories?.length) {
      const preferred = options.data.categories.includes("SurfaceCare")
        ? ["SurfaceCare"]
        : [options.data.categories[0]];
      setFilters((prev) => ({ ...prev, categories: preferred }));
    }
  }, [filters.categories.length, options.data]);

  const handleFilterChange = useCallback((name, values) => {
    setFilters((prev) => ({ ...prev, [name]: values }));
  }, []);

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
    // summary/trend default
    const { categories, manufacturers, retailers, time_periods } = base;
    return { categories, manufacturers, retailers, time_periods };
  }, [filters, activeTab]);

  return (
    <div className="container py-4">
      <FilterBar
        filters={filters}
        onChange={handleFilterChange}
        activeTab={activeTab}
      />
      <div className="d-flex flex-wrap gap-4 mb-3 justify-content-center border-bottom border-secondary">
        <button
          type="button"
          className={`mb-3 btn ${
            activeTab === "summary" ? "btn-primary" : "btn-outline-secondary"
          }`}
          onClick={() => setActiveTab("summary")}
          style={{ width: "200px" }}
        >
          <i className="fa-solid fa-chart-pie me-2" />
          Summary
        </button>
        <button
          type="button"
          className={`mb-3 btn ${
            activeTab === "trend" ? "btn-primary" : "btn-outline-secondary"
          }`}
          onClick={() => setActiveTab("trend")}
          style={{ width: "200px" }}
        >
          <i className="fa-solid fa-chart-pie me-2" />
          Trend Analysis
        </button>
        <button
          type="button"
          className={`mb-3 btn ${
            activeTab === "simulation" ? "btn-primary" : "btn-outline-secondary"
          }`}
          onClick={() => setActiveTab("simulation")}
          style={{ width: "200px" }}
        >
          <i className="fa-solid fa-sliders me-2" />
          Simulation
        </button>
      </div>
      {activeTab === "summary" && <Summary filters={filterPayload} />}
      {activeTab === "simulation" && <Simulation filters={filterPayload} />}
      {activeTab === "trend" && <Trend filters={filterPayload} />}
    </div>
  );
};

export default Pricing;
