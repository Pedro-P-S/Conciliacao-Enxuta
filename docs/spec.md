# Spec: Conciliação Enxuta

**Status:** ready-for-agent

As decisões de origem estão no `GRILL.md` e os termos no `CONTEXT.md`. A spec, o glossário e os tickets do projeto grande não valem aqui.

## Problema

O analista tem duas bases que deviam ter os mesmos valores e não têm. Somar e ordenar ele já faz no Excel, então uma ferramenta que só faz isso não ajuda. A versão anterior foi para o outro extremo: pedia para mapear cada coluna, e o resultado saía num Excel de umas 10 abas e num HTML de mais umas 15 páginas. Era complicado e não ajudava a achar o que importa.

## Solução

O usuário escolhe dois arquivos, Base A e Base B, confere a Tolerância e clica em Conciliar. As colunas `Chave`, `Data` e `Valor` são reconhecidas pelo nome, e o resto é Atributo. Cada arquivo pode trazer várias Data-bases, por exemplo uma posição por dia útil durante seis meses.

Sai um único `.xlsx` com 4 abas:
- **Resumo**: os totais da Data-base mais recente, a Idade da Diferença por faixa, os avisos e um gráfico da Diferença absoluta no tempo.
- **Por Tipo do Erro**: quanto da Diferença cada Tipo explica.
- **Por Atributo**: onde a Diferença se concentra, descontado o peso que cada valor já tem no total.
- **Operações com Diferença**: as Chaves com Diferença na Data-base mais recente, da maior para a menor, com o Tipo do Erro e o Aberta desde.

O que o Excel não dá de graça e a ferramenta entrega: o cruzamento pela Chave, o Tipo do Erro, a Concentração por Atributo e há quanto tempo cada Diferença está aberta.

## Histórias do usuário

1. Como analista, quero escolher só os dois arquivos, para não ter de dizer qual coluna é qual.
2. Como analista, quero que as colunas `Chave`, `Data` e `Valor` sejam reconhecidas mesmo com maiúscula, acento ou espaço diferente, para não ter de renomear o arquivo.
3. Como analista, quero que toda coluna além dessas três vire Atributo automaticamente, com o nome que eu dei.
4. Como analista, quero usar `.csv`, `.xlsx` ou `.parquet`, para trabalhar com o que o sistema exporta.
5. Como analista, quero que valores no formato brasileiro (`1.234,56`, `(1.234,56)`, `R$`) sejam lidos certo.
6. Como analista, quero que datas do Excel, `DD/MM/AAAA` e `AAAA-MM-DD` sejam aceitas.
7. Como analista, quero uma mensagem clara que diga qual coluna falta e em qual arquivo, e liste as colunas encontradas.
8. Como analista, quero saber o arquivo, a linha e o conteúdo de um Valor ou de uma Data que não pôde ser lido.
9. Como analista, quero mandar um arquivo com seis meses de posições diárias, para acompanhar a Diferença no tempo.
10. Como analista, quero que as Data-bases que estão só numa base sejam ignoradas e listadas, para não ver picos falsos.
11. Como analista, quero que linhas com a mesma Chave na mesma Data-base sejam somadas.
12. Como analista, quero que linhas sem Chave fiquem fora do cruzamento e que o Resumo me diga quantas são e quanto somam.
13. Como analista, quero definir uma Tolerância (padrão de R$ 1,00), para que diferenças de centavos não poluam o resultado.
14. Como analista, quero que a Tolerância valha também para Chaves Só em A ou Só em B.
15. Como analista, quero ver no Resumo o Total A, o Total B, a Diferença total, a Diferença absoluta e quantas Chaves têm Diferença na Data-base mais recente.
16. Como analista, quero ver a Diferença absoluta além da total, para não me enganar quando positivas e negativas se anulam.
17. Como analista, quero ver no Resumo a Idade da Diferença em faixas (até 30 dias, 31 a 90, 91 a 365, 366 dias a 5 anos, mais de 5 anos), com Chaves e valor em cada uma.
18. Como analista, quero ser avisado quando uma Diferença já existia na primeira Data-base do arquivo, porque aí a idade real pode ser maior.
19. Como analista, quero um gráfico simples da Diferença absoluta por Data-base, sem uma tabela que estoure o Excel.
20. Como analista, quero ver quanto cada Tipo do Erro explica, em Chaves e em Diferença absoluta.
21. Como analista, quero saber que uma Chave com dois Tipos conta nos dois.
22. Como analista, quero ver quais valores de Atributo concentram a Diferença, ordenados pela Concentração por valor.
23. Como analista, não quero que um valor de Atributo que todas as Chaves têm apareça como suspeito.
24. Como analista, quero ver por Atributo só a Diferença e a % da Diferença, sem colunas técnicas.
25. Como analista, quero a lista das Chaves com Diferença na Data-base mais recente, da maior para a menor Diferença absoluta.
26. Como analista, quero ver em cada Chave o Valor A, o Valor B, a Diferença, o Tipo do Erro, o Aberta desde e todos os Atributos.
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

