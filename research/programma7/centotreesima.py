"""Prova 165 (CENTOTREESIMA.md + «Chiusura della verifica» + VERIFICA_CENTOTREESIMA.md punti 3-5, 8-15, 17-19): vendere le monete che
somigliano a quelle chiuse. Modello a due numeri (volume medio dei 30 giorni e suo rapporto con i 60 giorni prima, in classifica fra i
contratti vivi), regressione logistica L2 rifatta a ogni decisione, N monete con punteggio piu' alto in short e Bitcoin long per lo
stesso valore. Solo le varianti A (N=5, primo del mese) e B (N=10, lunedi'). Seme 2026 (solo per la selezione a caso).

Dati: solo quelli scaricati da centotreesima_dati.py (candele giornaliere) e il funding del pannello (`seconda.pannello`, solo fino al
31 ottobre 2026). Capitale fisso di 1.000 USDT, senza comporre.

Uso: python3 -m research.programma7.centotreesima --fase modello    (punteggi e controllo di coerenza, nessun rendimento)
     python3 -m research.programma7.centotreesima --fase prova      (rendimenti, esame, controlli, registro)
"""
from __future__ import annotations

import argparse
import json
import math
import traceback
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import rankdata
from sklearn.exceptions import ConvergenceWarning
from sklearn.linear_model import LogisticRegression

from research.programma5.strumenti import motore5 as m5
from research.programma6 import asticella as ast
from research.programma6 import seconda as sc
from research.programma6 import terza as te
from research.programma7 import centotreesima_dati as dat
from research.src import prove

QUI = Path(__file__).parent
RIS = QUI / "risultati_centotreesima"
ID = "centotreesima"
DAY0 = sc.giorno(2021, 12, 1)
DAYN = sc.giorno(2026, 11, 1)                    # apertura del 1 novembre 2026: le posizioni aperte si chiudono li'
NG = DAYN - DAY0 + 1
CAPITALE = 1000.0
TAKER = 0.0005
SCARTO_ALTRE_DOPPIO = 0.0004
USCITA_PROT, SCARTO_PROT = 1.30, 1.01
GIORNI_ETICHETTA, MIN_CHIUSI = 45, 10
ULTIMO_ANNUNCIO_NOTO = sc.giorno(2026, 10, 1) - DAY0      # l'ultimo annuncio del file degli eventi e' del 1 ottobre 2026 (prudente: niente dopo)
SEME = 2026
ESTRAZIONI = 1000
VARIANTI = {"A": {"N": 5, "decisione": "primo del mese", "inizio": sc.giorno(2024, 6, 1)},
            "B": {"N": 10, "decisione": "lunedi", "inizio": sc.giorno(2024, 5, 13)}}


