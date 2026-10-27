# 40: Coluna Batimento nas abas do Excel

**What to build:** com vários Batimentos, as abas Por Tipo do Erro, Por Atributo, Operações com Diferença e Erros têm a coluna `Batimento` na frente, com filtro no cabeçalho; as linhas vêm por Batimento (na ordem da Base A) e depois na ordem de cada aba. O limite de linhas é da aba inteira: nas Operações, se cortar, ficam as maiores Diferenças absolutas de todos os Batimentos, e o aviso usa o total de todos. Na aba Erros, a Linha rejeitada pela Data e a Data-base ignorada aparecem uma vez, com `Batimento` = `Todos`; a rejeitada pelo Valor leva o seu Batimento. Um `.xlsx` só, com o nome de hoje. Ver spec: Saída (Coluna Batimento, Operações, Erros), Testes/Vários Batimentos (de ponta a ponta); história 63.

**Blocked by:** 38, 39

**Status:** done

- [x] Teste de ponta a ponta: um `.xlsx` só; a coluna `Batimento` nas quatro abas, com filtro, e as linhas por Batimento na ordem da Base A.
- [x] Teste de ponta a ponta: o corte com o limite reduzido por parâmetro vale para a aba inteira e deixa as maiores Diferenças absolutas de todos os Batimentos; o aviso diz "mostrando N de M".
- [x] Teste de ponta a ponta: na aba Erros, a Data rejeitada e a Data-base ignorada têm `Todos`; a rejeitada pelo Valor tem o seu Batimento.
- [x] Com um Batimento só, as abas continuam como hoje, com a coluna `Batimento` na frente trazendo o nome dele.
- [x] `C:\Users\josef\Projetos\Conciliacao-Enxuta\.venv\Scripts\python -m pytest -q` passa.
- [x] Teste com olhos de usuário: rodar a CLI sobre `exemplo\`, abrir o `.xlsx` e filtrar pela coluna `Batimento` nas quatro abas, conferindo as linhas contra o gabarito.

**Notas de entrega:**
Seams (escolhidos pela spec, sem seam nova): a de ponta a ponta (arquivos -> CLI -> `.xlsx` lido com openpyxl) e o `gravar_excel` com o limite reduzido. `Resultado` ganhou o campo `batimento` (padrão `Valor`), que o `conciliar_batimentos` preenche com o nome da `Leitura`; `conciliar` não mudou. `gravar_excel` recebe a lista de Resultados. As abas Por Tipo do Erro, Por Atributo, Operações e Erros têm `Batimento` na frente e filtro; o corte de Operações e de Erros é da aba inteira (maiores Diferenças absolutas de todos, aviso com o total de todos, também no Resumo via `avisos(..., operacoes=)`). Erros: a Data-base ignorada e a Linha rejeitada pela Data saem uma vez, `Todos`, no bloco do primeiro Batimento (com um só, a ordem é a de hoje); a rejeitada pelo Valor leva o seu Batimento. Resumo e gráficos seguem só o primeiro Batimento (ticket 41); o atalho `shortcut:` do `cli` agora só vale para o Resumo e o `.html`. Testes antigos de `test_ponta_a_ponta.py` ajustados à coluna nova; 4 testes novos. Suíte: 298 passed. Olhos de usuário: CLI sobre `exemplo\`, contagens por Batimento nas quatro abas batem com o gabarito (Valor 140 e Juros 40 operações).
Arquivos: `conciliacao_enxuta/excel.py`, `conciliacao_enxuta/cli.py`, `conciliacao_enxuta/cruzamento.py`, `tests/test_ponta_a_ponta.py`.

**Onde está agora (depois da entrega):**
As quatro abas do `.xlsx` já filtram por Batimento; falta a lista suspensa e as fórmulas do Resumo (ticket 41) e o `.html` (ticket 42).
