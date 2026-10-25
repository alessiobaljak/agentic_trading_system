"""Programma 7, trentacinquesima prova (TRENTACINQUESIMA.md): CC, la vendita coperta del funding: il lato venduto di F5 sul perpetuo,
coperto comprando a pronti la stessa moneta per lo stesso valore; funding incassato meno costi piu' la variazione della base.

Uso: python3 -m research.programma7.trentacinquesima
"""
from __future__ import annotations

import gzip
import io
import json
import time
import urllib.request
import zipfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np
import pandas as pd

from research.programma6 import asticella as ast
from research.programma6 import ottava as ot
from research.programma6 import seconda as sc
from research.programma6 import sesta as se
from research.programma6 import terza as te
from research.programma6 import ventiquattresima as vq

QUI = Path(__file__).parent
RIS = QUI / "risultati_trentacinquesima"
DATI = QUI.parent / "data" / "spot_1d"
URL = "https://data.binance.vision/data/spot/monthly/klines/{s}/1d/{s}-1d-{m}.zip"
MESI = [f"{a}-{m:02d}" for a in range(2020, 2027) for m in range(1, 13) if f"{a}-{m:02d}" >= "2020-12" and f"{a}-{m:02d}" <= "2026-09"]
COSTO_PRONTI = 0.0015          # 0,10% di commissione + 0,05% di scarto, per lato
MARGINE = 0.5                  # il margine del perpetuo a leva 2: capitale = 1,5 × nozionale
CAPITALE = 1.0 + MARGINE


def base(perp: str) -> str:
    b = perp[:-4]
    for pre in ("1000000", "1000", "1M"):
        if b.startswith(pre):
            return b[len(pre):]
    return b


def pronti(perp: str) -> str:
    return base(perp) + "USDT"


