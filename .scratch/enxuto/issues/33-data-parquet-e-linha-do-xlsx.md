# 33: Data, tipos do `.parquet` e Linha do `.xlsx`

**What to build:** na leitura, a Data tem ano de 4 dígitos (`31/01/26` é `Data ilegível`) e uma data do Excel acima de 2958465 (31/12/9999) é `Data ilegível`. Num `.parquet`, um Valor ou uma Data de um tipo que não é número, texto nem data (ex.: `bool`, `time`) é ilegível; o `decimal` é número; uma coluna `categorical` é lida pelo seu texto; uma coluna só com nulos é vazia. Nenhum desses para a execução. A Linha de uma Linha rejeitada de um `.xlsx` é a linha da planilha, contando as linhas vazias antes do cabeçalho. Ver spec: Regras (Linha rejeitada, Data, Tipos do `.parquet`), bloco "Decisões de 24/10/2026" (Valor e Data, Linha no `.xlsx`), Testes/Correções da auditoria (leitura); histórias 50, 51 e 57.

**Blocked by:** 32

**Status:** done

- [x] Teste de leitura: `31/01/26` é `Data ilegível`; a data do Excel 2958466 é `Data ilegível` e 2958465 é lida.
- [x] Teste de leitura de `.parquet`: coluna `decimal` lida como número; `bool` e `time` como ilegível; `categorical` pelo texto; coluna só com nulos como vazia. Nenhum para a execução.
- [x] Teste de leitura: num `.xlsx` com linhas vazias antes do cabeçalho, a Linha da Linha rejeitada é a da planilha.
- [x] `C:\Users\josef\Projetos\Conciliacao-Enxuta\.venv\Scripts\python -m pytest -q` passa.
- [x] Teste com olhos de usuário: numa cópia `.xlsx` de uma base de `exemplo\`, inserir duas linhas vazias antes do cabeçalho e uma Data `31/01/26`, rodar a CLI e conferir na aba Erros que a Linha aponta para a linha certa da planilha.

**Notas de entrega:**

- Seam: `ler_base` (a leitura), como a spec manda ("a leitura para Valor, Data e `.parquet`"); sem seam nova.
- Data: o texto só é lido em `DD/MM/AAAA`, `AAAA-...` ou só dígitos, então o ano tem 4 dígitos (`31/01/26` e `26-01-31` são `Data ilegível`); a data do Excel acima de 2958465 é `Data ilegível` (2958465 = 31/12/9999 é lida).
- `.parquet`: `_tipo_lido` passa o `decimal` a número e o `categorical`/`enum` e a coluna só com nulos a texto; um Valor ou uma Data de outro tipo (`bool`, `time`) vira ilegível, sem parar a execução.
- `.xlsx`: `_linhas_vazias_no_topo` conta, pelo `fastexcel`, as linhas vazias antes do cabeçalho, e a Linha rejeitada soma esse número (é a linha da planilha).
- Testes novos em `tests/test_leitura.py`: `31/01/26`, `26-01-31` e `2958466` em `test_data_ilegivel_nao_some_em_silencio`; `test_a_ultima_data_do_excel_e_31_12_9999`; `test_valor_e_data_de_tipos_do_parquet_sao_lidos_ou_viram_linha_rejeitada`; `test_a_linha_rejeitada_do_xlsx_conta_as_linhas_vazias_antes_do_cabecalho`.
- Teste com olhos de usuário: `exemplo\caso_33ase_a.xlsx` (a `base_a.csv` com duas linhas vazias antes do cabeçalho e `31/01/26` na linha 10 da planilha) contra a `base_b.csv`, pela CLI: na aba Erros, `Base A, 10, C00008, 31/01/26, Data ilegível`.
- Arquivos alterados: `conciliacao_enxuta/leitura.py`, `tests/test_leitura.py`.

**Onde está agora (depois da entrega):**
