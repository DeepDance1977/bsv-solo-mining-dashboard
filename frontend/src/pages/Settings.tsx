import { useEffect, useState } from "react";
import { api } from "../api/client";
import { useAuth } from "../context/AuthContext";
import type { UserOut, EventItem } from "../types";

export default function Settings() {
  const { user } = useAuth();
  const [users, setUsers] = useState<UserOut[]>([]);
  const [events, setEvents] = useState<EventItem[]>([]);
  const [newUser, setNewUser] = useState({ username: "", password: "", role: "viewer" });
  const [message, setMessage] = useState<string | null>(null);

  const isAdmin = user?.role === "admin";

  const loadUsers = () => api.get<UserOut[]>("/auth/users").then((r) => setUsers(r.data)).catch(() => {});
  const loadEvents = () => api.get<EventItem[]>("/system/events?limit=50").then((r) => setEvents(r.data)).catch(() => {});

  useEffect(() => {
    if (isAdmin) loadUsers();
    loadEvents();
    const interval = setInterval(loadEvents, 15000);
    return () => clearInterval(interval);
  }, [isAdmin]);

  const createUser = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.post("/auth/users", newUser);
      setMessage("Benutzer erfolgreich angelegt.");
      setNewUser({ username: "", password: "", role: "viewer" });
      loadUsers();
    } catch {
      setMessage("Fehler beim Anlegen des Benutzers.");
    }
  };

  const toggleActive = async (u: UserOut) => {
    await api.patch(`/auth/users/${u.id}`, { is_active: !u.is_active });
    loadUsers();
  };

  const deleteUser = async (u: UserOut) => {
    if (!confirm(`Benutzer '${u.username}' wirklich loeschen?`)) return;
    await api.delete(`/auth/users/${u.id}`);
    loadUsers();
  };

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold">Einstellungen</h1>
        <p className="text-sm text-slate-400">Benutzerverwaltung, Rollen und Ereignisprotokoll</p>
      </div>

      {isAdmin && (
        <div className="rounded-xl bg-white dark:bg-bsv-panel border border-slate-200 dark:border-slate-700/50 p-4">
          <h2 className="font-semibold mb-3">Benutzerverwaltung</h2>

          <table className="w-full text-sm mb-4">
            <thead className="text-slate-500 dark:text-slate-400">
              <tr>
                <th className="text-left py-2">Benutzername</th>
                <th className="text-left py-2">Rolle</th>
                <th className="text-left py-2">Status</th>
                <th className="text-left py-2">Letzter Login</th>
                <th className="text-right py-2">Aktionen</th>
              </tr>
            </thead>
            <tbody>
              {users.map((u) => (
                <tr key={u.id} className="border-t border-slate-100 dark:border-slate-800">
                  <td className="py-2 font-medium">{u.username}</td>
                  <td className="py-2 capitalize">{u.role}</td>
                  <td className="py-2">{u.is_active ? "Aktiv" : "Deaktiviert"}</td>
                  <td className="py-2 text-slate-500">
                    {u.last_login ? new Date(u.last_login).toLocaleString() : "-"}
                  </td>
                  <td className="py-2 text-right space-x-2">
                    <button
                      onClick={() => toggleActive(u)}
                      className="text-xs px-2 py-1 rounded bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700"
                    >
                      {u.is_active ? "Deaktivieren" : "Aktivieren"}
                    </button>
                    <button
                      onClick={() => deleteUser(u)}
                      className="text-xs px-2 py-1 rounded bg-red-500/10 text-red-400 hover:bg-red-500/20"
                    >
                      Loeschen
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          <form onSubmit={createUser} className="flex flex-wrap gap-2 items-end">
            <div>
              <label className="block text-xs text-slate-400 mb-1">Benutzername</label>
              <input
                required
                className="rounded-lg bg-slate-100 dark:bg-slate-800 px-3 py-2 text-sm"
                value={newUser.username}
                onChange={(e) => setNewUser({ ...newUser, username: e.target.value })}
              />
            </div>
            <div>
              <label className="block text-xs text-slate-400 mb-1">Passwort</label>
              <input
                required
                type="password"
                className="rounded-lg bg-slate-100 dark:bg-slate-800 px-3 py-2 text-sm"
                value={newUser.password}
                onChange={(e) => setNewUser({ ...newUser, password: e.target.value })}
              />
            </div>
            <div>
              <label className="block text-xs text-slate-400 mb-1">Rolle</label>
              <select
                className="rounded-lg bg-slate-100 dark:bg-slate-800 px-3 py-2 text-sm"
                value={newUser.role}
                onChange={(e) => setNewUser({ ...newUser, role: e.target.value })}
              >
                <option value="admin">Admin</option>
                <option value="operator">Operator</option>
                <option value="viewer">Betrachter</option>
              </select>
            </div>
            <button className="bg-bsv-gold text-slate-900 font-semibold px-4 py-2 rounded-lg hover:bg-orange-500">
              Anlegen
            </button>
          </form>
          {message && <p className="text-xs text-slate-400 mt-2">{message}</p>}
        </div>
      )}

      <div>
        <h2 className="font-semibold mb-3">Ereignisprotokoll</h2>
        <div className="rounded-xl border border-slate-200 dark:border-slate-700/50 divide-y divide-slate-100 dark:divide-slate-800 max-h-96 overflow-y-auto">
          {events.map((e) => (
            <div key={e.id} className="p-3 flex items-start gap-3 text-sm">
              <span
                className={`mt-1 w-2 h-2 rounded-full shrink-0 ${
                  e.severity === "error" || e.severity === "critical"
                    ? "bg-red-500"
                    : e.severity === "warning"
                    ? "bg-amber-400"
                    : "bg-sky-400"
                }`}
              />
              <div>
                <div>{e.message}</div>
                <div className="text-xs text-slate-400">
                  {new Date(e.timestamp).toLocaleString()} · {e.category}
                </div>
              </div>
            </div>
          ))}
          {events.length === 0 && <div className="p-4 text-center text-slate-400 text-sm">Keine Ereignisse.</div>}
        </div>
      </div>
    </div>
  );
}
