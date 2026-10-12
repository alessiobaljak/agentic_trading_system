"""Il candidato MATICUSDT-025 (V40) in forma con parametri, per le verifiche della Fase 4.

Con i parametri predefiniti e' ESATTAMENTE V40 (``varianti.V40``): short su 1h quando lo squilibrio
taker delle ultime 6 barre e' sotto media - 2 dev. std. delle 720 barre precedenti e BTCUSDT non e'
salito nelle 24 barre prima; stop a min(2 ATR14, 6%) sopra la chiusura; uscita dopo 12 barre.
Le verifiche spostano un parametro alla volta; i parametri in barre si convertono per i timeframe
adiacenti (``barre_per_ora``).
"""
from __future__ import annotations

import numpy as np

import quadro
import varianti
from quadro import Regole

PREDEFINITI = {"finestra": 6, "k_sd": 2.0, "media": 720, "btc": 24, "tenuta": 12, "atr_n": 14,
               "atr_mult": 2.0, "tetto": 0.06}


def fabbrica(**cambi):
    p = dict(PREDEFINITI, **cambi)

    def regole(s):
        tb = varianti._taker_buy(s)
        n, f, w = s.n, int(p["finestra"]), int(p["media"])
        q = np.full(n, np.nan)
        for i in range(f - 1, n):
            v = s.v[i - f + 1:i + 1].sum()
            if v > 0:
                q[i] = tb[i - f + 1:i + 1].sum() / v - 0.5
        media = np.full(n, np.nan)
        sd = np.full(n, np.nan)
        for i in range(w + f - 1, n):
            x = q[i - w:i]
            if not np.isnan(x).any():
                media[i], sd[i] = x.mean(), x.std(ddof=1)
        a = quadro.atr(s, int(p["atr_n"]))
        btc = quadro.rendimento(s.btc_c, int(p["btc"]))
        pronto = varianti._ok(q, media, sd, a) & ~np.isnan(btc)
        ingresso = (pronto & (np.nan_to_num(q) < np.nan_to_num(media - p["k_sd"] * sd, nan=-np.inf))
                    & (np.nan_to_num(btc, nan=1.0) <= 0))
        stop = np.where(pronto, s.c + np.minimum(p["atr_mult"] * a, p["tetto"] * s.c), np.nan)
        return Regole(s, "short", ingresso, stop, tenuta=int(p["tenuta"]))

    return regole
