"""Validazione (dopo la Fase 5): ogni candidato congelato gira UNA volta sul periodo di validazione.

    python research/campagne/DYDXUSDT/codice/validazione.py

Serie dall'inizio della costruzione al 2023-12-31 (indicatori caldi); contano i trade entrati dal
2023-04-20. (a) e (b) sul periodo di validazione; p-value dell'asticella = contro_baseline(...)["p_value"]
contro la (b) di validazione; Benjamini-Hochberg al 10% sui candidati validati (uno per famiglia).
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import comune  # noqa: E402
import registro  # noqa: E402
import varianti  # noqa: E402
from research.src import statistica  # noqa: E402

CANDIDATI = {"DYDXUSDT-008": ("I08_long", "1h", 161)}

p_values = {}
for id_, (nome, tf, trade_costr) in CANDIDATI.items():
    vid = f"{id_}-VAL"
    registro.aggiungi({"id": vid, "tipo": "registrazione", "tipo_test": "verifica", "verifica_di": id_,
                       "verifica": "validazione", "timeframe": tf, "periodo": "validazione",
                       "trade_stimati": round(trade_costr * 30 / 70),
                       "nota_stima": "stima proporzionale (trade di costruzione x 30/70), non conta_trade",
                       "criterio_successo": "almeno 30 trade in validazione e passa l'asticella di Benjamini-Hochberg al 10% (p-value contro la (b) di validazione)",
                       "previsione": "fra 25 e 70 trade; R medio fra -0,05 e +0,10; p-value fra 0,05 e 0,6: mi aspetto che il vantaggio di costruzione, al limite della soglia, si riduca"})
    ris = comune.valuta(tf, varianti.CREA[nome], periodo="validazione")
    pubb = comune.pubblico(ris)
    m = pubb["metriche"]
    b = pubb.get("baseline_b", {})
    p = b.get("p_value", 1.0) if m["trade"] >= comune.TRADE_MINIMI_VALIDAZIONE else 1.0
    p_values[id_] = p
    registro.aggiungi({"id": vid, "tipo": "risultato", "verifica": "validazione", "metriche": m,
                       "blocco": pubb.get("blocco"), "baseline_a": pubb.get("baseline_a"), "baseline_b": b,
                       "percentile_caso": pubb.get("percentile_caso"),
                       "buy_and_hold_per_anno": pubb.get("buy_and_hold_per_anno"),
                       "sopra_trade_minimi": m["trade"] >= comune.TRADE_MINIMI_VALIDAZIONE, "p_value_asticella": p})
    print(json.dumps(registro._pulisci({"id": vid, "trade": m["trade"], "r_medio": m["r_medio"], "pf": m["profit_factor"],
                                        "t_b": b.get("t"), "netta_b": b.get("netta"), "p": p,
                                        "t_a": pubb.get("baseline_a", {}).get("t")}), ensure_ascii=False))

ids = list(p_values)
passa = statistica.benjamini_hochberg([p_values[i] for i in ids], q=0.10)
esito = {i: {"p_value": p_values[i], "passa_asticella_provvisorio": bool(x)} for i, x in zip(ids, passa)}
registro.aggiungi({"id": "DYDXUSDT-ASTICELLA", "tipo": "nota", "argomento": "asticella di Benjamini-Hochberg al 10% (provvisoria: la conferma il coordinamento al Passo 4)",
                   "m": len(ids), "esito": esito})
print("ASTICELLA", json.dumps(esito))
