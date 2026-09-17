interface Props {
  label: string;
  value: string;
  sub?: string;
  accent?: "gold" | "green" | "red" | "blue";
}

const accentMap: Record<string, string> = {
  gold: "text-bsv-gold",
  green: "text-emerald-400",
  red: "text-red-400",
  blue: "text-sky-400",
};

export default function StatCard({ label, value, sub, accent = "blue" }: Props) {
  return (
    <div className="rounded-xl bg-white dark:bg-bsv-panel shadow-sm border border-slate-200 dark:border-slate-700/50 p-4 flex flex-col gap-1">
      <span className="text-xs uppercase tracking-wide text-slate-500 dark:text-slate-400">{label}</span>
      <span className={`text-2xl font-bold ${accentMap[accent]}`}>{value}</span>
      {sub && <span className="text-xs text-slate-400">{sub}</span>}
    </div>
  );
}
