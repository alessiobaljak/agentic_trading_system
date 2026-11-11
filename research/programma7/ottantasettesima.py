"""Programma 7, ottantasettesima prova (prova 149 del registro): la 1:1:1, una moneta, un intervallo, una strategia (`OTTANTASETTESIMA.md`).

10 monete (volume medio giornaliero 2023) x 2 intervalli (4 ore, 1 giorno) x 3 strategie (A tendenza, B rottura, C ritorno alla media),
parametri fissi, 60 combinazioni, nessuna variante. Segnale alla chiusura della barra, ordine all'apertura della barra dopo; leva 1;
costi: 0,05% a mercato per lato + scarto di prezzo (0,01% BTC, ETH, SOL; 0,02% le altre); funding vero del perpetuo (somma giornaliera del
pannello del programma 6, divisa in parti uguali fra le barre del giorno).

Letture scelte dove le regole lasciano margine (dichiarate nel risultato): massimo e minimo delle barre = massimi e minimi (alto e basso)
delle candele; RSI di Wilder a 14 barre; volume medio 2023 = somma dei volumi in USDT del 2023 / 365 giorni.

Uso: python3 -m research.programma7.ottantasettesima
"""
from __future__ import annotations

import json
import math
import time
from pathlib import Path

import numpy as np
import pandas as pd

from research.programma5.strumenti import motore5 as m5
from research.programma6 import asticella as ast
from research.programma6 import quarta as qa
from research.programma6 import seconda as sc
from research.programma6 import terza as te
from research.programma6 import trentaquattresima as tq
from research.programma7.revisione_g1n import nucleo as nu
from research.src.prove import registra

QUI = Path(__file__).parent
OUT = QUI / "risultati_ottantasettesima"
ID = "ottantasettesima"
INIZIO, FINE = sc.giorno(2021, 1, 1), sc.giorno(2026, 10, 31)     # giorni inclusi
N_PROVE = 306
SOGLIA_SHARPE_CORRETTO, SOGLIA_T = 0.80, 3.0
STRATEGIE = {"A": "tendenza (media a 50)", "B": "rottura (20 dentro, 10 fuori)", "C": "ritorno alla media (RSI 14, 30/70, uscita 50)"}
TEMPI = ("4h", "1d")


def log(*a):
    print(time.strftime("%H:%M:%S"), *a, flush=True)


# ---------------------------------------------------------------- le monete
def dieci_monete(pan: dict):
    t0, V = pan["t0"], pan["quote_volume"]
    a, b = sc.giorno(2023, 1, 1) - t0, sc.giorno(2023, 12, 31) - t0 + 1
    v = np.nan_to_num(V[a:b])
    media = v.sum(axis=0) / 365.0
    giorni = (v > 0).sum(axis=0)
    ordine = np.argsort(-media, kind="stable")
    tab = [(pan["simboli"][j], float(media[j]), int(giorni[j])) for j in ordine[:14]]
    return tab[:10], tab


# ---------------------------------------------------------------- i segnali (posizione dopo la chiusura di ogni barra)
def segnale_A(c: np.ndarray) -> np.ndarray:
    m = pd.Series(c).rolling(50).mean().to_numpy()
    pos = np.zeros(len(c))
    p = 0.0
    for i in range(len(c)):
        if np.isfinite(m[i]):
            if c[i] > m[i]:
                p = 1.0
            elif c[i] < m[i]:
                p = -1.0
        pos[i] = p
    return pos


def segnale_B(h: np.ndarray, l: np.ndarray, c: np.ndarray) -> np.ndarray:
    n = len(c)
    H20 = pd.Series(h).rolling(20).max().shift(1).to_numpy()
    L20 = pd.Series(l).rolling(20).min().shift(1).to_numpy()
    H10 = pd.Series(h).rolling(10).max().shift(1).to_numpy()
    L10 = pd.Series(l).rolling(10).min().shift(1).to_numpy()
    pos = np.zeros(n)
    p = 0.0
    for i in range(n):
        if p == 1.0 and c[i] < L10[i]:
            p = 0.0
        elif p == -1.0 and c[i] > H10[i]:
            p = 0.0
        if p == 0.0:
            if c[i] > H20[i]:
                p = 1.0
            elif c[i] < L20[i]:
                p = -1.0
        pos[i] = p
    return pos


