import json, sys
import numpy as np
sys.path.insert(0, ".")
from research.src import catalogo3 as cat
from research.src.motore3 import esegui, simula_da, Regole, COSTI_NORMALI
import research.collaudo_3.collaudo as co

righe = [json.loads(x) for x in open("research/collaudo_3/esiti/prova_a.jsonl")]
out = []
for r in righe:
    v = r["variante"]; s = co.serie_rimescolata(v["timeframe"], r["serie"])
    c = cat.compila(v, s)
    ris = esegui(c, Regole(), COSTI_NORMALI, 0, len(s) - 1)
    def scomponi(trades):
        costi = np.array([t.commissioni / t.rischio_usdt for t in trades])
        fund = np.array([t.funding / t.rischio_usdt for t in trades])
        rr = np.array([t.r for t in trades])
        lordo = rr + costi - fund
        dist = np.array([abs(t.prezzo_ingresso - t.stop_iniziale) / t.prezzo_ingresso for t in trades])
        durata = np.array([t.candele_in_posizione for t in trades])
        return dict(r=rr.mean(), lordo=lordo.mean(), costi=costi.mean(), funding=fund.mean(), dist=dist.mean(), durata=durata.mean())
    cand = scomponi(ris.trade)
    amm = np.flatnonzero(c.ammessa)
    forz = [simula_da(c, int(j), Regole(), COSTI_NORMALI, len(s) - 1, forzato=True) for j in amm]
    forz = [e.trade for e in forz if e.tipo == "trade"]
    caso = scomponi(forz)
    out.append(dict(numero=r["numero"], p=r["p_value"], tf=v["timeframe"], dir=v["direzione"],
                    filtro=(v["filtro"] or {}).get("codice"), ingresso=v["ingresso"]["codice"],
                    conferma=(v["conferma"] or {}).get("codice"), tipo=v["tipo_ingresso"]["codice"],
                    stop=v["stop"]["codice"], uscite="+".join(u["codice"] for u in v["uscite"]),
                    cand=cand, caso=caso, casuali_fase2=r["media_casuali"]))
json.dump(out, open("research/collaudo_3/diagnosi/diagnosi_a.json", "w"))
for o in sorted(out, key=lambda o: o["p"])[:30]:
    a, b = o["cand"], o["caso"]
    print(f"p {o['p']:.3f} {o['tf']:>3} {o['dir']:5} {str(o['filtro']):4} {o['ingresso']:3} {str(o['conferma']):4} {o['tipo']} {o['stop']} {o['uscite']:7} | "
          f"R {a['r']:+.3f}/{b['r']:+.3f} (fase2 {o['casuali_fase2']:+.3f}) lordo {a['lordo']:+.3f}/{b['lordo']:+.3f} costi {a['costi']:.3f}/{b['costi']:.3f} "
          f"fund {a['funding']:+.3f}/{b['funding']:+.3f} dist {a['dist']*100:.2f}/{b['dist']*100:.2f}% dur {a['durata']:.1f}/{b['durata']:.1f}")
