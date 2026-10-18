"""Programma 5: la procedura che sceglie con il vantaggio sul caso (M-002) e il calcolo della prova in avanti delle
procedure (REGOLE.md, sezione 9).

M-002 e' M-001c (finestra di 12 mesi, 10 celle, al massimo 2 per famiglia, solo trade chiusi) con una differenza: una
cella si sceglie per il t del suo **vantaggio sul caso** nei 12 mesi prima, cioe' del netto meno il rendimento medio, nella
stessa moneta e nello stesso mese, della stessa direzione tenuta per lo stesso numero di ore (un mese si usa solo quando
e' finito), e deve avere sia il netto medio sia il vantaggio medio positivi. Cosi' si scelgono le celle che sanno **quando**
entrare, non quelle che erano solo long in un mercato che saliva.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from research.programma5.strumenti import meta
from research.programma5.strumenti.esplora_calendario import celle as celle_calendario
from research.programma5.strumenti.esplora_fase2 import BTC, celle_moneta, sfoltisci


def trade_candidate_base(monete, periodo: str, idea: str, log=print) -> dict:
    """Come ``meta.trade_candidate``, con in piu' ``base``: la media sul mese d'ingresso, nella stessa moneta, del
    rendimento della stessa cella su tutte le ore (nel verso «segue»)."""
    ore, P, A = meta.pannello(monete, periodo, idea)
    btc = P[BTC]
    mese_ora = meta.indice_mese(ore * 60)
    raccolte: dict = {}
    for s in P:
        b = P[s]
        nel = b["periodo"].to_numpy(bool)
        c_s, c_b = meta.costo(s), meta.costo(BTC)
        sorgenti = [(n, f, h, p, c, d, v) for n, f, h, p, c, d, v in celle_moneta(s, b, btc, A)]
        sorgenti += [(n, f, h, p, c, d, None) for n, f, h, p, c, d in celle_calendario(b)]
        medie_cache = {}
        for nome, fam, h, pausa, cond, d, valore in sorgenti:
            a = A[h][s] if valore is None else valore
            ev = sfoltisci(np.asarray(cond, bool) & nel & np.isfinite(a), pausa)
            if not len(ev):
                continue
            chiave = (h, nome if valore is not None else None)
            if chiave not in medie_cache:
                ok = nel & np.isfinite(a)
                medie_cache[chiave] = pd.Series(a[ok]).groupby(mese_ora[ok]).mean()
            base = d[ev] * pd.Series(mese_ora[ev]).map(medie_cache[chiave]).to_numpy(float)
            lordo = d[ev] * a[ev]
            cst = np.full(len(ev), c_s)
            if fam == "G1":
                w = int(nome.split()[1][1:])
                beta = b["beta"].shift(w).to_numpy()[ev]
                cst = cst + np.abs(np.nan_to_num(beta)) * c_b
            entrata = (ore[ev] + 1) * 60
            raccolte.setdefault(nome, [fam, []])[1].append(pd.DataFrame(
                {"moneta": s, "entrata": entrata, "uscita": entrata + 60 * h, "lordo": lordo, "costo": cst,
                 "base": base}))
        log(f"[meta2 {periodo}] {s}")
    out = {}
    for nome, (fam, parti) in raccolte.items():
        t = pd.concat(parti, ignore_index=True)
        t["famiglia"] = fam
        out[nome] = t
    return out


def con_versi(per_cella: dict) -> dict:
    out = {}
    for cella, t in per_cella.items():
        out[(cella, "segue")] = t
        c = t.copy()
        c["lordo"] = -c["lordo"]
        if "base" in c:
            c["base"] = -c["base"]
        out[(cella, "contro")] = c
    return out


def scegli_eccesso(cand: dict, L: int, K: int, primo: int, ultimo: int, n_mesi: int, max_famiglia: int = 2,
                   min_trade: int = 30, t_min: float = 2.0) -> tuple:
    """Come ``meta.scegli_e_tieni``, con il punteggio sul vantaggio sul caso (``lordo - base``) e la condizione che il
    netto medio e il vantaggio medio siano tutti e due positivi. I trade senza ``base`` (mese senza ore valide) non
    contano per la scelta."""
    chiavi = list(cand)
    netti, ag_n, ag_x = {}, np.zeros((len(chiavi), n_mesi, 6)), np.zeros((len(chiavi), n_mesi, 6))
    for i, k in enumerate(chiavi):
        t = cand[k]
        netti[k] = t["lordo"].to_numpy() - t["costo"].to_numpy()
        ecc = t["lordo"].to_numpy() - t["base"].to_numpy()
        ok = np.isfinite(ecc)
        u = t["uscita"].to_numpy()
        ag_n[i] = meta.aggregati(netti[k][ok], u[ok], n_mesi)
        ag_x[i] = meta.aggregati(ecc[ok], u[ok], n_mesi)
    cum_n = np.concatenate([np.zeros((len(chiavi), 1, 6)), np.cumsum(ag_n, axis=1)], axis=1)
    cum_x = np.concatenate([np.zeros((len(chiavi), 1, 6)), np.cumsum(ag_x, axis=1)], axis=1)
    mesi_entrata = {k: meta.indice_mese(cand[k]["entrata"].to_numpy()) for k in chiavi}
    scelti, scelte = [], {}
    for m in range(primo, ultimo + 1):
        da = max(0, m - L)
        righe = []
        for i, k in enumerate(chiavi):
            n, media_n, _ = meta.t_da_aggregati(cum_n[i, m] - cum_n[i, da])
            _, media_x, tx = meta.t_da_aggregati(cum_x[i, m] - cum_x[i, da])
            if n >= min_trade and media_n > 0 and media_x > 0 and np.isfinite(tx) and tx >= t_min:
                righe.append((tx, k))
        righe.sort(reverse=True)
        presi, per_fam, celle = [], {}, set()
        for tx, k in righe:
            cella = k[0]
            fam = cand[k]["famiglia"].iat[0]
            if per_fam.get(fam, 0) >= max_famiglia or cella in celle:
                continue
            presi.append(k)
            per_fam[fam] = per_fam.get(fam, 0) + 1
            celle.add(cella)
            if len(presi) == K:
                break
        scelte[m] = presi
        for k in presi:
            sel = mesi_entrata[k] == m
            if sel.any():
                t = cand[k][sel]
                scelti.append(pd.DataFrame({"simbolo": t["moneta"].to_numpy(), "minuto": t["entrata"].to_numpy(),
                                            "uscita": t["uscita"].to_numpy(), "netto": netti[k][sel],
                                            "netto_doppio": netti[k][sel] - t["costo"].to_numpy(),
                                            "lordo": t["lordo"].to_numpy(), "costo": t["costo"].to_numpy(),
                                            "base": t["base"].to_numpy(), "cella": k[0], "verso": k[1]}))
    return (pd.concat(scelti, ignore_index=True) if scelti else pd.DataFrame()), scelte
