# 04: Mensagens de erro claras na leitura e na CLI

**What to build:** quando um arquivo não serve, o analista entende o porquê em linguagem simples, sem traceback na tela. Se falta `Chave`, `Data` ou `Valor`, a mensagem diz qual coluna falta, em qual arquivo, e lista as colunas encontradas. Se um Valor ou uma Data não pode ser lido, a mensagem diz o arquivo, a linha e o conteúdo. A CLI mostra a mensagem e sai com código diferente de 0. Ver spec: Decisões de implementação (Módulos/`leitura`), Interface; histórias 7, 8 e 35.

**Blocked by:** 02

**Status:** done

- [x] Falta de coluna: a mensagem nomeia a coluna e o arquivo e lista as colunas encontradas.
- [x] Valor ilegível (ex.: `12,3,4` ou `abc`): a mensagem traz o arquivo, a linha como o usuário a vê no arquivo e o conteúdo.
- [x] Data ilegível (ex.: `31/02/2026` ou `ontem`): a mensagem traz o arquivo, a linha e o conteúdo.
- [x] Um Valor ou Data vazio numa linha com Chave é tratado como erro com arquivo e linha (decisão do implementador registrada nas notas de entrega, se divergir).
- [x] A CLI mostra só a mensagem (sem traceback) e sai com código diferente de 0; nenhum `.xlsx` é gerado.
- [x] Testes de ponta a ponta para cada mensagem, conferindo o texto.
- [x] `C:\Users\josef\Projetos\Desafio-Conciliacao\.venv\Scripts\python -m pytest -q` passa.
- [x] Teste com olhos de usuário: em `exemplo\`, criar uma cópia da Base A sem a coluna `Valor` e outra com um valor `abc` numa linha; rodar a CLI com cada uma (`PYTHONIOENCODING=utf-8`) e conferir que a tela mostra uma mensagem simples, com arquivo, linha e conteúdo, e nenhum traceback.

**Notas de entrega:**

- `leitura.py`: nova exceção `ErroDeLeitura` (subclasse de `ValueError`). Mensagens:
  - `base_a.csv: falta a coluna Valor. Colunas encontradas: CHAVE, data.` (colunas como estão no arquivo, sem BOM e sem espaço nas pontas; se faltar mais de uma: `faltam as colunas Data, Valor`).
  - `base_a.csv, linha 3: Valor ilegível: 'abc'.` e `..., linha 2: Data ilegível: '31/02/2026'.` A linha é a do arquivo (cabeçalho = linha 1). Valor grande demais para centavos `Int64` também é "Valor ilegível", sem traceback.
  - Decisão: Valor ou Data vazio numa linha com Chave é erro (`linha 3: Valor vazio.` / `Data vazia.`); numa linha sem Chave, não (ela já fica fora do cruzamento, ticket 05).
  - Checa todos os Valores antes das Datas e para no primeiro problema.
- `cli.py`: trata `ErroDeLeitura` como `SemDataBaseComum`: só a mensagem no stderr, código 1, nenhum `.xlsx`.
- `tests/test_ponta_a_ponta.py`: um teste de ponta a ponta por mensagem, conferindo o texto, a ausência de traceback e de `.xlsx`.
- Teste com olhos de usuário em `exemplo\`: cópias da Base A sem `Valor` e com `abc` na linha 6; a CLI mostrou as duas mensagens acima, código 1, nenhum traceback e nenhum `.xlsx`.
- Fora do escopo, vistos na revisão: ainda dão traceback um caminho inexistente, um `.csv` em latin-1, um arquivo vazio e colunas duplicadas (`Valor` e `valor`); com campo entre aspas que quebra linha, a linha informada conta registros e não linhas físicas; Valor com 3 ou mais casas decimais é arredondado sem aviso (já era assim).
- Arquivos: `conciliacao_enxuta/leitura.py`, `conciliacao_enxuta/cli.py`, `tests/test_ponta_a_ponta.py`.

**Onde está agora (depois da entrega):**
