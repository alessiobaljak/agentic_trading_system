"""Prova 35 — le azioni «in gioco»: ogni mattina le 20 con il volume dei primi 5 minuti più alto del solito, la rottura della prima
candela da 5 minuti, stop a un decimo dell'ATR, uscita alla chiusura (idea I37; Zarattini, Barbon, Aziz 2024).

    python -m stock.prove.p035            # servono le chiavi di Alpaca: gira su GitHub (azioni-ricerca); si riprende da dove si è fermato

Regole: `P035_azioni_in_gioco.md` (scritte e committate prima del calcolo, con l'aggiunta sul minuto dell'ingresso). Tappe: (1) i
filtri del giorno dalle barre al giorno; (2) le barre da 5 minuti delle 9:30 dei titoli che servono; (3) i 20 del giorno; (4) le barre
al minuto dei 20; (5) le operazioni; (6) lo scarto misurato su 500 operazioni; (7) il conto. I prezzi restano nella memoria del lavoro
(`~/stock_dati/p035`), mai nel repository.
"""
from __future__ import annotations

import math
import random
from dataclasses import dataclass
from datetime import UTC, date, datetime, time
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd

from stock.dati import alpaca, archivio, controlli
from stock.dati.scarto import fotografie_al_minuto, scarto_relativo
from stock.prove.p001 import CAPITALE, QUI, annuo, carica_serie, comprare_e_tenere, salva_serie
from stock.prove.p027 import aspetta_fuori_dagli_ordini
from stock.prove.p028 import decisioni as fine_mese
from stock.prove.p032 import ORDINARIE, campionamento, t_di
from stock.simulatore import asticella
from stock.simulatore.finestre import finestre
from stock.strategie import tono

NY = ZoneInfo("America/New_York")
DAL, FINO = date(2016, 1, 4), date(2024, 12, 31)
SEDUTE, PREZZO, VOLUME, ATR_MIN = 14, 5.0, 1_000_000, 0.50
QUANTI, RV_MIN = 20, 1.0
RISCHIO, LEVA, FRAZIONE_STOP = 0.01, 4.0, 0.10
SLIT_STOP, SLIT_CHIUSURA = 5e-4, 2e-4
IB_PER_AZIONE, IB_MINIMO, IB_MASSIMO = 0.005, 1.0, 0.01
CAMPIONE, SEME = 500, 35
GRUPPO = 400
TIPI = {"raw": "1Day_allora", "az": "azioni_allora"}
COLONNE = ["open", "high", "low", "close"]

sr = lambda x: annuo(asticella.sharpe(x))  # noqa: E731
tot = lambda x: (1 + x).prod() - 1  # noqa: E731
dd = lambda x: ((1 + x).cumprod() / (1 + x).cumprod().cummax() - 1).min()  # noqa: E731


def cartella(nome: str):
    p = archivio.cartella_dati() / "p035" / nome
    p.mkdir(parents=True, exist_ok=True)
    return p


# --- (1) i filtri del giorno -------------------------------------------------------------------------------------------------------
def filtri(df: pd.DataFrame, rett: pd.Series, volume: pd.Series) -> pd.DataFrame:
    """Per un titolo, giorno per giorno: l'ATR e il volume medio delle 14 sedute prima nei termini di oggi (frazionamenti e dividendi
    tolti con il fattore della chiusura rettificata `f`), il fattore, e se passa i filtri (apertura di oggi sopra 5 dollari)."""
    g = pd.Index(controlli.date_ny(df.index))
    d = pd.DataFrame({c: df[c].to_numpy(float) for c in COLONNE}, index=g)
    d["volume"] = volume.reindex(df.index).to_numpy(float)
    d["f"] = rett.reindex(g).to_numpy() / d["close"]
    hi, lo, cl = d["high"] * d["f"], d["low"] * d["f"], d["close"] * d["f"]
    tr = pd.concat([hi, cl.shift(1)], axis=1).max(axis=1) - pd.concat([lo, cl.shift(1)], axis=1).min(axis=1)
    d["atr"] = tr.shift(1).rolling(SEDUTE).mean() / d["f"]
    d["adv"] = (d["volume"] / d["f"]).shift(1).rolling(SEDUTE).mean() * d["f"]
    d["passa"] = (d["open"] > PREZZO) & (d["adv"] >= VOLUME) & (d["atr"] > ATR_MIN)
    return d[["atr", "adv", "f", "passa"]]


