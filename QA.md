# ================================================================
# JARVIS CV — RELATÓRIO DE QA
# ARQUIVO: QA.md
# DATA: 02/05/2026
# QA: Testes completos de interface, código e segurança
# ================================================================

# RELATÓRIO COMPLETO DE QUALIDADE — JARVIS CV v3.0.0

---

## RESUMO EXECUTIVO

| Métrica | Valor |
|---------|-------|
| Páginas testadas | 8 (/, /vagas, /linkedin, /login, /registro, /precos, /dashboard, 404) |
| Bugs CRÍTICOS | 3 |
| Bugs HIGH | 6 |
| Bugs MEDIUM | 5 |
| Bugs LOW | 4 |
| **Total de Findings** | **18** |

---

## METODOLOGIA DE TESTE

- **Análise Estática**: Revisão completa de 32 arquivos de código fonte (React/TypeScript + Python/FastAPI)
- **Teste de Interface**: Navegação real no browser (Chrome DevTools) em todas as 8 rotas
- **Teste de Responsividade**: Simulação de viewport mobile (375x812)
- **Teste de Acessibilidade**: Verificação de tab navigation, HTML5 validation, heading hierarchy
- **Análise de Segurança**: Verificação de secrets expostos, .gitignore, validação de inputs

---

## BUGS CRÍTICOS

### [CRIT-001] SEM MENU MOBILE — NAVEGAÇÃO INACESSÍVEL NO MOBILE
**Severidade**: CRÍTICO  
**Local**: `web/src/components/layout/Navbar.tsx`  
**Descrição**: Os links de navegação "Vagas", "LinkedIn" e "Preços" estão dentro de `<div className="hidden md:flex">` que só aparece em telas >= 768px. NÃO existe menu hamburger ou qualquer alternativa de navegação para mobile (<= 767px). Usuários mobile só conseguem ver Home + botão "Começar Agora".

**Reprodução**:
1. Reduza o browser para largura < 768px
2. Observe que Vagas, LinkedIn, Preços desaparecem
3. Não há botão hamburger, drawer, ou bottom nav

**Sugestão**: Adicionar `useState` com toggle de menu mobile + ícone hamburger (lucide-react tem `Menu`/`X`) com `md:hidden`.

---

### [CRIT-002] SEM PÁGINA 404 — ROTA INVÁLIDA MOSTRA TELA EM BRANCO
**Severidade**: CRÍTICO  
**Local**: `web/src/App.tsx:215-223`  
**Descrição**: O `Routes` não possui `<Route path="*" element={<NotFound />} />`. Navegar para qualquer rota inválida (ex: `/admin`, `/qualquercoisa`) mostra navbar + footer com conteúdo completamente vazio. Nenhuma mensagem de erro.

**Reprodução**:
1. Navegue para `http://localhost:5173/rota-inexistente`
2. Página mostra navbar + footer sem conteúdo

**Sugestão**: Adicionar componente `NotFound` com link "Voltar ao início" e `<Route path="*" element={<NotFound />} />` como última rota.

---

### [CRIT-003] NENHUM .gitignore — RISCO DE COMMIT DE SECRETS
**Severidade**: CRÍTICO  
**Local**: Raiz do projeto  
**Descrição**: O repositório não possui arquivo `.gitignore`. Arquivos como `.env` (contendo `NVIDIA_API_KEY` real), `__pycache__/`, `node_modules/`, e `dist/` podem ser acidentalmente commitados. Atualmente o repo está sem commits, mas qualquer `git add . && git commit` vazará a chave NVIDIA.

**Sugestão**: Criar `.gitignore` com pelo menos:
```
.env
__pycache__/
node_modules/
dist/
*.pyc
.venv/
```

---

## BUGS HIGH

### [HIGH-001] COLUNA ERRADA NO `log_usage` — GRAVAÇÃO DE USO COR ROMPIDA
**Severidade**: HIGH  
**Local**: `api/app/utils/supabase_client.py:66-72`  
**Descrição**: O método `log_usage` insere `{"user_id": user_id, "feature": feature}`, mas a tabela `usage_logs` no banco define a coluna como `action TEXT NOT NULL CHECK (action IN (...))`. A coluna `feature` não existe. Isso causa erro no banco toda vez que um log de uso é tentado.

**Também afeta**: `get_daily_usage` (linha 78) que faz `.eq("feature", feature)` — mesma coluna errada.

**Linhas exatas**: `supabase_client.py:69` e `supabase_client.py:78`

---

