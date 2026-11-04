# Grill do projeto enxuto

Registro das decisões. O glossário fica em `CONTEXT.md`. Quando uma decisão muda, a antiga sai daqui.

## Entrada

1. **Sem mapeamento de colunas.** O usuário escolhe só os dois arquivos. As colunas `Chave` e `Data` têm nome fixo, e as de valor seguem a convenção da decisão 35; o resto é Atributo.
2. **Várias Data-bases no mesmo arquivo** (ex.: dias úteis de 6 meses, sem precisar ter todos os dias).
3. **Tolerância:** diferença de até R$ 1,00 (padrão, o usuário pode mudar) conta como zero.

## O que a ferramenta faz

4. **Núcleo:** cruzar pela Chave, dar o Tipo do Erro, mostrar os valores de Atributo com Diferença acima do peso e acompanhar a Diferença no tempo. Ficam fora: Aging, Justificativas, Pareto, Compensação Oculta, Bases Auxiliares, dashboard HTML (o Resumo em HTML é a exceção, ver 23 e 41).
5. **Tipo do Erro lista todos os que se aplicam** (sem prioridade): Só em A, Só em B, Sinal invertido, Duplicado, Vírgula deslocada, Dígitos trocados, Casa com linha sem Chave, Sem padrão. Cortados: Valor Fixo, Percentual Constante, Ponta Zerada, Arredondamento (a Tolerância já zera).
6. **Aberta desde = última abertura.** Se a Diferença some e volta, vale a data da volta. Se só muda de valor sem sumir, mantém a data original.

## Saída: um Excel com 5 abas e o Resumo em HTML

7. **Resumo:** os totais da Data-base mais recente (Total A, Total B, Diferença total, Diferença absoluta, Chaves com Diferença, Tolerância), os avisos, os Atributos Problemáticos, um gráfico de barras da Idade da Diferença e um gráfico de linha da Diferença absoluta por Data-base. Sem tabela do histórico nem da Idade.
8. **Por Tipo do Erro:** uma linha por Tipo, com quantidade de Chaves e Diferença absoluta.
9. **Por Atributo:** colunas Atributo, Valor, Diferença absoluta e Diferença acima do peso (% da Diferença absoluta − % do Total). Ordenada pela Diferença acima do peso, da maior para a menor; só entram os valores com Diferença acima do peso > 0. Sem filtro.
10. **Operações com Diferença:** só a Data-base mais recente, uma linha por Chave com Diferença, ordenada pela maior Diferença absoluta. Colunas: Chave, Valor A, Valor B, Diferença absoluta, Tipo do Erro, Aberta desde, Linha sem Chave, todos os Atributos. Limite de 700 mil linhas; se cortar, um aviso na própria aba diz que nem todas couberam.
11. **Atributos Problemáticos no Resumo:** as 5 primeiras linhas da aba Por Atributo, misturando Atributos, com as mesmas colunas.
12. **Idade da Diferença por faixa vira gráfico de barras** no Resumo: até 30 dias, 31 a 90, 91 a 365, 366 dias a 5 anos, mais de 5 anos. A barra é a Diferença absoluta da faixa, com as linhas sem Chave; a quantidade de Chaves e de linhas sem Chave vai no rótulo. Idade = dias corridos entre Aberta desde e a Data-base mais recente.
13. **Diferença já presente na primeira Data-base:** o Aberta desde mostra "DD/MM/AAAA ou antes". Fica na faixa que a conta der.
14. **Aba Erros:** uma linha por Linha rejeitada, de todas as Data-bases (Base, Linha, Chave e Data como vieram no arquivo, o Valor em reais quando foi lido e como veio quando não, Motivo), e uma linha por Data-base ignorada com a Data e o motivo (ex.: 01/10/2026, "Data-base só na Base B"). Mesmo limite e mesmo aviso de corte das Operações.
15. **O Resumo avisa as Linhas rejeitadas** numa linha, "Linhas rejeitadas: N (veja a aba Erros)", só quando houver. As Data-bases ignoradas saem do Resumo e vão para a aba Erros.

## Bordas

