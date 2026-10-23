# 12: Idade da Diferença por faixa no Resumo

**What to build:** o analista vê no Resumo, logo abaixo do quadro de totais, a Idade da Diferença em 5 faixas (até 30 dias, 31 a 90, 91 a 365, 366 dias a 5 anos, mais de 5 anos), cada uma com Chaves e Diferença absoluta. A Idade é a quantidade de dias corridos entre o Aberta desde e a Data-base mais recente; Chaves "ou antes" ficam na faixa que a conta der. Ver spec: Solução, Decisões de implementação (Regras/Idade, Saída/Resumo); história 17.

**Blocked by:** 11

**Status:** done

- [x] Seam 1: as bordas caem na faixa certa: 30 → até 30; 31 → 31 a 90; 90 → 31 a 90; 91 → 91 a 365; 365 → 91 a 365; 366 → 366 a 5 anos; 1826 → 366 a 5 anos; 1827 → mais de 5 anos.
- [x] Seam 1: Diferença aberta na própria Data-base mais recente tem Idade 0 e cai em até 30.
- [x] Seam 1: a soma das Chaves e da Diferença absoluta das 5 faixas é igual a Chaves com Diferença e à Diferença absoluta do Resumo.
- [x] Resumo: as 5 faixas aparecem sempre (mesmo vazias), na ordem da spec, com Chaves e Diferença absoluta em reais, abaixo do quadro de totais e acima dos avisos.
- [x] O teste de ponta a ponta confere as faixas contra o gabarito do gerador de exemplo.
- [x] `C:\Users\josef\Projetos\Desafio-Conciliacao\.venv\Scripts\python -m pytest -q` passa.
- [x] Teste com olhos de usuário: rodar a CLI sobre o `exemplo\` de seis meses e conferir com openpyxl (`PYTHONIOENCODING=utf-8`) que as 5 faixas aparecem no Resumo e que os totais delas batem com Chaves com Diferença e Diferença absoluta.

**Notas de entrega:**

- `cruzamento`: `FAIXAS_DE_IDADE` (nome e teto em dias; a última sem teto) e `Resultado.por_idade`, uma tupla (Faixa, Chaves, Diferença absoluta em centavos) com as 5 faixas sempre, na ordem da spec. A Idade é `Data-base mais recente − Aberta desde` em dias corridos. As Chaves "ou antes" caem na faixa que a conta der.
- `excel`: no Resumo, uma linha abaixo do quadro, vem o cabeçalho "Idade da Diferença | Chaves | Diferença absoluta" e as 5 faixas (Chaves `#,##0`, Diferença absoluta em reais). Os avisos começam uma linha abaixo das faixas (atende à nota do ticket 06), e o gráfico continua por último.
- `exemplo`: `Gabarito.por_idade`, montado das Diferenças plantadas e do Aberta desde do gabarito, sem passar pelo cruzamento. No exemplo de seis meses: 1 / 1 / 138 / 0 / 0 Chaves.
- Testes: Seam 1 com as 8 bordas, a Idade 0, a soma das faixas igual a Chaves com Diferença e Diferença absoluta, e uma Chave "ou antes" com mais de 5 anos. Seam 2 confere as faixas contra o gabarito e a posição entre o quadro e os avisos. O helper `avisos_do_resumo` agora começa depois da última faixa.
- Olhos de usuário: CLI sobre `exemplo\`, conferida com openpyxl. As 5 faixas aparecem e somam 140 Chaves e R$ 312.219.067,84, iguais ao quadro. pytest: 109 passed.
- Arquivos: `conciliacao_enxuta/cruzamento.py`, `conciliacao_enxuta/excel.py`, `conciliacao_enxuta/exemplo.py`, `tests/test_cruzamento.py`, `tests/test_ponta_a_ponta.py`.

**Onde está agora (depois da entrega):**

O Resumo mostra a Idade da Diferença por faixa entre o quadro de totais e os avisos. Nada pendente.
