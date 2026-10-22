# Grill do projeto enxuto

Registro das decisões. O glossário fica em `CONTEXT.md`. Quando uma decisão muda, a antiga sai daqui.

## Entrada

1. **Sem mapeamento de colunas.** O usuário escolhe só os dois arquivos. As colunas `Chave`, `Data` e `Valor` têm nome fixo; o resto é Atributo.
2. **Várias Data-bases no mesmo arquivo** (ex.: dias úteis de 6 meses, sem precisar ter todos os dias).
3. **Tolerância:** diferença de até R$ 1,00 (padrão, o usuário pode mudar) conta como zero.

## O que a ferramenta faz

4. **Núcleo:** cruzar pela Chave, dar o Tipo do Erro, mostrar onde a Diferença se concentra por Atributo e acompanhar a Diferença no tempo. Ficam fora: Aging, Justificativas, Pareto, Compensação Oculta, Bases Auxiliares, dashboard HTML.
5. **Tipo do Erro lista todos os que se aplicam** (sem prioridade): Só em A, Só em B, Sinal invertido, Duplicado, Vírgula deslocada, Dígitos trocados, Sem padrão. Cortados: Valor Fixo, Percentual Constante, Ponta Zerada, Arredondamento (a Tolerância já zera).
6. **Aberta desde = última abertura.** Se a Diferença some e volta, vale a data da volta. Se só muda de valor sem sumir, mantém a data original.

## Saída: um Excel com 4 abas

7. **Resumo:** os totais da Data-base mais recente (Total A, Total B, Diferença total, Diferença absoluta, Chaves com Diferença, Tolerância) a Idade da Diferença por faixa e um gráfico de linha da Diferença absoluta por Data-base. Sem tabela do histórico, para não estourar.
8. **Por Tipo do Erro:** uma linha por Tipo, com quantidade de Chaves e Diferença absoluta.
9. **Por Atributo:** colunas Atributo, Valor, Diferença, % da Diferença. Ordenada pela Concentração por valor (% da Diferença absoluta ÷ % do Total), que é calculada mas não aparece. Sem filtro.
10. **Operações com Diferença:** só a Data-base mais recente, uma linha por Chave com Diferença, ordenada pela maior Diferença absoluta. Colunas: Chave, Valor A, Valor B, Diferença, Tipo do Erro, Aberta desde, todos os Atributos. Limite de 700 mil linhas; se cortar, um aviso na própria aba diz que nem todas couberam.

11. **Sem Abertas/Regularizadas no Resumo** (rejeitado). No lugar, **Idade da Diferença por faixa** no Resumo: até 30 dias, 31 a 90, 91 a 365, 366 dias a 5 anos, mais de 5 anos — com quantidade de Chaves e Diferença absoluta. Idade = dias corridos entre Aberta desde e a Data-base mais recente.

12. **Diferença já presente na primeira Data-base:** o Aberta desde mostra "DD/MM ou antes" e o Resumo avisa quantas Chaves estão assim (a idade delas é no mínimo a mostrada). Ficam na faixa que a conta der.

## Bordas

13. **Atributo diferente entre A e B:** vale o de A; se A não tiver a coluna ou o valor, vale o de B.
14. **Data-base só numa base:** entram só as Data-bases que existem nas duas; o Resumo avisa quais foram ignoradas.
15. **Chave repetida na mesma Data-base:** soma os valores.
16. **Linha sem Chave:** fica fora; o Resumo avisa o total.
17. **Números no formato brasileiro aceitos; nomes de coluna sem diferença de maiúscula e acento.**
18. **A Tolerância vale também para Só em A / Só em B.**
