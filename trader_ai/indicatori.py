"""Gli indicatori calcolati dal codice sull'ultima candela chiusa (REGOLE.md, versione 3, sezione 4). Formule di manuale,
senza librerie: medie esponenziali, RSI di Wilder, MACD 12-26-9, bande di Bollinger 20-2, ATR di Wilder, VWAP del giorno UTC,
volume rispetto alla media di 20. Ogni candela: dict con apertura, massimo, minimo, chiusura, volume, chiusa (datetime)."""
from __future__ import annotations

import math
from typing import Dict, List, Optional


def ema(valori: List[float], n: int) -> List[float]:
    if not valori:
        return []
    k = 2 / (n + 1)
    out = [valori[0]]
    for v in valori[1:]:
        out.append(v * k + out[-1] * (1 - k))
    return out


def rsi(chiusure: List[float], n: int = 14) -> Optional[float]:
    if len(chiusure) <= n:
        return None
    su = [max(chiusure[i] - chiusure[i - 1], 0) for i in range(1, len(chiusure))]
    giu = [max(chiusure[i - 1] - chiusure[i], 0) for i in range(1, len(chiusure))]
    ms, mg = sum(su[:n]) / n, sum(giu[:n]) / n
    for s, g in zip(su[n:], giu[n:]):
        ms, mg = (ms * (n - 1) + s) / n, (mg * (n - 1) + g) / n
    return 100.0 if mg == 0 else 100 - 100 / (1 + ms / mg)


def atr(candele: List[dict], n: int = 14) -> Optional[float]:
    if len(candele) <= n:
        return None
    tr = [max(c["massimo"] - c["minimo"], abs(c["massimo"] - p["chiusura"]), abs(c["minimo"] - p["chiusura"]))
          for p, c in zip(candele, candele[1:])]
    a = sum(tr[:n]) / n
    for t in tr[n:]:
        a = (a * (n - 1) + t) / n
    return a


def riassunto(candele: List[dict]) -> Dict[str, Optional[float]]:
    c = [x["chiusura"] for x in candele]
    if not c:
        return {}
    e12, e26 = ema(c, 12), ema(c, 26)
    macd = [a - b for a, b in zip(e12, e26)]
    segnale = ema(macd, 9)
    ultimi = c[-20:]
    media = sum(ultimi) / len(ultimi)
    dev = math.sqrt(sum((x - media) ** 2 for x in ultimi) / len(ultimi))
    giorno = candele[-1]["chiusa"].date()
    oggi = [x for x in candele if x["chiusa"].date() == giorno]
    vol_oggi = sum(x["volume"] for x in oggi)
    vwap = (sum((x["massimo"] + x["minimo"] + x["chiusura"]) / 3 * x["volume"] for x in oggi) / vol_oggi) if vol_oggi else None
    vols = [x["volume"] for x in candele[-21:-1]]
    return {
        "ema9": ema(c, 9)[-1], "ema21": ema(c, 21)[-1], "ema50": ema(c, 50)[-1],
        "rsi14": rsi(c, 14),
        "macd": macd[-1], "macd_segnale": segnale[-1], "macd_istogramma": macd[-1] - segnale[-1],
        "bollinger_alta": media + 2 * dev, "bollinger_media": media, "bollinger_bassa": media - 2 * dev,
        "atr14": atr(candele, 14),
        "vwap_giorno": vwap,
        "volume_su_media20": (candele[-1]["volume"] / (sum(vols) / len(vols))) if vols and sum(vols) else None,
    }
