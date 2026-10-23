# 20: Tipo do Erro Casa com linha sem Chave e coluna Linha sem Chave

**What to build:** o analista fica sabendo quando uma Linha sem Chave tem o valor que zeraria a Diferença de uma Chave. Cada valor de linha sem Chave é comparado uma vez só, na primeira Data-base comum em que aparece entre as linhas sem Chave da sua base (nas seguintes, o mesmo valor é o mesmo lançamento). Nessa Data-base, a linha casa com uma Chave que tinha Diferença quando |Diferença + Valor| ≤ Tolerância (linha na Base A) ou |Diferença − Valor| ≤ Tolerância (linha na Base B). Uma linha para uma Chave, sem combinar linhas; uma linha pode casar com várias Chaves. O Tipo **Casa com linha sem Chave** entra antes de Sem padrão e só aparece nas Chaves com Diferença na Data-base mais recente, mesmo que a Diferença tenha mudado depois. Na aba Operações com Diferença, a coluna **Linha sem Chave** fica entre Aberta desde e os Atributos, em texto como `−10.000,00 em 15/03/2026 na Base B`, várias separadas por `; `, vazia quando não casa. A linha não é juntada à Chave. Ver spec: Solução, Decisões de implementação (Regras/Tipo do Erro e Casa com linha sem Chave; Saída/Operações com Diferença), Fora do escopo; histórias 26, 39, 40 e 41.

**Blocked by:** 18, 19

**Status:** done

- [x] Seam 1: uma linha sem Chave na Base A e outra na Base B casam com a Diferença de uma Chave, cada uma com o seu sinal.
- [x] Seam 1: casa dentro da folga da Tolerância e não casa logo acima dela.
- [x] Seam 1: a comparação é na Data-base em que a linha aparece pela primeira vez, onde a Diferença da Chave era outra; o Tipo aparece na mais recente mesmo com a Diferença mudada.
- [x] Seam 1: o mesmo valor repetido nas Data-bases seguintes não é comparado de novo.
- [x] Seam 1: a Chave sem Diferença naquela Data-base não ganha o Tipo.
- [x] Seam 1: uma linha que casa com duas Chaves dá o Tipo às duas.
- [x] Seam 1: Casa com linha sem Chave convive com os outros Tipos, na ordem da spec, e uma Chave com ele não é Sem padrão; Por Tipo do Erro ganha a linha do novo Tipo.
- [x] Aba `Operações com Diferença`: coluna `Linha sem Chave` depois de Aberta desde, com o valor em reais com sinal, a Data-base comparada e a base; vazia quando não casa.
- [x] O gerador de exemplo planta uma linha sem Chave que casa com a Diferença de uma Chave numa Data-base antiga, e a Diferença dessa Chave muda depois; o teste de ponta a ponta confere o Tipo e a coluna contra o gabarito.
- [x] `C:\Users\josef\Projetos\Conciliacao-Enxuta\.venv\Scripts\python -m pytest -q` passa.
- [x] Teste com olhos de usuário: rodar a CLI sobre `exemplo\` e conferir com openpyxl (`PYTHONIOENCODING=utf-8`) que a Chave plantada mostra Casa com linha sem Chave e que a coluna Linha sem Chave aponta o valor, a data e a base da linha.

**Notas de entrega:**

Seams (escolhidos pela spec, seção Testes): Seam 1 `conciliar` e Seam 2 de ponta a ponta (CLI → `.xlsx` lido com openpyxl).

- `conciliacao_enxuta/cruzamento.py`: nova `_casas`, que pega cada valor de linha sem Chave por base na primeira Data-base comum em que aparece e o compara com as Chaves com Diferença dessa Data-base (Base A: |Diferença + Valor| ≤ Tolerância; Base B: |Diferença − Valor| ≤ Tolerância). `Resultado.operacoes` ganha a coluna `Casa` (lista de Valor em centavos, Data e Base `A`/`B`, em ordem de Data; nula quando não casa). O Tipo `Casa com linha sem Chave` entra depois de Dígitos trocados e antes de Sem padrão; Por Tipo do Erro o conta como os outros.
- `conciliacao_enxuta/excel.py`: coluna `Linha sem Chave` (G) depois de Aberta desde, em texto como `−1.870,10 em 04/05/2026 na Base B`, várias com `; `, vazia quando não casa; os Atributos passam a começar em H.
- `conciliacao_enxuta/exemplo.py`: planta uma linha sem Chave na Base B só em 04/05/2026 (`CASA_DATA`), com o valor da Diferença que a `C00041` tinha nesse dia; a Diferença dela muda depois. O gabarito ganha `linha_sem_chave` (texto esperado da coluna), o Tipo da C00041 vira Casa com linha sem Chave e o Histórico de 04/05 soma a linha.
- `tests/test_cruzamento.py`: 6 testes novos (Base A e B com sinais, folga da Tolerância, Data-base antiga com Diferença mudada, valor repetido não comparado de novo, Chave sem Diferença naquela Data-base, linha que casa com duas Chaves e Chave com duas linhas, convivência com Só em A e Por Tipo); colunas de `operacoes` com `Casa`.
- `tests/test_ponta_a_ponta.py`: 2 testes novos (formato da coluna com duas linhas e vazia; a Chave plantada do exemplo contra o gabarito, com a Diferença de hoje diferente do valor da linha); cabeçalhos, faixas do filtro e índices dos Atributos ajustados para a coluna nova; Por Tipo espera o novo Tipo.
- Os testes do Seam 1 depois do primeiro passaram de primeira, porque a primeira implementação já cobria a regra inteira; conferi que falham com duas mutações (`<=` → `<` na Tolerância e comparar o valor em toda Data-base).
- Teste com olhos de usuário: CLI sobre `exemplo\` (csv) e openpyxl: a C00041 mostra `Casa com linha sem Chave` e `−1.870,10 em 04/05/2026 na Base B`, com Diferença absoluta de hoje 2.226,16; Por Tipo do Erro tem a linha `Casa com linha sem Chave | 1 | 2.226,16`.
- pytest: 145 passed.

**Onde está agora (depois da entrega):**
