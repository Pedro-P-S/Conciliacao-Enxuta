"""Resultado → `.html` com o Resumo do Excel, num arquivo só, sem script e sem nada buscado na internet."""

from __future__ import annotations

from html import escape
from pathlib import Path

from conciliacao_enxuta.cruzamento import Resultado
from conciliacao_enxuta.excel import (
    LIMITE_DE_LINHAS,
    ROTULOS_DO_QUADRO,
    TITULO_GRAFICO_DA_IDADE,
    TITULO_GRAFICO_DO_HISTORICO,
    TITULO_PROBLEMATICOS,
    TITULOS_POR_ATRIBUTO,
    TITULOS_SEM_CHAVE,
    avisos,
    milhar,
    reais,
    rotulo_da_faixa,
)

ESTILO = """
body { font-family: Calibri, Arial, sans-serif; margin: 24px; color: #222; background: #fff; }
table { border-collapse: collapse; margin-bottom: 20px; }
th, td { padding: 3px 12px; text-align: left; }
td.n { text-align: right; }
svg { display: block; margin-bottom: 24px; font-size: 13px; }
svg text { fill: #222; }
"""
COR = "#2f6db5"


def gravar_html(resultado: Resultado, pasta: str | Path, limite: int = LIMITE_DE_LINHAS) -> Path:
    """Grava `conciliacao_AAAA-MM-DD.html` em `pasta`, sobrescrevendo, e devolve o caminho.

    `limite` é o mesmo do `.xlsx`: acima dele, o Resumo avisa do corte das operações.
    """
    caminho = Path(pasta) / f"conciliacao_{resultado.data_base.isoformat()}.html"
    quadro = [
        f"{resultado.data_base:%d/%m/%Y}",
        reais(resultado.tolerancia),
        reais(resultado.total_a),
        reais(resultado.total_b),
        reais(resultado.diferenca_total),
        reais(resultado.diferenca_absoluta),
        milhar(resultado.chaves_com_diferenca),
    ]
    partes = ["<table>"]
    partes += [
        f'<tr><th>{escape(r)}</th><td class="n">{escape(v)}</td></tr>' for r, v in zip(ROTULOS_DO_QUADRO, quadro)
    ]
    partes.append("</table>")

    # Avisos, só quando acontecem
    if resultado.sem_chave_a.linhas or resultado.sem_chave_b.linhas:
        partes.append(_cabecalho(TITULOS_SEM_CHAVE))
        for base, sem_chave in [("Base A", resultado.sem_chave_a), ("Base B", resultado.sem_chave_b)]:
            partes.append(
                f'<tr><td>{base}</td><td class="n">{milhar(sem_chave.linhas)}</td>'
                f'<td class="n">{reais(sem_chave.soma)}</td></tr>'
            )
        partes.append("</table>")
    partes += [f"<p>{escape(aviso)}</p>" for aviso in avisos(resultado, limite)]

    # Os Atributos Problemáticos; sem Atributo acima do peso, a tabela não aparece
    if resultado.atributos_problematicos.height:
        partes.append(f"<h2>{escape(TITULO_PROBLEMATICOS)}</h2>")
        partes.append(_cabecalho(TITULOS_POR_ATRIBUTO))
        for atributo, valor, absoluta, acima_do_peso in resultado.atributos_problematicos.iter_rows():
            percentual = f"{acima_do_peso * 100:.2f}%".replace(".", ",")
            partes.append(
                f'<tr><td>{escape(atributo)}</td><td>{escape(valor)}</td><td class="n">{reais(absoluta)}</td>'
                f'<td class="n">{percentual}</td></tr>'
            )
        partes.append("</table>")

    partes.append(_grafico_de_barras(resultado))
    partes.append(_grafico_de_linha(resultado))

    titulo = f"Conciliação {resultado.data_base:%d/%m/%Y}"
    pagina = (
        '<!doctype html>\n<html lang="pt-BR"><head><meta charset="utf-8">'
        f"<title>{escape(titulo)}</title><style>{ESTILO}</style></head>\n<body>\n<h1>Resumo</h1>\n"
        + "\n".join(partes)
        + "\n</body></html>\n"
    )
    caminho.write_text(pagina, encoding="utf-8")
    return caminho


def _cabecalho(titulos: tuple[str, ...]) -> str:
    """O começo de uma tabela, com a linha de títulos."""
    return "<table><tr>" + "".join(f"<th>{escape(t)}</th>" for t in titulos) + "</tr>"


def _grafico_de_barras(resultado: Resultado) -> str:
    """A Diferença absoluta por faixa de Idade, em barras deitadas, com os rótulos das faixas como no Excel."""
    rotulos = 330  # largura da coluna dos rótulos
    largura_maxima = 340
    maior = max((absoluta for *_, absoluta in resultado.por_idade), default=0) or 1
    linhas = ['<svg width="820" height="{}" role="img">']
    linhas.append(f'<text x="0" y="16" font-weight="bold">{escape(TITULO_GRAFICO_DA_IDADE)}</text>')
    for i, (faixa, chaves, sem_chave, absoluta) in enumerate(resultado.por_idade):
        y = 32 + i * 30
        largura = round(absoluta / maior * largura_maxima)
        linhas.append(f'<text x="0" y="{y + 15}">{escape(rotulo_da_faixa(faixa, chaves, sem_chave))}</text>')
        linhas.append(f'<rect x="{rotulos}" y="{y}" width="{largura}" height="20" fill="{COR}"/>')
        linhas.append(f'<text x="{rotulos + largura + 6}" y="{y + 15}">{reais(absoluta)}</text>')
    altura = 32 + len(resultado.por_idade) * 30
    linhas[0] = linhas[0].format(altura)
    linhas.append("</svg>")
    return "\n".join(linhas)


def _grafico_de_linha(resultado: Resultado) -> str:
    """A Diferença absoluta por Data-base, com a primeira e a última data no eixo e o maior valor no topo."""
    esquerda, topo, largura, altura = 110, 30, 680, 220
    historico = resultado.historico
    maior = max((absoluta for _, absoluta in historico), default=0) or 1
    passo = largura / max(len(historico) - 1, 1)
    pontos = " ".join(
        f"{esquerda + i * passo:.1f},{topo + altura - absoluta / maior * altura:.1f}"
        for i, (_, absoluta) in enumerate(historico)
    )
    base = topo + altura
    linhas = [
        f'<svg width="820" height="{base + 30}" role="img">',
        f'<text x="0" y="16" font-weight="bold">{escape(TITULO_GRAFICO_DO_HISTORICO)}</text>',
        f'<line x1="{esquerda}" y1="{topo}" x2="{esquerda}" y2="{base}" stroke="#999"/>',
        f'<line x1="{esquerda}" y1="{base}" x2="{esquerda + largura}" y2="{base}" stroke="#999"/>',
        f'<text x="{esquerda - 6}" y="{topo + 5}" text-anchor="end">{reais(maior)}</text>',
        f'<text x="{esquerda - 6}" y="{base + 5}" text-anchor="end">0,00</text>',
        f'<polyline points="{pontos}" fill="none" stroke="{COR}" stroke-width="2"/>',
    ]
    if historico:
        linhas.append(f'<text x="{esquerda}" y="{base + 20}">{historico[0][0]:%d/%m/%Y}</text>')
        linhas.append(
            f'<text x="{esquerda + largura}" y="{base + 20}" text-anchor="end">{historico[-1][0]:%d/%m/%Y}</text>'
        )
    linhas.append("</svg>")
    return "\n".join(linhas)
