# 34: Atributo com nome de coluna interna

**What to build:** o nome do Atributo é livre: um Atributo chamado `Peso`, `Absoluta` ou `Atributo` (nomes que a ferramenta usa por dentro) concilia normalmente, sem derrubar a conciliação. Junto, os testes da seam 1 passam a pegar duas mutações: tirar o filtro de Data-bases comuns do Casa com linha sem Chave e trocar `>` por `>=` no corte da Diferença acima do peso. Ver spec: Regras (Atributo), bloco "Decisões de 24/10/2026" (Atributo com nome de coluna interna, Seams dos testes), Testes/Correções da auditoria (seam 1); história 47.

**Blocked by:** 29

**Status:** ready-for-agent

- [ ] Teste na seam 1 (`conciliar`): bases com Atributos `Peso`, `Absoluta` e `Atributo` conciliam, e a tabela Por Atributo e as Operações com Diferença trazem esses Atributos.
- [ ] Teste na seam 1 que falha se o Casa com linha sem Chave deixar de filtrar as Data-bases comuns.
- [ ] Teste na seam 1 que falha se o corte da Diferença acima do peso usar `>=` no lugar de `>`.
- [ ] `C:\Users\josef\Projetos\Conciliacao-Enxuta\.venv\Scripts\python -m pytest -q` passa.
- [ ] Teste com olhos de usuário: numa cópia das bases de `exemplo\`, renomear um Atributo para `Peso`, rodar a CLI e conferir que as abas Por Atributo e Operações com Diferença mostram a coluna `Peso` com os valores.

**Notas de entrega:**

**Onde está agora (depois da entrega):**
