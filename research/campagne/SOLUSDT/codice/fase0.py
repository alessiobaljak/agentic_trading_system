"""Fase 0, punto 3: analisi dei dati in-sample di SOLUSDT per fase0_dati.md.

Stampa: impronte registrate, buchi per timeframe, allineamento last/mark,
coerenza fra candele native e aggregate, funding (copertura e intervallo),
volume medio giornaliero in USDT per anno (colonna quote_volume dei file) e
giorni/mesi sotto la soglia di liquidita'. Non legge nulla oltre il 2023-12-31.
"""
import json
from collections import defaultdict
from datetime import date, datetime, timezone
from pathlib import Path

from research.src import dati

S = "SOLUSDT"
INI, FINE = date(2020, 9, 1), date(2023, 12, 31)
TF = ["15m", "30m", "1h", "2h", "4h", "6h", "8h", "12h", "1d"]
SOGLIA = 20_000_000


def g(ts):
    return datetime.fromtimestamp(ts / 1000, tz=timezone.utc)


def buchi(candele):
    out = []
    for a, b in zip(candele, candele[1:]):
        if b.ts > a.close_ts + 1:
            out.append((g(a.close_ts + 1).isoformat(), g(b.ts).isoformat(), round((b.ts - a.close_ts - 1) / 60000)))
    return out


# 1. impronte
impronte = dati.registra_impronte(S)
print("IMPRONTE:", len(impronte), "file")

# 2. buchi e allineamento per timeframe
riassunto = {}
for tf in TF:
    c = dati.carica_candele(S, tf, INI, FINE)
    m = dati.carica_candele(S, tf, INI, FINE, tipo="markPriceKlines")
    b = buchi(c)
    bm = buchi(m)
    ts_c, ts_m = {x.ts for x in c}, {x.ts for x in m}
    riassunto[tf] = dict(n=len(c), prima=g(c[0].ts).isoformat(), ultima=g(c[-1].close_ts + 1).isoformat(),
                         buchi=b, n_mark=len(m), buchi_mark=bm,
                         solo_last=len(ts_c - ts_m), solo_mark=len(ts_m - ts_c))
    print(tf, "last", len(c), "mark", len(m), "buchi last", len(b), "buchi mark", len(bm),
          "solo last", len(ts_c - ts_m), "solo mark", len(ts_m - ts_c))
    for x in b[:10]:
        print("   buco last:", x)
    for x in bm[:10]:
        if x not in b:
            print("   buco mark:", x)

# 3. coerenza native vs aggregate (dal 15m)
c15 = dati.carica_candele(S, "15m", INI, FINE)
for tf in ["1h", "4h", "1d"]:
    agg = {x.ts: x for x in dati.aggrega_candele(c15, tf)}
    nat = dati.carica_candele(S, tf, INI, FINE)
    diff = 0
    comuni = 0
    for x in nat:
        y = agg.get(x.ts)
        if y is None:
            continue
        comuni += 1
        if abs(x.open - y.open) > 1e-9 or abs(x.high - y.high) > 1e-9 or abs(x.low - y.low) > 1e-9 or abs(x.close - y.close) > 1e-9:
            diff += 1
    print(f"coerenza {tf}: native {len(nat)}, aggregate {len(agg)}, confrontate {comuni}, diverse (OHLC) {diff}")

# 4. funding
righe = dati.carica_funding_dettaglio(S, INI, FINE)
print("FUNDING:", len(righe), "settlement, primo", g(righe[0][0]).isoformat(), "ultimo", g(righe[-1][0]).isoformat())
print("  intervalli dichiarati:", [(g(t).isoformat(), h) for t, h in dati.intervallo_funding(righe)])
coppie = [(t, r) for t, h, r in righe]
print("  intervalli dedotti dalle distanze:", [(g(t).isoformat(), h) for t, h in dati.intervallo_funding(coppie)][:20])
# settlement mancanti rispetto a 8h regolari
mancanti = []
for (t1, _, _), (t2, _, _) in zip(righe, righe[1:]):
    if t2 - t1 > 8 * 3600_000 + 60_000:
        mancanti.append((g(t1).isoformat(), g(t2).isoformat(), round((t2 - t1) / 3600_000, 1)))
print("  distanze oltre 8h:", len(mancanti), mancanti[:15])
tassi = [r for _, _, r in righe]
per_anno = defaultdict(list)
for t, _, r in righe:
    per_anno[g(t).year].append(r)
for a in sorted(per_anno):
    v = per_anno[a]
    print(f"  funding {a}: n={len(v)} media={sum(v)/len(v):.6f} min={min(v):.6f} max={max(v):.6f} quota positivi={sum(1 for x in v if x>0)/len(v):.2f}")

# 5. volume in USDT per giorno dalla colonna quote_volume dei file 1d
vol_giorno = {}
cartella = Path(dati.RADICE_DEFAULT) / "data" / "insample" / S / "klines" / "1d"
for z in sorted(cartella.glob("*.zip")):
    for riga in dati.righe_csv_da_zip(z):
        ts = dati.normalizza_ts(int(riga[0]))
        vol_giorno[g(ts).date()] = float(riga[7])
per_anno_v = defaultdict(list)
for d, v in sorted(vol_giorno.items()):
    per_anno_v[d.year].append(v)
print("VOLUME USDT/giorno per anno:")
for a in sorted(per_anno_v):
    v = per_anno_v[a]
    print(f"  {a}: giorni={len(v)} media={sum(v)/len(v)/1e6:.1f}M mediana={sorted(v)[len(v)//2]/1e6:.1f}M min={min(v)/1e6:.1f}M sotto_soglia={sum(1 for x in v if x < SOGLIA)}")
# mesi con volume medio sotto soglia
per_mese = defaultdict(list)
for d, v in vol_giorno.items():
    per_mese[(d.year, d.month)].append(v)
print("  volume medio per mese (M USDT):")
for k in sorted(per_mese):
    v = per_mese[k]
    print(f"   {k[0]}-{k[1]:02d}: {sum(v)/len(v)/1e6:.1f}" + ("  <-- SOTTO SOGLIA" if sum(v) / len(v) < SOGLIA else ""))
sotto = sorted(d for d, v in vol_giorno.items() if v < SOGLIA)
print("  giorni singoli sotto soglia:", len(sotto), sotto[:5], "...", sotto[-5:] if sotto else "")
# volume 2023 medio (verifica fascia slippage)
v23 = per_anno_v[2023]
print(f"  volume medio 2023: {sum(v23)/len(v23)/1e6:.1f}M -> fascia", "0,01%" if sum(v23)/len(v23) > 1e9 else "altra")

# 6. prezzo: estremi per anno (solo per dichiarare l'ambiente, non e' un'ipotesi)
c1d = dati.carica_candele(S, "1d", INI, FINE)
per_anno_p = defaultdict(list)
for x in c1d:
    per_anno_p[g(x.ts).year].append(x)
for a in sorted(per_anno_p):
    v = per_anno_p[a]
    print(f"  prezzo {a}: apertura {v[0].open} chiusura {v[-1].close} min {min(x.low for x in v)} max {max(x.high for x in v)}")

json.dump(riassunto, open("/tmp/claude-0/-home-user/af362999-f788-5846-9fa9-3ad76396e3b2/scratchpad/riassunto_tf.json", "w"), indent=1, default=str)
