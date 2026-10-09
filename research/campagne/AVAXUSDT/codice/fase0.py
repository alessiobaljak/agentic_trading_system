"""Fase 0 punti 2-3: controlli dei dati scaricati. Scrive data/insample/AVAXUSDT/fase0_controlli.json.

* checksum: per ogni zip scaricato rilegge il CHECKSUM remoto e lo confronta col file su disco
  (lo scarico lo ha gia' fatto, ma il suo elenco dei CHECKSUM mancanti non e' leggibile
  dalla sessione: lo si rifa' qui);
* per ogni timeframe: barre del last e del mark, barre tolte dall'allineamento con gli
  intervalli di date, buchi nella serie allineata, prima e ultima barra;
* funding: numero di settlement, intervalli nel tempo, distanze anomale fra settlement;
* volume medio giornaliero in USDT per anno e per mese, mesi sotto la soglia;
* BTCUSDT: barre per timeframe;
* impronte: registra_impronte per le due monete.
"""
import json
import sys
from datetime import date, datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import comune  # noqa: E402
from comune import CARTELLA_DATI, FINE_IN_SAMPLE, PRIMO_GIORNO, dati  # noqa: E402

TF = ["15m", "30m", "1h", "2h", "4h", "6h", "8h", "12h", "1d"]
USCITA = CARTELLA_DATI / "fase0_controlli.json"
AVANZAMENTO = CARTELLA_DATI / "fase0_avanzamento.txt"


def d(ts):
    return datetime.fromtimestamp(ts / 1000, tz=timezone.utc).strftime("%Y-%m-%d %H:%M")