### [HIGH-002] ENV VARS USAM `process.env` EM VEZ DE `import.meta.env`
**Severidade**: HIGH  
**Local**: `web/src/services/supabaseClient.ts:10-11`  
**Descrição**: O código usa `process.env.REACT_APP_*` que é padrão Create React App, mas o projeto usa **Vite**. No Vite, variáveis de ambiente devem usar `import.meta.env.VITE_*`. Como resultado, `supabaseUrl` e `supabaseAnonKey` serão sempre strings vazias, e o cliente Supabase é criado com valores inválidos.

**Código atual**:
```typescript
const supabaseUrl = process.env.REACT_APP_SUPABASE_URL || '';
const supabaseAnonKey = process.env.REACT_APP_SUPABASE_ANON_KEY || '';
```

**Correção**:
```typescript
const supabaseUrl = import.meta.env.VITE_SUPABASE_URL || '';
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY || '';
```

---

### [HIGH-003] ENDPOINT INEXISTENTE NO `jarvisApi.analyzeRaw`
**Severidade**: HIGH  
**Local**: `web/src/services/supabaseClient.ts:17`  
**Descrição**: O método `analyzeRaw` chama `http://localhost:3001/analyze`, mas a rota correta no backend é `POST /api/analysis/ats/raw`. A rota `/analyze` não existe.

**NOTA**: Este método parece ser código legado — o `App.tsx` não o utiliza (chama `${API_BASE}/analysis/ats/raw` diretamente).

---

### [HIGH-004] API_BASE HARDCODED EM 6 ARQUIVOS — SEM OVERRIDE POR ENV
**Severidade**: HIGH  
**Local**: Múltiplos arquivos frontend  
**Descrição**: `const API_BASE = 'http://localhost:3001/api'` está hardcoded em:
- `web/src/App.tsx:20` (Analisador ATS)
- `web/src/components/auth/AuthPage.tsx:12` (Login/Registro)
- `web/src/components/dashboard/DashboardPage.tsx:16` (Dashboard)
- `web/src/components/jobs/JobSearchPage.tsx:11` (Vagas)
- `web/src/components/linkedin/LinkedInAuditPage.tsx:11` (LinkedIn)
- `web/src/components/pricing/PricingPage.tsx:11` (Preços)

Em produção, isso impossibilita apontar para o backend real sem rebuild. Não há arquivo de configuração centralizado ou env var para API_BASE.

**Sugestão**: Criar constante centralizada em `src/config.ts` usando `import.meta.env.VITE_API_BASE`.

---

### [HIGH-005] BOTÃO "VER DEMO" SEM AÇÃO
**Severidade**: HIGH  
**Local**: `web/src/components/home/Hero.tsx:44`  
**Descrição**: O botão "Ver Demo" no Hero Section é um `<button>` sem `onClick` handler. É um botão morto que não faz absolutamente nada quando clicado.

**Código**:
```tsx
<button className="btn-ghost px-10 py-4 rounded-2xl text-lg">
  Ver Demo
</button>
```

---

### [HIGH-006] `refresh_token` É UM STUB VAZIO
**Severidade**: HIGH  
**Local**: `api/app/routers/auth.py:87-90`  
**Descrição**: O endpoint `POST /api/auth/refresh` está declarado mas implementado como stub que não faz nada (`pass`). A dependência `Depends(lambda: None)` é injetada mas o token nunca é verificado ou renovado. Qualquer chamada retorna `null` silenciosamente.

---

## BUGS MEDIUM

