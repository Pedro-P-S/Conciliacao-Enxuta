# Briefing: correções da auditoria

Origem: a auditoria do repositório em `.scratch/enxuto/review.md` (seção "Auditoria do repositório inteiro"). Aqui entra só o que a spec, o `GRILL.md` e o `CONTEXT.md` já respondem. As regras novas estão no `GRILL.md`, decisões 27 a 34. O glossário (`CONTEXT.md`) e o `CLAUDE.md` já foram alinhados à spec.

## Comportamento (vai para a spec: regras e histórias)

1. **Atributo chamado `Peso`, `Absoluta` ou `Atributo`** (ou qualquer nome que uma coluna interna use) não derruba a conciliação (GRILL 16, história 45). Auditoria, crítico 1.
2. **Separadores do Valor** (GRILL 27): críticos 3 e 4.
3. **Valor que não cabe em centavos `Int64`**, inclusive o inteiro grande do `.parquet`, é Valor ilegível (GRILL 27): crítico 2.
4. **Data com ano de 2 dígitos e data do Excel enorme** são Data ilegível (GRILL 28): críticos 5 e 6.
5. **Tipos do `.parquet`** (`decimal`, `bool`, `null`, `categorical`, `time`) viram Linha rejeitada ou são lidos, nunca param a execução (GRILL 28): crítico 7.
6. **Erros do arquivo inteiro com mensagem simples, sem traceback** (GRILL 29, história 35): crítico 8 e Nice to have 15 (UTF-16 pede UTF-8; `Valor;Valor` é coluna repetida).
7. **`.xlsx` gravado antes do `.html`** (GRILL 30): crítico 9.
8. **GUI aceita caminho com aspas ou espaço nas pontas; `erros.log` que não grava não escapa** (GRILL 31): críticos 10 e 11.
9. **Tolerância** no formato brasileiro e com mensagem simples quando grande demais (GRILL 32): crítico 12, sem mexer no arredondamento.
10. **Linha da Linha rejeitada no `.xlsx`** conta as linhas vazias antes do cabeçalho (GRILL 33, "a Linha é a que o usuário vê"): crítico 16.
11. **HTML igual ao Excel** (GRILL 34, "o mesmo Resumo do Excel, com os mesmos rótulos"): Nice to have 14.

## Implementação (vai para a spec: decisões de implementação; não muda o que o usuário vê)

12. Um pipeline só ler → conciliar → gravar, `conciliar_arquivos(base_a, base_b, tolerancia, pasta)` no `cli.py`, usado pela CLI e pela `gui_estado`. Sugestão 1.
13. Casa com linha sem Chave sem o produto completo antes de filtrar (join por faixa). Sugestão 2.
14. Gravar o `.xlsx` mais rápido, sem mudar o que ele mostra. Sugestão 3.
15. Corte por limite e o seu aviso numa função só. Sugestão 4.
16. `quadro_do_resumo(resultado)` no `excel.py`, usado pelo Excel e pelo HTML, no lugar do `zip(ROTULOS_DO_QUADRO, quadro)`. Sugestão 5.
17. Reais formatados num lugar só (`leitura._em_reais` e `excel.reais`). Sugestão 6.
18. A regra de sinal da linha sem Chave num lugar só. Sugestão 7.
19. `por_idade` e `historico` como dataclasses congeladas (`FaixaDeIdade`, `PontoDoHistorico`) no `cruzamento.py`. Sugestão 11.
20. A Idade numa função `_idades` só, sem a Chave de texto fictícia. Sugestão 12.
21. Limpezas: a Chave calculada uma vez e o sufixo testado num lugar só na leitura, sem BOM literal invisível no código; o parâmetro `aviso_de_corte` sem sombrear a função; o gerador de exemplo aceita o formato sem diferenciar maiúscula (`"CSV"` grava `.csv`). Nice to have 15 e 16.
22. O comentário do `excel.py:1` ("reais só aqui") passa a dizer Excel e HTML. Sugestão 13.

## Testes (vai para a spec: seção Testes)

23. Testes para cada item acima, para o escape de `<`, `&` e aspas no HTML e para o `erros.log` que não grava. Testes que matem as duas mutações que hoje passam: tirar o filtro de Data-bases comuns da Casa e trocar `>` por `>=` no Por Atributo. Sugestão 9.
24. Os testes param de ler atributos privados do openpyxl (`_charts`, `anchor._from.row`). Sugestão 10.

## Fora, porque a spec não responde (perguntas para o usuário)

- **Cortados do briefing (só gosto, sem bug nem divergência):** itens 13, 14, 19, 20, 21 (menos o gerador com `"CSV"`, que fica) e 24. Não entram na spec.
- Críticos 13 (corte da aba Por Atributo), 14 (célula Linha sem Chave acima de 32.767 caracteres) e 15 (Chave numérica de mais de 15 dígitos no `.xlsx`).
- Sugestão 8 (onde a Tolerância mora) e o arredondamento da Tolerância (pergunta 8).
- Nice to have 16: Atributo com nome de coluna do relatório (`Valor A`, `Tipo do Erro`) e a soma acima do `Int64` numa Chave.
- Nice to have 17 (`exemplo.py` fora do pacote) e o termo Folga da Tolerância.
- As perguntas abertas 1 a 15 da auditoria.