def intervalli_ts(lista, passo):
    """Raggruppa ts consecutivi (distanza = passo) in intervalli [primo, ultimo]."""
    out = []
    for t in lista:
        if out and t - out[-1][1] == passo:
            out[-1][1] = t
        else:
            out.append([t, t])
    return [(d(a), d(b), (b - a) // passo + 1) for a, b in out]


def scrivi(msg):
    with AVANZAMENTO.open("a", encoding="utf-8") as f:
        f.write(msg + "\n")


def controlla_checksum(radice_simbolo: Path, simbolo: str):
    mancanti, diversi, ok = [], [], 0
    for p in sorted(radice_simbolo.rglob("*.zip")):
        rel = p.relative_to(radice_simbolo).as_posix()
        parti = rel.split("/")
        tipo = parti[0]
        nome = parti[-1]
        anno, mese = int(nome[-11:-7]), int(nome[-6:-4])
        intervallo = None if tipo == "fundingRate" else parti[1]
        url = dati.url_mese(simbolo, tipo, intervallo, anno, mese)
        testo = dati.fetch_http(dati.url_checksum(url))
        if testo is None:
            mancanti.append(rel)
            continue
        if dati.leggi_checksum(testo, url) != dati.impronta_file(p):
            diversi.append(rel)
        else:
            ok += 1
    return {"ok": ok, "senza_checksum": mancanti, "diversi": diversi}


def main():
    AVANZAMENTO.write_text("", encoding="utf-8")
    out = {}
    out["checksum_AVAXUSDT"] = controlla_checksum(CARTELLA_DATI, "AVAXUSDT")
    scrivi(f"checksum AVAX {out['checksum_AVAXUSDT']['ok']}")
    out["checksum_BTCUSDT"] = controlla_checksum(comune.RADICE_REPO / "research" / "data" / "insample" / "BTCUSDT", "BTCUSDT")
    scrivi("checksum BTC fatto")
    per_tf = {}
    for tf in TF:
        ser = dati.carica_serie_allineate("AVAXUSDT", tf, PRIMO_GIORNO, FINE_IN_SAMPLE)
        last = dati.carica_candele("AVAXUSDT", tf, PRIMO_GIORNO, FINE_IN_SAMPLE)
        mark = dati.carica_candele("AVAXUSDT", tf, PRIMO_GIORNO, FINE_IN_SAMPLE, tipo="markPriceKlines")
        btc = dati.carica_candele("BTCUSDT", tf, PRIMO_GIORNO, FINE_IN_SAMPLE)
        passo = dati.durata_intervallo(tf)
        c = ser["candele"]
        buchi = [(d(a.ts), d(b.ts), (b.ts - a.ts) // passo - 1) for a, b in zip(c, c[1:]) if b.ts > a.close_ts + 1]
        buchi_last = [(d(a.ts), d(b.ts), (b.ts - a.ts) // passo - 1) for a, b in zip(last, last[1:]) if b.ts > a.close_ts + 1]
        ts_btc = {x.ts for x in btc}
        per_tf[tf] = {
            "barre_last": len(last), "barre_mark": len(mark), "barre_allineate": len(c),
            "prima": d(c[0].ts) if c else None, "ultima": d(c[-1].ts) if c else None,
            "tolte_last": ser["n_tolte_last"], "tolte_mark": ser["n_tolte_mark"],
            "intervalli_tolte_last": intervalli_ts(ser["tolte_last"], passo),
            "intervalli_tolte_mark": intervalli_ts(ser["tolte_mark"], passo),
            "buchi_serie_allineata": len(buchi), "buchi_dettaglio": buchi[:40],
            "buchi_last": len(buchi_last), "buchi_last_dettaglio": buchi_last[:40],
            "barre_btc": len(btc), "barre_avax_senza_btc": sum(1 for x in c if x.ts not in ts_btc),
            "volume_mancante": ser["n_volume_mancante"],
        }
        scrivi(f"tf {tf} fatto")
    out["timeframe"] = per_tf
    fund = dati.carica_funding_dettaglio("AVAXUSDT", PRIMO_GIORNO, FINE_IN_SAMPLE)
    distanze = {}
    anomalie = []
    for (a, oa, _), (b, ob, _) in zip(fund, fund[1:]):
        ore = (b - a) / 3_600_000
        distanze[ore] = distanze.get(ore, 0) + 1
        if ore != oa:
            anomalie.append((d(a), d(b), ore, oa))
    out["funding"] = {
        "settlement": len(fund), "primo": d(fund[0][0]), "ultimo": d(fund[-1][0]),
        "intervalli_dichiarati": [(d(t), o) for t, o in dati.intervallo_funding(fund)],
        "distanze_ore": {str(k): v for k, v in sorted(distanze.items())},
        "distanze_diverse_dal_dichiarato": anomalie[:50], "n_distanze_diverse": len(anomalie),
        "tasso_min": min(r for _, _, r in fund), "tasso_max": max(r for _, _, r in fund),
        "settlement_sopra_0_0003": sum(1 for _, _, r in fund if r >= 0.0003),
        "settlement_negativi": sum(1 for _, _, r in fund if r < 0),
    }
    vol = comune.volume_giornaliero_usdt()
    per_anno, per_mese = {}, {}
    for ts, v in vol.items():
        g = datetime.fromtimestamp(ts / 1000, tz=timezone.utc)
        if g.date() < PRIMO_GIORNO or g.date() > FINE_IN_SAMPLE:
            continue
        per_anno.setdefault(g.year, []).append(v)
        per_mese.setdefault(f"{g.year}-{g.month:02d}", []).append(v)
    out["volume_medio_giornaliero_usdt_per_anno"] = {str(a): round(sum(v) / len(v)) for a, v in sorted(per_anno.items())}
    out["volume_medio_giornaliero_usdt_per_mese"] = {m: round(sum(v) / len(v)) for m, v in sorted(per_mese.items())}
    out["giorni_con_volume"] = len(vol)
    out["mesi_sotto_soglia"] = [f"{a}-{m:02d}" for a, m in comune.mesi_illiquidi()]
    out["impronte_AVAXUSDT"] = len(dati.registra_impronte("AVAXUSDT"))
    out["impronte_BTCUSDT"] = len(dati.registra_impronte("BTCUSDT"))
    out["sha256_impronte_json_AVAXUSDT"] = dati.impronta_file(CARTELLA_DATI / "impronte.json")
    out["sha256_impronte_json_BTCUSDT"] = dati.impronta_file(comune.RADICE_REPO / "research" / "data" / "insample" / "BTCUSDT" / "impronte.json")
    USCITA.write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
    scrivi("fine")


if __name__ == "__main__":
    main()
