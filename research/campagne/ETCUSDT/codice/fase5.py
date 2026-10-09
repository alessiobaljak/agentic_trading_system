"""Fase 5: le domande dello scettico sulla famiglia ETCUSDT-023, con test sui soli dati di costruzione.

Ogni test si registra nel log PRIMA di eseguirlo (tipo registrazione, tipo_test verifica, verifica_di
ETCUSDT-023) e il risultato va in una voce separata. Nessun test serve a costruire o scegliere una
regola: il budget e' esaurito e le regole dei candidati sono ferme.

T1  short ogni giorno nell'ultima mezz'ora UTC, senza condizione sulla giornata, con l'esame completo
    (baseline (a) e (b)): se batte la (b) come 023, il vantaggio e' dell'ora, non della giornata in calo.
T2  placebo delle mezz'ore: per ogni mezz'ora h del giorno, rendimento lordo medio della mezz'ora dopo
    h nelle giornate in calo fino a h (sotto 0 e sotto -5%), contro tutte le giornate: se l'effetto c'e'
    a molte ore, l'ultima mezz'ora non e' speciale.
T3  e' solo il mercato? Lo stesso calcolo lordo su BTCUSDT (30m) nell'ultima mezz'ora.
T4  funding: i trade di 023 divisi per segno dell'ultimo funding regolato prima del segnale (16:00 UTC).
"""
from __future__ import annotations

import bisect
from datetime import datetime, timezone

import numpy as np

import comune as C
import registro
import varianti as V
from comune import Variante

G, H = V.GIORNO, V.ORA
MEZZ = 30 * 60_000


def reg(nome, descrizione, criterio):
    registro.scrivi({"id": f"ETCUSDT-F5-{nome}", "tipo": "registrazione", "tipo_test": "verifica",
                     "verifica_di": "ETCUSDT-023", "fase": 5, "verifica": descrizione, "criterio_successo": criterio,
                     "periodo": "costruzione"})


def risultato(nome, dati):
    registro.scrivi({"id": f"ETCUSDT-F5-{nome}", "tipo": "risultato", **dati})
    C.stampa(f"F5-{nome}", dati)


def bp(x):
    return None if x is None else round(10_000 * x, 2)


# ---------------------------------------------------------------- T1
reg("T1", "short ogni giorno alle 23:30 UTC per 30 minuti, senza condizione sulla giornata (stop 2 ATR, esame completo)",
    "se il t contro la (b) e' vicino a quello di 023 (3,15) il vantaggio di 023 e' dell'ora del giorno, non del calo")


def prepara_t1(serie):
    ind = V._base(serie)
    ind["ultima"] = [c.ts % G == 23 * H for c in serie.candele]
    ind["riscaldamento"] = V._riscaldamento(ind["atr"])
    return ind


var_t1 = Variante("F5-T1", "30m", "short", prepara_t1, lambda ind, i: ind["ultima"][i], V._stop(2.0, "short"), max_barre=1)
r1 = C.esame(var_t1)
risultato("T1", {"trade": r1["metriche"]["trade"], "r_medio": r1["metriche"]["r_medio"],
                 "r_medio_per_anno": r1["metriche"]["r_medio_per_anno"],
                 "t_a": r1["baseline_a"]["t"], "t_b": r1["baseline_b"]["t"], "media_b": r1["baseline_b"]["media"],
                 "netta_b": r1["baseline_b"]["netta"], "percentile": r1.get("percentile_caso")})

# ---------------------------------------------------------------- T2 e T3
reg("T2", "placebo delle mezz'ore su ETCUSDT: rendimento lordo medio della mezz'ora successiva, per ogni mezz'ora del giorno, "
          "nelle giornate in calo fino a quel momento (sotto 0 e sotto -5%) e in tutte",
    "l'ultima mezz'ora e' speciale se il suo valore nelle giornate sotto -5% e' fra i piu' negativi e se le altre ore non "
    "mostrano lo stesso effetto")
reg("T3", "lo stesso calcolo su BTCUSDT 30m (solo l'ultima mezz'ora e il confronto con le altre)",
    "se BTC ha lo stesso effetto, per ETC e' il mercato comune")


