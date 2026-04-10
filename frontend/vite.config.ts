import path from "node:path";
import react from "@vitejs/plugin-react-swc";
import { defineConfig } from "vitest/config";

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "src"),
      "@shared": path.resolve(__dirname, "../shared"),
    },
  },
  server: {
    allowedHosts: [".up.railway.app"],
    fs: {
      allow: [path.resolve(__dirname, "..")],
    },
  },
  preview: {
    allowedHosts: [".up.railway.app"],
  },
  test: {
    environment: "jsdom",
    setupFiles: "./src/test/setup.ts",
    globals: true,
  },
});
