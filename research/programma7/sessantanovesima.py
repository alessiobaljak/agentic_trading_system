"""Programma 7, sessantanovesima prova (SESSANTANOVESIMA.md): DI, la diluizione a settimana come F5. DA: short il quinto con la crescita
piu' alta dell'offerta in circolazione nelle 12 settimane, long il piu' basso; DB: lo stesso con l'offerta che resta da sbloccare (finale
diviso in circolazione). Calendari di DefiLlama (gli stessi della prova 74).

Uso: python3 -m research.programma7.sessantanovesima
"""
from __future__ import annotations

import gzip
import json
from pathlib import Path

import numpy as np
import pandas as pd

from research.programma6 import annunci as an
from research.programma6 import asticella as ast
from research.programma6 import ottava as ot
from research.programma6 import seconda as sc
from research.programma6 import sesta as se
from research.programma6 import terza as te
from research.programma6 import ventiquattresima as vq
from research.programma7 import diciassettesima as dc

QUI = Path(__file__).parent
RIS = QUI / "risultati_sessantanovesima"
PREZZI_CACHE = dc.DATI / "prezzi_controllo_DI.json"
FINE = sc.giorno(2026, 10, 1)
RITARDO, FINESTRA, ETA_MIN, TOLLERANZA, MESCOLATE, SEME = 2, 84, 37, 0.20, 20, 2026


def segnali(pan: dict, ps: dict, dati: list, log=print) -> tuple:
    simboli, t0 = pan["simboli"], pan["t0"]
    lun = ps["lunedi"]
    W, S = len(lun), len(simboli)
    DA, DB = np.full((W, S), np.nan), np.full((W, S), np.nan)
    conti = {"calendari": len(dati), "senza_sigla": 0, "senza_perpetuo": 0, "doppioni": 0, "prezzo_diverso": 0, "senza_settimane": 0,
             "monete_usate": 0}
    cache = json.loads(PREZZI_CACHE.read_text()) if PREZZI_CACHE.exists() else {}
    visti, controlli = set(), []
    for x in dati:
        if "errore" in x or not x.get("circolante"):
            continue
        if not x.get("sigla"):
            conti["senza_sigla"] += 1
            continue
        s = an.perpetuo(x["sigla"].upper(), simboli)
        if not s or s == "BTCUSDT":
            conti["senza_perpetuo"] += 1
            continue
        if s in visti:
            conti["doppioni"] += 1
            continue
        visti.add(s)
        j = simboli.index(s)
        c = pd.Series(dict((int(g), float(v)) for g, v in x["circolante"])).sort_index()
        c = c.reindex(np.arange(c.index.min(), c.index.max() + 1)).ffill()
        finale = float(c.max())
        a = c.reindex(lun - RITARDO).to_numpy()
        b = c.reindex(lun - RITARDO - FINESTRA).to_numpy()
        with np.errstate(all="ignore"):
            da = np.where((b > 0) & np.isfinite(a), a / b - 1, np.nan)
            db = np.where(a > 0, finale / a, np.nan)
        ok = ps["U"][:, j] & (np.isfinite(da) | np.isfinite(db))
        if not ok.any():
            conti["senza_settimane"] += 1
            continue
        g_c = int(lun[np.flatnonzero(ok)[0]])
        chiave = f"{g_c}:{x['token']}"
        if chiave not in cache:
            try:
                r = dc._get(dc.PREZZI.format(f"historical/{g_c * 86_400 + 3_600}/{x['token']}"))
                cache[chiave] = float(next(iter((r.get("coins") or {}).values()))["price"])
            except Exception:  # noqa: BLE001
                cache[chiave] = float("nan")
        pz = cache[chiave]
        rapporto = pan["open"][g_c - t0, j] / dc.prefisso(s, x["sigla"].upper()) / pz if pz and pz > 0 else float("nan")
        controlli.append({"protocollo": x["protocollo"], "sigla": x["sigla"], "perpetuo": s, "giorno": sc.data(g_c), "rapporto": rapporto})
        if not abs(rapporto - 1) <= TOLLERANZA:
            conti["prezzo_diverso"] += 1
            continue
        conti["monete_usate"] += 1
        DA[:, j], DB[:, j] = da, db
    PREZZI_CACHE.write_text(json.dumps(cache))
    return DA, DB, conti, pd.DataFrame(controlli)


