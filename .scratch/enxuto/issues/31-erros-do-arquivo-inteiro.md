# 31: Erros do arquivo inteiro em mensagem simples

**What to build:** todo erro do arquivo inteiro para a execução com uma mensagem simples que diz o arquivo, na CLI e na GUI, sem traceback: o arquivo que não existe ou não abre, vazio, corrompido, com campo a mais, numa codificação que não é UTF-8 nem cp1252 (um UTF-16 pede para salvar em UTF-8), com formato não suportado, sem `Chave`, `Data` ou `Valor`, ou com uma delas repetida (`Data` e `DATA`, ou `Valor;Valor`), que a mensagem chama de coluna repetida. A pasta de saída que não existe também para, com mensagem simples. Um erro inesperado na CLI sai sem traceback na tela. Ver spec: Regras (Erros do arquivo inteiro), Interface (CLI), bloco "Decisões de 24/10/2026" (Erros do arquivo inteiro), Testes/Correções da auditoria (de ponta a ponta); história 52.

**Blocked by:** 30

**Status:** done

- [x] Teste de ponta a ponta, pela CLI e pelo `gui_estado`, para cada caso: arquivo que não existe, que não abre, vazio, corrompido, com campo a mais, UTF-16 (pede para salvar em UTF-8), formato não suportado, coluna fixa faltando e coluna repetida (`Data` e `DATA`, `Valor;Valor`). A mensagem diz o arquivo e não tem traceback.
- [x] A pasta de saída (`--saida`) que não existe dá mensagem simples.
- [x] Um erro inesperado na CLI sai com mensagem simples, sem traceback na tela.
- [x] `C:\Users\josef\Projetos\Conciliacao-Enxuta\.venv\Scripts\python -m pytest -q` passa.
- [x] Teste com olhos de usuário: copiar uma base de `exemplo\`, salvá-la em UTF-16, com `Valor;Valor` e vazia, rodar a CLI em cada uma (`PYTHONIOENCODING=utf-8`) e conferir que a mensagem é simples, diz o arquivo e não mostra traceback.

**Notas de entrega:**
- Seams (as que já existem, sem seam nova, como manda a spec): a CLI `main` e o `gui_estado.conciliar_pela_janela`, os dois pelo `conciliar_arquivos`.
- `leitura.ler_base` traduz os erros do arquivo inteiro em `ErroDeLeitura` com o nome do arquivo: não existe (`o arquivo não existe.`), não abre (`não deu para abrir o arquivo.`), vazio (`o arquivo está vazio.`), `.xlsx`/`.parquet` corrompido (`o arquivo está corrompido.`), campo a mais no `.csv` (`uma linha tem mais campos que o cabeçalho.`) e coluna repetida (`coluna repetida: Data.`), que reconhece `Data`/`DATA` e o `Valor;Valor` que o polars renomeia para `Valor_duplicated_0`. O `.csv` com byte zero (UTF-16) cai na mensagem que já existia: "Salve o .csv como UTF-8."
- `cli.conciliar_arquivos`: a pasta de saída que não existe dá `<pasta>: a pasta de saída não existe.` (conferida depois da leitura, para a GUI dizer antes que a Base A não existe). `cli.main` pega o erro inesperado e imprime `Algo deu errado e a conciliação não foi feita: <erro>`, sem traceback.
- Os dois testes da GUI que usavam uma pasta como erro inesperado (agora é o "não abre") passaram a simular a falha no `conciliar_arquivos`.
- Teste com olhos de usuário em `exemplo\caso_erros_31\`: a `base_a.csv` em UTF-16, com `Valor;Valor` e vazia, e `--saida` numa pasta que não existe; as quatro mensagens são simples, dizem o arquivo, sem traceback, código de saída 1.
- Arquivos: `conciliacao_enxuta/leitura.py`, `conciliacao_enxuta/cli.py`, `tests/test_ponta_a_ponta.py`, `tests/test_gui.py`.

**Onde está agora (depois da entrega):**
Os erros do arquivo inteiro estão em `ler_base` (`leitura.py`); a pasta de saída e o erro inesperado da CLI, em `cli.py`. Testes: `test_erro_do_arquivo_inteiro_da_mensagem_simples_com_o_arquivo_na_cli_e_na_janela`, `test_pasta_de_saida_que_nao_existe_da_mensagem_simples` e `test_erro_inesperado_na_cli_sai_com_mensagem_simples_sem_traceback` em `tests/test_ponta_a_ponta.py`.
