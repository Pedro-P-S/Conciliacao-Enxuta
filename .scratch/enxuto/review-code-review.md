# Review (code-review), rodada final: `git diff bd242c3...HEAD`

Commit: c1431e0 (correção do segundo review). Escopo: só a correção dos dois Problemas críticos do float (a lentidão do Valor float, deste arquivo, e o `Float32` que perdia um centavo, do `review.md`). Spec: `docs/spec.md` (Regras / Valor) e o ticket 32. Padrões: `CLAUDE.md` e a linha de base de cheiros da skill. Os dois eixos foram feitos um depois do outro, sem subagentes. A suíte passa: 275 testes (em 172 s).

Os casos marcados "conferido" foram rodados num script fora do repositório, contra o código do HEAD.

## Standards

**Problemas críticos**

Nenhum.

**Sugestões**

1. **Possível Duplicated Code: as regras de separador** (continua). `cli.tolerancia_em_centavos` refaz com `re` as regras que `leitura._centavos` faz em polars; as duas só dividem `MILHAR`. O limite `2**63 - 1` também aparece nos dois módulos.
2. **Possível Duplicated Code e Mysterious Name: `_do_arquivo`** (continua). `excel._do_arquivo(ws, linha, coluna, valor)` e `html._do_arquivo(texto)` têm o mesmo nome, assinaturas diferentes e a mesma regra (`ILLEGAL_CHARACTERS_RE.sub("", ...)`).
3. **Possível Primitive Obsession / Data Clumps: `quadro_do_resumo`** (continua). A tupla posicional `(rótulo, valor, formato, texto)` é lida pela metade em cada lado, com `_`.
4. **Dependência invertida** (continua). `leitura` importa `excel.reais` (`leitura → excel → cruzamento`); a função poderia morar num módulo neutro. `gui_estado.TOLERANCIA_PADRAO_EM_TEXTO` formata reais à mão.
5. **Frágil: depender do texto do erro do polars** (continua). `_ler_tabela` reconhece o campo a mais por `"more fields" in str(erro)`.
6. **Custo: a planilha é lida duas vezes** (continua). `_topo_do_xlsx` carrega a folha inteira como texto para as linhas vazias e o cabeçalho cru; as duas coisas só precisam das primeiras linhas (`n_rows` no `load_sheet`).
7. **Possível Duplicated Code: o ponto trocado por vírgula** (continua, mudou de lugar). Agora está em `_valor_float_em_texto` (`.replace(".", ",")` em Python) e no ramo `decimal` de `_centavos_de` (`.str.replace(".", ",", literal=True)`). Os dois tipos poderiam virar texto no mesmo `_valor_float_em_texto` (que passaria a ser "Valor numérico em texto"), e o `_centavos_de` ficaria só com inteiro e texto.
8. **Teste de tempo na suíte.** `test_parquet_grande_com_valor_float_e_lido_em_poucos_segundos` mede relógio (`< 5 s`, hoje 1,5 s). Pega a regressão, mas pode falhar numa máquina carregada sem defeito no código. A alternativa que o review anterior sugeriu (conferir que a conversão roda uma vez só) não depende da máquina; com a conversão agora fora da expressão, o teste de tempo é aceitável.
9. **Pequenos** (continua). Em `gui_estado.conciliar_pela_janela`, o `.strip()` depois de `_caminho_limpo` é redundante. Nas notas dos tickets 29, 31, 33 e 36, caminhos seguem quebrados pelo `\b`, `\n` e `\v` lidos como escape (no 31, `exemplo\caso_reviewalor_repetido.xlsx`, o certo é `exemplo\caso_review\valor_repetido.xlsx`). A nota do ticket 29 ainda diz "Nada commitado".

## Spec

**Críticos da rodada anterior**

- **Valor numérico 15 a 150 vezes mais lento: resolvido (conferido).** `_valor_float_em_texto` troca a coluna Valor `float` por texto uma vez só, antes do `select`; não há mais UDF dentro do `_centavos`. Medido com 200 mil linhas: `.xlsx` com Valor numérico em 3,5 s (antes 27 s), `.parquet` em ~1,5 s (antes 25 s). A suíte voltou de 241 s para 172 s.
- **`Float32` perdia um centavo: resolvido (conferido).** O texto vem do `cast(pl.String)` do próprio tipo: `Float32` `1.005` dá 101, como `1,005` no `.csv`. Continuam certos, em `Float64` e `Float32`: `2.1249999999` → 212 (em `Float32`, que guarda `2.125`, 213), `1e16`, `1e-7` → 0, `-0.0` → 0, `-10.005` → -1001, `0.1 + 0.2` → 30. NaN, infinito e `1e300` seguem `Valor ilegível`, nulo segue `Valor vazio`. As rejeitadas mostram o Valor como veio (`NaN`, `inf`, `1e+300`), e a rejeitada pela Data mostra o Valor em reais (`1,50`).

**Problemas críticos**

Nenhum. A correção não criou problema novo.

**Sugestões**

1. **Mensagem do `PermissionError`** (continua). Qualquer `PermissionError` ao gravar o `.xlsx` vira "feche o arquivo no Excel e tente de novo", inclusive uma pasta sem permissão de escrita.
2. **Falha no `.html` depois do `.xlsx`** (continua). Se o `.xlsx` grava e o `.html` falha, os dois ficam de execuções diferentes. A spec só cobre a falha do `.xlsx`.
3. **Um pouco além do pedido, sem prejuízo** (continua). O `26-01-31` e o `0.500,00` como ilegíveis, o `UInt64` do `.parquet` e o `ArquivoNaoGravado` também para a pasta que não existe.
4. **O float com ruído de fórmula segue o número guardado** (continua, só para `Float64`). Um float guardado como `1.0049999999999999` (que o Excel mostra como `1,005`) dá 100 centavos, e não 101. É o que a spec pede ("uma vez só"), então não é defeito; fica registrado porque muda o resultado de quem tem Valores calculados por fórmula. O caso do `Float32` deixou de valer: agora dá 101.

---

**Resumo:** Os dois críticos do float estão resolvidos, sem problema novo. Standards tem 0 problemas críticos e 9 sugestões; a pior continua a planilha lida duas vezes inteira (sugestão 6). Spec tem 0 problemas críticos e 4 sugestões; a pior é a mensagem do `PermissionError` (sugestão 1).
