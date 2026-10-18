"""Programma 5, fase 2: le idee di portafoglio fra monete (famiglie G2-G12 delle esplorazioni E-111 ed E-114).

A ogni decisione (ogni h ore dalle 00:00 UTC, come ``esplora_fase2.decisioni``) si mettono in fila le monete per un
carattere; «segue»: long le ``quanti`` prime e short le ``quanti`` ultime (al contrario per «contro»), pesi uguali, metà
capitale per parte; ingresso all'apertura dell'ora dopo, uscita alla chiusura dell'ora t+h, funding compreso (come
``esplora_fase2.avanti``: sono le candele da 1 minuto aggregate a ore, quindi lo stesso ingresso e la stessa uscita del
motore a minuti). Costi: ogni gamba paga un giro intero a mercato (commissione 0,05% per lato e lo scarto del programma
per lato), senza contare le gambe che restano dal periodo prima (prudente).

Ogni gamba e' una riga (``simbolo`` = la moneta, ``netto`` = il suo contributo al rendimento del portafoglio per unita' di
capitale): la somma delle righe di una decisione e' il rendimento del portafoglio. Per l'esame (REGOLE.md, sezione 7) un
trade e' una gamba; il bootstrap a blocchi di giorni usa le somme del giorno, cioe' il rendimento dei portafogli.
Il caso: alle stesse decisioni, ``quanti`` monete long e ``quanti`` short prese a caso fra quelle in fila.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from research.programma5.strumenti import motore5 as m5
from research.programma5.strumenti.esplora_fase2 import BTC, avanti, decisioni
from research.programma5.strumenti.ore import barre


def pannello(monete, periodo: str, idea: str):
    """Come ``esplora_fase2.pannello``, passando l'idea al guardiano dei periodi."""
    grezze = {s: barre(s, periodo, idea) for s in monete}
    grezze = {s: b for s, b in grezze.items() if len(b)}
    ore = np.arange(min(b.index.min() for b in grezze.values()), max(b.index.max() for b in grezze.values()) + 1)
    P = {}
    for s, b in grezze.items():
        b = b.reindex(ore).copy()
        b["periodo"] = b["periodo"].eq(True)
        b["funding_cum"] = b["funding_cum"].ffill().fillna(0.0)
        b["lc"] = np.log(b["close"])
        b["r1"] = b["lc"].diff()
        b["sigma"] = b["r1"].rolling(720, min_periods=500).std()
        P[s] = b
    rb = P[BTC]["r1"]
    m = dict(window=720, min_periods=500)
    for s in P:
        if s == BTC:
            continue
        b = P[s]
        cov = (b["r1"] * rb).rolling(**m).mean() - b["r1"].rolling(**m).mean() * rb.rolling(**m).mean()
        b["beta"] = cov / rb.rolling(**m).var(ddof=0)
    return ore, P


def punteggio(cella: str, P: dict) -> dict:
    """Il carattere della cella per ogni moneta (stesse definizioni di ``esplora_fase2`` ed ``esplora_fattori``)."""
    parti = cella.split()
    fam = parti[0]
    btc = P[BTC]
    m = dict(window=720, min_periods=500)
    out = {}
    for s, b in P.items():
        if fam == "G2":
            w = int(parti[2][1:])
            r = b["lc"] - b["lc"].shift(w)
            if parti[1] == "residuo":
                if s == BTC:
                    continue
                r = r - b["beta"].shift(w) * (btc["lc"] - btc["lc"].shift(w))
            out[s] = r.to_numpy()
        elif fam == "G3":
            out[s] = b["funding_8h"].to_numpy(float)
        elif fam == "G4":
            w = int(parti[2][1:])
            lo = np.log(b["oi"].where(b["oi"] > 0))
            out[s] = (lo - lo.shift(w)).to_numpy()
        elif fam == "G5":
            v24 = b["volume"].rolling(24).sum()
            out[s] = (v24 / v24.rolling(720, min_periods=500).median().shift(24)).to_numpy()
        elif fam == "G7":
            out[s] = b["sigma"].to_numpy()
        elif fam == "G8":
            if s != BTC:
                out[s] = b["beta"].to_numpy()
        elif fam == "G9":
            out[s] = (b["lc"] - b["lc"].shift(24)).rolling(**m).max().to_numpy()
        elif fam == "G10":
            qv = (b["volume"] * b["close"]).where(lambda x: x > 0)
            out[s] = (b["r1"].abs() / qv).rolling(**m).mean().to_numpy()
        elif fam == "G11":
            out[s] = (b["lc"] - np.log(b["high"].rolling(**m).max())).to_numpy()
        elif fam == "G12":
            out[s] = b["r1"].rolling(**m).skew().to_numpy()
        else:
            raise ValueError(cella)
    return out


