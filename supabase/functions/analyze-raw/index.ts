// ================================================================
// JARVIS CV
// ARQUIVO: index.ts (analyze-raw)
// DESCRIÇÃO: Análise Bruta - Especialista Global em ATS (Soberano Mode)
// AUTOR: SILVANO MORAES DE SOUZA
// VERSÃO: 1.2.0
// ================================================================
// Importação do servidor HTTP do Deno
import { serve } from 'https://deno.land/std@0.177.0/http/server.ts'

// Headers CORS para permitir requisições de qualquer origem
const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
}

serve(async (req) => {
  // Responde a requisições OPTIONS (preflight CORS)
  if (req.method === 'OPTIONS') return new Response('ok', { headers: corsHeaders })

  try {
    // Extrai os dados da requisição
    const { cv_text, job_text } = await req.json()

    // Prompt do sistema - define o comportamento da IA
    const systemPrompt = `Você é um Especialista Global em Recrutamento de Classe Mundial, Mestre em ATS e Estrategista de Marca Profissional.
Sua análise deve ser BRUTALMENTE HONESTA. Não use eufemismos.
Responda EXCLUSIVAMENTE em PORTUGUÊS BRASILEIRO (pt-br).
Retorne um objeto JSON PURO com exatamente estas chaves:
{
  "score": number,
  "strengths": string[],
  "weaknesses": string[],
  "missing_skills": string[],
  "rewritten_summary": string,
  "suggested_headline": string,
  "recommendations": string[]
}`;

    // Prompt do usuário com os dados
    const userPrompt = `CURRÍCULO: ${cv_text}\n\nVAGA: ${job_text}`;

    // Requisição para a API NVIDIA
    const response = await fetch('https://integrate.api.nvidia.com/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${Deno.env.get('NVIDIA_API_KEY')}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        model: 'qwen/qwen3.5-122b-a10b',
        messages: [
          { role: 'system', content: systemPrompt },
          { role: 'user', content: userPrompt }
        ],
        temperature: 0.6,
        top_p: 0.95,
        max_tokens: 16384,
        response_format: { type: 'json_object' },
      })
    })

    // Processa resposta da IA
    const aiResult = await response.json()
    return new Response(aiResult.choices[0].message.content, { 
      status: 200, 
      headers: { ...corsHeaders, 'Content-Type': 'application/json' } 
    })

  } catch (err) {
    // Tratamento de erros
    return new Response(JSON.stringify({ error: err.message }), { status: 400, headers: { ...corsHeaders, 'Content-Type': 'application/json' } })
  }
})
