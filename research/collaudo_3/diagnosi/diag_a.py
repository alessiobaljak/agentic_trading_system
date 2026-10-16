"""Diagnosi della prova A (NON e' la prova ufficiale): stesse 100 varianti, serie senza tendenza e/o costi zero."""
import json, sys, os
from concurrent.futures import ProcessPoolExecutor
import numpy as np
sys.path.insert(0, ".")
MODO = sys.argv[1]  # "senza_tendenza", "senza_costi", "entrambi"

def prepara():
    import research.collaudo_3.collaudo as co
    import research.src.statistica3 as st
    from research.src.motore3 import Costi
    if MODO in ("senza_costi", "entrambi"):
        st.COSTI_NORMALI = Costi(0.0, 0.0, 0.0)
    if MODO in ("senza_tendenza", "entrambi"):
        vera = co.rimescola
        def senza(s, seme):
            r = vera(s, seme)
            o, h, l, c = r.open, r.high, r.low, r.close
            mosse = (o[1:] / c[:-1]) * (c[1:] / o[1:])
            f = 1.0 / mosse.mean()
            # ogni candela dalla seconda: tutti i prezzi moltiplicati per f^k (k = candele passate)
            k = np.arange(len(o), dtype=float)
            scala = f ** k
            for nome in ("open", "high", "low", "close", "mark_open", "mark_high", "mark_low", "mark_close"):
                setattr(r, nome, getattr(r, nome) * scala)
            return r
        co.rimescola = senza
    return co, st

def lavoro(riga):
    co, st = prepara()
    from research.src import catalogo3 as cat
    v = riga["variante"]; s = co.serie_rimescolata(v["timeframe"], riga["serie"])
    try:
        es = st.fase2(v, s, 0, len(s) - 1)
    except st.SimulazioneImpossibile as e:
        return {"numero": riga["numero"], "impossibile": str(e)}
    return {"numero": riga["numero"], "p": es["p_value"], "r": es["metriche"]["r_medio"], "caso": es["casuali"]["media"],
            "supera": es["supera"], "dir": v["direzione"], "stop": v["stop"]["codice"]}

if __name__ == "__main__":
    righe = [json.loads(x) for x in open("research/collaudo_3/esiti/prova_a.jsonl")]
    out = []
    with ProcessPoolExecutor(3) as ex:
        for r in ex.map(lavoro, righe):
            out.append(r)
    ok = [r for r in out if "p" in r]
    print(MODO, "varianti", len(ok), "impossibili", len(out) - len(ok), "p<0.10:", sum(r["p"] < 0.10 for r in ok),
          "superano:", sum(r["supera"] for r in ok), "R medio %.3f caso %.3f" % (np.mean([r["r"] for r in ok]), np.mean([r["caso"] for r in ok])))
    for g in ("long", "short"):
        x = [r for r in ok if r["dir"] == g]; print("  ", g, len(x), "p<0.10:", sum(r["p"] < 0.10 for r in x))
    for g in ("S1", "S2", "S3"):
        x = [r for r in ok if r["stop"] == g]; print("  ", g, len(x), "p<0.10:", sum(r["p"] < 0.10 for r in x))
    json.dump(out, open(f"research/collaudo_3/diagnosi/diag_{MODO}.json", "w"))
