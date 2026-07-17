// @ts-check
import { defineConfig } from "astro/config";
import node from "@astrojs/node";
import react from "@astrojs/react";
import sitemap from "@astrojs/sitemap";

// Sitio público de DISPOLA SAS — SSR con islas React (D1).
export default defineConfig({
  // TODO[D4]: reemplazar por el dominio real cuando se suministre.
  site: "http://localhost:8889",
  output: "server",
  adapter: node({ mode: "standalone" }),
  integrations: [react(), sitemap()],
  server: { port: 8889 },
  vite: {
    server: {
      proxy: {
        // Las llamadas del navegador a /api se redirigen al backend FastAPI (8890).
        "/api": {
          target: "http://localhost:8890",
          changeOrigin: true,
        },
      },
    },
  },
});
