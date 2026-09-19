import { useEffect, useState } from "react";
import { api } from "../api/client";
import StatCard from "../components/StatCard";
import type { WalletInfo } from "../types";

export default function Wallet() {
  const [wallet, setWallet] = useState<WalletInfo | null>(null);
  const [copied, setCopied] = useState(false);

  const load = () => api.get<WalletInfo>("wallet").then((r) => setWallet(r.data)).catch(() => {});

  useEffect(() => {
    load();
    const interval = setInterval(load, 30000);
    return () => clearInterval(interval);
  }, []);

  const copyAddress = () => {
    if (!wallet?.address) return;
    navigator.clipboard.writeText(wallet.address);
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Wallet</h1>
        <p className="text-sm text-slate-400">Guthaben und Mining-Belohnungen der Node-Wallet</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <StatCard label="Guthaben" value={`${wallet?.balance?.toFixed(8) ?? "0.00000000"} BSV`} accent="gold" />
        <StatCard label="Unbestaetigt" value={`${wallet?.unconfirmed_balance?.toFixed(8) ?? "0.00000000"} BSV`} accent="blue" />
        <StatCard label="Mining-Belohnungen (letzte)" value={String(wallet?.last_mining_rewards.length ?? 0)} accent="green" />
      </div>

      <div className="rounded-xl bg-white dark:bg-bsv-panel border border-slate-200 dark:border-slate-700/50 p-4">
        <h3 className="text-sm font-semibold mb-2 text-slate-500 dark:text-slate-300">Empfangsadresse</h3>
        <div className="flex items-center gap-2 flex-wrap">
          <code className="text-sm bg-slate-100 dark:bg-slate-800 px-3 py-2 rounded-lg break-all">
            {wallet?.address ?? "Nicht verfuegbar"}
          </code>
          <button
            onClick={copyAddress}
            className="text-xs bg-bsv-gold text-slate-900 font-semibold px-3 py-2 rounded-lg hover:bg-orange-500"
          >
            {copied ? "Kopiert!" : "Kopieren"}
          </button>
        </div>
      </div>

      <div>
        <h3 className="text-sm font-semibold mb-2 text-slate-500 dark:text-slate-300">Mining-Belohnungen</h3>
        <TransactionTable txs={wallet?.last_mining_rewards ?? []} emptyText="Noch keine Mining-Belohnungen empfangen." />
      </div>

      <div>
        <h3 className="text-sm font-semibold mb-2 text-slate-500 dark:text-slate-300">Letzte Transaktionen</h3>
        <TransactionTable txs={wallet?.transactions ?? []} emptyText="Keine Transaktionen gefunden." />
      </div>
    </div>
  );
}

function TransactionTable({ txs, emptyText }: { txs: WalletInfo["transactions"]; emptyText: string }) {
  return (
    <div className="overflow-x-auto rounded-xl border border-slate-200 dark:border-slate-700/50">
      <table className="w-full text-sm">
        <thead className="bg-slate-50 dark:bg-slate-800/60 text-slate-500 dark:text-slate-400">
          <tr>
            <th className="text-left p-3">TXID</th>
            <th className="text-left p-3">Kategorie</th>
            <th className="text-right p-3">Betrag</th>
            <th className="text-right p-3">Bestaetigungen</th>
            <th className="text-right p-3">Zeit</th>
          </tr>
        </thead>
        <tbody>
          {txs.map((tx) => (
            <tr key={tx.txid} className="border-t border-slate-100 dark:border-slate-800">
              <td className="p-3 font-mono text-xs">{tx.txid.slice(0, 16)}...</td>
              <td className="p-3">
                {tx.is_mining_reward ? (
                  <span className="text-bsv-gold font-medium">Mining-Belohnung</span>
                ) : (
                  tx.category
                )}
              </td>
              <td className={`p-3 text-right font-mono ${tx.amount >= 0 ? "text-emerald-500" : "text-red-400"}`}>
                {tx.amount.toFixed(8)}
              </td>
              <td className="p-3 text-right">{tx.confirmations}</td>
              <td className="p-3 text-right text-slate-500">{new Date(tx.time).toLocaleString()}</td>
            </tr>
          ))}
          {txs.length === 0 && (
            <tr>
              <td colSpan={5} className="p-6 text-center text-slate-400">{emptyText}</td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
}