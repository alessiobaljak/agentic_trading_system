"""Programma 7, quarantottesima prova (QUARANTOTTESIMA.md): VO, vendere le opzioni su BTC ed ETH: la chiamata coperta mensile al +10% (CC)
e la vendita settimanale di un'opzione di acquisto e una di vendita al prezzo di oggi (SS). Prezzi stimati con Black e Scholes dalla
volatilita' implicita di Deribit a 30 giorni (DVOL): approssimazione dichiarata.

Uso: python3 -m research.programma7.quarantottesima
"""
from __future__ import annotations

import datetime as dt
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd

from research.programma6 import asticella as ast
from research.programma6 import esecuzione as es
from research.programma6 import seconda as sc
from research.programma6 import terza as te

QUI = Path(__file__).parent
RIS = QUI / "risultati_quarantottesima"
DVOL = QUI.parent / "data" / "dvol"
MONETE = {"BTC": "BTCUSDT", "ETH": "ETHUSDT"}
FEE, FEE_CAP, SCARTO_PREMIO, SETTLE = 0.0003, 0.125, 0.03, 0.00015
OTM = 0.10
FINE = dt.date(2026, 10, 23)


def _N(x: float) -> float:
    return 0.5 * (1 + math.erf(x / math.sqrt(2)))


def bs(S: float, K: float, T: float, sigma: float, call: bool) -> float:
    if T <= 0 or sigma <= 0:
        return max(0.0, (S - K) if call else (K - S))
    d1 = (math.log(S / K) + 0.5 * sigma * sigma * T) / (sigma * math.sqrt(T))
    d2 = d1 - sigma * math.sqrt(T)
    return S * _N(d1) - K * _N(d2) if call else K * _N(-d2) - S * _N(-d1)


def costo(S: float, premio: float) -> float:
    return min(FEE * S, FEE_CAP * premio) + SCARTO_PREMIO * premio


def venerdi(da: dt.date, a: dt.date) -> list:
    g = da + dt.timedelta(days=(4 - da.weekday()) % 7)
    out = []
    while g <= a:
        out.append(g)
        g += dt.timedelta(days=7)
    return out


def ultimi_venerdi(da: dt.date, a: dt.date) -> list:
    v = venerdi(da, a)
    return [x for x in v if (x + dt.timedelta(days=7)).month != x.month]


def prezzo(c: pd.DataFrame, g: dt.date) -> float:
    h = int(dt.datetime(g.year, g.month, g.day, 8, tzinfo=dt.timezone.utc).timestamp()) // 3600
    return float(c.loc[h, "open"]) if h in c.index and np.isfinite(c.loc[h, "open"]) else float("nan")


