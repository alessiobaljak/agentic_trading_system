"""Limiti: durate rispetto al margine e allo sfasamento; trade lunghi; sfasata piu' vicina. Sola lettura."""
import json, math
from collections import Counter
from datetime import datetime, timezone
import numpy as np
from scipy.stats import norm, t as student

D = "/home/user/coordinamento/research/taratura/placebo_gruppo"
righe = [json.loads(l) for k in range(4) for l in open(f"{D}/esiti_k{k}.jsonl") if l.strip()]

def z_of(c):
    t_, g = float(c["t"]), int(c["gradi_liberta"])
    return float(norm.isf(student.sf(t_, g))) if t_ >= 0 else float(norm.ppf(student.cdf(t_, g)))

def valutabile(r):
    e = r.get("esame")
    if not e or not e.get("contro_b") or not e["contro_b"].get("valutabile"):
        return False
    if r["periodo"] == "costruzione":
        return r["conta"]["esito"] == "registrabile" and e["trade"] >= 700 and r["conta"]["quota_moneta_piu_presente"] <= 0.1
    return e["trade"] >= 300

val = [r for r in righe if valutabile(r)]
flag = [r for r in val if r["esame"]["durata_massima_barre"] >= r["margine"] - 60]
print("valutabili", len(val), "segnalate", len(flag))
oltre = [r for r in flag if r["esame"]["durata_massima_barre"] > r["margine"]]
print("segnalate con durata massima OLTRE il margine:", len(oltre), "; sotto il margine (fra margine-60 e margine):", len(flag) - len(oltre))
rat = [r["esame"]["durata_massima_barre"] / r["margine"] for r in flag]
print("rapporto durata/margine fra le segnalate: mediana %.2f, min %.2f, max %.2f" % (np.median(rat), min(rat), max(rat)))
# durata >= L - d (il trade di un ingresso che ha fatto il giro puo' arrivare al suo segnale vero)
wrap = [r for r in val if r["esame"]["durata_massima_barre"] >= r["L"] - r["d"]]
wrap2 = [r for r in val if r["esame"]["durata_massima_barre"] >= min(r["d"], r["L"] - r["d"])]
print("valutabili con durata massima >= L - d:", len(wrap), "; >= min(d, L-d):", len(wrap2))
for r in wrap2:
    print("   ", r["etichetta"], "d", r["d"], "L", r["L"], "dur", r["esame"]["durata_massima_barre"], "z %.2f" % z_of(r["esame"]["contro_b"]))
# z delle segnalate vs non segnalate
for p in ("costruzione", "validazione"):
    zf = [z_of(r["esame"]["contro_b"]) for r in flag if r["periodo"] == p]
    zn = [z_of(r["esame"]["contro_b"]) for r in val if r["periodo"] == p and r not in flag]
    print(p, "z segnalate n %d mu %.3f sd %.3f | altre n %d mu %.3f sd %.3f" % (len(zf), np.mean(zf), np.std(zf, ddof=1), len(zn), np.mean(zn), np.std(zn, ddof=1)))
    zs = np.array(zn); mu, sd = zs.mean(), zs.std(ddof=1)
    s = 2.0 if p == "costruzione" else 1.2816
    print("   M3 sulle sole non segnalate: %.2f%%" % (100 * norm.sf((s - mu) / sd)), "conteggio", int((zs > s).sum()), "su", len(zs))

# sfasata piu' vicina: distanza 0
for r in val:
    v = r["esame"]["sfasate"].get("senza_la_piu_vicina")
    if v and v["distanza_barre"] == 0:
        print("distanza 0:", r["etichetta"], "scarto_in_sd %.2f" % v["scarto_in_sd"], "z %.2f" % z_of(r["esame"]["contro_b"]))
sc = [r["esame"]["sfasate"]["senza_la_piu_vicina"]["scarto_in_sd"] for r in val if r["esame"]["sfasate"].get("senza_la_piu_vicina") and r["esame"]["sfasate"]["senza_la_piu_vicina"].get("scarto_in_sd") is not None]
print("scarto_in_sd della sfasata piu' vicina: n", len(sc), "mediana %.2f media %.2f, >2: %d, >1.645: %d" % (np.median(sc), np.mean(sc), sum(1 for x in sc if x > 2), sum(1 for x in sc if x > 1.645)))
for p in ("costruzione", "validazione"):
    sc = [(r["esame"]["sfasate"]["senza_la_piu_vicina"]["distanza_barre"], r["esame"]["sfasate"]["senza_la_piu_vicina"]["scarto_in_sd"]) for r in val if r["periodo"] == p]
    near = [s for dd, s in sc if dd <= 24]
    print(p, "sfasate entro 24 barre dagli ingressi veri:", len(near), "scarto mediano %.2f" % np.median(near) if near else "")

# trade piu' lunghi
r = max(righe, key=lambda r: r["esame"]["durata_massima_barre"])
print("piu' lunga:", r["etichetta"], r["esame"]["durata_massima_barre"])
tr = [json.loads(l) for l in open(r["esame"]["file"]["trade"])]
step = 3600_000 if r["timeframe"] == "1h" else 4 * 3600_000
tr.sort(key=lambda x: x["ts_uscita"] - x["ts_entrata"], reverse=True)
for x in tr[:3]:
    print("   ", x["simbolo"], datetime.fromtimestamp(x["ts_entrata"] / 1000, timezone.utc), datetime.fromtimestamp(x["ts_uscita"] / 1000, timezone.utc), x["esito"], "entrata", x["entrata"], "stop", x["stop"], "target", x["target"], "r %.2f" % x["r"])
# trade di costruzione che escono dopo la fine della costruzione (finestra unione)
fuori = Counter()
for r in righe:
    fin = r["finestra_unione"][1]
    ini = r["finestra_unione"][0]
    for l in open(r["esame"]["file"]["trade"]):
        x = json.loads(l)
        if x["ts_uscita"] > fin or x["ts_entrata"] < ini:
            fuori[r["periodo"]] += 1
print("trade con uscita oltre la fine della finestra del periodo (o entrata prima):", dict(fuori))
print("esiti dei trade (tutte):")
es = Counter()
for r in righe:
    for l in open(r["esame"]["file"]["trade"]):
        es[(r["regola"], json.loads(l)["esito"])] += 1
print(es)
