import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../api/client";
import { useAuth } from "../context/AuthContext";

export default function ChangePassword() {
  const { refreshUser, user } = useAuth();
  const navigate = useNavigate();
  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (newPassword !== confirmPassword) {
      setError("Die neuen Passwoerter stimmen nicht ueberein.");
      return;
    }
    if (newPassword.length < 8) {
      setError("Das neue Passwort muss mindestens 8 Zeichen lang sein.");
      return;
    }

    setLoading(true);
    try {
      await api.post("auth/change-password", {
        current_password: currentPassword,
        new_password: newPassword,
      });
      await refreshUser();
      navigate("/");
    } catch {
      setError("Aktuelles Passwort ist falsch.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-bsv-dark px-4">
      <form onSubmit={handleSubmit} className="w-full max-w-sm bg-bsv-panel rounded-2xl shadow-xl p-8 border border-slate-700/50">
        <div className="flex flex-col items-center mb-6">
          <img src={`${import.meta.env.BASE_URL}icon.svg`} alt="BSV Node" className="w-16 h-16 rounded-xl mb-3" />
          <h1 className="text-xl font-bold text-white">Passwort aendern</h1>
          <p className="text-xs text-slate-400 mt-1 text-center">
            Aus Sicherheitsgruenden musst du beim ersten Login
            ({user?.username}) ein eigenes Passwort vergeben.
          </p>
        </div>

        {error && (
          <div className="mb-4 text-sm bg-red-500/10 text-red-400 border border-red-500/30 rounded-lg px-3 py-2">
            {error}
          </div>
        )}

        <label className="block text-xs text-slate-400 mb-1">Aktuelles Passwort</label>
        <input
          type="password"
          className="w-full mb-4 rounded-lg bg-slate-800 border border-slate-700 px-3 py-2 text-sm text-white focus:outline-none focus:border-bsv-gold"
          value={currentPassword}
          onChange={(e) => setCurrentPassword(e.target.value)}
          autoFocus
          required
        />

        <label className="block text-xs text-slate-400 mb-1">Neues Passwort (mind. 8 Zeichen)</label>
        <input
          type="password"
          className="w-full mb-4 rounded-lg bg-slate-800 border border-slate-700 px-3 py-2 text-sm text-white focus:outline-none focus:border-bsv-gold"
          value={newPassword}
          onChange={(e) => setNewPassword(e.target.value)}
          required
        />

        <label className="block text-xs text-slate-400 mb-1">Neues Passwort bestaetigen</label>
        <input
          type="password"
          className="w-full mb-6 rounded-lg bg-slate-800 border border-slate-700 px-3 py-2 text-sm text-white focus:outline-none focus:border-bsv-gold"
          value={confirmPassword}
          onChange={(e) => setConfirmPassword(e.target.value)}
          required
        />

        <button
          type="submit"
          disabled={loading}
          className="w-full bg-bsv-gold hover:bg-orange-500 text-slate-900 font-semibold rounded-lg py-2 transition-colors disabled:opacity-50"
        >
          {loading ? "Speichern..." : "Passwort speichern"}
        </button>
      </form>
    </div>
  );
}
