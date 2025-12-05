import React, { useState, useRef, useEffect } from "react";
import PropTypes from "prop-types";

const MultiSelect = ({
  label,
  options = [],
  selected = [],
  onChange,
  name,
}) => {
  const [open, setOpen] = useState(false);
  const dropdownRef = useRef(null);

  const toggle = () => setOpen((s) => !s);

  const handleToggleValue = (value) => {
    const exists = selected.includes(value);
    const next = exists
      ? selected.filter((v) => v !== value)
      : [...selected, value];
    onChange(name, next);
  };

  useEffect(() => {
    function handleClickOutside(e) {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target)) {
        setOpen(false); // close dropdown
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, []);

  const clearAll = () => onChange(name, []);

  return (
    <div className="mb-3 position-relative">
      {/* <label className="form-label fw-semibold text-secondary">{label}</label> */}
      <div className="dropdown w-100" ref={dropdownRef}>
        <button
          type="button"
          className="btn btn-light w-100 d-flex justify-content-between align-items-center border border-dark border-opacity-50"
          onClick={toggle}
        >
          <span className="text-start" style={{ overflow: "auto" }}>
            {selected.length ? (
              <span className="d-inline-flex flex-wrap gap-1">
                {selected.slice(0, 3).map((s) => (
                  <span
                    className="badge bg-primary"
                    key={s}
                    // style={{ maxWidth: "245px", overflow: "auto" }}
                  >
                    {s}
                  </span>
                ))}
                {selected.length > 3 && (
                  <span className="badge bg-secondary">
                    +{selected.length - 3}
                  </span>
                )}
              </span>
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
          {(options || []).map((opt) => (
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

const FilterBar = ({ filters = {}, onChange, fields = [], eventNumber }) => {
  return (
    <div className="card border shadow-sm mb-4">
      <div className="card-body">
        <div className="d-flex justify-content-between align-items-center mb-3">
          <span className="fw-semibold text-muted">
            Filters for Event {eventNumber}
          </span>
          <span className="badge bg-light text-secondary px-3 py-2">Panel</span>
        </div>
        <div className="row g-3 px-3 pb-3">
          {(fields || []).map(({ label, name, icon, options = [], col }) => {
            // Decide what input to render based on the field name
            const isMultiSelectField = [
              "offer_type",
              "promo_tactics",
              "offer_mechanic",
            ].includes(name);
            const isDateField = name === "start_date";
            const isNumberField = [
              "duration",
              "discount",
              "redemption_rate",
            ].includes(name);
            const requiredField = ["start_date", "duration"].includes(name);

            return (
              <div className={`col-lg-${col || 3} col-md-6`} key={name}>
                {/* Common label with icon */}
                <label className="form-label d-flex align-items-center justify-content-between">
                  <div>
                    {icon && <i className={`${icon} me-2`} />}
                    <span className="text-secondary">{label}</span>
                  </div>
                  {requiredField && (
                    <i className="fa-solid fa-asterisk fa-2xs text-danger me-2"></i>
                  )}
                </label>

                {/* 1️⃣ MultiSelect for top 3 */}
                {isMultiSelectField && (
                  <MultiSelect
                    name={name}
                    options={options || []}
                    selected={filters?.[name] || []}
                    onChange={onChange}
                  />
                )}

                {/* 2️⃣ Date input for Start Date */}
                {isDateField && (
                  <input
                    type="date"
                    name={name}
                    className="form-control"
                    value={filters?.[name] || ""}
                    onChange={(e) => onChange(name, e.target.value)}
                  />
                )}

                {/* 3️⃣ Number input for Duration / Discount / Redemption */}
                {isNumberField && (
                  <input
                    type="number"
                    name={name}
                    min="0"
                    className="form-control"
                    placeholder={
                      name === "duration"
                        ? "Enter days"
                        : name === "discount"
                        ? "Enter discount %"
                        : "Enter redemption rate"
                    }
                    value={filters?.[name] ?? ""}
                    onChange={(e) =>
                      onChange(
                        name,
                        e.target.value === "" ? null : Number(e.target.value)
                      )
                    }
                  />
                )}
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};

FilterBar.propTypes = {
  filters: PropTypes.object,
  onChange: PropTypes.func.isRequired,
  fields: PropTypes.arrayOf(
    PropTypes.shape({
      label: PropTypes.string.isRequired,
      name: PropTypes.string.isRequired,
      options: PropTypes.arrayOf(PropTypes.string).isRequired,
      col: PropTypes.number,
    })
  ).isRequired,
};

FilterBar.defaultProps = {
  filters: {},
  fields: [],
};

export default FilterBar;