def rsi14(c: np.ndarray) -> np.ndarray:
    d = np.diff(c, prepend=np.nan)
    su, giu = np.where(d > 0, d, 0.0), np.where(d < 0, -d, 0.0)
    su[0] = giu[0] = np.nan
    mu = pd.Series(su).ewm(alpha=1 / 14, adjust=False, min_periods=14, ignore_na=True).mean().to_numpy()
    md = pd.Series(giu).ewm(alpha=1 / 14, adjust=False, min_periods=14, ignore_na=True).mean().to_numpy()
    with np.errstate(all="ignore"):
        r = 100 - 100 / (1 + mu / md)
    return np.where(md == 0, 100.0, r)


def segnale_C(c: np.ndarray) -> np.ndarray:
    r = rsi14(c)
    pos = np.zeros(len(c))
    p = 0.0
    for i in range(len(c)):
        if np.isfinite(r[i]):
            if p == 1.0 and r[i] > 50:
                p = 0.0
            elif p == -1.0 and r[i] < 50:
                p = 0.0
            if p == 0.0:
                if r[i] < 30:
                    p = 1.0
                elif r[i] > 70:
                    p = -1.0
        pos[i] = p
    return pos


# ---------------------------------------------------------------- le barre
def barre(pan: dict, j: int, tempo: str):
    """(open, high, low, close, giorno di ogni barra, quota del giorno)."""
    if tempo == "1d":
        b = pd.DataFrame({k: pan[k][:, j] for k in ("open", "high", "low", "close")}).dropna()
        return b, b.index.to_numpy() + pan["t0"], 1.0
    h = qa.ore(pan["simboli"][j])                                    # 1 ora, archivio mensile di Binance (scarico_ore.py)
    blocco = h.index.to_numpy() // 4
    pieno = h["open"].notna().groupby(blocco).sum() == 4             # una barra a 4 ore vale solo con tutte e 4 le ore
    b = tq.quattro_ore(h)
    b = b[pieno.reindex(b.index).fillna(False).to_numpy()]
    return b, b.index.to_numpy() * 4 // 24, 4 / 24


def conto(b: pd.DataFrame, g: np.ndarray, quota: float, sig: np.ndarray, pan: dict, j: int, costo: float):
    """Giorni, netto per giorno e operazioni. La posizione tenuta nella barra k e' il segnale della chiusura di k-1."""
    o, c = b["open"].to_numpy(float), b["close"].to_numpy(float)
    dopo = np.append(o[1:], c[-1])
    R = dopo / o - 1
    X = np.concatenate([[0.0], sig[:-1]])
    dentro = (g >= INIZIO) & (g <= FINE)
    prima = np.concatenate([[0.0], X[:-1]])
    delta = np.abs(X - prima)
    gi = g - pan["t0"]
    F = np.where((gi >= 0) & (gi < pan["funding"].shape[0]), pan["funding"][np.clip(gi, 0, pan["funding"].shape[0] - 1), j], 0.0) * quota
    lordo, spese, fund = X * R, delta * costo, X * F
    nuove = ((X != 0) & (X != prima)).astype(int)          # entrate in una posizione (compresi i rovesciamenti)
    d = pd.DataFrame({"lordo": lordo, "spese": spese, "funding": fund, "operazioni": nuove, "giro": delta, "tenuta": np.abs(X)})[dentro]
    d = d.groupby(g[dentro]).sum()
    d["netto"] = d["lordo"] - d["spese"] - d["funding"]
    return d


