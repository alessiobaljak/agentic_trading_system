"""Ricalcolo indipendente della prova a placebo di gruppo, solo dagli esiti_k*.jsonl.
Non importa riassunto.py ne' esegui.py."""
import hashlib
import json
import math
import re
import sys
import zlib
from collections import Counter, defaultdict
from fractions import Fraction
from pathlib import Path

import numpy as np
from scipy.stats import norm
from scipy.stats import t as student

CART = Path("/home/user/coordinamento/research/taratura/placebo_gruppo")
PRINC = Path("/home/user/agentic_trading_system")
REGOLE = ("incrocio_medie", "rsi", "rottura_20", "bollinger", "macd", "momento_10")
DIR = ("long", "short")
TF = ("1h", "4h")
PER = ("costruzione", "validazione")
KS = (0, 1, 2, 3)
CINQUE = ["research/src/gruppo.py", "research/src/statistica.py", "research/src/motore.py",
          "research/src/dati.py", "research/config/parametri.yaml"]

righe = []
illeggibili = 0
for k in KS:
    for i, testo in enumerate((CART / f"esiti_k{k}.jsonl").read_text(encoding="utf-8").splitlines()):
        if not testo.strip():
            print(f"riga vuota k{k} n{i}")
            continue
        try:
            r = json.loads(testo)
        except Exception as ex:
            illeggibili += 1
            print("illeggibile", k, i, ex)
            continue
        r["_file_k"] = k
        righe.append(r)
print("righe", len(righe), "illeggibili", illeggibili)

# (a) copertura
etich = Counter(r["etichetta"] for r in righe)
dup = {e: c for e, c in etich.items() if c > 1}
print("duplicati", dup)
attese = {f"GRUPPO|{tf}|{rg}|{d}|{p}|{k}" for tf in TF for rg in REGOLE for d in DIR for p in PER for k in KS}
print("attese", len(attese), "mancanti", sorted(attese - set(etich)), "in piu'", sorted(set(etich) - attese))
errori = [r["etichetta"] for r in righe if r.get("errore")]
print("righe con errore", errori)
incoer = []
for r in righe:
    att = f"GRUPPO|{r['timeframe']}|{r['regola']}|{r['direzione']}|{r['periodo']}|{r['k']}"
    if att != r["etichetta"] or r["k"] != r["_file_k"]:
        incoer.append(r["etichetta"])
print("etichetta incoerente coi campi o col file", incoer)
print("giudicata False:", [r["etichetta"] for r in righe if not r.get("giudicata")])
print("esame mancante:", [r["etichetta"] for r in righe if not r.get("esame")])

# (b) identita'
ids = Counter(json.dumps(r.get("identita"), sort_keys=True) for r in righe)
print("identita' diverse", len(ids))
print("funzionamento True", [r["etichetta"] for r in righe if r.get("funzionamento") or r["identita"].get("funzionamento")])
print("regole_bozza True", [r["etichetta"] for r in righe if r.get("regole_bozza") is not False])
print("commit_file_della_prova", Counter(r.get("commit_file_della_prova") for r in righe))
print("commit_prova", Counter(r.get("commit_prova") for r in righe))
print("commit_principale", Counter(r.get("commit_principale") for r in righe))
print("ramo_principale", Counter(r.get("ramo_principale") for r in righe))
print("formato", Counter(r.get("formato") for r in righe))
print("minimi", Counter(json.dumps(r.get("minimi"), sort_keys=True) for r in righe))

testo_regole = (CART / "regole.md").read_text(encoding="utf-8")
imp_regole = {}
for m in re.finditer(r"^([0-9a-f]{64})  (\S+)$", testo_regole, re.M):
    imp_regole[m.group(2)] = m.group(1)
print("impronte in regole.md punto 7:", len(imp_regole), sorted(imp_regole) == sorted(CINQUE))
imp_disco = {p: hashlib.sha256((PRINC / p).read_bytes()).hexdigest() for p in CINQUE}
print("regole.md == disco principale:", imp_regole == imp_disco)
imp_righe = Counter(json.dumps(r["esame"].get("impronte_strumenti"), sort_keys=True) for r in righe if r.get("esame"))
print("impronte esame diverse:", len(imp_righe))
for j in imp_righe:
    print("  esame.impronte == regole.md:", json.loads(j) == imp_regole)
imp_id = Counter(json.dumps(r["identita"].get("strumenti"), sort_keys=True) for r in righe)
for j in imp_id:
    print("  identita.strumenti == regole.md:", json.loads(j) == imp_regole)
