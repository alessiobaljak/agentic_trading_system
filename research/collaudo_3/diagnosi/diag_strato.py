"""Diagnosi (NON prova ufficiale): entrate casuali con la stessa distribuzione di larghezza dello stop del candidato."""
import json, sys, math, bisect
from concurrent.futures import ProcessPoolExecutor
import numpy as np
sys.path.insert(0, ".")
N_BIN = int(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1].isdigit() else 5

def entrate_stratificate(c, cand_trades, inizio, fine, n_sim=1000, seme=2026):
    from research.src.motore3 import simula_da, Regole, COSTI_NORMALI
    n_trade = len(cand_trades)
    ammesse = [int(x) for x in np.flatnonzero(c.ammessa[inizio:fine + 1]) + inizio]
    esiti = [simula_da(c, j, Regole(), COSTI_NORMALI, fine, forzato=True) for j in ammesse]
    larg = np.array([abs(t.prezzo_ingresso - t.stop_iniziale) / t.prezzo_ingresso for t in cand_trades])
    tagli = np.quantile(larg, np.linspace(0, 1, N_BIN + 1)[1:-1]) if N_BIN > 1 else np.array([])
    def bin_di(x): return int(np.searchsorted(tagli, x, side="right"))
    e_trade = np.array([e.tipo == "trade" for e in esiti]); e_r = np.array([e.trade.r if e.tipo == "trade" else 0.0 for e in esiti])
    e_bin = np.array([bin_di(abs(e.trade.prezzo_ingresso - e.trade.stop_iniziale) / e.trade.prezzo_ingresso) if e.tipo == "trade" else -1 for e in esiti])
    succ = np.array([bisect.bisect_left(ammesse, max(e.libero_da, j + 1)) for j, e in zip(ammesse, esiti)])
    quota_c = np.bincount([bin_di(x) for x in larg], minlength=N_BIN) / n_trade
    quota_a = np.bincount(e_bin[e_trade], minlength=N_BIN) / max(1, e_trade.sum())
    w = np.where(quota_a > 0, quota_c / np.maximum(quota_a, 1e-12), 0.0); w = w / w.max()
    peso = np.where(e_trade, w[np.maximum(e_bin, 0)], 1.0)  # candele senza trade: peso 1 (non cambia niente)
    rng = np.random.default_rng(seme); n_amm = len(ammesse)
    def giri(q, quanti):
        pos = np.zeros(quanti, dtype=np.int64); conta = np.zeros(quanti, dtype=np.int64); somma = np.zeros(quanti); vive = np.arange(quanti)
        while len(vive):
            # processo di Bernoulli con probabilita' q * peso a ogni candela libera, per diradamento:
            # salto geometrico con probabilita' q, poi si entra con probabilita' peso
            pos[vive] += rng.geometric(q, size=len(vive)) - 1
            dentro = pos[vive] < n_amm
            vive = vive[dentro]
            if not len(vive): break
            pv = pos[vive]
            entra = rng.random(len(vive)) < peso[pv]
            ei = vive[entra]; pe = pv[entra]
            t = e_trade[pe]; conta[ei] += t; somma[ei] += np.where(t, e_r[pe], 0.0); pos[ei] = succ[pe]
            pos[vive[~entra]] += 1
        return conta, somma
    basso, alto = math.log(1e-6), 0.0
    for _ in range(22):
        m = 0.5 * (basso + alto); cnt, _ = giri(math.exp(m), 128)
        if cnt.mean() < n_trade: basso = m
        else: alto = m
    q = math.exp(0.5 * (basso + alto)); medie = []; fatti = 0
    while len(medie) < n_sim and fatti < 600000:
        cnt, som = giri(q, 4096); fatti += 4096
        for k in np.flatnonzero(cnt == n_trade):
            if len(medie) < n_sim: medie.append(som[k] / n_trade)
    return np.array(medie)

def lavoro(riga):
    import research.collaudo_3.collaudo as co
    from research.src import catalogo3 as cat
    from research.src.motore3 import esegui, metriche
    v = riga["variante"]; s = co.serie_rimescolata(v["timeframe"], riga["serie"])
    c = cat.compila(v, s); ris = esegui(c, inizio=0, fine=len(s) - 1); m = metriche(ris, s)
    val = entrate_stratificate(c, ris.trade, 0, len(s) - 1)
    if len(val) < 1000: return {"numero": riga["numero"], "pochi": len(val)}
    p = (1 + int(np.sum(val >= m["r_medio"]))) / 1001
    return {"numero": riga["numero"], "p": p, "r": m["r_medio"], "caso": float(val.mean()), "dir": v["direzione"], "stop": v["stop"]["codice"]}

if __name__ == "__main__":
    righe = [json.loads(x) for x in open("research/collaudo_3/esiti/prova_a.jsonl")]
    with ProcessPoolExecutor(3) as ex: out = list(ex.map(lavoro, righe))
    ok = [r for r in out if "p" in r]
    print("bin", N_BIN, "varianti", len(ok), "p<0.10:", sum(r["p"] < 0.10 for r in ok), "p<0.023:", sum(r["p"] <= 0.023 for r in ok),
          "R %.3f caso %.3f" % (np.mean([r["r"] for r in ok]), np.mean([r["caso"] for r in ok])))
    for g in ("S1", "S2", "S3"):
        x = [r for r in ok if r["stop"] == g]; print("  ", g, len(x), "p<0.10:", sum(r["p"] < 0.10 for r in x))
    dec = [sum(1 for r in ok if k/10 <= r["p"] < (k+1)/10) for k in range(10)]; print("  decimi", dec)
