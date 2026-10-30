"""Programma 7, settantatreesima prova (SETTANTATREESIMA.md): HL, il funding di Hyperliquid contro quello di Binance, deciso ogni giorno
come G1: short il quinto con lo scarto dei 7 giorni piu' alto, long il piu' basso; deve battere G1 sulle stesse monete.

Uso: python3 -m research.programma7.settantatreesima
"""
from __future__ import annotations

import json
import time
import urllib.request
from pathlib import Path

import numpy as np
import pandas as pd

from research.programma6 import asticella as ast
from research.programma6 import ottava as ot
from research.programma6 import seconda as sc
from research.programma6 import sesta as se
from research.programma6 import terza as te
from research.programma6 import ventiquattresima as vq
from research.programma7 import cinquantaduesima as kp
from research.programma7 import prima as g1
from research.programma7 import settantesima as fm

QUI = Path(__file__).parent
RIS = QUI / "risultati_settantatreesima"
DATI = QUI.parent / "data" / "hyperliquid"
API = "https://api.hyperliquid.xyz/info"
DAL = sc.giorno(2023, 6, 5)
INIZIO_MS = 1_680_000_000_000            # aprile 2023, prima dell'inizio dello storico


def _post(corpo: dict):
    for k in range(5):
        try:
            r = urllib.request.Request(API, data=json.dumps(corpo).encode(), headers={"Content-Type": "application/json",
                                                                                      "User-Agent": "ricerca/1.0"})
            with urllib.request.urlopen(r, timeout=60) as x:
                return json.load(x)
        except Exception:  # noqa: BLE001
            time.sleep(2 ** (k + 1))
    return None


def storico(moneta: str) -> list:
    f = DATI / f"{moneta}.json"
    if f.exists():
        return json.loads(f.read_text())
    out, t = [], INIZIO_MS
    while True:
        d = _post({"type": "fundingHistory", "coin": moneta, "startTime": t})
        if not d:
            break
        out += [(int(x["time"]), float(x["fundingRate"])) for x in d]
        if len(d) < 500:
            break
        t = int(d[-1]["time"]) + 1
        time.sleep(0.3)
    DATI.mkdir(parents=True, exist_ok=True)
    f.write_text(json.dumps(out))
    return out


