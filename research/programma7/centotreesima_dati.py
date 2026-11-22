"""Prova 165 (CENTOTREESIMA.md + «Chiusura della verifica», punto 1): scarico delle candele giornaliere mensili di tutti i perpetui
USDT-M dell'archivio pubblico di Binance (data.binance.vision), compresi quelli chiusi, dal dicembre 2021 al 31 ottobre 2026, con il
CHECKSUM, le impronte e il conto dei buchi. Solo dati gratuiti. Non calcola nessun rendimento. Riprende dai file gia' scaricati.

Scrive in ``research/data/centotreesima/d1/<SIMBOLO>/`` (fuori da git) e in ``risultati_centotreesima/``: ``impronte_dati.json`` e
``buchi_dati.json``.

Uso: python3 -m research.programma7.centotreesima_dati --fase elenca
     python3 -m research.programma7.centotreesima_dati --fase scarica [--minuti 50]
     python3 -m research.programma7.centotreesima_dati --fase rapporto
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import re
import time
import zipfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np
import pandas as pd

from research.programma5.strumenti.scarico import BASE, _prendi, elenca
from research.programma5.strumenti.universo import simboli
from research.programma6.scarico_giorni import ammesso
from research.src.dati import leggi_checksum

QUI = Path(__file__).parent
RIS = QUI / "risultati_centotreesima"
DATI = QUI.parent / "data" / "centotreesima" / "d1"          # research/data e' ignorato da git
PRIMO_MESE, ULTIMO_MESE = "2021-12", "2026-10"
ELENCO_JSON = RIS / "elenco_file.json"


def lavori() -> list:
    return json.loads(ELENCO_JSON.read_text())["chiavi"]


def fase_elenca() -> None:
    sim = [s for s in simboli() if ammesso(s)]
    with ThreadPoolExecutor(max_workers=8) as ex:
        elenchi = list(ex.map(lambda s: elenca(f"data/futures/um/monthly/klines/{s}/1d/"), sim))
    chiavi = []
    per_simbolo = {}
    for s, ch in zip(sim, elenchi):
        tenuti = []
        for k in ch:
            m = re.search(r"-(\d{4}-\d{2})\.zip$", k)
            if m and PRIMO_MESE <= m.group(1) <= ULTIMO_MESE:
                tenuti.append(k)
        per_simbolo[s] = {"mensili_totali": len(ch), "mensili_nel_periodo": len(tenuti)}
        chiavi += sorted(tenuti)
    RIS.mkdir(exist_ok=True)
    ELENCO_JSON.write_text(json.dumps({"simboli": len(sim), "file": len(chiavi), "per_simbolo": per_simbolo, "chiavi": chiavi}))
    print(f"simboli {len(sim)}; file da scaricare {len(chiavi)}")


def _scarica(chiave: str):
    s = chiave.split("/")[4]
    nome = chiave.rsplit("/", 1)[1]
    f = DATI / s / nome
    ok = f.with_suffix(".zip.ok")
    if f.exists() and ok.exists():
        return chiave, ok.read_text().strip()
    contenuto = _prendi(BASE + chiave)
    if contenuto is None:
        return chiave, None
    somma = _prendi(BASE + chiave + ".CHECKSUM")
    impronta = hashlib.sha256(contenuto).hexdigest()
    if somma is not None and leggi_checksum(somma, chiave) != impronta:
        raise RuntimeError(f"CHECKSUM diverso per {chiave}")
    f.parent.mkdir(parents=True, exist_ok=True)
    tmp = f.with_suffix(".tmp")
    tmp.write_bytes(contenuto)
    tmp.replace(f)
    ok.write_text(impronta if somma is not None else impronta + " senza-checksum")
    return chiave, ok.read_text().strip()


def fase_scarica(minuti: float) -> None:
    fine = time.time() + 60 * minuti
    da_fare = [k for k in lavori() if not ((DATI / k.split("/")[4] / k.rsplit("/", 1)[1]).exists()
                                           and (DATI / k.split("/")[4] / k.rsplit("/", 1)[1]).with_suffix(".zip.ok").exists())]
    print(f"da scaricare ancora {len(da_fare)}", flush=True)
    fatti = errori = 0
    with ThreadPoolExecutor(max_workers=16) as ex:
        for i in range(0, len(da_fare), 400):
            if time.time() > fine:
                print("tempo finito: rilanciare", flush=True)
                break
            for k, h in ex.map(_scarica, da_fare[i:i + 400]):
                fatti += 1
                errori += h is None
    print(f"fatti {fatti}, senza file (404) {errori}")


def leggi_k(f: Path) -> pd.DataFrame:
    with zipfile.ZipFile(f) as z:
        g = z.read(z.namelist()[0])
    d = pd.read_csv(io.BytesIO(g), header=0 if g[:1].isalpha() else None).iloc[:, :8]
    d.columns = ["t", "open", "high", "low", "close", "volume", "t_chiusura", "qvolume"]
    t = pd.to_numeric(d["t"])
    d["t"] = t.where(t < 10 ** 14, t // 1000)
    return d


def fase_rapporto() -> None:
    el = json.loads(ELENCO_JSON.read_text())
    out = {"file_attesi": el["file"], "simboli": el["simboli"], "simboli_con_file": 0, "file_presenti": 0, "senza_ok": 0,
           "sha256_unico": "", "per_simbolo": {}}
    buchi = {}
    h = hashlib.sha256()
    for s in sorted(el["per_simbolo"]):
        fs = sorted((DATI / s).glob("*.zip")) if (DATI / s).exists() else []
        if not fs:
            continue
        out["simboli_con_file"] += 1
        righe = []
        for f in fs:
            okf = f.with_suffix(".zip.ok")
            if not okf.exists():
                out["senza_ok"] += 1
                continue
            righe.append(f"{f.name} {okf.read_text().strip()}")
        out["file_presenti"] += len(righe)
        h.update("\n".join(righe).encode())
        out["per_simbolo"][s] = {"file": len(righe), "primo": fs[0].name, "ultimo": fs[-1].name}
        d = pd.concat([leggi_k(f) for f in fs], ignore_index=True)
        g = np.unique(d["t"].to_numpy() // 86_400_000)
        dup = int(len(d) - len(g))
        attesi = np.arange(g.min(), g.max() + 1)
        manc = np.setdiff1d(attesi, g)
        mesi_attesi = pd.period_range(fs[0].name[-11:-4], fs[-1].name[-11:-4], freq="M")
        mesi_pres = {f.name[-11:-4] for f in fs}
        mesi_manc = [str(m) for m in mesi_attesi if str(m) not in mesi_pres]
        fuori = int((d["t"] % 86_400_000 != 0).sum())
        if len(manc) or dup or mesi_manc or fuori:
            buchi[s] = {"giorni_mancanti_interni": int(len(manc)),
                        "primi_giorni": [pd.Timestamp(int(x) * 86400, unit="s").strftime("%Y-%m-%d") for x in manc[:8]],
                        "duplicati": dup, "mesi_mancanti_interni": mesi_manc, "fuori_mezzanotte": fuori}
    out["sha256_unico"] = h.hexdigest()
    out["simboli_con_buchi"] = len(buchi)
    RIS.mkdir(exist_ok=True)
    (RIS / "impronte_dati.json").write_text(json.dumps(out, indent=1, ensure_ascii=False))
    (RIS / "buchi_dati.json").write_text(json.dumps(buchi, indent=1, ensure_ascii=False))
    print(json.dumps({k: v for k, v in out.items() if k != "per_simbolo"}))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--fase", required=True, choices=["elenca", "scarica", "rapporto"])
    ap.add_argument("--minuti", type=float, default=50)
    a = ap.parse_args()
    {"elenca": fase_elenca, "scarica": lambda: fase_scarica(a.minuti), "rapporto": fase_rapporto}[a.fase]()


if __name__ == "__main__":
    main()
