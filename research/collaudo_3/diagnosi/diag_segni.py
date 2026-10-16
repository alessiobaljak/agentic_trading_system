"""Diagnosi (NON prova ufficiale): serie con la direzione di ogni candela girata a caso (volatilita' al suo posto)."""
import json, sys
from concurrent.futures import ProcessPoolExecutor
import numpy as np
sys.path.insert(0, ".")
sys.path.insert(0, "research/collaudo_3/diagnosi")
STRATO = len(sys.argv) > 1 and sys.argv[1] == "strato"

def gira(s, seme):
    from research.src import catalogo3 as cat
    o, h, l, c = s.open, s.high, s.low, s.close
    g = np.log(o[1:] / c[:-1]); b = np.log(c[1:] / o[1:]); u = np.log(h[1:] / o[1:]); d = np.log(l[1:] / o[1:])
    mo, mh, ml, mc = (np.log(x[1:] / o[1:]) for x in (s.mark_open, s.mark_high, s.mark_low, s.mark_close))
    giro = np.random.default_rng(seme).random(len(g)) < 0.5
    g2 = np.where(giro, -g, g); b2 = np.where(giro, -b, b); u2 = np.where(giro, -d, u); d2 = np.where(giro, -u, d)
    mo2 = np.where(giro, -mo, mo); mh2 = np.where(giro, -ml, mh); ml2 = np.where(giro, -mh, ml); mc2 = np.where(giro, -mc, mc)
    lc = np.log(c[0]) + np.cumsum(g2 + b2); lo = np.concatenate([[np.log(c[0])], lc[:-1]]) + g2
    n_o = np.concatenate([[o[0]], np.exp(lo)]); n_c = np.concatenate([[c[0]], np.exp(lc)])
    n_h = np.concatenate([[h[0]], np.exp(lo + u2)]); n_l = np.concatenate([[l[0]], np.exp(lo + d2)])
    m_o = np.concatenate([[s.mark_open[0]], np.exp(lo + mo2)]); m_h = np.concatenate([[s.mark_high[0]], np.exp(lo + mh2)])
    m_l = np.concatenate([[s.mark_low[0]], np.exp(lo + ml2)]); m_c = np.concatenate([[s.mark_close[0]], np.exp(lo + mc2)])
    return cat.Serie(s.timeframe, s.ts.copy(), n_o, n_h, n_l, n_c, s.volume.copy(), m_o, m_h, m_l, m_c, s.funding_ts.copy(), s.funding_tasso.copy())

def lavoro(riga):
    import research.collaudo_3.collaudo as co
    from research.src import catalogo3 as cat
    from research.src import statistica3 as st
    from research.src.motore3 import esegui, metriche
    v = riga["variante"]; s = gira(co.serie_vera(v["timeframe"]), riga["serie"])
    c = cat.compila(v, s); ris = esegui(c, inizio=0, fine=len(s) - 1); m = metriche(ris, s)
    if m["trade"] < 30: return {"numero": riga["numero"], "pochi_trade": m["trade"]}
    if STRATO:
        from diag_strato import entrate_stratificate
        val = entrate_stratificate(c, ris.trade, 0, len(s) - 1)
        if len(val) < 1000: return {"numero": riga["numero"], "pochi": len(val)}
    else:
        try: val = st.entrate_casuali(c, m["trade"], 0, len(s) - 1)["valori"]
        except st.SimulazioneImpossibile as e: return {"numero": riga["numero"], "impossibile": str(e)}
    p = (1 + int(np.sum(val >= m["r_medio"]))) / 1001
    v2 = riga["variante"]
    return {"numero": riga["numero"], "p": p, "r": m["r_medio"], "caso": float(np.mean(val)), "trade": m["trade"],
            "vol": v2["ingresso"]["codice"] == "E12" or (v2["conferma"] or {}).get("codice") == "C1"}

if __name__ == "__main__":
    righe = [json.loads(x) for x in open("research/collaudo_3/esiti/prova_a.jsonl")]
    with ProcessPoolExecutor(3) as ex: out = list(ex.map(lavoro, righe))
    ok = [r for r in out if "p" in r]
    print("strato" if STRATO else "normale", "varianti", len(ok), "p<0.10:", sum(r["p"] < 0.10 for r in ok), "p<=0.023:", sum(r["p"] <= 0.023 for r in ok),
          "R %.3f caso %.3f" % (np.mean([r["r"] for r in ok]), np.mean([r["caso"] for r in ok])))
    x = [r for r in ok if r["vol"]]; print("   con volume", len(x), "p<0.10:", sum(r["p"] < 0.10 for r in x))
    print("   decimi", [sum(1 for r in ok if k/10 <= r["p"] < (k+1)/10) for k in range(10)])
