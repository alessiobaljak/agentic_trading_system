#!/usr/bin/env python3
"""Passo 0 della seconda edizione (research/PROTOCOLLO_2.md, sezione 10, punti 2 e 6): le misure sul motore a
barre giornaliere.

A. **Funding a 1 giorno contro 8 ore** (sezione 3.4): la stessa strategia giornaliera (rottura dei 20 giorni, idea
   A1-20, long e short, ingresso a limite, stop 2,5 ATR(20), uscita sotto il minimo dei 10 giorni, uscita a tempo 60
   giorni) eseguita su BTCUSDT 2020-2023 con candele di 1 giorno e con candele di 8 ore (segnali calcolati alle
   chiusure dei giorni UTC aggregando le 8 ore; ordine limite valido 3 barre = il giorno dopo). Si confrontano, trade
   per trade (stesso giorno di segnale), il funding pagato e l'R, e i totali. Con 8 ore i settlement cadono sempre
   all'apertura di una barra (esatti); con 1 giorno due su tre cadono dentro la barra e il motore li addebita
   sull'apertura della candela mark che li contiene: la differenza e' l'approssimazione dichiarata.
B. **Distanza dello stop e costo atteso per trade** (sezione 3.2): per ognuna delle 80 monete del paniere, la
   distanza 2,5 ATR(20) / prezzo sui giorni 2020-2023 (mediana, quartili) e il costo per trade in R che ne segue con
   la fascia di scarto della scheda: (maker 0,02% + taker 0,05% + scarto d'uscita) / distanza dello stop.

Scrive misure_motore_1d.json e misure_motore_1d.md in questa cartella. Solo dati fino al 2023-12-31.
"""
from __future__ import annotations

import csv
import dataclasses
import json
import sys
import time
from datetime import date
from pathlib import Path
from statistics import median

import numpy as np

QUI = Path(__file__).resolve().parent
RADICE = QUI.parents[1]
sys.path.insert(0, str(RADICE))
from research.src import dati, motore  # noqa: E402
from research.src.motore import Parametri, Segnale  # noqa: E402

RADICE_RICERCA = RADICE / "research"
INIZIO, FINE = date(2020, 1, 1), date(2023, 12, 31)
GIORNO_MS = 86_400_000
N_ROTTURA, N_USCITA, N_ATR, K_ATR, BARRE_TEMPO = 20, 10, 20, 2.5, 60
MAKER, TAKER = 0.0002, 0.0005


def parametri(slippage: float, validita: int) -> Parametri:
    return Parametri(commissione_per_lato=TAKER, slippage_per_lato=slippage, rischio_per_trade=0.01, leva_max=2.0,
                     modalita_margine="isolated", tasso_margine_mantenimento=0.025, margine_minimo_da_liquidazione=0.8,
                     capitale_iniziale=1000.0, riempimento_intrabarra="stop_prima", moltiplicatore_costi=1.0,
                     ritardo_barre=0, ingresso="limite", limite_validita_barre=validita,
                     limite_condizione="attraversato", commissione_maker_per_lato=MAKER)


def livelli_giornalieri(giorni):
    """Array causali sui giorni: alla posizione k usano solo i giorni <= k."""
    n = len(giorni)
    h = np.array([c.high for c in giorni]); l = np.array([c.low for c in giorni]); c_ = np.array([c.close for c in giorni])
    hi20 = np.full(n, np.nan); lo20 = np.full(n, np.nan); hi10 = np.full(n, np.nan); lo10 = np.full(n, np.nan); atr = np.full(n, np.nan)
    tr = np.full(n, np.nan)
    tr[1:] = np.maximum(h[1:] - l[1:], np.maximum(abs(h[1:] - c_[:-1]), abs(l[1:] - c_[:-1])))
    for k in range(n):
        if k >= N_ROTTURA:
            hi20[k] = h[k - N_ROTTURA:k].max(); lo20[k] = l[k - N_ROTTURA:k].min()
        if k >= N_USCITA:
            hi10[k] = h[k - N_USCITA:k].max(); lo10[k] = l[k - N_USCITA:k].min()
        if k >= N_ATR:
            atr[k] = tr[k - N_ATR + 1:k + 1].mean()
    return dict(hi20=hi20, lo20=lo20, hi10=hi10, lo10=lo10, atr=atr, close=c_)


