"""Gerador de bases de exemplo com gabarito.

As Diferenças são plantadas e o gabarito é montado a partir delas, sem passar pelo cruzamento.
Cada base traz uma posição por dia útil de seis meses, e a Base B traz ainda uma Data-base que a Base A não tem.
Uso: `python -m conciliacao_enxuta.exemplo [PASTA]` (padrão: `exemplo`).
"""

from __future__ import annotations

import csv
import random
import sys
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path

from conciliacao_enxuta.cruzamento import TOLERANCIA_PADRAO as TOLERANCIA

PRIMEIRA_DATA_BASE = date(2026, 4, 1)
DATA_BASE = date(2026, 9, 30)  # a mais recente comum às duas bases
SO_NA_BASE_B = date(2026, 10, 1)  # ignorada: a Base A não tem
N_CHAVES = 200


@dataclass(frozen=True)
class Gabarito:
    """O que o Resumo deve mostrar com a Tolerância padrão. Dinheiro em centavos."""

    base_a: Path
    base_b: Path
    data_base: date
    total_a: int
    total_b: int
    diferenca_total: int
    diferenca_absoluta: int
    chaves_com_diferenca: int
    data_bases_so_em_b: tuple[date, ...]


def _reais(centavos: int) -> str:
    """Centavos → texto simples como `1234.56`."""
    sinal = "-" if centavos < 0 else ""
    reais, resto = divmod(abs(centavos), 100)
    return f"{sinal}{reais}.{resto:02d}"


def _dias_uteis(inicio: date, fim: date) -> list[date]:
    dias = (inicio + timedelta(n) for n in range((fim - inicio).days + 1))
    return [d for d in dias if d.weekday() < 5]


def _escrever(caminho: Path, posicoes: dict[date, dict[str, int]]) -> None:
    with caminho.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["Chave", "Data", "Valor"])
        for data, valores in posicoes.items():
            for chave, valor in valores.items():
                w.writerow([chave, data.isoformat(), _reais(valor)])


def _posicao(sorteio: random.Random) -> tuple[dict[str, int], dict[str, int], list[int]]:
    """Uma Data-base: os valores de A e de B e as Diferenças plantadas acima da Tolerância."""
    a: dict[str, int] = {}
    b: dict[str, int] = {}
    diferencas: list[int] = []

    for i in range(1, N_CHAVES + 1):
        chave = f"C{i:05d}"
        valor = sorteio.randint(1_000, 10_000_000)
        caso = i % 10
        if caso == 1:  # Diferença acima da Tolerância, positiva ou negativa
            delta = sorteio.choice([-1, 1]) * sorteio.randint(TOLERANCIA + 1, 500_000)
            a[chave], b[chave] = valor, valor - delta
            diferencas.append(delta)
        elif caso == 2:  # Diferença dentro da Tolerância
            a[chave], b[chave] = valor, valor - sorteio.randint(-TOLERANCIA, TOLERANCIA)
        elif caso == 3:  # Só em A
            a[chave] = valor
            diferencas.append(valor)
        elif caso == 4:  # Só em B
            b[chave] = valor
            diferencas.append(-valor)
        else:
            a[chave] = b[chave] = valor

    # Órfãs dentro da Tolerância também não contam
    a["SO_A_CENTAVOS"] = TOLERANCIA
    b["SO_B_CENTAVOS"] = TOLERANCIA
    return a, b, diferencas


def gerar_bases_exemplo(pasta: str | Path) -> Gabarito:
    """Escreve `base_a.csv` e `base_b.csv` em `pasta` e devolve o gabarito."""
    pasta = Path(pasta)
    pasta.mkdir(parents=True, exist_ok=True)
    sorteio = random.Random(42)  # sempre as mesmas bases

    posicoes_a: dict[date, dict[str, int]] = {}
    posicoes_b: dict[date, dict[str, int]] = {}
    plantadas: dict[date, list[int]] = {}
    for data in _dias_uteis(PRIMEIRA_DATA_BASE, DATA_BASE):
        posicoes_a[data], posicoes_b[data], plantadas[data] = _posicao(sorteio)
    a, b, diferencas = posicoes_a[DATA_BASE], posicoes_b[DATA_BASE], plantadas[DATA_BASE]
    _, posicoes_b[SO_NA_BASE_B], _ = _posicao(sorteio)

    base_a, base_b = pasta / "base_a.csv", pasta / "base_b.csv"
    _escrever(base_a, posicoes_a)
    _escrever(base_b, posicoes_b)
    return Gabarito(
        base_a=base_a,
        base_b=base_b,
        data_base=DATA_BASE,
        total_a=sum(a.values()),
        total_b=sum(b.values()),
        diferenca_total=sum(diferencas),
        diferenca_absoluta=sum(abs(d) for d in diferencas),
        chaves_com_diferenca=len(diferencas),
        data_bases_so_em_b=(SO_NA_BASE_B,),
    )


if __name__ == "__main__":
    print(gerar_bases_exemplo(sys.argv[1] if len(sys.argv) > 1 else "exemplo"))
