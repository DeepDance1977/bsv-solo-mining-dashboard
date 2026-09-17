interface Props {
  progress: number; // 0..1
  synced: boolean;
}

export default function SyncProgressBar({ progress, synced }: Props) {
  const pct = Math.min(100, Math.max(0, progress * 100));
  return (
    <div className="w-full">
      <div className="flex justify-between text-xs mb-1 text-slate-500 dark:text-slate-400">
        <span>Synchronisation</span>
        <span>{synced ? "Vollstaendig synchronisiert" : `${pct.toFixed(2)}%`}</span>
      </div>
      <div className="w-full h-3 rounded-full bg-slate-200 dark:bg-slate-700 overflow-hidden">
        <div
          className={`h-full rounded-full transition-all duration-500 ${
            synced ? "bg-emerald-500" : "bg-bsv-gold"
          }`}
          style={{ width: `${pct}%` }}
        />
      </div>
    </div>
  );
}