def settimane_e_anni(d: pd.DataFrame):
    giorni = d.index.to_numpy()
    lun = giorni - ((giorni + 3) % 7)
    w = d.groupby(lun).sum()
    w = w[(w.index >= INIZIO) & (w.index + 6 <= FINE)]
    return w


def anno_di(giorni):
    return pd.to_datetime(np.asarray(giorni) * 86400, unit="s").year.to_numpy()


def misure(d: pd.DataFrame) -> dict:
    w = settimane_e_anni(d)
    netto = w["netto"]
    m = te.numeri_settimana(netto)
    a = anno_di(w.index)
    per_anno = {int(y): float(netto[a == y].mean() * 52) for y in sorted(set(a))}
    m.update({"per_anno": per_anno, "anni_positivi": int(sum(v > 0 for v in per_anno.values())), "anni": len(per_anno),
              "t": float(m["sharpe"] * math.sqrt(m["settimane"] / 52)), "operazioni": int(d["operazioni"].sum()),
              "spese_annue": float(w["spese"].mean() * 52), "funding_annuo": float(w["funding"].mean() * 52),
              "lordo_annuo": float(w["lordo"].mean() * 52), "tempo_in_posizione": float(d["tenuta"].sum() / len(d)),
              "costo_per_operazione": float(w["spese"].sum() / max(1, d["operazioni"].sum()))})
    return m, netto


