"""Fase 0, punto 3: buchi, barre tolte dall'allineamento, funding, volume per anno e per mese.

Scrive un riassunto in research/data/insample/GALAUSDT/fase0_uscita.json (fuori da git):
fase0_dati.md si scrive da li'.
"""

import json
from datetime import datetime, timezone

from research.src import dati
from research.campagne.GALAUSDT.codice import comune

TF = ["15m", "30m", "1h", "2h", "4h", "6h", "8h", "12h", "1d"]


def data(ts: int) -> str:
    return datetime.fromtimestamp(ts / 1000, tz=timezone.utc).strftime("%Y-%m-%d %H:%M")


def intervalli(ts_lista, ms):
    """Raggruppa ts consecutivi (a distanza ms) in intervalli di date."""
    out = []
    for ts in ts_lista:
        if out and ts - out[-1][1] == ms:
            out[-1][1] = ts
        else:
            out.append([ts, ts])
    return [[data(a), data(b), (b - a) // ms + 1] for a, b in out]


def main() -> None:
    uscita = {}
    for tf in TF:
        s = dati.carica_serie_allineate("GALAUSDT", tf, comune.INIZIO, comune.FINE_IN_SAMPLE)
        c = s["candele"]
        ms = comune.MS[tf]
        buchi = []
        for a, b in zip(c, c[1:]):
            if b.ts - a.ts != ms:
                buchi.append([data(a.ts), data(b.ts), (b.ts - a.ts) // ms - 1])
        btc = dati.carica_candele("BTCUSDT", tf, comune.INIZIO, comune.FINE_IN_SAMPLE)
        ts_btc = {x.ts for x in btc}
        uscita[tf] = {
            "barre_tenute": len(c),
            "prima": data(c[0].ts), "ultima": data(c[-1].ts),
            "n_tolte_last": s["n_tolte_last"], "tolte_last": intervalli(s["tolte_last"], ms),
            "n_tolte_mark": s["n_tolte_mark"], "tolte_mark": intervalli(s["tolte_mark"], ms),
            "buchi_dopo_allineamento": buchi,
            "n_volume_mancante": s["n_volume_mancante"],
            "barre_costruzione": sum(1 for x in c if x.close_ts <= comune.FINE_COSTRUZIONE_TS),
            "btc_barre": len(btc), "btc_mancanti_sui_ts_gala": sum(1 for x in c if x.ts not in ts_btc),
        }
        print(tf, len(c), s["n_tolte_last"], s["n_tolte_mark"], len(buchi), flush=True)
    righe = dati.carica_funding_dettaglio("GALAUSDT", comune.INIZIO, comune.FINE_IN_SAMPLE)
    uscita["funding"] = {
        "n": len(righe), "primo": data(righe[0][0]), "ultimo": data(righe[-1][0]),
        "intervalli": [[data(t), h] for t, h in dati.intervallo_funding(righe)],
        "tasso_medio": sum(r[2] for r in righe) / len(righe),
        "tasso_min": min(r[2] for r in righe), "tasso_max": max(r[2] for r in righe),
    }
    vm = comune.volume_mensile()
    uscita["volume_mensile_usdt"] = {f"{a}-{m:02d}": v for (a, m), v in sorted(vm.items())}
    per_anno = {}
    for (a, m), v in vm.items():
        per_anno.setdefault(a, []).append(v)
    # media per anno pesata sui giorni: ricalcolata dai file giornalieri
    giorni_anno = {}
    for anno, mese in dati.mesi_del_periodo(comune.INIZIO, comune.FINE_IN_SAMPLE):
        p = dati.percorso_mese("GALAUSDT", "klines", "1d", anno, mese)
        if p.is_file():
            giorni_anno.setdefault(anno, []).extend(dati.volume_usdt_da_zip(p).values())
    uscita["volume_medio_giornaliero_per_anno"] = {str(a): sum(v) / len(v) for a, v in giorni_anno.items()}
    uscita["giorni_per_anno"] = {str(a): len(v) for a, v in giorni_anno.items()}
    uscita["mesi_esclusi"] = [f"{a}-{m:02d}" for a, m in comune.mesi_esclusi()]
    uscita["checksum_mancanti"] = list(dati.CHECKSUM_MANCANTI)
    (comune.CARTELLA_DATI / "fase0_uscita.json").write_text(json.dumps(uscita, indent=1), encoding="utf-8")
    print("fatto", flush=True)


if __name__ == "__main__":
    main()
