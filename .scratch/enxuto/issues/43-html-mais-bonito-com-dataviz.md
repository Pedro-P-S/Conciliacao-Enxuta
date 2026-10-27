# 43: HTML mais bonito e simples, seguindo a skill dataviz

**What to build:** o visual do `.html` fica mais bonito e simples de ler, com um tema só, sem mudar o que ele mostra (mesmos números, rótulos e ordem do Resumo do Excel). Os subagentes não carregam a skill `dataviz` sozinhos; as regras dela que valem para esta página estão abaixo e são o critério do ticket. Ver spec: Saída (HTML), bloco "Decisões de 27/10/2026" (Visual do HTML); história 66.

Regras da skill `dataviz` que valem aqui:
- Forma: o quadro de números são cartões de número (rótulo em caixa normal, sem dois-pontos; valor em fonte sem serifa, semibold; nunca fonte de exibição ou serifa). Os dois gráficos são o de barras (Diferença absoluta por faixa de Idade) e o de linha (Diferença absoluta por Data-base); nunca eixo duplo.
- Cor: papéis definidos como propriedades CSS em `:root` (superfície, texto primário, secundário e discreto, série 1, grade). Os dois gráficos têm uma série só: usam a série 1 (azul `#2a78d6` no claro, `#3987e5` no escuro), sem caixa de legenda (o título diz o que é). O texto nunca usa a cor da série: rótulos, valores e eixos vão nos tokens de texto. O tema escuro é escolhido, não inversão automática: declarar os valores escuros em `@media (prefers-color-scheme: dark)` com `:root:not([data-theme="light"])` e também em `:root[data-theme="dark"]`, e dar ao `body` fundo explícito. Se usar outras cores além da série 1, rodar o `validate_palette.js` da skill antes; cor de estado (vermelho, verde) só com ícone ou texto junto.
- Marcas: barra de no máximo 24px de espessura, com 4px arredondados na ponta do dado e reta na base, saindo de uma linha de base só; linha de 2px com junção redonda; ponto de 8px ou mais (r >= 4) com anel de 2px na cor da superfície; área, se houver, a 10% de opacidade; grade e eixos em cinza de 1px, contínuos e discretos; nenhuma borda em volta de marca.
- Rótulos: o valor na ponta da barra e no fim da linha, nunca um número em cada ponto; rótulo que não cabe vai para fora da barra, sem corte; ticks do eixo em números redondos. O rótulo da faixa segue a spec (`31 a 90 dias (12 Chaves)`).
- Interação: cada barra e cada ponto têm dica ao passar o mouse (alvo maior que a marca), sem nada de fora do arquivo. O `<script>` do filtro de Batimento continua o único.
- Acessibilidade: os dados dos gráficos também em tabela (visível ou num `<details>`); contraste de texto de pelo menos 4,5:1 nos dois temas; a identidade nunca só pela cor.
- Layout: cabe em 375px de largura sem rolagem horizontal, com margem lateral de 16px; gráficos em SVG com `viewBox` e largura de 100%.
- Depois de pronto, renderizar a página nos dois temas e em 375px e olhar: o validador confere cor, não layout.

**Blocked by:** 42

**Status:** ready-for-agent

- [ ] O `.html` tem um tema só, com as cores em tokens e os temas claro e escuro declarados como acima.
- [ ] Teste de ponta a ponta: os números, os rótulos, os percentuais, os gráficos e a ordem do Resumo continuam iguais ao Excel (os testes de `test_html` seguem passando); o arquivo continua único, com o filtro como único script e nada buscado fora.
- [ ] Teste de ponta a ponta: o `.html` traz a tabela dos dados dos gráficos e as dicas das marcas.
- [ ] Marcas e rótulos conforme as regras acima (barra <= 24px com 4px na ponta, linha de 2px, ponto de 8px com anel, sem borda em marca, rótulos só nas pontas).
- [ ] `C:\Users\josef\Projetos\Conciliacao-Enxuta\.venv\Scripts\python -m pytest -q` passa.
- [ ] Teste com olhos de usuário: rodar a CLI sobre `exemplo\`, abrir o `.html` no navegador nos temas claro e escuro e em 375px de largura, passar o mouse nas barras e nos pontos, trocar o Batimento e conferir que nada corta, sobrepõe ou rola na horizontal.

**Notas de entrega:**
(preencher na entrega)

**Onde está agora (depois da entrega):**
(preencher na entrega)
