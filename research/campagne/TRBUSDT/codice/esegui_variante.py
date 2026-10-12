"""Esegue in serie le varianti date (id di varianti.py): conteggio, registrazione, test, risultato.

Ordine per ogni variante (sezione 8 e regola 2): conta_trade una volta sola sulle regole esatte;
se sotto 70 trade -> voce `scarto` (nessun budget); altrimenti voce `registrazione` PRIMA del test,
poi il test e la voce `risultato`. Un riassunto va in data/insample/TRBUSDT/ultimo_lotto.json.

Uso: python -m research.campagne.TRBUSDT.codice.esegui_variante I-01-L I-01-S ...
"""

import json
import sys
import traceback

from research.campagne.TRBUSDT.codice import banco, registro
from research.campagne.TRBUSDT.codice import varianti as V

USCITA = banco.RADICE / "data" / "insample" / "TRBUSDT" / "ultimo_lotto.json"


def gia_fatte():
    return {v["id"] for v in registro.voci() if v.get("tipo") in ("registrazione", "scarto") and v.get("tipo_test", "variante") == "variante"}


def esegui(id_, extra=None, variante=None, ritocco_di=None, famiglia=None, previsione=None, parametri=None,
           idea=None, motivo=None):
    v = variante or V.VARIANTI[id_]()
    idea = idea or id_[:4]
    conteggio = banco.conta(v)
    base = {"id": id_, "tipo_test": "variante", "idea": idea, "famiglia": famiglia or id_, "ritocco_di": ritocco_di,
            "fonte": V.FONTI[idea], "meccanismo": V.MECCANISMI[idea], "timeframe": v.timeframe,
            "direzione": v.direzione, "parametri": parametri or V.PARAMETRI[id_], "periodo": "costruzione",
            "trade_stimati": conteggio["trade"], "conteggio": conteggio}
    if motivo:
        base["motivo"] = motivo
    if conteggio["trade"] < banco.TRADE_MINIMI["costruzione"]:
        voce = dict(base, tipo="scarto", motivo_scarto=f"trade stimati {conteggio['trade']} sotto il minimo di 70 in costruzione")
        banco.scrivi(voce)
        return {"id": id_, "esito": "scarto", "trade_stimati": conteggio["trade"]}
    (lo, hi), attesa = previsione or V.PREVISIONI[id_]
    voce = dict(base, tipo="registrazione", previsione=f"R medio dopo i costi fra {lo} e {hi}; {attesa}",
                previsione_r_medio=[lo, hi], criterio_successo=V.CRITERIO, variante_n=registro.prossima_variante_n())
    banco.scrivi(voce)
    out = banco.valuta(v)
    r = out["metriche"]["r_medio"]
    corretta = bool(lo <= r <= hi)
    commento = (f"{'candidato' if out['candidato'] else 'non candidato'}; netta (a) {out['baseline_a_esito'].get('netta')}, "
                f"netta (b) {out['baseline_b_esito'].get('netta')}, t (b) {out['baseline_b_esito'].get('t')}")
    banco.scrivi(banco.voce_risultato(id_, out, corretta, commento))
    return {"id": id_, "esito": "testata", "trade": out["n_trade"], "r_medio": r, "t_a": out["baseline_a_esito"].get("t"),
            "netta_a": out["baseline_a_esito"].get("netta"), "t_b": out["baseline_b_esito"].get("t"),
            "netta_b": out["baseline_b_esito"].get("netta"), "media_b": out["baseline_b"].get("media"),
            "media_a": out["baseline_a"].get("media"), "candidato": out["candidato"], "valutabile": out["valutabile"],
            "r_per_anno": out["metriche"]["r_medio_per_anno"], "senza_3": out["metriche"]["r_medio_senza_3_migliori"],
            "percentile": out["percentile_caso"], "durata": out["metriche"]["durata_media_barre"]}


def main(ids):
    fatte = gia_fatte()
    riassunto = []
    for id_ in ids:
        if id_ in fatte:
            riassunto.append({"id": id_, "esito": "gia' nel log, saltata"})
            continue
        try:
            riassunto.append(esegui(id_))
        except Exception:
            riassunto.append({"id": id_, "errore": traceback.format_exc()})
        with open(USCITA, "w", encoding="utf-8") as f:
            json.dump(banco._json_ok(riassunto), f, indent=1, ensure_ascii=False)
    print(json.dumps(banco._json_ok(riassunto), indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main(sys.argv[1:])
