# 06: Várias Data-bases no mesmo arquivo

**What to build:** o analista manda arquivos com muitas Data-bases (por exemplo, uma posição por dia útil durante seis meses). Entram só as Data-bases comuns às duas bases; a Data-base mais recente é a maior comum, e é dela que saem os totais do Resumo e o nome do arquivo. As Data-bases que estão só numa base são ignoradas e listadas num aviso do Resumo. O cruzamento é feito por Data-base, e o Resultado guarda a Diferença absoluta de cada Data-base comum (o Histórico da Diferença), para os tickets seguintes. Ver spec: Solução, Decisões de implementação (Regras/Data-bases, Cruzamento por Data-base, Saída/Resumo — avisos); histórias 9 e 10.

**Blocked by:** 01

**Status:** ready-for-agent

- [ ] Seam 1: com Data-bases {1, 2, 3} em A e {2, 3, 4} em B, a mais recente é 3 e as Data-bases 1 e 4 vêm como ignoradas, cada uma com a base em que estava.
- [ ] Seam 1: o cruzamento é por Chave dentro de cada Data-base (uma Chave em A na Data-base 2 não cruza com a mesma Chave em B na Data-base 3).
- [ ] Seam 1: o Resultado traz a Diferença absoluta de cada Data-base comum, em ordem de data.
- [ ] Resumo: totais e nome do arquivo usam a Data-base mais recente comum; o aviso de Data-bases ignoradas aparece só quando há alguma e diz quais são e de qual base.
- [ ] Sem Data-base comum, a mensagem é simples e nenhum `.xlsx` é gerado.
- [ ] O gerador de exemplo passa a gerar várias Data-bases (dias úteis de alguns meses) e uma Data-base só numa base; o teste de ponta a ponta confere contra o gabarito.
- [ ] `C:\Users\josef\Projetos\Desafio-Conciliacao\.venv\Scripts\python -m pytest -q` passa.
- [ ] Teste com olhos de usuário: regenerar `exemplo\` com seis meses de dias úteis e uma Data-base extra só na Base B, rodar a CLI e conferir (openpyxl, `PYTHONIOENCODING=utf-8`) que o nome do arquivo e o Resumo usam a maior Data-base comum e que o aviso lista a Data-base ignorada.

**Notas de entrega:**

**Onde está agora (depois da entrega):**
