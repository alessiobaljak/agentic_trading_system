"""Prova 42 — gli attivisti: comprare in seduta (o all'asta d'apertura) dopo la pubblicazione di un modulo 13D alla SEC, coperti con
lo stesso valore di IWM venduto, per 20 sedute (`P042_attivisti.md`, regole scritte prima; idea I43).

    python -m stock.prove.p042        # gira su GitHub (azioni-ricerca): prezzi di Alpaca; i depositi da dati/sec_attivisti.csv.gz

Il primo passo (`p042a.py`) scrive l'elenco dei 13D con l'ora d'accettazione; questo programma parte solo dopo il controllo dell'ora
(`ORA_CONTROLLATA`, scritto nelle regole prima del calcolo).
"""
from __future__ import annotations

import bisect
import math
import random
from dataclasses import dataclass
from datetime import UTC, date, datetime, time
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd

from stock.dati import archivio, controlli
from stock.prove.p001 import CAPITALE, QUI, carica_serie, comprare_e_tenere, salva_serie
from stock.prove.p032 import campionamento, t_di
from stock.prove.p035 import alle, commissione, dd, sr, tot
from stock.simulatore import asticella
from stock.simulatore.finestre import finestre

NY = ZoneInfo("America/New_York")
ORA_DELLA_SEC = "America/New_York"   # il fuso dell'ora scritta nell'intestazione: da confermare con il controllo di P042a
ORA_CONTROLLATA = False              # True solo dopo il controllo dell'ora, scritto nelle regole prima del calcolo
DAL, ULTIMO_DEPOSITO, FINO = date(2016, 1, 4), date(2024, 11, 29), date(2024, 12, 31)
RITARDO, SEDUTE = 2, 20
QUOTA, MASSIMO = 0.025, 20
SLIT, PRESTITO = 2e-4, 0.005
PREZZO_MINIMO, DOLLARI_MINIMI, SEDUTE_DOLLARI = 5.0, 2_000_000.0, 20
CAMPIONE, SEME = 500, 42
APERTURA, ULTIMO_INGRESSO, FINE_RICERCA, CHIUSURA = time(9, 30), time(15, 57), time(15, 59), time(16, 0)
TIPI = {"raw": "1Day_allora", "az": "azioni_allora", "asof": "-"}


# --- senza rete -------------------------------------------------------------------------------------------------------------------
def accettato(testo: str) -> pd.Timestamp:
    """L'ora dell'intestazione («AAAAMMGGhhmmss», nel fuso `ORA_DELLA_SEC`) in UTC."""
    return pd.Timestamp(datetime.strptime(str(testo), "%Y%m%d%H%M%S"), tz=ORA_DELLA_SEC).tz_convert("UTC")


def piano(t: pd.Timestamp, calendario: list[date]) -> tuple[date, str, pd.Timestamp | None] | None:
    """Da dove si entra: l'accettazione più 2 minuti (al minuto dopo). In seduta fra le 9:30 e le 15:57 di un giorno di borsa:
    (giorno, «seduta», primo istante); prima delle 9:30 di un giorno di borsa: (giorno, «asta», None); altrimenti l'asta d'apertura
    del giorno di borsa dopo."""
    x = (t + pd.Timedelta(minutes=RITARDO)).ceil("min")
    ny = x.tz_convert(NY)
    g = ny.date()
    k = bisect.bisect_left(calendario, g)
    if k < len(calendario) and calendario[k] == g:
        if APERTURA <= ny.time() <= ULTIMO_INGRESSO:
            return g, "seduta", x
        if ny.time() < APERTURA:
            return g, "asta", None
    k = bisect.bisect_right(calendario, g)
    return (calendario[k], "asta", None) if k < len(calendario) else None


