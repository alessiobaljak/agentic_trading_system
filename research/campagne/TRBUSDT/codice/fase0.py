"""Fase 0, punti 2-3: impronte, buchi, barre tolte dall'allineamento, funding, volume, mesi illiquidi.

Scrive ``impronte.json`` (TRBUSDT e BTCUSDT) e ``fase0_numeri.json`` nella cartella della campagna.
Nessun risultato di strategia: solo fatti dei dati.
"""

import json
from datetime import date, datetime, timezone

from research.src import dati
from research.campagne.TRBUSDT.codice.banco import CARTELLA, PERIODI, RADICE, SOGLIA_LIQUIDITA, SIMBOLO
from research.campagne.TRBUSDT.codice.scarica import TIMEFRAME

FINE = date(2023, 12, 31)


def iso(ts):
    return datetime.fromtimestamp(ts / 1000, tz=timezone.utc).strftime("%Y-%m-%d %H:%M")


def intervalli(ts_lista, durata):
    """Comprime una lista di ts in intervalli contigui [da, a]."""
    out = []
    for ts in ts_lista:
        if out and ts == out[-1][1] + durata:
            out[-1][1] = ts
        else:
            out.append([ts, ts])
    return [(iso(a), iso(b), (b - a) // durata + 1) for a, b in out]


def buchi(candele, durata):
    out = []
    for p, d in zip(candele, candele[1:]):
        if d.ts > p.ts + durata:
            out.append((iso(p.ts + durata), iso(d.ts - durata), (d.ts - p.ts) // durata - 1))
    return out


def main():
    impronte = {"TRBUSDT": dati.calcola_impronte("TRBUSDT", RADICE), "BTCUSDT": dati.calcola_impronte("BTCUSDT", RADICE)}
    with open(CARTELLA / "impronte.json", "w", encoding="utf-8") as f:
        json.dump(impronte, f, indent=1, sort_keys=True)
    numeri = {"n_file": {k: len(v) for k, v in impronte.items()}, "timeframe": {}}
    for tf in TIMEFRAME:
        durata = dati.durata_intervallo(tf)
        last = dati.carica_candele(SIMBOLO, tf, PERIODI["inizio"], FINE, RADICE, "klines")
        mark = dati.carica_candele(SIMBOLO, tf, PERIODI["inizio"], FINE, RADICE, "markPriceKlines")
        s = dati.carica_serie_allineate(SIMBOLO, tf, PERIODI["inizio"], FINE, RADICE)
        btc = dati.carica_candele("BTCUSDT", tf, PERIODI["inizio"], FINE, RADICE, "klines")
        numeri["timeframe"][tf] = {
            "barre_last": len(last), "barre_mark": len(mark), "barre_tenute": len(s["candele"]),
            "prima_barra": iso(last[0].ts) if last else None, "ultima_barra": iso(last[-1].ts) if last else None,
            "n_tolte_last": s["n_tolte_last"], "tolte_last": intervalli(s["tolte_last"], durata),
            "n_tolte_mark": s["n_tolte_mark"], "tolte_mark": intervalli(s["tolte_mark"], durata),
            "buchi_last": buchi(last, durata), "buchi_tenute": len(buchi(s["candele"], durata)),
            "barre_btc": len(btc), "buchi_btc": len(buchi(btc, durata)),
        }
        print(tf, numeri["timeframe"][tf]["barre_tenute"], flush=True)
    righe = dati.carica_funding_dettaglio(SIMBOLO, PERIODI["inizio"], FINE, RADICE)
    numeri["funding"] = {
        "n_settlement": len(righe), "primo": iso(righe[0][0]) if righe else None, "ultimo": iso(righe[-1][0]) if righe else None,
        "intervalli_dichiarati": [(iso(t), o) for t, o in dati.intervallo_funding(righe)],
        "intervalli_da_distanza": [(iso(t), o) for t, o in dati.intervallo_funding([(t, r) for t, _o, r in righe])],
    }
    # volume in USDT dai file 1d del last, su tutti i giorni
    per_mese, per_anno = {}, {}
    for p in dati._percorsi_presenti(SIMBOLO, "klines", "1d", PERIODI["inizio"], FINE, RADICE):
        for ts, v in dati.volume_usdt_da_zip(p).items():
            g = datetime.fromtimestamp(ts / 1000, tz=timezone.utc)
            per_mese.setdefault(f"{g.year:04d}-{g.month:02d}", []).append(v)
            per_anno.setdefault(str(g.year), []).append(v)
    numeri["volume_medio_giorno_usdt_per_anno"] = {a: round(sum(v) / len(v)) for a, v in sorted(per_anno.items())}
    numeri["volume_medio_giorno_usdt_per_mese"] = {m: round(sum(v) / len(v)) for m, v in sorted(per_mese.items())}
    numeri["mesi_sotto_soglia"] = sorted(m for m, v in per_mese.items() if sum(v) / len(v) < SOGLIA_LIQUIDITA)
    numeri["giorni_per_mese"] = {m: len(v) for m, v in sorted(per_mese.items())}
    numeri["checksum_mancanti"] = list(dati.CHECKSUM_MANCANTI)
    with open(CARTELLA / "fase0_numeri.json", "w", encoding="utf-8") as f:
        json.dump(numeri, f, indent=1, ensure_ascii=False)
    print("fatto")


if __name__ == "__main__":
    main()
