import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    // En desarrollo, /api/... va al backend (uvicorn en el puerto 8000).
    // Así el frontend usa rutas relativas y no hace falta configurar CORS.
    proxy: {
      '/api': 'http://localhost:8000',
    },
  },
})
