"""Fase 3 (studio dei fallimenti) per le varianti long dell'idea C, solo sui trade di COSTRUZIONE salvati da gruppo.py.

Legge trade/<id>_costruzione.jsonl e, per ogni trade, il giorno di segnale (il giorno prima dell'ingresso: ordine
limite valido un giorno), il rendimento di Bitcoin quel giorno, il rendimento della moneta, la distanza (ritardo) e il
rendimento di Bitcoin nei 5 giorni dopo, dalle candele giornaliere del last della Fase 0 (dati.carica_candele, mai
oltre il 2023-01-16). Raggruppa gli R per: anno d'uscita, esito (stop o segnale), giorno di segnale (quanti giorni
forti, quanto pesano i migliori), ampiezza del ritardo, ampiezza del giorno forte, andamento di Bitcoin dopo. Nessun
calcolo d'esame: solo medie e conteggi descrittivi per decidere un ritocco (regola 6).

Uso: fase3_ritardo.py <id> [<id> ...]
"""

import json
import statistics
import sys
from datetime import date, datetime, timezone
from pathlib import Path

RADICE = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(RADICE))

from research.src import dati  # noqa: E402

CARTELLA = Path(__file__).resolve().parents[1]
GIORNO = 86_400_000
FINE = date(2023, 1, 16)


def chiusure(simbolo, inizio):
    return {c.ts: c.close for c in dati.carica_candele(simbolo, "1d", inizio, FINE)}


def media(xs):
    return round(statistics.fmean(xs), 3) if xs else None


def gruppi(trade, chiave):
    out = {}
    for t in trade:
        out.setdefault(chiave(t), []).append(t["r"])
    return {k: {"n": len(v), "r_medio": media(v)} for k, v in sorted(out.items(), key=lambda x: str(x[0]))}


def quartili(trade, campo):
    valori = sorted(t[campo] for t in trade if t.get(campo) is not None)
    if len(valori) < 8:
        return {}
    tagli = [valori[len(valori) * q // 4] for q in (1, 2, 3)]
    def fascia(x):
        return sum(x >= c for c in tagli)
    return gruppi([t for t in trade if t.get(campo) is not None], lambda t: f"Q{fascia(t[campo]) + 1}")


def analizza(id_variante):
    trade = [json.loads(r) for r in (CARTELLA / "trade" / f"{id_variante}_costruzione.jsonl").read_text().splitlines() if r]
    btc = chiusure("BTCUSDT", date(2020, 1, 1))
    cache = {}
    for t in trade:
        s = t["simbolo"]
        if s not in cache:
            cache[s] = chiusure(s, date(2020, 1, 1))
        g = t["ts_entrata"] - GIORNO
        c = cache[s]
        t["giorno_segnale"] = datetime.fromtimestamp(g / 1000, tz=timezone.utc).date().isoformat()
        t["anno"] = datetime.fromtimestamp(t["ts_uscita"] / 1000, tz=timezone.utc).year
        if g in btc and g - GIORNO in btc and g in c and g - GIORNO in c:
            rb = btc[g] / btc[g - GIORNO] - 1
            rc = c[g] / c[g - GIORNO] - 1
            t["r_btc"], t["ritardo"] = rb, rb - rc
        if g in btc and g + 5 * GIORNO in btc:
            t["btc_5_giorni_dopo"] = btc[g + 5 * GIORNO] / btc[g] - 1
    per_giorno = {}
    for t in trade:
        per_giorno.setdefault(t["giorno_segnale"], []).append(t["r"])
    giorni = sorted(((g, len(v), sum(v)) for g, v in per_giorno.items()), key=lambda x: -x[2])
    r_tutti = [t["r"] for t in trade]
    senza_3_giorni = [t["r"] for t in trade if t["giorno_segnale"] not in {g for g, _, _ in giorni[:3]}]
    return {
        "trade": len(trade), "r_medio": media(r_tutti),
        "per_anno_uscita": gruppi(trade, lambda t: t["anno"]),
        "per_esito": gruppi(trade, lambda t: t["esito"]),
        "giorni_di_segnale": len(giorni),
        "giorni_migliori": [{"giorno": g, "trade": n, "somma_r": round(s, 2)} for g, n, s in giorni[:5]],
        "giorni_peggiori": [{"giorno": g, "trade": n, "somma_r": round(s, 2)} for g, n, s in giorni[-5:]],
        "r_medio_senza_i_3_giorni_migliori": media(senza_3_giorni),
        "per_quartile_del_ritardo": quartili(trade, "ritardo"),
        "per_quartile_del_giorno_forte": quartili(trade, "r_btc"),
        "per_segno_di_btc_nei_5_giorni_dopo": gruppi([t for t in trade if "btc_5_giorni_dopo" in t],
                                                     lambda t: "btc su" if t["btc_5_giorni_dopo"] > 0 else "btc giu"),
        "trade_per_giorno_di_segnale_mediana": statistics.median(n for _, n, _ in giorni),
    }


def main():
    esito = {i: analizza(i) for i in sys.argv[1:]}
    (CARTELLA / "lavoro" / "fase3_ritardo.json").write_text(json.dumps(esito, indent=1, ensure_ascii=False) + "\n",
                                                            encoding="utf-8")
    print(json.dumps(esito, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
