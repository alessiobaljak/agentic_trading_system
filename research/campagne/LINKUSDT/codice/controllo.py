"""Controllo positivo degli strumenti (lezioni/metodo.md): una strategia con lookahead DICHIARATO.

Alla chiusura della barra i guarda la barra i+1 (futuro): se chiude sopra la sua apertura entra
long all'apertura di i+1, stop a 2 ATR(14), uscita dopo 1 barra. Deve battere nettamente la (a) e la
(b) e crollare con il ritardo di una barra. 1h, costruzione. Non e' una variante: non consuma budget.
"""
import sys
from dataclasses import replace
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import comune as C  # noqa: E402
import indicatori as I  # noqa: E402
from research.src.motore import Segnale  # noqa: E402


def prepara(candele, extra):
    o, c = I.arr(candele, "open"), I.arr(candele, "close")
    a = I.atr(candele, 14)
    n = len(c)

    def entra(i):
        return i + 1 < n and c[i + 1] > o[i + 1]  # LOOKAHEAD voluto

    def segnale(i):
        if not I.ok(a[i]):
            return None
        return Segnale("long", c[i] - 2 * a[i])

    def esci(i, ie):
        return i - ie + 1 >= 1

    return C.Prep(entra, segnale, esci)


if __name__ == "__main__":
    ctx = C.contesto("1h", "costruzione")
    for nome, par in (("senza_ritardo", C.PARAMETRI), ("ritardo_1", replace(C.PARAMETRI, ritardo_barre=1))):
        out = C.valuta(ctx, prepara, "costruzione", par)
        m = out["metriche"]
        print(nome, "trade", m["trade"], "r_medio", round(m["r_medio"], 4),
              "a:", out["baseline_a"].get("t"), out["baseline_a"].get("netta"),
              "b:", out["baseline_b"].get("t"), out["baseline_b"].get("netta"), "media_b", out["baseline_b"].get("media"))
        C.scrivi_json(C.CARTELLA_DATI / f"controllo_{nome}.json", out)
