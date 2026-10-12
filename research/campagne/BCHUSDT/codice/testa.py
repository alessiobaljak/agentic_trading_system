"""Esegue il test di Fase 2 di varianti gia' registrate e scrive il risultato nel log.

Uso: python -m research.campagne.BCHUSDT.codice.testa <id> [<id> ...]

Rifiuta un id senza registrazione o con un risultato gia' scritto. I trade del test
si salvano in data/insample/BCHUSDT/trade/<id>.json (fuori da git) per la Fase 3.
``previsione_corretta`` confronta l'R medio con l'intervallo ``previsione_r_medio``
scritto nella registrazione.
"""
import json
import sys
from dataclasses import asdict

from research.campagne.BCHUSDT.codice import comune, registra, varianti
from research.campagne.BCHUSDT.codice.registra_variante import voci_log


def main():
    cartella = comune.CARTELLA_DATI / "trade"
    cartella.mkdir(exist_ok=True)
    for vid in sys.argv[1:]:
        log = voci_log()
        reg = [x for x in log if x.get("id") == vid and x["tipo"] == "registrazione"]
        if not reg or any(x.get("id") == vid and x["tipo"] == "risultato" for x in log):
            print(vid, "senza registrazione o gia' testata")
            continue
        reg = reg[0]
        v = varianti.VARIANTI[vid]()
        r = comune.esamina(v)
        trades = r.pop("_trades", [])
        (cartella / f"{vid}.json").write_text(json.dumps([asdict(t) for t in trades]), encoding="utf-8")
        lo, hi = reg.get("previsione_r_medio", [None, None])
        rm = r["metriche"]["r_medio"]
        voce = {"id": vid, "tipo": "risultato"}
        voce.update(r)
        voce["t_contro_b"] = r.get("baseline_b", {}).get("t")
        voce["previsione_corretta"] = (lo is not None and lo <= rm <= hi)
        if r["metriche"]["trade"] != reg["trade_stimati"]:
            voce["nota_trade"] = f"trade del test {r['metriche']['trade']} diversi dalla stima {reg['trade_stimati']}"
        scritta = registra.aggiungi(voce)
        b = r.get("baseline_b", {})
        a = r.get("baseline_a", {})
        print(scritta["data"], vid, "trade", r["metriche"]["trade"], "R", round(rm, 4),
              "t_a", a.get("t"), "netta_a", a.get("netta"), "t_b", b.get("t"), "netta_b", b.get("netta"),
              "candidato", r.get("candidato"), flush=True)


if __name__ == "__main__":
    main()
