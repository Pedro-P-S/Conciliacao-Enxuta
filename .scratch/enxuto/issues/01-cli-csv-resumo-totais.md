# 01: Pela linha de comando, dois CSV viram um Excel com o Resumo dos totais

**What to build:** o primeiro caminho completo, de ponta a ponta. O analista roda `python -m conciliacao_enxuta conciliar BASE_A BASE_B [--tolerancia 1,00] [--saida PASTA]` com dois `.csv` que têm as colunas `Chave`, `Data` e `Valor` (nomes exatos, valores simples como `1234.56`, uma única Data-base) e recebe `conciliacao_AAAA-MM-DD.xlsx` na pasta da Base A (ou em `--saida`), com a aba **Resumo**: Data-base mais recente, Tolerância, Total A, Total B, Diferença total, Diferença absoluta e Chaves com Diferença. Cruzamento por junção completa pela Chave, Diferença = A − B com o lado que falta valendo 0, e uma Chave tem Diferença quando |Diferença| > Tolerância (inclusive Só em A e Só em B). Cria o pacote `conciliacao_enxuta` com os módulos `leitura`, `cruzamento` (seam `conciliar(base_a, base_b, tolerancia)` devolvendo um Resultado), `excel` e `cli`, e um gerador de bases de exemplo com gabarito, que também preenche a pasta `exemplo\` (no `.gitignore`, ainda inexistente neste worktree). Ver spec: Solução, Decisões de implementação (Módulos, Cruzamento por Data-base, Invariante, Saída/Arquivo, Saída/Resumo, Interface/CLI, Técnico) e Testes; histórias 13, 14, 15, 16, 33 e 36.

**Blocked by:** —

**Status:** ready-for-agent

- [ ] `conciliar` recebe os dois DataFrames lidos e a Tolerância em centavos e devolve um Resultado com Total A, Total B, Diferença total, Diferença absoluta e Chaves com Diferença da Data-base mais recente; dinheiro sempre em centavos `Int64`.
- [ ] Testes da seam 1 (DataFrames montados no teste): junção completa, lado ausente = 0, Tolerância como `>` estrito (diferença igual à Tolerância não conta), Tolerância também em Chaves Só em A e Só em B.
- [ ] Teste da seam 1 da invariante: Total A − Total B = Diferença total das Chaves com Diferença + soma das Diferenças dentro da Tolerância.
- [ ] A Diferença absoluta e a Diferença total aparecem separadas, e um teste mostra um caso em que positivas e negativas se anulam na total e não na absoluta.
- [ ] O arquivo sai como `conciliacao_AAAA-MM-DD.xlsx` (Data-base mais recente), na pasta da Base A por padrão ou na pasta de `--saida`, sobrescrevendo se já existir; a CLI imprime o caminho do resultado.
- [ ] `--tolerancia` aceita o formato brasileiro (`1,00`, `0,50`) e o padrão é 1,00.
- [ ] No Resumo os valores em reais têm o formato `#.##0,00` (convertidos de centavos só no Excel).
- [ ] Gerador de bases de exemplo com gabarito (totais e Chaves com Diferença esperados); teste de ponta a ponta (seam 2) gera os arquivos, roda a CLI, lê o `.xlsx` com openpyxl e confere o Resumo contra o gabarito.
- [ ] Nada é importado do pacote do projeto grande; peças copiadas e adaptadas são aceitas.
- [ ] `C:\Users\josef\Projetos\Desafio-Conciliacao\.venv\Scripts\python -m pytest -q` passa.
- [ ] Teste com olhos de usuário: criar `exemplo\` com o gerador (Base A e Base B em `.csv`), rodar a CLI sobre eles, abrir o `.xlsx` gerado com openpyxl (com `PYTHONIOENCODING=utf-8`) e conferir que o Resumo mostra os totais esperados e o caminho impresso é o da pasta da Base A.

**Notas de entrega:**

**Onde está agora (depois da entrega):**
