# 39: Gerador de exemplo com um segundo Batimento

**What to build:** o gerador de bases de exemplo planta uma segunda coluna de valor (`Valor Juros`) nas duas bases, com Diferenças próprias (Chaves, Tipos do Erro e Linhas rejeitadas pelo Valor diferentes das do `Valor`) e o gabarito dela, para os testes de ponta a ponta e os testes com olhos de usuário dos tickets seguintes. O primeiro Batimento (`Valor`) e o seu gabarito não mudam. Ver spec: Testes/Vários Batimentos (o gerador planta um segundo Batimento com Diferenças próprias); apoia as histórias 59 a 66.

**Blocked by:** 38

**Status:** ready-for-agent

- [ ] O gerador grava as duas bases com `Valor` e `Valor Juros`, e o gabarito traz os dois Batimentos, com Diferenças que não coincidem entre eles.
- [ ] Teste: o resultado de cada Batimento, pelo `conciliar_arquivos`, bate com o gabarito do gerador.
- [ ] Os testes que já usam o gerador seguem passando sem mudar o gabarito do `Valor`.
- [ ] `C:\Users\josef\Projetos\Conciliacao-Enxuta\.venv\Scripts\python -m pytest -q` passa.
- [ ] Teste com olhos de usuário: gerar `exemplo\` de novo, rodar a CLI e conferir os dois Batimentos contra o gabarito.

**Notas de entrega:**
(preencher na entrega)

**Onde está agora (depois da entrega):**
(preencher na entrega)
