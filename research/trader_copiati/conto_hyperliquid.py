"""Il conto della copia dei trader migliori di Hyperliquid (HYPERLIQUID.md, sezione 2), dalle posizioni raccolte in `hyperliquid/`.

A ogni giro della raccolta (ogni 4 ore) il portafoglio copiato è la media dei 20 conti della settimana del peso di ogni moneta (valore
della posizione con il segno diviso il valore del conto), abbinato ai perpetui di Binance e scalato a un'esposizione totale non oltre 2.
I pesi entrano all'apertura dell'ora dopo il giro e si tengono fino all'entrata del giro dopo, sui prezzi orari di Binance (file
giornalieri dell'archivio pubblico, che escono il giorno dopo), con il costo a mercato sui cambi di peso e il funding di Binance.

Uso: python3 -m research.trader_copiati.conto_hyperliquid
"""
from __future__ import annotations

import gzip
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import numpy as np
import pandas as pd

QUI = Path(__file__).parent
ARCHIVIO = QUI / "hyperliquid"
ESPOSIZIONE_MAX = 2.0


def simbolo_binance(moneta: str, simboli: set) -> str | None:
    if moneta.startswith("k") and moneta[1:].isupper():
        cand = (f"1000{moneta[1:]}USDT",)
    else:
        cand = (f"{moneta}USDT", f"1000{moneta}USDT")
    return next((s for s in cand if s in simboli), None)


