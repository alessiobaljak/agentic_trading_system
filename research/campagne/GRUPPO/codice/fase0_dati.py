"""Fase 0 del gruppo (regole.md, sezione 2, punti 6 e 9): tabella per moneta in fase0_dati.md.

Uso: python3 -u fase0_dati.py [TF ...]   (i timeframe oltre 1d di cui contare le barre tolte dall'allineamento)

Per ogni moneta: mesi presenti di last, mark e funding rispetto agli attesi (dal primo mese della scheda al
2023-12); giorni mancanti nelle serie 1d; barre tolte dall'allineamento di last e mark (1d e i timeframe
chiesti); intervallo del funding nel tempo; volume medio giornaliero in USDT per anno (colonna quote_volume
dei file 1d del last); mesi sotto la liquidita' minima (dati.mesi_sotto_liquidita, la funzione unica);
controllo della storia (primo giorno in comune fra last e mark 1d prima del 2022-01-01); il salto di prezzo
giornaliero piu' grande (indizio di un cambio di contratto, sezione 2, punto 9).
Per BTCUSDT: barre presenti e mancanti di ogni timeframe ammesso.
Scrive campagne/GRUPPO/fase0_dati.md e campagne/GRUPPO/lavoro/fase0_dati.json. Nessun calcolo d'esame.
"""
import hashlib
import json
import math
import sys
from datetime import date, datetime, timezone

from comune import CARTELLA_GRUPPO, RADICE_RICERCA, dati, monete, schede

FINE = date(2023, 12, 31)
LIMITE_STORIA = date(2022, 1, 1)
TIMEFRAME_AMMESSI = ("15m", "30m", "1h", "2h", "4h", "6h", "8h", "12h", "1d")


def giorno(ts):
    return datetime.fromtimestamp(ts / 1000, tz=timezone.utc).date()


def intervalli_di_giorni(giorni):
    """Giorni (date ordinate) compressi in intervalli 'AAAA-MM-GG..AAAA-MM-GG'."""
    out = []
    for g in giorni:
        if out and (g - out[-1][1]).days == 1:
            out[-1][1] = g
        else:
            out.append([g, g])
    return [f"{a}" if a == b else f"{a}..{b}" for a, b in out]


def mesi_presenti(simbolo, tipo, intervallo, inizio):
    attesi, presenti, mancanti = 0, 0, []
    for anno, mese in dati.mesi_del_periodo(inizio, FINE):
        attesi += 1
        if dati.percorso_mese(simbolo, tipo, intervallo, anno, mese, RADICE_RICERCA).is_file():
            presenti += 1
        else:
            mancanti.append(f"{anno:04d}-{mese:02d}")
    return attesi, presenti, mancanti


