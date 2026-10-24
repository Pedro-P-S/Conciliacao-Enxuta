> Itens 1 a 4 das Sugestões corrigidos (Valor lido da aba Erros agora sai em reais; spec atualizada).

# Review de confirmação: tickets 18 a 28 (`git diff 4fcfc5f...HEAD`)

**O que esta mudança faz:** As linhas sem Chave passam a entrar nos totais, na Diferença de cada Data-base, na Idade e no novo Tipo "Casa com linha sem Chave". A leitura não para mais numa linha ruim: ela vira Linha rejeitada e vai para a nova aba Erros, junto com as Data-bases ignoradas. O Resumo ganha os Atributos Problemáticos e o gráfico de barras da Idade, e sai também num `.html` com SVG.

Carga assumida: uma pessoa rodando a GUI ou a CLI na própria máquina, com até centenas de milhares de linhas. Os 206 testes passam.

**Correções da rodada anterior conferidas.**

- **Caractere de controle (antigo 1): resolvido.** `_do_arquivo` em `excel.py` tira os caracteres que o Excel não aceita (`ILLEGAL_CHARACTERS_RE`) de todo texto que veio do arquivo. Conferi todas as chamadas de `ws.cell`: a Chave, os títulos e valores de Atributo (aba Operações), a tabela por Atributo (aba Por Atributo e Atributos Problemáticos do Resumo) e as células da aba Erros passam por ela. As outras células só recebem texto fixo, números e datas. O nome do arquivo não vai para o Excel. O teste de ponta a ponta cobre o Valor, a Chave e o Atributo.
- **Data numérica NaN, infinita ou enorme (antigo 2): resolvido.** `_data_de` usa `cast(pl.Int64, strict=False)`. No `.xlsx`, `_ler_tabela` pega o `InvalidOperationError` do `pl.read_excel` e lê de novo com as colunas decimais fixadas como `Float64`. Testado também: o `1e30` no Valor de uma coluna de números redondos, títulos repetidos e coluna sem título passam pela releitura sem quebrar e com os mesmos nomes de coluna. O `fastexcel` já está no `requirements.txt`. Mas a releitura tem um efeito colateral (item 1 abaixo).
- **Texto com `=` virando fórmula (antigo 3): resolvido.** `_do_arquivo` marca a célula de texto com `data_type = "s"`. O teste confere a aba Erros, a Chave e o Atributo.

## Problemas críticos

Nenhum.

## Sugestões

### Should fix

1. **A releitura do `.xlsx` muda o texto de todas as colunas de números redondos, não só da que quebrou** (`conciliacao_enxuta/leitura.py`, `_ler_tabela`, ramo `except`; efeito em `_em_texto` e no `como_veio` de `ler_base`)
   - **O que é:** Quando o `.xlsx` tem um número grande demais (por exemplo `1e30` digitado na Data), a base é lida de novo com toda coluna decimal como `Float64`.
   - **Problema:** Sem a releitura, uma coluna só de números redondos vem como inteiro; com ela, vem como decimal, e o decimal vira texto de outro jeito. Testado: uma Chave numérica `12345678901234567` sai `"12345678901234570"` na leitura normal, mas `"1.234567890123457e+16"` quando outra linha do mesmo arquivo tem `1e30` na Data. Uma Chave `1e17` sai `"1e+17"`. Essas Chaves não cruzam mais com as da outra base e viram Só em A ou Só em B. Na aba Erros, o Valor `5` da linha rejeitada aparece como `5.0`, e a Data `46295` como `46295.0`, quando a spec pede "como vieram".
   - **Correção:** Escrever o decimal redondo como inteiro na hora de virar texto, em `_em_texto` e no `como_veio`: para coluna float, `pl.when(c == c.round(0)).then(c.cast(pl.Int64, strict=False).cast(pl.String)).otherwise(c.cast(pl.String))`, com `coalesce` para o NaN e o infinito que não viram inteiro. Assim o tipo da leitura não muda o texto, e o `str.replace(r"\.0$", "")` de `_em_texto` sai. Um teste de leitura com Chave de 17 dígitos e `1e30` na Data de outra linha.
   - **Se ficar:** Um único erro de digitação num `.xlsx` com Chaves numéricas longas faz todas essas Chaves aparecerem como Diferença falsa, sem nada que aponte a causa. É raro (precisa das duas coisas no mesmo arquivo), por isso não é crítico.