# --- (3) i 20 del giorno -----------------------------------------------------------------------------------------------------------
def volume_relativo(oggi: float, prima: list[float | None]) -> float | None:
    """Il volume dei primi 5 minuti di oggi diviso la media delle 14 sedute prima (tutte e 14 servono), nella stessa base."""
    if len(prima) < SEDUTE or any(v is None or not v > 0 for v in prima):
        return None
    return oggi / float(np.mean(prima))


def scegli(rv: dict[str, float]) -> list[str]:
    ok = {s: v for s, v in rv.items() if v is not None and v >= RV_MIN}
    return sorted(ok, key=lambda s: (-ok[s], s))[:QUANTI]


# --- (5) le operazioni -------------------------------------------------------------------------------------------------------------
@dataclass
class Operazione:
    giorno: date
    simbolo: str
    lato: int
    ingresso: float
    ora_ingresso: pd.Timestamp
    uscita: float
    ora_uscita: pd.Timestamp
    allo_stop: bool
    distanza_stop: float


def esegui(barre: pd.DataFrame, lato: int, livello: float, atr: float, giorno: date, simbolo: str) -> Operazione | None:
    """`barre`: i minuti dalle 9:35 alla chiusura. Ordine stop d'ingresso al `livello`; stop a un decimo dell'ATR dal prezzo eseguito;
    nel minuto dell'ingresso lo stop vale solo se il minuto è iniziato oltre il livello (allora vale il minimo o il massimo) o se la sua
    chiusura è oltre lo stop (aggiunta prima del calcolo); uscita all'ultimo minuto della seduta."""
    if barre.empty or not atr > 0:
        return None
    o, h, lo_, c = (barre[x].to_numpy(float) for x in COLONNE)
    tocca = h >= livello if lato > 0 else lo_ <= livello
    if not tocca.any():
        return None
    k = int(np.argmax(tocca))
    oltre = o[k] >= livello if lato > 0 else o[k] <= livello
    ingresso = o[k] if oltre else livello
    d = FRAZIONE_STOP * atr
    stop = ingresso - d if lato > 0 else ingresso + d
    fuori = (lambda x: x <= stop) if lato > 0 else (lambda x: x >= stop)
    estremo = lo_ if lato > 0 else h
    if (oltre and fuori(estremo[k])) or (not oltre and fuori(c[k])):
        return Operazione(giorno, simbolo, lato, ingresso, barre.index[k], stop, barre.index[k], True, d)
    for j in range(k + 1, len(o)):
        if fuori(o[j]):
            return Operazione(giorno, simbolo, lato, ingresso, barre.index[k], o[j], barre.index[j], True, d)
        if fuori(estremo[j]):
            return Operazione(giorno, simbolo, lato, ingresso, barre.index[k], stop, barre.index[j], True, d)
    return Operazione(giorno, simbolo, lato, ingresso, barre.index[k], c[-1], barre.index[-1], False, d)


def azioni(capitale: float, prezzo: float, distanza: float, leva: float = LEVA) -> int:
    """Rischio dell'1% del capitale allo stop; al massimo un ventesimo di `leva` volte il capitale; azioni intere."""
    if distanza <= 0 or prezzo <= 0:
        return 0
    return int(math.floor(min(RISCHIO * capitale / distanza, leva * capitale / QUANTI / prezzo)))


def commissione(n: int, prezzo: float) -> float:
    return min(max(IB_MINIMO, IB_PER_AZIONE * n), IB_MASSIMO * n * prezzo) if n else 0.0


