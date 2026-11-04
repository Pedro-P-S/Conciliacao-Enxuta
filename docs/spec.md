# Spec: Conciliação Enxuta

**Status:** ready-for-agent

As decisões de origem estão no `GRILL.md` e os termos no `CONTEXT.md`. A spec, o glossário e os tickets do projeto grande não valem aqui.

## Problema

O analista tem duas bases que deviam ter os mesmos valores e não têm. Somar e ordenar ele já faz no Excel, então uma ferramenta que só faz isso não ajuda. A versão anterior foi para o outro extremo: pedia para mapear cada coluna, e o resultado saía num Excel de umas 10 abas e num HTML de mais umas 15 páginas. Era complicado e não ajudava a achar o que importa.

## Solução

O usuário escolhe dois arquivos, Base A e Base B, confere a Tolerância e clica em Conciliar. As colunas `Chave`, `Data` e `Valor` são reconhecidas pelo nome, e o resto é Atributo. Cada arquivo pode trazer várias Data-bases, por exemplo uma posição por dia útil durante seis meses. As linhas sem Chave, como lançamentos manuais, ficam fora do cruzamento pela Chave, mas entram nos totais e na Diferença de cada Data-base. Uma linha com a Data ou o Valor vazio ou ilegível é uma Linha rejeitada: fica fora de tudo, aparece na aba Erros e não interrompe a execução.

Sai um `.xlsx` com 5 abas:
- **Resumo**: os totais da Data-base mais recente, os avisos, os Atributos Problemáticos, um gráfico da Idade da Diferença e um gráfico da Diferença absoluta no tempo.
- **Por Tipo do Erro**: quanto da Diferença cada Tipo explica.
- **Por Atributo**: os valores de Atributo com Diferença acima do peso, do maior para o menor.
- **Operações com Diferença**: as Chaves com Diferença na Data-base mais recente, da maior para a menor, com o Tipo do Erro e o Aberta desde.
- **Erros**: as Linhas rejeitadas, com o motivo, e as Data-bases ignoradas.

Ao lado do `.xlsx` sai um `.html` com o mesmo Resumo, para abrir no navegador.

As bases podem trazer mais de uma coluna de valor para bater, como `Valor Juros` e `Valor Receita`. Cada uma é um Batimento, conciliado por inteiro. O `.xlsx` e o `.html` são um só para todos: as abas têm a coluna Batimento para filtrar, e o Resumo tem uma lista para escolher o Batimento.

O que o Excel não dá de graça e a ferramenta entrega: o cruzamento pela Chave, o Tipo do Erro, a linha sem Chave que casa com a Diferença de uma Chave, a Diferença acima do peso por Atributo e há quanto tempo cada Diferença está aberta.

## Histórias do usuário

