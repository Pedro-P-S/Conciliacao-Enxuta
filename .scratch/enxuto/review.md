# Code review: `c49ac48...HEAD` (tickets 01 a 17)

Revisado contra `docs/spec.md` e `.scratch/enxuto/issues/01` a `17`, nos dois eixos da skill `code-review`: **Standards** e **Spec**. Os testes passam (129). O código não foi alterado.

## Problemas críticos

1. **`.csv` em cp1252/latin-1 quebra a leitura** (eixo Spec). Quando o Excel em português salva um `.csv`, o arquivo sai em cp1252. A Base com acento no cabeçalho ou nos dados dá `UnicodeDecodeError`. Na CLI isso vira traceback, e na janela vira "Algo deu errado…".
   - Onde: `leitura.py:73` (`_separador` abre com `utf-8-sig`) e `leitura.py:81` (`pl.read_csv` espera utf-8).
   - Contraria a spec, histórias 4 ("usar `.csv` … para trabalhar com o que o sistema exporta") e 35 ("mensagens de erro em linguagem simples, sem traceback").
   - Correção sugerida: tentar utf-8 e, se falhar, ler em cp1252, nos dois pontos.

2. **A soma das linhas sem Chave conta a mesma posição várias vezes** (eixo Spec). Desde o merge 05/06, `_sem_chave` (`cruzamento.py:88-91`) conta e soma as linhas sem Chave de todas as Data-bases comuns.
   - Exemplo: com posições diárias (história 9), uma linha de R$ 5,00 repetida em 3 Data-bases sai como `SemChave(linhas=3, soma=1500)`.
   - O Resumo mostra essa "Soma" (`excel.py:81-89`) sem dizer o período, logo abaixo dos totais de uma única Data-base. Com seis meses de posições diárias, o número fica ~120 vezes maior e engana quem lê.
   - Contraria a spec, história 12 ("o Resumo me diga quantas são e quanto somam"), lida junto com o quadro da Data-base mais recente.
   - Nenhum teste pega o problema, porque o gerador só planta essas linhas na `DATA_BASE` (`exemplo.py:304`).
   - Correção sugerida: contar só a Data-base mais recente, ou dizer explicitamente no aviso o período somado.

## Sugestões

### Spec

1. **Valor com 3 ou mais casas decimais é arredondado sem aviso.** No `.csv` o arredondamento é para o par (`1,005` → 100, `leitura.py:52`). No `.xlsx` o meio vai para longe do zero (`leitura.py:119`). O impacto fica abaixo da Tolerância, mas os dois formatos estão incoerentes entre si. Unifique o arredondamento ou recuse o valor com a mensagem da história 8.
2. **A CLI ainda mostra traceback** com caminho inexistente, arquivo vazio (`NoDataError`), colunas duplicadas como `Chave` e `chave` (`DuplicateError`) e `.xlsx` de saída aberto no Excel. Neste último caso, `gravar_excel` está fora do `try` (`cli.py:41-47`). Para o analista técnico (história 36), uma mensagem simples, como a da história 35, seria melhor.
3. **Uma coluna repetida (`X;X`) é renomeada pelo polars sem aviso** e vira um Atributo com nome trocado (história 3).
4. **Uma linha sem Chave e com Data vazia some sem aviso.** `leitura.py:151` aceita a linha e `cruzamento.py:90` a descarta.
5. **O Atributo com valor vazio fica fora da aba Por Atributo** (`drop_nulls("Valor")`, `cruzamento.py:212`). A spec não exclui esse caso, e o vazio pode ser justamente onde a Diferença se concentra. Mostrar "(vazio)" segue o princípio de mostrar o que está escondido.
6. **Na janela, `.xlsx` aberto no Excel (`PermissionError`) e caminho inexistente caem na mensagem genérica** (`gui_estado.py:53-55`). Como a saída sobrescreve o arquivo na pasta da Base A, rodar de novo com o resultado aberto é comum. A mensagem deveria dizer "feche o arquivo" ou "arquivo não encontrado".
7. **Falta um teste que garanta que a aba Por Atributo continua inteira quando há corte.** Hoje o código está certo: `por_atributo` vem do cruzado, e o corte existe só em `_aba_operacoes` (`excel.py:188`). Ninguém protege isso de uma regressão.