# ---------------------------------------------------------------------------------------------------------------- dati
def carica() -> dict:
    cache = dat.DATI.parent / "array_d1.npz"
    sim = sorted(p.name for p in dat.DATI.iterdir() if p.is_dir())
    if cache.exists():
        z = np.load(cache, allow_pickle=True)
        if list(z["sim"]) == sim:
            return {"sim": sim, "O": z["O"], "H": z["H"], "C": z["C"], "Q": z["Q"]}
    ns = len(sim)
    O = np.full((NG, ns), np.nan); H = O.copy(); C = O.copy(); Q = O.copy()
    for j, s in enumerate(sim):
        for f in sorted((dat.DATI / s).glob("*.zip")):
            d = dat.leggi_k(f)
            k = (d["t"].to_numpy() // 86_400_000 - DAY0).astype(int)
            ok = (k >= 0) & (k < NG)
            O[k[ok], j] = d["open"].to_numpy(float)[ok]; H[k[ok], j] = d["high"].to_numpy(float)[ok]
            C[k[ok], j] = d["close"].to_numpy(float)[ok]; Q[k[ok], j] = d["qvolume"].to_numpy(float)[ok]
    np.savez(cache, sim=np.array(sim), O=O, H=H, C=C, Q=Q)
    return {"sim": sim, "O": O, "H": H, "C": C, "Q": Q}


class Dati:
    def __init__(self):
        d = carica()
        self.sim = d["sim"]
        self.idx = {s: i for i, s in enumerate(self.sim)}
        self.ns = len(self.sim)
        self.O, self.H, self.C, self.Q = d["O"], d["H"], d["C"], d["Q"]
        self.O[NG - 1] = self.C[NG - 2]                       # apertura del 1 novembre = chiusura del 31 ottobre (manca il file di novembre)
        ev = pd.read_csv(QUI / "revisione_107" / "eventi_finale.csv")
        self.ev = ev
        self.HE = np.full(self.ns, np.inf); self.HU = np.full(self.ns, np.inf)
        self.ev_fuori = []
        for r in ev.itertuples():
            if r.simbolo in self.idx:
                self.HE[self.idx[r.simbolo]] = r.h_e; self.HU[self.idx[r.simbolo]] = r.h_u
            else:
                self.ev_fuori.append(r.simbolo)
        # contratti con volume positivo oltre 7 giorni dopo la chiusura (prima di togliere i dati dopo la chiusura)
        giorni_ore = (np.arange(NG) + DAY0) * 24
        self.dopo_chiusura = []
        for j in range(self.ns):
            if np.isfinite(self.HU[j]):
                m = (giorni_ore > self.HU[j] + 7 * 24) & (np.nan_to_num(self.Q[:, j]) > 0)
                if m.any():
                    self.dopo_chiusura.append((self.sim[j], int(m.sum()), sc.data(int(np.flatnonzero(m)[-1]) + DAY0)))
        # dopo la chiusura nessun dato (anche se l'archivio continua)
        for j in range(self.ns):
            if np.isfinite(self.HU[j]):
                cut = int(self.HU[j] // 24) - DAY0
                for a in (self.O, self.H, self.C, self.Q):
                    a[max(cut, 0):, j] = np.nan
        # funding dal pannello (solo fino al 31 ottobre; mai la stima dei 90 giorni)
        pan = sc.pannello()
        pidx = {s: i for i, s in enumerate(pan["simboli"])}
        self.F = np.zeros((NG, self.ns))
        self.senza_funding = []
        for j, s in enumerate(self.sim):
            if s not in pidx:
                self.senza_funding.append(s)
                continue
            r0 = DAY0 - pan["t0"]
            f = pan["funding"][r0:r0 + NG, pidx[s]]
            self.F[:len(f), j] = np.nan_to_num(f)
        self.F[NG - 1:] = 0.0                                  # il 1 novembre non c'e': nessun funding dopo il 31 ottobre
        self.btc, self.eth = self.idx["BTCUSDT"], self.idx["ETHUSDT"]
        self.rate = np.array([TAKER + m5.scarto(s) for s in self.sim])
        self.rate_doppio = np.array([TAKER + (SCARTO_ALTRE_DOPPIO if m5.scarto(s) == m5.SCARTO_ALTRE else m5.scarto(s)) for s in self.sim])
        self.rate_limite = np.array([0.0002 + m5.scarto(s) for s in self.sim])
        self.esclusi_dopo_chiusura = np.zeros(self.ns, bool)
        for s, _, _ in self.dopo_chiusura:
            self.esclusi_dopo_chiusura[self.idx[s]] = True
        self.prepara_numeri()

    def prepara_numeri(self):
        """I due numeri (in classifica) di ogni contratto vivo a ogni giorno t, con i soli giorni t-90..t-1."""
        Q = self.Q
        ok = np.isfinite(Q) & np.isfinite(self.C) & np.isfinite(self.O)
        cs = np.vstack([np.zeros((1, self.ns)), np.cumsum(np.where(ok, Q, 0.0), axis=0)])
        cn = np.vstack([np.zeros((1, self.ns), int), np.cumsum(ok, axis=0)])
        self.X1 = np.full((NG, self.ns), np.nan); self.X2 = np.full((NG, self.ns), np.nan)
        self.vivo = np.zeros((NG, self.ns), bool)                # eleggibile al giorno t (senza il filtro delle classifiche pari)
        ore_t = (np.arange(NG) + DAY0) * 24
        for t in range(90, NG):
            piene = (cn[t] - cn[t - 90]) == 90
            m30 = (cs[t] - cs[t - 30]) / 30.0
            m60 = (cs[t - 30] - cs[t - 90]) / 60.0
            el = piene & (m60 > 0) & (m30 > 0) & (self.HE >= ore_t[t])
            el[self.btc] = el[self.eth] = False
            self.vivo[t] = el
            if el.sum() < 2:
                continue
            n = int(el.sum())
            self.X1[t, el] = (rankdata(np.log(m30[el])) - 1) / (n - 1)
            self.X2[t, el] = (rankdata(m30[el] / m60[el]) - 1) / (n - 1)
        # righe di allenamento: tutte le coppie (t, c) vive, con l'etichetta (annunciato entro 45 giorni da t)
        tt, cc = np.nonzero(self.vivo)
        self.rt, self.rc = tt, cc
        self.rx = np.column_stack([self.X1[tt, cc], self.X2[tt, cc]])
        he = self.HE[cc]
        self.ry = ((he >= (tt + DAY0) * 24) & (he < (tt + DAY0 + GIORNI_ETICHETTA) * 24)).astype(int)


# ---------------------------------------------------------------------------------------------------------------- modello
def modello_a(d: Dati, D: int, escludi=None) -> dict:
    """Il modello alla decisione D (indice di giorno): righe con t + 45 <= D - 1. Restituisce coefficienti, punteggi degli ammissibili."""
    m = d.rt <= D - 1 - GIORNI_ETICHETTA
    if escludi is not None:
        m &= ~escludi[d.rc]
    y = d.ry[m]
    pos_c = np.unique(d.rc[m][y == 1])
    out = {"D": D, "righe": int(m.sum()), "positivi": int(y.sum()), "chiusi_validi": int(len(pos_c)), "ok": False}
    if len(pos_c) < MIN_CHIUSI or y.min() == y.max():
        out["motivo"] = "meno di 10 contratti chiusi con righe valide"
        return out
    mod = LogisticRegression(penalty="l2", C=1.0, solver="lbfgs", max_iter=1000)
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        mod.fit(d.rx[m], y)
    if any(issubclass(x.category, ConvergenceWarning) for x in w):
        out["motivo"] = "il modello non converge"
        return out
    el = d.vivo[D]
    if escludi is not None:
        el = el & ~escludi
    cand = np.flatnonzero(el)
    x = np.column_stack([d.X1[D, cand], d.X2[D, cand]])
    p = mod.predict_proba(x)[:, 1]
    out.update(ok=True, coef=[float(c) for c in mod.coef_[0]], intercetta=float(mod.intercept_[0]), cand=cand, punteggio=p)
    return out


def date_decisione(v: str) -> list:
    inizio = VARIANTI[v]["inizio"]
    ultimo = DAYN - 1
    out = []
    if v == "A":
        a, m = 2024, 6
        while sc.giorno(a, m, 1) <= ultimo:
            out.append(sc.giorno(a, m, 1) - DAY0)
            a, m = (a + 1, 1) if m == 12 else (a, m + 1)
    else:
        x = inizio
        while x <= ultimo:
            out.append(x - DAY0)
            x += 7
    return out


def prime_n(mo: dict, N: int):
    o = np.lexsort((mo["cand"], -mo["punteggio"]))
    return mo["cand"][o[:N]]


def fase_modello(d: Dati, log=print) -> dict:
    """Nessun rendimento: date di partenza, coefficienti e segni, precisione descrittiva."""
    RIS.mkdir(exist_ok=True)
    out = {"universo_simboli": d.ns, "eventi_nel_file": int(len(d.ev)), "eventi_senza_dati_nel_nostro_archivio": d.ev_fuori,
           "senza_funding_nel_pannello": len(d.senza_funding)}
    ev = d.ev.copy()
    out["annunci_per_anno"] = ev.groupby(ev["data"].str[:4]).size().to_dict()
    prima = (ev["h_e"] < (sc.giorno(2024, 5, 7)) * 24).sum()
    out["annunci_prima_del_7_maggio_2024"] = int(prima)
    out["contratti_con_volume_oltre_7_giorni_dopo_la_chiusura"] = [{"simbolo": s, "giorni_con_volume": n, "ultimo_giorno": u} for s, n, u in d.dopo_chiusura]
    base = {}
    for v in VARIANTI:
        N = VARIANTI[v]["N"]
        righe, segni_prec, cambi = [], None, 0
        sel_tot = {"n": 0, "chiusi45": 0, "chiusi90": 0, "n90": 0, "base45": 0, "base90": 0, "elig45": 0, "elig90": 0}
        top5 = {"n": 0, "chiusi45": 0, "annunciati45_tot": 0}
        for D in date_decisione(v):
            mo = modello_a(d, D)
            r = {"data": sc.data(D + DAY0), "righe": mo["righe"], "positivi": mo["positivi"], "chiusi_validi": mo["chiusi_validi"], "ok": mo["ok"]}
            if mo["ok"]:
                segni = tuple(np.sign(mo["coef"]).astype(int))
                if segni_prec is not None and segni != segni_prec:
                    cambi += 1
                segni_prec = segni
                r.update(coef_volume=mo["coef"][0], coef_calo=mo["coef"][1], intercetta=mo["intercetta"], candidati=int(len(mo["cand"])))
                sel = prime_n(mo, N)
                he = d.HE
                a0, a45, a90 = (D + DAY0) * 24, (D + DAY0 + 45) * 24, (D + DAY0 + 90) * 24
                if D + 45 <= ULTIMO_ANNUNCIO_NOTO:
                    sel_tot["n"] += len(sel); sel_tot["chiusi45"] += int(((he[sel] >= a0) & (he[sel] < a45)).sum())
                    sel_tot["elig45"] += len(mo["cand"]); sel_tot["base45"] += int(((he[mo["cand"]] >= a0) & (he[mo["cand"]] < a45)).sum())
                    k5 = max(1, int(math.ceil(0.05 * len(mo["cand"]))))
                    t5 = mo["cand"][np.lexsort((mo["cand"], -mo["punteggio"]))[:k5]]
                    top5["n"] += k5; top5["chiusi45"] += int(((he[t5] >= a0) & (he[t5] < a45)).sum())
                    top5["annunciati45_tot"] += int(((he[mo["cand"]] >= a0) & (he[mo["cand"]] < a45)).sum())
                if D + 90 <= ULTIMO_ANNUNCIO_NOTO:
                    sel_tot["n90"] += len(sel); sel_tot["chiusi90"] += int(((he[sel] >= a0) & (he[sel] < a90)).sum())
                    sel_tot["elig90"] += len(mo["cand"]); sel_tot["base90"] += int(((he[mo["cand"]] >= a0) & (he[mo["cand"]] < a90)).sum())
            righe.append(r)
        okr = [r for r in righe if r["ok"]]
        base[v] = {"decisioni": len(righe), "decisioni_con_modello": len(okr), "prima_decisione": righe[0]["data"],
                   "chiusi_validi_alla_prima": righe[0]["chiusi_validi"], "ultimo_modello_coef_volume": okr[-1]["coef_volume"] if okr else None,
                   "ultimo_modello_coef_calo": okr[-1]["coef_calo"] if okr else None,
                   "decisioni_con_coef_volume_negativo": int(sum(r["coef_volume"] < 0 for r in okr)),
                   "decisioni_con_coef_calo_negativo": int(sum(r["coef_calo"] < 0 for r in okr)),
                   "cambi_di_segno_fra_decisioni": cambi,
                   "precisione_prime_N_45_giorni": sel_tot["chiusi45"] / sel_tot["n"] if sel_tot["n"] else None,
                   "frequenza_di_base_45_giorni": sel_tot["base45"] / sel_tot["elig45"] if sel_tot["elig45"] else None,
                   "precisione_prime_N_90_giorni": sel_tot["chiusi90"] / sel_tot["n90"] if sel_tot["n90"] else None,
                   "frequenza_di_base_90_giorni": sel_tot["base90"] / sel_tot["elig90"] if sel_tot["elig90"] else None,
                   "primo_5pct_precisione_45": top5["chiusi45"] / top5["n"] if top5["n"] else None,
                   "primo_5pct_quota_delle_chiusure_45": top5["chiusi45"] / top5["annunciati45_tot"] if top5["annunciati45_tot"] else None,
                   "primo_5pct_monete_totali": top5["n"], "conteggi_selezione": sel_tot}
        pd.DataFrame(righe).to_csv(RIS / f"modello_{v}.csv", index=False)
    out["modello"] = base
    (RIS / "modello.json").write_text(json.dumps(out, indent=1, ensure_ascii=False, default=float))
    log(json.dumps({v: {k: base[v][k] for k in ("prima_decisione", "chiusi_validi_alla_prima", "decisioni_con_modello", "ultimo_modello_coef_volume",
                                                 "ultimo_modello_coef_calo", "cambi_di_segno_fra_decisioni")} for v in base}))
    return out


# ---------------------------------------------------------------------------------------------------------------- motore
class Costi:
    def __init__(self, d: Dati, rate):
        self.rate = rate


def periodo_moneta(d: Dati, c: int, D: int, E: int, Pe: float, V: float, rate: np.ndarray, cache: dict) -> dict:
    """Una moneta in short dall'apertura del giorno D (indice) fino alla decisione dopo E (o all'uscita prima), con la sua parte di
    Bitcoin long. Entrata all'apertura D; prezzo di entrata della protezione Pe."""
    chiave = (c, D, E, Pe, V, id(rate))
    if chiave in cache:
        return cache[chiave]
    b = d.btc
    O, H, C, F = d.O, d.H, d.C, d.F
    q = V / O[D, c]
    qb = V / O[D, b]
    he, hu = d.HE[c], d.HU[c]
    x_ann = math.inf
    annunciata = bool((D + DAY0) * 24 <= he < (E + DAY0) * 24)
    if annunciata:
        x_ann = int(hu // 24) - 1 - DAY0
    fine = min(E, x_ann)                                      # ultima apertura di tenuta (uscita a quell'apertura)
    tipo, uscita_prezzo, dend = "", None, None
    if fine <= D:
        tipo, dend = "ann_subito", D - 1
        pnl = np.zeros(0)
        res = {"pnl": pnl, "fund": np.zeros(0), "dend": D - 1, "tipo": tipo, "viva": False, "q": q, "Pe": Pe, "costo_uscita": 0.0, "costo_uscita_giorno": D,
               "annunciata": annunciata, "giorno_ann": int(he // 24) - DAY0 if annunciata else None, "qb": qb, "aperta": True}
        res["costo_uscita"] = q * O[D, c] * rate[c] + qb * O[D, b] * rate[b]
        cache[chiave] = res
        return res
    giorni = np.arange(D, fine)                                # giorni di tenuta intera D..fine-1
    onext = O[giorni + 1, c]
    # prezzo mancante (non per annuncio): prima apertura successiva non valida
    mancanti = np.flatnonzero(~np.isfinite(onext))
    dm = int(giorni[mancanti[0]]) if len(mancanti) else None
    # protezione: massimo giornaliero sopra 1,30 x Pe
    soglia = USCITA_PROT * Pe
    sopra = np.flatnonzero(H[giorni, c] > soglia)
    dp = int(giorni[sopra[0]]) if len(sopra) else None
    cand = [x for x in (dp, dm) if x is not None]
    pex = None
    if cand:
        dend = min(cand)
        if dp is not None and dend == dp:
            tipo, pex = "prot", soglia * SCARTO_PROT
        else:
            tipo = "manca"
            pex = C[dend, c] if np.isfinite(C[dend, c]) else O[dend, c]
        n = dend - D + 1
        g = np.arange(D, dend + 1)
        o0 = O[g, c]
        o1 = np.empty(n)
        o1[:-1] = O[g[:-1] + 1, c]
        o1[-1] = pex
        pnl_s = -q * (o1 - o0)
        ex_day_btc = dend + 1
    else:
        dend = fine - 1
        g = giorni
        o0 = O[g, c]
        o1 = onext
        pnl_s = -q * (o1 - o0)
        ex_day_btc = fine
        if fine < E:
            tipo = "ann"
    fund_s = F[g, c] * q * o0
    ob0, ob1 = O[g, b], O[g + 1, b]
    pnl_b = qb * (ob1 - ob0)
    fund_b = -F[g, b] * qb * ob0
    viva = tipo == ""
    costo_u, giorno_u = 0.0, None
    if not viva:
        pu = pex if tipo in ("prot", "manca") else O[fine, c]
        costo_u = q * pu * rate[c] + qb * O[min(ex_day_btc, NG - 1), b] * rate[b]
        giorno_u = fine if tipo == "ann" else dend + 1
    res = {"pnl": pnl_s + pnl_b, "fund": fund_s + fund_b, "dend": int(dend), "tipo": tipo, "viva": viva, "q": q, "Pe": Pe, "qb": qb,
           "costo_uscita": costo_u, "costo_uscita_giorno": giorno_u, "annunciata": annunciata,
           "giorno_ann": int(he // 24) - DAY0 if annunciata else None, "aperta": True, "pnl_s": pnl_s, "pnl_b": pnl_b}
    cache[chiave] = res
    return res


def simula(d: Dati, decisioni: list, selezioni: dict, rate: np.ndarray, N: int, cache: dict, dettaglio: bool = False) -> dict:
    """Esegue la tenuta: ``selezioni`` {D: lista di monete}. Costi a mercato su ogni scambio."""
    V = CAPITALE / N
    b = d.btc
    D0 = decisioni[0]
    nd = DAYN - DAY0 - D0                                      # giorni D0 .. 31 ottobre (indice DAYN-1 - D0 + 1)
    pnl = np.zeros(nd); fund = np.zeros(nd); spese = np.zeros(nd)
    viva = {}                                                  # c -> (q, Pe, qb, record)
    recs = []
    n_non_aperte = 0
    tipi = {"prot": 0, "ann": 0, "manca": 0, "ann_subito": 0}
    ncoin_dec = []
    for k, D in enumerate(decisioni):
        E = decisioni[k + 1] if k + 1 < len(decisioni) else DAYN - DAY0
        sel = selezioni.get(D, [])
        sel_set = set(sel)
        q_btc_old = sum(v[2] for v in viva.values())            # il Bitcoin long di prima (anche per le monete che escono ora)
        # uscite alla decisione delle monete che non restano
        for c in [c for c in viva if c not in sel_set]:
            q, Pe, qb, rec = viva.pop(c)
            cu = q * d.O[D, c] * rate[c]
            spese[D - D0] += cu
            if rec is not None:
                rec["costo"] += cu; rec["giorno_ultimo_costo"] = D
        nuovi = {}
        n_ap = 0
        recs_k = []
        for c in sel:
            if not np.isfinite(d.O[D, c]) or d.O[D, c] <= 0:
                n_non_aperte += 1
                continue
            stay = c in viva
            Pe = viva[c][1] if stay else d.O[D, c]
            r = periodo_moneta(d, c, D, E, Pe, V, rate, cache)
            ce = abs(V - viva[c][0] * d.O[D, c]) * rate[c] if stay else V * rate[c]
            spese[D - D0] += ce
            L = len(r["pnl"])
            if L:
                pnl[D - D0: D - D0 + L] += r["pnl"]; fund[D - D0: D - D0 + L] += r["fund"]
            if r["tipo"]:
                tipi[r["tipo"]] += 1
                spese[min(max(r["costo_uscita_giorno"], D), NG - 2) - D0] += r["costo_uscita"]
            n_ap += 1
            rec = {"c": c, "D": D, "E": E, "r": r, "costo": ce + r["costo_uscita"], "stay": stay} if dettaglio else None
            if dettaglio:
                recs.append(rec)
                recs_k.append(rec)
            if r["viva"]:
                nuovi[c] = (r["q"], Pe, r["qb"], rec)
        # Bitcoin: ritaratura netta alla decisione (long = valore totale degli short effettivi)
        q_btc_new = n_ap * V / d.O[D, b]
        cb = abs(q_btc_new - q_btc_old) * d.O[D, b] * rate[b]
        spese[D - D0] += cb
        if dettaglio and recs_k:
            for rec in recs_k:
                rec["costo"] += cb / len(recs_k)
        viva = nuovi
        ncoin_dec.append(n_ap)
    # chiusura al 1 novembre: tutto si chiude con le spese (ultimo giorno = 31 ottobre)
    q_btc_old = sum(v[2] for v in viva.values())
    ce_tot = 0.0
    for c, (q, Pe, qb, rec) in viva.items():
        cu = q * d.O[DAYN - DAY0, c] * rate[c]
        ce_tot += cu
        if rec is not None:
            rec["costo"] += cu
    ce_tot += q_btc_old * d.O[DAYN - DAY0, b] * rate[b]
    spese[nd - 1] += ce_tot
    out = {"pnl": pnl, "fund": fund, "spese": spese, "D0": D0, "tipi": tipi, "non_aperte": n_non_aperte, "monete_per_decisione": ncoin_dec}
    if dettaglio:
        out["recs"] = recs
    return out


def serie_giorni(d: Dati, s: dict) -> pd.DataFrame:
    D0 = s["D0"]
    idx = np.arange(D0, D0 + len(s["pnl"])) + DAY0
    df = pd.DataFrame({"lordo": s["pnl"] / CAPITALE, "funding": s["fund"] / CAPITALE, "spese": s["spese"] / CAPITALE}, index=idx)
    df["netto"] = df["lordo"] + df["funding"] - df["spese"]
    return df


def selezioni_modello(d: Dati, v: str, escludi=None) -> tuple:
    N = VARIANTI[v]["N"]
    dec, sel, info = [], {}, []
    for D in date_decisione(v):
        mo = modello_a(d, D, escludi)
        dec.append(D)
        if not mo["ok"]:
            sel[D] = []
            info.append((D, None))
            continue
        sel[D] = [int(x) for x in prime_n(mo, N)]
        info.append((D, mo))
    return dec, sel, info


def settimanale(df: pd.DataFrame) -> pd.DataFrame:
    g = df.groupby(ast._lunedi(df.index))
    return pd.DataFrame({"netto": g["netto"].sum(), "spese": g["spese"].sum(), "funding": g["funding"].sum(), "lordo": g["lordo"].sum()})


def numeri(df: pd.DataFrame, w: pd.DataFrame) -> dict:
    wp = ast.periodo(w["netto"])
    n = te.numeri_settimana(wp)
    r = df["netto"].to_numpy()
    anno = pd.to_datetime(df.index.to_numpy() * 86400, unit="s").year
    per = lambda col: {int(a): float(df[col].to_numpy()[anno == a].mean() * 365) for a in sorted(set(anno))}  # noqa: E731
    sett_anno = {int(a): int(s) for a, s in pd.Series(pd.to_datetime(w.index.to_numpy() * 86400, unit="s").year).value_counts().sort_index().items()}
    eq = 1 + np.cumsum(r)                                      # capitale fisso, senza comporre
    return {"giorni": int(len(df)), "annuo_capitale": float(r.mean() * 365), "per_anno": per("netto"), "funding_per_anno": per("funding"),
            "spese_per_anno": per("spese"), "lordo_prezzo_per_anno": per("lordo"), "settimane_per_anno": sett_anno,
            "sharpe_settimane": n["sharpe"], "settimane": n["settimane"], "t": n["sharpe"] * math.sqrt(n["settimane"] / 52),
            "asimmetria": n["asimmetria"], "curtosi": n["curtosi"],
            "discesa_giornaliera": float((eq / np.maximum.accumulate(eq) - 1).min()), "discesa_settimanale": n["discesa_max"],
            "sharpe_365_giorni": float(r.mean() / r.std(ddof=1) * math.sqrt(365)) if r.std() > 0 else 0.0,
            "costo_medio_annuo_capitale": float(df["spese"].mean() * 365), "funding_annuo": float(df["funding"].mean() * 365),
            "lordo_prezzo_annuo": float(df["lordo"].mean() * 365), "netto_medio_settimanale": float(r.mean() * 7),
            "primo_giorno": sc.data(int(df.index[0])), "ultimo_giorno": sc.data(int(df.index[-1])),
            "periodo_esame_dal": sc.data(int(wp.index[0])), "periodo_esame_al": sc.data(int(wp.index[-1]))}


def abc(d: Dati, recs: list, esclusi_coin=()) -> dict:
    """A = giorni prima di quello dell'annuncio, B = il giorno dell'annuncio e i successivi, C = mai annunciata nella tenuta."""
    tot = {}
    for rec in recs:
        if rec["c"] in esclusi_coin:
            continue
        r = rec["r"]
        L = len(r["pnl"])
        gg = np.arange(rec["D"], rec["D"] + L)
        anni = pd.to_datetime((gg + DAY0) * 86400, unit="s").year.to_numpy()
        if r["annunciata"]:
            ga = r["giorno_ann"]
            cls = np.where(gg < ga, "A", "B")
        else:
            cls = np.array(["C"] * L)
        netto = r["pnl"] + r["fund"]
        for kk in range(L):
            key = (str(cls[kk]), int(anni[kk]))
            e = tot.setdefault(key, [0.0, 0.0])
            e[0] += netto[kk]; e[1] += r["fund"][kk]
        # costi: all'ultimo giorno di tenuta (o al primo se non ci sono giorni) nella sua classe
        if L:
            key = (str(cls[0]), int(anni[0])); tot.setdefault(key, [0.0, 0.0])[0] -= rec["costo"]
        else:
            key = ("B" if r["annunciata"] else "C", int(pd.Timestamp((rec["D"] + DAY0) * 86400, unit="s").year)); tot.setdefault(key, [0.0, 0.0])[0] -= rec["costo"]
    out = {"netto_per_classe": {}, "funding_per_classe": {}, "netto_per_classe_anno": {}}
    for (cl, a), (n, f) in tot.items():
        out["netto_per_classe"][cl] = out["netto_per_classe"].get(cl, 0.0) + n
        out["funding_per_classe"][cl] = out["funding_per_classe"].get(cl, 0.0) + f
        out["netto_per_classe_anno"].setdefault(str(a), {})[cl] = n
    t = sum(out["netto_per_classe"].values())
    out["totale_usdt"] = t
    out["quota_per_classe"] = {k: (v / t if t > 0 else None) for k, v in out["netto_per_classe"].items()}
    return out


def contributo_monete(d: Dati, recs: list) -> pd.Series:
    x = {}
    for rec in recs:
        r = rec["r"]
        x[d.sim[rec["c"]]] = x.get(d.sim[rec["c"]], 0.0) + float(r["pnl"].sum() + r["fund"].sum()) - rec["costo"]
    return pd.Series(x).sort_values(ascending=False)


def pc(x):
    return f"{100 * x:+.2f}%"


def esegui(log=print) -> dict:
    RIS.mkdir(exist_ok=True)
    d = Dati()
    modello = json.loads((RIS / "modello.json").read_text())   # la fase 'modello' va fatta prima (coefficienti e precisione scritti prima dei risultati)
    out = {"modello_gia_scritto": True}
    res, serie_w, cache = {}, {}, {}
    for v in VARIANTI:
        N = VARIANTI[v]["N"]
        par = {"N": N, "decisione": VARIANTI[v]["decisione"], "etichetta_giorni": GIORNI_ETICHETTA, "numeri": "volume 30g, rapporto 30g/60g", "modello": "logistica L2 C=1.0 lbfgs",
               "protezione": "max giornaliero > 1,30 x entrata, uscita 1,30 x 1,01", "spese": "0,05% + scarto 0,01% BTC/ETH/SOL 0,02% altre", "capitale": CAPITALE,
               "primo_giorno": sc.data(VARIANTI[v]["inizio"]), "ultimo_giorno": "2026-10-31 (chiusura 1 nov)"}
        try:
            dec, sel, info = selezioni_modello(d, v)
            s = simula(d, dec, sel, d.rate, N, cache, dettaglio=True)
            df = serie_giorni(d, s); w = settimanale(df)
            df.to_csv(RIS / f"giorni_{v}.csv.gz"); w.to_csv(RIS / f"settimane_{v}.csv.gz")
            res[v] = {"dec": dec, "sel": sel, "info": info, "s": s, "df": df, "w": w, "num": numeri(df, w)}
            serie_w[v] = w["netto"]
        except Exception:  # noqa: BLE001
            prove.registra(ID, v, par, "giornaliera, esame sulle settimane", 0, {}, "errore", traceback.format_exc()[-300:], seme=SEME)
            raise
    cand = {f"centotreesima_{v}": {"sharpe": res[v]["num"]["sharpe_settimane"], "settimane": res[v]["num"]["settimane"], "asimmetria": res[v]["num"]["asimmetria"],
                                   "curtosi": res[v]["num"]["curtosi"]} for v in VARIANTI}
    corr = ast.corretto_famiglie({f"centotreesima_{v}": serie_w[v] for v in VARIANTI}, cand)
    out["famiglie"] = {"serie_nel_mazzo": corr["serie"], "famiglie": corr["famiglie"], "in_v": corr["in_v"], "deviazione_v": corr["deviazione_v"]}
    g1w = pd.read_csv(QUI / "risultati_prima" / "settimane_G1.csv.gz", index_col=0)["netto"]
    for v in VARIANTI:
        r, df, w, num = res[v], res[v]["df"], res[v]["w"], res[v]["num"]
        c = corr["candidate"][f"centotreesima_{v}"]
        N = VARIANTI[v]["N"]
        # ---- anni: ogni anno con decisioni positivo; l'anno parziale conta se ha almeno 8 settimane
        anni_validi = {a: x for a, x in num["per_anno"].items() if num["settimane_per_anno"].get(a, 0) >= 8}
        # ---- selezione a caso (stessa tenuta, stessa uscita, stesse spese, seme 2026)
        rng = np.random.default_rng(SEME)
        ammiss = {}
        for D, mo in r["info"]:
            ammiss[D] = mo["cand"] if mo is not None else None
        medie = np.zeros(ESTRAZIONI)
        cache_c = {}
        for e in range(ESTRAZIONI):
            sel_r = {D: ([int(x) for x in rng.choice(a, size=min(N, len(a)), replace=False)] if a is not None and len(a) else []) for D, a in ammiss.items()}
            s = simula(d, r["dec"], sel_r, d.rate, N, cache_c)
            medie[e] = float((s["pnl"] + s["fund"] - s["spese"]).mean() * 7 / CAPITALE)
        reale = num["netto_medio_settimanale"]
        p95 = float(np.percentile(medie, 95))
        caso = {"media_casuale": float(medie.mean()), "p5": float(np.percentile(medie, 5)), "p50": float(np.percentile(medie, 50)), "p95": p95, "p99": float(np.percentile(medie, 99)),
                "reale": reale, "quota_estrazioni_sotto_il_reale": float((medie < reale).mean()), "reale_sopra_p95": bool(reale > p95)}
        # ---- controlli descrittivi
        ctrl = {"selezione_a_caso": caso}
        def corri(nome, rate_, escludi=None):
            dec_, sel_, _ = selezioni_modello(d, v, escludi) if escludi is not None else (r["dec"], r["sel"], None)
            ss = simula(d, dec_, sel_, rate_, N, {})
            dd = serie_giorni(d, ss); ww = settimanale(dd); nn = numeri(dd, ww)
            ctrl[nome] = {"annuo_capitale": nn["annuo_capitale"], "per_anno": nn["per_anno"], "sharpe_settimane": nn["sharpe_settimane"], "t": nn["t"],
                          "costo_medio_annuo": nn["costo_medio_annuo_capitale"], "discesa_giornaliera": nn["discesa_giornaliera"]}
        corri("scarto_0_04", d.rate_doppio)
        corri("ordine_limite_0_02", d.rate_limite)
        corri("senza_contratti_con_volume_dopo_la_chiusura", d.rate, escludi=d.esclusi_dopo_chiusura)
        # ---- A/B/C
        recs = r["s"]["recs"]
        contributo = contributo_monete(d, recs)
        migliori5 = [d.idx[x] for x in contributo.index[:5]]
        ctrl["abc"] = abc(d, recs)
        ctrl["abc_senza_5_migliori"] = abc(d, recs, esclusi_coin=set(migliori5))
        ctrl["abc_senza_5_migliori"]["monete"] = list(contributo.index[:5])
        ctrl["contributo_top5_usdt"] = {k: float(x) for k, x in contributo.head(5).items()}
        ctrl["contributo_peggiori3_usdt"] = {k: float(x) for k, x in contributo.tail(3).items()}
        # ---- descrittivi
        durate = [(x["r"]["dend"] - x["D"] + 1) for x in recs if x["r"]["dend"] >= x["D"]]
        ctrl["durata_media_giorni"] = float(np.mean(durate)) if durate else 0.0
        ctrl["uscite_per_tipo"] = r["s"]["tipi"]
        ctrl["non_aperte_per_prezzo_mancante"] = r["s"]["non_aperte"]
        ctrl["monete_per_decisione_media"] = float(np.mean(r["s"]["monete_per_decisione"]))
        ctrl["monete_senza_funding_nel_pannello_selezionate"] = int(sum(d.sim[x["c"]] in set(d.senza_funding) for x in recs))
        ctrl["posizioni_totali"] = len(recs)
        ctrl["posizioni_rimaste_dalla_decisione_prima"] = int(sum(x["stay"] for x in recs))
        com = pd.concat([ast.periodo(w["netto"]), g1w], axis=1, join="inner").dropna(); com.columns = ["x", "g1"]
        ctrl["G1"] = {"corr_settimane": float(com.corr().iloc[0, 1]), "settimane_comuni": int(len(com))}
        cond = {"netto_positivo": bool(num["annuo_capitale"] > 0), "ogni_anno_positivo": bool(all(x > 0 for x in anni_validi.values())),
                "t_almeno_3": bool(num["t"] >= 3), "sharpe_corretto_almeno_0_80": bool(c["corretto"] >= 0.80), "meglio_della_selezione_a_caso_p95": caso["reale_sopra_p95"]}
        out[v] = {"numeri": num, "sharpe_corretto": c["corretto"], "gruppo": c["gruppo"], "condizioni": cond, "controlli": ctrl, "anni_validi": list(anni_validi)}
        out[v]["esito_parziale"] = "passa" if all(cond.values()) else "non passa"
    # natura del guadagno: se B e' la maggior parte del netto, non promosso per natura del guadagno
    for v in VARIANTI:
        q = out[v]["controlli"]["abc"]["quota_per_classe"].get("B")
        natura = bool(q is not None and q > 0.5)
        out[v]["parte_B_maggioranza"] = natura
        out[v]["esito"] = "non promosso per natura del guadagno" if (natura and out[v]["esito_parziale"] == "passa") else out[v]["esito_parziale"]
        p = {"N": VARIANTI[v]["N"], "decisione": VARIANTI[v]["decisione"], "etichetta_giorni": GIORNI_ETICHETTA, "numeri": "volume 30g, rapporto 30g/60g", "modello": "logistica L2 C=1.0 lbfgs",
             "protezione": "max giornaliero > 1,30 x entrata, uscita 1,30 x 1,01", "spese": "0,05% + scarto 0,01% BTC/ETH/SOL 0,02% altre", "capitale": CAPITALE,
             "primo_giorno": sc.data(VARIANTI[v]["inizio"]), "ultimo_giorno": "2026-10-31 (chiusura 1 nov)"}
        num = out[v]["numeri"]
        prove.registra(ID, v, p, "giornaliera, esame sulle settimane", num["giorni"],
                       {"annuo_capitale": num["annuo_capitale"], "per_anno": num["per_anno"], "sharpe": num["sharpe_settimane"], "t": num["t"],
                        "sharpe_corretto": out[v]["sharpe_corretto"], "discesa": num["discesa_giornaliera"], "costo_medio_annuo": num["costo_medio_annuo_capitale"],
                        "p95_caso": out[v]["controlli"]["selezione_a_caso"]["p95"], "reale_sett": num["netto_medio_settimanale"]},
                       out[v]["esito"], "calcolata; seme 2026 solo per la selezione a caso; condizioni=%s" % json.dumps(out[v]["condizioni"]), seme=SEME)
    (RIS / "esame.json").write_text(json.dumps(out, ensure_ascii=False, indent=1, default=float), encoding="utf-8")
    for v in VARIANTI:
        x = out[v]; n = x["numeri"]
        log(f"{v}: annuo {pc(n['annuo_capitale'])} anni {{{', '.join(f'{k}: {pc(a)}' for k, a in n['per_anno'].items())}}} Sharpe {n['sharpe_settimane']:.2f} "
            f"t {n['t']:.2f} corr {x['sharpe_corretto']:.2f} disc {pc(n['discesa_giornaliera'])} caso>p95 {x['controlli']['selezione_a_caso']['reale_sopra_p95']} -> {x['esito']}")
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--fase", required=True, choices=["modello", "prova"])
    a = ap.parse_args()
    if a.fase == "modello":
        fase_modello(Dati())
    else:
        esegui()
