"""Validazione del candidato ADAUSDT-037: una sola esecuzione, regole congelate (registrazione
ADAUSDT-037-V06). Serie dal 2020-01-01 al 2023-12-31; contano solo i trade entrati dopo la fine della
costruzione; (a) e (b) sullo stesso periodo di validazione. Asticella: Benjamini-Hochberg al 10% con m=1."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import comune as C  # noqa: E402
import registro  # noqa: E402
import varianti as V  # noqa: E402
from research.src import statistica  # noqa: E402
from run import _pulisci, _scrivi  # noqa: E402

if any(v["id"] == "ADAUSDT-037-V06" and v["tipo"] == "risultato" for v in registro.voci_presenti()):
    raise SystemExit("la validazione si fa una volta sola")
v = C.valuta(V.VARIANTI["ADAUSDT-037"], periodo="validazione")
m = v["metriche"]
esito = C.per_log(v)
n = m.get("trade", 0)
if n >= 30:
    p = v["baseline_b"].get("p_value", 1.0)
else:
    p = 1.0
passa = statistica.benjamini_hochberg([p], 0.10)[0] and n >= 30
voce = dict(esito, id="ADAUSDT-037-V06", tipo="risultato", verifica_di="ADAUSDT-037", verifica="validazione",
            p_value_asticella=p, asticella={"metodo": "Benjamini-Hochberg 10%", "m": 1, "passa": bool(passa),
                                             "provvisorio": True}, trade_minimi_validazione_raggiunti=n >= 30)
registro.aggiungi(_pulisci(voce))
_scrivi("uscita_validazione.txt", json.dumps(_pulisci({"trade": n, "r_medio": m.get("r_medio"), "pf": m.get("profit_factor"),
                                                      "r_anno": m.get("r_medio_per_anno"), "senza3": m.get("r_medio_senza_3_migliori"),
                                                      "a": v.get("baseline_a"), "b": v.get("baseline_b"), "p": p, "passa": passa,
                                                      "perc": v.get("percentile_caso"), "bh": v.get("buy_and_hold_per_anno")})))
