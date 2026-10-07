"""Fase 0, punto 3: esame dei dati in-sample di BTCUSDT per fase0_dati.md.

Stampa (e salva in codice/fase0_analisi.json): candele attese e presenti per
serie, buchi (barre mancanti, con inizio e durata), coerenza fra 15m last e
15m mark, confronto fra l'aggregazione 15m -> 1d e le candele 1d native,
intervallo del funding nel tempo, volume medio giornaliero per anno in USDT,
giorni sotto la soglia di liquidita' (20 milioni di USDT al giorno).
"""
from __future__ import annotations

import json
import sys
from collections import defaultdict
from datetime import date, datetime, timezone
from pathlib import Path

RADICE_REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(RADICE_REPO))
from research.src import dati  # noqa: E402

SIMBOLO = "BTCUSDT"
INIZIO, FINE = date(2020, 1, 1), date(2023, 12, 31)
SOGLIA_LIQ = 20_000_000.0


def ts_iso(ts_ms: int) -> str:
    return datetime.fromtimestamp(ts_ms / 1000, tz=timezone.utc).strftime("%Y-%m-%d %H:%M")


def buchi(candele, durata_ms):
    out = []
    for a, b in zip(candele, candele[1:]):
        if b.ts != a.ts + durata_ms:
            mancanti = (b.ts - a.ts) // durata_ms - 1
            out.append({"da": ts_iso(a.ts + durata_ms), "a": ts_iso(b.ts - durata_ms), "barre_mancanti": int(mancanti)})
    return out


esito = {}
last15 = dati.carica_candele(SIMBOLO, "15m", INIZIO, FINE)
mark15 = dati.carica_candele(SIMBOLO, "15m", INIZIO, FINE, tipo="markPriceKlines")
d1 = dati.carica_candele(SIMBOLO, "1d", INIZIO, FINE)
giorni_totali = (FINE - INIZIO).days + 1
attese_15m = giorni_totali * 96

esito["serie"] = {
    "last_15m": {"attese": attese_15m, "presenti": len(last15), "prima": ts_iso(last15[0].ts), "ultima": ts_iso(last15[-1].ts), "buchi": buchi(last15, 15 * 60_000)},
    "mark_15m": {"attese": attese_15m, "presenti": len(mark15), "prima": ts_iso(mark15[0].ts), "ultima": ts_iso(mark15[-1].ts), "buchi": buchi(mark15, 15 * 60_000)},
    "last_1d": {"attese": giorni_totali, "presenti": len(d1), "buchi": buchi(d1, 86_400_000)},
}

# allineamento last/mark
ts_last = {c.ts for c in last15}
ts_mark = {c.ts for c in mark15}
esito["allineamento_last_mark"] = {
    "solo_last": [ts_iso(t) for t in sorted(ts_last - ts_mark)][:20],
    "n_solo_last": len(ts_last - ts_mark),
    "solo_mark": [ts_iso(t) for t in sorted(ts_mark - ts_last)][:20],
    "n_solo_mark": len(ts_mark - ts_last),
}

# scarto fra mark e last (close), per sapere quanto differiscono
scarti = []
per_ts_mark = {c.ts: c for c in mark15}
for c in last15:
    m = per_ts_mark.get(c.ts)
    if m:
        scarti.append(abs(m.close - c.close) / c.close)
scarti.sort()
esito["scarto_mark_last_close"] = {"mediana": scarti[len(scarti) // 2], "p99": scarti[int(len(scarti) * 0.99)], "max": scarti[-1]}

# aggregazione 15m -> 1d contro 1d nativo
agg = dati.aggrega_candele(last15, "1d")
per_ts_d1 = {c.ts: c for c in d1}
diff = []
for c in agg:
    n = per_ts_d1.get(c.ts)
    if n is None:
        diff.append({"ts": ts_iso(c.ts), "motivo": "manca la 1d nativa"})
        continue
    for campo in ("open", "high", "low", "close"):
        if abs(getattr(c, campo) - getattr(n, campo)) > 1e-9:
            diff.append({"ts": ts_iso(c.ts), "campo": campo, "aggregato": getattr(c, campo), "nativo": getattr(n, campo)})
    if abs(c.volume - n.volume) > 1e-3 * max(1.0, n.volume):
        diff.append({"ts": ts_iso(c.ts), "campo": "volume", "aggregato": c.volume, "nativo": n.volume})
esito["aggregazione_1d"] = {"giorni_aggregati_completi": len(agg), "giorni_nativi": len(d1), "differenze": diff[:30], "n_differenze": len(diff)}

# funding
righe = dati.carica_funding_dettaglio(SIMBOLO, INIZIO, FINE)
esito["funding"] = {
    "n_settlement": len(righe),
    "primo": ts_iso(righe[0][0]), "ultimo": ts_iso(righe[-1][0]),
    "intervalli_dichiarati": [(ts_iso(ts), ore) for ts, ore in dati.intervallo_funding(righe)],
}
# intervallo osservato fra settlement consecutivi
conteggio = defaultdict(int)
for a, b in zip(righe, righe[1:]):
    conteggio[round((b[0] - a[0]) / 3_600_000, 2)] += 1
esito["funding"]["distanze_osservate_ore"] = dict(sorted(conteggio.items(), key=lambda kv: -kv[1])[:8])
tassi = sorted(r[2] for r in righe)
esito["funding"]["tasso"] = {"mediana": tassi[len(tassi) // 2], "medio": sum(tassi) / len(tassi), "min": tassi[0], "max": tassi[-1]}
per_anno_f = defaultdict(list)
for ts, _ore, tasso in righe:
    per_anno_f[datetime.fromtimestamp(ts / 1000, tz=timezone.utc).year].append(tasso)
esito["funding"]["medio_per_anno"] = {a: sum(v) / len(v) for a, v in sorted(per_anno_f.items())}
esito["funding"]["quota_positivi_per_anno"] = {a: sum(1 for x in v if x > 0) / len(v) for a, v in sorted(per_anno_f.items())}

# volume in USDT per giorno (dal quote_volume: la Candela non lo porta, quindi close*volume base)
# Nota: Candela.volume e' il volume in moneta base; USDT ~ volume * close.
vol_giorno = {}
for c in d1:
    vol_giorno[datetime.fromtimestamp(c.ts / 1000, tz=timezone.utc).date()] = c.volume * c.close
per_anno = defaultdict(list)
for g, v in vol_giorno.items():
    per_anno[g.year].append(v)
esito["volume_usdt_giorno"] = {
    "stima": "volume in moneta base x close del giorno (approssima il quote_volume)",
    "medio_per_anno": {a: sum(v) / len(v) for a, v in sorted(per_anno.items())},
    "minimo_per_anno": {a: min(v) for a, v in sorted(per_anno.items())},
    "giorni_sotto_soglia": [g.isoformat() for g, v in sorted(vol_giorno.items()) if v < SOGLIA_LIQ],
}
# prezzo per anno (solo descrizione dei dati, non un risultato)
per_anno_p = defaultdict(list)
for c in d1:
    per_anno_p[datetime.fromtimestamp(c.ts / 1000, tz=timezone.utc).year].append(c)
esito["prezzo_per_anno"] = {a: {"primo_open": v[0].open, "ultimo_close": v[-1].close, "min": min(c.low for c in v), "max": max(c.high for c in v)} for a, v in sorted(per_anno_p.items())}

out = Path(__file__).resolve().parent / "fase0_analisi.json"
out.write_text(json.dumps(esito, indent=1, ensure_ascii=False, default=str))
print(json.dumps(esito, indent=1, ensure_ascii=False, default=str))