1. Como analista, quero escolher só os dois arquivos, para não ter de dizer qual coluna é qual.
2. Como analista, quero que as colunas `Chave`, `Data` e `Valor` sejam reconhecidas mesmo com maiúscula, acento ou espaço diferente, para não ter de renomear o arquivo.
3. Como analista, quero que toda coluna além dessas três vire Atributo automaticamente, com o nome que eu dei.
4. Como analista, quero usar `.csv`, `.xlsx` ou `.parquet`, para trabalhar com o que o sistema exporta.
5. Como analista, quero que valores no formato brasileiro (`1.234,56`, `(1.234,56)`, `R$`) sejam lidos certo.
6. Como analista, quero que datas do Excel, `DD/MM/AAAA` e `AAAA-MM-DD` sejam aceitas.
7. Como analista, quero uma mensagem clara que diga qual coluna falta e em qual arquivo, e liste as colunas encontradas.
8. Como analista, quero que uma linha com a Data ou o Valor vazio ou ilegível não pare a conciliação, e que a aba Erros me mostre a base, a linha, a Chave, a Data como veio no arquivo, o Valor (em reais, quando foi lido; como veio, quando não) e o motivo.
9. Como analista, quero mandar um arquivo com seis meses de posições diárias, para acompanhar a Diferença no tempo.
10. Como analista, quero que as Data-bases que estão só numa base sejam ignoradas e listadas na aba Erros, para não ver picos falsos.
11. Como analista, quero que linhas com a mesma Chave na mesma Data-base sejam somadas.
12. Como analista, quero que linhas sem Chave fiquem fora do cruzamento pela Chave e que o Resumo me diga quantas são e quanto somam.
13. Como analista, quero definir uma Tolerância (padrão de R$ 1,00), para que diferenças de centavos não poluam o resultado.
14. Como analista, quero que a Tolerância valha também para Chaves Só em A ou Só em B.
15. Como analista, quero ver no Resumo o Total A, o Total B, a Diferença total, a Diferença absoluta e quantas Chaves têm Diferença na Data-base mais recente.
16. Como analista, quero ver a Diferença absoluta além da total, para não me enganar quando positivas e negativas se anulam.
17. Como analista, quero ver no Resumo um gráfico de barras da Idade da Diferença em faixas (até 30 dias, 31 a 90, 91 a 365, 366 dias a 5 anos, mais de 5 anos), com a Diferença absoluta de cada faixa e quantas Chaves e linhas sem Chave ela tem.
18. (Retirada: o Resumo não avisa mais das Diferenças que já existiam na primeira Data-base; o "ou antes" da história 30 basta.)
19. Como analista, quero um gráfico simples da Diferença absoluta por Data-base, sem uma tabela que estoure o Excel.
20. Como analista, quero ver quanto cada Tipo do Erro explica, em Chaves e em Diferença absoluta.
21. Como analista, quero saber que uma Chave com dois Tipos conta nos dois.
22. Como analista, quero ver os valores de Atributo com Diferença acima do peso, do maior para o menor, sem os que não passam do peso.
23. Como analista, não quero que um valor de Atributo que todas as Chaves têm apareça como suspeito.
24. Como analista, quero ver por Atributo só a Diferença absoluta e a Diferença acima do peso, sem colunas técnicas.
25. Como analista, quero a lista das Chaves com Diferença na Data-base mais recente, da maior para a menor Diferença absoluta.
26. Como analista, quero ver em cada Chave o Valor A, o Valor B, a Diferença absoluta, o Tipo do Erro, o Aberta desde, a Linha sem Chave e todos os Atributos.
27. Como analista, quero que o Tipo do Erro liste todos os tipos que se aplicam.
28. Como analista, quero que o Aberta desde mostre a data da última abertura, quando a Diferença some e volta.
29. Como analista, quero que o Aberta desde não mude quando a Diferença só muda de valor.
30. Como analista, quero ver "DD/MM/AAAA ou antes" quando a Diferença já existia na primeira Data-base.
31. Como analista, quero filtrar e ordenar a aba de operações pelo cabeçalho.
32. Como analista, quero ser avisado na própria aba quando a lista passar de 700 mil linhas e for cortada.
33. Como analista, quero que o arquivo de saída tenha a Data-base no nome e fique na pasta da Base A.
34. Como analista, quero ver o caminho do resultado no fim e poder abrir a pasta com um clique.
35. Como analista, quero mensagens de erro em linguagem simples, sem traceback na tela.
36. Como analista técnico, quero rodar a conciliação pela linha de comando, para automatizar.
37. Como analista, quero que o Total A e o Total B incluam as linhas sem Chave, para que batam com a soma de cada arquivo, fora as Linhas rejeitadas.
38. Como analista, quero que cada linha sem Chave conte como Diferença do valor inteiro na Data-base em que está, no Resumo e no gráfico, porque ela não tem par na outra base.
39. Como analista, quero saber quando uma linha sem Chave tem o valor que zeraria a Diferença de uma Chave, para achar o lançamento manual feito para ela.
40. Como analista, quero que essa comparação seja feita só na Data-base em que a linha aparece pela primeira vez, porque depois a Diferença da Chave muda e o mesmo lançamento se repete nas posições seguintes.
41. Como analista, quero ver ao lado da Chave o valor, a data e a base dessa linha, para achá-la no arquivo e conferir.
42. Como analista, quero ver no Resumo os 5 Atributos Problemáticos, para saber por onde começar sem abrir a aba Por Atributo.
43. Como analista, quero que o Resumo me avise quantas Linhas rejeitadas houve, para não deixar de abrir a aba Erros.
44. Como analista, quero que um Valor com mais de 2 casas seja arredondado para centavos, e não rejeitado.
45. Como analista, quero que um Atributo aceite qualquer conteúdo, número, letra ou símbolo, sem quebrar a conciliação.
46. Como analista, quero o Resumo também num `.html`, com os gráficos, que abra sem internet, para mandar ou mostrar sem abrir o Excel.
47. Como analista, quero que um Atributo com qualquer nome, inclusive `Peso`, `Absoluta` ou `Atributo`, não derrube a conciliação.
48. Como analista, quero que um Valor com os separadores ambíguos (`1,234.56`, `1.2.3,4`) seja uma Linha rejeitada, e não um número lido errado.
49. Como analista, quero que um Valor grande demais para a ferramenta seja uma Linha rejeitada, e não pare a execução nem vire outro número.
50. Como analista, quero que uma Data com o ano de 2 dígitos ou uma data do Excel depois de 31/12/9999 seja uma Linha rejeitada, e não pare a execução.
51. Como analista, quero que um `.parquet` com coluna `decimal`, `bool`, `time`, `categorical` ou só com nulos seja lido ou dê Linhas rejeitadas, sem parar a execução.
52. Como analista, quero que um arquivo que não abre, vazio, corrompido, com campo a mais, numa codificação que não é UTF-8 nem cp1252 ou com a mesma coluna fixa duas vezes dê uma mensagem simples que diga o arquivo, sem traceback, na GUI e na linha de comando.
53. Como analista, quero que, se o `.xlsx` estiver aberto no Excel e não puder ser gravado, nem o `.xlsx` nem o `.html` mudem, para não ficar com os dois de execuções diferentes.
54. Como analista, quero colar na janela o caminho copiado com "Copiar como caminho" do Windows, entre aspas ou com espaço nas pontas.
55. Como analista, quero ver a mensagem simples mesmo quando o `erros.log` não pode ser gravado, e não ver na tela o resultado da execução anterior.
56. Como analista, quero digitar a Tolerância no formato brasileiro (`1.000` é R$ 1.000,00) e receber uma mensagem simples quando ela não for um valor válido.
57. Como analista, quero que a Linha de uma Linha rejeitada de um `.xlsx` seja a linha da planilha, mesmo com linhas vazias antes do cabeçalho, para achá-la no arquivo.
58. Como analista, quero que o `.html` mostre os mesmos números e gráficos do Resumo do Excel, também com uma Data-base só ou sem Diferença.
59. Como analista, quero bater mais de uma coluna de valor entre as duas bases (`Valor Juros`, `Valor Receita`), cada uma conciliada por inteiro, sem configurar nada além do nome da coluna.
60. Como analista, quero que o `Valor` puro continue funcionando sozinho, para os arquivos de hoje não mudarem.
61. Como analista, quero ser avisado quando uma coluna de valor existe só numa base, sem parar a conciliação das outras.
62. Como analista, quero que um Valor ilegível rejeite a linha só no seu Batimento, para não perder as outras colunas dela.
63. Como analista, quero um `.xlsx` só, com a coluna Batimento nas abas para filtrar pelo cabeçalho.
64. Como analista, quero escolher o Batimento numa lista no Resumo do Excel e ver o quadro, os avisos, os Atributos Problemáticos e os gráficos dele.
65. Como analista, quero escolher o Batimento numa lista no `.html`, que continua abrindo sem internet.
66. Como analista, quero um `.html` mais bonito e simples de ler.
67. Como gestor, quero que o `.html` comece por uma frase que diga o que mais explica a diferença, para entender a conclusão antes dos números.
68. Como gestor, quero ver no `.html` quanto cada Tipo do Erro explica, para saber por que as bases não batem sem abrir o Excel.
69. Como gestor, quero os valores do `.html` em reais, com `R$` e abreviados (`R$ 688,3 mi`), para ler de longe.
70. Como gestor, quero ver nos Atributos Problemáticos do `.html` a parte da diferença e a parte do valor de cada um (81% da diferença com 2% do valor), em vez de uma diferença de porcentagens.

