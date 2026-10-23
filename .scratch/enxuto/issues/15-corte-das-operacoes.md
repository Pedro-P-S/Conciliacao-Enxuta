# 15: Corte das Operações com Diferença acima do limite

**What to build:** quando há mais Chaves com Diferença do que o limite de linhas (parâmetro do módulo `excel`, padrão 700.000), a aba Operações com Diferença mostra só as maiores, e um aviso na linha 1 diz "Nem todas as operações com diferença couberam: mostrando 700.000 de N, as maiores."; o cabeçalho passa para a linha 2, congelado e com filtro. O Resumo também avisa o corte, por último na lista de avisos. Ver spec: Decisões de implementação (Módulos/`excel`, Saída/Resumo — avisos, Saída/Operações com Diferença), Testes (corte com o limite reduzido por parâmetro); história 32.

**Blocked by:** 13

**Status:** done

- [x] Com o limite reduzido por parâmetro (ex.: 3) e 5 Chaves com Diferença, a aba mostra as 3 maiores por |Diferença|.
- [x] A linha 1 tem o aviso com o limite e o N formatados no padrão brasileiro (`700.000`); o cabeçalho fica na linha 2, congelado, e o filtro começa nele.
- [x] Sem corte, não há aviso e o cabeçalho fica na linha 1.
- [x] Resumo: o aviso de corte aparece só quando há corte e é o último dos avisos.
- [x] O teste de ponta a ponta usa o limite reduzido por parâmetro e confere aviso, cabeçalho, ordem e quantidade de linhas.
- [x] `C:\Users\josef\Projetos\Desafio-Conciliacao\.venv\Scripts\python -m pytest -q` passa.
- [x] Teste com olhos de usuário: gerar o Excel de `exemplo\` com o limite reduzido (chamando o módulo `excel` com limite pequeno) e conferir com openpyxl (`PYTHONIOENCODING=utf-8`) o aviso na linha 1, o cabeçalho na linha 2 e o aviso de corte no Resumo.

**Notas de entrega:**
- `gravar_excel(resultado, pasta, limite=LIMITE_DE_LINHAS)` (700.000). Acima do limite, a aba Operações com Diferença mostra as `limite` primeiras (já vêm ordenadas por |Diferença|), cortando `operacoes` e `atributos` juntos com o mesmo `head`, para continuarem alinhados.
- Com corte, a linha 1 tem o aviso em negrito, com o limite e o N com separador de milhar brasileiro; o cabeçalho vai para a linha 2, o congelamento para A3 e o filtro começa na linha 2. Sem corte, nada muda.
- O Resumo repete o mesmo texto do aviso, por último na lista de avisos, só quando há corte.
- Testes de ponta a ponta (arquivos → `conciliar` → `gravar_excel` com limite reduzido): 5 Chaves com limite 3 (aviso, cabeçalho, ordem, Atributo acompanhando a Chave, congelamento, filtro, aviso no Resumo); no limite exato, sem corte; bases de exemplo com limite 4 (as maiores do gabarito, aviso depois do de Data-bases ignoradas); 1.234 Chaves com limite 1.000 (separador de milhar).
- Olhos de usuário: `exemplo\` gerado com limite 5 e lido com openpyxl: aviso "mostrando 5 de 140" na A1, cabeçalho na linha 2, A3 congelado, filtro A2:H7, aviso por último no Resumo; sem limite, cabeçalho na A1 e filtro A1:H141.
- Arquivos: `conciliacao_enxuta/excel.py`, `tests/test_ponta_a_ponta.py`.

**Onde está agora (depois da entrega):**
