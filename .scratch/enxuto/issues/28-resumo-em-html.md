# 28: Resumo em HTML

**What to build:** ao lado do `.xlsx` sai `conciliacao_AAAA-MM-DD.html`, na mesma pasta e sobrescrevendo se existir, com o mesmo Resumo do Excel, na mesma ordem e com os mesmos rótulos: quadro, avisos, Atributos Problemáticos, gráfico de barras da Idade e gráfico de linha da Diferença absoluta por Data-base, os dois em SVG. Um arquivo só, montado com a biblioteca padrão, sem script e sem nada buscado na internet. A CLI e a GUI gravam os dois arquivos; a CLI imprime os dois caminhos e a GUI continua mostrando o do `.xlsx`. Ver spec: Solução, Decisões de implementação (Módulos/html, cli e gui; Saída/Arquivos e HTML; Interface; Técnico), Testes/Seam 2; história 46.

**Blocked by:** 18, 22, 23, 24, 25, 27

**Status:** done

- [x] O `.html` sai ao lado do `.xlsx`, com o mesmo nome e a data da Data-base mais recente, sobrescrevendo.
- [x] Traz o quadro com os totais, os avisos que houver, os Atributos Problemáticos (ou nada, se não houver) e os dois gráficos em SVG, com os rótulos da Idade iguais aos do Excel; valores em reais no formato brasileiro.
- [x] Não tem `<script>`, nem `src` ou `href` apontando para fora do arquivo.
- [x] CLI: imprime o caminho do `.xlsx` e do `.html`; GUI (`gui_estado`): grava os dois e mostra o caminho do `.xlsx`.
- [x] O teste de ponta a ponta confere que o `.html` existe, traz os totais e os Atributos Problemáticos do gabarito e não aponta para nada fora do arquivo.
- [x] O autoteste da GUI (`CONCILIACAO_AUTOTESTE=1`) continua saindo com 0.
- [x] `C:\Users\josef\Projetos\Conciliacao-Enxuta\.venv\Scripts\python -m pytest -q` passa.
- [x] Teste com olhos de usuário: rodar a CLI sobre `exemplo\` e ler o `.html` gerado (`PYTHONIOENCODING=utf-8`), conferindo que os totais, os avisos e os Atributos Problemáticos batem com a aba Resumo do `.xlsx` e que os dois gráficos estão no arquivo.

**Notas de entrega:**
- Novo módulo `conciliacao_enxuta/html.py`: `gravar_html(resultado, pasta, limite=700_000)` grava `conciliacao_AAAA-MM-DD.html` (sobrescreve) com o Resumo na ordem do Excel: quadro, avisos (linhas sem Chave por base, Linhas rejeitadas, corte das operações), Atributos Problemáticos (só se houver) e os dois gráficos em SVG embutido (barras deitadas da Idade, linha da Diferença absoluta por Data-base com a primeira e a última data e o maior valor no eixo). Biblioteca padrão só (`html.escape`), sem `<script>`, sem `src`/`href`/`url(`. Reais em `1.234,56`, percentual em `79,01%`. Reaproveita do `excel.py` `_milhar`, `_rotulo_da_faixa`, `_aviso_de_corte`, `TITULO_PROBLEMATICOS` e `LIMITE_DE_LINHAS`, para os rótulos serem os mesmos.
- `cli.py` imprime o caminho do `.xlsx` e, na linha seguinte, o do `.html`. `gui_estado.py` grava os dois e a Resposta continua com o `.xlsx`.
- Seams (escolhidos pela spec, Seam 2): a CLI `main` (arquivos → `.xlsx` + `.html`), `gravar_html` direto só para o limite reduzido (como `gravar_excel` nos testes de corte), e `gui_estado.conciliar_pela_janela`. O `.html` é lido nos testes com `html.parser`.
- Testes: novo `tests/test_html.py` (caminhos impressos, quadro, avisos e ausência deles, corte, Atributos Problemáticos e ausência, gráficos com os rótulos da Idade lidos da aba `_grafico` do `.xlsx`, nada fora do arquivo). `tests/test_ponta_a_ponta.py` passou a ler a primeira linha da saída da CLI, e o teste de `--saida` confere que o `.html` antigo também é sobrescrito. `tests/test_gui.py` confere que o `.html` sai ao lado.
- Olhos de usuário: CLI sobre `exemplo\`; o `.html` traz os mesmos totais, avisos (2 e 1 linhas sem Chave, 4 rejeitadas) e os 3 Atributos Problemáticos da aba Resumo, 2 SVGs e a linha com 131 pontos.
- Arquivos: `conciliacao_enxuta/html.py` (novo), `conciliacao_enxuta/cli.py`, `conciliacao_enxuta/gui_estado.py`, `tests/test_html.py` (novo), `tests/test_ponta_a_ponta.py`, `tests/test_gui.py`.

**Onde está agora (depois da entrega):**
A CLI e a GUI gravam o `.xlsx` e o `.html` lado a lado; o `.html` é o Resumo do Excel em uma página, sem internet. 196 testes passando.
