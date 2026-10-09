"""Registra e testa una variante del catalogo (o un ritocco), nell'ordine del protocollo.

Uso: python esegui.py <NOME>            (es. I-01-L)
     python esegui.py --controllo       (controllo positivo degli strumenti: note prima e dopo)

1. conta_trade sulle regole esatte (una volta sola);
2. sotto 70 trade: voce `scarto` (nessun budget consumato), fine;
3. altrimenti voce `registrazione` nel log, POI il test (esame), POI la voce `risultato`.
"""
from __future__ import annotations

import json
import sys
import time

import comune as C
import registro
import varianti as V


def _intervallo_previsto(meta):
    return meta.get("r_previsto")


def nuovo_id() -> str:
    usati = [v["id"] for v in registro.voci() if v.get("tipo") in ("registrazione", "scarto") and v["id"].startswith("ETCUSDT-0")]
    numeri = [int(x.split("-")[1]) for x in usati]
    return f"ETCUSDT-{(max(numeri) + 1) if numeri else 1:03d}"


def esegui_variante(var, meta, ritocco_di=None, famiglia=None, extra=None):
    C.stampa("conto dei trade di", meta["nome"])
    conteggio = C.conta(var)
    vid = nuovo_id()
    base = {
        "id": vid,
        "idea": meta["idea"],
        "nome_in_ipotesi": meta["nome"],
        "fonte": meta["fonte"],
        "meccanismo": meta["meccanismo"],
        "timeframe": var.tf,
        "direzione": var.direzione,
        "parametri": meta["parametri"],
        "periodo": "costruzione",
        "trade_stimati": conteggio["trade"],
        "conteggio": conteggio,
    }
    if conteggio["trade"] < C.TRADE_MINIMI_COSTRUZIONE:
        voce = dict(base, tipo="scarto", motivo=f"trade stimati {conteggio['trade']} sotto il minimo di costruzione "
                                               f"({C.TRADE_MINIMI_COSTRUZIONE}): nessun budget consumato",
                    famiglia=famiglia or vid, ritocco_di=ritocco_di)
        if extra:
            voce.update(extra)
        registro.scrivi(voce)
        C.stampa(json.dumps(voce, ensure_ascii=False))
        return voce
    voce = dict(base, tipo="registrazione", tipo_test="variante", famiglia=famiglia or vid, ritocco_di=ritocco_di,
                previsione=meta["previsione"], criterio_successo=meta["criterio_successo"],
                variante_n=C.prossimo_numero_variante())
    if extra:
        voce.update(extra)
    registro.scrivi(voce)
    C.stampa("registrata", vid, "variante", voce["variante_n"], "trade stimati", conteggio["trade"])
    t0 = time.time()
    ris = C.esame(var)
    risultato = {"id": vid, "tipo": "risultato", **ris, "secondi": round(time.time() - t0, 1)}
    if risultato["metriche"]["trade"] != conteggio["trade"]:
        risultato["avviso"] = "trade del test diversi da conta_trade"
    registro.scrivi(risultato)
    m = ris["metriche"]
    C.stampa(vid, meta["nome"], "trade", m["trade"], "R medio", round(m["r_medio"], 4), "PF", round(m["profit_factor"], 3),
             "t(a)", ris.get("baseline_a", {}).get("t"), "netta(a)", ris.get("baseline_a", {}).get("netta"),
             "t(b)", ris.get("baseline_b", {}).get("t"), "netta(b)", ris.get("baseline_b", {}).get("netta"),
             "percentile", ris.get("percentile_caso"), "candidato", ris.get("candidato"))
    return risultato


def controllo():
    var = V.controllo_positivo()
    registro.scrivi({"id": "ETCUSDT-N-CP3", "tipo": "nota", "testo": "Controllo positivo degli strumenti (lezioni/metodo.md), "
                     "PRIMA dell'esecuzione: strategia che legge di proposito la barra dopo (entra long se la barra di "
                     "ingresso chiudera' sopra la sua apertura), 1h, stop 2 ATR, uscita dopo 1 barra, stesse baseline delle "
                     "varianti. Attesa: batte nettamente la (a) e la (b); col ritardo di una barra il t contro la (b) "
                     "crolla (sotto la meta' e vicino a zero). Non e' una variante, non consuma budget."})
    ris = C.esame(var)
    rit = C.esame(var, parametri=C.replace(C.PARAMETRI, ritardo_barre=1))
    sintesi = {
        "senza_ritardo": {"trade": ris["metriche"]["trade"], "r_medio": ris["metriche"]["r_medio"],
                          "t_a": ris["baseline_a"].get("t"), "netta_a": ris["baseline_a"].get("netta"),
                          "t_b": ris["baseline_b"].get("t"), "netta_b": ris["baseline_b"].get("netta"),
                          "media_b": ris["baseline_b"].get("media"), "percentile": ris.get("percentile_caso")},
        "ritardo_1": {"trade": rit["metriche"]["trade"], "r_medio": rit["metriche"]["r_medio"],
                      "t_b": rit["baseline_b"].get("t"), "netta_b": rit["baseline_b"].get("netta"),
                      "media_b": rit["baseline_b"].get("media")},
    }
    ok = bool(sintesi["senza_ritardo"]["netta_a"] and sintesi["senza_ritardo"]["netta_b"]
              and sintesi["ritardo_1"]["t_b"] < 0.5 * sintesi["senza_ritardo"]["t_b"])
    registro.scrivi({"id": "ETCUSDT-N-CP4", "tipo": "nota", "testo": "Controllo positivo, DOPO: " +
                     ("superato" if ok else "NON superato"), "esito": sintesi, "superato": ok})
    C.stampa(json.dumps(sintesi, ensure_ascii=False, default=str))


if __name__ == "__main__":
    if sys.argv[1] == "--controllo":
        controllo()
    else:
        var, meta = V.CATALOGO[sys.argv[1]]()
        esegui_variante(var, meta)
