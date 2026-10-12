"""Registra e testa le varianti, in serie (il log ha id progressivi: mai due lotti in parallelo).

Uso:  python esegui.py registra ID [ID ...]   -> conta_trade una volta e scrive registrazione o scarto
      python esegui.py testa ID [ID ...]      -> test in costruzione e voce risultato
Ogni comando scrive anche un riassunto in data/insample/DOGEUSDT/uscite/<ID>.txt.
"""
import json
import sys
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import quadro as q  # noqa: E402
import registro  # noqa: E402
from meta import META  # noqa: E402
from varianti import VARIANTI  # noqa: E402

USCITE = q.RADICE_REPO / "research" / "data" / "insample" / "DOGEUSDT" / "uscite"
USCITE.mkdir(parents=True, exist_ok=True)


def scrivi(nome, testo):
    with open(USCITE / f"{nome}.txt", "a", encoding="utf-8") as f:
        f.write(testo + "\n")


def gia(id_, tipo):
    return any(v.get("id") == id_ and v.get("tipo") == tipo for v in registro.voci())


def prossimo_n():
    return 1 + sum(1 for v in registro.voci() if v.get("tipo") == "registrazione" and v.get("tipo_test") == "variante")


def registra(id_, extra=None):
    if gia(id_, "registrazione") or gia(id_, "scarto"):
        raise SystemExit(f"{id_} gia' registrata: la stima si fa una volta sola")
    v = VARIANTI[id_]()
    conteggio = q.conta(v)
    meta = dict(META[id_])
    meta.pop("previsione_intervallo", None)
    meta.update(extra or {})
    base = {"id": id_, "famiglia": meta.pop("famiglia", id_), "ritocco_di": meta.pop("ritocco_di", None), **meta,
            "periodo": "costruzione", "trade_stimati": conteggio["trade"], "conteggio": conteggio}
    if conteggio["trade"] < q.TRADE_MINIMI_COSTRUZIONE:
        voce = registro.aggiungi({"tipo": "scarto", "motivo": f"trade stimati {conteggio['trade']} sotto il minimo di 70 in costruzione: non si testa e non consuma budget", **base})
    else:
        voce = registro.aggiungi({"tipo": "registrazione", "tipo_test": "variante", **base, "variante_n": prossimo_n()})
    scrivi(id_, json.dumps(voce, ensure_ascii=False))
    print(id_, voce["tipo"], conteggio, flush=True)


def testa(id_):
    if not gia(id_, "registrazione") or gia(id_, "risultato"):
        raise SystemExit(f"{id_}: serve una registrazione e nessun risultato")
    v = VARIANTI[id_]()
    out, trades = q.valuta(v)
    reg = [x for x in registro.voci() if x.get("id") == id_ and x.get("tipo") == "registrazione"][-1]
    if out["metriche"]["trade"] != reg["trade_stimati"]:
        out["avviso"] = f"trade del test {out['metriche']['trade']} diversi dalla stima {reg['trade_stimati']}"
    lo, hi = META[id_]["previsione_intervallo"] if id_ in META else (None, None)
    rm = out["metriche"]["r_medio"]
    out["previsione_corretta"] = (lo <= rm <= hi) if lo is not None else None
    voce = registro.aggiungi({"id": id_, "tipo": "risultato", **out})
    scrivi(id_, json.dumps(voce, ensure_ascii=False))
    m = out["metriche"]
    print(id_, "trade", m["trade"], "R", round(rm, 4), "PF", round(m["profit_factor"], 3) if m["profit_factor"] != float("inf") else "inf",
          "a:", out.get("baseline_a", {}).get("t"), out.get("baseline_a", {}).get("netta"),
          "b:", out.get("baseline_b", {}).get("t"), out.get("baseline_b", {}).get("netta"),
          "cand", out.get("candidato"), flush=True)


if __name__ == "__main__":
    comando, ids = sys.argv[1], sys.argv[2:]
    for id_ in ids:
        try:
            registra(id_) if comando == "registra" else testa(id_)
        except SystemExit as e:
            print(e, flush=True)
            scrivi(id_, str(e))
        except Exception:
            scrivi(id_, traceback.format_exc())
            raise
