"""Programma 6, paper: la misura in avanti a tavolino dell'idea 45 del registro (``paper/REGOLE.md``, sezione 18): F5 con
l'esposizione dimezzata nelle settimane in cui il funding medio dei 7 giorni dell'universo e' sotto -11% l'anno.

Scritta il 27 novembre 2026 (audit del 26 novembre, punti ciechi 8), prima di ogni settimana misurata: si contano solo le
settimane dal lunedi' 30 novembre 2026, nessun numero sulle settimane di prima (l'idea e' nata guardando tutti gli anni usati,
``programma6/PERDITE_F5.md``, punto 4). Ogni settimana, dal pannello della ricerca (``seconda.pannello``, con la stima dal premio
nei giorni ancora senza il funding vero, come il paper: ``aggiorna.applica_stima``), per ogni lunedi':

* il funding medio dei 7 giorni dell'universo di F5: fra le monete dell'universo che F5 ordina (le 100 della settimana con la
  volatilita' dei 30 giorni), la media della somma del funding dei 7 giorni di tenuta prima del lunedi' (come ``funding_medio_7``
  di ``bot/portafoglio/f5.py``, idea 48), in ragione d'anno con 365/7;
* F5 com'e' (lo stesso codice del paper: ``ventiquattresima.pesi_banda``) e F5 con la regola (tutti i pesi per 0,5 nelle settimane
  sotto la soglia), con lo stesso conto (``terza.conto``: le spese per dimezzare e per tornare pieni ci sono).

Le settimane di prima servono solo alla banda di F5 (chi e' dentro dipende dalle settimane prima): non si scrivono. Quando arriva
il funding vero si rifa' tutto da capo: conta il numero col funding vero.

Uso (dopo ``paper/aggiorna.sh``, che rifa' il pannello): python3 -m research.programma6.paper.funding_medio [--uscita FILE]
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from research.programma6 import ottava as ot
from research.programma6 import seconda as sc
from research.programma6 import sesta as se
from research.programma6 import terza as te
from research.programma6 import ventiquattresima as vq

QUI = Path(__file__).parent
USCITA = QUI / "funding_medio.json"
PAPER_JSON = QUI / "paper.json"
INIZIO = sc.giorno(2026, 11, 30)       # il primo lunedi' dopo la regola, scritta venerdi' 27 novembre 2026
SOGLIA_ANNUA = -0.11                   # idea 45: sotto -11% l'anno l'esposizione si dimezza
DIMEZZATA = 0.5
GIORNI_ANNO = 365.0
REGOLA = ("idea 45 (paper/REGOLE.md, sezione 18): F5 con l'esposizione dimezzata quando il funding medio dei 7 giorni "
          "dell'universo e' sotto -11% l'anno")


def funding_medio_7(s7: np.ndarray, U: np.ndarray, sig: np.ndarray) -> tuple:
    """(media, numero di monete) per lunedi': la media di ``s7`` (la somma del funding dei 7 giorni prima, settimane x monete)
    fra le monete dell'universo con la volatilita' dei 30 giorni, cioe' quelle che F5 ordina (``ventiquattresima.pesi_banda``,
    come il bot); NaN senza monete."""
    with np.errstate(invalid="ignore"):
        dentro = U & np.isfinite(sig) & (sig > 0)
    n = dentro.sum(axis=1)
    somma = np.where(dentro, s7, 0.0).sum(axis=1)
    return np.where(n > 0, somma / np.maximum(n, 1), np.nan), n


def annuo(medio):
    """La somma dei 7 giorni in ragione d'anno (per 365/7)."""
    return np.asarray(medio, dtype=float) * GIORNI_ANNO / 7


def esposizione(medio) -> np.ndarray:
    """0,5 se il funding medio dei 7 giorni, in ragione d'anno, e' sotto la soglia; altrimenti 1 (anche senza il dato)."""
    with np.errstate(invalid="ignore"):
        return np.where(annuo(medio) < SOGLIA_ANNUA, DIMEZZATA, 1.0)