def cerca_in_seduta(barre: pd.DataFrame | None, dal: pd.Timestamp) -> tuple[pd.Timestamp, float] | None:
    """La prima barra al minuto che inizia da `dal` in poi, lo stesso giorno, fino alle 15:59 di New York: (inizio, apertura)."""
    if barre is None or barre.empty:
        return None
    b = barre[barre.index >= dal]
    if b.empty:
        return None
    t = b.index[0]
    ny = t.tz_convert(NY)
    if ny.date() != dal.tz_convert(NY).date() or not (APERTURA <= ny.time() <= FINE_RICERCA):
        return None
    return t, float(b["open"].iloc[0])


def passa_i_filtri(chiusure: pd.Series, dollari: pd.Series, g: date) -> bool:
    """Sul giorno di borsa prima di g: chiusura di almeno 5 dollari e mediana dei dollari scambiati nelle 20 sedute prima di almeno
    2 milioni (come la prova 27)."""
    c = chiusure[chiusure.index < g]
    v = dollari[dollari.index < g].iloc[-SEDUTE_DOLLARI:]
    return len(c) > 0 and float(c.iloc[-1]) >= PREZZO_MINIMO and len(v) == SEDUTE_DOLLARI and float(v.median()) >= DOLLARI_MINIMI


@dataclass(frozen=True)
class Operazione:
    simbolo: str
    accettato: pd.Timestamp
    tipo: str                 # «seduta» o «asta»
    ora_ingresso: pd.Timestamp
    giorno_in: date
    prezzo_in: float          # non rettificato
    f_in: float               # chiusura rettificata / chiusura, il giorno dell'ingresso
    giorno_out: date
    prezzo_out: float         # chiusura ufficiale non rettificata
    f_out: float
    iwm_in: float
    iwm_f_in: float
    iwm_out: float
    iwm_f_out: float
    da_prima: float = float("nan")    # dalla chiusura prima dell'accettazione all'ingresso, rettificato
    grande: bool = False              # nell'S&P 500 al giorno dell'ingresso

    @property
    def lordo(self) -> float:
        return self.prezzo_out * self.f_out / (self.prezzo_in * self.f_in) - 1

    @property
    def iwm_lordo(self) -> float:
        return self.iwm_out * self.iwm_f_out / (self.iwm_in * self.iwm_f_in) - 1


def scegli_ingressi(ops: list[Operazione], massimo: int = MASSIMO) -> list[Operazione]:
    """In ordine d'ingresso (a pari ora, alfabetico): al massimo `massimo` posizioni aperte insieme (aperte fino alla chiusura del
    giorno d'uscita); una posizione aperta sullo stesso titolo blocca."""
    aperte: list[Operazione] = []
    out = []
    for op in sorted(ops, key=lambda o: (o.ora_ingresso, o.simbolo)):
        aperte = [a for a in aperte if pd.Timestamp(alle(a.giorno_out, 16, 0)) > op.ora_ingresso]
        if len(aperte) >= massimo or any(a.simbolo == op.simbolo for a in aperte):
            continue
        aperte.append(op)
        out.append(op)
    return out


def conto(ops: list[Operazione], giorni: list[date], mezzo: float, mezzo_iwm: float, fattore: float = 1.0,
          costi: bool = True) -> pd.Series:
    """I rendimenti di ogni giorno di borsa: il 2,5% del conto all'inizio del giorno dell'ingresso nel titolo e lo stesso valore di
    IWM venduto (azioni intere), il guadagno contato nel giorno dell'uscita. `mezzo`, `mezzo_iwm`: metà dello scarto in seduta (alle
    aste nessuno scarto); slittamento 2 punti base su ognuno dei quattro ordini; commissioni; prestito di IWM."""
    per_in: dict[date, list[Operazione]] = {}
    for op in ops:
        per_in.setdefault(op.giorno_in, []).append(op)
    v = CAPITALE
    da_contare: dict[date, float] = {}
    out = {}
    for g in giorni:
        inizio = v
        for op in per_in.get(g, []):
            n = math.floor(QUOTA * inizio / op.prezzo_in)
            m = math.floor(n * op.prezzo_in / op.iwm_in)
            if n <= 0 or m <= 0:
                continue
            valore, coperto = n * op.prezzo_in, m * op.iwm_in
            utile = valore * op.lordo - coperto * op.iwm_lordo
            if costi:
                s1, s2 = (mezzo, mezzo_iwm) if op.tipo == "seduta" else (0.0, 0.0)
                c = valore * (s1 + SLIT) + valore * (1 + op.lordo) * SLIT
                c += coperto * (s2 + SLIT) + coperto * (1 + op.iwm_lordo) * SLIT
                c += commissione(n, op.prezzo_in) + commissione(n, op.prezzo_in * (1 + op.lordo))
                c += commissione(m, op.iwm_in) + commissione(m, op.iwm_in * (1 + op.iwm_lordo))
                c += coperto * PRESTITO * (op.giorno_out - op.giorno_in).days / 365
                utile -= fattore * c
            da_contare[op.giorno_out] = da_contare.get(op.giorno_out, 0.0) + utile
        utile_g = da_contare.pop(g, 0.0)
        out[g] = utile_g / inizio
        v += utile_g
    return pd.Series(out)


