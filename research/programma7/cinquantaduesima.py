"""Programma 7, cinquantaduesima prova (CINQUANTADUESIMA.md): KP, il premio coreano fra le monete deciso ogni giorno come G1. Short il
quinto con il premio relativo di Upbit (rispetto al Bitcoin, media dei 7 giorni prima) piu' alto, long il piu' basso, banda 20/40,
ordini limite.

Uso: python3 -m research.programma7.cinquantaduesima
"""
from __future__ import annotations

import json
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

from research.programma6 import annunci as an
from research.programma6 import asticella as ast
from research.programma6 import cinquantaseiesima as cs
from research.programma6 import ottava as ot
from research.programma6 import seconda as sc
from research.programma6 import sesta as se
from research.programma6 import terza as te
from research.programma6 import ventiquattresima as vq
from research.programma7 import prima as g1

QUI = Path(__file__).parent
RADICE = QUI.parents[1]
RIS = QUI / "risultati_cinquantaduesima"
DATI = RADICE / "research" / "data" / "upbit" / "giorni"
API = "https://api.upbit.com/v1"
DAL, FINE = sc.giorno(2020, 12, 1), sc.giorno(2026, 10, 19)
TETTO, VALORE_MIN, GIORNI, VALIDI = 0.20, 1e8, 7, 5


def _get(url: str):
    for k in range(6):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "ricerca/1.0"}), timeout=60) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code in (429, 418, 500, 502, 503):
                time.sleep(1.5 * (k + 1))
                continue
            return None
        except Exception:  # noqa: BLE001
            time.sleep(1.5 * (k + 1))
    return None


def mercati() -> dict:
    """Perpetuo di Binance → mercato in won di Upbit (``KRW-SIGLA``), per i mercati che esistono oggi."""
    pan = sc.pannello()
    out = {}
    for x in _get(f"{API}/market/all") or []:
        if x["market"].startswith("KRW-"):
            p = an.perpetuo(x["market"][4:], pan["simboli"])
            if p:
                out[p] = x["market"]
    return out


def candele(mercato: str) -> pd.DataFrame:
    """Le candele giornaliere in won (giorno UTC → chiusura, valore scambiato), dal dicembre 2020, salvate in ``DATI``."""
    f = DATI / f"{mercato}.csv.gz"
    if f.exists():
        return pd.read_csv(f, index_col=0)
    righe, fino = [], datetime(2026, 10, 26, tzinfo=timezone.utc)
    while True:
        d = _get(f"{API}/candles/days?market={mercato}&count=200&to={fino.strftime('%Y-%m-%dT%H:%M:%SZ')}")
        time.sleep(0.12)
        if not d:
            break
        righe += [(sc.giorno(*map(int, x["candle_date_time_utc"][:10].split("-"))), float(x["trade_price"]),
                   float(x["candle_acc_trade_price"])) for x in d]
        primo = min(x["candle_date_time_utc"] for x in d)
        if len(d) < 200 or primo[:10] <= sc.data(DAL):
            break
        fino = datetime.fromisoformat(primo).replace(tzinfo=timezone.utc)
    df = pd.DataFrame(righe, columns=["giorno", "chiusura", "valore"]).drop_duplicates("giorno").set_index("giorno").sort_index()
    DATI.mkdir(parents=True, exist_ok=True)
    df.to_csv(f)
    return df


def multiplo(simbolo: str) -> float:
    """Quante monete vale un contratto con il prefisso dei multipli (1000PEPE = 1.000 PEPE)."""
    for pre, m in (("1000000", 1e6), ("1M", 1e6), ("1000", 1e3)):
        if simbolo.startswith(pre):
            return m
    return 1.0