def giri(simboli: set) -> pd.DataFrame:
    """Una riga per giro: l'ora del giro, i pesi copiati (scalati) e la leva media dei conti prima di scalare."""
    scelti = {}
    for f in sorted(ARCHIVIO.glob("scelti_*.json")):
        scelti[f.stem.split("_", 1)[1]] = {c["indirizzo"] for c in json.loads(f.read_text())["conti"]}
    righe: dict = {}
    for f in sorted(ARCHIVIO.glob("posizioni_*.jsonl.gz")):
        for linea in gzip.open(f, "rt", encoding="utf-8"):
            r = json.loads(linea)
            righe.setdefault(r["ora"], []).append(r)
    out = []
    for ora, conti in sorted(righe.items()):
        t = datetime.strptime(ora, "%Y-%m-%d %H:%M").replace(tzinfo=timezone.utc)
        lun = (t - timedelta(days=t.weekday())).strftime("%Y-%m-%d")
        ammessi = scelti.get(lun) or scelti.get(max(k for k in scelti if k <= lun), set())
        pesi: dict = {}
        leve = []
        n = 0
        for r in conti:
            if r["indirizzo"] not in ammessi or not r.get("conto"):
                continue
            n += 1
            lordo = 0.0
            for p in r["posizioni"]:
                w = (1 if p["quantita"] > 0 else -1) * float(p["valore"]) / float(r["conto"])
                lordo += abs(w)
                s = simbolo_binance(p["moneta"], simboli)
                if s:
                    pesi[s] = pesi.get(s, 0.0) + w
            leve.append(lordo)
        if not n:
            continue
        pesi = {s: w / n for s, w in pesi.items() if abs(w) > 1e-12}
        g = sum(abs(w) for w in pesi.values())
        if g > ESPOSIZIONE_MAX:
            pesi = {s: w * ESPOSIZIONE_MAX / g for s, w in pesi.items()}
        out.append({"ora": t, "entrata": int(t.timestamp() // 3600) + 1, "pesi": pesi, "conti": n,
                    "leva_media_conti": float(np.mean(leve)) if leve else 0.0, "esposizione": min(g, ESPOSIZIONE_MAX)})
    return pd.DataFrame(out)


def scarica_giorni(simbolo: str, dal: datetime, al: datetime) -> None:
    from research.programma6 import quarta as qa
    from research.programma6 import scarico_giorni as sg
    g = dal
    while g <= al:
        d = g.strftime("%Y-%m-%d")
        try:
            sg._scarica(f"data/futures/um/daily/klines/{simbolo}/1h/{simbolo}-1h-{d}.zip", qa.DATI / simbolo / "ore")
        except Exception:  # noqa: BLE001
            pass
        g += timedelta(days=1)


def esegui(log=print) -> dict:
    from research.programma6 import esecuzione as es
    from research.programma6 import seconda as sc
    pan = sc.pannello()
    simboli = set(pan["simboli"])
    gg = giri(simboli)
    if gg.empty:
        log("[copia] nessun giro raccolto")
        return {}
    usati = sorted({s for p in gg["pesi"] for s in p})
    dal, al = gg["ora"].min(), datetime.now(timezone.utc) - timedelta(days=1)
    for s in usati:
        scarica_giorni(s, dal, al)
    ore = {s: es.ore_di(s) for s in usati}
    costo = dict(zip(pan["simboli"], sc.costi_moneta(pan["simboli"])))
    F = pan["funding"]
    t0 = pan["t0"]
    jj = {s: i for i, s in enumerate(pan["simboli"])}
    righe, prima = [], {}
    for k in range(len(gg) - 1):
        h1, h2, pesi = int(gg["entrata"].iloc[k]), int(gg["entrata"].iloc[k + 1]), gg["pesi"].iloc[k]
        lordo, manca = 0.0, False
        for s, w in pesi.items():
            o = ore[s]
            if h1 not in o.index or h2 not in o.index or not np.isfinite(o.loc[[h1, h2], "open"]).all():
                manca = True
                break
            lordo += w * (o.loc[h2, "open"] / o.loc[h1, "open"] - 1)
        if manca:
            break                                   # i prezzi di questo tratto non sono ancora nell'archivio
        spese = sum(abs(pesi.get(s, 0.0) - prima.get(s, 0.0)) * costo.get(s, 0.001) for s in set(pesi) | set(prima))
        fund = 0.0
        for s, w in pesi.items():
            for h in range(h1, h2):
                d = h // 24 - t0
                if 0 <= d < F.shape[0] and np.isfinite(F[d, jj[s]]):
                    fund += w * F[d, jj[s]] / 24
        righe.append({"dal": sc.data(h1 // 24) + f" {h1 % 24:02d}:00", "ore": h2 - h1, "lordo": lordo, "spese": spese, "funding": fund,
                      "netto": lordo - spese - fund, "esposizione": gg["esposizione"].iloc[k], "leva_media_conti": gg["leva_media_conti"].iloc[k]})
        prima = pesi
    d = pd.DataFrame(righe)
    out = {"giri_raccolti": int(len(gg)), "tratti_con_i_prezzi": int(len(d))}
    if len(d):
        out.update({"rendimento": float((1 + d["netto"]).prod() - 1), "lordo": float(d["lordo"].sum()), "spese": float(d["spese"].sum()),
                    "funding": float(d["funding"].sum()), "ore": int(d["ore"].sum()), "esposizione_media": float(d["esposizione"].mean()),
                    "leva_media_dei_conti": float(d["leva_media_conti"].mean())})
    (QUI / "hyperliquid_conto.json").write_text(json.dumps({**out, "tratti": righe}, ensure_ascii=False, indent=1, default=str))
    pc = lambda v: f"{100 * v:+.2f}%"  # noqa: E731
    testo = ["# La copia dei trader migliori di Hyperliquid: il conto in avanti", "",
             "Regole in `HYPERLIQUID.md`. Solo informazione: non entra nel bot (soldi finti a tavolino).", "",
             f"* Giri raccolti {out['giri_raccolti']}, tratti con i prezzi di Binance già pubblicati {out['tratti_con_i_prezzi']}."]
    if len(d):
        testo += [f"* **Dal {righe[0]['dal']} UTC, {out['ore']} ore: {pc(out['rendimento'])}** (prezzo {pc(out['lordo'])}, spese "
                  f"{pc(-out['spese'])}, funding {pc(-out['funding'])}); esposizione media {out['esposizione_media']:.2f}; leva media dei 20 conti "
                  f"prima di scalare {out['leva_media_dei_conti']:.2f}."]
    (QUI / "HYPERLIQUID_CONTO.md").write_text("\n".join(testo) + "\n", encoding="utf-8")
    log("\n".join(testo))
    return out


if __name__ == "__main__":
    esegui()
