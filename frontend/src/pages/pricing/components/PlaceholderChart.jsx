import {
  ResponsiveContainer,
  ComposedChart,
  XAxis,
  YAxis,
  CartesianGrid,
  Rectangle,
} from "recharts";

const PlaceholderChart = () => {
  const placeholderData = [
    { date: "2022-01", vol: 0 },
    { date: "2022-04", vol: 0 },
    { date: "2022-07", vol: 0 },
    { date: "2022-10", vol: 0 },
  ];

  return (
    <ResponsiveContainer width="100%" height={350}>
      <ComposedChart data={placeholderData}>
        {/* --- Shimmer Gradient --- */}
        <defs>
          <linearGradient id="shimmerGradient">
            <stop offset="0%" stopColor="#e0e0e0" />
            <stop offset="50%" stopColor="#f5f5f5">
              <animate
                attributeName="offset"
                from="-1"
                to="2"
                dur="1.5s"
                repeatCount="indefinite"
              />
            </stop>
            <stop offset="100%" stopColor="#e0e0e0" />
          </linearGradient>
        </defs>

        {/* Grid */}
        <CartesianGrid strokeDasharray="4 4" stroke="#ddd" />

        {/* X-axis */}
        <XAxis
          dataKey="date"
          tick={{ fontSize: 12, fill: "#999" }}
          axisLine={{ stroke: "#aaa" }}
          tickLine={{ stroke: "#aaa" }}
        />

        {/* Y-axis left */}
        <YAxis
          yAxisId="left"
          tick={{ fontSize: 12, fill: "#999" }}
          axisLine={{ stroke: "#aaa" }}
          tickLine={{ stroke: "#aaa" }}
          domain={[0, 100]}
        />

        {/* Y-axis right */}
        <YAxis
          yAxisId="right"
          orientation="right"
          tick={{ fontSize: 12, fill: "#999" }}
          axisLine={{ stroke: "#aaa" }}
          tickLine={{ stroke: "#aaa" }}
          domain={[0, 100]}
        />

        {/* ---- SHIMMER RECTANGLE ---- */}
        <Rectangle
          x={60}
          y={30}
          width="85%"
          height="70%"
          className="shimmer-fill"
          radius={8}
        />
      </ComposedChart>
    </ResponsiveContainer>
  );
};

export default PlaceholderChart;
