"""La serie di paniere della seconda edizione (research/PROTOCOLLO_2.md, sezione 5, idea B, e sezione 10, punto 3).

Le idee trasversali (le monete piu' forti contro le piu' deboli) hanno bisogno, per
ogni moneta e per ogni giorno ``t``, di sapere dove sta la moneta nella classifica
del paniere per rendimento degli ultimi ``n`` giorni. Il motore di ricerca esegue
una moneta alla volta: la classifica e' quindi una SERIE ESTERNA per moneta,
calcolata una volta dalle chiusure giornaliere di tutte le monete e letta dalla
strategia come ``btc_close`` nelle campagne della prima edizione.

Causalita' (sezione 10, punto 3): ogni valore al giorno ``t`` usa SOLO chiusure di
giorni ``<= t``. Il rendimento a ``n`` giorni al giorno ``t`` e' ``close[t] /
close[t - n] - 1`` sulla stessa moneta, con i giorni contati sul calendario UTC (un
giorno senza candela e' un buco: il rendimento e' NaN se manca una delle due
chiusure). La classifica del giorno ``t`` ordina le monete con rendimento finito:
rango 1 = la piu' forte; a parita' di rendimento vince la moneta che viene prima
nell'ordine alfabetico (regola fissa, senza caso). ``n_monete[t]`` dice quante
monete hanno un rango quel giorno.

Il «giorno forte» di Bitcoin dell'idea C (sezione 5): ``rendimenti_giornalieri``
e ``deviazione_mobile`` (deviazione standard dei rendimenti dei ``n`` giorni
PRECEDENTI a ``t``, esclusa ``t``) danno gli ingredienti; ``giorni_forti`` li mette
insieme: ``t`` e' forte se ``|r[t]| > k * dev[t]`` (``dev[t]`` dai giorni ``t - n ..
t - 1``, almeno ``minimo`` finiti).

Tutto vive nel calendario dei giorni UTC: ``ts`` e' l'apertura del giorno in ms.
"""
from __future__ import annotations

from typing import Dict, Mapping, Sequence, Tuple

import numpy as np

from research.src.motore import Candela

GIORNO_MS = 86_400_000


def _giorno(ts: int) -> int:
    if ts % GIORNO_MS:
        raise ValueError(f"candela non allineata al giorno UTC: ts {ts}")
    return ts // GIORNO_MS


def allinea_giorni(candele: Mapping[str, Sequence[Candela]]) -> Tuple[np.ndarray, Tuple[str, ...], np.ndarray]:
    """(giorni, simboli, chiusure): il calendario comune e la matrice delle chiusure.

    ``giorni`` sono le aperture (ms) di TUTTI i giorni UTC dal primo all'ultimo
    giorno presente in una qualunque moneta, senza buchi; ``simboli`` in ordine
    alfabetico; ``chiusure[i, j]`` e' la chiusura della moneta ``j`` nel giorno
    ``i``, NaN se quel giorno la moneta non ha la candela. Una candela che non
    apre a mezzanotte UTC o due candele dello stesso giorno sono un errore.
    """
    if not candele:
        raise ValueError("nessuna moneta")
    simboli = tuple(sorted(candele))
    primo, ultimo = None, None
    for s in simboli:
        for c in candele[s]:
            g = _giorno(c.ts)
            primo = g if primo is None else min(primo, g)
            ultimo = g if ultimo is None else max(ultimo, g)
    if primo is None:
        raise ValueError("nessuna candela")
    n = ultimo - primo + 1
    chiusure = np.full((n, len(simboli)), np.nan)
    for j, s in enumerate(simboli):
        visti = set()
        for c in candele[s]:
            g = _giorno(c.ts) - primo
            if g in visti:
                raise ValueError(f"{s}: due candele nello stesso giorno (ts {c.ts})")
            visti.add(g)
            chiusure[g, j] = float(c.close)
    giorni = (np.arange(n, dtype=np.int64) + primo) * GIORNO_MS
    return giorni, simboli, chiusure


def rendimento_n_giorni(chiusure: np.ndarray, n: int) -> np.ndarray:
    """``close[t] / close[t - n] - 1`` per ogni moneta; NaN dove manca una delle due o nei primi ``n`` giorni."""
    if n < 1:
        raise ValueError("n deve essere almeno 1")
    out = np.full_like(chiusure, np.nan)
    if chiusure.shape[0] > n:
        out[n:] = chiusure[n:] / chiusure[:-n] - 1.0
    return out