## Decisões de implementação

**Módulos:**
- `leitura`: arquivo → a base lida e as Linhas rejeitadas. A base é um DataFrame com Chave (texto, sem espaço nas pontas), Data-base (data), Valor (centavos `Int64`) e Atributos (texto). As Linhas rejeitadas são um DataFrame com Linha, Chave, Data e Valor em texto, e o Motivo: a Chave e a Data como vieram no arquivo (número redondo sem `.0`); o Valor que foi lido (a linha caiu pela Data) no formato de reais `1.234.567,89`, com `-` no negativo, e o que não pôde ser lido como veio. Os nomes de coluna são reconhecidos sem diferenciar maiúscula, acento e espaço nas pontas. Só param a execução os erros do arquivo inteiro (ver Regras); a mensagem diz o arquivo.
- `cruzamento`: a seam principal. `conciliar(base_a, base_b, tolerancia, rejeitadas_a, rejeitadas_b)` recebe as duas leituras e a Tolerância em centavos, e devolve um Resultado com tudo o que o Excel e o HTML mostram: os totais, a Idade por faixa, os avisos, a série do gráfico, a tabela por Tipo do Erro, a tabela por Atributo, as Operações com Diferença, as Linhas rejeitadas das duas bases e as Data-bases ignoradas. Só funções puras sobre DataFrames. A regra de sinal da linha sem Chave (+Valor na Base A, −Valor na Base B) fica num lugar só, usado por todas as contas que a precisam.
- `excel`: Resultado → `.xlsx` com as 5 abas e a aba oculta dos gráficos. O limite de linhas é um parâmetro, com padrão 700.000. Expõe `quadro_do_resumo(resultado)`, os rótulos e os valores do quadro do Resumo, que o Excel e o HTML usam, no lugar de cada um juntar os rótulos com os valores. O corte por limite e o seu aviso ficam numa função só, usada pelas Operações e pelos Erros. Os reais formatados como texto (`1.234,56`) saem de uma função só, usada pela leitura, pelo Excel e pelo HTML. O `excel` e o `html` são os únicos lugares onde os centavos viram reais, e o comentário do módulo diz isso.
- `html`: Resultados → `.html` com o Resumo, sem a Tolerância, as linhas sem Chave e o aviso das Linhas rejeitadas, que ficam só no Excel; ao lado de Chaves com Diferença vem a porcentagem que elas são de todas as Chaves cruzadas na Data-base mais recente ("5,49% das 2.550 Chaves"). Também só no HTML: a frase-resposta no topo, o gráfico Por Tipo do Erro, os reais com `R$` abreviados e as partes da diferença e do valor nos Atributos Problemáticos (ver o bloco de 04/11/2026). Arquivo único, sem nada buscado na internet: as barras vão como SVG, e o único script desenha o gráfico da Diferença no tempo (com eixos, botões de período e zoom arrastando sobre o gráfico) e faz o filtro de Batimento.
- **Batimentos:** a `leitura` devolve, para cada Batimento, a base (com o Valor daquele Batimento em centavos) e as Linhas rejeitadas. O `conciliar` não muda: roda uma vez por Batimento. O `excel` e o `html` recebem os Resultados de todos os Batimentos, na ordem da Base A, e gravam um arquivo só.
- `cli`, `gui` e `gui_estado`. O pipeline ler → conciliar → gravar é um só, `conciliar_arquivos(base_a, base_b, tolerancia, pasta)` no `cli`, usado pela CLI e pelo `gui_estado`; ele lê as duas bases, concilia e grava o `.xlsx` e depois o `.html`. A GUI é casca: as regras ficam em `gui_estado`, que não importa Tkinter.
- Gerador de bases de exemplo: o formato pedido não diferencia maiúscula (`"CSV"` grava `.csv`).