def costo_gamba(s: str) -> float:
    return 2 * (m5.TAKER + m5.scarto(s))


def gambe(ore, punti: dict, A_h: dict, dec, quanti: int, minimo: int, verso: int, rng=None) -> pd.DataFrame:
    """Le righe (una per gamba) dei portafogli alle decisioni ``dec``; con ``rng`` le monete sono prese a caso."""
    monete = [s for s in punti if s in A_h]
    S = np.vstack([punti[s] for s in monete])
    R = np.vstack([A_h[s] for s in monete])
    c = np.array([costo_gamba(s) for s in monete])
    peso = 1.0 / (2 * quanti)
    righe = []
    for t in dec:
        p, r = S[:, t], R[:, t]
        ok = np.isfinite(p) & np.isfinite(r)
        if ok.sum() < minimo:
            continue
        idx = np.flatnonzero(ok)
        if rng is None:
            ordine = idx[np.argsort(p[idx], kind="stable")]
        else:
            ordine = rng.permutation(idx)
        basse, alte = ordine[:quanti], ordine[-quanti:]
        lunghe, corte = (alte, basse) if verso > 0 else (basse, alte)
        media = r[idx].mean()
        for i, d in [(i, 1) for i in lunghe] + [(i, -1) for i in corte]:
            lordo = peso * d * r[i]
            righe.append({"simbolo": monete[i], "decisione": int(t), "minuto": int(ore[t] * 60), "direzione": d,
                          "lordo": lordo, "costo": peso * c[i], "funding": 0.0,
                          "netto": lordo - peso * c[i], "netto_doppio": lordo - 2 * peso * c[i], "motivo": "tempo",
                          "contributo": d * (r[i] - media)})
    return pd.DataFrame(righe)


def calcola(idea: str, varianti: dict, periodo: str, monete, quanti: int = 10, minimo: int = 40,
            ripetizioni: int = 20, seme: int = 2026) -> dict:
    """Per ogni variante ``{"cella": ..., "verso": "segue" | "contro"}``: (righe delle gambe, righe del caso)."""
    ore, P = pannello(monete, periodo, idea)
    nel = P[BTC]["periodo"].to_numpy()
    out = {}
    cache_A = {}
    for n, v in varianti.items():
        h = int(v["cella"].split()[-1][1:])
        if h not in cache_A:
            cache_A[h] = {s: avanti(P[s], h) for s in P}
        punti = punteggio(v["cella"], P)
        dec = decisioni(ore, nel, h)
        verso = 1 if v["verso"] == "segue" else -1
        t = gambe(ore, punti, cache_A[h], dec, quanti, minimo, verso)
        rng = np.random.default_rng(seme)
        casi = []
        for r in range(ripetizioni):
            c = gambe(ore, punti, cache_A[h], dec, quanti, minimo, verso, rng=rng)
            c["ripetizione"] = r
            casi.append(c)
        out[n] = (t, pd.concat(casi, ignore_index=True) if casi else t)
    return out


def esame_portafoglio(trade: pd.DataFrame, trade_caso: pd.DataFrame, n_boot: int = 10000) -> dict:
    """Come ``motore5.esame``, con il netto medio **del portafoglio** a decisione (somma delle gambe) e il criterio delle
    monete sul contributo di ogni moneta quando e' nel portafoglio."""
    if trade.empty:
        return {"trade": 0}
    per_dec = trade.groupby("decisione").agg(minuto=("minuto", "first"), netto=("netto", "sum"),
                                             netto_doppio=("netto_doppio", "sum"), lordo=("lordo", "sum"))
    m = per_dec["minuto"].to_numpy()
    out = {"trade": int(len(trade)), "portafogli": int(len(per_dec)),
           "netto": m5.bootstrap_giorni(per_dec["netto"].to_numpy(), m, n_boot),
           "netto_doppio": m5.bootstrap_giorni(per_dec["netto_doppio"].to_numpy(), m, n_boot),
           "lordo": float(per_dec["lordo"].mean()), "costo": float(trade.groupby("decisione")["costo"].sum().mean()),
           "funding": 0.0}
    anni = pd.to_datetime(m * 60, unit="s").year
    out["per_anno"] = {int(a): {"trade": int((anni == a).sum()), "netto": float(per_dec["netto"][anni == a].mean())}
                       for a in sorted(set(anni))}
    out["per_moneta"] = {s: {"trade": int(len(g)), "netto": float(g["contributo"].mean())}
                         for s, g in trade.groupby("simbolo")}
    if trade_caso is not None and not trade_caso.empty:
        caso = trade_caso.groupby(["ripetizione", "decisione"])["netto"].sum()
        out["caso_netto"] = float(caso.mean())
        out["contro_caso"] = float(per_dec["netto"].mean() - caso.mean())
    return out


