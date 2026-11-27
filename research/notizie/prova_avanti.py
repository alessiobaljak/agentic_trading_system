"""La prova in avanti delle notizie (REGOLE.md, sezione 3 e nota del 27 novembre 2026; backlog P31): «GA2 al contrario» sugli articoli
della nostra raccolta, ogni lunedì dal 30 novembre 2026, accanto a G1 sulle stesse settimane.

Il calcolo delle regole già scritte, senza cambiarle (lo stesso della prova 147, `programma7/ottantacinquesima.py`, con gli articoli
della raccolta al posto dei titoli katelabs):
* per ogni lunedì l e ogni moneta, gli articoli raccolti che la citano dal giorno l − 29 al giorno l − 2 (28 giorni), più uno, diviso il
  volume in dollari del perpetuo negli stessi giorni, in logaritmo;
* contano le monete dell'universo di G1 della settimana con almeno 3 articoli nei giorni raccolti fino a l − 2 (al massimo 112);
* long il quinto con il valore più alto, short il quinto con il più basso, banda 20/40, pesi secondo l'inverso della volatilità, almeno 20
  monete (`ventiquattresima.pesi_banda`); costi e funding come F5 (`terza.conto`).
Due conti: con le parole comuni di oggi (`raccolta.PAROLE`, la misura) e senza le sigle aggiunte il 27 novembre 2026. Ogni articolo conta
una volta sola, nel giorno (UTC) in cui la raccolta l'ha visto. Una settimana si conta quando è finita (il lunedì dopo).

Uso (il lunedì, dopo `python3 -m research.programma6.paper.aggiorna`, che rifà il pannello con i giorni nuovi):
    python3 -m research.notizie.prova_avanti
Scrive `research/notizie/avanti/` (settimane.csv, scelte.json, esito.json, RISULTATI.md); a schermo poche righe. Sui dati veri non parte
prima del 30 novembre 2026: è una prova in avanti.
"""
from __future__ import annotations

import gzip
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

from research.notizie import raccolta
from research.programma6 import ottava as ot
from research.programma6 import seconda as sc
from research.programma6 import sesta as se
from research.programma6 import terza as te
from research.programma6 import ventiquattresima as vq

QUI = Path(__file__).resolve().parent
USCITA = QUI / "avanti"
P7 = QUI.parent / "programma7"
INIZIO_RACCOLTA = sc.giorno(2026, 10, 30)          # il primo giro della raccolta (REGOLE.md, scritto il 30 ottobre)
PRIMO_LUNEDI = sc.giorno(2026, 11, 30)             # REGOLE.md, sezione 3
RITARDO, RECENTE, MINIMO, MASSIMO = 2, 28, 3, 112
OGGI, SENZA = "parole di oggi", "senza le sigle del 27 novembre"
VARIANTI = (OGGI, SENZA)


