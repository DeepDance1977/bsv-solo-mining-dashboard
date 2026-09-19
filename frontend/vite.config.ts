import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  // Relativer Basis-Pfad: 5tratumOS ruft die App ueber einen Unterordner
  // auf (z.B. http://<pi-ip>/apps/deepdance-dashboard/), nicht direkt ueber
  // Host:Port. Mit "./" statt "/" werden alle JS-/CSS-Pfade relativ zur
  // aktuellen URL aufgeloest und funktionieren dadurch unter jedem
  // beliebigen Unterordner-Pfad (Umbrel, 5tratumOS, direkter Port-Zugriff).
  base: "./",
  plugins: [react()],
  server: {
    host: "0.0.0.0",
    port: 5173,
  },
  build: {
    outDir: "dist",
  },
});