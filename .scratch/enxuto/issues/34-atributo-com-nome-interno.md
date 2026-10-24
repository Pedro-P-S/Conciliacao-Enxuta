# 34: Atributo com nome de coluna interna

**What to build:** o nome do Atributo é livre: um Atributo chamado `Peso`, `Absoluta` ou `Atributo` (nomes que a ferramenta usa por dentro) concilia normalmente, sem derrubar a conciliação. Junto, os testes da seam 1 passam a pegar duas mutações: tirar o filtro de Data-bases comuns do Casa com linha sem Chave e trocar `>` por `>=` no corte da Diferença acima do peso. Ver spec: Regras (Atributo), bloco "Decisões de 24/10/2026" (Atributo com nome de coluna interna, Seams dos testes), Testes/Correções da auditoria (seam 1); história 47.

**Blocked by:** 29

**Status:** done

- [x] Teste na seam 1 (`conciliar`): bases com Atributos `Peso`, `Absoluta` e `Atributo` conciliam, e a tabela Por Atributo e as Operações com Diferença trazem esses Atributos.
- [x] Teste na seam 1 que falha se o Casa com linha sem Chave deixar de filtrar as Data-bases comuns.
- [x] Teste na seam 1 que falha se o corte da Diferença acima do peso usar `>=` no lugar de `>`.
- [x] `C:\Users\josef\Projetos\Conciliacao-Enxuta\.venv\Scripts\python -m pytest -q` passa.
- [x] Teste com olhos de usuário: numa cópia das bases de `exemplo\`, renomear um Atributo para `Peso`, rodar a CLI e conferir que as abas Por Atributo e Operações com Diferença mostram a coluna `Peso` com os valores.

**Notas de entrega:**

- Seam testada: só a seam 1 (`conciliar`), como manda a spec (Seams dos testes). Nenhuma seam nova.
- Causa: `_por_atributo` juntava as colunas internas `Peso` e `Absoluta` com os Atributos e fazia `unpivot` com `variable_name="Atributo"`; um Atributo com um desses nomes dava `DuplicateError`. Agora cada Atributo entra separado ao lado das Chaves (`pl.concat` de um frame por Atributo), sem colisão de nome possível.
- Testes novos em `tests/test_cruzamento.py`: `test_atributo_com_nome_de_coluna_interna_concilia_normalmente` (parametrizado em `Peso`, `Absoluta`, `Atributo`; falhava antes da correção), `test_linha_sem_chave_que_aparece_antes_numa_data_base_so_de_a_casa_na_primeira_data_base_comum` (falha se o `_casas` deixar de filtrar as Data-bases comuns; antes nenhum teste pegava essa mutação) e `test_valor_com_diferenca_igual_ao_peso_nao_aparece` (falha com `>=` no corte; essa mutação já era pega por `test_valor_que_todas_as_chaves_tem_e_os_abaixo_do_peso_nao_aparecem`, agora com um teste próprio da borda). As duas mutações foram aplicadas à mão e os testes falharam.
- Teste com olhos de usuário: `exemplo\caso_34\` com as bases de `exemplo\` e a coluna `Carteira` renomeada para `Peso`; a CLI gerou o `.xlsx` e o `.html`, e as abas Por Atributo (`Peso | Legado` no topo) e Operações com Diferença (coluna `Peso` com `Legado`/`Atual`) mostram o Atributo.
- Arquivos alterados: `conciliacao_enxuta/cruzamento.py`, `tests/test_cruzamento.py`, este ticket.

**Onde está agora (depois da entrega):**
`conciliacao_enxuta/cruzamento.py`, em `_por_atributo` (um frame por Atributo, juntados com `pl.concat`). Testes em `tests/test_cruzamento.py`: `test_atributo_com_nome_de_coluna_interna_concilia_normalmente`, `test_linha_sem_chave_que_aparece_antes_numa_data_base_so_de_a_casa_na_primeira_data_base_comum` e `test_valor_com_diferenca_igual_ao_peso_nao_aparece`.
