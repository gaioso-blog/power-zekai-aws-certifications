# zekai-aws-certifications

> 🇬🇧 [English documentation available in README.en.md](README.en.md)

Um Kiro Power que transforma o IDE em um motor completo de estudo para certificações AWS.
Gera questões originais fundamentadas em documentação oficial, simulados interativos,
desafios de arquitetura com rubrica ponderada, flashcards, planos de estudo e comparações
de serviços para qualquer certificação AWS atual — Foundational, Associate, Professional e Specialty.

> Cada resposta cita documentação oficial da AWS. Sem invenções, sem alucinações,
> sem necessidade de conta ou credenciais AWS.

---

## Índice

- [Por que este power?](#por-que-este-power)
- [Funcionalidades](#funcionalidades)
- [Exames suportados](#exames-suportados)
- [Instalação](#instalação)
- [Modos de estudo](#modos-de-estudo)
  - [Modo Estudo](#modo-estudo)
  - [Modo Quiz Interativo](#modo-quiz-interativo)
  - [Modo Desafio de Arquitetura](#modo-desafio-de-arquitetura)
  - [Modo Análise de Questão](#modo-análise-de-questão)
- [Estado da sessão](#estado-da-sessão)
- [Referência dos scripts](#referência-dos-scripts)
  - [session.py](#sessionpy)
  - [resolve_exam.py](#resolve_exampy)
  - [export_report.py](#export_reportpy)
- [Estrutura de arquivos](#estrutura-de-arquivos)
- [Configuração](#configuração)
- [Modelos recomendados](#modelos-recomendados)
- [Solução de problemas](#solução-de-problemas)
- [Aviso legal](#aviso-legal)

---

## Por que este power?

Exames de certificação AWS testam raciocínio arquitetural, não memorização. Estudo passivo
(vídeos, flashcards) só vai até certo ponto. Você precisa de prática ativa: cenários
realistas, feedback ponderado fundamentado em fontes oficiais e exercícios de design que
forçam você a propor soluções antes de ver a resposta.

Este power oferece quatro modos de estudo complementares dentro do Kiro. Instale uma vez
e tenha um kit de estudo completo que se adapta a qualquer certificação AWS, incluindo
exames recém-lançados verificados contra o índice oficial em tempo real.

---

## Funcionalidades

- **Contexto de exame sempre ativo** — cada resposta é adaptada ao exame escolhido:
  mapeamento de domínios, citações da documentação oficial e adaptação de linguagem.
- **Quatro modos de estudo** — Estudo, Quiz Interativo, Desafio de Arquitetura e Análise
  de Questão, cada um treinando uma habilidade cognitiva diferente.
- **Estado de sessão persistente** — pontuação, sequências, tópicos perguntados e questões
  pendentes sobrevivem à compactação de contexto e a novas sessões de chat via estado em
  disco (`~/.zekai`).
- **Cronômetro por questão** — cada questão no Quiz Interativo é cronometrada do momento
  em que aparece até o envio da resposta. O tempo decorrido é exibido no bloco
  pós-resposta e consolidado no relatório final com média por domínio.
- **Cobertura ponderada por domínio** — a seleção de questões espelha os pesos de domínio
  do guia oficial do exame, não intuição.
- **Anti-repetição** — histórico de tópicos por sessão e entre sessões impede que o mesmo
  cenário apareça duas vezes no mesmo arco de aprendizado.
- **Dificuldade adaptativa** — sinais automáticos do `session.py` sugerem aumento de
  dificuldade após acertos consecutivos e explicações de conceito após sequências de erros.
- **Modo Desafio de Arquitetura** — propostas de design livres avaliadas contra uma
  rubrica ponderada, com uma mudança de requisito inesperada ("curveball") que força
  adaptação real.
- **Quality gate** — checklist de 12 itens roda silenciosamente antes de cada questão
  hard/exam-level; ativável no modo debug para auditoria completa.
- **Calibração de dificuldade** — feedback de dificuldade percebida após questões difíceis
  é registrado e usado para fechar a lacuna entre a dificuldade gerada e a real do exame.
- **Relatórios markdown** — relatórios completos de sessão salvos em
  `ExamResults/<CÓDIGO>/` com score escalado, precisão por domínio, tempo por questão e
  log completo.
- **Multilíngue** — responde no idioma em que o usuário escreve.
- **Apenas fontes oficiais** — cada afirmação factual é verificada via servidor MCP
  embutido de documentação AWS contra `docs.aws.amazon.com`.

---

## Exames suportados

O power funciona com qualquer exame de certificação AWS atual. No início da sessão, o
Kiro consulta a estrutura do exame (domínios, pesos, quantidade de questões, tempo limite,
nota de aprovação) no índice oficial em tempo real.

Metadados locais pré-carregados para estes exames:

| Nível | Código | Nome |
|---|---|---|
| Foundational | CLF-C02 | AWS Certified Cloud Practitioner |
| Foundational | AIF-C01 | AWS Certified AI Practitioner |
| Associate | SAA-C03 | AWS Certified Solutions Architect – Associate |
| Associate | DVA-C02 | AWS Certified Developer – Associate |
| Associate | SOA-C03 | AWS Certified CloudOps Engineer – Associate |
| Associate | DEA-C01 | AWS Certified Data Engineer – Associate |
| Associate | MLA-C01 | AWS Certified Machine Learning Engineer – Associate |
| Professional | SAP-C02 | AWS Certified Solutions Architect – Professional |
| Professional | DOP-C02 | AWS Certified DevOps Engineer – Professional |
| Professional | AIP-C01 | AWS Certified Generative AI Developer – Professional |
| Specialty | ANS-C01 | AWS Certified Advanced Networking – Specialty |
| Specialty | SCS-C02 | AWS Certified Security – Specialty |

Qualquer código não listado aqui é verificado automaticamente contra o índice oficial.
Exames recém-lançados são suportados sem necessidade de atualizar o power.

---

## Instalação

**Pré-requisitos**

| Requisito | Finalidade |
|---|---|
| Kiro IDE | Executa o power |
| `uv` | Executa o servidor MCP de documentação AWS embutido |

Instale o `uv` se ainda não estiver presente:
```bash
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# macOS via Homebrew
brew install uv
```

```powershell
# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Nenhuma conta ou credencial AWS é necessária — o servidor MCP lê apenas documentação pública.

**Passos**

1. Abra o Kiro e acesse o painel Powers na barra lateral.
2. Escolha **Add Custom Power**.
3. Selecione **Import power from GitHub**.
4. Informe a URL do repositório: `https://github.com/gaioso-blog/power-zekai-aws-certifications`.
5. Clique em **Install**.
6. Abra qualquer pasta de workspace — o Kiro exige uma pasta aberta para ativar powers.

**Verificar**

```
Estou estudando para o SAA-C03. O que é o Amazon S3?
```

O Kiro confirmará o exame, consultará sua estrutura no guia oficial e responderá com
conteúdo mapeado ao domínio correto.

---

## Modos de estudo

### Modo Estudo

Entrega a resposta completa imediatamente: questão, todas as alternativas, resposta
correta, explicação da opção correta, explicação de cada opção errada, armadilha do
exame, resumo para revisão e links da documentação oficial.

**Sinais de ativação:** "com gabarito", "com explicação", "questões resolvidas",
"explique as alternativas", "with answer key"

**Tamanho de lote padrão:** 5 questões. Pedidos de 6+ são entregues em lotes de 5.

Não usa estado do `session.py` a menos que o usuário peça rastreamento de pontuação.

---

### Modo Quiz Interativo

Uma questão por vez. A resposta e todos os metadados de fonte são ocultados até o
envio. Após o envio, a explicação completa é revelada.

**Sinais de ativação:** "modo quiz", "me pergunte uma por vez", "simulado interativo",
"mock exam", "me testa", "faça como prova"

**Padrão:** entra neste modo silenciosamente quando o sinal é ambíguo.

**Formatos de questão:**
- Escolha única: 1 de 4 opções (A–D)
- Múltipla resposta — selecione dois: 2 de 5 opções (A–E)
- Múltipla resposta — selecione três: 3 de 6 opções (A–F) — apenas Professional e Specialty

**Cronômetro por questão:** o timer inicia automaticamente quando a questão é exibida
(via `session.py timer-start`) e para quando você envia a resposta. O tempo decorrido
aparece no bloco de resultado logo abaixo da sua resposta, e é armazenado em cada
registro de resposta. No relatório final, você vê:
- Tempo total da sessão
- Tempo médio por questão
- Tempo médio por domínio
- Tempo individual de cada questão no log

Isso permite identificar quais domínios consomem mais tempo — útil para gerenciar o
tempo real do exame.

**Dificuldade adaptativa:** após 3 acertos consecutivos, o agente oferece subir de
nível. Após 2 erros consecutivos no mesmo domínio, oferece explicação do conceito.

**Anti-repetição:** `session.py suggest` seleciona o domínio com maior déficit ponderado
e retorna `avoid_topics` (sessão atual) e `historical_topics` (entre sessões) para
evitar reuso.

---

### Modo Desafio de Arquitetura

O aluno propõe uma arquitetura AWS livre para um cenário de negócio realista, recebe
feedback por rubrica ponderada e depois adapta o design após uma mudança inesperada de
requisito (o "curveball").

**Sinais de ativação:** "modo desafio", "desafio de arquitetura", "projete uma arquitetura",
"quero treinar design", "me dá um cenário aberto", "architecture challenge"

**Como funciona:**

1. **Fase inicial** — o aluno recebe um cenário e uma lista de 3–5 requisitos (sem
   alternativas pré-definidas, sem dicas). O aluno propõe uma arquitetura completa em
   texto livre.
2. **Avaliação por rubrica** — o agente avalia cada requisito como `satisfied`,
   `partial` (crédito de 0,5×) ou `missed`, depois chama `session.py design-grade
   --phase initial`.
3. **Revelação do curveball** — após a avaliação, uma nova restrição de negócio é
   revelada (ex.: "o cliente agora precisa de uma réplica de leitura em uma terceira
   região"). O curveball nunca é sugerido antes deste momento.
4. **Fase adaptada** — o aluno ajusta sua arquitetura. A pontuação agora inclui todos os
   requisitos originais mais o requisito adicionado pelo curveball (renormalizado para 100).
5. **Relatório final** — score combinado (média das duas fases), detalhamento por
   requisito, princípio arquitetural demonstrado, pontos fortes, armadilha do exame e
   links de documentação.

**Status da rubrica:**

| Status | Critério | Pontos |
|---|---|---|
| `satisfied` | Serviço correto nomeado com justificativa que atende o requisito | Peso total |
| `partial` | Direção certa mas serviço específico errado, ou serviço correto sem justificativa | 50% do peso |
| `missed` | Requisito ignorado, serviço errado, ou serviço certo pelo motivo errado | 0 |

**Limites de veredito (% combinada):**

| Score | Veredito |
|---|---|
| ≥ 80% | ✅ Excelente — arquitetura sólida |
| ≥ 70% | ✅ Aprovado — bom domínio dos requisitos |
| ≥ 50% | ⚠️ Parcial — revise os requisitos perdidos |
| < 50% | ❌ Precisa reforçar — releia a documentação indicada |

**Integração com sessão:** desafios concluídos são registrados em `session.py` nos campos
`answers` e `domain_stats`, contribuindo para anti-repetição, cobertura ponderada e o
relatório final, exatamente como questões de múltipla escolha.

---

### Modo Análise de Questão

Um diálogo guiado de quatro passos. O aluno e o agente analisam a mesma questão
independentemente em cada passo, o agente revela sua própria análise apenas após o
aluno enviar a dele.

**Sinais de ativação:** "modo análise", "analisar questão", "me ajuda a pensar",
"question breakdown", "walk me through", "como eu raciocino", "me ensina a eliminar"

**Os quatro passos:**

1. **Extraia o sinal** — identifique o objetivo, restrições explícitas, restrições
   implícitas e a palavra-chave do exame que guia a eliminação.
2. **Primeira eliminação** — elimine opções que violam uma restrição específica
   declarada. Cada eliminação deve nomear a restrição, não apenas "parece errada".
3. **Diferencie os finalistas** — para cada opção restante, explique por que satisfaz
   os requisitos e o que a desclassifica ou a torna segunda melhor.
4. **Reflita e generalize** — identifique a armadilha do exame, o padrão de raciocínio
   generalizável e um resumo de duas frases para revisão espaçada.

A resposta não é secreta neste modo, o processo de raciocínio é o produto.

---

## Estado da sessão

Todo o estado interativo vive em disco em `~/.zekai` (sobrescrito via `$ZEKAI_STATE_DIR`).

| Arquivo | Conteúdo |
|---|---|
| `session.json` | Sessão ativa: exame, dificuldade, pontuação, stats por domínio, questão pendente, estado do desafio de arquitetura |
| `history.json` | Tópicos perguntados por exame, entre todas as sessões (anti-repetição cross-session) |
| `calibration.jsonl` | Log append-only de dificuldade percebida vs gerada por questão |
| `sessions_archive.json` | Resumos de sessões concluídas usados pelo `export_report.py` |

O estado sobrevive à compactação de contexto, reinicializações do IDE e novas sessões de chat.

---

## Referência dos scripts

### session.py

`scripts/session.py` é a fonte da verdade para todo o estado de sessão interativa.
Emite JSON no stdout e usa código de saída 0 para sucesso, 1 para erros.

**Diretório de estado:** resolvido na ordem: flag `--state-dir` → `$ZEKAI_STATE_DIR` → `~/.zekai`

#### Comandos de Quiz / Simulação

| Comando | Argumentos | Descrição |
|---|---|---|
| `start` | `--exam CÓDIGO --difficulty NÍVEL [--total N] [--domains JSON] [--fresh]` | Inicia ou retoma uma sessão. `--domains` é um array JSON do guia oficial: `[{"name":"...", "weight":30}]`. Use `--fresh` para descartar uma sessão ativa. |
| `status` | — | Exibe resumo da sessão atual (pontuação, stats por domínio, questão pendente). |
| `pending-set` | `--payload JSON` | Persiste uma questão totalmente fundamentada antes de exibi-la. Campos obrigatórios: `domain`, `topic`, `question`, `options`, `correct_answers`, `grounding`. |
| `pending-get` | — | Recupera a questão pendente segura para o aluno (chave de resposta e grounding ocultos). |
| `pending-clear` | — | Pula e descarta a questão pendente sem avaliar. |
| `timer-start` | — | Registra o timestamp de exibição. Chame imediatamente após `pending-set` e antes de mostrar a questão. O `grade` calcula o tempo decorrido automaticamente a partir deste registro. |
| `grade` | `--response LETRAS [--elapsed-seconds N] [--difficulty NÍVEL]` | Avalia a questão pendente. Revela a chave de resposta apenas após o envio. Retorna array de `signals` adaptativos. |
| `calibrate` | `--perceived NÍVEL [--question N] [--notes TEXTO]` | Associa dificuldade percebida a uma resposta existente sem alterar a pontuação. Adiciona ao `calibration.jsonl`. |
| `suggest` | — | Retorna o domínio com maior déficit de cobertura ponderada, mais `avoid_topics` e `historical_topics`. |
| `asked` | `[--exam CÓDIGO] [--scope session\|history]` | Lista slugs de tópicos já usados na sessão atual ou no histórico completo. |
| `progress` | — | Exibe bloco de progresso (pontuação, domínio, sequência). |
| `debug` | `on\|off` | Ativa/desativa o bloco do quality gate de 12 itens antes de questões hard/exam-level. |
| `end` | `[--output-dir CAMINHO]` | Encerra a sessão, grava em `sessions_archive.json`, retorna JSON do relatório final. |
| `reset` | — | Descarta a sessão atual. Histórico e calibração são mantidos. |

**Sinais adaptativos do `grade`:**

| Sinal | Condição | Ação do agente |
|---|---|---|
| `offer_increase_difficulty` | 3 acertos consecutivos | Oferece subir um nível de dificuldade |
| `offer_concept_explanation` | 2 erros consecutivos no mesmo domínio | Oferece explicação breve do conceito |
| `show_progress_summary` | A cada 5 questões | Exibe o bloco de progresso |
| `session_complete` | `question_number >= total_planned` | Oferece encerrar a sessão |

**Fluxo do cronômetro por questão:**

```
1. session.py pending-set --payload '...'   → persiste a questão
2. session.py timer-start                   → registra timestamp de exibição
3. [exibe a questão ao aluno]
4. [aluno envia resposta]
5. session.py grade --response A            → calcula elapsed automaticamente
                                              (ou passe --elapsed-seconds N para sobrescrever)
```

Cada registro de resposta armazena `elapsed_seconds`. O comando `end` agrega
`total_seconds`, `avg_seconds_per_question` e timing por domínio no relatório final.

#### Comandos do Modo Desafio de Arquitetura

| Comando | Argumentos | Descrição |
|---|---|---|
| `design-start` | `--payload JSON --difficulty NÍVEL` | Persiste um desafio fundamentado antes de exibi-lo. Payload: `domain`, `topic`, `scenario`, `requirements` (`[{id, label, weight}]`), `curveball` (`{label, added_requirement: {id, label, weight}}`), `grounding`. Pesos são normalizados para 100 internamente. |
| `design-pending` | — | Retorna estado do desafio ativo. Curveball fica oculto (`curveball_hidden: true`) até a fase inicial ser avaliada. |
| `design-grade` | `--phase initial\|adapted --scores JSON [--elapsed-seconds N]` | Registra scores da rubrica e avança a fase. `--scores` é `[{id, status}]` onde `status` é `satisfied`, `partial` ou `missed`. Retorna `signal: curveball_revealed` após a fase inicial e `signal: challenge_complete` após a adaptada. |
| `design-clear` | — | Descarta o desafio ativo sem avaliar. |

**Scoring:** `satisfied` = peso total, `partial` = 50% do peso, `missed` = 0. Pesos são
normalizados para somar 100 por fase. A fase adaptada mescla os requisitos originais com
o requisito adicionado pelo curveball e renormaliza.

---

### resolve_exam.py

`scripts/resolve_exam.py <CÓDIGO>` valida um código de exame contra o catálogo local.

| Status retornado | Significado | Ação do agente |
|---|---|---|
| `local_catalog_match` | Código encontrado no cache local | Usa metadados enriquecidos; verifica contra o guia ao vivo |
| `needs_online_verification` | Código ausente do cache local | Busca no índice oficial; pode ser exame recém-lançado |
| `known_retired` | Código substituído ou retirado | Explica ao usuário; não prossegue |
| `malformed` | Entrada vazia | Pede o código exato ao usuário; nunca autocorrige |

O catálogo local é um cache de conveniência, não uma lista de permissão. Código de saída
0 para correspondências e candidatos a verificação online; 1 para códigos retirados e
malformados.

```bash
python3 scripts/resolve_exam.py SAA-C03   # verificar um código
python3 scripts/resolve_exam.py --list    # listar todos os exames em cache local
```

---

### export_report.py

`scripts/export_report.py` gera um relatório markdown completo de uma sessão encerrada.

```bash
python3 scripts/export_report.py                          # sessão mais recente
python3 scripts/export_report.py --index 2               # 3ª sessão (índice 0)
python3 scripts/export_report.py --output-dir ./reports  # diretório de saída personalizado
python3 scripts/export_report.py --stdout                # imprime no stdout em vez de arquivo
```

Arquivo de saída: `<output-dir>/ExamResults/<CÓDIGO>/<CÓDIGO>_<AAAAMMDD_HHMMSS>.md`

**Conteúdo do relatório:**
- Cartão resumo: exame, datas, pontuação, score escalado (100–1000), veredito aprovado/reprovado
- Tabela de desempenho por domínio com barras de progresso ASCII, % de precisão e tempo
  médio por questão
- Log por questão: domínio, tópico, resultado, dificuldade, tempo decorrido
- Revisão recomendada: domínios mais fracos em ordem de prioridade
- Tópicos cobertos na sessão

**Fórmula do score escalado:** `100 + (% bruta / 100) × 900`, arredondado para inteiro.

**Limites de aprovação usados:**

| Exames | Limite |
|---|---|
| CLF-C02, AIF-C01 | 700 / 1000 |
| SAA-C03, DVA-C02, SOA-C03, DEA-C01, MLA-C01 | 720 / 1000 |
| SAP-C02, DOP-C02, AIP-C01, ANS-C01, SCS-C02 | 750 / 1000 |
| Todos os outros | 720 / 1000 (padrão AWS) |

---

## Estrutura de arquivos

```
zekai-aws-certifications/
├── plugin.json                                    # Manifesto do power (Agent Plugins v1.0.0)
├── mcp.json                                       # Configuração do servidor MCP de docs AWS
├── README.md                                      # Esta documentação (português)
├── README.en.md                                   # Documentação em inglês
└── skills/
    └── zekai-aws-certifications/
        ├── SKILL.md                               # Skill principal: todos os modos, regras, sequência de startup
        ├── scripts/
        │   ├── session.py                         # Motor de estado de sessão (quiz + desafio de arquitetura)
        │   ├── resolve_exam.py                    # Validador de código de exame e cache de metadados
        │   └── export_report.py                   # Gerador de relatório markdown
        ├── references/
        │   ├── session-workflow.md                # Modo Quiz Interativo: ordem exata de comandos
        │   ├── question-breakdown.md              # Modo Análise: processo de quatro passos
        │   ├── architecture-challenge.md          # Modo Desafio de Arquitetura: workflow completo
        │   ├── documentation-grounding.md         # Como verificar fatos AWS antes de gerar conteúdo
        │   ├── distractor-engineering.md          # Como construir distractors hard/exam-level
        │   ├── explanation-template.md            # Templates para resumos, comparações, flashcards
        │   ├── mcp-retrieval.md                   # Descoberta de ferramentas MCP, retries, fallbacks
        │   ├── exam-guides.md                     # URL do índice de guias oficiais e estrutura
        │   ├── aws-service-by-exam.md             # Índice fallback de serviço por exame
        │   └── exams/
        │       ├── aif-c01.md                     # Mapa de estudo: AWS AI Practitioner
        │       ├── aip-c01.md                     # Mapa de estudo: Generative AI Developer Professional
        │       ├── ans-c01.md                     # Mapa de estudo: Advanced Networking Specialty
        │       ├── clf-c02.md                     # Mapa de estudo: Cloud Practitioner
        │       ├── dea-c01.md                     # Mapa de estudo: Data Engineer Associate
        │       ├── dop-c02.md                     # Mapa de estudo: DevOps Engineer Professional
        │       ├── dva-c02.md                     # Mapa de estudo: Developer Associate
        │       ├── mla-c01.md                     # Mapa de estudo: Machine Learning Engineer Associate
        │       ├── saa-c03.md                     # Mapa de estudo: Solutions Architect Associate
        │       ├── sap-c02.md                     # Mapa de estudo: Solutions Architect Professional
        │       ├── scs-c02.md                     # Mapa de estudo: Security Specialty
        │       └── soa-c03.md                     # Mapa de estudo: CloudOps Engineer Associate
        └── assets/
            └── question-output-template.md        # Templates de output para todos os modos e tipos de questão
```

---

## Configuração

O servidor MCP é configurado em `mcp.json` na raiz do power:

```json
{
  "$schema": "https://agent-plugins.org/schemas/1.0.0/mcp.schema.json",
  "mcpServers": {
    "aws-docs": {
      "type": "stdio",
      "command": "uvx",
      "args": ["awslabs.aws-documentation-mcp-server@latest"],
      "env": {
        "FASTMCP_LOG_LEVEL": "ERROR"
      }
    }
  }
}
```

**Diretório de estado:** padrão `~/.zekai`. Sobrescreva com a variável de ambiente
`ZEKAI_STATE_DIR` para usar um caminho diferente (ex.: diretório específico do projeto).

---

## Modelos recomendados

| Modo | Modelo recomendado | Por quê |
|---|---|---|
| Quiz Interativo | Claude Opus 4.8/5, GPT 5.6 Sol ou Sonnet 4.6/5 | Sonnet resolve bem a maioria das questões; use Opus para dificuldade exam-level onde a precisão de avaliação importa mais |
| Desafio de Arquitetura | Claude Opus 4.8/5, GPT 5.6 Sol ou Sonnet 4.6/5 | Avaliação de múltiplos requisitos com scoring ponderado exige atenção a detalhes |
| Análise de Questão | Claude Opus 4.8/5, GPT 5.6 Sol ou Sonnet 4.6/5 | Avalia o raciocínio do aluno em cada um dos quatro passos |
| Modo Estudo | Claude Sonnet 4.6/5 | Explicações de conceitos e citações; sem avaliação de resposta |

> **Nota:** os modelos acima são os que eu testei pessoalmente e validei como bons para cada modo. Isso não significa que sejam os únicos compatíveis, outros modelos podem ser testados e avaliados, e contribuições relatando resultados com outros modelos são bem-vindas.

---

## Solução de problemas

**O power não parece ativar**
- Abra uma pasta de workspace. O Kiro exige uma pasta aberta para ativar powers.
- Verifique o painel Powers, confirme que o power está listado como instalado e habilitado.
- Reinicie o Kiro. Powers recém-instalados às vezes precisam de reinicialização.

**Comando `uv` / `uvx` não encontrado**
```bash
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
```
```powershell
# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```
Depois reinicie o Kiro para que o novo PATH seja reconhecido.

**Servidor MCP falha ao conectar**
```bash
uv --version                                          # verificar se uv está instalado
uvx awslabs.aws-documentation-mcp-server@latest --help  # testar o servidor diretamente
```
Abra a paleta de comandos do Kiro e busque "MCP" para verificar o status do servidor.

**Estado da sessão parece perdido**
O estado fica em `~/.zekai/session.json`. Verifique:
```bash
python3 scripts/session.py status
```
Se a sessão estiver inativa, inicie uma nova. Histórico e calibração em `history.json`
e `calibration.jsonl` são preservados entre resets.

**Curveball do desafio de arquitetura revelado cedo demais**
O agente precisa chamar `design-grade --phase initial` antes do curveball ficar acessível.
Se o curveball aparecer antes da avaliação, execute `design-clear` e inicie um novo desafio.

**Código de exame não reconhecido**
- O catálogo local é um cache de conveniência. Se o código retornar
  `needs_online_verification`, o agente buscará no índice oficial ao vivo, isso é
  normal para exames recém-lançados.
- Nunca autocorrija um código (ex.: AIF-C01 e AIP-C01 são exames diferentes).

**O Kiro esqueceu qual exame estou estudando**
Isso pode acontecer após sessões muito longas. Diga o código do exame novamente
(ex.: "Estou estudando para o SAA-C03") e o agente restabelecerá o contexto.

---

## Aviso legal

Este power é uma ferramenta de estudo independente. Não é um produto oficial de
Certificação AWS e não tem afiliação, endosso ou patrocínio da Amazon Web Services
ou do programa de Certificação AWS. As questões práticas são geradas dinamicamente
pelo modelo de IA com base em documentação pública da AWS, não vêm de bancos de
questões oficiais da AWS. Passar em uma sessão prática não prevê resultados reais
do exame.

Sempre verifique detalhes críticos na documentação oficial da AWS. Use este power
junto com recursos oficiais de preparação para exames (AWS Skill Builder, guias de
exame, whitepapers), não como sua única fonte de estudo.
