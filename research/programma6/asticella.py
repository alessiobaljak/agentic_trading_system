"""Programma 6: l'asticella rivista (ASTICELLA.md). Lo Sharpe corretto con N = gruppi di prove simili e V = varianza degli
Sharpe dei gruppi (López de Prado 2019 e 2020), accanto al calcolo di prima e al t dello Sharpe contro 3,0 (Harvey, Liu e
Zhu 2016).

Uso: python3 -m research.programma6.asticella
"""
from __future__ import annotations

import json
import math
import re
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
# L'esame in vigore (`esame`): probabilita' che non sia fortuna da 0,80 (9 novembre), t dello Sharpe da 3, ogni anno positivo.
SOGLIA_PROBABILITA, SOGLIA_T = 0.80, 3.0
# I numeri NON ufficiali accanto (`esame`; ASTICELLA.md, sezione 6): le prove a incasso quasi fisso (backlog P34, 15 novembre), le
# serie dei calcoli bocciati dal revisore (FAIL, audits/reports/2026-11-15-PROVA157.md), i ritardi di Newey e West (base, controllo).
INCASSO_FISSO = (157, 159, 161)
BOCCIATE_DAL_REVISORE = ("157 A", "157 B")
RITARDI, RITARDI_CONTROLLO = 4, 13


class Solo(float):
    """Lo Sharpe di una prova senza serie, con le settimane su cui e' misurato (``settimane``). Si usa come un numero: le funzioni che
    lo trattano come uno Sharpe continuano a funzionare; ``per_v`` ne usa le settimane per il t. 27 novembre 2026 (audit del 26
    novembre, esame-4): prima il t di tutte le prove senza serie si calcolava sulle 300 settimane del programma, anche per la 151 (19
    settimane) e la 153 (196), che cosi' uscivano da V."""

    def __new__(cls, sharpe: float, settimane: int = SETTIMANE_PROGRAMMA):
        x = super().__new__(cls, sharpe)
        x.settimane = int(settimane)
        return x


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


def correlazioni(serie: dict) -> tuple:
    """(nomi, R): la correlazione dei rendimenti settimanali di ogni coppia di serie, sulle settimane comuni in cui almeno una delle
    due ha operato (almeno ``MIN_COMUNI``, altrimenti 0). 27 novembre 2026 (audit del 26 novembre, esame-8): le settimane vuote
    (NaN, per esempio le 93 e 108 settimane prima della quotazione di APT e MATIC nella 149) si tolgono coppia per coppia; prima la
    correlazione con una serie piena usciva NaN, cioe' 0, e quelle serie non potevano entrare in un'altra famiglia."""
    nomi = list(serie)
    n = len(nomi)
    vuote = [bool(serie[m].isna().any()) for m in nomi]
    R = np.zeros((n, n))
    for i in range(n):
        for j in range(i + 1, n):
            a, b = serie[nomi[i]], serie[nomi[j]]
            comuni = a.index.intersection(b.index)
            x, y = a.loc[comuni], b.loc[comuni]
            ok = (x.abs() > 0) | (y.abs() > 0)          # le settimane in cui almeno una delle due ha operato
            if vuote[i] or vuote[j]:
                ok &= x.notna() & y.notna()             # senza le settimane vuote della coppia
            rho = float(np.corrcoef(x[ok], y[ok])[0, 1]) if ok.sum() >= MIN_COMUNI and x[ok].std() > 0 and y[ok].std() > 0 else 0.0
            R[i, j] = R[j, i] = rho if np.isfinite(rho) else 0.0
    np.fill_diagonal(R, 1.0)
    return nomi, R


def gruppi(serie: dict, taglio: float, corr: tuple | None = None) -> list:
    """Le famiglie (ASTICELLA.md, sezione 3). ``corr`` = (nomi, R) di `correlazioni` gia' calcolate, nello stesso ordine e per gli
    stessi nomi di ``serie`` (la correlazione di una coppia non dipende dalle altre serie: `esame` la calcola una volta sola)."""
    nomi, R = corr if corr is not None else correlazioni(serie)
    D = np.sqrt(np.clip((1 - R) / 2, 0, None))
    Z = linkage(squareform(D, checks=False), method="average")
    etichette = fcluster(Z, t=math.sqrt((1 - taglio) / 2), criterion="distance")
    out = []
    for g in sorted(set(etichette)):
        membri = [nomi[i] for i in np.flatnonzero(etichette == g)]
        media = pd.concat([serie[m] for m in membri], axis=1).mean(axis=1)
        out.append({"membri": membri, "sharpe": sharpe(media), "settimane": int(media.notna().sum())})
    return out


def per_v(gr: list, soli: list, escludi_perdenti: bool, simmetrica: bool = False) -> list:
    """Gli Sharpe dei gruppi che entrano in V. Con ``escludi_perdenti`` (ASTICELLA.md, sezione 5) i gruppi con il t dello
    Sharpe sotto -3 restano in N ma non in V. Per le prove senza serie il t si calcola sulle loro settimane (``Solo.settimane``,
    dal 27 novembre 2026); un numero semplice vale 300 settimane, quelle del programma (le prove 1 e 2B, che lo coprono tutto).
    ``simmetrica`` (NON ufficiale, ASTICELLA.md, sezione 6): fuori da V anche i gruppi con il t sopra +3."""
    tutti = [(g["sharpe"], g["settimane"]) for g in gr] + [(float(x), getattr(x, "settimane", SETTIMANE_PROGRAMMA)) for x in soli]
    if not escludi_perdenti:
        return [sr for sr, _ in tutti]
    return [sr for sr, n in tutti if T_PERDENTI <= sr * math.sqrt(n / 52) and (not simmetrica or sr * math.sqrt(n / 52) <= -T_PERDENTI)]


