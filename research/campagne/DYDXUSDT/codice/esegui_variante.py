"""Registra e testa UNA variante, nell'ordine del protocollo.

    python research/campagne/DYDXUSDT/codice/esegui_variante.py <file registrazione json>

Il file di registrazione (in codice/registrazioni/) contiene i campi della voce di log scritti
PRIMA del test: nome della variante in varianti.CREA, idea, fonte, meccanismo, timeframe,
direzione, parametri, previsione, criterio di successo (e ritocco_di per i ritocchi).

1. conta i trade con conta_trade (una volta sola, sulle regole che si registrano);
2. sotto 70: voce ``scarto`` e fine (nessun budget);
3. altrimenti voce ``registrazione`` (con trade_stimati e variante_n), poi il test con le baseline
   (a) e (b) sul periodo di costruzione, poi la voce ``risultato``;
4. il risultato completo va in risultati/<id>.json (nella cartella della campagna).
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import comune  # noqa: E402
import registro  # noqa: E402
import varianti  # noqa: E402

CARTELLA = Path(__file__).resolve().parent.parent
RISULTATI = CARTELLA / "risultati"


def prossimi_numeri():
    voci = registro.voci()
    n_var = sum(1 for v in voci if v.get("tipo") == "registrazione" and v.get("tipo_test") == "variante")
    n_scarti = sum(1 for v in voci if v.get("tipo") == "scarto")
    return n_var + 1, n_scarti + 1


def main(percorso: str, chiave: str = None) -> None:
    reg = json.loads(Path(percorso).read_text(encoding="utf-8"))
    if chiave is not None:
        reg = dict(reg[chiave])
    nome = reg.pop("nome")
    crea_spec = varianti.CREA[nome]
    tf = reg["timeframe"]
    conteggio = comune.conta(tf, crea_spec)
    n_var, n_scarto = prossimi_numeri()
    if conteggio["trade"] < comune.TRADE_MINIMI_COSTRUZIONE:
        voce = {"id": f"DYDXUSDT-S{n_scarto:03d}", "tipo": "scarto", "variante": nome, **reg,
                "trade_stimati": conteggio["trade"], "conteggio": conteggio,
                "motivo": f"sotto i trade minimi di costruzione ({conteggio['trade']} < 70): non si testa, nessun budget"}
        print(json.dumps(registro.aggiungi(voce), ensure_ascii=False))
        return
    id_ = reg.pop("id", None) or f"DYDXUSDT-{n_var:03d}"
    famiglia = reg.pop("famiglia", None) or id_
    voce = {"id": id_, "tipo": "registrazione", "tipo_test": "variante", "variante": nome, "famiglia": famiglia,
            "ritocco_di": reg.pop("ritocco_di", None), **reg, "periodo": "costruzione",
            "trade_stimati": conteggio["trade"], "conteggio": conteggio, "variante_n": n_var}
    registro.aggiungi(voce)
    print("registrata", id_, nome, conteggio, flush=True)

    ris = comune.valuta(tf, crea_spec)
    pubb = comune.pubblico(ris)
    met = pubb["metriche"]
    a, b = pubb.get("baseline_a", {}), pubb.get("baseline_b", {})
    risultato = {
        "id": id_, "tipo": "risultato", "variante": nome,
        "metriche": met,
        "blocco": pubb.get("blocco"),
        "baseline_a": a, "baseline_b": b,
        "percentile_caso": pubb.get("percentile_caso"),
        "buy_and_hold_per_anno": pubb.get("buy_and_hold_per_anno"),
        "valutabile": pubb.get("valutabile"),
        "candidato": pubb.get("candidato", False),
        "trade_uguali_alla_stima": met["trade"] == conteggio["trade"],
    }
    registro.aggiungi(risultato)
    RISULTATI.mkdir(exist_ok=True)
    trades = [{"ts_entrata": t.ts_entrata, "ts_uscita": t.ts_uscita, "r": t.r, "esito": t.esito,
               "entrata": t.entrata, "uscita": t.uscita, "stop": t.stop, "funding": t.funding_pagato}
              for t in ris.get("_trades", [])]
    (RISULTATI / f"{id_}.json").write_text(json.dumps(registro._pulisci({"registrazione": voce, "risultato": risultato,
                                                                         "trades": trades}), ensure_ascii=False, indent=1))
    sintesi = {"id": id_, "trade": met["trade"], "r_medio": met["r_medio"], "pf": met["profit_factor"],
               "r_per_anno": met["r_medio_per_anno"], "senza3": met["r_medio_senza_3_migliori"],
               "a_media": a.get("media"), "t_a": a.get("t"), "netta_a": a.get("netta"),
               "b_media": b.get("media"), "t_b": b.get("t"), "netta_b": b.get("netta"),
               "soglia_b": b.get("soglia"), "percentile": pubb.get("percentile_caso"),
               "valutabile": pubb.get("valutabile"), "candidato": pubb.get("candidato")}
    print(json.dumps(registro._pulisci(sintesi), ensure_ascii=False))


if __name__ == "__main__":
    for k in sys.argv[2:] or [None]:
        main(sys.argv[1], k)
