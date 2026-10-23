# Review: tickets 18 a 28 (`git diff 4fcfc5f...HEAD`)

**O que esta mudança faz:** As linhas sem Chave passam a entrar nos totais, na Diferença de cada Data-base, na Idade e no novo Tipo "Casa com linha sem Chave". A leitura não para mais numa linha ruim: ela vira Linha rejeitada e vai para a nova aba Erros, junto com as Data-bases ignoradas. O Resumo ganha os Atributos Problemáticos e o gráfico de barras da Idade, e sai também num `.html` com SVG.

Carga assumida: uma pessoa rodando a GUI ou a CLI na própria máquina, com até centenas de milhares de linhas. Os 198 testes passam.

## Problemas críticos

1. **Uma Data-base com só linhas sem Chave numa base é ignorada** (`conciliacao_enxuta/cruzamento.py`, em `conciliar`: `datas_a, datas_b = set(base_a["Data"]), set(base_b["Data"])`)
   - **O que é:** As Data-bases comuns, que decidem o que entra e qual é a mais recente, saem das bases depois da Preparação.
   - **Problema:** A Preparação já tirou as linhas sem Chave. Caso real, testado: a Base A tem só um lançamento manual de R$ 500,00 em 02/03 e a Base B tem a K1 em 02/03. O 02/03 sai como "Data-base só na Base B" na aba Erros, a mais recente vira 01/03 e os R$ 500,00 somem do Total A, da Diferença e do gráfico. Isso contradiz a spec ("Data-bases: entram só as comuns às duas bases") e a história 37. Se a base inteira for de linhas sem Chave, a execução para com `SemDataBaseComum`.
   - **Correção:** Tirar as datas das bases antes da Preparação: `datas_a, datas_b = set(base_a_lida["Data"]), set(base_b_lida["Data"])` (guardar a base recebida antes de reatribuir `base_a`). Uma linha muda, e mais um teste no Seam 1 com esse caso.
   - **Se ficar:** Num dia só com lançamentos manuais, o analista vê o dia como "só na Base B" e o valor manual não aparece em lugar nenhum.
   - **Feito:** Em `conciliar`, as Data-bases de cada base agora saem da base recebida, antes da Preparação (a linha `datas_a, datas_b = ...` subiu para antes de `_preparar`). Dois testes novos no Seam 1 (`tests/test_cruzamento.py`), vistos falhando antes da correção: `test_data_base_com_so_linhas_sem_chave_numa_base_e_comum_e_entra_nos_totais` (o caso do review) e `test_base_inteira_de_linhas_sem_chave_ainda_tem_data_base_comum` (antes parava com `SemDataBaseComum`). 200 testes passam. Conferido pela CLI em `exemplo\caso_sem_chave\`: Data-base mais recente 02/03/2026, Total A R$ 500,00, aba Erros vazia.

## Sugestões

### Should fix

2. **O `html.py` usa nomes privados do `excel.py` e copia os textos do Resumo** (`conciliacao_enxuta/html.py:9`, `:45-71`; `conciliacao_enxuta/excel.py:76-101`)
   - **O que é:** A spec pede que o HTML mostre o mesmo Resumo do Excel, "com os mesmos rótulos".
   - **Problema:** O `html.py` importa `_milhar`, `_rotulo_da_faixa` e `_aviso_de_corte` (o `_` diz "não use de fora"), e repete à mão os textos `Linhas rejeitadas: N (veja a aba Erros)`, `Linhas sem Chave, fora do cruzamento` e os quatro títulos da tabela de Atributos. Quem mudar um rótulo no Excel e esquecer o HTML deixa os dois diferentes, e só os testes de string pegam.
   - **Correção:** Tirar o `_` dos três nomes e passar a usar, nos dois arquivos, uma função pública no `excel.py` que devolve a lista de avisos (`avisos(resultado, limite) -> list[str]`) e uma constante com os títulos da tabela de Atributos. Sem módulo novo.
   - **Se ficar:** Com o tempo, o Resumo do `.html` e o do `.xlsx` passam a dizer coisas diferentes.

### Nice to have

3. **Valor em reais formatado em três lugares** (`conciliacao_enxuta/html.py:22-25`, `conciliacao_enxuta/excel.py:46-48`)
   - **O que é:** Centavos viram `1.234,56` no HTML e na coluna Linha sem Chave do Excel.
   - **Problema:** As duas fazem o mesmo `divmod` + `_milhar`, só muda o sinal (`-` e `−`). Mudar o formato pede duas mudanças.
   - **Correção:** Uma função `reais(centavos, sinal="-")` no `excel.py`, usada pelos dois.
   - **Se ficar:** Só mais umas linhas para manter.

4. **`_sem_chave` calculado duas vezes por base** (`conciliacao_enxuta/cruzamento.py`, no `return Resultado(...)`)
   - **O que é:** O Total A soma `_sem_chave(sem_chave_a, data_base).soma`, e logo abaixo `sem_chave_a=` chama a mesma função de novo (o mesmo para B).
   - **Problema:** Trabalho repetido e duas fontes para o mesmo número.
   - **Correção:** Calcular uma vez em variáveis (`sem_a = _sem_chave(...)`) e usar nos dois lugares.
   - **Se ficar:** Nada quebra; só leitura pior.

## Pontos pedidos pelo orquestrador

- **Imports com `_`:** ver item 2.
- **Tickets 20 e 22 editados por script:** os diffs dos arquivos de ticket mudam só o Status, os checkboxes e as Notas de entrega/Onde está agora. Nada fora do escopo.
- **Merges com conflito (`8dd2326`, `cb9d840`, `99f678b`, `234694a`):** o código final tem cada entrega dos tickets 18 a 28 (totais com linhas sem Chave, Diferença absoluta nas Operações, Casa com linha sem Chave, Por Atributo, Atributos Problemáticos, barras da Idade, Idade da linha sem Chave, aba Erros, regras de Valor e Atributo, Data-bases ignoradas na aba Erros fora do Resumo, HTML). 198 testes passam. Não achei nada perdido.
- **`conciliar` com as rejeitadas opcionais:** os dois chamadores (`cli.py` e `gui_estado.py`) passam as duas. O padrão `None` só poupa os testes do Seam 1. Não é um problema hoje.

**Veredito:** corrigir o 1 antes.
**Lean:** cerca de -10 linhas possíveis (itens 2 a 4).
**Não conferido:** o `.html` aberto num navegador de verdade (só li o SVG gerado).
