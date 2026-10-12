"""Fase 4: verifiche del candidato DOGEUSDT-042 sui dati di costruzione, ognuna registrata PRIMA.

Criteri (PROTOCOLLO.md, Fase 4, «Quando una verifica e' superata»). Le verifiche non cambiano
le regole del candidato e non servono a sceglierne un'altra.
Uscite in data/insample/DOGEUSDT/uscite/verifiche.txt; FINE alla fine.
"""
import sys
from dataclasses import replace
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import quadro as q  # noqa: E402
import registro  # noqa: E402
from varianti import Strettoia, allentata  # noqa: E402

CAND = "DOGEUSDT-042"
BASE = dict(tf="1h", stop_atr=3.0, finestra=480, barre=12, nb=20, kb=2.0, percentile=20, n_atr=14)
USCITA = q.RADICE_REPO / "research" / "data" / "insample" / "DOGEUSDT" / "uscite" / "verifiche.txt"


def scrivi(t):
    with open(USCITA, "a") as f:
        f.write(t + "\n")
    print(t, flush=True)


def crea(**cambi):
    return allentata(Strettoia, "short", **{**BASE, **cambi})


def sintesi(out):
    m = out["metriche"]
    a, b = out.get("baseline_a", {}), out.get("baseline_b", {})
    return {"trade": m["trade"], "r_medio": m["r_medio"], "profit_factor": m["profit_factor"],
            "r_medio_per_anno": m["r_medio_per_anno"], "r_medio_senza_3_migliori": m["r_medio_senza_3_migliori"],
            "violazioni_liquidazione": m["violazioni_liquidazione"], "stop_oltre_6_per_cento": m["stop_oltre_6_per_cento"],
            "t_a": a.get("t"), "netta_a": a.get("netta"), "t_b": b.get("t"), "netta_b": b.get("netta"),
            "soglia_b": b.get("soglia"), "media_b": b.get("media"), "valutabile": out.get("valutabile")}


def verifica(id_, cosa, previsione, crea_v, parametri=q.PARAMETRI, stop_mark=False):
    v = crea_v()
    cont = q.conta(v, parametri, stop_mark)
    registro.aggiungi({"id": id_, "tipo": "registrazione", "tipo_test": "verifica", "verifica_di": CAND,
                       "cosa": cosa, "previsione": previsione, "periodo": "costruzione",
                       "trade_stimati": cont["trade"], "conteggio": cont})
    if cont["trade"] < q.TRADE_MINIMI_COSTRUZIONE:
        registro.aggiungi({"id": id_, "tipo": "risultato", "esito": "sotto i trade minimi: si dichiara e non conta",
                           "trade": cont["trade"]})
        scrivi(f"{id_} {cosa}: sotto il minimo ({cont['trade']})")
        return None
    out, _ = q.valuta(crea_v(), parametri=parametri, stop_mark=stop_mark)
    s = sintesi(out)
    registro.aggiungi({"id": id_, "tipo": "risultato", **s})
    scrivi(f"{id_} {cosa}: {s}")
    return s


ris = {}
# 1. robustezza: ogni parametro numerico +-20%, uno alla volta (interi: round con le meta' in su)
casi = [("nb", 16, 24), ("kb", 1.6, 2.4), ("finestra", 384, 576), ("percentile", 16, 24),
        ("barre", 10, 14), ("stop_atr", 2.4, 3.6), ("n_atr", 11, 17)]
k = 0
for nome, giu, su in casi:
    for val in (giu, su):
        k += 1
        ris[f"rob_{nome}_{val}"] = verifica(f"{CAND}-V{k:02d}", f"robustezza: {nome} = {val} (originale {BASE[nome]})",
                                            "t contro la (b) positivo; netta in circa meta' dei casi o meno",
                                            lambda nome=nome, val=val: crea(**{nome: val}))
# 2. timeframe adiacenti, parametri in barre convertiti per la stessa durata
ris["tf_30m"] = verifica(f"{CAND}-V15", "timeframe adiacente 30m (bande 40, finestra 960, uscita 24, ATR 28)",
                         "t contro la (b) positivo", lambda: crea(tf="30m", nb=40, finestra=960, barre=24, n_atr=28))
ris["tf_2h"] = verifica(f"{CAND}-V16", "timeframe adiacente 2h (bande 10, finestra 240, uscita 6, ATR 7)",
                        "t contro la (b) positivo", lambda: crea(tf="2h", nb=10, finestra=240, barre=6, n_atr=7))
# 6. ritardo di una barra, (b) ricalcolata col ritardo
ris["ritardo"] = verifica(f"{CAND}-V17", "ritardo di una barra", "t contro la (b) positivo e almeno meta' di 2,14",
                          lambda: crea(), parametri=replace(q.PARAMETRI, ritardo_barre=1))
# 8. costi doppi, (b) a costi doppi
ris["costi_doppi"] = verifica(f"{CAND}-V18", "costi doppi", "R medio positivo; netta contro la (b) incerta",
                              lambda: crea(), parametri=replace(q.PARAMETRI, moltiplicatore_costi=2.0))
# 5. regola intra-barra opposta e dettagli del feed (si dichiara la differenza)
ris["target_prima"] = verifica(f"{CAND}-V19", "regola intra-barra opposta (target prima)",
                               "nessuna differenza: il candidato non ha target", lambda: crea(),
                               parametri=replace(q.PARAMETRI, riempimento_intrabarra="target_prima"))
ris["stop_sul_mark"] = verifica(f"{CAND}-V20", "dettagli del feed: stop che scatta sul mark invece che sul last",
                                "differenza piccola", lambda: crea(), stop_mark=True)
scrivi("FINE")
