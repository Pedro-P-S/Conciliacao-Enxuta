# 30: Um pipeline só, com o `.xlsx` antes do `.html`

**What to build:** o pipeline ler → conciliar → gravar passa a ser um só, `conciliar_arquivos(base_a, base_b, tolerancia, pasta)` no `cli`, usado pela CLI e pelo `gui_estado`: lê as duas bases, concilia e grava o `.xlsx` e depois o `.html`. Se o `.xlsx` não pode ser gravado (por exemplo, aberto no Excel), nem o `.xlsx` nem o `.html` mudam e o usuário recebe uma mensagem simples, na CLI e na GUI. Ver spec: Decisões de implementação (Módulos: `cli`, `gui` e `gui_estado`; Saída/Arquivos), bloco "Decisões de 24/10/2026" (Gravação, Implementação), Testes/Correções da auditoria (de ponta a ponta); história 53.

**Blocked by:** —

**Status:** ready-for-agent

- [ ] `conciliar_arquivos` existe no `cli` e é o único caminho da CLI e do `gui_estado` até os dois arquivos.
- [ ] O `.xlsx` é gravado antes do `.html`.
- [ ] Teste de ponta a ponta: com o `.xlsx` impedido de ser gravado, o `.xlsx` e o `.html` antigos ficam como estavam, e a mensagem é simples, sem traceback, na CLI e no `gui_estado`.
- [ ] `C:\Users\josef\Projetos\Conciliacao-Enxuta\.venv\Scripts\python -m pytest -q` passa.
- [ ] Teste com olhos de usuário: gerar os dois arquivos sobre `exemplo\`, abrir o `.xlsx` no Excel (ou travá-lo), rodar de novo com outra Tolerância e conferir a mensagem simples e que a data de modificação do `.xlsx` e do `.html` não mudou.

**Notas de entrega:**

**Onde está agora (depois da entrega):**