ident = json.loads(next(iter(ids)))
sha_regole = hashlib.sha256((CART / "regole.md").read_bytes()).hexdigest()
print("identita regole.md == sha attuale:", ident["regole.md"] == sha_regole)
for nome, h in ident["codice"].items():
    print(f"  identita codice {nome} == file attuale:", hashlib.sha256((CART / nome).read_bytes()).hexdigest() == h)
print("impronta_variante == placebo_gruppo.py:",
      Counter(r["esame"].get("impronta_variante") == ident["codice"]["placebo_gruppo.py"] for r in righe if r.get("esame")))
print("monete.csv sha", ident["monete"]["monete.csv"],
      hashlib.sha256((PRINC / "research/campagne/GRUPPO/monete.csv").read_bytes()).hexdigest())

# (c) campione e misure
def coda_t(t, g):
    return float(student.sf(t, g))

def z_da_t(t, g):
    # z = Phi^-1(T(t))
    if t >= 0:
        return float(norm.isf(student.sf(t, g)))
    return float(norm.ppf(student.cdf(t, g)))

problemi_p = []
problemi_t = []
quota_oltre = []
somma_diversa = []
for r in righe:
    e = r.get("esame") or {}
    for nome in ("contro_b", "senza_pavimento", "contro_a"):
        c = e.get(nome)
        if not c or not c.get("valutabile"):
            continue
        t, p = c["t"], c["p_value"]; g = c.get("gradi_liberta", e["n_blocchi"] - 1)
        pp = coda_t(t, g)
        if not math.isclose(p, pp, rel_tol=1e-9, abs_tol=1e-15):
            problemi_p.append((r["etichetta"], nome, p, pp))
    c = e.get("contro_b")
    if c and c.get("valutabile"):
        # ricostruzione t
        diff = e["r_medio"] - e["B"]
        if not math.isclose(diff, c["differenza"], rel_tol=1e-9, abs_tol=1e-12):
            problemi_t.append((r["etichetta"], "differenza", diff, c["differenza"]))
        emin = max(c.get("errore_minimo_baseline", 0), c.get("pavimento_minimo") or 0)
        if not math.isclose(emin, c["errore_minimo"], rel_tol=1e-12):
            problemi_t.append((r["etichetta"], "errore_minimo", emin, c["errore_minimo"]))
        ecand = max(c["errore_candidato_senza_pavimento"], c["errore_minimo"])
        if not math.isclose(ecand, c["errore_candidato"], rel_tol=1e-12):
            problemi_t.append((r["etichetta"], "errore_candidato", ecand, c["errore_candidato"]))
        ed = math.sqrt(c["errore_candidato"] ** 2 + c["baseline_errore_standard"] ** 2)
        if not math.isclose(ed, c["errore_differenza"], rel_tol=1e-9):
            problemi_t.append((r["etichetta"], "errore_differenza", ed, c["errore_differenza"]))
        tt = c["differenza"] / c["errore_differenza"]
        if not math.isclose(tt, c["t"], rel_tol=1e-9, abs_tol=1e-12):
            problemi_t.append((r["etichetta"], "t", tt, c["t"]))
        nb = e["trade"] // e["blocco"]
        if nb != c["n_blocchi"] or c["gradi_liberta"] != nb - 1 or e["n_blocchi"] != nb:
            problemi_t.append((r["etichetta"], "blocchi", nb, c["n_blocchi"], c["gradi_liberta"]))
        so = float(student.ppf(0.97725, c["gradi_liberta"]))
        if not math.isclose(so, c["soglia"], rel_tol=1e-6):
            problemi_t.append((r["etichetta"], "soglia", so, c["soglia"]))
        if bool(c["netta"]) != (c["t"] > c["soglia"]):
            problemi_t.append((r["etichetta"], "netta", c["netta"], c["t"], c["soglia"]))
        pav = (e.get("pavimento_sfasate") or {}).get("pavimento")
        if pav is not None and not math.isclose(pav, c["pavimento_minimo"], rel_tol=1e-12):
            problemi_t.append((r["etichetta"], "pavimento_minimo", pav, c["pavimento_minimo"]))
        if not math.isclose(e["pavimento_b"], c["errore_minimo_baseline"], rel_tol=1e-12):
            problemi_t.append((r["etichetta"], "pavimento_b", e["pavimento_b"], c["errore_minimo_baseline"]))
        if not math.isclose(e["B"], c["baseline_media"], rel_tol=1e-12):
            problemi_t.append((r["etichetta"], "B", e["B"], c["baseline_media"]))
    tpm = e.get("trade_per_moneta") or {}
    if tpm:
        s = sum(tpm.values())
        if s != e["trade"]:
            somma_diversa.append((r["etichetta"], s, e["trade"]))
        q = max(tpm.values()) / s
        if q > 0.10:
            quota_oltre.append((r["etichetta"], q))
        if not math.isclose(q, e["quota_moneta_piu_presente"], rel_tol=1e-12):
            somma_diversa.append((r["etichetta"], "quota", q, e["quota_moneta_piu_presente"]))
    co = r.get("conta")
    if co:
        if co.get("quota_moneta_piu_presente", 0) > 0.10:
            quota_oltre.append((r["etichetta"], "conta", co["quota_moneta_piu_presente"]))
