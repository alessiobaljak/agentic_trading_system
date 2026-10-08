"""Applica i criteri della Fase 4 (PROTOCOLLO.md, «Quando una verifica è superata») ai risultati del log.

  python sintesi_fase4.py <ID> [<ID> ...]      stampa il giudizio (sola lettura; la nota si scrive a parte)
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import comune  # noqa: E402
import registro  # noqa: E402


def ultimo_risultato(voci, vid):
    r = [v for v in voci if v.get("id") == vid and v.get("tipo") in ("risultato", "correzione") and "metriche" in v]
    return r[-1] if r else None


def giudica(vid):
    voci = registro.voci()
    base = ultimo_risultato(voci, vid)
    reg = {v["caso"]: v for v in voci if v.get("tipo") == "registrazione" and v.get("verifica_di") == vid}
    ris = {}
    for caso, r in reg.items():
        x = ultimo_risultato(voci, r["id"])
        if x is not None:
            ris[caso] = x
    out = {"id": vid, "esiti": {}}
    m, b = base["metriche"], base["baseline_b"]
    t0, media_b = b["t"], b["media"]

    # costi doppi
    c = ris.get("costi_doppi")
    if c:
        ok = bool(c["baseline_b"].get("netta")) and c["metriche"]["r_medio"] > 0
        out["esiti"]["costi_doppi"] = {"superata": ok, "r_medio": c["metriche"]["r_medio"], "t_b": c["baseline_b"].get("t"),
                                       "netta_b": c["baseline_b"].get("netta")}
    # robustezza
    rob = {k: v for k, v in ris.items() if k.startswith("robustezza_")}
    contano = {k: v for k, v in rob.items() if v["metriche"].get("trade", 0) >= comune.TRADE_MINIMI_COSTRUZIONE}
    dettagli = {k: {"trade": v["metriche"].get("trade"), "t_b": v["baseline_b"].get("t"), "netta_b": v["baseline_b"].get("netta"),
                    "valutabile": v["baseline_b"].get("valutabile")} for k, v in rob.items()}
    if rob:
        valut = [v for v in contano.values() if v["baseline_b"].get("valutabile")]
        tutti_pos = len(valut) == len(contano) and all((v["baseline_b"].get("t") or -1) > 0 for v in contano.values())
        nette = sum(1 for v in contano.values() if v["baseline_b"].get("netta"))
        ok = len(contano) * 2 >= len(rob) and tutti_pos and nette * 2 >= len(contano)
        out["esiti"]["robustezza"] = {"superata": ok, "casi_previsti": len(rob), "casi_che_contano": len(contano),
                                      "nette": nette, "casi": dettagli}
    # timeframe adiacenti
    tfs = {k: v for k, v in ris.items() if k.startswith("timeframe_")}
    if tfs:
        det, ok = {}, True
        for k, v in tfs.items():
            n = v["metriche"].get("trade", 0)
            det[k] = {"trade": n, "t_b": v["baseline_b"].get("t"), "valutabile": v["baseline_b"].get("valutabile")}
            if n >= comune.TRADE_MINIMI_COSTRUZIONE:
                if not v["baseline_b"].get("valutabile") or not (v["baseline_b"].get("t") or -1) > 0:
                    ok = False
        out["esiti"]["timeframe_adiacenti"] = {"superata": ok, "casi": det}
    # stabilita' temporale
    anni = {a: r for a, r in m["r_medio_per_anno"].items() if m["trade_per_anno"].get(a, 0) >= 10}
    sopra = sum(1 for r in anni.values() if r > media_b)
    out["esiti"]["stabilita_temporale"] = {"superata": sopra * 2 > len(anni), "anni_con_almeno_10_trade": anni,
                                           "anni_sopra_la_b": sopra, "media_b": media_b}
    # trade estremi
    out["esiti"]["pochi_trade_estremi"] = {"superata": m["r_medio_senza_3_migliori"] > media_b,
                                           "r_senza_3_migliori": m["r_medio_senza_3_migliori"], "media_b": media_b}
    # ritardo
    rit = ris.get("ritardo")
    if rit:
        tr = rit["baseline_b"].get("t")
        ok = tr is not None and tr > 0 and tr >= 0.5 * t0
        out["esiti"]["ritardo"] = {"superata": ok, "t_b_ritardo": tr, "t_b_senza": t0, "r_medio_ritardo": rit["metriche"]["r_medio"]}
    # intra-barra opposta: si dichiara la differenza
    ib = ris.get("intrabarra_opposta")
    if ib:
        out["esiti"]["intrabarra_opposta"] = {"dichiarata": True, "r_medio": ib["metriche"]["r_medio"], "r_medio_base": m["r_medio"],
                                              "differenza": round(ib["metriche"]["r_medio"] - m["r_medio"], 5)}
    # liquidazione
    out["esiti"]["liquidazione"] = {"superata": m.get("violazioni_liquidazione", 0) == 0, "violazioni": m.get("violazioni_liquidazione")}
    out["passa_la_fase_4"] = all(e.get("superata", True) for e in out["esiti"].values())
    return out


if __name__ == "__main__":
    for vid in sys.argv[1:]:
        print(json.dumps(giudica(vid), ensure_ascii=False))
