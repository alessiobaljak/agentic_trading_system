"""Fase 4: verifiche sui dati di costruzione del candidato BNBUSDT-043, ognuna registrata PRIMA.

Uso: python verifiche.py [nome ...]  (senza nomi: tutte). Esiti anche in data/insample/BNBUSDT/esiti.txt.
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))

import comune as C  # noqa: E402
import registro  # noqa: E402
import varianti as V  # noqa: E402
from lancia import scrivi_esito  # noqa: E402

import os  # noqa: E402

CAND = os.environ.get("CANDIDATO", "BNBUSDT-043")
if len(sys.argv) > 1 and sys.argv[1].startswith("BNBUSDT-"):
    CAND = sys.argv.pop(1)
if CAND == "BNBUSDT-043":
    BASE = dict(max_barre=12, k_stop=2.5, soglia_rsi=5.0, n_lunga=200, n_corta=5, atr_rel_min=0.015, n_atr=14, n_rsi=2)
    FILTRO = ("atr_rel_min", lambda ind: ~(ind["atr"] >= 0.015 * ind["close"]),
              "la (b) entra solo nelle barre con ATR(14) >= 1,5% della chiusura")
elif CAND == "BNBUSDT-044":
    BASE = dict(max_barre=12, k_stop=2.5, soglia_rsi=5.0, n_lunga=200, n_corta=5, dist_lunga_atr=1.7, n_atr=14, n_rsi=2)
    FILTRO = ("dist_lunga_atr", lambda ind: ~(ind["close"] - ind["sma200"] >= 1.7 * ind["atr"]),
              "la (b) entra solo nelle barre con close - SMA200 >= 1,7 ATR(14), cioe' in forte tendenza")
else:
    raise SystemExit(f"candidato sconosciuto {CAND}")


def fab(tf="1h", **mod):
    p = dict(BASE)
    p.update(mod)
    return lambda vid: V.i03(tf, vid, **p)


ROBUSTEZZA = [("soglia_rsi", 4.0), ("soglia_rsi", 6.0), ("n_lunga", 160), ("n_lunga", 240), ("n_corta", 4), ("n_corta", 6),
              ("k_stop", 2.0), ("k_stop", 3.0), ("max_barre", 10), ("max_barre", 14)]
if CAND == "BNBUSDT-043":
    ROBUSTEZZA += [("atr_rel_min", 0.012), ("atr_rel_min", 0.018)]
else:
    ROBUSTEZZA += [("dist_lunga_atr", 1.36), ("dist_lunga_atr", 2.04)]
ROBUSTEZZA += [("n_atr", 11), ("n_atr", 17), ("n_rsi", 1), ("n_rsi", 3)]

VERIFICHE = {}
for nome, val in ROBUSTEZZA:
    VERIFICHE[f"robustezza_{nome}_{val}"] = {"fab": fab(**{nome: val}), "kw": {"con_a": False},
                                            "descrizione": f"robustezza: {nome} da {BASE[nome]} a {val}, il resto invariato",
                                            "criterio": "conta se ha almeno 70 trade; t contro la (b) positivo; in almeno meta' dei casi che contano batte nettamente la (b)"}
VERIFICHE["tf_30m"] = {"fab": fab("30m", n_lunga=400, n_corta=10, max_barre=24, n_atr=28, n_rsi=4), "kw": {"con_a": False},
                       "descrizione": "timeframe adiacente 30m, parametri in barre convertiti alla stessa durata (SMA 400, SMA 10, 24 barre, ATR 28, RSI 4)",
                       "criterio": "se ha almeno 70 trade, t contro la (b) positivo"}
VERIFICHE["tf_2h"] = {"fab": fab("2h", n_lunga=100, n_corta=3, max_barre=6, n_atr=7, n_rsi=1), "kw": {"con_a": False},
                      "descrizione": "timeframe adiacente 2h, parametri in barre convertiti (SMA 100, SMA 3 da 2,5 arrotondato in su, 6 barre, ATR 7, RSI 1)",
                      "criterio": "se ha almeno 70 trade, t contro la (b) positivo"}
VERIFICHE["costi_doppi"] = {"fab": fab(), "kw": {"moltiplicatore_costi": 2.0, "con_a": False},
                            "descrizione": "costi doppi (commissioni, slippage e funding quando e' un costo), (b) ricalcolata a costi doppi",
                            "criterio": "batte ancora nettamente la (b) a costi doppi e R medio a costi doppi positivo"}
VERIFICHE["ritardo"] = {"fab": fab(), "kw": {"ritardo_barre": 1, "con_a": False},
                        "descrizione": "esecuzione ritardata di una barra, (b) ricalcolata col ritardo",
                        "criterio": "t contro la (b) positivo e almeno meta' del t senza ritardo"}
VERIFICHE["intrabarra_opposta"] = {"fab": fab(), "kw": {"riempimento": "target_prima", "con_a": False},
                                   "descrizione": "regola intra-barra opposta (target prima): la variante non ha target, atteso identico",
                                   "criterio": "si dichiara la differenza"}
VERIFICHE["scettico_b_volatile" if CAND == "BNBUSDT-043" else "scettico_b_tendenza"] = {
    "fab": fab(), "kw": {"con_a": False, "vieta_extra": FILTRO[1]},
    "descrizione": (f"prova dello scettico (Fase 5): {FILTRO[2]}, come il filtro del candidato; se il vantaggio era "
                    "solo l'effetto del filtro, contro questa (b) sparisce"),
    "criterio": "t contro questa (b) oltre la soglia: il vantaggio non e' solo l'effetto del filtro; t vicino a 0: lo e'"}


def esegui(nome):
    s = VERIFICHE[nome]
    vid_v = f"{CAND}-{nome}"
    v = s["fab"](vid_v)
    conteggio = C.conta(v)
    registro.aggiungi({"id": vid_v, "tipo": "registrazione", "tipo_test": "verifica", "verifica_di": CAND,
                       "descrizione": s["descrizione"], "timeframe": v.tf, "periodo": "costruzione",
                       "trade_stimati": conteggio["trade"], "criterio_successo": s["criterio"]})
    if conteggio["trade"] < 70 and nome != "ritardo":
        registro.aggiungi({"id": vid_v, "tipo": "risultato", "conta": False,
                           "commento": f"{conteggio['trade']} trade, sotto il minimo di 70: si dichiara e non conta"})
        scrivi_esito(f"{vid_v} NON CONTA {conteggio['trade']} trade")
        return
    res = C.valuta(v, **s["kw"])
    b = res.get("baseline_b", {})
    registro.aggiungi({"id": vid_v, "tipo": "risultato", "conta": True, "metriche": res["metriche"],
                       "baseline_b": b, "percentile_caso": res.get("percentile_caso"), "blocco": res.get("blocco"),
                       "barre_vietate_extra_quota": res.get("barre_vietate_extra_quota"),
                       "commento": f"t contro la (b) {b.get('t')}, netta {b.get('netta')}, R medio {res['metriche']['r_medio']:+.3f}"})
    scrivi_esito(f"{vid_v} n={res['metriche']['trade']} R={res['metriche']['r_medio']:+.3f} t_b={b.get('t')} netta={b.get('netta')}")


if __name__ == "__main__":
    for n in (sys.argv[1:] or list(VERIFICHE)):
        esegui(n)
    scrivi_esito("VERIFICHE FINITE")
