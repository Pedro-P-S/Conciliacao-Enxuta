"""Linha de comando: `python -m conciliacao_enxuta conciliar BASE_A BASE_B [--tolerancia 1,00] [--saida PASTA]`."""

from __future__ import annotations

import argparse
import sys
from dataclasses import replace
from pathlib import Path

import polars as pl

from conciliacao_enxuta.cruzamento import TOLERANCIA_PADRAO, Resultado, SemDataBaseComum, conciliar
from conciliacao_enxuta.excel import gravar_excel
from conciliacao_enxuta.html import gravar_html
from conciliacao_enxuta.leitura import ErroDeLeitura, centavos, ler_batimentos


class ArquivoNaoGravado(Exception):
    """O `.xlsx` não pôde ser gravado (aberto no Excel, ou a pasta de saída não existe); nem ele nem o `.html` mudaram."""


def conciliar_batimentos(base_a: Path, base_b: Path, tolerancia: int) -> tuple[list[Resultado], list[str]]:
    """Lê as duas bases e concilia cada Batimento (coluna de valor nas duas), na ordem da Base A.
    Devolve os Resultados e os avisos das colunas de valor que estão só numa base."""
    lidas_a, lidas_b = ler_batimentos(base_a), ler_batimentos(base_b)
    comuns = [chave for chave in lidas_a if chave in lidas_b]
    if not comuns:
        raise ErroDeLeitura("A Base A e a Base B não têm nenhuma coluna de valor em comum.")
    avisos = [f"{lida.coluna} só na Base A: não conciliado" for chave, lida in lidas_a.items() if chave not in lidas_b]
    avisos += [f"{lida.coluna} só na Base B: não conciliado" for chave, lida in lidas_b.items() if chave not in lidas_a]
    resultados = [
        replace(
            conciliar(
                lidas_a[c].base, lidas_b[c].base, tolerancia,
                lidas_a[c].rejeitadas, lidas_b[c].rejeitadas, lidas_a[c].datas, lidas_b[c].datas,
            ),
            batimento=lidas_a[c].nome,
        )
        for c in comuns
    ]
    return resultados, avisos


def conciliar_arquivos(base_a: Path, base_b: Path, tolerancia: int, pasta: Path) -> tuple[Path, Path, list[str]]:
    """Lê as duas bases, concilia e grava o `.xlsx` e depois o `.html` em `pasta`. Devolve os dois caminhos e os avisos."""
    resultados, avisos = conciliar_batimentos(base_a, base_b, tolerancia)
    if not pasta.is_dir():
        raise ArquivoNaoGravado(f"{pasta}: a pasta de saída não existe.")
    try:
        xlsx = gravar_excel(resultados, pasta)
    except PermissionError as erro:
        # Só o arquivo que já existe pode estar aberto no Excel; senão, falta permissão na pasta
        if Path(erro.filename).exists():
            raise ArquivoNaoGravado(
                f"{Path(erro.filename).name}: não deu para gravar; feche o arquivo no Excel e tente de novo."
            ) from erro
        raise ArquivoNaoGravado(f"{pasta}: não deu para gravar na pasta de saída; falta permissão.") from erro
    return xlsx, gravar_html(resultados, pasta), avisos


def tolerancia_em_centavos(texto: str) -> int:
    """'1,00' → 100; '1.000' → 100000; '0,50' → 50. Lida como o Valor das bases, com o mesmo arredondamento.

    Recusa o que o Valor recusaria (inclusive o grande demais) e o negativo.
    """
    lida = pl.select(centavos(pl.lit(texto.strip()))).item()
    if lida is None or lida < 0:
        raise argparse.ArgumentTypeError(f"Tolerância inválida: {texto!r}. Use, por exemplo, 1,00.")
    return lida


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m conciliacao_enxuta", description="Conciliação Enxuta")
    comandos = parser.add_subparsers(dest="comando", required=True)
    comando_conciliar = comandos.add_parser("conciliar", help="cruza a Base A com a Base B e gera o .xlsx e o .html")
    comando_conciliar.add_argument("base_a", type=Path, help="arquivo da Base A")
    comando_conciliar.add_argument("base_b", type=Path, help="arquivo da Base B")
    comando_conciliar.add_argument(
        "--tolerancia", type=tolerancia_em_centavos, default=TOLERANCIA_PADRAO, help="em reais (padrão 1,00)"
    )
    comando_conciliar.add_argument("--saida", type=Path, help="pasta do resultado (padrão: a pasta da Base A)")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        *caminhos, avisos = conciliar_arquivos(args.base_a, args.base_b, args.tolerancia, args.saida or args.base_a.parent)
    except (ErroDeLeitura, SemDataBaseComum, ArquivoNaoGravado) as erro:
        print(erro, file=sys.stderr)
        return 1
    except Exception as erro:
        print(f"Algo deu errado e a conciliação não foi feita: {erro}", file=sys.stderr)
        return 1
    for aviso in avisos:
        print(aviso, file=sys.stderr)
    for caminho in caminhos:
        print(caminho)
    return 0
