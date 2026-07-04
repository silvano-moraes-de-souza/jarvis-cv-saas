// ================================================================
// JARVIS CV
// ARQUIVO: tailwind.config.js
// DESCRIÇÃO: Configuração do Tailwind CSS para estilização da aplicação
// AUTOR: SILVANO MORAES DE SOUZA
// VERSÃO: 1.2.0
// ================================================================
/** @type {import('tailwindcss').Config} */
export default {
  // Arquivos que o Tailwind deve escanear para classes CSS
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}