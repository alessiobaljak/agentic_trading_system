"""Validazione (dopo la Fase 5): XRPUSDT-V21r3 gira UNA volta sul periodo di validazione, senza modifiche.

Serie dal 2020-01-01 al 2023-12-31 (indicatori caldi); contano solo i trade entrati dal 2022-10-19.
La (a) e la (b) sono calcolate sugli stessi trade e barre di validazione. Asticella: Benjamini-Hochberg al
10% sui candidati validati della moneta (uno solo, m = 1). Esito provvisorio (Passo 4).
"""
from research.src import statistica
from research.campagne.XRPUSDT.codice import quadro as q
from research.campagne.XRPUSDT.codice.esegui import scrivi_esito
from research.campagne.XRPUSDT.codice.verifiche import var

CAND = "XRPUSDT-V21r3"
q.scrivi_log({"id": f"{CAND}-validazione", "tipo": "registrazione", "tipo_test": "verifica", "verifica_di": CAND,
              "verifica": "validazione", "timeframe": "1h", "periodo": "validazione",
              "periodo_date": "trade entrati dal 2022-10-19 al 2023-12-31, serie dal 2020-01-01",
              "trade_stimati": 42, "trade_stimati_nota": "stima proporzionale 97 x 30/70 = 41,6 (non conta_trade)",
              "criterio_successo": "almeno 30 trade di validazione; p-value contro la (b) di validazione (contro_baseline) "
                                   "che passa Benjamini-Hochberg al 10% con m = 1 (p <= 0,10)",
              "previsione": "probabile sotto 30 trade (circa 60%); altrimenti R medio fra -0,10 e +0,15 e p sopra 0,10"})
s = q.serie("1h", q.FINE_IN_SAMPLE)
r = q.valuta(var(), s, q.parametri(), solo_da_ts=q.INIZIO_VALIDAZIONE_TS)
m = r["metriche"]
n = m["trade"]
p = r.get("baseline_b", {}).get("p_value", 1.0) if n >= 30 else 1.0
passa = statistica.benjamini_hochberg([p], q=0.10)[0] if n >= 30 else False
q.scrivi_log({"id": f"{CAND}-validazione", "tipo": "risultato", "metriche": m, "blocco": r.get("blocco"),
              "baseline_a": r.get("baseline_a"), "baseline_b": r.get("baseline_b"),
              "percentile_caso": r.get("percentile_caso"), "buy_and_hold_per_anno": r.get("buy_and_hold_per_anno"),
              "trade_minimi_validazione": n >= 30, "p_value": p, "m_asticella": 1,
              "asticella_passata_provvisoria": bool(passa)})
scrivi_esito(f"VALIDAZIONE {CAND}: trade={n} R={m['r_medio']:.3f} PF={m['profit_factor']:.2f} "
             f"b={r.get('baseline_b', {}).get('media')} t_b={r.get('baseline_b', {}).get('t')} p={p} passa={passa} "
             f"t_a={r.get('baseline_a', {}).get('t')} R_anno={m['r_medio_per_anno']} dd={m.get('drawdown_max')}")
