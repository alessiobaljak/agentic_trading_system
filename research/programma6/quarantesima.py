"""Programma 6, quarantesima prova (QUARANTESIMA.md): le coppie di monete che si allontanano. Ogni primo lunedi' del mese,
con i 180 giorni prima, per ogni moneta dell'universo la piu' correlata; coppie con correlazione almeno 0,80, le 20 piu'
correlate senza monete ripetute; rapporto log(A) − b·log(B), z sui 60 giorni prima; entrata con |z| sopra 2, uscita sotto
0,5, sopra 4 o dopo 20 giorni; 5% per gamba, al massimo 20 coppie aperte.

Scelte di calcolo non scritte nelle regole (fissate prima di guardare i risultati): A e' la moneta meno scambiata delle
due, B la piu' scambiata (si copre la minore con la maggiore); la regressione e' log(A) su log(B) con l'intercetta; una
coppia con b non positivo non si usa; per entrare le due monete devono essere nell'universo del giorno; le operazioni
ancora aperte quando finiscono i dati non si contano.

Uso: python3 -m research.programma6.quarantesima
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from research.programma5.strumenti import motore5 as m5
from research.programma6 import seconda as sc
from research.programma6 import sesta as se
from research.programma6 import terza as te
from research.programma6 import trentaquattresima as tq
from research.programma6.motore import TAKER

QUI = Path(__file__).parent
RIS = QUI / "risultati_quarantesima"
GIORNI_SCELTA, CORR_MIN, N_COPPIE, GIORNI_Z = 180, 0.80, 20, 60
Z_ENTRA, Z_ESCE, Z_ROTTA, MAX_GIORNI, B_MAX = 2.0, 0.5, 4.0, 20, 2.0
QUOTA, MAX_APERTE = 0.05, 20
DA, A = tq.DA, tq.A


def primi_lunedi(da: int, a: int) -> list:
    """I primi lunedi' di ogni mese fra `da` e `a` (giorni dall'epoca)."""
    out, visti = [], set()
    for g in range(da, a + 1):
        if (g + 3) % 7 == 0:
            y, m = sc.data(g)[:7].split("-")
            if (y, m) not in visti:
                visti.add((y, m))
                out.append(g)
    return out


def scegli_coppie(LP: np.ndarray, V: np.ndarray, Ud: np.ndarray, m: int) -> list:
    """Le coppie del mese che parte dal giorno `m` (indice del pannello): (A, B, b, correlazione), dalla piu' correlata."""
    idx = np.flatnonzero(Ud[m])
    fin = LP[m - GIORNI_SCELTA - 1: m][:, idx]
    ok = np.isfinite(fin).all(axis=0)
    idx = idx[ok]
    if len(idx) < 2:
        return []
    lp = LP[m - GIORNI_SCELTA - 1: m][:, idx]
    r = np.diff(lp, axis=0)
    C = np.corrcoef(r.T)
    np.fill_diagonal(C, -np.inf)
    vol = np.nanmedian(V[m - GIORNI_SCELTA: m][:, idx], axis=0)
    cand = {}
    for i in range(len(idx)):
        j = int(np.argmax(C[i]))
        if C[i, j] >= CORR_MIN:
            cand[(min(i, j), max(i, j))] = float(C[i, j])
    scelte, usate = [], set()
    for (i, j), c in sorted(cand.items(), key=lambda kv: -kv[1]):
        if len(scelte) >= N_COPPIE:
            break
        if i in usate or j in usate:
            continue
        a, b_ = (i, j) if vol[i] <= vol[j] else (j, i)
        y, x = lp[1:, a], lp[1:, b_]
        X = np.vstack([np.ones(len(x)), x]).T
        coef, *_ = np.linalg.lstsq(X, y, rcond=None)
        if not coef[1] > 0:
            continue
        usate |= {i, j}
        scelte.append((int(idx[a]), int(idx[b_]), float(coef[1]), c))
    return scelte


def zeta(LP: np.ndarray, a: int, b_: int, beta: float) -> np.ndarray:
    s = pd.Series(LP[:, a] - beta * LP[:, b_])
    prima = s.shift(1).rolling(GIORNI_Z, min_periods=GIORNI_Z)
    return ((s - prima.mean()) / prima.std()).to_numpy()


