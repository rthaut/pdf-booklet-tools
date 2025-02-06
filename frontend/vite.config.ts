import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    proxy: {
      "/api": {
        target: "http://127.0.0.1:8000",
        changeOrigin: true,
      },
    },
  },
  build: {
    // Generate source maps for production
    sourcemap: true,
    // Ensure assets are built with hash for cache busting
    assetsDir: "assets",
    // Output directory (this should match what we copy in Dockerfile)
    outDir: "dist",
  },
});
