# 39: Gerador de exemplo com um segundo Batimento

**What to build:** o gerador de bases de exemplo planta uma segunda coluna de valor (`Valor Juros`) nas duas bases, com Diferenças próprias (Chaves, Tipos do Erro e Linhas rejeitadas pelo Valor diferentes das do `Valor`) e o gabarito dela, para os testes de ponta a ponta e os testes com olhos de usuário dos tickets seguintes. O primeiro Batimento (`Valor`) e o seu gabarito não mudam. Ver spec: Testes/Vários Batimentos (o gerador planta um segundo Batimento com Diferenças próprias); apoia as histórias 59 a 66.

**Blocked by:** 38

**Status:** done

- [x] O gerador grava as duas bases com `Valor` e `Valor Juros`, e o gabarito traz os dois Batimentos, com Diferenças que não coincidem entre eles.
- [x] Teste: o resultado de cada Batimento, pelo `conciliar_arquivos`, bate com o gabarito do gerador.
- [x] Os testes que já usam o gerador seguem passando sem mudar o gabarito do `Valor`.
- [x] `C:\Users\josef\Projetos\Conciliacao-Enxuta\.venv\Scripts\python -m pytest -q` passa.
- [x] Teste com olhos de usuário: gerar `exemplo\` de novo, rodar a CLI e conferir os dois Batimentos contra o gabarito.

**Notas de entrega:**
Seams (escolhidos pela spec, seam 2): gerador de exemplo -> `conciliar_batimentos` (o mesmo pipeline do `conciliar_arquivos`, que só devolve caminhos). O gerador grava `Valor Juros` (Base A) e `valor_juros` (Base B) logo depois do Valor, e o `Gabarito` ganha `juros` (`GabaritoJuros`: totais, Diferenças, Operações e Linhas rejeitadas). As Diferenças do Juros ficam nas Chaves terminadas em 5 e 6 (Sem padrão, Duplicado, Sinal invertido), que o Valor não planta; Chaves só em A/B e linhas sem Chave valem 0 no Juros. Linhas rejeitadas: a Data rejeita nos dois; a Base A sem Chave tem Valor ilegível no Valor e Valor vazio no Juros; a rejeitada da Base B só vale no Valor. O gabarito do Valor não mudou (294 testes passam). Teste novo em `tests/test_ponta_a_ponta.py` (csv, xlsx, parquet). Teste com olhos de usuário: `exemplo\` gerado de novo, CLI rodada e os dois Batimentos conferidos contra o gabarito (40 Chaves e totais do Juros batem). Arquivos: `conciliacao_enxuta/exemplo.py`, `tests/test_ponta_a_ponta.py`.

**Onde está agora (depois da entrega):**
`conciliacao_enxuta/exemplo.py` (`_juros`, `GabaritoJuros`, `Gabarito.juros`); o `.xlsx` e o `.html` ainda desenham só o primeiro Batimento (tickets 40 a 42).
