"""Fase 0, punto 3: i numeri dei dati di ETHUSDT per fase0_dati.md.

Legge solo i file in-sample gia' scaricati (fino al 2023-12-31). Scrive:
* research/data/insample/ETHUSDT/lavoro/fase0.json (tutti i numeri);
* research/campagne/ETHUSDT/impronte.json (SHA-256 di ogni zip, ETHUSDT e BTCUSDT).
Ricontrolla anche ogni zip contro il CHECKSUM pubblicato accanto al file.
"""

import hashlib
import json
import sys
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime, timezone
from pathlib import Path

RADICE_REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(RADICE_REPO))

from research.src import dati  # noqa: E402

SIMBOLO = "ETHUSDT"
INIZIO = date(2020, 1, 1)
FINE = date(2023, 12, 31)
TIMEFRAME = ["15m", "30m", "1h", "2h", "4h", "6h", "8h", "12h", "1d"]
SOGLIA = 20_000_000
INSAMPLE = RADICE_REPO / "research" / "data" / "insample"
USCITA = INSAMPLE / SIMBOLO / "lavoro" / "fase0.json"
IMPRONTE = RADICE_REPO / "research" / "campagne" / SIMBOLO / "impronte.json"


def utc(ts: int) -> str:
    return datetime.fromtimestamp(ts / 1000, tz=timezone.utc).strftime("%Y-%m-%d %H:%M")


def barre_attese(tf: str) -> int:
    return (dati.ms_da_data(date(2024, 1, 1)) - dati.ms_da_data(INIZIO)) // dati.durata_intervallo(tf)


