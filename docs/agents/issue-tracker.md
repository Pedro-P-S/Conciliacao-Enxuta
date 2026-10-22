# Issue tracker: Markdown local

- A spec é `docs/spec.md`, única para o projeto. Trabalho novo edita no lugar, na seção que muda.
- Um arquivo por ticket em `issues/NN-slug.md`, numerado a partir de `01` e continuando do último. Nunca um arquivo só com vários tickets.
- Layout do ticket:
  - `# NN: <título>`
  - `**O que construir:**` (um parágrafo, apontando a seção da spec)
  - `**Blocked by:**` (números dos tickets, ou `—`)
  - `**Status:**` (ver `triage-labels.md`)
  - checklist `- [ ]`; o último item é sempre o "Teste com olhos de usuário" em `exemplo\`
  - `**Notas de entrega:**`, preenchido na entrega
- Comentários vão no fim do arquivo, sob `## Comentários`.
- `HANDOFF.md` guarda o estado entre sessões. Atualize quando um ticket fecha.
- "Publicar no issue tracker" = criar o próximo arquivo em `issues/`. "Buscar o ticket" = ler `issues/NN-*.md`.
