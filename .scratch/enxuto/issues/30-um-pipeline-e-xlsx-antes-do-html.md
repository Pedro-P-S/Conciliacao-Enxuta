# 30: Um pipeline só, com o `.xlsx` antes do `.html`

**What to build:** o pipeline ler → conciliar → gravar passa a ser um só, `conciliar_arquivos(base_a, base_b, tolerancia, pasta)` no `cli`, usado pela CLI e pelo `gui_estado`: lê as duas bases, concilia e grava o `.xlsx` e depois o `.html`. Se o `.xlsx` não pode ser gravado (por exemplo, aberto no Excel), nem o `.xlsx` nem o `.html` mudam e o usuário recebe uma mensagem simples, na CLI e na GUI. Ver spec: Decisões de implementação (Módulos: `cli`, `gui` e `gui_estado`; Saída/Arquivos), bloco "Decisões de 24/10/2026" (Gravação, Implementação), Testes/Correções da auditoria (de ponta a ponta); história 53.

**Blocked by:** —

**Status:** done

- [x] `conciliar_arquivos` existe no `cli` e é o único caminho da CLI e do `gui_estado` até os dois arquivos.
- [x] O `.xlsx` é gravado antes do `.html`.
- [x] Teste de ponta a ponta: com o `.xlsx` impedido de ser gravado, o `.xlsx` e o `.html` antigos ficam como estavam, e a mensagem é simples, sem traceback, na CLI e no `gui_estado`.
- [x] `C:\Users\josef\Projetos\Conciliacao-Enxuta\.venv\Scripts\python -m pytest -q` passa.
- [x] Teste com olhos de usuário: gerar os dois arquivos sobre `exemplo\`, abrir o `.xlsx` no Excel (ou travá-lo), rodar de novo com outra Tolerância e conferir a mensagem simples e que a data de modificação do `.xlsx` e do `.html` não mudou.

**Notas de entrega:**

- `cli.conciliar_arquivos(base_a, base_b, tolerancia, pasta)` lê, concilia e grava o `.xlsx` e depois o `.html`, devolvendo os dois caminhos. Um `PermissionError` ao gravar o `.xlsx` vira `ArquivoNaoGravado` com a mensagem "`<nome>.xlsx`: não deu para gravar; feche o arquivo no Excel e tente de novo." e o `.html` não é tocado. O `openpyxl` falha ao abrir o arquivo, antes de escrever, então o `.xlsx` antigo fica intacto.
- `cli.main` e `gui_estado.conciliar_pela_janela` passam a chamar só o `conciliar_arquivos` e tratam `ArquivoNaoGravado` como os outros erros simples (CLI: stderr e código 1; GUI: `Resposta.mensagem`). O `gui_estado` gravava o `.html` antes do `.xlsx`; agora é a ordem da spec.
- Seams (escolhidas pela spec, "Seams dos testes"): seam 2, de ponta a ponta pela CLI (`main`) e pelo `gui_estado` (`conciliar_pela_janela`). Sem seam nova. O `.xlsx` é travado nos testes como só de leitura, que dá o mesmo `PermissionError` do Excel.
- Testes novos: `test_xlsx_que_nao_grava_nao_muda_nenhum_dos_dois_e_da_mensagem_simples_na_cli` (`tests/test_ponta_a_ponta.py`) e `..._na_janela` (`tests/test_gui.py`): conferem bytes e data de modificação dos dois arquivos, a mensagem sem traceback e o código 1.
- Olhos de usuário: gerei os dois arquivos em `exemplo\`, travei o `.xlsx` com um handle aberto sem compartilhar escrita (como o Excel), rodei de novo com `--tolerancia 5,00` pela CLI e pelo `gui_estado`: a mensagem simples aparece nos dois e a data de modificação do `.xlsx` e do `.html` não mudou.
- Arquivos: `conciliacao_enxuta/cli.py`, `conciliacao_enxuta/gui_estado.py`, `tests/test_ponta_a_ponta.py`, `tests/test_gui.py`.

**Onde está agora (depois da entrega):**

O pipeline é `conciliar_arquivos` em `conciliacao_enxuta/cli.py`; CLI e `gui_estado` só o chamam. 214 testes passam.
