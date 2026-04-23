import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

// Vite dev server on port 3005; proxy /api to the FastAPI backend on 8000.
export default defineConfig({
  plugins: [react()],
  server: {
    port: 3005,
    proxy: {
      "/api": {
        target: "http://localhost:8000",
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ""),
      },
    },
  },
});
