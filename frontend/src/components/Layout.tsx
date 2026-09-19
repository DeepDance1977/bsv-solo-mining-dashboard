import { NavLink, Outlet } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

const navItems = [
  { to: "/", label: "Dashboard", end: true },
  { to: "/miners", label: "Miner" },
  { to: "/wallet", label: "Wallet" },
  { to: "/settings", label: "Einstellungen" },
];

export default function Layout() {
  const { user, logout } = useAuth();

  return (
    <div className="min-h-screen flex flex-col md:flex-row bg-slate-100 dark:bg-bsv-dark">
      <aside className="md:w-56 w-full bg-white dark:bg-bsv-panel border-b md:border-b-0 md:border-r border-slate-200 dark:border-slate-700/50 flex md:flex-col">
        <div className="flex items-center gap-2 p-4">
          <img src={`${import.meta.env.BASE_URL}icon.svg`} alt="BSV Node" className="w-8 h-8 rounded-md" />
          <div className="leading-tight">
            <div className="font-bold text-sm">BSV Node</div>
            <div className="text-[10px] text-slate-400">by DeepDance</div>
          </div>
        </div>
        <nav className="flex md:flex-col flex-1 gap-1 p-2">
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.end}
              className={({ isActive }) =>
                `px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                  isActive
                    ? "bg-bsv-gold/15 text-bsv-gold"
                    : "text-slate-500 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800"
                }`
              }
            >
              {item.label}
            </NavLink>
          ))}
        </nav>
        <div className="p-3 text-xs text-slate-400 hidden md:block">
          <div className="mb-2">Angemeldet als <b>{user?.username}</b> ({user?.role})</div>
          <button
            onClick={logout}
            className="w-full text-left px-3 py-2 rounded-lg bg-slate-100 dark:bg-slate-800 hover:bg-red-500/20 hover:text-red-400"
          >
            Abmelden
          </button>
        </div>
      </aside>
      <main className="flex-1 p-4 md:p-6 overflow-y-auto">
        <Outlet />
      </main>
    </div>
  );
}