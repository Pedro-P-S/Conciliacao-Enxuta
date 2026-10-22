# 02: Nomes de coluna flexíveis, valores e datas no formato brasileiro

**What to build:** o analista não precisa ajustar o arquivo exportado. As colunas `Chave`, `Data` e `Valor` são reconhecidas sem diferenciar maiúscula, acento e espaço nas pontas (`CHAVE`, ` data `, `valor`); a Chave vira texto sem espaço nas pontas; o Valor aceita `1.234,56`, `(1.234,56)` (negativo), `-1.234,56` e `R$ 1.234,56`; a Data aceita `DD/MM/AAAA`, `AAAA-MM-DD` e data do Excel. Ver spec: Decisões de implementação (Módulos/`leitura`), Notas (peças que podem ser copiadas do projeto grande); histórias 1, 2, 5 e 6.

**Blocked by:** 01

**Status:** ready-for-agent

- [ ] Arquivos com `CHAVE`, `Data ` e `VALOR` (e variações de acento e espaço nas pontas) são lidos como se tivessem os nomes exatos.
- [ ] Valores `1.234,56`, `(1.234,56)`, `-1.234,56`, `R$ 1.234,56` e `1234,5` viram os centavos certos (`Int64`), sem passar por float com arredondamento errado.
- [ ] Datas `31/01/2026`, `2026-01-31` e data do Excel viram a mesma Data-base.
- [ ] A Chave é lida como texto e sem espaço nas pontas, de modo que ` 123 ` em A cruza com `123` em B.
- [ ] O gerador de exemplo passa a escrever as bases com valores e datas no formato brasileiro e nomes de coluna com variações; o teste de ponta a ponta confere o Resumo contra o gabarito.
- [ ] `C:\Users\josef\Projetos\Desafio-Conciliacao\.venv\Scripts\python -m pytest -q` passa.
- [ ] Teste com olhos de usuário: regenerar `exemplo\` com valores como `R$ 1.234,56` e `(500,00)`, datas `DD/MM/AAAA` e cabeçalhos `CHAVE`/`data`/`Valor `, rodar a CLI e conferir no `.xlsx` (lido com openpyxl, `PYTHONIOENCODING=utf-8`) que os totais do Resumo batem com a soma feita à mão.

**Notas de entrega:**

**Onde está agora (depois da entrega):**
