# Review (code-review), segunda rodada: `git diff 6460da8...HEAD`

Commit: c8f3923 (correção do review). Escopo: só a correção dos Problemas críticos de `review-code-review.md` e `review.md` da primeira rodada (`7476ce5...6460da8`). Spec: `docs/spec.md` (Regras / Valor, Erros do arquivo inteiro, Tipos do `.parquet`) e os tickets 31 a 34. Padrões: `CLAUDE.md` e a linha de base de cheiros da skill. Os dois eixos foram feitos um depois do outro, sem subagentes. A suíte passa: 274 testes (em 241 s).

Os casos marcados "conferido" foram rodados num script fora do repositório, contra o código do HEAD e, para comparar, contra o de 6460da8.

## Standards

**Críticos da primeira rodada**

- **Ticket sem o "Onde está agora" (33 e 34): resolvido.** As duas seções estão preenchidas e apontam as funções e os testes certos.

**Problemas críticos**

Nenhum.

**Sugestões**

1. **Possível Duplicated Code: as regras de separador** (da primeira rodada, continua). `cli.tolerancia_em_centavos` refaz com `re` as regras que `leitura._centavos` faz em polars; as duas só dividem `MILHAR`. O limite `2**63 - 1` também aparece nos dois módulos.
2. **Possível Duplicated Code e Mysterious Name: `_do_arquivo`** (continua). `excel._do_arquivo(ws, linha, coluna, valor)` e `html._do_arquivo(texto)` têm o mesmo nome, assinaturas diferentes e a mesma regra (`ILLEGAL_CHARACTERS_RE.sub("", ...)`).
3. **Possível Primitive Obsession / Data Clumps: `quadro_do_resumo`** (continua). A tupla posicional `(rótulo, valor, formato, texto)` é lida pela metade em cada lado, com `_`.
4. **Dependência invertida** (continua). `leitura` importa `excel.reais` (`leitura → excel → cruzamento`); a função poderia morar num módulo neutro. `gui_estado.TOLERANCIA_PADRAO_EM_TEXTO` formata reais à mão.
5. **Frágil: depender do texto do erro do polars** (continua). `_ler_tabela` reconhece o campo a mais por `"more fields" in str(erro)`.
6. **Custo: a planilha é lida duas vezes** (continua, e agora pesa mais). `_topo_do_xlsx` (antes `_linhas_vazias_no_topo`) ainda carrega a folha inteira como texto, agora para as linhas vazias e para o cabeçalho cru. As duas coisas só precisam das primeiras linhas (`n_rows` no `load_sheet`).
7. **Possível Duplicated Code: o texto do número com o ponto trocado por vírgula.** Os dois ramos novos de `_centavos_de` (`decimal` e float) terminam iguais, `_centavos(<texto>.str.replace(".", ",", literal=True))`. Um ramo só, com o texto escolhido pelo tipo, deixaria isso num lugar.
8. **Pequenos** (continua, com um caso novo). Em `gui_estado.conciliar_pela_janela`, o `.strip()` depois de `_caminho_limpo` é redundante. Nas notas dos tickets 29, 33 e 36, os caminhos seguem quebrados pelo `\b` e pelo `\n` lidos como escape; a nota nova do ticket 31 repete o defeito: `exemplo\caso_reviewalor_repetido.xlsx` tem um tab vertical no lugar da barra seguida de `v` (conferido com `od -c`); o certo é `exemplo\caso_review\valor_repetido.xlsx`. A nota do ticket 29 ainda diz "Nada commitado".

## Spec

**Críticos da primeira rodada**

