# Graph Report - JARVIS CV  (2026-05-03)

## Corpus Check
- 54 files · ~26,202 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 216 nodes · 243 edges · 21 communities detected
- Extraction: 88% EXTRACTED · 12% INFERRED · 0% AMBIGUOUS · INFERRED: 29 edges (avg confidence: 0.8)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Community 0|Community 0]]
- [[_COMMUNITY_Community 1|Community 1]]
- [[_COMMUNITY_Community 2|Community 2]]
- [[_COMMUNITY_Community 3|Community 3]]
- [[_COMMUNITY_Community 4|Community 4]]
- [[_COMMUNITY_Community 5|Community 5]]
- [[_COMMUNITY_Community 6|Community 6]]
- [[_COMMUNITY_Community 7|Community 7]]
- [[_COMMUNITY_Community 8|Community 8]]
- [[_COMMUNITY_Community 9|Community 9]]
- [[_COMMUNITY_Community 10|Community 10]]
- [[_COMMUNITY_Community 11|Community 11]]
- [[_COMMUNITY_Community 12|Community 12]]
- [[_COMMUNITY_Community 13|Community 13]]
- [[_COMMUNITY_Community 14|Community 14]]
- [[_COMMUNITY_Community 15|Community 15]]
- [[_COMMUNITY_Community 16|Community 16]]
- [[_COMMUNITY_Community 29|Community 29]]
- [[_COMMUNITY_Community 30|Community 30]]
- [[_COMMUNITY_Community 31|Community 31]]
- [[_COMMUNITY_Community 32|Community 32]]

## God Nodes (most connected - your core abstractions)
1. `normalize_text()` - 11 edges
2. `AIEngine` - 10 edges
3. `SupabaseClient` - 10 edges
4. `ATSEngine` - 9 edges
5. `JobScraper` - 9 edges
6. `LinkedInOptimizer` - 7 edges
7. `Logger` - 6 edges
8. `JobResponse` - 5 edges
9. `ResumeResponse` - 5 edges
10. `UserResponse` - 5 edges

## Surprising Connections (you probably didn't know these)
- `create_job()` --calls--> `JobResponse`  [INFERRED]
  api\app\routers\jobs.py → api\app\models\job.py
- `get_job()` --calls--> `JobResponse`  [INFERRED]
  api\app\routers\jobs.py → api\app\models\job.py
- `upload_resume()` --calls--> `ResumeResponse`  [INFERRED]
  api\app\routers\resumes.py → api\app\models\resume.py
- `get_resume()` --calls--> `ResumeResponse`  [INFERRED]
  api\app\routers\resumes.py → api\app\models\resume.py
- `generate_cover_letter()` --calls--> `AnalysisResponse`  [INFERRED]
  api\app\routers\analysis.py → api\app\models\analysis.py

## Communities (47 total, 10 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.14
Nodes (10): ATSEngine, ATSResult, Scoring ATS completo - 6 dimensões com pesos reais, Converte ATSResult para dict compatível com API, Motor ATS Local - Scoring determinístico híbrido, LinkedInAudit, LinkedInOptimizer, Auditoria completa de perfil LinkedIn (+2 more)

### Community 1 - "Community 1"
Cohesion: 0.14
Nodes (19): BaseModel, AnalysisHybridResponse, AnalysisRawRequest, AnalysisRequest, AnalysisResponse, CoverLetterRequest, WeeklyStrategyResponse, PasswordReset (+11 more)

### Community 2 - "Community 2"
Cohesion: 0.16
Nodes (8): AIEngine, Motor de IA Multi-Model — 5 especialistas NVIDIA, Análise ATS completa - 9 outputs realistas (BRAIN model), Carta de apresentação executiva (WRITER model), Estratégia semanal de guerra (PLANNER model), Auditoria completa de LinkedIn (ANALYZER model), Score de fit por vaga (FAST model), Reescrita de currículo (WRITER model)

### Community 3 - "Community 3"
Cohesion: 0.19
Nodes (11): JobList, JobManual, JobResponse, JobSearch, JobSearchRequest, JobSearchResult, create_job(), get_job() (+3 more)

### Community 5 - "Community 5"
Cohesion: 0.27
Nodes (3): JobMatch, JobScraper, Engine de Vagas - Scraping modular com 9 portais

### Community 6 - "Community 6"
Cohesion: 0.31
Nodes (6): ResumeList, ResumeResponse, ResumeUpload, get_resume(), list_resumes(), upload_resume()

### Community 7 - "Community 7"
Cohesion: 0.5
Nodes (6): TokenResponse, UserResponse, _create_token(), login(), refresh_token(), register()

### Community 8 - "Community 8"
Cohesion: 0.29
Nodes (6): check_rate_limit(), get_current_user(), Decodifica JWT e retorna dados do usuário autenticado, Factory que cria dependência para verificar plano mínimo do usuário, Verifica limites de uso diário baseado no plano do usuário, require_plan()

### Community 11 - "Community 11"
Cohesion: 0.4
Nodes (4): _add_horizontal_line(), DocxGenerator, generate_premium_resume(), Pipeline DOCX Premium - Template ATS recruiter-friendly sem mentira

### Community 12 - "Community 12"
Cohesion: 0.4
Nodes (3): Config, Settings, BaseSettings

### Community 13 - "Community 13"
Cohesion: 0.4
Nodes (4): Inicialização: conexão Redis, verificação de serviços, Encerramento: fechamento de conexões, shutdown(), startup()

## Knowledge Gaps
- **27 isolated node(s):** `Config`, `Decodifica JWT e retorna dados do usuário autenticado`, `Factory que cria dependência para verificar plano mínimo do usuário`, `Verifica limites de uso diário baseado no plano do usuário`, `Inicialização: conexão Redis, verificação de serviços` (+22 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **10 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `normalize_text()` connect `Community 0` to `Community 5`?**
  _High betweenness centrality (0.018) - this node is a cross-community bridge._
- **Why does `ResumeResponse` connect `Community 6` to `Community 1`?**
  _High betweenness centrality (0.010) - this node is a cross-community bridge._
- **Are the 10 inferred relationships involving `normalize_text()` (e.g. with `._extract_keywords()` and `._detect_sections()`) actually correct?**
  _`normalize_text()` has 10 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Config`, `Decodifica JWT e retorna dados do usuário autenticado`, `Factory que cria dependência para verificar plano mínimo do usuário` to the rest of the system?**
  _27 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Community 0` be split into smaller, more focused modules?**
  _Cohesion score 0.14 - nodes in this community are weakly interconnected._
- **Should `Community 1` be split into smaller, more focused modules?**
  _Cohesion score 0.14 - nodes in this community are weakly interconnected._