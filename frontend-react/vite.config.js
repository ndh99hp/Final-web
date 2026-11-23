import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// React chạy ở http://localhost:3000 (trùng với CORS_ALLOWED_ORIGINS và FRONTEND_URL trong core/settings.py của Django)
export default defineConfig({
  plugins: [react()],
  server: { port: 3000, strictPort: true },
});