def studio_moneta(simbolo, scheda, timeframe_extra):
    inizio = scheda["primo_mese"]
    voce = {"primo_mese": str(inizio), "slippage_per_lato": scheda["slippage_per_lato"]}
    for nome, tipo, intervallo in (("last_1d", "klines", "1d"), ("mark_1d", "markPriceKlines", "1d"),
                                   ("funding", "fundingRate", None)):
        attesi, presenti, mancanti = mesi_presenti(simbolo, tipo, intervallo, inizio)
        voce[f"mesi_{nome}"] = {"attesi": attesi, "presenti": presenti, "mancanti": mancanti}
    last = dati.carica_candele(simbolo, "1d", inizio, FINE, RADICE_RICERCA, "klines")
    mark = dati.carica_candele(simbolo, "1d", inizio, FINE, RADICE_RICERCA, "markPriceKlines")
    for nome, serie in (("last", last), ("mark", mark)):
        if serie:
            presenti = {giorno(c.ts) for c in serie}
            primo = min(presenti)
            tutti = [date.fromordinal(o) for o in range(primo.toordinal(), FINE.toordinal() + 1)]
            mancanti = [g for g in tutti if g not in presenti]
            voce[f"{nome}_1d"] = {"primo_giorno": str(primo), "ultimo_giorno": str(max(presenti)),
                                   "giorni": len(presenti), "giorni_mancanti": len(mancanti),
                                   "intervalli_mancanti": intervalli_di_giorni(mancanti)}
        else:
            voce[f"{nome}_1d"] = {"primo_giorno": None, "giorni": 0}
    allineate = {}
    for tf in ("1d",) + tuple(timeframe_extra):
        s = dati.carica_serie_allineate(simbolo, tf, inizio, FINE, RADICE_RICERCA)
        allineate[tf] = {"barre": len(s["candele"]), "tolte_last": s["n_tolte_last"], "tolte_mark": s["n_tolte_mark"],
                         "intervalli_tolte_last": intervalli_di_giorni(sorted({giorno(t) for t in s["tolte_last"]})),
                         "intervalli_tolte_mark": intervalli_di_giorni(sorted({giorno(t) for t in s["tolte_mark"]})),
                         "primo_giorno_in_comune": str(giorno(s["candele"][0].ts)) if s["candele"] else None}
    voce["allineamento"] = allineate
    primo_comune = allineate["1d"]["primo_giorno_in_comune"]
    voce["storia_ok"] = primo_comune is not None and date.fromisoformat(primo_comune) < LIMITE_STORIA
    funding = dati.carica_funding_dettaglio(simbolo, inizio, FINE, RADICE_RICERCA)
    voce["funding"] = {"regolamenti": len(funding),
                       "primo": str(giorno(funding[0][0])) if funding else None,
                       "intervalli_ore": [[str(giorno(ts)), ore] for ts, ore in dati.intervallo_funding(funding)]}
    volumi = {}
    for anno, mese in dati.mesi_del_periodo(inizio, FINE):
        percorso = dati.percorso_mese(simbolo, "klines", "1d", anno, mese, RADICE_RICERCA)
        if percorso.is_file():
            for ts, v in dati.volume_usdt_da_zip(percorso).items():
                volumi.setdefault(ts, v)
    per_anno = {}
    for ts, v in volumi.items():
        per_anno.setdefault(giorno(ts).year, []).append(v)
    voce["volume_medio_per_anno_musdt"] = {str(a): round(sum(v) / len(v) / 1e6, 1) for a, v in sorted(per_anno.items())}
    voce["mesi_sotto_liquidita"] = [f"{a:04d}-{m:02d}" for a, m in dati.mesi_sotto_liquidita(simbolo, inizio, FINE, RADICE_RICERCA)]
    salto, quando = 0.0, None
    for a, b in zip(last, last[1:]):
        if a.close > 0 and b.close > 0:
            x = abs(math.log(b.close / a.close))
            if x > salto:
                salto, quando = x, str(giorno(b.ts))
    voce["salto_giornaliero_massimo"] = {"rapporto": round(math.exp(salto), 3), "giorno": quando}
    return voce


def studio_btc():
    out = {}
    for tf in TIMEFRAME_AMMESSI:
        candele = dati.carica_candele("BTCUSDT", tf, date(2020, 1, 1), FINE, RADICE_RICERCA, "klines")
        durata = dati.durata_intervallo(tf)
        attese = (dati.ms_da_data(date(2024, 1, 1)) - dati.ms_da_data(date(2020, 1, 1))) // durata
        ts = [c.ts for c in candele]
        buchi = sum(1 for a, b in zip(ts, ts[1:]) if b - a != durata)
        out[tf] = {"barre": len(candele), "attese": attese, "mancanti": attese - len(candele), "buchi": buchi,
                   "prima": str(giorno(ts[0])) if ts else None, "ultima": str(giorno(ts[-1])) if ts else None}
    return out


def main():
    extra = sys.argv[1:]
    sch = schede()
    risultati = {s: studio_moneta(s, sch[s], extra) for s in monete()}
    btc = studio_btc()
    (CARTELLA_GRUPPO / "lavoro" / "fase0_dati.json").write_text(json.dumps({"monete": risultati, "btc": btc},
                                                                          ensure_ascii=False, indent=1))
    print("monete studiate:", len(risultati))
    print("storia non superata:", [s for s, v in risultati.items() if not v["storia_ok"]])
    print("salti oltre 3x:", {s: v["salto_giornaliero_massimo"] for s, v in risultati.items()
                               if v["salto_giornaliero_massimo"]["rapporto"] > 3 or v["salto_giornaliero_massimo"]["rapporto"] < 1 / 3})
    print("btc:", json.dumps(btc))


if __name__ == "__main__":
    main()