### Standards

8. **Duplicated Code.** `cli.py:41-46` e `gui_estado.py:48-52` repetem o pipeline `ler_base` → `conciliar` → `gravar_excel` com o mesmo `except (ErroDeLeitura, SemDataBaseComum)`. Extrair uma função única deixa as duas cascas finas.
9. **Conversão da Tolerância no lugar errado.**
   - `gui_estado.py:7,12,45-47` importa `tolerancia_em_centavos` de `cli` e captura `argparse.ArgumentTypeError`, então as regras da janela dependem do argparse.
   - `gui_estado.py:17` converte centavos em reais fora do Excel, perto de violar a regra fixa do `CLAUDE.md` ("vira reais só no Excel").
   - A ida e a volta da Tolerância deveriam morar juntas e lançar um erro do domínio.
10. **Shotgun Surgery.** `exemplo.py:258` redeclara as faixas de `FAIXAS_DE_IDADE` (`cruzamento.py:14-20`), e `exemplo.py:~197` usa o literal "Sem padrão" no lugar de `SEM_PADRAO`, embora o módulo já importe outras constantes de `cruzamento`. Se uma faixa mudar, é preciso editar dois lugares.
11. **Esquema implícito das Operações.**
    - As colunas de `Resultado.operacoes` existem só num comentário (`cruzamento.py:54-56`).
    - `excel.py:194` desempacota 7 colunas pela posição, então uma coluna nova quebra sem aviso.
    - O `Resultado` mistura tuplas (`por_idade`, `historico`) e DataFrames (`por_tipo`, `por_atributo`) para tabelas do mesmo formato.
12. **Duplicação em `excel.py`.** O cabeçalho em negrito aparece 5 vezes (linhas 63, 83, 144, 162 e 192), e a trinca rótulo/Chaves/reais se repete em 65-69, 85-89 e 146-149. Um `_cabecalho(ws, linha, titulos)` resolve a primeira.
13. **Miudezas.**
    - `leitura.py:137` tem um BOM literal invisível, enquanto as linhas 27 e 101 usam o escape.
    - `pl.col("A").fill_null(0), pl.col("B").fill_null(0)` se repete em `cruzamento.py:100, 191, 259 e 271`.
    - Os totais em `cruzamento.py:280-281` filtram a Data-base de novo, embora `a_na_mais_recente` e `b_na_mais_recente` já existam.

## Pontos em aberto deixados pelos implementers

| # | Ponto | Classificação |
|---|---|---|
| 1 | Ticket 02: Valor com 3 ou mais casas | Sugestão 1 |
| 2 | Ticket 04: traceback na CLI | latin-1: **Crítico 1**. O resto: Sugestão 2 |
| 3 | Ticket 05/06: sem Chave só nas Data-bases comuns | **Crítico 2**. Filtrar pelas comuns está certo; somar todas elas é o problema |
| 4 | Ticket 10: folga = Tolerância | Ok. A spec manda assim. Falsos positivos só aparecem em valores da ordem da Tolerância |
| 5 | Ticket 11: "ou antes" relativo à primeira Data-base comum | Ok. Fora das comuns não há Diferença conhecida, e o aviso mostra a data usada |
| 6 | Ticket 14: Atributo vazio fora da aba Por Atributo | Sugestão 5 |
| 7 | Ticket 16/17: Tolerância via `cli.py` e mensagem genérica | Sugestões 6 e 9 |
| 8 | Ticket 15: sem teste da aba Por Atributo inteira com corte | Sugestão 7 |

