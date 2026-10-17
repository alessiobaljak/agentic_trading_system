"""Stampa le versioni di Python, numpy e scipy (regola 11) e le confronta con parametri_4.yaml."""
import sys
from pathlib import Path

import numpy
import scipy
import yaml

RADICE = Path(__file__).resolve().parents[4]
attese = yaml.safe_load((RADICE / "research/config/parametri_4.yaml").read_text())["versioni"]
trovate = {
    "python": ".".join(str(x) for x in sys.version_info[:3]),
    "numpy": numpy.__version__,
    "scipy": scipy.__version__,
}
for nome, valore in trovate.items():
    esito = "uguale" if str(attese.get(nome)) == valore else "DIVERSA"
    print(f"{nome}: trovata {valore}, attesa {attese.get(nome)} -> {esito}")
