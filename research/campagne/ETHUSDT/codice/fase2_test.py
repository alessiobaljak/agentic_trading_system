"""Fase 2: test di una variante sui dati di COSTRUZIONE, con registrazione nel log PRIMA
dell'esecuzione e risultato DOPO, in due voci separate (regole 2 e 4 del protocollo).

Uso: python3 fase2_test.py <IDEA> <long|short> <file json con previsione e criterio>
Il file json porta: previsione (testo), criterio_successo (testo), e opzionalmente
note. La stima dei trade si legge da fase1_stime.json (calcolata prima, solo sui segnali).

Cosa fa, nell'ordine:
1. scrive la voce `registrazione` (tipo_test variante, variante_n progressivo);
2. esegue il backtest sul periodo di costruzione con i parametri del protocollo;
3. baseline (a) ogni barra, (b) 200 entrate casuali con la stessa uscita, (c) buy and hold;
4. scrive la voce `risultato` con metriche, confronto con le baseline e giudizio
   sulla previsione. Salva i trade in risultati/<id>_costruzione.json per le verifiche.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

QUI = Path(__file__).resolve().parent
sys.path.insert(0, str(QUI))
import comune  # noqa: E402
import strategie  # noqa: E402
from log import aggiungi, prossimo_id, prossimo_numero_variante  # noqa: E402
from research.src import statistica  # noqa: E402

RISULTATI = QUI.parent / "risultati"
RISULTATI.mkdir(exist_ok=True)


def esegui_variante(codice: str, nome_dir: str, extra: dict, registra: bool = True) -> dict:
    idea = strategie.IDEE[codice]
    direzione = 1 if nome_dir == "long" else -1
    stime: dict = {}
    for nome_file in sorted(QUI.parent.glob("fase1_stime*.json")):  # un file per lotto
        stime.update(json.loads(nome_file.read_text(encoding="utf-8")))
    stima = stime[f"{codice}-{nome_dir}"]
    s = comune.serie(idea.timeframe, comune.INIZIO_DATI, comune.FINE_COSTRUZIONE, con_btc=idea.con_btc)
    segn_tutti, uscita, riscaldamento = idea.costruisci(s)
    segn = strategie.solo(segn_tutti, direzione)
    da, a = riscaldamento, len(s.ts)
    atr_serie = comune.atr(s, 14)

    # 1. registrazione PRIMA del test
    id_voce = prossimo_id()
    n_var = prossimo_numero_variante()
    aggiungi({"id": id_voce, "tipo": "registrazione", "tipo_test": "variante", "idea": codice,
              "nome_idea": idea.nome, "fonte": strategie.FONTI[codice], "meccanismo": strategie.MECCANISMI[codice],
              "timeframe": idea.timeframe, "direzione": nome_dir,
              "parametri": {"k_atr": uscita.k_atr, "h_barre": uscita.h_barre, "rr_target": uscita.rr_target,
                            "uscita_su_segnale": uscita.chiusura_segnale is not None, "riscaldamento_barre": riscaldamento,
                            "regole": "come in ipotesi.md, sezione " + codice},
              "periodo": "costruzione 2020-01-01 -> 2022-10-19",
              "previsione": extra["previsione"], "criterio_successo": extra["criterio_successo"],
              "trade_stimati": stima["trade_stimati"], "stima_dettaglio": {k: stima[k] for k in ("segnali", "trade_stimati_distanza_h", "trade_stimati_uscita_segnale")},
              "variante_n": n_var, **({"note": extra["note"]} if extra.get("note") else {})})

    # 2. backtest
    strat = comune.costruisci_strategia(s, segn, uscita, atr_serie, da, a)
    ris = comune.esegui(s, strat)
    m = comune.riassunto(ris, s)
    r_cand = comune.serie_r(ris)
    blocco = comune.lunghezza_blocco(ris)

    # 3. baseline
    n_trade = len(ris.trades)
    durata_media_barre = max(1, int(round(np.mean([(t.ts_uscita - t.ts_entrata) for t in ris.trades]) / (s.ts[1] - s.ts[0])))) if ris.trades else 1
    bl_a = comune.baseline_ogni_barra(s, direzione, uscita, atr_serie, da, a)
    m_a = comune.riassunto(bl_a, s)
    r_a = comune.serie_r(bl_a)
    casuale = comune.baseline_casuale(s, direzione, uscita, atr_serie, da, a, n_trade, durata_media_barre, n_strategie=200, seme=1) if n_trade >= 2 else None
    bh = comune.buy_and_hold(s, da, a)

    confronto = {"buy_and_hold": bh, "baseline_a_ogni_barra": {"n_trade": m_a["n_trade"], "r_medio": m_a["r_medio"], "profit_factor": m_a["profit_factor"]},
                 "netto_vs_a": comune.confronto_netto(r_cand, r_a, blocco, seme=3) if len(r_cand) > 2 and len(r_a) > 2 else None}
    if casuale is not None:
        pct = comune.percentile_di(float(np.mean(r_cand)), casuale["r_medi"])
        confronto["baseline_b_casuale"] = {"n_strategie": 200, "r_medio_mediano": round(float(np.median(casuale["r_medi"])), 4),
                                           "r_medio_percentile_90": round(float(np.percentile(casuale["r_medi"], 90)), 4),
                                           "pf_mediano": round(casuale["pf_mediano"], 3),
                                           "percentile_del_candidato": round(pct, 1)}
        confronto["netto_vs_b"] = comune.confronto_netto(r_cand, casuale["serie_mediana"], blocco, seme=5) if len(casuale["serie_mediana"]) > 2 else None

    # giudizio: batte nettamente le baseline?
    batte = bool(confronto.get("netto_vs_b") and confronto["netto_vs_b"]["netta"] and confronto["netto_vs_b"]["segno"] > 0
                 and confronto.get("baseline_b_casuale", {}).get("percentile_del_candidato", 0) >= 90
                 and confronto.get("netto_vs_a") and confronto["netto_vs_a"]["segno"] > 0)
    sotto_minimo = n_trade < 100

    # 4. risultato
    esito = {"id": id_voce, "tipo": "risultato", "periodo": "costruzione", "metriche": m, "blocco_bootstrap": blocco,
             "confronto_baseline": confronto, "trade_minimi_costruzione_rispettati": not sotto_minimo,
             "batte_nettamente_le_baseline": batte,
             "esito_fase2": ("non si sa: sotto 100 trade" if sotto_minimo else ("passa alla Fase 3" if batte else "non batte le baseline: si ferma qui"))}
    (RISULTATI / f"{id_voce}_costruzione.json").write_text(json.dumps({
        "variante": f"{codice}-{nome_dir}", "trades": [t.__dict__ for t in ris.trades], "metriche": m}, indent=1, default=str), encoding="utf-8")
    return esito


if __name__ == "__main__":
    codice, nome_dir, file_extra = sys.argv[1], sys.argv[2], sys.argv[3]
    extra = json.loads(Path(file_extra).read_text(encoding="utf-8"))
    esito = esegui_variante(codice, nome_dir, extra)
    # il commento sulla previsione lo scrive chi lancia, dopo aver letto le metriche: qui si registra
    # il risultato nudo, e la valutazione della previsione va in una voce `nota` separata.
    aggiungi(esito)
    print(json.dumps({k: esito[k] for k in ("id", "metriche", "confronto_baseline", "esito_fase2")}, indent=1, ensure_ascii=False, default=str))