def conto(operazioni: list[Operazione], giorni: list[date], mezzo_in: float, mezzo_out: float, fattore: float = 1.0,
          scarto: bool = True, commissioni: bool = True, leva: float = LEVA) -> pd.Series:
    """I rendimenti di ogni giorno di borsa: il capitale dell'inizio del giorno decide le quantità; scarto, slittamento e commissioni
    moltiplicati per `fattore`; `scarto=False` toglie scarto e slittamento, `commissioni=False` le commissioni."""
    per: dict[date, list[Operazione]] = {}
    for op in operazioni:
        per.setdefault(op.giorno, []).append(op)
    v, out = CAPITALE, {}
    for g in giorni:
        utile = 0.0
        for op in per.get(g, []):
            n = azioni(v, op.ingresso, op.distanza_stop, leva)
            if not n:
                continue
            utile += n * op.lato * (op.uscita - op.ingresso)
            if scarto:
                uscita = mezzo_out + (SLIT_STOP if op.allo_stop else SLIT_CHIUSURA)
                utile -= fattore * n * (op.ingresso * (mezzo_in + SLIT_STOP) + op.uscita * uscita)
            if commissioni:
                utile -= fattore * (commissione(n, op.ingresso) + commissione(n, op.uscita))
        out[g] = utile / v
        v += utile
    return pd.Series(out)


# --- gli scarichi ------------------------------------------------------------------------------------------------------------------
def alle(g: date, h: int, m: int) -> datetime:
    return datetime.combine(g, time(h, m), NY).astimezone(UTC)


