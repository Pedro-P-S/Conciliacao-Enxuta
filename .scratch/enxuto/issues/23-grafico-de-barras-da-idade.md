# 23: Gráfico de barras da Idade no Resumo, sem a tabela

**What to build:** a tabela da Idade da Diferença por faixa sai do Resumo e vira um gráfico de barras: as 5 faixas sempre, a barra é a Diferença absoluta da faixa e o rótulo traz a quantidade de Chaves, como `31 a 90 dias (12 Chaves)`. Os dados do gráfico ficam na aba oculta `_grafico`, ao lado dos da linha. O Resumo fica nesta ordem: quadro, avisos, Atributos Problemáticos, gráfico de barras da Idade, gráfico de linha da Diferença absoluta por Data-base. Ver spec: Decisões de implementação (Saída/Resumo itens 1 a 5); história 17.

**Blocked by:** 22

**Status:** done

- [x] Resumo: não há mais a tabela das faixas de Idade.
- [x] Resumo: um gráfico de barras com as 5 faixas, mesmo vazias, com a Diferença absoluta de cada uma e o rótulo com as Chaves (`1 Chave` no singular).
- [x] Os dados das barras ficam em `_grafico`, que continua oculta, sem mexer nos dados do gráfico de linha.
- [x] A ordem do Resumo é: quadro, avisos, Atributos Problemáticos, barras da Idade, linha da Diferença.
- [x] O teste de ponta a ponta confere os dois gráficos e os dados das faixas contra o gabarito.
- [x] `C:\Users\josef\Projetos\Conciliacao-Enxuta\.venv\Scripts\python -m pytest -q` passa.
- [x] Teste com olhos de usuário: rodar a CLI sobre `exemplo\` e conferir com openpyxl (`PYTHONIOENCODING=utf-8`) que o Resumo tem dois gráficos, um de barras e um de linha, e que os rótulos e valores das faixas em `_grafico` batem com o gabarito.

**Notas de entrega:**
- Seam testada (escolhida pela spec, sem acesso ao usuário): Seam 2, de ponta a ponta (arquivos → CLI → `.xlsx` lido com openpyxl), contra o gabarito de `gerar_bases_exemplo`. Nenhuma mudança no `cruzamento`: o `Resultado.por_idade` já trazia o que o gráfico precisa.
- `conciliacao_enxuta/excel.py`: a tabela da Idade saiu do Resumo; os avisos começam uma linha abaixo do quadro. `_grafico_da_diferenca` virou `_graficos`: grava os dados da linha em `_grafico` A:B (sem mudança) e os das barras em D:E (`Idade da Diferença`, `Diferença absoluta`; rótulo `31 a 90 dias (12 Chaves)`, `1 Chave` no singular, as 5 faixas sempre). O gráfico de barras vai abaixo de tudo no Resumo e o de linha 20 linhas abaixo dele.
- `tests/test_ponta_a_ponta.py`: novo teste das barras (dados em `_grafico` D:E com rótulos literais e valores do gabarito, `BarChart` antes do `LineChart`, ambos abaixo do conteúdo); o teste da tabela das faixas virou "sem tabela de Idade e avisos logo abaixo do quadro"; o teste da linha lê só A:B de `_grafico`; `avisos_do_resumo` começa depois de `Chaves com Diferença`.
- As linhas sem Chave no rótulo (`1 linha sem Chave`) ficam para o ticket 24.
- Olhos de usuário: CLI sobre `exemplo\`; o Resumo tem `BarChart` (linha 21) e `LineChart` (linha 41), abaixo dos Atributos Problemáticos; `_grafico` oculta, com os 5 rótulos e valores batendo com o gabarito.
- Correção visual (achada ao abrir no Excel o `.xlsx` de `exemplo\`): a linha da Diferença absoluta saía com cada trecho de uma cor e suavizada, e os títulos dos dois gráficos cobriam a área do gráfico. `conciliacao_enxuta/excel.py`: a linha ganhou `varyColors = False` e a série `smooth = False`; os dois gráficos ganharam `title.overlay = False`. `tests/test_ponta_a_ponta.py`: dois testes novos no Seam 2 (linha com `varyColors` falso e série sem `smooth`; título dos dois gráficos sem overlay), vistos falhando antes da correção. Olhos de usuário: CLI sobre `exemplo\`; o XML dos gráficos traz `overlay val="0"` nos dois e `varyColors val="0"`/`smooth val="0"` na linha, com uma série só.

**Onde está agora (depois da entrega):**
O Resumo mostra quadro, avisos, Atributos Problemáticos, barras da Idade e linha da Diferença absoluta; os dados dos dois gráficos ficam em `_grafico` (linha em A:B, barras em D:E).