def funding_hl(pan: dict, log=print) -> tuple:
    simboli, t0 = pan["simboli"], pan["t0"]
    T = pan["close"].shape[0]
    meta = _post({"type": "meta"})
    nomi = [x["name"] for x in meta["universe"]]
    Fh = np.full((T, len(simboli)), np.nan)
    abbinati = {}
    for n in nomi:
        base = n[1:] if n.startswith("k") and n[1:].isupper() else n
        cand = (f"1000{base}USDT",) if n.startswith("k") and n[1:].isupper() else (f"{base}USDT", f"1000{base}USDT")
        s = next((p for p in cand if p in simboli), None)
        if not s or s in abbinati.values():
            continue
        righe = storico(n)
        if not righe:
            continue
        df = pd.DataFrame(righe, columns=["ts", "tasso"]).drop_duplicates("ts")
        tenuta = (df["ts"].to_numpy() // 60_000 - 1) // 1440
        g = pd.Series(df["tasso"].to_numpy(float), index=tenuta).groupby(level=0).sum()
        g = g[(g.index >= t0) & (g.index < t0 + T)]
        Fh[g.index.to_numpy() - t0, simboli.index(s)] = g.to_numpy()
        abbinati[n] = s
    log(f"[settantatreesima] {len(nomi)} monete su Hyperliquid oggi, abbinate a Binance {len(abbinati)}")
    return Fh, abbinati


def esegui(log=print) -> dict:
    pan = sc.pannello()
    ps = te.pannello_settimane(pan, log=lambda x: None, indicatori_si=False)
    Fh, abbinati = funding_hl(pan, log)
    giorni = np.arange(DAL, g1.FINE, dtype=np.int64)
    idx = giorni - pan["t0"]
    Ud = g1.universo_del_giorno(giorni, ps["lunedi"], ps["U"])
    sig = ot.sigma_30(pan, idx)
    fb = se.funding_7(pan, idx)
    fh = fm.somma_7(Fh, idx)
    scarto = np.round(fh - fb, 12)
    Ur = Ud & np.isfinite(scarto)
    R = sc.rendimenti(pan)[idx]
    F = np.nan_to_num(pan["funding"][idx])
    costo = sc.costi_moneta(pan["simboli"])
    btc = pd.Series(ps["R"][:, ps["simboli"].index("BTCUSDT")], index=ps["lunedi"])
    rango = lambda M: pd.DataFrame(np.where(Ur, M, np.nan)).rank(axis=1, pct=True).to_numpy()  # noqa: E731
    varianti = {"HL": -scarto, "G1 sulle stesse monete": -fb, "media dei ranghi": -(rango(fb) + rango(scarto)) / 2}
    out, sett = {}, {}
    RIS.mkdir(exist_ok=True)
    for nome, ct in varianti.items():
        W = vq.pesi_banda(np.where(np.isfinite(sig) & Ur, ct, np.nan), Ur, sig)
        lim, ordini = kp.conto(W, R, F, costo, giorni, pan["simboli"])
        s = g1.per_settimana(lim, giorni)
        s.to_csv(RIS / f"settimane_{nome.replace(' ', '_')}.csv.gz")
        e = te.esame(s, btc, inizio=DAL, anni_pieni=(2024, 2025))
        e["ordini"], e["movimenti"] = ordini, g1.movimenti(W)
        e["giorni_con_posizioni"] = int((np.abs(W).sum(axis=1) > 0).sum())
        out[nome], sett[nome] = e, s
    e = out["HL"]
    rivisto = ast.corretto_rivisto({**ast.serie_nuove(), "135 HL": sett["HL"]["netto"]}, {"135 HL": e["intero"]})
    r = rivisto["candidate"]["135 HL"]
    e["sharpe_corretto"], e["t"], e["gruppi"] = r["corretto_con_aggiunta"], r["t"], rivisto["gruppi"]
    e["esito_scritto"] = te.esito(e, e["sharpe_corretto"])
    e["sopra_G1_stesse_monete"] = bool(e["intero"]["sharpe"] > out["G1 sulle stesse monete"]["intero"]["sharpe"])
    e["esito"] = (e["esito_scritto"] if e["esito_scritto"] != "VALIDA" else
                  "VALIDA" if e["sopra_G1_stesse_monete"] else "non sopra G1 sulle stesse monete")
    anni = e.get("per_anno", {})
    e["regola_proprietario"] = bool(e["sharpe_corretto"] >= 0.90 and e["t"] > 3 and anni and all(v > 0 for v in anni.values()))
    g1s = pd.read_csv(QUI / "risultati_prima" / "settimane_G1.csv.gz", index_col=0)
    c = sett["HL"].index.intersection(g1s.index)
    e["correlazione_G1"] = float(np.corrcoef(sett["HL"].loc[c, "netto"], g1s.loc[c, "netto"])[0, 1])
    e["monete_con_segnale_mediana"] = float(np.median(Ur.sum(axis=1)))
    cc = [np.corrcoef(fb[k, Ur[k]], scarto[k, Ur[k]])[0, 1] for k in range(len(giorni)) if Ur[k].sum() >= 10]
    e["correlazione_scarto_funding_mediana"] = float(np.nanmedian(cc)) if cc else None
    e["scarto_medio_annuo"] = float(np.nanmean(np.where(Ur, scarto, np.nan)) * 365 / 7)
    (RIS / "esame.json").write_text(json.dumps({"abbinati": abbinati, **out}, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    pc = lambda v: f"{100 * v:+.1f}%"  # noqa: E731
    i = e["intero"]
    altre = "; ".join(f"{n}: Sharpe {out[n]['intero']['sharpe']:.2f}, {pc(out[n]['intero']['annuo'])} l'anno, discesa "
                      f"{100 * out[n]['intero']['discesa_max']:.1f}%" for n in varianti if n != "HL")
    testo = "\n".join([
        "# Programma 7 — risultati della settantatreesima prova (HL: il funding di Hyperliquid contro quello di Binance, ogni giorno)", "",
        "Regole in `SETTANTATREESIMA.md` (scritte prima). Dal 5 giugno 2023 al 5 ottobre 2026, universo di G1 ristretto alle monete "
        "quotate oggi anche su Hyperliquid, ordini limite.", "",
        f"* {len(abbinati)} monete abbinate; monete con il segnale ogni giorno, mediana {e['monete_con_segnale_mediana']:.0f}; giorni con le "
        f"posizioni {e['giorni_con_posizioni']} su {len(giorni)} (almeno 20 monete).",
        f"* Lo scarto medio fra il funding di Hyperliquid e quello di Binance: {pc(e['scarto_medio_annuo'])} l'anno; correlazione con il "
        f"funding di Binance fra le monete dello stesso giorno, mediana {e['correlazione_scarto_funding_mediana']:.2f}.",
        f"* **HL: Sharpe {i['sharpe']:.2f}**, {pc(i['annuo'])} l'anno, volatilità {100 * i['volatilita']:.1f}%, discesa "
        f"{100 * i['discesa_max']:.1f}%; spese {100 * e['spese_annue']:.1f}% l'anno; lato long {pc(e['long_annuo'])}, short "
        f"{pc(e['short_annuo'])} l'anno.",
        "* Per anno: " + ", ".join(f"{a} {pc(v)}" for a, v in e["per_anno"].items()) + ".",
        f"* Per confronto: {altre}.",
        f"* Correlazione con G1: {e['correlazione_G1']:.2f}.",
        f"* Sharpe corretto con l'aggiunta {e['sharpe_corretto']:.2f} ({e['gruppi']} gruppi); t {e['t']:.2f}; sopra G1 sulle stesse monete: "
        f"{'sì' if e['sopra_G1_stesse_monete'] else 'no'}; regola del proprietario: {'sì' if e['regola_proprietario'] else 'no'}.", "",
        f"**Esito: {e['esito']}**"]) + "\n"
    (QUI / "RISULTATI_SETTANTATREESIMA.md").write_text(testo, encoding="utf-8")
    log(testo)
    return out


if __name__ == "__main__":
    esegui(log=lambda x: print(x, flush=True))
    print("SETTANTATREESIMA FINITA", flush=True)
