# 03: Bases em .xlsx e .parquet

**What to build:** o analista usa o arquivo que o sistema exporta: Base A e Base B podem ser `.csv`, `.xlsx` ou `.parquet`, inclusive misturados (A em `.xlsx`, B em `.parquet`), com o mesmo resultado que teriam em `.csv`. Uma extensão não suportada dá uma mensagem simples. Ver spec: Decisões de implementação (Módulos/`leitura`, Técnico), Notas; história 4.

**Blocked by:** 02

**Status:** ready-for-agent

- [ ] As mesmas bases salvas em `.csv`, `.xlsx` e `.parquet` produzem o mesmo Resumo.
- [ ] No `.xlsx`, Valor numérico e Data como data do Excel são lidos certo; Chave numérica vira texto sem `.0` no fim.
- [ ] Um arquivo com extensão diferente dessas três dá uma mensagem em linguagem simples com o nome do arquivo, sem traceback.
- [ ] O teste de ponta a ponta roda o gerador de exemplo nos três formatos e confere contra o gabarito.
- [ ] `C:\Users\josef\Projetos\Desafio-Conciliacao\.venv\Scripts\python -m pytest -q` passa.
- [ ] Teste com olhos de usuário: gravar em `exemplo\` a Base A em `.xlsx` e a Base B em `.parquet`, rodar a CLI e conferir no `.xlsx` de saída (openpyxl, `PYTHONIOENCODING=utf-8`) que o Resumo é igual ao da rodada com `.csv`.

**Notas de entrega:**

**Onde está agora (depois da entrega):**