**Regras:**
- **Linha rejeitada:** a Data vazia ou ilegível, ou o Valor vazio ou ilegível, rejeita a linha, com o motivo `Data vazia`, `Data ilegível`, `Valor vazio` ou `Valor ilegível`. A linha não entra em nada: totais, cruzamento, linhas sem Chave e gráficos. Isso vale também para uma linha sem Chave. A linha toda vazia (sem Chave, Data e Valor) é ignorada em silêncio, sem ir para a aba Erros. A Linha é a que o usuário vê: no `.csv` o cabeçalho é a linha 1; no `.xlsx` é a linha da planilha, contando as linhas vazias antes do cabeçalho; no `.parquet` a primeira linha de dados é a 1.
- **Valor:** aceita número, o formato brasileiro (`1.234,56`), `R$`, parênteses e sinal de menos. Com vírgula, o ponto só separa grupos de 3 dígitos e o primeiro grupo não começa com zero (`1.234,56`); fora disso, o Valor é ilegível (`1,234.56`, `1.2.3,4`, `1.2,3`). Sem vírgula, o ponto é separador de milhar só nesse mesmo formato (`1.234` é R$ 1.234,00); senão é decimal (`0.125` é R$ 0,13, `00.500` é R$ 0,50). Com mais de 2 casas, arredonda para centavos, com o meio para longe do zero, uma vez só. Qualquer outro caractere (ex.: `abc`, `#`) torna o Valor ilegível. Um Valor que não cabe em centavos `Int64`, de qualquer formato, inclusive um inteiro grande de um `.parquet`, é ilegível.
- **Data:** aceita data, data do Excel (número), `DD/MM/AAAA` e `AAAA-MM-DD`. O ano tem 4 dígitos (`31/01/26` é Data ilegível). Uma data do Excel acima de 2958465 (31/12/9999) é Data ilegível.
- **Tipos do `.parquet`:** um Valor ou uma Data de um tipo que não é número, texto nem data (ex.: `bool`, `time`) é ilegível; o `decimal` é número; uma coluna `categorical` é lida pelo seu texto; uma coluna só com nulos é vazia. Nenhum desses para a execução.
- **Atributo:** aceita qualquer conteúdo e vira texto; vazio vira nulo. Nunca rejeita a linha nem para a execução. O nome do Atributo é livre: um nome igual ao de uma coluna que a ferramenta usa por dentro (ex.: `Peso`, `Absoluta`, `Atributo`) não derruba a conciliação.
- **Colunas de valor e Batimentos:** uma coluna chamada `Valor`, ou `Valor` + espaço ou `_` + nome (`Valor Juros`, `Valor_Juros`), é uma coluna de valor; o nome é comparado como o das outras colunas. Cada uma é um Batimento, chamado pelo que vem depois de `Valor` como está na Base A (`Juros`); o `Valor` puro é o Batimento `Valor`. Só vira Batimento a coluna que existe nas duas bases; a que está só numa base dá o aviso "Valor Juros só na Base A: não conciliado" na CLI e na GUI, e a execução segue. A ordem dos Batimentos é a das colunas na Base A. Cada Batimento é uma conciliação inteira, com as regras desta spec e a mesma Tolerância; nele, nenhuma outra coluna de valor vira Atributo, e as linhas sem Chave entram com o valor daquele Batimento. O Valor vazio ou ilegível rejeita a linha só no seu Batimento; a Data vazia ou ilegível rejeita a linha em todos. A Data-base mais recente é a maior comum, a mesma para todos; se todas as linhas de uma data caem pelo Valor num Batimento, a Diferença dele nessa data é zero.
- **Erros do arquivo inteiro:** param a execução, com uma mensagem simples que diz o arquivo, na CLI e na GUI, sem traceback: o arquivo que não existe ou não abre, vazio, corrompido, com campo a mais, numa codificação que não é UTF-8 nem cp1252 (um UTF-16 pede para salvar em UTF-8), com formato não suportado, sem `Chave`, sem `Data` ou sem nenhuma coluna de valor (a mensagem diz que falta a coluna `Valor`), sem nenhum Batimento nas duas bases, ou com uma coluna fixa ou de valor repetida (como `Data` e `DATA`, ou `Valor;Valor`), que a mensagem chama de coluna repetida. A pasta de saída que não existe também para, com mensagem simples. Um erro inesperado na CLI sai sem traceback na tela.
- **Preparação:** linhas sem Chave (vazia ou só espaço) saem do cruzamento pela Chave. Linhas com a mesma Chave e a mesma Data-base são somadas, e os Atributos vêm da primeira linha.
- **Linhas sem Chave:** cada uma é uma Diferença do valor inteiro na sua Data-base: +Valor na Base A, −Valor na Base B, sem somar uma linha com outra. Como as Chaves Só em A ou Só em B, conta como Diferença quando |Valor| > Tolerância. Entram no Total A, no Total B, na Diferença total, na Diferença absoluta e no gráfico da Diferença no tempo. Entram também na Idade (ver abaixo). Não entram em Chaves com Diferença, Por Tipo do Erro, Por Atributo nem na aba de operações. Valem só nas Data-bases comuns, como o resto.
- **Data-bases:** entram só as comuns às duas bases. A Data-base mais recente é a maior comum. As ignoradas vão para a aba Erros.
- **Cruzamento por Data-base:** junção completa pela Chave. Diferença = A − B, e o lado que falta conta como 0. Uma Chave tem Diferença quando |Diferença| > Tolerância. O Atributo vem de A e, se vazio ou ausente, de B.
- **Tipo do Erro**, só na Data-base mais recente, com todos os que se aplicam separados por `; ` nesta ordem:
  - Só em A;
  - Só em B;
  - Sinal invertido: A = −B, com A ≠ 0;
  - Duplicado: A = 2×B ou B = 2×A;
  - Vírgula deslocada: A/B ∈ {10, 100, 1000, 0,1, 0,01, 0,001};
  - Dígitos trocados: |Diferença| múltiplo de 9 centavos e os mesmos dígitos de |A| e |B| em outra ordem;
  - Casa com linha sem Chave: uma linha sem Chave zera a Diferença que a Chave tinha na Data-base dessa linha (ver abaixo);
  - Sem padrão: nenhum dos anteriores.

  A Tolerância vale como folga nas comparações de Sinal, Duplicado, Vírgula e Casa com linha sem Chave. A detecção pode ser copiada do projeto grande e adaptada, sem importar.
