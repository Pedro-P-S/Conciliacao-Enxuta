# Review: correção dos críticos (segunda rodada)

Revisado: `git diff 6460da8...HEAD` (commit `c8f3923`), contra `docs/spec.md` (Regras: Valor, Tipos do `.parquet`, Erros do arquivo inteiro), o `GRILL.md` 27 e os tickets 31 a 34. Conferidos os críticos de `review.md` (1 e 2) e de `review-code-review.md` (Standards 1; Spec 1 e 2). Carga assumida: uma pessoa rodando a ferramenta no próprio computador, com bases de até umas centenas de milhares de linhas. A suíte passa: 274 testes.

**O que esta mudança faz:** o Valor que já vem como número (`float` do `.xlsx`/`.parquet` e `decimal` do `.parquet`) passa a virar texto e a usar o mesmo `_centavos` do `.csv`, que arredonda uma vez só. No `.xlsx`, a coluna repetida passa a ser conferida no cabeçalho cru da planilha. Os tickets 33 e 34 ganham o "Onde está agora".

**Os críticos antigos:**

- `review.md` 1 / Spec 2 (Valor numérico arredondado duas vezes): **resolvido** para o `float` (`Float64`) e o `decimal`. Conferido: `2.1249999999` dá 212, `0.00499999999` dá 0, `Decimal("123456789012345.67")` dá 12345678901234567; NaN, infinito e `1e20` saem como `Valor ilegível`. Mas a correção criou os problemas 1 e 2 abaixo.
- `review.md` 2 / Spec 1 (`Valor` repetido no `.xlsx`): **resolvido**. Conferido: com linhas vazias no topo, o erro sai igual; um Atributo de verdade chamado `Valor_1` não é confundido; cabeçalho com célula vazia no meio e cabeçalho numérico funcionam.
- Standards 1 ("Onde está agora" vazio nos tickets 33 e 34): **resolvido**.

## Problemas críticos

1. **Ler um Valor numérico ficou mais de 100 vezes mais lento** (`conciliacao_enxuta/leitura.py:208-215`)
   - **O que é:** O `float` do Valor vira texto com um `map_batches`, que roda código Python linha a linha, e esse texto entra no `_centavos`.
   - **Problema:** O `_centavos` usa a expressão de entrada dezenas de vezes (`limpo`, `numero`, `casas`...), e o polars roda o `map_batches` de novo em cada uso. Medido num `.parquet` de 200 mil linhas com Valor `float`: o `ler_base` levava 0,23 s no `6460da8` e agora leva 32 s (20 mil linhas: 0,06 s → 4,8 s). Uma passada só da mesma conversão leva 0,4 s. O `.xlsx` sofre igual, porque a célula numérica chega como `Float64`.
   - **Correção:** Converter a coluna uma vez só, antes de montar as expressões: no `ler_base` (ou no `_tipo_lido`, se ele valer para os dois formatos), quando o Valor é `float`, trocar a coluna pelo texto (`df.with_columns(pl.Series("Valor", [...]))`), com o ponto já trocado por vírgula. Daí em diante ela segue o caminho do texto, e o `map_batches` sai.
   - **Se ficar:** Uma base `.xlsx` ou `.parquet` grande leva meio minuto para abrir, por base, e a janela parece travada.

2. **Valor `float32` do `.parquet` perde um centavo** (`conciliacao_enxuta/leitura.py:211-213`)
   - **O que é:** O texto do `float` sai de `repr(v)` depois do `s.to_list()`, que passa todo número a `float` de 64 bits do Python.
   - **Problema:** Um `float32` (`pl.Float32`) com `1.005` vira `1.0049999952316284` e dá 100 centavos. O texto mais curto do `float32` é `1.005`, que dá 101, como o mesmo `1,005` no `.csv`; o `6460da8` também dava 101. É o que a correção quis evitar: o mesmo número com centavos diferentes conforme o arquivo.
   - **Correção:** Na mesma conversão do item 1, partir do texto que o próprio polars dá ao número (`s.cast(pl.String)`, que já é o mais curto para `Float32` e `Float64`: `1.005`, `1e+16`) e só tirar a notação científica com `format(Decimal(t), "f")`. Um caso `Float32` no `test_valor_numerico_do_xlsx_e_do_parquet_e_arredondado_para_centavos_uma_vez_so`.
   - **Se ficar:** Quem exporta o `.parquet` com `float32` vê Diferenças de 1 centavo que não estão nos dados.

## Sugestões

### Should fix

3. **O `.xlsx` é lido duas vezes inteiro** (`conciliacao_enxuta/leitura.py:132-137`)
   - **O que é:** `_topo_do_xlsx` (antes `_linhas_vazias_no_topo`) carrega a planilha toda de novo, como texto, só para achar a primeira linha não vazia e o cabeçalho cru.
   - **Problema:** Medido na rodada anterior num `.xlsx` de 200 mil linhas: o `ler_base` levava 1,49 s, e 0,72 s disso era essa segunda leitura. A conta só precisa das primeiras linhas.
   - **Correção:** Passar `n_rows` ao `load_sheet` (por exemplo, 1.000 linhas) com um comentário `shortcut:` que diga o limite. O cabeçalho cru sai da mesma leitura curta.
   - **Se ficar:** Cada base `.xlsx` grande leva quase o dobro do tempo para abrir.

### Nice to have

4. **Data do gráfico de linha escrita em dois ramos** (`conciliacao_enxuta/html.py:146-155`)
   - **O que é:** Com uma Data-base só, o ramo `if len(historico) == 1` acrescenta a primeira data; o `elif historico` acrescenta a mesma linha e mais a última data. O rótulo do topo entra com `linhas.insert(4, ...)`, que depende da posição na lista.
   - **Problema:** Duas cópias da mesma linha para mudar juntas, e um índice que quebra em silêncio se a lista mudar.
   - **Correção:** Acrescentar a primeira data uma vez quando há histórico; o `<circle>` só com um ponto, a última data só com mais de um. Pôr o rótulo do topo na lista com `if maior`, sem o `insert`.
   - **Se ficar:** Nada quebra hoje; só fica mais difícil de ler e mudar.

5. **Caminhos quebrados nas notas dos tickets** (`.scratch/enxuto/issues/29-*.md`, `31-*.md`, `33-*.md`, `36-*.md`)
   - **O que é:** As notas citam os arquivos de exemplo usados no teste com olhos de usuário.
   - **Problema:** O `\b`, o `\n` e o `\v` dos caminhos foram gravados como caracteres de controle. Já estava assim nos tickets 29, 33 e 36 (`exemploase_a.csv`, `exemplo` seguido de quebra de linha e `ao_existe.csv`), e a nota nova do ticket 31 repete o erro: `exemplo\caso_review` + tabulação vertical + `alor_repetido.xlsx`, em vez de `exemplo\caso_review\valor_repetido.xlsx`. O "Onde está agora" dos tickets 33 e 34 já foi preenchido.
   - **Correção:** Corrigir os caminhos para `exemplo\base_a.csv`, `exemplo\nao_existe.csv`, `exemplo\caso_33\base_a.xlsx` e `exemplo\caso_review\valor_repetido.xlsx`.
   - **Se ficar:** Quem pega o próximo ticket não acha os arquivos de exemplo citados.

Verdict: fix 1 and 2 first.
Lean: -4 lines possible (o `map_batches` sai com a conversão única).
Not checked: o `.html` num navegador de verdade e a GUI com clique; o tempo do `.xlsx` de 200 mil linhas com a mudança (só o `.parquet` foi medido, e o `.xlsx` usa o mesmo caminho).
