# 05: Linhas sem Chave e Chaves repetidas

**What to build:** a Preparação antes do cruzamento. Linhas sem Chave (vazia ou só espaço) ficam fora do cruzamento, e o Resumo avisa, por base, quantas são e quanto somam. Linhas com a mesma Chave e a mesma Data-base são somadas numa só. Ver spec: Decisões de implementação (Regras/Preparação, Saída/Resumo — avisos); histórias 11 e 12.

**Blocked by:** 01

**Status:** done

- [x] Seam 1: duas linhas da mesma Chave na mesma Data-base viram uma, com o Valor somado, antes de comparar com a outra base.
- [x] Seam 1: linhas sem Chave não entram nos totais nem nas Chaves com Diferença; o Resultado traz, por base, a quantidade e a soma delas.
- [x] Resumo: o aviso de linhas sem Chave aparece só quando há alguma, com a quantidade e a soma (em reais, `#.##0,00`) de cada base; sem linhas sem Chave, nenhum aviso.
- [x] A invariante continua valendo com Chaves repetidas.
- [x] O gerador de exemplo planta Chaves repetidas e linhas sem Chave; o teste de ponta a ponta confere o aviso e os totais contra o gabarito.
- [x] `C:\Users\josef\Projetos\Conciliacao-Enxuta\.venv\Scripts\python -m pytest -q` passa.
- [x] Teste com olhos de usuário: regenerar `exemplo\` com linhas sem Chave e uma Chave repetida, rodar a CLI e conferir no Resumo (openpyxl, `PYTHONIOENCODING=utf-8`) o aviso com quantidade e soma por base e os totais com a Chave repetida somada.

**Notas de entrega:**
- `cruzamento.py`: nova Preparação (`_preparar`) antes do cruzamento. Tira as linhas sem Chave (nula, vazia ou só espaço) e soma numa só as linhas de mesma Chave e Data-base. O `Resultado` ganhou `sem_chave_a` e `sem_chave_b`, do tipo `SemChave(linhas, soma)`, com a soma em centavos. A contagem e a soma pegam o arquivo inteiro, todas as Data-bases. O ticket 06 pode rever isso, se o aviso tiver de olhar só a mais recente.
- `excel.py`: só quando há alguma linha sem Chave, o Resumo ganha, uma linha abaixo do quadro, o bloco "Linhas sem Chave, fora do cruzamento" com as colunas Linhas e Soma e uma linha para a Base A e outra para a Base B. A Soma vai em `#.##0,00`. Também ganhou a constante `FORMATO_INTEIRO`.
- `exemplo.py`: o gerador grava C00005 e C00011 em duas linhas na Base A, e C00006 e C00021 em duas linhas na Base B. Em cada base, uma dessas Chaves tem Diferença e a outra não. Também planta 2 linhas sem Chave em A (uma vazia e uma só com espaço) e 1 em B. O `Gabarito` ganhou `sem_chave_a` e `sem_chave_b`.
- Testes: na Seam 1 (`tests/test_cruzamento.py`), Chaves repetidas somadas, linhas sem Chave fora do cruzamento e contadas, contagem zero sem elas e a invariante com Chaves repetidas. Na Seam 2 (`tests/test_ponta_a_ponta.py`), o aviso e os totais conferidos contra o gabarito, e nenhum aviso quando não há linha sem Chave.
- Teste com olhos de usuário: regenerei `exemplo\`, rodei a CLI e conferi o Resumo com openpyxl. O aviso mostra Base A com 2 linhas e soma 103,45, e Base B com 1 linha e soma 777,00. Os totais batem com o gabarito, com as Chaves repetidas somadas.

**Onde está agora (depois da entrega):**
