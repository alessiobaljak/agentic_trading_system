"""Fase 0 punti 2-3: barre tolte dall'allineamento, buchi, funding, volume, mesi illiquidi, impronte.
Scrive campagne/FTMUSDT/fase0_dati.md e impronte.json."""
import hashlib
import json
from datetime import date, datetime, timezone

import numpy as np

from comune import CARTELLA, PERIODI, PRIMO_GIORNO, SIMBOLO, dati
import quadro

TF = ["15m", "30m", "1h", "2h", "4h", "6h", "8h", "12h", "1d"]
FINE = date(2023, 12, 31)


def d(ts):
    return datetime.fromtimestamp(int(ts) / 1000, tz=timezone.utc).strftime("%Y-%m-%d %H:%M")


def intervalli(ts_list, ms):
    out = []
    for t in ts_list:
        if out and t - out[-1][1] <= ms:
            out[-1][1] = t
        else:
            out.append([t, t])
    return out


righe = ["# FTMUSDT — dati della Fase 0", "",
         f"Scritto da `codice/fase0_analisi.py`. Periodo: dal {PRIMO_GIORNO} al {FINE} (in-sample). "
         f"Costruzione dal {PERIODI['inizio']} al {PERIODI['fine_costruzione']} ({PERIODI['giorni_costruzione']} giorni); "
         f"validazione dal {PERIODI['inizio_validazione']} al {PERIODI['fine_validazione']}.", "",
         "Fonte: data.binance.vision, file mensili (klines, markPriceKlines, fundingRate), scaricati con "
         "`dati.scarica_periodo` con il controllo del CHECKSUM remoto. Nessun file oltre il 2023-12.", ""]

righe += ["## Barre per timeframe e barre tolte dall'allineamento last/mark (`carica_serie_allineate`)", "",
          "| timeframe | barre tenute | tolte dal last (mancano nel mark) | tolte dal mark (mancano nel last) | buchi nella serie tenuta | prima barra | ultima barra |",
          "|---|---|---|---|---|---|---|"]
dettagli = []
for tf in TF:
    s = dati.carica_serie_allineate(SIMBOLO, tf, PRIMO_GIORNO, FINE)
    c = s["candele"]
    ms = quadro.MS[tf]
    buchi = sum(1 for a, b in zip(c, c[1:]) if b.ts > a.close_ts + 1)
    righe.append(f"| {tf} | {len(c)} | {s['n_tolte_last']} | {s['n_tolte_mark']} | {buchi} | {d(c[0].ts)} | {d(c[-1].ts)} |")
    for nome in ("tolte_last", "tolte_mark"):
        if s[nome]:
            iv = intervalli(s[nome], ms)
            dettagli.append(f"* {tf}, {nome}: " + "; ".join(f"{d(a)} → {d(b)}" for a, b in iv[:30])
                            + (f" (e altri {len(iv) - 30} intervalli)" if len(iv) > 30 else ""))
    gap = [(a.close_ts + 1, b.ts) for a, b in zip(c, c[1:]) if b.ts > a.close_ts + 1]
    if gap:
        dettagli.append(f"* {tf}, buchi nella serie tenuta: " + "; ".join(f"{d(a)} → {d(b)}" for a, b in gap[:30])
                        + (f" (e altri {len(gap) - 30})" if len(gap) > 30 else ""))
righe += ["", "Intervalli (date UTC di apertura delle barre):", ""] + (dettagli or ["* nessuno"]) + [""]

f = dati.carica_funding_dettaglio(SIMBOLO, PRIMO_GIORNO, FINE)
seg = dati.intervallo_funding(f)
tassi = np.array([x[2] for x in f])
righe += ["## Funding", "",
          f"Settlement: {len(f)}, dal {d(f[0][0])} al {d(f[-1][0])}. Intervalli dichiarati dal file nel tempo: "
          + "; ".join(f"dal {d(t)}: {o} ore" for t, o in seg) + ".",
          f"Distanza fra settlement consecutivi (ore): " +
          str(sorted({round((b[0] - a[0]) / 3_600_000, 2) for a, b in zip(f, f[1:])})) + ".",
          f"Tasso: media {tassi.mean():.6f}, mediana {np.median(tassi):.6f}, minimo {tassi.min():.6f}, massimo {tassi.max():.6f}.", ""]

vol = quadro.volumi_giornalieri()
per_anno, per_mese = {}, {}
for t, v in vol.items():
    dt = datetime.fromtimestamp(t / 1000, tz=timezone.utc)
    per_anno.setdefault(dt.year, []).append(v)
    per_mese.setdefault(f"{dt.year:04d}-{dt.month:02d}", []).append(v)
righe += ["## Volume (quote_volume dei file 1d del last, `volume_usdt_da_zip`)", "",
          "| anno | giorni | volume medio giornaliero (milioni di USDT) |", "|---|---|---|"]
for a in sorted(per_anno):
    righe.append(f"| {a} | {len(per_anno[a])} | {np.mean(per_anno[a]) / 1e6:.1f} |")
illiq = sorted(quadro.mesi_illiquidi())
righe += ["", "Mesi sotto la liquidità minima (media giornaliera < 20 milioni di USDT): "
          + (", ".join(f"{m} ({np.mean(per_mese[m]) / 1e6:.1f} M)" for m in illiq) if illiq else "nessuno") + ".", "",
          "Filtro (uguale per conta_trade, test e baseline (a); stesse barre vietate alla (b)): nessuna posizione si apre su "
          "un segnale di una barra che apre in uno di quei mesi; una posizione già aperta esce con la sua uscita "
          "(`quadro.Serie.illiquida`). I mesi non si tolgono dalla serie e non spostano le date di costruzione e validazione.", ""]

impronte = dati.calcola_impronte(SIMBOLO)
testo = json.dumps(impronte, indent=1, sort_keys=True) + "\n"
(CARTELLA / "impronte.json").write_text(testo)
righe += ["## Impronte", "",
          f"{len(impronte)} file zip in `data/insample/FTMUSDT/`; le impronte SHA-256 sono in `impronte.json` "
          f"(questa cartella). Impronta di `impronte.json`: {hashlib.sha256(testo.encode()).hexdigest()}.", ""]
btc = dati.calcola_impronte("BTCUSDT")
righe += [f"Riferimento di mercato BTCUSDT (solo last, dal 2020-01): {len(btc)} file; impronta dell'elenco ordinato "
          f"delle impronte: {hashlib.sha256(json.dumps(btc, sort_keys=True).encode()).hexdigest()}.", ""]
righe += ["## Cambi di contratto e sospensioni", "",
          "La scheda dà un solo simbolo (FTMUSDT) per tutto l'in-sample: nessuna cucitura. Le sospensioni si vedono "
          "come buchi nelle tabelle sopra.", "",
          "## Storia utile", "",
          f"Dal 2020-09-01 al 2023-12-31: {PERIODI['giorni']} giorni (3,3 anni), sopra i 2 anni di `storia_minima_anni`.", ""]
(CARTELLA / "fase0_dati.md").write_text("\n".join(righe))
print("\n".join(righe))
