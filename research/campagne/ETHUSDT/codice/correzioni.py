"""Voci ``correzione`` del ricalcolo dopo la correzione del caricatore del funding.

Uso: python research/campagne/ETHUSDT/codice/correzioni.py [--scrivi]

Confronta gli esiti di ricalcolo.py (data/insample/ETHUSDT/lavoro/ricalcolo/) con le voci
originali del log e prepara una voce ``correzione`` per ogni risultato ricalcolato, con i
numeri nuovi, gli originali e la differenza. Senza ``--scrivi`` stampa solo il riepilogo;
con ``--scrivi`` aggiunge le voci al log (solo in aggiunta, con registro.aggiungi) e scrive
il riepilogo in lavoro/ricalcolo/riepilogo.json.

Il controllo positivo (nota N006) non ha una voce di risultato con i numeri completi: si
confronta con i numeri scritti nel testo di N006.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import ricalcolo  # noqa: E402
import registro  # noqa: E402

MOTIVO = "ricalcolo dopo la correzione del caricatore del funding (CHANGELOG 2026-10-08)"
CANDIDATO_ID = "ETHUSDT-026"

# Numeri del controllo positivo come scritti nella nota N006 (arrotondati li').
N006 = {"senza_ritardo": {"trade": 1205, "r_medio": 0.371, "t_b": 42.5, "netta_b": True},
        "ritardo": {"trade": 992, "r_medio": -0.017, "t_b": 0.40, "netta_b": False}}


def _num(x):
    if isinstance(x, str) and x in ("inf", "-inf", "nan"):
        return float(x)
    return x


def diff(nuovo, vecchio):
    nuovo, vecchio = _num(nuovo), _num(vecchio)
    if isinstance(nuovo, bool) or isinstance(vecchio, bool):
        return None if nuovo == vecchio else f"{vecchio} -> {nuovo}"
    if isinstance(nuovo, (int, float)) and isinstance(vecchio, (int, float)):
        d = nuovo - vecchio
        return d if d == d else None
    return None if nuovo == vecchio else f"{vecchio} -> {nuovo}"


def numeri_costruzione(r):
    m = r.get("metriche", {})
    a = r.get("baseline_a", {}) or {}
    b = r.get("baseline_b", {}) or {}
    return {"trade": m.get("trade"), "r_medio": m.get("r_medio"), "profit_factor": m.get("profit_factor"),
            "funding_totale": m.get("funding_totale"), "r_medio_senza_3_migliori": m.get("r_medio_senza_3_migliori"),
            "t_a": a.get("t"), "netta_a": a.get("netta"), "media_a": a.get("media"),
            "t_b": b.get("t"), "netta_b": b.get("netta"), "media_b": b.get("media"),
            "percentile_caso": r.get("percentile_caso"), "valutabile": r.get("valutabile"),
            "candidato": r.get("candidato")}


def confronto(nuovi, vecchi):
    d = {k: diff(nuovi.get(k), vecchi.get(k)) for k in nuovi}
    return {k: v for k, v in d.items() if v not in (None, 0, 0.0)}


def voce(id_, rimanda, nuovi, vecchi, esito_cambiato, extra=None):
    v = {"id": id_, "tipo": "correzione", "rimanda_a": rimanda, "motivo": MOTIVO,
         "numeri_nuovi": nuovi, "numeri_originali": vecchi, "differenze": confronto(nuovi, vecchi),
         "esito_cambiato": esito_cambiato}
    if extra:
        v.update(extra)
    return v


def prepara():
    log = registro.voci()
    reg = {(v["id"], v["tipo"]): v for v in log}
    per_variante = {v.get("variante_ipotesi"): v["id"] for v in log
                    if v["tipo"] in ("registrazione", "scarto") and v.get("tipo_test", "variante") == "variante"
                    and v.get("variante_ipotesi")}
    out = []

    # Controllo positivo
    for extra, chiave_n006 in (("", "senza_ritardo"), ("ritardo", "ritardo")):
        e = ricalcolo.leggi("controllo_ETHUSDT-C01" + (f"_{extra}" if extra else ""))
        b = e.get("baseline_b", {})
        nuovi = {"trade": e["metriche"]["trade"], "r_medio": e["metriche"]["r_medio"], "t_b": b.get("t"),
                 "netta_b": b.get("netta")}
        vecchi = N006[chiave_n006]
        out.append(voce("ETHUSDT-N006", {"id": "ETHUSDT-N006", "tipo": "nota", "parte": chiave_n006},
                        nuovi, vecchi, bool(nuovi["netta_b"]) != vecchi["netta_b"],
                        {"nota_confronto": "numeri originali dal testo di N006, arrotondati li'"}))

    # Conteggi dei trade (registrazioni e scarti)
    for nome in ricalcolo.nomi_contati():
        id_ = per_variante[nome]
        tipo = "scarto" if (id_, "scarto") in reg else "registrazione"
        vecchio = reg[(id_, tipo)]["trade_stimati"]
        nuovo = ricalcolo.leggi(f"conta_{nome}")["trade"]
        sotto_prima, sotto_ora = vecchio < 70, nuovo < 70
        out.append(voce(id_, {"id": id_, "tipo": tipo, "campo": "trade_stimati"},
                        {"trade_stimati": nuovo}, {"trade_stimati": vecchio}, sotto_prima != sotto_ora,
                        {"variante_ipotesi": nome}))

    # Fase 2 delle 30 varianti testate
    for nome in ricalcolo.nomi_testati():
        id_ = per_variante[nome]
        vecchi = numeri_costruzione(reg[(id_, "risultato")])
        nuovi = numeri_costruzione(ricalcolo.leggi(f"costruzione_{nome}"))
        cambiato = (bool(nuovi["candidato"]) != bool(vecchi["candidato"])
                    or bool(nuovi["valutabile"]) != bool(vecchi["valutabile"]))
        out.append(voce(id_, {"id": id_, "tipo": "risultato"}, nuovi, vecchi, cambiato, {"variante_ipotesi": nome}))

    # Verifiche della Fase 4 del candidato
    ver = ricalcolo.leggi(f"verifiche_{ricalcolo.CANDIDATO}")
    for nome_v, nuovo in ver.items():
        id_ = f"{CANDIDATO_ID}-V-{nome_v}"
        vecchio = reg[(id_, "risultato")]
        if nome_v in ("costi_doppi", "ritardo", "intrabarra_opposta"):
            n = dict(nuovo["esito"])
            o = dict(vecchio["esito"])
            n.pop("r_medio_per_anno", None)
            o.pop("r_medio_per_anno", None)
        elif nome_v in ("robustezza", "timeframe_adiacenti"):
            chiave = "parametro" if nome_v == "robustezza" else "timeframe"

            def riassunto(casi):
                r = {}
                for c in casi:
                    k = f"{c[chiave]}={c.get('valore')}" if nome_v == "robustezza" else c[chiave]
                    r[k] = {x: c.get(x) for x in ("trade_stimati", "r_medio", "t_b", "netta_b", "conta")}
                return r
            n, o = riassunto(nuovo["casi"]), riassunto(vecchio["casi"])
            for k in ("casi_che_contano", "t_positivo", "netti"):
                if k in nuovo:
                    n[k], o[k] = nuovo[k], vecchio.get(k)
        else:
            n = {k: nuovo[k] for k in ("media_b", "r_senza_3_migliori", "stabilita", "estremi",
                                       "violazioni_liquidazione", "superata")}
            o = {k: vecchio.get(k) for k in n}
        n["superata"], o["superata"] = nuovo.get("superata"), vecchio.get("superata")
        if nome_v in ("robustezza", "timeframe_adiacenti"):
            diffs = {}
            for k in n:
                if isinstance(n[k], dict):
                    dk = confronto(n[k], o.get(k) or {})
                    if dk:
                        diffs[k] = dk
                else:
                    d = diff(n[k], o.get(k))
                    if d not in (None, 0, 0.0):
                        diffs[k] = d
            v = {"id": id_, "tipo": "correzione", "rimanda_a": {"id": id_, "tipo": "risultato"}, "motivo": MOTIVO,
                 "numeri_nuovi": n, "numeri_originali": o, "differenze": diffs,
                 "esito_cambiato": n["superata"] != o["superata"]}
        else:
            v = voce(id_, {"id": id_, "tipo": "risultato"}, n, o, n["superata"] != o["superata"])
        out.append(v)
    return out


def riepilogo(voci):
    cambiati = [v for v in voci if v["differenze"]]
    esiti = [v for v in voci if v["esito_cambiato"]]
    r_diff = [(abs(v["differenze"]["r_medio"]), v["id"], v["differenze"]["r_medio"]) for v in voci
              if isinstance(v["differenze"].get("r_medio"), float)]
    return {"voci": len(voci), "con_differenze": len(cambiati), "esiti_cambiati": [v["id"] for v in esiti],
            "differenza_r_medio_massima": max(r_diff) if r_diff else None,
            "ids_con_differenze": [(v["id"], v["rimanda_a"].get("tipo"), v["rimanda_a"].get("parte"),
                                    v["differenze"]) for v in cambiati]}


def main() -> None:
    voci = prepara()
    rie = riepilogo(voci)
    print(json.dumps(registro.pulisci(rie), indent=1, ensure_ascii=False))
    if "--scrivi" in sys.argv:
        for v in voci:
            registro.aggiungi(v)
        (ricalcolo.CARTELLA / "riepilogo.json").write_text(
            json.dumps(registro.pulisci(rie), indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
        print("scritte", len(voci), "voci")


if __name__ == "__main__":
    main()