- **Casa com linha sem Chave:** cada valor de linha sem Chave é comparado uma vez só, na primeira Data-base comum em que ele aparece entre as linhas sem Chave da sua base; depois, o mesmo valor nas Data-bases seguintes é o mesmo lançamento e não é comparado de novo. Nessa Data-base, a linha casa com uma Chave que tinha Diferença quando |Diferença + Valor| ≤ Tolerância, se a linha está na Base A, ou |Diferença − Valor| ≤ Tolerância, se está na Base B. Uma linha para uma Chave, sem combinar várias linhas. Uma linha pode casar com mais de uma Chave, e todas ganham o Tipo. O Tipo só aparece nas Chaves com Diferença na Data-base mais recente, mesmo que a Diferença tenha mudado depois do lançamento.
- **Aberta desde:** a primeira Data-base de uma sequência contínua de Diferença até a mais recente. Se a sequência começa na primeira Data-base, é marcada como "ou antes".
- **Idade:** dias corridos entre o Aberta desde e a Data-base mais recente. Faixas: ≤ 30, 31–90, 91–365, 366–1826 e > 1826 dias. Uma linha sem Chave com Diferença na Data-base mais recente também tem Idade: o mesmo valor nas Data-bases seguintes é o mesmo lançamento, então ela conta desde a primeira Data-base de uma sequência contínua em que esse valor aparece entre as linhas sem Chave da sua base, até a mais recente. Assim, a soma das faixas é a Diferença absoluta do Resumo.
- **Diferença acima do peso:** para cada Atributo e valor, é a % da Diferença absoluta menos a % de |Valor A| no total (usa B quando A é zero). As duas porcentagens são sobre as Chaves, sem as linhas sem Chave. Entram só os valores com Diferença acima do peso > 0; valor de Atributo vazio não entra. A tabela é ordenada pela Diferença acima do peso, decrescente; no empate, pelo Atributo e pelo Valor. A coluna Diferença absoluta é a soma das |Diferença| das Chaves com esse valor.
- **Atributos Problemáticos:** as 5 primeiras linhas da tabela Por Atributo, misturando Atributos. Menos de 5 se a tabela tiver menos.
- **Invariante:** na Data-base mais recente, Total A − Total B = Diferença total (das Chaves com Diferença e das linhas sem Chave acima da Tolerância) + a soma das Diferenças dentro da Tolerância. As Linhas rejeitadas ficam fora dos dois lados.

**Saída:**
- **Arquivos:** `conciliacao_AAAA-MM-DD.xlsx` e `conciliacao_AAAA-MM-DD.html`, na pasta da Base A, sobrescrevendo se já existirem. Reais com formato `#.##0,00`. O `.xlsx` é gravado antes do `.html`: se o `.xlsx` não pode ser gravado (por exemplo, aberto no Excel), nenhum dos dois muda e o usuário recebe uma mensagem simples.
- **Resumo**, nesta ordem:
  1. Um quadro com a Data-base mais recente, a Tolerância, Total A, Total B, Diferença total, Diferença absoluta (as quatro com as linhas sem Chave) e Chaves com Diferença.
  2. Os avisos, só quando acontecem: as linhas sem Chave por base, quantas e quanto somam na Data-base mais recente; "Linhas rejeitadas: N (veja a aba Erros)", com o total das duas bases; e o corte das operações.
  3. Os Atributos Problemáticos, com as colunas da aba Por Atributo. Sem Atributo com Diferença acima do peso, a tabela não aparece.
  4. Um gráfico de barras da Diferença absoluta por faixa de Idade, as 5 faixas sempre, com a quantidade de Chaves no rótulo de cada faixa, como `31 a 90 dias (12 Chaves)`, e a de linhas sem Chave quando houver, como `91 a 365 dias (12 Chaves, 1 linha sem Chave)`.
  5. Um gráfico de linha da Diferença absoluta por Data-base.

  Os dados dos dois gráficos ficam na aba oculta `_grafico`. Sem tabela de histórico nem de Idade.

  O Resumo tem no topo uma lista suspensa (validação de dados) com os Batimentos, na ordem da Base A, e abre no primeiro; sem "Todos". Com um Batimento só, a lista tem uma opção, para o Resumo ser montado de um jeito só. O quadro, os avisos, os Atributos Problemáticos e os dois gráficos seguem a escolha por fórmula, sem macro: os números de cada Batimento ficam na aba `_grafico`, e as células do Resumo e as séries dos gráficos os buscam pelo Batimento escolhido.
- **Coluna Batimento:** as abas Por Tipo do Erro, Por Atributo, Operações com Diferença e Erros têm a coluna `Batimento` na frente, com filtro no cabeçalho, e as linhas vêm por Batimento e depois na ordem desta seção. O limite de linhas é da aba inteira; nas Operações, se cortar, ficam as maiores Diferenças absolutas de todos os Batimentos. Na aba Erros, a Linha rejeitada pela Data e a Data-base ignorada aparecem uma vez, com `Batimento` = `Todos`; a rejeitada pelo Valor leva o seu Batimento.
- **Por Tipo do Erro:** colunas Tipo do Erro, Chaves e Diferença absoluta, ordenadas pela Diferença absoluta, com uma nota de que uma Chave pode contar em mais de um Tipo.
- **Por Atributo:** colunas Atributo, Valor, Diferença absoluta e Diferença acima do peso (em %). Sem filtro. Sem Atributo nas bases, fica só o cabeçalho.
- **Operações com Diferença:** colunas Chave, Valor A, Valor B, Diferença absoluta, Tipo do Erro, Aberta desde, Linha sem Chave e os Atributos com o nome original, ordenadas pela Diferença absoluta, decrescente. Valor A e Valor B mostram o sinal. Cabeçalho congelado e com filtro. Acima do limite, mostra as maiores, e um aviso na linha 1 diz "Nem todas as operações com diferença couberam: mostrando 700.000 de N, as maiores."; o cabeçalho passa para a linha 2. A coluna Linha sem Chave é texto, como `−10.000,00 em 15/03/2026 na Base B` (o valor da linha, a Data-base em que foi comparada e a base), com várias separadas por `; `, e fica vazia quando a Chave não casa com nenhuma.
- **Erros:** colunas Base, Linha, Chave, Data, Valor e Motivo. Primeiro, uma linha por Data-base ignorada, com a Base que a tem, a Data e o Motivo `Data-base só na Base A` ou `Data-base só na Base B`. Depois, as Linhas rejeitadas da Base A e da Base B, na ordem do arquivo, com a Chave e a Data como vieram e o Valor em reais quando foi lido (`1.234,56`), ou como veio quando não. A aba existe sempre; sem erros, fica só o cabeçalho. Cabeçalho congelado e com filtro. Acima do limite, o mesmo corte e o mesmo tipo de aviso das Operações: "Nem todos os erros couberam: mostrando 700.000 de N."
- **HTML:** o mesmo Resumo do Excel, na mesma ordem e com os mesmos rótulos, com os dois gráficos em SVG. Um arquivo só, que abre sem internet, sem biblioteca. Com vários Batimentos, uma lista suspensa no topo e um JavaScript pequeno mostram o Resumo do Batimento escolhido; os Resumos de todos já vêm prontos no arquivo, e sem JavaScript aparece o primeiro. Sem "Todos". O visual é mais bonito e simples, com um tema só, e segue a skill `dataviz` (cores, gráficos, quadro de números e layout). Mostra o que o Excel mostra: o percentual arredonda como no Excel; o eixo do gráfico mostra 0 quando não há Diferença; com uma Data-base só, o gráfico de linha mostra o ponto e a data uma vez; o caractere de controle sai do texto, como no Excel; `<`, `&` e aspas aparecem como texto.

