# 18: Linhas sem Chave nos totais, na Diferença de cada Data-base e no gráfico

**What to build:** hoje a Linha sem Chave só é contada e somada no aviso do Resumo. Passa a ser uma Diferença do valor inteiro na sua Data-base: +Valor na Base A, −Valor na Base B, uma linha por vez, sem somar uma com outra, e conta como Diferença quando |Valor| > Tolerância. Na Data-base mais recente ela entra no Total A, no Total B, na Diferença total e na Diferença absoluta; em cada Data-base comum, entra na Diferença absoluta do gráfico da Diferença no tempo. Não entra em Chaves com Diferença, Por Tipo do Erro, Por Atributo nem nas Operações com Diferença, e só vale nas Data-bases comuns. O aviso das linhas sem Chave por base continua como está. Ver spec: Solução, Decisões de implementação (Regras/Preparação, Linhas sem Chave e Invariante; Saída/Resumo item 1); histórias 12, 37 e 38.

**Blocked by:** —

**Status:** done

- [x] Seam 1: Total A e Total B da Data-base mais recente incluem as linhas sem Chave das duas bases.
- [x] Seam 1: uma linha sem Chave na Base A soma +Valor e uma na Base B soma −Valor na Diferença total; as duas somam |Valor| na Diferença absoluta.
- [x] Seam 1: uma linha sem Chave com |Valor| ≤ Tolerância não entra na Diferença total nem na absoluta, mas continua nos Totais.
- [x] Seam 1: duas linhas sem Chave que se anulariam (ex.: +100 e −100 na mesma base) contam cada uma na Diferença absoluta.
- [x] Seam 1: o Histórico da Diferença inclui as linhas sem Chave de cada Data-base comum; as de Data-bases que não são comuns não entram em nada.
- [x] Seam 1: Chaves com Diferença, Por Tipo do Erro, Por Atributo e Operações não mudam com as linhas sem Chave.
- [x] Seam 1: a invariante vale com as linhas sem Chave (Total A − Total B = Diferença total + soma das Diferenças dentro da Tolerância).
- [x] O gabarito do gerador de exemplo passa a somar as linhas sem Chave nos totais e no histórico; o teste de ponta a ponta confere o quadro do Resumo e os dados do gráfico em `_grafico`.
- [x] `C:\Users\josef\Projetos\Conciliacao-Enxuta\.venv\Scripts\python -m pytest -q` passa.
- [x] Teste com olhos de usuário: rodar a CLI sobre `exemplo\` e conferir com openpyxl (`PYTHONIOENCODING=utf-8`) que o Total A e o Total B do Resumo batem com a soma de cada arquivo na Data-base mais recente e que a Diferença absoluta inclui as linhas sem Chave.

**Notas de entrega:**
- Seams (escolhidos pela spec, seção Testes): Seam 1 `conciliar` com DataFrames pequenos; Seam 2 ponta a ponta (CLI → `.xlsx` lido com openpyxl, contra o gabarito do gerador).
- `conciliacao_enxuta/cruzamento.py`: em `conciliar`, as linhas sem Chave viram Diferenças soltas (+Valor em A, −Valor em B, uma por linha, só as com |Valor| > Tolerância). Entram na Diferença total e na absoluta da Data-base mais recente e na Diferença absoluta de cada Data-base comum do Histórico; Total A e Total B somam as linhas sem Chave da Data-base mais recente. Chaves com Diferença, Por Tipo, Por Atributo e Operações não mudam. As Data-bases comuns continuam vindo só das linhas com Chave.
- `conciliacao_enxuta/exemplo.py`: `DIFERENCAS_SEM_CHAVE`; o gabarito soma as linhas sem Chave nos totais, na Diferença total e absoluta e no Histórico.
- `tests/test_cruzamento.py`: 7 testes novos (totais, sinal por base, Tolerância, as que se anulariam, Histórico e Data-bases não comuns, nada muda em Chaves/Tipo/Atributo/Operações, invariante). O teste antigo que dizia que as linhas sem Chave ficavam fora dos totais e da Diferença foi reduzido ao que ainda vale (fora do cruzamento, contadas no aviso).
- `tests/test_ponta_a_ponta.py`: os testes do quadro do Resumo e de `_grafico` já conferiam contra o gabarito e ficaram vermelhos até o gabarito mudar. A asserção "a soma das faixas de Idade é a Diferença absoluta" passou a descontar as linhas sem Chave, porque a Idade delas é o ticket 24, que deve voltar a asserção ao original.
- Teste com olhos de usuário: CLI sobre `exemplo\`; Total A 25.485.021,49 e Total B 441.870.284,80 batem com a soma de cada arquivo em 30/09/2026; Diferença absoluta 688.281.380,19 = soma das Operações (688.280.459,74) + 123,45 + 20,00 + 777,00 das linhas sem Chave; o último ponto de `_grafico` tem o mesmo valor.
- pytest: 137 passed.

**Onde está agora (depois da entrega):**
