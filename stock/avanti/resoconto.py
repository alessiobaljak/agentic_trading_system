"""Il resoconto del lunedì delle tre strategie sul demo (prima candela, miscela, prova 45), con le misure che le regole chiedono e che il
riepilogo scritto dal programma degli ordini non dava (audit del 27 novembre 2026, `stock/AUDIT_2026-11-27.md`):

* il **costo vero dell'ingresso** della prima candela (prezzo eseguito contro la chiusura della candela, `REGOLE.md`, «I numeri»);
* il **t sui giorni**: le 10 operazioni dello stesso giorno sono legate fra loro, contarle come indipendenti gonfia il t;
* il **confronto con lo SPY** negli stessi giorni;
* la **tabella per settimana senza i giorni fuori regola** (quella di `riepilogo.md` conta l'11 novembre, il totale no);
* i giorni con l'ingresso dopo le 9:50 e gli ordini «già oltre lo stop», che le regole vogliono a parte.

Solo lettura dei diari: non manda ordini, non tocca il conto, non cambia `riepilogo.md`. I prezzi dello SPY vengono da Yahoo e non si
scrivono mai: nel file vanno solo rendimenti.

    python -m stock.avanti.resoconto        # scrive stock/avanti/resoconto.md
"""
from __future__ import annotations

import math
from datetime import UTC, datetime, time
from pathlib import Path

import numpy as np
import pandas as pd

QUI = Path(__file__).parent
NY = "America/New_York"
FUORI_REGOLA = {"2026-11-11"}            # come GIORNI_FUORI_REGOLA di avanti.py (REGOLE.md, deviazioni)
INGRESSO_PUNTUALE = time(9, 50)          # REGOLE.md: «un ingresso dopo le 9:50 si segnala nel riepilogo»
GIA_OLTRE = ("42210000", "stop_price must be", "già oltre lo stop")
CAPITALE = 100_000.0                     # il capitale virtuale di partenza di ognuna delle tre strategie (REGOLE.md, conto.py)


# ---- funzioni pure (provate da stock/tests/test_resoconto.py) -----------------------------------------------------------

def costo_ingresso_pb(lato: str, ingresso: float, riferimento: float) -> float:
    """Punti base pagati all'ingresso contro la chiusura della candela; positivo = peggio (si compra più caro, si vende più basso)."""
    if not (ingresso and riferimento) or any(map(math.isnan, (float(ingresso), float(riferimento)))):
        return float("nan")
    x = float(ingresso) / float(riferimento) - 1
    return 1e4 * (x if lato == "buy" else -x)


def scarto_stop_pb(lato: str, uscita: float, stop: float) -> float:
    """Punti base persi all'uscita allo stop contro il prezzo dello stop; positivo = peggio. `lato` è quello dell'ingresso."""
    if not (uscita and stop) or any(map(math.isnan, (float(uscita), float(stop)))):
        return float("nan")
    x = float(uscita) / float(stop) - 1
    return 1e4 * (-x if lato == "buy" else x)


def ora_di_new_york(iso: str) -> time | None:
    try:
        return pd.Timestamp(iso).tz_convert(NY).time()
    except (TypeError, ValueError):
        return None


def nel_giudizio(diario: pd.DataFrame) -> pd.DataFrame:
    return diario[~diario["giorno"].astype(str).isin(FUORI_REGOLA)]


def chiuse(diario: pd.DataFrame) -> pd.DataFrame:
    return diario.dropna(subset=["proporzione"])


def netta(fatte: pd.DataFrame) -> pd.Series:
    """Il guadagno in proporzione meno la commissione stimata di Interactive Brokers."""
    return fatte["proporzione"].astype(float) - fatte["commissione_ib"].astype(float) / (
        fatte["ingresso"].astype(float) * fatte["quantita"].astype(float))


def t_di(x: pd.Series) -> float:
    x = x.dropna().astype(float)
    return float(x.mean() / x.std(ddof=1) * math.sqrt(len(x))) if len(x) > 1 and x.std(ddof=1) > 0 else float("nan")


def per_giorno(fatte: pd.DataFrame, colonna: pd.Series | None = None) -> pd.Series:
    """Il guadagno medio a operazione di ogni giorno: la serie su cui si misura il t (un giorno = un'osservazione)."""
    x = fatte["proporzione"].astype(float) if colonna is None else colonna
    return x.groupby(fatte["giorno"].astype(str)).mean()