def buchi(candele, ms):
    out = []
    for a, b in zip(candele, candele[1:]):
        if b.ts > a.ts + ms:
            out.append({"dopo": utc(a.ts), "riprende": utc(b.ts), "barre_mancanti": (b.ts - a.ts) // ms - 1})
    return out


def serie_tf(simbolo: str, tf: str):
    ms = dati.durata_intervallo(tf)
    last = dati.carica_candele(simbolo, tf, INIZIO, FINE)
    out = {"last": len(last), "attese": barre_attese(tf), "buchi_last": buchi(last, ms)}
    if simbolo == SIMBOLO:
        mark = dati.carica_candele(simbolo, tf, INIZIO, FINE, tipo="markPriceKlines")
        ts_l = {c.ts for c in last}
        ts_m = {c.ts for c in mark}
        solo_last = sorted(ts_l - ts_m)
        solo_mark = sorted(ts_m - ts_l)
        out.update({
            "mark": len(mark),
            "intersezione": len(ts_l & ts_m),
            "solo_last": len(solo_last),
            "solo_mark": len(solo_mark),
            "giorni_solo_last": sorted({utc(t)[:10] for t in solo_last}),
            "giorni_solo_mark": sorted({utc(t)[:10] for t in solo_mark}),
            "buchi_mark": buchi(mark, ms),
        })
    return out


def volume_giornaliero():
    """Volume in USDT (colonna quote_volume) delle candele giornaliere last."""
    righe = []
    for anno in range(2020, 2024):
        for mese in range(1, 13):
            p = dati.percorso_mese(SIMBOLO, "klines", "1d", anno, mese)
            for r in dati.righe_csv_da_zip(p):
                righe.append((dati.normalizza_ts(r[0]), float(r[7]), float(r[4])))
    per_mese = defaultdict(list)
    per_anno = defaultdict(list)
    for ts, qv, _close in righe:
        d = datetime.fromtimestamp(ts / 1000, tz=timezone.utc)
        per_mese[f"{d.year}-{d.month:02d}"].append(qv)
        per_anno[str(d.year)].append(qv)
    media_mese = {k: sum(v) / len(v) for k, v in sorted(per_mese.items())}
    media_anno = {k: sum(v) / len(v) for k, v in sorted(per_anno.items())}
    sotto = [k for k, v in media_mese.items() if v < SOGLIA]
    salti = []
    closes = [c for _t, _q, c in righe]
    for (t, _q, c0), (_t1, _q1, c1) in zip(righe, righe[1:]):
        if c0 > 0 and (c1 / c0 > 1.5 or c1 / c0 < 0.5):
            salti.append({"giorno": utc(t)[:10], "rapporto": c1 / c0})
    return {
        "volume_medio_giornaliero_usdt_per_anno": media_anno,
        "volume_medio_giornaliero_usdt_per_mese": media_mese,
        "mesi_sotto_soglia": sotto,
        "minimo_mensile": min(media_mese.items(), key=lambda kv: kv[1]),
        "salti_di_prezzo_oltre_50pct_fra_chiusure": salti,
        "giorni": len(righe),
        "prima_chiusura": closes[0],
    }


def funding():
    righe = dati.carica_funding_dettaglio(SIMBOLO, INIZIO, FINE)
    per_anno = defaultdict(list)
    for ts, _ore, tasso in righe:
        per_anno[str(datetime.fromtimestamp(ts / 1000, tz=timezone.utc).year)].append(tasso)
    distanze = defaultdict(int)
    for a, b in zip(righe, righe[1:]):
        distanze[str(round((b[0] - a[0]) / 3_600_000, 3))] += 1
    return {
        "settlement": len(righe),
        "primo": utc(righe[0][0]),
        "ultimo": utc(righe[-1][0]),
        "intervalli_dichiarati": [(utc(t), o) for t, o in dati.intervallo_funding(righe)],
        "distanze_fra_settlement_ore": dict(distanze),
        "per_anno": {a: {"n": len(v), "medio": sum(v) / len(v), "minimo": min(v), "massimo": max(v),
                         "quota_positivi": sum(1 for x in v if x > 0) / len(v)} for a, v in sorted(per_anno.items())},
    }


def controlla_checksum(percorso: Path):
    rel = percorso.relative_to(INSAMPLE)
    parti = rel.parts  # SIMBOLO / tipo / [intervallo] / nome
    simbolo, tipo = parti[0], parti[1]
    nome = parti[-1]
    intervallo = parti[2] if len(parti) == 4 else None
    anno, mese = int(nome[-11:-7]), int(nome[-6:-4])
    url = dati.url_mese(simbolo, tipo, intervallo, anno, mese)
    testo = dati.fetch_http(url + dati.SUFFISSO_CHECKSUM)
    if testo is None:
        return str(rel), "checksum assente"
    atteso = dati.leggi_checksum(testo, url)
    trovato = dati.impronta_file(percorso)
    return str(rel), "ok" if atteso == trovato else f"diverso (atteso {atteso[:12]}, trovato {trovato[:12]})"


def main() -> None:
    risultato = {"serie": {}, "riferimento_btc": {}}
    for tf in TIMEFRAME:
        risultato["serie"][tf] = serie_tf(SIMBOLO, tf)
        risultato["riferimento_btc"][tf] = serie_tf("BTCUSDT", tf)
    risultato["volume"] = volume_giornaliero()
    risultato["funding"] = funding()

    zip_tutti = sorted(INSAMPLE.joinpath(SIMBOLO).rglob("*.zip")) + sorted(INSAMPLE.joinpath("BTCUSDT").rglob("*.zip"))
    with ThreadPoolExecutor(max_workers=16) as pool:
        esiti = list(pool.map(controlla_checksum, zip_tutti))
    risultato["checksum_remoto"] = {
        "file": len(esiti),
        "ok": sum(1 for _, e in esiti if e == "ok"),
        "problemi": [(n, e) for n, e in esiti if e != "ok"],
    }

    impronte = {
        SIMBOLO: dati.registra_impronte(SIMBOLO),
        "BTCUSDT": dati.registra_impronte("BTCUSDT"),
    }
    testo = json.dumps(impronte, indent=1, sort_keys=True) + "\n"
    IMPRONTE.write_text(testo, encoding="utf-8")
    risultato["impronte_file"] = {
        "percorso": "research/campagne/ETHUSDT/impronte.json",
        "sha256": hashlib.sha256(testo.encode("utf-8")).hexdigest(),
        "n_ethusdt": len(impronte[SIMBOLO]),
        "n_btcusdt": len(impronte["BTCUSDT"]),
    }
    USCITA.parent.mkdir(parents=True, exist_ok=True)
    USCITA.write_text(json.dumps(risultato, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print("scritto", USCITA)


if __name__ == "__main__":
    main()