def _barre(simboli: list[str], quadro: str, inizio: datetime, fine: datetime) -> dict[str, pd.DataFrame]:
    """`alpaca.barre_di_piu` a gruppi; un simbolo che Alpaca rifiuta fa dividere il gruppo a metà finché si trova."""
    out = {}
    for i in range(0, len(simboli), GRUPPO):
        pila = [simboli[i:i + GRUPPO]]
        while pila:
            gruppo = pila.pop()
            aspetta_fuori_dagli_ordini()
            try:
                out.update(alpaca.barre_di_piu(gruppo, quadro, inizio, fine, asof="-"))
            except alpaca.ErroreAlpaca:
                if len(gruppo) > 1:
                    pila += [gruppo[:len(gruppo) // 2], gruppo[len(gruppo) // 2:]]
    return out


def primi_cinque(g: date, simboli: list[str]) -> pd.DataFrame:
    """La barra da 5 minuti delle 9:30 (open, high, low, close, volume) dei simboli quel giorno; memoria del lavoro, con l'elenco di
    chi non ha la barra (per non richiederlo)."""
    f, fv = cartella("primi5") / f"{g}.csv.gz", cartella("primi5") / f"{g}.vuoti"
    x = pd.read_csv(f, index_col=0, keep_default_na=False, na_values=[""]) if f.exists() else \
        pd.DataFrame(columns=COLONNE + ["volume"])
    vuoti = set(fv.read_text().split()) if fv.exists() else set()
    mancano = sorted(set(simboli) - set(x.index) - vuoti)
    if not mancano:
        return x
    righe = {}
    for s, df in _barre(mancano, "5Min", alle(g, 9, 30), alle(g, 9, 34)).items():
        df = df[[t.tz_convert(NY).time() == time(9, 30) for t in df.index]]
        if len(df):
            righe[s] = df.iloc[0][COLONNE + ["volume"]]
    nuovi = pd.DataFrame.from_dict(righe, orient="index") if righe else pd.DataFrame(columns=x.columns)
    x = pd.concat([x, nuovi])
    x = x[~x.index.duplicated()]
    x.index.name = "simbolo"
    x.to_csv(f)
    fv.write_text(" ".join(sorted(vuoti | (set(mancano) - set(righe)))))
    return x


def minuti(g: date, simboli: list[str]) -> dict[str, pd.DataFrame]:
    f = cartella("minuti") / f"{g}.csv.gz"
    if f.exists():
        x = pd.read_csv(f, keep_default_na=False, na_values=[""])
    else:
        b = _barre(simboli, "1Min", alle(g, 9, 35), alle(g, 15, 59)) if simboli else {}
        pezzi = [df.rename_axis("t").reset_index().assign(simbolo=s) for s, df in b.items() if len(df)]
        x = pd.concat(pezzi) if pezzi else pd.DataFrame(columns=["t"] + COLONNE + ["volume", "simbolo"])
        x.to_csv(f, index=False)
    out = {}
    for s, df in x.groupby("simbolo"):
        df = df.set_index(pd.to_datetime(df["t"], utc=True))
        ny = df.index.tz_convert(NY)
        df = df[(ny.time >= time(9, 35)) & (ny.time < time(16, 0))].sort_index()
        out[str(s)] = df[COLONNE].astype(float)
    return out


def scarto_misurato(campione: list[Operazione]) -> tuple[list[float], list[float]]:
    """Lo scarto relativo negli ultimi 15 secondi del minuto dell'ingresso e di quello dell'uscita (l'ultima quotazione valida)."""
    dentro, fuori = [], []
    for op in campione:
        for t, lista in ((op.ora_ingresso, dentro), (op.ora_uscita, fuori)):
            aspetta_fuori_dagli_ordini()
            try:
                q = alpaca.quotazioni(op.simbolo, (t + pd.Timedelta(seconds=45)).to_pydatetime(),
                                      (t + pd.Timedelta(seconds=60)).to_pydatetime(), massimo=5000)
            except alpaca.ErroreAlpaca:
                continue
            fot = fotografie_al_minuto(q)
            if len(fot):
                lista.append(float(scarto_relativo(fot).iloc[-1]))
    return dentro, fuori


# --- il calcolo --------------------------------------------------------------------------------------------------------------------
def calcola() -> dict:
    from stock.prove import p032
    from stock.prove.p003 import prepara_titolo
    spy = archivio.carica("SPY", "1Day_raw")
    giorni = sorted(g for g in controlli.date_ny(spy.index) if DAL <= g <= FINO)
    indice = {g: k for k, g in enumerate(giorni)}
    _, membri = fine_mese()
    vs = p032.vendite_scoperto()
    simboli = sorted(({s for v in vs.values() for s in v} | set().union(*membri.values())) - {"SPY", "IWM", "QQQ"})
    nomi = alpaca.nomi_dei_titoli()
    simboli = [s for s in simboli if ORDINARIE.fullmatch(s) and not tono.e_un_fondo(nomi.get(s, ""))]
    print(f"(1) titoli {len(simboli)}", flush=True)
    passa: dict[date, list[str]] = {g: [] for g in giorni}
    fattore: dict[str, dict[date, float]] = {}
    atr: dict[tuple[str, date], float] = {}
    rotti = con_prezzi = 0
    for s in simboli:
        grezzo = archivio.carica(s, TIPI["raw"])
        if grezzo is None or grezzo.empty:
            continue
        try:
            df, rett, _ = prepara_titolo(s, FINO, TIPI["raw"], TIPI["az"])
        except Exception:  # noqa: BLE001 — titolo con i dati rotti: si conta e resta fuori
            rotti += 1
            continue
        if len(df) <= SEDUTE + 1:
            continue
        con_prezzi += 1
        d = filtri(df, rett, grezzo["volume"])
        si = [g for g in d.index[d["passa"].to_numpy()] if g in indice]
        if not si:
            continue
        fattore[s] = {g: float(v) for g, v in d["f"].items() if g in indice}
        for g in si:
            passa[g].append(s)
            atr[(s, g)] = float(d.at[g, "atr"])
    print(f"(1) con i prezzi {con_prezzi}, rotti {rotti}, che passano almeno un giorno {len(fattore)}; per giorno: mediana "
          f"{np.median([len(v) for v in passa.values()]):.0f}", flush=True)
    servono: dict[date, set[str]] = {g: set() for g in giorni}
    for k, g in enumerate(giorni):
        for g0 in giorni[max(0, k - SEDUTE):k + 1]:
            servono[g0].update(passa[g])
    vol: dict[date, dict[str, float]] = {}
    candela: dict[date, pd.DataFrame] = {}
    for k, g in enumerate(giorni):
        p5 = primi_cinque(g, sorted(servono[g]))
        p5 = p5[p5.index.isin(servono[g])]
        vol[g] = {s: float(v) / fattore[s][g] for s, v in p5["volume"].items() if g in fattore.get(s, {}) and fattore[s][g] > 0}
        candela[g] = p5.loc[p5.index.isin(passa[g]), COLONNE].astype(float)
        if k % 100 == 0:
            print(f"(2) {g}: {len(p5)} titoli con la barra delle 9:30", flush=True)
    ops: list[Operazione] = []
    scelti_n = []
    for k, g in enumerate(giorni):
        if k < SEDUTE:
            continue
        rv, lati, livelli = {}, {}, {}
        for s, r in candela[g].iterrows():
            v = volume_relativo(vol[g].get(s, 0.0), [vol[g0].get(s) for g0 in giorni[k - SEDUTE:k]])
            lato = 1 if r["close"] > r["open"] else -1 if r["close"] < r["open"] else 0
            if v is not None and lato:
                rv[s], lati[s], livelli[s] = v, lato, float(r["high"] if lato > 0 else r["low"])
        scelti = scegli(rv)
        scelti_n.append(len(scelti))
        b = minuti(g, scelti)
        for s in scelti:
            op = esegui(b.get(s, pd.DataFrame(columns=COLONNE)), lati[s], livelli[s], atr[(s, g)], g, s)
            if op:
                ops.append(op)
        if k % 100 == 0:
            print(f"(4) {g}: scelti {len(scelti)}, operazioni finora {len(ops)}", flush=True)
    campione = random.Random(SEME).sample(ops, min(CAMPIONE, len(ops)))
    dentro, fuori = scarto_misurato(campione)
    if not dentro or not fuori:
        raise SystemExit("lo scarto non si è potuto misurare: nessun risultato")
    return dict(ops=ops, giorni=giorni[SEDUTE:], dentro=dentro, fuori=fuori, passa=passa, titoli=con_prezzi, scelti=scelti_n)


def main():
    c = calcola()
    ops, giorni = c["ops"], c["giorni"]
    mi, mo = float(np.median(c["dentro"])) / 2, float(np.median(c["fuori"])) / 2
    g = {"costi": conto(ops, giorni, mi, mo), "costi doppi": conto(ops, giorni, mi, mo, 2.0),
         "solo commissioni": conto(ops, giorni, 0.0, 0.0, scarto=False),
         "senza costi": conto(ops, giorni, 0.0, 0.0, scarto=False, commissioni=False),
         "senza leva": conto(ops, giorni, mi, mo, leva=1.0)}
    gc = g["costi"]
    a, b = gc.index.min(), gc.index.max()
    spy = comprare_e_tenere("SPY", a, b)
    miscela = carica_serie()["P025_miscela"]
    salva_serie("P035_azioni_in_gioco", gc)
    comuni = miscela.index.intersection(gc.index)
    salva_serie("P035_miscela", 0.75 * miscela.loc[comuni] + 0.25 * gc.loc[comuni])
    tutte = carica_serie()
    nuova = tutte["P035_miscela"]
    ast = asticella.sharpe_corretto(gc, tutte)
    q = [float((1 + gc[(gc.index >= x) & (gc.index < y)]).prod() - 1)
         for x, y in (f["prova"] for f in finestre(date(2016, 1, 1), date(2025, 1, 1), chiuso_dal=date(2025, 1, 1))) if x >= a]
    quota = sum(x > 0 for x in q) / len(q)
    sr_c, sr_2 = sr(gc), sr(g["costi doppi"])
    da_sola = sr_c > sr(spy) and ast["sharpe_corretto"] >= 0.95 and sr_2 > 0 and quota >= 0.6
    corr = float(np.corrcoef(miscela.loc[comuni], gc.loc[comuni])[0, 1])
    spy_c = comprare_e_tenere("SPY", comuni.min(), comuni.max())
    t_parte = t_di(gc.to_numpy())
    vinte = campionamento(miscela.loc[comuni], gc.loc[comuni])
    entra = sr(gc.loc[comuni]) > 0 and sr(g["costi doppi"].reindex(comuni).dropna()) > 0 and corr < 0.3 \
        and sr(nuova) > sr(miscela.loc[comuni]) and sr(nuova) > sr(spy_c) and t_parte >= 1.3 and vinte >= 0.8
    anni = (1 + gc).groupby(pd.Index([d.year for d in gc.index])).prod() - 1
    lordo = np.array([op.lato * (op.uscita - op.ingresso) / op.ingresso for op in ops])
    stop_pb = np.array([op.distanza_stop / op.ingresso for op in ops]) * 1e4
    sd, sf = np.array(c["dentro"]) * 1e4, np.array(c["fuori"]) * 1e4
    costo = (mi + SLIT_STOP) + mo + float(np.mean([SLIT_STOP if op.allo_stop else SLIT_CHIUSURA for op in ops]))
    testo = ["# Prova 35 — risultati", "",
             f"Calcolato da `python -m stock.prove.p035` il {datetime.now(UTC):%Y-%m-%d %H:%M} UTC con le regole di "
             f"`P035_azioni_in_gioco.md` (committate prima, con l'aggiunta sul minuto dell'ingresso). Dal {a} al {b}. Nel conto "
             f"dell'asticella: {len(tutte)} serie.", "",
             f"* Titoli con i prezzi {c['titoli']}; che passano i filtri del giorno: mediana "
             f"{np.median([len(v) for v in c['passa'].values()]):.0f}; scelti al giorno: mediana {np.median(c['scelti']):.0f}. "
             f"**Operazioni {len(ops)}**, allo stop {np.mean([op.allo_stop for op in ops]):.0%}, in guadagno prima dei costi "
             f"{(lordo > 0).mean():.0%}; **a operazione prima dei costi {lordo.mean():+.3%}** (t {t_di(lordo):.2f}).",
             f"* **Lo scarto misurato** su {len(sd)} ingressi e {len(sf)} uscite (campione di {CAMPIONE} operazioni a caso): all'ingresso "
             f"mediana {np.median(sd):.1f} punti base (media {sd.mean():.1f}, 90° percentile {np.percentile(sd, 90):.1f}); all'uscita "
             f"mediana {np.median(sf):.1f} (media {sf.mean():.1f}). Lo stop è a {np.median(stop_pb):.1f} punti base dall'ingresso "
             f"(mediana; media {stop_pb.mean():.1f}). **Costo a operazione senza commissioni: {costo:.3%}.**", "",
             "| | La strategia | Tenere lo SPY |", "|---|---|---|",
             f"| Guadagno totale senza costi / con le sole commissioni / con i costi / costi doppi | {tot(g['senza costi']):+.1%} / "
             f"{tot(g['solo commissioni']):+.1%} / {tot(gc):+.1%} / {tot(g['costi doppi']):+.1%} | {tot(spy):+.1%} |",
             f"| **1.** Sharpe annuo con i costi | **{sr_c:.2f}** (senza costi {sr(g['senza costi']):.2f}, con le sole commissioni "
             f"{sr(g['solo commissioni']):.2f}) | {sr(spy):.2f} |",
             f"| **2.** Sharpe corretto (soglia 0,95) | {ast['sharpe_corretto']:.2f} (gruppi {ast['gruppi']}, t {ast['t_sharpe']:.2f}) | — |",
             f"| **3.** Sharpe con i costi doppi (> 0) | {sr_2:.2f} | — |",
             f"| **4.** Trimestri in guadagno (60%) | {sum(x > 0 for x in q)} su {len(q)} ({quota:.0%}) | — |",
             f"| Perdita massima dal picco | {dd(gc):.1%} | {dd(spy):.1%} |",
             f"| Senza leva (al massimo un ventesimo del capitale a operazione) | Sharpe {sr(g['senza leva']):.2f}, "
             f"{tot(g['senza leva']):+.1%} | — |",
             f"| Anno per anno | {' '.join(f'{y}: {x:+.1%}' for y, x in anni.items())} | — |",
             f"| **Esito da sola** | **{'passa la ricerca' if da_sola else 'bocciata'}** | |", "",
             f"**Per entrare nella miscela** (giorni in comune dal {comuni.min()} al {comuni.max()}): Sharpe della parte "
             f"{sr(gc.loc[comuni]):.2f}, con i costi doppi {sr(g['costi doppi'].reindex(comuni).dropna()):.2f}; correlazione con la "
             f"miscela {corr:.2f} (soglia 0,3); miscela nuova {sr(nuova):.2f} contro {sr(miscela.loc[comuni]):.2f} della miscela e "
             f"{sr(spy_c):.2f} del tenere lo SPY; **t dello Sharpe della parte {t_parte:.2f} (soglia 1,3)**; **miscela nuova più alta "
             f"nel {vinte:.0%} dei campionamenti (soglia 80%)**. **Esito: "
             f"{'entra nella miscela (prima il revisore, poi la misura in avanti)' if entra else 'non entra'}**", "",
             "Limite noto: i titoli vengono dall'archivio delle prove 28-34 (simboli di FINRA dal 2018 e membri dell'S&P 500): per il "
             "2016-2017 mancano i titoli spariti prima del 2018. Nel conto: 2 prove (87)."]
    (QUI / "P035_risultati.md").write_text("\n".join(testo) + "\n")
    print("\n".join(testo[-16:]))


if __name__ == "__main__":
    main()
