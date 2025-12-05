export const formatPercent = (value) => `${value.toFixed(2)}%`;

export const formatNumber = (value, decimal = 2) => {
  if (value == null || isNaN(value)) return value;

  // If value is an integer, return as is
  if (Number.isInteger(Number(value))) {
    return Number(value).toString();
  }

  // Otherwise, format to 2 decimals
  return Number(value).toFixed(decimal);
};

export const formatInteger = (value) => Math.round(value);

export const formatCurrency = (value) =>
  "$" + value.toLocaleString(undefined, { minimumFractionDigits: 2 });

export const formatVolume = (value, decimal = 1) => {
  if (value == null || isNaN(value)) return "-";

  const absVal = Math.abs(value);

  if (absVal >= 1_000_000_000)
    return (value / 1_000_000_000).toFixed(decimal) + "B";

  if (absVal >= 1_000_000) return (value / 1_000_000).toFixed(decimal) + "M";

  if (absVal >= 1_000) return (value / 1_000).toFixed(decimal) + "K";

  return value.toFixed(decimal);
};

export const noFormat = (value) => value;
