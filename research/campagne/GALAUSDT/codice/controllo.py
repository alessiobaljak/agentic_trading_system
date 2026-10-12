"""Controllo positivo degli strumenti (lezioni/metodo.md): una strategia che legge di proposito la
barra successiva deve battere nettamente il caso e crollare con il ritardo di una barra.
Si registra come nota, prima e dopo; non consuma budget."""

import json

from research.campagne.GALAUSDT.codice import comune, registro
from research.campagne.GALAUSDT.codice.catalogo import CATALOGO, crea_variante


def main():
    voce = CATALOGO["CONTROLLO-1"]
    var = crea_variante("CONTROLLO-1")
    conteggio = comune.conta(var)
    registro.aggiungi({"id": "GALAUSDT-N-CONTROLLO-PRIMA", "tipo": "nota", "fase": "1",
                       "testo": "Controllo positivo degli strumenti, registrato prima di eseguirlo (non e' una variante, non consuma budget).",
                       "regole": voce["regole"], "timeframe": var.tf, "direzione": var.direzione,
                       "previsione": voce["previsione"], "trade_contati": conteggio["trade"],
                       "criterio": "t contro la (b) oltre la soglia senza ritardo; col ritardo di una barra t contro la (b) ricalcolata sotto la meta' (crollo)"})
    r0 = comune.valuta(var, "costruzione", con_a=True)
    r1 = comune.valuta(var, "costruzione", ritardo_barre=1, con_a=False)
    sintesi = {
        "senza_ritardo": {"trade": r0["metriche"]["trade"], "r_medio": r0["metriche"]["r_medio"],
                          "t_b": r0["baseline_b"].get("t"), "netta_b": r0["baseline_b"].get("netta"),
                          "t_a": r0["baseline_a"].get("t"), "netta_a": r0["baseline_a"].get("netta"),
                          "media_b": r0["baseline_b"].get("media")},
        "ritardo_1": {"trade": r1["metriche"]["trade"], "r_medio": r1["metriche"]["r_medio"],
                      "t_b": r1["baseline_b"].get("t"), "netta_b": r1["baseline_b"].get("netta"),
                      "media_b": r1["baseline_b"].get("media")},
    }
    t0, t1 = sintesi["senza_ritardo"]["t_b"], sintesi["ritardo_1"]["t_b"]
    passa = bool(sintesi["senza_ritardo"]["netta_b"]) and (t1 is not None and t1 < 0.5 * t0)
    registro.aggiungi({"id": "GALAUSDT-N-CONTROLLO-DOPO", "tipo": "nota", "fase": "1",
                       "testo": "Esito del controllo positivo degli strumenti.", "esito": sintesi,
                       "controllo_superato": passa})
    (comune.CARTELLA_DATI / "controllo.json").write_text(json.dumps(registro._pulisci(sintesi), indent=1))


if __name__ == "__main__":
    main()
