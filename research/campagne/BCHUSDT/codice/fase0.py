"""Fase 0, punti 2-3: resoconto dei dati di BCHUSDT (e controllo dei dati BTCUSDT).

Scrive ``data/insample/BCHUSDT/fase0_resoconto.json`` con: verifica dei CHECKSUM
remoti contro i file su disco; per ogni timeframe le barre di last e mark, le barre
tolte dall'allineamento (con gli intervalli di date) e i buchi del last; funding
(settlement, intervalli nel tempo, distanze anomale); volume medio giornaliero in
USDT per anno e per mese dalle candele 1d del last; i mesi sotto la liquidita' minima.
"""
import json
from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime, timezone
from pathlib import Path

from research.src import dati
from research.campagne.BCHUSDT.codice import comune

TF = ["15m", "30m", "1h", "2h", "4h", "6h", "8h", "12h", "1d"]
USCITA = comune.CARTELLA_DATI / "fase0_resoconto.json"


def iso(ts):
    return datetime.fromtimestamp(ts / 1000, tz=timezone.utc).strftime("%Y-%m-%d %H:%M")


def intervalli_ts(lista, ms):
    out = []
    for ts in lista:
        if out and ts - out[-1][1] <= ms:
            out[-1][1] = ts
        else:
            out.append([ts, ts])
    return [[iso(a), iso(b), int((b - a) // ms + 1)] for a, b in out]


def verifica_checksum(simbolo):
    cartella = dati.RADICE_DEFAULT / "data" / "insample" / simbolo
    file = sorted(cartella.rglob("*.zip"))

    def uno(p):
        rel = p.relative_to(cartella).parts
        tipo = rel[0]
        tf = rel[1] if tipo != "fundingRate" else None
        nome = p.stem
        anno, mese = int(nome[-7:-3]), int(nome[-2:])
        url = dati.url_mese(simbolo, tipo, tf, anno, mese)
        testo = dati.fetch_http(dati.url_checksum(url))
        if testo is None:
            return ("mancante", p.name)
        return ("ok" if dati.leggi_checksum(testo, url) == dati.impronta_file(p) else "diverso", p.name)

    with ThreadPoolExecutor(max_workers=16) as pool:
        esiti = list(pool.map(uno, file))
    ris = {"file": len(esiti)}
    for e, nome in esiti:
        ris[e] = ris.get(e, 0) + 1
    ris["non_ok"] = [[e, n] for e, n in esiti if e != "ok"]
    return ris


def main():
    out = {"checksum": {"BCHUSDT": verifica_checksum("BCHUSDT"), "BTCUSDT": verifica_checksum("BTCUSDT")}}
    out["timeframe"] = {}
    for tf in TF:
        ms = dati.durata_intervallo(tf)
        s = dati.carica_serie_allineate("BCHUSDT", tf, comune.INIZIO, comune.FINE_VALIDAZIONE)
        c = s["candele"]
        buchi = []
        for a, b in zip(c, c[1:]):
            if b.ts > a.close_ts + 1:
                buchi.append([iso(a.ts), iso(b.ts), int((b.ts - a.ts) // ms - 1)])
        last = dati.carica_candele("BCHUSDT", tf, comune.INIZIO, comune.FINE_VALIDAZIONE)
        btc = dati.carica_candele("BTCUSDT", tf, comune.INIZIO, comune.FINE_VALIDAZIONE)
        out["timeframe"][tf] = {
            "barre_last": len(last), "barre_tenute": len(c),
            "prima": iso(c[0].ts), "ultima": iso(c[-1].ts),
            "n_tolte_last": s["n_tolte_last"], "tolte_last": intervalli_ts(s["tolte_last"], ms),
            "n_tolte_mark": s["n_tolte_mark"], "tolte_mark": intervalli_ts(s["tolte_mark"], ms),
            "buchi_dopo_allineamento": len(buchi), "buchi": buchi[:40],
            "n_volume_mancante": s["n_volume_mancante"],
            "barre_btc": len(btc), "btc_prima": iso(btc[0].ts) if btc else None,
        }
    righe = dati.carica_funding_dettaglio("BCHUSDT", comune.INIZIO, comune.FINE_VALIDAZIONE)
    distanze = {}
    for a, b in zip(righe, righe[1:]):
        h = round((b[0] - a[0]) / 3_600_000, 3)
        distanze[str(h)] = distanze.get(str(h), 0) + 1
    out["funding"] = {
        "settlement": len(righe), "primo": iso(righe[0][0]), "ultimo": iso(righe[-1][0]),
        "intervalli_dichiarati": [[iso(t), h] for t, h in dati.intervallo_funding(righe)],
        "distanze_ore": distanze,
        "tasso_medio": sum(r[2] for r in righe) / len(righe),
        "tasso_medio_per_anno": {},
    }
    per_anno = {}
    for t, _h, r in righe:
        per_anno.setdefault(comune.anno(t), []).append(r)
    out["funding"]["tasso_medio_per_anno"] = {str(a): sum(v) / len(v) for a, v in sorted(per_anno.items())}
    volumi = {}
    for p in sorted((comune.CARTELLA_DATI / "klines" / "1d").glob("*.zip")):
        for ts, v in dati.volume_usdt_da_zip(p).items():
            volumi.setdefault(ts, v)
    per_mese, per_anno_v = {}, {}
    for ts, v in volumi.items():
        g = datetime.fromtimestamp(ts / 1000, tz=timezone.utc)
        per_mese.setdefault(f"{g.year}-{g.month:02d}", []).append(v)
        per_anno_v.setdefault(str(g.year), []).append(v)
    out["volume_medio_giorno_usdt_per_anno"] = {a: round(sum(v) / len(v)) for a, v in sorted(per_anno_v.items())}
    out["volume_medio_giorno_usdt_per_mese"] = {m: round(sum(v) / len(v)) for m, v in sorted(per_mese.items())}
    out["giorni_con_volume"] = len(volumi)
    out["mesi_sotto_liquidita"] = [f"{a}-{m:02d}" for a, m in comune.mesi_sotto_liquidita()]
    USCITA.write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
    print("scritto", USCITA)


if __name__ == "__main__":
    main()
