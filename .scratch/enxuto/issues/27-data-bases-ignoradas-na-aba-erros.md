# 27: Data-bases ignoradas na aba Erros

**What to build:** as Data-bases que estão só numa base saem dos avisos do Resumo e vão para a aba Erros, antes das Linhas rejeitadas: uma linha por Data-base ignorada, com a Base que a tem, a Data e o Motivo `Data-base só na Base A` ou `Data-base só na Base B` (Linha, Chave e Valor vazios). Elas contam no limite e no aviso de corte da aba. Ver spec: Decisões de implementação (Regras/Data-bases; Saída/Resumo item 2 e Erros); história 10.

**Blocked by:** 25

**Status:** ready-for-agent

- [ ] Aba `Erros`: primeiro as Data-bases ignoradas, em ordem de data, com a Base, a Data e o Motivo; depois as Linhas rejeitadas.
- [ ] Resumo: não há mais aviso de Data-bases ignoradas.
- [ ] Com o limite reduzido por parâmetro, o corte conta as Data-bases ignoradas junto com as Linhas rejeitadas.
- [ ] O teste de ponta a ponta confere a linha da Data-base plantada só na Base B (01/10/2026).
- [ ] `C:\Users\josef\Projetos\Conciliacao-Enxuta\.venv\Scripts\python -m pytest -q` passa.
- [ ] Teste com olhos de usuário: rodar a CLI sobre `exemplo\` e conferir com openpyxl (`PYTHONIOENCODING=utf-8`) que a primeira linha da aba Erros é 01/10/2026 com `Data-base só na Base B` e que o Resumo não fala dela.

**Notas de entrega:**

**Onde está agora (depois da entrega):**
