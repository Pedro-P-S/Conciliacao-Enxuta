# 16: Janela Tkinter com autoteste

**What to build:** o analista concilia sem linha de comando. A janela tem Base A e Base B, cada uma com o botão Procurar, a Tolerância (padrão `1,00`) e o botão Conciliar. No fim, mostra o caminho do resultado e um botão para abrir a pasta. A GUI é casca: as regras (validar que os dois arquivos foram escolhidos, ler a Tolerância em formato brasileiro, chamar a conciliação e devolver o caminho ou a mensagem) ficam em `gui_estado`, que não importa Tkinter. Com `CONCILIACAO_AUTOTESTE=1`, a janela monta escondida, fecha sozinha e sai com 0 (ou 1, se falhar). Ver spec: Decisões de implementação (Módulos, Interface/GUI Tkinter, Interface/Autoteste), Testes (GUI); histórias 1, 13 e 34.

**Blocked by:** 04

**Status:** done

- [x] `gui_estado` testado direto (sem Tkinter): sem Base A ou Base B dá mensagem simples; Tolerância `1,00`, `0,5` e `2` são aceitas e convertidas para centavos; Tolerância inválida dá mensagem simples; com tudo certo devolve o caminho do `.xlsx`.
- [x] `gui_estado` não importa Tkinter (teste confere).
- [x] A janela tem os campos e botões da spec; no fim mostra o caminho e um botão que abre a pasta do resultado.
- [x] Com `CONCILIACAO_AUTOTESTE=1`, a GUI monta escondida, fecha sozinha e sai com 0; um teste roda esse autoteste em subprocesso e confere o código de saída. Nenhum teste abre a janela sem essa variável.
- [x] A GUI abre por um ponto de entrada simples do pacote (por exemplo, `python -m conciliacao_enxuta` sem subcomando), registrado nas notas de entrega.
- [x] `C:\Users\josef\Projetos\Desafio-Conciliacao\.venv\Scripts\python -m pytest -q` passa.
- [x] Teste com olhos de usuário: com `CONCILIACAO_AUTOTESTE=1`, rodar a GUI e conferir que sai com 0; chamar `gui_estado` com as bases de `exemplo\` e Tolerância `1,00` e conferir que o caminho devolvido existe e é o da pasta da Base A (`PYTHONIOENCODING=utf-8`).

**Notas de entrega:**

- Ponto de entrada: `python -m conciliacao_enxuta` sem argumentos abre a janela; com subcomando (`conciliar ...`) segue a CLI (`__main__.py` decide pela presença de argumentos).
- `gui_estado.conciliar_pela_janela(base_a, base_b, tolerancia)` recebe os textos da janela e devolve `Resposta(caminho, mensagem)`: "Escolha o arquivo da Base A/B." se falta arquivo; a mensagem de `tolerancia_em_centavos` (reaproveitada da CLI) se a Tolerância é inválida; senão concilia e grava o `.xlsx` na pasta da Base A. `TOLERANCIA_PADRAO_EM_TEXTO` ("1,00") vem de `TOLERANCIA_PADRAO`. Não importa Tkinter.
- `gui.py`: Base A e Base B com Procurar (filtro `.csv .xlsx .parquet`), Tolerância, Conciliar, a linha com o caminho do resultado (ou a mensagem) e o botão "Abrir pasta" (`os.startfile`), habilitado só depois de um resultado. Com `CONCILIACAO_AUTOTESTE=1` a janela monta escondida (`withdraw`), fecha sozinha (`after` → `destroy`) e sai com 0; uma falha ao montar sai com 1 (exceção não tratada).
- Erros de leitura e inesperados na janela e o `erros.log` ficam para o ticket 17.
- Teste com olhos de usuário: `exemplo\` gerado; autoteste saiu com 0; `conciliar_pela_janela` com as bases de `exemplo\` e "1,00" devolveu `exemplo\conciliacao_2026-09-30.xlsx`, que existe e está na pasta da Base A; sem Base A e com Tolerância "um real" deram as mensagens simples.
- pytest: 82 passed.
- Arquivos: `conciliacao_enxuta/gui_estado.py` (novo), `conciliacao_enxuta/gui.py` (novo), `conciliacao_enxuta/__main__.py`, `tests/test_gui.py` (novo).

**Onde está agora (depois da entrega):** a janela concilia pelos caminhos felizes e valida entrada; o tratamento de erros de leitura na janela e o log vêm no ticket 17.
