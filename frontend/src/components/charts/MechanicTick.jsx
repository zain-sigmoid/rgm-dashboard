const MechanicsTick = ({ x, y, payload }) => {
  const label = payload.value || "";

  // Simple split by space, then group into lines
  const words = label.split(" ");
  const lines = [];
  let current = "";

  words.forEach((w) => {
    if ((current + " " + w).length > 10) {
      // 10 chars per line, tweak
      lines.push(current.trim());
      current = w;
    } else {
      current += " " + w;
    }
  });
  if (current) lines.push(current.trim());

  return (
    <text x={x} y={y + 5} textAnchor="middle" fontSize={10}>
      {lines.map((line, idx) => (
        <tspan key={idx} x={x} dy={idx === 0 ? 0 : 10}>
          {line}
        </tspan>
      ))}
    </text>
  );
};
export default MechanicsTick;
