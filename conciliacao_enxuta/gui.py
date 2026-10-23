"""A janela Tkinter. É casca: as regras ficam em `gui_estado`.

Com `CONCILIACAO_AUTOTESTE=1`, a janela monta escondida, fecha sozinha e sai com 0 (ou 1, se falhar).
"""

from __future__ import annotations

import os
import tkinter as tk
from tkinter import filedialog, ttk

from conciliacao_enxuta.gui_estado import TOLERANCIA_PADRAO_EM_TEXTO, conciliar_pela_janela

TIPOS_DE_ARQUIVO = [("Bases", "*.csv *.xlsx *.parquet"), ("Todos os arquivos", "*.*")]


class Janela:
    def __init__(self, raiz: tk.Tk) -> None:
        raiz.title("Conciliação Enxuta")
        self.base_a = tk.StringVar()
        self.base_b = tk.StringVar()
        self.tolerancia = tk.StringVar(value=TOLERANCIA_PADRAO_EM_TEXTO)
        self.situacao = tk.StringVar()
        self.pasta_do_resultado = None

        quadro = ttk.Frame(raiz, padding=12)
        quadro.grid()
        for linha, (rotulo, variavel) in enumerate([("Base A", self.base_a), ("Base B", self.base_b)]):
            ttk.Label(quadro, text=rotulo).grid(row=linha, column=0, sticky="w")
            ttk.Entry(quadro, textvariable=variavel, width=60).grid(row=linha, column=1, padx=6, pady=3)
            ttk.Button(quadro, text="Procurar", command=lambda v=variavel: self._procurar(v)).grid(row=linha, column=2)
        ttk.Label(quadro, text="Tolerância (R$)").grid(row=2, column=0, sticky="w")
        ttk.Entry(quadro, textvariable=self.tolerancia, width=10).grid(row=2, column=1, sticky="w", padx=6, pady=3)
        ttk.Button(quadro, text="Conciliar", command=self._conciliar).grid(row=3, column=1, sticky="w", padx=6, pady=6)
        ttk.Label(quadro, textvariable=self.situacao, wraplength=520).grid(row=4, column=0, columnspan=3, sticky="w")
        self.abrir_pasta = ttk.Button(quadro, text="Abrir pasta", command=self._abrir_pasta, state="disabled")
        self.abrir_pasta.grid(row=5, column=1, sticky="w", padx=6, pady=6)

    def _procurar(self, variavel: tk.StringVar) -> None:
        caminho = filedialog.askopenfilename(filetypes=TIPOS_DE_ARQUIVO)
        if caminho:
            variavel.set(caminho)

    def _conciliar(self) -> None:
        resposta = conciliar_pela_janela(self.base_a.get(), self.base_b.get(), self.tolerancia.get())
        if resposta.caminho is None:
            self.pasta_do_resultado = None
            self.situacao.set(resposta.mensagem)
            self.abrir_pasta.state(["disabled"])
            return
        self.pasta_do_resultado = resposta.caminho.parent
        self.situacao.set(f"Resultado: {resposta.caminho}")
        self.abrir_pasta.state(["!disabled"])

    def _abrir_pasta(self) -> None:
        if self.pasta_do_resultado is not None:
            os.startfile(self.pasta_do_resultado)


def main() -> int:
    raiz = tk.Tk()
    autoteste = os.environ.get("CONCILIACAO_AUTOTESTE") == "1"
    if autoteste:
        raiz.withdraw()
    Janela(raiz)
    if autoteste:
        raiz.after(100, raiz.destroy)
    raiz.mainloop()
    return 0
