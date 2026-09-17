import { useEffect, useState } from "react";
import { api } from "../api/client";
import { useWebSocket } from "../hooks/useWebSocket";
import StatCard from "../components/StatCard";
import SyncProgressBar from "../components/SyncProgressBar";
import HashrateChart from "../components/HashrateChart";
import SystemGauges from "../components/SystemGauges";
import type { NodeStatus, SystemMetrics, HashratePoint } from "../types";

function formatHashrate(hs?: number): string {
  if (!hs) return "0 H/s";
  const units = ["H/s", "kH/s", "MH/s", "GH/s", "TH/s", "PH/s", "EH/s"];
  let value = hs;
  let i = 0;
  while (value >= 1000 && i < units.length - 1) {
    value /= 1000;
    i++;
  }
  return `${value.toFixed(2)} ${units[i]}`;
}

function formatUptime(seconds?: number): string {
  if (!seconds) return "-";
  const d = Math.floor(seconds / 86400);
  const h = Math.floor((seconds % 86400) / 3600);
  return `${d}d ${h}h`;
}

export default function Dashboard() {
  const [node, setNode] = useState<NodeStatus | null>(null);
  const [system, setSystem] = useState<SystemMetrics | null>(null);
  const [history, setHistory] = useState<HashratePoint[]>([]);

  useEffect(() => {
    api.get<NodeStatus>("/node/status").then((r) => setNode(r.data)).catch(() => {});
    api.get<HashratePoint[]>("/node/hashrate-history").then((r) => setHistory(r.data)).catch(() => {});
  }, []);

  useWebSocket((type, data) => {
    if (type === "node_status") setNode(data);
    if (type === "system_metrics") setSystem(data);
    if (type === "new_block") {
      api.get<HashratePoint[]>("/node/hashrate-history").then((r) => setHistory(r.data)).catch(() => {});
    }
  });

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Node-Uebersicht</h1>
        <p className="text-sm text-slate-400">
          Status:{" "}
          <span className={node?.connected ? "text-emerald-400" : "text-red-400"}>
            {node?.connected ? "Verbunden" : "Nicht erreichbar"}
          </span>
          {node?.chain && ` · Netzwerk: ${node.chain}`}
        </p>
      </div>

      {node && (
        <div className="rounded-xl bg-white dark:bg-bsv-panel border border-slate-200 dark:border-slate-700/50 p-4">
          <SyncProgressBar progress={node.verification_progress ?? 0} synced={node.is_synced} />
        </div>
      )}

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatCard label="Blockhoehe" value={node?.block_height?.toLocaleString() ?? "-"} accent="gold" />
        <StatCard label="Verbundene Peers" value={String(node?.peer_count ?? "-")} accent="blue" />
        <StatCard label="Difficulty" value={node?.difficulty ? node.difficulty.toLocaleString(undefined, { maximumFractionDigits: 2 }) : "-"} accent="blue" />
        <StatCard label="Netzwerk-Hashrate" value={formatHashrate(node?.network_hashrate)} accent="gold" />
        <StatCard label="Node-Uptime" value={formatUptime(node?.uptime_seconds)} accent="green" />
        <StatCard label="Node-Version" value={node?.version ?? "-"} accent="blue" />
      </div>

      <HashrateChart data={history} title="Netzwerk-Hashrate (Verlauf)" />

      <div>
        <h2 className="text-lg font-semibold mb-3">System (Raspberry Pi 5)</h2>
        <SystemGauges metrics={system} />
      </div>
    </div>
  );
}