def tabella(candele, nome):
    per_giorno = {}
    for c in candele:
        per_giorno.setdefault(c.ts - c.ts % G, {})[c.ts % G] = c
    out = {}
    for k in range(48):
        h = k * MEZZ  # barra di segnale che apre a h; rendimento della barra dopo (h + 30 minuti)
        tutte, sotto0, sotto5 = [], [], []
        for g0, barre in per_giorno.items():
            if 0 not in barre or h not in barre:
                continue
            seg = barre[h]
            nxt = barre.get(h + MEZZ) if h + MEZZ < G else per_giorno.get(g0 + G, {}).get(0)
            if nxt is None:
                continue
            rg = seg.close / barre[0].open - 1
            rn = nxt.close / nxt.open - 1
            tutte.append(rn)
            if rg < 0:
                sotto0.append(rn)
            if rg < -0.05:
                sotto5.append(rn)
        out[f"{h // H:02d}:{(h % H) // 60_000:02d}"] = {
            "n_tutte": len(tutte), "tutte_bp": bp(np.mean(tutte)) if tutte else None,
            "n_sotto0": len(sotto0), "sotto0_bp": bp(np.mean(sotto0)) if sotto0 else None,
            "n_sotto5": len(sotto5), "sotto5_bp": bp(np.mean(sotto5)) if sotto5 else None,
        }
    return out


etc = C.carica("30m", "costruzione")
t2 = tabella(etc.candele, "ETCUSDT")
ult = t2["23:00"]
ordinate = sorted((v["sotto5_bp"], k) for k, v in t2.items() if v["sotto5_bp"] is not None and v["n_sotto5"] >= 30)
risultato("T2", {"ultima_mezz_ora": ult, "posizione_ultima_fra_le_ore_sotto5": [k for _, k in ordinate].index("23:00") + 1
                 if "23:00" in [k for _, k in ordinate] else None, "ore_contate": len(ordinate),
                 "le_5_piu_negative_sotto5": ordinate[:5], "le_5_piu_positive_sotto5": ordinate[-5:],
                 "media_delle_ore_sotto5_bp": round(float(np.mean([v for v, _ in ordinate])), 2),
                 "tabella": t2})

btc = [c for c in C.btc_allineato(etc) if c is not None]
t3 = tabella(btc, "BTCUSDT")
ordb = sorted((v["sotto0_bp"], k) for k, v in t3.items() if v["sotto0_bp"] is not None)
risultato("T3", {"ultima_mezz_ora_btc": t3["23:00"], "posizione_ultima_fra_le_ore_sotto0": [k for _, k in ordb].index("23:00") + 1,
                 "ore": len(ordb), "media_delle_ore_sotto0_bp": round(float(np.mean([v for v, _ in ordb])), 2)})

# ---------------------------------------------------------------- T4
reg("T4", "i trade di ETCUSDT-023 divisi per segno dell'ultimo funding regolato prima del segnale (16:00 UTC)",
    "se il vantaggio sta solo nei giorni di funding positivo, la spiegazione 'chi e' long chiude prima di pagare il "
    "funding delle 00:00' resta in piedi")
var23, _ = V.CATALOGO["I-12-S"]()
serie, ind, ris = C.trade_di(var23)
fts = [t for t, _ in sorted(serie.funding)]
ftassi = [r for _, r in sorted(serie.funding)]
gruppi = {"positivo": [], "non_positivo": []}
lordi = {"positivo": [], "non_positivo": []}
for t in ris.trades:
    k = bisect.bisect_right(fts, t.ts_entrata - 1) - 1
    chiave = "positivo" if k >= 0 and ftassi[k] > 0 else "non_positivo"
    gruppi[chiave].append(t.r)
    lordi[chiave].append(t.pnl_lordo / t.rischio_iniziale)
risultato("T4", {g: {"n": len(v), "r_medio": float(np.mean(v)) if v else None,
                     "r_lordo_medio": float(np.mean(lordi[g])) if lordi[g] else None} for g, v in gruppi.items()})
