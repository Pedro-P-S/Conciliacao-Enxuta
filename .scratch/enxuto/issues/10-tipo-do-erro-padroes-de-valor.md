# 10: Tipo do Erro pelos padrões de valor

**What to build:** o Tipo do Erro reconhece os padrões que o analista não vê a olho: Sinal invertido (A = −B, com A ≠ 0), Duplicado (A = 2×B ou B = 2×A), Vírgula deslocada (A/B ∈ {10, 100, 1000, 0,1, 0,01, 0,001}) e Dígitos trocados (|Diferença| múltiplo de 9 centavos e os mesmos dígitos de |A| e |B| em outra ordem). Todos os que se aplicam são listados, separados por `; `, na ordem da spec; Sem padrão só quando nenhum outro se aplica. A Tolerância vale como folga nas comparações de Sinal, Duplicado e Vírgula. A detecção pode ser copiada do projeto grande e adaptada, sem importar. Ver spec: Decisões de implementação (Regras/Tipo do Erro), Fora do escopo (Valor Fixo, Percentual Constante, Ponta Zerada e Arredondamento não entram), Notas; histórias 20, 21 e 27.

**Blocked by:** 09

**Status:** ready-for-agent

- [ ] Seam 1: um caso para cada Tipo (Sinal invertido, Duplicado nos dois sentidos, Vírgula deslocada em cada fator, Dígitos trocados).
- [ ] Seam 1: combinações listam todos os Tipos que se aplicam, na ordem da spec (por exemplo, um par que é Duplicado e também cai em outro padrão).
- [ ] Seam 1: a Tolerância como folga faz um quase-Sinal invertido (A = −B ± centavos dentro da Tolerância) ser Sinal invertido, e o mesmo para Duplicado e Vírgula.
- [ ] Seam 1: Dígitos trocados exige as duas condições (múltiplo de 9 e mesmos dígitos); só uma não basta.
- [ ] A aba Por Tipo do Erro conta uma Chave com dois Tipos nos dois.
- [ ] O gerador de exemplo planta cada padrão no gabarito; o teste de ponta a ponta confere a coluna Tipo do Erro e a aba Por Tipo do Erro.
- [ ] `C:\Users\josef\Projetos\Desafio-Conciliacao\.venv\Scripts\python -m pytest -q` passa.
- [ ] Teste com olhos de usuário: regenerar `exemplo\` com os padrões plantados, rodar a CLI e conferir com openpyxl (`PYTHONIOENCODING=utf-8`) que cada Chave plantada mostra o Tipo certo nas Operações com Diferença e que a aba Por Tipo do Erro tem uma linha por Tipo presente.

**Notas de entrega:**

**Onde está agora (depois da entrega):**
