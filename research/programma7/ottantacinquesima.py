"""Programma 7, ottantacinquesima prova (OTTANTACINQUESIMA.md): GA2C, GA2 al contrario (prova 138) confermata sull'archivio katelabs
(titoli di febbraio-aprile 2026, mai usati): long il quinto più citato rispetto al volume, short il meno citato, a settimana come F5.

Uso: python3 -m research.programma7.ottantacinquesima
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from research.programma6 import annunci as an
from research.programma6 import ottava as ot
from research.programma6 import seconda as sc
from research.programma6 import terza as te
from research.programma6 import ventiquattresima as vq

QUI = Path(__file__).parent
RIS = QUI / "risultati_ottantacinquesima"
FILE = QUI.parent / "data" / "notizie_katelabs" / "headlines_2026-02_2026-04.parquet"
DAL, AL = sc.giorno(2026, 3, 9), sc.giorno(2026, 4, 27)
INIZIO_ARCHIVIO = sc.giorno(2026, 2, 1)
RITARDO, RECENTE, MINIMO = 2, 28, 3


def titoli(pan: dict) -> tuple:
    d = pd.read_parquet(FILE, columns=["ingested_at", "coins"])
    g = (pd.to_datetime(d["ingested_at"], utc=True).astype("int64") // 86_400_000_000_000).astype(int).to_numpy()
    T, S = pan["close"].shape
    t0, simboli = pan["t0"], list(pan["simboli"])
    A = np.zeros((T, S))
    mappa: dict = {}
    for gi, cs in zip(g, d["coins"].to_numpy()):
        k = gi - t0
        if not 0 <= k < T or cs is None:
            continue
        for x in set(str(c).upper() for c in cs):
            if x not in mappa:
                mappa[x] = an.perpetuo(x, simboli)
            if mappa[x]:
                A[k, simboli.index(mappa[x])] += 1
    return A, {k: v for k, v in mappa.items() if v}, len(d)


def esegui(log=print) -> dict:
    pan = sc.pannello()
    ps = te.pannello_settimane(pan, log=lambda x: None, indicatori_si=False)
    A, mappa, n = titoli(pan)
    lun = ps["lunedi"]
    idx = lun - pan["t0"]
    Ac = np.vstack([np.zeros((1, A.shape[1])), np.cumsum(A, axis=0)])
    V = np.nan_to_num(pan["quote_volume"])
    Vc = np.vstack([np.zeros((1, V.shape[1])), np.cumsum(V, axis=0)])
    fine = idx - RITARDO + 1
    a_rec = Ac[fine] - Ac[fine - RECENTE]
    inizio_arch = np.maximum(fine - 112, INIZIO_ARCHIVIO - pan["t0"])
    a_tutti = Ac[fine] - Ac[np.clip(inizio_arch, 0, None)]
    v_rec = Vc[fine] - Vc[fine - RECENTE]
    with np.errstate(all="ignore"):
        ga2 = np.log((a_rec + 1) / v_rec)
    dentro = (lun >= DAL) & (lun <= AL)
    ga2 = np.where(dentro[:, None] & (a_tutti >= MINIMO) & (v_rec > 0) & np.isfinite(ga2), ga2, np.nan)
    sig = ot.sigma_30(pan, idx)
    costo = sc.costi_moneta(pan["simboli"])
    U = ps["U"] & dentro[:, None]
    g1 = pd.read_csv(QUI / "risultati_ottantesima" / "settimane_G1.csv.gz", index_col=0)
    out = {"titoli": n, "sigle_abbinate": len(mappa)}
    RIS.mkdir(exist_ok=True)
    for nome, verso in (("GA2C", +1.0), ("GA2 com'era scritta", -1.0)):
        W = vq.pesi_banda(np.where(np.isfinite(sig) & U, verso * ga2, np.nan), U, sig)
        df = te.conto(W, ps["R"], ps["F"], costo)
        df.index = lun
        df = df[(df.index >= DAL) & (df.index <= AL)]
        df.to_csv(RIS / f"settimane_{'GA2C' if verso > 0 else 'GA2'}.csv.gz")
        c = df.index.intersection(g1.index)
        out[nome] = {"settimane": int(len(df)), "settimane_con_posizioni": int((df["giro"] > 0).sum() if "giro" in df else 0),
                     "media_settimana": float(df["netto"].mean()), "positive": int((df["netto"] > 0).sum()),
                     "somma": float(df["netto"].sum()), "lordo_medio": float(df["lordo"].mean()),
                     "per_settimana": {sc.data(int(k)): round(float(v), 5) for k, v in df["netto"].items()},
                     "G1_media_stesse_settimane": float(g1.loc[c, "netto"].mean()) if len(c) else None, "settimane_G1": int(len(c))}
    valide = (np.isfinite(ga2) & U)[dentro]
    out["monete_con_segnale"] = [int(x) for x in valide.sum(axis=1)]
    e = out["GA2C"]
    conferma = bool(e["media_settimana"] > 0 and e["G1_media_stesse_settimane"] is not None and e["media_settimana"] > e["G1_media_stesse_settimane"])
    out["esito"] = "conferma" if conferma else "non conferma"
    (RIS / "esame.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    pc = lambda v: "—" if v is None or v != v else f"{100 * v:+.2f}%"  # noqa: E731
    righe = ["# Programma 7 — risultati dell'ottantacinquesima prova (GA2C: le notizie, conferma sul 2026)", "",
             "Regole in `OTTANTACINQUESIMA.md` (scritte prima). Archivio katelabs, titoli dal 1° febbraio al 30 aprile 2026; i lunedì dal 9 marzo "
             "al 27 aprile 2026, come F5.", "",
             f"* Titoli {n}, sigle abbinate a un perpetuo {len(mappa)}; monete con il segnale per settimana: {out['monete_con_segnale']}."]
    for nome in ("GA2C", "GA2 com'era scritta"):
        x = out[nome]
        righe.append(f"* **{nome}**: {x['settimane']} settimane, **{pc(x['media_settimana'])} a settimana** dopo i costi (lordo "
                     f"{pc(x['lordo_medio'])}), positive {x['positive']} su {x['settimane']}, in tutto {pc(x['somma'])}; G1 nelle stesse "
                     f"settimane {pc(x['G1_media_stesse_settimane'])} a settimana ({x['settimane_G1']} settimane). Settimana per settimana: "
                     + ", ".join(f"{k} {pc(v)}" for k, v in x["per_settimana"].items()) + ".")
    righe += ["", f"**Esito: {out['esito']}** (la regola: media dopo i costi sopra zero e sopra G1 nelle stesse settimane)."]
    testo = "\n".join(righe) + "\n"
    (QUI / "RISULTATI_OTTANTACINQUESIMA.md").write_text(testo, encoding="utf-8")
    log(testo)
    return out


if __name__ == "__main__":
    esegui(log=lambda x: print(x, flush=True))
    print("OTTANTACINQUESIMA FINITA", flush=True)
