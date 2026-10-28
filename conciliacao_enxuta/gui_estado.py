"""As regras da janela, sem Tkinter: validar a entrada, conciliar e devolver o caminho ou a mensagem."""

from __future__ import annotations

import os
import traceback
from argparse import ArgumentTypeError
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from conciliacao_enxuta.cli import ArquivoNaoGravado, conciliar_arquivos, tolerancia_em_centavos
from conciliacao_enxuta.cruzamento import TOLERANCIA_PADRAO, SemDataBaseComum
from conciliacao_enxuta.leitura import ErroDeLeitura

TOLERANCIA_PADRAO_EM_TEXTO = f"{TOLERANCIA_PADRAO // 100},{TOLERANCIA_PADRAO % 100:02d}"


@dataclass(frozen=True)
class Resposta:
    """O que a janela mostra: o caminho do `.xlsx` ou, se não deu, uma mensagem simples."""

    caminho: Path | None = None
    mensagem: str = ""
    avisos: tuple[str, ...] = ()


def _gravar_traceback(erro: Exception) -> Path:
    """Acrescenta o traceback de `erro` a `%LOCALAPPDATA%/ConciliacaoEnxuta/erros.log`, criando a pasta se faltar."""
    log = Path(os.environ["LOCALAPPDATA"]) / "ConciliacaoEnxuta" / "erros.log"
    log.parent.mkdir(parents=True, exist_ok=True)
    with log.open("a", encoding="utf-8") as arquivo:
        arquivo.write(f"--- {datetime.now():%Y-%m-%d %H:%M:%S} ---\n")
        arquivo.write("".join(traceback.format_exception(erro)))
    return log


def _caminho_limpo(texto: str) -> str:
    """Tira o espaço das pontas e as aspas do "Copiar como caminho" do Windows."""
    return texto.strip().strip('"').strip()


def conciliar_pela_janela(base_a: str, base_b: str, tolerancia: str) -> Resposta:
    """Os textos da janela → o `.xlsx` e o `.html` na pasta da Base A (a resposta traz o do `.xlsx`), ou a mensagem do que falta."""
    base_a, base_b = _caminho_limpo(base_a), _caminho_limpo(base_b)
    if not base_a:
        return Resposta(mensagem="Escolha o arquivo da Base A.")
    if not base_b:
        return Resposta(mensagem="Escolha o arquivo da Base B.")
    try:
        centavos = tolerancia_em_centavos(tolerancia)
    except ArgumentTypeError as erro:
        return Resposta(mensagem=str(erro))
    try:
        xlsx, _, avisos = conciliar_arquivos(Path(base_a), Path(base_b), centavos, Path(base_a).parent)
        return Resposta(caminho=xlsx, avisos=tuple(avisos))
    except (ErroDeLeitura, SemDataBaseComum, ArquivoNaoGravado) as erro:
        return Resposta(mensagem=str(erro))
    except Exception as erro:
        try:
            log = _gravar_traceback(erro)
        except Exception:
            return Resposta(mensagem="Algo deu errado e a conciliação não foi feita. Os detalhes não puderam ser gravados no erros.log.")
        return Resposta(mensagem=f"Algo deu errado e a conciliação não foi feita. Os detalhes estão em {log}.")
