# 20: Tipo do Erro Casa com linha sem Chave e coluna Linha sem Chave

**What to build:** o analista fica sabendo quando uma Linha sem Chave tem o valor que zeraria a Diferença de uma Chave. Cada valor de linha sem Chave é comparado uma vez só, na primeira Data-base comum em que aparece entre as linhas sem Chave da sua base (nas seguintes, o mesmo valor é o mesmo lançamento). Nessa Data-base, a linha casa com uma Chave que tinha Diferença quando |Diferença + Valor| ≤ Tolerância (linha na Base A) ou |Diferença − Valor| ≤ Tolerância (linha na Base B). Uma linha para uma Chave, sem combinar linhas; uma linha pode casar com várias Chaves. O Tipo **Casa com linha sem Chave** entra antes de Sem padrão e só aparece nas Chaves com Diferença na Data-base mais recente, mesmo que a Diferença tenha mudado depois. Na aba Operações com Diferença, a coluna **Linha sem Chave** fica entre Aberta desde e os Atributos, em texto como `−10.000,00 em 15/03/2026 na Base B`, várias separadas por `; `, vazia quando não casa. A linha não é juntada à Chave. Ver spec: Solução, Decisões de implementação (Regras/Tipo do Erro e Casa com linha sem Chave; Saída/Operações com Diferença), Fora do escopo; histórias 26, 39, 40 e 41.

**Blocked by:** 18, 19

**Status:** ready-for-agent

- [ ] Seam 1: uma linha sem Chave na Base A e outra na Base B casam com a Diferença de uma Chave, cada uma com o seu sinal.
- [ ] Seam 1: casa dentro da folga da Tolerância e não casa logo acima dela.
- [ ] Seam 1: a comparação é na Data-base em que a linha aparece pela primeira vez, onde a Diferença da Chave era outra; o Tipo aparece na mais recente mesmo com a Diferença mudada.
- [ ] Seam 1: o mesmo valor repetido nas Data-bases seguintes não é comparado de novo.
- [ ] Seam 1: a Chave sem Diferença naquela Data-base não ganha o Tipo.
- [ ] Seam 1: uma linha que casa com duas Chaves dá o Tipo às duas.
- [ ] Seam 1: Casa com linha sem Chave convive com os outros Tipos, na ordem da spec, e uma Chave com ele não é Sem padrão; Por Tipo do Erro ganha a linha do novo Tipo.
- [ ] Aba `Operações com Diferença`: coluna `Linha sem Chave` depois de Aberta desde, com o valor em reais com sinal, a Data-base comparada e a base; vazia quando não casa.
- [ ] O gerador de exemplo planta uma linha sem Chave que casa com a Diferença de uma Chave numa Data-base antiga, e a Diferença dessa Chave muda depois; o teste de ponta a ponta confere o Tipo e a coluna contra o gabarito.
- [ ] `C:\Users\josef\Projetos\Conciliacao-Enxuta\.venv\Scripts\python -m pytest -q` passa.
- [ ] Teste com olhos de usuário: rodar a CLI sobre `exemplo\` e conferir com openpyxl (`PYTHONIOENCODING=utf-8`) que a Chave plantada mostra Casa com linha sem Chave e que a coluna Linha sem Chave aponta o valor, a data e a base da linha.

**Notas de entrega:**

**Onde está agora (depois da entrega):**
