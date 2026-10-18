"""Autopsia delle strategie vecchie: perche' perdono, misurato contro il caso.

Le regole sono in ``research/autopsia/regole.md``, committate prima di qualunque calcolo
(commit 7dbb624e). Qui le misure 1-6 sulle varianti delle ricerche BTC51 e LINK6, rieseguite
con gli strumenti congelati sul solo periodo di costruzione, e sulle loro entrate casuali.

Uso:
    python3 -m research.autopsia.autopsia varianti      # calcola e scrive varianti.jsonl
    python3 -m research.autopsia.autopsia riepilogo     # legge varianti.jsonl, scrive riepilogo.json
"""
from __future__ import annotations

import json
import math
import sys
from concurrent.futures import ProcessPoolExecutor
from datetime import date
from pathlib import Path

import numpy as np

from research.src import catalogo3 as cat
from research.src import dati
from research.src import motore3 as mot
from research.src import statistica3 as st3
from research.src.statistica4 import COSTI_LINK, REGOLE_LINK

QUI = Path(__file__).resolve().parent
RADICE = QUI.parent.parent
INIZIO = date(2020, 1, 1)
FINE = date(2022, 9, 30)
N_SIM = 20
SEME = 2026
ZERO = mot.Costi(taker=0.0, maker=0.0, slippage=0.0)
FINESTRA_VOL = 24          # candele per la volatilita' alla candela del segnale (misura 6)
GIORNI_STORIA = 365        # storia per il percentile della volatilita'
GIORNI_MINIMI = 60         # con meno storia la volatilita' non si classifica
CANDELE_GIORNO = {"15m": 96, "30m": 48, "1h": 24, "2h": 12, "4h": 6, "6h": 4, "8h": 3, "12h": 2, "1d": 1}

CAMPAGNE = {
    "BTC51": {"simbolo": "BTCUSDT", "carica": "serie_3", "regole": mot.Regole(), "costi": mot.COSTI_NORMALI},
    "LINK6": {"simbolo": "LINKUSDT", "carica": "serie_4", "regole": REGOLE_LINK, "costi": COSTI_LINK},
}

#: famiglie per codice d'ingresso del catalogo (sezione 7 dei protocolli 3 e 4), solo descrittive
FAMIGLIA = {"E1": "tendenza", "E2": "tendenza", "E3": "tendenza", "E7": "tendenza", "E9": "tendenza",
            "E4": "rotture di volatilita'", "E10": "orari e range", "E5": "ritorno alla media",
            "E6": "ritorno alla media", "E8": "ritorno alla media", "E11": "funding", "E12": "volume"}


def varianti(campagna: str) -> list:
    """Le varianti con un risultato di Fase 2 nel log, con la loro specifica registrata."""
    reg, res = {}, {}
    for riga in (RADICE / "research" / "campagne" / campagna / "log.jsonl").read_text(encoding="utf-8").splitlines():
        if not riga.strip():
            continue
        d = json.loads(riga)
        if d.get("tipo") == "registrazione" and "specifica" in d:
            reg[d["id"]] = d["specifica"]
        if d.get("tipo") == "risultato" and "metriche" in d:
            res[d["id"]] = d["metriche"]
    return [(campagna, vid, reg[vid]) for vid in sorted(reg) if vid in res]


_SERIE: dict = {}


def serie(campagna: str, tf: str):
    chiave = (campagna, tf)
    if chiave not in _SERIE:
        cfg = CAMPAGNE[campagna]
        s = getattr(dati, cfg["carica"])(cfg["simbolo"], tf, INIZIO, FINE)
        ts = np.asarray(s.ts)
        a = int(np.searchsorted(ts, dati.ms_da_data(INIZIO)))
        b = int(np.searchsorted(ts, dati.ms_da_data(date(2022, 10, 1)))) - 1
        _SERIE[chiave] = (s, a, b)
    return _SERIE[chiave]


