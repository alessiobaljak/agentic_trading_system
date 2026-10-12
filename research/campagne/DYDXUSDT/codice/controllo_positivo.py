"""Controllo positivo degli strumenti (lezioni/metodo.md): una strategia che legge DI PROPOSITO la
barra successiva deve battere nettamente il caso e crollare con il ritardo di una barra.

Si registra come nota (prima e dopo), senza consumare budget. Timeframe 1h, long, stop 2 ATR(14),
uscita dopo 1 barra: le stesse baseline (a) e (b) delle varianti vere.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import comune  # noqa: E402
import registro  # noqa: E402
import varianti  # noqa: E402

registro.aggiungi({
    "id": "DYDXUSDT-CP1", "tipo": "nota",
    "argomento": "controllo positivo degli strumenti: PRIMA dell'esecuzione",
    "regola": "1h, long se la barra SUCCESSIVA chiude sopra la sua apertura (lookahead dichiarato), stop 2 ATR(14), uscita dopo 1 barra",
    "previsione": "senza ritardo: batte nettamente la (b) con t molto sopra la soglia; con il ritardo di una barra il t contro la (b) ricalcolata crolla verso 0 (sotto la meta' di quello senza ritardo)",
})
crea = varianti.CREA["controllo_positivo"]
senza = comune.valuta("1h", crea)
con = comune.valuta("1h", crea, par=comune.parametri(ritardo_barre=1))
esito = {}
for nome, r in (("senza_ritardo", senza), ("ritardo_1", con)):
    p = comune.pubblico(r)
    esito[nome] = {"trade": p["metriche"]["trade"], "r_medio": p["metriche"]["r_medio"],
                   "t_a": p["baseline_a"].get("t"), "netta_a": p["baseline_a"].get("netta"),
                   "t_b": p["baseline_b"].get("t"), "netta_b": p["baseline_b"].get("netta"),
                   "media_b": p["baseline_b"].get("media"), "percentile": p.get("percentile_caso")}
passa = bool(esito["senza_ritardo"]["netta_b"] and esito["ritardo_1"]["t_b"] < 0.5 * esito["senza_ritardo"]["t_b"])
voce = registro.aggiungi({"id": "DYDXUSDT-CP2", "tipo": "nota",
                          "argomento": "controllo positivo degli strumenti: DOPO l'esecuzione",
                          "esito": esito, "superato": passa})
print(json.dumps(voce, ensure_ascii=False))
