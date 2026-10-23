# 28: Resumo em HTML

**What to build:** ao lado do `.xlsx` sai `conciliacao_AAAA-MM-DD.html`, na mesma pasta e sobrescrevendo se existir, com o mesmo Resumo do Excel, na mesma ordem e com os mesmos rótulos: quadro, avisos, Atributos Problemáticos, gráfico de barras da Idade e gráfico de linha da Diferença absoluta por Data-base, os dois em SVG. Um arquivo só, montado com a biblioteca padrão, sem script e sem nada buscado na internet. A CLI e a GUI gravam os dois arquivos; a CLI imprime os dois caminhos e a GUI continua mostrando o do `.xlsx`. Ver spec: Solução, Decisões de implementação (Módulos/html, cli e gui; Saída/Arquivos e HTML; Interface; Técnico), Testes/Seam 2; história 46.

**Blocked by:** 18, 22, 23, 24, 25, 27

**Status:** ready-for-agent

- [ ] O `.html` sai ao lado do `.xlsx`, com o mesmo nome e a data da Data-base mais recente, sobrescrevendo.
- [ ] Traz o quadro com os totais, os avisos que houver, os Atributos Problemáticos (ou nada, se não houver) e os dois gráficos em SVG, com os rótulos da Idade iguais aos do Excel; valores em reais no formato brasileiro.
- [ ] Não tem `<script>`, nem `src` ou `href` apontando para fora do arquivo.
- [ ] CLI: imprime o caminho do `.xlsx` e do `.html`; GUI (`gui_estado`): grava os dois e mostra o caminho do `.xlsx`.
- [ ] O teste de ponta a ponta confere que o `.html` existe, traz os totais e os Atributos Problemáticos do gabarito e não aponta para nada fora do arquivo.
- [ ] O autoteste da GUI (`CONCILIACAO_AUTOTESTE=1`) continua saindo com 0.
- [ ] `C:\Users\josef\Projetos\Conciliacao-Enxuta\.venv\Scripts\python -m pytest -q` passa.
- [ ] Teste com olhos de usuário: rodar a CLI sobre `exemplo\` e ler o `.html` gerado (`PYTHONIOENCODING=utf-8`), conferindo que os totais, os avisos e os Atributos Problemáticos batem com a aba Resumo do `.xlsx` e que os dois gráficos estão no arquivo.

**Notas de entrega:**

**Onde está agora (depois da entrega):**