def operazioni(pan: dict, Ud: np.ndarray) -> tuple:
    """Simulazione giorno per giorno: le operazioni chiuse, le coppie per mese e le operazioni lasciate aperte."""
    sim, t0 = pan["simboli"], pan["t0"]
    O, C, F = pan["open"], pan["close"], pan["funding"]
    with np.errstate(divide="ignore", invalid="ignore"):
        LP = np.log(C)
    T = C.shape[0]
    mesi = [g - t0 for g in primi_lunedi(DA, A)]
    per_mese, coppie_mese, zcache = {}, {}, {}
    for k, m in enumerate(mesi):
        cp = scegli_coppie(LP, pan["quote_volume"], Ud, m)
        fine = mesi[k + 1] if k + 1 < len(mesi) else A - t0 + 1
        coppie_mese[m] = (fine, cp)
        per_mese[sc.data(m + t0)[:7]] = len(cp)
        for a, b_, beta, _ in cp:
            zcache.setdefault((a, b_, beta), zeta(LP, a, b_, beta))
    attive, aperte, righe = [], [], []
    for d in range(mesi[0], T - 1):
        if d in coppie_mese:
            attive = coppie_mese[d]
        restano = []
        for x in aperte:
            z = x["z"][d]
            tenuta = d + 1 - x["e"]
            motivo = None
            if np.isfinite(z) and abs(z) < Z_ESCE:
                motivo = "obiettivo"
            elif np.isfinite(z) and abs(z) > Z_ROTTA:
                motivo = "rottura"
            elif tenuta >= MAX_GIORNI:
                motivo = "tempo"
            a, b_, w, s = x["a"], x["b"], x["w"], x["verso"]
            mancano = not (np.isfinite(O[d + 1, a]) and np.isfinite(O[d + 1, b_]))
            if mancano and np.isfinite(C[d, a]) and np.isfinite(C[d, b_]):
                motivo = "dati mancanti"
            if motivo is None or (mancano and motivo != "dati mancanti"):
                restano.append(x)
                continue
            u = d + 1
            pa, pb = (C[d, a], C[d, b_]) if mancano else (O[u, a], O[u, b_])
            ra = pa / O[x["e"], a] - 1
            rb = pb / O[x["e"], b_] - 1
            costo = 2 * (TAKER + m5.scarto(sim[a])) + w * 2 * (TAKER + m5.scarto(sim[b_]))
            fa, fb = float(F[x["e"]: u, a].sum()), float(F[x["e"]: u, b_].sum())
            r = s * ra - s * w * rb - costo - (s * fa - s * w * fb)
            righe.append({"simbolo": f"{sim[a]}/{sim[b_]}", "data": sc.data(x["e"] + t0), "uscita": sc.data(u + t0),
                          "annuncio": int((x["e"] + t0 + 3) // 7), "verso": s, "r": r, "ore": 24 * (u - x["e"]),
                          "motivo": motivo, "costo": costo, "z_entrata": x["z0"], "correlazione": x["c"], "b": x["beta"]})
        aperte = restano
        if attive and d + t0 <= A:
            fine, cp = attive
            if d < fine:
                for a, b_, beta, c in cp:
                    if len(aperte) >= MAX_APERTE:
                        break
                    if any(x["a"] == a and x["b"] == b_ for x in aperte):
                        continue
                    z = zcache[(a, b_, beta)]
                    if not (np.isfinite(z[d]) and abs(z[d]) > Z_ENTRA and Ud[d, a] and Ud[d, b_]):
                        continue
                    if not (np.isfinite(O[d + 1, a]) and np.isfinite(O[d + 1, b_])):
                        continue
                    aperte.append({"a": a, "b": b_, "beta": beta, "w": min(beta, B_MAX), "c": c, "z": z, "e": d + 1,
                                   "verso": -1 if z[d] > 0 else 1, "z0": float(z[d])})
    return pd.DataFrame(righe), per_mese, len(aperte)


def portafoglio(df: pd.DataFrame) -> pd.DataFrame:
    """La settimana somma le operazioni chiuse (dal lunedi'), il 5% del capitale per la gamba A."""
    usc = np.array([sc.giorno(*map(int, u.split("-"))) for u in df["uscita"]])
    lun = ((usc + 3) // 7) * 7 - 3
    sett = pd.Series(QUOTA * df["r"].to_numpy(), index=lun).groupby(level=0).sum()
    sett_d = pd.Series(QUOTA * (df["r"] - df["costo"]).to_numpy(), index=lun).groupby(level=0).sum()
    tutte = np.arange(DA, A + 7, 7)
    out = pd.DataFrame({"netto": sett.reindex(tutte).fillna(0.0), "netto_doppio": sett_d.reindex(tutte).fillna(0.0)})
    for k in ("lordo", "spese", "funding", "giro", "long", "short"):
        out[k] = 0.0
    out["monete"] = 1
    return out


def prove_fino_alla_trentanovesima() -> list:
    sr = tq.prove_fino_alla_trentatreesima()
    e34 = json.loads((QUI / "risultati_trentaquattresima" / "esame.json").read_text())
    sr += [e34["T1"]["portafoglio"]["intero"]["sharpe"], e34["T2"]["portafoglio"]["intero"]["sharpe"],
           json.loads((QUI / "risultati_trentacinquesima" / "esame.json").read_text())["portafoglio"]["intero"]["sharpe"],
           json.loads((QUI / "risultati_trentaseiesima" / "esame.json").read_text())["T5"]["intero"]["sharpe"],
           json.loads((QUI / "risultati_trentasettesima" / "esame.json").read_text())["portafoglio"]["intero"]["sharpe"],
           json.loads((QUI / "risultati_trentanovesima" / "esame.json").read_text())["portafoglio"]["intero"]["sharpe"]]
    return sr


def esegui(log=print) -> dict:
    pan = sc.pannello()
    ps = te.pannello_settimane(pan, log=lambda x: None, indicatori_si=False)
    _, Ud = tq.rango_funding(pan, ps)
    df, per_mese, lasciate = operazioni(pan, Ud)
    RIS.mkdir(exist_ok=True)
    df.to_csv(RIS / "operazioni_coppie.csv.gz", index=False)
    jb = ps["simboli"].index("BTCUSDT")
    btc = pd.Series(ps["R"][:, jb], index=ps["lunedi"])
    sr = prove_fino_alla_trentanovesima()
    tq.P_SOGLIA = 0.01
    e = {"operazioni": tq.esame_operazioni(df), "numero": int(len(df)), "lasciate_aperte": lasciate,
         "coppie_per_mese": per_mese, "coppie_media_mese": float(np.mean(list(per_mese.values()))),
         "mesi_senza_coppie": int(sum(1 for v in per_mese.values() if v == 0)),
         "costo_medio": float(df["costo"].mean()),
         "entrate_sopra_4": {"numero": int((df["z_entrata"].abs() > Z_ROTTA).sum()),
                             "media": float(df.loc[df["z_entrata"].abs() > Z_ROTTA, "r"].mean())},
         "per_motivo": {k: {"numero": int(len(g)), "media": float(g["r"].mean())} for k, g in df.groupby("motivo")},
         "per_anno_operazioni": {a: float(g["r"].mean()) for a, g in df.groupby(df["data"].str[:4])}}
    e["portafoglio"] = te.esame(portafoglio(df), btc, inizio=DA, anni_pieni=se.ANNI_PIENI)
    sr.append(e["portafoglio"]["intero"]["sharpe"])
    i = e["portafoglio"]["intero"]
    e["portafoglio"]["sharpe_corretto"] = te.sharpe_corretto(i["sharpe"], i["settimane"], i["asimmetria"], i["curtosi"], sr, 52)
    e["portafoglio"]["prove_nel_conto"] = len(sr)
    e["portafoglio"]["esito"] = te.esito(e["portafoglio"], e["portafoglio"]["sharpe_corretto"])
    e["esito"] = "VALIDA" if e["operazioni"]["passa"] and e["portafoglio"]["esito"] == "VALIDA" else "non valida"
    (RIS / "esame.json").write_text(json.dumps(e, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    o, p = e["operazioni"], e["portafoglio"]
    pm = e["per_motivo"]
    testo = "\n".join([
        "# Programma 6 — risultati della quarantesima prova (le coppie di monete che si allontanano)", "",
        "Regole in `QUARANTESIMA.md` (scritte prima); le scelte di calcolo non scritte nelle regole sono in testa a "
        "`quarantesima.py`.", "",
        f"* Coppie: in media {e['coppie_media_mese']:.1f} al mese ({e['mesi_senza_coppie']} mesi senza coppie su {len(per_mese)}).",
        f"* {e['numero']} operazioni chiuse ({lasciate} ancora aperte alla fine dei dati, non contate); costi medi "
        f"{100 * e['costo_medio']:.2f}% a operazione (sulla gamba A).",
        f"* Media netta {100 * o['boot']['media']:+.3f}% a operazione (intervallo {100 * o['boot']['basso']:+.3f}; "
        f"{100 * o['boot']['alto']:+.3f}, p {o['boot']['p']:.4f}); vinte {100 * o['vinte']:.0f}%; tenuta media "
        f"{o['ore_medie'] / 24:.1f} giorni.",
        "* Uscite: " + ", ".join(f"{k} {v['numero']} (media {100 * v['media']:+.2f}%)" for k, v in pm.items()) + ".",
        f"* Entrate con |z| già sopra 4: {e['entrate_sopra_4']['numero']} (media {100 * e['entrate_sopra_4']['media']:+.2f}%).",
        f"* Metà: {100 * o['prima_meta']:+.3f}%, {100 * o['seconda_meta']:+.3f}%; senza le 5 migliori "
        f"{100 * o['senza_5_migliori']:+.3f}%.",
        "* Per anno d'entrata: " + ", ".join(f"{a} {100 * v:+.2f}%" for a, v in e["per_anno_operazioni"].items()) + ".",
        f"* Portafoglio: Sharpe {p['intero']['sharpe']:.2f}, {100 * p['intero']['annuo']:+.1f}% l'anno, discesa "
        f"{100 * p['intero']['discesa_max']:.1f}%; Sharpe corretto {p['sharpe_corretto']:.2f} con {len(sr)} prove; "
        f"esito del portafoglio: {p['esito']}.",
        "* Portafoglio per anno: " + ", ".join(f"{a} {100 * v:+.1f}%" for a, v in p["per_anno"].items()) + ".", "",
        f"**Esito: {e['esito']}**"]) + "\n"
    (QUI / "RISULTATI_QUARANTESIMA.md").write_text(testo, encoding="utf-8")
    log(testo)
    return e


if __name__ == "__main__":
    esegui(log=lambda x: print(x, flush=True))
    print("QUARANTESIMA FINITA", flush=True)
