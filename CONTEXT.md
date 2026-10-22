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

**Atributo**:
Qualquer coluna além de Chave, Data e Valor, com o nome que o usuário quiser. Serve para achar onde a diferença se concentra.

**Data-base**:
Cada valor distinto da coluna `Data`. Uma base pode trazer várias Data-bases, por exemplo uma posição por dia útil durante seis meses, sem precisar ter todos os dias.

## Resultado

**Diferença**:
Valor A menos Valor B de uma Chave numa Data-base.

**Diferença total**:
A soma das Diferenças com sinal. Positivas e negativas se anulam.

**Diferença absoluta**:
A soma das Diferenças sem sinal. Mede o tamanho do problema, mesmo quando a Diferença total dá perto de zero.

**Concentração**:
Quanto um valor de Atributo pesa na Diferença absoluta comparado ao quanto pesa no Total. Serve para ordenar; não aparece para o usuário.

**Tolerância**:
O valor até o qual uma Diferença conta como zero. Padrão de R$ 1,00; o usuário pode mudar.

**Tipo do Erro**:
O que explica a Diferença de uma Chave: Só em A, Só em B, Sinal invertido, Duplicado, Vírgula deslocada, Dígitos trocados ou Sem padrão. Uma Chave pode ter mais de um.

**Aberta desde**:
A Data-base em que a Diferença de uma Chave apareceu e, desde então, não sumiu mais. Se ela some e volta, vale a data da volta; se só muda de valor, a data não muda.

**Idade da Diferença**:
Dias corridos entre o Aberta desde e a Data-base mais recente. Agrupada em faixas: até 30 dias, 31 a 90, 91 a 365, 366 dias a 5 anos, mais de 5 anos.

**Histórico da Diferença**:
A Diferença absoluta em cada Data-base, do início ao fim do período.
