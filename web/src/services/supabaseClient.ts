// ================================================================
// JARVIS CV
// ARQUIVO: supabaseClient.ts
// DESCRIÇÃO: Cliente de conexão com o backend Supabase e API Local
// AUTOR: SILVANO MORAES DE SOUZA
// VERSÃO: 1.2.0
// ================================================================
import { createClient } from '@supabase/supabase-js';
import { API_BASE } from '../config';

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL || '';
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY || '';

export const supabase = supabaseUrl ? createClient(supabaseUrl, supabaseAnonKey) : null;

export const jarvisApi = {
  async analyzeRaw(cv_text: string, job_text: string) {
    const response = await fetch(`${API_BASE}/analysis/ats/raw`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ cv_text, job_text }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Erro na análise do servidor.');
    }

    return response.json();
  }
};