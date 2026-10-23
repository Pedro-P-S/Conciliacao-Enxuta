# 26: Valor com mais de 2 casas, caractere estranho e Atributo com qualquer conteúdo

**What to build:** um Valor com mais de 2 casas é arredondado para centavos, com o meio para longe do zero, tanto em texto quanto numérico, e não rejeitado. Continuam aceitos o formato brasileiro, `R$`, parênteses e sinal de menos; qualquer outro caractere (ex.: `abc`, `#`) torna o Valor ilegível e rejeita a linha. O Atributo aceita qualquer conteúdo (número, letra, símbolo) e vira texto, vazio vira nulo, e nunca rejeita a linha nem para a execução. Ver spec: Decisões de implementação (Regras/Valor e Atributo), Testes/Leitura; histórias 5, 44 e 45.

**Blocked by:** 25

**Status:** done

- [x] Leitura: `1.234,567`, `1234.565` e `-0,005` em texto viram centavos arredondados com o meio para longe do zero; o mesmo com o Valor numérico do `.xlsx` e do `.parquet`.
- [x] Leitura: `abc`, `#` e `12a` viram Linha rejeitada com `Valor ilegível`.
- [x] Leitura: os formatos já aceitos continuam iguais (`R$ 1.234,56`, `(1.234,56)`, `-1.234,56`, `1.234`).
- [x] Leitura: um Atributo com número, letra, símbolo e vazio, nos três formatos de arquivo, vira texto ou nulo e não rejeita a linha.
- [x] `C:\Users\josef\Projetos\Conciliacao-Enxuta\.venv\Scripts\python -m pytest -q` passa.
- [x] Teste com olhos de usuário: copiar uma base de `exemplo\`, pôr um Valor com 3 casas, um `#` no Valor e um símbolo num Atributo, rodar a CLI e conferir com openpyxl (`PYTHONIOENCODING=utf-8`) que o Valor de 3 casas entra arredondado, que o `#` aparece na aba Erros e que o Atributo aparece como veio.

**Notas de entrega:**
Seam testada: `ler_base` (Testes/Leitura da spec, arquivos pequenos em `tmp_path`), escolhida pela spec sem consulta ao usuário.

- Valor em texto: o Decimal passou de 2 para 10 casas e o arredondamento para centavos é explícito, com o meio para longe do zero (antes `1234.565` virava 123456 e `-0,005` virava 0).
- Valor em texto: só passa dígito, ponto e vírgula, com um `-` na frente ou entre parênteses (depois de tirar `R$` e espaços). Antes `--5` virava R$ 5,00 positivo e `(5` e `5)` viravam 5; agora são `Valor ilegível`. `abc`, `#` e `12a` já eram rejeitados; ficaram com teste.
- Valor numérico do `.xlsx` e do `.parquet` com 3 casas já arredondava certo; ficou com teste de regressão.
- Atributo: número, letra, símbolo e vazio já viravam texto ou nulo nos três formatos (agora com teste). Uma coluna de lista ou de duração no `.parquet` parava a leitura com erro do polars; agora vira texto pelo `str` do Python.
- Olhos de usuário: cópia de `exemplo\` com `Z99999;30/09/2026;1.234,567;#@! Símbolo` e `Z99998;30/09/2026;#`. Na aba Operações com Diferença, Z99999 aparece com 1234,57 e Produto `#@! Símbolo`; na aba Erros, Base A, Linha 24241, Valor `#`, `Valor ilegível`.

Arquivos: `conciliacao_enxuta/leitura.py` (`_centavos`, `_atributo`), `tests/test_leitura.py`.

**Onde está agora (depois da entrega):**
As regras de Valor e de Atributo estão em `conciliacao_enxuta/leitura.py`: `_centavos` (Valor em texto), `_centavos_de` (Valor numérico) e `_atributo`.
