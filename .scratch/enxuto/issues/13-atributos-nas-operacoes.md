# 13: Atributos nas Operações com Diferença

**What to build:** toda coluna além de `Chave`, `Data` e `Valor` vira Atributo automaticamente, lida como texto e com o nome que o analista deu. Os Atributos aparecem nas Operações com Diferença, depois de Aberta desde, com o nome original. O valor do Atributo vem de A; se em A estiver vazio ou a coluna não existir, vem de B. Numa Chave repetida na mesma Data-base, os Atributos vêm da primeira linha. Ver spec: Solução, Decisões de implementação (Módulos/`leitura`, Regras/Preparação, Cruzamento por Data-base, Saída/Operações com Diferença); histórias 3 e 26.

**Blocked by:** 05, 11

**Status:** ready-for-agent

- [ ] Leitura: colunas extras viram Atributos em texto, com o nome original (sem normalizar maiúscula ou acento na exibição).
- [ ] Seam 1: Atributo com valor em A usa o de A; vazio em A usa o de B; coluna só em B usa o de B; Chave Só em B usa o de B.
- [ ] Seam 1: Chave repetida na mesma Data-base fica com os Atributos da primeira linha.
- [ ] Operações com Diferença: depois de Aberta desde vêm todos os Atributos (de A e de B, sem repetir nomes iguais), com o nome original no cabeçalho, cobertos pelo filtro.
- [ ] Bases sem nenhum Atributo continuam funcionando.
- [ ] O gerador de exemplo inclui Atributos (por exemplo, Produto e Filial) com um Atributo só em B e valores vazios em A; o teste de ponta a ponta confere as colunas e valores contra o gabarito.
- [ ] `C:\Users\josef\Projetos\Desafio-Conciliacao\.venv\Scripts\python -m pytest -q` passa.
- [ ] Teste com olhos de usuário: regenerar `exemplo\` com Atributos, rodar a CLI e conferir com openpyxl (`PYTHONIOENCODING=utf-8`) que as Operações com Diferença mostram os Atributos com o nome do arquivo e o valor de B quando A está vazio.

**Notas de entrega:**

**Onde está agora (depois da entrega):**
