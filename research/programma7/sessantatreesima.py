"""Programma 7, sessantatreesima prova (SESSANTATREESIMA.md): FG, l'indice di paura e avidita' sul Bitcoin. PA long dalla paura estrema
(indice <= 20) fino a 50; AV short dall'avidita' estrema (>= 80) fino a 50; il valore del giorno d decide il giorno d + 2.

Uso: python3 -m research.programma7.sessantatreesima
"""
from __future__ import annotations

import json
import urllib.request
from pathlib import Path

import numpy as np
import pandas as pd

from research.programma6 import asticella as ast
from research.programma6 import seconda as sc
from research.programma6 import terza as te
from research.programma7 import prima as g1

QUI = Path(__file__).parent
RIS = QUI / "risultati_sessantatreesima"
DATI = QUI.parents[1] / "research" / "data" / "paura_avidita.json"
DAL, AL, RITARDO = sc.giorno(2020, 1, 1), sc.giorno(2026, 10, 25), 2


def indice() -> pd.Series:
    if not DATI.exists():
        r = urllib.request.urlopen(urllib.request.Request("https://api.alternative.me/fng/?limit=0&format=json",
                                                          headers={"User-Agent": "ricerca/1.0"}), timeout=60).read()
        DATI.write_bytes(r)
    d = json.loads(DATI.read_text())["data"]
    return pd.Series({int(x["timestamp"]) // 86400: int(x["value"]) for x in d}).sort_index()


def posizioni(fg: pd.Series, giorni: np.ndarray, entra, esce, verso: float) -> np.ndarray:
    pos, out = 0.0, []
    for g in giorni:
        v = fg.get(int(g) - RITARDO, np.nan)
        if np.isfinite(v):
            if pos == 0.0 and entra(v):
                pos = verso
            elif pos != 0.0 and esce(v):
                pos = 0.0
        out.append(pos)
    return np.array(out)


def conto(P: np.ndarray, R: np.ndarray, F: np.ndarray, costo: float, giorni: np.ndarray) -> pd.DataFrame:
    prima = np.concatenate([[0.0], P[:-1]])
    giro = np.abs(P - prima)
    d = pd.DataFrame({"lordo": P * R, "spese": giro * costo, "funding": P * F})
    d["netto"] = d["lordo"] - d["spese"] - d["funding"]
    d["netto_doppio"] = d["lordo"] - 2 * d["spese"] - d["funding"]
    d["giro"], d["long"], d["short"], d["monete"] = giro, np.maximum(P, 0), np.maximum(-P, 0), 1
    return d


def esegui(log=print) -> dict:
    fg = indice()
    pan = sc.pannello()
    ps = te.pannello_settimane(pan, log=lambda x: None, indicatori_si=False)
    j = pan["simboli"].index("BTCUSDT")
    costo = float(sc.costi_moneta(["BTCUSDT"])[0])
    giorni = np.arange(DAL, AL + 1, dtype=np.int64)
    R = sc.rendimenti(pan)[giorni - pan["t0"], j]
    F = np.nan_to_num(pan["funding"][giorni - pan["t0"], j])
    btc = pd.Series(ps["R"][:, ps["simboli"].index("BTCUSDT")], index=ps["lunedi"])
    P = {"PA": posizioni(fg, giorni, lambda v: v <= 20, lambda v: v >= 50, 1.0),
         "AV": posizioni(fg, giorni, lambda v: v >= 80, lambda v: v <= 50, -1.0)}
    P["PA + AV"] = P["PA"] + P["AV"]
    out, serie = {}, {}
    RIS.mkdir(exist_ok=True)
    for nome, p in P.items():
        d = conto(p, R, F, costo, giorni)
        s = g1.per_settimana(d, giorni)
        s.to_csv(RIS / f"settimane_{nome.replace(' + ', '_')}.csv.gz")
        e = te.esame(s, btc, inizio=int(s.index.min()), anni_pieni=(2020, 2021, 2022, 2023, 2024, 2025))
        e["giorni_dentro"] = int((p != 0).sum())
        e["operazioni"] = int(((p != 0) & (np.concatenate([[0.0], p[:-1]]) == 0)).sum())
        out[nome] = e
        if nome != "PA + AV":
            serie[f"125 {nome}"] = s["netto"]
    rivisto = ast.corretto_rivisto({**ast.serie_nuove(), **serie}, {k: out[k[4:]]["intero"] for k in serie})
    for k in serie:
        e = out[k[4:]]
        r = rivisto["candidate"][k]
        e["sharpe_corretto"], e["t"], e["gruppi"] = r["corretto_con_aggiunta"], r["t"], rivisto["gruppi"]
        e["esito"] = te.esito(e, e["sharpe_corretto"])
        anni = e.get("per_anno", {})
        e["regola_proprietario"] = bool(e["sharpe_corretto"] >= 0.90 and e["t"] > 3 and anni and all(v > 0 for v in anni.values()))
    # descrittivo: il Bitcoin nei 30 giorni dopo, per fasce dell'indice (valore di d, rendimento da d + 2)
    rb = pd.Series(sc.rendimenti(pan)[:, j], index=np.arange(pan["t0"], pan["t0"] + pan["close"].shape[0]))
    fasce = {}
    for a, b in ((0, 20), (21, 40), (41, 60), (61, 80), (81, 100)):
        xs = [float(np.prod(1 + rb.reindex(np.arange(g + RITARDO, g + RITARDO + 30)).fillna(0).to_numpy()) - 1)
              for g, v in fg.items() if a <= v <= b and DAL <= g <= AL - 32]
        fasce[f"{a}-{b}"] = {"giorni": len(xs), "media_30_giorni": float(np.mean(xs)) if xs else None}
    out["fasce"] = fasce
    s_btc = g1.per_settimana(conto(np.ones(len(giorni)), R, F, costo, giorni), giorni)
    out["btc_tenuto"] = te.esame(s_btc, btc, inizio=int(s_btc.index.min()), anni_pieni=(2020, 2021, 2022, 2023, 2024, 2025))["intero"]
    (RIS / "esame.json").write_text(json.dumps(out, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    righe = ["# Programma 7 — risultati della sessantatreesima prova (FG: l'indice di paura e avidità sul Bitcoin)", "",
             "Regole in `SESSANTATREESIMA.md` (scritte prima). Dal 1° gennaio 2020 al 25 ottobre 2026, perpetuo del Bitcoin di Binance.", ""]
    for nome in ("PA", "AV", "PA + AV"):
        e, i = out[nome], out[nome]["intero"]
        extra = (f"; Sharpe corretto {e['sharpe_corretto']:.2f}, t {e['t']:.2f}; **esito: {e['esito']}**" if "sharpe_corretto" in e else "")
        righe.append(f"* **{nome}**: Sharpe {i['sharpe']:.2f}, {100 * i['annuo']:+.1f}% l'anno, discesa {100 * i['discesa_max']:.1f}%; "
                     f"{e['operazioni']} operazioni, {e['giorni_dentro']} giorni dentro; per anno " +
                     ", ".join(f"{a} {100 * v:+.1f}%" for a, v in e["per_anno"].items()) + extra + ".")
    bt = out["btc_tenuto"]
    righe.append(f"* Il Bitcoin tenuto sempre: Sharpe {bt['sharpe']:.2f}, {100 * bt['annuo']:+.1f}% l'anno, discesa {100 * bt['discesa_max']:.1f}%.")
    righe.append("* Il Bitcoin nei 30 giorni dopo, per fasce dell'indice: " + ", ".join(
        f"{k} {100 * (v['media_30_giorni'] or 0):+.1f}% ({v['giorni']} giorni)" for k, v in fasce.items()) + ".")
    testo = "\n".join(righe) + "\n"
    (QUI / "RISULTATI_SESSANTATREESIMA.md").write_text(testo, encoding="utf-8")
    log(testo)
    return out


if __name__ == "__main__":
    esegui(log=lambda x: print(x, flush=True))
    print("SESSANTATREESIMA FINITA", flush=True)