def serie(pan: dict, inizio: int = INIZIO) -> dict:
    """F5 com'e' e F5 con la regola su tutte le settimane complete del pannello, con il funding medio e l'esposizione di ogni
    lunedi' (prima di ``inizio`` l'esposizione e' sempre piena). Le settimane di prima servono alla banda: non si scrivono."""
    ps = te.pannello_settimane(pan, log=lambda x: None, indicatori_si=False)
    lun = ps["lunedi"] - pan["t0"]
    sig = ot.sigma_30(pan, lun)
    s7 = se.funding_7(pan, lun)
    W = vq.pesi_banda(np.where(np.isfinite(sig), -s7, np.nan), ps["U"], sig)
    medio, n = funding_medio_7(s7, ps["U"], sig)
    k = np.where(ps["lunedi"] >= inizio, esposizione(medio), 1.0)
    costo = sc.costi_moneta(ps["simboli"])
    f5 = te.conto(W, ps["R"], ps["F"], costo)
    regola = te.conto(W * k[:, None], ps["R"], ps["F"], costo)
    f5.index = ps["lunedi"]
    regola.index = ps["lunedi"]
    return {"lunedi": ps["lunedi"], "U": ps["U"], "sig": sig, "W": W, "medio": medio, "monete": n, "k": k,
            "f5": f5, "regola": regola}


def _r(x, cifre: int = 6):
    x = float(x)
    return round(x, cifre) if np.isfinite(x) else None


def _stimati(pan: dict, da: int, a: int, colonne: np.ndarray):
    """I giorni-moneta senza il funding vero (``funding_stimato`` del pannello) dei giorni ``da``..``a`` (escluso) e delle
    monete ``colonne``; None se il pannello non lo dice."""
    M = pan.get("funding_stimato")
    if M is None:
        return None
    return int(M[max(0, da): a][:, colonne].sum())


def settimana_in_corso(pan: dict, inizio: int = INIZIO):
    """La decisione del lunedi' della settimana non ancora chiusa (se il pannello ha gia' la candela del lunedi' e il lunedi' e'
    dal giorno ``inizio``): si conta solo a settimana chiusa."""
    T = pan["close"].shape[0]
    giorni = np.arange(T) + pan["t0"]
    lun = np.flatnonzero((giorni + 3) % 7 == 0)
    if not len(lun) or lun[-1] + 7 <= T or lun[-1] < 8 or giorni[lun[-1]] < inizio:
        return None
    m = int(lun[-1])
    U = te.universo_lunedi(pan, m)[0][None]
    sig = ot.sigma_30(pan, np.array([m]))
    medio, n = funding_medio_7(se.funding_7(pan, np.array([m])), U, sig)
    with np.errstate(invalid="ignore"):
        dentro = np.flatnonzero(U[0] & np.isfinite(sig[0]) & (sig[0] > 0))
    return {"lunedi": sc.data(int(giorni[m])), "funding_medio_7": _r(medio[0], 8), "funding_medio_annuo": _r(annuo(medio[0])),
            "monete": int(n[0]), "esposizione": float(esposizione(medio)[0]),
            "stimati_finestra": _stimati(pan, m - 7, m, dentro)}


def confronto_con_paper(settimane: list, file):
    """Lo scarto massimo fra F5 di qui e F5 di ``paper.json`` nelle stesse settimane (devono essere uguali se il pannello e'
    lo stesso); None senza settimane in comune."""
    try:
        f5 = json.loads(Path(file).read_text(encoding="utf-8"))["candidate"]["F5"]["settimane"]
    except (OSError, ValueError, KeyError, TypeError):
        return None
    comuni = [(x["F5"], float(f5[x["lunedi"]])) for x in settimane if x["lunedi"] in f5 and x["F5"] is not None]
    if not comuni:
        return None
    return {"settimane": len(comuni), "scarto_massimo": max(abs(a - b) for a, b in comuni)}


