"""I controlli dei prezzi: frazionamenti, dividendi, buchi, orari.

Ogni controllo restituisce un elenco di problemi (dizionari con `controllo`, `quando`, `dettaglio`):
vuoto vuol dire che il controllo è passato. Nessun controllo corregge i dati in silenzio.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

NY = "America/New_York"


def _problema(controllo: str, quando, dettaglio: str) -> dict:
    return {"controllo": controllo, "quando": str(quando), "dettaglio": dettaglio}


def date_ny(indice: pd.DatetimeIndex) -> pd.Index:
    """Il giorno di New York di ogni barra (le barre giornaliere di Alpaca hanno l'ora 04:00 o
    05:00 UTC, cioè la mezzanotte di New York)."""
    return pd.Index(indice.tz_convert(NY).date)


def controlla_barre(df: pd.DataFrame) -> list[dict]:
    """Coerenza interna: prezzi positivi, minimo ≤ apertura/chiusura ≤ massimo, volume non negativo,
    tempi in ordine e senza doppioni."""
    p: list[dict] = []
    if df.index.has_duplicates:
        for t in df.index[df.index.duplicated()].unique():
            p.append(_problema("doppione", t, "barra ripetuta"))
    if not df.index.is_monotonic_increasing:
        p.append(_problema("ordine", "-", "le barre non sono in ordine di tempo"))
    prezzi = df[["open", "high", "low", "close"]]
    for t in df.index[(prezzi <= 0).any(axis=1) | prezzi.isna().any(axis=1)]:
        p.append(_problema("prezzo", t, "prezzo mancante, zero o negativo"))
    tolleranza = 1e-9
    basso = df["low"] > df[["open", "close"]].min(axis=1) + tolleranza
    alto = df["high"] < df[["open", "close"]].max(axis=1) - tolleranza
    for t in df.index[basso | alto]:
        p.append(_problema("ohlc", t, "minimo o massimo incoerenti con apertura e chiusura"))
    for t in df.index[df["volume"] < 0]:
        p.append(_problema("volume", t, "volume negativo"))
    return p


def controlla_giorni(df_giorno: pd.DataFrame, cal: pd.DataFrame) -> list[dict]:
    """Ogni giorno di borsa del calendario ha la sua barra, e nessuna barra cade in un giorno chiuso.
    Si guarda solo l'intervallo coperto dalle barre."""
    if df_giorno.empty:
        return [_problema("buco", "-", "nessuna barra")]
    giorni = set(date_ny(df_giorno.index))
    primo, ultimo = min(giorni), max(giorni)
    attesi = {d for d in cal.index if primo <= d <= ultimo}
    p = [_problema("buco", d, "giorno di borsa senza barra") for d in sorted(attesi - giorni)]
    p += [_problema("giorno chiuso", d, "barra in un giorno senza seduta") for d in sorted(giorni - attesi)]
    return p


