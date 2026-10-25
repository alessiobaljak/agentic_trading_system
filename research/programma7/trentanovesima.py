"""Programma 7, trentanovesima prova (TRENTANOVESIMA.md): VS, il volume in dollari del perpetuo sui 7 giorni diviso quello a pronti
(la speculazione rispetto all'uso) come segnale fra le 100 piu' scambiate: short il piu' speculativo, long il meno; banda 20/40 come F5.

Uso: python3 -m research.programma7.trentanovesima            (scarica i volumi a pronti se mancano, poi calcola)
     python3 -m research.programma7.trentanovesima scarica    (solo lo scarico)
"""
from __future__ import annotations

import gzip
import hashlib
import io
import json
import sys
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
from research.programma7 import trentacinquesima as cc

QUI = Path(__file__).parent
RIS = QUI / "risultati_trentanovesima"
DATI = QUI.parent / "data" / "spot_1d_vol"
SEME = 2026


def _scarica_mese(s: str, m: str):
    url = cc.URL.format(s=s, m=m)
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
        righe = []
        for riga in z.read(z.namelist()[0]).decode().splitlines():
            c = riga.split(",")
            if not c or not c[0].isdigit():
                continue
            ts = int(c[0])
            if ts > 10 ** 14:
                ts //= 1000
            righe.append((ts // 86_400_000, float(c[1]), float(c[4]), float(c[7])))      # giorno, apertura, chiusura, volume in dollari
        return righe


def scarica(coppie: list, log=print) -> dict:
    DATI.mkdir(parents=True, exist_ok=True)

    def una(s):
        f = DATI / f"{s}.csv.gz"
        if f.exists():
            return s, "ok"
        tutte, errori = [], 0
        for m in cc.MESI:
            r = _scarica_mese(s, m)
            if r is None:
                errori += 1
            else:
                tutte += r
        if not tutte:
            f.write_bytes(gzip.compress(b"giorno,open,close,quote_volume\n"))
            return s, "senza pronti" if errori == 0 else f"errori {errori}"
        pd.DataFrame(tutte, columns=["giorno", "open", "close", "quote_volume"]).drop_duplicates("giorno").sort_values("giorno").to_csv(f, index=False)
        return s, "ok" if errori == 0 else f"ok con {errori} mesi in errore"
    stati = {}
    with ThreadPoolExecutor(max_workers=16) as ex:
        for k, (s, st) in enumerate(ex.map(una, coppie), 1):
            stati[s] = st
            if k % 50 == 0:
                log(f"[trentanovesima] scaricate {k}/{len(coppie)}")
    return stati


def coppie_dell_universo(pan: dict, ps: dict) -> list:
    dentro = (ps["U"]).any(axis=0)
    return sorted({cc.pronti(s) for s, c in zip(pan["simboli"], dentro) if c})


def volumi_pronti(coppie: list, t0: int, n: int) -> np.ndarray:
    V = np.full((n, len(coppie)), np.nan)
    for j, s in enumerate(coppie):
        f = DATI / f"{s}.csv.gz"
        if not f.exists():
            continue
        d = pd.read_csv(f)
        if d.empty:
            continue
        k = d["giorno"].to_numpy() - t0
        ok = (k >= 0) & (k < n)
        V[k[ok], j] = d["quote_volume"].to_numpy()[ok]
    return V


def esegui(log=print) -> dict:
    pan = sc.pannello()
    ps = te.pannello_settimane(pan, log=lambda x: None, indicatori_si=False)
    simboli = pan["simboli"]
    coppie = coppie_dell_universo(pan, ps)
    log(f"[trentanovesima] {len(coppie)} coppie a pronti per le monete dell'universo")
    stati = scarica(coppie, log)
    RIS.mkdir(exist_ok=True)
    (RIS / "stato_scarico.json").write_text(json.dumps(stati, ensure_ascii=False, indent=1))
    n = pan["close"].shape[0]
    Vs = volumi_pronti(coppie, pan["t0"], n)
    impronta = hashlib.sha256(np.nan_to_num(Vs, nan=-1.0).tobytes()).hexdigest()
    pos = {c: k for k, c in enumerate(coppie)}
    Vs_pan = np.full((n, len(simboli)), np.nan)
    for j, s in enumerate(simboli):
        k = pos.get(cc.pronti(s))
        if k is not None:
            Vs_pan[:, j] = Vs[:, k]
    Vp = np.nan_to_num(pan["quote_volume"])
    lun = ps["lunedi"] - pan["t0"]
    seg = np.full((len(lun), len(simboli)), np.nan)
    for w, m in enumerate(lun):
        a, b = m - 7, m
        if a < 0:
            continue
        sp = Vs_pan[a:b]
        ok = np.isfinite(sp).all(axis=0) & (np.nan_to_num(sp).sum(axis=0) > 0) & (Vp[a:b].sum(axis=0) > 0)
        with np.errstate(all="ignore"):
            r = np.log(Vp[a:b].sum(axis=0) / np.nan_to_num(sp).sum(axis=0))
        seg[w] = np.where(ok, r, np.nan)
    U = ps["U"] & np.isfinite(seg)
    sig = ot.sigma_30(pan, lun)
    costo = sc.costi_moneta(simboli)
    W = vq.pesi_banda(np.where(np.isfinite(sig), -seg, np.nan), U, sig)          # -segnale: long il meno speculativo, short il piu'
    rng = np.random.default_rng(SEME)
    mesc = seg.copy()
    for w in range(mesc.shape[0]):
        idx = np.flatnonzero(U[w])
        if len(idx) > 1:
            mesc[w, idx] = rng.permutation(mesc[w, idx])
    Wm = vq.pesi_banda(np.where(np.isfinite(sig), -mesc, np.nan), U, sig)
    conti = {}
    for nome, Wx in (("VS", W), ("VS mescolato", Wm)):
        d = te.conto(Wx, ps["R"], ps["F"], costo)
        d.index = ps["lunedi"]
        conti[nome] = d
        d.to_csv(RIS / f"settimane_{nome.replace(' ', '_')}.csv.gz")
    btc = pd.Series(ps["R"][:, simboli.index("BTCUSDT")], index=ps["lunedi"])
    out = {nm: te.esame(d, btc, inizio=se.INIZIO, anni_pieni=se.ANNI_PIENI) for nm, d in conti.items()}
    dentro = ps["lunedi"] >= se.INIZIO
    ammessi = U.sum(axis=1)[dentro]
    f7 = se.funding_7(pan, lun)
    Cl = pan["close"]
    r7 = np.full_like(seg, np.nan)
    for w, m in enumerate(lun):
        if m - 8 >= 0:
            with np.errstate(all="ignore"):
                r7[w] = Cl[m - 1] / Cl[m - 8] - 1
    rango = lambda v: pd.Series(v).rank().to_numpy()  # noqa: E731
    x = seg[U]
    okf = np.isfinite(x) & np.isfinite(f7[U])
    okr = np.isfinite(x) & np.isfinite(r7[U])
    out["descrittivo"] = {"coppie": len(coppie), "con_dati": int(sum(1 for v in stati.values() if v.startswith("ok"))),
                          "ammessi_medi": float(ammessi.mean()), "ammessi_min": int(ammessi.min()), "ammessi_max": int(ammessi.max()),
                          "settimane_ferme": int((W[dentro] == 0).all(axis=1).sum()), "settimane": int(dentro.sum()),
                          "correlazione_con_funding_7": float(np.corrcoef(rango(x[okf]), rango(f7[U][okf]))[0, 1]),
                          "correlazione_con_rendimento_7_prima": float(np.corrcoef(rango(x[okr]), rango(r7[U][okr]))[0, 1]),
                          "rapporto_mediano": float(np.exp(np.nanmedian(seg[U]))), "impronta": impronta}
    serie = {**ast.serie_nuove(), "101 VS": conti["VS"]["netto"]}
    rivisto = ast.corretto_rivisto(serie, {"101 VS": out["VS"]["intero"]})
    r = rivisto["candidate"]["101 VS"]
    e = out["VS"]
    e["sharpe_corretto"], e["t"], e["gruppi"] = r["corretto_con_aggiunta"], r["t"], rivisto["gruppi"]
    e["esito"] = te.esito(e, e["sharpe_corretto"])
    e["regola_del_proprietario"] = bool(e["sharpe_corretto"] >= 0.90 and all(v > 0 for v in e["per_anno"].values()) and e["t"] > 3)
    (RIS / "esame.json").write_text(json.dumps(out, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    de = out["descrittivo"]
    pc = lambda v: f"{100 * v:+.1f}%"  # noqa: E731
    righe = ["# Programma 7 — risultati della trentanovesima prova (VS: il volume del perpetuo su quello a pronti)", "",
             "Regole in `TRENTANOVESIMA.md` (scritte prima). Dal 4 gennaio 2021 al 5 ottobre 2026, a settimana.", "",
             "| | Sharpe | l'anno | volatilità | discesa | spese l'anno | long l'anno | short l'anno | per anno |", "|---|---|---|---|---|---|---|---|---|"]
    for nm in ("VS", "VS mescolato"):
        i = out[nm]["intero"]
        righe.append(f"| {nm} | {i['sharpe']:.2f} | {pc(i['annuo'])} | {100 * i['volatilita']:.1f}% | {100 * i['discesa_max']:.1f}% | "
                     f"{100 * out[nm]['spese_annue']:.1f}% | {pc(out[nm]['long_annuo'])} | {pc(out[nm]['short_annuo'])} | "
                     + ", ".join(f"{y} {pc(v)}" for y, v in out[nm]["per_anno"].items()) + " |")
    b = e["boot"]
    righe += ["",
              f"* {de['coppie']} coppie a pronti per le monete dell'universo ({de['con_dati']} con i dati); ammesse per settimana in media {de['ammessi_medi']:.0f} "
              f"(da {de['ammessi_min']} a {de['ammessi_max']}); settimane ferme {de['settimane_ferme']} su {de['settimane']}; rapporto mediano perpetuo/pronti "
              f"{de['rapporto_mediano']:.1f}.",
              f"* Netto medio a settimana {100 * b['media']:+.2f}% (intervallo {100 * b['basso']:+.2f}; {100 * b['alto']:+.2f}, p {b['p']:.3f}); a costi doppi "
              f"{100 * e['costi_doppi']:+.2f}%; oltre il Bitcoin {pc(e['extra_btc_annuo'])} l'anno, beta {e['beta_btc']:.2f}.",
              f"* Correlazione (per ranghi) del segnale con il funding dei 7 giorni {de['correlazione_con_funding_7']:.2f}, con il rendimento dei 7 giorni prima "
              f"{de['correlazione_con_rendimento_7_prima']:.2f}.",
              f"* **VS**: Sharpe corretto {e['sharpe_corretto']:.2f} ({e['gruppi']} gruppi), t {e['t']:.2f}; esito {e['esito']}; regola del proprietario: "
              f"{'sì' if e['regola_del_proprietario'] else 'no'}.", f"* Impronta dei volumi scaricati: `{de['impronta'][:16]}`."]
    testo = "\n".join(righe) + "\n"
    (QUI / "RISULTATI_TRENTANOVESIMA.md").write_text(testo, encoding="utf-8")
    log(testo)
    return out


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "scarica":
        pan = sc.pannello()
        ps = te.pannello_settimane(pan, log=lambda x: None, indicatori_si=False)
        coppie = coppie_dell_universo(pan, ps)
        print(f"[trentanovesima] {len(coppie)} coppie da scaricare", flush=True)
        scarica(coppie, log=lambda x: print(x, flush=True))
        print("SCARICO FINITO", flush=True)
    else:
        esegui(log=lambda x: print(x, flush=True))
        print("TRENTANOVESIMA FINITA", flush=True)
