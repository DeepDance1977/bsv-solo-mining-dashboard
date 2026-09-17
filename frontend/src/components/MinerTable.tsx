import type { Miner } from "../types";

function formatHashrate(hs: number): string {
  const units = ["H/s", "kH/s", "MH/s", "GH/s", "TH/s", "PH/s"];
  let value = hs;
  let i = 0;
  while (value >= 1000 && i < units.length - 1) {
    value /= 1000;
    i++;
  }
  return `${value.toFixed(2)} ${units[i]}`;
}

function formatUptime(seconds: number | null): string {
  if (!seconds) return "-";
  const d = Math.floor(seconds / 86400);
  const h = Math.floor((seconds % 86400) / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  return `${d}d ${h}h ${m}m`;
}

export default function MinerTable({ miners }: { miners: Miner[] }) {
  return (
    <div className="overflow-x-auto rounded-xl border border-slate-200 dark:border-slate-700/50">
      <table className="w-full text-sm">
        <thead className="bg-slate-50 dark:bg-slate-800/60 text-slate-500 dark:text-slate-400">
          <tr>
            <th className="text-left p-3">Status</th>
            <th className="text-left p-3">Miner</th>
            <th className="text-left p-3">IP-Adresse</th>
            <th className="text-right p-3">Hashrate</th>
            <th className="text-right p-3">Akzeptiert</th>
            <th className="text-right p-3">Abgelehnt</th>
            <th className="text-right p-3">Uptime</th>
            <th className="text-right p-3">Letzter Share</th>
          </tr>
        </thead>
        <tbody>
          {miners.map((m) => (
            <tr key={m.worker_name} className="border-t border-slate-100 dark:border-slate-800">
              <td className="p-3">
                <span
                  className={`inline-block w-2.5 h-2.5 rounded-full mr-2 ${
                    m.is_online ? "bg-emerald-500" : "bg-red-500"
                  }`}
                />
                {m.is_online ? "Online" : "Offline"}
              </td>
              <td className="p-3 font-medium">{m.worker_name}</td>
              <td className="p-3 text-slate-500">{m.ip_address ?? "-"}</td>
              <td className="p-3 text-right font-mono">{formatHashrate(m.hashrate)}</td>
              <td className="p-3 text-right text-emerald-500">{m.accepted_shares}</td>
              <td className="p-3 text-right text-red-400">{m.rejected_shares}</td>
              <td className="p-3 text-right">{formatUptime(m.uptime_seconds)}</td>
              <td className="p-3 text-right text-slate-500">
                {m.last_share_at ? new Date(m.last_share_at).toLocaleTimeString() : "-"}
              </td>
            </tr>
          ))}
          {miners.length === 0 && (
            <tr>
              <td colSpan={8} className="p-6 text-center text-slate-400">
                Noch keine Miner mit dem Stratum-Server verbunden.
              </td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
}
