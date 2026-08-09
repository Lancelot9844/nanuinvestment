import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': 'http://127.0.0.1:8000',
      '/admin': 'http://127.0.0.1:8000',
      '/customer': 'http://127.0.0.1:8000',
      '/login': 'http://127.0.0.1:8000',
      '/media': 'http://127.0.0.1:8000',
      '/static/admin': 'http://127.0.0.1:8000',
      '/static/admin-modern.css': 'http://127.0.0.1:8000',
      '/static/admin-logo.png': 'http://127.0.0.1:8000',
    },
  },
  build: {
    outDir: '../templates/react',
    emptyOutDir: true,
    rollupOptions: {
      output: {
        entryFileNames: 'assets/index.js',
        chunkFileNames: 'assets/[name].js',
        assetFileNames: 'assets/[name][extname]',
      },
    },
  },
})
