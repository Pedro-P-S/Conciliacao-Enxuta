# 05: Linhas sem Chave e Chaves repetidas

**What to build:** a Preparação antes do cruzamento. Linhas sem Chave (vazia ou só espaço) ficam fora do cruzamento, e o Resumo avisa, por base, quantas são e quanto somam. Linhas com a mesma Chave e a mesma Data-base são somadas numa só. Ver spec: Decisões de implementação (Regras/Preparação, Saída/Resumo — avisos); histórias 11 e 12.

**Blocked by:** 01

**Status:** ready-for-agent

- [ ] Seam 1: duas linhas da mesma Chave na mesma Data-base viram uma, com o Valor somado, antes de comparar com a outra base.
- [ ] Seam 1: linhas sem Chave não entram nos totais nem nas Chaves com Diferença; o Resultado traz, por base, a quantidade e a soma delas.
- [ ] Resumo: o aviso de linhas sem Chave aparece só quando há alguma, com a quantidade e a soma (em reais, `#.##0,00`) de cada base; sem linhas sem Chave, nenhum aviso.
- [ ] A invariante continua valendo com Chaves repetidas.
- [ ] O gerador de exemplo planta Chaves repetidas e linhas sem Chave; o teste de ponta a ponta confere o aviso e os totais contra o gabarito.
- [ ] `C:\Users\josef\Projetos\Desafio-Conciliacao\.venv\Scripts\python -m pytest -q` passa.
- [ ] Teste com olhos de usuário: regenerar `exemplo\` com linhas sem Chave e uma Chave repetida, rodar a CLI e conferir no Resumo (openpyxl, `PYTHONIOENCODING=utf-8`) o aviso com quantidade e soma por base e os totais com a Chave repetida somada.

**Notas de entrega:**

**Onde está agora (depois da entrega):**