## Decisões de implementação

**Módulos:**
- `leitura`: arquivo → DataFrame com Chave (texto, sem espaço nas pontas), Data-base (data), Valor (centavos `Int64`) e Atributos (texto). Os nomes de coluna são reconhecidos sem diferenciar maiúscula, acento e espaço nas pontas. Os erros dizem o arquivo, a linha e o conteúdo.
- `cruzamento`: a seam principal. `conciliar(base_a, base_b, tolerancia)` recebe os dois DataFrames lidos e a Tolerância em centavos, e devolve um Resultado com os totais, a Idade por faixa, os avisos, a série do gráfico, a tabela por Tipo do Erro, a tabela por Atributo e as Operações com Diferença. Só funções puras sobre DataFrames.
- `excel`: Resultado → `.xlsx` com as 4 abas e a aba oculta do gráfico. O limite de linhas é um parâmetro, com padrão 700.000.
- `cli`, `gui` e `gui_estado`. A GUI é casca: as regras ficam em `gui_estado`, que não importa Tkinter.

**Regras:**
- **Preparação:** linhas sem Chave saem do cruzamento e são contadas e somadas por base. Linhas com a mesma Chave e a mesma Data-base são somadas, e os Atributos vêm da primeira linha.
- **Data-bases:** entram só as comuns às duas bases. A Data-base mais recente é a maior comum.
- **Cruzamento por Data-base:** junção completa pela Chave. Diferença = A − B, e o lado que falta conta como 0. Uma Chave tem Diferença quando |Diferença| > Tolerância. O Atributo vem de A e, se vazio ou ausente, de B.
- **Tipo do Erro**, só na Data-base mais recente, com todos os que se aplicam separados por `; ` nesta ordem:
  - Só em A;
  - Só em B;
  - Sinal invertido: A = −B, com A ≠ 0;
  - Duplicado: A = 2×B ou B = 2×A;
  - Vírgula deslocada: A/B ∈ {10, 100, 1000, 0,1, 0,01, 0,001};
  - Dígitos trocados: |Diferença| múltiplo de 9 centavos e os mesmos dígitos de |A| e |B| em outra ordem;
  - Sem padrão: nenhum dos anteriores.

  A Tolerância vale como folga nas comparações de Sinal, Duplicado e Vírgula. A detecção pode ser copiada do projeto grande e adaptada, sem importar.
- **Aberta desde:** a primeira Data-base de uma sequência contínua de Diferença até a mais recente. Se a sequência começa na primeira Data-base, é marcada como "ou antes".
- **Idade:** dias corridos entre o Aberta desde e a Data-base mais recente. Faixas: ≤ 30, 31–90, 91–365, 366–1826 e > 1826 dias.
- **Concentração por valor:** para cada Atributo e valor, é a % da Diferença absoluta dividida pela % de |Valor A| no total (usa B quando A é zero). Entram só os valores com pelo menos uma Chave com Diferença. A tabela é ordenada pela Concentração, decrescente, e a Concentração não é exibida. A coluna Diferença é a soma com sinal, e a % da Diferença é a parte da Diferença absoluta.
- **Invariante:** na Data-base mais recente, Total A − Total B = Diferença total das Chaves com Diferença + a soma das Diferenças dentro da Tolerância.

