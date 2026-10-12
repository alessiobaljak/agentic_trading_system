"""Conta, registra e testa in SERIE una lista di varianti (ognuna: registra.py poi testa.py).

Uso: python research/campagne/ETHUSDT/codice/lotto.py I-01b I-02a ...

Per ogni variante: prima registra.py (conteggio e voce nel log), poi, solo se la voce e'
una registrazione, testa.py. Una alla volta, nell'ordine dato. L'avanzamento va in
data/insample/ETHUSDT/lavoro/lotto.txt (la sessione legge solo li').
"""

import subprocess
import sys
from pathlib import Path

QUI = Path(__file__).resolve().parent
RADICE = QUI.parents[3]
AVANZAMENTO = RADICE / "research" / "data" / "insample" / "ETHUSDT" / "lavoro" / "lotto.txt"


def scrivi(riga: str) -> None:
    with open(AVANZAMENTO, "a", encoding="utf-8") as f:
        f.write(riga + "\n")


def main() -> None:
    for nome in sys.argv[1:]:
        r = subprocess.run([sys.executable, str(QUI / "registra.py"), nome], capture_output=True, text=True, cwd=RADICE)
        scrivi(f"[registra {nome}] {r.stdout.strip()} {r.stderr.strip()[-500:]}")
        if r.returncode != 0 or "registrazione" not in r.stdout:
            continue
        t = subprocess.run([sys.executable, str(QUI / "testa.py"), nome], capture_output=True, text=True, cwd=RADICE)
        scrivi(f"[testa {nome}] {t.stdout.strip()} {t.stderr.strip()[-500:]}")
    scrivi("fine lotto")


if __name__ == "__main__":
    main()
