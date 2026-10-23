# 08: Aba Operações com Diferença

**What to build:** o analista vê a lista das Chaves com Diferença na Data-base mais recente, uma linha por Chave, da maior para a menor |Diferença|, com as colunas Chave, Valor A, Valor B e Diferença (em reais, `#.##0,00`). Cabeçalho congelado e com filtro, para filtrar e ordenar pelo cabeçalho. As colunas Tipo do Erro, Aberta desde e Atributos entram nos tickets seguintes. Ver spec: Solução, Decisões de implementação (Saída/Operações com Diferença); histórias 25, 26 (parte) e 31.

**Blocked by:** 06

**Status:** done

- [x] Seam 1: o Resultado traz as Operações com Diferença só da Data-base mais recente, só as Chaves com |Diferença| > Tolerância, ordenadas por |Diferença| decrescente.
- [x] A aba `Operações com Diferença` tem as colunas Chave, Valor A, Valor B e Diferença, com Só em A/Só em B mostrando o lado ausente como 0.
- [x] Cabeçalho congelado e com autofiltro cobrindo as colunas e linhas.
- [x] O teste de ponta a ponta confere nomes e quantidade de abas, colunas, ordem das linhas e valores contra o gabarito.
- [x] `C:\Users\josef\Projetos\Desafio-Conciliacao\.venv\Scripts\python -m pytest -q` passa.
- [x] Teste com olhos de usuário: rodar a CLI sobre `exemplo\` e conferir com openpyxl (`PYTHONIOENCODING=utf-8`) que a aba lista as Chaves com Diferença da Data-base mais recente, da maior para a menor, com cabeçalho congelado e filtro, e que a quantidade bate com Chaves com Diferença do Resumo.

**Notas de entrega:**

- `Resultado.operacoes` (DataFrame com Chave, A, B e Diferenca, em centavos): só a Data-base mais recente, só |Diferença| > Tolerância, lado ausente 0, ordenado por |Diferença| decrescente e, no empate, pela Chave (para a ordem ser determinística).
- Nova aba `Operações com Diferença` depois do Resumo: Chave, Valor A, Valor B e Diferença em reais (`#,##0.00`), cabeçalho em negrito, congelado em A2 e autofiltro `A1:D{n+1}`.
- O gabarito do exemplo guarda as Diferenças plantadas por Chave e ganhou `operacoes`, na mesma ordem.
- Testes: seam 1 (`test_operacoes_com_diferenca_...`) e ponta a ponta (`test_aba_operacoes_com_diferenca_...`, mais as abas esperadas no primeiro teste). pytest: 52 passed.
- Olhos de usuário em `exemplo\`: 60 linhas, igual a Chaves com Diferença do Resumo, em ordem decrescente de |Diferença|, cabeçalho congelado e com filtro, órfãs com o lado ausente 0.
- Arquivos: `conciliacao_enxuta/cruzamento.py`, `conciliacao_enxuta/excel.py`, `conciliacao_enxuta/exemplo.py`, `tests/test_cruzamento.py`, `tests/test_ponta_a_ponta.py`.

**Onde está agora (depois da entrega):**