def premio(pan: dict, mappa: dict, log=print) -> np.ndarray:
    """P[t, j]: il premio relativo di Upbit alla chiusura del giorno t (NaN dove non valido)."""
    T, S = pan["close"].shape
    t0 = pan["t0"]
    btc = candele("KRW-BTC")
    j_btc = pan["simboli"].index("BTCUSDT")
    krw_btc = btc["chiusura"].reindex(np.arange(t0, t0 + T)).to_numpy()
    P = np.full((T, S), np.nan)
    for n, (s, m) in enumerate(sorted(mappa.items())):
        if s == "BTCUSDT":
            continue
        c = candele(m)
        if c.empty:
            continue
        j = pan["simboli"].index(s)
        kj = c["chiusura"].reindex(np.arange(t0, t0 + T)).to_numpy()
        vj = c["valore"].reindex(np.arange(t0, t0 + T)).to_numpy()
        with np.errstate(all="ignore"):
            p = (kj / krw_btc) / ((pan["close"][:, j] / multiplo(s)) / pan["close"][:, j_btc]) - 1
        p[~(np.abs(p) <= TETTO) | ~(np.nan_to_num(vj) >= VALORE_MIN)] = np.nan
        P[:, j] = p
        if n % 40 == 0:
            log(f"[cinquantaduesima] {n} mercati letti")
    return P


def segnale(P: np.ndarray, idx: np.ndarray) -> np.ndarray:
    """La media di P nei 7 giorni prima di ogni giorno (almeno 5 validi)."""
    out = np.full((len(idx), P.shape[1]), np.nan)
    for k, i in enumerate(idx):
        blocco = P[i - GIORNI:i]
        n = np.isfinite(blocco).sum(axis=0)
        with np.errstate(all="ignore"):
            m = np.nanmean(blocco, axis=0)
        out[k] = np.where(n >= VALIDI, m, np.nan)
    return out


def conto(W, R, F, costo, giorni, simboli) -> pd.DataFrame:
    mercato = te.conto(W, R, F, costo)
    limite = mercato.copy()
    spese, n_tot, n_lim, n_senza = cs.spese_a_limite(W, R, giorni, simboli, costo)
    limite["spese"] = spese
    limite["netto"] = limite["lordo"] - limite["spese"] - limite["funding"]
    limite["netto_doppio"] = limite["lordo"] - 2 * limite["spese"] - limite["funding"]
    return limite, {"variazioni": n_tot, "eseguite_con_il_limite": n_lim, "senza_candele_a_1_ora": n_senza}