def strategia_rottura(direzione: str, giorni, indice_giorno):
    """La strategia A1-20 sui giorni. ``indice_giorno(storia)`` -> k del giorno chiuso dall'ultima barra, o None se
    l'ultima barra non chiude un giorno (8 ore) o il giorno non e' completo."""
    L = livelli_giornalieri(giorni)
    lato = 1 if direzione == "long" else -1

    def strategia(storia, pos):
        k = indice_giorno(storia)
        if k is None:
            return None
        if pos is not None:
            tenuti = (storia[-1].close_ts + 1 - pos.ts_entrata) // GIORNO_MS
            if tenuti >= BARRE_TEMPO:
                return "chiudi"
            if lato == 1 and not np.isnan(L["lo10"][k]) and L["close"][k] < L["lo10"][k]:
                return "chiudi"
            if lato == -1 and not np.isnan(L["hi10"][k]) and L["close"][k] > L["hi10"][k]:
                return "chiudi"
            return None
        if np.isnan(L["hi20"][k]) or np.isnan(L["atr"][k]):
            return None
        c = L["close"][k]
        if lato == 1 and c > L["hi20"][k]:
            return Segnale("long", stop=c - K_ATR * L["atr"][k])
        if lato == -1 and c < L["lo20"][k]:
            return Segnale("short", stop=c + K_ATR * L["atr"][k])
        return None
    return strategia


def corsa_1d(candele, mark, funding, direzione, slippage):
    def indice_giorno(storia):
        return len(storia) - 1
    ris = motore.esegui(candele, None, mark, funding, strategia_rottura(direzione, candele, indice_giorno), parametri(slippage, 1))
    return ris


def corsa_8h(candele8, mark8, funding, direzione, slippage):
    giorni = dati.aggrega_candele(candele8, "1d", solo_complete=True)
    k_per_close_ts = {g.close_ts: k for k, g in enumerate(giorni)}

    def indice_giorno(storia):
        return k_per_close_ts.get(storia[-1].close_ts)   # solo la barra che chiude un giorno completo
    ris = motore.esegui(candele8, None, mark8, funding, strategia_rottura(direzione, giorni, indice_giorno), parametri(slippage, 3))
    return ris


def riassunto(ris, ms):
    t = ris.trades
    n = len(t)
    if n == 0:
        return {"trade": 0}
    return {
        "trade": n, "saltati": ris.n_saltati,
        "r_medio": float(np.mean([x.r for x in t])),
        "r_lordo_medio": float(np.mean([x.pnl_lordo / x.rischio_iniziale for x in t])),
        "costo_medio_r": float(np.mean([(x.commissioni + x.slippage_costo) / x.rischio_iniziale for x in t])),
        "funding_medio_r": float(np.mean([x.funding_pagato / x.rischio_iniziale for x in t])),
        "funding_totale_usdt": float(sum(x.funding_pagato for x in t)),
        "pnl_totale_usdt": float(sum(x.pnl for x in t)),
        "esiti": {e: sum(1 for x in t if x.esito == e) for e in ("stop", "segnale", "fine_dati", "liquidazione", "target")},
        "durata_media_giorni": float(np.mean([(x.ts_uscita - x.ts_entrata) / GIORNO_MS for x in t])),
        "stop_medio_pct": float(np.mean([abs(x.entrata - x.stop) / x.entrata for x in t])) * 100,
    }


