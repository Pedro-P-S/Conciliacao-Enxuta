# 41: Lista suspensa de Batimentos no Resumo do Excel

**What to build:** com vários Batimentos, o Resumo tem no topo uma lista suspensa (validação de dados) com os Batimentos, na ordem da Base A, abrindo no primeiro, sem "Todos". O quadro, os avisos, os Atributos Problemáticos e os dois gráficos seguem a escolha por fórmula, sem macro: os números de cada Batimento ficam na aba oculta `_grafico`, e as células do Resumo e as séries dos gráficos os buscam pelo Batimento escolhido. Com um Batimento só, o Resumo é o de hoje. O openpyxl não calcula, então o teste confere as fórmulas e a `_grafico`. Ver spec: Saída (Resumo, com vários Batimentos), Testes/Vários Batimentos (de ponta a ponta); história 64.

**Blocked by:** 38, 39

**Status:** ready-for-agent

- [ ] Teste de ponta a ponta: a lista suspensa existe no topo do Resumo, com os Batimentos na ordem da Base A, e abre no primeiro.
- [ ] Teste de ponta a ponta: a `_grafico` traz os números de cada Batimento (quadro, avisos, Atributos Problemáticos, faixas de Idade e Diferença por Data-base) e as células do Resumo e as séries dos gráficos são fórmulas que buscam o Batimento escolhido.
- [ ] Teste de ponta a ponta: os valores da `_grafico` de cada Batimento batem com o Resultado dele, e os dois gráficos continuam existindo.
- [ ] `C:\Users\josef\Projetos\Conciliacao-Enxuta\.venv\Scripts\python -m pytest -q` passa.
- [ ] Teste com olhos de usuário: rodar a CLI sobre `exemplo\`, abrir o `.xlsx` no Excel (ou no LibreOffice), trocar o Batimento na lista e conferir que o quadro, os avisos, os Atributos Problemáticos e os dois gráficos mudam e batem com o gabarito de cada um.

**Notas de entrega:**
(preencher na entrega)

**Onde está agora (depois da entrega):**
(preencher na entrega)
