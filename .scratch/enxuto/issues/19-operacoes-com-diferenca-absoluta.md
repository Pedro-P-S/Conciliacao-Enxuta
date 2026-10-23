# 19: Operações com Diferença absoluta

**What to build:** na aba Operações com Diferença, a coluna Diferença vira **Diferença absoluta**, sem sinal; Valor A e Valor B continuam com o sinal, e a ordem continua pela Diferença absoluta, decrescente. Nada mais muda na aba. Ver spec: Decisões de implementação (Saída/Operações com Diferença); histórias 25 e 26.

**Blocked by:** —

**Status:** done

- [x] Aba `Operações com Diferença`: o cabeçalho diz `Diferença absoluta` no lugar de `Diferença`, na mesma posição, em reais e sem sinal.
- [x] Valor A e Valor B continuam com o sinal (uma Chave com Sinal invertido mostra um positivo e um negativo).
- [x] A ordem das linhas e o corte acima do limite não mudam.
- [x] O teste de ponta a ponta confere a coluna contra o gabarito.
- [x] `C:\Users\josef\Projetos\Conciliacao-Enxuta\.venv\Scripts\python -m pytest -q` passa.
- [x] Teste com olhos de usuário: rodar a CLI sobre `exemplo\` e conferir com openpyxl (`PYTHONIOENCODING=utf-8`) que a coluna Diferença absoluta não tem valores negativos e que a primeira linha é a maior.

**Notas de entrega:** a aba Operações com Diferença escreve `abs(Diferença)` sob o cabeçalho `Diferença absoluta`, na mesma coluna D e em reais; Valor A e Valor B seguem com o sinal. O Resultado (`cruzamento`) não mudou: já vinha ordenado pela Diferença absoluta, então ordem e corte ficam iguais. Seam testado: a CLI de ponta a ponta (`main(["conciliar", ...])` lido com openpyxl), contra o gabarito (`abs(d)`), mais a conferência de que as Chaves com Sinal invertido mostram um Valor positivo e um negativo; os testes de cabeçalho sem Atributos e de corte passaram a esperar `Diferença absoluta`. Olhos de usuário: `exemplo\` gerado com `python -m conciliacao_enxuta.exemplo`, CLI rodada; 140 linhas, nenhuma Diferença absoluta negativa, ordem decrescente com a maior na primeira linha, 46 linhas com Valor A ou B negativo. Arquivos: `conciliacao_enxuta/excel.py`, `tests/test_ponta_a_ponta.py`.

**Onde está agora (depois da entrega):** `_aba_operacoes` em `conciliacao_enxuta/excel.py`.