def corretto_rivisto(nuove: dict, candidate: dict, taglio: float = TAGLIO) -> dict:
    """Lo Sharpe corretto rivisto per prove nuove: ``nuove`` = {nome: serie settimanale netta} (gia' nel conto),
    ``candidate`` = {nome: esame["intero"]}. Gruppi ricalcolati con le prove nuove dentro.

    **Non e' l'esame di oggi.** Il mazzo e' quello delle prove fino alla 48 piu' le sole serie passate in ``nuove``: serve ai
    riesami che rifanno il conto «fino alla prova N» com'era allora (per esempio la 55). Per le prove nuove si usa
    ``corretto_famiglie`` (mazzo completo, decisione dell'11 novembre; la 152 con questa funzione ha scritto 0,88 invece di 0,74)."""
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
                 ("93 G1-S", "risultati_trentunesima/settimane_G1-S.csv.gz"),
                 ("94 G1N-S", "risultati_trentaduesima/settimane_G1N-S.csv.gz"),
                 ("95 CF", "risultati_trentatreesima/settimane_CF.csv.gz"), ("97 CC", "risultati_trentacinquesima/settimane_CC.csv.gz"),
                 ("100 SC", "risultati_trentottesima/settimane_SC.csv.gz"),
                 ("101 VS", "risultati_trentanovesima/settimane_VS.csv.gz"),
                 ("102 G25", "risultati_quarantesima/settimane_G25.csv.gz"),
                 # 12 novembre (backlog P34): le prove a portafoglio dalla 103 alla 152 e quelle prima della 103 che mancavano;
                 # l'elenco intero, con le escluse e il perche', e' in MAZZO_ASTICELLA.md
                 ("77 G18", "risultati_ventesima/settimane_G18.csv.gz"),
                 ("79 P9A", "../programma9/risultati_prima/settimane_79_P9A.csv.gz"),
                 ("80 P9B", "../programma9/risultati_prima/settimane_80_P9B.csv.gz"),
                 ("85 G21", "risultati_ventitreesima/settimane_G21.csv.gz"), ("87 PC", "risultati_venticinquesima/settimane_PC.csv.gz"),
                 ("109 GR-L", "risultati_quarantasettesima/settimane_GR-L.csv.gz"),
                 ("109 GR-N", "risultati_quarantasettesima/settimane_GR-N.csv.gz"),
                 ("112 LQ", "risultati_cinquantesima/settimane_LQ.csv.gz"),
                 ("114 KP", "risultati_cinquantaduesima/settimane_KP.csv.gz"), ("116 VU", "risultati_cinquantaquattresima/settimane_VU.csv.gz"),
                 ("117 EMI", "risultati_cinquantacinquesima/settimane_EMI.csv.gz"),
                 ("117 EWIL", "risultati_cinquantacinquesima/settimane_EWIL.csv.gz"),
                 ("118 MV", "risultati_cinquantaseiesima/settimane_MV.csv.gz"), ("119 CU", "risultati_cinquantasettesima/settimane_CU.csv.gz"),
                 ("121 RR", "risultati_cinquantanovesima/settimane_RR.csv.gz"), ("122 RRE", "risultati_sessantesima/settimane_RRE.csv.gz"),
                 ("123 RRB", "risultati_sessantunesima/settimane_RRB.csv.gz"), ("124 G1M", "risultati_sessantaduesima/settimane_G1M.csv.gz"),
                 ("125 PA", "risultati_sessantatreesima/settimane_PA.csv.gz"), ("125 AV", "risultati_sessantatreesima/settimane_AV.csv.gz"),
                 ("127 RA", "risultati_sessantacinquesima/settimane_RA.csv.gz"),
                 ("131 DA", "risultati_sessantanovesima/settimane_DA.csv.gz"), ("131 DB", "risultati_sessantanovesima/settimane_DB.csv.gz"),
                 ("132 FM", "risultati_settantesima/settimane_FM.csv.gz"), ("135 HL", "risultati_settantatreesima/settimane_HL.csv.gz"),
                 ("137 HLI", "risultati_settantacinquesima/settimane_HLI_101-200.csv.gz"),
                 ("138 GA1", "risultati_settantaseiesima/settimane_GA1.csv.gz"), ("138 GA2", "risultati_settantaseiesima/settimane_GA2.csv.gz"),
                 ("142 G1S", "risultati_ottantesima/settimane_G1S.csv.gz"),
                 ("143 SM", "risultati_ottantunesima/settimane_SM.csv.gz"), ("144 FP", "risultati_ottantaduesima/settimane_FP.csv.gz"),
                 ("145 NV", "risultati_ottantatreesima/settimane_NV.csv.gz"), ("147 GA2C", "risultati_ottantacinquesima/settimane_GA2C.csv.gz"),
                 ("150 v7", "risultati_ottantottesima/settimane_v7.csv.gz"), ("150 v30", "risultati_ottantottesima/settimane_v30.csv.gz")):
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
        s = pd.Series(0.01 * d["R"].to_numpy(), index=g).groupby(level=0).sum()
        # 27 novembre 2026 (audit esame-8): le settimane senza operazioni valgono zero, come in `qu.portafoglio` (prima c'erano solo
        # le 150 settimane operate, con salti fino a 126 giorni: Sharpe -1,94 invece di -1,35 sulle 301 settimane)
        out["68 G10"] = s.reindex(np.arange(int(s.index.min()), int(s.index.max()) + 1, 7)).fillna(0.0)
    out.update(_eventi_mancanti(p7))
    f = p7 / "risultati_ottantaseiesima" / "giorni.csv.gz"            # 148: la sola regola nuova (B), dai giorni alle settimane
    if f.exists():
        d = pd.read_csv(f, index_col=0)
        out["148 B"] = d["B, 280 USDT"].groupby(_lunedi(d.index)).sum()
    f = p7 / "risultati_ottantasettesima" / "settimane.csv.gz"        # 149: le 60 varianti 1:1:1
    if f.exists():
        d = pd.read_csv(f, index_col=0)
        out.update({f"149 {c}": d[c] for c in d.columns})
    f = p7 / "risultati_novantesima" / "settimane_conto1.csv.gz"     # 152: le tre varianti (G1 accanto e' la copia della 57)
    if f.exists():
        d = pd.read_csv(f, index_col=0)
        out.update({f"152 {v}": d[v] for v in ("V1", "V2", "V3")})
    for n, cartella in ((154, "risultati_novantaduesima"), (155, "risultati_novantatreesima"),
                        (156, "risultati_novantaquattresima"), (157, "risultati_novantacinquesima"),
                        (158, "risultati_novantaseiesima"), (159, "risultati_novantasettesima"),
                        (160, "risultati_novantottesima"), (161, "risultati_novantanovesima"),
                        (162, "risultati_centesima"), (163, "risultati_centounesima"),
                        (165, "risultati_centotreesima"), (168, "risultati_centosesta"),
                        (169, "risultati_centosettima_bis")):                                   # 154-169: A e B
        for v in ("A", "B"):                                                                     # non i controlli di ritardo)
            f = p7 / cartella / f"settimane_{v}.csv.gz"
            if f.exists():
                out[f"{n} {v}"] = pd.read_csv(f, index_col=0)["netto"]
    f = p7 / "risultati_quarantottesima" / "settimane_SS.csv.gz"     # 110: il file mette la vendita del venerdi' g0 al lunedi'
    if f.exists():                                                    # g0 - 4; si chiude il venerdi' g0 + 7: settimana del lunedi' g0 + 3
        s = pd.read_csv(f, index_col=0)["netto"]
        out["110 SS"] = pd.Series(s.to_numpy(), index=s.index.to_numpy() + 7)
    f = p7 / "risultati_settantasettesima" / "settimane_CF.csv"      # 139: 3 settimane etichettate di domenica (rapporto del lunedi'
    if f.exists():                                                    # + 6): vanno al lunedi' dopo, che nel file manca
        s = pd.read_csv(f, index_col=0)["netto"]
        i = s.index.to_numpy()
        out["139 CF"] = pd.Series(s.to_numpy(), index=i + (7 - (i + 3) % 7) % 7)
    return out


