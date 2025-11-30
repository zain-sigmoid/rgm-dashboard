import React, { useState } from "react";
import PropTypes from "prop-types";

/** --- MULTISELECT (reused, slightly polished for sidebar) --- */
const MultiSelect = ({ label, options, selected, onChange, name, icon }) => {
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
      <button
        type="button"
        className="btn w-100 d-flex justify-content-between align-items-center px-2 py-2 sidebar-filter-trigger"
        onClick={toggle}
      >
        <div className="d-flex flex-column text-start">
          <span className="small text-muted">{label}</span>
          <span className="fw-semibold sidebar-filter-value">
            {selected.length ? (
              <span className="d-inline-flex flex-wrap gap-1">
                {selected.slice(0, 3).map((s) => (
                  <span
                    className="badge bg-primary bg-opacity-75"
                    key={s}
                    style={{ maxWidth: "245px", overflow: "auto" }}
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
              <span className="text-muted">All</span>
            )}
          </span>
        </div>
        <div className="d-flex align-items-center gap-2">
          <i
            className={`fa-solid fa-chevron-${open ? "up" : "down"} small ms-2`}
          />
        </div>
      </button>

      <ul
        className={`dropdown-menu w-100 mt-1 shadow-sm sidebar-filter-dropdown ${
          open ? "show" : ""
        }`}
        style={{ maxHeight: "260px", overflowY: "auto" }}
      >
        <li className="d-flex justify-content-between align-items-center px-3 py-2">
          <span className="fw-semibold small text-secondary">{label}</span>
          <button
            type="button"
            className="btn btn-link btn-sm text-danger text-decoration-none p-0"
            onClick={clearAll}
          >
            Clear
          </button>
        </li>
        <li>
          <hr className="dropdown-divider my-1" />
        </li>
        {options.map((opt) => (
          <li key={opt}>
            <button
              type="button"
              className="dropdown-item d-flex align-items-center small"
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
  );
};

MultiSelect.propTypes = {
  label: PropTypes.string.isRequired,
  name: PropTypes.string.isRequired,
  options: PropTypes.arrayOf(PropTypes.string).isRequired,
  selected: PropTypes.arrayOf(PropTypes.string).isRequired,
  onChange: PropTypes.func.isRequired,
  icon: PropTypes.string,
};

/** --- SIDEBAR FILTER --- */
const FilterSidebar = ({
  title = "Filters",
  filters,
  onChange,
  fields,
  clear,
}) => {
  return (
    <aside
      className="bg-white border-end shadow-sm sidebar-filters d-flex flex-column"
      style={{
        width: "320px",
        position: "fixed",
        top: "72px",
        height: "88vh",
      }}
    >
      <div className="d-flex justify-content-between align-items-center px-3 py-3 border-bottom">
        <div>
          <h6 className="mb-0 fw-bold">{title}</h6>
          <small className="text-muted">Refine your results</small>
        </div>
        <button
          type="button"
          className="btn btn-sm btn-outline-secondary"
          onClick={clear}
        >
          Reset
        </button>
      </div>

      <div
        className="px-3 py-3 flex-grow-1"
        style={{ overflow: "auto", minHeight: 0 }}
      >
        {fields.map(({ label, name, options = [], icon }) => (
          <MultiSelect
            key={name}
            label={label}
            name={name}
            options={options}
            selected={filters[name] || []}
            onChange={onChange}
            icon={icon}
          />
        ))}
      </div>
    </aside>
  );
};

FilterSidebar.propTypes = {
  title: PropTypes.string,
  filters: PropTypes.object.isRequired,
  onChange: PropTypes.func.isRequired,
  fields: PropTypes.arrayOf(
    PropTypes.shape({
      label: PropTypes.string.isRequired,
      name: PropTypes.string.isRequired,
      options: PropTypes.arrayOf(PropTypes.string).isRequired,
    })
  ).isRequired,
  onClearAll: PropTypes.func,
};

export default FilterSidebar;
