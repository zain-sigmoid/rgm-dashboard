import React, { useEffect, useState, useContext } from "react";
import PropTypes from "prop-types";
import { userContext } from "../../../context/userContext";

const MultiSelect = ({ label, options, selected, onChange, name }) => {
  const [open, setOpen] = useState(false);

  const toggle = () => setOpen((s) => !s);

  const handleToggleValue = (value) => {
    const exists = selected.includes(value);
    const next = exists
      ? selected.filter((v) => v !== value)
      : [...selected, value];
    onChange(name, next);
  };

  const clearAll = () => onChange(name, []);

  return (
    <div className="mb-3 position-relative">
      <label className="form-label fw-semibold text-secondary">{label}</label>
      <div className="dropdown w-100">
        <button
          type="button"
          className="btn btn-light w-100 d-flex justify-content-between align-items-center border border-dark border-opacity-50"
          onClick={toggle}
        >
          <span className="text-start">
            {selected.length ? (
              <div className="d-flex flex-wrap gap-1">
                {selected.map((s) => (
                  <span className="badge bg-primary" key={s}>
                    {s}
                  </span>
                ))}
              </div>
            ) : (
              <span className="text-muted">Select...</span>
            )}
          </span>
          <i className={`fa-solid fa-chevron-${open ? "up" : "down"} small`} />
        </button>
        <ul
          className={`dropdown-menu w-100 ${open ? "show" : ""}`}
          style={{ maxHeight: "240px", overflowY: "auto" }}
        >
          <li>
            <button
              type="button"
              className="dropdown-item text-danger"
              onClick={clearAll}
            >
              Clear
            </button>
          </li>
          <li>
            <hr className="dropdown-divider" />
          </li>
          {options.map((opt) => (
            <li key={opt}>
              <button
                type="button"
                className="dropdown-item d-flex align-items-center"
                onClick={() => handleToggleValue(opt)}
              >
                <input
                  type="checkbox"
                  className="form-check-input me-2"
                  readOnly
                  checked={selected.includes(opt)}
                />
                {opt}
              </button>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
};

MultiSelect.propTypes = {
  label: PropTypes.string.isRequired,
  name: PropTypes.string.isRequired,
  options: PropTypes.arrayOf(PropTypes.string).isRequired,
  selected: PropTypes.arrayOf(PropTypes.string).isRequired,
  onChange: PropTypes.func.isRequired,
};

const FilterBar = ({ filters, onChange, activeTab }) => {
  const { options, fetchOptions } = useContext(userContext);

  useEffect(() => {
    if (!options.fetched && !options.loading) {
      fetchOptions();
    }
  }, [options.fetched, options.loading, fetchOptions]);

  const categoryOptions = options.data?.categories || ["SurfaceCare"];
  const manufacturerOptions = options.data?.manufacturers || [];
  const retailerOptions = options.data?.retailers || [];
  const timePeriodOptions = options.data?.time_periods || [];
  const brandOptions = options.data?.brands || [];
  const ppgOptions = options.data?.ppgs || [];
  const isSimulation = activeTab === "simulation";

  console.log(categoryOptions);

  return (
    <div className="card border shadow-sm mb-4">
      <div className="card-body">
        <div className="row g-3">
          <div className={`col-lg-${isSimulation ? "3" : "3"} col-md-6`}>
            <MultiSelect
              label="Category"
              name="categories"
              options={categoryOptions}
              selected={filters.categories}
              onChange={onChange}
            />
          </div>
          <div className={`col-lg-${isSimulation ? "3" : "3"} col-md-6`}>
            <MultiSelect
              label="Manufacturer"
              name="manufacturers"
              options={manufacturerOptions}
              selected={filters.manufacturers}
              onChange={onChange}
            />
          </div>
          <div className={`col-lg-${isSimulation ? "3" : "3"} col-md-6`}>
            <MultiSelect
              label="Retailer"
              name="retailers"
              options={retailerOptions}
              selected={filters.retailers}
              onChange={onChange}
            />
          </div>
          {isSimulation ? (
            <>
              <div className={`col-lg-${isSimulation ? "3" : "3"} col-md-6`}>
                <MultiSelect
                  label="Brand"
                  name="brands"
                  options={brandOptions}
                  selected={filters.brands}
                  onChange={onChange}
                />
              </div>
              <div className={`col-lg-${isSimulation ? "3" : "3"} col-md-6`}>
                <MultiSelect
                  label="PPG"
                  name="ppgs"
                  options={ppgOptions}
                  selected={filters.ppgs}
                  onChange={onChange}
                />
              </div>
            </>
          ) : (
            <div className={`col-lg-${isSimulation ? "3" : "3"} col-md-6`}>
              <MultiSelect
                label="Time Period"
                name="time_periods"
                options={timePeriodOptions}
                selected={filters.time_periods}
                onChange={onChange}
              />
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

FilterBar.propTypes = {
  filters: PropTypes.shape({
    categories: PropTypes.arrayOf(PropTypes.string).isRequired,
    manufacturers: PropTypes.arrayOf(PropTypes.string).isRequired,
    brands: PropTypes.arrayOf(PropTypes.string),
    ppgs: PropTypes.arrayOf(PropTypes.string),
    retailers: PropTypes.arrayOf(PropTypes.string).isRequired,
    time_periods: PropTypes.arrayOf(PropTypes.string).isRequired,
  }).isRequired,
  onChange: PropTypes.func.isRequired,
  activeTab: PropTypes.string.isRequired,
};

export default FilterBar;