**Resumo por eixo:**

- **Standards:** 6 sugestões e nenhuma violação dura. A pior é a dependência da janela em `cli` e `argparse` para a Tolerância, junto com a duplicação do pipeline.
- **Spec:** 2 críticos e 7 sugestões. O pior é o `.csv` em cp1252, que não é lido.

## Correções

Só os 2 problemas críticos. As sugestões ficaram como estavam. Antes da correção, cada teste novo falhava pelo motivo certo. Resultado: `pytest -q` dá 131 passed.

1. **`.csv` em cp1252.**
   - `leitura.py`: o `.csv` agora é lido primeiro em UTF-8 (com ou sem BOM) e, se falhar, em cp1252 (`_texto_do_csv`). O texto já decodificado vai para o `pl.read_csv`, e o separador sai da primeira linha desse texto. A função `_separador` deixou de existir.
   - Se o arquivo não for nem UTF-8 nem cp1252, `ler_base` lança um `ErroDeLeitura` com a mensagem "não foi possível ler o texto do arquivo. Salve o .csv como UTF-8." A CLI e a janela já tratavam esse erro, então não aparece traceback.
   - Testes:
     - `test_csv_em_cp1252_com_acento_e_lido`: acento no cabeçalho e nos dados.
     - `test_csv_que_nao_e_utf8_nem_cp1252_da_mensagem_simples`.
   - Gerador: no `.csv`, a Base B passou a sair em cp1252 sem BOM, como o "CSV (separado por vírgulas)" do Excel, com os acentos do Produto. A Base A continua em UTF-8 com BOM. Com o código antigo, 19 testes de ponta a ponta falhavam.
   - Olhos de usuário em `exemplo\`:
     - As bases geradas viraram `.xlsx` pela CLI, com "Crédito", "Câmbio" e "Débito" certos nas abas.
     - Um `.csv` em cp1252 feito à mão, com `Dáta` e `Descrição` no cabeçalho e "Crédito à vista" nos dados, foi conciliado pela CLI e por `conciliar_pela_janela` (sem abrir a GUI).
     - Um arquivo ilegível deu só a mensagem simples, com código 1 na CLI.

2. **Linhas sem Chave contadas várias vezes.**
   - Agora `_sem_chave` conta e soma só a Data-base mais recente, a mesma dos totais do quadro do Resumo.
   - Teste: o antigo `test_linhas_sem_chave_contam_so_nas_data_bases_que_entram_no_cruzamento` virou `test_linhas_sem_chave_contam_so_na_data_base_mais_recente_como_os_totais`, com a mesma linha repetida em 3 Data-bases.
   - Gerador: as linhas sem Chave agora se repetem em toda Data-base, como numa posição diária. O gabarito continua com uma cópia só. Com o código antigo, o aviso do Resumo dava 262 linhas e R$ 13.551,95 na Base A, em vez de 2 linhas e R$ 103,45.
   - Olhos de usuário em `exemplo\`: o Resumo mostra Base A com 2 linhas e 103,45, e Base B com 1 linha e 777,00.
   - Spec: a linha da Preparação diz agora "só na Data-base mais recente, como os totais".

Arquivos alterados:
- `conciliacao_enxuta/leitura.py`
- `conciliacao_enxuta/cruzamento.py`
- `conciliacao_enxuta/exemplo.py`
- `tests/test_leitura.py`
- `tests/test_cruzamento.py`
- `docs/spec.md`
- `.scratch/enxuto/review.md`

Pontos em aberto, do code review das correções:
- Como o cp1252 decodifica quase qualquer byte, um arquivo em outra codificação, ou misto, pode passar com acentos trocados e sem aviso.
- O texto do `.csv` é codificado de novo em UTF-8 para o polars. Isso dobra a memória na leitura, mas é a solução mais simples.
- O título do aviso no Resumo não cita a Data-base. Ele fica logo abaixo do quadro da Data-base mais recente.
