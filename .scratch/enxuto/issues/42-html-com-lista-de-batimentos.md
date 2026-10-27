# 42: Lista suspensa de Batimentos no HTML

**What to build:** com vários Batimentos, o `.html` tem uma lista suspensa no topo e um JavaScript pequeno que mostra o Resumo do Batimento escolhido; os Resumos de todos já vêm prontos no arquivo, e sem JavaScript aparece o primeiro. Sem "Todos". O arquivo continua único, abre sem internet e sem biblioteca; o único script é o filtro. Com um Batimento só, o `.html` é o de hoje (sem lista). Cada Resumo mostra o que o do Excel mostra, com os mesmos rótulos. Ver spec: Decisões de implementação (`html`), Saída (HTML), Testes/Vários Batimentos (de ponta a ponta); história 65.

**Blocked by:** 38, 39

**Status:** ready-for-agent

- [ ] Teste de ponta a ponta: o `.html` traz a lista com os Batimentos na ordem da Base A e o Resumo de cada um (totais e Atributos Problemáticos conferidos contra o `.xlsx`); sem o script, só o primeiro está visível.
- [ ] Teste de ponta a ponta: o único `<script>` é o filtro, e o arquivo não aponta para nada fora dele (sem `src` ou `href` externos).
- [ ] Teste: um nome de Batimento com `<`, `&` ou aspas aparece como texto (escapado).
- [ ] `C:\Users\josef\Projetos\Conciliacao-Enxuta\.venv\Scripts\python -m pytest -q` passa.
- [ ] Teste com olhos de usuário: rodar a CLI sobre `exemplo\`, abrir o `.html` no navegador sem internet, trocar o Batimento na lista e conferir cada Resumo ao lado da aba Resumo do `.xlsx` naquele Batimento.

**Notas de entrega:**
(preencher na entrega)

**Onde está agora (depois da entrega):**
(preencher na entrega)
