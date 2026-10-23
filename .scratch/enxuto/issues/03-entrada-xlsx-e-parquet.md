# 03: Bases em .xlsx e .parquet

**What to build:** o analista usa o arquivo que o sistema exporta: Base A e Base B podem ser `.csv`, `.xlsx` ou `.parquet`, inclusive misturados (A em `.xlsx`, B em `.parquet`), com o mesmo resultado que teriam em `.csv`. Uma extensão não suportada dá uma mensagem simples. Ver spec: Decisões de implementação (Módulos/`leitura`, Técnico), Notas; história 4.

**Blocked by:** 02

**Status:** done

- [x] As mesmas bases salvas em `.csv`, `.xlsx` e `.parquet` produzem o mesmo Resumo.
- [x] No `.xlsx`, Valor numérico e Data como data do Excel são lidos certo; Chave numérica vira texto sem `.0` no fim.
- [x] Um arquivo com extensão diferente dessas três dá uma mensagem em linguagem simples com o nome do arquivo, sem traceback.
- [x] O teste de ponta a ponta roda o gerador de exemplo nos três formatos e confere contra o gabarito.
- [x] `C:\Users\josef\Projetos\Conciliacao-Enxuta\.venv\Scripts\python -m pytest -q` passa.
- [x] Teste com olhos de usuário: gravar em `exemplo\` a Base A em `.xlsx` e a Base B em `.parquet`, rodar a CLI e conferir no `.xlsx` de saída (openpyxl, `PYTHONIOENCODING=utf-8`) que o Resumo é igual ao da rodada com `.csv`.

**Notas de entrega:**
- `leitura.ler_base` lê `.csv` (todo texto, como antes), `.xlsx` (primeira aba) e `.parquet` com os tipos nativos. Valor numérico vira centavos sem passar pelo parse brasileiro, então um `2.125` não vira milhar. Data nativa fica data, e número na coluna Data é a data do Excel. Chave numérica vira texto sem `.0`.
- No `.xlsx`, o tipo da coluna sai de todas as linhas (`infer_schema_length=None`). Com a amostra padrão, um texto depois de 100 linhas numéricas virava vazio e a linha sumia sem aviso. Uma coluna de tipos misturados vem como texto, e `_data` passou a aceitar também `AAAA-MM-DD HH:MM:SS`, que é como vem a data nativa nesse caso.
- Limite conhecido: numa coluna de Valor com número e texto misturados, um número com exatamente 3 casas decimais (`2.125`) é lido como milhar. Em coluna só numérica isso não acontece.
- Extensão fora das três dá `FormatoNaoSuportado` (um `ValueError`), e a CLI mostra `<arquivo>: formato não suportado. Use .csv, .xlsx ou .parquet.` e sai com 1, sem traceback e sem gerar `.xlsx`.
- O gerador de exemplo ganhou o parâmetro `formato` (`csv`, `xlsx` ou `parquet`), também na linha de comando: `python -m conciliacao_enxuta.exemplo [PASTA] [FORMATO]`. Em `.xlsx` e `.parquet`, a Data vai como data e o Valor como número em reais. As bases e o gabarito são os mesmos.
- Testes: leitura de `.xlsx` (Chave numérica, Data do Excel, Valor numérico), `.parquet` e `.xlsx` com tipos misturados; de ponta a ponta, os três formatos contra o gabarito, A em `.xlsx` com B em `.parquet` dando o mesmo Resumo que em `.csv`, e a extensão não suportada.
- Teste com olhos de usuário: `exemplo\base_a.xlsx` e `exemplo\base_b.parquet` pela CLI deram o Resumo igual, célula a célula, ao da rodada com `exemplo\csv\`. Um `.ods` deu a mensagem simples, com código 1.
- Arquivos: `conciliacao_enxuta/leitura.py`, `conciliacao_enxuta/cli.py`, `conciliacao_enxuta/exemplo.py`, `tests/test_leitura.py`, `tests/test_ponta_a_ponta.py`.

**Onde está agora (depois da entrega):**
