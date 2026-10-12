"""Registrazione e test delle varianti di ADAUSDT.

  python run.py registra ID [ID ...]   conta i trade (conta_trade, una volta) e scrive la registrazione
                                       (o lo scarto se sotto i 70 trade) PRIMA di qualunque test
  python run.py testa ID [ID ...]      esegue la variante registrata e scrive il risultato (Fase 2)

Le regole e i testi delle registrazioni stanno in varianti.py (VARIANTI e REG). L'uscita di ogni
comando si scrive anche in research/data/insample/ADAUSDT/uscita_<comando>.txt.
"""
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import comune as C  # noqa: E402
import registro  # noqa: E402
import varianti as V  # noqa: E402

USCITA = C.RADICE / "research" / "data" / "insample" / "ADAUSDT"


def _scrivi(nome, testo):
    with (USCITA / nome).open("a", encoding="utf-8") as f:
        f.write(testo + "\n")
    print(testo, flush=True)


def _pulisci(x):
    if isinstance(x, float) and (math.isinf(x) or math.isnan(x)):
        return str(x)
    if isinstance(x, dict):
        return {str(k): _pulisci(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [_pulisci(v) for v in x]
    return x


def _registrate():
    return [v for v in registro.voci_presenti() if v["tipo"] in ("registrazione", "scarto")]


def registra(ident):
    if any(v["id"] == ident for v in _registrate()):
        raise SystemExit(f"{ident} gia' registrata o scartata")
    var = V.VARIANTI[ident]
    reg = V.REG[ident]
    c = C.conta(var)
    base = {"id": ident, "idea": reg["idea"], "famiglia": reg.get("famiglia", ident),
            "ritocco_di": reg.get("ritocco_di"), "fonte": reg["fonte"], "meccanismo": reg["meccanismo"],
            "timeframe": var.tf, "direzione": var.direzione, "parametri": var.descrizione()["parametri"],
            "regole": reg["regole"], "periodo": "costruzione",
            "cambia": reg.get("cambia"), "perche": reg.get("perche"), "trade_stimati": c["trade"], "conta_trade": c}
    if c["trade"] < C.TRADE_MINIMI_COSTRUZIONE:
        voce = dict(base, tipo="scarto", motivo=f"sotto i trade minimi di costruzione ({c['trade']} < 70): non si testa, nessun budget")
        if reg.get("ritocco_di"):
            voce["nota"] = "ritocco scartato: conta fra i ritocchi della sua famiglia"
    else:
        n = sum(1 for v in registro.voci_presenti() if v["tipo"] == "registrazione" and v.get("tipo_test") == "variante") + 1
        voce = dict(base, tipo="registrazione", tipo_test="variante", previsione=reg["previsione"],
                    criterio_successo=reg.get("criterio_successo", "batte nettamente la (a) e la (b) con contro_baseline e R medio dopo i costi positivo"),
                    variante_n=n)
    scritta = registro.aggiungi(_pulisci(voce))
    _scrivi("uscita_registra.txt", json.dumps({"id": ident, "tipo": scritta["tipo"], "trade_stimati": c["trade"],
                                               "variante_n": scritta.get("variante_n")}))


def testa(ident):
    regs = [v for v in registro.voci_presenti() if v["id"] == ident and v["tipo"] == "registrazione"]
    if not regs:
        raise SystemExit(f"{ident}: nessuna registrazione")
    if any(v["id"] == ident and v["tipo"] == "risultato" for v in registro.voci_presenti()):
        raise SystemExit(f"{ident}: risultato gia' scritto")
    var = V.VARIANTI[ident]
    v = C.valuta(var)
    trades = v["_trades"]
    # i trade per lo studio dei fallimenti (fuori da git)
    with (USCITA / f"trade_{ident}.json").open("w", encoding="utf-8") as f:
        json.dump([{"e": t.ts_entrata, "u": t.ts_uscita, "r": t.r, "esito": t.esito, "entrata": t.entrata,
                    "stop": t.stop} for t in trades], f)
    if v["metriche"]["trade"] != regs[0]["trade_stimati"]:
        _scrivi("uscita_testa.txt", f"ATTENZIONE {ident}: trade del test {v['metriche']['trade']} diversi dalla stima {regs[0]['trade_stimati']}")
    voce = dict(C.per_log(v), id=ident, tipo="risultato")
    voce["t_contro_b"] = v["baseline_b"].get("t")
    voce["previsione_corretta"] = None
    voce["commento"] = "da completare in una voce nota con il confronto con la previsione"
    registro.aggiungi(_pulisci(voce))
    m = v["metriche"]
    _scrivi("uscita_testa.txt", json.dumps(_pulisci({
        "id": ident, "trade": m["trade"], "r_medio": round(m["r_medio"], 4), "pf": round(m["profit_factor"], 3),
        "r_anno": m["r_medio_per_anno"], "senza3": m["r_medio_senza_3_migliori"],
        "a": {k: v["baseline_a"].get(k) for k in ("media", "t", "netta", "valutabile")},
        "b": {k: v["baseline_b"].get(k) for k in ("media", "t", "netta", "valutabile")},
        "perc": v.get("percentile_caso"), "candidato": v["candidato"], "stop_pct": m["stop_medio_pct"],
        "durata_h": m["durata_media_ore"]})))


if __name__ == "__main__":
    comando, ids = sys.argv[1], sys.argv[2:]
    for i in ids:
        {"registra": registra, "testa": testa}[comando](i)
