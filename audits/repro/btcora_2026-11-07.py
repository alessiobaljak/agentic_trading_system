"""Audit del 7 novembre 2026, prova BTCORA (research/collaudo_agenti/btcora/ (prima research/prova_finta_audit/)): riproduzione e controlli.

Non modifica nulla fuori da audits/: importa le funzioni della prova (dati, segnali, conto) senza chiamare main(), che
riscriverebbe research/collaudo_agenti/btcora/risultati.json. Scrive solo audits/repro/btcora_2026-11-07_esito.json.

Uso (dalla radice del repo): python3 audits/repro/btcora_2026-11-07.py
"""
from __future__ import annotations

import json
import sys
import warnings
from pathlib import Path

RADICE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RADICE))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from research.collaudo_agenti.btcora import strategia as st  # noqa: E402
from research.programma6 import seconda as sc  # noqa: E402
from research.programma6 import controllo_giorni as cg  # noqa: E402
from research.programma6 import buchi_archivio as ba  # noqa: E402  (solo giorni_mancanti: lettura, niente rete)
from research.programma5.strumenti import motore5 as m5  # noqa: E402
from research.src.dati import funding_da_zip  # noqa: E402

QUI = Path(__file__).parent
ESITO = QUI / "btcora_2026-11-07_esito.json"
G0, G1 = sc.giorno(2023, 1, 1), sc.giorno(2024, 1, 1)


def sharpe(x: pd.Series, ann: int) -> float:
    return float(x.mean() / x.std() * np.sqrt(ann))


def sortino(x: pd.Series, ann: int) -> float:
    giu = x[x < 0]
    return float(x.mean() / np.sqrt((giu ** 2).sum() / len(x)) * np.sqrt(ann))


def discesa(per_giorno: pd.Series) -> dict:
    eq = per_giorno.cumsum()                     # capitale fisso, come la prova (somma dei rendimenti)
    picco = eq.cummax()
    dd = eq - picco
    fondo = int(dd.idxmin())
    inizio = int(eq.loc[:fondo].idxmax())
    dopo = eq.loc[fondo:]
    rec = dopo[dopo >= eq.loc[inizio]]
    fine = int(rec.index[0]) if len(rec) else None
    return {"discesa_max": float(dd.min()), "dal": sc.data(inizio), "fondo": sc.data(fondo),
            "recupero": sc.data(fine) if fine is not None else "mai nel periodo",
            "durata_giorni": (fine if fine is not None else int(per_giorno.index[-1])) - inizio}


