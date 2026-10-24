# 32: Valor com separador ambíguo ou grande demais

**What to build:** na leitura, com vírgula, o ponto só separa grupos de 3 dígitos e o primeiro grupo não começa com zero (`1.234,56`); fora disso, o Valor é ilegível (`1,234.56`, `1.2.3,4`, `1.2,3`). Sem vírgula, o ponto é separador de milhar só nesse mesmo formato (`1.234` é R$ 1.234,00); senão é decimal (`0.125` é R$ 0,13, `00.500` é R$ 0,50). O arredondamento para centavos acontece uma vez só. Um Valor que não cabe em centavos `Int64`, de qualquer formato, inclusive um inteiro grande de um `.parquet`, é ilegível. Todos viram Linha rejeitada com o motivo `Valor ilegível`; nenhum para a execução. Ver spec: Regras (Valor), bloco "Decisões de 24/10/2026" (Valor e Data), Testes/Correções da auditoria (leitura); histórias 48 e 49.

**Blocked by:** 29

**Status:** ready-for-agent

- [ ] Teste de leitura: `1,234.56`, `1.2.3,4` e `1.2,3` são `Valor ilegível`; `1.234` é 123400 centavos, `0.125` é 13, `00.500` é 50.
- [ ] Teste de leitura: um Valor fora de `Int64` em texto e como inteiro de `.parquet` é `Valor ilegível`, sem parar a execução.
- [ ] Os formatos já aceitos (número, `1.234,56`, `R$`, parênteses, menos, mais de 2 casas) continuam lidos como antes.
- [ ] `C:\Users\josef\Projetos\Conciliacao-Enxuta\.venv\Scripts\python -m pytest -q` passa.
- [ ] Teste com olhos de usuário: numa cópia de uma base de `exemplo\`, trocar alguns Valores por `1,234.56`, `1.2.3,4` e `99999999999999999999`, rodar a CLI e conferir que viram Linhas rejeitadas na aba Erros, com a Linha certa, e que o resto concilia.

**Notas de entrega:**

**Onde está agora (depois da entrega):**