def confronto_trade(t1d, t8h):
    """Abbina i trade per giorno di segnale."""
    per_giorno_1d = {x.ts_segnale // GIORNO_MS: x for x in t1d}
    per_giorno_8h = {x.ts_segnale // GIORNO_MS: x for x in t8h}
    comuni = sorted(set(per_giorno_1d) & set(per_giorno_8h))
    diff_f = [per_giorno_1d[g].funding_pagato - per_giorno_8h[g].funding_pagato for g in comuni]
    diff_fr = [(per_giorno_1d[g].funding_pagato - per_giorno_8h[g].funding_pagato) / per_giorno_1d[g].rischio_iniziale for g in comuni]
    diff_r = [per_giorno_1d[g].r - per_giorno_8h[g].r for g in comuni]
    stessa_uscita = sum(1 for g in comuni if per_giorno_1d[g].esito == per_giorno_8h[g].esito)
    return {
        "comuni": len(comuni), "solo_1d": len(per_giorno_1d) - len(comuni), "solo_8h": len(per_giorno_8h) - len(comuni),
        "stessa_uscita": stessa_uscita,
        "funding_diff_media_usdt": float(np.mean(diff_f)) if comuni else None,
        "funding_diff_media_r": float(np.mean(diff_fr)) if comuni else None,
        "funding_diff_max_abs_r": float(np.max(np.abs(diff_fr))) if comuni else None,
        "r_diff_media": float(np.mean(diff_r)) if comuni else None,
        "r_diff_mediana": float(np.median(diff_r)) if comuni else None,
        "r_diff_max_abs": float(np.max(np.abs(diff_r))) if comuni else None,
    }


def parte_a():
    out = {}
    s1 = dati.carica_serie_allineate("BTCUSDT", "1d", INIZIO, FINE, RADICE_RICERCA)
    s8 = dati.carica_serie_allineate("BTCUSDT", "8h", INIZIO, FINE, RADICE_RICERCA)
    funding = dati.carica_funding("BTCUSDT", INIZIO, FINE, RADICE_RICERCA)
    slippage = 0.0001  # fascia di BTCUSDT (scheda_moneta della campagna BTCUSDT: 0,01% per lato)
    out["dati"] = {"barre_1d": len(s1["candele"]), "tolte_1d": [s1["n_tolte_last"], s1["n_tolte_mark"]],
                   "barre_8h": len(s8["candele"]), "tolte_8h": [s8["n_tolte_last"], s8["n_tolte_mark"]],
                   "settlement": len(funding),
                   "settlement_dentro_la_barra_1d": sum(1 for t, _ in funding if t % GIORNO_MS != 0)}
    for direzione in ("long", "short"):
        t0 = time.time()
        r1 = corsa_1d(s1["candele"], s1["candele_mark"], funding, direzione, slippage)
        r8 = corsa_8h(s8["candele"], s8["candele_mark"], funding, direzione, slippage)
        out[direzione] = {"1d": riassunto(r1, GIORNO_MS), "8h": riassunto(r8, 3 * GIORNO_MS // 9 * 3),
                          "confronto": confronto_trade(r1.trades, r8.trades), "secondi": round(time.time() - t0, 1)}
        print(direzione, json.dumps(out[direzione], indent=None)[:600], flush=True)
    return out


def parte_b():
    monete = [r["simbolo"] for r in csv.DictReader(open(RADICE_RICERCA / "campagne/GRUPPO/monete.csv"))]
    righe = {}
    for s in monete:
        scheda = dati.leggi_scheda_gruppo(s, RADICE_RICERCA)
        c = dati.carica_candele(s, "1d", scheda["primo_mese"], FINE, RADICE_RICERCA)
        if len(c) < N_ATR + 2:
            continue
        L = livelli_giornalieri(c)
        stop_pct = K_ATR * L["atr"][N_ATR:] / L["close"][N_ATR:]
        stop_pct = stop_pct[~np.isnan(stop_pct)]
        band = float(scheda["slippage_per_lato"])
        costo_frac = MAKER + TAKER + band   # ingresso maker senza scarto; uscita taker con lo scarto della fascia
        righe[s] = {"giorni": int(len(c)), "stop_pct_mediana": float(np.median(stop_pct)) * 100,
                    "stop_pct_q25": float(np.percentile(stop_pct, 25)) * 100, "stop_pct_q75": float(np.percentile(stop_pct, 75)) * 100,
                    "slippage_per_lato": band, "costo_per_giro_pct": costo_frac * 100,
                    "costo_r_alla_mediana": float(costo_frac / np.median(stop_pct))}
    stop_med = [v["stop_pct_mediana"] for v in righe.values()]
    costo = [v["costo_r_alla_mediana"] for v in righe.values()]
    return {"monete": len(righe), "stop_pct_mediana_delle_mediane": float(median(stop_med)),
            "stop_pct_min": float(min(stop_med)), "stop_pct_max": float(max(stop_med)),
            "costo_r_mediana": float(median(costo)), "costo_r_min": float(min(costo)), "costo_r_max": float(max(costo)),
            "per_moneta": righe}


def md(out):
    a, b = out["A"], out["B"]
    righe = ["# Misure sul motore a barre giornaliere (Passo 0, seconda edizione)", "",
             f"Scritto da `misure_motore_1d.py` il {out['quando']}; dati fino al 2023-12-31; commit {out['commit']}.", "",
             "## A. Funding a 1 giorno contro 8 ore (BTCUSDT 2020-2023, idea A1-20 con ingresso a limite)", "",
             f"Dati: {a['dati']['barre_1d']} barre 1d (tolte {a['dati']['tolte_1d']}), {a['dati']['barre_8h']} barre 8h (tolte {a['dati']['tolte_8h']}), "
             f"{a['dati']['settlement']} settlement di cui {a['dati']['settlement_dentro_la_barra_1d']} dentro la barra di 1 giorno.", "",
             "| Verso | Barre | Trade | Saltati | R medio | R lordo | Costo R | Funding R | Funding USDT | Esiti | Stop % | Durata gg |",
             "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for d in ("long", "short"):
        for tf in ("1d", "8h"):
            r = a[d][tf]
            righe.append(f"| {d} | {tf} | {r['trade']} | {r.get('saltati')} | {r['r_medio']:+.4f} | {r['r_lordo_medio']:+.4f} | {r['costo_medio_r']:.4f} | "
                         f"{r['funding_medio_r']:+.4f} | {r['funding_totale_usdt']:+.2f} | {r['esiti']} | {r['stop_medio_pct']:.1f} | {r['durata_media_giorni']:.1f} |")
    righe.append("")
    for d in ("long", "short"):
        c = a[d]["confronto"]
        righe.append(f"* **{d}**: trade con lo stesso giorno di segnale {c['comuni']} (solo 1d {c['solo_1d']}, solo 8h {c['solo_8h']}), "
                     f"stessa uscita {c['stessa_uscita']}; differenza di funding per trade (1d − 8h) media {c['funding_diff_media_r']:+.5f} R "
                     f"(massima in valore assoluto {c['funding_diff_max_abs_r']:.5f} R, {c['funding_diff_media_usdt']:+.4f} USDT); differenza di R "
                     f"media {c['r_diff_media']:+.4f}, mediana {c['r_diff_mediana']:+.4f}, massima {c['r_diff_max_abs']:.4f}.")
    righe += ["", "## B. Distanza dello stop (2,5 ATR(20)) e costo atteso per trade sulle 80 monete (1d, 2020-2023)", "",
              f"Monete {b['monete']}: distanza dello stop mediana {b['stop_pct_mediana_delle_mediane']:.1f}% del prezzo "
              f"(da {b['stop_pct_min']:.1f}% a {b['stop_pct_max']:.1f}%); costo per trade in R alla distanza mediana: mediana "
              f"{b['costo_r_mediana']:.4f} R (da {b['costo_r_min']:.4f} a {b['costo_r_max']:.4f}). Costo per giro = maker 0,02% + taker 0,05% + scarto "
              "d'uscita della fascia della scheda; in R = costo / distanza dello stop.", "",
              "| Moneta | Giorni | Stop % mediana (q25-q75) | Scarto per lato | Costo per giro % | Costo R |", "|---|---|---|---|---|---|"]
    for s, v in sorted(b["per_moneta"].items()):
        righe.append(f"| {s} | {v['giorni']} | {v['stop_pct_mediana']:.1f} ({v['stop_pct_q25']:.1f}-{v['stop_pct_q75']:.1f}) | {v['slippage_per_lato']*100:.2f}% | "
                     f"{v['costo_per_giro_pct']:.3f}% | {v['costo_r_alla_mediana']:.4f} |")
    return "\n".join(righe) + "\n"


def main():
    import subprocess
    from datetime import datetime, timezone
    out = {"quando": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
           "commit": subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=RADICE, capture_output=True, text=True).stdout.strip()}
    out["A"] = parte_a()
    out["B"] = parte_b()
    (QUI / "misure_motore_1d.json").write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
    (QUI / "misure_motore_1d.md").write_text(md(out), encoding="utf-8")
    print("scritto", QUI / "misure_motore_1d.md")


if __name__ == "__main__":
    main()