16. **Atributo diferente entre A e B:** vale o de A; se A não tiver a coluna ou o valor, vale o de B. O Atributo aceita qualquer conteúdo (número, letra, símbolo) e nunca derruba a execução.
17. **Data-base só numa base:** entram só as Data-bases que existem nas duas; as ignoradas vão para a aba Erros.
18. **Chave repetida na mesma Data-base:** soma os valores.
19. **Linha sem Chave** (ex.: lançamento manual): fica fora do cruzamento pela Chave, mas entra nos totais, no gráfico e na Diferença da sua Data-base com o valor inteiro, em qualquer Data-base comum. Também tem Idade: o mesmo valor repetido nas Data-bases seguintes é o mesmo lançamento, e a Idade conta desde a primeira Data-base em que ele aparece sem sumir. O Resumo avisa quantas são e quanto somam. Não aparece na aba de operações, nem agrupada.
20. **Números no formato brasileiro aceitos; nomes de coluna sem diferença de maiúscula e acento.**
21. **A Tolerância vale também para Só em A / Só em B.**
22. **Casa com linha sem Chave:** uma linha sem Chave que zeraria a Diferença de uma Chave é um Tipo do Erro. Compara uma vez só, na primeira Data-base em que o valor aparece (o dia do lançamento; depois a Diferença muda e o lançamento se repete). Só uma linha para uma Chave. A coluna Linha sem Chave mostra o valor, a data e a base, para o analista achar e conferir. A linha não é juntada à Chave: o erro continua na Chave.
23. **Resumo em HTML:** além do Excel, sai `conciliacao_AAAA-MM-DD.html` ao lado do `.xlsx`, com o mesmo conteúdo da aba Resumo, os gráficos incluídos. Abre sem internet. O Excel continua com a aba Resumo.
24. **Data vazia ou ilegível:** a linha é rejeitada (sem Data-base, não há onde somar) e vai para a aba Erros. A execução segue.
25. **Valor:** aceita número com qualquer número de casas; mais de 2 casas é arredondado para centavos. Texto ou caractere estranho (ex.: `abc`, `#`) rejeita a linha. Valor vazio também fica fora de tudo e aparece na aba Erros. Continuam aceitos o formato brasileiro, `R$`, parênteses e sinal.
26. **Linha toda vazia** (sem Chave, Data e Valor) é ignorada em silêncio, como as linhas em branco no fim de uma planilha.

## Correções da auditoria (24/10/2026)

27. **Separadores do Valor:** com vírgula, o ponto só separa grupos de 3 dígitos e o primeiro grupo não começa com zero (`1.234,56`); fora disso, Valor ilegível (`1,234.56`, `1.2.3,4`, `1.2,3`). Sem vírgula, o ponto é milhar só nesse mesmo formato; senão é decimal (`0.125` é R$ 0,13, `00.500` é R$ 0,50). Um Valor que não cabe em centavos `Int64`, de qualquer formato, é ilegível. O arredondamento para centavos é feito uma vez só.
28. **Data:** o ano tem 4 dígitos (`31/01/26` é Data ilegível). Uma data do Excel acima de 2958465 (31/12/9999) é Data ilegível. Valor ou Data de um tipo que não é número, texto nem data (ex.: `bool`, `time` num `.parquet`) é ilegível; o `decimal` é número. Nenhum desses para a execução.
29. **Erros do arquivo inteiro** (arquivo que não existe ou não abre, vazio, corrompido, com campo a mais, numa codificação que não é UTF-8 nem cp1252, ou com `Chave`, `Data` ou `Valor` repetida, como `Data` e `DATA`) param a execução com uma mensagem simples que diz o arquivo, na CLI e na GUI, sem traceback. A pasta de saída que não existe também. Um erro inesperado na CLI sai sem traceback na tela.
30. **Gravação:** o `.xlsx` é gravado antes do `.html`. Se o `.xlsx` não pode ser gravado (aberto no Excel), nenhum dos dois muda.
31. **GUI:** o caminho colado com espaço nas pontas ou entre aspas (o "Copiar como caminho" do Windows) é aceito. Se o `erros.log` não pode ser gravado, a mensagem simples aparece mesmo assim, e o resultado anterior sai da tela.
32. **Tolerância:** lida no formato brasileiro, como o Valor (`1.000` é R$ 1.000,00). Uma Tolerância que não vira número, ou grande demais, dá uma mensagem simples. O arredondamento dela é o do Valor, com o meio para longe do zero (decidido em 28/10/2026).
33. **Linha da Linha rejeitada no `.xlsx`:** a do arquivo, contando as linhas vazias antes do cabeçalho.
34. **HTML igual ao Excel:** o percentual arredonda como no Excel; o eixo do gráfico mostra 0 quando não há Diferença; com uma Data-base só, o gráfico de linha mostra o ponto e a data uma vez; o caractere de controle sai do texto, como no Excel.

