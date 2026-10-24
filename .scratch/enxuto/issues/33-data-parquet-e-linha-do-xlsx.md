# 33: Data, tipos do `.parquet` e Linha do `.xlsx`

**What to build:** na leitura, a Data tem ano de 4 dígitos (`31/01/26` é `Data ilegível`) e uma data do Excel acima de 2958465 (31/12/9999) é `Data ilegível`. Num `.parquet`, um Valor ou uma Data de um tipo que não é número, texto nem data (ex.: `bool`, `time`) é ilegível; o `decimal` é número; uma coluna `categorical` é lida pelo seu texto; uma coluna só com nulos é vazia. Nenhum desses para a execução. A Linha de uma Linha rejeitada de um `.xlsx` é a linha da planilha, contando as linhas vazias antes do cabeçalho. Ver spec: Regras (Linha rejeitada, Data, Tipos do `.parquet`), bloco "Decisões de 24/10/2026" (Valor e Data, Linha no `.xlsx`), Testes/Correções da auditoria (leitura); histórias 50, 51 e 57.

**Blocked by:** 32

**Status:** ready-for-agent

- [ ] Teste de leitura: `31/01/26` é `Data ilegível`; a data do Excel 2958466 é `Data ilegível` e 2958465 é lida.
- [ ] Teste de leitura de `.parquet`: coluna `decimal` lida como número; `bool` e `time` como ilegível; `categorical` pelo texto; coluna só com nulos como vazia. Nenhum para a execução.
- [ ] Teste de leitura: num `.xlsx` com linhas vazias antes do cabeçalho, a Linha da Linha rejeitada é a da planilha.
- [ ] `C:\Users\josef\Projetos\Conciliacao-Enxuta\.venv\Scripts\python -m pytest -q` passa.
- [ ] Teste com olhos de usuário: numa cópia `.xlsx` de uma base de `exemplo\`, inserir duas linhas vazias antes do cabeçalho e uma Data `31/01/26`, rodar a CLI e conferir na aba Erros que a Linha aponta para a linha certa da planilha.

**Notas de entrega:**

**Onde está agora (depois da entrega):**
