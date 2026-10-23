# 22: Atributos Problemáticos no Resumo

**What to build:** o analista vê no Resumo por onde começar sem abrir a aba Por Atributo. Os Atributos Problemáticos são as 5 primeiras linhas da tabela Por Atributo, misturando Atributos, com as mesmas colunas (Atributo, Valor, Diferença absoluta, Diferença acima do peso); menos de 5 se a tabela tiver menos; sem nenhuma linha, a tabela não aparece. Ficam no Resumo depois dos avisos. Ver spec: Solução, Decisões de implementação (Regras/Atributos Problemáticos; Saída/Resumo item 3); história 42.

**Blocked by:** 21

**Status:** ready-for-agent

- [ ] Seam 1: com mais de 5 valores acima do peso, os Atributos Problemáticos são os 5 primeiros da tabela Por Atributo, na mesma ordem e misturando Atributos.
- [ ] Seam 1: com menos de 5, vêm todos; com nenhum, vem vazio.
- [ ] Resumo: a tabela com título e as colunas da aba Por Atributo, nos mesmos formatos, depois dos avisos; sem Atributo acima do peso, nada aparece.
- [ ] O teste de ponta a ponta confere a tabela no Resumo contra o gabarito.
- [ ] `C:\Users\josef\Projetos\Conciliacao-Enxuta\.venv\Scripts\python -m pytest -q` passa.
- [ ] Teste com olhos de usuário: rodar a CLI sobre `exemplo\` e conferir com openpyxl (`PYTHONIOENCODING=utf-8`) que o Resumo mostra os mesmos 5 primeiros valores da aba Por Atributo, com Carteira Legado em primeiro.

**Notas de entrega:**

**Onde está agora (depois da entrega):**
