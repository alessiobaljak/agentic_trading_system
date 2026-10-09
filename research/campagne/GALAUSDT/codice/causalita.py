"""Controllo di causalita' del codice delle varianti: condizione, segnale e uscita calcolati sulla serie
intera e sulla serie troncata alla barra k devono coincidere su tutte le barre <= k.

Uso: python -m research.campagne.GALAUSDT.codice.causalita
"""

import json

import numpy as np

from research.campagne.GALAUSDT.codice import comune
from research.campagne.GALAUSDT.codice.catalogo import CATALOGO, crea_variante


def firma(var, a, i, df):
    s = var.segnale(a, i, df)
    c = bool(var.condizione(a, i, df)) if s is not None or True else None
    return (c, None if s is None else (s.direzione, round(s.stop, 10), None if s.target is None else round(s.target, 10)))


def main():
    out = {}
    for vid in CATALOGO:
        var = crea_variante(vid)
        ctx = comune.contesto(var.tf, "costruzione")
        df = ctx.df
        a = var.prepara(df)
        n = len(df)
        rng = np.random.default_rng(0)
        tagli = sorted(set(rng.integers(300, n - 1, size=6).tolist()))
        diverse = 0
        for k in tagli:
            dk = df.iloc[: k + 1].reset_index(drop=True)
            ak = var.prepara(dk)
            for i in range(max(0, k - 50), k + 1):
                if firma(var, a, i, df) != firma(var, ak, i, dk):
                    diverse += 1
        out[vid] = diverse
    print(json.dumps(out))
    print("tutte causali" if all(v == 0 for v in out.values()) else "ATTENZIONE: differenze")


if __name__ == "__main__":
    main()
