import React, { useState } from "react";
import PropTypes from "prop-types";

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
          <span className="text-start" style={{ overflow: "auto" }}>
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

const FilterBar = ({ filters, onChange, fields }) => {
  return (
    <div className="card border shadow-sm mb-4">
      <div className="card-body">
        <div className="row g-3">
          {fields.map(({ label, name, options = [], col }) => (
            <div className={`col-lg-${col || 3} col-md-6`} key={name}>
              <MultiSelect
                label={label}
                name={name}
                options={options}
                selected={filters[name] || []}
                onChange={onChange}
              />
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

FilterBar.propTypes = {
  filters: PropTypes.object.isRequired,
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

export default FilterBar;
