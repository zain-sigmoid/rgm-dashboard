import React, { useEffect, useMemo, useContext, useCallback } from "react";
import PropTypes from "prop-types";
import { userContext } from "../../../context/userContext";
import {
  Bar,
  CartesianGrid,
  Legend,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
  LabelList,
  LineChart,
  Line,
  ComposedChart,
  Label,
} from "recharts";
import "../styling/promo.css";
import MechanicsTick from "../../../components/charts/MechanicTick";
import BarLabel from "../../pricing/components/BarLabel";
import {
  formatNumber,
  formatPercent,
  formatVolume,
} from "../../config/labelFormatter";

const PastPromotion = ({ filters }) => {
  const { pastPromotion, fetchPastPromotion } = useContext(userContext);
  const barsize = [20, 35];

  useEffect(() => {
    fetchPastPromotion(filters);
  }, [filters, fetchPastPromotion]);

  const cards = useMemo(
    () => pastPromotion.data?.metrics ?? [],
    [pastPromotion.data]
  );
  const upliftDiscount = pastPromotion.data?.uplift_vs_discount || [];
  const upliftOffer = pastPromotion.data?.uplift_vs_offer || [];
  const upliftPromo = pastPromotion.data?.uplift_vs_promo || [];
  const volumeBaseline = pastPromotion.data?.volume_vs_baseline || [];

  const grads = ["grad-1", "grad-2", "grad-3", "grad-4", "grad-5", "grad-6"];

  const normalizeComboData = useCallback((data) => {
    return (data || []).map((item) => ({
      ...item,
      uplift: Number(item?.uplift) || 0,
      avg_roi: Number(item?.avg_roi) || 0,
    }));
  }, []);

  const normalizedDiscount = useMemo(
    () => normalizeComboData(upliftDiscount),
    [normalizeComboData, upliftDiscount]
  );
  const normalizedOffer = useMemo(
    () => normalizeComboData(upliftOffer),
    [normalizeComboData, upliftOffer]
  );
  const normalizedPromo = useMemo(
    () => normalizeComboData(upliftPromo),
    [normalizeComboData, upliftPromo]
  );

  const renderDualLine = () => (
    <div className="card shadow-sm border h-100">
      <div className="card-body">
        <div className="d-flex justify-content-between align-items-center mb-2">
          <h6 className="mb-0">Volume vs Baseline</h6>
          <span className="badge bg-light text-secondary">Dual Line</span>
        </div>
        <div style={{ height: 320 }}>
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={volumeBaseline} className="my-4 pe-4 ps-2">
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="x" tick={{ fontSize: "12" }} />
              <YAxis
                tick={{ fontSize: 12 }}
                tickFormatter={(v) => formatVolume(v, 1)}
                domain={[0, (dataMax) => (dataMax * 1.1).toFixed(1)]}
              >
                <Label
                  value="Volume"
                  angle={-90}
                  position="left"
                  offset={0}
                  style={{ textAnchor: "middle", fontSize: "12px" }}
                />
              </YAxis>
              <Tooltip formatter={(value) => formatVolume(value, 3)} />
              <Legend />
              <Line
                type="monotone"
                dataKey="avg_baseline"
                name="Baseline"
                stroke="#1E3D7D"
                strokeWidth={3}
                dot={false}
              />
              <Line
                type="monotone"
                dataKey="avg_total_volume"
                name="Total Volume"
                stroke="#06C480"
                strokeWidth={3}
                dot={false}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );

  const renderComboChart = (title, data, xKey, barsize) => {
    const upliftValues = data.map((d) => d.uplift ?? 0);
    const maxUplift = upliftValues.length ? Math.max(...upliftValues, 0) : 0;
    const minUplift = upliftValues.length ? Math.min(...upliftValues, 0) : 0;
    const upliftDomain = [
      Math.min(0, minUplift * 1.1),
      Math.max(1, maxUplift * 1.1),
    ];

    return (
      <div className="card shadow-sm border h-100">
        <div className="card-body">
          <div className="d-flex justify-content-between align-items-center mb-2">
            <h6 className="mb-0">{title}</h6>
            <span className="badge bg-light text-secondary">Combo</span>
          </div>
          <div style={{ height: 320 }}>
            <ResponsiveContainer width="100%" height="100%">
              <ComposedChart data={data} barSize={barsize} className="my-4">
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis
                  dataKey={xKey}
                  interval={0}
                  tick={<MechanicsTick />}
                ></XAxis>
                <YAxis
                  yAxisId="left"
                  tick={{ fontSize: 12 }}
                  tickFormatter={formatNumber}
                  domain={upliftDomain}
                >
                  <Label
                    value="Uplift %"
                    angle={-90}
                    position="left"
                    offset={0}
                    style={{ textAnchor: "middle", fontSize: "12px" }}
                  />
                </YAxis>
                <YAxis
                  yAxisId="right"
                  orientation="right"
                  domain={[1, 2]}
                  tick={{ fontSize: 12 }}
                >
                  <Label
                    value="Avg ROI"
                    angle={90}
                    position="right"
                    offset={0}
                    style={{ textAnchor: "middle", fontSize: "12px" }}
                  />
                </YAxis>
                <Tooltip formatter={formatNumber} />
                <Legend />
                <Bar
                  yAxisId="left"
                  dataKey="uplift"
                  name="Uplift %"
                  fill="#1E3D7D"
                  radius={[6, 6, 0, 0]}
                >
                  <LabelList
                    dataKey="uplift"
                    content={
                      <BarLabel width={barsize} formatter={formatPercent} />
                    }
                  />
                </Bar>
                <Line
                  yAxisId="right"
                  type="monotone"
                  dataKey="avg_roi"
                  name="Avg ROI"
                  stroke="#06C480"
                  strokeWidth={3}
                  dot={{ r: 4 }}
                />
              </ComposedChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    );
  };

  const comboCharts = [
    {
      title: "Uplift vs Discount Depth",
      data: normalizedDiscount,
      xKey: "promo_depth",
    },
    {
      title: "Uplift vs Offer Mechanic",
      data: normalizedOffer,
      xKey: "offer_mechanic",
    },
    {
      title: "Uplift vs Promo Tactic",
      data: normalizedPromo,
      xKey: "promo_tactic",
    },
  ];

  return (
    <div className="py-4 pe-4" id="promo">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h4 className="mb-1">Past Promotion Analysis</h4>
        </div>
        {pastPromotion.loading && (
          <span className="badge bg-info text-dark">Loading...</span>
        )}
        {pastPromotion.error && (
          <span className="badge bg-danger">{pastPromotion.error}</span>
        )}
      </div>
      <div className="row g-3 mb-4">
        {cards.length > 0
          ? cards.map((card, idx) => (
              <div className="col-md-2" key={card.label}>
                <div
                  className={`glass-card d-flex flex-column justify-content-between h-100 ${
                    grads[idx % grads.length]
                  }`}
                >
                  <div className="fw-semibold small">{card.label}</div>
                  <div className="fw-bold fs-5">{card.value}</div>
                </div>
              </div>
            ))
          : [...Array(6)].map((_, idx) => (
              <div className="col-md-2" key={idx}>
                <div
                  className={`glass-card h-100 ${grads[idx % grads.length]}`}
                >
                  <div className="placeholder-glow">
                    <div className="placeholder placeholder-sm col-6 mb-2 d-block"></div>
                    <div className="placeholder placeholder-xs col-4 d-block"></div>
                  </div>
                </div>
              </div>
            ))}
      </div>
      <div className="col-md-12 my-5">{renderDualLine()}</div>
      <div className="row g-4 mb-5">
        {comboCharts.slice(0, 1).map((chart) => (
          <div className="col-md-12" key={chart.title}>
            {renderComboChart(chart.title, chart.data, chart.xKey, 50)}
          </div>
        ))}
      </div>
      <div className="row g-4">
        {comboCharts.slice(1).map((chart, idx) => (
          <div className="col-md-6" key={chart.title}>
            {renderComboChart(
              chart.title,
              chart.data,
              chart.xKey,
              barsize[idx]
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default PastPromotion;
