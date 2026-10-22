# 16: Janela Tkinter com autoteste

**What to build:** o analista concilia sem linha de comando. A janela tem Base A e Base B, cada uma com o botão Procurar, a Tolerância (padrão `1,00`) e o botão Conciliar. No fim, mostra o caminho do resultado e um botão para abrir a pasta. A GUI é casca: as regras (validar que os dois arquivos foram escolhidos, ler a Tolerância em formato brasileiro, chamar a conciliação e devolver o caminho ou a mensagem) ficam em `gui_estado`, que não importa Tkinter. Com `CONCILIACAO_AUTOTESTE=1`, a janela monta escondida, fecha sozinha e sai com 0 (ou 1, se falhar). Ver spec: Decisões de implementação (Módulos, Interface/GUI Tkinter, Interface/Autoteste), Testes (GUI); histórias 1, 13 e 34.

**Blocked by:** 04

**Status:** ready-for-agent

- [ ] `gui_estado` testado direto (sem Tkinter): sem Base A ou Base B dá mensagem simples; Tolerância `1,00`, `0,5` e `2` são aceitas e convertidas para centavos; Tolerância inválida dá mensagem simples; com tudo certo devolve o caminho do `.xlsx`.
- [ ] `gui_estado` não importa Tkinter (teste confere).
- [ ] A janela tem os campos e botões da spec; no fim mostra o caminho e um botão que abre a pasta do resultado.
- [ ] Com `CONCILIACAO_AUTOTESTE=1`, a GUI monta escondida, fecha sozinha e sai com 0; um teste roda esse autoteste em subprocesso e confere o código de saída. Nenhum teste abre a janela sem essa variável.
- [ ] A GUI abre por um ponto de entrada simples do pacote (por exemplo, `python -m conciliacao_enxuta` sem subcomando), registrado nas notas de entrega.
- [ ] `C:\Users\josef\Projetos\Desafio-Conciliacao\.venv\Scripts\python -m pytest -q` passa.
- [ ] Teste com olhos de usuário: com `CONCILIACAO_AUTOTESTE=1`, rodar a GUI e conferir que sai com 0; chamar `gui_estado` com as bases de `exemplo\` e Tolerância `1,00` e conferir que o caminho devolvido existe e é o da pasta da Base A (`PYTHONIOENCODING=utf-8`).

**Notas de entrega:**

**Onde está agora (depois da entrega):**
