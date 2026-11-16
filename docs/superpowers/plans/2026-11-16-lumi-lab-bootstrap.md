# Lumi Lab Bootstrap Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Publicar o repo inicial `ceia-pdc-slms/lumi-lab` e organizar o trabalho dos dois times para 19 e 26/11/2026.

**Architecture:** Um repo novo de pesquisa, público e compartilhado, separado do acervo da fase 1. Hugging Face concentra artefatos de modelos/dados e o hub existente concentra divulgação; sua implementação fica nas tarefas do time.

**Tech Stack:** Markdown, JSON, CSV, GitHub Issues/Milestones, Git e GitHub CLI/conector.

**Spec:** `docs/superpowers/specs/2026-11-16-lumi-lab-design.md`

## Global Constraints

- Organização: `ceia-pdc-slms`; nome: `lumi-lab`; visibilidade: pública.
- Marcos: 19 e 26/11/2026, America/Sao_Paulo.
- Todo o trabalho é público, incluindo os dados.
- As trilhas de conhecimento e decisão sobre ferramentas são apresentadas separadamente.
- Não implementar pesquisa ou resultados fictícios nesta preparação.
- Não alterar o repo da fase 1 nem publicar conteúdo no hub neste pedido.

## Review Focus

- Guias precisam distinguir estrutura preparada e experimento executado.
- Issues precisam cobrir ambas as frentes e preservar a avaliação de teste.
- Dependências precisam apontar para issues existentes, sem ciclos.
- Links locais e formatos JSON/CSV/YAML precisam ser válidos.
- Datas e permissões precisam corresponder ao repo remoto correto.

---

### Task 1: Preparar documentação e estrutura

**Files:** `README.md`, `CONTRIBUTING.md`, guias por pasta, `docs/`, `configs/run.example.json`, `data/catalogo-fontes.csv`, `.github/` e `.gitignore`.

**Interfaces:** Consome a especificação e o planejamento original; produz arquivos versionáveis e links internos verificáveis.

- [x] Criar os guias e preservar o planejamento de novembro.
- [x] Validar links internos, JSON, CSV e ausência de pesos/dados pessoais locais.
- [x] Revisar consistência com as duas trilhas e os dois marcos.

Expected: todos os arquivos são documentação ou modelos explicitamente identificados; verificações sem erro.

### Task 2: Criar repo e organizar tarefas

**Files:** `docs/entregas.md` e `docs/tarefas.md`.

**Interfaces:** Consome a estrutura; produz repo público, marcos, labels, issues e índice com números reais.

- [x] Criar o repo público na organização e os dois marcos.
- [x] Criar as tarefas, depois registrar dependências pelos números retornados.
- [x] Registrar links e critérios de aceite no índice de tarefas.

Expected: todas as tarefas abertas estão em um marco correto e apontam para dependências existentes.

### Task 3: Revisar, publicar e conferir

**Interfaces:** Consome os arquivos e as tarefas; produz commit inicial publicado e acesso do time.

- [x] Realizar revisão independente do conjunto e corrigir achados relevantes.
- [x] Publicar o commit inicial e conceder escrita ao time existente da fase 1; convites individuais enviados aos seis integrantes que não pertencem a esse time.
- [x] Conferir visibilidade, branch, arquivos, marcos, tarefas e acesso remotos; aceite dos convites depende dos destinatários.

Expected: `ceia-pdc-slms/lumi-lab` público e utilizável pelos dois times; pesquisa permanece aberta.
