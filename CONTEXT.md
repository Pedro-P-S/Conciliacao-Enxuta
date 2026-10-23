# Conciliação Enxuta

Versão simples da Conciliação Financeira: duas bases que deviam ser iguais, e a ferramenta mostra onde e por que não são. Usa o projeto maior como fonte, mas só leva o que ajuda o analista a resolver a diferença.

## Entrada

**Base A / Base B**:
Os dois arquivos que deviam ter os mesmos valores. O usuário só escolhe os dois arquivos; não preenche mais nada.

**Colunas fixas**:
As colunas são reconhecidas pelo nome, sem configuração: `Chave`, `Data` e `Valor`. Toda outra coluna é Atributo.
_Evitar_: mapear colunas, escolher a coluna da chave

**Chave**:
O identificador que liga uma linha da Base A a uma linha da Base B.

**Linha sem Chave**:
Uma linha com a Chave vazia, por exemplo um lançamento manual. Fica fora do cruzamento pela Chave, mas entra nos totais e é uma Diferença do valor inteiro na sua Data-base.

**Linha rejeitada**:
Uma linha do arquivo que fica fora de tudo porque a Data ou o Valor estão vazios ou não puderam ser lidos. Aparece com o motivo na aba Erros.

**Atributo**:
Qualquer coluna além de Chave, Data e Valor, com o nome que o usuário quiser. Serve para achar quais valores têm Diferença acima do peso.

**Data-base**:
Cada valor distinto da coluna `Data`. Uma base pode trazer várias Data-bases, por exemplo uma posição por dia útil durante seis meses, sem precisar ter todos os dias.

## Resultado

**Diferença**:
Valor A menos Valor B de uma Chave numa Data-base. Uma Linha sem Chave é uma Diferença do valor inteiro: positiva na Base A, negativa na Base B.

**Diferença total**:
A soma das Diferenças com sinal. Positivas e negativas se anulam.

**Diferença absoluta**:
A soma das Diferenças sem sinal. Mede o tamanho do problema, mesmo quando a Diferença total dá perto de zero.

**Diferença acima do peso**:
Quanto a parte de um valor de Atributo na Diferença absoluta passa da parte dele no Total: % da Diferença absoluta − % do Total. Perto de zero, o valor só tem a Diferença que o seu peso explica.
_Evitar_: Concentração (sugere "onde está a maior parte da Diferença")

**Atributos Problemáticos**:
Os valores de Atributo com a maior Diferença acima do peso, misturando Atributos.

**Tolerância**:
O valor até o qual uma Diferença conta como zero. Padrão de R$ 1,00; o usuário pode mudar.

**Tipo do Erro**:
O que explica a Diferença de uma Chave: Só em A, Só em B, Sinal invertido, Duplicado, Vírgula deslocada, Dígitos trocados, Casa com linha sem Chave ou Sem padrão. Uma Chave pode ter mais de um.

**Casa com linha sem Chave**:
O Tipo do Erro de uma Chave cuja Diferença seria zerada por uma Linha sem Chave, comparando na primeira Data-base em que o valor da linha aparece. Aponta um candidato, como um lançamento manual feito para a Chave; quem confirma é o analista.

**Aberta desde**:
A Data-base em que a Diferença de uma Chave apareceu e, desde então, não sumiu mais. Se ela some e volta, vale a data da volta; se só muda de valor, a data não muda.

**Idade da Diferença**:
Dias corridos entre o Aberta desde e a Data-base mais recente. Uma Linha sem Chave conta desde a primeira Data-base em que o mesmo valor aparece, sem sumir, na sua base. Agrupada em faixas: até 30 dias, 31 a 90, 91 a 365, 366 dias a 5 anos, mais de 5 anos.

**Histórico da Diferença**:
A Diferença absoluta em cada Data-base, do início ao fim do período.