# Le cartelle di risultati con un file di serie o di eventi che restano fuori dal mazzo, e perche' (12 novembre, backlog P34;
# l'elenco intero in MAZZO_ASTICELLA.md). Il test `tests/test_asticella_mazzo.py` fallisce se una cartella di risultati dalla
# prova 49 in poi ha una serie o degli eventi ma non e' ne' nel mazzo ne' qui.
FUORI_DAL_MAZZO = {
    "programma6/risultati_cinquantesima": "prova 50: conferma, il registro non la conta (fuori come le conferme 7, 22, 27, 38)",
    "programma7/risultati_quarantaquattresima": "prova 106: conferma, il registro non la conta",
    "programma7/risultati_centocinquesima": "prova 167: campione troppo piccolo (26 eventi), nessun rendimento calcolato, non entra nel conto",
}

# Le varianti che il registro conta e che non sono nel mazzo delle serie, con il perche' (il test confronta il registro con il
# mazzo prova per prova).
DIFFERENZE_DAL_REGISTRO = {
    89: "il registro conta 2 (F5C e il controllo col fattore mescolato, VENTISETTESIMA.md); nel mazzo solo F5C: un controllo non e' "
        "una strategia provata",
}


def senza_serie() -> list:
    """(nome, Sharpe) delle varianti dalla 49 in poi che il registro conta senza una serie salvata nel mazzo: contano ognuna come
    un gruppo a se' (ASTICELLA.md, sezione 3: «scelta prudente: N piu' alto»), come le prove 1 e 2B. Lo Sharpe e' un ``Solo``
    con le settimane su cui e' misurato, che ``per_v`` usa per il t (27 novembre 2026, audit esame-4; prima 300 per tutte).

    * 108 (18 varianti) e 111 (8): lo Sharpe non e' salvato; ogni variante perde lo 0,11% a operazione dopo i costi con p 1,00
      (``esame.json``): t molto sotto -3, quindi entrano in N e non in V qualunque sia il valore. Il -10 e' convenzionale; le
      settimane sono quelle del periodo delle prove (dal 1° gennaio 2024 al 30 settembre 2026, QUARANTASEIESIMA.md, sezione 2).
    * 110, la chiamata coperta: lo Sharpe di ``esame.json`` (``CC_opzioni``, mensile), sui suoi 66 mesi (286 settimane).
    * 151: lo Sharpe della sua serie nel periodo, sulle sue 19 settimane (la prova si e' fermata per dati troppo corti, senza esame).
    * 153: la prova ha salvato solo i riassunti del segnale, non le serie: lo Sharpe e le settimane (196) delle varianti A e B da
      ``esame.json``."""
    p7 = QUI.parent / "programma7"
    out = []
    w108 = round((sc.giorno(2026, 9, 30) - sc.giorno(2024, 1, 1) + 1) / 7)
    for n, cartella in ((108, "risultati_quarantaseiesima"), (111, "risultati_quarantanovesima")):
        f = p7 / cartella / "esame.json"
        if f.exists():
            out += [(f"{n} {k}", Solo(-10.0, w108)) for k in json.loads(f.read_text())]
    f = p7 / "risultati_quarantottesima" / "esame.json"
    if f.exists():
        cc = json.loads(f.read_text())["CC_opzioni"]
        out.append(("110 CC", Solo(float(cc["sharpe"]), round(cc["portafoglio"]["n"] * 52 / 12))))
    f = p7 / "risultati_ottantanovesima" / "settimane.csv"
    if f.exists():
        d = pd.read_csv(f, index_col=0)
        d = d[d["fatta"].astype(bool)]
        s = periodo(pd.Series(d["netto"].to_numpy(), index=[sc.giorno(*map(int, x.split("-"))) for x in d.index]))
        out.append(("151 WE", Solo(sharpe(s), int(s.notna().sum()))))
    f = p7 / "risultati_novantunesima" / "esame.json"
    if f.exists():
        v = json.loads(f.read_text())["varianti"]
        out += [(f"153 {k}", Solo(float(v[k]["sharpe"]), int(v[k]["settimane"]))) for k in ("A", "B")]
    return out


