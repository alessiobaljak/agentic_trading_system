"""Programma 7, trentottesima prova (TRENTOTTESIMA.md): SC, le stablecoin che entrano nelle catene (DefiLlama): la crescita a 30 giorni del
totale in dollari delle stablecoin sulla catena come segnale fra i gettoni delle catene con il perpetuo; banda 20/40 come F5.

Uso: python3 -m research.programma7.trentottesima
"""
from __future__ import annotations

import hashlib
import json
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np
import pandas as pd

from research.programma6 import asticella as ast
from research.programma6 import ottava as ot
from research.programma6 import seconda as sc
from research.programma6 import terza as te
from research.programma6 import ventiquattresima as vq
from research.programma7 import trentatreesima as cf

QUI = Path(__file__).parent
RIS = QUI / "risultati_trentottesima"
DATI = QUI.parent / "data" / "llama_stable"
URL = "https://stablecoins.llama.fi/stablecoincharts/{}"
INIZIO = sc.giorno(2022, 1, 3)
FINE = sc.giorno(2026, 10, 5)
GIORNI = 30
MINIMO_USD = 10_000_000
SEME = 2026


def scarica(scelte: list, log=print) -> dict:
    DATI.mkdir(parents=True, exist_ok=True)

    def una(x):
        nome, _ = x
        f = DATI / (nome.replace("/", "_") + ".json")
        if f.exists():
            return nome, True
        try:
            d = cf._get(URL.format(urllib.request.quote(nome)))
            serie = [(int(p["date"]), float((p.get("totalCirculatingUSD") or {}).get("peggedUSD", float("nan")))) for p in d] if isinstance(d, list) else []
            f.write_text(json.dumps({"catena": nome, "serie": serie}))
            return nome, True
        except Exception as e:  # noqa: BLE001
            log(f"[trentottesima] {nome}: {type(e).__name__} {str(e)[:60]}")
            return nome, False
    with ThreadPoolExecutor(max_workers=6) as ex:
        esiti = dict(ex.map(una, scelte))
    log(f"[trentottesima] scaricate {sum(esiti.values())} su {len(scelte)}")
    return esiti


def tabella(scelte: list, t0: int, n: int) -> tuple:
    per_gettone = {}
    for nome, gettone in scelte:
        f = DATI / (nome.replace("/", "_") + ".json")
        if not f.exists():
            continue
        serie = [(ts, v) for ts, v in json.loads(f.read_text())["serie"] if v == v and v > 0]
        if not serie:
            continue
        chiave = (len(serie), serie[-1][1])
        if gettone not in per_gettone or chiave > per_gettone[gettone][0]:
            per_gettone[gettone] = (chiave, nome, serie)
    out = {}
    for gettone, (_, nome, serie) in per_gettone.items():
        col = np.full(n, np.nan)
        for ts, v in serie:
            k = ts // 86400 - t0
            if 0 <= k < n:
                col[k] = v
        out[gettone] = col
    return pd.DataFrame(out), {g: nm for g, (_, nm, _) in per_gettone.items()}


def segnale(S: np.ndarray, lun_idx: np.ndarray) -> np.ndarray:
    """log(totale della domenica / totale di 30 giorni prima); NaN se manca uno dei due o il totale di 30 giorni prima e' sotto il minimo."""
    out = np.full((len(lun_idx), S.shape[1]), np.nan)
    for w, m in enumerate(lun_idx):
        a, b = m - 1 - GIORNI, m - 1
        if a < 0 or b >= S.shape[0]:
            continue
        with np.errstate(all="ignore"):
            r = np.log(S[b] / S[a])
        ok = np.isfinite(S[a]) & np.isfinite(S[b]) & (S[a] >= MINIMO_USD) & np.isfinite(r)
        out[w] = np.where(ok, r, np.nan)
    return out