def volatilita(close: np.ndarray) -> np.ndarray:
    """Deviazione dei rendimenti logaritmici delle FINESTRA_VOL candele che finiscono a ogni candela."""
    lr = np.diff(np.log(close), prepend=np.nan)
    v = np.full(len(close), np.nan)
    for i in range(FINESTRA_VOL, len(close)):
        v[i] = np.std(lr[i - FINESTRA_VOL + 1:i + 1])
    return v


def percentile_vol(v: np.ndarray, i: int, per_giorno: int) -> float:
    """Percentile di v[i] fra le candele dei GIORNI_STORIA giorni prima (sottocampionate)."""
    w = GIORNI_STORIA * per_giorno
    lo = max(0, i - w)
    if i - lo < GIORNI_MINIMI * per_giorno or not np.isfinite(v[i]):
        return float("nan")
    passo = max(1, (i - lo) // 3000)
    storia = v[lo:i:passo]
    storia = storia[np.isfinite(storia)]
    return float(np.mean(storia < v[i])) if len(storia) else float("nan")


def misure_trade(s, t, r_lordo, vol, per_giorno: int, h_dopo: int) -> dict:
    """Le misure 1-6 di un trade (Trade del motore) sulle candele della serie."""
    long = t.long
    segno = 1.0 if long else -1.0
    rd = abs(t.prezzo_ingresso - t.stop_iniziale)
    if rd <= 0:
        return {}
    hi, lo, cl = s.high, s.low, s.close
    a, b = t.indice_ingresso, t.indice_uscita
    # 1: chi arriva prima, -0,5 R o +0,5 R
    su = t.prezzo_ingresso + segno * 0.5 * rd
    giu = t.prezzo_ingresso - segno * 0.5 * rd
    primo = None
    for k in range(a, b + 1):
        fav = hi[k] >= su if long else lo[k] <= su
        con = lo[k] <= giu if long else hi[k] >= giu
        if fav and con:
            primo = "non deciso"
            break
        if fav:
            primo = "favore"
            break
        if con:
            primo = "contro"
            break
    # 2: movimento prima del segnale, in R
    j = t.indice_segnale
    pre4 = segno * (cl[j] - cl[j - 4]) / rd if j >= 4 else float("nan")
    pre12 = segno * (cl[j] - cl[j - 12]) / rd if j >= 12 else float("nan")
    # 3: massimo a favore e restituito
    if long:
        mfe = (np.max(hi[a:b + 1]) - t.prezzo_ingresso) / rd
    else:
        mfe = (t.prezzo_ingresso - np.min(lo[a:b + 1])) / rd
    # 4: dopo lo stop, il prezzo tocca ingresso + 1 R?
    rimbalzo = None
    if t.motivo == "stop":
        c = min(len(cl) - 1, b + h_dopo)
        if c > b:
            obiettivo = t.prezzo_ingresso + segno * rd
            rimbalzo = bool(np.max(hi[b + 1:c + 1]) >= obiettivo) if long else bool(np.min(lo[b + 1:c + 1]) <= obiettivo)
    return {"primo": primo, "pre4": pre4, "pre12": pre12, "mfe": float(mfe), "r": float(t.r),
            "r_lordo": None if r_lordo is None else float(r_lordo),
            "costo": None if r_lordo is None else float(r_lordo - t.r),
            "motivo": t.motivo, "rimbalzo": rimbalzo,
            "vol": percentile_vol(vol, j, per_giorno), "long": long}


def analizza(arg) -> dict:
    campagna, vid, spec = arg
    cfg = CAMPAGNE[campagna]
    s, a, b = serie(campagna, spec["timeframe"])
    c = cat.compila(spec, s)
    ris = mot.esegui(c, cfg["regole"], cfg["costi"], a, b)
    if not ris.trade:
        return {"campagna": campagna, "id": vid, "trade": 0}
    lordi = {t.indice_ingresso: t.r for t in mot.esegui(c, cfg["regole"], ZERO, a, b).trade}
    per_giorno = CANDELE_GIORNO[spec["timeframe"]]
    vol = volatilita(np.asarray(s.close, dtype=float))
    h_dopo = int(np.median([t.candele_in_posizione for t in ris.trade])) or 1
    strat = [misure_trade(s, t, lordi.get(t.indice_ingresso), vol, per_giorno, h_dopo) for t in ris.trade]
    raccolti: list = []
    vecchio = st3._OSSERVATORE
    st3._OSSERVATORE = lambda lista: raccolti.append(lista)
    try:
        st3.entrate_casuali(c, len(ris.trade), a, b, cfg["regole"], cfg["costi"], N_SIM, SEME,
                            larghezze_candidato=[st3.larghezza_stop(t) for t in ris.trade])
    except st3.SimulazioneImpossibile:
        raccolti = []
    finally:
        st3._OSSERVATORE = vecchio
    caso = []
    for lista in raccolti[:N_SIM]:
        for j, t in lista:
            lordo = mot.simula_da(c, j, cfg["regole"], ZERO, b, forzato=True)
            caso.append(misure_trade(s, t, lordo.trade.r if lordo.tipo == "trade" else None, vol,
                                     per_giorno, h_dopo))
    return {"campagna": campagna, "id": vid, "famiglia": FAMIGLIA.get(spec["ingresso"]["codice"], "altro"),
            "codice": spec["ingresso"]["codice"], "timeframe": spec["timeframe"], "direzione": spec["direzione"],
            "trade": len(strat), "simulazioni": len(raccolti[:N_SIM]), "strategia": strat, "caso": caso}


# ---------------------------------------------------------------------------
# riepilogo
# ---------------------------------------------------------------------------

def _media(xs):
    xs = [x for x in xs if x is not None and not (isinstance(x, float) and math.isnan(x))]
    return float(np.mean(xs)) if xs else float("nan")


def indicatori(trades: list) -> dict:
    """Le misure 1-5 e le fasce della 6 su un insieme di trade."""
    decisi = [t for t in trades if t.get("primo") in ("favore", "contro")]
    grandi = [t for t in trades if t.get("mfe", 0) >= 1.0 and t.get("r_lordo") is not None]
    stop = [t for t in trades if t.get("motivo") == "stop" and t.get("rimbalzo") is not None]
    out = {
        "n": len(trades),
        "m1_contro_prima": _media([1.0 if t["primo"] == "contro" else 0.0 for t in decisi]),
        "m2_prima_4": _media([t.get("pre4") for t in trades]),
        "m2_prima_12": _media([t.get("pre12") for t in trades]),
        "m3_restituito": _media([(t["mfe"] - t["r_lordo"]) / t["mfe"] for t in grandi]),
        "m3_chiusi_sotto_zero": _media([1.0 if t["r_lordo"] <= 0 else 0.0 for t in grandi]),
        "m3_quota_con_1R": _media([1.0 if t.get("mfe", 0) >= 1.0 else 0.0 for t in trades]),
        "m4_rimbalzo_dopo_stop": _media([1.0 if t["rimbalzo"] else 0.0 for t in stop]),
        "m5_costo_r": _media([t.get("costo") for t in trades]),
        "r_netto": _media([t.get("r") for t in trades]),
        "r_lordo": _media([t.get("r_lordo") for t in trades]),
    }
    for q in range(5):
        fascia = [t for t in trades if t.get("vol") is not None and not math.isnan(t["vol"])
                  and q / 5 <= t["vol"] < (q + 1) / 5 + (1e-9 if q == 4 else 0)]
        out[f"m6_Q{q + 1}_n"] = len(fascia)
        out[f"m6_Q{q + 1}_r_netto"] = _media([t.get("r") for t in fascia])
        out[f"m6_Q{q + 1}_r_lordo"] = _media([t.get("r_lordo") for t in fascia])
        out[f"m6_Q{q + 1}_costo"] = _media([t.get("costo") for t in fascia])
    return out


def bootstrap(differenze: list, n: int = 2000, seme: int = SEME) -> dict:
    d = np.asarray([x for x in differenze if np.isfinite(x)])
    if len(d) < 3:
        return {"media": float("nan"), "basso": float("nan"), "alto": float("nan"), "varianti": int(len(d))}
    rng = np.random.default_rng(seme)
    medie = [float(np.mean(rng.choice(d, len(d), replace=True))) for _ in range(n)]
    return {"media": float(np.mean(d)), "basso": float(np.percentile(medie, 2.5)),
            "alto": float(np.percentile(medie, 97.5)), "varianti": int(len(d))}


def riepilogo(righe: list) -> dict:
    chiavi = [k for k in indicatori([]).keys() if k != "n" and not k.endswith("_n")]
    per_var = []
    for r in righe:
        if not r.get("trade") or not r.get("caso"):
            continue
        per_var.append({"campagna": r["campagna"], "id": r["id"], "famiglia": r["famiglia"],
                        "strategia": indicatori(r["strategia"]), "caso": indicatori(r["caso"])})
    out = {"varianti": len(per_var), "senza_caso": [r["id"] for r in righe if r.get("trade") and not r.get("caso")]}
    for gruppo, filtro in (("tutte", lambda v: True), ("BTC51", lambda v: v["campagna"] == "BTC51"),
                           ("LINK6", lambda v: v["campagna"] == "LINK6")):
        sel = [v for v in per_var if filtro(v)]
        out[gruppo] = {k: {"strategia": _media([v["strategia"][k] for v in sel]),
                           "caso": _media([v["caso"][k] for v in sel]),
                           "differenza": bootstrap([v["strategia"][k] - v["caso"][k] for v in sel])}
                       for k in chiavi}
    fam = {}
    for v in per_var:
        fam.setdefault(v["famiglia"], []).append(v)
    out["famiglie"] = {f: {"varianti": len(vs),
                           **{k: {"strategia": _media([v["strategia"][k] for v in vs]),
                                  "caso": _media([v["caso"][k] for v in vs])}
                              for k in ("m1_contro_prima", "m2_prima_4", "m3_restituito", "m4_rimbalzo_dopo_stop",
                                        "m5_costo_r", "r_netto", "r_lordo", "m6_Q1_r_netto", "m6_Q5_r_netto")}}
                       for f, vs in sorted(fam.items())}
    return out


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    cmd = argv[0] if argv else "varianti"
    uscita = QUI / "varianti.jsonl"
    if cmd == "varianti":
        tutte = varianti("BTC51") + varianti("LINK6")
        if len(argv) > 1:
            tutte = [v for v in tutte if v[1] in argv[1:]]
        fatti = set()
        if uscita.exists():
            fatti = {(json.loads(r)["campagna"], json.loads(r)["id"])
                     for r in uscita.read_text(encoding="utf-8").splitlines() if r.strip()}
        da_fare = [v for v in tutte if (v[0], v[1]) not in fatti]
        print(f"[autopsia] {len(da_fare)} varianti da fare su {len(tutte)}", flush=True)
        with ProcessPoolExecutor(max_workers=4) as ex, open(uscita, "a", encoding="utf-8") as f:
            for r in ex.map(analizza, da_fare):
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
                f.flush()
                print(f"[autopsia] {r['campagna']} {r['id']}: {r['trade']} trade, "
                      f"{len(r.get('caso', []))} trade a caso", flush=True)
        return 0
    if cmd == "riepilogo":
        righe = [json.loads(r) for r in uscita.read_text(encoding="utf-8").splitlines() if r.strip()]
        out = riepilogo(righe)
        out["versioni"] = {"python": sys.version.split()[0], "numpy": np.__version__}
        (QUI / "riepilogo.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
        print(json.dumps({k: out[k] for k in ("varianti", "senza_caso")}, ensure_ascii=False))
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main())