**Interface:**
- **GUI Tkinter:** Base A e Base B, cada uma com o botão Procurar, a Tolerância (padrão 1,00) e o botão Conciliar. No fim, mostra o caminho do `.xlsx` e um botão para abrir a pasta. Os erros aparecem em linguagem simples, e o traceback vai para `%LOCALAPPDATA%\ConciliacaoEnxuta\erros.log`. O caminho colado com espaço nas pontas ou entre aspas (o "Copiar como caminho" do Windows) é aceito. Se o `erros.log` não pode ser gravado, a mensagem simples aparece mesmo assim, e o resultado da execução anterior sai da tela.
- **Tolerância**, na GUI e na CLI: lida no formato brasileiro, com as mesmas regras de separador do Valor (`1.000` é R$ 1.000,00, `0,50` é R$ 0,50). Uma Tolerância que não vira número, negativa ou grande demais dá uma mensagem simples. Arredonda para centavos como o Valor, com o meio para longe do zero (`0,125` é R$ 0,13).
- **CLI:** `python -m conciliacao_enxuta conciliar BASE_A BASE_B [--tolerancia 1,00] [--saida PASTA]`. Imprime o caminho dos dois arquivos. Os erros saem em mensagem simples, sem traceback na tela, inclusive o inesperado.
- **Autoteste:** com `CONCILIACAO_AUTOTESTE=1`, a GUI monta escondida, fecha sozinha e sai com 0 (ou 1, se falhar).
- **Executável:** o `gerar_exe.bat` gera com o PyInstaller uma pasta `dist\ConciliacaoEnxuta` com o `ConciliacaoEnxuta.exe`, que abre a janela, e a pasta `_internal`. É uma pasta, e não um arquivo só, para o `.exe` abrir rápido. O passo a passo está no `README.md`.

**Técnico:** Polars para os dados, openpyxl para o `.xlsx` e os gráficos do Excel, e o HTML montado com a biblioteca padrão. Dinheiro em centavos `Int64` até o Excel e o HTML. Nada é importado do pacote do projeto grande.

### Decisões de 24/10/2026: correções da auditoria

Origem: `GRILL.md`, decisões 27 a 34, e o briefing da auditoria. Histórias 47 a 58.

- **Valor e Data:** os separadores do Valor, o Valor fora de `Int64`, o ano de 4 dígitos, a data do Excel até 31/12/9999 e os tipos do `.parquet` estão em Regras. Todos viram Linha rejeitada ou são lidos; nenhum para a execução.
- **Atributo com nome de coluna interna** (`Peso`, `Absoluta`, `Atributo`) não derruba a conciliação.
- **Erros do arquivo inteiro:** a lista completa está em Regras; todos com mensagem simples, sem traceback, na CLI e na GUI.
- **Gravação:** o `.xlsx` antes do `.html`; se o `.xlsx` falha, nenhum dos dois muda.
- **GUI:** aceita o caminho com aspas ou espaço nas pontas; o `erros.log` que não grava não impede a mensagem simples e tira da tela o resultado anterior.
- **Tolerância:** no formato brasileiro, com mensagem simples quando inválida ou grande demais. O arredondamento passou a ser o do Valor em 28/10/2026, a pedido do usuário.
- **Linha no `.xlsx`:** conta as linhas vazias antes do cabeçalho.
- **HTML igual ao Excel:** percentual, eixo com 0, uma Data-base só e caractere de controle, como em Saída.
- **Implementação, sem mudar o que o usuário vê:** um pipeline só, `conciliar_arquivos`, usado pela CLI e pelo `gui_estado`; `quadro_do_resumo` no `excel`, usado pelo Excel e pelo HTML; o corte por limite e o seu aviso numa função só; os reais em texto numa função só; a regra de sinal da linha sem Chave num lugar só; o gerador de exemplo aceita o formato sem diferenciar maiúscula.
- **Seams dos testes:** as que já existem, sem seam nova. A seam 1 (`conciliar`) para o Atributo com nome interno; a leitura para Valor, Data e `.parquet`; a seam 2, de ponta a ponta pela CLI e pelo `gui_estado` (que passam pelo `conciliar_arquivos`), para os erros do arquivo inteiro, a gravação, a Tolerância, a GUI e o HTML.

### Decisões de 27/10/2026: vários Batimentos

Origem: `GRILL.md`, decisões 35 a 41. Histórias 59 a 66.