print("p_value incoerenti", problemi_p[:10], len(problemi_p))
print("ricostruzione t incoerente", problemi_t[:10], len(problemi_t))
print("quote oltre 10%", quota_oltre)
print("somma trade_per_moneta diversa", somma_diversa[:5], len(somma_diversa))

conta_esiti = Counter((r["periodo"], (r.get("conta") or {}).get("esito")) for r in righe)
print("conta esiti", conta_esiti)
print("conta.trade_stimati != esame.trade in costruzione:",
      [r["etichetta"] for r in righe if r["periodo"] == "costruzione" and r["conta"]["trade_stimati"] != r["esame"]["trade"]])


def valutabile(r):
    e = r["esame"]
    c = e.get("contro_b") or {}
    if not c.get("valutabile"):
        return False, "contro_b non valutabile: " + str(c.get("motivo_non_valutabile"))
    if r["periodo"] == "costruzione":
        co = r["conta"]
        if co["trade_stimati"] < 700 or e["trade"] < 700:
            return False, "sotto 700"
        if co["quota_moneta_piu_presente"] > 0.10 or max(e["trade_per_moneta"].values()) / e["trade"] > 0.10:
            return False, "moneta oltre 10%"
        if co["esito"] != "registrabile":
            return False, "conta non registrabile"
        return True, ""
    if e["trade"] < 300:
        return False, "sotto 300"
    return True, ""


