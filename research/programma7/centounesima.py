"""Prova 163 (CENTOUNESIMA.md + «Chiusura della verifica»): l'arbitraggio del funding fra Binance e Hyperliquid, una gamba per borsa
sulla stessa moneta. Solo le varianti A (30 giorni, soglia 10% l'anno, il primo del mese) e B (7 giorni, 20% l'anno, il lunedi').
Dati: solo quelli scaricati da centounesima_dati.py. Deterministica (nessun seme).

Uso: python3 -m research.programma7.centounesima
"""
from __future__ import annotations

import io
import json
import math
import traceback
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd

from research.programma5.strumenti import motore5 as m5
from research.programma6 import asticella as ast
from research.programma6 import seconda as sc
from research.programma6 import terza as te
from research.programma7 import centounesima_dati as dat
from research.src import prove
from research.src.dati import funding_da_zip

QUI = Path(__file__).parent
RIS = QUI / "risultati_centounesima"
ID = "centounesima"
DAY = 86_400_000
DAY0 = sc.giorno(2023, 5, 1)
DAYN = sc.giorno(2026, 11, 1)                    # apertura del 1 novembre 2026: le posizioni aperte si chiudono li'
NG = DAYN - DAY0 + 1                             # indici di giorno 0..NG-1 (l'ultimo = 1 novembre)
NH = (NG - 1) * 24
START = sc.giorno(2023, 6, 5) - DAY0
TAGLIO_ORARIO = sc.giorno(2026, 4, 26) - DAY0    # dal 26 aprile 2026 candele orarie, prima massimo e minimo giornaliero
CAPITALE = 1000.0
COMM_B, COMM_H = 0.0005, 0.00045
COMM_B_LIM, COMM_H_LIM = 0.0002, 0.00015
MMR, SOGLIA_RISCHIO, PERDITA_LIQ = 0.005, 0.10, 0.01
SOGLIA_TRASF, COSTO_TRASF = 0.10, 1.0
MIN_STORIA = 30
VARIANTI = {"A": {"L": 30, "theta_anno": 0.10, "decisione": "primo del mese"},
            "B": {"L": 7, "theta_anno": 0.20, "decisione": "lunedi"}}
for _v in VARIANTI.values():
    _v["theta"] = _v["theta_anno"] / 365


