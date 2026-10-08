"""Fase 4: le verifiche di un candidato sui dati di costruzione, ognuna registrata PRIMA.

Uso: python research/campagne/ETHUSDT/codice/verifiche.py <nome> <verifica> "<previsione>"

Verifiche: costi_doppi, ritardo, intrabarra_opposta, robustezza, timeframe_adiacenti,
stabilita_estremi_liquidazione. Per ognuna lo script: (1) se servono, conta i trade dei
casi con conta_trade; (2) scrive nel log la registrazione (tipo_test verifica,
verifica_di, previsione, criterio, trade stimati); (3) esegue; (4) scrive il risultato
con l'esito secondo la regola della Fase 4 («Quando una verifica e' superata»).

Le verifiche non cambiano le regole del candidato e non servono a sceglierne un'altra.
"""

import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import comune  # noqa: E402
import idee  # noqa: E402
import registro  # noqa: E402
from registra import parametri_completi  # noqa: E402

CRITERI = {
    "costi_doppi": "batte ancora nettamente la (b) ricalcolata a costi doppi e il suo R medio a costi doppi resta positivo",
    "ritardo": "il t contro la (b) ricalcolata col ritardo di una barra resta positivo e almeno la meta' del t senza ritardo",
    "intrabarra_opposta": "si dichiara la differenza (nessuna soglia)",
    "robustezza": ("ogni parametro numerico spostato del 20% in su e in giu', uno alla volta (interi a round(0,8 v) e "
                   "round(1,2 v), meta' verso l'alto, +-1 se restano uguali); ogni caso contato prima; un caso sotto 70 "
                   "trade si dichiara e non conta; un caso non valutabile conta come fallito; nei casi che contano t "
                   "contro la (b) ricalcolata positivo, e netta in almeno meta'; se contano meno della meta' dei casi "
                   "previsti la verifica non e' superata"),
    "timeframe_adiacenti": ("su ogni timeframe adiacente con i trade minimi il t contro la (b) ricalcolata resta "
                            "positivo; sotto i minimi si dichiara e non conta, non valutabile conta come fallito"),
    "stabilita_estremi_liquidazione": ("stabilita': R medio sopra la media della (b) in piu' della meta' degli anni di "
                                       "costruzione con almeno 10 trade (anno di uscita); estremi: senza i 3 trade "
                                       "migliori R medio sopra la media della (b); liquidazione: nessuna violazione"),
}

ADIACENTI = {"15m": ["30m"], "30m": ["15m", "1h"], "1h": ["30m", "2h"], "2h": ["1h", "4h"], "4h": ["2h", "6h"],
             "6h": ["4h", "8h"], "8h": ["6h", "12h"], "12h": ["8h", "1d"], "1d": ["12h"]}


def arrotonda(x):
    return int(math.floor(x + 0.5))


def casi_robustezza(V, kw):
    tutti = parametri_completi(V, kw)
    casi = []
    for nome, v in tutti.items():
        if isinstance(v, bool) or not isinstance(v, (int, float)):
            continue
        if isinstance(v, int):
            giu, su = arrotonda(0.8 * v), arrotonda(1.2 * v)
            if giu == v:
                giu = v - 1
            if su == v:
                su = v + 1
        else:
            giu, su = 0.8 * v, 1.2 * v
        for nuovo in (giu, su):
            casi.append({"parametro": nome, "valore": nuovo, "kw": dict(kw, **{nome: nuovo})})
    return casi


def kw_timeframe(V, kw, tf_da, tf_a):
    """Converte i parametri in barre per tenere la stessa durata (arrotondati, almeno 1)."""
    in_barre = getattr(V, "PARAMETRI_IN_BARRE", ())
    fattore = comune.dati.durata_intervallo(tf_da) / comune.dati.durata_intervallo(tf_a)
    tutti = parametri_completi(V, kw)
    nuovo = dict(kw)
    for nome in in_barre:
        nuovo[nome] = max(1, arrotonda(tutti[nome] * fattore))
    return nuovo


def sintesi(esito):
    m, b = esito["metriche"], esito.get("baseline_b", {})
    return {"trade": m["trade"], "r_medio": m["r_medio"], "r_medio_per_anno": m["r_medio_per_anno"],
            "t_b": b.get("t"), "netta_b": b.get("netta"), "valutabile_b": b.get("valutabile"),
            "media_b": b.get("media"), "percentile_caso": esito.get("percentile_caso")}