ris = {}
for p, soglia_z, quota, nome in (("costruzione", 2.00, Fraction("0.03"), "M1"), ("validazione", 1.2816, Fraction("0.13"), "M2")):
    rr = [r for r in righe if r["periodo"] == p]
    val, esclusi = [], Counter()
    for r in rr:
        ok, motivo = valutabile(r)
        if ok:
            val.append(r)
        else:
            esclusi[motivo] += 1
    z = np.array([z_da_t(r["esame"]["contro_b"]["t"], r["esame"]["contro_b"]["gradi_liberta"]) for r in val])
    n = len(val)
    cnt = int((z > soglia_z).sum())
    lim = math.floor(quota * n)
    mu, sd = z.mean(), z.std(ddof=1)
    coda = float(norm.sf((soglia_z - mu) / sd))
    soglia_m3 = 0.03 if p == "costruzione" else 0.13
    print(f"{p}: righe {len(rr)} valutabili {n}; esclusi {dict(esclusi)}")
    print(f"   {nome}: {cnt} con z>{soglia_z} limite {lim} -> {'regge' if cnt <= lim else 'NON regge'}")
    print(f"   mu {mu:.6f} sd {sd:.6f} M3 coda {coda*100:.4f}% soglia {soglia_m3*100}% -> {'regge' if coda <= soglia_m3 else 'NON regge'}")
    print(f"   z max {z.max():.4f} min {z.min():.4f}; z sorted top5 {np.sort(z)[-5:]}")
    trades = np.array([r["esame"]["trade"] for r in rr if r.get("esame")])
    print(f"   trade su tutte le righe: mediana {np.median(trades)} min {trades.min()}")
    trv = np.array([r["esame"]["trade"] for r in val])
    print(f"   trade sui valutabili: mediana {np.median(trv)} min {trv.min()}")
    qm = [r["esame"]["quota_moneta_piu_presente"] for r in val]
    print(f"   quota moneta piu' presente (esame) valutabili max {max(qm):.4%} mediana {np.median(qm):.4%}")
    qa = [r["esame"]["quota_moneta_piu_presente"] for r in rr]
    print(f"   quota moneta piu' presente (esame) tutte max {max(qa):.4%}")
    ris[p] = dict(n=n, cnt=cnt, lim=lim, mu=mu, sd=sd, coda=coda, val=val, z=z)
    # z dal p_value salvato (formula letterale delle regole)
    z2 = np.array([norm.ppf(1 - r["esame"]["contro_b"]["p_value"]) for r in val])
    print(f"   con z = ppf(1-p_value) letterale: max diff {np.nanmax(np.abs(z2 - z)):.2e}, finiti {np.isfinite(z2).all()}")
    # senza pavimento
    vs = [r for r in rr if (r["esame"].get("senza_pavimento") or {}).get("valutabile") and
          (valutabile(r)[0] or (r["periodo"] == "validazione" and r["esame"]["trade"] >= 300) )]
    vs = []
    for r in rr:
        e = r["esame"]
        sp = e.get("senza_pavimento") or {}
        if not sp.get("valutabile"):
            continue
        if p == "costruzione":
            if not (r["conta"]["esito"] == "registrabile" and e["trade"] >= 700):
                continue
        elif e["trade"] < 300:
            continue
        vs.append(r)
    zs = np.array([z_da_t(r["esame"]["senza_pavimento"]["t"], r["esame"]["senza_pavimento"]["gradi_liberta"]) for r in vs])
    print(f"   senza pavimento: n {len(vs)} conta {(zs > soglia_z).sum()} mu {zs.mean():.3f} sd {zs.std(ddof=1):.3f} coda {norm.sf((soglia_z - zs.mean())/zs.std(ddof=1))*100:.2f}%")
    # pavimento decide
    dv = [(r["esame"]["r_medio"] - r["esame"]["B"]) / r["esame"]["pavimento_sfasate"]["pavimento"] for r in val if r["esame"].get("pavimento_decide")]
    print(f"   pavimento decide: {len(dv)} sd {np.std(dv, ddof=1):.3f}")
    # pavimento decide ricomputato: errore_candidato == pavimento sfasate > errore senza pavimento e > pavimento b
    dv2 = [r["etichetta"] for r in val if r["esame"]["contro_b"]["pavimento_minimo"] > max(r["esame"]["contro_b"]["errore_candidato_senza_pavimento"], r["esame"]["contro_b"]["errore_minimo_baseline"])]
    print(f"   pavimento decide ricalcolato: {len(dv2)}; incoerenze con flag: {set(dv2) ^ {r['etichetta'] for r in val if r['esame'].get('pavimento_decide')}}")
    eg = [r["esame"]["effetto_grappolo"] for r in val]
    print(f"   effetto grappolo mediana {np.median(eg):.2f}")
    if p == "validazione":
        sp90 = [r for r in val if r["esame"]["sfasate"].get("sopra_p90") is not None]
        print(f"   sopra p90: {sum(r['esame']['sfasate']['sopra_p90'] for r in sp90)} su {len(sp90)}")
    # durata vicina al margine su tutte e su valutabili
    dur_all = [r["etichetta"] for r in rr if r["esame"]["durata_massima_barre"] >= r["margine"] - 60]
    dur_val = [r["etichetta"] for r in val if r["esame"]["durata_massima_barre"] >= r["margine"] - 60]
    print(f"   durata vicina al margine: tutte {len(dur_all)}, valutabili {len(dur_val)}")
    # contro_b non valutabili: elenco
    for r in rr:
        c = r["esame"].get("contro_b") or {}
        if not c.get("valutabile"):
            print("     non valutabile:", r["etichetta"], c.get("motivo_non_valutabile"), "trade", r["esame"]["trade"],
                  "blocco", r["esame"].get("blocco"), "r_medio", round(r["esame"].get("r_medio") or float('nan'), 4),
                  "B", r["esame"].get("B"), "t", c.get("t"))

# seme e d
bad_seed = []
bad_d = []
for r in righe:
    s = zlib.crc32(r["etichetta"].encode())
    if s != r["seme"]:
        bad_seed.append((r["etichetta"], s, r["seme"]))
    if not (r["margine"] <= r["d"] <= r["L"] - r["margine"]):
        bad_d.append((r["etichetta"], r["d"], r["L"], r["margine"]))
    bar = 3600000 if r["timeframe"] == "1h" else 4 * 3600000
    fu = r["finestra_unione"]
    L = (fu[1] + 1 - fu[0]) // bar
    if L != r["L"]:
        bad_d.append((r["etichetta"], "L", L, r["L"]))
    att_m = min(720 if r["timeframe"] == "1h" else 180, r["L"] // 4)
    if att_m != r["margine"]:
        bad_d.append((r["etichetta"], "margine", att_m, r["margine"]))
print("seme diverso da crc32(etichetta):", len(bad_seed), bad_seed[:3])
print("d/L/margine fuori regola:", bad_d[:5], len(bad_d))
fin = Counter((r["periodo"], tuple(r["finestra_unione"])) for r in righe)
from datetime import datetime, timezone
for (p, f), c in sorted(fin.items()):
    print(" finestra", p, datetime.fromtimestamp(f[0] / 1000, timezone.utc), datetime.fromtimestamp(f[1] / 1000, timezone.utc), c)
# distribuzione di d/L
fr = [min(r["d"], r["L"] - r["d"]) / r["L"] for r in righe]
print("distanza circolare minima d (frazione di L): min", min(fr))
print("monete", Counter(r["monete"] for r in righe), "monete_nel_periodo", Counter(r["esame"]["monete_nel_periodo"] for r in righe))
