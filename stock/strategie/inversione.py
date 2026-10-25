"""L'inversione dopo l'apertura, a 5 passi (`stock/prove/P022_inversione_apertura.md`).

Le regole sono scritte per gli acquisti; le vendite sono lo specchio: si cambia segno ai prezzi (minimo -> -massimo) e si usa la
stessa ricerca. Ogni segnale alla barra i usa solo le barre fino a i compresa.
"""
from __future__ import annotations

import math

import numpy as np
import pandas as pd

from stock.simulatore.motore import Ordine, Stato

NY = "America/New_York"
QUOTA = 0.98
MINUTI_SEDUTA = 390
LATO = 2                     # barre per lato di un minimo (o massimo) di oscillazione
SEDUTE_LIVELLI = 5
DISTANZA_TOCCHI = 4          # barre da 15 minuti fra i due tocchi
SCARTO_TOCCHI = 0.001
SOTTO_ZONA = 0.0015
SPALLA_SINISTRA = 30         # minuti al massimo fra S1 e T
PRINCIPALE = dict(testa=(10, 40), ingresso=89, zone=True)       # 9:40-10:10, entro le 10:59
SENZA_ZONE = dict(testa=(10, 40), ingresso=89, zone=False)
ORARIO_LARGO = dict(testa=(5, 120), ingresso=149, zone=True)    # 9:35-11:30, entro le 11:59


def minimi_oscillazione(basso: np.ndarray) -> np.ndarray:
    """Indici j con basso[j] più basso (strettamente) delle LATO barre prima e non più alto delle LATO barre dopo."""
    n = len(basso)
    out = []
    for j in range(LATO, n - LATO):
        if all(basso[j] < basso[j - d] for d in range(1, LATO + 1)) and all(basso[j] <= basso[j + d] for d in range(1, LATO + 1)):
            out.append(j)
    return np.array(out, dtype=int)


def zone(basso15: np.ndarray) -> list[tuple[float, float]]:
    """Le zone di supporto: coppie di minimi di oscillazione a 15 minuti distanti almeno DISTANZA_TOCCHI barre e con prezzi
    diversi al massimo dello SCARTO_TOCCHI."""
    m = minimi_oscillazione(basso15)
    out = []
    for a in range(len(m)):
        for b in range(a + 1, len(m)):
            x, y = basso15[m[a]], basso15[m[b]]
            if m[b] - m[a] >= DISTANZA_TOCCHI and abs(x - y) <= SCARTO_TOCCHI * abs(x + y) / 2:
                out.append((min(x, y), max(x, y)))
    return out


def cerca(o, h, l, c, k, zone_giorno, regole) -> tuple[int, float, float] | None:
    """Il primo segnale d'acquisto del giorno: (barra del segnale, minimo di S2, obiettivo), oppure None.
    `k`: minuti dall'apertura di ogni barra. Prezzi già girati per le vendite."""
    n = len(l)
    t0, t1 = regole["testa"]
    sw = minimi_oscillazione(l)
    sw_set = set(sw.tolist())
    migliore = None
    minimo_prima = np.minimum.accumulate(np.r_[np.inf, l[:-1]])     # il minimo delle barre prima di j
    for t in sw:
        if not (t0 <= k[t] <= t1) or not l[t] < minimo_prima[t]:
            continue
        precedenti = [j for j in sw if j < t and l[j] > l[t] and k[t] - k[j] <= SPALLA_SINISTRA]
        if not precedenti:
            continue
        s1 = precedenti[-1]
        if s1 + 1 > t - 1:
            continue
        alto_h = h[s1 + 1:t].max()
        if regole["zone"]:
            ok = False
            for zb, zt in zone_giorno:
                if zb - SOTTO_ZONA * abs(l[t]) <= l[t] <= zt and (c[:t] > zt).any():
                    ok = True
                    break
            if not ok:
                continue
        obiettivo = h[:t + 1].max()
        rottura = None
        for b in range(t + 1, n):
            if l[b] < l[t]:
                break
            if c[b] > alto_h:
                rottura = b
                break
        if rottura is None:
            continue
        s2 = None
        for i in range(rottura + 1, n):
            if l[i] < l[t] or k[i] > regole["ingresso"]:
                break
            if migliore is not None and i >= migliore[0]:
                break
            j = i - LATO                      # un minimo si conosce LATO barre dopo
            if j > rottura and j in sw_set and l[j] > l[t]:
                s2 = j
            if s2 is None or i < s2 + LATO:
                continue
            if c[i] > o[i] and c[i] > h[i - 1] and c[i] < obiettivo:
                migliore = (i, l[s2], obiettivo)
                break
    return migliore


