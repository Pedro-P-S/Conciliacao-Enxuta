# 24: Idade da linha sem Chave

**What to build:** uma Linha sem Chave com Diferença na Data-base mais recente também tem Idade. O mesmo valor nas Data-bases seguintes é o mesmo lançamento, então ela conta desde a primeira Data-base de uma sequência contínua em que esse valor aparece entre as linhas sem Chave da sua base, até a mais recente; se o valor some e volta, conta da volta. Ela entra na Diferença absoluta da sua faixa, e o rótulo da faixa ganha a quantidade de linhas sem Chave quando houver, como `91 a 365 dias (12 Chaves, 1 linha sem Chave)`. Assim, a soma das faixas é a Diferença absoluta do Resumo. Ver spec: Decisões de implementação (Regras/Linhas sem Chave e Idade; Saída/Resumo item 4); história 17.

**Blocked by:** 18, 23

**Status:** ready-for-agent

- [ ] Seam 1: o mesmo valor sem Chave repetido nas Data-bases seguintes conta desde a primeira em que apareceu.
- [ ] Seam 1: um valor sem Chave que some e volta conta desde a volta.
- [ ] Seam 1: cada faixa traz as Chaves, as linhas sem Chave e a Diferença absoluta com as duas; a soma das faixas é a Diferença absoluta do Resumo.
- [ ] Seam 1: linha sem Chave dentro da Tolerância não entra na Idade.
- [ ] Rótulo das barras: `(N Chaves, M linhas sem Chave)` quando houver, com singular e plural certos; sem linhas sem Chave, o rótulo não muda.
- [ ] O gabarito do gerador de exemplo inclui as linhas sem Chave nas faixas; o teste de ponta a ponta confere.
- [ ] `C:\Users\josef\Projetos\Conciliacao-Enxuta\.venv\Scripts\python -m pytest -q` passa.
- [ ] Teste com olhos de usuário: rodar a CLI sobre `exemplo\` e conferir com openpyxl (`PYTHONIOENCODING=utf-8`) que a soma das barras em `_grafico` é a Diferença absoluta do Resumo e que a faixa das linhas sem Chave mostra quantas são no rótulo.

**Notas de entrega:**

**Onde está agora (depois da entrega):**
