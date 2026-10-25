"""Programma 6: l'asticella rivista (ASTICELLA.md). Lo Sharpe corretto con N = gruppi di prove simili e V = varianza degli
Sharpe dei gruppi (López de Prado 2019 e 2020), accanto al calcolo di prima e al t dello Sharpe contro 3,0 (Harvey, Liu e
Zhu 2016).

Uso: python3 -m research.programma6.asticella
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.cluster.hierarchy import fcluster, linkage
from scipy.spatial.distance import squareform

from research.programma6 import quarantacinquesima as qc
from research.programma6 import quarantatreesima as qt
from research.programma6 import quarantesima as qr
from research.programma6 import quarantunesima as qu
from research.programma6 import seconda as sc
from research.programma6 import terza as te
from research.programma6 import trentaquattresima as tq

QUI = Path(__file__).parent
RIS = QUI / "risultati_asticella"
MIN_COMUNI, TAGLIO, ALTRI_TAGLI = 52, 0.5, (0.3, 0.7)
T_PERDENTI, SETTIMANE_PROGRAMMA = -3.0, 300


def _lunedi(giorni) -> np.ndarray:
    g = np.asarray(giorni, dtype=np.int64)
    return ((g + 3) // 7) * 7 - 3


def settimanale(f: str, colonna: str = "netto") -> pd.Series:
    d = pd.read_csv(QUI / f, index_col=0)
    if f.split("/")[-1].startswith("giorni"):
        x = d["netto"] if "netto" in d else d["lordo"] - d["spese"] - d["funding"]
        return x.groupby(_lunedi(d.index)).sum()
    return d[colonna]


def da_operazioni(df: pd.DataFrame, modo: str) -> pd.Series:
    if modo == "tq":
        return tq.portafoglio(df)["netto"]
    if modo == "qr":
        return qr.portafoglio(df)["netto"]
    if modo == "qu":
        return qu.portafoglio(df)["netto"]
    return qt.portafoglio(df)["netto"]


def le_prove() -> list:
    """(nome, serie settimanale o None, Sharpe pubblicato) delle 107 prove del conto, nello stesso ordine del conto."""
    out = []
    e1 = sorted((QUI / "risultati").glob("*.json"))
    for f in e1:
        e = json.loads(f.read_text())
        if e.get("trade"):
            out.append((f"1 {f.stem}", None, e["capitale"]["sharpe_annuo"]))
    for v in ("A1", "A2", "A3"):
        out.append((f"2A {v}", settimanale(f"risultati_seconda/giorni_{v}.csv.gz"), None))
    for f in sorted((QUI / "risultati_seconda").glob("B_*.json")):
        e = json.loads(f.read_text())
        if e.get("trade"):
            out.append((f"2B {f.stem[2:]}", None, e["capitale"]["sharpe_annuo"]))
    lista = [("3 C1", "risultati_terza/settimane_C1.csv.gz"), ("3 C2", "risultati_terza/settimane_C2.csv.gz"),
             ("3 C3", "risultati_terza/settimane_C3.csv.gz"), ("6 F1", "risultati_sesta/settimane_F1.csv.gz"),
             ("6 F2", "risultati_sesta/settimane_F2.csv.gz"), ("8 F3", "risultati_ottava/settimane_F3.csv.gz"),
             ("9 G1", "risultati_nona/settimane_G1.csv.gz"), ("9 G2", "risultati_nona/settimane_G2.csv.gz"),
             ("10 C4", "risultati_decima/settimane_C4.csv.gz"), ("11 P1", "risultati_undicesima/settimane_P1.csv.gz"),
             ("11 P2", "risultati_undicesima/settimane_P2.csv.gz"), ("12 K1", "risultati_dodicesima/settimane_K1.csv.gz"),
             ("13 BTC funding", "risultati_tredicesima/settimane.csv.gz"),
             ("14 M1", "risultati_quattordicesima/settimane_M1.csv.gz"), ("14 M2", "risultati_quattordicesima/settimane_M2.csv.gz"),
             ("15 F3+M1", "risultati_quindicesima/settimane_F3_M1.csv.gz"), ("16 M3", "risultati_sedicesima/giorni_M3.csv.gz"),
             ("17 M4", "risultati_diciassettesima/settimane_M4.csv.gz"), ("17 M5", "risultati_diciassettesima/settimane_M5.csv.gz"),
             ("18 N1", "risultati_diciottesima/settimane_N1.csv.gz"), ("18 N2", "risultati_diciottesima/settimane_N2.csv.gz"),
             ("19 P1", "risultati_diciannovesima/settimane_P1.csv.gz"), ("19 P2", "risultati_diciannovesima/settimane_P2.csv.gz"),
             ("20 S1", "risultati_ventesima/settimane_S1.csv.gz"), ("20 S2", "risultati_ventesima/settimane_S2.csv.gz"),
             ("23 M6", "risultati_ventitreesima/settimane_M6.csv.gz"), ("24 F5", "risultati_ventiquattresima/settimane_F5.csv.gz"),
             ("25 M7", "risultati_venticinquesima/settimane_M7.csv.gz"),
             ("25 F5+M7", "risultati_venticinquesima/settimane_F5_M7.csv.gz"),
             ("28 K2", "risultati_ventottesima/settimane_K2.csv.gz"),
             ("28 F5+M7+K2", "risultati_ventottesima/settimane_F5_M7_K2.csv.gz"),
             ("33 N3 portafoglio", "risultati_trentatreesima/settimane_N3.csv.gz"),
             ("33 F5+N3", "risultati_trentatreesima/settimane_F5_N3.csv.gz"),
             ("29 M8", "risultati_ventinovesima/settimane_M8.csv.gz"), ("31 M7+M8", "risultati_trentunesima/settimane_M7_M8.csv.gz")]
    out += [(n, settimanale(f), None) for n, f in lista]
    for n, f in (("34 T1", "risultati_trentaquattresima/operazioni_T1.csv.gz"),
                 ("34 T2", "risultati_trentaquattresima/operazioni_T2.csv.gz"),
                 ("35 T3", "risultati_trentacinquesima/operazioni_T3.csv.gz")):
        out.append((n, da_operazioni(pd.read_csv(QUI / f), "tq"), None))
    out.append(("36 T5", settimanale("risultati_trentaseiesima/giorni_T5.csv.gz"), None))
    for n, f in (("37 T6", "risultati_trentasettesima/operazioni_T6.csv.gz"),
                 ("39 T8", "risultati_trentanovesima/operazioni_T8.csv.gz")):
        out.append((n, da_operazioni(pd.read_csv(QUI / f), "tq"), None))
    out.append(("40 coppie", da_operazioni(pd.read_csv(QUI / "risultati_quarantesima/operazioni_coppie.csv.gz"), "qr"), None))
    out.append(("41 U1", da_operazioni(pd.read_csv(QUI / "risultati_quarantunesima/eventi_U1.csv"), "qu"), None))
    out.append(("42 F6", settimanale("risultati_quarantaduesima/settimane_F6.csv.gz"), None))
    for v in ("Q1", "Q2"):
        out.append((f"43 {v}", da_operazioni(pd.read_csv(QUI / f"risultati_quarantatreesima/eventi_{v}.csv"), "qt"), None))
    out.append(("44 S1", settimanale("risultati_quarantaquattresima/settimane_S1.csv.gz"), None))
    out.append(("45 I1", settimanale("risultati_quarantacinquesima/settimane_I1.csv.gz"), None))
    out.append(("45 I2", da_operazioni(pd.read_csv(QUI / "risultati_quarantacinquesima/eventi_I2.csv"), "qu"), None))
    tv = pd.read_csv(QUI / "risultati_quarantaseiesima/settimane_nette.csv.gz", index_col=0)
    e46 = json.loads((QUI / "risultati_quarantaseiesima" / "esame.json").read_text())
    out += [(f"46 {k}", tv[k], None) for k in e46]
    out += [(f"47 {v}", settimanale(f"risultati_quarantasettesima/settimane_{v}.csv.gz"), None) for v in ("O1", "O2")]
    out.append(("48 R1", settimanale("risultati_quarantottesima/settimane_R1.csv.gz"), None))
    return out


def periodo(s: pd.Series) -> pd.Series:
    """Le settimane del programma 6 (dal 4 gennaio 2021 al 5 ottobre 2026), senza le settimane ferme prima della prima operata."""
    s = s.astype(float)
    s = s[(s.index >= sc.giorno(2021, 1, 4)) & (s.index <= sc.giorno(2026, 10, 5))]
    nz = np.flatnonzero(s.to_numpy() != 0)
    return s.iloc[nz[0]:] if len(nz) else s


def conto_di_prima() -> list:
    """La lista degli Sharpe usata finora (come `quarantottesima.esegui`, piu' la 48)."""
    sr = qc.prove_fino_alla_quarantaquattresima()
    e45 = json.loads((QUI / "risultati_quarantacinquesima" / "esame.json").read_text())
    sr += [e45["I1"]["intero"]["sharpe"], e45["I2"]["portafoglio"]["intero"]["sharpe"]]
    sr += [e["intero"]["sharpe"] for e in json.loads((QUI / "risultati_quarantaseiesima" / "esame.json").read_text()).values()]
    sr += [e["intero"]["sharpe"] for e in json.loads((QUI / "risultati_quarantasettesima" / "esame.json").read_text()).values()]
    sr.append(json.loads((QUI / "risultati_quarantottesima" / "esame.json").read_text())["intero"]["sharpe"])
    return sr


def sharpe(x: pd.Series) -> float:
    x = x.dropna()
    sd = x.std(ddof=1)
    return float(x.mean() / sd * math.sqrt(52)) if len(x) > 2 and sd > 0 else 0.0


def gruppi(serie: dict, taglio: float) -> list:
    nomi = list(serie)
    n = len(nomi)
    R = np.zeros((n, n))
    for i in range(n):
        for j in range(i + 1, n):
            a, b = serie[nomi[i]], serie[nomi[j]]
            comuni = a.index.intersection(b.index)
            x, y = a.loc[comuni], b.loc[comuni]
            ok = (x.abs() > 0) | (y.abs() > 0)          # le settimane in cui almeno una delle due ha operato
            rho = float(np.corrcoef(x[ok], y[ok])[0, 1]) if ok.sum() >= MIN_COMUNI and x[ok].std() > 0 and y[ok].std() > 0 else 0.0
            R[i, j] = R[j, i] = rho if np.isfinite(rho) else 0.0
    np.fill_diagonal(R, 1.0)
    D = np.sqrt(np.clip((1 - R) / 2, 0, None))
    Z = linkage(squareform(D, checks=False), method="average")
    etichette = fcluster(Z, t=math.sqrt((1 - taglio) / 2), criterion="distance")
    out = []
    for g in sorted(set(etichette)):
        membri = [nomi[i] for i in np.flatnonzero(etichette == g)]
        media = pd.concat([serie[m] for m in membri], axis=1).mean(axis=1)
        out.append({"membri": membri, "sharpe": sharpe(media), "settimane": int(media.notna().sum())})
    return out


def per_v(gr: list, soli: list, escludi_perdenti: bool) -> list:
    """Gli Sharpe dei gruppi che entrano in V. Con ``escludi_perdenti`` (ASTICELLA.md, sezione 5) i gruppi con il t dello
    Sharpe sotto -3 restano in N ma non in V; per le prove senza serie il t si calcola sulle 300 settimane del programma."""
    tutti = [(g["sharpe"], g["settimane"]) for g in gr] + [(sr, SETTIMANE_PROGRAMMA) for sr in soli]
    if not escludi_perdenti:
        return [sr for sr, _ in tutti]
    return [sr for sr, n in tutti if sr * math.sqrt(n / 52) >= T_PERDENTI]


def corretto_rivisto(nuove: dict, candidate: dict, taglio: float = TAGLIO) -> dict:
    """Lo Sharpe corretto rivisto per prove nuove: ``nuove`` = {nome: serie settimanale netta} (gia' nel conto),
    ``candidate`` = {nome: esame["intero"]}. Gruppi ricalcolati con le prove nuove dentro."""
    prove = le_prove()
    serie = {n: periodo(s) for n, s, _ in prove if s is not None}
    serie.update({n: periodo(s) for n, s in nuove.items()})
    soli = [sr for _, s, sr in prove if s is None]
    gr = gruppi(serie, taglio)
    sr_gruppi = per_v(gr, soli, False)
    sr_v = per_v(gr, soli, True)
    out = {"gruppi": len(sr_gruppi), "deviazione": float(np.std(sr_gruppi, ddof=1)),
           "in_v_con_aggiunta": len(sr_v), "deviazione_con_aggiunta": float(np.std(sr_v, ddof=1)), "candidate": {}}
    for nome, i in candidate.items():
        membri = next((g["membri"] for g in gr if nome in g["membri"]), [nome])
        out["candidate"][nome] = {
            "corretto": te.sharpe_corretto(i["sharpe"], i["settimane"], i["asimmetria"], i["curtosi"], sr_gruppi, 52),
            "corretto_con_aggiunta": te.sharpe_corretto(i["sharpe"], i["settimane"], i["asimmetria"], i["curtosi"], sr_v, 52,
                                                        n_prove=len(sr_gruppi)),
            "t": i["sharpe"] * math.sqrt(i["settimane"] / 52), "gruppo": membri}
    return out


def serie_nuove() -> dict:
    """Le serie settimanali nette delle prove a portafoglio dalla 49 in poi (le prove fino alla 48 sono in ``le_prove``)."""
    out = {}
    for n, f in (("49 X1", "risultati_quarantanovesima/settimane_X1.csv.gz"), ("49 X2", "risultati_quarantanovesima/settimane_X2.csv.gz"),
                 ("51 F7", "risultati_cinquantunesima/settimane_F7.csv.gz"), ("52 B1", "risultati_cinquantaduesima/settimane_B1.csv.gz"),
                 ("53 F8", "risultati_cinquantatreesima/settimane_F8.csv.gz"), ("55 C3", "risultati_cinquantacinquesima/settimane_C3.csv.gz"),
                 ("56 F9", "risultati_cinquantaseiesima/settimane_F9.csv.gz")):
        if (QUI / f).exists():
            d = pd.read_csv(QUI / f, index_col=0)
            out[n] = d["netto"] if "netto" in d else d.iloc[:, 0]
    for f in sorted((QUI / "risultati_cinquantaquattresima").glob("settimane_*.csv.gz")):
        out[f"54 {f.name[len('settimane_'):-len('.csv.gz')]}"] = pd.read_csv(f, index_col=0).iloc[:, 0]
    out.update(serie_programma7())
    return out


def serie_programma7() -> dict:
    """Le serie settimanali nette delle prove del programma 7 (revisione del 23 ottobre: mancavano dal conto). Le prove a
    portafoglio con la loro serie; quelle a eventi con il portafoglio della prova 41 (5% a evento, al massimo 20 aperte); il
    buco del CME con l'1% di rischio a operazione."""
    p7 = QUI.parent / "programma7"
    out = {}
    for n, f in (("57 G1", "risultati_prima/settimane_G1.csv.gz"), ("58 G2", "risultati_seconda/settimane_G2.csv.gz"),
                 ("60 G3", "risultati_quarta/settimane_G3.csv.gz"), ("61 F5T", "risultati_quinta/settimane_F5T.csv.gz"),
                 ("61 G1T", "risultati_quinta/settimane_G1T.csv.gz"), ("63 G6", "risultati_settima/settimane_G6.csv.gz"),
                 ("63 G1+G6", "risultati_settima/settimane_G1_G6.csv.gz"), ("66 MAX", "risultati_decima/settimane_MAX.csv.gz"),
                 ("67 G9", "risultati_undicesima/settimane_G9.csv.gz"), ("69 G11", "risultati_tredicesima/settimane_G11.csv.gz"),
                 ("72 G14", "risultati_sedicesima/settimane_G14.csv.gz"), ("73 S1", "../programma8/risultati_prima/settimane_S1.csv.gz"),
                 ("73 S2", "../programma8/risultati_prima/settimane_S2.csv.gz"),
                 # 25 ottobre: le prove a portafoglio dalla 84 in poi mancavano dal mazzo della correzione
                 ("84 G20", "risultati_ventiduesima/settimane_G20.csv.gz"), ("86 F5N", "risultati_ventiquattresima/settimane_F5N.csv.gz"),
                 ("86 F5 120/80", "risultati_ventiquattresima/settimane_F5_120-80.csv.gz"),
                 ("88 G1N", "risultati_ventiseiesima/settimane_G1N.csv.gz"), ("88 G1 120/80", "risultati_ventiseiesima/settimane_G1_120-80.csv.gz"),
                 ("89 F5C", "risultati_ventisettesima/settimane_F5C.csv.gz"),
                 ("92 G1 clima", "risultati_trentesima/settimane_G1_clima.csv.gz"), ("92 F5 clima", "risultati_trentesima/settimane_F5_clima.csv.gz"),
                 ("93 G1-S", "risultati_trentunesima/settimane_G1-S.csv.gz")):
        if (p7 / f).exists():
            out[n] = pd.read_csv(p7 / f, index_col=0)["netto"]
    for n, f, ora_col in (("59 G4", "risultati_terza/eventi_G4.csv", None), ("62 G5", "risultati_sesta/eventi_G5.csv", None),
                          ("64 G7", "risultati_ottava/eventi_G7.csv", None), ("65 G8", "risultati_nona/eventi_G8.csv", "ora")):
        if not (p7 / f).exists():
            continue
        d = pd.read_csv(p7 / f)
        giorno = d["data"].map(lambda x: sc.giorno(*map(int, x.split("-")))).to_numpy()
        ora = giorno * 24 + (d[ora_col].to_numpy() if ora_col else 0)
        ev = pd.DataFrame({"simbolo": d["simbolo"] if "simbolo" in d else d["contratto"], "ora": ora,
                           "uscita_h": ora + np.round(d["giorni"].to_numpy() * 24).astype(int), "r": d["r"]})
        out[n] = qu.portafoglio(ev)["netto"]
    # 24 ottobre: G12 (7 giorni dall'ora dopo l'evento), G13 (le ore fino alla chiusura) e G15 (gli sblocchi) mancavano
    for n, f in (("70 G12", "risultati_quattordicesima/eventi_G12.csv"), ("71 G13", "risultati_quindicesima/eventi_G13.csv"),
                 ("74 G15", "risultati_diciassettesima/eventi_G15.csv")):
        if not (p7 / f).exists():
            continue
        d = pd.read_csv(p7 / f)
        ora = d["data"].map(lambda x: sc.giorno(*map(int, x.split("-")))).to_numpy() * 24
        if "ora_evento" in d:
            ora = ora + d["ora_evento"].to_numpy() + 1
        durata = 7 * 24 if n == "70 G12" else (d["ore"].to_numpy() if "ore" in d else np.round(d["giorni"].to_numpy() * 24).astype(int))
        ev = pd.DataFrame({"simbolo": d["simbolo"], "ora": ora, "uscita_h": ora + durata, "r": d["r7" if n == "70 G12" else "r"]})
        out[n] = qu.portafoglio(ev)["netto"]
    f = p7 / "risultati_dodicesima" / "operazioni_G10.csv"
    if f.exists():
        d = pd.read_csv(f)
        g = d["venerdi"].map(lambda x: sc.giorno(*map(int, x.split("-")))).to_numpy() + 3      # il lunedi' dopo il venerdi'
        out["68 G10"] = pd.Series(0.01 * d["R"].to_numpy(), index=g).groupby(level=0).sum()
    return out


def aggiunta_23(log=print) -> dict:
    """ASTICELLA.md, sezione 5: le candidate gia' viste e C3 con il calcolo della sezione 3 e con l'aggiunta, prove fino alla 55."""
    e25 = json.loads((QUI / "risultati_venticinquesima" / "esame.json").read_text())
    e28 = json.loads((QUI / "risultati_ventottesima" / "esame.json").read_text())
    esami = {"24 F5": json.loads((QUI / "risultati_ventiquattresima" / "esame.json").read_text())["intero"],
             "25 F5+M7": e25["F5 + M7"]["intero"], "28 K2": e28["K2"]["intero"], "28 F5+M7+K2": e28["F5 + M7 + K2"]["intero"],
             "42 F6": json.loads((QUI / "risultati_quarantaduesima" / "esame.json").read_text())["intero"],
             "55 C3": json.loads((QUI / "risultati_cinquantacinquesima" / "esame.json").read_text())["intero"]}
    r = corretto_rivisto(serie_nuove(), esami)
    gr = gruppi({**{n: periodo(s) for n, s, _ in le_prove() if s is not None}, **{n: periodo(s) for n, s in serie_nuove().items()}}, TAGLIO)
    fuori = [{"membri": g["membri"], "sharpe": round(g["sharpe"], 2), "t": round(g["sharpe"] * math.sqrt(g["settimane"] / 52), 1)}
             for g in gr if g["sharpe"] * math.sqrt(g["settimane"] / 52) < T_PERDENTI]
    soli_fuori = [round(sr, 2) for _, s, sr in le_prove() if s is None and sr * math.sqrt(SETTIMANE_PROGRAMMA / 52) < T_PERDENTI]
    r["fuori_da_v"], r["soli_fuori_da_v"] = fuori, soli_fuori
    RIS.mkdir(exist_ok=True)
    (RIS / "aggiunta_23.json").write_text(json.dumps(r, ensure_ascii=False, indent=1), encoding="utf-8")
    righe = ["# Programma 6 — l'asticella con l'aggiunta del 23 ottobre: i risultati", "",
             "Regola in `ASTICELLA.md`, sezione 5 (scritta prima di questo calcolo). Prove fino alla 55.", "",
             f"* Gruppi (N): **{r['gruppi']}**; deviazione degli Sharpe dei gruppi come nella sezione 3: {r['deviazione']:.2f}; "
             f"con l'aggiunta ({r['in_v_con_aggiunta']} gruppi in V): **{r['deviazione_con_aggiunta']:.2f}**.",
             f"* Fuori da V (t dello Sharpe sotto −3): " + "; ".join(f"{', '.join(g['membri'])} (Sharpe {g['sharpe']:+.2f}, t {g['t']:+.1f})"
                                                                  for g in fuori)
             + (f"; prove senza serie: {len(soli_fuori)} (Sharpe {', '.join(f'{x:+.2f}' for x in soli_fuori)})" if soli_fuori else "") + ".", "",
             "| Candidata | Sharpe | t dello Sharpe | Corretto (sezione 3) | Corretto con l'aggiunta |", "|---|---|---|---|---|"]
    for n, c in r["candidate"].items():
        righe.append(f"| {n} | {esami[n]['sharpe']:.2f} | {c['t']:.2f} | {c['corretto']:.2f} | **{c['corretto_con_aggiunta']:.2f}** |")
    righe += ["", "Tutte queste candidate sono state viste prima della regola: per la riserva della sezione 5 nessuna diventa «validata sul "
              "passato» per questo calcolo, qualunque sia il numero."]
    testo = "\n".join(righe) + "\n"
    (QUI / "RISULTATI_ASTICELLA_23.md").write_text(testo, encoding="utf-8")
    log(testo)
    return r


def esegui(log=print) -> dict:
    prove = le_prove()
    assert len(prove) == 107, len(prove)
    serie = {n: periodo(s) for n, s, _ in prove if s is not None}
    soli = [(n, sr) for n, s, sr in prove if s is None]
    vecchi = conto_di_prima()
    assert len(vecchi) == 107, len(vecchi)
    candidate = {"F5": "24 F5", "M7": "25 M7", "K2": "28 K2", "F5 + M7": "25 F5+M7", "F5 + M7 + K2": "28 F5+M7+K2",
                 "M7 + M8": "31 M7+M8", "F6": "42 F6", "R1": "48 R1"}
    esami = {"F5": json.loads((QUI / "risultati_ventiquattresima" / "esame.json").read_text())}
    e25 = json.loads((QUI / "risultati_venticinquesima" / "esame.json").read_text())
    e28 = json.loads((QUI / "risultati_ventottesima" / "esame.json").read_text())
    esami.update({"M7": e25["M7"], "F5 + M7": e25["F5 + M7"], "K2": e28["K2"], "F5 + M7 + K2": e28["F5 + M7 + K2"],
                  "M7 + M8": json.loads((QUI / "risultati_trentunesima" / "esame.json").read_text()),
                  "F6": json.loads((QUI / "risultati_quarantaduesima" / "esame.json").read_text()),
                  "R1": json.loads((QUI / "risultati_quarantottesima" / "esame.json").read_text())})
    out = {"prove": len(prove), "con_serie": len(serie), "da_sole": len(soli), "tagli": {}}
    for taglio in (TAGLIO,) + ALTRI_TAGLI:
        gr = gruppi(serie, taglio)
        sr_gruppi = [g["sharpe"] for g in gr] + [sr for _, sr in soli]
        riga = {"gruppi": len(sr_gruppi), "deviazione_sharpe_gruppi": float(np.std(sr_gruppi, ddof=1)), "candidate": {}}
        if taglio == TAGLIO:
            riga["composizione"] = [{"membri": g["membri"], "sharpe": round(g["sharpe"], 3)} for g in gr]
        for nome, e in esami.items():
            i = e["intero"]
            riga["candidate"][nome] = {
                "sharpe": i["sharpe"], "settimane": i["settimane"],
                "corretto_prima": te.sharpe_corretto(i["sharpe"], i["settimane"], i["asimmetria"], i["curtosi"], vecchi, 52),
                "corretto_rivisto": te.sharpe_corretto(i["sharpe"], i["settimane"], i["asimmetria"], i["curtosi"], sr_gruppi, 52),
                "t": i["sharpe"] * math.sqrt(i["settimane"] / 52)}
        out["tagli"][str(taglio)] = riga
    out["deviazione_sharpe_prove"] = float(np.std(vecchi, ddof=1))
    RIS.mkdir(exist_ok=True)
    (RIS / "esame.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    t0 = out["tagli"][str(TAGLIO)]
    righe = ["# Programma 6 — l'asticella rivista: i risultati", "",
             "Procedura in `ASTICELLA.md` (scritta prima del ricalcolo).", "",
             f"* Prove nel conto: {len(prove)}; con la serie dei rendimenti {len(serie)}, contate da sole {len(soli)} (prove 1 e 2B).",
             f"* Gruppi di prove simili (correlazione media almeno {TAGLIO}): **{t0['gruppi']}**; deviazione degli Sharpe dei gruppi "
             f"{t0['deviazione_sharpe_gruppi']:.2f} (delle prove una per una {out['deviazione_sharpe_prove']:.2f}).",
             f"* Agli altri tagli: " + "; ".join(f"{k}: {v['gruppi']} gruppi, deviazione {v['deviazione_sharpe_gruppi']:.2f}"
                                               for k, v in out["tagli"].items() if k != str(TAGLIO)) + ".", "",
             "| Candidata | Sharpe | Settimane | t dello Sharpe (soglia 3,0) | Corretto, calcolo di prima | Corretto rivisto (taglio 0,5) | "
             "taglio 0,3 | taglio 0,7 |", "|---|---|---|---|---|---|---|---|"]
    for nome in esami:
        c = t0["candidate"][nome]
        righe.append(f"| {nome} | {c['sharpe']:.2f} | {c['settimane']} | {c['t']:.2f} | {c['corretto_prima']:.2f} | "
                     f"**{c['corretto_rivisto']:.2f}** | {out['tagli']['0.3']['candidate'][nome]['corretto_rivisto']:.2f} | "
                     f"{out['tagli']['0.7']['candidate'][nome]['corretto_rivisto']:.2f} |")
    righe += ["", "**I gruppi (taglio 0,5)**:", ""]
    for g in sorted(t0["composizione"], key=lambda g: -len(g["membri"])):
        righe.append(f"* Sharpe {g['sharpe']:+.2f}: " + ", ".join(g["membri"]))
    testo = "\n".join(righe) + "\n"
    (QUI / "RISULTATI_ASTICELLA.md").write_text(testo, encoding="utf-8")
    log(testo)
    return out


if __name__ == "__main__":
    esegui(log=lambda x: print(x, flush=True))
