# 14: Aba Por Atributo, ordenada pela Concentração

**What to build:** o analista vê onde a Diferença se concentra, descontado o peso que cada valor de Atributo já tem no total. Na Data-base mais recente, para cada Atributo e valor com pelo menos uma Chave com Diferença, calcula-se a Concentração = % da Diferença absoluta ÷ % de |Valor A| no total (usando B quando A é zero). A aba **Por Atributo** tem as colunas Atributo, Valor, Diferença (soma com sinal) e % da Diferença (parte da Diferença absoluta), ordenada pela Concentração decrescente, que não é exibida. Sem filtro. Ver spec: Solução, Decisões de implementação (Regras/Concentração por valor, Saída/Por Atributo); histórias 22, 23 e 24.

**Blocked by:** 13

**Status:** ready-for-agent

- [ ] Seam 1: um valor de Atributo que concentra a Diferença (pouco peso no total, muita Diferença) fica no topo.
- [ ] Seam 1: um valor que todas as Chaves têm tem Concentração 1 e não fica acima de um valor realmente concentrado.
- [ ] Seam 1: o peso no total usa |Valor A| e cai para |Valor B| quando A é zero (Só em B incluído).
- [ ] Seam 1: entram só os valores com pelo menos uma Chave com Diferença.
- [ ] Aba `Por Atributo`: colunas Atributo, Valor, Diferença (reais, com sinal) e % da Diferença (formato percentual), sem coluna de Concentração e sem filtro.
- [ ] Bases sem Atributo geram a aba só com o cabeçalho (o Excel continua com as 4 abas).
- [ ] O gerador de exemplo planta um Atributo concentrado e um que todas as Chaves têm; o teste de ponta a ponta confere a ordem e os valores contra o gabarito.
- [ ] `C:\Users\josef\Projetos\Desafio-Conciliacao\.venv\Scripts\python -m pytest -q` passa.
- [ ] Teste com olhos de usuário: rodar a CLI sobre `exemplo\` e conferir com openpyxl (`PYTHONIOENCODING=utf-8`) que a aba Por Atributo mostra no topo o valor plantado como concentrado e que o valor que todas as Chaves têm não aparece como suspeito.

**Notas de entrega:**

**Onde está agora (depois da entrega):**
