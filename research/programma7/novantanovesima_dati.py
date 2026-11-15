"""Prova 161 (NOVANTANOVESIMA.md): scarico delle candele orarie del prezzo mark e del prezzo scambiato del perpetuo di BTCUSDT ed
ETHUSDT (mesi 2021-01 .. 2026-10) dall'archivio pubblico di Binance, con impronte e conto dei buchi. Non calcola nessun rendimento.
Il codice della 157 e i caricatori non si toccano.

Uso: python3 -m research.programma7.novantanovesima_dati
"""
from __future__ import annotations

import hashlib
import io
import json
import urllib.request
import zipfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np
import pandas as pd

QUI = Path(__file__).parent
RIS = QUI / "risultati_novantanovesima"
DATI = QUI.parent / "data" / "mark_1h"           # research/data e' ignorato da git
MONETE = ("BTCUSDT", "ETHUSDT")
MESI = [f"{a}-{m:02d}" for a in range(2021, 2027) for m in range(1, 13) if "2021-01" <= f"{a}-{m:02d}" <= "2026-10"]
URL = {"mark1h": "https://data.binance.vision/data/futures/um/monthly/markPriceKlines/{s}/1h/{s}-1h-{m}.zip",
       "perp1h": "https://data.binance.vision/data/futures/um/monthly/klines/{s}/1h/{s}-1h-{m}.zip"}
# dal 3 gennaio 2021 00:00 UTC (giorno prima dell'inizio: serve l'apertura) al 6 ottobre 2026 00:00 UTC escluso
MS_DA = 1609632000000
MS_A = 1791244800000


def uno(x):
    k, s, m = x
    f = DATI / k / f"{s}-{m}.zip"
    if f.exists() and f.stat().st_size > 0:
        return x, "ok"
    f.parent.mkdir(parents=True, exist_ok=True)
    try:
        with urllib.request.urlopen(URL[k].format(s=s, m=m), timeout=90) as r:
            f.write_bytes(r.read())
        return x, "ok"
    except Exception as e:  # noqa: BLE001
        return x, repr(e)[:90]


def leggi(f: Path) -> pd.DataFrame:
    with zipfile.ZipFile(f) as z:
        g = z.read(z.namelist()[0])
    d = pd.read_csv(io.BytesIO(g), header=0 if g[:1].isalpha() else None).iloc[:, :6]
    d.columns = ["t", "open", "high", "low", "close", "volume"]
    t = pd.to_numeric(d["t"])
    d["t"] = t.where(t < 10 ** 14, t // 1000)
    return d


def main() -> None:
    lavori = [(k, s, m) for k in URL for s in MONETE for m in MESI]
    with ThreadPoolExecutor(max_workers=8) as ex:
        esiti = list(ex.map(uno, lavori))
    ko = [(x, e) for x, e in esiti if e != "ok"]
    RIS.mkdir(exist_ok=True)
    out = {"file": len(esiti), "errori": ko[:10], "n_errori": len(ko), "impronte": {}, "buchi": {}}
    attese = (MS_A - MS_DA) // 3_600_000
    for k in URL:
        for s in MONETE:
            fs = sorted((DATI / k).glob(f"{s}-*.zip"))
            h = hashlib.sha256()
            for f in fs:
                h.update(f.name.encode() + f.read_bytes())
            out["impronte"][f"{k}_{s}"] = {"file": len(fs), "sha256_unico": h.hexdigest(),
                                           "byte": int(sum(f.stat().st_size for f in fs))}
            d = pd.concat([leggi(f) for f in fs], ignore_index=True)
            ore = (d["t"] // 3_600_000).to_numpy()
            d = d[(d["t"] >= MS_DA) & (d["t"] < MS_A)]
            ore = np.unique((d["t"] // 3_600_000).to_numpy())
            tutte = np.arange(MS_DA // 3_600_000, MS_A // 3_600_000)
            manc = np.setdiff1d(tutte, ore)
            giorni = sorted({pd.Timestamp(int(x) * 3600, unit="s").strftime("%Y-%m-%d") for x in manc})
            out["buchi"][f"{k}_{s}"] = {"ore_attese": int(attese), "ore_presenti": int(len(ore)), "duplicati": int(len(d) - len(ore)),
                                        "fuori_scoccare": int((d["t"] % 3_600_000 != 0).sum()), "ore_mancanti": int(len(manc)),
                                        "giorni_con_buchi": len(giorni), "primi_giorni": giorni[:12]}
    (RIS / "impronte_mark.json").write_text(json.dumps(out, indent=1, ensure_ascii=False))
    print(json.dumps({"file": out["file"], "n_errori": out["n_errori"], "errori": out["errori"][:3],
                      "buchi": {k: (v["ore_mancanti"], v["giorni_con_buchi"]) for k, v in out["buchi"].items()}}))


if __name__ == "__main__":
    main()
