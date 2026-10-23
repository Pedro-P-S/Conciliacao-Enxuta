# 24: Idade da linha sem Chave

**What to build:** uma Linha sem Chave com Diferença na Data-base mais recente também tem Idade. O mesmo valor nas Data-bases seguintes é o mesmo lançamento, então ela conta desde a primeira Data-base de uma sequência contínua em que esse valor aparece entre as linhas sem Chave da sua base, até a mais recente; se o valor some e volta, conta da volta. Ela entra na Diferença absoluta da sua faixa, e o rótulo da faixa ganha a quantidade de linhas sem Chave quando houver, como `91 a 365 dias (12 Chaves, 1 linha sem Chave)`. Assim, a soma das faixas é a Diferença absoluta do Resumo. Ver spec: Decisões de implementação (Regras/Linhas sem Chave e Idade; Saída/Resumo item 4); história 17.

**Blocked by:** 18, 23

**Status:** done

- [x] Seam 1: o mesmo valor sem Chave repetido nas Data-bases seguintes conta desde a primeira em que apareceu.
- [x] Seam 1: um valor sem Chave que some e volta conta desde a volta.
- [x] Seam 1: cada faixa traz as Chaves, as linhas sem Chave e a Diferença absoluta com as duas; a soma das faixas é a Diferença absoluta do Resumo.
- [x] Seam 1: linha sem Chave dentro da Tolerância não entra na Idade.
- [x] Rótulo das barras: `(N Chaves, M linhas sem Chave)` quando houver, com singular e plural certos; sem linhas sem Chave, o rótulo não muda.
- [x] O gabarito do gerador de exemplo inclui as linhas sem Chave nas faixas; o teste de ponta a ponta confere.
- [x] `C:\Users\josef\Projetos\Conciliacao-Enxuta\.venv\Scripts\python -m pytest -q` passa.
- [x] Teste com olhos de usuário: rodar a CLI sobre `exemplo\` e conferir com openpyxl (`PYTHONIOENCODING=utf-8`) que a soma das barras em `_grafico` é a Diferença absoluta do Resumo e que a faixa das linhas sem Chave mostra quantas são no rótulo.

**Notas de entrega:**
Seams (escolhidos pela spec, seção Testes): Seam 1 `conciliar(...).por_idade` com DataFrames pequenos; Seam 2 CLI → `.xlsx`, lendo `_grafico` com openpyxl contra o gabarito do gerador.

- `Resultado.por_idade` passa a ser `(Faixa, Chaves, Linhas sem Chave, Diferença absoluta das duas)`. Cada linha sem Chave acima da Tolerância na Data-base mais recente ganha um Desde: o lançamento é (base, valor), e o Desde vem do mesmo `_aberta_desde` das Chaves (sequência contínua até a mais recente; some e volta conta da volta). A soma das faixas é a Diferença absoluta do Resumo.
- As `soltas` em `conciliar` ganharam a coluna Base e o filtro das Data-bases comuns (o histórico já só usava as comuns).
- Rótulo das barras: `(N Chaves, M linhas sem Chave)` com singular/plural; sem linhas sem Chave, igual a antes.
- Gabarito do gerador: as 3 linhas sem Chave (repetidas desde a primeira Data-base) caem em 91 a 365 dias.
- A conferência do ticket 18 em `test_resumo_nao_tem_tabela_de_idade_e_os_avisos_vem_logo_abaixo_do_quadro` voltou ao original: soma das faixas = Diferença absoluta, sem desconto.
- Os testes de "some e volta", soma das faixas/Tolerância e o rótulo no singular passaram de primeira, porque a implementação reaproveita o `_aberta_desde` e o rótulo foi escrito junto com o plural.
- Uma linha sem Chave numa Data-base que só tem linhas sem Chave em uma base não faz dela Data-base comum (regra já existente); o teste usa uma Chave sem Diferença para tornar a data comum.
- Olhos de usuário: CLI sobre `exemplo\`; a soma das barras em `_grafico` (688.281.380,19) é a Diferença absoluta do Resumo, e a faixa mostra `91 a 365 dias (138 Chaves, 3 linhas sem Chave)`.
- pytest: 187 passed.

Arquivos: `conciliacao_enxuta/cruzamento.py`, `conciliacao_enxuta/excel.py`, `conciliacao_enxuta/exemplo.py`, `tests/test_cruzamento.py`, `tests/test_ponta_a_ponta.py`.

**Onde está agora (depois da entrega):**
O gráfico de barras da Idade no Resumo inclui as linhas sem Chave: a soma das faixas é a Diferença absoluta, e o rótulo diz quantas linhas sem Chave há em cada faixa.
