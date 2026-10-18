"""Passo 1, punti 2-4: i fatti dei dati di LINKUSDT e le impronte, scritti in fase0_dati.md.

Della validazione escono solo conteggi (dati.fatti_passo1_3, l'eccezione prevista dal Passo 1).
I prezzi si leggono solo sul periodo di costruzione (dati.serie_4_con_conteggi), per le candele anomale.
Avanzamento ed esito in data/insample/LINKUSDT/passo1_fatti.txt (ultima riga: FINE o ERRORE).
"""
import hashlib
import json
import sys
import traceback
from datetime import date, datetime, timezone
from pathlib import Path

import numpy as np
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))
from research.src import dati  # noqa: E402

SIMBOLO = "LINKUSDT"
TIMEFRAME = ("15m", "30m", "1h", "2h", "4h", "6h", "8h", "12h", "1d")
RADICE = dati.RADICE_DEFAULT
CARTELLA_DATI = RADICE / "data" / "insample" / SIMBOLO
USCITA = RADICE / "campagne" / "LINK6" / "fase0_dati.md"
AVANZAMENTO = CARTELLA_DATI / "passo1_fatti.txt"
FINE_COSTRUZIONE = date(2022, 9, 30)

# Soglie descrittive per segnalare le candele anomale della costruzione (non decidono nulla).
SOGLIA_ESCURSIONE_1D = 0.25   # (massimo - minimo) / apertura della candela giornaliera
SOGLIA_CORPO_1H = 0.10        # |chiusura / apertura - 1| della candela di 1 ora
SOGLIA_MARK_LAST_1H = 0.02    # |chiusura mark / chiusura last - 1| della candela di 1 ora


def scrivi(riga):
    with AVANZAMENTO.open("a", encoding="utf-8") as f:
        f.write(riga + "\n")


def utc(ts_ms):
    return datetime.fromtimestamp(int(ts_ms) / 1000, tz=timezone.utc).strftime("%Y-%m-%d %H:%M")


def it(testo):
    """Numero gia' formattato in stile inglese -> stile italiano (1,234.5 -> 1.234,5)."""
    return testo.replace(",", "\0").replace(".", ",").replace("\0", ".")


def durata_testo(minuti):
    if minuti % 1440 == 0:
        return f"{minuti // 1440} g"
    if minuti % 60 == 0:
        return f"{minuti // 60} h"
    return f"{minuti} min"


