"""`python -m conciliacao_enxuta` abre a janela; com subcomando, é a linha de comando."""

import sys

if len(sys.argv) > 1:
    from conciliacao_enxuta.cli import main
else:
    from conciliacao_enxuta.gui import main

sys.exit(main())
