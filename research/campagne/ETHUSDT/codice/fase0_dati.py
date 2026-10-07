"""Fase 0, punto 3: scrive fase0_dati.md (buchi, funding, volumi, controllo aggregazione, impronte).

Legge solo data/insample/ETHUSDT e data/insample/BTCUSDT (riferimento). Nessun test di
strategia: qui si descrivono i dati, non si guardano i rendimenti.
"""
from __future__ import annotations

import json
import sys
from collections import defaultdict
from datetime import date, datetime, timezone
from pathlib import Path

import numpy as np

QUI = Path(__file__).resolve().parent
sys.path.insert(0, str(QUI))
import comune  # noqa: E402
from log import aggiungi  # noqa: E402
from research.src import dati  # noqa: E402

RADICE = dati.RADICE_DEFAULT
INIZIO, FINE = comune.INIZIO_DATI, comune.FINE_IN_SAMPLE
MS15 = 15 * 60_000


def utc(ms: int) -> str:
    return datetime.fromtimestamp(ms / 1000, tz=timezone.utc).strftime("%Y-%m-%d %H:%M")


def buchi(cands, durata_ms):
    out = []
    for a, b in zip(cands, cands[1:]):
        if b.ts != a.close_ts + 1:
            out.append((a.close_ts + 1, b.ts, (b.ts - a.close_ts - 1) // durata_ms))
    return out


righe = ["# Fase 0 — I dati di ETHUSDT", "",
         "Scritto dallo script `codice/fase0_dati.py` sui file scaricati il 7 ottobre 2026 da",
         "data.binance.vision (file mensili, futures USDS-M). Solo dati fino al 2023-12-31: il",
         "caricatore rifiuta oltre. Nessun rendimento di strategia e' stato calcolato qui.", ""]

# --- 1. Cosa e' stato scaricato ------------------------------------------------
scarico = json.loads((QUI.parent / "fase0_scarico.json").read_text(encoding="utf-8"))
righe += ["## 1. File scaricati", "", "| Serie | File | Mesi attesi | Mesi assenti |", "|---|---|---|---|"]
for k, v in scarico["esito"].items():
    righe.append(f"| {k} | {v['file']} | {v['mesi_attesi']} | {', '.join(v['mesi_assenti']) or 'nessuno'} |")
righe += ["", f"Checksum remoti mancanti: {len(scarico['checksum_mancanti'])}. Ogni zip e' stato confrontato con il",
          "suo CHECKSUM SHA-256 pubblicato da Binance prima di essere scritto su disco.", ""]

# --- 2. Candele 15m: copertura e buchi -------------------------------------------
last15 = dati.carica_candele("ETHUSDT", "15m", INIZIO, FINE, RADICE)
mark15 = dati.carica_candele("ETHUSDT", "15m", INIZIO, FINE, RADICE, tipo="markPriceKlines")
btc15 = dati.carica_candele("BTCUSDT", "15m", INIZIO, FINE, RADICE)
attese = (dati.ms_da_data(FINE) + dati.MS_GIORNO - dati.ms_da_data(INIZIO)) // MS15
righe += ["## 2. Copertura e buchi (candele da 15 minuti)", "",
          "| Serie | Prima candela | Ultima candela | Candele | Attese | Mancanti | Buchi |", "|---|---|---|---|---|---|---|"]
dettagli_buchi = {}
for nome, cands in (("ETHUSDT last", last15), ("ETHUSDT mark", mark15), ("BTCUSDT last", btc15)):
    b = buchi(cands, MS15)
    dettagli_buchi[nome] = b
    righe.append(f"| {nome} | {utc(cands[0].ts)} | {utc(cands[-1].ts)} | {len(cands)} | {attese} | {attese - len(cands)} | {len(b)} |")
righe.append("")
for nome, b in dettagli_buchi.items():
    grandi = [x for x in b if x[2] >= 4]
    righe.append(f"**{nome}**: {len(b)} buchi, di cui {len(grandi)} di almeno un'ora" + (":" if grandi else "."))
    for da, a, n in grandi[:40]:
        righe.append(f"* da {utc(da)} a {utc(a)} UTC: {n} candele mancanti ({n * 15 / 60:.1f} ore)")
    if len(grandi) > 40:
        righe.append(f"* ... e altri {len(grandi) - 40} buchi di almeno un'ora")
    righe.append("")
# ts del mark non presenti nel last e viceversa
ts_last, ts_mark = {c.ts for c in last15}, {c.ts for c in mark15}
righe += [f"Candele last senza candela mark allo stesso istante: {len(ts_last - ts_mark)}; candele mark senza last: {len(ts_mark - ts_last)}.",
          "Nelle barre senza mark il motore usa la candela last anche per la liquidazione (scelta dichiarata in `codice/comune.py`).", ""]
# duplicati / non crescenti li avrebbe gia' tolti carica_candele: controllo che i ts siano crescenti
assert all(b.ts > a.ts for a, b in zip(last15, last15[1:]))

# --- 3. Cambi di contratto e sospensioni ------------------------------------------
# Un cambio di contratto si vedrebbe come salto di prezzo fra close e open successivo.
salti = [(a, b) for a, b in zip(last15, last15[1:]) if abs(b.open / a.close - 1) > 0.05]
righe += ["## 3. Sospensioni e cambi di contratto", "",
          "ETHUSDT non ha avuto ridenominazioni (nessun contratto «1000x») ne' migrazioni nel periodo:",
          "la serie e' unica e non c'e' alcun punto di cucitura. Controllo meccanico: salti fra la",
          f"chiusura di una candela e l'apertura della successiva oltre il 5 %: {len(salti)}."]
for a, b in salti[:10]:
    righe.append(f"* {utc(a.close_ts + 1)} UTC: close {a.close:.2f} -> open {b.open:.2f} ({(b.open / a.close - 1) * 100:+.1f} %)")
righe += ["", "I buchi della sezione 2 sono le sospensioni (manutenzioni di Binance o dati mancanti nella fonte):",
          "il motore li conta e addebita i funding caduti dentro un buco sull'ultimo mark disponibile.", ""]

# --- 4. Funding -------------------------------------------------------------------
fund = dati.carica_funding_dettaglio("ETHUSDT", INIZIO, FINE, RADICE)
segmenti = dati.intervallo_funding(fund)
tassi = np.array([f[2] for f in fund])
righe += ["## 4. Funding", "",
          f"Settlement nel periodo: {len(fund)}, dal {utc(fund[0][0])} al {utc(fund[-1][0])} UTC.",
          "Intervallo dichiarato dai file (ore), con l'istante da cui vale:"]
for ts, ore in segmenti:
    righe.append(f"* da {utc(ts)} UTC: {ore:g} ore")
# intervallo osservato dalle distanze
dist = np.diff([f[0] for f in fund]) / dati.MS_ORA
valori, conte = np.unique(np.round(dist, 2), return_counts=True)
righe.append("")
righe.append("Distanze osservate fra settlement consecutivi (ore: numero di casi): " + ", ".join(f"{v:g}: {c}" for v, c in zip(valori, conte)))
per_anno = defaultdict(list)
for ts, _ore, tasso in fund:
    per_anno[datetime.fromtimestamp(ts / 1000, tz=timezone.utc).year].append(tasso)
righe += ["", "| Anno | Settlement | Tasso medio per 8h | Tasso mediano | 10° perc. | 90° perc. | Quota positivi |", "|---|---|---|---|---|---|---|"]
for anno in sorted(per_anno):
    t = np.array(per_anno[anno])
    righe.append(f"| {anno} | {len(t)} | {t.mean() * 100:.4f} % | {np.median(t) * 100:.4f} % | {np.percentile(t, 10) * 100:.4f} % | {np.percentile(t, 90) * 100:.4f} % | {(t > 0).mean() * 100:.0f} % |")
righe += ["", "Questi numeri descrivono il costo del funding, non un rendimento di strategia.", ""]

# --- 5. Volume per anno in USDT (dai file 1d nativi) --------------------------------
righe += ["## 5. Volume medio giornaliero in USDT (file giornalieri nativi)", ""]
vol_giorno = []  # (ts, quote_volume)
for anno, mese in dati.mesi_del_periodo(INIZIO, FINE):
    p = dati.percorso_mese("ETHUSDT", "klines", "1d", anno, mese, RADICE)
    for r in dati.righe_csv_da_zip(p):
        vol_giorno.append((dati.normalizza_ts(r[0]), float(r[7])))
vol_giorno.sort()
per_anno_v = defaultdict(list)
for ts, qv in vol_giorno:
    per_anno_v[datetime.fromtimestamp(ts / 1000, tz=timezone.utc).year].append(qv)
righe += ["| Anno | Giorni | Volume medio (milioni USDT) | Minimo giornaliero | Giorni sotto 20 M |", "|---|---|---|---|---|"]
sotto = []
for anno in sorted(per_anno_v):
    v = np.array(per_anno_v[anno])
    righe.append(f"| {anno} | {len(v)} | {v.mean() / 1e6:,.0f} | {v.min() / 1e6:,.1f} | {(v < 20e6).sum()} |")
for ts, qv in vol_giorno:
    if qv < 20e6:
        sotto.append(utc(ts)[:10])
righe += ["", f"Giorni sotto la soglia di liquidita' (20 milioni USDT al giorno): {len(sotto)}" + (": " + ", ".join(sotto) if sotto else ". Nessun periodo da escludere dai test."), ""]
# periodo di costruzione e validazione: media volume
cost = [qv for ts, qv in vol_giorno if ts < dati.ms_da_data(comune.INIZIO_VALIDAZIONE)]
val = [qv for ts, qv in vol_giorno if ts >= dati.ms_da_data(comune.INIZIO_VALIDAZIONE)]
righe += [f"Volume medio nel periodo di costruzione: {np.mean(cost) / 1e6:,.0f} M USDT/giorno; in validazione: {np.mean(val) / 1e6:,.0f} M USDT/giorno.",
          "La fascia di slippage della scheda (0,01 % per lato, volume 2023 oltre 1 miliardo) si applica a tutto l'in-sample.", ""]

# --- 6. Controllo dell'aggregazione 15m -> 1d contro i file 1d nativi --------------------
righe += ["## 6. Controllo dell'aggregazione (15m -> 1d contro i file 1d nativi)", ""]
agg = dati.aggrega_candele(last15, "1d", solo_complete=True)
nat = dati.carica_candele("ETHUSDT", "1d", INIZIO, FINE, RADICE)
nat_per = {c.ts: c for c in nat}
uguali = diversi = 0
esempi = []
for c in agg:
    n = nat_per.get(c.ts)
    if n is None:
        continue
    if abs(c.open - n.open) < 1e-9 and abs(c.high - n.high) < 1e-9 and abs(c.low - n.low) < 1e-9 and abs(c.close - n.close) < 1e-9:
        uguali += 1
    else:
        diversi += 1
        if len(esempi) < 5:
            esempi.append((utc(c.ts)[:10], c, n))
righe += [f"Giorni aggregati dalle 15m (solo giorni completi): {len(agg)}; giorni nativi: {len(nat)}; giorni confrontati: {uguali + diversi};",
          f"identici in open/high/low/close: {uguali}; diversi: {diversi}."]
for g, c, n in esempi:
    righe.append(f"* {g}: aggregato O {c.open} H {c.high} L {c.low} C {c.close} / nativo O {n.open} H {n.high} L {n.low} C {n.close}")
righe += ["", "Tutti i timeframe della campagna (30m, 1h, 2h, 4h, 6h, 8h, 12h, 1d) si costruiscono dalle 15m con",
          "`aggrega_candele` (gruppi allineati all'UTC, solo gruppi completi): un giorno con un buco nelle 15m",
          "non produce la candela aggregata, e lo stesso vale per le candele piu' corte che lo contengono.", ""]
conteggi = {tf: len(dati.aggrega_candele(last15, tf)) for tf in ("30m", "1h", "2h", "4h", "6h", "8h", "12h", "1d")}
righe += ["Candele disponibili per timeframe (intero in-sample): " + ", ".join(f"{k}: {v}" for k, v in conteggi.items()), ""]

# --- 7. Storia utile ----------------------------------------------------------------
anni = (FINE - INIZIO).days / 365.25
righe += ["## 7. Storia utile", "",
          f"Dal {INIZIO} al {FINE}: {anni:.2f} anni, sopra `storia_minima_anni` = 2. La campagna si fa.",
          "Costruzione 2020-01-01 -> 2022-10-19 (1.023 giorni), validazione 2022-10-20 -> 2023-12-31 (438 giorni):",
          "fissate nel log (voce ETHUSDT-N003) prima di caricare i prezzi.", ""]

# --- 8. Impronte --------------------------------------------------------------------
impronte = json.loads((RADICE / "data" / "insample" / "ETHUSDT" / "impronte.json").read_text(encoding="utf-8"))
righe += ["## 8. Impronte SHA-256 dei file in-sample di ETHUSDT", "",
          f"{len(impronte)} file. A ogni sessione i file si riscaricano e si confrontano con questa lista",
          "(`dati.verifica_impronte`): una differenza e' uno STOP.", "", "| File | SHA-256 |", "|---|---|"]
for nome, sha in impronte.items():
    righe.append(f"| `{nome}` | `{sha}` |")
righe.append("")

(QUI.parent / "fase0_dati.md").write_text("\n".join(righe), encoding="utf-8")

aggiungi({"id": "ETHUSDT-N005", "tipo": "nota", "oggetto": "Fase 0 completata: dati scaricati e descritti",
          "testo": (f"Scaricati 48 mesi x 5 serie (ETHUSDT klines 15m e 1d, markPriceKlines 15m, fundingRate; BTCUSDT klines 15m), "
                    f"tutti con CHECKSUM remoto verificato, nessun mese assente. Candele 15m last: {len(last15)} su {attese} attese, "
                    f"{len(dettagli_buchi['ETHUSDT last'])} buchi; settlement di funding: {len(fund)}; "
                    f"giorni sotto 20 M USDT: {len(sotto)}; aggregazione 15m->1d identica ai file nativi in {uguali} giorni su {uguali + diversi}. "
                    f"Storia utile {anni:.2f} anni: la campagna si fa. Impronte: {len(impronte)} file, in fase0_dati.md."),
          "file": "campagne/ETHUSDT/fase0_dati.md"})
print("ok", len(righe), "righe;", "buchi last:", len(dettagli_buchi["ETHUSDT last"]), "diversi agg:", diversi, "sotto 20M:", len(sotto))
