# 22: Atributos Problemáticos no Resumo

**What to build:** o analista vê no Resumo por onde começar sem abrir a aba Por Atributo. Os Atributos Problemáticos são as 5 primeiras linhas da tabela Por Atributo, misturando Atributos, com as mesmas colunas (Atributo, Valor, Diferença absoluta, Diferença acima do peso); menos de 5 se a tabela tiver menos; sem nenhuma linha, a tabela não aparece. Ficam no Resumo depois dos avisos. Ver spec: Solução, Decisões de implementação (Regras/Atributos Problemáticos; Saída/Resumo item 3); história 42.

**Blocked by:** 21

**Status:** done

- [x] Seam 1: com mais de 5 valores acima do peso, os Atributos Problemáticos são os 5 primeiros da tabela Por Atributo, na mesma ordem e misturando Atributos.
- [x] Seam 1: com menos de 5, vêm todos; com nenhum, vem vazio.
- [x] Resumo: a tabela com título e as colunas da aba Por Atributo, nos mesmos formatos, depois dos avisos; sem Atributo acima do peso, nada aparece.
- [x] O teste de ponta a ponta confere a tabela no Resumo contra o gabarito.
- [x] `C:\Users\josef\Projetos\Conciliacao-Enxuta\.venv\Scripts\python -m pytest -q` passa.
- [x] Teste com olhos de usuário: rodar a CLI sobre `exemplo\` e conferir com openpyxl (`PYTHONIOENCODING=utf-8`) que o Resumo mostra os mesmos 5 primeiros valores da aba Por Atributo, com Carteira Legado em primeiro.

**Notas de entrega:**
- Seams (escolhidos pela spec, seção Testes, sem acesso ao usuário): Seam 1 `conciliar` → `Resultado.atributos_problematicos`; Seam 2 CLI → `.xlsx` lido com openpyxl.
- `Resultado.atributos_problematicos` é uma propriedade: `por_atributo.head(5)` (constante `QUANTOS_PROBLEMATICOS`), com as mesmas colunas.
- Defeito achado pelo teste "com nenhum, vem vazio": sem Diferença nenhuma, a % da Diferença absoluta dava 0/0 = NaN, e o polars trata NaN > 0 como verdadeiro, então a tabela Por Atributo vinha com linhas NaN. `_por_atributo` agora devolve a tabela vazia quando a Diferença absoluta total é 0.
- Resumo: título "Atributos Problemáticos" em negrito, uma linha abaixo do último aviso (`ws.max_row + 2`), e a tabela com o cabeçalho e os formatos da aba Por Atributo. O cabeçalho e as linhas saem de `_tabela_por_atributo`, usada pelas duas. Sem linhas, nada aparece. Coluna D do Resumo com largura 22.
- Testes: dois no Seam 1 (7 valores acima do peso → os 5 primeiros misturando Canal e Produto; 1 valor e nenhum) e dois no Seam 2 (a tabela no Resumo contra `gabarito.por_atributo[:5]`, depois dos avisos; e bases em que nada passa do peso, sem a tabela). O teste "sem a tabela" de ponta a ponta já passava antes do código (é a ausência). O helper `avisos_do_resumo` agora para no título dos Atributos Problemáticos.
- O gabarito do exemplo tem só 3 valores acima do peso (Carteira Legado, Produto Seguro, Filial 05), então o Resumo mostra 3; não mexi no gerador, por estar fora do ticket.
- Teste com olhos de usuário: CLI sobre `exemplo\`; o Resumo mostra as mesmas 3 linhas da aba Por Atributo, com Carteira Legado em primeiro, `#,##0.00` e `0.00%`, depois do aviso de Data-bases ignoradas.
- Arquivos: `conciliacao_enxuta/cruzamento.py`, `conciliacao_enxuta/excel.py`, `tests/test_cruzamento.py`, `tests/test_ponta_a_ponta.py`.

**Onde está agora (depois da entrega):**
Os Atributos Problemáticos estão no `Resultado` e no Resumo do `.xlsx`, entre os avisos e o gráfico. Quando o 25 for juntado, o aviso de Linhas rejeitadas entra antes do título; a tabela usa `ws.max_row + 2`, então continua depois dos avisos. O `.html` (ticket do Resumo em HTML) ainda precisa trazer a mesma tabela.
