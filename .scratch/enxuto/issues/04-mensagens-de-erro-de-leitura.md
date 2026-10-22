# 04: Mensagens de erro claras na leitura e na CLI

**What to build:** quando um arquivo não serve, o analista entende o porquê em linguagem simples, sem traceback na tela. Se falta `Chave`, `Data` ou `Valor`, a mensagem diz qual coluna falta, em qual arquivo, e lista as colunas encontradas. Se um Valor ou uma Data não pode ser lido, a mensagem diz o arquivo, a linha e o conteúdo. A CLI mostra a mensagem e sai com código diferente de 0. Ver spec: Decisões de implementação (Módulos/`leitura`), Interface; histórias 7, 8 e 35.

**Blocked by:** 02

**Status:** ready-for-agent

- [ ] Falta de coluna: a mensagem nomeia a coluna e o arquivo e lista as colunas encontradas.
- [ ] Valor ilegível (ex.: `12,3,4` ou `abc`): a mensagem traz o arquivo, a linha como o usuário a vê no arquivo e o conteúdo.
- [ ] Data ilegível (ex.: `31/02/2026` ou `ontem`): a mensagem traz o arquivo, a linha e o conteúdo.
- [ ] Um Valor ou Data vazio numa linha com Chave é tratado como erro com arquivo e linha (decisão do implementador registrada nas notas de entrega, se divergir).
- [ ] A CLI mostra só a mensagem (sem traceback) e sai com código diferente de 0; nenhum `.xlsx` é gerado.
- [ ] Testes de ponta a ponta para cada mensagem, conferindo o texto.
- [ ] `C:\Users\josef\Projetos\Desafio-Conciliacao\.venv\Scripts\python -m pytest -q` passa.
- [ ] Teste com olhos de usuário: em `exemplo\`, criar uma cópia da Base A sem a coluna `Valor` e outra com um valor `abc` numa linha; rodar a CLI com cada uma (`PYTHONIOENCODING=utf-8`) e conferir que a tela mostra uma mensagem simples, com arquivo, linha e conteúdo, e nenhum traceback.

**Notas de entrega:**

**Onde está agora (depois da entrega):**
