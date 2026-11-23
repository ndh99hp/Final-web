import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// chạy ở cổng 3000 (Django đã cho phép cổng này gọi API - CORS)
export default defineConfig({ plugins: [react()], server: { port: 3000, strictPort: true } });
