# CLAUDE.md — Conciliação Enxuta

Projeto próprio, separado da Conciliação Financeira (o "projeto grande", em `..\Desafio-Conciliacao`). Tudo em português: código, mensagens, documentos e commits.

## Princípios

Guias, não leis. Na dúvida, eles decidem.

- Entre duas soluções equivalentes, a mais simples.
- Lute contra o scope creep: só o que foi pedido.
- O ganho é de quem lê o resultado: mostrar o que está escondido e não é fácil de ver, do jeito mais simples e claro.

## Fonte da verdade

- `docs/spec.md`: a spec única.
- `GRILL.md`: as decisões de origem da spec.
- `CONTEXT.md`: o glossário. Use estes termos.
- `.scratch/enxuto/issues/NN-slug.md` e `.scratch/enxuto/HANDOFF.md`: tickets e estado do trabalho, criados quando forem necessários.

## O projeto grande é só peça de reposição

- Pode **ler** `..\Desafio-Conciliacao\conciliacao\` para copiar e adaptar peças (leitura, parse de valor e data, centavos, formatação, detecção de padrões). **Nunca escreva** lá, nem importe de lá.
- A spec, o glossário, os ADRs, os tickets e o CLAUDE.md do projeto grande **não valem** aqui. Se algo de lá contradiz o `GRILL.md` ou a spec, vale o daqui.
- Não traga o que foi cortado: dashboard HTML, Bases Auxiliares, Histórico em Parquet, Aging, Justificativas, Pareto, Compensação Oculta, Pares Prováveis, mapeamento de colunas, Qualidade, Manifesto, mais de 4 abas.

## Regras fixas

- Trabalhe só dentro desta pasta. A exceção é ler o projeto grande, como dito acima, e o `%LOCALAPPDATA%\ConciliacaoEnxuta\erros.log`.
- Dinheiro é sempre centavos `Int64`; vira reais só no Excel.
- TDD; os testes com olhos de usuário usam `exemplo\` (no `.gitignore`).
- Nunca abra a GUI sem `CONCILIACAO_AUTOTESTE=1`; ninguém vê a janela.
- Ao imprimir acentos no console, use `PYTHONIOENCODING=utf-8`.

## Comandos

```bash
C:\Users\josef\Projetos\Conciliacao-Enxuta\.venv\Scripts\python -m pytest -q
```

O `.venv` é do projeto, com os pacotes de `requirements.txt`. O caminho é absoluto porque os worktrees (`.claude\worktrees\<nome>\`) não têm `.venv`.

## Agentes

O fluxo é `/fluxo-completo` (spec → tickets → implementação → review), com os agentes em `.claude/agents/`: `spec-writer`, `ticket-writer`, `implementer` e `reviewer`.

## Issue tracker

Markdown local. A spec é uma só, `docs/spec.md`. Os tickets são um arquivo cada em `.scratch/enxuto/issues/NN-slug.md`, numerados a partir do último, com este layout:

- `# NN: <título>`
- `**What to build:**` (um parágrafo, apontando a seção da spec)
- `**Blocked by:**` (números dos tickets, ou `—`)
- `**Status:**` um dos rótulos `needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`, ou `done` quando entregue
- um checklist `- [ ]`; o último item é sempre o "Teste com olhos de usuário" em `exemplo\`
- `**Notas de entrega:**` e `**Onde está agora (depois da entrega):**`, preenchidos na entrega

Não há ADRs ainda: as decisões ficam no `GRILL.md` e nos blocos de decisões da spec.
