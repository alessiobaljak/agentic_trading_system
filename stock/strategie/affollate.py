"""Le azioni più vendute allo scoperto (giorni per ricomprarle), con la soglia larga (`stock/prove/P024_vendite_allo_scoperto.md`)."""
from __future__ import annotations

import bisect
from datetime import date

import numpy as np
import pandas as pd

from stock.simulatore.portafoglio import Storia, StatoConto, verso_pesi
from stock.strategie.rimbalzo import giorni_dopo

RITARDO = 10            # giorni di borsa dopo la data di regolamento prima di usare i dati di FINRA
COMPLETO = 0.9          # il controllo dei dati: almeno il 90%
ENTRA, ESCE = 0.2, 0.4  # la soglia larga
SEDUTE_VOL = 63


def giorni_per_ricomprare(finra: pd.DataFrame, cambi: dict[str, str]) -> dict[date, dict[str, float]]:
    """Per ogni data di regolamento: simbolo (con i cambi di simbolo applicati) -> giorni per ricomprarle."""
    out: dict[date, dict[str, float]] = {}
    for d, g in finra.groupby("settlementDate"):
        v = {}
        for s, x in zip(g["symbolCode"], g["daysToCoverQuantity"]):
            if isinstance(s, str) and x is not None and np.isfinite(x) and x >= 0:
                v[cambi.get(s, s)] = float(x)
        out[d] = v
    return out


def data_utilizzabile(giorno: date, date_finra: list[date], calendario: list[date]) -> int:
    """L'indice dell'ultima data di FINRA utilizzabile il `giorno` (RITARDO giorni di borsa dopo il regolamento), o -1."""
    pos = bisect.bisect_right(calendario, giorno) - 1
    limite = calendario[pos - RITARDO] if pos - RITARDO >= 0 else None
    if limite is None:
        return -1
    return bisect.bisect_right(date_finra, limite) - 1


def scegli_data(k: int, date_finra: list[date], gpr: dict[date, dict[str, float]], membri: list[str]) -> int:
    """Il controllo dei dati: si scende alla data prima finché i membri coperti non sono almeno il 90% di quelli della data prima."""
    while k > 0:
        ora = sum(1 for m in membri if m in gpr[date_finra[k]])
        prima = sum(1 for m in membri if m in gpr[date_finra[k - 1]])
        if prima == 0 or ora >= COMPLETO * prima:
            return k
        k -= 1
    return k


def soglia_larga(valori: dict[str, float], dentro: set[str], piu_alti: bool) -> set[str]:
    """Entra chi è nel 20% della classifica, resta chi è ancora nel 40%."""
    ordine = sorted(valori, key=lambda s: (-valori[s], s) if piu_alti else (valori[s], s))
    n = len(ordine)
    rango = {s: i for i, s in enumerate(ordine)}
    return {s for s in ordine if rango[s] < ENTRA * n} | {s for s in dentro if s in rango and rango[s] < ESCE * n}


def pesi_inversi(scelti: set[str], vol: dict[str, float], quota: float) -> dict[str, float]:
    inv = {s: 1 / vol[s] for s in scelti if vol.get(s, 0) > 0}
    tot = sum(inv.values())
    return {s: quota * v / tot for s, v in inv.items()} if tot else {}


def strategia_affollate(membri, calendario: list[date], rettificati: dict[str, pd.Series],
                        gpr: dict[date, dict[str, float]], variante: str, diario: list | None = None):
    """`variante`: "A" (50% comprato nei meno affollati, 50% venduto nei più affollati) o "B" (SPY 100% e 30% venduto nei più
    affollati). `diario` raccoglie una riga per decisione (data di FINRA usata, quanti titoli per lato)."""
    dopo = giorni_dopo(calendario)
    date_finra = sorted(gpr)
    corti: set[str] = set()
    lunghi: set[str] = set()
    in_attesa = {"si": False}

    def decidi(giorno: date, storia: Storia, stato: StatoConto) -> list:
        nonlocal corti, lunghi
        prossimo = dopo.get(giorno)
        fine_mese = prossimo is not None and prossimo.month != giorno.month
        if not (fine_mese or in_attesa["si"]) or prossimo is None:
            return []
        m = membri(giorno)
        con_barra = {s for s in m if (h := storia(s)) is not None and not h.empty and h.index[-1] == giorno}
        if len(con_barra) < COMPLETO * len(m):
            in_attesa["si"] = True               # il controllo dei dati: giorno incompleto, si decide il giorno dopo
            return []
        k = data_utilizzabile(giorno, date_finra, calendario)
        if k < 0:
            return []
        k = scegli_data(k, date_finra, gpr, m)
        dtc = gpr[date_finra[k]]
        valori, vol, prezzi = {}, {}, {}
        for s in con_barra:
            r = rettificati.get(s)
            if s not in dtc or r is None:
                continue
            passato = r.loc[:giorno]
            if len(passato) < SEDUTE_VOL + 1:
                continue
            v = float(passato.iloc[-SEDUTE_VOL - 1:].pct_change().dropna().std(ddof=1))
            if not np.isfinite(v) or v <= 0:
                continue
            valori[s], vol[s] = dtc[s], v
            prezzi[s] = float(storia(s)["close"].iloc[-1])
        if len(valori) < 100:
            return []
        in_attesa["si"] = False
        corti = soglia_larga(valori, corti, piu_alti=True)
        pesi = {s: -w for s, w in pesi_inversi(corti, vol, 0.5 if variante == "A" else 0.3).items()}
        if variante == "A":
            lunghi = soglia_larga(valori, lunghi, piu_alti=False)
            pesi.update(pesi_inversi(lunghi, vol, 0.5))
        else:
            h = storia("SPY")
            if h is None or h.empty or h.index[-1] != giorno:
                return []
            pesi["SPY"] = 1.0
            prezzi["SPY"] = float(h["close"].iloc[-1])
        for s in stato.azioni:
            if s not in prezzi:
                h = storia(s)
                if h is not None and not h.empty:
                    prezzi[s] = float(h["close"].iloc[-1])
        if diario is not None:
            diario.append({"giorno": giorno, "finra": date_finra[k], "titoli": len(valori), "corti": len(corti),
                           "lunghi": len(lunghi)})
        return verso_pesi(stato, pesi, prezzi, etichetta="mese")
    return decidi