2. **O `html.py` usa nomes privados do `excel.py` e copia os textos do Resumo** (`conciliacao_enxuta/html.py:9`, `:45-71`; `conciliacao_enxuta/excel.py`, avisos e `_tabela_por_atributo`)
   - **O que é:** A spec pede que o HTML mostre o mesmo Resumo do Excel, "com os mesmos rótulos".
   - **Problema:** O `html.py` importa `_milhar`, `_rotulo_da_faixa` e `_aviso_de_corte` (o `_` diz "não use de fora"), e repete à mão os textos `Linhas rejeitadas: N (veja a aba Erros)`, `Linhas sem Chave, fora do cruzamento` e os quatro títulos da tabela de Atributos. Quem mudar um rótulo no Excel e esquecer o HTML deixa os dois diferentes, e só os testes de string pegam.
   - **Correção:** Tirar o `_` dos três nomes e passar a usar, nos dois arquivos, uma função pública no `excel.py` que devolve a lista de avisos (`avisos(resultado, limite) -> list[str]`) e uma constante com os títulos da tabela de Atributos. Sem módulo novo.
   - **Se ficar:** Com o tempo, o Resumo do `.html` e o do `.xlsx` passam a dizer coisas diferentes.

### Nice to have

3. **Valor em reais formatado em dois lugares** (`conciliacao_enxuta/html.py`, `_reais`; `conciliacao_enxuta/excel.py`, `_linha_sem_chave`)
   - **O que é:** Centavos viram `1.234,56` no HTML e na coluna Linha sem Chave do Excel.
   - **Problema:** As duas fazem o mesmo `divmod` + `_milhar`, só muda o sinal (`-` e `−`). Mudar o formato pede duas mudanças.
   - **Correção:** Uma função `reais(centavos, sinal="-")` no `excel.py`, usada pelos dois.
   - **Se ficar:** Só mais umas linhas para manter.

4. **`_sem_chave` calculado duas vezes por base** (`conciliacao_enxuta/cruzamento.py:389-398`)
   - **O que é:** O Total A soma `_sem_chave(sem_chave_a, data_base).soma`, e logo abaixo `sem_chave_a=` chama a mesma função de novo (o mesmo para B).
   - **Problema:** Trabalho repetido e duas fontes para o mesmo número.
   - **Correção:** Calcular uma vez em variáveis (`sem_a = _sem_chave(...)`) e usar nos dois lugares.
   - **Se ficar:** Nada quebra; só leitura pior.

**Veredito:** Pode entregar. O item 1 é o próximo a corrigir.
**Lean:** cerca de -10 linhas possíveis (itens 2 a 4).
**Não conferido:** o `.html` aberto num navegador de verdade (só li o SVG gerado).

---

# Auditoria do repositório inteiro (40 agentes, confirmada)

40 agentes Haiku auditaram o código atual, 10 por skill: ponytail-audit, code-review, domain-modeling e improve-codebase-architecture. Cada um provou ter acesso à skill. Depois, um agente Opus caçou falsos positivos e reproduziu os bugs. Aqui só entra o que ele confirmou, com as correções que fez. Ficaram de fora os falsos positivos: Data com hora no CSV (a spec não pede), o `gui.main` sempre 0 (a exceção já sai com 1), o arquivo como argumento do `__main__` (fora da spec), a Tolerância `1e30` (a spec aceita) e os erros da GUI "sem teste" (o `test_gui.py:84-119` cobre).

Carga assumida: uma pessoa, no próprio PC, até 700 mil linhas. Suíte: 211 testes passam.

## Problemas críticos (resultado errado ou quebra)