def giorni_per_t3(giornaliera: pd.Series) -> float:
    g = giornaliera.dropna()
    return float((3 * g.std(ddof=1) / g.mean()) ** 2) if len(g) > 1 and g.mean() > 0 else float("nan")


def gia_oltre_lo_stop(diario: pd.DataFrame) -> int:
    note = diario["nota"].fillna("").astype(str)
    return int(note.apply(lambda s: any(k in s for k in GIA_OLTRE)).sum())


def giorni_in_ritardo(diario: pd.DataFrame) -> dict[str, str]:
    """I giorni con almeno un ingresso dopo le 9:50 di New York, con l'ora del primo ingresso."""
    out = {}
    for giorno, g in diario.dropna(subset=["ora_ingresso"]).groupby(diario["giorno"].astype(str)):
        ore = [o for o in (ora_di_new_york(x) for x in g["ora_ingresso"]) if o is not None]
        if ore and max(ore) > INGRESSO_PUNTUALE:
            out[giorno] = min(ore).strftime("%H:%M")
    return out


def costi(diario: pd.DataFrame) -> pd.DataFrame:
    """Per ogni operazione con l'ingresso eseguito: costo d'ingresso in punti base e in dollari, e lo scarto allo stop."""
    d = diario.dropna(subset=["ingresso"]).copy()
    d["costo_pb"] = [costo_ingresso_pb(lt, i, r) for lt, i, r in zip(d["lato"], d["ingresso"], d["riferimento"])]
    d["costo_dollari"] = d["costo_pb"] / 1e4 * d["riferimento"].astype(float) * d["quantita"].astype(float)
    allo_stop = d["uscita"].fillna("").astype(str).str.contains("stop")
    d["scarto_stop_pb"] = [scarto_stop_pb(lt, u, s) if a else float("nan")
                           for lt, u, s, a in zip(d["lato"], d["uscita_prezzo"], d["stop"], allo_stop)]
    return d


def settimane(diario: pd.DataFrame) -> pd.DataFrame:
    """La tabella per settimana (da sabato a venerdì) dei soli giorni nel giudizio: torna con il totale."""
    fatte = chiuse(nel_giudizio(diario)).copy()
    fatte["settimana"] = pd.to_datetime(fatte["giorno"]).dt.to_period("W-FRI").dt.start_time.dt.date
    g = fatte.groupby("settimana")
    out = pd.DataFrame({"giorni": g["giorno"].nunique(), "operazioni": g.size(),
                        "guadagno": g["guadagno"].sum().astype(float), "commissioni_ib": g["commissione_ib"].sum().astype(float)})
    out["netto"] = out["guadagno"] - out["commissioni_ib"]
    return out


def spy_negli_stessi_giorni(spy: pd.DataFrame, giorni: list[str]) -> dict:
    """Lo SPY nei soli giorni dati, composto: dall'apertura alla chiusura di ogni giorno (come la prima candela, che sta dentro la
    giornata) e da una chiusura alla chiusura dopo. `spy`: barre al giorno con `open` e `close`, indice il giorno di New York."""
    s = spy.copy()
    s.index = [pd.Timestamp(x).date().isoformat() for x in s.index]
    s = s.sort_index()
    prima = s["close"].shift(1)
    dentro = [g for g in giorni if g in s.index and not math.isnan(float(prima.loc[g]))]
    if not dentro:
        return {"giorni": 0, "apertura_chiusura": float("nan"), "chiusura_chiusura": float("nan")}
    ac = float(np.prod([s.loc[g, "close"] / s.loc[g, "open"] for g in dentro]) - 1)
    cc = float(np.prod([s.loc[g, "close"] / prima.loc[g] for g in dentro]) - 1)
    return {"giorni": len(dentro), "apertura_chiusura": ac, "chiusura_chiusura": cc}


def variazione(valori: pd.DataFrame, colonna: str) -> tuple[str | None, str | None, float]:
    """(primo giorno, ultimo giorno, variazione dal capitale di partenza): il valore di ogni riga è quello di fine giornata."""
    v = valori[["giorno", colonna]].dropna()
    if not len(v):
        return None, None, float("nan")
    return str(v["giorno"].iloc[0]), str(v["giorno"].iloc[-1]), float(v[colonna].iloc[-1] / CAPITALE - 1)


