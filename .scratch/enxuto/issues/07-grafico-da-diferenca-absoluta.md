# 07: Gráfico da Diferença absoluta no tempo

**What to build:** no fim do Resumo, um gráfico de linha da Diferença absoluta por Data-base, para o analista ver a Diferença no tempo sem uma tabela de histórico que estoure o Excel. Os dados do gráfico ficam numa aba oculta `_grafico`. Ver spec: Solução, Decisões de implementação (Módulos/`excel`, Saída/Resumo); história 19.

**Blocked by:** 06

**Status:** done

- [x] O Resumo tem um gráfico de linha (openpyxl) abaixo dos avisos, com a Diferença absoluta (em reais) por Data-base.
- [x] A aba `_grafico` existe, está oculta e tem uma linha por Data-base comum, em ordem de data; o Resumo não tem tabela de histórico.
- [x] As abas visíveis continuam sendo só as da spec (a oculta não conta para as 4).
- [x] O teste de ponta a ponta confere a existência do gráfico, a aba oculta e os valores dela contra o gabarito.
- [x] `C:\Users\josef\Projetos\Conciliacao-Enxuta\.venv\Scripts\python -m pytest -q` passa.
- [x] Teste com olhos de usuário: rodar a CLI sobre o `exemplo\` de seis meses e conferir com openpyxl (`PYTHONIOENCODING=utf-8`) que o Resumo tem um gráfico de linha, que `_grafico` está oculta e que ela tem uma linha por Data-base comum.

**Notas de entrega:**
- `excel.gravar_excel` cria a aba oculta `_grafico` (cabeçalho Data-base / Diferença absoluta, uma linha por Data-base comum de `Resultado.historico`, em reais) e um `LineChart` no Resumo, ancorado uma linha abaixo de tudo o que está escrito (quadro e avisos). Eixos marcados como visíveis (no openpyxl 3.1 eles somem no Excel sem isso). Sem tabela de histórico no Resumo.
- O gabarito do gerador de exemplo ganhou `historico`, calculado das Diferenças plantadas, sem passar pelo cruzamento.
- Teste de ponta a ponta novo confere o gráfico de linha, a posição abaixo do conteúdo, a aba oculta e os valores dela contra o gabarito; o teste antigo de abas passou a olhar só as visíveis.
- Olhos de usuário: CLI sobre `exemplo\` gerou Resumo visível com um `LineChart` e `_grafico` oculta com 131 linhas, uma por Data-base comum (01/04 a 30/09/2026), em ordem.
- Arquivos: `conciliacao_enxuta/excel.py`, `conciliacao_enxuta/exemplo.py`, `tests/test_ponta_a_ponta.py`.

**Onde está agora (depois da entrega):**
