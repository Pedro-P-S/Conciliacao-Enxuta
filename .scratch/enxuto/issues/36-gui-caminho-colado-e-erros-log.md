# 36: GUI com caminho colado e `erros.log` que não grava

**What to build:** na GUI, o caminho colado com espaço nas pontas ou entre aspas (o "Copiar como caminho" do Windows) é aceito. Se o `erros.log` não pode ser gravado, a mensagem simples aparece mesmo assim, e o resultado da execução anterior sai da tela. As regras ficam no `gui_estado`; a GUI continua casca. Ver spec: Interface (GUI Tkinter), bloco "Decisões de 24/10/2026" (GUI), Testes/Correções da auditoria (de ponta a ponta); histórias 54 e 55.

**Blocked by:** 30

**Status:** done

- [x] Teste pelo `gui_estado`: um caminho entre aspas e um com espaço nas pontas conciliam como o caminho limpo.
- [x] Teste pelo `gui_estado`: com o `erros.log` impedido de ser gravado, a Resposta traz a mensagem simples, sem exceção.
- [x] Depois de um erro, o caminho do `.xlsx` da execução anterior não fica na tela.
- [x] O autoteste da GUI (`CONCILIACAO_AUTOTESTE=1`) continua saindo com 0.
- [x] `C:\Users\josef\Projetos\Conciliacao-Enxuta\.venv\Scripts\python -m pytest -q` passa.
- [x] Teste com olhos de usuário: chamar o `gui_estado` com os caminhos de `exemplo\` copiados com "Copiar como caminho" (entre aspas) e conferir que gera o `.xlsx`; depois chamar com um arquivo que não existe e conferir que a Resposta não traz o caminho anterior.

**Notas de entrega:**
- Seam testada: `conciliar_pela_janela` (`gui_estado`), escolhida pela spec; a janela só pelo autoteste.
- `conciliacao_enxuta/gui_estado.py`: `_caminho_limpo` tira o espaço das pontas e as aspas dos caminhos da Base A e da Base B. Se gravar o `erros.log` falha, a Resposta traz "Algo deu errado e a conciliação não foi feita. Os detalhes não puderam ser gravados no erros.log." em vez de deixar a exceção escapar.
- A GUI não mudou: ela já troca a situação pela mensagem e desliga o "Abrir pasta" quando a Resposta não tem caminho; o resultado anterior só ficava na tela porque a exceção do log escapava do clique.
- `tests/test_gui.py`: caminho entre aspas, com espaço e os dois juntos (parametrizado); `erros.log` impedido (um arquivo no lugar da pasta `ConciliacaoEnxuta`).
- Olhos de usuário: `exemplo\base_a.csv` e `base_b.csv` entre aspas geraram `exemplo\conciliacao_2026-09-30.xlsx`; depois, `"exemplo
ao_existe.csv"` deu só `nao_existe.csv: o arquivo não existe.`, sem caminho.
- pytest: 268 passed.

**Onde está agora (depois da entrega):**
A GUI aceita o caminho colado do "Copiar como caminho" e dá a mensagem simples mesmo sem conseguir gravar o `erros.log`.
