---
name: fluxo-completo
description: Orquestra o fluxo depois do grill-with-docs: spec → tickets → implementação → code review, cada etapa num subagente que usa a sua skill. Use quando o usuário pedir para rodar o fluxo completo.
---
Você é o orquestrador. NÃO faça nenhuma etapa você mesmo: cada uma vai para um subagente (ferramenta Agent com o `subagent_type` indicado), e você espera ele terminar antes de seguir. Os subagentes não veem esta conversa; tudo o que eles precisam vai em arquivo ou no prompt.

0. **Briefing do grill.** Se a conversa tem um grill-with-docs, resuma as decisões (o que construir, regras, fora do escopo, termos novos) em `GRILL.md`. Se o grill foi em outra conversa, peça ao usuário o arquivo ou o resumo. Anote o commit atual (`git rev-parse HEAD`) como base do review.
1. **Spec:** `spec-writer`, passando o caminho do briefing. Confira que `docs/spec.md` mudou.
2. **Tickets:** `ticket-writer`, passando as seções novas da spec. Confira que os tickets estão em `.scratch/enxuto/issues/`.
3. **Implementação:** para CADA ticket, na ordem dos `Blocked by`, um `implementer` com o caminho daquele ticket. Um ticket por chamada. Depois de cada um, confira que o pytest passou e commite.
4. **Review:** `reviewer`, passando o commit base do passo 0.
5. Se houver problemas críticos, chame o `implementer` para corrigir só eles (passe `.scratch/enxuto/review.md`) e o `reviewer` de novo. No máximo 2 vezes.
6. No final, mostre um resumo curto: tickets feitos, problemas restantes e onde estão os arquivos.

Regras:
- Não leia código nem implemente no contexto principal.
- A comunicação entre etapas é só por arquivos.
- Confira que cada subagente começou com "Usando skill …", que a resposta não tem `SKILL INDISPONÍVEL` e que os arquivos esperados da etapa existem. Se algo disso falhar, pare e avise o usuário.
