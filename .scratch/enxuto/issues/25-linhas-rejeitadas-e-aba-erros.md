# 25: Linhas rejeitadas e aba Erros

**What to build:** uma linha com a Data ou o Valor vazio ou ilegível deixa de parar a execução: vira uma Linha rejeitada, com o motivo `Data vazia`, `Data ilegível`, `Valor vazio` ou `Valor ilegível`, e fica fora de tudo (totais, cruzamento, linhas sem Chave e gráficos), inclusive quando não tem Chave. A linha toda vazia (sem Chave, Data e Valor) é ignorada em silêncio. A leitura devolve a base e as Linhas rejeitadas (Linha, Chave, Data e Valor como vieram, em texto, e o Motivo); `conciliar` passa a receber as rejeitadas das duas bases e as devolve no Resultado. Sai a 5ª aba, **Erros**, com as colunas Base, Linha, Chave, Data, Valor e Motivo, as rejeitadas da Base A e depois da Base B, na ordem do arquivo; existe sempre (sem erros, só o cabeçalho), com cabeçalho congelado e filtro, e com o mesmo corte das Operações acima do limite ("Nem todos os erros couberam: mostrando 700.000 de N."). O Resumo avisa "Linhas rejeitadas: N (veja a aba Erros)", com o total das duas bases, só quando houver. Continuam parando só os erros do arquivo inteiro: coluna faltando, formato não suportado e texto ilegível. Ver spec: Solução, Decisões de implementação (Módulos/leitura e cruzamento; Regras/Linha rejeitada; Saída/Resumo item 2 e Erros), Testes/Leitura; histórias 8 e 43.

**Blocked by:** —

**Status:** done

- [x] Leitura: cada motivo gera uma Linha rejeitada com a Linha, a Chave, a Data e o Valor como vieram; a execução segue.
- [x] Leitura: uma linha sem Chave com Data ou Valor ruim é rejeitada e não vira linha sem Chave.
- [x] Leitura: a linha toda vazia é ignorada e não aparece nas rejeitadas.
- [x] Leitura: o número da Linha é o que o usuário vê em `.csv`, `.xlsx` (cabeçalho é a linha 1) e `.parquet` (primeira linha de dados é a 1).
- [x] Seam 1: as Linhas rejeitadas não entram nos totais nem nas linhas sem Chave, e voltam no Resultado com a base.
- [x] Aba `Erros` como 5ª aba, com as colunas, a ordem, o cabeçalho congelado e o filtro; sem erros, só o cabeçalho; com o limite reduzido por parâmetro, o aviso de corte na linha 1 e o cabeçalho na linha 2.
- [x] Resumo: o aviso de Linhas rejeitadas aparece só quando houver, com o total das duas bases.
- [x] Os testes antigos que esperavam a execução parar por Valor ou Data ruim passam a esperar a Linha rejeitada; CLI e GUI continuam funcionando com a nova leitura.
- [x] O gerador de exemplo planta Linhas rejeitadas de cada motivo; o teste de ponta a ponta confere a aba Erros e o aviso contra o gabarito.
- [x] `C:\Users\josef\Projetos\Conciliacao-Enxuta\.venv\Scripts\python -m pytest -q` passa.
- [x] Teste com olhos de usuário: rodar a CLI sobre `exemplo\` e conferir com openpyxl (`PYTHONIOENCODING=utf-8`) que o Excel tem 5 abas, que a aba Erros lista as linhas plantadas com o motivo certo e que o Resumo avisa quantas são.

**Notas de entrega:**
- Seams (escolhidos pela spec, sem acesso ao usuário): `ler_base(caminho) -> (base, rejeitadas)` (Leitura); `conciliar(base_a, base_b, tolerancia, rejeitadas_a=None, rejeitadas_b=None)` devolvendo `Resultado.rejeitadas` (Seam 1); CLI e `gravar_excel(..., limite)` → `.xlsx` lido com openpyxl (Seam 2).
- `leitura.py`: a Data ou o Valor vazio (inclusive só espaço) ou ilegível vira Linha rejeitada (Linha, Chave, Data, Valor como vieram, em texto, e Motivo; a Data tem precedência quando as duas estão ruins) e sai da base; a linha toda vazia (sem Chave, Data e Valor) some em silêncio. O `.xlsx` passa a ser lido com `drop_empty_rows=False`, para a numeração das Linhas ser a que o usuário vê. Só param a execução coluna faltando, formato não suportado e texto ilegível.
- `cruzamento.py`: `rejeitadas_a` e `rejeitadas_b` opcionais (os testes antigos e os dos tickets em paralelo seguem chamando com três argumentos); `Resultado.rejeitadas` com Base, Linha, Chave, Data, Valor e Motivo, A antes de B. O campo foi posto logo depois de `sem_chave_b`, longe do fim da classe, para facilitar a junção com os tickets 19 e 21.
- `excel.py`: 5ª aba `Erros`, sempre presente, com cabeçalho congelado e filtro e o corte pelo mesmo `limite` das Operações ("Nem todos os erros couberam: mostrando N de M." na linha 1). O aviso "Linhas rejeitadas: N (veja a aba Erros)" sai no Resumo antes das Data-bases ignoradas, só quando houver. As Data-bases ignoradas na aba Erros ficaram para o ticket 27.
- `cli.py` e `gui_estado.py`: usam a nova leitura e passam as rejeitadas ao `conciliar`.
- `exemplo.py`: planta no fim da Base A Data vazia, Data ilegível e Valor ilegível (esta sem Chave) e no fim da Base B um Valor vazio; o gabarito ganha `rejeitadas`. No `.parquet`, tipos nativos não guardam texto ilegível, então só a Base B traz a rejeitada.
- Testes: `tests/test_leitura.py` (cada motivo, sem Chave rejeitada, linha toda vazia, número da Linha em `.csv`, `.xlsx` e `.parquet`; os antigos que esperavam parar agora esperam a rejeitada), `tests/test_cruzamento.py` (Seam 1), `tests/test_ponta_a_ponta.py` (aba Erros para cada motivo no lugar dos testes de mensagem de erro, sem erros, corte, gabarito nos 3 formatos; `ABAS` com `Erros`).
- Observação de TDD: os testes da linha toda vazia, do corte da aba Erros e da aba sem erros passaram já na primeira execução, porque a implementação do passo anterior os cobria inteira.
- Teste com olhos de usuário: `python -m conciliacao_enxuta.exemplo exemplo csv` e a CLI sobre `exemplo\`; o Excel tem 5 abas, a aba Erros lista as 4 linhas plantadas com o motivo certo e com o número de linha do arquivo, e o Resumo avisa "Linhas rejeitadas: 4 (veja a aba Erros)".
- Arquivos: `conciliacao_enxuta/leitura.py`, `cruzamento.py`, `excel.py`, `exemplo.py`, `cli.py`, `gui_estado.py`; `tests/test_leitura.py`, `test_cruzamento.py`, `test_ponta_a_ponta.py`.

**Onde está agora (depois da entrega):**
Entregue, sem commit (o orquestrador commita). `pytest -q`: 148 passed.
