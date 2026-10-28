"""Resultado → `.html` com o Resumo do Excel, num arquivo só e sem nada buscado na internet.

O único script é o filtro de Batimento, que só existe com mais de um.

Este módulo e o `excel` são os únicos lugares onde os centavos viram reais.
"""

from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal
from html import escape
from pathlib import Path

from openpyxl.cell.cell import ILLEGAL_CHARACTERS_RE

from conciliacao_enxuta.cruzamento import Resultado
from conciliacao_enxuta.excel import (
    LIMITE_DE_LINHAS,
    TITULO_GRAFICO_DA_IDADE,
    TITULO_GRAFICO_DO_HISTORICO,
    TITULO_PROBLEMATICOS,
    TITULOS_POR_ATRIBUTO,
    TITULOS_SEM_CHAVE,
    avisos,
    milhar,
    quadro_do_resumo,
    reais,
    rotulo_da_faixa,
)

# Um tema só: os papéis de cor são tokens em `:root`. O escuro é escolhido, não inversão, e vale pela preferência do
# sistema ou por `data-theme="dark"`; `data-theme="light"` trava o claro.
_ESCURO = (
    "--superficie:#14161a;--cartao:#1e2128;--texto:#ececee;--texto-2:#b4b9c2;--texto-3:#9ba1ac;"
    "--grade:#3a3f48;--serie-1:#3987e5;"
)
ESTILO = (
    ":root{--superficie:#ffffff;--cartao:#f3f4f6;--texto:#15171a;--texto-2:#4a505a;--texto-3:#5b6370;"
    "--grade:#d5d8de;--serie-1:#2a78d6;}\n"
    '@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){' + _ESCURO + "}}\n"
    ':root[data-theme="dark"]{' + _ESCURO + """}
body { font-family: system-ui, -apple-system, "Segoe UI", Roboto, Arial, sans-serif; margin: 0 auto; padding: 16px;
  max-width: 720px; color: var(--texto); background: var(--superficie); }
h1 { font-size: 22px; margin: 0 0 16px; }
h2 { font-size: 15px; font-weight: 600; margin: 24px 0 8px; }
select { font: inherit; color: var(--texto); background: var(--cartao); border: 1px solid var(--grade); padding: 6px 8px;
  margin-bottom: 16px; max-width: 100%; }
.cartoes { display: grid; grid-template-columns: repeat(auto-fill, minmax(150px, 1fr)); gap: 8px; }
.cartao { background: var(--cartao); border-radius: 8px; padding: 10px 12px; }
.rotulo { display: block; font-size: 13px; color: var(--texto-2); }
.valor { display: block; font-size: 20px; font-weight: 600; font-variant-numeric: tabular-nums; overflow-wrap: anywhere; }
table { border-collapse: collapse; width: 100%; margin: 8px 0; font-size: 14px; }
th, td { padding: 6px 8px; text-align: left; overflow-wrap: anywhere; border-bottom: 1px solid var(--grade); }
th { font-weight: 600; color: var(--texto-2); }
td.n { text-align: right; font-variant-numeric: tabular-nums; }
p { color: var(--texto-2); font-size: 14px; }
details { margin-bottom: 8px; font-size: 14px; color: var(--texto-2); }
svg { display: block; width: 100%; height: auto; font-size: 12px; }
svg text { fill: var(--texto-2); }
svg .v { fill: var(--texto); paint-order: stroke; stroke: var(--superficie); stroke-width: 4px; }  /* legível sobre a linha */
.grade { stroke: var(--grade); stroke-width: 1; }
.barra { fill: var(--serie-1); }
.linha { stroke: var(--serie-1); }
.ponto { fill: var(--serie-1); stroke: var(--superficie); stroke-width: 2; }
.alvo { fill: transparent; }
"""
)
# O único script: mostra só o Resumo do Batimento escolhido. Roda também na abertura, para a lista e o Resumo
# não divergirem quando o navegador devolve a escolha anterior.
FILTRO = """
var lista = document.getElementById("batimento");
function mostrar() {
  document.querySelectorAll("section").forEach(function (s, i) { s.hidden = i !== lista.selectedIndex; });
}
lista.onchange = mostrar;
mostrar();
"""