1. **Atributo chamado `Peso`, `Absoluta` ou `Atributo` derruba a conciliação** (`cruzamento.py:260`, `:265`, `:275-276`). As colunas internas têm o mesmo nome do Atributo no concat. Dá `DuplicateError`, e nada é gravado. A spec diz que o Atributo nunca derruba a execução (GRILL 16). Correção: nomes internos que um arquivo não usa, e um teste com esses três nomes.
2. **Valor inteiro grande no `.parquet` estoura e troca o sinal** (`leitura.py:157-158`). `100000000000000000` vira `-8446744073709551616` centavos e entra nos totais. O ramo float já rejeita. Correção: conferir o limite antes do `* 100` e rejeitar a linha.
3. **Valor com separadores fora do formato brasileiro sai errado, em silêncio** (`leitura.py:46-57`). `1,234.56` vira R$ 1,23, `1.2.3,4` vira R$ 123,40, `1.2,3` vira R$ 12,30. `0.125` vira R$ 125,00 e `00.500` vira R$ 500,00: o zero à esquerda é tratado como milhar. Correção: com vírgula, o ponto só separa grupos de 3; o primeiro grupo não começa com zero; fora disso, Valor ilegível.
4. **Float com muitas casas arredonda errado** (`leitura.py`, `_centavos_de`). `2.1249999999` vira 213 centavos, e o certo é 212, porque há um `round(6)` antes do `round(0)`. Correção: arredondar uma vez só.
5. **Data com ano de 2 dígitos vira o ano 26** (`leitura.py:70`). `31/01/26` vira 31/01/0026, sem aviso, e a spec pede DD/MM/AAAA.
6. **Data numérica enorme quebra a conciliação** (`leitura.py:68-73`). `9999999` é lido como o ano 29279, e o `conciliar` quebra com "year 29279 is out of range". Números menores são datas do Excel válidas. Correção: acima de 2958465 (31/12/9999), Data ilegível.
7. **Parquet com Valor `decimal`, ou Valor e Data `bool`, `null`, `categorical` ou `time`, para a execução** (`leitura.py`, `_centavos_de`, `_data_de`). Dá `InvalidOperationError` em vez de Linha rejeitada. Correção: no ramo `else`, converter para texto antes; o Decimal vai pelo caminho numérico.
8. **A CLI mostra traceback nos erros comuns** (`cli.py:45`). Isso vale para arquivo inexistente, pasta de saída inexistente, CSV vazio, `.xlsx` ou `.parquet` corrompido, CSV com campo a mais, colunas `Data`/`DATA` e o item 7. A história 35 pede "sem traceback na tela". Correção: `ler_base` como porta única dos erros de arquivo, com OSError, NoDataError, ComputeError, CalamineError e coluna repetida virando ErroDeLeitura com o nome do arquivo. Mais um pipeline único (sugestão 1).
9. **GUI: Excel aberto deixa um `.html` novo e um `.xlsx` velho** (`gui_estado.py:53-54`). O `.html` é gravado antes, e a janela diz que nada foi feito. Correção: gravar o `.xlsx` primeiro.
10. **GUI: caminho com espaço no fim ou entre aspas dá "formato não suportado"** (`gui_estado.py:50`). Acontece com o "Copiar como caminho" do Windows. Correção: `strip().strip('"')`.
11. **GUI: se o `erros.log` não pode ser gravado, o erro escapa** (`gui_estado.py:31`, `:57-59`). Sem LOCALAPPDATA, sai um `KeyError`, e a janela continua mostrando o resultado anterior.
12. **Tolerância** (`cli.py:24`). `1e3000000` quebra com `decimal.Overflow`, na CLI e na GUI. `1.000` vira R$ 1,00, mas o mesmo texto como Valor é R$ 1.000,00. O arredondamento é meio-para-par (`0,005` vira 0, `0,025` vira 2), e o do Valor é meio para longe do zero. A spec não fixa o arredondamento da Tolerância (pergunta 8).
13. **Aba Por Atributo sem corte** (`excel.py`, `_tabela_por_atributo`). Pode passar das 1.048.576 linhas do Excel, sem aviso.
14. **A célula "Linha sem Chave" é cortada em 32.767 caracteres, sem aviso** (`excel.py:273`). Acontece com Tolerância grande e muitas Casas.
15. **xlsx: Chave numérica com mais de 15 dígitos junta Chaves diferentes** (limite do double do Excel). `12345678901234567` e `…568` viram `12345678901234570` e são somadas. O teste `test_leitura.py:456-473` aceita isso. Decidir: avisar ou rejeitar.
16. **xlsx: a Linha da rejeitada sai errada com linha vazia antes do cabeçalho** (`leitura.py:204`, `primeira_linha` fixo).

