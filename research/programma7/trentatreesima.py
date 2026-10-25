"""Programma 7, trentatreesima prova (TRENTATREESIMA.md): CF, l'uso vero delle catene (le commissioni giornaliere pagate dagli utenti,
DefiLlama) dei 7 giorni rispetto ai 90 prima, come segnale fra i gettoni delle catene con il perpetuo su Binance; banda 20/40 come F5.

Uso: python3 -m research.programma7.trentatreesima
"""
from __future__ import annotations

import hashlib
import json
import time
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

QUI = Path(__file__).parent
RIS = QUI / "risultati_trentatreesima"
DATI = QUI.parent / "data" / "llama_fees"
CATENE = "https://api.llama.fi/v2/chains"
COMMISSIONI = "https://api.llama.fi/overview/fees/{}?excludeTotalDataChart=false&excludeTotalDataChartBreakdown=true&dataType=dailyFees"
INIZIO = sc.giorno(2022, 5, 2)
FINE = sc.giorno(2026, 10, 5)
GIORNI_SEGNALE, GIORNI_BASE, MIN_PRESENTI = 7, 90, 80
SEME = 2026


def _get(url: str, prove: int = 4):
    for k in range(prove):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "ricerca/1.0"})
            with urllib.request.urlopen(req, timeout=120) as r:
                return json.load(r)
        except Exception as e:  # noqa: BLE001
            if k == prove - 1:
                raise
            time.sleep(2 ** k)


def base_del_perpetuo(simbolo: str) -> str:
    b = simbolo[:-4]
    for pre in ("1000000", "1000", "1M"):
        if b.startswith(pre):
            b = b[len(pre):]
    return b.upper()


def scarica(simboli: list, log=print) -> list:
    """Scarica le catene con il gettone fra i perpetui e le loro commissioni giornaliere; salva in DATI. Ritorna l'elenco [(catena, gettone)]."""
    DATI.mkdir(parents=True, exist_ok=True)
    catene = _get(CATENE)
    (DATI / "chains.json").write_text(json.dumps(catene))
    basi = {base_del_perpetuo(s) for s in simboli}
    scelte = [(c["name"], c["tokenSymbol"].upper()) for c in catene if c.get("tokenSymbol") and c["tokenSymbol"].upper() in basi]
    log(f"[trentatreesima] {len(scelte)} catene con il gettone fra i perpetui; scarico le commissioni")

    def una(x):
        nome, _ = x
        f = DATI / (nome.replace("/", "_") + ".json")
        if f.exists():
            return nome, True
        try:
            d = _get(COMMISSIONI.format(urllib.request.quote(nome)))
            f.write_text(json.dumps({"catena": nome, "totale": d.get("totalAllTime"), "serie": d.get("totalDataChart") or []}))
            return nome, True
        except Exception as e:  # noqa: BLE001
            log(f"[trentatreesima] {nome}: {type(e).__name__} {str(e)[:60]}")
            return nome, False
    with ThreadPoolExecutor(max_workers=6) as ex:
        esiti = dict(ex.map(una, scelte))
    log(f"[trentatreesima] scaricate {sum(esiti.values())} su {len(scelte)}")
    return [x for x in scelte if esiti.get(x[0])]


def tabella(scelte: list, t0: int, n_giorni: int) -> tuple:
    """Commissioni giornaliere (giorni del pannello × gettoni); con due catene per gettone si tiene la storia piu' lunga (poi il totale)."""
    per_gettone = {}
    for nome, gettone in scelte:
        f = DATI / (nome.replace("/", "_") + ".json")
        if not f.exists():
            continue
        d = json.loads(f.read_text())
        serie = d["serie"]
        if not serie:
            continue
        chiave = (len(serie), float(d.get("totale") or 0))
        if gettone not in per_gettone or chiave > per_gettone[gettone][0]:
            per_gettone[gettone] = (chiave, nome, serie)
    out = {}
    for gettone, (_, nome, serie) in per_gettone.items():
        col = np.full(n_giorni, np.nan)
        for ts, v in serie:
            k = int(ts) // 86400 - t0
            if 0 <= k < n_giorni and v is not None:
                col[k] = float(v)
        out[gettone] = col
    return pd.DataFrame(out), {g: n for g, (_, n, _) in per_gettone.items()}


