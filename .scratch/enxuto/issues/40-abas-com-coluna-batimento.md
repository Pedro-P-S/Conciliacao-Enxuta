# 40: Coluna Batimento nas abas do Excel

**What to build:** com vários Batimentos, as abas Por Tipo do Erro, Por Atributo, Operações com Diferença e Erros têm a coluna `Batimento` na frente, com filtro no cabeçalho; as linhas vêm por Batimento (na ordem da Base A) e depois na ordem de cada aba. O limite de linhas é da aba inteira: nas Operações, se cortar, ficam as maiores Diferenças absolutas de todos os Batimentos, e o aviso usa o total de todos. Na aba Erros, a Linha rejeitada pela Data e a Data-base ignorada aparecem uma vez, com `Batimento` = `Todos`; a rejeitada pelo Valor leva o seu Batimento. Um `.xlsx` só, com o nome de hoje. Ver spec: Saída (Coluna Batimento, Operações, Erros), Testes/Vários Batimentos (de ponta a ponta); história 63.

**Blocked by:** 38, 39

**Status:** ready-for-agent

- [ ] Teste de ponta a ponta: um `.xlsx` só; a coluna `Batimento` nas quatro abas, com filtro, e as linhas por Batimento na ordem da Base A.
- [ ] Teste de ponta a ponta: o corte com o limite reduzido por parâmetro vale para a aba inteira e deixa as maiores Diferenças absolutas de todos os Batimentos; o aviso diz "mostrando N de M".
- [ ] Teste de ponta a ponta: na aba Erros, a Data rejeitada e a Data-base ignorada têm `Todos`; a rejeitada pelo Valor tem o seu Batimento.
- [ ] Com um Batimento só, as abas continuam como hoje, com a coluna `Batimento` na frente trazendo o nome dele.
- [ ] `C:\Users\josef\Projetos\Conciliacao-Enxuta\.venv\Scripts\python -m pytest -q` passa.
- [ ] Teste com olhos de usuário: rodar a CLI sobre `exemplo\`, abrir o `.xlsx` e filtrar pela coluna `Batimento` nas quatro abas, conferindo as linhas contra o gabarito.

**Notas de entrega:**
(preencher na entrega)

**Onde está agora (depois da entrega):**
(preencher na entrega)
