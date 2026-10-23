# 25: Linhas rejeitadas e aba Erros

**What to build:** uma linha com a Data ou o Valor vazio ou ilegível deixa de parar a execução: vira uma Linha rejeitada, com o motivo `Data vazia`, `Data ilegível`, `Valor vazio` ou `Valor ilegível`, e fica fora de tudo (totais, cruzamento, linhas sem Chave e gráficos), inclusive quando não tem Chave. A linha toda vazia (sem Chave, Data e Valor) é ignorada em silêncio. A leitura devolve a base e as Linhas rejeitadas (Linha, Chave, Data e Valor como vieram, em texto, e o Motivo); `conciliar` passa a receber as rejeitadas das duas bases e as devolve no Resultado. Sai a 5ª aba, **Erros**, com as colunas Base, Linha, Chave, Data, Valor e Motivo, as rejeitadas da Base A e depois da Base B, na ordem do arquivo; existe sempre (sem erros, só o cabeçalho), com cabeçalho congelado e filtro, e com o mesmo corte das Operações acima do limite ("Nem todos os erros couberam: mostrando 700.000 de N."). O Resumo avisa "Linhas rejeitadas: N (veja a aba Erros)", com o total das duas bases, só quando houver. Continuam parando só os erros do arquivo inteiro: coluna faltando, formato não suportado e texto ilegível. Ver spec: Solução, Decisões de implementação (Módulos/leitura e cruzamento; Regras/Linha rejeitada; Saída/Resumo item 2 e Erros), Testes/Leitura; histórias 8 e 43.

**Blocked by:** —

**Status:** ready-for-agent

- [ ] Leitura: cada motivo gera uma Linha rejeitada com a Linha, a Chave, a Data e o Valor como vieram; a execução segue.
- [ ] Leitura: uma linha sem Chave com Data ou Valor ruim é rejeitada e não vira linha sem Chave.
- [ ] Leitura: a linha toda vazia é ignorada e não aparece nas rejeitadas.
- [ ] Leitura: o número da Linha é o que o usuário vê em `.csv`, `.xlsx` (cabeçalho é a linha 1) e `.parquet` (primeira linha de dados é a 1).
- [ ] Seam 1: as Linhas rejeitadas não entram nos totais nem nas linhas sem Chave, e voltam no Resultado com a base.
- [ ] Aba `Erros` como 5ª aba, com as colunas, a ordem, o cabeçalho congelado e o filtro; sem erros, só o cabeçalho; com o limite reduzido por parâmetro, o aviso de corte na linha 1 e o cabeçalho na linha 2.
- [ ] Resumo: o aviso de Linhas rejeitadas aparece só quando houver, com o total das duas bases.
- [ ] Os testes antigos que esperavam a execução parar por Valor ou Data ruim passam a esperar a Linha rejeitada; CLI e GUI continuam funcionando com a nova leitura.
- [ ] O gerador de exemplo planta Linhas rejeitadas de cada motivo; o teste de ponta a ponta confere a aba Erros e o aviso contra o gabarito.
- [ ] `C:\Users\josef\Projetos\Conciliacao-Enxuta\.venv\Scripts\python -m pytest -q` passa.
- [ ] Teste com olhos de usuário: rodar a CLI sobre `exemplo\` e conferir com openpyxl (`PYTHONIOENCODING=utf-8`) que o Excel tem 5 abas, que a aba Erros lista as linhas plantadas com o motivo certo e que o Resumo avisa quantas são.

**Notas de entrega:**

**Onde está agora (depois da entrega):**
