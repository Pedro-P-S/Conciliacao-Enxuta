# 23: Gráfico de barras da Idade no Resumo, sem a tabela

**What to build:** a tabela da Idade da Diferença por faixa sai do Resumo e vira um gráfico de barras: as 5 faixas sempre, a barra é a Diferença absoluta da faixa e o rótulo traz a quantidade de Chaves, como `31 a 90 dias (12 Chaves)`. Os dados do gráfico ficam na aba oculta `_grafico`, ao lado dos da linha. O Resumo fica nesta ordem: quadro, avisos, Atributos Problemáticos, gráfico de barras da Idade, gráfico de linha da Diferença absoluta por Data-base. Ver spec: Decisões de implementação (Saída/Resumo itens 1 a 5); história 17.

**Blocked by:** 22

**Status:** ready-for-agent

- [ ] Resumo: não há mais a tabela das faixas de Idade.
- [ ] Resumo: um gráfico de barras com as 5 faixas, mesmo vazias, com a Diferença absoluta de cada uma e o rótulo com as Chaves (`1 Chave` no singular).
- [ ] Os dados das barras ficam em `_grafico`, que continua oculta, sem mexer nos dados do gráfico de linha.
- [ ] A ordem do Resumo é: quadro, avisos, Atributos Problemáticos, barras da Idade, linha da Diferença.
- [ ] O teste de ponta a ponta confere os dois gráficos e os dados das faixas contra o gabarito.
- [ ] `C:\Users\josef\Projetos\Conciliacao-Enxuta\.venv\Scripts\python -m pytest -q` passa.
- [ ] Teste com olhos de usuário: rodar a CLI sobre `exemplo\` e conferir com openpyxl (`PYTHONIOENCODING=utf-8`) que o Resumo tem dois gráficos, um de barras e um de linha, e que os rótulos e valores das faixas em `_grafico` batem com o gabarito.

**Notas de entrega:**

**Onde está agora (depois da entrega):**