def main() -> None:
    nome, verifica, previsione = sys.argv[1], sys.argv[2], sys.argv[3]
    V, kw, tf = idee.VARIANTI[nome]
    voci = registro.voci()
    reg = [v for v in voci if v.get("variante_ipotesi") == nome and v["tipo"] == "registrazione" and v.get("tipo_test") == "variante"][0]
    ris = [v for v in voci if v["id"] == reg["id"] and v["tipo"] == "risultato"][0]
    ident = f"{reg['id']}-V-{verifica}"
    if any(v["id"] == ident for v in voci):
        raise SystemExit(f"{ident} gia' registrata")

    casi = []
    if verifica == "robustezza":
        for c in casi_robustezza(V, kw):
            c["trade_stimati"] = comune.conta(V, c["kw"], tf)["trade"]
            casi.append(c)
        stimati = {f"{c['parametro']}={c['valore']}": c["trade_stimati"] for c in casi}
    elif verifica == "timeframe_adiacenti":
        for tf2 in ADIACENTI[tf]:
            k2 = kw_timeframe(V, kw, tf, tf2)
            casi.append({"timeframe": tf2, "kw": k2, "trade_stimati": comune.conta(V, k2, tf2)["trade"]})
        stimati = {c["timeframe"]: c["trade_stimati"] for c in casi}
    else:
        stimati = reg["trade_stimati"]

    registro.aggiungi({
        "id": ident, "tipo": "registrazione", "tipo_test": "verifica", "verifica_di": reg["id"],
        "variante_ipotesi": nome, "verifica": verifica, "periodo": "costruzione",
        "casi": [{k: v for k, v in c.items() if k != "kw"} | {"parametri": c["kw"]} for c in casi] or None,
        "previsione": previsione, "criterio_successo": CRITERI[verifica], "trade_stimati": stimati,
    })

    t0 = float(ris["baseline_b"]["t"])
    media_b0 = float(ris["baseline_b"]["media"])
    out = {"id": ident, "tipo": "risultato", "verifica": verifica}
    if verifica == "costi_doppi":
        e = comune.valuta(V, kw, tf, comune.parametri(moltiplicatore_costi=2.0), con_a=False)
        s = sintesi(e)
        out.update({"esito": s, "superata": bool(s["netta_b"] and s["r_medio"] > 0)})
    elif verifica == "ritardo":
        e = comune.valuta(V, kw, tf, comune.parametri(ritardo_barre=1), con_a=False)
        s = sintesi(e)
        t1 = s["t_b"] if isinstance(s["t_b"], (int, float)) else -math.inf
        out.update({"esito": s, "t_senza_ritardo": t0, "superata": bool(t1 > 0 and t1 >= 0.5 * t0)})
    elif verifica == "intrabarra_opposta":
        e = comune.valuta(V, kw, tf, comune.parametri(riempimento_intrabarra="target_prima"), con_a=False)
        s = sintesi(e)
        out.update({"esito": s, "differenza_r_medio": s["r_medio"] - float(ris["metriche"]["r_medio"]),
                    "superata": None, "nota": "il candidato non ha target: la regola intra-barra non puo' cambiare nulla"
                    if all(parametri_completi(V, kw).get(k) is None for k in ("target",)) else ""})
    elif verifica == "robustezza":
        righe, contano, positivi, netti = [], 0, 0, 0
        for c in casi:
            riga = {"parametro": c["parametro"], "valore": c["valore"], "trade_stimati": c["trade_stimati"]}
            if c["trade_stimati"] < comune.TRADE_MINIMI_COSTRUZIONE:
                riga["conta"] = False
            else:
                e = comune.valuta(V, c["kw"], tf, con_a=False)
                s = sintesi(e)
                riga.update(s)
                riga["conta"] = True
                contano += 1
                if s["valutabile_b"] and s["t_b"] > 0:
                    positivi += 1
                if s["valutabile_b"] and s["netta_b"]:
                    netti += 1
            righe.append(riga)
        superata = bool(contano >= len(casi) / 2 and positivi == contano and netti >= contano / 2)
        out.update({"casi": righe, "casi_previsti": len(casi), "casi_che_contano": contano,
                    "t_positivo": positivi, "netti": netti, "superata": superata})
    elif verifica == "timeframe_adiacenti":
        righe, ok = [], True
        for c in casi:
            riga = {"timeframe": c["timeframe"], "parametri": c["kw"], "trade_stimati": c["trade_stimati"]}
            if c["trade_stimati"] < comune.TRADE_MINIMI_COSTRUZIONE:
                riga["conta"] = False
            else:
                e = comune.valuta(V, c["kw"], c["timeframe"], con_a=False)
                s = sintesi(e)
                riga.update(s)
                riga["conta"] = True
                if not (s["valutabile_b"] and s["t_b"] > 0):
                    ok = False
            righe.append(riga)
        out.update({"casi": righe, "superata": ok})
    elif verifica == "stabilita_estremi_liquidazione":
        m = ris["metriche"]
        anni = [a for a, n in m["trade_per_anno"].items() if n >= 10]
        sopra = [a for a in anni if m["r_medio_per_anno"][a] > media_b0]
        stabile = len(sopra) > len(anni) / 2
        senza3 = m["r_medio_senza_3_migliori"]
        estremi = senza3 is not None and senza3 > media_b0
        liq = m.get("n_violazioni_liquidazione", 0) == 0
        out.update({"anni_con_10_trade": anni, "anni_sopra_media_b": sopra, "media_b": media_b0,
                    "stabilita": stabile, "r_senza_3_migliori": senza3, "estremi": estremi,
                    "violazioni_liquidazione": m.get("n_violazioni_liquidazione"), "liquidazione": liq,
                    "superata": bool(stabile and estremi and liq)})
    out["data"] = registro.adesso()
    registro.aggiungi(out)
    uscita = comune.LAVORO / f"{nome}_verifica_{verifica}.json"
    uscita.write_text(json.dumps(registro.pulisci(out), indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(ident, "superata:", out.get("superata"))


if __name__ == "__main__":
    main()
