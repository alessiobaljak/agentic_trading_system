"""Fase 0, punto 3: controllo dei dati di SOLUSDT e preparazione delle serie (solo fino al 2023-12-31).

Stampa: buchi nelle serie a 15 minuti (last e mark), barre tolte dall'intersezione,
funding (disponibilita' e intervallo), volume medio giornaliero in USDT per anno e per
mese (colonna quote_volume delle candele 1d), mesi sotto la liquidita' minima. Registra
le impronte dei file in data/insample/SOLUSDT/impronte.json (e quelle di BTCUSDT).
"""
import json
import sys
from collections import defaultdict
from datetime import date, datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))

from research.src import dati  # noqa: E402

INIZIO = date(2020, 9, 1)
FINE = date(2023, 12, 31)
MS15 = 15 * 60_000


def giorno(ts):
    return datetime.fromtimestamp(ts / 1000, tz=timezone.utc).strftime("%Y-%m-%d %H:%M")


def buchi(candele, passo):
    out = []
    for a, b in zip(candele, candele[1:]):
        if b.ts != a.ts + passo:
            out.append((giorno(a.ts + passo), (b.ts - a.ts) // passo - 1))
    return out


if __name__ == "__main__":
    last = dati.carica_candele("SOLUSDT", "15m", INIZIO, FINE)
    mark = dati.carica_candele("SOLUSDT", "15m", INIZIO, FINE, tipo="markPriceKlines")
    print("last 15m:", len(last), "da", giorno(last[0].ts), "a", giorno(last[-1].ts))
    print("mark 15m:", len(mark), "da", giorno(mark[0].ts), "a", giorno(mark[-1].ts))
    bl, bm = buchi(last, MS15), buchi(mark, MS15)
    print("buchi last:", len(bl), "barre mancanti:", sum(n for _, n in bl))
    for b in bl:
        print("   last", b)
    print("buchi mark:", len(bm), "barre mancanti:", sum(n for _, n in bm))
    for b in bm[:40]:
        print("   mark", b)
    ts_l = {c.ts for c in last}
    ts_m = {c.ts for c in mark}
    solo_last = sorted(ts_l - ts_m)
    solo_mark = sorted(ts_m - ts_l)
    print("barre solo in last (tolte):", len(solo_last), "solo in mark (tolte):", len(solo_mark))
    per_giorno = defaultdict(int)
    for t in solo_last:
        per_giorno[giorno(t)[:10]] += 1
    print("   giorni con barre tolte:", dict(per_giorno))
    # controllo di coerenza: high >= max(open, close), low <= min(open, close), prezzi positivi
    cattive = [c for c in last if not (c.low <= min(c.open, c.close) <= max(c.open, c.close) <= c.high and c.low > 0)]
    print("candele last incoerenti:", len(cattive))
    cattive_m = [c for c in mark if not (c.low <= min(c.open, c.close) <= max(c.open, c.close) <= c.high and c.low > 0)]
    print("candele mark incoerenti:", len(cattive_m))

    # funding
    fd = dati.carica_funding_dettaglio("SOLUSDT", INIZIO, FINE)
    print("funding: settlement", len(fd), "da", giorno(fd[0][0]), "a", giorno(fd[-1][0]))
    print("   intervalli dichiarati:", dati.intervallo_funding(fd))
    fs = dati.carica_funding("SOLUSDT", INIZIO, FINE)
    distanze = defaultdict(int)
    for (t1, _), (t2, _) in zip(fs, fs[1:]):
        distanze[round((t2 - t1) / 3_600_000)] += 1
    print("   distanze fra settlement (ore arrotondate: quante):", dict(distanze))
    tassi = [r for _, r in fs]
    print("   tasso medio %.6f, min %.6f, max %.6f" % (sum(tassi) / len(tassi), min(tassi), max(tassi)))
    fuori_griglia = [giorno(t) for t, _ in fs if t % (8 * 3_600_000) not in range(0, 60_000)]
    print("   settlement fuori dalla griglia di 8 ore (oltre 1 minuto):", len(fuori_griglia), fuori_griglia[:10])

    # volume in USDT dalle candele 1d (colonna quote_volume)
    righe = []
    for p in sorted((dati.RADICE_DEFAULT / "data/insample/SOLUSDT/klines/1d").glob("*.zip")):
        for r in dati.righe_csv_da_zip(p):
            righe.append((dati.normalizza_ts(r[0]), float(r[7])))
    righe = sorted(set(righe))
    per_anno = defaultdict(list)
    per_mese = defaultdict(list)
    for ts, qv in righe:
        d = datetime.fromtimestamp(ts / 1000, tz=timezone.utc)
        per_anno[d.year].append(qv)
        per_mese[(d.year, d.month)].append(qv)
    print("candele 1d:", len(righe))
    for a in sorted(per_anno):
        print("   volume medio giornaliero %d: %.0f milioni USDT (%d giorni)" % (a, sum(per_anno[a]) / len(per_anno[a]) / 1e6, len(per_anno[a])))
    sotto = []
    for m in sorted(per_mese):
        media = sum(per_mese[m]) / len(per_mese[m])
        print("   mese %d-%02d: %.1f milioni (%d giorni)" % (m[0], m[1], media / 1e6, len(per_mese[m])))
        if media < 20e6:
            sotto.append("%d-%02d" % m)
    print("mesi sotto 20 milioni USDT al giorno:", sotto)

    imp = dati.registra_impronte("SOLUSDT")
    imp_btc = dati.registra_impronte("BTCUSDT")
    print("impronte SOLUSDT:", len(imp), "BTCUSDT:", len(imp_btc))
    btc = dati.carica_candele("BTCUSDT", "15m", date(2020, 1, 1), FINE)
    bb = buchi(btc, MS15)
    print("BTC 15m:", len(btc), "buchi:", len(bb), "barre mancanti:", sum(n for _, n in bb))
    for b in bb:
        print("   btc", b)
