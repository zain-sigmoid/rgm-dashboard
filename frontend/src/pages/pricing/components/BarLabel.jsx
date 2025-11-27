const BarLabel = (props) => {
  const { x, y, width, height, value } = props;
  if (value == null) return null;

  const label = `${value.toFixed(2)}%`;

  const barTooSmall = width < 40; // tweak this threshold

  // if bar is big enough -> draw inside, aligned to right
  const posX = barTooSmall ? x + width + 4 : x + width - 4;
  const textAnchor = barTooSmall ? "start" : "end";
  const fill = barTooSmall ? "#000000" : "#ffffff";

  return (
    <text
      x={posX}
      y={y + height / 2}
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
