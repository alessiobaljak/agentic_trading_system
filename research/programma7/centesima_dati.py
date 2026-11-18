"""Prova 162 (CENTESIMA.md, sezione «Chiusura della verifica», punto 13): scarico da data.binance.vision di fundingRate, candele 1d,
candele 1h e prezzo mark a 1 ora dei 40 simboli in USDC e dei corrispondenti in USDT, con impronte e buchi in risultati_centesima/.
Non calcola nessun rendimento. Riprende dai file gia' scaricati (un 404 si ricorda con un file .404 vuoto).

Uso: python3 -m research.programma7.centesima_dati [--minuti 50]     (scarica, ferma dopo i minuti dati, si rilancia)
     python3 -m research.programma7.centesima_dati --rapporto        (impronte e buchi, a scarico finito)
"""
from __future__ import annotations

import hashlib
import json
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

QUI = Path(__file__).parent
RIS = QUI / "risultati_centesima"
DATI = QUI.parent / "data" / "centesima"           # research/data e' ignorato da git
ULTIMO_MESE = "2026-10"
# Elenco fisso dei 40 simboli: base -> primo mese del file in USDC (VERIFICA_CENTESIMA.md, punto 1 della chiusura)
PRIMO_MESE = {}
for _m, _b in (("2024-01", "BNB BTC DOGE ETH SOL XRP"), ("2024-02", "LINK ORDI SUI"), ("2024-03", "1000PEPE 1000SHIB AVAX WLD"),
               ("2024-04", "ARB BCH BOME FIL LTC MATIC NEAR NEO TIA WIF"), ("2024-05", "1000BONK ENA ETHFI"), ("2024-07", "CRV"),
               ("2025-03", "ADA HBAR IP KAITO PNUT TRUMP"), ("2025-06", "AAVE UNI"), ("2025-07", "PENGU"), ("2025-08", "BIO"),
               ("2025-09", "WLFI"), ("2025-11", "ZEC"), ("2026-07", "DATAIP")):
    for _x in _b.split():
        PRIMO_MESE[_x] = _m
BASI = sorted(PRIMO_MESE)
assert len(BASI) == 40
TIPI = {"funding": "https://data.binance.vision/data/futures/um/monthly/fundingRate/{s}/{s}-fundingRate-{m}.zip",
        "d1": "https://data.binance.vision/data/futures/um/monthly/klines/{s}/1d/{s}-1d-{m}.zip",
        "k1h": "https://data.binance.vision/data/futures/um/monthly/klines/{s}/1h/{s}-1h-{m}.zip",
        "mark1h": "https://data.binance.vision/data/futures/um/monthly/markPriceKlines/{s}/1h/{s}-1h-{m}.zip"}


def mesi_da(primo: str) -> list:
    a, m = map(int, primo.split("-"))
    out = []
    while f"{a}-{m:02d}" <= ULTIMO_MESE:
        out.append(f"{a}-{m:02d}")
        a, m = (a + 1, 1) if m == 12 else (a, m + 1)
    return out


def lavori() -> list:
    return [(k, b + q, m) for b in BASI for q in ("USDC", "USDT") for m in mesi_da(PRIMO_MESE[b]) for k in TIPI]


def uno(x):
    k, s, m = x
    f = DATI / k / s / f"{s}-{m}.zip"
    if (f.exists() and f.stat().st_size > 0) or f.with_suffix(".404").exists():
        return x, "gia"
    f.parent.mkdir(parents=True, exist_ok=True)
    for tentativo in range(3):
        try:
            with urllib.request.urlopen(TIPI[k].format(s=s, m=m), timeout=90) as r:
                dati = r.read()
            f.write_bytes(dati)
            return x, "ok"
        except urllib.error.HTTPError as e:
            if e.code == 404:
                f.with_suffix(".404").write_bytes(b"")
                return x, "404"
            err = repr(e)[:90]
        except Exception as e:  # noqa: BLE001
            err = repr(e)[:90]
        time.sleep(2 * (tentativo + 1))
    return x, err