def _scarica_mese(s: str, m: str):
    url = URL.format(s=s, m=m)
    for k in range(3):
        try:
            with urllib.request.urlopen(url, timeout=60) as r:
                dati = r.read()
            break
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return []
            if k == 2:
                return None
            time.sleep(2 ** k)
        except Exception:  # noqa: BLE001
            if k == 2:
                return None
            time.sleep(2 ** k)
    with zipfile.ZipFile(io.BytesIO(dati)) as z:
        nome = z.namelist()[0]
        righe = []
        for riga in z.read(nome).decode().splitlines():
            c = riga.split(",")
            if not c or not c[0].isdigit():
                continue
            ts = int(c[0])
            if ts > 10 ** 14:
                ts //= 1000          # microsecondi (file dal 2025) → millisecondi
            righe.append((ts // 86_400_000, float(c[1]), float(c[4])))
        return righe


def scarica(simboli_pronti: list, log=print) -> dict:
    """Scarica le candele giornaliere a pronti (apertura, chiusura) per ogni coppia; salva un csv.gz per coppia. Ritorna {coppia: stato}."""
    DATI.mkdir(parents=True, exist_ok=True)

    def una(s):
        f = DATI / f"{s}.csv.gz"
        if f.exists():
            return s, "ok"
        tutte, errori = [], 0
        for m in MESI:
            r = _scarica_mese(s, m)
            if r is None:
                errori += 1
            else:
                tutte += r
        if not tutte:
            f.write_bytes(gzip.compress(b"giorno,open,close\n"))
            return s, "senza pronti" if errori == 0 else f"errori {errori}"
        df = pd.DataFrame(tutte, columns=["giorno", "open", "close"]).drop_duplicates("giorno").sort_values("giorno")
        df.to_csv(f, index=False)
        return s, "ok" if errori == 0 else f"ok con {errori} mesi in errore"
    stati = {}
    with ThreadPoolExecutor(max_workers=16) as ex:
        for k, (s, st) in enumerate(ex.map(una, simboli_pronti), 1):
            stati[s] = st
            if k % 50 == 0:
                log(f"[trentacinquesima] scaricate {k}/{len(simboli_pronti)}")
    return stati


def tabella_pronti(coppie: list, t0: int, n: int) -> np.ndarray:
    """Le aperture giornaliere a pronti (giorni del pannello × coppie), NaN dove mancano."""
    O = np.full((n, len(coppie)), np.nan)
    for j, s in enumerate(coppie):
        f = DATI / f"{s}.csv.gz"
        if not f.exists():
            continue
        d = pd.read_csv(f)
        if d.empty:
            continue
        k = d["giorno"].to_numpy() - t0
        ok = (k >= 0) & (k < n)
        O[k[ok], j] = d["open"].to_numpy()[ok]
    return O


def esegui(log=print) -> dict:
    pan = sc.pannello()
    ps = te.pannello_settimane(pan, log=lambda x: None, indicatori_si=False)
    simboli = pan["simboli"]
    lun = ps["lunedi"] - pan["t0"]
    sig = ot.sigma_30(pan, lun)
    W = vq.pesi_banda(np.where(np.isfinite(sig), -se.funding_7(pan, lun), np.nan), ps["U"], sig)
    Ws = np.where(W < 0, -W, 0.0)
    somma = Ws.sum(axis=1, keepdims=True)
    Ws = np.where(somma > 0, Ws / np.where(somma > 0, somma, 1.0), 0.0)       # nozionale 1 sul lato venduto
    vendute = [s for s, c in zip(simboli, (Ws > 0).any(axis=0)) if c]
    coppie = sorted({pronti(s) for s in vendute})
    log(f"[trentacinquesima] {len(vendute)} perpetui nel lato venduto, {len(coppie)} coppie a pronti da scaricare")
    stati = scarica(coppie, log)
    RIS.mkdir(exist_ok=True)
    (RIS / "stato_scarico.json").write_text(json.dumps(stati, ensure_ascii=False, indent=1))
    n_ok = sum(1 for v in stati.values() if v.startswith("ok"))
    log(f"[trentacinquesima] coppie con il pronti: {n_ok} su {len(coppie)}")
    n_giorni = pan["close"].shape[0]
    Op = tabella_pronti(coppie, pan["t0"], n_giorni)
    jp = {s: coppie.index(pronti(s)) for s in simboli}
    O_perp = pan["open"]
    costo = sc.costi_moneta(simboli)
    F = ps["F"]                                   # funding della settimana di tenuta (somma), settimane × monete
    righe, prima = [], np.zeros(len(simboli))
    for w, m in enumerate(lun):
        m2 = m + 7
        x = Ws[w].copy()
        if m2 >= n_giorni or x.sum() == 0:
            righe.append({"lordo": 0.0, "spese": 0.0, "funding": 0.0, "netto": 0.0, "netto_doppio": 0.0, "giro": 0.0, "long": 0.0, "short": 0.0,
                          "monete": 0, "funding_incassato": 0.0, "base": 0.0, "senza_pronti": 0.0, "scoperto": 0.0})
            prima = np.zeros(len(simboli))
            continue
        with np.errstate(all="ignore"):
            rp = O_perp[m2] / O_perp[m] - 1
            rs = np.array([Op[m2, jp[s]] / Op[m, jp[s]] - 1 if np.isfinite(Op[m, jp[s]]) and np.isfinite(Op[m2, jp[s]]) else np.nan for s in simboli])
        disp = np.isfinite(rs) & np.isfinite(rp) & (x > 0)
        senza = float(x[(x > 0) & ~disp].sum())
        x = np.where(disp, x, 0.0)
        fund = float((x * np.nan_to_num(F[w])).sum())                 # il funding che lo short incassa (positivo = incassa)
        base_ = float((x * (np.nan_to_num(rs) - np.nan_to_num(rp))).sum())
        giro = np.abs(x - prima)
        spese = float((giro * costo).sum() + (giro * COSTO_PRONTI).sum())
        netto = base_ + fund - spese
        scoperto = float((x * -np.nan_to_num(rp)).sum() + fund - (giro * costo).sum())
        righe.append({"lordo": base_, "spese": spese, "funding": -fund, "netto": netto, "netto_doppio": base_ + fund - 2 * spese, "giro": float(giro.sum()),
                      "long": float((x * np.nan_to_num(rs)).sum()), "short": float((x * -np.nan_to_num(rp)).sum()), "monete": int((x > 0).sum()),
                      "funding_incassato": fund, "base": base_, "senza_pronti": senza, "scoperto": scoperto})
        prima = x
    noz = pd.DataFrame(righe, index=ps["lunedi"])
    cap = noz.copy()
    for c in ("lordo", "spese", "funding", "netto", "netto_doppio", "long", "short", "funding_incassato", "base", "scoperto"):
        cap[c] = noz[c] / CAPITALE
    noz.to_csv(RIS / "settimane_CC_nozionale.csv.gz")
    cap.to_csv(RIS / "settimane_CC.csv.gz")
    btc = pd.Series(ps["R"][:, simboli.index("BTCUSDT")], index=ps["lunedi"])
    out = {"CC": te.esame(cap, btc, inizio=se.INIZIO, anni_pieni=se.ANNI_PIENI),
           "CC per nozionale": te.esame(noz, btc, inizio=se.INIZIO, anni_pieni=se.ANNI_PIENI)}
    dentro = cap[cap.index >= se.INIZIO]
    anni = pd.to_datetime(dentro.index.to_numpy() * 86400, unit="s").year
    out["per_anno"] = {int(a): {"funding_incassato": float(dentro["funding_incassato"][anni == a].sum()),
                                "base": float(dentro["base"][anni == a].sum()), "spese": float(dentro["spese"][anni == a].sum()),
                                "netto": float(dentro["netto"][anni == a].sum()), "senza_pronti_medio": float(dentro["senza_pronti"][anni == a].mean())}
                       for a in sorted(set(anni))}
    scop = noz.loc[dentro.index, "scoperto"]
    out["lato_venduto_scoperto"] = te.numeri_settimana(scop)
    out["senza_pronti_medio"] = float(dentro["senza_pronti"].mean())
    out["coppie"] = {"vendute": len(vendute), "coppie": len(coppie), "con_pronti": n_ok}
    serie = {**ast.serie_nuove(), "97 CC": cap["netto"]}
    rivisto = ast.corretto_rivisto(serie, {"97 CC": out["CC"]["intero"]})
    r = rivisto["candidate"]["97 CC"]
    e = out["CC"]
    e["sharpe_corretto"], e["t"], e["gruppi"] = r["corretto_con_aggiunta"], r["t"], rivisto["gruppi"]
    e["esito"] = te.esito(e, e["sharpe_corretto"])
    e["regola_del_proprietario"] = bool(e["sharpe_corretto"] >= 0.90 and all(v > 0 for v in e["per_anno"].values()) and e["t"] > 3)
    (RIS / "esame.json").write_text(json.dumps(out, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    pc = lambda v: f"{100 * v:+.1f}%"  # noqa: E731
    i, n_ = e["intero"], out["CC per nozionale"]["intero"]
    sc_ = out["lato_venduto_scoperto"]
    righe_t = ["# Programma 7 — risultati della trentacinquesima prova (CC: la vendita coperta del funding)", "",
               "Regole in `TRENTACINQUESIMA.md` (scritte prima). Dal 4 gennaio 2021 al 5 ottobre 2026, a settimana.", "",
               "| | Sharpe | l'anno | volatilità | discesa | spese l'anno | per anno |", "|---|---|---|---|---|---|---|",
               f"| CC per capitale (1,5 × nozionale) | {i['sharpe']:.2f} | {pc(i['annuo'])} | {100 * i['volatilita']:.1f}% | {100 * i['discesa_max']:.1f}% | "
               f"{100 * e['spese_annue']:.1f}% | " + ", ".join(f"{y} {pc(v)}" for y, v in e["per_anno"].items()) + " |",
               f"| CC per nozionale | {n_['sharpe']:.2f} | {pc(n_['annuo'])} | {100 * n_['volatilita']:.1f}% | {100 * n_['discesa_max']:.1f}% | "
               f"{100 * out['CC per nozionale']['spese_annue']:.1f}% | " + ", ".join(f"{y} {pc(v)}" for y, v in out["CC per nozionale"]["per_anno"].items()) + " |",
               f"| lato venduto scoperto (per nozionale) | {sc_['sharpe']:.2f} | {pc(sc_['annuo'])} | {100 * sc_['volatilita']:.1f}% | {100 * sc_['discesa_max']:.1f}% | — | — |",
               "",
               f"* {out['coppie']['vendute']} perpetui nel lato venduto, {out['coppie']['coppie']} coppie a pronti, {out['coppie']['con_pronti']} con i dati; quota del "
               f"nozionale senza pronti in media {100 * out['senza_pronti_medio']:.0f}%.",
               "* Per anno (per nozionale, somme): " + "; ".join(f"{a} funding {pc(v['funding_incassato'] * CAPITALE)}, base {pc(v['base'] * CAPITALE)}, spese "
                                                               f"{pc(v['spese'] * CAPITALE)}, netto {pc(v['netto'] * CAPITALE)}" for a, v in out["per_anno"].items()) + ".",
               f"* **CC**: Sharpe corretto {e['sharpe_corretto']:.2f} ({e['gruppi']} gruppi), t {e['t']:.2f}; esito {e['esito']}; regola del proprietario: "
               f"{'sì' if e['regola_del_proprietario'] else 'no'}."]
    testo = "\n".join(righe_t) + "\n"
    (QUI / "RISULTATI_TRENTACINQUESIMA.md").write_text(testo, encoding="utf-8")
    log(testo)
    return out


if __name__ == "__main__":
    esegui(log=lambda x: print(x, flush=True))
    print("TRENTACINQUESIMA FINITA", flush=True)
