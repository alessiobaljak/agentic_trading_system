"""Le varianti della campagna FILUSDT, una funzione per ognuna (regole esatte registrate nel log).

Ogni funzione restituisce una ``quadro.Variante``. Le regole stanno anche in ``ipotesi.md``.
"""
from __future__ import annotations

import numpy as np

import quadro as q
from quadro import Variante


def _stop_atr(direzione: str, n_atr: int, k: float):
    def f(s):
        a = q.atr(s, n_atr)
        return s.c - k * a if direzione == "long" else s.c + k * a
    return f


# ---------------------------------------------------------------------------
# Controllo positivo degli strumenti (lezioni/metodo.md): NON e' una variante.
# ---------------------------------------------------------------------------

def controllo_positivo() -> Variante:
    """Lookahead dichiarato: entra long se la barra SUCCESSIVA chiude oltre l'1% sopra la sua apertura."""
    def ingresso(s):
        prossima_su = np.zeros(len(s.c), dtype=bool)
        prossima_su[:-1] = s.c[1:] > s.o[1:] * 1.01
        return prossima_su
    return Variante("FILUSDT-CONTROLLO", "4h", "long", ingresso, _stop_atr("long", 14, 2.0), barre_max=1,
                    descrizione="lookahead dichiarato: legge la barra dopo")


# ---------------------------------------------------------------------------
# I-01 Momento della serie storica (4h, 42 barre)
# ---------------------------------------------------------------------------

def i01(direzione: str, id_: str) -> Variante:
    def ingresso(s):
        r = q.rendimento(s.c, 42)
        return (r > 0) if direzione == "long" else (r < 0)
    return Variante(id_, "4h", direzione, ingresso, _stop_atr(direzione, 14, 2.0), barre_max=42,
                    descrizione=f"I-01 momento settimanale {direzione}")


# ---------------------------------------------------------------------------
# I-02 Rottura del canale (4h, 30 barre, uscita a canale opposto di 15 barre)
# ---------------------------------------------------------------------------

def i02(direzione: str, id_: str, n_in: int = 30, n_out: int = 15) -> Variante:
    def ingresso(s):
        if direzione == "long":
            return s.c > q.massimo_precedente(s.h, n_in)
        return s.c < q.minimo_precedente(s.l, n_in)

    def uscita(s):
        if direzione == "long":
            return s.c < q.minimo_precedente(s.l, n_out)
        return s.c > q.massimo_precedente(s.h, n_out)
    return Variante(id_, "4h", direzione, ingresso, _stop_atr(direzione, 14, 2.0), uscita=uscita,
                    descrizione=f"I-02 rottura del canale {direzione}")


# ---------------------------------------------------------------------------
# I-03 Inversione dopo movimenti estremi di 24 ore (1h)
# ---------------------------------------------------------------------------

def _z24(s):
    r1 = q.rendimento(s.c, 1)
    sd = q.dev_std_mobile(np.nan_to_num(r1, nan=0.0), 720)
    sd[:720] = np.nan
    return q.rendimento(s.c, 24) / (sd * np.sqrt(24))


def i03(direzione: str, id_: str) -> Variante:
    def ingresso(s):
        z = _z24(s)
        return (z < -2) if direzione == "long" else (z > 2)
    return Variante(id_, "1h", direzione, ingresso, _stop_atr(direzione, 24, 3.0), barre_max=24,
                    descrizione=f"I-03 inversione dopo 24 ore estreme {direzione}")


TUTTE = {
    "controllo": controllo_positivo,
    "FILUSDT-001": lambda: i01("long", "FILUSDT-001"),
    "FILUSDT-002": lambda: i01("short", "FILUSDT-002"),
    "FILUSDT-003": lambda: i02("long", "FILUSDT-003"),
    "FILUSDT-004": lambda: i02("short", "FILUSDT-004"),
    "FILUSDT-005": lambda: i03("long", "FILUSDT-005"),
    "FILUSDT-006": lambda: i03("short", "FILUSDT-006"),
    "FILUSDT-007": lambda: i02("long", "FILUSDT-007", 20, 10),
    "FILUSDT-008": lambda: i02("short", "FILUSDT-008", 20, 10),
}
