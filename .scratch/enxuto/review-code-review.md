# Review (code-review): `git diff 7476ce5...HEAD`

Commits: 865864d (spec), 6b0afc6 (tickets), 40e74a2 (29) a 155409e (37). Spec: `docs/spec.md`, bloco "Decisões de 24/10/2026: correções da auditoria" e os tickets 29 a 37. Padrões: `CLAUDE.md` e a linha de base de cheiros da skill. Os dois eixos foram feitos um depois do outro, sem subagentes. A suíte passa: 272 testes.

Os casos marcados "conferido" foram rodados num script fora do repositório, contra o código do HEAD.

## Standards

**Problemas críticos**

1. **Ticket sem o "Onde está agora".** O `CLAUDE.md` (Issue tracker) pede "`**Notas de entrega:**` e `**Onde está agora (depois da entrega):**`, preenchidos na entrega". Em `.scratch/enxuto/issues/33-data-parquet-e-linha-do-xlsx.md` e `34-atributo-com-nome-interno.md`, o "Onde está agora" está vazio, e os dois tickets estão `done`.

**Sugestões**

1. **Possível Duplicated Code: as regras de separador.** `cli.tolerancia_em_centavos` faz de novo, com `re` em Python, as regras que `leitura._centavos` faz em expressão do polars: com vírgula, `(\d*|MILHAR),\d*`; sem vírgula, `MILHAR` ou decimal; e por fim `\d+\.?\d*|\.\d+`. As duas só dividem a constante `MILHAR`. A spec diz que a Tolerância segue "as mesmas regras de separador do Valor". Hoje elas estão em dois lugares que podem divergir. O limite `2**63 - 1` também aparece nos dois módulos.
2. **Possível Duplicated Code e Mysterious Name: `_do_arquivo`.** `excel._do_arquivo(ws, linha, coluna, valor)` e `html._do_arquivo(texto)` têm o mesmo nome, assinaturas diferentes e a mesma regra (`ILLEGAL_CHARACTERS_RE.sub("", ...)`). Além disso, o nome não diz o que a função faz, que é limpar o texto e escapar.
3. **Possível Primitive Obsession / Data Clumps: `quadro_do_resumo`.** A função devolve uma tupla posicional `(rótulo, valor, formato, texto)`. Cada lado usa metade dela e ignora o resto com `_` (`for linha, (rotulo, valor, formato, _)` e `for rotulo, _, _, texto`). Uma tupla nomeada deixaria claro o que cada posição é.
4. **Dependência invertida.** `leitura` passou a importar `excel.reais`, então a leitura depende do módulo de saída (`leitura → excel → cruzamento`). A spec pede que os reais em texto saiam de uma função só, mas essa função poderia morar num módulo neutro. Com isso, a frase do `CLAUDE.md` "vira reais só no Excel" e o novo comentário "os únicos lugares onde os centavos viram reais" ficam menos verdadeiros, porque a leitura também gera reais em texto. Também ficou de fora do diff o `gui_estado.TOLERANCIA_PADRAO_EM_TEXTO`, que formata centavos em reais à mão.
5. **Frágil: depender do texto do erro do polars.** `_ler_tabela` reconhece o campo a mais por `"more fields" in str(erro)`. Se o polars mudar a frase, o caso cai em "o arquivo está corrompido". O teste de ponta a ponta pega isso, mas só ao atualizar o polars.
6. **Custo: a planilha é lida duas vezes.** `_linhas_vazias_no_topo` lê o `.xlsx` inteiro de novo, como texto, só para achar a primeira linha não vazia. Para um `.xlsx` grande, isso dobra a leitura. Bastariam as primeiras linhas.
7. **Pequenos.** Em `gui_estado.conciliar_pela_janela`, o `.strip()` depois de `_caminho_limpo` é redundante, e a linha da mensagem do `erros.log` passa de 120 colunas. Nas notas dos tickets 29, 33 e 36, os caminhos saíram quebrados (`exemploase_a.csv`, `exemplo\caso_33ase_a.xlsx`, `"exemplo⏎ao_existe.csv"`): o `\b` e o `\n` foram lidos como escape. A nota do ticket 29 diz "Nada commitado", e isso já não vale.

## Spec

**Problemas críticos**

1. **`Valor;Valor` num `.xlsx` não é coluna repetida (conferido).** A spec, em Regras / Erros do arquivo inteiro, diz: "sem `Chave`, `Data` ou `Valor`, ou com uma delas repetida (como `Data` e `DATA`, ou `Valor;Valor`), que a mensagem chama de coluna repetida". O `ler_base` só reconhece o sufixo que o polars põe no `.csv` (`_duplicated_N`). O `fastexcel` renomeia a segunda coluna para `Valor_1`. Resultado: um `.xlsx` com cabeçalho `Chave, Data, Valor, Valor` concilia sem erro, usa a primeira coluna e põe a segunda como um Atributo `Valor_1`. Faltam a correção e um caso `.xlsx` em `ERROS_DO_ARQUIVO_INTEIRO`. `Data` e `DATA` num `.xlsx` funcionam, porque os nomes não colidem.
2. **O `decimal` do `.parquet` arredonda duas vezes e perde precisão (conferido).** A spec diz, em Regras / Valor, "arredonda para centavos, com o meio para longe do zero, uma vez só", e em Tipos do `.parquet`, "o `decimal` é número". O `_tipo_lido` passa o `decimal` a `Float64`, e o `_centavos_de` faz `round(6)` e depois `round(0)`. Um `Decimal("0.0049999999")` dá 1 centavo, enquanto o mesmo texto `0,0049999999` dá 0. Um `Decimal("12345678901234567.89")` vira 1234567890123456768 centavos, e não 1234567890123456789. O `decimal` já é exato: daria para tirar os centavos dele sem passar por float.

**Sugestões**

1. **Mensagem do `PermissionError`.** O `conciliar_arquivos` traduz qualquer `PermissionError` ao gravar o `.xlsx` como "feche o arquivo no Excel e tente de novo". Uma pasta sem permissão de escrita recebe a mesma mensagem, que fica enganosa. A spec só pede uma mensagem simples, então isso não é um erro.
2. **Falha no `.html` depois do `.xlsx`.** Se o `.xlsx` grava e o `.html` falha, os dois ficam de execuções diferentes, que é justamente o que a história 53 quer evitar. A spec só cobre a falha do `.xlsx`, então fica como pergunta, não como defeito.
3. **Um pouco além do pedido, sem prejuízo.** O `26-01-31` e o `0.500,00` como ilegíveis, o `UInt64` do `.parquet` e o `ArquivoNaoGravado` também para a pasta que não existe. Todos seguem a letra das regras novas.
4. **Os tickets 29, 30, 31 e 34 a 37 conferem com a spec.** O `conciliar_arquivos` é o único caminho e grava o `.xlsx` antes do `.html`. `quadro_do_resumo`, `cortar`, `excel.reais` e `_soltas` são peças únicas. O Atributo `Peso`, `Absoluta` e `Atributo`, os dois testes de mutação, a Tolerância brasileira, o caminho colado, o `erros.log` que não grava, o percentual, o eixo com 0, o ponto único e o caractere de controle no `.html` estão feitos e testados. A Linha do `.xlsx` com linhas vazias no topo também (conferido com células só a partir da linha 3).

---

**Resumo:** Standards tem 1 problema crítico e 7 sugestões; o pior é o "Onde está agora" vazio nos tickets 33 e 34. Spec tem 2 problemas críticos e 4 sugestões; o pior é o `Valor;Valor` num `.xlsx`, que passa sem erro.
