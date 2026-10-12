"""Fase 0, punti 2-3: inventario, integrita', buchi, barre tolte, funding, volume, liquidita'.

Scrive il riepilogo in data/insample/LTCUSDT/fase0_riepilogo.json (fuori da git)
e le impronte in data/insample/LTCUSDT/impronte.json; fase0_dati.md si scrive a
mano da questo riepilogo. Il controllo del CHECKSUM remoto si rifa' qui per tutti
i file su disco, perche' l'elenco dei CHECKSUM mancanti del primo scarico e'
rimasto nell'uscita di un comando che il guardiano non lascia leggere.
"""
import json
import sys
from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))

from research.src import dati  # noqa: E402

TIMEFRAME = ["15m", "30m", "1h", "2h", "4h", "6h", "8h", "12h", "1d"]
INIZIO = date(2020, 1, 1)
FINE = date(2023, 12, 31)
RADICE = dati.RADICE_DEFAULT
USCITA = RADICE / "data" / "insample" / "LTCUSDT" / "fase0_riepilogo.json"


def giorno(ts):
    return datetime.fromtimestamp(ts / 1000, tz=timezone.utc).strftime("%Y-%m-%d %H:%M")


def controlla_checksum(percorso_url):
    percorso, url = percorso_url
    testo = dati.fetch_http(dati.url_checksum(url))
    if testo is None:
        return url, "mancante"
    attesa = dati.leggi_checksum(testo, url)
    return url, "ok" if attesa == dati.impronta_file(percorso) else "DIVERSO"


def inventario(simbolo, tipo, tf):
    presenti, assenti = [], []
    for anno, mese in dati.mesi_del_periodo(INIZIO, FINE):
        p = dati.percorso_mese(simbolo, tipo, tf, anno, mese)
        (presenti if p.is_file() else assenti).append((f"{anno}-{mese:02d}", p, dati.url_mese(simbolo, tipo, tf, anno, mese)))
    return presenti, assenti


def buchi(candele, ms):
    out = []
    for a, b in zip(candele, candele[1:]):
        if b.ts > a.close_ts + 1:
            out.append((giorno(a.close_ts + 1), giorno(b.ts), (b.ts - a.close_ts - 1) // ms))
    return out


def raggruppa(ts_lista, ms):
    """Intervalli contigui di ts (lista ordinata) come (da, a, numero di barre)."""
    out = []
    for ts in ts_lista:
        if out and ts == out[-1][1] + ms:
            out[-1][1] = ts
            out[-1][2] += 1
        else:
            out.append([ts, ts, 1])
    return [(giorno(a), giorno(b), n) for a, b, n in out]


if __name__ == "__main__":
    riepilogo = {"inventario": {}, "checksum": {}, "serie": {}}
    da_controllare = []
    for simbolo, tipo, tfs in (("LTCUSDT", "klines", TIMEFRAME), ("LTCUSDT", "markPriceKlines", TIMEFRAME),
                               ("LTCUSDT", "fundingRate", [None]), ("BTCUSDT", "klines", TIMEFRAME)):
        for tf in tfs:
            presenti, assenti = inventario(simbolo, tipo, tf)
            riepilogo["inventario"][f"{simbolo} {tipo} {tf}"] = {
                "mesi_presenti": len(presenti), "primo": presenti[0][0] if presenti else None,
                "ultimo": presenti[-1][0] if presenti else None, "mesi_assenti": [m for m, _, _ in assenti]}
            da_controllare += [(p, u) for _, p, u in presenti]
    with ThreadPoolExecutor(max_workers=16) as pool:
        esiti = list(pool.map(controlla_checksum, da_controllare))
    riepilogo["checksum"] = {
        "file": len(esiti),
        "ok": sum(1 for _, e in esiti if e == "ok"),
        "mancanti": [u for u, e in esiti if e == "mancante"],
        "diversi": [u for u, e in esiti if e == "DIVERSO"],
    }
    for tf in TIMEFRAME:
        ms = dati.durata_intervallo(tf)
        al = dati.carica_serie_allineate("LTCUSDT", tf, INIZIO, FINE)
        riepilogo["serie"][tf] = {
            "barre_tenute": len(al["candele"]),
            "prima": giorno(al["candele"][0].ts), "ultima": giorno(al["candele"][-1].ts),
            "n_tolte_last": al["n_tolte_last"], "tolte_last": raggruppa(al["tolte_last"], ms),
            "n_tolte_mark": al["n_tolte_mark"], "tolte_mark": raggruppa(al["tolte_mark"], ms),
            "buchi_dopo_intersezione": buchi(al["candele"], ms),
            "n_volume_mancante": al["n_volume_mancante"],
        }
        btc = dati.carica_candele("BTCUSDT", tf, INIZIO, FINE)
        riepilogo["serie"][tf]["btc_barre"] = len(btc)
        riepilogo["serie"][tf]["btc_buchi"] = buchi(btc, ms)
    righe = dati.carica_funding_dettaglio("LTCUSDT", INIZIO, FINE)
    riepilogo["funding"] = {
        "settlement": len(righe), "primo": giorno(righe[0][0]), "ultimo": giorno(righe[-1][0]),
        "intervalli_dichiarati": [(giorno(t), o) for t, o in dati.intervallo_funding(righe)],
        "intervalli_dalle_distanze": [(giorno(t), o) for t, o in dati.intervallo_funding([(t, r) for t, _, r in righe])],
        "tasso_medio_per_anno": {},
    }
    per_anno = {}
    for t, _, r in righe:
        per_anno.setdefault(datetime.fromtimestamp(t / 1000, tz=timezone.utc).year, []).append(r)
    riepilogo["funding"]["tasso_medio_per_anno"] = {a: sum(v) / len(v) for a, v in sorted(per_anno.items())}
    volumi_mese, volumi_anno = {}, {}
    for percorso in sorted((RADICE / "data" / "insample" / "LTCUSDT" / "klines" / "1d").glob("*.zip")):
        for ts, v in dati.volume_usdt_da_zip(percorso).items():
            d = datetime.fromtimestamp(ts / 1000, tz=timezone.utc)
            volumi_mese.setdefault(d.strftime("%Y-%m"), []).append(v)
            volumi_anno.setdefault(d.year, []).append(v)
    riepilogo["volume_medio_giornaliero_usdt_per_anno"] = {a: sum(v) / len(v) for a, v in sorted(volumi_anno.items())}
    riepilogo["volume_medio_giornaliero_usdt_per_mese"] = {m: sum(v) / len(v) for m, v in sorted(volumi_mese.items())}
    riepilogo["mesi_sotto_20_milioni"] = [m for m, v in sorted(volumi_mese.items()) if sum(v) / len(v) < 20_000_000]
    impronte = dati.registra_impronte("LTCUSDT")
    impronte_btc = dati.registra_impronte("BTCUSDT")
    riepilogo["impronte"] = {"LTCUSDT_file": len(impronte), "BTCUSDT_file": len(impronte_btc),
                             "LTCUSDT_impronte_json": dati.impronta_file(RADICE / "data" / "insample" / "LTCUSDT" / "impronte.json"),
                             "BTCUSDT_impronte_json": dati.impronta_file(RADICE / "data" / "insample" / "BTCUSDT" / "impronte.json")}
    USCITA.write_text(json.dumps(riepilogo, indent=1, default=str), encoding="utf-8")
    print("scritto", USCITA)
