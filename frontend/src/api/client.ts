import axios from "axios";

// Basis-URLs werden relativ zur tatsaechlichen Dokument-Adresse aufgeloest,
// damit die App unabhaengig davon funktioniert, unter welchem Pfad sie
// aufgerufen wird (direkter Port-Zugriff, Umbrel-App-Proxy, 5tratumOS
// Unterordner-Reverse-Proxy wie "/apps/deepdance-dashboard/" etc.).
// document.baseURI aendert sich dank HashRouter (siehe App.tsx) auch beim
// Navigieren zwischen Seiten nicht, bleibt also zuverlaessig korrekt.
const apiBaseUrl = new URL("api/", document.baseURI).toString();

export const api = axios.create({
  baseURL: apiBaseUrl,
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (res) => res,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem("access_token");
      window.location.hash = "#/login";
    }
    return Promise.reject(error);
  }
);

export function wsUrl(): string {
  const token = localStorage.getItem("access_token") || "";
  const httpUrl = new URL("ws", document.baseURI);
  httpUrl.protocol = httpUrl.protocol === "https:" ? "wss:" : "ws:";
  httpUrl.search = `?token=${encodeURIComponent(token)}`;
  return httpUrl.toString();
}