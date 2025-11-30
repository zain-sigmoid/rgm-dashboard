import React, { useContext, useEffect, useMemo, useCallback } from "react";
import PropTypes from "prop-types";
import {
  BarChart,
  Bar,
  CartesianGrid,
  Legend,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
  LabelList,
  Label,
} from "recharts";
import { userContext } from "../../../context/userContext";
import BarLabel from "./BarLabel";
import { formatNumber, formatVolume } from "../config/labelFormatter";

const Contribution = ({ filters }) => {
  const { contribution, getContribution } = useContext(userContext);

  const priceElasticity = contribution.data?.price_elasticity;
  const crossPriceElasticity = contribution.data?.cross_price_elasticity;
  const distributionElasticity = contribution.data?.distribution_elasticity;
  const contributionByDriver = contribution.data?.contribution_by_driver;

  const mappedFilters = useMemo(
    () => ({
      categories: filters?.categories || [],
      manufacturers: filters?.manufacturers || [],
      brands: filters?.brands || [],
      ppgs: filters?.ppgs || [],
      retailers: filters?.retailers || [],
    }),
    [
      filters?.categories,
      filters?.manufacturers,
      filters?.brands,
      filters?.ppgs,
      filters?.retailers,
    ]
  );

  useEffect(() => {
    getContribution(mappedFilters);
  }, [mappedFilters, getContribution]);

  const buildElasticityChartData = useCallback((payload) => {
    if (!payload?.bars) return [];
    return payload.bars.map((item) => ({
      name: item.driver,
      value: item.elasticity,
      fill: item.elasticity < 0 ? "#1E3D7D" : "#06C480",
    }));
  }, []);

  console.log(contribution);

  const priceElasticityData = useMemo(
    () => buildElasticityChartData(priceElasticity),
    [buildElasticityChartData, priceElasticity]
  );
  const crossElasticityData = useMemo(
    () => buildElasticityChartData(crossPriceElasticity),
    [buildElasticityChartData, crossPriceElasticity]
  );
  const distributionElasticityData = useMemo(
    () => buildElasticityChartData(distributionElasticity),
    [buildElasticityChartData, distributionElasticity]
  );

  const contributionDriverData = useMemo(() => {
    if (!contributionByDriver?.categories || !contributionByDriver?.values) {
      return [];
    }
    return contributionByDriver.categories.map((label, idx) => ({
      name: label,
      value: contributionByDriver.values[idx],
      fill:
        contributionByDriver.values[idx] < 0 ? "#C0392B" : "var(--bs-primary)",
    }));
  }, [contributionByDriver]);

  const renderElasticityCard = (title, data, shadow = false) => (
    <div className={`card ${shadow ? "shadow" : "shadow-sm"} border h-100`}>
      <div className="card-body">
        <div className="d-flex justify-content-between align-items-center mb-2">
          <h6 className="mb-0">{title}</h6>
          <span className="badge bg-light text-secondary">Elasticity</span>
        </div>
        <div style={{ height: 260 }}>
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={data} barSize={48}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} />
              <XAxis dataKey="name" tick={{ fontSize: 12 }} />
              <YAxis
                tick={{ fontSize: 12 }}
                domain={["dataMin - 0.1", "dataMax + 0.1"]}
                tickFormatter={formatNumber}
              />
              <Tooltip />
              <Bar dataKey="value" radius={[6, 6, 0, 0]}>
                <LabelList
                  dataKey="value"
                  content={
                    <BarLabel formatter={formatNumber} orientation="vertical" />
                  }
                />
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );

  const renderContributionCard = () => (
    <div className="card shadow-sm border">
      <div className="card-body">
        <div className="d-flex justify-content-between align-items-center mb-3">
          <h6 className="mb-0">Contribution by Driver</h6>
          <span className="badge bg-light text-secondary">Waterfall</span>
        </div>
        <div style={{ height: 340 }}>
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={contributionDriverData} barSize={60}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} />
              <XAxis dataKey="name" tick={{ fontSize: 12 }}>
                <Label
                  value="Drivers"
                  angle={0}
                  position="insideBottom"
                  offset={0}
                  style={{ textAnchor: "middle", fontSize: "12px" }}
                />
              </XAxis>
              <YAxis tick={{ fontSize: 12 }} tickFormatter={formatVolume}>
                <Label
                  value="Volume"
                  angle={-90}
                  position="left"
                  offset={0}
                  style={{ textAnchor: "middle", fontSize: "12px" }}
                />
              </YAxis>
              <Tooltip formatter={formatVolume} />
              <Legend />
              <Bar dataKey="value" name="Change" radius={[6, 6, 0, 0]}>
                <LabelList
                  dataKey="value"
                  content={<BarLabel formatter={formatVolume} />}
                />
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );

  return (
    <div className="py-4 pe-4">
      <div className="d-flex justify-content-between align-items-center mb-3">
        <h4 className="mb-1">Elasticity and Contribution</h4>
        {contribution.loading && (
          <span className="badge bg-info text-dark">Loading...</span>
        )}
        {contribution.error && (
          <span className="badge bg-danger">{contribution.error}</span>
        )}
      </div>

      <div
        className="card shadow-sm border p-4"
        style={{
          background:
            "linear-gradient(to bottom right, #eef2ff, white, #f3e8ff)",
          borderColor: "#e0e7ff",
        }}
      >
        <div className="card-body">
          <div className="row g-5">
            <div className="col-lg-6">
              <div className="h-100">
                <div className="p-4">
                  <div className="d-flex align-items-center mb-3">
                    <span
                      className="rounded-circle d-inline-flex align-items-center justify-content-center me-3"
                      style={{
                        width: "44px",
                        height: "44px",
                        background: "linear-gradient(135deg, #1E3D7D, #3459A8)",
                        color: "white",
                      }}
                    >
                      <i className="fa-solid fa-chart-column fs-5"></i>
                    </span>

                    <h5 className="fw-bold mb-0 fs-4">Price Elasticity</h5>
                  </div>

                  <p className="text-muted mb-0" style={{ lineHeight: "1.55" }}>
                    Price elasticity measures how shoppers respond to changes in
                    product price. Lower elasticity means customers are less
                    sensitive to price adjustments.
                  </p>
                </div>
              </div>
            </div>

            <div className="col-lg-6">
              {renderElasticityCard(
                priceElasticity?.title || "Price Elasticity",
                priceElasticityData,
                true
              )}
            </div>
          </div>
        </div>
      </div>

      <div className="mt-4 pt-4">
        <div className="text-center">
          <h6 className="text-uppercase mb-0 fs-4">Cross Drivers</h6>
        </div>
        <div className="row g-4 mt-2">
          <div className="col-md-6">
            {renderElasticityCard(
              crossPriceElasticity?.title || "Cross Price Elasticity",
              crossElasticityData
            )}
          </div>
          <div className="col-md-6">
            {renderElasticityCard(
              distributionElasticity?.title || "Distribution Elasticity",
              distributionElasticityData
            )}
          </div>
        </div>
      </div>

      <div className="mt-4">{renderContributionCard()}</div>
    </div>
  );
};

Contribution.propTypes = {
  filters: PropTypes.shape({
    categories: PropTypes.arrayOf(PropTypes.string),
    manufacturers: PropTypes.arrayOf(PropTypes.string),
    brands: PropTypes.arrayOf(PropTypes.string),
    ppgs: PropTypes.arrayOf(PropTypes.string),
    retailers: PropTypes.arrayOf(PropTypes.string),
  }),
};

Contribution.defaultProps = {
  filters: {
    categories: [],
    manufacturers: [],
    brands: [],
    ppgs: [],
    retailers: [],
  },
};

export default Contribution;
