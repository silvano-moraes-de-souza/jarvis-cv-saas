// ================================================================
// JARVIS CV
// ARQUIVO: vite.config.ts
// DESCRIÇÃO: Configuração do Vite para React + TypeScript
// AUTOR: SILVANO MORAES DE SOUZA
// VERSÃO: 1.0.0
// ================================================================
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    host: true
  }
})
