"""Fase 4: verifiche del candidato XRPUSDT-V21r3 sui dati di costruzione, ognuna registrata prima di eseguirla.

Le verifiche non cambiano le regole e non servono a scegliere. Esiti anche in data/insample/XRPUSDT/esiti.txt.
"""
import time

from research.campagne.XRPUSDT.codice import quadro as q
from research.campagne.XRPUSDT.codice.esegui import scrivi_esito
from research.campagne.XRPUSDT.codice.quadro import Variante
from research.campagne.XRPUSDT.codice.varianti import _i11

CAND = "XRPUSDT-V21r3"
BASE = dict(soglia=0.0020, caduta=0.10, k=1.5, n_atr=14, tenuta=4)


def var(tf="1h", **kw):
    p = {**BASE, **kw}
    return Variante(CAND, tf, "long", _i11("long", p["soglia"], p["caduta"], p["k"], p["n_atr"]), p["tenuta"],
                    {"idea": "I-11"})


VERIFICHE = []
# 1. robustezza: ogni parametro numerico +-20%, uno alla volta (interi: round(0,8 x) e round(1,2 x))
for nome, valori in (("soglia", (0.0016, 0.0024)), ("caduta", (0.08, 0.12)), ("k", (1.2, 1.8)),
                     ("n_atr", (11, 17)), ("tenuta", (3, 5))):
    for x in valori:
        VERIFICHE.append((f"robustezza {nome}={x}", "robustezza", var(**{nome: x}), q.parametri()))
# 2. timeframe adiacenti: parametri in barre convertiti alla stessa durata
VERIFICHE.append(("timeframe 30m (tenuta 8, ATR 28)", "timeframe", var("30m", tenuta=8, n_atr=28), q.parametri()))
VERIFICHE.append(("timeframe 2h (tenuta 2, ATR 7)", "timeframe", var("2h", tenuta=2, n_atr=7), q.parametri()))
# 6. ritardo di una barra, 8. costi doppi, 5. regola intra-barra opposta
VERIFICHE.append(("ritardo di una barra", "ritardo", var(), q.parametri(ritardo_barre=1)))
VERIFICHE.append(("costi doppi", "costi_doppi", var(), q.parametri(moltiplicatore_costi=2.0)))
VERIFICHE.append(("regola intra-barra opposta (target prima)", "intrabarra", var(), q.parametri(riempimento="target_prima")))

CRITERI = {
    "robustezza": "il caso si conta prima con conta_trade; sotto 70 non conta; nei casi che contano t contro la (b) "
                  "positivo, e in almeno meta' dei casi netta; se contano meno della meta' dei 10 casi, non superata",
    "timeframe": "con almeno 70 trade, t contro la (b) ricalcolata positivo; sotto 70 si dichiara e non conta",
    "ritardo": "t contro la (b) ricalcolata col ritardo positivo e almeno la meta' di 2,33",
    "costi_doppi": "batte nettamente la (b) ricalcolata a costi doppi e R medio a costi doppi positivo",
    "intrabarra": "si dichiara la differenza (la variante non ha target: attesa nessuna differenza)",
}

for nome, tipo, v, par in VERIFICHE:
    s = q.serie(v.tf)
    c = q.conta(v, par) if tipo in ("robustezza", "timeframe") else None
    stimati = c["trade"] if c else 97
    q.scrivi_log({"id": f"{CAND}-verifica-{nome}", "tipo": "registrazione", "tipo_test": "verifica", "verifica_di": CAND,
                  "verifica": tipo, "descrizione": nome, "timeframe": v.tf, "periodo": "costruzione",
                  "trade_stimati": stimati, "criterio_successo": CRITERI[tipo]})
    if c and c["trade"] < q.TRADE_MINIMI_COSTRUZIONE:
        q.scrivi_log({"id": f"{CAND}-verifica-{nome}", "tipo": "risultato", "conta": "sotto i trade minimi: non conta",
                      "trade": c["trade"]})
        scrivi_esito(f"VERIFICA {nome}: sotto minimo ({c['trade']})")
        continue
    t0 = time.time()
    r = q.valuta(v, s, par)
    m = r["metriche"]
    q.scrivi_log({"id": f"{CAND}-verifica-{nome}", "tipo": "risultato", "metriche": m, "blocco": r.get("blocco"),
                  "baseline_a": r.get("baseline_a"), "baseline_b": r.get("baseline_b"),
                  "percentile_caso": r.get("percentile_caso"), "valutabile": r.get("valutabile"),
                  "secondi": round(time.time() - t0, 1)})
    scrivi_esito(f"VERIFICA {nome}: trade={m['trade']} R={m['r_medio']:.3f} b_media={r['baseline_b'].get('media', float('nan')):.3f} "
                 f"t_b={r['baseline_b'].get('t', float('nan')):.2f} netta_b={r['baseline_b'].get('netta')} "
                 f"t_a={r['baseline_a'].get('t', float('nan')):.2f} viol_liq={m['n_violazioni_liquidazione']} "
                 f"ridotti={m['n_ridotti']} R_anno={ {k: round(x, 3) for k, x in m['r_medio_per_anno'].items()} } "
                 f"trade_anno={m['trade_per_anno']} senza3={m['r_medio_senza_3_migliori']}")
