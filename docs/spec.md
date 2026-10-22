# Spec — Conciliação Enxuta

Spec única da Conciliação Enxuta. As decisões de origem estão em `GRILL.md` e os termos em `CONTEXT.md`. Nada da spec, do glossário ou dos tickets do projeto grande vale aqui.

## Problema

O analista tem duas bases que deviam ter os mesmos valores e não têm. Somar e ordenar ele já faz no Excel. A ferramenta precisa entregar o que o Excel não dá de graça:
- o cruzamento pela Chave;
- o Tipo do Erro de cada Diferença;
- onde a Diferença se concentra por Atributo;
- há quanto tempo cada Diferença está aberta.

Tudo isso precisa caber num Excel pequeno, que se lê de uma vez.

## Solução

O usuário escolhe dois arquivos (Base A e Base B), confere a Tolerância e clica em Conciliar. Sai um `.xlsx` com 4 abas: **Resumo**, **Por Tipo do Erro**, **Por Atributo** e **Operações com Diferença**. Ninguém mapeia colunas, e não há outros arquivos de saída.

## Histórias do usuário

1. Como analista, escolho só os dois arquivos, sem dizer qual coluna é qual.
2. Como analista, mando um arquivo com seis meses de posições diárias e a ferramenta usa todas.
3. Como analista, abro o Resumo e vejo de uma vez os totais da última Data-base, a idade das Diferenças e um gráfico da Diferença absoluta no tempo.
4. Como analista, vejo quanto da Diferença vem de cada Tipo do Erro.
5. Como analista, vejo quais valores de Atributo concentram a Diferença, sem me enganar com um Atributo que todas as Chaves têm.
6. Como analista, recebo a lista das Chaves com Diferença na última Data-base, da maior para a menor, cada uma com o Tipo do Erro e a data em que abriu.
7. Como analista, mudo a Tolerância quando R$ 1,00 não serve.
8. Como analista, sou avisado quando algo ficou de fora: linhas sem Chave, Data-bases que estão só numa base, operações além do limite.

## Entrada

### Arquivos

- `.csv`, `.xlsx` (primeira aba) ou `.parquet`, um por base.
- Os nomes das colunas são reconhecidos sem diferenciar maiúscula, acento e espaço nas pontas:
  - `Chave`: obrigatória, lida como texto. Tira os espaços das pontas.
  - `Data`: obrigatória. Aceita data do Excel, `DD/MM/AAAA` e `AAAA-MM-DD`.
  - `Valor`: obrigatória. Aceita número nativo e o formato brasileiro (`1.234,56`, `-1.234,56`, `(1.234,56)`, `R$`). Vira centavos `Int64` e fica assim até a apresentação.
  - Qualquer outra coluna é **Atributo**, lida como texto.
- Se faltar uma coluna obrigatória, a mensagem diz qual falta, em qual arquivo, e lista as colunas encontradas.
- Se um Valor ou uma Data não puder ser lido, a mensagem diz o arquivo, a linha e o conteúdo.

### Parâmetro

- **Tolerância**: em reais, padrão `1,00`, não negativa. Uma Diferença com |Diferença| ≤ Tolerância conta como zero, inclusive quando a Chave está Só em A ou Só em B.

## Regras

### Preparação (por base)

1. As linhas com Chave vazia saem do cruzamento. O Resumo mostra quantas são e a soma delas, por base.
2. As linhas com a mesma Chave e a mesma Data-base são **somadas**. Os Atributos dessa Chave vêm da primeira linha.

### Data-bases

3. Entram só as Data-bases que existem nas duas bases. As que estão só numa base saem, e o Resumo lista quais foram.
4. A **Data-base mais recente** é a maior Data-base comum.

### Cruzamento (por Data-base)

5. Junção completa pela Chave. Diferença = Valor A − Valor B, e o lado que falta conta como 0.
6. Uma Chave tem Diferença na Data-base quando |Diferença| > Tolerância.
7. Atributo: vale o de A. Se A não tiver a coluna ou o valor estiver vazio, vale o de B.