def mazzo(nuove: dict | None = None, fino_alla: int | None = None) -> tuple:
    """Il mazzo completo dell'esame: (serie settimanali nel periodo, Sharpe delle prove senza serie, come ``Solo`` con le loro
    settimane). ``nuove`` = serie da aggiungere (una prova appena calcolata); a parita' di nome sostituiscono quelle del mazzo.
    ``fino_alla`` = solo le prove del mazzo fino a quel numero (per una strategia gia' scelta, il mazzo di quando e' stata scelta:
    decisione del 23 novembre; G1 alla 57: 102 serie, 65 famiglie); le ``nuove`` entrano comunque."""
    def dentro(nome: str) -> bool:
        return fino_alla is None or (_numero_prova(nome) or 0) <= fino_alla

    prove = le_prove()
    serie = {n: periodo(s) for n, s, _ in prove if s is not None and dentro(n)}
    serie.update({n: periodo(s) for n, s in serie_nuove().items() if dentro(n)})
    serie.update({n: periodo(s) for n, s in (nuove or {}).items()})
    soli = [Solo(sr) for n, s, sr in prove if s is None and dentro(n)] + [sr for n, sr in senza_serie() if dentro(n)]
    return serie, soli


def corretto_famiglie(nuove: dict, candidate: dict, taglio: float = TAGLIO) -> dict:
    """La probabilita' dell'esame di oggi (decisione dell'11 novembre): lo Sharpe corretto con N = famiglie di prove simili e V con
    l'aggiunta del 23 ottobre, sul mazzo completo (``mazzo``) piu' le serie ``nuove`` = {nome: serie settimanale netta}.
    ``candidate`` = {nome: {"sharpe", "settimane", "asimmetria", "curtosi"}}. Dal 27 novembre 2026 l'esame intero (probabilita', t,
    ogni anno positivo, verdetto e i numeri non ufficiali accanto) e' `esame`, che da' la stessa probabilita'; questa resta per le
    prove che la chiamano gia'."""
    serie, soli = mazzo(nuove)
    gr = gruppi(serie, taglio)
    sr_g, sr_v = per_v(gr, soli, False), per_v(gr, soli, True)
    out = {"serie": len(serie), "senza_serie": len(soli), "famiglie": len(sr_g), "in_v": len(sr_v),
           "deviazione_v": float(np.std(sr_v, ddof=1)), "taglio": taglio, "candidate": {}}
    for nome, i in candidate.items():
        out["candidate"][nome] = {
            "corretto": te.sharpe_corretto(i["sharpe"], i["settimane"], i["asimmetria"], i["curtosi"], sr_v, 52, n_prove=len(sr_g)),
            "t": i["sharpe"] * math.sqrt(i["settimane"] / 52),
            "gruppo": next((g["membri"] for g in gr if nome in g["membri"]), [nome])}
    return out


# ---------------------------------------------------------------------------------------------------------------------------------
# L'esame in vigore in una funzione sola, con i numeri non ufficiali accanto (27 novembre 2026; ASTICELLA.md, sezione 6)
# ---------------------------------------------------------------------------------------------------------------------------------

def _numero_prova(nome: str) -> int | None:
    """Il numero della prova dal nome della serie («157 A» -> 157, «2A A1» -> 2); None se il nome non comincia con un numero."""
    m = re.match(r"\d+", nome)
    return int(m.group()) if m else None