def calcola(pan: dict, inizio: int = INIZIO, paper_json=None) -> dict:
    """Le settimane chiuse dal lunedi' ``inizio`` (solo quelle), il totale, la settimana in corso e, con ``paper_json``, il
    confronto di F5 con quello del paper."""
    s = serie(pan, inizio)
    t0, T = pan["t0"], pan["close"].shape[0]
    sel = np.flatnonzero(s["lunedi"] >= inizio)
    settimane = []
    for i in sel:
        m = int(s["lunedi"][i]) - t0
        with np.errstate(invalid="ignore"):
            dentro = np.flatnonzero(s["U"][i] & np.isfinite(s["sig"][i]) & (s["sig"][i] > 0))
        a, b = s["f5"].iloc[i], s["regola"].iloc[i]
        settimane.append({
            "lunedi": sc.data(int(s["lunedi"][i])), "funding_medio_7": _r(s["medio"][i], 8),
            "funding_medio_annuo": _r(annuo(s["medio"][i])), "monete": int(s["monete"][i]), "esposizione": float(s["k"][i]),
            "F5": _r(a["netto"]), "F5_regola": _r(b["netto"]), "differenza": _r(b["netto"] - a["netto"]),
            "spese_F5": _r(a["spese"]), "spese_regola": _r(b["spese"]),
            "stimati_finestra": _stimati(pan, m - 7, m, dentro),
            "stimati_settimana": _stimati(pan, m, m + 7, np.flatnonzero(s["W"][i] != 0))})
    totale = None
    if len(sel):
        x5, xr = s["f5"]["netto"].to_numpy()[sel], s["regola"]["netto"].to_numpy()[sel]
        totale = {"settimane": int(len(sel)), "dimezzate": int((s["k"][sel] < 1).sum()),
                  "F5": _r(np.prod(1 + x5) - 1), "F5_regola": _r(np.prod(1 + xr) - 1),
                  "differenza_media": _r((xr - x5).mean())}
    return {"regola": REGOLA, "inizio": sc.data(inizio), "soglia_annua": SOGLIA_ANNUA, "dati_fino_al": sc.data(t0 + T - 1),
            "settimane": settimane, "totale": totale, "settimana_in_corso": settimana_in_corso(pan, inizio),
            "confronto_con_paper": confronto_con_paper(settimane, paper_json) if paper_json else None}


def _pc(x) -> str:
    return "n.d." if x is None else f"{100 * x:+.2f}%"


def riassunto(res: dict, righe_max: int = 10) -> list:
    """Al massimo 15 righe per lo schermo e per il messaggio della settimana."""
    out = [f"[funding medio] {res['regola']}; settimane dal {res['inizio']}, dati fino al {res['dati_fino_al']}"]
    st = res["settimane"]
    if not st:
        out.append(f"  nessuna settimana chiusa dal {res['inizio']}: la prima si conta quando il pannello arriva alla domenica dopo")
    for x in st[-righe_max:]:
        stima = [f"{x[k]} giorni-moneta {d}" for k, d in (("stimati_finestra", "prima"), ("stimati_settimana", "nella settimana"))
                 if x.get(k)]
        out.append(f"  {x['lunedi']}: funding medio {_pc(x['funding_medio_annuo'])} l'anno su {x['monete']} monete, esposizione "
                   f"{'dimezzata' if x['esposizione'] < 1 else 'piena'}; F5 {_pc(x['F5'])}, con la regola {_pc(x['F5_regola'])}"
                   + (f" (funding stimato: {', '.join(stima)})" if stima else ""))
    t = res["totale"]
    if t:
        out.append(f"  totale: {t['settimane']} settimane, {t['dimezzate']} {'dimezzata' if t['dimezzate'] == 1 else 'dimezzate'}; "
                   f"F5 {_pc(t['F5'])}, con la regola "
                   f"{_pc(t['F5_regola'])}; differenza media {100 * t['differenza_media']:+.2f} punti a settimana")
    c = res["settimana_in_corso"]
    if c:
        out.append(f"  settimana in corso dal {c['lunedi']}: funding medio {_pc(c['funding_medio_annuo'])} l'anno, esposizione "
                   f"{'dimezzata' if c['esposizione'] < 1 else 'piena'} (si conta a settimana chiusa)")
    cp = res.get("confronto_con_paper")
    if cp and cp["scarto_massimo"] > 1e-6:
        out.append(f"  attenzione: F5 diverso da paper.json in {cp['settimane']} settimane (scarto massimo "
                   f"{100 * cp['scarto_massimo']:.4f} punti): il pannello non e' quello del paper")
    return out


def esegui(uscita=USCITA, log=print, paper_json=PAPER_JSON) -> dict:
    # la stessa stima del paper nei giorni senza il funding vero (REGOLE.md, sezione 2); un pannello salvato prima del 27
    # novembre 2026 si rifa' dai file (seconda.rifai_funding, dentro applica_stima)
    from research.programma6.paper import aggiorna as ag
    pan = sc.pannello()
    ag.applica_stima(pan)
    res = calcola(pan, INIZIO, paper_json)
    Path(uscita).write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    for riga in riassunto(res):
        log(riga)
    return res


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="La misura in avanti dell'idea 45 (paper/REGOLE.md, sezione 18)")
    p.add_argument("--uscita", type=Path, default=USCITA, help="il file JSON dei risultati")
    a = p.parse_args(argv)
    esegui(a.uscita, log=lambda x: print(x, flush=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