## Vários batimentos (27/10/2026)

35. **Coluna de valor:** `Valor` + espaço ou `_` + nome (ex.: `Valor Juros`, `Valor_Juros`) é um Batimento, com o nome que vem depois (`Juros`). O nome é comparado sem maiúscula, acento e espaço nas pontas, como as outras colunas. O `Valor` puro também é um Batimento, chamado `Valor`, e deixa de ser obrigatório: basta uma coluna de valor. Sem nenhuma, a mensagem continua dizendo que falta a coluna Valor.
36. **Coluna de valor só numa base:** não vira Batimento; a CLI e a GUI avisam ("Valor Juros só na Base A: não conciliado") e a execução segue. Sem nenhum Batimento nas duas bases, para com uma mensagem simples.
37. **Cada Batimento é uma conciliação inteira**, com as regras de hoje e a mesma Tolerância. Nele, nenhuma outra coluna de valor vira Atributo. As linhas sem Chave entram com o valor daquele Batimento. O Valor vazio ou ilegível rejeita a linha só no seu Batimento; a Data vazia ou ilegível rejeita em todos.
38. **Ordem dos Batimentos:** a das colunas de valor na Base A.
39. **Um `.xlsx` e um `.html` para todos os Batimentos**, com o nome de hoje. A Data-base mais recente é uma só, a maior comum. Se todas as linhas de uma data caem pelo Valor num Batimento, a Diferença dele nessa data é zero, sem tratamento especial.
40. **Excel:** as abas Por Tipo do Erro, Por Atributo, Operações com Diferença e Erros ganham a coluna `Batimento` na frente, e o filtro do cabeçalho filtra por ela. As linhas vêm por Batimento e depois na ordem de hoje. O limite de 700 mil é da aba inteira; se cortar, ficam as maiores de todos os Batimentos. Na aba Erros, a linha rejeitada pela Data e a Data-base ignorada aparecem uma vez, com `Batimento` = `Todos`. O Resumo tem uma lista suspensa no topo com os Batimentos; o quadro, os avisos, os Atributos Problemáticos e os gráficos seguem a escolha por fórmula, sem macro. Sem "Todos" no Resumo; abre no primeiro Batimento.
41. **HTML:** uma lista suspensa no topo, e um JavaScript pequeno mostra o Resumo do Batimento escolhido. Os Resumos já vêm prontos no arquivo; sem JavaScript, aparece o primeiro. Continua um arquivo só, que abre sem internet e sem biblioteca. Sem "Todos". O visual fica mais bonito e simples, com um tema só, seguindo a skill `dataviz`.


## HTML pelas aulas do Módulo 3 (04/11/2026)

42. **Uma frase-resposta no topo do HTML**, antes do quadro: "Vírgula deslocada explica 99,25% da Diferença absoluta, em 20 Chaves." É o Tipo do Erro com a maior Diferença absoluta, a parte dele na Diferença absoluta do Resumo e as suas Chaves. Sem Chave com Diferença, não há frase. A conclusão vem primeiro (Pirâmide de Minto).
43. **O Tipo do Erro entra no Resumo do HTML**, num gráfico de barras como o da Idade, depois do quadro e dos avisos e antes dos Atributos Problemáticos: a Diferença absoluta de cada Tipo, com as Chaves no rótulo (`Vírgula deslocada (20 Chaves)`) e a nota de que uma Chave pode contar em mais de um Tipo. Sem Chave com Diferença, o gráfico não aparece. O Excel não muda.
44. **Reais com unidade e abreviados no HTML:** todo valor em reais que aparece na página vai com `R$` e abreviado, com uma casa: `R$ 688,3 mi`, `R$ 4,2 mil`, `R$ 1,1 bi`; abaixo de R$ 1.000, com os centavos (`R$ 705,42`); negativo com o sinal na frente (`-R$ 416,4 mi`). O arredondamento é o do Valor, com o meio para longe do zero; se ele chega a 1.000 de uma unidade, passa para a próxima (`R$ 1,0 mi`). Os valores exatos ficam nas tabelas "Dados do gráfico", com "(R$)" no título, e no Excel.
45. **Os Atributos Problemáticos do HTML trocam a Concentração desproporcional por duas partes**, em linguagem de gente: colunas Atributo, Valor, Diferença absoluta, `% da diferença` (a parte do valor na Diferença absoluta das Chaves) e `% do valor` (a parte dele no peso), as duas com 2 casas como o Excel. A ordem continua a da Concentração desproporcional. O Excel não muda.
