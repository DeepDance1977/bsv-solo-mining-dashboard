import { HashRouter, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider, useAuth } from "./context/AuthContext";
import Layout from "./components/Layout";
import Login from "./pages/Login";
import ChangePassword from "./pages/ChangePassword";
import Dashboard from "./pages/Dashboard";
import Miners from "./pages/Miners";
import Wallet from "./pages/Wallet";
import Settings from "./pages/Settings";

function RequireAuth({ children }: { children: JSX.Element }) {
  const { user, loading } = useAuth();
  if (loading) {
    return <div className="min-h-screen flex items-center justify-center text-slate-400">Lade...</div>;
  }
  if (!user) return <Navigate to="/login" replace />;
  // Erzwingt eine Passwortaenderung beim ersten Login, bevor der Rest der
  // App genutzt werden kann.
  if (user.must_change_password) return <Navigate to="/change-password" replace />;
  return children;
}

function RequireAuthOnly({ children }: { children: JSX.Element }) {
  // Wie RequireAuth, aber OHNE die must_change_password-Weiterleitung -
  // wird von der ChangePassword-Seite selbst verwendet, damit man sie
  // ueberhaupt erreichen kann.
  const { user, loading } = useAuth();
  if (loading) {
    return <div className="min-h-screen flex items-center justify-center text-slate-400">Lade...</div>;
  }
  if (!user) return <Navigate to="/login" replace />;
  return children;
}

export default function App() {
  return (
    <HashRouter>
      <AuthProvider>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route
            path="/change-password"
            element={
              <RequireAuthOnly>
                <ChangePassword />
              </RequireAuthOnly>
            }
          />
          <Route
            path="/"
            element={
              <RequireAuth>
                <Layout />
              </RequireAuth>
            }
          >
            <Route index element={<Dashboard />} />
            <Route path="miners" element={<Miners />} />
            <Route path="wallet" element={<Wallet />} />
            <Route path="settings" element={<Settings />} />
          </Route>
        </Routes>
      </AuthProvider>
    </HashRouter>
  );
}