# --- con i prezzi ------------------------------------------------------------------------------------------------------------------
def giorni_e_dollari(s: str, raw: str, az: str):
    """Giorno → (apertura, chiusura, fattore) non rettificati; le chiusure e i dollari scambiati per giorno."""
    from stock.prove.p003 import prepara_titolo
    try:
        df, rett, _ = prepara_titolo(s, FINO, raw, az)
    except Exception:  # noqa: BLE001 — titolo con i dati rotti: resta fuori, si conta
        return None
    g = controlli.date_ny(df.index)
    r = rett.reindex(pd.Index(g)).to_numpy(float)
    d = {x: (float(o), float(c), float(y / c)) for x, o, c, y in zip(g, df["open"], df["close"], r) if c > 0 and np.isfinite(y)}
    b = archivio.carica(s, raw)
    gb = pd.Index(controlli.date_ny(b.index))
    return d, pd.Series(b["close"].to_numpy(float), index=gb), pd.Series((b["close"] * b["volume"]).to_numpy(float), index=gb)


def operazioni(ev: pd.DataFrame, calendario: list[date], prezzi: dict, iwm: dict, fini, membri) -> tuple[list[Operazione], dict]:
    from stock.prove.p034 import membri_al
    from stock.prove.p036 import barre_del_giorno
    fuori = {"senza prezzi": 0, "filtri (5 dollari, 2 milioni)": 0, "senza ingresso": 0, "uscita oltre il 2024": 0}
    attesa: dict[date, list] = {}
    for r in ev.itertuples():
        p = piano(r.accettato, calendario)
        if p is None:
            fuori["senza ingresso"] += 1
            continue
        attesa.setdefault(p[0], []).append((r, p[1], p[2]))
    ops = []
    for g in sorted(attesa):
        lista = attesa[g]
        in_seduta = sorted({r.simbolo for r, tipo, _ in lista if tipo == "seduta"})
        barre = barre_del_giorno(g, in_seduta + ["IWM"]) if in_seduta else {}
        for r, tipo, dal in lista:
            x = prezzi.get(r.simbolo)
            if x is None:
                fuori["senza prezzi"] += 1
                continue
            d, chiusure, dollari = x
            gi = g
            if tipo == "seduta":
                e = cerca_in_seduta(barre.get(r.simbolo), dal)
                ib = barre.get("IWM")
                if e is not None and ib is not None and len(ib.loc[:e[0]]):
                    ora, prezzo, iwm_in = e[0], e[1], float(ib.loc[:e[0]]["open"].iloc[-1])
                else:                          # nessuna barra fino alle 15:59: l'asta d'apertura del giorno di borsa dopo
                    k = bisect.bisect_right(calendario, g)
                    if k >= len(calendario):
                        fuori["senza ingresso"] += 1
                        continue
                    tipo, gi = "asta", calendario[k]
            if tipo == "asta":
                if gi not in d or gi not in iwm:
                    fuori["senza ingresso"] += 1
                    continue
                ora, prezzo, iwm_in = pd.Timestamp(alle(gi, 9, 30)), d[gi][0], iwm[gi][0]
            if gi not in d or gi not in iwm:
                fuori["senza ingresso"] += 1
                continue
            if not passa_i_filtri(chiusure, dollari, gi):
                fuori["filtri (5 dollari, 2 milioni)"] += 1
                continue
            k = bisect.bisect_left(calendario, gi)
            if k + SEDUTE >= len(calendario) or calendario[k + SEDUTE] > FINO:
                fuori["uscita oltre il 2024"] += 1
                continue
            gu = calendario[k + SEDUTE]
            if gu not in d:                   # sparito dal listino prima: l'ultima chiusura dopo l'ingresso
                dopo = [x for x in d if gi < x <= gu]
                if not dopo:
                    fuori["senza prezzi"] += 1
                    continue
                gu = max(dopo)
            if gu not in iwm:
                fuori["senza prezzi"] += 1
                continue
            prima = [x for x in d if x < r.accettato.tz_convert(NY).date()
                     or (x == r.accettato.tz_convert(NY).date() and r.accettato.tz_convert(NY).time() >= CHIUSURA)]
            da_prima = prezzo * d[gi][2] / (d[max(prima)][1] * d[max(prima)][2]) - 1 if prima else float("nan")
            ops.append(Operazione(r.simbolo, r.accettato, tipo, ora, gi, prezzo, d[gi][2], gu, d[gu][1], d[gu][2],
                                  iwm_in, iwm[gi][2], iwm[gu][1], iwm[gu][2], da_prima, r.simbolo in membri_al(gi, fini, membri)))
    return ops, fuori