MEZZO_V2 = 29_453_760          # 2026-01-01 00:00 UTC in minuti dall'epoca


def esito(periodo: str, e: dict, n_varianti: int) -> tuple:
    """L'esame della fase 2 (REGOLE.md, sezione 7) per un'idea di portafoglio."""
    if not e.get("trade"):
        return False, "nessun trade"
    nt, nd = e["netto"], e["netto_doppio"]
    if not nt["basso"] > 0:
        return False, "netto con l'intervallo non sopra zero"
    if periodo == "C2":
        if not nt["media"] > e.get("caso_netto", float("inf")):
            return False, "non meglio del caso"
        return True, "passa C2"
    soglia = 0.005 / n_varianti
    if not nt["p"] <= soglia:
        return False, f"p {nt['p']:.4f} oltre la soglia {soglia:.4f}"
    if not nd["media"] > 0:
        return False, "non positivo a costi doppi"
    if not e.get("senza_migliore", -1) > 0:
        return False, "non positivo togliendo il giorno migliore"
    if any(v["netto"] <= 0 for v in e.get("per_meta", {}).values()) or len(e.get("per_meta", {})) < 2:
        return False, "non positivo in tutte e due le metà"
    monete = [m for m in e["per_moneta"].values() if m["trade"] >= 20]
    pos = sum(1 for m in monete if m["netto"] > 0)
    if len(monete) < 5 or pos < 0.6 * len(monete):
        return False, f"contributo positivo su {pos} monete su {len(monete)} con almeno 20 gambe"
    if e["trade"] < 200:
        return False, "meno di 200 gambe"
    return True, "passa V2: strategia valida"


def esegui(idea: str, varianti: dict, periodo: str, monete, cartella, quanti: int = 10, minimo: int = 40) -> str:
    import json
    ris = calcola(idea, varianti, periodo, monete, quanti, minimo)
    dati = {}
    for n, (t, c) in ris.items():
        e = esame_portafoglio(t, c)
        if e.get("trade"):
            per_dec = t.groupby("decisione").agg(minuto=("minuto", "first"), netto=("netto", "sum"))
            giorno = per_dec["minuto"] // 1440
            somme = per_dec.groupby(giorno)["netto"].sum()
            resto = per_dec[giorno != somme.idxmax()]
            e["senza_migliore"] = float(resto["netto"].mean())
            prima = per_dec["minuto"] < MEZZO_V2
            e["per_meta"] = {"2025-07 → 2025-12": {"trade": int(prima.sum()), "netto": float(per_dec["netto"][prima].mean())},
                             "2026-01 → 2026-09": {"trade": int((~prima).sum()),
                                                   "netto": float(per_dec["netto"][~prima].mean())}} \
                if periodo == "V2" else {}
            t.to_csv(cartella / f"trade_{periodo}_{n}.csv.gz", index=False)
        dati[n] = e
    (cartella / f"{periodo}.json").write_text(json.dumps(dati, ensure_ascii=False, indent=1, default=float),
                                              encoding="utf-8")
    righe = [f"# {idea} — periodo {periodo}", "", f"Numeri da `{periodo}.json`; esame di `REGOLE.md`, sezione 7, per i "
             "portafogli (`strumenti/portafoglio.py`). Netto **del portafoglio** a decisione, per unità di capitale.", "",
             "| Variante | Portafogli | Gambe | Netto | Intervallo al 95% | p | A costi doppi | Senza il giorno migliore | "
             "Caso | Esito |", "|---|---|---|---|---|---|---|---|---|---|"]
    for n, e in dati.items():
        ok, motivo = esito(periodo, e, len(dati))
        if not e.get("trade"):
            righe.append(f"| {n} | 0 | 0 | | | | | | | {motivo} |")
            continue
        nt = e["netto"]
        righe.append(f"| {n} | {e['portafogli']} | {e['trade']} | {100 * nt['media']:+.3f}% | {100 * nt['basso']:+.3f}; "
                     f"{100 * nt['alto']:+.3f} | {nt['p']:.4f} | {100 * e['netto_doppio']['media']:+.3f}% | "
                     f"{100 * e['senza_migliore']:+.3f}% | {100 * e.get('caso_netto', float('nan')):+.3f}% | "
                     f"{'**' + motivo + '**' if ok else motivo} |")
    for n, e in dati.items():
        if e.get("per_meta"):
            righe.append(f"* {n} per metà: " + ", ".join(f"{k} {100 * v['netto']:+.3f}% ({v['trade']})"
                                                         for k, v in e["per_meta"].items()))
    testo = "\n".join(righe) + "\n"
    (cartella / f"{periodo}.md").write_text(testo, encoding="utf-8")
    return testo
