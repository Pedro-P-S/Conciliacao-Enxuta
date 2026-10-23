"""Linha de comando: `python -m conciliacao_enxuta conciliar BASE_A BASE_B [--tolerancia 1,00] [--saida PASTA]`."""

from __future__ import annotations

import argparse
import sys
from decimal import Decimal, InvalidOperation
from pathlib import Path

from conciliacao_enxuta.cruzamento import TOLERANCIA_PADRAO, SemDataBaseComum, conciliar
from conciliacao_enxuta.excel import gravar_excel
from conciliacao_enxuta.leitura import ErroDeLeitura, ler_base


def tolerancia_em_centavos(texto: str) -> int:
    """'1,00' → 100; '0,50' → 50. Recusa o que não for um valor em reais finito e não negativo."""
    try:
        reais = Decimal(texto.strip().replace(",", "."))
    except InvalidOperation:
        reais = None
    if reais is None or not reais.is_finite() or reais < 0:
        raise argparse.ArgumentTypeError(f"Tolerância inválida: {texto!r}. Use, por exemplo, 1,00.")
    return int((reais * 100).to_integral_value())


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m conciliacao_enxuta", description="Conciliação Enxuta")
    comandos = parser.add_subparsers(dest="comando", required=True)
    comando_conciliar = comandos.add_parser("conciliar", help="cruza a Base A com a Base B e gera o .xlsx")
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
        resultado = conciliar(ler_base(args.base_a), ler_base(args.base_b), args.tolerancia)
    except (ErroDeLeitura, SemDataBaseComum) as erro:
        print(erro, file=sys.stderr)
        return 1
    caminho = gravar_excel(resultado, args.saida or args.base_a.parent)
    print(caminho)
    return 0
