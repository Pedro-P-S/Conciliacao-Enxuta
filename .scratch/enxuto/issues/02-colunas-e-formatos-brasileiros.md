# 02: Nomes de coluna flexíveis, valores e datas no formato brasileiro

**What to build:** o analista não precisa ajustar o arquivo exportado. As colunas `Chave`, `Data` e `Valor` são reconhecidas sem diferenciar maiúscula, acento e espaço nas pontas (`CHAVE`, ` data `, `valor`); a Chave vira texto sem espaço nas pontas; o Valor aceita `1.234,56`, `(1.234,56)` (negativo), `-1.234,56` e `R$ 1.234,56`; a Data aceita `DD/MM/AAAA`, `AAAA-MM-DD` e data do Excel. Ver spec: Decisões de implementação (Módulos/`leitura`), Notas (peças que podem ser copiadas do projeto grande); histórias 1, 2, 5 e 6.

**Blocked by:** 01

**Status:** done

- [x] Arquivos com `CHAVE`, `Data ` e `VALOR` (e variações de acento e espaço nas pontas) são lidos como se tivessem os nomes exatos.
- [x] Valores `1.234,56`, `(1.234,56)`, `-1.234,56`, `R$ 1.234,56` e `1234,5` viram os centavos certos (`Int64`), sem passar por float com arredondamento errado.
- [x] Datas `31/01/2026`, `2026-01-31` e data do Excel viram a mesma Data-base.
- [x] A Chave é lida como texto e sem espaço nas pontas, de modo que ` 123 ` em A cruza com `123` em B.
- [x] O gerador de exemplo passa a escrever as bases com valores e datas no formato brasileiro e nomes de coluna com variações; o teste de ponta a ponta confere o Resumo contra o gabarito.
- [x] `C:\Users\josef\Projetos\Desafio-Conciliacao\.venv\Scripts\python -m pytest -q` passa.
- [x] Teste com olhos de usuário: regenerar `exemplo\` com valores como `R$ 1.234,56` e `(500,00)`, datas `DD/MM/AAAA` e cabeçalhos `CHAVE`/`data`/`Valor `, rodar a CLI e conferir no `.xlsx` (lido com openpyxl, `PYTHONIOENCODING=utf-8`) que os totais do Resumo batem com a soma feita à mão.

**Notas de entrega:**
- `leitura.ler_base`: as colunas `Chave`, `Data` e `Valor` são reconhecidas sem diferenciar maiúscula, acento, espaço nas pontas e BOM. A Chave vira texto sem espaço nas pontas. O Valor aceita `1.234,56`, `(1.234,56)`, `-1.234,56`, `R$ 1.234,56`, `1234,5` e ainda `1234.56`, e vira centavos via `Decimal`, sem float. A Data aceita `DD/MM/AAAA`, `AAAA-MM-DD` e a data do Excel (`46053`).
- Duas decisões além do texto do ticket:
  - O `.csv` pode vir separado por `;` (o padrão do Excel no Brasil, necessário com vírgula decimal) ou por `,`. O separador é escolhido pelo cabeçalho.
  - Sem vírgula, o ponto é milhar quando separa grupos de 3 dígitos (`1.234` = R$ 1.234,00); nos outros casos é decimal.
- Uma Data ilegível dá `ValueError` com o nome do arquivo e o conteúdo, em vez de sumir do cruzamento. A mensagem completa, com a linha, fica para o ticket 04. Um Valor ilegível continua dando o erro do Polars, também a cargo do ticket 04. Casas além da segunda não são tratadas: o `Decimal(38, 2)` as descarta sem avisar.
- `exemplo.py`: o gerador grava `;` com BOM e valores negativos. A Base A sai com o cabeçalho `CHAVE;data;Valor `, valores `R$ 1.234,56`/`(500,00)` e datas `DD/MM/AAAA`. A Base B sai com ` Chave;DATA;VALOR`, valores `-1234,56`, data do Excel e Chaves com espaço nas pontas. O teste de ponta a ponta existente confere o Resumo contra o gabarito.
- Teste com olhos de usuário: regenerei `exemplo\`, rodei a CLI e li o `.xlsx` com openpyxl. Total A 4.037.564,20, Total B 3.991.495,82, Diferença total 46.064,72, Diferença absoluta 2.101.968,04 e 60 Chaves com Diferença: tudo bate com a soma à mão dos `.csv`.
- Arquivos alterados: `conciliacao_enxuta/leitura.py`, `conciliacao_enxuta/exemplo.py` e `tests/test_leitura.py`. O pytest dá 37 passed.

**Onde está agora (depois da entrega):**