def spy_da_chiusura(spy: pd.DataFrame, dal: str, al: str) -> float:
    s = spy.copy()
    s.index = [pd.Timestamp(x).date().isoformat() for x in s.index]
    if dal not in s.index or al not in s.index:
        return float("nan")
    return float(s.loc[al, "close"] / s.loc[dal, "close"] - 1)


# ---- il file -------------------------------------------------------------------------------------------------------------

def _pb(x: float) -> str:
    return "—" if x is None or (isinstance(x, float) and math.isnan(x)) else f"{x:+.1f}".replace(".", ",")


def _pc(x: float) -> str:
    return "—" if x is None or (isinstance(x, float) and math.isnan(x)) else f"{x:+.2%}".replace(".", ",")


def _n(x: float) -> str:
    return "—" if math.isnan(x) else f"{x:.2f}".replace(".", ",")


def _usd(x: float) -> str:
    return f"{x:+,.2f}".replace(",", "'").replace(".", ",")


def testo(diario: pd.DataFrame, valori: pd.DataFrame | None, gamma: pd.DataFrame | None, spy: pd.DataFrame | None,
          adesso: datetime | None = None) -> str:
    adesso = adesso or datetime.now(UTC)
    giudizio = nel_giudizio(diario)
    fatte = chiuse(giudizio)
    giorni = sorted(giudizio["giorno"].astype(str).unique())
    ritardi = giorni_in_ritardo(giudizio)
    c = costi(giudizio)
    puntuali = c[~c["giorno"].astype(str).isin(ritardi)]
    g_lordo, g_netto = per_giorno(fatte), per_giorno(fatte, netta(fatte))
    tot, comm = float(fatte["guadagno"].astype(float).sum()), float(fatte["commissione_ib"].astype(float).sum())
    stop = c["scarto_stop_pb"].dropna()
    r = ["# Il resoconto del lunedì — le tre strategie sul demo", "",
         (f"Aggiornato il {adesso:%Y-%m-%d %H:%M} UTC da `python -m stock.avanti.resoconto` (solo lettura dei diari; lo SPY da Yahoo, mai "
          "nel repository). Misure chieste dalle regole e mancanti in `riepilogo.md` (audit `stock/AUDIT_2026-11-27.md`)."), "",
         "## La prima candela (`REGOLE.md`)", "",
         (f"* Giorni nel giudizio: {len(giorni)} (fuori regola, nel diario ma non nel giudizio: {', '.join(sorted(FUORI_REGOLA))}); operazioni "
          f"chiuse: {len(fatte)}; ordini «già oltre lo stop» (saltati, si contano a parte): {gia_oltre_lo_stop(giudizio)}."),
         f"* Totale: {_usd(tot)} dollari prima delle commissioni, {_usd(tot - comm)} dopo la commissione stimata di Interactive Brokers.",
         f"* **Il t sui giorni** (le operazioni dello stesso giorno sono legate: un giorno è un'osservazione): guadagno medio a operazione "
         f"{_pc(float(g_lordo.mean()) if len(g_lordo) else float('nan'))}, t {_n(t_di(g_lordo))}; con la commissione "
         f"{_pc(float(g_netto.mean()) if len(g_netto) else float('nan'))}, t {_n(t_di(g_netto))}. Contando le operazioni come "
         f"indipendenti il t sarebbe {_n(t_di(netta(fatte)))}. Giorni che servirebbero per arrivare a t 3 con la media netta di oggi: "
         + (f"circa {giorni_per_t3(g_netto):,.0f}." if not math.isnan(giorni_per_t3(g_netto)) else "nessun numero (media netta non positiva)."),
         (f"* **Il costo vero dell'ingresso** (prezzo eseguito contro la chiusura della candela, punti base, positivo = peggio): nei giorni "
          f"puntuali media {_pb(float(puntuali['costo_pb'].mean()))}, mediana {_pb(float(puntuali['costo_pb'].median()))}, "
          f"{_usd(float(puntuali['costo_dollari'].sum()))} dollari su {len(puntuali)} ingressi; su tutti i giorni media "
          f"{_pb(float(c['costo_pb'].mean()))}. Sul passato la prova 23 supponeva circa 1-2,5 punti base per lato."),
         "* Giorni con l'ingresso dopo le 9:50 (si segnalano, `REGOLE.md`): "
         + (", ".join(f"{g} (dalle {o})" for g, o in ritardi.items()) if ritardi else "nessuno") + ".",
         (f"* Uscite allo stop: {len(stop)}; scarto contro il prezzo dello stop: media {_pb(float(stop.mean()) if len(stop) else float('nan'))} "
          "punti base (negativo = eseguito meglio dello stop: il demo è più comodo del vero).")]
    if spy is not None and giorni:
        s = spy_negli_stessi_giorni(spy, giorni)
        r.append(f"* **Lo SPY negli stessi giorni** ({s['giorni']}): dall'apertura alla chiusura {_pc(s['apertura_chiusura'])}, da una "
                 f"chiusura all'altra {_pc(s['chiusura_chiusura'])}; la prima candela {_pc(tot / CAPITALE)} del capitale prima delle "
                 f"commissioni, {_pc((tot - comm) / CAPITALE)} dopo.")
    else:
        r.append("* Lo SPY negli stessi giorni: non disponibile in questo giro (Yahoo non ha risposto).")
    if valori is not None and "prima_candela" in valori:
        _, al, var = variazione(valori, "prima_candela")
        r.append(f"* Il valore della prima candela nel conto (`valori.csv`, la Plancia) al {al}: {_pc(var)} dal capitale di partenza. È diverso dal "
                 "totale qui sopra perché comprende l'11 novembre (fuori regola) e le tasse americane sulle vendite che il conto addebita.")
    r += ["", "| Settimana (dal sabato) | Giorni | Operazioni | Guadagno (dollari) | Commissioni IB stimate | Netto |", "|---|---|---|---|---|---|"]
    for w, x in settimane(diario).iterrows():
        r.append(f"| {w} | {int(x['giorni'])} | {int(x['operazioni'])} | {_usd(x['guadagno'])} | {_usd(x['commissioni_ib'])[1:]} | "
                 f"{_usd(x['netto'])} |")
    r += ["", "## La miscela (`MISCELA.md`)", ""]
    if valori is not None and "miscela" in valori:
        dal, al, var = variazione(valori, "miscela")
        riga = f"* Dalla sera del {dal} al {al}: {_pc(var)}"
        if spy is not None and dal:
            riga += f"; lo SPY da una chiusura all'altra negli stessi giorni {_pc(spy_da_chiusura(spy, dal, al))}"
        r.append(riga + ".")
        r.append("* I valori di fine giornata si scrivono all'ora del primo lavoro dopo la chiusura, a volte con i prezzi del dopo borsa "
                 "(audit): qualche decimo di differenza in un giorno, che si annulla nei giorni dopo.")
    r += ["", "## La prova 45 (`GAMMA.md`)", ""]
    if gamma is not None and len(gamma):
        sotto = gamma["copertura"].astype(str).str.contains("sotto").sum()
        ops = gamma.dropna(subset=["quantita"])
        gua = float(ops["guadagno"].astype(float).sum()) if len(ops) else 0.0
        saltati = gamma["nota"].fillna("").astype(str).str.contains("saltat").sum()
        r.append(f"* Giorni: {len(gamma)}; con la copertura sotto zero: {sotto}; operazioni: {len(ops)}; guadagno {_usd(gua)} dollari; "
                 f"giorni saltati: {saltati}.")
    else:
        r.append("* Ancora nessun giorno nel diario.")
    return "\n".join(r) + "\n"


def main() -> str:
    diario = pd.read_csv(QUI / "diario.csv")
    valori = pd.read_csv(QUI / "valori.csv") if (QUI / "valori.csv").exists() else None
    gamma = pd.read_csv(QUI / "gamma_diario.csv") if (QUI / "gamma_diario.csv").exists() else None
    spy = None
    try:
        from stock.dati import yahoo
        primo = min(diario["giorno"].astype(str).min(), str(valori["giorno"].min()) if valori is not None else "9999")
        spy = yahoo.prezzi("SPY", (pd.Timestamp(primo) - pd.Timedelta(days=7)).date().isoformat(), datetime.now(UTC).date().isoformat())
    except Exception:  # noqa: BLE001 - senza lo SPY il resoconto si scrive lo stesso, e lo dice
        spy = None
    t = testo(diario, valori, gamma, spy)
    (QUI / "resoconto.md").write_text(t)
    return t


if __name__ == "__main__":
    print(main())
