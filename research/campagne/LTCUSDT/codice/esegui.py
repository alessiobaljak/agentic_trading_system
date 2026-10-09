"""Esecuzione delle varianti della campagna LTCUSDT, nell'ordine del protocollo.

Comandi (uno per volta, mai in parallelo: gli id del log sono in un file solo):

  python esegui.py testa <ID>
      1. se l'id e' gia' nel log, si ferma;
      2. conta i trade con conta_trade (una volta, sulle regole registrate);
      3. sotto i 70: scrive uno «scarto» e si ferma;
      4. altrimenti scrive la «registrazione» (con la previsione gia' scritta in
         varianti.py e ipotesi.md) e SOLO DOPO esegue il test di Fase 2;
      5. salva l'esito in data/insample/LTCUSDT/risultati/<ID>.json (fuori da git).

  python esegui.py risultato <ID> <file del commento>
      scrive nel log la voce «risultato» dal file salvato al punto 5, con
      ``previsione_corretta`` e ``commento`` presi dal file del commento (JSON).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import quadro  # noqa: E402
from aggiungi_log import LOG, aggiungi  # noqa: E402
from varianti import REGISTRO  # noqa: E402

CARTELLA_RISULTATI = quadro.CARTELLA_DATI / "risultati"


def voci_log():
    if not LOG.is_file():
        return []
    return [json.loads(r) for r in LOG.read_text(encoding="utf-8").splitlines() if r.strip()]


def prossimo_variante_n(voci) -> int:
    return 1 + sum(1 for v in voci if v.get("tipo") == "registrazione" and v.get("tipo_test") == "variante")


def testa(id_variante: str) -> None:
    voci = voci_log()
    if any(v.get("id") == id_variante for v in voci):
        raise SystemExit(f"{id_variante} e' gia' nel log: niente da fare")
    crea, meta = REGISTRO[id_variante]
    variante = crea()
    conteggio = quadro.stima(variante)
    base = {
        "id": id_variante,
        "idea": meta["idea"],
        "famiglia": meta.get("famiglia", id_variante),
        "ritocco_di": meta.get("ritocco_di"),
        "fonte": meta["fonte"],
        "meccanismo": meta["meccanismo"],
        "timeframe": variante.tf,
        "direzione": variante.direzione,
        "parametri": meta["parametri"],
    }
    if conteggio["trade"] < quadro.TRADE_MINIMI_COSTRUZIONE:
        voce = {"id": id_variante, "tipo": "scarto", "tipo_test": "variante", **{k: v for k, v in base.items() if k != "id"},
                "periodo": "costruzione", "trade_stimati": conteggio["trade"], "conteggio": conteggio,
                "motivo": f"sotto i trade minimi di costruzione ({conteggio['trade']} < {quadro.TRADE_MINIMI_COSTRUZIONE}): non si testa e non consuma budget"
                          + (" (ritocco: conta fra i ritocchi della famiglia)" if meta.get("ritocco_di") else "")}
        aggiungi([voce])
        print("SCARTO", id_variante, conteggio)
        return
    registrazione = {"id": id_variante, "tipo": "registrazione", "tipo_test": "variante",
                     **{k: v for k, v in base.items() if k != "id"},
                     "periodo": "costruzione", "previsione": meta["previsione"],
                     "criterio_successo": meta.get("criterio_successo",
                                                   "batte nettamente la (a) e la (b) (contro_baseline) e R medio dopo i costi positivo"),
                     "trade_stimati": conteggio["trade"], "conteggio": conteggio,
                     "variante_n": prossimo_variante_n(voci)}
    if meta.get("cosa_cambia"):
        registrazione["cosa_cambia"] = meta["cosa_cambia"]
        registrazione["perche"] = meta["perche"]
    aggiungi([registrazione])
    print("REGISTRATA", id_variante, "trade stimati", conteggio["trade"], flush=True)
    ris = quadro.giudica(variante, salva_trade=id_variante)
    ris["esito_fase2"] = quadro.esito_fase2(ris)
    if ris["metriche"]["trade"] != conteggio["trade"]:
        ris["avviso"] = f"trade del test {ris['metriche']['trade']} diversi dalla stima {conteggio['trade']}"
    quadro.scrivi_json(CARTELLA_RISULTATI / f"{id_variante}.json", ris)
    print(json.dumps({k: ris[k] for k in ("metriche", "baseline_a", "baseline_b", "percentile_caso", "esito_fase2")},
                     ensure_ascii=False, default=str, indent=1))


def risultato(id_variante: str, file_commento: str) -> None:
    voci = voci_log()
    if not any(v.get("id") == id_variante and v.get("tipo") == "registrazione" for v in voci):
        raise SystemExit(f"{id_variante}: nessuna registrazione nel log")
    if any(v.get("id") == id_variante and v.get("tipo") == "risultato" for v in voci):
        raise SystemExit(f"{id_variante}: risultato gia' scritto")
    ris = json.loads((CARTELLA_RISULTATI / f"{id_variante}.json").read_text(encoding="utf-8"))
    commento = json.loads(Path(file_commento).read_text(encoding="utf-8"))
    voce = {"id": id_variante, "tipo": "risultato", "metriche": ris["metriche"], "blocco": ris["blocco"],
            "baseline_a": ris["baseline_a"], "baseline_b": ris["baseline_b"],
            "percentile_caso": ris["percentile_caso"], "buy_and_hold_per_anno": ris["buy_and_hold_per_anno"],
            "esito_fase2": ris["esito_fase2"], "previsione_corretta": commento["previsione_corretta"],
            "commento": commento["commento"]}
    if "avviso" in ris:
        voce["avviso"] = ris["avviso"]
    aggiungi([voce])
    print("risultato scritto", id_variante)


if __name__ == "__main__":
    comando = sys.argv[1]
    if comando == "testa":
        testa(sys.argv[2])
    elif comando == "risultato":
        risultato(sys.argv[2], sys.argv[3])
    else:
        raise SystemExit(f"comando sconosciuto {comando}")
