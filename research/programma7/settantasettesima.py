"""Programma 7, settantasettesima prova (SETTANTASETTESIMA.md): CF, i gestori di patrimoni sul Bitcoin del CME. Long il Bitcoin per la
settimana dal lunedi' dopo l'uscita del rapporto della CFTC se la loro posizione netta e' salita, short se e' scesa.

Uso: python3 -m research.programma7.settantasettesima
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
from research.programma6 import ventunesima as vu

QUI = Path(__file__).parent
RIS = QUI / "risultati_settantasettesima"
DATI = QUI.parent / "data" / "cftc" / "bitcoin_cme.json"
URL = ("https://publicreporting.cftc.gov/resource/gpe5-46if.json?$limit=2000&$order=report_date_as_yyyy_mm_dd"
       "&$where=cftc_contract_market_code=%27133741%27")
DAL, AL = sc.giorno(2020, 1, 6), sc.giorno(2026, 9, 28)


def rapporti() -> pd.DataFrame:
    if not DATI.exists():
        with urllib.request.urlopen(urllib.request.Request(URL, headers={"User-Agent": "ricerca/1.0"}), timeout=120) as r:
            d = json.load(r)
        DATI.parent.mkdir(parents=True, exist_ok=True)
        DATI.write_text(json.dumps(d))
    d = pd.DataFrame(json.loads(DATI.read_text()))
    d["martedi"] = (pd.to_datetime(d["report_date_as_yyyy_mm_dd"]).astype("int64") // 86_400_000_000_000).astype(int)
    for c in ("asset_mgr_positions_long", "asset_mgr_positions_short", "lev_money_positions_long", "lev_money_positions_short"):
        d[c] = pd.to_numeric(d[c], errors="coerce")
    d["gestori"] = d["asset_mgr_positions_long"] - d["asset_mgr_positions_short"]
    d["leva"] = d["lev_money_positions_long"] - d["lev_money_positions_short"]
    return d.drop_duplicates("martedi").sort_values("martedi").set_index("martedi")


def settimane(pan: dict, pos: pd.Series) -> pd.DataFrame:
    """Il conto settimanale del Bitcoin con la posizione `pos` (indice = lunedi' d'inizio della tenuta)."""
    t0, jb = pan["t0"], list(pan["simboli"]).index("BTCUSDT")
    O, F = pan["open"][:, jb], np.nan_to_num(pan["funding"][:, jb])
    righe, prima = [], 0.0
    for l, p in pos.items():
        a, b = l - t0, l + 7 - t0
        if b >= len(O) or not (np.isfinite(O[a]) and np.isfinite(O[b])):
            continue
        lordo = p * (O[b] / O[a] - 1)
        giro = abs(p - prima)
        spese = giro * vu.COSTO_BTC / 2
        fund = p * F[a:b].sum()
        righe.append({"lunedi": l, "lordo": lordo, "spese": spese, "funding": fund, "netto": lordo - spese - fund,
                      "netto_doppio": lordo - 2 * spese - fund, "giro": giro, "long": (lordo - spese - fund) if p > 0 else 0.0,
                      "short": (lordo - spese - fund) if p < 0 else 0.0, "monete": int(p != 0)})
        prima = p
    return pd.DataFrame(righe).set_index("lunedi")


def esegui(log=print) -> dict:
    pan = sc.pannello()
    ps = te.pannello_settimane(pan, log=lambda x: None, indicatori_si=False)
    btc = pd.Series(ps["R"][:, ps["simboli"].index("BTCUSDT")], index=ps["lunedi"])
    d = rapporti()
    log(f"[settantasettesima] {len(d)} rapporti, dal {sc.data(int(d.index.min()))} al {sc.data(int(d.index.max()))}")
    lunedi = d.index + 6                                      # il martedi' del rapporto + 6 giorni = il lunedi' dopo l'uscita (venerdi')
    dg, dl = d["gestori"].diff(), d["leva"].diff()
    varianti = {"CF": pd.Series(np.sign(dg.to_numpy()), index=lunedi),
                "solo long": pd.Series(np.where(dg.to_numpy() > 0, 1.0, 0.0), index=lunedi),
                "fondi a leva al contrario": pd.Series(-np.sign(dl.to_numpy()), index=lunedi),
                "Bitcoin tenuto": pd.Series(1.0, index=lunedi)}
    out, serie = {}, {}
    RIS.mkdir(exist_ok=True)
    for nome, pos in varianti.items():
        pos = pos[(pos.index >= DAL) & (pos.index <= AL)].fillna(0.0)
        s = settimane(pan, pos)
        s.to_csv(RIS / f"settimane_{nome.replace(' ', '_')}.csv")
        out[nome] = te.esame(s, btc, inizio=DAL, anni_pieni=(2021, 2022, 2023, 2024, 2025))
        serie[nome] = (s, pos)
    e = out["CF"]
    rivisto = ast.corretto_rivisto({**ast.serie_nuove(), "139 CF": serie["CF"][0]["netto"]}, {"139 CF": e["intero"]})
    r = rivisto["candidate"]["139 CF"]
    e["sharpe_corretto"], e["t"], e["gruppi"] = r["corretto_con_aggiunta"], r["t"], rivisto["gruppi"]
    e["esito"] = te.esito(e, e["sharpe_corretto"])
    anni = e.get("per_anno", {})
    e["regola_proprietario"] = bool(e["sharpe_corretto"] >= 0.90 and e["t"] > 3 and anni and all(v > 0 for v in anni.values()))
    p = serie["CF"][1]
    e["settimane_long"], e["settimane_short"] = int((p > 0).sum()), int((p < 0).sum())
    (RIS / "esame.json").write_text(json.dumps(out, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    pc = lambda v: f"{100 * v:+.1f}%"  # noqa: E731
    i = e["intero"]
    altre = "; ".join(f"{n}: Sharpe {out[n]['intero']['sharpe']:.2f}, {pc(out[n]['intero']['annuo'])} l'anno" for n in varianti if n != "CF")
    testo = "\n".join([
        "# Programma 7 — risultati della settantasettesima prova (CF: i gestori di patrimoni sul Bitcoin del CME)", "",
        "Regole in `SETTANTASETTESIMA.md` (scritte prima). Dal 6 gennaio 2020 al 28 settembre 2026, rapporto settimanale della CFTC, long o "
        "short il perpetuo del Bitcoin per la settimana dal lunedì dopo l'uscita.", "",
        f"* {len(d)} rapporti; settimane long {e['settimane_long']}, short {e['settimane_short']}.",
        f"* **CF: Sharpe {i['sharpe']:.2f}**, {pc(i['annuo'])} l'anno, volatilità {100 * i['volatilita']:.1f}%, discesa "
        f"{100 * i['discesa_max']:.1f}%; spese {100 * e['spese_annue']:.1f}% l'anno; in più del Bitcoin {pc(e['extra_btc_annuo'])} l'anno.",
        "* Per anno: " + ", ".join(f"{a} {pc(v)}" for a, v in e["per_anno"].items()) + ".",
        f"* Per confronto: {altre}.",
        f"* Sharpe corretto con l'aggiunta {e['sharpe_corretto']:.2f} ({e['gruppi']} gruppi); t {e['t']:.2f}; regola del proprietario: "
        f"{'sì' if e['regola_proprietario'] else 'no'}.", "",
        f"**Esito: {e['esito']}**"]) + "\n"
    (QUI / "RISULTATI_SETTANTASETTESIMA.md").write_text(testo, encoding="utf-8")
    log(testo)
    return out


if __name__ == "__main__":
    esegui(log=lambda x: print(x, flush=True))
    print("SETTANTASETTESIMA FINITA", flush=True)