def gravar_html(resultados: list[Resultado], pasta: str | Path, limite: int = LIMITE_DE_LINHAS) -> Path:
    """Grava `conciliacao_AAAA-MM-DD.html` em `pasta`, sobrescrevendo, e devolve o caminho.

    `resultados` são os Batimentos, na ordem da Base A. Com mais de um, o arquivo traz uma lista suspensa e o
    Resumo de cada um; só o primeiro aparece sem o script. `limite` é o mesmo do `.xlsx`: acima dele, o Resumo
    avisa do corte das operações.
    """
    caminho = Path(pasta) / f"conciliacao_{resultados[0].data_base.isoformat()}.html"
    total = sum(r.operacoes.height for r in resultados)  # o corte é da aba inteira, como no Excel
    corpo = _resumo(resultados[0], limite, total)
    if len(resultados) > 1:
        opcoes = "".join(f"<option>{_do_arquivo(r.batimento)}</option>" for r in resultados)
        secoes = "\n".join(
            f"<section{' hidden' if i else ''}>\n{_resumo(r, limite, total)}\n</section>" for i, r in enumerate(resultados)
        )
        corpo = f'<select id="batimento">{opcoes}</select>\n{secoes}\n<script>{FILTRO}</script>'
    titulo = f"Conciliação {resultados[0].data_base:%d/%m/%Y}"
    pagina = (
        '<!doctype html>\n<html lang="pt-BR"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        f"<title>{escape(titulo)}</title><style>{ESTILO}</style></head>\n<body>\n<h1>Resumo</h1>\n"
        + corpo
        + "\n</body></html>\n"
    )
    caminho.write_text(pagina, encoding="utf-8")
    return caminho


def _resumo(resultado: Resultado, limite: int, total_de_operacoes: int) -> str:
    """O Resumo de um Batimento: o quadro, os avisos, os Atributos Problemáticos e os dois gráficos."""
    partes = ['<div class="cartoes">']
    partes += [
        f'<div class="cartao"><span class="rotulo">{escape(rotulo)}</span><span class="valor">{escape(texto)}</span></div>'
        for rotulo, _, _, texto in quadro_do_resumo(resultado)
    ]
    partes.append("</div>")

    # Avisos, só quando acontecem
    if resultado.sem_chave_a.linhas or resultado.sem_chave_b.linhas:
        partes.append(_cabecalho(TITULOS_SEM_CHAVE))
        for base, sem_chave in [("Base A", resultado.sem_chave_a), ("Base B", resultado.sem_chave_b)]:
            partes.append(
                f'<tr><td>{base}</td><td class="n">{milhar(sem_chave.linhas)}</td>'
                f'<td class="n">{reais(sem_chave.soma)}</td></tr>'
            )
        partes.append("</table>")
    partes += [f"<p>{escape(aviso)}</p>" for aviso in avisos(resultado, limite, total_de_operacoes)]

    # Os Atributos Problemáticos; sem Atributo acima do peso, a tabela não aparece
    if resultado.atributos_problematicos.height:
        partes.append(f"<h2>{escape(TITULO_PROBLEMATICOS)}</h2>")
        partes.append(_cabecalho(TITULOS_POR_ATRIBUTO))
        for atributo, valor, absoluta, acima_do_peso in resultado.atributos_problematicos.iter_rows():
            percentual = f"{_percentual(acima_do_peso)}%".replace(".", ",")
            partes.append(
                f'<tr><td>{_do_arquivo(atributo)}</td><td>{_do_arquivo(valor)}</td><td class="n">{reais(absoluta)}</td>'
                f'<td class="n">{percentual}</td></tr>'
            )
        partes.append("</table>")

    partes.append(_grafico_de_barras(resultado))
    partes.append(_grafico_de_linha(resultado))
    return "\n".join(partes)


def _do_arquivo(texto: str) -> str:
    """Um texto que veio do arquivo (Atributo e o seu valor) sem os caracteres de controle, como no Excel, e escapado."""
    return escape(ILLEGAL_CHARACTERS_RE.sub("", texto))


def _percentual(fracao: float) -> Decimal:
    """A fração em %, com 2 casas, como o Excel mostra `0.00%`: com 15 dígitos e o meio arredondado para cima."""
    return (Decimal(f"{fracao:.15g}") * 100).quantize(Decimal("0.01"), ROUND_HALF_UP)


def _cabecalho(titulos: tuple[str, ...]) -> str:
    """O começo de uma tabela, com a linha de títulos."""
    return "<table><tr>" + "".join(f"<th>{escape(t)}</th>" for t in titulos) + "</tr>"


def _dados_do_grafico(titulos: tuple[str, str], linhas: list[tuple[str, str]]) -> str:
    """Os dados do gráfico em tabela, recolhida, para quem não enxerga as marcas."""
    corpo = "".join(f'<tr><td>{escape(r)}</td><td class="n">{v}</td></tr>' for r, v in linhas)
    return f"<details><summary>Dados do gráfico</summary>{_cabecalho(titulos)}{corpo}</table></details>"


