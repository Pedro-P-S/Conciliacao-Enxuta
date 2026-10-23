# 21: Por Atributo com Diferença absoluta e Diferença acima do peso

**What to build:** a aba Por Atributo passa a mostrar só os valores de Atributo com Diferença acima do peso, do maior para o menor. Para cada Atributo e valor, na Data-base mais recente, Diferença acima do peso = % da Diferença absoluta − % de |Valor A| no total (usa B quando A é zero), as duas sobre as Chaves, sem as linhas sem Chave. Entram só os valores com Diferença acima do peso > 0; valor vazio não entra. Ordem pela Diferença acima do peso, decrescente; no empate, Atributo e Valor. Colunas: Atributo, Valor, **Diferença absoluta** (soma das |Diferença| das Chaves com o valor) e **Diferença acima do peso** (em %). O termo Concentração sai do código e da saída. Sem filtro; sem Atributo, só o cabeçalho. Ver spec: Solução, Decisões de implementação (Regras/Diferença acima do peso; Saída/Por Atributo); histórias 22, 23 e 24.

**Blocked by:** —

**Status:** done

- [x] Seam 1: um valor com pouco peso no total e muita Diferença fica no topo, com a Diferença acima do peso certa.
- [x] Seam 1: um valor que todas as Chaves têm (Diferença acima do peso ≤ 0) não aparece.
- [x] Seam 1: a ordem é pela Diferença acima do peso, com o empate por Atributo e Valor.
- [x] Seam 1: a coluna Diferença absoluta é a soma sem sinal; Chaves com Diferenças de sinais opostos não se anulam.
- [x] Seam 1: linhas sem Chave não mexem nas porcentagens.
- [x] Aba `Por Atributo`: colunas Atributo, Valor, Diferença absoluta (reais) e Diferença acima do peso (`0.00%`), sem filtro; sem Atributo, só o cabeçalho.
- [x] O gabarito do gerador de exemplo troca a Concentração pela Diferença acima do peso e corta os valores ≤ 0; o teste de ponta a ponta confere a ordem e os valores.
- [x] `C:\Users\josef\Projetos\Conciliacao-Enxuta\.venv\Scripts\python -m pytest -q` passa.
- [x] Teste com olhos de usuário: rodar a CLI sobre `exemplo\` e conferir com openpyxl (`PYTHONIOENCODING=utf-8`) que Carteira Legado está no topo, que Moeda BRL não aparece e que nenhuma Diferença acima do peso é zero ou negativa.

**Notas de entrega:**
Seams escolhidos pela spec (sem acesso ao usuário): Seam 1 `conciliar` → `Resultado.por_atributo`, e Seam 2 CLI → `.xlsx` lido com openpyxl, comparado com o gabarito do gerador.

- `conciliacao_enxuta/cruzamento.py`: `_por_atributo` devolve as colunas Atributo, Valor, Absoluta (soma das |Diferença| acima da Tolerância das Chaves com o valor) e AcimaDoPeso (% da Diferença absoluta − % de |A|, ou |B| quando A é zero). Entram só os valores com AcimaDoPeso > 0. A ordem é AcimaDoPeso decrescente, com o empate por Atributo e Valor. As linhas sem Chave já saem na Preparação, então não mexem nas porcentagens. Saíram a soma com sinal e a Concentração.
- `conciliacao_enxuta/excel.py`: aba Por Atributo com os cabeçalhos "Diferença absoluta" (reais) e "Diferença acima do peso" (`0.00%`), sem filtro.
- `conciliacao_enxuta/exemplo.py`: o gabarito traz (Atributo, Valor, Diferença absoluta, Diferença acima do peso), corta ≤ 0 e ordena como o cruzamento. As órfãs dentro da Tolerância passam a ter a Moeda BRL. Sem isso, BRL não estava em todas as Chaves e ficava com +6e-8 acima do peso.
- `tests/test_cruzamento.py`: testes novos (topo, BRL e abaixo do peso fora, ordem e empate, soma sem sinal, linhas sem Chave) e os antigos adaptados.
- `tests/test_ponta_a_ponta.py`: confere a ordem, os valores, o formato, Legado no topo, BRL fora e tudo > 0.
- O teste das linhas sem Chave não confere a Diferença absoluta do Resumo, porque ela entra nos totais pelo ticket 19, feito em paralelo.
- Olhos de usuário: a CLI sobre `exemplo\` mostra Carteira Legado (79,01%), Produto Seguro (74,02%) e Filial 05 (22,66%). BRL não aparece e nenhum valor é ≤ 0.

**Onde está agora (depois da entrega):**
A aba Por Atributo mostra só os valores com Diferença acima do peso, do maior para o menor. Os Atributos Problemáticos do Resumo (outro ticket) podem pegar as 5 primeiras linhas de `Resultado.por_atributo`.