def segnale(comm: pd.DataFrame, lun_idx: np.ndarray) -> np.ndarray:
    """Per ogni lunedi' (indice del pannello) e gettone: somma dei 7 giorni fino alla domenica / (media dei 90 giorni prima × 7); NaN se
    mancano piu' di 10 dei 90 giorni o la media non e' sopra zero."""
    C = comm.to_numpy()
    out = np.full((len(lun_idx), C.shape[1]), np.nan)
    for w, m in enumerate(lun_idx):
        a, b = m - GIORNI_SEGNALE, m            # i 7 giorni: [m-7, m)
        a0 = a - GIORNI_BASE                    # i 90 prima: [m-97, m-7)
        if a0 < 0:
            continue
        sett, base = C[a:b], C[a0:a]
        n_ok = np.isfinite(base).sum(axis=0)
        with np.errstate(all="ignore"):
            media = np.nanmean(np.where(np.isfinite(base), base, np.nan), axis=0)
            somma = np.nansum(np.where(np.isfinite(sett), sett, 0.0), axis=0)
            r = somma / (media * GIORNI_SEGNALE)
        ok = (n_ok >= MIN_PRESENTI) & np.isfinite(media) & (media > 0) & (np.isfinite(sett).sum(axis=0) >= GIORNI_SEGNALE - 2)
        out[w] = np.where(ok, r, np.nan)
    return out