def classifica(rendimenti: np.ndarray, simboli: Sequence[str]) -> Tuple[np.ndarray, np.ndarray]:
    """(rango, n_monete): per ogni giorno il rango di ogni moneta fra quelle con rendimento finito.

    Rango 1 = rendimento piu' alto; a parita' vince il simbolo alfabeticamente
    minore; NaN per le monete senza rendimento quel giorno. ``n_monete[t]`` e' il
    numero di monete classificate il giorno ``t``.
    """
    n_giorni, n_simboli = rendimenti.shape
    if len(simboli) != n_simboli:
        raise ValueError("simboli e colonne non corrispondono")
    ordine_alfabetico = np.argsort(np.array(simboli, dtype=object), kind="stable")
    posizione_alfabetica = np.empty(n_simboli, dtype=np.int64)
    posizione_alfabetica[ordine_alfabetico] = np.arange(n_simboli)
    rango = np.full((n_giorni, n_simboli), np.nan)
    n_monete = np.zeros(n_giorni, dtype=np.int64)
    for t in range(n_giorni):
        riga = rendimenti[t]
        validi = np.where(np.isfinite(riga))[0]
        n_monete[t] = len(validi)
        if not len(validi):
            continue
        # dal rendimento piu' alto; parita' rotta dall'ordine alfabetico (stabile)
        chiavi = sorted(validi, key=lambda j: (-riga[j], posizione_alfabetica[j]))
        for r, j in enumerate(chiavi, start=1):
            rango[t, j] = r
    return rango, n_monete


def rendimenti_giornalieri(chiusure: np.ndarray) -> np.ndarray:
    """``close[t] / close[t - 1] - 1``; NaN al primo giorno e dove manca una chiusura."""
    return rendimento_n_giorni(chiusure, 1)


def deviazione_mobile(serie: np.ndarray, n: int, minimo: int) -> np.ndarray:
    """Deviazione standard (ddof 1) dei ``n`` valori PRECEDENTI a ``t`` (da ``t - n`` a ``t - 1``, ``t`` escluso),
    NaN se i valori finiti in quella finestra sono meno di ``minimo`` (o ``t < n``)."""
    if n < 2 or minimo < 2 or minimo > n:
        raise ValueError("servono n >= 2 e 2 <= minimo <= n")
    out = np.full(len(serie), np.nan)
    for t in range(n, len(serie)):
        finestra = serie[t - n:t]
        finiti = finestra[np.isfinite(finestra)]
        if len(finiti) >= minimo:
            out[t] = float(np.std(finiti, ddof=1))
    return out


def giorni_forti(rendimenti: np.ndarray, k: float, n: int = 60, minimo: int = 40) -> np.ndarray:
    """+1 nei giorni con ``r[t] > k * dev[t]``, -1 con ``r[t] < -k * dev[t]``, 0 altrimenti (anche senza dev)."""
    if k <= 0:
        raise ValueError("k deve essere positivo")
    dev = deviazione_mobile(rendimenti, n, minimo)
    out = np.zeros(len(rendimenti), dtype=np.int8)
    ok = np.isfinite(rendimenti) & np.isfinite(dev) & (dev > 0)
    out[ok & (rendimenti > k * dev)] = 1
    out[ok & (rendimenti < -k * dev)] = -1
    return out


def serie_paniere(candele: Mapping[str, Sequence[Candela]], n_giorni: int, storia_minima: int = 0) -> Dict[str, object]:
    """La serie esterna delle idee trasversali, da passare alla strategia di ogni moneta.

    ``candele``: {simbolo: candele giornaliere (last)} di tutto il paniere;
    ``n_giorni``: la finestra del rendimento; ``storia_minima``: una moneta entra
    nella classifica di un giorno solo se ha almeno tanti giorni di candele fino a
    quel giorno (0 = nessun minimo oltre ai ``n_giorni`` del rendimento).
    Ritorna ``giorni`` (ms), ``simboli``, ``rendimento`` e ``rango`` ({simbolo:
    array per giorno}), ``n_monete`` (array per giorno) e ``indice`` ({ts: i}),
    cosi' una strategia legge ``rango[simbolo][indice[ts]]`` alla chiusura del
    giorno ``ts`` usando solo chiusure fino a quel giorno.
    """
    giorni, simboli, chiusure = allinea_giorni(candele)
    rend = rendimento_n_giorni(chiusure, n_giorni)
    if storia_minima > 0:
        presenti = np.isfinite(chiusure).cumsum(axis=0)
        rend[presenti < storia_minima] = np.nan
    rango, n_monete = classifica(rend, simboli)
    return {
        "giorni": giorni, "simboli": simboli, "n_giorni": n_giorni,
        "rendimento": {s: rend[:, j] for j, s in enumerate(simboli)},
        "rango": {s: rango[:, j] for j, s in enumerate(simboli)},
        "n_monete": n_monete,
        "indice": {int(ts): i for i, ts in enumerate(giorni)},
    }
