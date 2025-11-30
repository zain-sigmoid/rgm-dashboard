const BarLabel = (props) => {
  const {
    x,
    y,
    width,
    height,
    value,
    orientation = "vertical", // "vertical" | "horizontal"
    formatter = (v) => v.toFixed(2),
    smallThreshold = 40, // px; tweak to taste
  } = props;

  if (value == null) return null;

  const label = formatter(value);

  // Use absolute size so negative bars still behave correctly
  const size =
    orientation === "horizontal" ? Math.abs(width) : Math.abs(height);
  const barTooSmall = size < smallThreshold;

  let posX;
  let posY;
  let textAnchor;
  let fill;

  if (orientation === "horizontal") {
    // Bar grows along X
    posY = y + height / 2;

    if (barTooSmall) {
      // outside-right
      posX = x + width + 4;
      textAnchor = "start";
      fill = "#000000";
    } else {
      // inside-right
      posX = x + width - 4;
      textAnchor = "end";
      fill = "#ffffff";
    }
  } else {
    // orientation === "vertical" – bar grows along Y (up for positive, down for negative)
    posX = x + width / 2;
    textAnchor = "middle";

    if (barTooSmall) {
      // above for positive bars, below for negative bars
      posY = value >= 0 ? y - 4 : y + height + 12;
      fill = "#000000";
    } else {
      // inside the bar (always white)
      posY = y + height / 2;
      fill = "#ffffff";
    }
  }

  return (
    <text
      x={posX}
      y={posY}
      dy={4}
      fontSize={10}
      textAnchor={textAnchor}
      fill={fill}
    >
      {label}
    </text>
  );
};
export default BarLabel;
