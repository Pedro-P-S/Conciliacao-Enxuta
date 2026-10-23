# 19: Operações com Diferença absoluta

**What to build:** na aba Operações com Diferença, a coluna Diferença vira **Diferença absoluta**, sem sinal; Valor A e Valor B continuam com o sinal, e a ordem continua pela Diferença absoluta, decrescente. Nada mais muda na aba. Ver spec: Decisões de implementação (Saída/Operações com Diferença); histórias 25 e 26.

**Blocked by:** —

**Status:** ready-for-agent

- [ ] Aba `Operações com Diferença`: o cabeçalho diz `Diferença absoluta` no lugar de `Diferença`, na mesma posição, em reais e sem sinal.
- [ ] Valor A e Valor B continuam com o sinal (uma Chave com Sinal invertido mostra um positivo e um negativo).
- [ ] A ordem das linhas e o corte acima do limite não mudam.
- [ ] O teste de ponta a ponta confere a coluna contra o gabarito.
- [ ] `C:\Users\josef\Projetos\Conciliacao-Enxuta\.venv\Scripts\python -m pytest -q` passa.
- [ ] Teste com olhos de usuário: rodar a CLI sobre `exemplo\` e conferir com openpyxl (`PYTHONIOENCODING=utf-8`) que a coluna Diferença absoluta não tem valores negativos e que a primeira linha é a maior.

**Notas de entrega:**

**Onde está agora (depois da entrega):**
