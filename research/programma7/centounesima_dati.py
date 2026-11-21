"""Prova 163 (CENTOUNESIMA.md + «Chiusura della verifica»): scarico dei dati dell'arbitraggio del funding fra Binance e Hyperliquid.
Solo dati gratuiti e pubblici: archivio mensile di Binance (data.binance.vision: funding, candele giornaliere, prezzo mark a 1 ora) e
interfaccia pubblica di Hyperliquid (fundingHistory, candleSnapshot 1d e 1h). Non calcola nessun rendimento.
Riprende dai file gia' scaricati; ogni passo si ferma dopo i minuti dati (sotto i 55) e si rilancia.

Uso: python3 -m research.programma7.centounesima_dati --fase abbina
     python3 -m research.programma7.centounesima_dati --fase hl [--minuti 50]
     python3 -m research.programma7.centounesima_dati --fase bn [--minuti 50]
     python3 -m research.programma7.centounesima_dati --fase rapporto
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
RIS = QUI / "risultati_centounesima"
DATI = QUI.parent / "data" / "centounesima"           # research/data e' ignorato da git
SEME_HL = QUI.parent / "data" / "hyperliquid"         # lo storico del funding scaricato dalla prova 135/73 (seme, poi esteso)
API = "https://api.hyperliquid.xyz/info"
PRIMO_MESE, ULTIMO_MESE = "2023-05", "2026-10"
FINE_MS = 1_793_491_200_000                           # 1 novembre 2026 00:00 UTC (il funding dell'ultimo giorno arriva fino a li')
INIZIO_MS = 1_680_000_000_000                         # aprile 2023
TIPI = {"funding": "https://data.binance.vision/data/futures/um/monthly/fundingRate/{s}/{s}-fundingRate-{m}.zip",
        "d1": "https://data.binance.vision/data/futures/um/monthly/klines/{s}/1d/{s}-1d-{m}.zip",
        "mark1h": "https://data.binance.vision/data/futures/um/monthly/markPriceKlines/{s}/1h/{s}-1h-{m}.zip"}
PAUSA_HL = 1.8                                        # secondi fra due richieste (peso di fundingHistory alto: limite 1200 al minuto)


def mesi() -> list:
    out, a, m = [], 2023, 5
    while f"{a}-{m:02d}" <= ULTIMO_MESE:
        out.append(f"{a}-{m:02d}")
        a, m = (a + 1, 1) if m == 12 else (a, m + 1)
    return out


PAUSA = {"s": PAUSA_HL, "n429": 0}                    # pausa adattiva fra richieste: raddoppia dopo un 429, scende piano


def _post(corpo: dict):
    for k in range(6):
        try:
            r = urllib.request.Request(API, data=json.dumps(corpo).encode(), headers={"Content-Type": "application/json", "User-Agent": "ricerca/1.0"})
            with urllib.request.urlopen(r, timeout=60) as x:
                PAUSA["s"] = max(PAUSA_HL, PAUSA["s"] * 0.98)
                return json.load(x)
        except urllib.error.HTTPError as e:
            if e.code == 429:
                PAUSA["n429"] += 1
                PAUSA["s"] = min(6.0, PAUSA["s"] * 1.5)
            time.sleep(10 * (k + 1) if e.code == 429 else 2 ** (k + 1))
        except Exception:  # noqa: BLE001
            time.sleep(2 ** (k + 1))
    return None


# ---------------------------------------------------------------------------------------------------------------- abbinamento
def abbina() -> None:
    """Abbina i nomi di Hyperliquid ai simboli di Binance come `settantatreesima.funding_hl` (elenco dei simboli del pannello)."""
    from research.programma6 import seconda as sc
    pan = sc.pannello()
    simboli = list(pan["simboli"])
    meta = _post({"type": "meta"})
    ab, usati, senza = {}, set(), []
    for x in meta["universe"]:
        n = x["name"]
        base = n[1:] if n.startswith("k") and n[1:].isupper() else n
        cand = (f"1000{base}USDT",) if n.startswith("k") and n[1:].isupper() else (f"{base}USDT", f"1000{base}USDT")
        s = next((p for p in cand if p in simboli), None)
        if not s or s in usati:
            senza.append(n)
            continue
        usati.add(s)
        ab[n] = {"binance": s, "isDelisted": bool(x.get("isDelisted", False))}
    DATI.mkdir(parents=True, exist_ok=True)
    (DATI / "abbinati.json").write_text(json.dumps({"abbinati": ab, "senza_abbinamento": senza, "nomi_hl": len(meta["universe"])}, indent=1))
    print(f"nomi su Hyperliquid {len(meta['universe'])}; abbinati {len(ab)} (ritirati {sum(v['isDelisted'] for v in ab.values())}); senza {len(senza)}")


def carica_ab() -> dict:
    return json.loads((DATI / "abbinati.json").read_text())["abbinati"]


# ---------------------------------------------------------------------------------------------------------------- hyperliquid
def hl_funding(n: str, t_fine: float) -> str:
    f = DATI / "hl_funding" / f"{n}.json"
    f.parent.mkdir(parents=True, exist_ok=True)
    stato = json.loads(f.read_text()) if f.exists() else None
    if stato and stato.get("completo"):
        return "gia"
    righe = stato["righe"] if stato else []
    seme = SEME_HL / f"{n}.json"
    if not righe and seme.exists():
        righe = [tuple(x) for x in json.loads(seme.read_text())]
    t = (righe[-1][0] + 1) if righe else INIZIO_MS
    nuove = 0
    while True:
        if time.time() > t_fine:
            f.write_text(json.dumps({"righe": righe, "completo": False}))
            return "tempo"
        d = _post({"type": "fundingHistory", "coin": n, "startTime": t, "endTime": FINE_MS + 3_600_000})
        if d is None:
            f.write_text(json.dumps({"righe": righe, "completo": False}))
            return "errore"
        righe += [(int(x["time"]), float(x["fundingRate"])) for x in d]
        nuove += len(d)
        time.sleep(PAUSA["s"])
        if len(d) < 500:
            break
        t = int(d[-1]["time"]) + 1
    f.write_text(json.dumps({"righe": righe, "completo": True, "scaricato_il": time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())}))
    return f"ok +{nuove}"


def hl_candele(n: str, intervallo: str) -> str:
    f = DATI / "hl_candele" / f"{n}_{intervallo}.json"
    f.parent.mkdir(parents=True, exist_ok=True)
    if f.exists():
        return "gia"
    ora = int(time.time() * 1000)
    da = INIZIO_MS if intervallo == "1d" else ora - 5100 * 3_600_000
    d = _post({"type": "candleSnapshot", "req": {"coin": n, "interval": intervallo, "startTime": da, "endTime": ora}})
    time.sleep(PAUSA["s"])
    if d is None:
        return "errore"
    f.write_text(json.dumps({"scaricato_il": time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()),
                             "candele": [[int(x["t"]), float(x["o"]), float(x["h"]), float(x["l"]), float(x["c"]), float(x["v"])] for x in d]}))
    return f"ok {len(d)}"


def fase_hl(minuti: float) -> None:
    t_fine = time.time() + 60 * minuti
    ab = carica_ab()
    conto = {}
    for n in ab:
        for nome, fn in (("candele1d", lambda n=n: hl_candele(n, "1d")), ("candele1h", lambda n=n: hl_candele(n, "1h")),
                         ("funding", lambda n=n: hl_funding(n, t_fine))):
            if time.time() > t_fine:
                break
            e = fn()
            conto[f"{nome}:{e.split()[0]}"] = conto.get(f"{nome}:{e.split()[0]}", 0) + 1
    print(json.dumps(conto), "429:", PAUSA["n429"], "pausa:", round(PAUSA["s"], 2))
    resto = [n for n in ab if not _hl_finito(n)]
    print(f"monete non ancora complete: {len(resto)} su {len(ab)}")


def _hl_finito(n: str) -> bool:
    f = DATI / "hl_funding" / f"{n}.json"
    return (f.exists() and json.loads(f.read_text()).get("completo", False) and (DATI / "hl_candele" / f"{n}_1d.json").exists()
            and (DATI / "hl_candele" / f"{n}_1h.json").exists())


# ---------------------------------------------------------------------------------------------------------------- binance
def uno(x):
    k, s, m = x
    f = DATI / "bn" / k / s / f"{s}-{m}.zip"
    if (f.exists() and f.stat().st_size > 0) or f.with_suffix(".404").exists():
        return x, "gia"
    f.parent.mkdir(parents=True, exist_ok=True)
    err = ""
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


def lavori() -> list:
    ab = carica_ab()
    return [(k, v["binance"], m) for v in ab.values() for m in mesi() for k in TIPI]


def fase_bn(minuti: float) -> None:
    t_fine = time.time() + 60 * minuti
    tutti = lavori()
    fatto = lambda x: (DATI / "bn" / x[0] / x[1] / f"{x[1]}-{x[2]}.zip").exists() or (DATI / "bn" / x[0] / x[1] / f"{x[1]}-{x[2]}.404").exists()  # noqa: E731
    da_fare = [x for x in tutti if not fatto(x)]
    print(f"da scaricare: {len(da_fare)} file su {len(tutti)}")
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
    print(f"restano: {len([x for x in tutti if not fatto(x)])}")


# ---------------------------------------------------------------------------------------------------------------- rapporto
def rapporto() -> None:
    RIS.mkdir(exist_ok=True)
    ab = carica_ab()
    out = {"monete": len(ab), "impronte": {}, "hl": {}}
    for k in TIPI:
        h = hashlib.sha256()
        nf = nb = n404 = 0
        for v in ab.values():
            for f in sorted((DATI / "bn" / k / v["binance"]).glob("*")) if (DATI / "bn" / k / v["binance"]).exists() else []:
                if f.suffix == ".zip":
                    h.update(f.name.encode() + f.read_bytes())
                    nf += 1
                    nb += f.stat().st_size
                else:
                    n404 += 1
        out["impronte"][k] = {"file": nf, "byte": nb, "non_trovati_404": n404, "sha256_unico": h.hexdigest()}
    for n in ab:
        f = DATI / "hl_funding" / f"{n}.json"
        if f.exists():
            r = json.loads(f.read_text())["righe"]
            c1 = json.loads((DATI / "hl_candele" / f"{n}_1d.json").read_text())["candele"] if (DATI / "hl_candele" / f"{n}_1d.json").exists() else []
            c2 = json.loads((DATI / "hl_candele" / f"{n}_1h.json").read_text())["candele"] if (DATI / "hl_candele" / f"{n}_1h.json").exists() else []
            out["hl"][n] = {"funding_righe": len(r), "funding_da": r[0][0] if r else None, "funding_a": r[-1][0] if r else None,
                            "candele_1d": len(c1), "candele_1h": len(c2)}
    (RIS / "impronte_dati.json").write_text(json.dumps(out, indent=1))
    print(json.dumps({k: (v["file"], v["non_trovati_404"]) for k, v in out["impronte"].items()}), "hl con funding:", len(out["hl"]))


if __name__ == "__main__":
    fase = sys.argv[sys.argv.index("--fase") + 1] if "--fase" in sys.argv else ""
    mn = float(sys.argv[sys.argv.index("--minuti") + 1]) if "--minuti" in sys.argv else 50.0
    {"abbina": abbina, "hl": lambda: fase_hl(mn), "bn": lambda: fase_bn(mn), "rapporto": rapporto}[fase]()
