# 36: GUI com caminho colado e `erros.log` que não grava

**What to build:** na GUI, o caminho colado com espaço nas pontas ou entre aspas (o "Copiar como caminho" do Windows) é aceito. Se o `erros.log` não pode ser gravado, a mensagem simples aparece mesmo assim, e o resultado da execução anterior sai da tela. As regras ficam no `gui_estado`; a GUI continua casca. Ver spec: Interface (GUI Tkinter), bloco "Decisões de 24/10/2026" (GUI), Testes/Correções da auditoria (de ponta a ponta); histórias 54 e 55.

**Blocked by:** 30

**Status:** ready-for-agent

- [ ] Teste pelo `gui_estado`: um caminho entre aspas e um com espaço nas pontas conciliam como o caminho limpo.
- [ ] Teste pelo `gui_estado`: com o `erros.log` impedido de ser gravado, a Resposta traz a mensagem simples, sem exceção.
- [ ] Depois de um erro, o caminho do `.xlsx` da execução anterior não fica na tela.
- [ ] O autoteste da GUI (`CONCILIACAO_AUTOTESTE=1`) continua saindo com 0.
- [ ] `C:\Users\josef\Projetos\Conciliacao-Enxuta\.venv\Scripts\python -m pytest -q` passa.
- [ ] Teste com olhos de usuário: chamar o `gui_estado` com os caminhos de `exemplo\` copiados com "Copiar como caminho" (entre aspas) e conferir que gera o `.xlsx`; depois chamar com um arquivo que não existe e conferir que a Resposta não traz o caminho anterior.

**Notas de entrega:**

**Onde está agora (depois da entrega):**
