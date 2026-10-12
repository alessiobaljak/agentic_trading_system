"""Validazione (dopo la Fase 5): il candidato congelato BNBUSDT-045 gira UNA volta sul periodo di
validazione, senza modifiche, e si applica l'asticella (Benjamini-Hochberg al 10%, m = 1).

La serie va dall'inizio della costruzione al 2023-12-31 (indicatori caldi); contano solo i trade
entrati dal 2022-10-29. La (b) entra solo nelle barre di validazione.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import comune as C  # noqa: E402
import registro  # noqa: E402
import varianti as V  # noqa: E402
from research.src import statistica  # noqa: E402

CAND = "BNBUSDT-045"
VID = f"{CAND}-validazione"
v = V.i03("1h", VID, max_barre=12, solo_fine_settimana=True)

registro.aggiungi({"id": VID, "tipo": "registrazione", "tipo_test": "verifica", "verifica_di": CAND,
                   "periodo": "validazione", "timeframe": "1h", "direzione": "long",
                   "descrizione": "validazione del candidato congelato (candidati/BNBUSDT-045/regole.md), una sola volta",
                   "trade_stimati": 32,
                   "trade_stimati_nota": "stima proporzionale dichiarata: 74 trade di costruzione x 30/70 = 31,7; conta_trade non si usa sulla validazione",
                   "previsione": "R medio fra -0,10 e +0,10, sotto quello di costruzione; probabile p-value sopra 0,10 o meno di 30 trade",
                   "criterio_successo": "almeno 30 trade in validazione e asticella di Benjamini-Hochberg al 10% con m = 1 (p-value di contro_baseline contro la (b) di validazione <= 0,10); esito provvisorio, lo conferma il coordinamento al Passo 4"})
res = C.valuta(v, periodo="validazione")
m = res["metriche"]
b = res.get("baseline_b", {})
p = float(b.get("p_value", 1.0)) if m["trade"] >= 30 and b.get("valutabile") else 1.0
passa = statistica.benjamini_hochberg([p], 0.10)[0] and m["trade"] >= 30
registro.aggiungi({"id": VID, "tipo": "risultato", "metriche": m, "blocco": res.get("blocco"),
                   "durata_media_barre": res.get("durata_media_barre"),
                   "baseline_a": res.get("baseline_a"), "baseline_b": b, "percentile_caso": res.get("percentile_caso"),
                   "buy_and_hold_per_anno": res.get("buy_and_hold_per_anno"),
                   "btc_stessa_finestra": res.get("btc_stessa_finestra"),
                   "trade_minimi_validazione": m["trade"] >= 30, "p_value_asticella": p, "m_asticella": 1,
                   "passa_asticella_provvisorio": bool(passa),
                   "previsione_corretta": bool(-0.10 <= m["r_medio"] <= 0.10 and not passa),
                   "commento": f"validazione: {m['trade']} trade, R medio {m['r_medio']:+.3f}, p-value {p:.4f}, "
                               f"asticella {'superata' if passa else 'non superata'} (provvisorio)"})
print(C.compatto(res))
print("p_value", p, "passa", passa)
