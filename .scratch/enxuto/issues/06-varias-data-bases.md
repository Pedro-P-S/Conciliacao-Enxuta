# 06: Várias Data-bases no mesmo arquivo

**What to build:** o analista manda arquivos com muitas Data-bases (por exemplo, uma posição por dia útil durante seis meses). Entram só as Data-bases comuns às duas bases; a Data-base mais recente é a maior comum, e é dela que saem os totais do Resumo e o nome do arquivo. As Data-bases que estão só numa base são ignoradas e listadas num aviso do Resumo. O cruzamento é feito por Data-base, e o Resultado guarda a Diferença absoluta de cada Data-base comum (o Histórico da Diferença), para os tickets seguintes. Ver spec: Solução, Decisões de implementação (Regras/Data-bases, Cruzamento por Data-base, Saída/Resumo — avisos); histórias 9 e 10.

**Blocked by:** 01

**Status:** done

- [x] Seam 1: com Data-bases {1, 2, 3} em A e {2, 3, 4} em B, a mais recente é 3 e as Data-bases 1 e 4 vêm como ignoradas, cada uma com a base em que estava.
- [x] Seam 1: o cruzamento é por Chave dentro de cada Data-base (uma Chave em A na Data-base 2 não cruza com a mesma Chave em B na Data-base 3).
- [x] Seam 1: o Resultado traz a Diferença absoluta de cada Data-base comum, em ordem de data.
- [x] Resumo: totais e nome do arquivo usam a Data-base mais recente comum; o aviso de Data-bases ignoradas aparece só quando há alguma e diz quais são e de qual base.
- [x] Sem Data-base comum, a mensagem é simples e nenhum `.xlsx` é gerado.
- [x] O gerador de exemplo passa a gerar várias Data-bases (dias úteis de alguns meses) e uma Data-base só numa base; o teste de ponta a ponta confere contra o gabarito.
- [x] `C:\Users\josef\Projetos\Desafio-Conciliacao\.venv\Scripts\python -m pytest -q` passa.
- [x] Teste com olhos de usuário: regenerar `exemplo\` com seis meses de dias úteis e uma Data-base extra só na Base B, rodar a CLI e conferir (openpyxl, `PYTHONIOENCODING=utf-8`) que o nome do arquivo e o Resumo usam a maior Data-base comum e que o aviso lista a Data-base ignorada.

**Notas de entrega:**
- `cruzamento.conciliar` filtra as Data-bases comuns às duas bases e faz a junção completa por Chave e Data-base. Os totais, a Diferença e as Chaves com Diferença saem da maior Data-base comum. O `Resultado` ganhou três campos: `data_bases_so_em_a` e `data_bases_so_em_b`, com as Data-bases ignoradas de cada base em ordem, e `historico`, com tuplas (Data-base comum, Diferença absoluta) em ordem de data, que vale 0 quando não há Diferença.
- Sem Data-base comum (o que inclui uma base sem linhas), `conciliar` levanta `SemDataBaseComum`, e a CLI só mostra "A Base A e a Base B não têm nenhuma Data-base em comum." no stderr, sai com 1 e não gera `.xlsx`. Decisão: a mensagem não lista os períodos das bases, para continuar simples (e não quebrar com uma base vazia).
- O Resumo traz uma linha de aviso por base que tenha Data-bases ignoradas, na coluna A, uma linha abaixo do quadro: "Data-bases ignoradas por estarem só na Base B: 01/10/2026.". Se não há nenhuma, não aparece aviso. A posição é fixa logo abaixo do quadro; quando as faixas de Idade entrarem (ticket 12), os avisos devem descer.
- O gerador de exemplo escreve uma posição por dia útil, de 01/04/2026 a 30/09/2026 (131 Data-bases, com valores novos a cada dia), e a Base B traz também 01/10/2026. O gabarito ganhou `data_bases_so_em_b`.
- Teste com olhos de usuário: regenerei o `exemplo\` e rodei a CLI. O arquivo saiu como `conciliacao_2026-09-30.xlsx`, e o Resumo bate com o gabarito: Total A 8.505.601,79, Total B 8.596.547,00 e 60 Chaves com Diferença. O aviso lista 01/10/2026 como só na Base B. Com uma Base B só de 01/10/2026, a tela mostra a mensagem simples, o código de saída é 1 e nenhum `.xlsx` novo é gerado.
- Arquivos: `conciliacao_enxuta/cruzamento.py`, `conciliacao_enxuta/cli.py`, `conciliacao_enxuta/excel.py`, `conciliacao_enxuta/exemplo.py`, `tests/test_cruzamento.py`, `tests/test_ponta_a_ponta.py`.
- pytest: 22 passed.
- No merge com o 05: a contagem e a soma das linhas sem Chave passaram a pegar só as Data-bases comuns, as que entram no cruzamento; as das Data-bases ignoradas não contam. O aviso de linhas sem Chave vem antes do de Data-bases ignoradas, na ordem da spec.

**Onde está agora (depois da entrega):**
