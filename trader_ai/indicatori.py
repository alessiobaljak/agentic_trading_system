"""Gli indicatori calcolati dal codice sulle candele chiuse (REGOLE.md, sezione 4). Formule di manuale, senza librerie: medie
esponenziali, RSI di Wilder, MACD 12-26-9, bande di Bollinger 20-2, ATR di Wilder, volume rispetto alla media di 20, ampiezza mediana
delle ultime 20 candele. Dal 26 novembre 2026 anche gli ultimi 4 valori di RSI, istogramma del MACD e volume sulla media (controllo del
26 novembre, punto 3.9: un valore solo non dice dove va l'indicatore); il VWAP è uno solo, del giorno UTC, nel blocco della moneta
(punto 2.8). Ogni candela: dict con apertura, massimo, minimo, chiusura, volume."""
from __future__ import annotations

import math
from statistics import median
from typing import Dict, List, Optional

ULTIMI = 4


def ema(valori: List[float], n: int) -> List[float]:
    if not valori:
        return []
    k = 2 / (n + 1)
    out = [valori[0]]
    for v in valori[1:]:
        out.append(v * k + out[-1] * (1 - k))
    return out


def rsi_serie(chiusure: List[float], n: int = 14) -> List[Optional[float]]:
    """L'RSI di Wilder a ogni candela (None finché non ci sono n variazioni)."""
    out: List[Optional[float]] = [None] * len(chiusure)
    if len(chiusure) <= n:
        return out
    su = [max(chiusure[i] - chiusure[i - 1], 0) for i in range(1, len(chiusure))]
    giu = [max(chiusure[i - 1] - chiusure[i], 0) for i in range(1, len(chiusure))]
    ms, mg = sum(su[:n]) / n, sum(giu[:n]) / n

    def valore(a, b):
        return 100.0 if b == 0 else 100 - 100 / (1 + a / b)
    out[n] = valore(ms, mg)
    for i, (s, g) in enumerate(zip(su[n:], giu[n:]), start=n + 1):
        ms, mg = (ms * (n - 1) + s) / n, (mg * (n - 1) + g) / n
        out[i] = valore(ms, mg)
    return out


def rsi(chiusure: List[float], n: int = 14) -> Optional[float]:
    return rsi_serie(chiusure, n)[-1] if chiusure else None


def atr(candele: List[dict], n: int = 14) -> Optional[float]:
    if len(candele) <= n:
        return None
    tr = [max(c["massimo"] - c["minimo"], abs(c["massimo"] - p["chiusura"]), abs(c["minimo"] - p["chiusura"]))
          for p, c in zip(candele, candele[1:])]
    a = sum(tr[:n]) / n
    for t in tr[n:]:
        a = (a * (n - 1) + t) / n
    return a


def vwap(candele: List[dict]) -> Optional[float]:
    vol = sum(x["volume"] for x in candele)
    return sum((x["massimo"] + x["minimo"] + x["chiusura"]) / 3 * x["volume"] for x in candele) / vol if vol else None


def riassunto(candele: List[dict]) -> Dict[str, object]:
    c = [x["chiusura"] for x in candele]
    if not c:
        return {}
    e12, e26 = ema(c, 12), ema(c, 26)
    macd = [a - b for a, b in zip(e12, e26)]
    segnale = ema(macd, 9)
    istogramma = [a - b for a, b in zip(macd, segnale)]
    ultimi = c[-20:]
    media = sum(ultimi) / len(ultimi)
    dev = math.sqrt(sum((x - media) ** 2 for x in ultimi) / len(ultimi))
    vol = [x["volume"] for x in candele]
    rapporti = []
    for i in range(max(0, len(vol) - ULTIMI), len(vol)):
        prima = vol[max(0, i - 20):i]
        rapporti.append(vol[i] / (sum(prima) / len(prima)) if prima and sum(prima) else None)
    return {
        "ema9": ema(c, 9)[-1], "ema21": ema(c, 21)[-1], "ema50": ema(c, 50)[-1],
        "rsi14": rsi(c, 14),
        "macd": macd[-1], "macd_segnale": segnale[-1], "macd_istogramma": istogramma[-1],
        "bollinger_alta": media + 2 * dev, "bollinger_media": media, "bollinger_bassa": media - 2 * dev,
        "atr14": atr(candele, 14),
        "volume_su_media20": rapporti[-1] if rapporti else None,
        "ampiezza_mediana20": median(x["massimo"] - x["minimo"] for x in candele[-20:]),
        "ultimi_rsi14": rsi_serie(c, 14)[-ULTIMI:],
        "ultimi_macd_istogramma": istogramma[-ULTIMI:],
        "ultimi_volume_su_media20": rapporti,
    }