def prepara(barre: pd.DataFrame, cal: pd.DataFrame, giorni_esclusi: set, regole: dict = PRINCIPALE) -> dict:
    """Per ogni barra di segnale: direzione, stop e obiettivo (prezzi veri); la barra della chiusura di fine giornata."""
    t = barre.index.tz_convert(NY)
    giorni = np.array(t.date)
    n = len(barre)
    ap, al, ba, ch = (barre[col].to_numpy(float) for col in ("open", "high", "low", "close"))
    direzione = np.zeros(n)
    stop = np.full(n, np.nan)
    obiettivo = np.full(n, np.nan)
    giorno_di = np.full(n, -1)
    uscita = np.zeros(n, dtype=bool)
    tagli = np.r_[0, np.where(giorni[1:] != giorni[:-1])[0] + 1, n]
    # barre da 15 minuti di ogni seduta (minimo e massimo), in ordine
    quindici = []
    for a, b in zip(tagli[:-1], tagli[1:]):
        k = ((t[a:b] - cal.loc[giorni[a], "apertura"]).total_seconds() // 60).astype(int).to_numpy()
        gruppo = k // 15
        df = pd.DataFrame({"g": gruppo, "l": ba[a:b], "h": al[a:b]}).groupby("g").agg(l=("l", "min"), h=("h", "max"))
        quindici.append((df["l"].to_numpy(), df["h"].to_numpy()))
    for j, (a, b) in enumerate(zip(tagli[:-1], tagli[1:])):
        d = giorni[a]
        apertura, chiusura = cal.loc[d, "apertura"], cal.loc[d, "chiusura"]
        if j < SEDUTE_LIVELLI or d in giorni_esclusi or (chiusura - apertura) != pd.Timedelta(minutes=MINUTI_SEDUTA):
            continue
        k = ((t[a:b] - apertura).total_seconds() // 60).astype(int).to_numpy()
        if k[-1] != MINUTI_SEDUTA - 1 or (MINUTI_SEDUTA - 2) not in set(k.tolist()):
            continue
        b15 = np.concatenate([quindici[x][0] for x in range(j - SEDUTE_LIVELLI, j)])
        a15 = np.concatenate([quindici[x][1] for x in range(j - SEDUTE_LIVELLI, j)])
        o, h, l, c = ap[a:b], al[a:b], ba[a:b], ch[a:b]
        su = cerca(o, h, l, c, k, zone(b15), regole)
        giu = cerca(-o, -l, -h, -c, k, zone(-a15), regole)
        scelta = None
        if su and (not giu or su[0] < giu[0]):
            scelta = (1.0, su[0], su[1] - 0.01, su[2])
        elif giu and (not su or giu[0] < su[0]):
            scelta = (-1.0, giu[0], -giu[1] + 0.01, -giu[2])
        giorno_di[a:b] = j
        uscita[a + int(np.where(k == MINUTI_SEDUTA - 2)[0][0])] = True
        if scelta:
            segno, i, liv_stop, liv_ob = scelta
            direzione[a + i], stop[a + i], obiettivo[a + i] = segno, liv_stop, liv_ob
    return {"direzione": direzione, "stop": stop, "obiettivo": obiettivo, "giorno": giorno_di, "uscita": uscita}


def strategia(seg: dict):
    direzione, stop, obiettivo, giorno_di, uscita = (seg[x] for x in ("direzione", "stop", "obiettivo", "giorno", "uscita"))
    aperta = {}                                   # giorno -> (segno, stop, obiettivo)

    def livelli(segno, liv_stop, liv_ob, q):
        ordini = [Ordine(-segno * q, "stop", liv_stop, solo_riduce=True, etichetta="stop", dopo_ingresso=True)]
        if liv_ob > 0:
            ordini.append(Ordine(-segno * q, "limite", liv_ob, solo_riduce=True, etichetta="obiettivo", dopo_ingresso=True))
        return ordini

    def decidi(storia: pd.DataFrame, stato: Stato) -> list:
        i = len(storia) - 1
        g = giorno_di[i]
        if uscita[i]:
            aperta.pop(g, None)
            return [Ordine(-stato.azioni, "mercato", etichetta="chiusura")] if stato.azioni else []
        if direzione[i] != 0 and stato.azioni == 0 and g not in aperta:
            c = float(storia["close"].iat[-1])
            q = math.floor(QUOTA * stato.valore(c) / c)
            if q <= 0:
                return []
            aperta[g] = (direzione[i], stop[i], obiettivo[i])
            return [Ordine(direzione[i] * q, "mercato", etichetta="ingresso")] + livelli(direzione[i], stop[i], obiettivo[i], q)
        if stato.azioni and g in aperta:
            segno, liv_stop, liv_ob = aperta[g]
            return livelli(segno, liv_stop, liv_ob, abs(stato.azioni))
        return []
    return decidi