### [MED-001] MÉTODO `_normalize` DUPLICADO EM 3 ARQUIVOS
**Severidade**: MEDIUM  
**Local**: `ats_engine.py:66-75`, `job_scraper.py:267-275`, `linkedin_optimizer.py:95-103`  
**Descrição**: O mesmo método `_normalize()` (remoção de acentos, lowercasing, limpeza) está copiado em 3 arquivos diferentes. Viola DRY (Don't Repeat Yourself) e dificulta manutenção — qualquer mudança precisa ser feita 3 vezes.

**Sugestão**: Extrair para `api/app/utils/text_utils.py` como `normalize_text()`.

---

### [MED-002] REACT ROUTER V7 DEPRECATION WARNINGS
**Severidade**: MEDIUM  
**Local**: Console do browser em todas as páginas  
**Descrição**: Dois warnings aparecem no console ao carregar qualquer página:
```
React Router Future Flag Warning: React Router will begin wrapping state updates in `React.startTransition` in v7.
React Router Future Flag Warning: Relative route resolution within Splat routes is changing in v7.
```

**Sugestão**: Adicionar `future={{ v7_startTransition: true, v7_relativeSplatPath: true }}` ao `<BrowserRouter>`.

---

### [MED-003] SEM TOGGLE DE VISIBILIDADE DE SENHA
**Severidade**: MEDIUM  
**Local**: `web/src/components/auth/AuthPage.tsx:105-116`  
**Descrição**: Os campos de senha no login e registro são `<input type="password">` puros. Não há ícone/botão para mostrar/ocultar a senha. Isso é uma convenção de UX moderna esperada e também melhora acessibilidade.

**Sugestão**: Adicionar botão com ícone `Eye`/`EyeOff` do lucide-react que alterna `type` entre `password` e `text`.

---

### [MED-004] SEM INDICADOR DE FORÇA DE SENHA NO REGISTRO
**Severidade**: MEDIUM  
**Local**: `web/src/components/auth/AuthPage.tsx` (modo register)  
**Descrição**: O campo de senha no registro não tem indicador de força (fraco/médio/forte). O único requisito visível é `minLength={6}` na DOM, mas não há feedback visual se a senha é forte o suficiente.

**Sugestão**: Adicionar barra de força com validação de: min 8 chars, maiúscula, número, caractere especial.

---

### [MED-005] PDFs ESCANEADOS NÃO SÃO EXTRAÍDOS
**Severidade**: MEDIUM  
**Local**: `api/app/services/resume_parser.py:41-49`  
**Descrição**: O parser de PDF usa `PdfReader.extract_text()` que só funciona com PDFs baseados em texto. PDFs escaneados (imagens de currículo) retornariam texto vazio sem nenhum aviso. Não há fallback para OCR (pytesseract).

**Sugestão**: Verificar se texto extraído é vazio e retornar erro claro: "PDF parece ser imagem escaneada. Converta para PDF com texto selecionável."

---

## BUGS LOW

### [LOW-001] SEM `tsconfig.json` NA RAIZ DO PROJETO WEB
**Severidade**: LOW  
**Local**: `web/`  
**Descrição**: O `package.json` define `"build": "tsc && vite build"`, mas não existe `tsconfig.json` no diretório `web/`. O build atual funciona porque o `dist/` já está gerado, mas qualquer `npm run build` limpo falharia no passo `tsc`.

**Sugestão**: Criar `tsconfig.json` ou mudar build para `"build": "vite build"` (Vite já faz type-check parcial).

---

### [LOW-002] CAMPO "NOME COMPLETO" NO REGISTRO SEM `required`
**Severidade**: LOW  
**Local**: `web/src/components/auth/AuthPage.tsx:83-89`  
**Descrição**: O campo de nome completo no registro não tem o atributo `required`, ao contrário de email e senha. O backend também tem `full_name: Optional[str] = None`, então um registro sem nome funciona, mas a UX no dashboard mostra "Usuário" como fallback.

---

### [LOW-003] EMAIL DO CRIADOR NO FOOTER DO DOCX
**Severidade**: LOW  
**Local**: `api/app/services/docx_generator.py:223`  
**Descrição**: O footer do DOCX gerado contém email pessoal hardcoded: `jarmoraez@gmail.com`. Embora seja intencional (assinatura do criador), pode ser melhor usar uma variável de ambiente ou email de suporte configurável.

---

### [LOW-004] VALIDAÇÃO DE `cv.length < 200` VISUAL MAS NÃO BLOQUEANTE
**Severidade**: LOW  
**Local**: `web/src/App.tsx:104-106`  
**Descrição**: O analisador mostra aviso "Mínimo 200 caracteres" quando `cv.length < 200 && cv.length > 0`, mas o botão "Analisar" só é desabilitado quando `!cv || !job` (ambos vazios). Ou seja, é possível enviar CV com < 200 caracteres. O motor ATS local já trata isso (`_check_format_issues` retorna erro "muito curto"), mas o frontend poderia reforçar com `disabled={loading || !cv || !job || cv.length < 200}`.

---

## TESTES DE INTERFACE

### Páginas testadas no browser real (localhost:5173):

| Rota | Status | Observações |
|------|--------|-------------|
| `/` (Landing) | OK | Hero + Analisador renderizados corretamente |
| `/vagas` | OK | Busca funcional, botão Remoto alterna |
| `/linkedin` | OK | Formulário renderizado, botão desabilitado sem dados |
| `/login` | OK | Validação HTML5 nativa funciona |
| `/registro` | OK | Nome/email/senha + link para login |
| `/precos` | OK | 3 cards, Free → /registro, Pro → /login (sem token) |
| `/dashboard` | OK | Redireciona para /login sem token (comportamento correto) |
| `/rota-que-nao-existe` | **BUG** | Tela em branco, sem 404 (CRIT-002) |

### Comportamento de formulários:

| Componente | Comportamento |
|------------|--------------|
| Textareas (Analisador) | Controlados por React state, contador de caracteres |
| Login form | Submit bloqueado por `required` nativo |
| Registro | Submit bloqueado por `required` em email/senha, nome opcional |
| Botão Analisar | Desabilitado até ambos campos terem conteúdo |
| Botão Auditar LinkedIn | Desabilitado até pelo menos 1 campo preenchido |

---

## TESTES DE RESPONSIVIDADE

| Viewport | Navbar | Hero | Textareas | Footer |
|----------|--------|------|-----------|--------|
| 1440px (Desktop) | OK | OK | Grid 2 colunas | OK |
| 1024px (Tablet) | OK | OK | Grid 2 colunas | OK |
| 768px (Tablet small) | Links visíveis | OK | Stack vertical | OK |
| 375px (Mobile) | **BUG** — Sem menu! | OK | Stack vertical | OK |

---

## TESTES DE NAVEGAÇÃO E FLUXO

1. Fluxo Home → Login → Dashboard:  
   `/login` mostra formulário → sem token, `/dashboard` redireciona corretamente para `/login`. OK.

2. Fluxo Pricing → Registro:  
   "Começar Grátis" → `/registro`. OK.  
   "Assinar Pro" → `/login` (sem token). OK.

3. Navegação entre páginas via Navbar:  
   Links "Vagas", "LinkedIn", "Preços" funcionam no desktop. Mobile quebrado (CRIT-001).

4. Deep linking:  
   Navegar diretamente para `/vagas`, `/linkedin`, `/precos` funciona. OK.

---

## ANÁLISE DE CÓDIGO

### O que está bom:
- Design system premium consistente (Tailwind classes reutilizáveis)
- Componentização adequada (separação por domínio)
- Tratamento de erros try/catch em todos os endpoints
- Sistema híbrido ATS (local + IA) com fallback
- FastAPI bem estruturado (routers, models, services)
- Tipagem Pydantic forte em todos os modelos
- Logging estruturado em todas as camadas

### O que precisa melhorar:
- Não há testes automatizados (unit, integration, e2e)
- Múltiplos `API_BASE` hardcoded
- Mix de estilos de endpoint (`/api/analysis/ats` vs `/analysis/ats/raw`)
- `refresh_token` é um stub vazio
- Sem rate limiting real implementado (só verifica permissão, não conta uso diário)

---

## VERIFICAÇÃO DE SEGURANÇA

| Item | Status | Observações |
|------|--------|-------------|
| API key NVIDIA em .env | OK (não commitado) | Mas sem .gitignore, risco existe |
| JWT secret hardcoded | ⚠️ | `jarvis-cv-secret-key-change-in-production` — padrão fraco |
| HTTPS | N/A | Apenas dev local |
| SQL Injection | OK | Supabase client parametrizado |
| XSS | ⚠️ | React escapa por padrão, mas `dangerouslySetInnerHTML` não usado = OK |
| CORS | OK | Configurado no FastAPI |
| Rate Limiting | ⚠️ | Definido mas não implementado (não checa Redis/counts) |
| LGPD | ⚠️ | Definido no CONCLUIDO.md mas não implementado |
| Stripe webhook | OK | Verificação de assinatura implementada |

---

## RECOMENDAÇÕES PRIORIZADAS

### Para o próximo commit (IMEDIATO):
1. ✅ Criar `.gitignore` com `.env`, `__pycache__/`, `node_modules/`, `dist/`
2. ✅ Implementar menu hamburger mobile no Navbar
3. ✅ Adicionar página 404
4. ✅ Corrigir `feature` → `action` no `supabase_client.py`

### Para a próxima sprint:
5. Corrigir `process.env` → `import.meta.env` no `supabaseClient.ts`
6. Centralizar `API_BASE` em arquivo de config com env var
7. Adicionar ação ao botão "Ver Demo" (ou removê-lo)
8. Implementar `refresh_token` no backend
9. Adicionar toggle de visibilidade de senha

### Para o futuro:
10. Criar `tsconfig.json` ou simplificar build
11. Extrair `_normalize()` para util compartilhado
12. Adicionar indicador de força de senha
13. Implementar OCR fallback para PDFs escaneados
14. Adicionar testes automatizados

---

## CONCLUSÃO

O projeto JARVIS CV apresenta uma arquitetura bem planejada com separação clara de responsabilidades (frontend React, backend FastAPI, Supabase). O design system é consistente e premium.

**Pontos fortes**: Estrutura de código limpa, tipagem forte, tratamento de erros robusto, motor ATS híbrido inovador, boa componentização.

**Pontos críticos a resolver**: Sem navegação mobile (quebra experiência para ~60% dos usuários), sem página 404, sem .gitignore (risco de vazamento de secrets), e bugs de integração banco de dados (coluna `feature` vs `action`).

**Nota geral**: 7.2/10 — Aplicação funcional mas com débito técnico significativo que precisa ser resolvido antes do deploy em produção.

---

*Relatório gerado em 02/05/2026 via análise automatizada + testes manuais no browser.*