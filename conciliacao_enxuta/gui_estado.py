"""As regras da janela, sem Tkinter: validar a entrada, conciliar e devolver o caminho ou a mensagem."""

from __future__ import annotations

from argparse import ArgumentTypeError
from dataclasses import dataclass
from pathlib import Path

from conciliacao_enxuta.cli import tolerancia_em_centavos
from conciliacao_enxuta.cruzamento import TOLERANCIA_PADRAO, conciliar
from conciliacao_enxuta.excel import gravar_excel
from conciliacao_enxuta.leitura import ler_base

TOLERANCIA_PADRAO_EM_TEXTO = f"{TOLERANCIA_PADRAO // 100},{TOLERANCIA_PADRAO % 100:02d}"


@dataclass(frozen=True)
class Resposta:
    """O que a janela mostra: o caminho do `.xlsx` ou, se não deu, uma mensagem simples."""

    caminho: Path | None = None
    mensagem: str = ""


def conciliar_pela_janela(base_a: str, base_b: str, tolerancia: str) -> Resposta:
    """Os textos da janela → o `.xlsx` na pasta da Base A, ou a mensagem do que falta."""
    if not base_a.strip():
        return Resposta(mensagem="Escolha o arquivo da Base A.")
    if not base_b.strip():
        return Resposta(mensagem="Escolha o arquivo da Base B.")
    try:
        centavos = tolerancia_em_centavos(tolerancia)
    except ArgumentTypeError as erro:
        return Resposta(mensagem=str(erro))
    resultado = conciliar(ler_base(Path(base_a)), ler_base(Path(base_b)), centavos)
    return Resposta(caminho=gravar_excel(resultado, Path(base_a).parent))
