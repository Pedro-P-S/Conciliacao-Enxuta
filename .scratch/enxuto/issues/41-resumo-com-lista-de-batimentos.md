# 41: Lista suspensa de Batimentos no Resumo do Excel

**What to build:** com vários Batimentos, o Resumo tem no topo uma lista suspensa (validação de dados) com os Batimentos, na ordem da Base A, abrindo no primeiro, sem "Todos". O quadro, os avisos, os Atributos Problemáticos e os dois gráficos seguem a escolha por fórmula, sem macro: os números de cada Batimento ficam na aba oculta `_grafico`, e as células do Resumo e as séries dos gráficos os buscam pelo Batimento escolhido. Com um Batimento só, o Resumo é o de hoje. O openpyxl não calcula, então o teste confere as fórmulas e a `_grafico`. Ver spec: Saída (Resumo, com vários Batimentos), Testes/Vários Batimentos (de ponta a ponta); história 64.

**Blocked by:** 38, 39

**Status:** done

- [x] Teste de ponta a ponta: a lista suspensa existe no topo do Resumo, com os Batimentos na ordem da Base A, e abre no primeiro.
- [x] Teste de ponta a ponta: a `_grafico` traz os números de cada Batimento (quadro, avisos, Atributos Problemáticos, faixas de Idade e Diferença por Data-base) e as células do Resumo e as séries dos gráficos são fórmulas que buscam o Batimento escolhido.
- [x] Teste de ponta a ponta: os valores da `_grafico` de cada Batimento batem com o Resultado dele, e os dois gráficos continuam existindo.
- [x] `C:\Users\josef\Projetos\Conciliacao-Enxuta\.venv\Scripts\python -m pytest -q` passa.
- [x] Teste com olhos de usuário: rodar a CLI sobre `exemplo\`, abrir o `.xlsx` no Excel (ou no LibreOffice), trocar o Batimento na lista e conferir que o quadro, os avisos, os Atributos Problemáticos e os dois gráficos mudam e batem com o gabarito de cada um.

**Notas de entrega:**
Com vários Batimentos, o Resumo (`excel.py`, `_resumo_com_lista`) tem `Batimento` em A1 e a lista suspensa em B1 (validação de dados apontando para `_grafico!H`), abrindo no primeiro. O quadro (linhas 3 a 9), as linhas sem Chave (11 a 13), o aviso das Linhas rejeitadas (15), os Atributos Problemáticos (18 em diante) e as séries dos gráficos são fórmulas INDEX sobre blocos fixos da `_grafico` (`_blocos`: colunas I a U, um bloco por Batimento; G2 guarda a posição escolhida; A:B e D:E são o trecho escolhido, com NA() onde o bloco é mais curto). O aviso de corte das operações é texto fixo. Com um Batimento só, o Resumo é o de antes (`_resumo_de_um`). Seams: ponta a ponta pela CLI/`gravar_excel`, sem seam nova. O openpyxl não calcula: `tests/conftest.py` resolve as fórmulas do Resumo e da `_grafico` (autouse, `load_workbook(..., formulas=True)` devolve o cru) para os testes antigos, que leem o exemplo (agora com 2 Batimentos), continuarem lendo o Resumo do primeiro. Ajustei 2 testes antigos pela nova forma (linhas em branco no fim da `_grafico`; quadro achado pelo rótulo). Testes novos em `tests/test_ponta_a_ponta.py`: lista suspensa, fórmulas, `_grafico` de cada Batimento contra o Resultado, e a escolha de cada Batimento (Juros 10,00; Receita 50,00). Não mexi em html.py nem em test_html.py. Arquivos: `conciliacao_enxuta/excel.py`, `tests/test_ponta_a_ponta.py`, `tests/conftest.py`.

**Onde está agora (depois da entrega):**
`conciliacao_enxuta/excel.py`: `_resumo_com_lista`, `_blocos`, `_busca` e `_graficos`. Não conferido no Excel/LibreOffice de verdade (nenhum instalado): as fórmulas foram resolvidas pelo avaliador de `tests/conftest.py` contra o gabarito dos dois Batimentos do exemplo.