- **`Valor;Valor` num `.xlsx` não era coluna repetida: resolvido (conferido).** `ler_base` confere a repetição no cabeçalho cru da planilha (`_topo_do_xlsx`). Um `.xlsx` com `Chave, Data, Valor, Valor` dá `coluna repetida: Valor.`, também com linhas vazias no topo e com `Valor`/`valor`. `Data`/`DATA` segue dando erro. Um Atributo de verdade chamado `Valor_1` não é confundido, e o cabeçalho com célula vazia no meio continua lendo. Há caso novo em `ERROS_DO_ARQUIVO_INTEIRO`.
- **O `decimal` do `.parquet` arredondava duas vezes: resolvido (conferido).** O `decimal` do Valor não passa mais a `Float64`, e o seu texto exato vai a `_centavos`. `Decimal("0.0049999999")` dá 0, `Decimal("123456789012345.67")` dá 12345678901234567, `-10.005` dá -1001, escala 0 funciona, e a rejeitada pela Data mostra o Valor em reais (`1,50`). O float do `.xlsx`/`.parquet` também deixou o `round(6)`: `2.1249999999` dá 212; `1e16`, `1e-7` e `-0.0` saem certos; NaN, infinito e `1e300` seguem `Valor ilegível`.

**Problemas críticos**

1. **O Valor numérico ficou de 15 a 150 vezes mais lento (conferido).** É um problema novo da correção. Em `_centavos_de`, o float vira texto por um `map_batches` em Python, e o `_centavos` usa esse texto em muitos pontos da expressão (`limpo`, `negativo`, `numero`, `casas`, `digitos`...). O polars não junta a UDF repetida: o plano da expressão tem 150 `python_udf`, e a conversão de 0,35 s roda dezenas de vezes. Medido com 200 mil linhas de Valor float: o `.parquet` passou de 0,17 s para 25 s, e o `.xlsx` de 1,6 s para 27 s. O mesmo `.parquet` com o Valor em texto leva 1,5 s. A suíte passou a levar 4 minutos. A spec não dá um tempo, então o enquadramento como crítico é por julgamento, mas ela conta com esse volume: "um arquivo com seis meses de posições diárias" (história 9) e listas de até 700 mil linhas (história 32). O caso afetado é o mais comum, um `.xlsx` com o Valor numérico; com 700 mil linhas, seriam uns 90 s por base. A correção é calcular o texto uma vez só, como coluna, antes de passar a `_centavos` (por exemplo, trocar o Valor float por texto no `df` antes do `select`, ou fazer `_centavos` receber uma coluna já materializada). Falta também um teste que pegue isso, mas não precisa ser de tempo: basta a UDF rodar uma vez.

**Sugestões**

1. **Mensagem do `PermissionError`** (da primeira rodada, continua). Qualquer `PermissionError` ao gravar o `.xlsx` vira "feche o arquivo no Excel e tente de novo", inclusive uma pasta sem permissão de escrita.
2. **Falha no `.html` depois do `.xlsx`** (continua). Se o `.xlsx` grava e o `.html` falha, os dois ficam de execuções diferentes. A spec só cobre a falha do `.xlsx`.
3. **Um pouco além do pedido, sem prejuízo** (continua). O `26-01-31` e o `0.500,00` como ilegíveis, o `UInt64` do `.parquet` e o `ArquivoNaoGravado` também para a pasta que não existe.
4. **O float com ruído de fórmula agora segue o número guardado.** Com o `round(6)` fora, um float guardado como `1.0049999999999999` (que o Excel mostra como `1,005`) dá 100 centavos, e não 101; o mesmo vale para um `float32` do `.parquet` (`1.005` em `float32` dá 100). É o que a spec pede ("uma vez só") e o que o review anterior recomendou, então não é defeito. Fica registrado porque muda o resultado de quem tem Valores calculados por fórmula.

---

**Resumo:** Os 2 críticos de Spec e o 1 de Standards da primeira rodada estão resolvidos. Standards tem 0 problemas críticos e 8 sugestões; a pior é a planilha lida duas vezes inteira (sugestão 6). Spec tem 1 problema crítico novo e 4 sugestões; o pior é o Valor numérico 15 a 150 vezes mais lento, pela UDF repetida no plano do `_centavos`.
