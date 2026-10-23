# 13: Atributos nas Operações com Diferença

**What to build:** toda coluna além de `Chave`, `Data` e `Valor` vira Atributo automaticamente, lida como texto e com o nome que o analista deu. Os Atributos aparecem nas Operações com Diferença, depois de Aberta desde, com o nome original. O valor do Atributo vem de A; se em A estiver vazio ou a coluna não existir, vem de B. Numa Chave repetida na mesma Data-base, os Atributos vêm da primeira linha. Ver spec: Solução, Decisões de implementação (Módulos/`leitura`, Regras/Preparação, Cruzamento por Data-base, Saída/Operações com Diferença); histórias 3 e 26.

**Blocked by:** 05, 11

**Status:** done

- [x] Leitura: colunas extras viram Atributos em texto, com o nome original (sem normalizar maiúscula ou acento na exibição).
- [x] Seam 1: Atributo com valor em A usa o de A; vazio em A usa o de B; coluna só em B usa o de B; Chave Só em B usa o de B.
- [x] Seam 1: Chave repetida na mesma Data-base fica com os Atributos da primeira linha.
- [x] Operações com Diferença: depois de Aberta desde vêm todos os Atributos (de A e de B, sem repetir nomes iguais), com o nome original no cabeçalho, cobertos pelo filtro.
- [x] Bases sem nenhum Atributo continuam funcionando.
- [x] O gerador de exemplo inclui Atributos (por exemplo, Produto e Filial) com um Atributo só em B e valores vazios em A; o teste de ponta a ponta confere as colunas e valores contra o gabarito.
- [x] `C:\Users\josef\Projetos\Conciliacao-Enxuta\.venv\Scripts\python -m pytest -q` passa.
- [x] Teste com olhos de usuário: regenerar `exemplo\` com Atributos, rodar a CLI e conferir com openpyxl (`PYTHONIOENCODING=utf-8`) que as Operações com Diferença mostram os Atributos com o nome do arquivo e o valor de B quando A está vazio.

**Notas de entrega:**

- `leitura`: toda coluna além de Chave, Data e Valor vira Atributo em texto, com o nome que veio no arquivo (só sem o BOM). O valor sai sem espaço nas pontas, e só espaço vira vazio (nulo). Um número no `.xlsx` ou no `.parquet` vira texto sem `.0`. `_chave_em_texto` virou `_em_texto`, que serve à Chave e aos Atributos.
- `cruzamento`: a Preparação guarda os Atributos da primeira linha de cada Chave e Data-base. `Resultado.atributos` é um DataFrame à parte, na mesma ordem das linhas de `operacoes`, com os Atributos de A e depois os só de B, sem repetir nomes iguais. O valor vem de A e, se vazio ou ausente, de B, na Data-base mais recente. Fica fora de `operacoes` para um Atributo poder se chamar, por exemplo, Tipo.
- `excel`: as Operações com Diferença mostram os Atributos depois de Aberta desde, com o nome original, cobertos pelo filtro.
- `exemplo`: a Base A traz Produto, vazio nas Chaves múltiplas de 7. A Base B traz Produto e Filial. O gabarito ganhou `atributos` ({Chave: {Atributo: valor}}).
- Testes: 2 de leitura, 4 do Seam 1 (A com reserva em B, Chave repetida, Data-base mais recente, sem Atributos) e 2 de ponta a ponta. O de ponta a ponta confere os Atributos contra o gabarito nos 3 formatos, e o outro confere que as bases sem Atributo terminam em Aberta desde. O teste de ponta a ponta que já existia agora espera Produto e Filial e o filtro até H.
- Teste com olhos de usuário: regenerei `exemplo\`, rodei a CLI e conferi com openpyxl. O cabeçalho termina em Produto e Filial, e o filtro é A1:H141. C00007 e C00021 têm o Produto vazio em A e mostram o de B (Seguro/03 e Débito/02).
- Atenção para o ticket 15 (corte): `Resultado.atributos` se alinha a `operacoes` pela posição das linhas, então o corte tem de cortar e deslocar os dois juntos.
- Arquivos: `conciliacao_enxuta/leitura.py`, `conciliacao_enxuta/cruzamento.py`, `conciliacao_enxuta/excel.py`, `conciliacao_enxuta/exemplo.py`, `tests/test_leitura.py`, `tests/test_cruzamento.py`, `tests/test_ponta_a_ponta.py`.

**Onde está agora (depois da entrega):**