### Tipo do Erro (só na Data-base mais recente)

Lista todos os tipos que se aplicam, separados por `; ` e na ordem abaixo:

| Tipo | Regra |
|---|---|
| Só em A | a Chave não existe em B nessa Data-base |
| Só em B | a Chave não existe em A nessa Data-base |
| Sinal invertido | A = −B, com A ≠ 0 |
| Duplicado | A = 2×B ou B = 2×A |
| Vírgula deslocada | A/B ∈ {10, 100, 1000, 0,1, 0,01, 0,001} |
| Dígitos trocados | \|Diferença\| é múltiplo de 9 centavos e os dígitos de \|A\| e \|B\| em centavos são os mesmos em outra ordem |
| Sem padrão | nenhum dos anteriores |

As comparações de Sinal invertido, Duplicado e Vírgula deslocada aceitam a Tolerância como folga. A detecção pode ser adaptada de `conciliacao/diagnostico.py` do projeto grande, mas copiando, sem importar.

### Aberta desde e Idade da Diferença

8. **Aberta desde** de uma Chave com Diferença na Data-base mais recente: anda para trás pelas Data-bases comuns e para na primeira em que a Chave não tinha Diferença (ou não existia nas duas bases). Aberta desde é a Data-base logo depois dessa. Se a Diferença só mudou de valor sem ficar abaixo da Tolerância, a data não muda.
9. Se a Chave tem Diferença em todas as Data-bases, desde a primeira, o Aberta desde é a primeira Data-base, marcado como "ou antes" (texto `DD/MM/AAAA ou antes`).
10. **Idade** = dias corridos entre Aberta desde e a Data-base mais recente.
11. **Faixas**: até 30 dias, 31 a 90, 91 a 365, 366 dias a 5 anos (até 1826 dias) e mais de 5 anos.

### Concentração por Atributo (só na Data-base mais recente)

12. Para cada Atributo e cada valor dele:
    - **Diferença** = soma das Diferenças com sinal das Chaves com Diferença;
    - **% da Diferença** = soma de |Diferença| desse valor ÷ Diferença absoluta total;
    - **Concentração** = % da Diferença ÷ (soma de |Valor A| desse valor ÷ soma de |Valor A| total). Se A for zero, usa B.
13. A aba é ordenada pela Concentração, decrescente. A Concentração não aparece na aba. Entram só os valores com pelo menos uma Chave com Diferença.

## Saída: `conciliacao_AAAA-MM-DD.xlsx`

A data no nome é a Data-base mais recente. O arquivo vai para a pasta da Base A, e um arquivo com o mesmo nome é sobrescrito. Os valores saem em reais, com formato `#.##0,00`.

### Aba "Resumo"

Em cima, um quadro com:
- Data-base mais recente e Tolerância;
- Total A, Total B, Diferença total, Diferença absoluta, Chaves com Diferença.

Embaixo do quadro, a Idade da Diferença: uma linha por faixa, com Chaves e Diferença absoluta.

Depois vêm os avisos, cada um numa linha e só quando acontece:
- "X Chaves já tinham Diferença na primeira Data-base (DD/MM/AAAA); a idade delas é no mínimo a mostrada."
- "Linhas sem Chave: A tem N linhas (R$ …), B tem M linhas (R$ …). Ficaram fora."
- "Data-bases ignoradas por estarem só numa base: …"
- "Operações com Diferença foi cortada em 700.000 linhas."

Por último, um **gráfico de linha** da Diferença absoluta por Data-base comum. Os dados do gráfico ficam numa aba oculta `_grafico`, que não conta como aba visível. A aba Resumo não tem tabela de histórico.

### Aba "Por Tipo do Erro"