def esegui(log=print) -> dict:
    pan = sc.pannello()
    ps = te.pannello_settimane(pan, log=lambda x: None, indicatori_si=False)
    assert ps["simboli"] == pan["simboli"]
    dati = json.load(gzip.open(dc.FILE))
    DA, DB, conti, controlli = segnali(pan, ps, dati, log)
    log(f"[sessantanovesima] {conti}")
    lun = ps["lunedi"]
    idx = lun - pan["t0"]
    ok = np.isfinite(pan["close"])
    primo = np.where(ok.any(axis=0), ok.argmax(axis=0), 10 ** 9) + pan["t0"]
    eta = lun[:, None] - primo[None, :]
    Uv = ps["U"] & (eta >= ETA_MIN) & (lun[:, None] < FINE)
    sig = ot.sigma_30(pan, idx)
    costo = sc.costi_moneta(pan["simboli"])
    btc = pd.Series(ps["R"][:, ps["simboli"].index("BTCUSDT")], index=lun)
    tieni = (lun >= se.INIZIO) & (lun < FINE)
    out, serie, Wd = {}, {}, {}
    for nome, D in (("DA", DA), ("DB", DB)):
        ct = np.where(np.isfinite(sig), -D, np.nan)
        W = vq.pesi_banda(ct, Uv, sig)
        df = te.conto(W, ps["R"], ps["F"], costo)
        df.index = lun
        df = df[df.index < FINE]
        RIS.mkdir(exist_ok=True)
        df.to_csv(RIS / f"settimane_{nome}.csv.gz")
        out[nome] = te.esame(df, btc, inizio=se.INIZIO, anni_pieni=se.ANNI_PIENI)
        serie[nome], Wd[nome] = df, W
    rivisto = ast.corretto_rivisto({**ast.serie_nuove(), "131 DA": serie["DA"]["netto"], "131 DB": serie["DB"]["netto"]},
                                   {"131 DA": out["DA"]["intero"], "131 DB": out["DB"]["intero"]})
    f5 = pd.read_csv(QUI.parent / "programma6" / "risultati_controllo_parita" / "settimane_F5.csv.gz", index_col=0)
    rng = np.random.default_rng(SEME)
    for nome, D in (("DA", DA), ("DB", DB)):
        e = out[nome]
        r = rivisto["candidate"][f"131 {nome}"]
        e["sharpe_corretto"], e["t"], e["gruppi"] = r["corretto_con_aggiunta"], r["t"], rivisto["gruppi"]
        e["esito"] = te.esito(e, e["sharpe_corretto"])
        anni = e.get("per_anno", {})
        e["regola_proprietario"] = bool(e["sharpe_corretto"] >= 0.90 and e["t"] > 3 and anni and all(v > 0 for v in anni.values()))
        c = serie[nome].index.intersection(f5.index)
        e["correlazione_F5"] = float(np.corrcoef(serie[nome].loc[c, "netto"], f5.loc[c, "netto"])[0, 1])
        valide = (np.isfinite(D) & Uv)[tieni]
        e["monete_con_segnale_mediana"] = float(np.median(valide.sum(axis=1)))
        e["settimane_con_posizioni"] = int((np.abs(Wd[nome][tieni]).sum(axis=1) > 0).sum())
        e["settimane"] = int(tieni.sum())
        # il segnale mescolato fra le monete della stessa settimana
        sh = []
        for _ in range(MESCOLATE):
            M = np.full_like(D, np.nan)
            for k in range(D.shape[0]):
                jj = np.flatnonzero(np.isfinite(D[k]) & Uv[k])
                if len(jj):
                    M[k, jj] = rng.permutation(D[k, jj])
            Wm = vq.pesi_banda(np.where(np.isfinite(sig), -M, np.nan), Uv, sig)
            dm = te.conto(Wm, ps["R"], ps["F"], costo)
            dm.index = lun
            dm = dm[(dm.index >= se.INIZIO) & (dm.index < FINE)]
            sh.append(te.numeri_settimana(dm["netto"])["sharpe"])
        e["mescolato_sharpe_medio"] = float(np.mean(sh))
        e["mescolato_sopra"] = int(sum(1 for v in sh if v >= e["intero"]["sharpe"]))
        # per capire: monete giovani (perpetuo da meno di un anno) contro le altre, lordo della settimana dopo, quinto alto meno basso
        g, v = [], []
        for k in np.flatnonzero(tieni):
            jj = np.flatnonzero(np.isfinite(D[k]) & Uv[k])
            for gruppo, lista in (("giovani", g), ("vecchie", v)):
                sel = jj[(eta[k, jj] < 365) if gruppo == "giovani" else (eta[k, jj] >= 365)]
                if len(sel) >= 10:
                    q = pd.Series(D[k, sel]).rank(pct=True).to_numpy()
                    lista.append(float(np.nanmean(ps["R"][k, sel[q <= 0.2]]) - np.nanmean(ps["R"][k, sel[q > 0.8]])))
        e["giovani_basso_meno_alto"] = {"settimane": len(g), "media": float(np.mean(g)) if g else None}
        e["vecchie_basso_meno_alto"] = {"settimane": len(v), "media": float(np.mean(v)) if v else None}
    controlli.to_csv(RIS / "controllo_prezzi.csv", index=False)
    (RIS / "esame.json").write_text(json.dumps({"conti": conti, **out}, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    pc = lambda x: "—" if x is None or x != x else f"{100 * x:+.1f}%"  # noqa: E731
    righe = ["# Programma 7 — risultati della sessantanovesima prova (DI: la diluizione, a settimana)", "",
             "Regole in `SESSANTANOVESIMA.md` (scritte prima). Dal 4 gennaio 2021 a fine settembre 2026, calendari di DefiLlama, come F5.", "",
             "* **I calendari**: " + ", ".join(f"{k} {v}" for k, v in conti.items()) + "."]
    for nome, titolo in (("DA", "la crescita dell'offerta in 12 settimane"), ("DB", "l'offerta che resta da sbloccare")):
        e = out[nome]
        i = e["intero"]
        righe += [
            f"* **{nome} ({titolo}): Sharpe {i['sharpe']:.2f}**, {pc(i['annuo'])} l'anno, volatilità {100 * i['volatilita']:.1f}%, discesa "
            f"{100 * i['discesa_max']:.1f}%; spese {100 * e['spese_annue']:.1f}% l'anno; lato long {pc(e['long_annuo'])}, short "
            f"{pc(e['short_annuo'])} l'anno.",
            "  * Per anno: " + ", ".join(f"{a} {pc(x)}" for a, x in e["per_anno"].items()) + ".",
            f"  * Monete con il segnale, mediana {e['monete_con_segnale_mediana']:.0f} a settimana; settimane con le posizioni "
            f"{e['settimane_con_posizioni']} su {e['settimane']}.",
            f"  * Il segnale mescolato: Sharpe medio {e['mescolato_sharpe_medio']:.2f}, {e['mescolato_sopra']} su {MESCOLATE} sopra quello vero; "
            f"correlazione con F5 {e['correlazione_F5']:.2f}.",
            f"  * Lordo della settimana dopo, il quinto che diluisce meno meno il quinto che diluisce di più: monete giovani "
            f"{pc(e['giovani_basso_meno_alto']['media'])} ({e['giovani_basso_meno_alto']['settimane']} settimane), le altre "
            f"{pc(e['vecchie_basso_meno_alto']['media'])} ({e['vecchie_basso_meno_alto']['settimane']}).",
            f"  * Sharpe corretto con l'aggiunta {e['sharpe_corretto']:.2f} ({e['gruppi']} gruppi); t {e['t']:.2f}; regola del proprietario: "
            f"{'sì' if e['regola_proprietario'] else 'no'}. **Esito: {e['esito']}**."]
    testo = "\n".join(righe) + "\n"
    (QUI / "RISULTATI_SESSANTANOVESIMA.md").write_text(testo, encoding="utf-8")
    log(testo)
    return out


if __name__ == "__main__":
    esegui(log=lambda x: print(x, flush=True))
    print("SESSANTANOVESIMA FINITA", flush=True)