def articoli(archivio: Path | None = None) -> tuple[list, dict]:
    """Gli articoli dell'archivio, ognuno una volta sola (il primo salvataggio dello stesso collegamento): [(giorno, testo), ...], con il
    giorno (dall'epoca, in UTC) in cui la raccolta l'ha visto; e i conti delle righe per il rapporto."""
    archivio = archivio or raccolta.ARCHIVIO
    visti: set = set()
    out: list = []
    n = {"righe": 0, "doppie": 0, "senza_ora": 0}
    for f in sorted(archivio.glob("????-??-??.jsonl.gz")):
        with gzip.open(f, "rt", encoding="utf-8") as g:
            for r in g:
                if not r.strip():
                    continue
                a = json.loads(r)
                n["righe"] += 1
                if a["id"] in visti:
                    n["doppie"] += 1
                    continue
                visti.add(a["id"])
                q = raccolta.ora_utc(a.get("visto"))
                if q is None:
                    n["senza_ora"] += 1
                    continue
                out.append((int(q.timestamp() // 86400), f"{a.get('titolo', '')} {a.get('sommario', '')}"))
    return out, n


def _citatori(mese: str, cache: dict) -> tuple:
    """Per l'elenco dei nomi del mese (REGOLE.md, sezione 2): il citatore con le parole di oggi, le monete toccate dalle sigle del 27
    novembre e il citatore di quelle sole monete senza le sigle del 27 novembre. Per tutte le altre monete i due elenchi di parole danno
    per forza lo stesso risultato (la loro sigla e il loro nome non sono fra le sigle nuove), quindi il conto «senza» si rifà solo per
    queste: è lo stesso di `raccolta.citatore(elenco, PAROLE meno le sigle nuove)` (un test lo controlla), in metà del tempo."""
    if mese not in cache:
        f = raccolta.QUI / f"nomi_{mese}.json"
        if not f.exists():
            raise SystemExit(f"manca research/notizie/{f.name}: lo fa la raccolta al primo giro del mese (REGOLE.md, sezione 2)")
        el = json.loads(f.read_text(encoding="utf-8"))["elenco"]
        nuove = raccolta.PAROLE_27_NOVEMBRE
        tocca = {s: x for s, x in el.items() if x["sigla"] in nuove or x["nome"] in nuove or x["nome"].upper() in nuove}
        cache[mese] = (raccolta.citatore(el), set(tocca), raccolta.citatore(tocca, set(raccolta.PAROLE) - nuove))
    return cache[mese]


def conteggi(pan: dict, arts: list) -> dict:
    """Per i due conti, A[giorno del pannello, moneta]: gli articoli visti quel giorno che citano la moneta."""
    T, S = pan["close"].shape
    pos = {s: j for j, s in enumerate(pan["simboli"])}
    A = {v: np.zeros((T, S)) for v in VARIANTI}
    cache: dict = {}
    for giorno, testo in arts:
        k = giorno - pan["t0"]
        if not 0 <= k < T:
            continue
        oggi, tocca, senza = _citatori(sc.data(giorno)[:7], cache)
        a = oggi(testo)
        b = [s for s in a if s not in tocca] + senza(testo)
        for v, monete in ((OGGI, a), (SENZA, b)):
            for s in monete:
                if s in pos:
                    A[v][k, pos[s]] += 1
    return A


def segnale(A: np.ndarray, V: np.ndarray, lun_idx: np.ndarray, inizio_idx: int) -> np.ndarray:
    """GA2 di ogni lunedì (righe) e moneta: log((articoli dei 28 giorni fino a l − 2 + 1) / volume in dollari degli stessi giorni); NaN
    dove la moneta ha meno di 3 articoli nei giorni raccolti fino a l − 2 (al massimo 112) o non ha volume. Come la prova 147."""
    Ac = np.vstack([np.zeros((1, A.shape[1])), np.cumsum(A, axis=0)])
    Vc = np.vstack([np.zeros((1, V.shape[1])), np.cumsum(np.nan_to_num(V), axis=0)])
    fine = np.asarray(lun_idx, dtype=np.int64) - RITARDO + 1        # esclusa: le finestre finiscono alla fine del giorno l − 2
    if (fine - RECENTE < 0).any():
        raise ValueError("un lunedì senza 28 giorni di pannello prima di l − 2")
    a_rec = Ac[fine] - Ac[fine - RECENTE]
    a_tutti = Ac[fine] - Ac[np.maximum(fine - MASSIMO, max(int(inizio_idx), 0))]
    v_rec = Vc[fine] - Vc[fine - RECENTE]
    with np.errstate(all="ignore"):
        ga2 = np.log((a_rec + 1) / v_rec)
    return np.where((a_tutti >= MINIMO) & (v_rec > 0) & np.isfinite(ga2), ga2, np.nan)


def calcola(pan: dict, ps: dict, A: np.ndarray) -> tuple:
    """Il conto settimanale di GA2 al contrario sulle settimane finite dal 30 novembre 2026: (conto, pesi, monete con il segnale)."""
    lun = np.asarray(ps["lunedi"], dtype=np.int64)
    dentro = lun >= PRIMO_LUNEDI
    idx = lun - pan["t0"]
    ga2 = np.full((len(lun), A.shape[1]), np.nan)
    if dentro.any():
        ga2[dentro] = segnale(A, pan["quote_volume"], idx[dentro], INIZIO_RACCOLTA - pan["t0"])
    sig = ot.sigma_30(pan, idx)
    U = ps["U"] & dentro[:, None]
    W = vq.pesi_banda(np.where(np.isfinite(sig) & U, ga2, np.nan), U, sig)    # verso +1: long il valore più alto (GA2 al contrario)
    df = te.conto(W, ps["R"], ps["F"], sc.costi_moneta(pan["simboli"]))
    df.index = lun
    return df[dentro], W[dentro], (np.isfinite(ga2) & U)[dentro].sum(axis=1)


def g1(pan: dict, ps: dict, limite: bool = True) -> pd.DataFrame:
    """G1 a tavolino per settimana (le regole di `programma7/prima.py`: F5 decisa ogni giorno, banda dal 4 gennaio 2021), sulle settimane
    finite dal 30 novembre 2026: tutto a mercato e, se `limite`, con le spese a limite (a mercato dove mancano le candele a 1 ora)."""
    from research.programma7 import prima as pr
    lun = np.asarray(ps["lunedi"], dtype=np.int64)
    giorni = np.arange(max(se.INIZIO, int(lun[0])), int(lun[-1]) + 7, dtype=np.int64)
    idx = giorni - pan["t0"]
    Ud = pr.universo_del_giorno(giorni, lun, ps["U"])
    sig = ot.sigma_30(pan, idx)
    W = vq.pesi_banda(np.where(np.isfinite(sig), -se.funding_7(pan, idx), np.nan), Ud, sig)
    R = sc.rendimenti(pan)[idx]
    F = np.nan_to_num(pan["funding"][idx])
    costo = sc.costi_moneta(pan["simboli"])
    mercato = te.conto(W, R, F, costo)
    out = pd.DataFrame({"G1 a mercato": pr.per_settimana(mercato, giorni)["netto"]})
    tieni = giorni >= PRIMO_LUNEDI
    if limite and tieni.any():
        from research.programma6 import cinquantaseiesima as cs
        k0 = max(0, int(np.argmax(tieni)) - 1)       # un giorno prima: dal primo giorno tenuto le variazioni sono quelle vere
        spese, *_ = cs.spese_a_limite(W[k0:], R[k0:], giorni[k0:], pan["simboli"], costo)
        lim = mercato.iloc[k0:].reset_index(drop=True)
        lim["spese"] = spese
        lim["netto"] = lim["lordo"] - lim["spese"] - lim["funding"]
        out["G1 a limite"] = pr.per_settimana(lim, giorni[k0:])["netto"]
    return out[out.index >= PRIMO_LUNEDI]


def _numeri(x: pd.Series) -> dict:
    x = x.dropna()
    d = {"settimane": int(len(x)), "positive": int((x > 0).sum()), "media_settimana": float(x.mean()) if len(x) else None,
         "somma": float(x.sum()) if len(x) else None}
    d["sharpe"] = te.numeri_settimana(x)["sharpe"] if len(x) >= 2 else None
    return d


def _passato() -> dict:
    """I numeri sul passato della stessa regola, per il confronto (prove 138 e 147)."""
    out = {}
    try:
        e = json.loads((P7 / "risultati_settantaseiesima" / "esame.json").read_text(encoding="utf-8"))
        out["prova 138, verso opposto di GA2, Sharpe 2021-gennaio 2025"] = e["GA2"]["opposto_sharpe"]
    except (OSError, KeyError, ValueError):
        pass
    try:
        e = json.loads((P7 / "risultati_ottantacinquesima" / "esame.json").read_text(encoding="utf-8"))
        out["prova 147, GA2C, media a settimana marzo-aprile 2026"] = e["GA2C"]["media_settimana"]
        out["prova 147, G1 nelle stesse settimane"] = e["GA2C"]["G1_media_stesse_settimane"]
    except (OSError, KeyError, ValueError):
        pass
    return out


def esegui(log=print, pan: dict | None = None, uscita: Path = USCITA, limite: bool = True) -> dict:
    if pan is None:
        if datetime.now(timezone.utc).timestamp() < PRIMO_LUNEDI * 86400:
            raise SystemExit("la prova in avanti parte il 30 novembre 2026 (REGOLE.md, sezione 3): prima non si guardano i numeri")
        from research.programma6.paper import aggiorna as ag
        pan = sc.pannello()
        ag.applica_stima(pan)           # il funding come nel conto a tavolino (F5): la stima dal premio dove manca il dato vero
    ps = te.pannello_settimane(pan, log=lambda x: None, indicatori_si=False)
    arts, n = articoli()
    A = conteggi(pan, arts)
    ultimo = sc.data(pan["t0"] + pan["close"].shape[0] - 1)
    tab = pd.DataFrame()
    scelte: dict = {}
    for v in VARIANTI:
        df, W, nseg = calcola(pan, ps, A[v])
        tab[f"GA2C ({v})"] = df["netto"]
        tab[f"monete con il segnale ({v})"] = nseg
        for k, m in enumerate(df.index):
            pesi = {pan["simboli"][j]: round(float(W[k, j]), 6) for j in np.flatnonzero(W[k])}
            scelte.setdefault(sc.data(int(m)), {})[v] = {
                "monete_con_il_segnale": int(nseg[k]),
                "long": {s: p for s, p in sorted(pesi.items(), key=lambda x: -x[1]) if p > 0},
                "short": {s: p for s, p in sorted(pesi.items(), key=lambda x: x[1]) if p < 0}}
    if len(tab):
        g = g1(pan, ps, limite)
        for c in g.columns:
            tab[c] = g[c].reindex(tab.index)
    tab.index = [sc.data(int(m)) for m in tab.index]
    tab.index.name = "lunedi"
    serie = [c for c in tab.columns if not c.startswith("monete")]
    res = {"regole": "research/notizie/REGOLE.md, sezione 3 e nota del 27 novembre 2026", "dati_fino_al": ultimo,
           "articoli": {**n, "contati": len(arts)}, "settimane_finite": int(len(tab)),
           "numeri": {c: _numeri(tab[c]) for c in serie}, "passato": _passato(),
           "nota": "solo informazione: nessuna attesa fissa (REGOLE.md, aggiunta del 1° novembre); a 26 e 52 settimane si rifà il conto"}
    if len(tab) >= 52:
        u = tab.iloc[-52:]
        sh = {c: _numeri(u[c])["sharpe"] for c in serie}
        res["regola_52_settimane"] = {v: bool(sh[f"GA2C ({v})"] > 0.5 and all(sh[f"GA2C ({v})"] > sh[c] for c in serie if c.startswith("G1")))
                                      for v in VARIANTI}
    uscita.mkdir(parents=True, exist_ok=True)
    tab.to_csv(uscita / "settimane.csv")
    (uscita / "scelte.json").write_text(json.dumps(scelte, ensure_ascii=False, indent=1), encoding="utf-8")
    (uscita / "esito.json").write_text(json.dumps(res, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    pc = lambda x: "—" if x is None or x != x else f"{100 * x:+.2f}%"  # noqa: E731
    righe = ["# Notizie: la prova in avanti di GA2 al contrario", "",
             f"Regole in `REGOLE.md` (sezione 3 e nota del 27 novembre 2026), scritte prima. Dati dei prezzi fino al {ultimo}; articoli "
             f"contati {len(arts)} (righe dell'archivio {n['righe']}, doppie {n['doppie']}, senza ora {n['senza_ora']}).", ""]
    if not len(tab):
        righe.append("Nessuna settimana finita dal 30 novembre 2026: il primo numero (la settimana dal 30 novembre al 6 dicembre) arriva "
                     "lunedì 7 dicembre.")
    else:
        for c in serie:
            x = res["numeri"][c]
            sh = "—" if x["sharpe"] is None else f"{x['sharpe']:.2f}"
            righe.append(f"* **{c}**: {x['settimane']} settimane, {pc(x['media_settimana'])} a settimana dopo i costi, positive "
                         f"{x['positive']}, in tutto {pc(x['somma'])}, Sharpe {sh}.")
        righe += ["", "| lunedì | " + " | ".join(tab.columns) + " |", "|---" * (len(tab.columns) + 1) + "|"]
        for m, r in tab.iterrows():
            righe.append(f"| {m} | " + " | ".join(f"{int(r[c])}" if c.startswith("monete") else pc(r[c]) for c in tab.columns) + " |")
    if res["passato"]:
        righe += ["", "Il passato della stessa regola: " + "; ".join(
            f"{k} {x:.2f}" if "Sharpe" in k else f"{k} {pc(x)}" for k, x in res["passato"].items()) + "."]
    righe += ["", "Limiti dichiarati prima (audit del 26 novembre): l'abbinamento è automatico, senza una persona che filtri; le sigle che "
              "davano abbinamenti falsi (ARK, HIVE, GENIUS, SATS, APR) contano solo con il «$» dal 27 novembre, e la colonna «senza» dice "
              "quanto pesavano; le monete con la sigla diversa fra CoinGecko e Binance (per esempio RAYSOL, BEAMX, LUNA2, DODOX) non si "
              "abbinano mai; ANTUSDT (le azioni di Anthropic) non è nell'universo di G1.",
              "", f"S{res['nota'][1:]}."]
    testo = "\n".join(righe) + "\n"
    (uscita / "RISULTATI.md").write_text(testo, encoding="utf-8")
    for r in righe[:20]:
        log(r)
    return res


if __name__ == "__main__":
    esegui()
