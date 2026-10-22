# 15: Corte das Operações com Diferença acima do limite

**What to build:** quando há mais Chaves com Diferença do que o limite de linhas (parâmetro do módulo `excel`, padrão 700.000), a aba Operações com Diferença mostra só as maiores, e um aviso na linha 1 diz "Nem todas as operações com diferença couberam: mostrando 700.000 de N, as maiores."; o cabeçalho passa para a linha 2, congelado e com filtro. O Resumo também avisa o corte, por último na lista de avisos. Ver spec: Decisões de implementação (Módulos/`excel`, Saída/Resumo — avisos, Saída/Operações com Diferença), Testes (corte com o limite reduzido por parâmetro); história 32.

**Blocked by:** 13

**Status:** ready-for-agent

- [ ] Com o limite reduzido por parâmetro (ex.: 3) e 5 Chaves com Diferença, a aba mostra as 3 maiores por |Diferença|.
- [ ] A linha 1 tem o aviso com o limite e o N formatados no padrão brasileiro (`700.000`); o cabeçalho fica na linha 2, congelado, e o filtro começa nele.
- [ ] Sem corte, não há aviso e o cabeçalho fica na linha 1.
- [ ] Resumo: o aviso de corte aparece só quando há corte e é o último dos avisos.
- [ ] O teste de ponta a ponta usa o limite reduzido por parâmetro e confere aviso, cabeçalho, ordem e quantidade de linhas.
- [ ] `C:\Users\josef\Projetos\Desafio-Conciliacao\.venv\Scripts\python -m pytest -q` passa.
- [ ] Teste com olhos de usuário: gerar o Excel de `exemplo\` com o limite reduzido (chamando o módulo `excel` com limite pequeno) e conferir com openpyxl (`PYTHONIOENCODING=utf-8`) o aviso na linha 1, o cabeçalho na linha 2 e o aviso de corte no Resumo.

**Notas de entrega:**

**Onde está agora (depois da entrega):**
