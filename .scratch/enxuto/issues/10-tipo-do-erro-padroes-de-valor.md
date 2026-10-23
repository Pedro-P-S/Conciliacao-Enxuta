# 10: Tipo do Erro pelos padrões de valor

**What to build:** o Tipo do Erro reconhece os padrões que o analista não vê a olho: Sinal invertido (A = −B, com A ≠ 0), Duplicado (A = 2×B ou B = 2×A), Vírgula deslocada (A/B ∈ {10, 100, 1000, 0,1, 0,01, 0,001}) e Dígitos trocados (|Diferença| múltiplo de 9 centavos e os mesmos dígitos de |A| e |B| em outra ordem). Todos os que se aplicam são listados, separados por `; `, na ordem da spec; Sem padrão só quando nenhum outro se aplica. A Tolerância vale como folga nas comparações de Sinal, Duplicado e Vírgula. A detecção pode ser copiada do projeto grande e adaptada, sem importar. Ver spec: Decisões de implementação (Regras/Tipo do Erro), Fora do escopo (Valor Fixo, Percentual Constante, Ponta Zerada e Arredondamento não entram), Notas; histórias 20, 21 e 27.

**Blocked by:** 09

**Status:** done

- [x] Seam 1: um caso para cada Tipo (Sinal invertido, Duplicado nos dois sentidos, Vírgula deslocada em cada fator, Dígitos trocados).
- [x] Seam 1: combinações listam todos os Tipos que se aplicam, na ordem da spec (por exemplo, um par que é Duplicado e também cai em outro padrão).
- [x] Seam 1: a Tolerância como folga faz um quase-Sinal invertido (A = −B ± centavos dentro da Tolerância) ser Sinal invertido, e o mesmo para Duplicado e Vírgula.
- [x] Seam 1: Dígitos trocados exige as duas condições (múltiplo de 9 e mesmos dígitos); só uma não basta.
- [x] A aba Por Tipo do Erro conta uma Chave com dois Tipos nos dois.
- [x] O gerador de exemplo planta cada padrão no gabarito; o teste de ponta a ponta confere a coluna Tipo do Erro e a aba Por Tipo do Erro.
- [x] `C:\Users\josef\Projetos\Conciliacao-Enxuta\.venv\Scripts\python -m pytest -q` passa.
- [x] Teste com olhos de usuário: regenerar `exemplo\` com os padrões plantados, rodar a CLI e conferir com openpyxl (`PYTHONIOENCODING=utf-8`) que cada Chave plantada mostra o Tipo certo nas Operações com Diferença e que a aba Por Tipo do Erro tem uma linha por Tipo presente.

**Notas de entrega:**
- `cruzamento._tipo_do_erro(tolerancia)` agora detecta, depois de Só em A e Só em B, os seguintes padrões. Sinal invertido: A ≠ 0 e |A + B| ≤ Tolerância. Duplicado: |A − 2B| ou |B − 2A| ≤ Tolerância. Vírgula deslocada: o mesmo teste com os fatores 10, 100 e 1000, nos dois sentidos. Dígitos trocados: Diferença múltipla de 9, |A| ≠ |B| e os mesmos dígitos ordenados. O lado ausente conta como 0, então nenhum padrão de valor pega uma órfã. A detecção foi reescrita com base no projeto grande, sem importar nada de lá.
- Decisão de interpretação: a folga é absoluta, em centavos (|x − fator·y| ≤ Tolerância), como diz a spec. O projeto grande usava erro relativo de 0,1%. Em Chaves de poucos reais isso pode dar um falso positivo (A = 2,50 e B = 0,20, com Tolerância de 1,00, sai Vírgula deslocada).
- `exemplo.py`: os casos 7, 8 e 9 plantam Sinal invertido, Duplicado e Vírgula deslocada. O caso 0 planta Dígitos trocados ou Duplicado com Dígitos trocados (125.874 × 2 = 251.748). O `_por_tipo` do gabarito conta a Chave em cada Tipo.
- Nos testes antigos, dois pares viraram Duplicado de verdade (100.000 × 200.000 e 1.000 × 2.000). Os dados foram ajustados para que continuem Sem padrão.
- Teste com olhos de usuário: `exemplo\` foi regenerado e a CLI rodou. Cada Tipo aparece nas Operações com Diferença. Na Por Tipo do Erro há uma linha por Tipo, e as 10 Chaves com "Duplicado; Dígitos trocados" contam nos dois Tipos (Duplicado 30, Dígitos trocados 20).
- Arquivos: `conciliacao_enxuta/cruzamento.py`, `conciliacao_enxuta/exemplo.py`, `tests/test_cruzamento.py`, `tests/test_ponta_a_ponta.py`.

**Onde está agora (depois da entrega):**
