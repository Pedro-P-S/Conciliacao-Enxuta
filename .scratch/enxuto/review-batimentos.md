# Review dos tickets 38 a 43 (vários Batimentos)

Base 33fa0db, review feito sobre o HEAD 3109db0. O reviewer só leu o diff: não rodou a suíte nem abriu o `.xlsx` e o `.html`.

## Corrigido (a spec é o correto)

1. Data-base única para todos os Batimentos (5a03441). A data cujas linhas caem todas pelo Valor entra no Histórico com Diferença zero.
2. Aviso de corte do HTML pelo total de todos os Batimentos, como no Excel (507b045).
3. Valor no fim da linha do gráfico de linha do HTML (507b045).

## O que faltou (sugestões do review, não corrigidas)

- **`leitura.ler_base`:** continua no código só para os testes antigos. Migrar esses testes para `ler_batimentos` e apagar a função.
- **Fórmulas do Resumo:** só foram conferidas pelo avaliador de `tests/conftest.py` (`eval`, com patch autouse em `openpyxl.load_workbook` para todos os testes). Nunca abriram num Excel ou LibreOffice (nenhum instalado). Conferir à mão num Excel real.
- **`if len(resultados) > 1` repetido** em `gravar_excel`, `_graficos` e `gravar_html`. Os dois caminhos do Resumo (`_resumo_de_um` e `_resumo_com_lista`) repetem o layout de formas diferentes.
- **`_tabela_por_atributo(..., com_batimento)`:** parâmetro-bandeira, lê as colunas pela posição (`valores[:-2]`, `valores[-2]`, `valores[-1]`).
- **`ler_batimentos`:** chama `_ler_um` uma vez por coluna de valor e relê e reconverte a Data e os Atributos a cada vez. O custo cresce com o número de Batimentos.
- **`exemplo.py`:** `_juros(chave)` é recalculado várias vezes e `linhas_da_base` percorre `_linhas_da_base` duas vezes em paralelo, com `zip`.
- **`html.py`:** duas linhas em branco a mais antes de `_dados_do_grafico`.

## Não verificado

- O rótulo do valor no fim da linha no navegador, a dica ao passar o mouse e a troca do Batimento por clique no `.html`; o 375px só foi checado por JavaScript.
- O `.xlsx` aberto num Excel de verdade.
- A `dataviz`: o `SKILL.md` não foi achado no `rpm`; o ticket 43 seguiu as regras do próprio ticket e o `validate_palette.js` não rodou.
- Linha sem Chave, sem Data e sem o Valor de um Batimento: é ignorada em silêncio nele, mas pode virar "Data vazia" no outro. A spec não define esse caso.
- O corte das Operações no Resumo do Excel é texto fixo, igual para todos os Batimentos. A `_grafico` cresce com os Batimentos (blocos de 131 linhas no exemplo).

## Fluxo

- O agente `implement-spec` não foi encontrado nas 3 tentativas (`Agent type 'implement-spec' not found`), embora `.claude/agents/implement-spec.md` esteja certo e commitado. A implementação foi coordenada direto com o `implementer`. O motivo do não carregamento segue desconhecido.
- A prova das skills veio completa de todos os implementers e do reviewer, com duas exceções de forma: o relatório do 38 não a trouxe e a do 42 veio sem "e ponytail" na primeira linha.
