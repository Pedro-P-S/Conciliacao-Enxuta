# CLAUDE.md — Conciliação Enxuta

Projeto próprio, separado da Conciliação Financeira (o "projeto grande", em `..\Desafio-Conciliacao`). Tudo em português: código, mensagens, documentos e commits.

## Fonte da verdade

- `docs/spec.md`: a spec única.
- `GRILL.md`: as decisões de origem da spec.
- `CONTEXT.md`: o glossário. Use estes termos.
- `issues/NN-slug.md` e `HANDOFF.md`: tickets e estado do trabalho, criados quando forem necessários.

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
..\Desafio-Conciliacao\.venv\Scripts\python -m pytest -q
```

Por enquanto usa o `.venv` do projeto grande; não instale nem atualize pacotes nele.

## Agentes

O fluxo é `/fluxo-completo` (spec → tickets → implementação → review), com os agentes em `.claude/agents/`: `spec-writer`, `ticket-writer`, `implementer` e `reviewer`. Aqui não há guardião da documentação. As convenções de tickets ficam em `docs/agents/`.
