# 32: Valor com separador ambíguo ou grande demais

**What to build:** na leitura, com vírgula, o ponto só separa grupos de 3 dígitos e o primeiro grupo não começa com zero (`1.234,56`); fora disso, o Valor é ilegível (`1,234.56`, `1.2.3,4`, `1.2,3`). Sem vírgula, o ponto é separador de milhar só nesse mesmo formato (`1.234` é R$ 1.234,00); senão é decimal (`0.125` é R$ 0,13, `00.500` é R$ 0,50). O arredondamento para centavos acontece uma vez só. Um Valor que não cabe em centavos `Int64`, de qualquer formato, inclusive um inteiro grande de um `.parquet`, é ilegível. Todos viram Linha rejeitada com o motivo `Valor ilegível`; nenhum para a execução. Ver spec: Regras (Valor), bloco "Decisões de 24/10/2026" (Valor e Data), Testes/Correções da auditoria (leitura); histórias 48 e 49.

**Blocked by:** 29

**Status:** done

- [x] Teste de leitura: `1,234.56`, `1.2.3,4` e `1.2,3` são `Valor ilegível`; `1.234` é 123400 centavos, `0.125` é 13, `00.500` é 50.
- [x] Teste de leitura: um Valor fora de `Int64` em texto e como inteiro de `.parquet` é `Valor ilegível`, sem parar a execução.
- [x] Os formatos já aceitos (número, `1.234,56`, `R$`, parênteses, menos, mais de 2 casas) continuam lidos como antes.
- [x] `C:\Users\josef\Projetos\Conciliacao-Enxuta\.venv\Scripts\python -m pytest -q` passa.
- [x] Teste com olhos de usuário: numa cópia de uma base de `exemplo\`, trocar alguns Valores por `1,234.56`, `1.2.3,4` e `99999999999999999999`, rodar a CLI e conferir que viram Linhas rejeitadas na aba Erros, com a Linha certa, e que o resto concilia.

**Notas de entrega:**
Seam: `ler_base` (a da leitura, como a spec manda; sem seam nova). Em `_centavos`, o ponto só é milhar em `[1-9]\d{0,2}(\.\d{3})+`; com vírgula, qualquer outro ponto torna o Valor ilegível. Os centavos saem dos dígitos do texto (a 3ª casa decide o arredondamento, uma vez só, sem passar por `Decimal(38,10)`, que arredondava antes: `0,00499999999999` dava 1). O inteiro de `.parquet` (inclusive `UInt64`) fora de centavos `Int64` vira nulo e sai como `Valor ilegível`, em vez de estourar em silêncio. O caminho do float (`.xlsx`/`.parquet`) ficou como estava: o `round(6)` tira o ruído do float (`1234.565`). Novos testes em `tests/test_leitura.py`: separadores ambíguos (`1,234.56`, `1.2.3,4`, `1.2,3`, `0.500,00`), ponto sem vírgula (`1.234`, `0.125`, `00.500`), Valor fora de `Int64` em texto e como inteiro de `.parquet` (`Int64` e `UInt64`), e o arredondamento uma vez só. Teste com olhos de usuário em `exemplo\caso_valor_32\`: as Linhas 3, 4 e 5 da Base A (`1,234.56`, `1.2.3,4`, `99999999999999999999`) saem na aba Erros como `Valor ilegível`, com a Linha certa, e o resto concilia. Arquivos: `conciliacao_enxuta/leitura.py`, `tests/test_leitura.py`.

Correção do review (crítico do Valor numérico): o caminho do float não ficou como estava. O `round(6)` era um primeiro arredondamento (`2.1249999999` dava 213). Agora o Valor numérico do `.xlsx`/`.parquet` vira texto e passa pelo mesmo `_centavos`, com o ponto trocado por vírgula: o float pelo texto mais curto que o representa (`format(Decimal(repr(x)), "f")`), o `decimal` pelo seu texto exato (o `_tipo_lido` não passa mais o `decimal` do Valor a `Float64`; o da Data, sim). NaN e infinito seguem `Valor ilegível`. Teste novo em `tests/test_leitura.py`: `test_valor_numerico_do_xlsx_e_do_parquet_e_arredondado_para_centavos_uma_vez_so` (`2.1249999999` → 212, `0.00499999999` → 0, `Decimal("0.0049999999")` → 0, `Decimal("123456789012345.67")` → 12345678901234567). Teste com olhos de usuário em `exemplo\caso_review\`: `base_a.xlsx` e `base_a.parquet` (`decimal`) contra `base_b.csv` (`2,12`, `0,00`, `1.234.567.890.123,45`) dão Diferença 0. Arquivos: `conciliacao_enxuta/leitura.py`, `tests/test_leitura.py`.

**Onde está agora (depois da entrega):**
`conciliacao_enxuta/leitura.py`, em `_centavos` (texto) e `_centavos_de` (inteiro); testes em `tests/test_leitura.py`.
