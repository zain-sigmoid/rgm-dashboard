const BarLabel = (props) => {
  const {
    x,
    y,
    width,
    height,
    value,
    orientation = "vertical", // "vertical" | "horizontal"
    formatter = (v) => v.toFixed(2),
    smallHeightThreshold = 40,
    smallWidthThreshold = 50,
    fontSize = 10,
  } = props;

  if (value == null) return null;

  const label = formatter(value);

  const absWidth = Math.abs(width);
  const absHeight = Math.abs(height);
  const isPositive = value >= 0;

  const isShort =
    orientation === "horizontal"
      ? absWidth < smallHeightThreshold
      : absHeight < smallHeightThreshold;

  const isNarrow = absWidth < smallWidthThreshold;

  let posX;
  let posY;
  let textAnchor = "middle";
  let fill = "#ffffff";
  let dy = 4;

  if (orientation === "horizontal") {
    // center of the bar vertically
    posY = y + height / 2;

    if (isShort || isNarrow) {
      // outside to the right
      posX = x + width + 4;
      textAnchor = "start";
      fill = "#000000";
      dy = 4;
    } else {
      // inside-right
      posX = x + width - 4;
      textAnchor = "end";
      fill = "#ffffff";
      dy = 4;
    }
  } else {
    // VERTICAL

    // For negative bars, height is negative and y is at baseline.
    // Compute actual top of bar and its center:
    const barTop = height >= 0 ? y : y + height;
    const barCenterY = barTop + absHeight / 2;

    posX = x + width / 2;
    textAnchor = "middle";

    if (isShort || isNarrow) {
      // bar too thin/short → place label OUTSIDE, but keep fill logic smart
      if (isPositive) {
        posY = barTop - 8; // above positive bar
      } else {
        posY = barTop + absHeight + 8; // below negative bar
      }
      // If you ALWAYS want white, keep this:
      // fill = "#ffffff";
      // If you want outside labels black:
      fill = "#000000";
      dy = 0;
    } else {
      // Inside bar center (works for positive and negative)
      posY = barCenterY;
      fill = "#ffffff"; // always white inside bar
      dy = 4;
    }
  }

  return (
    <text
      x={posX}
      y={posY}
      dy={dy}
      fontSize={fontSize}
      textAnchor={textAnchor}
      fill={fill}
      dominantBaseline="middle"
    >
      {label}
    </text>
  );
};

export default BarLabel;
