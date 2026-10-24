# Review: tickets 29 a 37 (correções da auditoria)

Revisado: `git diff 7476ce5...HEAD` (commits `865864d` a `155409e`), contra `docs/spec.md`, `GRILL.md` (27 a 34) e os tickets 29 a 37. Carga assumida: uma pessoa rodando a ferramenta no próprio computador, com bases de até umas centenas de milhares de linhas. A suíte passa: 272 testes.

**O que esta mudança faz:** fecha os críticos da auditoria antiga. A leitura passa a recusar separadores ambíguos, Valores fora de `Int64`, datas com ano de 2 dígitos e tipos estranhos do `.parquet`, e os erros do arquivo inteiro viram mensagem simples. A CLI e a GUI passam por um pipeline só (`conciliar_arquivos`), que grava o `.xlsx` antes do `.html`. O `.html` passa a mostrar o mesmo que o Resumo do Excel.

## Problemas críticos

1. **Valor numérico de `.xlsx`/`.parquet` ainda arredonda duas vezes** (`conciliacao_enxuta/leitura.py:201-205` e `:174-175`)
   - **O que é:** O crítico 4 da auditoria antiga. Um Valor que já vem como número (célula numérica do `.xlsx`, `float` ou `decimal` do `.parquet`) vira centavos com `(Valor * 100).round(6).round(0)`. O `decimal` do `.parquet` passa antes a `Float64` (`_tipo_lido`).
   - **Problema:** O `round(6)` é um primeiro arredondamento, e o GRILL 27 e a spec (Regras, Valor) pedem "uma vez só". Conferido rodando `ler_base`: `2.1249999999` dá 213 centavos no `.xlsx`, no `.parquet` `float` e no `.parquet` `decimal`; o certo é 212. `0.00499999999` dá 1; o certo é 0. E o `decimal` passado a `float` perde centavos em silêncio: `Decimal("123456789012345.67")` vira 12345678901234568, e não 12345678901234567. O ticket 32 diz que "o caminho do float ficou como estava", e nenhum teste pega isso: o teste do texto (`test_valor_em_texto_e_arredondado_para_centavos_uma_vez_so`) só cobre o `.csv`.
   - **Correção:** Passar o número a texto e usar o mesmo `_centavos` do `.csv`, que já arredonda uma vez só pelos dígitos. O `decimal` vira texto exato com `cast(pl.String)`; o `float` vira o texto mais curto que o representa (`format(Decimal(repr(x)), "f")`: `1.005` fica `1.005`, e `2.1249999999` fica `2.1249999999`), sem notação `1e+16`. No `_tipo_lido`, o `decimal` do Valor deixa de virar `Float64`. NaN e infinito viram `NaN`/`Infinity`, que o `_centavos` já recusa. Um teste de leitura com `2.1249999999` (`.xlsx` e `.parquet`) dando 212, e `Decimal("123456789012345.67")` dando 12345678901234567.
   - **Se ficar:** O mesmo número dá centavos diferentes conforme o arquivo seja `.csv` ou `.xlsx`, e um `.parquet` de valores grandes em `decimal` soma centavos que não estão no arquivo.

2. **`Valor` repetido num `.xlsx` não para a execução** (`conciliacao_enxuta/leitura.py:235-239`)
   - **O que é:** A checagem de coluna repetida tira o sufixo `_duplicated_N`, que é como o polars renomeia um cabeçalho repetido do `.csv`.
   - **Problema:** No `.xlsx`, o polars (via fastexcel) renomeia o segundo `Valor` para `Valor_1`. Conferido: um `.xlsx` com cabeçalho `Chave, Data, Valor, Valor` é lido sem erro, e `Valor_1` vira um Atributo. A spec (Regras, Erros do arquivo inteiro) diz que uma das colunas fixas repetida para a execução com "coluna repetida", em qualquer formato. `Data` e `DATA` funcionam, porque o nome não muda; só o nome idêntico escapa. O teste de ponta a ponta só cobre `Valor;Valor` no `.csv`.
   - **Correção:** No `.xlsx`, conferir a repetição no cabeçalho cru da planilha, que o `_linhas_vazias_no_topo` já carrega (`header_row=None`): a primeira linha não vazia é o cabeçalho como o usuário escreveu. Assim nenhum Atributo de verdade chamado `Valor_1` é confundido. Mais um caso `.xlsx` no teste `test_erro_do_arquivo_inteiro_da_mensagem_simples_com_o_arquivo_na_cli_e_na_janela`.
   - **Se ficar:** Quem tem duas colunas `Valor` na planilha concilia com a primeira sem saber, e a segunda aparece como Atributo nas abas Por Atributo e Operações com Diferença.

## Sugestões

### Should fix

3. **O `.xlsx` é lido duas vezes inteiro** (`conciliacao_enxuta/leitura.py:131-134`)
   - **O que é:** `_linhas_vazias_no_topo` carrega a planilha toda de novo, como texto, só para contar as linhas vazias antes do cabeçalho.
   - **Problema:** Medido num `.xlsx` de 200 mil linhas: o `ler_base` leva 1,49 s, e 0,72 s disso é essa segunda leitura. A conta só precisa das primeiras linhas.
   - **Correção:** Passar `n_rows` ao `load_sheet` (por exemplo, 1.000 linhas) com um comentário `shortcut:` que diga o limite. A mesma leitura curta serve para o cabeçalho cru do item 2.
   - **Se ficar:** Cada base `.xlsx` grande leva quase o dobro do tempo para abrir.

### Nice to have

4. **Data do gráfico de linha escrita em dois ramos** (`conciliacao_enxuta/html.py:146-155`)
   - **O que é:** Com uma Data-base só, o ramo `if len(historico) == 1` acrescenta a primeira data; o `elif historico` acrescenta a mesma linha e mais a última data. O rótulo do topo entra com `linhas.insert(4, ...)`, que depende da posição na lista.
   - **Problema:** Duas cópias da mesma linha para mudar juntas, e um índice que quebra em silêncio se a lista mudar.
   - **Correção:** Acrescentar a primeira data uma vez quando há histórico; o `<circle>` só com um ponto, a última data só com mais de um. Pôr o rótulo do topo na lista com `if maior`, sem o `insert`.
   - **Se ficar:** Nada quebra hoje; só fica mais difícil de ler e mudar.

5. **Notas de entrega incompletas nos tickets** (`.scratch/enxuto/issues/33-*.md`, `34-*.md`, `29-*.md`, `36-*.md`)
   - **O que é:** O `CLAUDE.md` pede o "Onde está agora (depois da entrega)" preenchido na entrega.
   - **Problema:** Nos tickets 33 e 34 essa seção está vazia. Nos tickets 29, 33 e 36, os caminhos perderam a barra invertida (`exemploase_a.csv`, `exemplo` seguido de quebra de linha e `ao_existe.csv`): o `\b` e o `\n` foram lidos como caracteres de escape.
   - **Correção:** Preencher as duas seções e corrigir os caminhos para `exemplo\base_a.csv` e `exemplo\nao_existe.csv`.
   - **Se ficar:** Quem pega o próximo ticket não sabe onde o código ficou e não acha os arquivos de exemplo citados.

Verdict: fix 1 and 2 first.
Lean: -3 lines possible.
Not checked: o `.html` aberto num navegador de verdade, e a GUI com clique (só o `gui_estado` e o autoteste).