# ---------------------------------------------------------------------------------------------------------------- dati
def leggi_k(f: Path) -> pd.DataFrame:
    with zipfile.ZipFile(f) as z:
        g = z.read(z.namelist()[0])
    d = pd.read_csv(io.BytesIO(g), header=0 if g[:1].isalpha() else None).iloc[:, :8]
    d.columns = ["t", "open", "high", "low", "close", "volume", "t_chiusura", "qvolume"]
    t = pd.to_numeric(d["t"])
    d["t"] = t.where(t < 10 ** 14, t // 1000)
    return d


def carica_moneta(n: str, s: str) -> dict:
    t0 = DAY0 * DAY
    out = {}
    # Binance candele giornaliere
    o = np.full(NG, np.nan); hi = o.copy(); lo = o.copy(); cl = o.copy(); qv = o.copy()
    for f in sorted((dat.DATI / "bn" / "d1" / s).glob("*.zip")):
        d = leggi_k(f)
        k = ((d["t"].to_numpy() - t0) // DAY).astype(int)
        ok = (k >= 0) & (k < NG)
        o[k[ok]] = d["open"].to_numpy(float)[ok]; hi[k[ok]] = d["high"].to_numpy(float)[ok]; lo[k[ok]] = d["low"].to_numpy(float)[ok]
        cl[k[ok]] = d["close"].to_numpy(float)[ok]; qv[k[ok]] = d["qvolume"].to_numpy(float)[ok]
    if np.isfinite(cl[NG - 2]):
        o[NG - 1] = cl[NG - 2]                                   # apertura del 1 novembre = chiusura del 31 ottobre (limite: manca il file di novembre)
    out.update(bo=o, bhi=hi, blo=lo, bqv=qv)
    # Binance mark a 1 ora
    mh = np.full(NH, np.nan); ml = mh.copy()
    for f in sorted((dat.DATI / "bn" / "mark1h" / s).glob("*.zip")):
        d = leggi_k(f)
        k = ((d["t"].to_numpy() - t0) // 3_600_000).astype(int)
        ok = (k >= 0) & (k < NH)
        mh[k[ok]] = d["high"].to_numpy(float)[ok]; ml[k[ok]] = d["low"].to_numpy(float)[ok]
    out.update(mh=mh, ml=ml)
    # funding Binance: pagamenti veri; tenuta = (minuto - 1) // 1440; ora = (minuto - 1) // 60
    fb = np.zeros(NH); nb = np.zeros(NG)
    righe = []
    for f in sorted((dat.DATI / "bn" / "funding" / s).glob("*.zip")):
        righe += funding_da_zip(f)
    if righe:
        r = pd.DataFrame(righe, columns=["ts", "ore", "tasso"]).drop_duplicates("ts")
        mi = r["ts"].to_numpy() // 60_000
        h = (mi - 1) // 60 - DAY0 * 24
        ok = (h >= 0) & (h < NH)
        np.add.at(fb, h[ok], r["tasso"].to_numpy(float)[ok]); np.add.at(nb, h[ok] // 24, 1)
    out.update(fb=fb, nb=nb)
    # Hyperliquid funding
    fh = np.zeros(NH); nh = np.zeros(NG)
    st = json.loads((dat.DATI / "hl_funding" / f"{n}.json").read_text())["righe"]
    if st:
        r = pd.DataFrame(st, columns=["ts", "tasso"]).drop_duplicates("ts")
        mi = r["ts"].to_numpy() // 60_000
        h = (mi - 1) // 60 - DAY0 * 24
        ok = (h >= 0) & (h < NH)
        np.add.at(fh, h[ok], r["tasso"].to_numpy(float)[ok]); np.add.at(nh, h[ok] // 24, 1)
    out.update(fh=fh, nh=nh)
    # Hyperliquid candele
    ho = np.full(NG, np.nan); hhi = ho.copy(); hlo = ho.copy()
    c = json.loads((dat.DATI / "hl_candele" / f"{n}_1d.json").read_text())["candele"]
    if c:
        a = np.array(c, float)
        k = ((a[:, 0] - t0) // DAY).astype(int)
        ok = (k >= 0) & (k < NG - 1)
        ho[k[ok]] = a[ok, 1]; hhi[k[ok]] = a[ok, 2]; hlo[k[ok]] = a[ok, 3]
        k31 = (NG - 2)
        i31 = np.flatnonzero(k == k31)
        if len(i31):
            ho[NG - 1] = a[i31[0], 4]                            # chiusura del 31 ottobre = apertura del 1 novembre
    hh = np.full(NH, np.nan); hl = hh.copy()
    c = json.loads((dat.DATI / "hl_candele" / f"{n}_1h.json").read_text())["candele"]
    if c:
        a = np.array(c, float)
        k = ((a[:, 0] - t0) // 3_600_000).astype(int)
        ok = (k >= 0) & (k < NH)
        hh[k[ok]] = a[ok, 2]; hl[k[ok]] = a[ok, 3]
    out.update(ho=ho, hhi=hhi, hlo=hlo, hh=hh, hl=hl)
    return out


def carica_tutto(log=print) -> dict:
    ab = dat.carica_ab()
    coin, sym, delist, X = [], [], [], []
    esclusi = {}
    for n, v in ab.items():
        s = v["binance"]
        try:
            x = carica_moneta(n, s)
        except Exception as e:  # noqa: BLE001
            esclusi[n] = f"errore nel caricare i dati: {e!r}"[:100]
            continue
        comune = np.flatnonzero(np.isfinite(x["bo"][:NG - 1]) & np.isfinite(x["ho"][:NG - 1]))
        if not len(comune):
            esclusi[n] = "nessun giorno con prezzi su tutte e due le borse"
            continue
        ratio = x["bo"][comune[0]] / x["ho"][comune[0]]
        if not (0.9 <= ratio <= 1.1):
            esclusi[n] = f"rapporto dei prezzi il primo giorno comune {ratio:.4g} fuori da 0,9-1,1"
            continue
        coin.append(n); sym.append(s); delist.append(v["isDelisted"]); X.append(x)
    nc = len(coin)
    P = {"coin": coin, "sym": sym, "delist": delist, "esclusi": esclusi}
    for k in X[0]:
        P[k] = np.vstack([x[k] for x in X])
    log(f"monete nell'universo {nc}; escluse {len(esclusi)}")
    return P


# ---------------------------------------------------------------------------------------------------------------- segnale
def prepara(P: dict, L: int, theta: float) -> dict:
    nc = len(P["coin"])
    okp = np.isfinite(P["bo"][:, :NG - 1]) & np.isfinite(P["ho"][:, :NG - 1])
    sf = P["fh"].reshape(nc, NG - 1, 24).sum(2) - P["fb"].reshape(nc, NG - 1, 24).sum(2)          # scarto giornaliero (HL - Binance)
    okf = (P["nb"][:, :NG - 1] > 0) & (P["nh"][:, :NG - 1] > 0)
    valido = okp & okf
    cs = np.concatenate([np.zeros((nc, 1)), np.cumsum(valido, axis=1)], axis=1)          # cs[:, i] = giorni validi strettamente prima di i
    cd = np.concatenate([np.zeros((nc, 1)), np.cumsum(np.where(valido, sf, 0.0), axis=1)], axis=1)
    sig = np.zeros((nc, NG - 1), int); dmed = np.full((nc, NG - 1), np.nan); fin = np.zeros((nc, NG - 1), bool); base = np.zeros((nc, NG - 1), bool)
    for i in range(L, NG - 1):
        fin[:, i] = (cs[:, i] - cs[:, i - L]) == L
        dmed[:, i] = (cd[:, i] - cd[:, i - L]) / L
    base = okp & (cs[:, :NG - 1] >= MIN_STORIA)
    sig[base & fin & (dmed > theta)] = 1                  # +1 = comprata su Binance, venduta su Hyperliquid
    sig[base & fin & (dmed < -theta)] = -1
    primo = np.array([int(np.flatnonzero(cs[c, :NG - 1] >= MIN_STORIA)[0]) if (cs[c, :NG - 1] >= MIN_STORIA).any() else -1 for c in range(nc)])
    return {"sig": sig, "base": base, "fin": fin, "dmed": dmed, "alive": okp, "primo": primo}


def e_decisione(var: str, i: int) -> bool:
    g = DAY0 + i
    if var == "A":
        return pd.Timestamp(g * 86400, unit="s").day == 1
    return (g + 3) % 7 == 0


def volume30(P: dict) -> np.ndarray:
    qv = np.nan_to_num(P["bqv"][:, :NG - 1]); ok = np.isfinite(P["bqv"][:, :NG - 1])
    c1 = np.concatenate([np.zeros((qv.shape[0], 1)), np.cumsum(qv, axis=1)], axis=1); c2 = np.concatenate([np.zeros((qv.shape[0], 1)), np.cumsum(ok, axis=1)], axis=1)
    out = np.full(qv.shape, np.nan)
    for i in range(1, NG - 1):
        j = max(0, i - 30)
        n = c2[:, i] - c2[:, j]
        out[:, i] = np.where(n > 0, (c1[:, i] - c1[:, j]) / np.maximum(n, 1), np.nan)
    return out


# ---------------------------------------------------------------------------------------------------------------- simulazione
def estremi_giorno(P: dict, i: int):
    """Prezzi del giorno i per il controllo del margine: (passi, lo_B, hi_B, lo_H, hi_H) con forma (monete, passi)."""
    nc = len(P["coin"])
    if i >= TAGLIO_ORARIO:
        h0 = i * 24
        lb, hb = P["ml"][:, h0:h0 + 24], P["mh"][:, h0:h0 + 24]
        lh, hh = P["hl"][:, h0:h0 + 24], P["hh"][:, h0:h0 + 24]
        # buchi orari: si ripiega sul massimo/minimo giornaliero (piu' severo)
        lb = np.where(np.isfinite(lb), lb, P["blo"][:, i:i + 1]); hb = np.where(np.isfinite(hb), hb, P["bhi"][:, i:i + 1])
        lh = np.where(np.isfinite(lh), lh, P["hlo"][:, i:i + 1]); hh = np.where(np.isfinite(hh), hh, P["hhi"][:, i:i + 1])
        return "orario", lb, hb, lh, hh
    h0 = i * 24
    mh = P["mh"][:, h0:h0 + 24]; ml = P["ml"][:, h0:h0 + 24]
    with np.errstate(all="ignore"):
        hb = np.where(np.isfinite(mh).any(1), np.nanmax(np.where(np.isfinite(mh), mh, -np.inf), axis=1), np.nan)[:, None]
        lb = np.where(np.isfinite(ml).any(1), np.nanmin(np.where(np.isfinite(ml), ml, np.inf), axis=1), np.nan)[:, None]
    hb = np.where(np.isfinite(hb), hb, P["bhi"][:, i:i + 1]); lb = np.where(np.isfinite(lb), lb, P["blo"][:, i:i + 1])
    return "giornaliero", lb, hb, P["hlo"][:, i:i + 1], P["hhi"][:, i:i + 1]


def ffill_righe(a: np.ndarray) -> np.ndarray:
    return pd.DataFrame(a.T).ffill().to_numpy().T


def simula(P: dict, Q: dict, var: str, filtro=None, comm_b: float = COMM_B, comm_h: float = COMM_H, escludi=()) -> dict:
    nc = len(P["coin"])
    scarto = np.array([m5.scarto(s) for s in P["sym"]])
    cB, cH = comm_b + scarto, comm_h + scarto
    PBf, PHf = ffill_righe(P["bo"]), ffill_righe(P["ho"])
    consentita = np.ones(nc, bool)
    for e in escludi:
        consentita[P["coin"].index(e) if e in P["coin"] else P["sym"].index(e)] = False
    side = np.zeros(nc, int); q = np.zeros(nc); p0b = np.ones(nc); p0h = np.ones(nc)
    vb = np.zeros(nc, bool); vh = np.zeros(nc, bool); pend = np.zeros(nc, bool)
    cash = np.array([CAPITALE / 2, CAPITALE / 2])          # [Binance, Hyperliquid]
    transit = np.zeros(2)
    righe = []; contrib = np.zeros(nc)
    ev = {"liquidazioni": [], "giorni_a_rischio": [], "trasferimenti": 0, "chiusure_buco": [], "cambi_lato": 0, "ingressi": 0, "decisioni": 0}
    n_moneta_dec = []
    E_prev = None

    def unreal(ratio_b, ratio_h):
        ub = np.where(vb, side * q * (ratio_b - 1), 0.0)
        uh = np.where(vh, -side * q * (ratio_h - 1), 0.0)
        return ub, uh

    for i in range(START, NG):
        cash += transit; transit[:] = 0
        ultimo = (i == NG - 1)
        alive = np.isfinite(P["bo"][:, i]) & np.isfinite(P["ho"][:, i])
        pb = np.where(alive, P["bo"][:, i], PBf[:, i]); ph = np.where(alive, P["ho"][:, i], PHf[:, i])
        ub, uh = unreal(pb / p0b, ph / p0h)
        E_pre = cash.sum() + ub.sum() + uh.sum()
        if E_prev is not None:                               # il rendimento del giorno prima si chiude qui
            righe[-1]["E_dopo"] = E_pre
        spese = 0.0; funding = 0.0; liq_loss = 0.0
        eventi_giorno = []
        # ---- chiusure forzate: buco di prezzi o liquidazione del giorno prima
        forzato = ((side != 0) & ~alive) | pend
        for c in np.flatnonzero((side != 0) & ~alive & ~pend):
            if not ultimo:
                ev["chiusure_buco"].append((P["coin"][c], sc.data(DAY0 + i)))
        # ---- decisione del giorno
        nuovo = side.copy()
        dec = (not ultimo) and e_decisione(var, i)
        if ultimo:
            nuovo[:] = 0
        elif dec:
            cand = Q["sig"][:, i].copy()
            cand[~consentita] = 0
            if filtro is not None:
                cand[~filtro(i)] = 0
            cand[~alive] = 0                                 # senza i prezzi di oggi non si apre e non si tiene
            nuovo = cand
            ev["decisioni"] += 1
        else:
            nuovo[forzato] = 0
        proc = np.ones(nc, bool) if (dec or ultimo) else forzato
        if proc.any():
            n_new = int((nuovo != 0).sum())
            qn = E_pre / n_new if n_new else 0.0
            for c in np.flatnonzero(proc):
                if side[c] == 0 and nuovo[c] == 0:
                    pend[c] = False
                    continue
                vbn = q[c] * pb[c] / p0b[c] if vb[c] else 0.0          # valore corrente delle gambe che si chiudono o si cambiano
                vhn = q[c] * ph[c] / p0h[c] if vh[c] else 0.0
                cash[0] += ub[c]; cash[1] += uh[c]                     # realizza il risultato (il margine contiene i guadagni non realizzati)
                if nuovo[c] == side[c] and not pend[c] and alive[c]:
                    sB, sH = abs(qn - vbn), abs(qn - vhn)              # stessa direzione: si cambia solo la quota
                else:
                    sB = vbn + (qn if nuovo[c] != 0 else 0.0)
                    sH = vhn + (qn if nuovo[c] != 0 else 0.0)
                    if side[c] != 0 and nuovo[c] != 0 and nuovo[c] != side[c]:
                        ev["cambi_lato"] += 1
                    if side[c] == 0 and nuovo[c] != 0:
                        ev["ingressi"] += 1
                fee = sB * cB[c] + sH * cH[c]
                cash[0] -= sB * cB[c]; cash[1] -= sH * cH[c]
                spese += fee
                contrib[c] += ub[c] + uh[c] - fee
                ub[c] = uh[c] = 0.0
                side[c] = nuovo[c]; pend[c] = False
                if nuovo[c] != 0:
                    q[c] = qn; p0b[c] = pb[c]; p0h[c] = ph[c]; vb[c] = vh[c] = True
                else:
                    q[c] = 0.0; vb[c] = vh[c] = False
            if dec:
                n_moneta_dec.append(n_new)
        if ultimo:
            righe.append({"i": i, "E_pre": E_pre, "spese": spese, "funding": 0.0, "liq": 0.0, "monete": 0})
            righe[-1]["E_dopo"] = E_pre - spese
            break
        # ---- trasferimento fra le borse (una volta al giorno, effetto dal giorno dopo)
        ub, uh = unreal(pb / p0b, ph / p0h)
        M = np.array([cash[0] + ub.sum(), cash[1] + uh.sum()])
        tot = M.sum()
        diff = M[0] - tot / 2
        if abs(diff) > SOGLIA_TRASF * (tot) and tot > 0:
            da, a = (0, 1) if diff > 0 else (1, 0)
            cash[da] -= abs(diff) + COSTO_TRASF
            transit[a] += abs(diff)
            spese += COSTO_TRASF
            ev["trasferimenti"] += 1
        # ---- il giorno: controllo del margine, funding, liquidazioni
        metodo, lb, hb, lh, hh = estremi_giorno(P, i)
        passi = lb.shape[1]
        rischio = False
        for s in range(passi):
            if not (vb.any() or vh.any()):
                break
            # lato peggiore per ogni gamba: Binance lunga -> minimo, corta -> massimo; Hyperliquid opposta
            xb = np.where(side > 0, lb[:, s], hb[:, s]) / p0b
            xh = np.where(side > 0, hh[:, s], lh[:, s]) / p0h
            xb = np.where(np.isfinite(xb), xb, pb / p0b); xh = np.where(np.isfinite(xh), xh, ph / p0h)
            ub2, uh2 = unreal(xb, xh)
            val = np.array([(q * xb)[vb].sum(), (q * xh)[vh].sum()])
            marg = np.array([cash[0] + ub2.sum(), cash[1] + uh2.sum()])
            for e_ in (0, 1):
                if val[e_] > 0 and marg[e_] < SOGLIA_RISCHIO * val[e_]:
                    rischio = True
            liquidate = [e_ for e_ in (0, 1) if val[e_] > 0 and marg[e_] < MMR * val[e_]]
            for e_ in liquidate:
                vv = vb if e_ == 0 else vh
                uu = ub2 if e_ == 0 else uh2
                xx = xb if e_ == 0 else xh
                for c in np.flatnonzero(vv):
                    perdita = PERDITA_LIQ * q[c] * xx[c]
                    cash[e_] += uu[c] - perdita
                    liq_loss += perdita
                    contrib[c] += uu[c] - perdita
                    vv[c] = False
                    altro = vh[c] if e_ == 0 else vb[c]
                    if altro:
                        pend[c] = True
                    else:
                        side[c] = 0; q[c] = 0.0; pend[c] = False
                ev["liquidazioni"].append((sc.data(DAY0 + i), "Binance" if e_ == 0 else "Hyperliquid", metodo))
            if metodo == "orario":
                # funding pagato in quest'ora (le gambe vive)
                h = i * 24 + s
                fB = -np.where(vb, side * q * P["fb"][:, h], 0.0); fH = -np.where(vh, -side * q * P["fh"][:, h], 0.0)
                cash[0] += fB.sum(); cash[1] += fH.sum(); funding += fB.sum() + fH.sum(); contrib += fB + fH
        if metodo == "giornaliero":
            sl = slice(i * 24, i * 24 + 24)
            fb_d = P["fb"][:, sl].sum(1); fh_d = P["fh"][:, sl].sum(1)
            fB = -np.where(vb, side * q * fb_d, 0.0); fH = -np.where(vh, -side * q * fh_d, 0.0)
            cash[0] += fB.sum(); cash[1] += fH.sum(); funding += fB.sum() + fH.sum(); contrib += fB + fH
            # liquidazione e rischio col lato peggiore del giorno (un solo passo, gia' fatto sopra)
        if rischio:
            ev["giorni_a_rischio"].append((sc.data(DAY0 + i), metodo))
        righe.append({"i": i, "E_pre": E_pre, "spese": spese, "funding": funding, "liq": liq_loss, "monete": int((side != 0).sum())})
        E_prev = E_pre
    d = pd.DataFrame([x for x in righe if "E_dopo" in x])
    d = d[d["i"] < NG - 1].copy()
    d.index = d["i"].to_numpy() + DAY0
    d["netto_usdt"] = d["E_dopo"] - d["E_pre"]
    d["netto"] = d["netto_usdt"] / d["E_pre"]
    d["funding"] = d["funding"] / d["E_pre"]
    d["spese"] = d["spese"] / d["E_pre"]
    d["liq"] = d["liq"] / d["E_pre"]
    d["lordo"] = d["netto"] - d["funding"] + d["spese"]          # prezzo (compresa la perdita delle liquidazioni)
    # il costo di chiusura del 1 novembre e' nell'ultima riga: si somma al 31 ottobre
    ult = [x for x in righe if x["i"] == NG - 1]
    if ult and len(d):
        extra = ult[0]["spese"]
        d.loc[d.index[-1], "spese"] += extra / d["E_pre"].iloc[-1]
        d.loc[d.index[-1], "netto"] -= extra / d["E_pre"].iloc[-1]
    return {"d": d, "ev": ev, "contrib": contrib, "coin": P["coin"], "n_moneta_dec": n_moneta_dec}


# ---------------------------------------------------------------------------------------------------------------- misure
def settimanale(d: pd.DataFrame) -> pd.DataFrame:
    g = d.groupby(ast._lunedi(d.index))
    return pd.DataFrame({"netto": g["netto"].sum(), "spese": g["spese"].sum(), "funding": g["funding"].sum(), "monete": g["monete"].max()})


def numeri(d: pd.DataFrame, w: pd.DataFrame) -> dict:
    wp = ast.periodo(w["netto"])
    n = te.numeri_settimana(wp)
    r = d["netto"].to_numpy()
    anno = pd.to_datetime(d.index.to_numpy() * 86400, unit="s").year
    per = lambda col: {int(a): float(d[col].to_numpy()[anno == a].mean() * 365) for a in sorted(set(anno))}  # noqa: E731
    eq = np.cumprod(1 + r)
    return {"giorni": int(len(d)), "annuo_capitale": float(r.mean() * 365), "per_anno": per("netto"), "funding_per_anno": per("funding"),
            "spese_per_anno": per("spese"), "lordo_prezzo_per_anno": per("lordo"),
            "sharpe_settimane": n["sharpe"], "settimane": n["settimane"], "t": n["sharpe"] * math.sqrt(n["settimane"] / 52),
            "asimmetria": n["asimmetria"], "curtosi": n["curtosi"], "discesa_settimanale": n["discesa_max"],
            "discesa_giornaliera": float((eq / np.maximum.accumulate(eq) - 1).min()),
            "sharpe_365_giorni": float(r.mean() / r.std(ddof=1) * math.sqrt(365)) if r.std() > 0 else 0.0,
            "costo_medio_annuo_capitale": float(d["spese"].mean() * 365), "funding_annuo": float(d["funding"].mean() * 365),
            "lordo_prezzo_annuo": float(d["lordo"].mean() * 365), "giorni_fermi": int((d["monete"] == 0).sum()),
            "monete_medie_in_posizione": float(d["monete"].mean()), "primo_giorno": sc.data(int(d.index[0])), "ultimo_giorno": sc.data(int(d.index[-1])),
            "periodo_esame_dal": sc.data(int(wp.index[0])), "periodo_esame_al": sc.data(int(wp.index[-1]))}


def conta_ev(ev: dict) -> dict:
    liq = {"giornaliero": 0, "orario": 0}
    for _, _, m in ev["liquidazioni"]:
        liq[m] += 1
    ris = {"giornaliero": 0, "orario": 0}
    for _, m in ev["giorni_a_rischio"]:
        ris[m] += 1
    return {"liquidazioni_per_metodo": liq, "liquidazioni_totali": len(ev["liquidazioni"]), "giorni_a_rischio_per_metodo": ris,
            "giorni_a_rischio_totali": len(ev["giorni_a_rischio"]), "primi_giorni_a_rischio": ev["giorni_a_rischio"][:6],
            "elenco_liquidazioni": ev["liquidazioni"][:10], "trasferimenti": ev["trasferimenti"], "chiusure_per_buco": len(ev["chiusure_buco"]),
            "primi_buchi": ev["chiusure_buco"][:6], "cambi_lato": ev["cambi_lato"], "ingressi": ev["ingressi"], "decisioni": ev["decisioni"]}


def pc(x):
    return f"{100 * x:+.2f}%"


def esegui(log=print) -> dict:
    RIS.mkdir(exist_ok=True)
    P = carica_tutto(log)
    nc = len(P["coin"])
    vol = volume30(P)
    out = {"universo_n": nc, "esclusi": P["esclusi"]}
    res, serie_w = {}, {}
    Qs = {v: prepara(P, par["L"], par["theta"]) for v, par in VARIANTI.items()}
    # elenco dell'universo, scritto a parte
    righe_u = []
    for c in range(nc):
        r = {"moneta_hl": P["coin"][c], "simbolo_binance": P["sym"][c], "ritirata_da_hl": P["delist"][c]}
        for v in VARIANTI:
            p = Qs[v]["primo"][c]
            r[f"primo_giorno_con_30_giorni_{v}"] = sc.data(DAY0 + p) if p >= 0 else ""
        righe_u.append(r)
    pd.DataFrame(righe_u).to_csv(RIS / "universo.csv", index=False)
    for v, par in VARIANTI.items():
        parametri = {"L": par["L"], "theta_anno": par["theta_anno"], "decisione": par["decisione"], "commissioni": "B 0,05% H 0,045% a mercato",
                     "scarto": "0,01% BTC ETH SOL, 0,02% altre", "periodo": "2023-06-05 .. 2026-10-31 (chiusura 1 nov)", "capitale": CAPITALE,
                     "universo": nc, "trasferimento": "1 USDT se scarto > 10% capitale", "margine_rischio": SOGLIA_RISCHIO, "mantenimento": MMR}
        try:
            r = simula(P, Qs[v], v)
            d = r["d"]; w = settimanale(d)
            d.to_csv(RIS / f"giorni_{v}.csv.gz"); w.to_csv(RIS / f"settimane_{v}.csv.gz")
            res[v] = {"r": r, "d": d, "w": w, "num": numeri(d, w)}
            serie_w[v] = w["netto"]
        except Exception:  # noqa: BLE001
            prove.registra(ID, v, parametri, "giornaliera, esame sulle settimane", 0, {}, "errore", traceback.format_exc()[-300:])
            raise
    cand = {f"163 {v}": {"sharpe": res[v]["num"]["sharpe_settimane"], "settimane": res[v]["num"]["settimane"], "asimmetria": res[v]["num"]["asimmetria"],
                         "curtosi": res[v]["num"]["curtosi"]} for v in VARIANTI}
    corr = ast.corretto_famiglie({f"163 {v}": serie_w[v] for v in VARIANTI}, cand)
    out["famiglie"] = {"serie_nel_mazzo": corr["serie"], "famiglie": corr["famiglie"], "in_v": corr["in_v"], "deviazione_v": corr["deviazione_v"]}
    g1d = pd.read_csv(QUI / "risultati_prima" / "giorni_G1.csv.gz")["netto"]
    g1d.index = np.arange(sc.giorno(2021, 1, 4), sc.giorno(2021, 1, 4) + len(g1d))
    g1w = pd.read_csv(QUI / "risultati_prima" / "settimane_G1.csv.gz", index_col=0)["netto"]
    idx_btc = [P["sym"].index(s) for s in ("BTCUSDT", "ETHUSDT") if s in P["sym"]]
    for v in VARIANTI:
        r, d, w, num = res[v]["r"], res[v]["d"], res[v]["w"], res[v]["num"]
        m = conta_ev(r["ev"])
        c = corr["candidate"][f"163 {v}"]
        cond = {"netto_positivo": bool(num["annuo_capitale"] > 0), "ogni_anno_positivo": bool(all(x > 0 for x in num["per_anno"].values())),
                "t_almeno_3": bool(num["t"] >= 3), "sharpe_corretto_almeno_0_80": bool(c["corretto"] >= 0.80),
                "nessuna_liquidazione": bool(m["liquidazioni_totali"] == 0)}
        passa = all(cond.values())
        poco = bool(num["annuo_capitale"] < 0.03)
        esito = "passa" if (passa and not poco) else ("non promosso per poco valore" if (passa and poco) else "non passa")
        # ---- controlli descrittivi (non sono varianti)
        solo = np.zeros(nc, bool); solo[idx_btc] = True
        def top30(i, v_=vol):
            x = v_[:, i]; ok = np.isfinite(x)
            top = np.zeros(nc, bool)
            if ok.sum():
                ordine = np.argsort(-np.where(ok, x, -np.inf))[:30]
                top[ordine] = True
            return top & ok
        controlli = {}
        def corri(nome, **kw):
            rr = simula(P, Qs[v], v, **kw); dd = rr["d"]; ww = settimanale(dd); nn = numeri(dd, ww)
            controlli[nome] = {"annuo_capitale": nn["annuo_capitale"], "per_anno": nn["per_anno"], "sharpe_settimane": nn["sharpe_settimane"], "t": nn["t"],
                               "discesa_giornaliera": nn["discesa_giornaliera"], "liquidazioni": len(rr["ev"]["liquidazioni"]),
                               "giorni_a_rischio": len(rr["ev"]["giorni_a_rischio"]), "costo_medio_annuo": nn["costo_medio_annuo_capitale"], "giorni": nn["giorni"]}
            return rr
        corri("solo_BTC_ETH", filtro=lambda i, s_=solo: s_)
        corri("prime_30_per_volume", filtro=top30)
        corri("le_altre_senza_le_prime_30", filtro=lambda i: ~top30(i))
        corri("spese_ordine_limite", comm_b=COMM_B_LIM, comm_h=COMM_H_LIM)
        contributo = pd.Series(r["contrib"], index=r["coin"]).sort_values(ascending=False)
        migliore = contributo.index[0]
        corri("senza_la_moneta_migliore", escludi=(migliore,))
        controlli["senza_la_moneta_migliore"]["moneta"] = migliore
        controlli["contributo_USDT_top5"] = {k: float(x) for k, x in contributo.head(5).items()}
        controlli["contributo_USDT_peggiori3"] = {k: float(x) for k, x in contributo.tail(3).items()}
        wp = ast.periodo(w["netto"])
        com = pd.concat([wp, g1w], axis=1, join="inner").dropna(); com.columns = ["x", "g1"]
        dcom = pd.concat([d["netto"], g1d], axis=1, join="inner").dropna()
        controlli["G1"] = {"corr_settimane": float(com.corr().iloc[0, 1]), "corr_giorni": float(dcom.corr().iloc[0, 1]), "settimane_comuni": int(len(com))}
        controlli["monete_per_decisione_media"] = float(np.mean(r["n_moneta_dec"])) if r["n_moneta_dec"] else 0.0
        out[v] = {"numeri": num, "sharpe_corretto": c["corretto"], "gruppo": c["gruppo"], "condizioni": cond, "esito": esito, "eventi": m, "controlli": controlli}
        prove.registra(ID, v, {"L": VARIANTI[v]["L"], "theta_anno": VARIANTI[v]["theta_anno"], "decisione": VARIANTI[v]["decisione"],
                                "commissioni": "B 0,05% H 0,045%", "periodo": "2023-06-05 .. 2026-10-31", "capitale": CAPITALE, "universo": nc},
                       "giornaliera, esame sulle settimane", num["giorni"],
                       {"annuo_capitale": num["annuo_capitale"], "per_anno": num["per_anno"], "sharpe": num["sharpe_settimane"], "t": num["t"],
                        "sharpe_corretto": c["corretto"], "discesa": num["discesa_giornaliera"], "liquidazioni": m["liquidazioni_totali"],
                        "giorni_a_rischio": m["giorni_a_rischio_totali"], "trasferimenti": m["trasferimenti"], "costo_medio_annuo": num["costo_medio_annuo_capitale"]},
                       esito, "calcolata; deterministica (nessun seme); condizioni=%s" % json.dumps(cond))
    (RIS / "esame.json").write_text(json.dumps(out, ensure_ascii=False, indent=1, default=float), encoding="utf-8")
    for v in VARIANTI:
        x = out[v]; n = x["numeri"]
        log(f"{v}: annuo {pc(n['annuo_capitale'])} anni {{{', '.join(f'{k}: {pc(a)}' for k, a in n['per_anno'].items())}}} Sharpe {n['sharpe_settimane']:.2f} "
            f"t {n['t']:.2f} corr {x['sharpe_corretto']:.2f} disc {pc(n['discesa_giornaliera'])} liq {x['eventi']['liquidazioni_totali']} "
            f"rischio {x['eventi']['giorni_a_rischio_totali']} -> {x['esito']}")
    return out


if __name__ == "__main__":
    esegui()
