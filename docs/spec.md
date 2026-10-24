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

## Decisões de implementação

**Módulos:**
- `leitura`: arquivo → a base lida e as Linhas rejeitadas. A base é um DataFrame com Chave (texto, sem espaço nas pontas), Data-base (data), Valor (centavos `Int64`) e Atributos (texto). As Linhas rejeitadas são um DataFrame com Linha, Chave, Data e Valor em texto, e o Motivo: a Chave e a Data como vieram no arquivo (número redondo sem `.0`); o Valor que foi lido (a linha caiu pela Data) no formato de reais `1.234.567,89`, com `-` no negativo, e o que não pôde ser lido como veio. Os nomes de coluna são reconhecidos sem diferenciar maiúscula, acento e espaço nas pontas. Só param a execução os erros do arquivo inteiro: coluna faltando, formato não suportado e texto que não pode ser lido; a mensagem diz o arquivo.
- `cruzamento`: a seam principal. `conciliar(base_a, base_b, tolerancia, rejeitadas_a, rejeitadas_b)` recebe as duas leituras e a Tolerância em centavos, e devolve um Resultado com tudo o que o Excel e o HTML mostram: os totais, a Idade por faixa, os avisos, a série do gráfico, a tabela por Tipo do Erro, a tabela por Atributo, as Operações com Diferença, as Linhas rejeitadas das duas bases e as Data-bases ignoradas. Só funções puras sobre DataFrames.
- `excel`: Resultado → `.xlsx` com as 5 abas e a aba oculta dos gráficos. O limite de linhas é um parâmetro, com padrão 700.000.
- `html`: Resultado → `.html` com o Resumo. Arquivo único: os gráficos vão no próprio arquivo como SVG, sem script nem nada buscado na internet.
- `cli`, `gui` e `gui_estado`. Gravam o `.xlsx` e o `.html`. A GUI é casca: as regras ficam em `gui_estado`, que não importa Tkinter.

**Regras:**
- **Linha rejeitada:** a Data vazia ou ilegível, ou o Valor vazio ou ilegível, rejeita a linha, com o motivo `Data vazia`, `Data ilegível`, `Valor vazio` ou `Valor ilegível`. A linha não entra em nada: totais, cruzamento, linhas sem Chave e gráficos. Isso vale também para uma linha sem Chave. A linha toda vazia (sem Chave, Data e Valor) é ignorada em silêncio, sem ir para a aba Erros. A Linha é a que o usuário vê: no `.csv` e no `.xlsx` o cabeçalho é a linha 1; no `.parquet` a primeira linha de dados é a 1.
- **Valor:** aceita número, o formato brasileiro (`1.234,56`), `R$`, parênteses e sinal de menos. Com mais de 2 casas, arredonda para centavos, com o meio para longe do zero. Qualquer outro caractere (ex.: `abc`, `#`) torna o Valor ilegível.
- **Atributo:** aceita qualquer conteúdo e vira texto; vazio vira nulo. Nunca rejeita a linha nem para a execução.
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
- **Arquivos:** `conciliacao_AAAA-MM-DD.xlsx` e `conciliacao_AAAA-MM-DD.html`, na pasta da Base A, sobrescrevendo se já existirem. Reais com formato `#.##0,00`.
- **Resumo**, nesta ordem:
  1. Um quadro com a Data-base mais recente, a Tolerância, Total A, Total B, Diferença total, Diferença absoluta (as quatro com as linhas sem Chave) e Chaves com Diferença.
  2. Os avisos, só quando acontecem: as linhas sem Chave por base, quantas e quanto somam na Data-base mais recente; "Linhas rejeitadas: N (veja a aba Erros)", com o total das duas bases; e o corte das operações.
  3. Os Atributos Problemáticos, com as colunas da aba Por Atributo. Sem Atributo com Diferença acima do peso, a tabela não aparece.
  4. Um gráfico de barras da Diferença absoluta por faixa de Idade, as 5 faixas sempre, com a quantidade de Chaves no rótulo de cada faixa, como `31 a 90 dias (12 Chaves)`, e a de linhas sem Chave quando houver, como `91 a 365 dias (12 Chaves, 1 linha sem Chave)`.
  5. Um gráfico de linha da Diferença absoluta por Data-base.

  Os dados dos dois gráficos ficam na aba oculta `_grafico`. Sem tabela de histórico nem de Idade.
- **Por Tipo do Erro:** colunas Tipo do Erro, Chaves e Diferença absoluta, ordenadas pela Diferença absoluta, com uma nota de que uma Chave pode contar em mais de um Tipo.
- **Por Atributo:** colunas Atributo, Valor, Diferença absoluta e Diferença acima do peso (em %). Sem filtro. Sem Atributo nas bases, fica só o cabeçalho.
- **Operações com Diferença:** colunas Chave, Valor A, Valor B, Diferença absoluta, Tipo do Erro, Aberta desde, Linha sem Chave e os Atributos com o nome original, ordenadas pela Diferença absoluta, decrescente. Valor A e Valor B mostram o sinal. Cabeçalho congelado e com filtro. Acima do limite, mostra as maiores, e um aviso na linha 1 diz "Nem todas as operações com diferença couberam: mostrando 700.000 de N, as maiores."; o cabeçalho passa para a linha 2. A coluna Linha sem Chave é texto, como `−10.000,00 em 15/03/2026 na Base B` (o valor da linha, a Data-base em que foi comparada e a base), com várias separadas por `; `, e fica vazia quando a Chave não casa com nenhuma.
- **Erros:** colunas Base, Linha, Chave, Data, Valor e Motivo. Primeiro, uma linha por Data-base ignorada, com a Base que a tem, a Data e o Motivo `Data-base só na Base A` ou `Data-base só na Base B`. Depois, as Linhas rejeitadas da Base A e da Base B, na ordem do arquivo, com a Chave e a Data como vieram e o Valor em reais quando foi lido (`1.234,56`), ou como veio quando não. A aba existe sempre; sem erros, fica só o cabeçalho. Cabeçalho congelado e com filtro. Acima do limite, o mesmo corte e o mesmo tipo de aviso das Operações: "Nem todos os erros couberam: mostrando 700.000 de N."
- **HTML:** o mesmo Resumo do Excel, na mesma ordem e com os mesmos rótulos, com os dois gráficos em SVG. Um arquivo só, que abre sem internet.