def main():
    t0 = time.time()
    OUT.mkdir(parents=True, exist_ok=True)
    pan = sc.pannello()
    prime, tab14 = dieci_monete(pan)
    elenco = [s for s, _, _ in prime]
    (OUT / "monete.json").write_text(json.dumps({"scelta": "somma dei volumi in USDT del 2023 / 365 (perpetui, tabella del programma 6); primi 14",
                                                 "monete": [{"simbolo": s, "volume_medio_giornaliero": v, "giorni_con_volume_2023": n}
                                                            for s, v, n in tab14]}, indent=1), encoding="utf-8")
    log("monete (scritte prima dei risultati in monete.json):", ", ".join(elenco))
    # il conto delle prove: gli Sharpe dei gruppi gia' nel conto (V), poi le 60 combinazioni
    prove = ast.le_prove()
    serie = {n: ast.periodo(s) for n, s, _ in prove if s is not None}
    serie.update({n: ast.periodo(s) for n, s in ast.serie_nuove().items()})
    soli = [sr for _, s, sr in prove if s is None]
    gr = ast.gruppi(serie, ast.TAGLIO)
    sr_base = ast.per_v(gr, soli, True)
    log("Sharpe dei gruppi gia' nel conto:", len(sr_base))

    righe, serie_w = [], {}
    for s in elenco:
        j = pan["simboli"].index(s)
        costo = nu.costo_di(s)
        for tf in TEMPI:
            b, g, quota = barre(pan, j, tf)
            sigs = {"A": lambda: segnale_A(b["close"].to_numpy(float)),
                    "B": lambda: segnale_B(b["high"].to_numpy(float), b["low"].to_numpy(float), b["close"].to_numpy(float)),
                    "C": lambda: segnale_C(b["close"].to_numpy(float))}
            for st in "ABC":
                idv = f"{s}_{tf}_{st}"
                par = {"moneta": s, "intervallo": tf, "strategia": st}
                try:
                    d = conto(b, g, quota, sigs[st](), pan, j, costo)
                    m, netto = misure(d)
                    m["prima_barra"] = int(g[0])
                    righe.append({"moneta": s, "tf": tf, "strategia": st, "m": m})
                    serie_w[idv] = netto
                    log(idv, f"annuo {m['annuo']:+.1%} Sharpe {m['sharpe']:.2f} op {m['operazioni']}")
                except Exception as e:  # noqa: BLE001
                    registra(ID, idv, par, tf, 0, {}, "errore", note=repr(e), seme=None)
                    righe.append({"moneta": s, "tf": tf, "strategia": st, "errore": repr(e)})
    # lo Sharpe corretto: N = 306; V = Sharpe dei gruppi del conto + le 60 combinazioni (variante principale); solo i gruppi (per capire)
    sr60 = [r["m"]["sharpe"] for r in righe if "m" in r]
    sr_v = sr_base + sr60
    for r in righe:
        if "m" not in r:
            continue
        m = r["m"]
        m["sharpe_corretto"] = te.sharpe_corretto(m["sharpe"], m["settimane"], m["asimmetria"], m["curtosi"], sr_v, 52, n_prove=N_PROVE)
        m["sharpe_corretto_solo_gruppi"] = te.sharpe_corretto(m["sharpe"], m["settimane"], m["asimmetria"], m["curtosi"], sr_base, 52,
                                                              n_prove=N_PROVE)
        perche = []
        if not m["annuo"] > 0:
            perche.append("netto non positivo")
        if m["anni_positivi"] < m["anni"]:
            perche.append(f"anni positivi {m['anni_positivi']}/{m['anni']}")
        if m["t"] < SOGLIA_T:
            perche.append(f"t {m['t']:.2f} sotto 3")
        if m["sharpe_corretto"] < SOGLIA_SHARPE_CORRETTO:
            perche.append(f"Sharpe corretto {m['sharpe_corretto']:.2f} sotto 0,80")
        r["passa"] = not perche
        r["esito"] = "passa" if not perche else "non passa: " + "; ".join(perche)
        m["passa_con_solo_gruppi"] = bool(m["annuo"] > 0 and m["anni_positivi"] == m["anni"] and m["t"] >= SOGLIA_T
                                          and m["sharpe_corretto_solo_gruppi"] >= SOGLIA_SHARPE_CORRETTO)
        registra(ID, f"{r['moneta']}_{r['tf']}_{r['strategia']}", {"moneta": r["moneta"], "intervallo": r["tf"], "strategia": r["strategia"]},
                 r["tf"], m["operazioni"],
                 {k: m[k] for k in ("annuo", "sharpe", "t", "sharpe_corretto", "discesa_max", "anni_positivi", "anni", "spese_annue",
                                    "funding_annuo", "lordo_annuo", "settimane")} | {"per_anno": m["per_anno"]},
                 "passa" if r["passa"] else "non passa", note=r["esito"], seme="nessuno (calcolo senza casualita')")
    (OUT / "risultati.json").write_text(json.dumps({"monete": elenco, "n_prove": N_PROVE, "righe": righe}, indent=1, ensure_ascii=False,
                                                    default=float), encoding="utf-8")
    pd.DataFrame(serie_w).to_csv(OUT / "settimane.csv.gz", float_format="%.8f")
    scrivi(righe, elenco, tab14, len(sr_base))
    log("fatto", f"{time.time() - t0:.0f} s; passano:", [f"{r['moneta']} {r['tf']} {r['strategia']}" for r in righe if r.get("passa")])


