// ================================================================
// JARVIS CV
// ARQUIVO: index.ts (analyze-match)
// DESCRIÇÃO: Backend de Processamento ATS via NVIDIA API (Expert Mode)
// AUTOR: SILVANO MORAES DE SOUZA
// VERSÃO: 1.2.0
// ================================================================
// Importação do servidor HTTP e cliente Supabase
import { serve } from 'https://deno.land/std@0.177.0/http/server.ts'
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

// Headers CORS para permitir requisições de qualquer origem
const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
}

serve(async (req) => {
  // Responde a requisições OPTIONS (preflight CORS)
  if (req.method === 'OPTIONS') return new Response('ok', { headers: corsHeaders })

  try {
    // Inicializa o cliente Supabase com variáveis de ambiente
    const supabaseClient = createClient(
      Deno.env.get('SUPABASE_URL') ?? '',
      Deno.env.get('SUPABASE_SERVICE_ROLE_KEY') ?? ''
    )

    // Extrai IDs do currículo e vaga da requisição
    const { resume_id, job_id } = await req.json()

    // Busca dados do currículo e da vaga no banco Supabase
    const { data: resume } = await supabaseClient.from('resumes').select('content, raw_text').eq('id', resume_id).single()
    const { data: job } = await supabaseClient.from('target_jobs').select('description').eq('id', job_id).single()

    if (!resume || !job) throw new Error('Contexto insuficiente: Currículo ou Vaga não encontrados')

    // Persona de Especialista Global em Recrutamento e ATS
    const systemPrompt = `Você é um Especialista Global em Recrutamento de Classe Mundial, Mestre em ATS (Applicant Tracking System) e Estrategista de Marca Profissional.
Sua missão é realizar uma análise semântica e estrutural profunda entre um currículo profissional e uma descrição de vaga para maximizar as chances do candidato de conseguir uma entrevista em empresas globais de elite.

Você DEVE retornar um objeto JSON estritamente válido com os seguintes campos:
{
  "score": number (0-100, representando compatibilidade ATS),
  "strengths": string[] (pontos detalhados onde o candidato excede ou atende aos requisitos),
  "weaknesses": string[] (lacunas críticas em experiência ou certificações faltantes),
  "missing_skills": string[] (palavras-chave específicas e habilidades técnicas faltantes para otimização ATS),
  "rewritten_summary": string (um resumo profissional de alto impacto, nível executivo, adaptado especificamente para esta vaga, usando verbos de poder e resultados quantificáveis),
  "recommendations": string[] (etapas estratégicas e acionáveis para melhorar o CV para esta função específica)
}

Diretrizes:
- Seja brutalmente honesto e objetivo.
- Foque em "Impacto" em vez de "Responsabilidades".
- Identifique "Palavras-chave Ocultas" da descrição da vaga que deveriam estar no currículo.

Responda EXCLUSIVAMENTE em PORTUGUÊS BRASILEIRO (pt-br).`;

    // Monta o prompt do usuário com os dados
    const userPrompt = `CURRÍCULO DO CANDIDATO: ${JSON.stringify(resume.content)}\n\nDESCRIÇÃO DA VAGA ALVO: ${job.description}`;

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
    const matchData = JSON.parse(aiResult.choices[0].message.content)

    // Salva resultados no banco Supabase
    const { data, error } = await supabaseClient
      .from('optimization_results')
      .upsert({
        resume_id,
        job_id,
        ats_score: matchData.score,
        missing_skills: matchData.missing_skills,
        rewritten_summary: matchData.rewritten_summary,
        improvements: matchData.recommendations,
        analysis: {
          strengths: matchData.strengths,
          weaknesses: matchData.weaknesses
        },
        user_id: resume.user_id
      })
      .select()
      .single()

    if (error) throw error

    // Retorna dados salvos
    return new Response(JSON.stringify(data), { 
      status: 200, 
      headers: { ...corsHeaders, 'Content-Type': 'application/json' } 
    })

  } catch (err) {
    // Log e retorno de erro
    console.error('Erro no Backend:', err.message)
    return new Response(JSON.stringify({ error: err.message }), { 
      status: 400, 
      headers: { ...corsHeaders, 'Content-Type': 'application/json' } 
    })
  }
})