**Interface:**
- **GUI Tkinter:** Base A e Base B, cada uma com o botão Procurar, a Tolerância (padrão 1,00) e o botão Conciliar. No fim, mostra o caminho do `.xlsx` e um botão para abrir a pasta. Os erros aparecem em linguagem simples, e o traceback vai para `%LOCALAPPDATA%\ConciliacaoEnxuta\erros.log`.
- **CLI:** `python -m conciliacao_enxuta conciliar BASE_A BASE_B [--tolerancia 1,00] [--saida PASTA]`. Imprime o caminho dos dois arquivos.
- **Autoteste:** com `CONCILIACAO_AUTOTESTE=1`, a GUI monta escondida, fecha sozinha e sai com 0 (ou 1, se falhar).

**Técnico:** Polars para os dados, openpyxl para o `.xlsx` e os gráficos do Excel, e o HTML montado com a biblioteca padrão. Dinheiro em centavos `Int64` até o Excel e o HTML. Nada é importado do pacote do projeto grande.

## Testes

- **Um bom teste** confere comportamento externo: dadas estas bases, o resultado, o Excel ou o HTML mostram isto. Não testa função interna.
- **Seam 1, `conciliar`:** DataFrames pequenos montados no próprio teste. Cobre o cruzamento, a Tolerância (inclusive em órfãs), cada Tipo do Erro e combinações, o Aberta desde (some e volta, muda de valor, "ou antes"), as bordas das faixas, a Idade da linha sem Chave (o mesmo valor repetido nos dias seguintes, e um valor que some e volta), a Diferença acima do peso (um Atributo acima do peso, um que todas as Chaves têm e não aparece, a ordem e o corte em > 0), os Atributos Problemáticos (5 e menos de 5), as Data-bases só numa base, as Chaves repetidas, as linhas sem Chave (nos totais, na Diferença de cada Data-base e com a Tolerância), o Casa com linha sem Chave (na Base A e na Base B, com folga da Tolerância, numa Data-base antiga em que a Diferença era outra, o mesmo valor repetido nos dias seguintes, a Chave sem Diferença naquela Data-base e uma linha que casa com duas Chaves), o Atributo de A com fallback para B e a invariante.
- **Leitura:** arquivos pequenos. Cobre as Linhas rejeitadas (cada motivo, linha sem Chave rejeitada, o número da Linha em `.csv`, `.xlsx` e `.parquet`), a linha toda vazia ignorada, o Valor com mais de 2 casas arredondado, os formatos de Valor aceitos e Atributos com número, letra e símbolo.
- **Seam 2, de ponta a ponta:** arquivos → `.xlsx` e `.html`. O `.xlsx` é lido com openpyxl. Usa um gerador de bases de exemplo com padrões plantados e um gabarito; o gerador planta uma linha sem Chave que casa com a Diferença de uma Chave numa Data-base antiga, e a Diferença dessa Chave muda depois, e planta Linhas rejeitadas de cada motivo. Confere os nomes e a quantidade de abas, os totais, os Atributos Problemáticos, a ordem das linhas, as colunas, o Aberta desde, os avisos, a existência dos dois gráficos, a aba Erros, os formatos de entrada, as mensagens de erro e o corte com o limite reduzido por parâmetro. No `.html`, confere que existe, que traz os totais e os Atributos Problemáticos e que não aponta para nada fora do arquivo.
- **GUI:** sem teste de clique. `gui_estado` é testado pela seam 1 ou direto, e o autoteste confere que a janela monta.
- **Prior art:** o projeto grande testa assim. Prepara duas bases, cruza, confere contra o gabarito do gerador de exemplo e lê o `.xlsx` com openpyxl.
- Todo ticket termina com um teste com olhos de usuário em `exemplo\`.

## Fora do escopo

- Dashboard HTML (só o Resumo vai para HTML) e saídas em CSV ou Parquet.
- Histórico persistido entre Execuções, Justificativas e Aging com episódios.
- Bases Auxiliares, mais de um Par de Valor, Chave composta e mapeamento de colunas.
- Qualidade, Pareto, Compensação Oculta e Pares Prováveis.
- Os Tipos Valor Fixo, Percentual Constante, Ponta Zerada e Arredondamento.
- Mostrar Abertas e Regularizadas por Data-base.
- No Casa com linha sem Chave: combinar várias linhas para zerar uma Chave, desempatar pelos Atributos, mostrar o número da linha no arquivo e juntar a linha à Chave para zerar a Diferença.
- Linhas sem Chave na aba de operações, uma a uma ou agrupadas.
- Corrigir ou adivinhar o Valor ou a Data de uma Linha rejeitada.
- O `.exe`, que fica para depois.

## Notas

- Princípios do `CLAUDE.md`: entre duas soluções equivalentes, a mais simples; nada além do pedido; o ganho é de quem lê o resultado.
- Peças que podem ser copiadas do projeto grande e adaptadas: parse de valor brasileiro e de data, centavos, leitura de csv/xlsx/parquet, formatação em reais e a detecção de padrões.
