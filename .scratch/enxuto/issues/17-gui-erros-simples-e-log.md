# 17: Erros na janela em linguagem simples, traceback no erros.log

**What to build:** quando a conciliação falha pela janela, o analista vê só uma mensagem em linguagem simples (as mesmas da leitura: coluna que falta, arquivo, linha e conteúdo); um erro inesperado mostra uma mensagem genérica simples. O traceback completo vai para `%LOCALAPPDATA%\ConciliacaoEnxuta\erros.log`, nunca para a tela. A decisão do que mostrar e do que gravar fica em `gui_estado`. Ver spec: Decisões de implementação (Interface/GUI Tkinter); história 35.

**Blocked by:** 16

**Status:** done

- [x] `gui_estado` testado direto: um erro de leitura vira a mensagem simples da leitura; um erro inesperado vira uma mensagem genérica que cita o erros.log.
- [x] O traceback é acrescentado (não sobrescrito) em `erros.log` dentro de `%LOCALAPPDATA%\ConciliacaoEnxuta\`, criando a pasta se não existir; nos testes, a pasta do log é redirecionada para uma pasta temporária.
- [x] A janela mostra a mensagem sem traceback e continua aberta para nova tentativa.
- [x] O autoteste continua saindo com 0.
- [x] `C:\Users\josef\Projetos\Conciliacao-Enxuta\.venv\Scripts\python -m pytest -q` passa.
- [x] Teste com olhos de usuário: chamar `gui_estado` com uma cópia de base de `exemplo\` sem a coluna `Valor` e conferir a mensagem simples; provocar um erro inesperado com o log apontando para uma pasta temporária e conferir que o traceback foi gravado lá e não aparece na mensagem (`PYTHONIOENCODING=utf-8`); por fim rodar a GUI com `CONCILIACAO_AUTOTESTE=1` e conferir a saída 0.

**Notas de entrega:**
- `conciliar_pela_janela` agora trata os erros: `ErroDeLeitura` e `SemDataBaseComum` viram `str(erro)`, a mesma mensagem simples da leitura (e do CLI). Qualquer outra exceção vira "Algo deu errado e a conciliação não foi feita. Os detalhes estão em <caminho do erros.log>."; o traceback, com data e hora, é acrescentado em `%LOCALAPPDATA%\ConciliacaoEnxuta\erros.log` (modo append, pasta criada se faltar).
- `gui.py` não mudou: já mostra só `Resposta.mensagem` e a janela segue aberta.
- Testes novos em `tests/test_gui.py` (fixture `pasta_do_log` redireciona `LOCALAPPDATA` para `tmp_path`): erro de leitura (coluna Valor faltando), erro inesperado (pasta chamada `base.csv`) com traceback no log e fora da mensagem, e log acumulando dois tracebacks.
- Olhos de usuário: cópia de `exemploase_a.csv` sem `Valor` deu "base_a_sem_valor.csv: falta a coluna Valor. Colunas encontradas: CHAVE, data."; o erro inesperado gravou o traceback no log temporário e a mensagem não o mostrou; a conciliação normal gerou o `.xlsx`; `CONCILIACAO_AUTOTESTE=1` saiu com 0. Suíte: 91 passed.
- Fora do escopo (decisão do dono): caminho inexistente (`FileNotFoundError`) e `.xlsx` aberto no Excel (`PermissionError`) caem na mensagem genérica; uma falha ao gravar o próprio log não é tratada.
- Arquivos: `conciliacao_enxuta/gui_estado.py`, `tests/test_gui.py`.

**Onde está agora (depois da entrega):**
