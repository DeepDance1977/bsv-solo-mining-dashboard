import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      await login(username, password);
      navigate("/");
    } catch {
      setError("Benutzername oder Passwort falsch.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-bsv-dark px-4">
      <form onSubmit={handleSubmit} className="w-full max-w-sm bg-bsv-panel rounded-2xl shadow-xl p-8 border border-slate-700/50">
        <div className="flex flex-col items-center mb-6">
          <img src={`${import.meta.env.BASE_URL}icon.svg`} alt="BSV Node" className="w-16 h-16 rounded-xl mb-3" />
          <h1 className="text-xl font-bold text-white">BSV Solo Mining Dashboard</h1>
          <p className="text-xs text-slate-400 mt-1">Entwickelt von DeepDance</p>
        </div>

        {error && (
          <div className="mb-4 text-sm bg-red-500/10 text-red-400 border border-red-500/30 rounded-lg px-3 py-2">
            {error}
          </div>
        )}

        <div className="mb-4 text-xs bg-sky-500/10 text-sky-300 border border-sky-500/30 rounded-lg px-3 py-2">
          Erstanmeldung: <b>admin</b> / <b>changeme123</b> – danach wirst du
          zur Vergabe eines eigenen Passworts aufgefordert.
        </div>

        <label className="block text-xs text-slate-400 mb-1">Benutzername</label>
        <input
          className="w-full mb-4 rounded-lg bg-slate-800 border border-slate-700 px-3 py-2 text-sm text-white focus:outline-none focus:border-bsv-gold"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          autoFocus
          required
        />

        <label className="block text-xs text-slate-400 mb-1">Passwort</label>
        <input
          type="password"
          className="w-full mb-6 rounded-lg bg-slate-800 border border-slate-700 px-3 py-2 text-sm text-white focus:outline-none focus:border-bsv-gold"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />

        <button
          type="submit"
          disabled={loading}
          className="w-full bg-bsv-gold hover:bg-orange-500 text-slate-900 font-semibold rounded-lg py-2 transition-colors disabled:opacity-50"
        >
          {loading ? "Anmelden..." : "Anmelden"}
        </button>
      </form>
    </div>
  );
}
