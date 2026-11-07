import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// https://vite.dev/config/
export default defineConfig({
  // Relative base so the build works under any GitHub Pages path (/<repo>/) or a custom domain.
  base: "./",
  plugins: [react()],
})