def scarti(campione: list[Operazione]) -> tuple[list[float], list[float]]:
    """Lo scarto relativo del titolo e di IWM all'ultima quotazione valida prima della fine del minuto dell'ingresso."""
    from stock.dati import alpaca
    from stock.dati.scarto import fotografie_al_minuto, scarto_relativo
    from stock.prove.p027 import aspetta_fuori_dagli_ordini
    tit, iw = [], []
    for op in campione:
        for s, dove in ((op.simbolo, tit), ("IWM", iw)):
            for da in (45, 0):                  # come la prova 36: prima gli ultimi 15 secondi del minuto, poi tutto il minuto
                aspetta_fuori_dagli_ordini()
                try:
                    q = alpaca.quotazioni(s, (op.ora_ingresso + pd.Timedelta(seconds=da)).to_pydatetime(),
                                          (op.ora_ingresso + pd.Timedelta(seconds=60)).to_pydatetime(), massimo=5000)
                except alpaca.ErroreAlpaca:
                    break
                fot = fotografie_al_minuto(q)
                if len(fot):
                    dove.append(float(scarto_relativo(fot).iloc[-1]))
                    break
    return tit, iw


def main():
    if not ORA_CONTROLLATA:
        raise SystemExit("prima il controllo dell'ora d'accettazione (P042a_risultati.md) e l'aggiunta alle regole")
    from stock.prove.p027 import scarica
    from stock.prove.p028 import decisioni
    ev = pd.read_csv(QUI / "dati" / "sec_attivisti.csv.gz", dtype={"simbolo": str, "accettazione": str, "numero": str},
                     keep_default_na=False, na_values=[""])
    tutti = len(ev)
    ev = ev[(ev["giorno"] >= DAL.isoformat()) & (ev["giorno"] <= ULTIMO_DEPOSITO.isoformat())]
    senza_simbolo = int(ev["simbolo"].isna().sum())
    ev = ev.dropna(subset=["simbolo"]).copy()
    ev["accettato"] = [accettato(x) for x in ev["accettazione"]]
    ev = ev.sort_values(["accettato", "numero"]).reset_index(drop=True)
    simboli = sorted(set(ev["simbolo"]))
    scarica(["SPY", "IWM"])
    scarica(simboli, TIPI["raw"], TIPI["az"], TIPI["asof"])
    spy = archivio.carica("SPY", "1Day_raw")
    calendario = sorted(d for d in controlli.date_ny(spy.index) if d <= FINO)
    prezzi = {s: x for s in simboli if (x := giorni_e_dollari(s, TIPI["raw"], TIPI["az"])) is not None}
    iwm = giorni_e_dollari("IWM", "1Day_raw", "azioni")[0]
    fini, membri = decisioni()
    tutte_ops, fuori = operazioni(ev, calendario, prezzi, iwm, fini, membri)
    ops = scegli_ingressi(tutte_ops)
    in_seduta = [o for o in ops if o.tipo == "seduta"]
    random.seed(SEME)
    tit, iw = scarti(random.sample(in_seduta, min(CAMPIONE, len(in_seduta))))
    mezzo = 0.5 * float(np.median(tit)) if tit else 0.0
    mezzo_iwm = 0.5 * float(np.median(iw)) if iw else 0.0
    giorni = [g for g in calendario if DAL <= g <= FINO]
    serie = {"costi": conto(ops, giorni, mezzo, mezzo_iwm), "costi doppi": conto(ops, giorni, mezzo, mezzo_iwm, 2.0),
             "senza costi": conto(ops, giorni, mezzo, mezzo_iwm, costi=False)}
    primo = min(o.giorno_in for o in ops)
    gg = {k: v[v.index >= primo] for k, v in serie.items()}
    gc = gg["costi"]
    a, b = gc.index.min(), gc.index.max()
    spy_r, iwm_r = comprare_e_tenere("SPY", a, b), comprare_e_tenere("IWM", a, b)
    miscela = carica_serie()["P025_miscela"]
    salva_serie("P042_attivisti", gc)
    comuni = miscela.index.intersection(gc.index)
    salva_serie("P042_miscela", 0.75 * miscela.loc[comuni] + 0.25 * gc.loc[comuni])
    tutte = carica_serie()
    nuova = tutte["P042_miscela"]
    ast = asticella.sharpe_corretto(gc, tutte)
    q = [float((1 + gc[(gc.index >= x) & (gc.index < y)]).prod() - 1)
         for x, y in (f["prova"] for f in finestre(date(2016, 1, 1), date(2025, 1, 1), chiuso_dal=date(2025, 1, 1))) if x >= a]
    quota = sum(x > 0 for x in q) / len(q)
    sr_c, sr_2 = sr(gc), sr(gg["costi doppi"])
    da_sola = sr_c > sr(spy_r) and sr_c > sr(iwm_r) and ast["sharpe_corretto"] >= 0.95 and sr_2 > 0 and quota >= 0.6
    corr = float(np.corrcoef(miscela.loc[comuni], gc.loc[comuni])[0, 1])
    spy_c = comprare_e_tenere("SPY", comuni.min(), comuni.max())
    t_parte = t_di(gc.to_numpy())
    vinte = campionamento(miscela.loc[comuni], gc.loc[comuni])
    entra = sr(gc.loc[comuni]) > 0 and sr(gg["costi doppi"].reindex(comuni).dropna()) > 0 and corr < 0.3 \
        and sr(nuova) > sr(miscela.loc[comuni]) and sr(nuova) > sr(spy_c) and t_parte >= 1.3 and vinte >= 0.8
    netto = np.array([o.lordo - o.iwm_lordo for o in ops])

    def riga(nome, xs):
        x = np.array([o.lordo - o.iwm_lordo for o in xs])
        p = np.array([o.da_prima for o in xs if np.isfinite(o.da_prima)])
        return (f"* {nome}: {len(x)} operazioni, titolo meno IWM prima dei costi **{x.mean():+.2%}** (t {t_di(x):.2f}), in guadagno "
                f"{(x > 0).mean():.0%}; già salito dalla chiusura prima dell'accettazione all'ingresso {p.mean():+.2%}") if len(x) else \
               f"* {nome}: nessuna operazione"
    anni = (1 + gc).groupby(pd.Index([x.year for x in gc.index])).prod() - 1
    per_anno = pd.Series([o.giorno_in.year for o in ops]).value_counts().sort_index()
    testo = ["# Prova 42 — risultati", "",
             f"Calcolato da `python -m stock.prove.p042` il {datetime.now(UTC):%Y-%m-%d %H:%M} UTC con le regole di "
             f"`P042_attivisti.md` (committate prima). Dal {a} al {b}. Nel conto dell'asticella: {len(tutte)} serie.", "",
             f"* Depositi nell'elenco {tutti}; nel periodo senza simbolo {senza_simbolo}; fuori: {fuori}; operazioni possibili "
             f"{len(tutte_ops)}, fatte {len(ops)} (le altre saltate per i 20 posti o per una posizione aperta sullo stesso titolo); "
             f"per anno: {', '.join(f'{y} {n}' for y, n in per_anno.items())}.",
             f"* Metà dello scarto misurata su {len(tit)} ingressi in seduta: titolo {mezzo * 1e4:.1f} punti base, IWM "
             f"{mezzo_iwm * 1e4:.2f} (misure IWM {len(iw)}).",
             riga("Tutte", ops), riga("In seduta", in_seduta), riga("All'asta d'apertura", [o for o in ops if o.tipo == "asta"]),
             riga("Aziende dell'S&P 500", [o for o in ops if o.grande]), "",
             "| | La strategia | Tenere lo SPY | Tenere l'IWM |", "|---|---|---|---|",
             f"| Guadagno totale senza costi / con i costi / costi doppi | {tot(gg['senza costi']):+.1%} / {tot(gc):+.1%} / "
             f"{tot(gg['costi doppi']):+.1%} | {tot(spy_r):+.1%} | {tot(iwm_r):+.1%} |",
             f"| **1.** Sharpe annuo con i costi | **{sr_c:.2f}** (senza costi {sr(gg['senza costi']):.2f}) | {sr(spy_r):.2f} | "
             f"{sr(iwm_r):.2f} |",
             f"| **2.** Sharpe corretto (soglia 0,95) | {ast['sharpe_corretto']:.2f} (gruppi {ast['gruppi']}, t {ast['t_sharpe']:.2f}) | — | — |",
             f"| **3.** Sharpe con i costi doppi (> 0) | {sr_2:.2f} | — | — |",
             f"| **4.** Trimestri in guadagno (60%) | {sum(x > 0 for x in q)} su {len(q)} ({quota:.0%}) | — | — |",
             f"| Perdita massima dal picco | {dd(gc):.1%} | {dd(spy_r):.1%} | {dd(iwm_r):.1%} |",
             f"| Anno per anno | {' '.join(f'{y}: {x:+.1%}' for y, x in anni.items())} | — | — |",
             f"| **Esito da sola** | **{'passa la ricerca' if da_sola else 'bocciata'}** | | |", "",
             f"**Per entrare nella miscela** (giorni in comune dal {comuni.min()} al {comuni.max()}): Sharpe della parte "
             f"{sr(gc.loc[comuni]):.2f}, con i costi doppi {sr(gg['costi doppi'].reindex(comuni).dropna()):.2f}; correlazione con la "
             f"miscela {corr:.2f} (soglia 0,3); miscela nuova {sr(nuova):.2f} contro {sr(miscela.loc[comuni]):.2f} della miscela e "
             f"{sr(spy_c):.2f} del tenere lo SPY; **t dello Sharpe della parte {t_parte:.2f} (soglia 1,3)**; **miscela nuova più alta "
             f"nel {vinte:.0%} dei campionamenti (soglia 80%)**. **Esito: "
             f"{'entra nella miscela (prima il revisore)' if entra else 'non entra'}**", "",
             f"Titolo meno IWM su tutte le operazioni: media {netto.mean():+.2%}, mediana {np.median(netto):+.2%}.", "",
             "Nel conto: 2 prove."]
    (QUI / "P042_risultati.md").write_text("\n".join(testo) + "\n")
    print("\n".join(testo[4:]))


if __name__ == "__main__":
    main()
