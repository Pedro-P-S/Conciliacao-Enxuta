# Review, segunda rodada: tickets 18 a 28 (`git diff 4fcfc5f...HEAD`)

**O que esta mudança faz:** As linhas sem Chave passam a entrar nos totais, na Diferença de cada Data-base, na Idade e no novo Tipo "Casa com linha sem Chave". A leitura não para mais numa linha ruim: ela vira Linha rejeitada e vai para a nova aba Erros, junto com as Data-bases ignoradas. O Resumo ganha os Atributos Problemáticos e o gráfico de barras da Idade, e sai também num `.html` com SVG.

Carga assumida: uma pessoa rodando a GUI ou a CLI na própria máquina, com até centenas de milhares de linhas. Os 200 testes passam.

**Correção da rodada anterior conferida.** O antigo crítico 1 (Data-base com só linhas sem Chave numa base era ignorada) está resolvido: em `conciliar`, `datas_a, datas_b` agora saem da base recebida, antes de `_preparar`. Os dois testes novos do Seam 1 cobrem o caso do review e a base inteira sem Chave. Conferi que a mudança não quebra nada depois: a Data-base nova entra em `comuns`, no Histórico, no Casa e na Idade como as outras, e uma Data-base só com linhas sem Chave que existe só numa base vai, corretamente, para a aba Erros.

## Problemas críticos

1. **Um Valor numérico NaN, infinito ou enorme para a execução inteira** (`conciliacao_enxuta/leitura.py`, `_centavos_de`, ramo `tipo.is_numeric()`: `... .round(0, mode="half_away_from_zero").cast(pl.Int64)`)
   - **O que é:** É aqui que um Valor numérico do `.xlsx` ou do `.parquet` vira centavos.
   - **Problema:** O `cast(pl.Int64)` é estrito. Testado: um `.parquet` com `Valor` float e uma linha com `NaN` (ou `inf`, ou `1e30`) dá `InvalidOperationError` do polars. Na CLI sai um traceback; na GUI, "Algo deu errado". O ticket 25 e a spec dizem que só param a execução os erros do arquivo inteiro; um Valor ilegível deveria virar Linha rejeitada.
   - **Correção:** No ramo numérico, só converter o que é finito e não ser estrito: `pl.when(pl.col("Valor").is_finite()).then((pl.col("Valor") * 100).round(6).round(0, mode="half_away_from_zero")).cast(pl.Int64, strict=False)`. O Valor nulo cai no Motivo já existente (`NaN` vira texto `"NaN"`, então sai como `Valor ilegível`). Um teste de leitura com um `.parquet` com `NaN` e `inf`.
   - **Se ficar:** Uma base com um único NaN (comum em arquivos gerados por script) não concilia, e o analista não sabe qual linha é.

## Sugestões

### Should fix

2. **Texto que começa com `=` vira fórmula na aba Erros** (`conciliacao_enxuta/excel.py`, `_aba_erros`: `ws.cell(linha, coluna, valor)`)
   - **O que é:** A aba Erros mostra a Chave, a Data e o Valor "como vieram", em texto.
   - **Problema:** O openpyxl grava como fórmula todo texto que começa com `=`. Testado: um `.csv` com Valor `=SOMA(A1:A2)` é rejeitado como `Valor ilegível` (certo), mas a célula E2 da aba Erros sai com `data_type == "f"`. O Excel mostra `#NOME?` ou outro valor no lugar do texto que veio, e é justamente esse texto que o analista precisa ver.
   - **Correção:** Na aba Erros, marcar a célula como texto depois de gravar: `celula = ws.cell(linha, coluna, valor)` e `if isinstance(valor, str): celula.data_type = "s"`. Duas linhas. A Chave e os Atributos da aba Operações têm o mesmo risco, mas isso já existia antes desta mudança.
   - **Se ficar:** Uma linha rejeitada aparece na aba Erros com um valor que não é o do arquivo.

3. **O `html.py` usa nomes privados do `excel.py` e copia os textos do Resumo** (`conciliacao_enxuta/html.py:9`, `:45-71`; `conciliacao_enxuta/excel.py`, avisos e `_tabela_por_atributo`)
   - **O que é:** A spec pede que o HTML mostre o mesmo Resumo do Excel, "com os mesmos rótulos".
   - **Problema:** O `html.py` importa `_milhar`, `_rotulo_da_faixa` e `_aviso_de_corte` (o `_` diz "não use de fora"), e repete à mão os textos `Linhas rejeitadas: N (veja a aba Erros)`, `Linhas sem Chave, fora do cruzamento` e os quatro títulos da tabela de Atributos. Quem mudar um rótulo no Excel e esquecer o HTML deixa os dois diferentes, e só os testes de string pegam.
   - **Correção:** Tirar o `_` dos três nomes e passar a usar, nos dois arquivos, uma função pública no `excel.py` que devolve a lista de avisos (`avisos(resultado, limite) -> list[str]`) e uma constante com os títulos da tabela de Atributos. Sem módulo novo.
   - **Se ficar:** Com o tempo, o Resumo do `.html` e o do `.xlsx` passam a dizer coisas diferentes.

### Nice to have

4. **Valor em reais formatado em dois lugares** (`conciliacao_enxuta/html.py`, `_reais`; `conciliacao_enxuta/excel.py`, `_linha_sem_chave`)
   - **O que é:** Centavos viram `1.234,56` no HTML e na coluna Linha sem Chave do Excel.
   - **Problema:** As duas fazem o mesmo `divmod` + `_milhar`, só muda o sinal (`-` e `−`). Mudar o formato pede duas mudanças.
   - **Correção:** Uma função `reais(centavos, sinal="-")` no `excel.py`, usada pelos dois.
   - **Se ficar:** Só mais umas linhas para manter.

5. **`_sem_chave` calculado duas vezes por base** (`conciliacao_enxuta/cruzamento.py`, no `return Resultado(...)`)
   - **O que é:** O Total A soma `_sem_chave(sem_chave_a, data_base).soma`, e logo abaixo `sem_chave_a=` chama a mesma função de novo (o mesmo para B).
   - **Problema:** Trabalho repetido e duas fontes para o mesmo número.
   - **Correção:** Calcular uma vez em variáveis (`sem_a = _sem_chave(...)`) e usar nos dois lugares.
   - **Se ficar:** Nada quebra; só leitura pior.

**Veredito:** corrigir o 1 antes.
**Lean:** cerca de -10 linhas possíveis (itens 3 a 5).
**Não conferido:** o `.html` aberto num navegador de verdade (só li o SVG gerado).