def misure(ore: pd.DataFrame, netto: pd.Series, pos: pd.Series, costo_unit: float) -> dict:
    per_giorno = netto.groupby(ore.index // 24).sum()
    cambi = pos.diff().abs().fillna(0.0)
    n_cambi = int((cambi > 0).sum())
    lordo = (pos * ore["close"].pct_change(fill_method=None).fillna(0.0))
    mesi = pd.Series(per_giorno.values, index=pd.to_datetime(per_giorno.index * 86400, unit="s")).resample("ME").sum()
    guad = per_giorno.sum()
    top5 = per_giorno.sort_values(ascending=False).head(5).sum()
    top3m = mesi.sort_values(ascending=False).head(3).sum()
    composto = float(np.prod(1 + per_giorno.values) - 1)
    return {"giorni": int(len(per_giorno)), "cambi_di_posizione": n_cambi,
            "rendimento_somma": float(guad), "rendimento_composto": composto,
            "sharpe_252": sharpe(per_giorno, 252), "sharpe_365": sharpe(per_giorno, 365),
            "sortino_365": sortino(per_giorno, 365),
            "t_sharpe": float(per_giorno.mean() / per_giorno.std() * np.sqrt(len(per_giorno))),
            **discesa(per_giorno),
            "esposizione": float((pos != 0).mean()),
            "lordo_medio_per_cambio": float(lordo.sum() / max(1, n_cambi)),
            "costo_per_cambio_da_-1_a_+1": 2 * costo_unit,
            "quota_5_giorni_migliori": float(top5 / guad) if guad else None,
            "quota_3_mesi_migliori": float(top3m / guad) if guad else None,
            "giorno_peggiore": float(per_giorno.min()),
            "mesi": {k.strftime("%Y-%m"): round(float(v), 4) for k, v in mesi.items()}}


def regimi(ore: pd.DataFrame, netto: pd.Series) -> dict:
    """Clima di mercato per mese, definito qui (la prova non lo dichiara): rendimento di BTC nel mese > +5% rialzo,
    < -5% ribasso, altrimenti laterale."""
    c = pd.Series(ore["close"].values, index=pd.to_datetime(ore.index * 3600, unit="s"))
    r_mese = c.resample("ME").last() / c.resample("ME").first() - 1
    s = pd.Series(netto.values, index=pd.to_datetime(ore.index * 3600, unit="s")).resample("ME").sum()
    clima = np.where(r_mese > 0.05, "rialzo", np.where(r_mese < -0.05, "ribasso", "laterale"))
    out = {}
    for k in ("rialzo", "ribasso", "laterale"):
        m = clima == k
        out[k] = {"mesi": int(m.sum()), "rendimento_somma": round(float(s[m].sum()), 4)}
    return out


def funding_orario(ore: pd.DataFrame) -> tuple:
    """Funding vero alle ore di regolamento lette dai file: il regolamento al minuto m lo paga chi tiene l'ora
    (m-1)//60 (stessa convenzione di seconda.py, all'ora invece che al giorno)."""
    righe = []
    for p in sorted((sc.DATI / "BTCUSDT" / "funding").glob("*.zip")):
        righe += funding_da_zip(p)
    df = pd.DataFrame(righe, columns=["ts", "ore", "tasso"]).drop_duplicates("ts")
    df["minuto"] = df["ts"] // 60_000
    df = df[(df["minuto"] > G0 * 1440) & (df["minuto"] <= G1 * 1440)]
    ora_tenuta = (df["minuto"].to_numpy() - 1) // 60
    f_h = pd.Series(df["tasso"].to_numpy(float), index=ora_tenuta).groupby(level=0).sum()
    f_h = f_h.reindex(ore.index).fillna(0.0)
    minuti_del_giorno = (df["minuto"] % 1440).value_counts().sort_index()
    resto_ms = int((df["ts"] % 60_000).abs().max())
    info = {"regolamenti_2023": int(len(df)), "attesi_3_al_giorno": int(3 * (G1 - G0)),
            "minuto_del_giorno_dei_regolamenti": {int(k): int(v) for k, v in minuti_del_giorno.items()},
            "intervalli_dichiarati_ore": sorted(set(int(x) for x in df["ore"])),
            "scarto_massimo_dal_minuto_tondo_ms": resto_ms,
            "somma_tassi_2023": float(df["tasso"].sum())}
    # confronto con il pannello: i giorni che il pannello ha stimato (riempi_funding) invece di leggerli
    pan = sc.pannello()
    j = pan["simboli"].index("BTCUSDT")
    F = pd.Series(pan["funding"][G0 - pan["t0"]:G1 - pan["t0"], j], index=np.arange(G0, G1))
    vero = sc.funding_giorni("BTCUSDT").reindex(np.arange(G0, G1))
    info["giorni_senza_dato_vero_nel_pannello"] = int(vero.isna().sum())
    info["giorni_pannello_diverso_dal_vero"] = int((~np.isclose(F.values, vero.fillna(np.nan).values, atol=1e-12)).sum())
    return f_h, info


def controllo_dati(giorni: pd.DataFrame, ore: pd.DataFrame) -> dict:
    idx = ore.index.to_numpy()
    atteso = np.arange(G0 * 24, G1 * 24)
    r = ore["close"].pct_change(fill_method=None)
    oc = (ore["open"] / ore["close"].shift(1) - 1).abs()
    ultima = ore["close"].groupby(ore.index // 24).last()
    rel = (giorni["close"] / ultima.reindex(giorni.index) - 1).abs()
    mancanti = sorted(set(atteso) - set(idx))
    out = {"ore_attese": int(len(atteso)), "ore_presenti": int(len(idx)), "ore_mancanti": len(mancanti),
           "prime_ore_mancanti": [pd.Timestamp(h * 3600, unit="s").strftime("%Y-%m-%d %H:00") for h in mancanti[:10]],
           "ore_con_chiusura_nan": int(ore["close"].isna().sum()), "duplicati": int(pd.Index(idx).duplicated().sum()),
           "in_ordine": bool(pd.Index(idx).is_monotonic_increasing),
           "ore_oltre_il_periodo": int(((idx < G0 * 24) | (idx >= G1 * 24)).sum()),
           "rendimento_orario_max_assoluto": float(r.abs().max()),
           "ora_del_massimo": pd.Timestamp(int(r.abs().idxmax()) * 3600, unit="s").strftime("%Y-%m-%d %H:00"),
           "ore_oltre_5pct": int((r.abs() > 0.05).sum()),
           "salto_apertura_chiusura_prima_max": float(oc.max()),
           "high_sotto_low": int((ore["high"] < ore["low"]).sum()),
           "giorni": int(len(giorni)), "giorni_chiusura_nan": int(giorni["close"].isna().sum()),
           "chiusura_giorno_contro_ultima_ora_max_rel": float(rel.max()),
           "giorni_mancanti_archivio_dal_2023": [sc.data(g) for g in ba.giorni_mancanti("BTCUSDT", G0) if g < G1]}
    conf = cg.confronto("BTCUSDT")        # candele giornaliere contro quelle fatte dai minuti verificati (tutti gli anni)
    out["confronto_giorni_con_minuti_tutti_gli_anni"] = conf
    return out


def corsa(media: int, ritardo_giorni: int, ore0: pd.DataFrame, giorni0: pd.DataFrame, costo: float,
          f_h: pd.Series | None, piatto_senza_media: bool) -> tuple:
    """La stessa regola della prova, con: lunghezza della media, ritardo del segnale giornaliero (0 = come la prova,
    1 = il segnale chiuso a fine giorno d usato per tutte le ore del giorno d+1, dall'apertura della sua prima ora),
    costo per lato, funding orario e posizione nulla finché la media non esiste."""
    g = giorni0.copy()
    g["media"] = g["close"].rolling(media).mean()
    su = np.where(g["close"] > g["media"], 1.0, -1.0)
    if piatto_senza_media:
        su = np.where(g["media"].isna(), 0.0, su)
    su = pd.Series(su, index=g.index)
    o = ore0.copy()
    r = o["close"].pct_change(fill_method=None).fillna(0.0)
    if ritardo_giorni:
        # il rendimento dell'ora h (chiusura h-1 -> chiusura h) lo tiene la posizione decisa alla chiusura del giorno
        # prima di quello in cui l'ora apre: nessuna ora usa la chiusura del suo stesso giorno
        o["pos"] = (o.index // 24 - 1).map(su).astype(float) * st.LEVA
        pos = o["pos"].fillna(0.0)
    else:
        o["pos"] = (o.index // 24).map(su).astype(float) * st.LEVA
        pos = o["pos"].shift(1).fillna(0.0)          # come la prova
    cambi = pos.diff().abs().fillna(0.0)
    netto = pos * r - cambi * costo
    if f_h is not None:
        netto = netto - pos * f_h          # comprato (pos>0) paga il tasso positivo, venduto lo incassa
    return o, netto, pos


def main() -> int:
    giorni, ore = st.dati()
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        o_prova = st.segnali(giorni, ore)
        pg, sh = st.conto(o_prova, giorni)
        avvisi = sorted(set(str(x.message)[:160] for x in w))
    ris = json.loads((RADICE / "research" / "collaudo_agenti" / "btcora" / "risultati.json").read_text(encoding="utf-8"))
    rip = {"sharpe": round(sh, 2), "rendimento": round(float(pg.sum()), 4), "giorni": int(len(pg))}
    out = {"riproduzione": {"risultati_json": ris, "rieseguito": rip,
                            "uguale": all(ris[k] == rip[k] for k in rip), "avvisi": avvisi}}
    out["dati"] = controllo_dati(giorni, ore)

    # sguardo nel futuro: quale chiusura giornaliera usa la posizione di ogni ora
    pos = o_prova["pos"].shift(1)
    ora_del_giorno = o_prova.index % 24
    r = o_prova["close"].pct_change().fillna(0.0)
    contrib = (pos.fillna(0.0) * r)
    out["sguardo_nel_futuro"] = {
        "ore_in_cui_la_posizione_usa_la_chiusura_del_giorno_stesso": int((ora_del_giorno != 0).sum()),
        "ore_totali": int(len(o_prova)),
        "rendimento_medio_ora_0_(segnale_del_giorno_prima)": float(contrib[ora_del_giorno == 0].mean()),
        "rendimento_medio_ore_1_23_(segnale_del_giorno_stesso)": float(contrib[ora_del_giorno != 0].mean()),
        "giorni_senza_media_trattati_come_venduto": int(giorni["close"].rolling(20).mean().isna().sum())}

    f_h, info_f = funding_orario(ore)
    out["funding"] = info_f
    costo_vero = st.COSTO + m5.scarto("BTCUSDT")

    varianti = {
        "prova_come_scritta": (20, 0, st.COSTO, None, False),
        "prova_annualizzata_365": (20, 0, st.COSTO, None, False),
        "senza_sguardo_nel_futuro": (20, 1, st.COSTO, None, False),
        "senza_sguardo_con_funding": (20, 1, st.COSTO, f_h, False),
        "senza_sguardo_funding_scarto": (20, 1, costo_vero, f_h, False),
        "corretta_completa_(anche_piatto_senza_media)": (20, 1, costo_vero, f_h, True),
    }
    out["varianti"] = {}
    for nome, (n, rit, c, f, piatto) in varianti.items():
        o, netto, p = corsa(n, rit, ore, giorni, c, f, piatto)
        m = misure(o, netto, p, c)
        if nome == "corretta_completa_(anche_piatto_senza_media)":
            m["clima"] = regimi(o, netto)
            # liquidazione a leva 1: il rialzo più grande da un ingresso venduto finché la posizione resta venduta
            pz = o["close"]
            seg = (p != p.shift(1)).cumsum()
            peggio = 0.0
            for _, s in pz[p < 0].groupby(seg[p < 0]):
                peggio = max(peggio, float(s.max() / s.iloc[0] - 1))
            m["rialzo_massimo_contro_il_venduto"] = peggio
            m["giorni_sotto_-5pct"] = int((netto.groupby(o.index // 24).sum() < -0.05).sum())
        if nome != "prova_come_scritta":
            m.pop("mesi", None)
        out["varianti"][nome] = m

    # controllo incrociato della versione senza sguardo, con le sole candele giornaliere (lordo, senza costi)
    gg = giorni.copy()
    gg["m"] = gg["close"].rolling(20).mean()
    sg = pd.Series(np.where(gg["close"] > gg["m"], 1.0, -1.0), index=gg.index).shift(1)
    rd = gg["close"].pct_change(fill_method=None)
    out["controllo_giornaliero_lordo"] = {"senza_sguardo_somma": float((sg * rd).sum()),
                                          "con_lo_sguardo_(segnale_dello_stesso_giorno)_somma":
                                              float((np.where(gg["close"] > gg["m"], 1.0, -1.0) * rd).sum()),
                                          "btc_2023_comprato_e_tenuto": float(gg["close"].iloc[-1] / gg["close"].iloc[0] - 1)}

    # sensibilità: media 16, 18, 20, 22, 24 (±10% e ±20%), sulla prova e sulla versione corretta
    out["sensibilita"] = {}
    for n in (16, 18, 20, 22, 24):
        o, netto, p = corsa(n, 0, ore, giorni, st.COSTO, None, False)
        a = netto.groupby(o.index // 24).sum()
        o, netto, p = corsa(n, 1, ore, giorni, costo_vero, f_h, True)
        b = netto.groupby(o.index // 24).sum()
        out["sensibilita"][n] = {"prova_sharpe_365": round(sharpe(a, 365), 2), "prova_rendimento": round(float(a.sum()), 4),
                                 "corretta_sharpe_365": round(sharpe(b, 365), 2),
                                 "corretta_rendimento": round(float(b.sum()), 4)}
    ESITO.write_text(json.dumps(out, indent=1, ensure_ascii=False, default=str), encoding="utf-8")
    print(json.dumps(out, indent=1, ensure_ascii=False, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
