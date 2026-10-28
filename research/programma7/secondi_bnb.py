"""Misura descrittiva per l'idea 84 (non una prova, non entra nel conto): in quanti secondi si muove il BNB dopo gli annunci di
Launchpool e Megadrop. Per ogni annuncio della prova 115 (stesso elenco) si leggono gli scambi del perpetuo del BNB (aggTrades,
archivio pubblico di Binance) e si misura il prezzo a -60, -10, -5, 0, +1, +2, +5, +10, +20, +30, +60, +120 e +300 secondi
dalla pubblicazione, rispetto all'ultimo scambio prima della pubblicazione. Il Bitcoin non si toglie: in 5 minuti si muove
poco rispetto al +0,9% del BNB, e i suoi file sono 30-50 volte piu' grandi.

Uso: python3 -m research.programma7.secondi_bnb CARTELLA_TEMPORANEA
"""
from __future__ import annotations

import io
import json
import sys
import urllib.request
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd

from research.programma6 import seconda as sc
from research.programma7 import cinquantatreesima as bl

QUI = Path(__file__).parent
URL = "https://data.binance.vision/data/futures/um/daily/aggTrades/BNBUSDT/BNBUSDT-aggTrades-{d}.zip"
SECONDI = (-60, -10, -5, 0, 1, 2, 5, 10, 20, 30, 60, 120, 300)


def scambi(giorno: str, cartella: Path) -> pd.DataFrame:
    f = cartella / f"bnb_{giorno}.pkl"
    if f.exists():
        return pd.read_pickle(f)
    b = urllib.request.urlopen(urllib.request.Request(URL.format(d=giorno), headers={"User-Agent": "ricerca/1.0"}), timeout=120).read()
    z = zipfile.ZipFile(io.BytesIO(b))
    df = pd.read_csv(z.open(z.namelist()[0]), header=None)
    if not str(df.iloc[0, 0]).isdigit():
        df = df.iloc[1:]
    out = pd.DataFrame({"ms": pd.to_numeric(df[5]).astype("int64"), "prezzo": pd.to_numeric(df[1]).astype(float)}).sort_values("ms")
    out.to_pickle(f)
    return out


def main(cartella: str) -> None:
    c = Path(cartella)
    c.mkdir(parents=True, exist_ok=True)
    righe = []
    for x in json.loads(bl.QUOTAZIONI.read_text(encoding="utf-8")):
        if not bl.EVENTO.search(x["titolo"]) or "Launchpad" in x["titolo"]:
            continue
        t0 = int(x["ms"])
        giorni = sorted({sc.data((t0 + s * 1000) // 86_400_000) for s in (SECONDI[0], SECONDI[-1])})
        try:
            d = pd.concat([scambi(g, c) for g in giorni])
        except Exception as e:  # noqa: BLE001
            print("salto", x["titolo"][:50], e, flush=True)
            continue
        ms, p = d["ms"].to_numpy(), d["prezzo"].to_numpy()
        i0 = np.searchsorted(ms, t0, side="left") - 1           # l'ultimo scambio prima della pubblicazione
        if i0 < 0:
            continue
        base = p[i0]
        riga = {"data": sc.data(t0 // 86_400_000), "titolo": x["titolo"][:70]}
        for s in SECONDI:
            i = np.searchsorted(ms, t0 + s * 1000, side="right") - 1
            riga[f"s{s}"] = float(p[i] / base - 1) if i >= 0 else np.nan
        righe.append(riga)
        print(riga["data"], f"{100 * riga['s300']:+.2f}% a 5 minuti", flush=True)
    df = pd.DataFrame(righe)
    df.to_csv(QUI / "risultati_secondi_bnb.csv", index=False)
    med, media = df[[f"s{s}" for s in SECONDI]].median(), df[[f"s{s}" for s in SECONDI]].mean()
    quota = media / media["s300"] if media["s300"] else media * np.nan
    testo = "\n".join([
        "# In quanti secondi si muove il BNB dopo gli annunci di Launchpool e Megadrop (misura descrittiva, idea 84)", "",
        f"Script `secondi_bnb.py`, {len(df)} annunci della prova 115, scambi del perpetuo del BNB (archivio pubblico di Binance), prezzo "
        "rispetto all'ultimo scambio prima della pubblicazione. Non è una prova: non entra nel conto.", "",
        "| Secondi dalla pubblicazione | Media | Mediana | Quota del movimento dei 5 minuti (media) |", "|---|---|---|---|"] +
        [f"| {s:+d} | {100 * media[f's{s}']:+.3f}% | {100 * med[f's{s}']:+.3f}% | {100 * quota[f's{s}']:.0f}% |" for s in SECONDI]) + "\n"
    (QUI / "SECONDI_BNB.md").write_text(testo, encoding="utf-8")
    print(testo, flush=True)


if __name__ == "__main__":
    main(sys.argv[1])
    print("SECONDI FINITA", flush=True)