- **Convenção pelo nome, sem configuração:** `Valor` e `Valor <nome>` são colunas de valor; cada uma, presente nas duas bases, é um Batimento.
- **Cada Batimento é uma conciliação inteira:** o `conciliar` roda uma vez por Batimento, sem mudar. A leitura separa as bases por Batimento e as Linhas rejeitadas pelo Valor de cada um.
- **Uma saída para todos:** um `.xlsx` (coluna `Batimento` nas abas, lista suspensa no Resumo com fórmulas) e um `.html` (lista suspensa com JavaScript). O HTML deixa de ser sem script: o JavaScript é só o filtro.
- **Visual do HTML:** segue a skill `dataviz`, com um tema só, na identidade do Banrisul (azul #0094FF dominante, azul-escuro #000050, turquesa e roxo de apoio). Em 28/10/2026, a pedido do usuário: a Tolerância e as linhas sem Chave saem do HTML, a coluna Diferença acima do peso passa a se chamar Concentração desproporcional da diferença (no Excel também), e o gráfico no tempo ganha eixos, período e zoom, desenhado pelo script. Depois, também a pedido: sai do HTML o aviso das Linhas rejeitadas, e entra a porcentagem das Chaves com Diferença. Os subagentes não carregam essa skill sozinhos: quem escrever o ticket do HTML põe nele as regras da skill que valem para a página.
- **Seams dos testes:** as que já existem, sem seam nova. A leitura para a convenção de nome e a rejeição por Batimento; a seam 1 (`conciliar`) não muda; a seam 2, de ponta a ponta, para o arquivo único, a coluna Batimento, a lista e as fórmulas do Resumo, o corte da aba inteira, a aba Erros com `Todos` e o filtro do `.html`.

### Decisões de 04/11/2026: o HTML pelas aulas do Módulo 3

Origem: `GRILL.md`, decisões 42 a 45, e a revisão do `.html` contra os PDFs do Módulo 3 (Pirâmide de Minto, anatomia do KPI e jargão sem tradução). Histórias 67 a 70. Só o `.html` muda; o Excel fica como está.

- **Frase-resposta:** antes do quadro, uma frase com o Tipo do Erro de maior Diferença absoluta: "Vírgula deslocada explica 99,25% da Diferença absoluta, em 20 Chaves." A parte é a Diferença absoluta do Tipo sobre a Diferença absoluta do Resumo, com 2 casas como o Excel; "1 Chave" no singular. Sem Chave com Diferença, não há frase.
- **Por Tipo do Erro:** depois do quadro e dos avisos e antes dos Atributos Problemáticos, o título "Diferença absoluta por Tipo do Erro", um gráfico de barras como o da Idade, um Tipo por barra na ordem da aba Por Tipo do Erro, com as Chaves no rótulo (`Vírgula deslocada (20 Chaves)`, `Casa com linha sem Chave (1 Chave)`), a nota "Uma Chave pode contar em mais de um Tipo do Erro." e a tabela "Dados do gráfico". Sem Chave com Diferença, nada disso aparece.
- **Reais:** todo valor em reais visível na página (o quadro, os Atributos Problemáticos, os rótulos e as dicas das barras, o valor no fim da linha e a dica do gráfico no tempo) vai com `R$` e abreviado: abaixo de R$ 1.000, com os centavos (`R$ 705,42`, `R$ 0,00`); a partir daí, com uma casa e `mil`, `mi` ou `bi` (`R$ 4,2 mil`, `R$ 688,3 mi`, `R$ 1,1 bi`; acima, `R$ 1.234,5 bi`). Arredonda com o meio para longe do zero; se o arredondado chega a 1.000 da unidade, passa para a próxima (R$ 999.960,00 é `R$ 1,0 mi`). O negativo leva o sinal na frente: `-R$ 416,4 mi`. As tabelas "Dados do gráfico" ficam com o valor exato (`688.281.380,19`) e com "(R$)" no título da coluna. Os eixos do gráfico no tempo continuam como estão.
- **Atributos Problemáticos:** as colunas passam a ser Atributo, Valor, Diferença absoluta, `% da diferença` e `% do valor`, com as mesmas linhas e a mesma ordem do Excel. `% da diferença` é a Diferença absoluta do valor sobre a soma das |Diferença| das Chaves com Diferença; `% do valor` é essa parte menos a Diferença acima do peso. As duas com 2 casas, arredondadas como o Excel.
- **Seams dos testes:** as que já existem. A de ponta a ponta (CLI → `.html`), de `tests/test_html.py`, para a frase, o gráfico Por Tipo, os reais e as colunas novas.

## Testes

- **Um bom teste** confere comportamento externo: dadas estas bases, o resultado, o Excel ou o HTML mostram isto. Não testa função interna.
- **Seam 1, `conciliar`:** DataFrames pequenos montados no próprio teste. Cobre o cruzamento, a Tolerância (inclusive em órfãs), cada Tipo do Erro e combinações, o Aberta desde (some e volta, muda de valor, "ou antes"), as bordas das faixas, a Idade da linha sem Chave (o mesmo valor repetido nos dias seguintes, e um valor que some e volta), a Diferença acima do peso (um Atributo acima do peso, um que todas as Chaves têm e não aparece, a ordem e o corte em > 0), os Atributos Problemáticos (5 e menos de 5), as Data-bases só numa base, as Chaves repetidas, as linhas sem Chave (nos totais, na Diferença de cada Data-base e com a Tolerância), o Casa com linha sem Chave (na Base A e na Base B, com folga da Tolerância, numa Data-base antiga em que a Diferença era outra, o mesmo valor repetido nos dias seguintes, a Chave sem Diferença naquela Data-base e uma linha que casa com duas Chaves), o Atributo de A com fallback para B e a invariante.
- **Leitura:** arquivos pequenos. Cobre as Linhas rejeitadas (cada motivo, linha sem Chave rejeitada, o número da Linha em `.csv`, `.xlsx` e `.parquet`), a linha toda vazia ignorada, o Valor com mais de 2 casas arredondado, os formatos de Valor aceitos e Atributos com número, letra e símbolo.
- **Seam 2, de ponta a ponta:** arquivos → `.xlsx` e `.html`. O `.xlsx` é lido com openpyxl. Usa um gerador de bases de exemplo com padrões plantados e um gabarito; o gerador planta uma linha sem Chave que casa com a Diferença de uma Chave numa Data-base antiga, e a Diferença dessa Chave muda depois, e planta Linhas rejeitadas de cada motivo. Confere os nomes e a quantidade de abas, os totais, os Atributos Problemáticos, a ordem das linhas, as colunas, o Aberta desde, os avisos, a existência dos dois gráficos, a aba Erros, os formatos de entrada, as mensagens de erro e o corte com o limite reduzido por parâmetro. No `.html`, confere que existe, que traz os totais e os Atributos Problemáticos e que não aponta para nada fora do arquivo.
- **Correções da auditoria (24/10/2026):** um teste para cada regra nova, na seam indicada no bloco de decisões:
  - seam 1: um Atributo chamado `Peso`, `Absoluta` ou `Atributo` concilia normalmente; uma mutação que tire o filtro de Data-bases comuns do Casa com linha sem Chave faz um teste falhar; uma que troque `>` por `>=` no corte da Diferença acima do peso também;
  - leitura: os separadores aceitos e os ilegíveis do Valor (`1,234.56`, `1.2.3,4`, `1.2,3`, `0.125`, `00.500`, `1.234`), o Valor fora de `Int64` em texto e como inteiro de `.parquet`, a Data `31/01/26`, a data do Excel acima de 2958465, as colunas `decimal`, `bool`, `null`, `categorical` e `time` de um `.parquet`, e a Linha de um `.xlsx` com linhas vazias antes do cabeçalho;
  - de ponta a ponta: cada erro do arquivo inteiro com mensagem simples e sem traceback (inclusive UTF-16 e `Valor;Valor`), a pasta de saída que não existe, o erro inesperado na CLI, o `.xlsx` aberto que não deixa mudar o `.html`, a Tolerância no formato brasileiro e a inválida ou grande demais, o caminho com aspas ou espaço na GUI, o `erros.log` que não grava, e no `.html` o percentual, o eixo com 0, uma Data-base só, o caractere de controle e o escape de `<`, `&` e aspas;
  - o gerador de exemplo com o formato `"CSV"` grava `.csv`.
- **Vários Batimentos (27/10/2026):**
  - leitura: `Valor Juros`, `Valor_Juros` e `valor juros` são o mesmo Batimento; o `Valor` puro sozinho continua funcionando; a coluna de valor só numa base dá o aviso e não para; sem nenhum Batimento nas duas bases, para com mensagem simples; o Valor ilegível rejeita a linha só no seu Batimento, e a Data ilegível em todos; uma coluna de valor não vira Atributo em outro Batimento;
  - de ponta a ponta: um `.xlsx` e um `.html` só, com o nome de hoje; a coluna `Batimento` nas quatro abas, na ordem da Base A; o corte da aba inteira com as maiores de todos os Batimentos; a aba Erros com `Todos` para a Data e a Data-base ignorada; no Resumo, a lista suspensa com os Batimentos e as fórmulas que buscam o escolhido na `_grafico` (o teste confere as fórmulas e a `_grafico`, porque o openpyxl não calcula); no `.html`, a lista, os Resumos de todos e nada buscado fora do arquivo;
  - o gerador de exemplo planta um segundo Batimento com Diferenças próprias.
- **GUI:** sem teste de clique. `gui_estado` é testado pela seam 1 ou direto, e o autoteste confere que a janela monta.
- **Prior art:** o projeto grande testa assim. Prepara duas bases, cruza, confere contra o gabarito do gerador de exemplo e lê o `.xlsx` com openpyxl.
- Todo ticket termina com um teste com olhos de usuário em `exemplo\`.

## Fora do escopo

- Dashboard HTML (só o Resumo vai para HTML, com o filtro de Batimento) e saídas em CSV ou Parquet.
- "Todos" os Batimentos somados no Resumo.
- Histórico persistido entre Execuções, Justificativas e Aging com episódios.
- Bases Auxiliares, Chave composta, mapeamento de colunas e arquivo de configuração.
- Qualidade, Pareto, Compensação Oculta e Pares Prováveis.
- Os Tipos Valor Fixo, Percentual Constante, Ponta Zerada e Arredondamento.
- Mostrar Abertas e Regularizadas por Data-base.
- No Casa com linha sem Chave: combinar várias linhas para zerar uma Chave, desempatar pelos Atributos, mostrar o número da linha no arquivo e juntar a linha à Chave para zerar a Diferença.
- Linhas sem Chave na aba de operações, uma a uma ou agrupadas.
- Corrigir ou adivinhar o Valor ou a Data de uma Linha rejeitada.

## Notas

- Princípios do `CLAUDE.md`: entre duas soluções equivalentes, a mais simples; nada além do pedido; o ganho é de quem lê o resultado.
- Peças que podem ser copiadas do projeto grande e adaptadas: parse de valor brasileiro e de data, centavos, leitura de csv/xlsx/parquet, formatação em reais e a detecção de padrões.
- Perguntas abertas da auditoria, fora desta spec até o usuário responder: o corte da aba Por Atributo, a célula Linha sem Chave acima de 32.767 caracteres, a Chave numérica de mais de 15 dígitos no `.xlsx`, onde a Tolerância mora, o Atributo com nome de coluna do relatório (`Valor A`, `Tipo do Erro`), a soma acima do `Int64` numa Chave, o `exemplo.py` fora do pacote, o termo Folga da Tolerância e as perguntas abertas 1 a 15.
