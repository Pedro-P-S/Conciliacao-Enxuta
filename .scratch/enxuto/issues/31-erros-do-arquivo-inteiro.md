# 31: Erros do arquivo inteiro em mensagem simples

**What to build:** todo erro do arquivo inteiro para a execução com uma mensagem simples que diz o arquivo, na CLI e na GUI, sem traceback: o arquivo que não existe ou não abre, vazio, corrompido, com campo a mais, numa codificação que não é UTF-8 nem cp1252 (um UTF-16 pede para salvar em UTF-8), com formato não suportado, sem `Chave`, `Data` ou `Valor`, ou com uma delas repetida (`Data` e `DATA`, ou `Valor;Valor`), que a mensagem chama de coluna repetida. A pasta de saída que não existe também para, com mensagem simples. Um erro inesperado na CLI sai sem traceback na tela. Ver spec: Regras (Erros do arquivo inteiro), Interface (CLI), bloco "Decisões de 24/10/2026" (Erros do arquivo inteiro), Testes/Correções da auditoria (de ponta a ponta); história 52.

**Blocked by:** 30

**Status:** ready-for-agent

- [ ] Teste de ponta a ponta, pela CLI e pelo `gui_estado`, para cada caso: arquivo que não existe, que não abre, vazio, corrompido, com campo a mais, UTF-16 (pede para salvar em UTF-8), formato não suportado, coluna fixa faltando e coluna repetida (`Data` e `DATA`, `Valor;Valor`). A mensagem diz o arquivo e não tem traceback.
- [ ] A pasta de saída (`--saida`) que não existe dá mensagem simples.
- [ ] Um erro inesperado na CLI sai com mensagem simples, sem traceback na tela.
- [ ] `C:\Users\josef\Projetos\Conciliacao-Enxuta\.venv\Scripts\python -m pytest -q` passa.
- [ ] Teste com olhos de usuário: copiar uma base de `exemplo\`, salvá-la em UTF-16, com `Valor;Valor` e vazia, rodar a CLI em cada uma (`PYTHONIOENCODING=utf-8`) e conferir que a mensagem é simples, diz o arquivo e não mostra traceback.

**Notas de entrega:**

**Onde está agora (depois da entrega):**
