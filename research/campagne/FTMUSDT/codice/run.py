"""Registra e testa le varianti. Uso: python run.py registra ID [ID...] | testa ID [ID...]

* registra: conta i trade UNA volta (conta_trade) e scrive nel log la registrazione, o lo scarto
  se sotto 70. Nessun risultato.
* testa: esegue il test di Fase 2 sui dati di costruzione e scrive il risultato. Rifiuta una
  variante senza registrazione precedente.
Le stampe vanno anche in data/insample/FTMUSDT/uscite/<ID>.txt.
"""
import json
import sys

from comune import LOG, RADICE_REPO, SIMBOLO, aggiungi_log
import quadro
from registro import CRITERIO, FONTI, VARIANTI

USCITE = RADICE_REPO / "research" / "data" / "insample" / SIMBOLO / "uscite"
USCITE.mkdir(parents=True, exist_ok=True)


def voci():
    with open(LOG, encoding="utf-8") as f:
        return [json.loads(r) for r in f if r.strip()]


def stampa(id_, testo):
    print(testo, flush=True)
    with open(USCITE / f"{id_}.txt", "a", encoding="utf-8") as f:
        f.write(testo + "\n")


def registra(id_, extra=None):
    log = voci()
    if any(v["id"] == id_ and v["tipo"] in ("registrazione", "scarto") for v in log):
        raise SystemExit(f"{id_} gia' registrata o scartata")
    idea, costruttore, meccanismo, parametri, (rmin, rmax) = VARIANTI[id_][:5]
    meta = VARIANTI[id_][5] if len(VARIANTI[id_]) > 5 else {}
    var = costruttore()
    n = quadro.conta(var)
    base = {"id": id_, "idea": idea, "famiglia": meta.get("famiglia", id_), "ritocco_di": meta.get("ritocco_di"),
            "fonte": FONTI.get(idea, meta.get("fonte")), "meccanismo": meccanismo, "timeframe": var.tf,
            "direzione": var.direzione, "parametri": parametri, "periodo": "costruzione", "trade_stimati": n["trade"],
            "conteggio": n}
    if meta.get("cosa_cambia"):
        base["cosa_cambia"] = meta["cosa_cambia"]
    if n["trade"] < 70:
        voce = aggiungi_log({**base, "tipo": "scarto", "motivo": f"sotto il minimo di 70 trade in costruzione ({n['trade']})"})
    else:
        variante_n = sum(1 for v in log if v["tipo"] == "registrazione" and v.get("tipo_test") == "variante") + 1
        voce = aggiungi_log({**base, "tipo": "registrazione", "tipo_test": "variante",
                             "previsione": f"R medio dopo i costi tra {rmin} e {rmax}; non netta contro la (b)"
                                           + (f"; {meta['previsione_extra']}" if meta.get("previsione_extra") else ""),
                             "previsione_r": [rmin, rmax], "criterio_successo": CRITERIO, "variante_n": variante_n})
    stampa(id_, f"{voce['tipo']} {id_}: trade stimati {n['trade']} {n}")


def testa(id_):
    log = voci()
    reg = [v for v in log if v["id"] == id_ and v["tipo"] == "registrazione"]
    if not reg or any(v["id"] == id_ and v["tipo"] == "risultato" for v in log):
        raise SystemExit(f"{id_}: nessuna registrazione, o gia' testata")
    reg = reg[0]
    var = VARIANTI[id_][1]()
    out = quadro.test_costruzione(var)
    m = out["metriche"]
    rmin, rmax = reg["previsione_r"]
    b = out.get("baseline_b", {})
    a = out.get("baseline_a", {})
    cand = quadro.candidato(out)
    prev_ok = (rmin <= m["r_medio"] <= rmax) and not b.get("netta", False)
    if m["trade"] != reg["trade_stimati"]:
        stampa(id_, f"ATTENZIONE: trade del test {m['trade']} diversi dalla stima {reg['trade_stimati']}")
    commento = (f"R medio {m['r_medio']:.3f} su {m['trade']} trade; contro (a) t={a.get('t')} netta={a.get('netta')}; "
                f"contro (b) t={b.get('t')} netta={b.get('netta')}; candidato={cand}")
    voce = aggiungi_log({"id": id_, "tipo": "risultato", **out, "candidato": cand, "previsione_corretta": prev_ok,
                         "commento": commento})
    stampa(id_, json.dumps({k: voce[k] for k in voce if k not in ("buy_and_hold_per_anno",)}, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    azione, ids = sys.argv[1], sys.argv[2:]
    for id_ in ids:
        {"registra": registra, "testa": testa}[azione](id_)
