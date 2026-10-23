# 27: Data-bases ignoradas na aba Erros

**What to build:** as Data-bases que estão só numa base saem dos avisos do Resumo e vão para a aba Erros, antes das Linhas rejeitadas: uma linha por Data-base ignorada, com a Base que a tem, a Data e o Motivo `Data-base só na Base A` ou `Data-base só na Base B` (Linha, Chave e Valor vazios). Elas contam no limite e no aviso de corte da aba. Ver spec: Decisões de implementação (Regras/Data-bases; Saída/Resumo item 2 e Erros); história 10.

**Blocked by:** 25

**Status:** done

- [x] Aba `Erros`: primeiro as Data-bases ignoradas, em ordem de data, com a Base, a Data e o Motivo; depois as Linhas rejeitadas.
- [x] Resumo: não há mais aviso de Data-bases ignoradas.
- [x] Com o limite reduzido por parâmetro, o corte conta as Data-bases ignoradas junto com as Linhas rejeitadas.
- [x] O teste de ponta a ponta confere a linha da Data-base plantada só na Base B (01/10/2026).
- [x] `C:\Users\josef\Projetos\Conciliacao-Enxuta\.venv\Scripts\python -m pytest -q` passa.
- [x] Teste com olhos de usuário: rodar a CLI sobre `exemplo\` e conferir com openpyxl (`PYTHONIOENCODING=utf-8`) que a primeira linha da aba Erros é 01/10/2026 com `Data-base só na Base B` e que o Resumo não fala dela.

**Notas de entrega:**
- `excel._aba_erros` monta a aba com as Data-bases ignoradas (de `Resultado.data_bases_so_em_a/b`, que o cruzamento já calculava) em ordem de data, com a Base, a Data e o Motivo `Data-base só na Base A/B` e Linha, Chave e Valor vazios, seguidas das Linhas rejeitadas. O limite e o aviso de corte valem para as duas juntas. A Data vai como texto `DD/MM/AAAA`, como a das Linhas rejeitadas, para a coluna ter um tipo só.
- O aviso "Data-bases ignoradas por estarem só na Base X" saiu do Resumo.
- Seam testada (escolhida pela spec, seção Testes, Seam 2): arquivos → CLI / `gravar_excel` → `.xlsx` lido com openpyxl. Testes novos: as Data-bases ignoradas em ordem antes das rejeitadas, a do exemplo (01/10/2026 só na Base B) e o corte com limite 2 contando as duas juntas. Este último já passou na primeira execução, porque o corte já incidia sobre a tabela combinada. Os testes antigos que conferiam o aviso no Resumo passaram a conferir que ele não aparece.
- Teste com olhos de usuário: CLI sobre `exemplo\`; a primeira linha da aba Erros é `Base B | | | 01/10/2026 | | Data-base só na Base B` e o Resumo não fala de Data-base ignorada.
- Arquivos: `conciliacao_enxuta/excel.py`, `tests/test_ponta_a_ponta.py`.

**Onde está agora (depois da entrega):**
A aba Erros mostra as Data-bases ignoradas e as Linhas rejeitadas; o Resumo avisa só das Linhas rejeitadas, das linhas sem Chave e do corte das operações.