def esegui(log=print) -> dict:
    pan = sc.pannello()
    ps = te.pannello_settimane(pan, log=lambda x: None, indicatori_si=False)
    simboli = pan["simboli"]
    catene = json.loads((cf.DATI / "chains.json").read_text())
    basi = {cf.base_del_perpetuo(s) for s in simboli}
    scelte = [(c["name"], c["tokenSymbol"].upper()) for c in catene if c.get("tokenSymbol") and c["tokenSymbol"].upper() in basi]
    log(f"[trentottesima] {len(scelte)} catene con il gettone fra i perpetui; scarico le stablecoin")
    scarica(scelte, log)
    stab, catena_di = tabella(scelte, pan["t0"], pan["close"].shape[0])
    impronta = hashlib.sha256(pd.util.hash_pandas_object(stab.fillna(-1.0), index=False).to_numpy().tobytes()).hexdigest()
    RIS.mkdir(exist_ok=True)
    stab_out = stab.copy()
    stab_out.index = np.arange(pan["close"].shape[0]) + pan["t0"]
    stab_out.to_csv(RIS / "stablecoin_giorni.csv.gz")
    log(f"[trentottesima] tabella: {stab.shape[1]} gettoni con le stablecoin, impronta {impronta[:16]}")
    S_pan = np.full((stab.shape[0], len(simboli)), np.nan)
    pos = {}
    for j, s in enumerate(simboli):
        b = cf.base_del_perpetuo(s)
        if b in stab.columns and b not in pos:
            pos[b] = j
            S_pan[:, j] = stab[b].to_numpy()
    lun_idx = ps["lunedi"] - pan["t0"]
    dentro = (ps["lunedi"] >= INIZIO) & (ps["lunedi"] <= FINE)
    sig_s = segnale(S_pan, lun_idx)
    V = pan["quote_volume"]
    vol_ok = np.zeros_like(sig_s, dtype=bool)
    for w, m in enumerate(lun_idx):
        if 1 <= m < V.shape[0]:
            vol_ok[w] = np.nan_to_num(V[m - 1]) > 0
    U = np.isfinite(sig_s) & vol_ok
    U[~dentro] = False
    sig = ot.sigma_30(pan, lun_idx)
    costo = sc.costi_moneta(simboli)
    W = vq.pesi_banda(np.where(np.isfinite(sig), sig_s, np.nan), U, sig)
    rng = np.random.default_rng(SEME)
    mesc = sig_s.copy()
    for w in range(mesc.shape[0]):
        idx = np.flatnonzero(U[w])
        if len(idx) > 1:
            mesc[w, idx] = rng.permutation(mesc[w, idx])
    Wm = vq.pesi_banda(np.where(np.isfinite(sig), mesc, np.nan), U, sig)
    conti = {}
    for nome, Wx in (("SC", W), ("SC mescolato", Wm)):
        d = te.conto(Wx, ps["R"], ps["F"], costo)
        d.index = ps["lunedi"]
        conti[nome] = d
        d.to_csv(RIS / f"settimane_{nome.replace(' ', '_')}.csv.gz")
    btc = pd.Series(ps["R"][:, simboli.index("BTCUSDT")], index=ps["lunedi"])
    out = {n: te.esame(d, btc, inizio=INIZIO, anni_pieni=(2022, 2023, 2024, 2025)) for n, d in conti.items()}
    ammessi = U.sum(axis=1)[dentro]
    r30 = np.full_like(sig_s, np.nan)
    Cl = pan["close"]
    for w, m in enumerate(lun_idx):
        if m - 31 >= 0 and m - 1 < Cl.shape[0]:
            with np.errstate(all="ignore"):
                r30[w] = Cl[m - 1] / Cl[m - 31] - 1
    x, y = sig_s[U], r30[U]
    ok = np.isfinite(x) & np.isfinite(y)
    rango = lambda v: pd.Series(v).rank().to_numpy()  # noqa: E731
    out["descrittivo"] = {"gettoni_con_stablecoin": int(stab.shape[1]), "ammessi_medi": float(ammessi.mean()), "ammessi_min": int(ammessi.min()),
                          "ammessi_max": int(ammessi.max()), "settimane_ferme": int((W[dentro] == 0).all(axis=1).sum()), "settimane": int(dentro.sum()),
                          "correlazione_segnale_rendimento_30_giorni_prima": float(np.corrcoef(rango(x[ok]), rango(y[ok]))[0, 1]),
                          "catena_per_gettone": catena_di, "impronta": impronta}
    serie = {**ast.serie_nuove(), "100 SC": conti["SC"]["netto"]}
    rivisto = ast.corretto_rivisto(serie, {"100 SC": out["SC"]["intero"]})
    r = rivisto["candidate"]["100 SC"]
    e = out["SC"]
    e["sharpe_corretto"], e["t"], e["gruppi"] = r["corretto_con_aggiunta"], r["t"], rivisto["gruppi"]
    e["esito"] = te.esito(e, e["sharpe_corretto"])
    e["regola_del_proprietario"] = bool(e["sharpe_corretto"] >= 0.90 and all(v > 0 for v in e["per_anno"].values()) and e["t"] > 3)
    (RIS / "esame.json").write_text(json.dumps(out, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    de = out["descrittivo"]
    pc = lambda v: f"{100 * v:+.1f}%"  # noqa: E731
    righe = ["# Programma 7 — risultati della trentottesima prova (SC: le stablecoin che entrano nelle catene)", "",
             "Regole in `TRENTOTTESIMA.md` (scritte prima). Dal 3 gennaio 2022 al 5 ottobre 2026, a settimana.", "",
             "| | Sharpe | l'anno | volatilità | discesa | spese l'anno | long l'anno | short l'anno | per anno |", "|---|---|---|---|---|---|---|---|---|"]
    for n in ("SC", "SC mescolato"):
        i = out[n]["intero"]
        righe.append(f"| {n} | {i['sharpe']:.2f} | {pc(i['annuo'])} | {100 * i['volatilita']:.1f}% | {100 * i['discesa_max']:.1f}% | "
                     f"{100 * out[n]['spese_annue']:.1f}% | {pc(out[n]['long_annuo'])} | {pc(out[n]['short_annuo'])} | "
                     + ", ".join(f"{y} {pc(v)}" for y, v in out[n]["per_anno"].items()) + " |")
    b = e["boot"]
    righe += ["",
              f"* {de['gettoni_con_stablecoin']} gettoni con le stablecoin sulla catena; ammessi per settimana in media {de['ammessi_medi']:.0f} "
              f"(da {de['ammessi_min']} a {de['ammessi_max']}); settimane ferme {de['settimane_ferme']} su {de['settimane']}.",
              f"* Netto medio a settimana {100 * b['media']:+.2f}% (intervallo {100 * b['basso']:+.2f}; {100 * b['alto']:+.2f}, p {b['p']:.3f}); a costi doppi "
              f"{100 * e['costi_doppi']:+.2f}%; oltre il Bitcoin {pc(e['extra_btc_annuo'])} l'anno, beta {e['beta_btc']:.2f}.",
              f"* Correlazione (per ranghi) fra il segnale e il rendimento dei 30 giorni prima del gettone: {de['correlazione_segnale_rendimento_30_giorni_prima']:.2f}.",
              f"* **SC**: Sharpe corretto {e['sharpe_corretto']:.2f} ({e['gruppi']} gruppi), t {e['t']:.2f}; esito {e['esito']}; regola del proprietario: "
              f"{'sì' if e['regola_del_proprietario'] else 'no'}.", f"* Impronta dei dati scaricati: `{de['impronta'][:16]}`."]
    testo = "\n".join(righe) + "\n"
    (QUI / "RISULTATI_TRENTOTTESIMA.md").write_text(testo, encoding="utf-8")
    log(testo)
    return out


if __name__ == "__main__":
    esegui(log=lambda x: print(x, flush=True))
    print("TRENTOTTESIMA FINITA", flush=True)
