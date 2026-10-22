# 17: Erros na janela em linguagem simples, traceback no erros.log

**What to build:** quando a conciliação falha pela janela, o analista vê só uma mensagem em linguagem simples (as mesmas da leitura: coluna que falta, arquivo, linha e conteúdo); um erro inesperado mostra uma mensagem genérica simples. O traceback completo vai para `%LOCALAPPDATA%\ConciliacaoEnxuta\erros.log`, nunca para a tela. A decisão do que mostrar e do que gravar fica em `gui_estado`. Ver spec: Decisões de implementação (Interface/GUI Tkinter); história 35.

**Blocked by:** 16

**Status:** ready-for-agent

- [ ] `gui_estado` testado direto: um erro de leitura vira a mensagem simples da leitura; um erro inesperado vira uma mensagem genérica que cita o erros.log.
- [ ] O traceback é acrescentado (não sobrescrito) em `erros.log` dentro de `%LOCALAPPDATA%\ConciliacaoEnxuta\`, criando a pasta se não existir; nos testes, a pasta do log é redirecionada para uma pasta temporária.
- [ ] A janela mostra a mensagem sem traceback e continua aberta para nova tentativa.
- [ ] O autoteste continua saindo com 0.
- [ ] `C:\Users\josef\Projetos\Desafio-Conciliacao\.venv\Scripts\python -m pytest -q` passa.
- [ ] Teste com olhos de usuário: chamar `gui_estado` com uma cópia de base de `exemplo\` sem a coluna `Valor` e conferir a mensagem simples; provocar um erro inesperado com o log apontando para uma pasta temporária e conferir que o traceback foi gravado lá e não aparece na mensagem (`PYTHONIOENCODING=utf-8`); por fim rodar a GUI com `CONCILIACAO_AUTOTESTE=1` e conferir a saída 0.

**Notas de entrega:**

**Onde está agora (depois da entrega):**
