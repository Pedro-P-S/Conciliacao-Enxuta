# 37: HTML igual ao Resumo do Excel

**What to build:** o `.html` mostra o que o Resumo do Excel mostra, usando o `quadro_do_resumo`: o percentual arredonda como no Excel; o eixo do gráfico mostra 0 quando não há Diferença; com uma Data-base só, o gráfico de linha mostra o ponto e a data uma vez; o caractere de controle sai do texto, como no Excel; `<`, `&` e aspas aparecem como texto. Ver spec: Saída (HTML), bloco "Decisões de 24/10/2026" (HTML igual ao Excel), Testes/Correções da auditoria (de ponta a ponta); história 58.

**Blocked by:** 29

**Status:** done

- [x] Teste de ponta a ponta: o percentual do `.html` é o mesmo que o Excel mostra para o mesmo número.
- [x] Teste de ponta a ponta: sem Diferença, o eixo do gráfico mostra 0.
- [x] Teste de ponta a ponta: com uma Data-base só, o gráfico de linha traz o ponto e a data aparece uma vez.
- [x] Teste de ponta a ponta: um Atributo com caractere de controle aparece sem ele, como no Excel; um com `<`, `&` e aspas aparece como texto.
- [x] `C:\Users\josef\Projetos\Conciliacao-Enxuta\.venv\Scripts\python -m pytest -q` passa.
- [x] Teste com olhos de usuário: rodar a CLI sobre `exemplo\` e sobre uma cópia com uma Data-base só, abrir o `.html` e conferir, ao lado da aba Resumo do `.xlsx`, que os números, os percentuais e os gráficos batem.

**Notas de entrega:**
Seam: só a seam 2, de ponta a ponta pela CLI (`main(["conciliar", ...])`) até o `.html`, com o `.xlsx` ao lado para comparar, como manda a spec (Seams dos testes); nenhuma seam nova. Quatro testes novos em `tests/test_html.py`, cada um vermelho antes do código, menos a parte do escape de `<`, `&` e aspas, que já passava (o `html.escape` já cuidava; o teste fica como guarda).
- Percentual: `_percentual` arredonda como o Excel mostra `0.00%` (15 dígitos, meio para cima); 0,90625 sai 90,63%, e não 90,62%.
- Eixo: sem Diferença, o gráfico de linha mostra só o 0,00 no eixo (antes mostrava 0,01 no topo).
- Uma Data-base só: o gráfico de linha ganha um `<circle>` no ponto e a data aparece uma vez.
- Caractere de controle: o Atributo e o seu valor saem sem ele, pela mesma regex do openpyxl que o Excel usa (`_do_arquivo` no `html`).
- Olhos de usuário: CLI sobre `exemplo\` e sobre `exemplo\caso_html_37\` (só a Data-base 30/09/2026); o quadro, os avisos, os Atributos Problemáticos (79,01%, 74,02%, 22,66%) e as faixas batem com a aba Resumo; com uma Data-base só, o gráfico traz o ponto e 30/09/2026 uma vez.
Arquivos: `conciliacao_enxuta/html.py`, `tests/test_html.py`.

**Onde está agora (depois da entrega):**
O `.html` mostra o que o Resumo do Excel mostra nos quatro casos da spec; suíte com 272 testes passando.
