"""Fase 0, punti 2-3: impronte, barre tolte dall'allineamento, buchi, funding, volume, mesi illiquidi.

Scrive i numeri in data/insample/XRPUSDT/fase0.json (fuori da git); fase0_dati.md li riporta.
"""
import json
from collections import defaultdict
from datetime import date, datetime, timezone

from research.src import dati

S = "XRPUSDT"
INIZIO, FINE = date(2020, 1, 1), date(2023, 12, 31)
TF = ["15m", "30m", "1h", "2h", "4h", "6h", "8h", "12h", "1d"]


def giorno(ts):
    return datetime.fromtimestamp(ts / 1000, tz=timezone.utc).strftime("%Y-%m-%d %H:%M")


def intervalli(tss, passo):
    """Comprime una lista di ts in intervalli contigui [primo, ultimo]."""
    out = []
    for t in tss:
        if out and t - out[-1][1] == passo:
            out[-1][1] = t
        else:
            out.append([t, t])
    return [[giorno(a), giorno(b), (b - a) // passo + 1] for a, b in out]


out = {}
impronte = dati.registra_impronte(S)
impronte_btc = dati.registra_impronte("BTCUSDT")
out["n_file"] = len(impronte)
out["n_file_btc"] = len(impronte_btc)

allineamento = {}
for tf in TF:
    al = dati.carica_serie_allineate(S, tf, INIZIO, FINE)
    passo = dati.durata_intervallo(tf)
    c = al["candele"]
    attese = (dati.ms_da_data(date(2024, 1, 1)) - dati.ms_da_data(INIZIO)) // passo
    buchi = []
    for a, b in zip(c, c[1:]):
        if b.ts > a.close_ts + 1:
            buchi.append([giorno(a.close_ts + 1), giorno(b.ts - 1), (b.ts - a.close_ts - 1) // passo])
    btc = dati.carica_candele("BTCUSDT", tf, INIZIO, FINE)
    allineamento[tf] = {
        "barre_tenute": len(c), "barre_attese_calendario": attese,
        "tolte_last": al["n_tolte_last"], "tolte_mark": al["n_tolte_mark"],
        "intervalli_tolte_last": intervalli(al["tolte_last"], passo),
        "intervalli_tolte_mark": intervalli(al["tolte_mark"], passo),
        "buchi_dopo_allineamento": buchi,
        "n_volume_mancante": al["n_volume_mancante"],
        "barre_btc": len(btc),
    }
out["allineamento"] = allineamento

# funding
fd = dati.carica_funding_dettaglio(S, INIZIO, FINE)
out["funding"] = {
    "n_settlement": len(fd), "primo": giorno(fd[0][0]), "ultimo": giorno(fd[-1][0]),
    "intervalli_ore": [[giorno(t), o] for t, o in dati.intervallo_funding(fd)],
    "intervalli_da_distanza": [[giorno(t), o] for t, o in dati.intervallo_funding([(t, r) for t, _o, r in fd])],
}
per_anno_f = defaultdict(list)
for t, o, r in fd:
    per_anno_f[datetime.fromtimestamp(t / 1000, tz=timezone.utc).year].append(r)
out["funding"]["media_per_anno"] = {a: sum(v) / len(v) for a, v in per_anno_f.items()}
out["funding"]["min_max"] = [min(r for _t, _o, r in fd), max(r for _t, _o, r in fd)]

# volume giornaliero in USDT dai file 1d del last, tutti i giorni
vol = {}
for anno, mese in dati.mesi_del_periodo(INIZIO, FINE):
    p = dati.percorso_mese(S, "klines", "1d", anno, mese)
    vol.update(dati.volume_usdt_da_zip(p))
per_mese = defaultdict(list)
per_anno = defaultdict(list)
for ts, v in vol.items():
    d = datetime.fromtimestamp(ts / 1000, tz=timezone.utc)
    per_mese[f"{d.year:04d}-{d.month:02d}"].append(v)
    per_anno[d.year].append(v)
out["volume_medio_giornaliero_per_anno"] = {a: sum(v) / len(v) for a, v in sorted(per_anno.items())}
out["volume_medio_giornaliero_per_mese"] = {m: sum(v) / len(v) for m, v in sorted(per_mese.items())}
out["giorni_con_volume"] = len(vol)
out["mesi_sotto_20_milioni"] = [m for m, v in sorted(per_mese.items()) if sum(v) / len(v) < 20_000_000]
out["mesi_tra_20_e_50_milioni"] = [m for m, v in sorted(per_mese.items()) if 20_000_000 <= sum(v) / len(v) < 50_000_000]

testo = json.dumps(out, indent=1, ensure_ascii=False)
(dati.RADICE_DEFAULT / "data" / "insample" / S / "fase0.json").write_text(testo + "\n")
print(json.dumps({k: v for k, v in out.items() if k != "allineamento"}, indent=1))
for tf, a in allineamento.items():
    print(tf, {k: a[k] for k in ("barre_tenute", "barre_attese_calendario", "tolte_last", "tolte_mark", "n_volume_mancante", "barre_btc")},
          "buchi", len(a["buchi_dopo_allineamento"]))
