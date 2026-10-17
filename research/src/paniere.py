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

Dal 14 ottobre 2026 (seconda edizione, PROTOCOLLO_2 correzione 5) le funzioni
della variante ricevono da ``gruppo.py`` le righe giornaliere del paniere
(``ctx.paniere_chiuse_entro(ts)``: ``GiornoPaniere`` con ``ts``, ``close_ts``,
``chiusure`` = {simbolo: chiusura} e ``sotto_liquidita``), e le tre funzioni
«dell'ultimo giorno» qui sotto (``rendimenti_ultimo_giorno``,
``classifica_ultimo_giorno``, ``giorno_forte_ultimo``) danno, per l'ultima riga
vista, lo stesso risultato delle funzioni sulle matrici intere: sono fatte per
essere chiamate alla chiusura di ogni barra, con un costo che non cresce con la
storia.
"""
from __future__ import annotations

from typing import Collection, Dict, Mapping, Sequence, Tuple

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


#: la moneta di riferimento, fuori dalla classifica del paniere (PROTOCOLLO_2, sezione 4)
MONETA_RIFERIMENTO = "BTCUSDT"


def rendimenti_ultimo_giorno(righe: Sequence, n_giorni: int, storia_minima: int = 0,
                             escludi: Collection[str] = (MONETA_RIFERIMENTO,)) -> Dict[str, float]:
    """{simbolo: close[t] / close[t - n] - 1} per l'ultima riga ``t`` di ``righe`` (le righe del paniere di ``gruppo.py``).

    Entrano le monete con la chiusura in ``t`` e in ``t - n_giorni`` (righe del
    calendario: un giorno senza candela e' un buco), non in ``escludi`` e non in
    ``sotto_liquidita`` di ``t``; con ``storia_minima`` > 0 anche con una
    chiusura nella riga ``t - storia_minima`` (presente almeno da tanti giorni).
    Vuoto se le righe non bastano. Stesso numero di ``rendimento_n_giorni`` sulla
    matrice intera, moneta per moneta, con l'aritmetica in virgola mobile nello
    stesso ordine.
    """
    if n_giorni < 1:
        raise ValueError("n_giorni deve essere almeno 1")
    if storia_minima < 0:
        raise ValueError("storia_minima non puo' essere negativa")
    n_righe = len(righe)
    if n_righe <= n_giorni or n_righe <= storia_minima:
        return {}
    oggi = righe[-1]
    prima = righe[-1 - n_giorni]
    antica = righe[-1 - storia_minima] if storia_minima > 0 else None
    vietate = set(escludi) | set(oggi.sotto_liquidita)
    out: Dict[str, float] = {}
    for simbolo, chiusura in oggi.chiusure.items():
        if simbolo in vietate:
            continue
        base = prima.chiusure.get(simbolo)
        if base is None:
            continue
        if antica is not None and simbolo not in antica.chiusure:
            continue
        out[simbolo] = float(chiusura) / float(base) - 1.0
    return out


def classifica_ultimo_giorno(righe: Sequence, n_giorni: int, storia_minima: int = 0,
                             escludi: Collection[str] = (MONETA_RIFERIMENTO,)) -> Tuple[Dict[str, int], int]:
    """({simbolo: rango}, n_monete) dell'ultima riga: rango 1 = rendimento a ``n_giorni`` piu' alto, parita' alfabetica.

    Le monete sono quelle di ``rendimenti_ultimo_giorno``; la regola del rango e'
    quella di ``classifica`` (ordine stabile per rendimento decrescente, poi
    simbolo). ``n_monete`` e' il numero delle monete classificate.
    """
    rendimenti = rendimenti_ultimo_giorno(righe, n_giorni, storia_minima, escludi)
    ordine = sorted(rendimenti, key=lambda s: (-rendimenti[s], s))
    return {s: r for r, s in enumerate(ordine, start=1)}, len(ordine)


def giorno_forte_ultimo(chiusure: Sequence[float], k: float, n: int = 60, minimo: int = 40) -> int:
    """+1, -1 o 0 per l'ultimo giorno di una sequenza di chiusure giornaliere (es. BTCUSDT), come ``giorni_forti``.

    Il rendimento dell'ultimo giorno si confronta con ``k`` volte la deviazione
    standard dei ``n`` rendimenti PRECEDENTI (``deviazione_mobile``, almeno
    ``minimo`` finiti); con meno di ``n + 2`` chiusure vale 0. Stesso valore di
    ``giorni_forti`` sulla serie intera, all'ultimo giorno.
    """
    valori = np.asarray([float(c) for c in list(chiusure)[-(n + 2):]], dtype=float)
    if valori.size < n + 2:
        return 0
    rendimenti = valori[1:] / valori[:-1] - 1.0
    return int(giorni_forti(rendimenti, k, n, minimo)[-1])