Colunas: Tipo do Erro, Chaves e Diferença absoluta. Uma linha por tipo, ordenada pela Diferença absoluta. Uma Chave com dois tipos conta nos dois, e uma nota abaixo da tabela avisa isso.

### Aba "Por Atributo"

Colunas: Atributo, Valor, Diferença e % da Diferença. Ordenada pela Concentração, conforme a regra 13. A aba não tem filtro.

### Aba "Operações com Diferença"

Uma linha por Chave com Diferença na Data-base mais recente, ordenada por |Diferença| decrescente. Colunas, nesta ordem: Chave, Valor A, Valor B, Diferença, Tipo do Erro, Aberta desde e todos os Atributos (com o nome original). O cabeçalho fica congelado e com filtro.

O limite é de **700.000 linhas**. Se passar disso, a aba fica com as 700.000 maiores, e a linha 1 traz o aviso "Nem todas as operações com diferença couberam: mostrando 700.000 de N, as maiores." Nesse caso o cabeçalho passa para a linha 2.

## Interface

- **GUI Tkinter** com um campo para a Base A, outro para a Base B (cada um com o botão Procurar), o campo Tolerância (padrão 1,00) e o botão Conciliar. No fim, a janela mostra o caminho do `.xlsx` e um botão para abrir a pasta. Os erros aparecem em linguagem simples e o traceback vai para `%LOCALAPPDATA%\ConciliacaoEnxuta\erros.log`.
- **CLI**: `python -m conciliacao_enxuta conciliar BASE_A BASE_B [--tolerancia 1,00] [--saida PASTA]`.
- **Autoteste**: com `CONCILIACAO_AUTOTESTE=1`, a GUI monta escondida, fecha sozinha e sai com 0. Se falhar, sai com 1.
- A GUI é só casca: as regras ficam em módulos sem Tkinter, que são testados.

## Implementação

- O código fica em `conciliacao_enxuta/` e os testes em `tests/`. O pacote não importa nada de `conciliacao/`. Leitura, parse de valor e data, centavos, formatação e detecção de padrões podem ser **copiados** do projeto grande e adaptados.
- Usa Polars para os dados e openpyxl para o `.xlsx`, incluindo o gráfico. Por enquanto usa o `.venv` do projeto grande (`..\Desafio-Conciliacao\.venv`).
- Módulos sugeridos:
  - `leitura`: arquivos → DataFrame com Chave, Data, Valor (centavos) e Atributos;
  - `cruzamento`: duas bases → uma linha por Data-base × Chave, com A, B, Diferença e Atributos;
  - `analise`: funções puras para Tipo do Erro, Aberta desde, Idade, faixas, Concentração e totais;
  - `excel`: as 4 abas;
  - `cli`, `gui`, `gui_estado`.
- **Invariante:** na Data-base mais recente, Total A − Total B = Diferença total das Chaves com Diferença + a soma das Diferenças abaixo da Tolerância.

## Testes

- TDD. O seam principal é `cruzamento` + `analise` sobre DataFrames pequenos montados no teste.
- Um gerador de bases de exemplo com padrões plantados e um gabarito: Diferenças de cada Tipo, Chaves que abrem e fecham, uma Chave aberta desde a primeira Data-base, um Atributo concentrado e um Atributo que todas as Chaves têm.
- Um teste de ponta a ponta lê o `.xlsx` com openpyxl e confere com o gabarito: abas, totais, faixas, ordem, Aberta desde, avisos e o corte das 700 mil linhas (com o limite reduzido por parâmetro no teste).
- Os testes com olhos de usuário usam `exemplo/`, que fica no `.gitignore`.

## Fora do escopo

Dashboard HTML, CSV e Parquet de saída, Histórico persistido entre Execuções, Justificativas, Bases Auxiliares, mais de um Par de Valor, Chave composta, mapeamento de colunas, Qualidade, Pareto, Compensação Oculta, Pares Prováveis, Valor Fixo, Percentual Constante, Ponta Zerada, Arredondamento e o .exe (fica para depois).