def scrivi(righe, elenco, tab14, n_gruppi):
    pc = lambda v: f"{100 * v:+.1f}%"  # noqa: E731
    t = ["# Programma 7 — risultati dell'ottantasettesima prova (prova 149: la 1:1:1)", "",
         "Regole in `OTTANTASETTESIMA.md` (scritte e committate prima del calcolo, commit 07d171e). Codice: `ottantasettesima.py`; dati completi: "
         "`risultati_ottantasettesima/risultati.json`; registro delle 60 combinazioni: `research/trials/ottantasettesima.csv`.", "",
         "## Le 10 monete (scelte con il volume del 2023, scritte prima di calcolare le strategie)", "",
         "Volume medio giornaliero 2023 in USDT = somma dei volumi del 2023 / 365 (tabella del programma 6, perpetui di Binance). Nessuno "
         "stablecoin o contratto non-moneta fra i primi 14.", "", "| # | moneta | volume medio al giorno | giorni con volume nel 2023 |", "|---|---|---|---|"]
    for i, (s, v, n) in enumerate(tab14, 1):
        t.append(f"| {i}{'' if i <= 10 else ' (fuori)'} | {s} | {v / 1e6:,.0f} milioni | {n} |")
    t += ["", "## Letture scelte dove le regole lasciano margine (da confermare)", "",
          "* massimo e minimo «delle barre» (strategia B) = massimo dell'alto e minimo del basso delle candele; la chiusura si confronta con questi.",
          "* RSI di Wilder a 14 barre (media mobile con alfa 1/14). Nella C, se nella stessa barra il comprato si chiude (RSI sopra 50) e l'RSI è "
          "sopra 70, si apre il venduto.",
          "* Nella A, se la chiusura è uguale alla media si tiene la posizione di prima; la posizione comincia dopo 50 chiusure.",
          "* Il volume medio 2023 è la somma/365 (con i giorni con dati, le monete nate nel 2023 con poche settimane di volume salirebbero in cima).",
          "* Operazione = entrata in una posizione (un rovesciamento da comprato a venduto vale 1 operazione e 2 lati di costo).",
          "* Funding: somma giornaliera del pannello del programma 6, divisa in parti uguali fra le barre del giorno, moltiplicata per la posizione.",
          "* Barre a 4 ore dalle candele mensili a 1 ora dell'archivio di Binance (`quarta.ore`, scaricate con `programma6.scarico_ore`); a 1 giorno dal pannello giornaliero. La storia prima del 2021 serve "
          "solo per gli indicatori.",
          "* Il rendimento l'anno e lo Sharpe sono sulle somme settimanali (lunedì-domenica) come le altre prove; settimane intere fra il 1° "
          "gennaio 2021 e il 31 ottobre 2026, o dalla prima candela. Il 2026 è parziale (10 mesi); l'anno di nascita di una moneta nata dopo il "
          "2021 pure.",
          f"* Sharpe corretto (probabilità, `terza.sharpe_corretto`, 52 settimane): N = {N_PROVE}; la varianza fra le prove viene dagli Sharpe dei "
          f"{n_gruppi} gruppi del conto (`asticella`) più le 60 combinazioni. Per capire, nel file `risultati.json` c'è anche lo stesso calcolo con i soli "
          "gruppi (`sharpe_corretto_solo_gruppi`).", "",
          "## Le 60 combinazioni", "",
          "| moneta | int. | str. | rend. l'anno | Sharpe | anni positivi | t | Sharpe corretto | operazioni | discesa | esito del filtro |",
          "|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in righe:
        if "m" not in r:
            t.append(f"| {r['moneta']} | {r['tf']} | {r['strategia']} | errore | | | | | | | {r['errore']} |")
            continue
        m = r["m"]
        t.append(f"| {r['moneta']} | {r['tf']} | {r['strategia']} | {pc(m['annuo'])} | {m['sharpe']:.2f} | {m['anni_positivi']}/{m['anni']} | "
                 f"{m['t']:.2f} | {m['sharpe_corretto']:.2f} | {m['operazioni']} | {pc(m['discesa_max'])} | {r['esito']} |")
    pas = [r for r in righe if r.get("passa")]
    t += ["", f"## Esito: passano il filtro {len(pas)} combinazioni su 60.", ""]
    for r in pas:
        m = r["m"]
        t.append(f"* {r['moneta']} {r['tf']} {r['strategia']}: {pc(m['annuo'])} l'anno, Sharpe {m['sharpe']:.2f}, corretto {m['sharpe_corretto']:.2f}, "
                 f"t {m['t']:.2f}, anni positivi {m['anni_positivi']}/{m['anni']}, anni: "
                 + ", ".join(f"{a} {pc(v)}" for a, v in m["per_anno"].items()))
    t.append("")
    t.append("Non è un giudizio di credibilità: chi passa va a backtest-auditor.")
    (QUI / "RISULTATI_OTTANTASETTESIMA.md").write_text("\n".join(t) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