def controlla_minuti(df_min: pd.DataFrame, cal: pd.DataFrame, minimo_quota: float = 0.95) -> tuple[list[dict], dict]:
    """Le barre al minuto rispetto alla seduta di ogni giorno (9:30-16:00 di New York, o la chiusura
    anticipata). Segnala i giorni in cui, dentro la seduta, ci sono meno di `minimo_quota` dei minuti
    attesi, e le barre in giorni senza seduta. Restituisce anche il riepilogo: quante barre stanno
    dentro la seduta e quante fuori (le ore prima e dopo, 4:00-9:30 e 16:00-20:00)."""
    p: list[dict] = []
    if df_min.empty:
        return [_problema("buco", "-", "nessuna barra")], {"dentro": 0, "fuori": 0, "giorni": 0}
    t_ny = df_min.index.tz_convert(NY)
    giorni = pd.Index(t_ny.date)
    dentro_tot = 0
    for d, idx in pd.Series(np.arange(len(df_min)), index=giorni).groupby(level=0):
        if d not in cal.index:
            p.append(_problema("giorno chiuso", d, f"{len(idx)} barre al minuto in un giorno senza seduta"))
            continue
        ap, ch = cal.loc[d, "apertura"], cal.loc[d, "chiusura"]
        tt = t_ny[idx.values]
        dentro = int(((tt >= ap) & (tt < ch)).sum())
        dentro_tot += dentro
        attesi = int((ch - ap).total_seconds() // 60)
        if dentro < minimo_quota * attesi:
            p.append(_problema("minuti mancanti", d, f"{dentro} minuti su {attesi} nella seduta"))
    primo, ultimo = min(giorni), max(giorni)
    visti = set(giorni)
    for d in cal.index:
        if primo <= d <= ultimo and d not in visti:
            p.append(_problema("buco", d, "giorno di borsa senza barre al minuto"))
    riepilogo = {"dentro": dentro_tot, "fuori": int(len(df_min) - dentro_tot), "giorni": int(giorni.nunique())}
    return p, riepilogo


def controlla_salti(df_giorno_raw: pd.DataFrame, azioni: pd.DataFrame, soglia: float = 0.25) -> list[dict]:
    """Sui prezzi NON rettificati: un salto fra la chiusura di ieri e l'apertura di oggi più grande di
    `soglia` (in proporzione) dev'essere spiegato da un frazionamento in quel giorno; e ogni
    frazionamento deve vedersi nei prezzi (il rapporto fra le due chiusure vicino al rapporto del
    frazionamento, entro un fattore 1,5)."""
    p: list[dict] = []
    giorni = list(date_ny(df_giorno_raw.index))
    fraz = {}
    if azioni is not None and not azioni.empty:
        f = azioni[azioni["tipo"] == "frazionamento"]
        fraz = dict(zip(f["data"], f["rapporto"]))
    chiusure = df_giorno_raw["close"].to_numpy()
    aperture = df_giorno_raw["open"].to_numpy()
    for i in range(1, len(giorni)):
        salto = aperture[i] / chiusure[i - 1]
        d = giorni[i]
        if d in fraz:
            atteso = 1.0 / fraz[d]
            visto = chiusure[i] / chiusure[i - 1]
            if not (atteso / 1.5 <= visto <= atteso * 1.5):
                p.append(_problema("frazionamento non visto", d,
                                   f"rapporto {fraz[d]:g}: chiusure {visto:.3f} invece di circa {atteso:.3f}"))
        elif abs(salto - 1) > soglia:
            p.append(_problema("salto", d, f"apertura/chiusura di ieri = {salto:.3f} senza frazionamento"))
    visti = set(giorni)
    for d in fraz:
        if giorni and giorni[0] < d <= giorni[-1] and d not in visti:
            p.append(_problema("frazionamento non visto", d, "il giorno di stacco non ha barra"))
    return p


def rettifica(df_giorno_raw: pd.DataFrame, azioni: pd.DataFrame, dividendi: bool = True) -> pd.Series:
    """Il fattore che porta i prezzi NON rettificati a quelli rettificati, calcolato da noi.

    Metodo standard (all'indietro): per ogni stacco, tutte le barre PRIMA del giorno di stacco si
    moltiplicano per 1/rapporto (frazionamento) e per (1 - dividendo / chiusura del giorno prima)
    (dividendo). L'ultima barra ha fattore 1. Serve per confrontare la rettifica di Alpaca con una
    calcolata in modo indipendente (`controlla_rettifica`)."""
    giorni = date_ny(df_giorno_raw.index)
    fattore = np.ones(len(giorni))
    if azioni is None or azioni.empty:
        return pd.Series(fattore, index=df_giorno_raw.index)
    pos = {d: i for i, d in enumerate(giorni)}
    for _, a in azioni.iterrows():
        i = pos.get(a["data"])
        if i is None or i == 0:
            continue
        if a["tipo"] == "frazionamento":
            fattore[:i] *= 1.0 / a["rapporto"]
        elif a["tipo"] == "dividendo" and dividendi:
            fattore[:i] *= 1.0 - a["importo"] / df_giorno_raw["close"].iloc[i - 1]
    return pd.Series(fattore, index=df_giorno_raw.index)


def controlla_rettifica(raw: pd.DataFrame, rettificati: pd.DataFrame, azioni: pd.DataFrame,
                        tolleranza: float = 0.002, dividendi: bool = True) -> list[dict]:
    """Confronta la rettifica di Alpaca (`rettificati` = barre con adjustment "all", o "split" con
    `dividendi=False`) con la nostra (`rettifica`). Tutti e due i fattori si normalizzano sull'ultima
    barra; si segnalano i giorni in cui differiscono più di `tolleranza` (in proporzione), una riga
    per ogni tratto consecutivo di giorni sbagliati."""
    comuni = raw.index.intersection(rettificati.index)
    if len(comuni) == 0:
        return [_problema("rettifica", "-", "nessun giorno in comune")]
    raw, rettificati = raw.loc[comuni], rettificati.loc[comuni]
    nostro = rettifica(raw, azioni, dividendi=dividendi).to_numpy()
    loro = (rettificati["close"] / raw["close"]).to_numpy()
    loro = loro / loro[-1]
    nostro = nostro / nostro[-1]
    scarto = np.abs(loro / nostro - 1)
    p: list[dict] = []
    giorni = list(date_ny(comuni))
    i = 0
    while i < len(scarto):
        if scarto[i] > tolleranza:
            j = i
            while j + 1 < len(scarto) and scarto[j + 1] > tolleranza:
                j += 1
            p.append(_problema("rettifica", f"{giorni[i]} → {giorni[j]}",
                               f"{j - i + 1} giorni, differenza massima {scarto[i:j + 1].max():.4f}"))
            i = j + 1
        else:
            i += 1
    return p


def controlla_cadenza_dividendi(azioni: pd.DataFrame, fattore: float = 1.6) -> list[dict]:
    """Un dividendo che manca in TUTTE le fonti di Alpaca non si vede confrontando le due rettifiche.
    Per chi paga a cadenza regolare (lo SPY ogni trimestre) si vede dal buco: due dividendi distanti
    più di `fattore` volte la distanza tipica (la mediana) fanno pensare a uno mancante in mezzo."""
    if azioni is None or azioni.empty:
        return []
    d = sorted(azioni.loc[azioni["tipo"] == "dividendo", "data"])
    if len(d) < 4:
        return []
    distanze = [(b - a).days for a, b in zip(d, d[1:])]
    tipica = float(np.median(distanze))
    return [_problema("dividendo mancante?", f"{a} → {b}", f"{(b - a).days} giorni fra due dividendi, di solito {tipica:.0f}")
            for (a, b), g in zip(zip(d, d[1:]), distanze) if g > fattore * tipica]