def varianza_lunga(x, ritardi: int) -> float:
    """La varianza di lungo periodo di Newey e West (1987, pesi di Bartlett) con ``ritardi`` settimane; con 0 ritardi e' la varianza
    semplice (divisa per n)."""
    v = np.asarray(pd.Series(x, dtype=float).dropna(), dtype=float)
    u = v - v.mean()
    n = len(u)
    s = float(u @ u) / n
    for k in range(1, min(int(ritardi), n - 1) + 1):
        s += 2.0 * (1.0 - k / (ritardi + 1.0)) * float(u[k:] @ u[:-k]) / n
    return s


def rapporto_robusto(x, ritardi: int) -> float:
    """Varianza semplice (divisa per n) / varianza di lungo periodo (`varianza_lunga`): le settimane efficaci sono le settimane per
    il rapporto e il t robusto e' il t per la radice del rapporto (con 0 ritardi il rapporto e' 1). Sotto 1 quando le settimane sono
    legate a quelle prima (G1: correlazione 0,19 con la settimana prima; audit del 26 novembre, esame-2)."""
    v = np.asarray(pd.Series(x, dtype=float).dropna(), dtype=float)
    lunga = varianza_lunga(v, ritardi)
    return float(v.var() / lunga) if lunga > 0 and v.var() > 0 else 1.0


def _anni(x: pd.Series):
    x = x.dropna()
    return x, pd.to_datetime(x.index.to_numpy() * 86400, unit="s").year


def per_anno(x: pd.Series) -> dict:
    """Ogni anno solare (l'anno del lunedi' della settimana): la media delle settimane per 52, come `terza.esame` (stesso segno della
    somma; gli anni parziali compresi, qualunque sia la loro lunghezza)."""
    x, anni = _anni(x)
    return {int(a): float(v * 52) for a, v in x.groupby(anni).mean().items()}


def per_anno_composto(x: pd.Series) -> dict:
    """Ogni anno solare sul conto composto (prodotto di 1 piu' il rendimento delle settimane, meno 1). NON ufficiale: si mostra accanto
    (audit del 26 novembre, esame-9: un anno con la somma positiva puo' essere una perdita sul conto)."""
    x, anni = _anni(x)
    return {int(a): float(v) for a, v in ((1 + x).groupby(anni).prod() - 1).items()}


def verdetto(annuo: float, anni: dict, t: float, probabilita: float) -> str:
    """Il verdetto dell'esame in vigore: «PROMETTENTE» se il netto e' positivo, ogni anno e' positivo, il t e' da 3 e la probabilita'
    che non sia fortuna e' da 0,80; altrimenti «NON PROMETTENTE» con i motivi (come `programma7.centosesta.esito_regole`)."""
    m = []
    if not annuo > 0:
        m.append("netto non positivo")
    neg = [a for a, v in sorted(anni.items()) if not v > 0]
    if not anni:
        m.append("anni non misurati")
    elif neg:
        m.append("anni non positivi " + ",".join(map(str, neg)))
    if not t >= SOGLIA_T:
        m.append(f"t {t:.2f} sotto 3")
    if not probabilita >= SOGLIA_PROBABILITA:
        m.append(f"probabilita' che non sia fortuna {probabilita:.2f} sotto 0,80")
    return "PROMETTENTE" if not m else "NON PROMETTENTE: " + "; ".join(m)


def _senza(gr: list, serie: dict, via) -> list:
    """Le famiglie con le serie ``via`` tolte dalla loro media; una famiglia che resta vuota non entra in V (in N resta: la prova e'
    stata fatta)."""
    via, out = set(via), []
    for g in gr:
        resto = [m for m in g["membri"] if m not in via]
        if len(resto) == len(g["membri"]):
            out.append(g)
        elif resto:
            media = pd.concat([serie[m] for m in resto], axis=1).mean(axis=1)
            out.append({"membri": resto, "sharpe": sharpe(media), "settimane": int(media.notna().sum())})
    return out