**Saída:**
- **Arquivo:** `conciliacao_AAAA-MM-DD.xlsx`, na pasta da Base A, sobrescrevendo se já existir. Reais com formato `#.##0,00`.
- **Resumo:** um quadro com a Data-base mais recente, a Tolerância, Total A, Total B, Diferença total, Diferença absoluta e Chaves com Diferença. Embaixo, as 5 faixas de Idade com Chaves e Diferença absoluta. Depois, os avisos, só quando acontecem: Chaves abertas desde a primeira Data-base, linhas sem Chave por base, Data-bases ignoradas e o corte de operações. Por último, um gráfico de linha da Diferença absoluta por Data-base, com os dados na aba oculta `_grafico`. Sem tabela de histórico.
- **Por Tipo do Erro:** colunas Tipo do Erro, Chaves e Diferença absoluta, ordenadas pela Diferença absoluta, com uma nota de que uma Chave pode contar em mais de um Tipo.
- **Por Atributo:** colunas Atributo, Valor, Diferença e % da Diferença. Sem filtro.
- **Operações com Diferença:** colunas Chave, Valor A, Valor B, Diferença, Tipo do Erro, Aberta desde e os Atributos com o nome original, ordenadas por |Diferença| decrescente. Cabeçalho congelado e com filtro. Acima do limite, mostra as maiores, e um aviso na linha 1 diz "Nem todas as operações com diferença couberam: mostrando 700.000 de N, as maiores."; o cabeçalho passa para a linha 2.

**Interface:**
- **GUI Tkinter:** Base A e Base B, cada uma com o botão Procurar, a Tolerância (padrão 1,00) e o botão Conciliar. No fim, mostra o caminho e um botão para abrir a pasta. Os erros aparecem em linguagem simples, e o traceback vai para `%LOCALAPPDATA%\ConciliacaoEnxuta\erros.log`.
- **CLI:** `python -m conciliacao_enxuta conciliar BASE_A BASE_B [--tolerancia 1,00] [--saida PASTA]`.
- **Autoteste:** com `CONCILIACAO_AUTOTESTE=1`, a GUI monta escondida, fecha sozinha e sai com 0 (ou 1, se falhar).

**Técnico:** Polars para os dados e openpyxl para o `.xlsx` e o gráfico. Dinheiro em centavos `Int64` até o Excel. Nada é importado do pacote do projeto grande.

## Testes

- **Um bom teste** confere comportamento externo: dadas estas bases, o resultado ou o Excel mostra isto. Não testa função interna.
- **Seam 1, `conciliar`:** DataFrames pequenos montados no próprio teste. Cobre o cruzamento, a Tolerância (inclusive em órfãs), cada Tipo do Erro e combinações, o Aberta desde (some e volta, muda de valor, "ou antes"), as bordas das faixas, a Concentração (um Atributo concentrado e um que todas as Chaves têm), as Data-bases só numa base, as Chaves repetidas, as linhas sem Chave, o Atributo de A com fallback para B e a invariante.
- **Seam 2, de ponta a ponta:** arquivos → `.xlsx`, lido com openpyxl. Usa um gerador de bases de exemplo com padrões plantados e um gabarito. Confere os nomes e a quantidade de abas, os totais, as faixas, a ordem das linhas, as colunas, o Aberta desde, os avisos, a existência do gráfico, os formatos de entrada, as mensagens de erro e o corte com o limite reduzido por parâmetro.
- **GUI:** sem teste de clique. `gui_estado` é testado pela seam 1 ou direto, e o autoteste confere que a janela monta.
- **Prior art:** o projeto grande testa assim. Prepara duas bases, cruza, confere contra o gabarito do gerador de exemplo e lê o `.xlsx` com openpyxl.
- Todo ticket termina com um teste com olhos de usuário em `exemplo\`.

## Fora do escopo

- Dashboard HTML e saídas em CSV ou Parquet.
- Histórico persistido entre Execuções, Justificativas e Aging com episódios.
- Bases Auxiliares, mais de um Par de Valor, Chave composta e mapeamento de colunas.
- Qualidade, Pareto, Compensação Oculta e Pares Prováveis.
- Os Tipos Valor Fixo, Percentual Constante, Ponta Zerada e Arredondamento.
- Mostrar Abertas e Regularizadas por Data-base.
- O `.exe`, que fica para depois.

## Notas

- Princípios do `CLAUDE.md`: entre duas soluções equivalentes, a mais simples; nada além do pedido; o ganho é de quem lê o Excel.
- Peças que podem ser copiadas do projeto grande e adaptadas: parse de valor brasileiro e de data, centavos, leitura de csv/xlsx/parquet, formatação em reais e a detecção de padrões.
