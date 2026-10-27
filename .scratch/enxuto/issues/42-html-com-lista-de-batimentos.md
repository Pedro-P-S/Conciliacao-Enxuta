# 42: Lista suspensa de Batimentos no HTML

**What to build:** com vários Batimentos, o `.html` tem uma lista suspensa no topo e um JavaScript pequeno que mostra o Resumo do Batimento escolhido; os Resumos de todos já vêm prontos no arquivo, e sem JavaScript aparece o primeiro. Sem "Todos". O arquivo continua único, abre sem internet e sem biblioteca; o único script é o filtro. Com um Batimento só, o `.html` é o de hoje (sem lista). Cada Resumo mostra o que o do Excel mostra, com os mesmos rótulos. Ver spec: Decisões de implementação (`html`), Saída (HTML), Testes/Vários Batimentos (de ponta a ponta); história 65.

**Blocked by:** 38, 39

**Status:** done

- [x] Teste de ponta a ponta: o `.html` traz a lista com os Batimentos na ordem da Base A e o Resumo de cada um (totais e Atributos Problemáticos conferidos contra o `.xlsx`); sem o script, só o primeiro está visível.
- [x] Teste de ponta a ponta: o único `<script>` é o filtro, e o arquivo não aponta para nada fora dele (sem `src` ou `href` externos).
- [x] Teste: um nome de Batimento com `<`, `&` ou aspas aparece como texto (escapado).
- [x] `C:\Users\josef\Projetos\Conciliacao-Enxuta\.venv\Scripts\python -m pytest -q` passa.
- [x] Teste com olhos de usuário: rodar a CLI sobre `exemplo\`, abrir o `.html` no navegador sem internet, trocar o Batimento na lista e conferir cada Resumo ao lado da aba Resumo do `.xlsx` naquele Batimento.

**Notas de entrega:**
Seams (pela spec, sem seam nova): seam 2, de ponta a ponta, pela CLI, lida com o html.parser. `Resultado` ganhou `batimento` (cabeçalho da Base A), posto pelo `conciliar_batimentos`. `gravar_html` recebe a lista de Resultados: com um, o `.html` é o de antes; com vários, `<select id="batimento">`, uma `<section>` por Resumo (as demais `hidden`) e um único `<script>` (FILTRO). Nomes escapados. Os testes de totais conferem contra o gabarito, porque o `.xlsx` ainda mostra só o primeiro Batimento (ticket 40/41). Teste com olhos de usuário: CLI sobre `exemplo\`, `.html` aberto no navegador, troca da lista mostra o outro Resumo. Arquivos: conciliacao_enxuta/html.py, cli.py, cruzamento.py, tests/test_html.py.

**Onde está agora (depois da entrega):**
O `.html` único com a lista e os Resumos está em `conciliacao_enxuta/html.py`; o atalho `shortcut:` do `conciliar_arquivos` em `cli.py` agora cobre só o `excel`.
