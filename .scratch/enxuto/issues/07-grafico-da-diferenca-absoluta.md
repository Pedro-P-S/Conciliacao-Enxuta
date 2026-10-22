# 07: Gráfico da Diferença absoluta no tempo

**What to build:** no fim do Resumo, um gráfico de linha da Diferença absoluta por Data-base, para o analista ver a Diferença no tempo sem uma tabela de histórico que estoure o Excel. Os dados do gráfico ficam numa aba oculta `_grafico`. Ver spec: Solução, Decisões de implementação (Módulos/`excel`, Saída/Resumo); história 19.

**Blocked by:** 06

**Status:** ready-for-agent

- [ ] O Resumo tem um gráfico de linha (openpyxl) abaixo dos avisos, com a Diferença absoluta (em reais) por Data-base.
- [ ] A aba `_grafico` existe, está oculta e tem uma linha por Data-base comum, em ordem de data; o Resumo não tem tabela de histórico.
- [ ] As abas visíveis continuam sendo só as da spec (a oculta não conta para as 4).
- [ ] O teste de ponta a ponta confere a existência do gráfico, a aba oculta e os valores dela contra o gabarito.
- [ ] `C:\Users\josef\Projetos\Desafio-Conciliacao\.venv\Scripts\python -m pytest -q` passa.
- [ ] Teste com olhos de usuário: rodar a CLI sobre o `exemplo\` de seis meses e conferir com openpyxl (`PYTHONIOENCODING=utf-8`) que o Resumo tem um gráfico de linha, que `_grafico` está oculta e que ela tem uma linha por Data-base comum.

**Notas de entrega:**

**Onde está agora (depois da entrega):**
