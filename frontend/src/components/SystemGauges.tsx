import type { SystemMetrics } from "../types";
import StatCard from "./StatCard";

function formatUptime(seconds: number): string {
  const d = Math.floor(seconds / 86400);
  const h = Math.floor((seconds % 86400) / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  return `${d}d ${h}h ${m}m`;
}

export default function SystemGauges({ metrics }: { metrics: SystemMetrics | null }) {
  if (!metrics) {
    return <div className="text-slate-400 text-sm">Lade Systemmetriken...</div>;
  }
  const tempAccent = metrics.temperature_celsius && metrics.temperature_celsius > 75 ? "red" : "green";

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
      <StatCard label="CPU-Auslastung" value={`${metrics.cpu_percent.toFixed(1)}%`} accent="blue" />
      <StatCard
        label="Arbeitsspeicher"
        value={`${metrics.memory_percent.toFixed(1)}%`}
        sub={`${(metrics.memory_used_mb / 1024).toFixed(1)} / ${(metrics.memory_total_mb / 1024).toFixed(1)} GB`}
        accent="blue"
      />
      <StatCard
        label="Festplatte"
        value={`${metrics.disk_percent.toFixed(1)}%`}
        sub={`${metrics.disk_used_gb.toFixed(1)} / ${metrics.disk_total_gb.toFixed(1)} GB`}
        accent="gold"
      />
      <StatCard
        label="Temperatur"
        value={metrics.temperature_celsius ? `${metrics.temperature_celsius.toFixed(1)} °C` : "n/v"}
        accent={tempAccent as any}
      />
      <StatCard
        label="Host-Uptime"
        value={formatUptime(metrics.host_uptime_seconds)}
        accent="green"
      />
    </div>
  );
}
