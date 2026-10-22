# 12: Idade da Diferença por faixa no Resumo

**What to build:** o analista vê no Resumo, logo abaixo do quadro de totais, a Idade da Diferença em 5 faixas (até 30 dias, 31 a 90, 91 a 365, 366 dias a 5 anos, mais de 5 anos), cada uma com Chaves e Diferença absoluta. A Idade é a quantidade de dias corridos entre o Aberta desde e a Data-base mais recente; Chaves "ou antes" ficam na faixa que a conta der. Ver spec: Solução, Decisões de implementação (Regras/Idade, Saída/Resumo); história 17.

**Blocked by:** 11

**Status:** ready-for-agent

- [ ] Seam 1: as bordas caem na faixa certa: 30 → até 30; 31 → 31 a 90; 90 → 31 a 90; 91 → 91 a 365; 365 → 91 a 365; 366 → 366 a 5 anos; 1826 → 366 a 5 anos; 1827 → mais de 5 anos.
- [ ] Seam 1: Diferença aberta na própria Data-base mais recente tem Idade 0 e cai em até 30.
- [ ] Seam 1: a soma das Chaves e da Diferença absoluta das 5 faixas é igual a Chaves com Diferença e à Diferença absoluta do Resumo.
- [ ] Resumo: as 5 faixas aparecem sempre (mesmo vazias), na ordem da spec, com Chaves e Diferença absoluta em reais, abaixo do quadro de totais e acima dos avisos.
- [ ] O teste de ponta a ponta confere as faixas contra o gabarito do gerador de exemplo.
- [ ] `C:\Users\josef\Projetos\Desafio-Conciliacao\.venv\Scripts\python -m pytest -q` passa.
- [ ] Teste com olhos de usuário: rodar a CLI sobre o `exemplo\` de seis meses e conferir com openpyxl (`PYTHONIOENCODING=utf-8`) que as 5 faixas aparecem no Resumo e que os totais delas batem com Chaves com Diferença e Diferença absoluta.

**Notas de entrega:**

**Onde está agora (depois da entrega):**
