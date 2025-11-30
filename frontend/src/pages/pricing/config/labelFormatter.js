export const formatPercent = (value) => `${value.toFixed(2)}%`;

export const formatNumber = (value) => value.toFixed(2);

export const formatInteger = (value) => Math.round(value);

export const formatCurrency = (value) =>
  "$" + value.toLocaleString(undefined, { minimumFractionDigits: 2 });

export const formatVolume = (value) => (value / 1_000_000).toFixed(1) + "M";

export const noFormat = (value) => value;
