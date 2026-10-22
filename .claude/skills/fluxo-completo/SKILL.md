---
name: fluxo-completo
description: Orquestra o fluxo depois do grill: spec → tickets → implementação → code review, cada etapa num subagente que usa a sua skill. Use quando o usuário pedir para rodar o fluxo completo.
---
Você é o orquestrador. NÃO faça nenhuma etapa você mesmo: cada uma vai para um subagente (ferramenta Agent com o `subagent_type` indicado), e você espera ele terminar antes de seguir. Os subagentes não veem esta conversa; tudo o que eles precisam vai em arquivo ou no prompt.

0. **Briefing.** As decisões do grill estão em `GRILL.md`. Se esta conversa trouxe decisões novas, acrescente-as lá antes de seguir. Anote o commit atual (`git rev-parse HEAD`) como base do review.
1. **Spec:** `spec-writer`, passando `GRILL.md`. Se `docs/spec.md` já cobre todo o `GRILL.md`, pule esta etapa e diga isso ao usuário.
2. **Tickets:** `ticket-writer`. Confira que os tickets estão em `issues/`.
3. **Implementação:** para CADA ticket, na ordem dos `Blocked by`, um `implementer` com o caminho daquele ticket. Um ticket por chamada. Depois de cada um, confira que o pytest passou (`..\Desafio-Conciliacao\.venv\Scripts\python -m pytest -q`) e commite.
4. **Review:** `reviewer`, passando o commit base do passo 0.
5. Se houver problemas críticos, chame o `implementer` para corrigir só eles (passe `review.md`) e o `reviewer` de novo. No máximo 2 vezes.
6. No final, mostre um resumo curto: tickets feitos, problemas restantes e onde estão os arquivos.

Regras:
- Não leia código nem implemente no contexto principal.
- A comunicação entre etapas é só por arquivos.
- Confira que cada subagente começou com "Usando skill …". Se não começou, ou se uma etapa falhar, pare e avise o usuário.
- Nada é escrito em `..\Desafio-Conciliacao`.
