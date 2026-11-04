# 44: HTML pelas aulas do Módulo 3

**What to build:** o `.html` passa a abrir com uma frase-resposta (o Tipo do Erro que mais explica a Diferença absoluta), ganha o gráfico de barras Por Tipo do Erro, mostra os reais com `R$` e abreviados (`R$ 688,3 mi`) e troca, nos Atributos Problemáticos, a Concentração desproporcional pelas colunas `% da diferença` e `% do valor`. O Excel não muda. Ver spec: bloco "Decisões de 04/11/2026: o HTML pelas aulas do Módulo 3"; histórias 67 a 70; `GRILL.md`, decisões 42 a 45.

**Blocked by:** —

**Status:** done

- [x] Teste de ponta a ponta: a frase-resposta vem antes do quadro, com o Tipo, a parte com 2 casas e as Chaves; sem Chave com Diferença, não há frase.
- [x] Teste de ponta a ponta: o gráfico Por Tipo do Erro vem depois do quadro e antes dos Atributos Problemáticos, com os rótulos `Tipo (N Chaves)` na ordem da aba Por Tipo do Erro, a nota e a tabela dos dados; sem Chave com Diferença, não aparece.
- [x] Teste de ponta a ponta: os reais visíveis vão com `R$` e abreviados, nas bordas (abaixo de R$ 1.000, a passagem para a próxima unidade, o negativo, o zero), e as tabelas dos dados ficam com o valor exato e "(R$)" no título.
- [x] Teste de ponta a ponta: os Atributos Problemáticos têm `% da diferença` e `% do valor`, arredondados como o Excel.
- [x] `C:\Users\josef\Projetos\Conciliacao-Enxuta\.venv\Scripts\python -m pytest -q` passa.
- [x] Teste com olhos de usuário: rodar a CLI sobre `exemplo\`, abrir o `.html` no navegador e conferir a frase, o gráfico Por Tipo, os reais e os Atributos Problemáticos, nos dois Batimentos.

**Notas de entrega:**
Seam de ponta a ponta (CLI -> `.html`), a de `tests/test_html.py`, sem seam nova. `html.py` ganhou `reais_curtos` (e o `reaisCurtos` no script, para o valor no fim da linha e a dica), a frase `p.frase` antes do painel, o gráfico Por Tipo do Erro pelo mesmo `_grafico_de_barras` da Idade (agora recebe título, coluna, barras e nota) e as colunas `% da diferença` e `% do valor`, calculadas sobre a soma das |Diferença| das Chaves de `operacoes`. As tabelas "Dados do gráfico" ficam com o valor exato e "Diferença absoluta (R$)". O Excel não mudou. 6 testes novos (um parametrizado com 9 casos) e 8 ajustados. Suíte inteira: 330 passam. Olhos de usuário: `exemplo\revisao_html\conciliacao_2026-09-30.html` no navegador, nos dois Batimentos e em 375px, sem rolagem horizontal.

**Onde está agora (depois da entrega):**
`conciliacao_enxuta/html.py` (`_resumo`, `reais_curtos`, `_grafico_de_barras`, `GRAFICO`) e `tests/test_html.py`.
