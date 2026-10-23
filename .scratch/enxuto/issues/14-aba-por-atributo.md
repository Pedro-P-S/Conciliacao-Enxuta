# 14: Aba Por Atributo, ordenada pela Concentração

**What to build:** o analista vê onde a Diferença se concentra, descontado o peso que cada valor de Atributo já tem no total. Na Data-base mais recente, para cada Atributo e valor com pelo menos uma Chave com Diferença, calcula-se a Concentração = % da Diferença absoluta ÷ % de |Valor A| no total (usando B quando A é zero). A aba **Por Atributo** tem as colunas Atributo, Valor, Diferença (soma com sinal) e % da Diferença (parte da Diferença absoluta), ordenada pela Concentração decrescente, que não é exibida. Sem filtro. Ver spec: Solução, Decisões de implementação (Regras/Concentração por valor, Saída/Por Atributo); histórias 22, 23 e 24.

**Blocked by:** 13

**Status:** done

- [x] Seam 1: um valor de Atributo que concentra a Diferença (pouco peso no total, muita Diferença) fica no topo.
- [x] Seam 1: um valor que todas as Chaves têm tem Concentração 1 e não fica acima de um valor realmente concentrado.
- [x] Seam 1: o peso no total usa |Valor A| e cai para |Valor B| quando A é zero (Só em B incluído).
- [x] Seam 1: entram só os valores com pelo menos uma Chave com Diferença.
- [x] Aba `Por Atributo`: colunas Atributo, Valor, Diferença (reais, com sinal) e % da Diferença (formato percentual), sem coluna de Concentração e sem filtro.
- [x] Bases sem Atributo geram a aba só com o cabeçalho (o Excel continua com as 4 abas).
- [x] O gerador de exemplo planta um Atributo concentrado e um que todas as Chaves têm; o teste de ponta a ponta confere a ordem e os valores contra o gabarito.
- [x] `C:\Users\josef\Projetos\Conciliacao-Enxuta\.venv\Scripts\python -m pytest -q` passa.
- [x] Teste com olhos de usuário: rodar a CLI sobre `exemplo\` e conferir com openpyxl (`PYTHONIOENCODING=utf-8`) que a aba Por Atributo mostra no topo o valor plantado como concentrado e que o valor que todas as Chaves têm não aparece como suspeito.

**Notas de entrega:**

- `conciliar` devolve `por_atributo` (Atributo, Valor, Diferenca com sinal, Parte = fração da Diferença absoluta, Concentracao), só com os valores que têm alguma Chave com Diferença, por Concentração decrescente (empate: Atributo e Valor). O peso de cada Chave é |A|, ou |B| quando A é zero ou ausente; os totais de peso e de Diferença absoluta contam todas as Chaves da Data-base mais recente. O Atributo segue a regra de A com fallback para B.
- Decisão: valor de Atributo vazio (nulo) não entra na tabela; por isso a % da Diferença de um Atributo com vazios pode não somar 100%. A revisão de Spec apontou a alternativa de uma linha "(vazio)" para o usuário decidir.
- A Concentração fica no Resultado (os testes da Seam 1 a usam), mas não vai para o Excel.
- Aba `Por Atributo` entre Por Tipo do Erro e Operações com Diferença: Atributo, Valor, Diferença (`#,##0.00`) e % da Diferença (`0.00%`), sem filtro; sem Atributo, só o cabeçalho.
- Gerador de exemplo: as duas bases ganham Carteira (Legado nas Chaves i % 20 == 19, sempre Vírgula deslocada com B = 1000 × A) e Moeda (BRL em todas). O gabarito ganha `por_atributo`, calculado sem passar pelo cruzamento. As Operações agora mostram Produto, Carteira, Moeda e Filial.
- Teste com olhos de usuário em `exemplo\`: no topo da aba aparece Carteira Legado; Moeda BRL vem abaixo, com Concentração 1. Produto Seguro e Filial 05 aparecem logo depois de Legado porque todas as Chaves Legado têm esse Produto e essa Filial.
- Arquivos: `conciliacao_enxuta/cruzamento.py`, `conciliacao_enxuta/excel.py`, `conciliacao_enxuta/exemplo.py`, `tests/test_cruzamento.py` e `tests/test_ponta_a_ponta.py`.
- pytest: 125 passed.

**Onde está agora (depois da entrega):**
