"""Verifiche della Fase 4 su un candidato, sui dati di costruzione. Ogni verifica si registra nel log
PRIMA di eseguirla (tipo_test "verifica", verifica_di), poi si scrive il risultato.

  python verifiche.py <ID> <verifica>   con verifica fra: costi_doppi, ritardo, intrabarra, robustezza, timeframe
"""
import copy
import json
import math
import sys
from dataclasses import replace
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import comune as C  # noqa: E402
import registro  # noqa: E402
import varianti as V  # noqa: E402
from run import _pulisci, _scrivi  # noqa: E402

CRITERI = {
    "costi_doppi": "batte ancora nettamente la (b) ricalcolata a costi doppi e R medio a costi doppi positivo",
    "ritardo": "t contro la (b) ricalcolata col ritardo positivo e almeno la meta' del t senza ritardo",
    "intrabarra": "si dichiara la differenza",
    "robustezza": "nei casi che contano (>= 70 trade) t contro la (b) positivo, e in almeno meta' netta; casi non valutabili falliti; se contano meno della meta' dei casi, non superata",
    "timeframe": "su ogni timeframe adiacente con i trade minimi t contro la (b) ricalcolata positivo; sotto i minimi si dichiara; non valutabile = fallito",
}


def _prossimo_id(base):
    n = sum(1 for v in registro.voci_presenti() if v["id"].startswith(base + "-V") and v["tipo"] == "registrazione") + 1
    return f"{base}-V{n:02d}"


def _sint(v):
    m = v["metriche"]
    if m.get("trade", 0) == 0:
        return {"trade": 0}
    return {"trade": m["trade"], "r_medio": m["r_medio"], "profit_factor": m["profit_factor"],
            "r_medio_per_anno": m["r_medio_per_anno"], "r_senza_3": m["r_medio_senza_3_migliori"],
            "violazioni_liquidazione": m["violazioni_liquidazione"], "trade_ridotti": m["trade_ridotti"],
            "a": {k: v["baseline_a"].get(k) for k in ("media", "t", "netta", "valutabile")},
            "b": {k: v["baseline_b"].get(k) for k in ("media", "t", "netta", "valutabile")}}


def casi(ident, tipo):
    """Lista di (descrizione, variante, parametri motore)."""
    var = V.VARIANTI[ident]
    out = []
    if tipo == "costi_doppi":
        out.append(("costi x2", var, replace(C.PARAM, moltiplicatore_costi=2.0)))
    elif tipo == "ritardo":
        out.append(("ritardo 1 barra", var, replace(C.PARAM, ritardo_barre=1)))
    elif tipo == "intrabarra":
        out.append(("target prima", var, replace(C.PARAM, riempimento_intrabarra="target_prima")))
    elif tipo == "robustezza":
        for nome, val in var.p.items():
            if isinstance(val, bool):
                continue
            if isinstance(val, int):
                giu = int(math.floor(0.8 * val + 0.5))
                su = int(math.floor(1.2 * val + 0.5))
                if giu == val:
                    giu = val - 1
                if su == val:
                    su = val + 1
                valori = [giu, su]
            else:
                valori = [0.8 * val, 1.2 * val]
            for x in valori:
                nv = copy.deepcopy(var)
                nv.p[nome] = x
                out.append((f"{nome}={x}", nv, C.PARAM))
    elif tipo == "timeframe":
        for nv in V.ADIACENTI[ident]:
            out.append((f"timeframe {nv.tf}", nv, C.PARAM))
    return out


def esegui(ident, tipo):
    elenco = casi(ident, tipo)
    vid = _prossimo_id(ident)
    conti = {}
    for desc, var, param in elenco:
        D = C.carica(var.tf)
        F = C.Fabbriche(var, D)
        from research.src import motore
        conti[desc] = motore.conta_trade(D["candele"], F.crea_strategia, C.FINE_COSTRUZIONE_TS, param,
                                         candele_mark=D["mark"], funding=D["funding"])["trade"]
    registro.aggiungi(_pulisci({"id": vid, "tipo": "registrazione", "tipo_test": "verifica", "verifica_di": ident,
                                "verifica": tipo, "periodo": "costruzione",
                                "casi": [{"caso": d, "timeframe": v.tf, "parametri": v.p} for d, v, _ in elenco],
                                "trade_stimati": conti, "criterio_successo": CRITERI[tipo],
                                "previsione": V.PREVISIONI_VERIFICHE.get((ident, tipo), "")}))
    esiti = {}
    for desc, var, param in elenco:
        if conti[desc] < C.TRADE_MINIMI_COSTRUZIONE:
            esiti[desc] = {"trade": conti[desc], "conta": False, "motivo": "sotto i trade minimi: si dichiara e non conta"}
            continue
        v = C.valuta(var, param, extra=False)
        esiti[desc] = dict(_sint(v), conta=True, candidato_nel_caso=v["candidato"])
    registro.aggiungi(_pulisci({"id": vid, "tipo": "risultato", "verifica_di": ident, "verifica": tipo, "esiti": esiti}))
    _scrivi("uscita_verifiche.txt", json.dumps(_pulisci({"id": vid, "verifica": tipo, "esiti": esiti})))


if __name__ == "__main__":
    esegui(sys.argv[1], sys.argv[2])