def esame(nuove: dict | None = None, candidate=None, taglio: float = TAGLIO, base: tuple | None = None) -> dict:
    """**L'esame in vigore** in una funzione sola (27 novembre 2026; backlog P34 e P37, audit del 26 novembre, esame-10) e accanto i
    numeri NON ufficiali da mostrare al proprietario finche' non decide (ASTICELLA.md, sezione 6). Qui le regole non cambiano.

    In vigore (decisioni del 9, 11 e 23 novembre, `docs/decisioni_del_proprietario.md`): «PROMETTENTE» se il netto e' positivo, ogni
    anno solare e' positivo (`per_anno`), il t dello Sharpe (Sharpe per la radice di settimane/52) e' da 3 e la probabilita' che non
    sia fortuna (`terza.sharpe_corretto`: N = famiglie del mazzo di oggi, V senza le famiglie con il t sotto -3) e' da 0,80. La
    probabilita' e' la stessa di `corretto_famiglie`. Una strategia gia' scelta (G1: prova 57, 0,945) si giudica con lo sconto una
    volta sola, quando e' stata scelta (23 novembre): il numero sul mazzo di oggi per lei e' solo un confronto.

    Accanto, NON ufficiali (non decidono niente; ognuno cambia una regola sola rispetto a quella in vigore):
    (a) senza le serie a incasso quasi fisso (le prove ``INCASSO_FISSO``, backlog P34, 15 novembre): famiglie rifatte senza di loro;
    (b) V simmetrica (fuori da V anche le famiglie con il t sopra +3; restano in N) e senza le serie ``BOCCIATE_DAL_REVISORE``;
    (c) il t robusto di Newey e West (``RITARDI`` settimane; ``RITARDI_CONTROLLO`` come controllo) e la probabilita' con le
        settimane efficaci (settimane per `rapporto_robusto`, sulla serie della candidata) al posto delle settimane;
    (d) (b) e (c) insieme.
    Piu' ogni anno sul conto composto (`per_anno_composto`), solo da mostrare.

    ``nuove``: {nome: serie settimanale netta} da aggiungere al mazzo (la prova appena calcolata; a parita' di nome sostituiscono).
    ``candidate``: i nomi da giudicare (misure dalla loro serie nel mazzo con `terza.numeri_settimana`, anni con `per_anno`) oppure
    {nome: misure} con "sharpe", "settimane", "asimmetria", "curtosi" e, se ci sono, "annuo" e "per_anno" (dall'esame della prova);
    la serie con quel nome nel mazzo (o con il nome in "serie", se le misure sono di un'altra misura della stessa strategia) serve
    per il t robusto, gli anni che mancano e gli anni composti. Senza ``candidate``: i nomi di ``nuove``.
    ``base``: (serie, soli) di `mazzo` gia' costruito, per non rileggerlo (le ``nuove`` si aggiungono sopra).
    Le correlazioni si calcolano una volta sola: il tempo e' circa quello di `gruppi`."""
    if base is None:
        serie, soli = mazzo(nuove)
    else:
        serie, soli = dict(base[0]), list(base[1])
        serie.update({n: periodo(s) for n, s in (nuove or {}).items()})
    if candidate is None:
        candidate = list(nuove or {})
    if not isinstance(candidate, dict):
        candidate = {n: None for n in candidate}
    nomi, R = correlazioni(serie)
    gr = gruppi(serie, taglio, (nomi, R))
    sr_n, sr_v = per_v(gr, soli, False), per_v(gr, soli, True)
    N = len(sr_n)
    k = [i for i, n in enumerate(nomi) if _numero_prova(n) not in INCASSO_FISSO]                      # (a)
    nomi_a = [nomi[i] for i in k]
    gr_a = gruppi({n: serie[n] for n in nomi_a}, taglio, (nomi_a, R[np.ix_(k, k)]))
    sr_n_a, sr_v_a = per_v(gr_a, soli, False), per_v(gr_a, soli, True)
    gr_b = _senza(gr, serie, BOCCIATE_DAL_REVISORE)                                                    # (b)
    sr_v_b = per_v(gr_b, soli, True, simmetrica=True)

    def mazzo_di(n_, v_):
        return {"famiglie": n_, "in_v": len(v_), "deviazione_v": float(np.std(v_, ddof=1)), "v": [float(x) for x in v_]}

    def tv(g):
        return g["sharpe"] * math.sqrt(g["settimane"] / 52)

    out = {"in_vigore": {"serie": len(serie), "senza_serie": len(soli), "taglio": taglio, **mazzo_di(N, sr_v)},
           "a_senza_incasso_fisso": {"tolte": [n for n in nomi if n not in set(nomi_a)], "serie": len(nomi_a),
                                     **mazzo_di(len(sr_n_a), sr_v_a)},
           "b_v_simmetrica_senza_bocciate": {"bocciate": [n for n in BOCCIATE_DAL_REVISORE if n in serie], **mazzo_di(N, sr_v_b),
                                             "fuori_da_v_vincenti": [g["membri"] for g in gr_b if tv(g) > -T_PERDENTI]},
           "gruppi": gr, "candidate": {}}
    for nome, date in candidate.items():
        chi = (date or {}).get("serie", nome)                       # la serie del mazzo della candidata (di norma, il suo nome)
        x = serie[chi].dropna() if chi in serie else None
        x = x if x is not None and len(x) > 2 else None
        mis = {**(te.numeri_settimana(x) if x is not None else {}), **{k_: v_ for k_, v_ in (date or {}).items() if k_ != "serie"}}
        sh, w, asim, curt = (float(mis[c]) for c in ("sharpe", "settimane", "asimmetria", "curtosi"))
        annuo = float(mis["annuo"])
        anni = mis.get("per_anno")
        anni = {int(a): float(v) for a, v in anni.items()} if isinstance(anni, dict) else (per_anno(x) if x is not None else {})
        t = sh * math.sqrt(w / 52)
        p = te.sharpe_corretto(sh, w, asim, curt, sr_v, 52, n_prove=N)
        p_a = te.sharpe_corretto(sh, w, asim, curt, sr_v_a, 52, n_prove=len(sr_n_a))
        p_b = te.sharpe_corretto(sh, w, asim, curt, sr_v_b, 52, n_prove=N)
        resto = annuo > 0 and bool(anni) and all(v > 0 for v in anni.values())        # le condizioni che (a)-(d) non cambiano
        c = {"a_senza_incasso_fisso": {"probabilita": p_a, "passerebbe": bool(resto and t >= SOGLIA_T and p_a >= SOGLIA_PROBABILITA)},
             "b_v_simmetrica_senza_bocciate": {"probabilita": p_b,
                                               "passerebbe": bool(resto and t >= SOGLIA_T and p_b >= SOGLIA_PROBABILITA)},
             "c_t_robusto": None, "d_b_e_c": None}
        if x is not None:
            rob = {}
            for L in (RITARDI, RITARDI_CONTROLLO):
                r = rapporto_robusto(x, L)
                w_eff = max(3, int(round(w * r)))
                rob[L] = {"ritardi": L, "rapporto": r, "settimane_efficaci": w_eff, "t": sh * math.sqrt(w * r / 52),
                          "probabilita": te.sharpe_corretto(sh, w_eff, asim, curt, sr_v, 52, n_prove=N),
                          "probabilita_d": te.sharpe_corretto(sh, w_eff, asim, curt, sr_v_b, 52, n_prove=N)}
            b4, b13 = rob[RITARDI], rob[RITARDI_CONTROLLO]
            c["c_t_robusto"] = {**{k_: b4[k_] for k_ in ("ritardi", "rapporto", "settimane_efficaci", "t", "probabilita")},
                                "controllo": {k_: b13[k_] for k_ in ("ritardi", "rapporto", "settimane_efficaci", "t", "probabilita")},
                                "passerebbe": bool(resto and b4["t"] >= SOGLIA_T and b4["probabilita"] >= SOGLIA_PROBABILITA)}
            c["d_b_e_c"] = {"probabilita": b4["probabilita_d"], "controllo": b13["probabilita_d"],
                            "passerebbe": bool(resto and b4["t"] >= SOGLIA_T and b4["probabilita_d"] >= SOGLIA_PROBABILITA)}
            comp = per_anno_composto(x)
            c["per_anno_composto"], c["ogni_anno_positivo_composto"] = comp, all(v > 0 for v in comp.values())
        out["candidate"][nome] = {
            "misure": {"sharpe": sh, "settimane": w, "asimmetria": asim, "curtosi": curt, "annuo": annuo}, "serie": chi,
            "gruppo": next((g["membri"] for g in gr if chi in g["membri"]), [chi]),
            "in_vigore": {"probabilita": p, "t": t, "per_anno": anni,
                          "ogni_anno_positivo": bool(anni) and all(v > 0 for v in anni.values()), "esito": verdetto(annuo, anni, t, p)},
            "non_ufficiali": c}
    return out