def scarica(minuti: float) -> None:
    t_fine = time.time() + 60 * minuti
    da_fare = [x for x in lavori() if not ((DATI / x[0] / x[1] / f"{x[1]}-{x[2]}.zip").exists() or
                                            (DATI / x[0] / x[1] / f"{x[1]}-{x[2]}.404").exists())]
    print(f"da scaricare: {len(da_fare)} file su {len(lavori())}")
    n = {"ok": 0, "404": 0, "errori": 0}
    errori = []
    with ThreadPoolExecutor(max_workers=8) as ex:
        for i in range(0, len(da_fare), 64):
            if time.time() > t_fine:
                print("tempo finito: rilanciare per riprendere")
                break
            for x, e in ex.map(uno, da_fare[i:i + 64]):
                if e in ("ok", "gia"):
                    n["ok"] += 1
                elif e == "404":
                    n["404"] += 1
                else:
                    n["errori"] += 1
                    errori.append((x, e))
    print(json.dumps(n), errori[:3])
    resto = [x for x in lavori() if not ((DATI / x[0] / x[1] / f"{x[1]}-{x[2]}.zip").exists() or (DATI / x[0] / x[1] / f"{x[1]}-{x[2]}.404").exists())]
    print(f"restano: {len(resto)}")


def rapporto() -> None:
    import io
    import zipfile

    import numpy as np
    import pandas as pd
    out = {"impronte": {}, "mancanti_404": {}, "buchi": {}}
    for k in TIPI:
        for b in BASI:
            for q in ("USDC", "USDT"):
                s = b + q
                fs = sorted((DATI / k / s).glob("*.zip")) if (DATI / k / s).exists() else []
                h = hashlib.sha256()
                for f in fs:
                    h.update(f.name.encode() + f.read_bytes())
                m404 = sorted(f.stem.split("-", 1)[1] if k == "funding" else f.stem for f in (DATI / k / s).glob("*.404")) if (DATI / k / s).exists() else []
                out["impronte"][f"{k}_{s}"] = {"file": len(fs), "sha256_unico": h.hexdigest(), "byte": int(sum(f.stat().st_size for f in fs))}
                if m404:
                    out["mancanti_404"][f"{k}_{s}"] = [x[-7:] for x in m404]
                if k in ("k1h", "mark1h", "d1") and fs:
                    passo = 3_600_000 if k != "d1" else 86_400_000
                    ts = []
                    for f in fs:
                        with zipfile.ZipFile(f) as z:
                            g = z.read(z.namelist()[0])
                        d = pd.read_csv(io.BytesIO(g), header=0 if g[:1].isalpha() else None).iloc[:, 0]
                        t = pd.to_numeric(d)
                        ts.append(t.where(t < 10 ** 14, t // 1000).to_numpy())
                    t = np.unique(np.concatenate(ts))
                    attese = np.arange(t.min(), t.max() + passo, passo)
                    manc = np.setdiff1d(attese, t)
                    out["buchi"][f"{k}_{s}"] = {"da": int(t.min()), "a": int(t.max()), "presenti": int(len(t)), "mancanti": int(len(manc)),
                                                "primi": [pd.Timestamp(int(x), unit="ms").strftime("%Y-%m-%d %H:%M") for x in manc[:8]]}
    (RIS / "impronte_dati.json").write_text(json.dumps(out, indent=1, ensure_ascii=False))
    tot = sum(v["file"] for v in out["impronte"].values())
    bu = {k: v["mancanti"] for k, v in out["buchi"].items() if v["mancanti"]}
    print(f"file {tot}; 404: {len(out['mancanti_404'])} serie; serie con buchi: {len(bu)}")
    print(json.dumps(dict(list(bu.items())[:12])))


if __name__ == "__main__":
    RIS.mkdir(exist_ok=True)
    if "--rapporto" in sys.argv:
        rapporto()
    else:
        mn = float(sys.argv[sys.argv.index("--minuti") + 1]) if "--minuti" in sys.argv else 50.0
        scarica(mn)
