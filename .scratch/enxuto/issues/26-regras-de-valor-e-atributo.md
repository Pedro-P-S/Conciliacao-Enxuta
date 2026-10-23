# 26: Valor com mais de 2 casas, caractere estranho e Atributo com qualquer conteúdo

**What to build:** um Valor com mais de 2 casas é arredondado para centavos, com o meio para longe do zero, tanto em texto quanto numérico, e não rejeitado. Continuam aceitos o formato brasileiro, `R$`, parênteses e sinal de menos; qualquer outro caractere (ex.: `abc`, `#`) torna o Valor ilegível e rejeita a linha. O Atributo aceita qualquer conteúdo (número, letra, símbolo) e vira texto, vazio vira nulo, e nunca rejeita a linha nem para a execução. Ver spec: Decisões de implementação (Regras/Valor e Atributo), Testes/Leitura; histórias 5, 44 e 45.

**Blocked by:** 25

**Status:** ready-for-agent

- [ ] Leitura: `1.234,567`, `1234.565` e `-0,005` em texto viram centavos arredondados com o meio para longe do zero; o mesmo com o Valor numérico do `.xlsx` e do `.parquet`.
- [ ] Leitura: `abc`, `#` e `12a` viram Linha rejeitada com `Valor ilegível`.
- [ ] Leitura: os formatos já aceitos continuam iguais (`R$ 1.234,56`, `(1.234,56)`, `-1.234,56`, `1.234`).
- [ ] Leitura: um Atributo com número, letra, símbolo e vazio, nos três formatos de arquivo, vira texto ou nulo e não rejeita a linha.
- [ ] `C:\Users\josef\Projetos\Conciliacao-Enxuta\.venv\Scripts\python -m pytest -q` passa.
- [ ] Teste com olhos de usuário: copiar uma base de `exemplo\`, pôr um Valor com 3 casas, um `#` no Valor e um símbolo num Atributo, rodar a CLI e conferir com openpyxl (`PYTHONIOENCODING=utf-8`) que o Valor de 3 casas entra arredondado, que o `#` aparece na aba Erros e que o Atributo aparece como veio.

**Notas de entrega:**

**Onde está agora (depois da entrega):**
