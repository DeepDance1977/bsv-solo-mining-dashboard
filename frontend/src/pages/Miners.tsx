import { useEffect, useState } from "react";
import { api } from "../api/client";
import { useWebSocket } from "../hooks/useWebSocket";
import MinerTable from "../components/MinerTable";
import HashrateChart from "../components/HashrateChart";
import StatCard from "../components/StatCard";
import type { Miner, HashratePoint } from "../types";

export default function Miners() {
  const [miners, setMiners] = useState<Miner[]>([]);
  const [selected, setSelected] = useState<string | null>(null);
  const [history, setHistory] = useState<HashratePoint[]>([]);

  useEffect(() => {
    api.get<Miner[]>("miners").then((r) => setMiners(r.data)).catch(() => {});
  }, []);

  useWebSocket((type, data) => {
    if (type === "miners") setMiners(data);
  });

  useEffect(() => {
    if (!selected) return;
    api
      .get<HashratePoint[]>(`miners/${encodeURIComponent(selected)}/hashrate-history`)
      .then((r) => setHistory(r.data))
      .catch(() => {});
  }, [selected]);

  const online = miners.filter((m) => m.is_online).length;
  const totalHashrate = miners.reduce((sum, m) => sum + (m.is_online ? m.hashrate : 0), 0);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Solo-Mining Ueberwachung</h1>
        <p className="text-sm text-slate-400">Alle mit dem Stratum-Server verbundenen Miner</p>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
        <StatCard label="Miner online" value={`${online} / ${miners.length}`} accent="green" />
        <StatCard
          label="Pool-Hashrate gesamt"
          value={`${(totalHashrate / 1e12).toFixed(3)} TH/s`}
          accent="gold"
        />
        <StatCard
          label="Shares (akzeptiert / abgelehnt)"
          value={`${miners.reduce((s, m) => s + m.accepted_shares, 0)} / ${miners.reduce((s, m) => s + m.rejected_shares, 0)}`}
          accent="blue"
        />
      </div>

      <MinerTable miners={miners} />

      <div>
        <div className="flex items-center gap-2 mb-2">
          <span className="text-sm text-slate-400">Miner-Hashrate im Verlauf:</span>
          <select
            className="bg-white dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-lg text-sm px-2 py-1"
            value={selected ?? ""}
            onChange={(e) => setSelected(e.target.value || null)}
          >
            <option value="">Miner waehlen...</option>
            {miners.map((m) => (
              <option key={m.worker_name} value={m.worker_name}>
                {m.worker_name}
              </option>
            ))}
          </select>
        </div>
        {selected && <HashrateChart data={history} title={`Hashrate-Verlauf: ${selected}`} />}
      </div>
    </div>
  );
}