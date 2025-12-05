import React, {
  useState,
  useMemo,
  useCallback,
  useEffect,
  useContext,
  useRef,
} from "react";
import { userContext } from "../../context/userContext";
import {
  PromotionalPerformanceFields,
  simulationFields,
} from "../config/promoFields";
import { buildFields } from "../config/buildFields";
import FilterSidebar from "../pricing/components/FilterSideBar";
import PastPromotion from "./tabs/PastPromotion";
import Performance from "./tabs/Performance";
import Simulation from "./tabs/Simulation";
// import "./styling/pricing.css";

const Promotion = (props) => {
  const { showAlert, showToast } = props.prop;
  const { promoOptions, fetchPromoOptions } = useContext(userContext);
  const [activeTab, setActiveTab] = useState("past_promotion");
  const prevKeyRef = useRef(null);
  const initialFilters = {
    categories: ["SurfaceCare"],
    brands: [],
    segment: [],
    retailers: [],
    ppgs: [],
    offer_type: [],
    promo_tactics: [],
    year: [],
    month: [],
  };
  const [filters, setFilters] = useState(initialFilters);

  useEffect(() => {
    if (!promoOptions.fetched && !promoOptions.loading) {
      fetchPromoOptions(filters);
    }
    // If categories empty and backend provides promoOptions, set default category
    if (
      filters.categories.length === 0 &&
      promoOptions.data?.categories?.length
    ) {
      const preferred = promoOptions.data.categories.includes("SurfaceCare")
        ? ["SurfaceCare"]
        : [promoOptions.data.categories[0]];
      setFilters((prev) => ({ ...prev, categories: preferred }));
    }
  }, [
    filters.categories.length,
    promoOptions.data,
    promoOptions.fetched,
    promoOptions.loading,
    fetchPromoOptions,
  ]);
  const filtersKey = JSON.stringify(filters);
  useEffect(() => {
    const key = `${activeTab}-${filtersKey}`;

    if (prevKeyRef.current === key) return;
    prevKeyRef.current = key;
    fetchPromoOptions(filters, activeTab);
  }, [filtersKey, activeTab]);

  const filterPayload = useMemo(() => {
    const base = { ...filters };
    Object.entries(base).forEach(([k, v]) => {
      if (Array.isArray(v) && v.length === 0) {
        base[k] = null;
      }
    });

    if (activeTab === "simulation") {
      const { categories, retailers, brands, ppgs, segment } = base;
      return { categories, retailers, brands, ppgs, segment };
    }
    return base;
  }, [filters, activeTab]);

  let fields = "";
  activeTab === "simulation"
    ? (fields = buildFields(simulationFields, promoOptions))
    : (fields = buildFields(PromotionalPerformanceFields, promoOptions));

  const handleFilterChange = useCallback((name, values) => {
    setFilters((prev) => ({ ...prev, [name]: values }));
  }, []);

  const handleClearAll = useCallback(() => {
    setFilters((prev) => ({
      ...initialFilters,
      categories:
        promoOptions.data?.categories && promoOptions.data.categories.length
          ? [promoOptions.data.categories[0]]
          : ["SurfaceCare"],
    }));
  }, [promoOptions.data]);

  console.log("promooptions", activeTab, promoOptions);

  return (
    <div className="container-fluid">
      <div className="row">
        {/* SIDEBAR */}
        <div className="col-12 col-md-3 mb-4">
          <FilterSidebar
            title={
              activeTab === "past_promotion"
                ? "Past Promotions Filters"
                : activeTab === "simulation"
                ? "Simulation Filters"
                : "Performance Filters"
            }
            filters={filters}
            onChange={handleFilterChange}
            clear={handleClearAll}
            fields={fields}
          />
        </div>
        {/* CONTENT */}
        <div className="col-12 col-md-9 p-4">
          {/* Tabs */}
          <div className="d-flex flex-row justify-content-between align-items-center tabs me-4">
            <div style={{ paddingBottom: "0" }}>
              <h4 className="tab-head fw-bold" style={{ paddingBottom: "0" }}>
                Optimal Promotion
              </h4>
            </div>
            <div className="tabs-wrapper d-flex gap-5">
              <div
                className={`tab-item ${
                  activeTab === "past_promotion" ? "active" : ""
                }`}
                onClick={() => {
                  setActiveTab("past_promotion");
                  handleClearAll();
                }}
              >
                Past Promotions
              </div>

              <div
                className={`tab-item ${
                  activeTab === "performance" ? "active" : ""
                }`}
                onClick={() => {
                  setActiveTab("performance");
                  handleClearAll();
                }}
              >
                Performance
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
          {activeTab === "past_promotion" && (
            <PastPromotion filters={filterPayload} showAlert={showAlert} />
          )}
          {activeTab === "performance" && (
            <Performance filters={filterPayload} />
          )}
          {activeTab === "simulation" && (
            <Simulation
              globalFilter={filterPayload}
              options={promoOptions}
              showAlert={showAlert}
            />
          )}
        </div>
      </div>
    </div>
  );
};

export default Promotion;