def esegui(log=print) -> dict:
    out, serie = {}, {}
    righe_cc, righe_ss = [], []
    for nome, simbolo in MONETE.items():
        dv = {int(k): float(v) for k, v in json.loads((DVOL / f"{nome}.json").read_text()).items()}
        c = es.ore_di(simbolo)
        primo = dt.date(1970, 1, 1) + dt.timedelta(days=min(dv) + 1)
        # CC: dall'ultimo venerdi' di un mese al successivo
        uv = ultimi_venerdi(primo, FINE)
        for g0, g1 in zip(uv[:-1], uv[1:]):
            S0, S1 = prezzo(c, g0), prezzo(c, g1)
            s = dv.get((g0 - dt.date(1970, 1, 1)).days - 1)
            if not (np.isfinite(S0) and np.isfinite(S1) and s):
                continue
            K = S0 * (1 + OTM)
            T = (g1 - g0).days / 365
            pr = bs(S0, K, T, s / 100, True)
            paga = max(0.0, S1 - K)
            opz = (pr - paga - costo(S0, pr) - (SETTLE * S1 if paga > 0 else 0.0)) / S0
            righe_cc.append({"moneta": nome, "data": str(g0), "premio": pr / S0, "pagato": paga / S0, "opzioni": opz,
                             "moneta_rend": S1 / S0 - 1, "totale": S1 / S0 - 1 + opz, "dvol": s})
        # SS: ogni venerdi'
        vv = venerdi(primo, FINE)
        for g0, g1 in zip(vv[:-1], vv[1:]):
            S0, S1 = prezzo(c, g0), prezzo(c, g1)
            s = dv.get((g0 - dt.date(1970, 1, 1)).days - 1)
            if not (np.isfinite(S0) and np.isfinite(S1) and s):
                continue
            T = 7 / 365
            pc_, pp_ = bs(S0, S0, T, s / 100, True), bs(S0, S0, T, s / 100, False)
            paga = abs(S1 - S0)
            r = (pc_ + pp_ - paga - costo(S0, pc_) - costo(S0, pp_) - SETTLE * S1) / S0
            lungo = (paga - pc_ - pp_ - costo(S0, pc_) - costo(S0, pp_) - SETTLE * S1) / S0       # lo specchio: comprare la volatilita'
            righe_ss.append({"moneta": nome, "data": str(g0), "premio": (pc_ + pp_) / S0, "pagato": paga / S0, "r": r, "comprare": lungo,
                             "dvol": s, "mossa": S1 / S0 - 1})
        log(f"[quarantottesima] {nome}: {sum(1 for x in righe_cc if x['moneta'] == nome)} mesi, {sum(1 for x in righe_ss if x['moneta'] == nome)} settimane")
    cc, ss = pd.DataFrame(righe_cc), pd.DataFrame(righe_ss)
    RIS.mkdir(exist_ok=True)
    cc.to_csv(RIS / "mesi_CC.csv", index=False)
    ss.to_csv(RIS / "settimane_SS.csv", index=False)

    def boot(x: np.ndarray, n: int = 10000) -> dict:
        rng = np.random.default_rng(2026)
        m = rng.choice(x, size=(n, len(x)), replace=True).mean(axis=1)
        return {"media": float(x.mean()), "basso": float(np.quantile(m, 0.025)), "alto": float(np.quantile(m, 0.975)),
                "p": float((np.sum(m <= 0) + 1) / (n + 1)), "n": int(len(x))}

    def descrivi(df: pd.DataFrame, col: str, per_anno_div: int) -> dict:
        port = df.groupby("data")[col].mean().sort_index()
        b = boot(port.to_numpy())
        anni = pd.to_datetime(port.index).year
        eq = (1 + port).cumprod()
        return {"portafoglio": b, "per_anno": {int(a): float(port[anni == a].mean() * per_anno_div) for a in sorted(set(anni))},
                "annuo": float(port.mean() * per_anno_div), "discesa": float((eq / eq.cummax() - 1).min()), "peggiori": port.nsmallest(5).round(4).to_dict(),
                "quota_perdenti": float((port < 0).mean()), "per_moneta": {m: float(x[col].mean()) for m, x in df.groupby("moneta")},
                "sharpe": float(port.mean() / port.std(ddof=1) * math.sqrt(per_anno_div)) if port.std(ddof=1) > 0 else None}
    out["CC_opzioni"] = descrivi(cc, "opzioni", 12)
    out["CC_totale"] = descrivi(cc, "totale", 12)
    out["CC_tenere"] = descrivi(cc, "moneta_rend", 12)
    out["SS"] = descrivi(ss, "r", 52)
    out["SS_comprare"] = descrivi(ss, "comprare", 52)
    out["premio_medio_SS"] = float(ss["premio"].mean())
    out["pagato_medio_SS"] = float(ss["pagato"].mean())
    # SS nel mazzo della correzione (settimanale: l'indice e' il lunedi' prima del venerdi')
    port = ss.groupby("data")["r"].mean().sort_index()
    lun = np.array([sc.giorno(*map(int, d.split("-"))) - 4 for d in port.index])
    s_ss = pd.Series(port.to_numpy(), index=lun)
    sett = pd.DataFrame({"netto": s_ss, "netto_doppio": s_ss - 0.0, "lordo": s_ss, "spese": 0.0, "funding": 0.0, "giro": 0.0, "long": 0.0,
                         "short": 0.0, "monete": 2})
    sett.to_csv(RIS / "settimane_SS.csv.gz")
    serie[f"110 SS"] = sett["netto"]
    riv = ast.corretto_rivisto({**ast.serie_nuove(), **serie}, {"110 SS": te.numeri_settimana(sett["netto"])})
    r = riv["candidate"]["110 SS"]
    out["SS"]["sharpe_corretto"], out["SS"]["t"] = r["corretto_con_aggiunta"], r["t"]
    for k in ("CC_opzioni", "SS"):
        b = out[k]["portafoglio"]
        anni_pieni = [v for a, v in out[k]["per_anno"].items() if 2022 <= a <= 2025]
        out[k]["valida"] = bool(b["p"] <= 0.01 and b["media"] > 0 and all(v > 0 for v in anni_pieni))
    (RIS / "esame.json").write_text(json.dumps(out, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    pc = lambda v: "—" if v is None else f"{100 * v:+.2f}%"  # noqa: E731
    def riga(nome, k, unita):
        x = out[k]
        b = x["portafoglio"]
        return (f"* **{nome}**: {b['n']} {unita}, {pc(b['media'])} a {unita[:-1] if unita.endswith('i') else unita} in media (intervallo {pc(b['basso'])}; "
                f"{pc(b['alto'])}, p {b['p']:.4f}); l'anno {pc(x['annuo'])}, Sharpe {x['sharpe']:.2f}, discesa {100 * x['discesa']:.1f}%; perdenti "
                f"{100 * x['quota_perdenti']:.0f}%; per anno " + ", ".join(f"{a} {pc(v)}" for a, v in x["per_anno"].items()) + "; per moneta "
                + ", ".join(f"{m} {pc(v)}" for m, v in x["per_moneta"].items()) + "; le peggiori " + ", ".join(f"{d} {pc(v)}" for d, v in x["peggiori"].items()) + ".")
    righe = ["# Programma 7 — risultati della quarantottesima prova (VO: vendere le opzioni)", "",
             "Regole in `QUARANTOTTESIMA.md` (scritte prima). Prezzi delle opzioni stimati con Black e Scholes dal DVOL di Deribit (approssimazione).", "",
             riga("CC, la parte delle opzioni (vendere ogni mese l'acquisto al +10%)", "CC_opzioni", "mesi"),
             riga("CC, il totale (moneta più opzioni)", "CC_totale", "mesi"),
             riga("Tenere la moneta, per confronto", "CC_tenere", "mesi"),
             riga("SS, vendere ogni settimana acquisto e vendita al prezzo di oggi", "SS", "settimane"),
             riga("Lo specchio di SS: comprare la volatilità (non contato)", "SS_comprare", "settimane"),
             f"* SS: premio medio incassato {pc(out['premio_medio_SS'])} del prezzo a settimana, pagato alla scadenza in media {pc(out['pagato_medio_SS'])}; "
             f"Sharpe corretto {out['SS']['sharpe_corretto']:.2f}, t {out['SS']['t']:.2f}.", "",
             f"**Esito: CC {'VALIDA' if out['CC_opzioni']['valida'] else 'no'}; SS {'VALIDA' if out['SS']['valida'] else 'no'}** (media sopra zero con p ≤ 0,01 e "
             "positiva in ogni anno pieno 2022-2025)."]
    testo = "\n".join(righe) + "\n"
    (QUI / "RISULTATI_QUARANTOTTESIMA.md").write_text(testo, encoding="utf-8")
    log(testo)
    return out


if __name__ == "__main__":
    esegui(log=lambda x: print(x, flush=True))
    print("QUARANTOTTESIMA FINITA", flush=True)