## Sugestões

### Should fix

1. **Pipeline ler → conciliar → gravar duplicado** (`cli.py:43-50`, `gui_estado.py:50-54`). As duas cópias já divergem: a ordem de gravação é outra, e o tratamento de erro também (itens 8 e 9). Correção: `conciliar_arquivos(base_a, base_b, tolerancia, pasta)` no `cli.py`, sem módulo novo. Ela grava o `.xlsx` antes do `.html`. A CLI pega o erro inesperado sem traceback e sem `erros.log`.
2. **Casa com linha sem Chave faz o produto completo antes de filtrar** (`cruzamento.py:188-192`). Com 20 mil Chaves e 2 mil linhas sem Chave, leva 2,0 s, contra 0,12 s sem elas, e cresce como produto. Correção: um join por faixa (`join_where`).
3. **Gravar o `.xlsx` é lento** (`excel.py:266-276`, célula a célula): 30 mil operações levam 5,2 s.
4. **Corte por limite escrito em quatro lugares** (`excel.py:55-56`, `:144`, `:254-256`, `:310-314`). Correção: uma função de corte e aviso.
5. **`zip(ROTULOS_DO_QUADRO, quadro)` corta em silêncio** (`excel.py:112`, `html.py:51`). Correção: `quadro_do_resumo(resultado) -> [(rótulo, valor, tipo)]` no `excel.py`, usada pelos dois.
6. **Reais formatados em dois lugares** (`leitura._em_reais` e `excel.reais`/`milhar`).
7. **Regra de sinal da linha sem Chave duplicada** (`cruzamento.py:180-181` e `:359-360`).
8. **`gui_estado` importa a Tolerância do `cli`** (`gui_estado.py:12`). Correção: `tolerancia_em_centavos` ao lado de `TOLERANCIA_PADRAO`, levantando ValueError.
9. **Faltam testes** para os críticos 2 a 8, 12 e 16; para o escape de `<`, `&` e aspas no HTML; para o `erros.log` que não pode ser gravado. Duas mutações passam sem nenhum teste falhar: tirar o filtro de Data-bases comuns da Casa (`cruzamento.py:184`) e trocar `>` por `>=` no Por Atributo (`cruzamento.py:262`).
10. **Testes leem atributos privados do openpyxl** (`test_ponta_a_ponta.py:75`, `80`, `105-107`, `115`, `126`: `_charts`, `anchor._from.row`).
11. **`por_idade` e `historico` são tuplas posicionais.** Correção: dataclasses congeladas no `cruzamento.py` (`FaixaDeIdade`, `PontoDoHistorico`). Mudam `test_cruzamento.py:153` e `:404-444`.
12. **Idade em três funções, com uma Chave de texto fictícia** (`cruzamento.py:198`, `:287`, `:293`, `:303`). Correção: uma `_idades` com o Lançamento por (Base, Valor), sem módulo novo; os testes continuam pelo `conciliar`.
13. **Documentos em conflito:**
    - O CLAUDE.md ("vira reais só no Excel") e o `excel.py:1` ("só aqui") contra a spec ("até o Excel e o HTML").
    - O GRILL 14 ("Valor como veio") ficou superado pela regra nova do Valor lido em reais.

### Nice to have

14. **HTML:**
    - O eixo mostra "0,01" quando não há Diferença (`html.py:120`, `:132`).
    - O gráfico de linha sai vazio com uma Data-base só, e a data aparece duas vezes (`html.py:121-125`).
    - O percentual arredonda meio-para-par: 0,125% sai "0,12%" no HTML e "0,13%" no Excel (`html.py:71`).
    - Um caractere de controle vai cru para o HTML (`html.py:73`).
15. **Leitura:**
    - UTF-16 dá "faltam as colunas … ÿþChave" em vez de pedir UTF-8.
    - `Valor;Valor` vira o Atributo `Valor_duplicated_0`, sem aviso.
    - A Chave é calculada duas vezes (`leitura.py:198`, `:207`).
    - O sufixo é testado em dois lugares (`:90`, `:204`).
    - Há um BOM literal invisível (`:194`).
