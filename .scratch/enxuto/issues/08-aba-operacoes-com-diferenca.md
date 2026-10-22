# 08: Aba Operações com Diferença

**What to build:** o analista vê a lista das Chaves com Diferença na Data-base mais recente, uma linha por Chave, da maior para a menor |Diferença|, com as colunas Chave, Valor A, Valor B e Diferença (em reais, `#.##0,00`). Cabeçalho congelado e com filtro, para filtrar e ordenar pelo cabeçalho. As colunas Tipo do Erro, Aberta desde e Atributos entram nos tickets seguintes. Ver spec: Solução, Decisões de implementação (Saída/Operações com Diferença); histórias 25, 26 (parte) e 31.

**Blocked by:** 06

**Status:** ready-for-agent

- [ ] Seam 1: o Resultado traz as Operações com Diferença só da Data-base mais recente, só as Chaves com |Diferença| > Tolerância, ordenadas por |Diferença| decrescente.
- [ ] A aba `Operações com Diferença` tem as colunas Chave, Valor A, Valor B e Diferença, com Só em A/Só em B mostrando o lado ausente como 0.
- [ ] Cabeçalho congelado e com autofiltro cobrindo as colunas e linhas.
- [ ] O teste de ponta a ponta confere nomes e quantidade de abas, colunas, ordem das linhas e valores contra o gabarito.
- [ ] `C:\Users\josef\Projetos\Desafio-Conciliacao\.venv\Scripts\python -m pytest -q` passa.
- [ ] Teste com olhos de usuário: rodar a CLI sobre `exemplo\` e conferir com openpyxl (`PYTHONIOENCODING=utf-8`) que a aba lista as Chaves com Diferença da Data-base mais recente, da maior para a menor, com cabeçalho congelado e filtro, e que a quantidade bate com Chaves com Diferença do Resumo.

**Notas de entrega:**

**Onde está agora (depois da entrega):**