def main():
    parametri = yaml.safe_load((RADICE / "config" / "parametri_4.yaml").read_text(encoding="utf-8"))
    fatti = dati.fatti_passo1_3(SIMBOLO, RADICE, TIMEFRAME)
    scrivi("fatti_passo1_3: ok")

    # Impronte (sezione 12) e impronta d'insieme come in parametri_4.yaml.
    impronte = dati.registra_impronte(SIMBOLO, RADICE)
    elenco = "\n".join(f"{nome} {impronta}" for nome, impronta in sorted(impronte.items()))
    varianti_elenco = {
        "righe 'nome impronta' unite da a capo": elenco,
        "righe 'nome impronta' unite da a capo, a capo finale": elenco + "\n",
        "righe 'nome  impronta' (due spazi), a capo finale": "".join(
            f"{n}  {i}\n" for n, i in sorted(impronte.items())),
        "righe 'impronta  nome' (due spazi), a capo finale": "".join(
            f"{i}  {n}\n" for n, i in sorted(impronte.items())),
    }
    attesa = parametri["fonte_dati"]["impronta_d_insieme_linkusdt"]
    insieme = {k: hashlib.sha256(v.encode("utf-8")).hexdigest() for k, v in varianti_elenco.items()}
    combacia = [k for k, v in insieme.items() if v == attesa]
    scrivi(f"impronte: {len(impronte)} file; combacia con parametri_4.yaml: {combacia or 'nessuna forma'}")

    # Serie di costruzione: mark sostituiti, candele ferme in coda, funding, candele anomale.
    costruzione = {}
    serie_1h = serie_1d = None
    for tf in TIMEFRAME:
        serie, conteggi = dati.serie_4_con_conteggi(SIMBOLO, tf, date(2020, 1, 1), FINE_COSTRUZIONE, RADICE)
        costruzione[tf] = conteggi
        if tf == "1h":
            serie_1h = serie
        if tf == "1d":
            serie_1d = serie
        scrivi(f"serie di costruzione {tf}: ok")

    anomale_1d = []
    escursione = (serie_1d.high - serie_1d.low) / serie_1d.open
    for i in np.flatnonzero(escursione >= SOGLIA_ESCURSIONE_1D):
        anomale_1d.append((utc(serie_1d.ts[i])[:10], escursione[i], serie_1d.close[i] / serie_1d.open[i] - 1))
    corpo = serie_1h.close / serie_1h.open - 1
    anomale_1h = [(utc(serie_1h.ts[i]), corpo[i]) for i in np.flatnonzero(np.abs(corpo) >= SOGLIA_CORPO_1H)]
    scarto_mark = serie_1h.mark_close / serie_1h.close - 1
    anomale_mark = [(utc(serie_1h.ts[i]), scarto_mark[i])
                    for i in np.flatnonzero(np.abs(scarto_mark) >= SOGLIA_MARK_LAST_1H)]
    incoerenti = {}
    volume_zero = {}
    for tf in TIMEFRAME:
        s = dati.serie_4(SIMBOLO, tf, date(2020, 1, 1), FINE_COSTRUZIONE, RADICE)
        alto = np.maximum(s.open, s.close)
        basso = np.minimum(s.open, s.close)
        incoerenti[tf] = int(np.sum((s.high < alto) | (s.low > basso) | (s.low <= 0)))
        volume_zero[tf] = [utc(t) for t in s.ts[s.volume <= 0]]

    # Volume medio giornaliero 2023 (sezione 4bis: volume dell'anno / giorni dell'anno).
    volume_anno = fatti["volume_medio_giornaliero_2023_usdt"] * fatti["giorni_volume_2023"]
    volume_medio = volume_anno / 365
    fasce = [(1e9, 0.0001), (2e8, 0.0002), (5e7, 0.0005), (0, 0.0010)]
    fascia = next(s for soglia, s in fasce if volume_medio > soglia)
    slippage_param = parametri["costi"]["slippage_per_lato"]

    r = []
    r.append("# Fase 0: i dati di LINKUSDT (Passo 1 del protocollo 4)")
    r.append("")
    r.append(f"Scritto da `codice/passo1_fatti.py` il {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M')} UTC, "
             "sui file scaricati da `codice/passo1_scarica.py` (fonte: "
             f"{parametri['fonte_dati']['archivio']}, file mensili, CHECKSUM di Binance controllato a ogni scarico). "
             "Della validazione (dal 2022-10-01 al 2023-12-31) qui ci sono solo conteggi; nessun dato dopo il 2023-12-31.")
    r.append("")
    r.append("## 1. Prima candela")
    r.append("")
    r.append("| Timeframe | Prima candela last (UTC) | Prima candela mark (UTC) |")
    r.append("|---|---|---|")
    for tf in TIMEFRAME:
        v = fatti["timeframe"][tf]
        r.append(f"| {tf} | {(v['klines']['prima_candela'] or '-')[:16].replace('T', ' ')} | "
                 f"{(v['markPriceKlines']['prima_candela'] or '-')[:16].replace('T', ' ')} |")
    r.append("")
    r.append(f"Valore in `parametri_4.yaml` (inizio della costruzione): {parametri['periodi']['costruzione']['da']}.")
    r.append("")
    r.append("## 2. Buchi nei dati")
    r.append("")
    r.append("Un buco e' una o piu' candele mancanti fra due candele presenti (dalla prima candela al 2023-12-31).")
    r.append("")
    for tipo, nome in (("klines", "last"), ("markPriceKlines", "mark")):
        r.append(f"### Candele {nome}")
        r.append("")
        r.append("| Timeframe | Buchi | Elenco (inizio UTC, durata) |")
        r.append("|---|---|---|")
        for tf in TIMEFRAME:
            buchi = fatti["timeframe"][tf][tipo]["buchi"]
            minuti_tf = dati.durata_intervallo(tf) // 60000
            elenco_b = "; ".join(f"{b['da'][:16].replace('T', ' ')}, {durata_testo(b['candele_mancanti'] * minuti_tf)}"
                                 for b in buchi) or "nessuno"
            r.append(f"| {tf} | {len(buchi)} | {elenco_b} |")
        r.append("")
    r.append("### Candele mark sostituite dal last nel periodo di costruzione (9.6)")
    r.append("")
    r.append("| Timeframe | Candele last | Mark sostituite dal last | Giorni | Mark senza last (tolte) | Candele ferme in coda tolte |")
    r.append("|---|---|---|---|---|---|")
    for tf in TIMEFRAME:
        c = costruzione[tf]
        r.append(f"| {tf} | {c['candele']} | {c['mark_sostituite']} | {', '.join(c['giorni_mark_sostituiti']) or '-'} | "
                 f"{c['mark_senza_last']} | {c['candele_ferme_in_coda_tolte']} |")
    r.append("")
    r.append("Nella validazione le candele mark mancanti si leggono dalla tabella dei buchi mark qui sopra.")
    r.append("")
    r.append("## 3. Funding")
    r.append("")
    r.append(f"Regolamenti dalla prima candela al 2023-12-31: {fatti['regolamenti_funding']}.")
    r.append("")
    r.append("| Da (UTC) | Ore di intervallo |")
    r.append("|---|---|")
    for x in fatti["intervalli_funding"]:
        r.append(f"| {x['da'][:16].replace('T', ' ')} | {x['ore']} |")
    r.append("")
    r.append(f"Regolamenti per intervallo nel periodo di costruzione: "
             f"{costruzione['1h']['intervalli_funding_ore']}. In `parametri_4.yaml` (2020-2023): "
             f"{parametri['motore']['intervalli_funding_linkusdt']}.")
    r.append("")
    r.append("## 4. Volume medio giornaliero 2023")
    r.append("")
    r.append(f"Giorni del 2023 con la candela giornaliera: {fatti['giorni_volume_2023']} su 365. "
             f"Volume del 2023 diviso 365 giorni (sezione 4bis): {it(f'{volume_medio:,.0f}')} USDT al giorno "
             "(colonna quote_volume delle candele giornaliere).")
    r.append("")
    r.append(f"Fascia di slippage che ne segue (sezione 6): {it(f'{fascia * 100:.2f}')}% per lato. "
             f"In `parametri_4.yaml`: {it(f'{slippage_param * 100:.2f}')}% per lato. "
             f"Esito: {'confermata' if abs(fascia - slippage_param) < 1e-12 else 'DIVERSA: STOP'}.")
    r.append("")
    r.append("## 5. Candele per timeframe")
    r.append("")
    r.append("| Timeframe | Last in costruzione | Last in validazione | Mark in costruzione | Mark in validazione |")
    r.append("|---|---|---|---|---|")
    for tf in TIMEFRAME:
        v = fatti["timeframe"][tf]
        r.append(f"| {tf} | {v['klines']['costruzione']} | {v['klines']['validazione']} | "
                 f"{v['markPriceKlines']['costruzione']} | {v['markPriceKlines']['validazione']} |")
    r.append("")
    r.append("## 6. Candele anomale nel periodo di costruzione (si tengono tutte)")
    r.append("")
    r.append("Soglie solo descrittive, scelte per segnalare, non per togliere: candela giornaliera con escursione "
             f"(massimo meno minimo, diviso l'apertura) di almeno il {SOGLIA_ESCURSIONE_1D:.0%}; candela di 1 ora con "
             f"chiusura lontana dall'apertura di almeno il {SOGLIA_CORPO_1H:.0%}; candela di 1 ora con la chiusura del "
             f"mark lontana da quella del last di almeno il {SOGLIA_MARK_LAST_1H:.0%}.")
    r.append("")
    r.append(f"Candele giornaliere con escursione di almeno il {SOGLIA_ESCURSIONE_1D:.0%}: {len(anomale_1d)}.")
    r.append("")
    r.append("| Giorno | Escursione | Chiusura sull'apertura |")
    r.append("|---|---|---|")
    for g, e, c in anomale_1d:
        r.append(f"| {g} | {it(f'{e:.1%}')} | {it(f'{c:+.1%}')} |")
    r.append("")
    r.append(f"Candele di 1 ora con chiusura lontana dall'apertura di almeno il {SOGLIA_CORPO_1H:.0%}: {len(anomale_1h)}"
             + (": " + "; ".join(f"{t} ({it(f'{c:+.1%}')})" for t, c in anomale_1h) if anomale_1h else "") + ".")
    r.append("")
    r.append(f"Candele di 1 ora con il mark lontano dal last di almeno il {SOGLIA_MARK_LAST_1H:.0%}: {len(anomale_mark)}"
             + (": " + "; ".join(f"{t} ({it(f'{c:+.1%}')})" for t, c in anomale_mark) if anomale_mark else "") + ".")
    r.append("")
    r.append("Candele incoerenti (massimo sotto apertura o chiusura, minimo sopra, minimo non positivo), per timeframe: "
             + ", ".join(f"{tf} {n}" for tf, n in incoerenti.items()) + ".")
    r.append("")
    r.append("Candele a volume zero in mezzo alla serie, per timeframe: "
             + "; ".join(f"{tf} {len(v)}" + (f" ({', '.join(v)})" if v else "") for tf, v in volume_zero.items()) + ".")
    r.append("")
    r.append("## 7. Impronte dei file (sezione 12)")
    r.append("")
    r.append(f"File in-sample: {len(impronte)} (in `parametri_4.yaml`: {parametri['fonte_dati']['file_insample_linkusdt']}).")
    r.append("")
    r.append("Impronta d'insieme in `parametri_4.yaml`: `" + attesa + "`. Calcolata qui sullo SHA-256 dell'elenco dei "
             "file in ordine di nome, in quattro forme dell'elenco:")
    r.append("")
    for k, v in insieme.items():
        r.append(f"- {k}: `{v}`" + (" (combacia)" if v == attesa else ""))
    r.append("")
    r.append("Esito: " + (f"combacia ({combacia[0]})." if combacia else
                          "NESSUNA forma combacia: da chiarire con il coordinamento."))
    r.append("")
    r.append("SHA-256 di ogni file (percorso relativo a `research/data/insample/LINKUSDT/`):")
    r.append("")
    r.append("```text")
    for nome, impronta in sorted(impronte.items()):
        r.append(f"{impronta}  {nome}")
    r.append("```")
    r.append("")
    USCITA.write_text("\n".join(r), encoding="utf-8")

    riassunto = {
        "file": len(impronte), "impronta_insieme_combacia": combacia,
        "prima_candela_min": fatti["prima_candela"],
        "volume_medio_2023": volume_medio, "giorni_volume_2023": fatti["giorni_volume_2023"],
        "fascia": fascia, "fascia_parametri": slippage_param,
        "intervalli_funding": fatti["intervalli_funding"], "regolamenti": fatti["regolamenti_funding"],
        "anomale_1d": len(anomale_1d), "anomale_1h": len(anomale_1h), "anomale_mark": len(anomale_mark),
        "incoerenti": incoerenti, "volume_zero": {k: len(v) for k, v in volume_zero.items()},
    }
    scrivi(json.dumps(riassunto, ensure_ascii=False))
    scrivi("FINE")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        scrivi(traceback.format_exc())
        scrivi("ERRORE")
