# 11: Aberta desde

**What to build:** o analista vê há quanto tempo cada Diferença está aberta. Para cada Chave com Diferença na Data-base mais recente, o Aberta desde é a primeira Data-base da sequência contínua de Diferença (|Diferença| > Tolerância, nas Data-bases comuns) que chega até a mais recente: se a Diferença some e volta, vale a data da volta; se só muda de valor, a data não muda. Quando a sequência começa na primeira Data-base do arquivo, aparece "DD/MM/AAAA ou antes", e o Resumo avisa quantas Chaves estão assim. A coluna Aberta desde entra nas Operações com Diferença, depois de Tipo do Erro. Ver spec: Decisões de implementação (Regras/Aberta desde, Saída/Resumo — avisos, Saída/Operações com Diferença); histórias 18, 28, 29 e 30.

**Blocked by:** 09

**Status:** done

- [x] Seam 1: Diferença que some numa Data-base e volta depois tem Aberta desde = data da volta.
- [x] Seam 1: Diferença que só muda de valor entre Data-bases mantém o Aberta desde original.
- [x] Seam 1: Diferença que cai para dentro da Tolerância numa Data-base conta como sumida.
- [x] Seam 1: Diferença presente desde a primeira Data-base é marcada como "ou antes".
- [x] Operações com Diferença: a coluna Aberta desde mostra `DD/MM/AAAA` ou `DD/MM/AAAA ou antes`.
- [x] Resumo: o aviso de Chaves abertas desde a primeira Data-base aparece só quando há alguma, com a quantidade, e é o primeiro da lista de avisos (ordem da spec: Aberta desde a primeira Data-base, linhas sem Chave, Data-bases ignoradas, corte).
- [x] O gerador de exemplo planta Chaves que somem e voltam, que mudam de valor e que já existem na primeira Data-base; o teste de ponta a ponta confere o Aberta desde e o aviso contra o gabarito.
- [x] `C:\Users\josef\Projetos\Desafio-Conciliacao\.venv\Scripts\python -m pytest -q` passa.
- [x] Teste com olhos de usuário: rodar a CLI sobre o `exemplo\` de seis meses e conferir com openpyxl (`PYTHONIOENCODING=utf-8`) o Aberta desde das Chaves plantadas (some e volta, muda de valor, "ou antes") e o aviso no Resumo.

**Notas de entrega:**

- `conciliacao_enxuta/cruzamento.py`: `Resultado.operacoes` ganhou as colunas `Desde` (o Aberta desde, data) e `OuAntes` (bool), e o `Resultado` ganhou `abertas_desde_a_primeira`. `_aberta_desde` acha, para cada Chave com Diferença na mais recente, a primeira Data-base da sequência contínua de Data-bases comuns com |Diferença| > Tolerância que chega até a mais recente. Ficar dentro da Tolerância ou ausente das duas bases numa Data-base quebra a sequência; mudar de valor não. "Ou antes" vale quando a sequência começa na primeira Data-base **comum** (a primeira que entra no cruzamento; antes dela não há como ter Diferença).
- `conciliacao_enxuta/excel.py`: a coluna Aberta desde (F) vem depois de Tipo do Erro, e o filtro vai até F. A célula é data, para ordenar e filtrar no Excel. O formato `DD/MM/YYYY` ou `DD/MM/YYYY" ou antes"` faz o Excel mostrar `DD/MM/AAAA` ou `DD/MM/AAAA ou antes`. O "ou antes" fica só na aparência: o filtro do Excel não o separa. No Resumo, o primeiro aviso, só quando há alguma Chave assim, diz "Chaves com Diferença desde a primeira Data-base (DD/MM/AAAA) ou antes: N. A Diferença delas pode ser ainda mais antiga."
- `conciliacao_enxuta/exemplo.py`: `PAUSAS` planta C00021, que some em 15/06 e volta (Aberta desde 16/06/2026); C00031, que cai para dentro da Tolerância em 29/09 (30/09/2026); e C00051, que só abre em 03/08/2026. As outras Chaves com Diferença mudam de valor a cada dia e vêm "ou antes". O sorteio continua o mesmo. O `Gabarito` ganhou `aberta_desde` e `abertas_desde_a_primeira`, calculados a partir das Diferenças plantadas.
- Testes: `tests/test_cruzamento.py` cobre some e volta (por A = B e por ausência das duas), muda de valor, cai na Tolerância, "ou antes" com uma Data-base só numa base e com uma Data-base só. `tests/test_ponta_a_ponta.py` cobre a coluna e o filtro, o Aberta desde mostrado contra o gabarito, o aviso em primeiro e a ausência do aviso.
- Olhos de usuário: no `exemplo\`, C00021 mostra 16/06/2026, C00031 mostra 30/09/2026, C00051 mostra 03/08/2026 e C00001 mostra 01/04/2026 ou antes (57 de 60 Chaves). O aviso de 57 é o primeiro do Resumo, antes das linhas sem Chave e das Data-bases ignoradas.
- O code review não achou violação dura nem scope creep.

**Onde está agora (depois da entrega):** o Aberta desde está nas Operações e no Resumo. O ticket 12 (Idade) pode usar `operacoes["Desde"]`. O ticket 13 (Atributos) acrescenta colunas depois de F em `_aba_operacoes`. Os testes do Resumo que leem avisos ancoram no rótulo "Chaves com Diferença". As faixas de Idade do ticket 12 entram entre o quadro e os avisos e vão precisar ajustar `avisos_do_resumo`. Sem commit.