def esegui(log=print) -> dict:
    pan = sc.pannello()
    ps = te.pannello_settimane(pan, log=lambda x: None, indicatori_si=False)
    scelte = scarica(pan["simboli"], log)
    comm, catena_di = tabella(scelte, pan["t0"], pan["close"].shape[0])
    impronta = hashlib.sha256(pd.util.hash_pandas_object(comm.fillna(-1.0), index=False).to_numpy().tobytes()).hexdigest()
    RIS.mkdir(exist_ok=True)
    comm.index = np.arange(pan["close"].shape[0]) + pan["t0"]
    comm.to_csv(RIS / "commissioni_giorni.csv.gz")
    log(f"[trentatreesima] tabella: {comm.shape[1]} gettoni, impronta {impronta[:16]}")
    # colonne nell'ordine del pannello
    simboli = pan["simboli"]
    S = len(simboli)
    basi = [base_del_perpetuo(s) for s in simboli]
    pos = {}
    for j, b in enumerate(basi):
        if b in comm.columns and b not in pos:          # un gettone → il primo perpetuo con quella base
            pos[b] = j
    C_pan = np.full((comm.shape[0], S), np.nan)
    for b, j in pos.items():
        C_pan[:, j] = comm[b].to_numpy()
    comm_pan = pd.DataFrame(C_pan)
    dentro = (ps["lunedi"] >= INIZIO) & (ps["lunedi"] <= FINE)
    lun_idx = ps["lunedi"] - pan["t0"]
    sig_comm = segnale(comm_pan, lun_idx)
    V = pan["quote_volume"]
    vol_ok = np.zeros_like(sig_comm, dtype=bool)
    for w, m in enumerate(lun_idx):
        if 1 <= m < V.shape[0]:
            vol_ok[w] = np.nan_to_num(V[m - 1]) > 0
    U = np.isfinite(sig_comm) & vol_ok
    U[~dentro] = False
    sig = ot.sigma_30(pan, lun_idx)
    costo = sc.costi_moneta(simboli)
    W = vq.pesi_banda(np.where(np.isfinite(sig), sig_comm, np.nan), U, sig)
    rng = np.random.default_rng(SEME)
    mesc = sig_comm.copy()
    for w in range(mesc.shape[0]):
        idx = np.flatnonzero(U[w])
        if len(idx) > 1:
            mesc[w, idx] = rng.permutation(mesc[w, idx])
    Wm = vq.pesi_banda(np.where(np.isfinite(sig), mesc, np.nan), U, sig)
    conti = {}
    for nome, Wx in (("CF", W), ("CF mescolato", Wm)):
        d = te.conto(Wx, ps["R"], ps["F"], costo)
        d.index = ps["lunedi"]
        conti[nome] = d
        d.to_csv(RIS / f"settimane_{nome.replace(' ', '_')}.csv.gz")
    btc = pd.Series(ps["R"][:, simboli.index("BTCUSDT")], index=ps["lunedi"])
    out = {n: te.esame(d, btc, inizio=INIZIO, anni_pieni=(2023, 2024, 2025)) for n, d in conti.items()}
    # descrittivo
    ammessi = U.sum(axis=1)[dentro]
    r7 = np.full_like(sig_comm, np.nan)
    Cl = pan["close"]
    for w, m in enumerate(lun_idx):
        if m - 8 >= 0 and m - 1 < Cl.shape[0]:
            with np.errstate(all="ignore"):
                r7[w] = Cl[m - 1] / Cl[m - 8] - 1
    x, y = sig_comm[U], r7[U]
    ok = np.isfinite(x) & np.isfinite(y)
    rango = lambda v: pd.Series(v).rank().to_numpy()  # noqa: E731
    out["descrittivo"] = {"gettoni_abbinati": int(comm.shape[1]), "ammessi_medi_per_settimana": float(ammessi.mean()),
                          "ammessi_min": int(ammessi.min()), "ammessi_max": int(ammessi.max()),
                          "settimane_ferme": int((W[dentro] == 0).all(axis=1).sum()), "settimane": int(dentro.sum()),
                          "correlazione_segnale_rendimento_7_giorni_prima": float(np.corrcoef(rango(x[ok]), rango(y[ok]))[0, 1]),
                          "catena_per_gettone": catena_di, "impronta_commissioni": impronta}
    serie = {**ast.serie_nuove(), "95 CF": conti["CF"]["netto"]}
    rivisto = ast.corretto_rivisto(serie, {"95 CF": out["CF"]["intero"]})
    r = rivisto["candidate"]["95 CF"]
    out["CF"]["sharpe_corretto"], out["CF"]["t"], out["CF"]["gruppi"] = r["corretto_con_aggiunta"], r["t"], rivisto["gruppi"]
    out["CF"]["esito"] = te.esito(out["CF"], out["CF"]["sharpe_corretto"])
    out["CF"]["regola_del_proprietario"] = bool(out["CF"]["sharpe_corretto"] >= 0.90 and all(v > 0 for v in out["CF"]["per_anno"].values())
                                               and out["CF"]["t"] > 3)
    (RIS / "esame.json").write_text(json.dumps(out, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    de = out["descrittivo"]
    pc = lambda v: f"{100 * v:+.1f}%"  # noqa: E731
    righe = ["# Programma 7 — risultati della trentatreesima prova (CF: l'uso vero delle catene fra i gettoni delle catene)", "",
             "Regole in `TRENTATREESIMA.md` (scritte prima). Dal 2 maggio 2022 al 5 ottobre 2026, a settimana.", "",
             "| | Sharpe | l'anno | volatilità | discesa | spese l'anno | long l'anno | short l'anno | per anno |", "|---|---|---|---|---|---|---|---|---|"]
    for n in ("CF", "CF mescolato"):
        i = out[n]["intero"]
        righe.append(f"| {n} | {i['sharpe']:.2f} | {pc(i['annuo'])} | {100 * i['volatilita']:.1f}% | {100 * i['discesa_max']:.1f}% | "
                     f"{100 * out[n]['spese_annue']:.1f}% | {pc(out[n]['long_annuo'])} | {pc(out[n]['short_annuo'])} | "
                     + ", ".join(f"{y} {pc(v)}" for y, v in out[n]["per_anno"].items()) + " |")
    b = out["CF"]["boot"]
    righe += ["",
              f"* {de['gettoni_abbinati']} gettoni con la catena su DefiLlama; ammessi per settimana in media {de['ammessi_medi_per_settimana']:.0f} "
              f"(da {de['ammessi_min']} a {de['ammessi_max']}); settimane ferme {de['settimane_ferme']} su {de['settimane']}.",
              f"* Netto medio a settimana {100 * b['media']:+.2f}% (intervallo {100 * b['basso']:+.2f}; {100 * b['alto']:+.2f}, p {b['p']:.3f}); a costi doppi "
              f"{100 * out['CF']['costi_doppi']:+.2f}%; oltre il Bitcoin {pc(out['CF']['extra_btc_annuo'])} l'anno, beta {out['CF']['beta_btc']:.2f}.",
              f"* Correlazione (per ranghi) fra il segnale e il rendimento dei 7 giorni prima del gettone: {de['correlazione_segnale_rendimento_7_giorni_prima']:.2f}.",
              f"* **CF**: Sharpe corretto {out['CF']['sharpe_corretto']:.2f} ({out['CF']['gruppi']} gruppi), t {out['CF']['t']:.2f}; esito {out['CF']['esito']}; "
              f"regola del proprietario: {'sì' if out['CF']['regola_del_proprietario'] else 'no'}.",
              f"* Impronta delle commissioni scaricate: `{de['impronta_commissioni'][:16]}`."]
    testo = "\n".join(righe) + "\n"
    (QUI / "RISULTATI_TRENTATREESIMA.md").write_text(testo, encoding="utf-8")
    log(testo)
    return out


if __name__ == "__main__":
    esegui(log=lambda x: print(x, flush=True))
    print("TRENTATREESIMA FINITA", flush=True)
