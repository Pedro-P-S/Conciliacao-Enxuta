# 01: Pela linha de comando, dois CSV viram um Excel com o Resumo dos totais

**What to build:** o primeiro caminho completo, de ponta a ponta. O analista roda `python -m conciliacao_enxuta conciliar BASE_A BASE_B [--tolerancia 1,00] [--saida PASTA]` com dois `.csv` que têm as colunas `Chave`, `Data` e `Valor` (nomes exatos, valores simples como `1234.56`, uma única Data-base) e recebe `conciliacao_AAAA-MM-DD.xlsx` na pasta da Base A (ou em `--saida`), com a aba **Resumo**: Data-base mais recente, Tolerância, Total A, Total B, Diferença total, Diferença absoluta e Chaves com Diferença. Cruzamento por junção completa pela Chave, Diferença = A − B com o lado que falta valendo 0, e uma Chave tem Diferença quando |Diferença| > Tolerância (inclusive Só em A e Só em B). Cria o pacote `conciliacao_enxuta` com os módulos `leitura`, `cruzamento` (seam `conciliar(base_a, base_b, tolerancia)` devolvendo um Resultado), `excel` e `cli`, e um gerador de bases de exemplo com gabarito, que também preenche a pasta `exemplo\` (no `.gitignore`, ainda inexistente neste worktree). Ver spec: Solução, Decisões de implementação (Módulos, Cruzamento por Data-base, Invariante, Saída/Arquivo, Saída/Resumo, Interface/CLI, Técnico) e Testes; histórias 13, 14, 15, 16, 33 e 36.

**Blocked by:** —

**Status:** done

- [x] `conciliar` recebe os dois DataFrames lidos e a Tolerância em centavos e devolve um Resultado com Total A, Total B, Diferença total, Diferença absoluta e Chaves com Diferença da Data-base mais recente; dinheiro sempre em centavos `Int64`.
- [x] Testes da seam 1 (DataFrames montados no teste): junção completa, lado ausente = 0, Tolerância como `>` estrito (diferença igual à Tolerância não conta), Tolerância também em Chaves Só em A e Só em B.
- [x] Teste da seam 1 da invariante: Total A − Total B = Diferença total das Chaves com Diferença + soma das Diferenças dentro da Tolerância.
- [x] A Diferença absoluta e a Diferença total aparecem separadas, e um teste mostra um caso em que positivas e negativas se anulam na total e não na absoluta.
- [x] O arquivo sai como `conciliacao_AAAA-MM-DD.xlsx` (Data-base mais recente), na pasta da Base A por padrão ou na pasta de `--saida`, sobrescrevendo se já existir; a CLI imprime o caminho do resultado.
- [x] `--tolerancia` aceita o formato brasileiro (`1,00`, `0,50`) e o padrão é 1,00.
- [x] No Resumo os valores em reais têm o formato `#.##0,00` (convertidos de centavos só no Excel).
- [x] Gerador de bases de exemplo com gabarito (totais e Chaves com Diferença esperados); teste de ponta a ponta (seam 2) gera os arquivos, roda a CLI, lê o `.xlsx` com openpyxl e confere o Resumo contra o gabarito.
- [x] Nada é importado do pacote do projeto grande; peças copiadas e adaptadas são aceitas.
- [x] `C:\Users\josef\Projetos\Desafio-Conciliacao\.venv\Scripts\python -m pytest -q` passa.
- [x] Teste com olhos de usuário: criar `exemplo\` com o gerador (Base A e Base B em `.csv`), rodar a CLI sobre eles, abrir o `.xlsx` gerado com openpyxl (com `PYTHONIOENCODING=utf-8`) e conferir que o Resumo mostra os totais esperados e o caminho impresso é o da pasta da Base A.

**Notas de entrega:**

- Pacote `conciliacao_enxuta` criado com `leitura` (`ler_base`: `.csv` com `Chave`, `Data` AAAA-MM-DD e `Valor` como `1234.56`, convertido para centavos via Decimal, sem float), `cruzamento` (`conciliar(base_a, base_b, tolerancia)` devolve o `Resultado` com os totais em centavos; usa a maior Data-base comum, que com uma só Data-base é ela mesma; `TOLERANCIA_PADRAO = 100`), `excel` (`gravar_excel`: aba Resumo em `conciliacao_AAAA-MM-DD.xlsx`, sobrescrevendo), `cli` (`conciliar BASE_A BASE_B [--tolerancia 1,00] [--saida PASTA]`, imprime o caminho), `__main__` e `exemplo` (`gerar_bases_exemplo(pasta)` com Diferenças plantadas e `Gabarito`; `python -m conciliacao_enxuta.exemplo [PASTA]` preenche `exemplo\`).
- Diferença total e Diferença absoluta somam só as Chaves com Diferença (|Diferença| > Tolerância), como pede a invariante.
- Formato dos reais: o código gravado no `.xlsx` é `#,##0.00`, que é como o arquivo guarda o formato; o Excel em português o mostra como `#.##0,00`. Gravar `#.##0,00` literalmente seria errado. Data-base com `DD/MM/YYYY`.
- `--tolerancia` aceita vírgula ou ponto e recusa valor negativo, não numérico ou não finito com "Tolerância inválida" (um negativo precisa ser passado como `--tolerancia=-1`, regra do argparse).
- Code review (Standards e Spec): sem falta nem scope creep. Corrigidos: Valor passava por float, Tolerância negativa aceita, padrão de Tolerância duplicado, nomes em inglês no gerador e parâmetros sem uso. Não aplicados: dividir o teste de ponta a ponta em vários e fazer o `Gabarito` reusar o `Resultado`.
- Teste com olhos de usuário: `exemplo\` gerado, a CLI imprimiu `exemplo\conciliacao_2026-09-30.xlsx` (pasta da Base A) e o Resumo bateu com o gabarito (Total A 9.043.336,04; Total B 8.944.015,02; Diferença total 99.316,49; Diferença absoluta 1.918.140,77; 60 Chaves com Diferença).
- Arquivos: `pytest.ini`, `conciliacao_enxuta/__init__.py`, `__main__.py`, `cli.py`, `cruzamento.py`, `excel.py`, `exemplo.py`, `leitura.py`, `tests/test_cruzamento.py`, `tests/test_leitura.py`, `tests/test_ponta_a_ponta.py`.
- pytest: 16 passed.

**Onde está agora (depois da entrega):**