def sharpe_minimo(settimane: float, v: list, n_prove: int, probabilita: float = SOGLIA_PROBABILITA) -> float:
    """Lo Sharpe che serve, con rendimenti normali (asimmetria 0, curtosi 3), per arrivare a ``probabilita`` su ``settimane`` con
    la dispersione ``v`` e N = ``n_prove`` (audit del 26 novembre, punti ciechi 1). Accanto vale anche il t da 3: Sharpe almeno
    3 per la radice di 52/settimane."""
    lo, hi = -5.0, 20.0
    for _ in range(100):
        mid = (lo + hi) / 2
        if te.sharpe_corretto(mid, settimane, 0.0, 3.0, v, 52, n_prove=n_prove) < probabilita:
            lo = mid
        else:
            hi = mid
    return hi


def _eventi_mancanti(p7: Path) -> dict:
    """Le prove a eventi dalla 75 alla 146 che mancavano (12 novembre, backlog P34), con il portafoglio della prova 41 come le altre
    a eventi: entrata e uscita all'ora (quando il file da' solo il giorno, la mezzanotte del giorno), solo le operazioni con ``r``.
    Ogni serie porta in ``attrs["eventi"]`` quante operazioni ha usato (il test le confronta con il registro)."""
    def gg(x: pd.Series) -> np.ndarray:
        return x.map(lambda s: sc.giorno(*map(int, str(s)[:10].split("-")))).to_numpy().astype(np.int64)

    def port(d: pd.DataFrame, ora, uscita, simbolo="BTCUSDT", r="r") -> pd.Series:
        ev = pd.DataFrame({"simbolo": d[simbolo].to_numpy() if simbolo in d else simbolo,
                           "ora": np.asarray(ora, dtype=np.int64), "uscita_h": np.asarray(uscita, dtype=np.int64), "r": d[r].to_numpy()})
        ev = ev[np.isfinite(ev["r"])]
        s = qu.portafoglio(ev)["netto"]
        s.attrs["eventi"] = int(len(ev))
        return s

    def leggi(f: str) -> pd.DataFrame | None:
        return pd.read_csv(p7 / f) if (p7 / f).exists() else None

    def minuti(d):                                                    # entrata_min / uscita_min (minuti dal 1970)
        return d["entrata_min"].to_numpy() // 60, -(-d["uscita_min"].to_numpy() // 60)

    def ore(d):                                                       # dal giorno della colonna data per le ore della colonna ore
        o = gg(d["data"]) * 24
        return o, o + d["ore"].to_numpy()

    def giorni(d):                                                    # come G4: dal giorno per i giorni della colonna giorni
        o = gg(d["data"]) * 24
        return o, o + np.round(d["giorni"].to_numpy() * 24).astype(np.int64)

    out = {}
    for n, f in (("75 G16", "risultati_diciottesima/eventi_G16.csv"), ("76 G17", "risultati_diciannovesima/eventi_G17.csv"),
                 ("78 G19", "risultati_ventunesima/eventi_G19.csv")):
        d = leggi(f)
        if d is not None:
            out[n] = port(d, *minuti(d), simbolo="simbolo")
    for n, f in (("81 P9C", "../programma9/risultati_seconda/eventi_P9C.csv"),          # 81 e 82: solo con i long affollati,
                 ("82 P9C lunga", "../programma9/risultati_terza/eventi_P9C_lunga.csv")):  # come le regole (seconda.py:93-94,
        d = leggi(f)                                                                     # terza.py:31-32; SOGLIA_8H 0,0001)
        if d is not None:
            d = d[d["funding_8h"].notna() & (d["funding_8h"] >= 0.0001)].reset_index(drop=True)
            out[n] = port(d, *minuti(d), simbolo="simbolo")
    parti = [leggi(f"risultati_quarantaduesima/eventi_G26_{p}.csv") for p in ("2021-2022", "2023-2024", "2025-2026")]
    if all(p is not None for p in parti):
        d = pd.concat(parti, ignore_index=True)
        out["104 G26"] = port(d, *minuti(d), simbolo="simbolo")
    for n, f in (("105 CB", "risultati_quarantatreesima/eventi_CB.csv"),
                 ("107 G13C", "risultati_quarantacinquesima/eventi_G13C.csv"), ("126 GT", "risultati_sessantaquattresima/eventi_GT.csv"),
                 ("140 QH", "risultati_settantottesima/eventi_QH.csv"), ("146 AT", "risultati_ottantaquattresima/eventi_AT.csv")):
        d = leggi(f)
        if d is not None:
            out[n] = port(d, *ore(d), simbolo="simbolo")
    d = leggi("risultati_settantaduesima/picchi_PM.csv")                          # 134: solo i picchi con la bandiera
    if d is not None:
        d = d[d["bandiera"].astype(bool)].reset_index(drop=True)
        out["134 PM"] = port(d, *ore(d), simbolo="simbolo")
    d = leggi("../programma9/risultati_quarta/eventi_N3B_funding.csv")             # 83: solo con i long affollati (SOGLIA_8H)
    if d is not None:
        d = d[d["funding_8h"] >= 0.0001].reset_index(drop=True)
        out["83 P9D"] = port(d, *giorni(d), simbolo="simbolo")
    d = leggi("risultati_ventottesima/eventi_N3V.csv")                             # 90: il gruppo A, «davvero nuove»
    if d is not None:
        d = d[d["gruppo"] == "A davvero nuove"].reset_index(drop=True)
        out["90 N3V"] = port(d, *giorni(d), simbolo="simbolo")
    d = leggi("risultati_ventinovesima/eventi_N3B2.csv")
    if d is not None:
        out["91 N3B2"] = port(d, *giorni(d), simbolo="simbolo")
    d, d32 = leggi("risultati_cinquantunesima/eventi_N3G.csv"), QUI / "risultati_trentaduesima" / "eventi_N3B.csv"
    if d is not None and d32.exists():                                           # 113: le monete gratis, durate dalla prova 32
        d = d[d["gratis"].astype(bool)].merge(pd.read_csv(d32)[["data", "simbolo", "giorni"]], on=["data", "simbolo"], how="left")
        out["113 N3G"] = port(d, *giorni(d), simbolo="simbolo")
    d = leggi("risultati_settantanovesima/eventi_FS.csv")                          # 141: 7 giorni (l'uscita a -30% non ha l'ora)
    if d is not None:
        o = gg(d["data"]) * 24
        out["141 FS"] = port(d, o, o + 7 * 24, simbolo="simbolo")
    for n, f in (("96 G22", "risultati_trentaquattresima/eventi_G22.csv"), ("98 G23", "risultati_trentaseiesima/eventi_G23.csv")):
        d = leggi(f)                                                              # dall'ora dopo il comunicato, per 6 ore
        if d is not None:
            o = gg(d["data"]) * 24 + d["ora_utc"].to_numpy() + 1
            out[n] = port(d, o, o + 6)
    d = leggi("risultati_trentasettesima/operazioni_G24.csv")                      # 99: dalle 02:00 UTC del giorno, per 24 ore
    if d is not None:
        o = gg(d["giorno"]) * 24 + 2
        out["99 G24"] = port(d, o, o + 24)
    d = leggi("risultati_quarantunesima/eventi_LV.csv")                            # 103: solo i tagli della leva
    if d is not None:
        d = d[d["tipo"] == "taglio"].reset_index(drop=True)
        out["103 LV"] = port(d, d["h0"], d["h1"], simbolo="simbolo")
    d = leggi("risultati_cinquantatreesima/eventi_BL.csv")                         # 115: BNB contro Bitcoin, 24 ore
    if d is not None:
        o = d["entrata_min"].to_numpy() // 60
        out["115 BL"] = port(d, o, o + 24, simbolo="BNBUSDT")
    for n, f, k in (("128 BP", "risultati_sessantaseiesima/eventi_BP.csv", 4), ("130 TE", "risultati_sessantottesima/eventi_TE.csv", 24)):
        d = leggi(f)                                                              # dall'ora dopo il segnale, per k ore
        if d is not None:
            o = d["ora"].to_numpy() + 1
            out[n] = port(d, o, o + k, simbolo="simbolo")
    d = leggi("risultati_sessantasettesima/eventi_IM.csv")                         # 129: dall'ultimo giorno del mese, 4 giorni
    if d is not None:
        o = gg(d["data"]) * 24
        out["129 IM"] = port(d, o, o + 4 * 24)
    d = leggi("risultati_settantunesima/operazioni_primo.csv.gz")                  # 133: ogni 4 ore sui 6 perpetui
    if d is not None:
        out["133 QO"] = port(d, d["ora"], d["ora"] + 4, simbolo="moneta", r="netto")
    d = leggi("risultati_settantaquattresima/eventi_tondi.csv.gz")                 # 136: 60 minuti dal passaggio
    if d is not None:
        out["136 NT"] = port(d, d["minuto"].to_numpy() // 60, -(-(d["minuto"].to_numpy() + 61) // 60), simbolo="moneta")
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
