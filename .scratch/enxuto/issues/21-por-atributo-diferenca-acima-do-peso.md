# 21: Por Atributo com Diferença absoluta e Diferença acima do peso

**What to build:** a aba Por Atributo passa a mostrar só os valores de Atributo com Diferença acima do peso, do maior para o menor. Para cada Atributo e valor, na Data-base mais recente, Diferença acima do peso = % da Diferença absoluta − % de |Valor A| no total (usa B quando A é zero), as duas sobre as Chaves, sem as linhas sem Chave. Entram só os valores com Diferença acima do peso > 0; valor vazio não entra. Ordem pela Diferença acima do peso, decrescente; no empate, Atributo e Valor. Colunas: Atributo, Valor, **Diferença absoluta** (soma das |Diferença| das Chaves com o valor) e **Diferença acima do peso** (em %). O termo Concentração sai do código e da saída. Sem filtro; sem Atributo, só o cabeçalho. Ver spec: Solução, Decisões de implementação (Regras/Diferença acima do peso; Saída/Por Atributo); histórias 22, 23 e 24.

**Blocked by:** —

**Status:** ready-for-agent

- [ ] Seam 1: um valor com pouco peso no total e muita Diferença fica no topo, com a Diferença acima do peso certa.
- [ ] Seam 1: um valor que todas as Chaves têm (Diferença acima do peso ≤ 0) não aparece.
- [ ] Seam 1: a ordem é pela Diferença acima do peso, com o empate por Atributo e Valor.
- [ ] Seam 1: a coluna Diferença absoluta é a soma sem sinal; Chaves com Diferenças de sinais opostos não se anulam.
- [ ] Seam 1: linhas sem Chave não mexem nas porcentagens.
- [ ] Aba `Por Atributo`: colunas Atributo, Valor, Diferença absoluta (reais) e Diferença acima do peso (`0.00%`), sem filtro; sem Atributo, só o cabeçalho.
- [ ] O gabarito do gerador de exemplo troca a Concentração pela Diferença acima do peso e corta os valores ≤ 0; o teste de ponta a ponta confere a ordem e os valores.
- [ ] `C:\Users\josef\Projetos\Conciliacao-Enxuta\.venv\Scripts\python -m pytest -q` passa.
- [ ] Teste com olhos de usuário: rodar a CLI sobre `exemplo\` e conferir com openpyxl (`PYTHONIOENCODING=utf-8`) que Carteira Legado está no topo, que Moeda BRL não aparece e que nenhuma Diferença acima do peso é zero ou negativa.

**Notas de entrega:**

**Onde está agora (depois da entrega):**