16. **Excel e gerador:**
    - O parâmetro `aviso_de_corte` sombreia a função de mesmo nome (`excel.py:246`).
    - Um Atributo chamado `Valor A` ou `Tipo do Erro` duplica o cabeçalho da aba Operações.
    - O gerador aceita `"CSV"` e grava um `.xlsx` com esse nome.
    - Uma soma acima do Int64 na mesma Chave estoura (só com valores irreais).
17. **`exemplo.py` (450 linhas) no pacote, usado só pelos testes e para gerar `exemplo\`.** Ir para `tests/` quebra o comando `python -m conciliacao_enxuta.exemplo` (pergunta 10).

## Glossário (CONTEXT.md), propostas dos agentes de domain-modeling

Premissas conferidas. Nada foi editado.

- **Diferença total e absoluta:** contam só o que está acima da Tolerância. Total A − Total B = Diferença total + **Folga da Tolerância** (nome proposto).
- **Peso:** a soma de |Valor A| (|B| quando A é zero) das Chaves, sem as linhas sem Chave. Substitui o "% do Total".
- **Termos novos:**
  - Data-base comum, mais recente e ignorada.
  - Total A/B e Valor A/B.
  - Chave com Diferença.
  - Lançamento (uma linha sem Chave por Base e Valor).
  - Motivo.
  - Valor de Atributo.
- **Linha sem Chave:** é Diferença só com |Valor| > Tolerância, com +Valor na A e −Valor na B (o glossário diz "positiva/negativa").
- **Casa:** a primeira Data-base *comum*. Uma Chave pode ter várias.
- **Aberta desde:** sumir é ficar dentro da Tolerância. "Ou antes" quer dizer a primeira observada, e então a Idade é a mínima. A faixa de "5 anos" é 1826 dias.
- **Tipo do Erro:** é uma hipótese, só na Data-base mais recente. A Tolerância também é a folga das comparações.

## Perguntas abertas (decisão sua)

1. Em Duplicado e Vírgula, a folga é absoluta: 2,00 contra 0,50 vira Duplicado, e 1,10 contra 0,01 vira Vírgula. Ela fica relativa, ou exige um mínimo?
2. Uma linha sem Chave abaixo da Tolerância pode ser Casa? Hoje pode.
3. Renomear colunas? Os casos:
   - a "Linha sem Chave" das Operações, que mostra as Casas;
   - o "Valor" do Por Atributo;
   - a "Diferença absoluta" de Por Tipo e Por Atributo, que soma só as Chaves.
4. Atributo com nome de coluna do relatório: renomear com sufixo?
5. Chaves com Atributo vazio entram no Peso total? Hoje entram.
6. Data de célula de data na aba Erros: `2026-09-30` (hoje) ou `30/09/2026`?
7. Mostrar a Folga da Tolerância no Resumo?
8. Como arredondar a Tolerância? E onde ela mora (no `cli.py` ou ao lado de `TOLERANCIA_PADRAO`)?
9. A história 37 (`spec.md:64`) diz que o Total A bate com a soma de cada arquivo, mas o código usa só a Data-base mais recente. Qual vale?
10. Se o `exemplo.py` sair do pacote, qual comando passa a gerar `exemplo\`?
11. Mostrar quanto valem as Data-bases ignoradas, na aba Erros?
12. Qual o nome do gráfico: "Diferença absoluta por Data-base" ou "Histórico da Diferença"?
13. Duas linhas sem Chave de mesmo valor, na mesma base e Data-base, viram uma só na Casa. É isso?
14. A Chave `00123` do CSV deve casar com o `123` do xlsx? Hoje não casa.
15. `1.005` é milhar (R$ 1.005,00, como hoje) ou decimal?

**Veredito:** Corrigir primeiro os críticos 1 a 4 (dinheiro errado ou quebra com dados comuns), depois o 8 com a sugestão 1.
**Não conferido:**
- A GUI aberta de verdade (regra do projeto).
- O Excel e o navegador reais.
- A carga de 700 mil linhas.
- A análise do Resumo por um dos agentes de arquitetura: a ferramenta recusou a skill, e o agente não aceitou a autorização repassada.
