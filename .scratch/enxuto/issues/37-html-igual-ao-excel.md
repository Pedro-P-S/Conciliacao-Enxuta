# 37: HTML igual ao Resumo do Excel

**What to build:** o `.html` mostra o que o Resumo do Excel mostra, usando o `quadro_do_resumo`: o percentual arredonda como no Excel; o eixo do gráfico mostra 0 quando não há Diferença; com uma Data-base só, o gráfico de linha mostra o ponto e a data uma vez; o caractere de controle sai do texto, como no Excel; `<`, `&` e aspas aparecem como texto. Ver spec: Saída (HTML), bloco "Decisões de 24/10/2026" (HTML igual ao Excel), Testes/Correções da auditoria (de ponta a ponta); história 58.

**Blocked by:** 29

**Status:** ready-for-agent

- [ ] Teste de ponta a ponta: o percentual do `.html` é o mesmo que o Excel mostra para o mesmo número.
- [ ] Teste de ponta a ponta: sem Diferença, o eixo do gráfico mostra 0.
- [ ] Teste de ponta a ponta: com uma Data-base só, o gráfico de linha traz o ponto e a data aparece uma vez.
- [ ] Teste de ponta a ponta: um Atributo com caractere de controle aparece sem ele, como no Excel; um com `<`, `&` e aspas aparece como texto.
- [ ] `C:\Users\josef\Projetos\Conciliacao-Enxuta\.venv\Scripts\python -m pytest -q` passa.
- [ ] Teste com olhos de usuário: rodar a CLI sobre `exemplo\` e sobre uma cópia com uma Data-base só, abrir o `.html` e conferir, ao lado da aba Resumo do `.xlsx`, que os números, os percentuais e os gráficos batem.

**Notas de entrega:**

**Onde está agora (depois da entrega):**