def _grafico_de_barras(resultado: Resultado) -> str:
    """A Diferença absoluta por faixa de Idade, em barras deitadas, com os rótulos das faixas como no Excel."""
    largura, linha, espessura, maxima = 340, 44, 16, 230  # a barra sai de x = 1, na linha de base
    faixas = [
        (rotulo_da_faixa(faixa, chaves, sem_chave), absoluta)
        for faixa, chaves, sem_chave, absoluta in resultado.por_idade
    ]
    maior = max((absoluta for _, absoluta in faixas), default=0) or 1
    altura = len(faixas) * linha
    titulo = escape(TITULO_GRAFICO_DA_IDADE)
    svg = [f'<svg viewBox="0 0 {largura} {altura}" width="100%" role="img" aria-label="{titulo}">']
    for i, (rotulo, absoluta) in enumerate(faixas):
        y, w = i * linha, round(absoluta / maior * maxima)
        dica = escape(f"{rotulo}: {reais(absoluta)}")
        svg.append(f'<g><title>{dica}</title><rect class="alvo" x="0" y="{y}" width="{largura}" height="{linha}"/>')
        svg.append(f'<text x="0" y="{y + 14}">{escape(rotulo)}</text>')
        if w:
            r = min(4, w)  # 4px arredondados só na ponta do dado; a base é reta
            svg.append(
                f'<path class="barra" data-h="{espessura}" d="M1,{y + 22} H{1 + w - r} a{r},{r} 0 0 1 {r},{r} '
                f'V{y + 22 + espessura - r} a{r},{r} 0 0 1 -{r},{r} H1 Z"/>'
            )
        svg.append(f'<text class="v" x="{w + 7}" y="{y + 35}">{reais(absoluta)}</text></g>')
    svg.append(f'<line class="grade" x1="0.5" y1="0" x2="0.5" y2="{altura}"/></svg>')
    dados = _dados_do_grafico(("Faixa", "Diferença absoluta"), [(r, reais(a)) for r, a in faixas])
    return f"<h2>{titulo}</h2>\n" + "\n".join(svg) + "\n" + dados


def _grafico_de_linha(resultado: Resultado) -> str:
    """A Diferença absoluta por Data-base, com a primeira e a última data no eixo e o maior valor no topo."""
    largura, esquerda, topo, altura, direita = 340, 92, 24, 180, 12  # o topo deixa lugar ao valor do fim da linha
    historico = resultado.historico
    maior = max((absoluta for _, absoluta in historico), default=0)
    passo = (largura - esquerda - direita) / max(len(historico) - 1, 1)
    pontos = [
        (esquerda + i * passo, topo + altura - absoluta / (maior or 1) * altura)
        for i, (_, absoluta) in enumerate(historico)
    ]
    base, fim = topo + altura, largura - direita
    titulo = escape(TITULO_GRAFICO_DO_HISTORICO)
    svg = [
        f'<svg viewBox="0 0 {largura} {base + 28}" width="100%" role="img" aria-label="{titulo}">',
        f'<line class="grade" x1="{esquerda}" y1="{topo}" x2="{fim}" y2="{topo}"/>',
        f'<line class="grade" x1="{esquerda}" y1="{base}" x2="{fim}" y2="{base}"/>',
    ]
    # Sem Diferença, o eixo só mostra o 0, como no Excel
    if maior:
        svg.append(f'<text x="{esquerda - 6}" y="{topo + 4}" text-anchor="end">{reais(maior)}</text>')
    svg.append(f'<text x="{esquerda - 6}" y="{base + 4}" text-anchor="end">0,00</text>')
    if len(historico) > 1:
        lista = " ".join(f"{x:.1f},{y:.1f}" for x, y in pontos)
        svg.append(f'<polyline class="linha" points="{lista}" fill="none" stroke-width="2" stroke-linejoin="round"/>')
    # A dica vale em todo ponto, mas só o último aparece: com muitas Data-bases, um ponto em cada uma esconde a linha
    for i, ((data, absoluta), (x, y)) in enumerate(zip(historico, pontos), start=1):
        dica = escape(f"{data:%d/%m/%Y}: {reais(absoluta)}")
        ponto = f'<circle class="ponto" cx="{x:.1f}" cy="{y:.1f}" r="4"/>' if i == len(historico) else ""
        svg.append(f'<g><title>{dica}</title><circle class="alvo" cx="{x:.1f}" cy="{y:.1f}" r="12"/>{ponto}</g>')
    if historico:  # o valor no fim da linha, acima do último ponto e alinhado à direita para não cortar
        x, y = pontos[-1]
        svg.append(f'<text class="v" x="{min(x, fim):.1f}" y="{y - 10:.1f}" text-anchor="end">{reais(historico[-1][1])}</text>')
        # A primeira data; com uma Data-base só, ela aparece uma vez
        svg.append(f'<text x="{esquerda}" y="{base + 20}">{historico[0][0]:%d/%m/%Y}</text>')
    if len(historico) > 1:
        svg.append(f'<text x="{fim}" y="{base + 20}" text-anchor="end">{historico[-1][0]:%d/%m/%Y}</text>')
    svg.append("</svg>")
    dados = _dados_do_grafico(("Data-base", "Diferença absoluta"), [(f"{d:%d/%m/%Y}", reais(a)) for d, a in historico])
    return f"<h2>{titulo}</h2>\n" + "\n".join(svg) + "\n" + dados
