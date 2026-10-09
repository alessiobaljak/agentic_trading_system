"""Fase 5: prova dello scettico su XRPUSDT-V21r3 con slippage 0,10% per lato (fascia da 20-50 milioni)."""
from dataclasses import replace

from research.campagne.XRPUSDT.codice import quadro as q
from research.campagne.XRPUSDT.codice.esegui import scrivi_esito
from research.campagne.XRPUSDT.codice.verifiche import var

CAND = "XRPUSDT-V21r3"
nome = "fase 5: slippage 0,10% per lato"
q.scrivi_log({"id": f"{CAND}-verifica-{nome}", "tipo": "registrazione", "tipo_test": "verifica", "verifica_di": CAND,
              "verifica": "fase5_slippage", "descrizione": nome, "timeframe": "1h", "periodo": "costruzione",
              "trade_stimati": 97,
              "criterio_successo": "nessuno vincolante (Fase 5, non e' una verifica della Fase 4): si dichiara se "
                                   "resta netta contro la (b) ricalcolata con lo stesso slippage e se R resta positivo",
              "previsione": "R medio fra 0,05 e 0,12, t contro la (b) fra 1,8 e 2,6"})
par = replace(q.parametri(), slippage_per_lato=0.001)
r = q.valuta(var(), q.serie("1h"), par)
m = r["metriche"]
q.scrivi_log({"id": f"{CAND}-verifica-{nome}", "tipo": "risultato", "metriche": m, "blocco": r.get("blocco"),
              "baseline_a": r.get("baseline_a"), "baseline_b": r.get("baseline_b"), "valutabile": r.get("valutabile")})
scrivi_esito(f"VERIFICA {nome}: trade={m['trade']} R={m['r_medio']:.3f} b_media={r['baseline_b']['media']:.3f} "
             f"t_b={r['baseline_b']['t']:.2f} netta_b={r['baseline_b']['netta']} t_a={r['baseline_a']['t']:.2f}")