def esegui(log=print) -> dict:
    pan = sc.pannello()
    ps = te.pannello_settimane(pan, log=lambda x: None, indicatori_si=False)
    mappa = mercati()
    log(f"[cinquantaduesima] {len(mappa)} perpetui con un mercato in won; scarico le candele di Upbit")
    P = premio(pan, mappa, log)
    giorni = np.arange(se.INIZIO, FINE, dtype=np.int64)
    idx = giorni - pan["t0"]
    Ud = g1.universo_del_giorno(giorni, ps["lunedi"], ps["U"])
    sig = ot.sigma_30(pan, idx)
    S = segnale(P, idx)
    R = sc.rendimenti(pan)[idx]
    F = np.nan_to_num(pan["funding"][idx])
    costo = sc.costi_moneta(pan["simboli"])
    btc = pd.Series(ps["R"][:, ps["simboli"].index("BTCUSDT")], index=ps["lunedi"])
    out = {}
    for nome, verso in (("KP", -1.0), ("KP opposto", 1.0)):
        W = vq.pesi_banda(np.where(np.isfinite(sig), verso * S, np.nan), Ud, sig)
        lim, ordini = conto(W, R, F, costo, giorni, pan["simboli"])
        sett = g1.per_settimana(lim, giorni)
        RIS.mkdir(exist_ok=True)
        sett.to_csv(RIS / f"settimane_{nome.replace(' ', '_')}.csv.gz")
        e = te.esame(sett, btc, inizio=se.INIZIO, anni_pieni=se.ANNI_PIENI)
        e["ordini"], e["movimenti"] = ordini, g1.movimenti(W)
        out[nome] = e
        if nome == "KP":
            W_kp, sett_kp = W, sett
    e = out["KP"]
    rivisto = ast.corretto_rivisto({**ast.serie_nuove(), "114 KP": sett_kp["netto"]}, {"114 KP": e["intero"]})
    r = rivisto["candidate"]["114 KP"]
    e["sharpe_corretto"], e["t"], e["gruppi"] = r["corretto_con_aggiunta"], r["t"], rivisto["gruppi"]
    e["esito"] = te.esito(e, e["sharpe_corretto"])
    g1s = pd.read_csv(QUI / "risultati_prima" / "settimane_G1.csv.gz", index_col=0)
    c = sett_kp.index.intersection(g1s.index)
    e["correlazione_G1"] = float(np.corrcoef(sett_kp.loc[c, "netto"], g1s.loc[c, "netto"])[0, 1])
    valide = np.isfinite(S) & Ud
    e["monete_con_segnale_mediana"] = float(np.median(valide.sum(axis=1)))
    scarti = []
    for k in range(len(idx)):
        v = S[k, valide[k]]
        if len(v) >= 20:
            q = np.sort(v)
            n5 = max(1, len(q) // 5)
            scarti.append(q[-n5:].mean() - q[:n5].mean())
    e["scarto_quinti_mediana"] = float(np.median(scarti)) if scarti else None
    anni = e.get("per_anno", {})
    e["regola_proprietario"] = bool(e["sharpe_corretto"] >= 0.90 and e["t"] > 3 and anni and all(v > 0 for v in anni.values()))
    (RIS / "esame.json").write_text(json.dumps(out, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    i, o, mv, op = e["intero"], e["ordini"], e["movimenti"], out["KP opposto"]["intero"]
    testo = "\n".join([
        "# Programma 7 — risultati della cinquantaduesima prova (KP: il premio coreano fra le monete, ogni giorno)", "",
        "Regole in `CINQUANTADUESIMA.md` (scritte prima). Dal 4 gennaio 2021 al 19 ottobre 2026, candele giornaliere di Upbit e di Binance.", "",
        f"* {len(mappa)} perpetui con un mercato in won; monete con il segnale ogni giorno, mediana {e['monete_con_segnale_mediana']:.0f}; "
        f"lo scarto del premio fra il quinto più alto e il più basso, mediana {100 * (e['scarto_quinti_mediana'] or 0):.2f}% (Coinbase, prova 87: 0,15%).",
        f"* Operazioni: {mv['entrate_al_giorno']:.1f} entrate e {mv['uscite_al_giorno']:.1f} uscite al giorno; una posizione dura in media "
        f"{mv['durata_media_giorni']:.1f} giorni; variazioni {o['variazioni']}, eseguite con il limite {o['eseguite_con_il_limite']}.",
        f"* **KP: Sharpe {i['sharpe']:.2f}**, {100 * i['annuo']:+.1f}% l'anno, volatilità {100 * i['volatilita']:.1f}%, discesa "
        f"{100 * i['discesa_max']:.1f}%; spese {100 * e['spese_annue']:.1f}% l'anno.",
        "* Per anno: " + ", ".join(f"{a} {100 * v:+.1f}%" for a, v in e["per_anno"].items()) + ".",
        f"* Il verso opposto (long il premio alto): Sharpe {op['sharpe']:.2f}, {100 * op['annuo']:+.1f}% l'anno.",
        f"* Correlazione con G1: {e['correlazione_G1']:.2f}.",
        f"* Sharpe corretto con l'aggiunta {e['sharpe_corretto']:.2f} ({e['gruppi']} gruppi); t dello Sharpe {e['t']:.2f}; regola del "
        f"proprietario (corretto ≥ 0,90, ogni anno positivo, t > 3): {'sì' if e['regola_proprietario'] else 'no'}.", "",
        f"**Esito: {e['esito']}**"]) + "\n"
    (QUI / "RISULTATI_CINQUANTADUESIMA.md").write_text(testo, encoding="utf-8")
    log(testo)
    return out


if __name__ == "__main__":
    esegui(log=lambda x: print(x, flush=True))
    print("CINQUANTADUESIMA FINITA", flush=True)
