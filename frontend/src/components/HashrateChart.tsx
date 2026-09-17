import {
  ResponsiveContainer, AreaChart, Area, XAxis, YAxis, Tooltip, CartesianGrid,
} from "recharts";
import type { HashratePoint } from "../types";

function formatShort(hs: number): string {
  const units = ["H", "kH", "MH", "GH", "TH", "PH"];
  let value = hs;
  let i = 0;
  while (value >= 1000 && i < units.length - 1) {
    value /= 1000;
    i++;
  }
  return `${value.toFixed(1)}${units[i]}`;
}

export default function HashrateChart({ data, title }: { data: HashratePoint[]; title: string }) {
  const chartData = data.map((p) => ({
    time: new Date(p.timestamp).toLocaleTimeString(),
    hashrate: p.hashrate,
  }));

  return (
    <div className="rounded-xl bg-white dark:bg-bsv-panel border border-slate-200 dark:border-slate-700/50 p-4">
      <h3 className="text-sm font-semibold mb-2 text-slate-600 dark:text-slate-300">{title}</h3>
      <ResponsiveContainer width="100%" height={220}>
        <AreaChart data={chartData}>
          <defs>
            <linearGradient id="hashGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#f7931a" stopOpacity={0.5} />
              <stop offset="95%" stopColor="#f7931a" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#334155" opacity={0.3} />
          <XAxis dataKey="time" tick={{ fontSize: 10 }} minTickGap={30} />
          <YAxis tickFormatter={formatShort} tick={{ fontSize: 10 }} width={50} />
          <Tooltip formatter={(v: number) => formatShort(v)} />
          <Area type="monotone" dataKey="hashrate" stroke="#f7931a" fill="url(#hashGradient)" strokeWidth={2} />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
