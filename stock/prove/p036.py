"""Prova 36 — gli acquisti dei dirigenti comprati due minuti dopo la pubblicazione alla SEC, venduti all'apertura dopo (idea I22).

    python -m stock.prove.p036            # servono le chiavi di Alpaca: gira su GitHub (azioni-ricerca); si riprende da dove si è fermato

Regole: `P036_dirigenti_subito.md` (scritte e committate prima del calcolo). Tappe: (1) i depositi con l'ora vera
(`dati/P036_depositi.csv.gz`, dati pubblici della SEC) e i prezzi al giorno dei titoli; (2) i segnali (la soglia dei 100'000 dollari
nella notte di borsa); (3) le barre al minuto dalle 4:00 alle 19:59 dei giorni che servono; (4) le operazioni e la scelta (al massimo
10 insieme); (5) lo scarto misurato su 500 ingressi; (6) il conto, le letture accanto e l'esame. I prezzi restano nella memoria del
lavoro (`~/stock_dati/p036`), mai nel repository.
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

from stock.dati import alpaca, archivio, controlli
from stock.dati.scarto import fotografie_al_minuto, scarto_relativo
from stock.prove.p001 import CAPITALE, QUI, carica_serie, comprare_e_tenere, salva_serie
from stock.prove.p027 import aspetta_fuori_dagli_ordini
from stock.prove.p032 import campionamento, t_di
from stock.prove.p035 import _barre, alle, commissione, dd, sr, tot
from stock.simulatore import asticella
from stock.simulatore.finestre import finestre

NY = ZoneInfo("America/New_York")
DAL, FINO = date(2016, 1, 4), date(2024, 12, 31)
SOGLIA, RITARDO = 100_000.0, 2
QUOTA, MASSIMO = 0.10, 10
SLIT_IN, SLIT_OUT = 2e-4, 2e-4
SCARTO_PREZZO = 0.5
CAMPIONE, SEME, MISURE_MINIME = 500, 36, 30
INIZIO, FINE, APERTURA, CHIUSURA = time(4, 0), time(19, 59), time(9, 30), time(16, 0)
TIPI = {"raw": "1Day_allora", "az": "azioni_allora", "asof": "-"}
RITARDI_LETTURA = (1, 5, 15, 60)
GIORNI_DI_RICERCA = 5           # un titolo senza nessuna barra per 5 giorni di borsa (sospeso, tolto) resta fuori, e si conta


def cartella(nome: str):
    p = archivio.cartella_dati() / "p036" / nome
    p.mkdir(parents=True, exist_ok=True)
    return p


# --- (2) i segnali -----------------------------------------------------------------------------------------------------------------
def notte(t: pd.Timestamp, calendario: list[date]) -> date | None:
    """La «notte di borsa» di un istante: il giorno di borsa D tale che l'istante cade dopo le 16:00 della seduta prima e entro le
    16:00 di D (un istante dopo le 16:00, o in un giorno senza borsa, appartiene al giorno di borsa dopo)."""
    ny = t.tz_convert(NY)
    g = ny.date()
    k = bisect.bisect_left(calendario, g)
    if k < len(calendario) and calendario[k] == g and ny.time() <= CHIUSURA:
        return g
    k = bisect.bisect_right(calendario, g)
    return calendario[k] if k < len(calendario) else None


def segnali(eventi: pd.DataFrame, calendario: list[date], soglia: float = SOGLIA) -> pd.DataFrame:
    """Per ogni azienda e notte di borsa, il modulo che porta la somma dei moduli ad almeno `soglia` dollari (al massimo uno).
    `eventi`: colonne numero, simbolo, valore, accettato (UTC). Esce ordinato per ora d'accettazione."""
    e = eventi.sort_values(["accettato", "numero"]).copy()
    e["notte"] = [notte(t, calendario) for t in e["accettato"]]
    e = e.dropna(subset=["notte"])
    e["somma"] = e.groupby(["simbolo", "notte"])["valore"].cumsum()
    e = e[e["somma"] >= soglia]
    return e.groupby(["simbolo", "notte"], sort=False).head(1).sort_values(["accettato", "numero"]).reset_index(drop=True)


# --- (4) l'ingresso, l'uscita, la scelta -------------------------------------------------------------------------------------------
def primo_istante(t: pd.Timestamp, ritardo: int, calendario: list[date]) -> tuple[date, pd.Timestamp] | None:
    """Il giorno di borsa e il primo istante (inizio di un minuto, UTC) da cui un ingresso è possibile: l'accettazione più `ritardo`
    minuti, arrotondata al minuto dopo; fuori dalla finestra delle 4:00-19:59 di un giorno di borsa, le 4:00 del giorno di borsa dopo."""
    x = (t + pd.Timedelta(minutes=ritardo)).ceil("min")
    ny = x.tz_convert(NY)
    g = ny.date()
    k = bisect.bisect_left(calendario, g)
    if k < len(calendario) and calendario[k] == g and ny.time() <= FINE:
        if ny.time() < INIZIO:
            return g, pd.Timestamp(alle(g, 4, 0))
        return g, x
    k = bisect.bisect_right(calendario, g)
    if k >= len(calendario):
        return None
    g = calendario[k]
    return g, pd.Timestamp(alle(g, 4, 0))


def cerca_ingresso(barre: pd.DataFrame | None, dal: pd.Timestamp) -> tuple[pd.Timestamp, float] | None:
    """La prima barra al minuto che inizia da `dal` in poi, fino alle 19:59 di New York di quel giorno: (inizio, apertura)."""
    if barre is None or barre.empty:
        return None
    b = barre[barre.index >= dal]
    if b.empty:
        return None
    t = b.index[0]
    ny = t.tz_convert(NY)
    if ny.date() != dal.tz_convert(NY).date() or not (INIZIO <= ny.time() <= FINE):
        return None
    return t, float(b["open"].iloc[0])


def giorno_d_uscita(t: pd.Timestamp, calendario: list[date]) -> date | None:
    """La prima seduta che apre dopo l'ingresso: quella del giorno se l'ingresso è prima delle 9:30, altrimenti la seduta dopo."""
    ny = t.tz_convert(NY)
    g = ny.date()
    if ny.time() < APERTURA:
        return g
    k = bisect.bisect_right(calendario, g)
    return calendario[k] if k < len(calendario) else None


def fascia(t: pd.Timestamp) -> str:
    x = t.tz_convert(NY).time()
    if APERTURA <= x < CHIUSURA:
        return "in seduta"
    return "dopo la chiusura" if x >= CHIUSURA else "prima dell'apertura"


@dataclass(frozen=True)
class Operazione:
    simbolo: str
    accettato: pd.Timestamp
    ora_ingresso: pd.Timestamp
    giorno_in: date
    prezzo_in: float          # non rettificato (come scambiato allora)
    f_in: float               # fattore della rettifica del giorno dell'ingresso (chiusura rettificata / chiusura)
    giorno_out: date
    prezzo_out: float         # apertura ufficiale non rettificata
    f_out: float
    spy_lordo: float = float("nan")
    da_prima: float = float("nan")    # dalla chiusura prima del deposito all'ingresso, rettificato

    @property
    def lordo(self) -> float:
        return self.prezzo_out * self.f_out / (self.prezzo_in * self.f_in) - 1


def scegli_ingressi(ops: list[Operazione], massimo: int = MASSIMO) -> list[Operazione]:
    """In ordine d'ingresso: al massimo `massimo` posizioni aperte insieme; una posizione aperta sullo stesso titolo blocca."""
    aperte: list[Operazione] = []
    out = []
    for op in sorted(ops, key=lambda o: (o.ora_ingresso, o.simbolo)):
        aperte = [a for a in aperte if pd.Timestamp(alle(a.giorno_out, 9, 30)) > op.ora_ingresso]
        if len(aperte) >= massimo or any(a.simbolo == op.simbolo for a in aperte):
            continue
        aperte.append(op)
        out.append(op)
    return out


def conto(ops: list[Operazione], giorni: list[date], mezzi: dict[str, float], fattore: float = 1.0, costi: bool = True,
          coperta: bool = False) -> pd.Series:
    """I rendimenti di ogni giorno di borsa: il 10% del conto all'inizio del giorno dell'ingresso, azioni intere, il guadagno contato
    nel giorno dell'uscita. `mezzi`: metà dello scarto per «in seduta» e «fuori seduta». `coperta`: la stessa cifra venduta sullo SPY."""
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
            if n <= 0:
                continue
            valore = n * op.prezzo_in
            utile = valore * op.lordo
            copri = coperta and np.isfinite(op.spy_lordo)       # senza la barra dello SPY in quel minuto, quell'operazione resta scoperta
            if copri:
                utile -= valore * op.spy_lordo
            if costi:
                mezzo = mezzi["in seduta" if fascia(op.ora_ingresso) == "in seduta" else "fuori seduta"]
                utile -= fattore * (valore * (mezzo + SLIT_IN) + valore * (1 + op.lordo) * SLIT_OUT)
                utile -= fattore * (commissione(n, op.prezzo_in) + commissione(n, op.prezzo_in * (1 + op.lordo)))
                if copri:
                    utile -= fattore * (2 * valore * SLIT_IN + 2.0)
            da_contare[op.giorno_out] = da_contare.get(op.giorno_out, 0.0) + utile
        utile_g = da_contare.pop(g, 0.0)
        out[g] = utile_g / inizio
        v += utile_g
    return pd.Series(out)


# --- (3) le barre al minuto --------------------------------------------------------------------------------------------------------
def barre_del_giorno(g: date, simboli: list[str]) -> dict[str, pd.DataFrame]:
    """Le barre al minuto (apertura) dalle 4:00 alle 19:59 di New York dei simboli quel giorno; memoria del lavoro, con l'elenco di
    chi non ha barre (per non richiederlo)."""
    f, fv = cartella("minuti") / f"{g}.csv.gz", cartella("minuti") / f"{g}.vuoti"
    x = pd.read_csv(f, keep_default_na=False, na_values=[""]) if f.exists() else pd.DataFrame(columns=["t", "open", "simbolo"])
    vuoti = set(fv.read_text().split()) if fv.exists() else set()
    mancano = sorted(set(simboli) - set(x["simbolo"].astype(str)) - vuoti)
    if mancano:
        b = _barre(mancano, "1Min", alle(g, 4, 0), alle(g, 20, 0))
        pezzi = [df.rename_axis("t").reset_index()[["t", "open"]].assign(simbolo=s) for s, df in b.items() if len(df)]
        if pezzi:
            x = pd.concat([x] + pezzi, ignore_index=True)
        x.to_csv(f, index=False)
        fv.write_text(" ".join(sorted(vuoti | (set(mancano) - {s for s, df in b.items() if len(df)}))))
    out = {}
    for s, df in x.groupby("simbolo"):
        if str(s) not in simboli:
            continue
        df = df.set_index(pd.to_datetime(df["t"], utc=True)).sort_index()
        ny = df.index.tz_convert(NY)
        out[str(s)] = df[(ny.time >= INIZIO) & (ny.time <= FINE)][["open"]].astype(float)
    return out


def scarto_misurato(campione: list[Operazione]) -> dict[str, list[float]]:
    """Lo scarto relativo all'ultima quotazione valida prima della fine del minuto dell'ingresso, per fascia."""
    out: dict[str, list[float]] = {"in seduta": [], "fuori seduta": []}
    for op in campione:
        t = op.ora_ingresso
        chiave = "in seduta" if fascia(t) == "in seduta" else "fuori seduta"
        for da in (45, 0):
            aspetta_fuori_dagli_ordini()
            try:
                q = alpaca.quotazioni(op.simbolo, (t + pd.Timedelta(seconds=da)).to_pydatetime(),
                                      (t + pd.Timedelta(seconds=60)).to_pydatetime(), massimo=5000)
            except alpaca.ErroreAlpaca:
                break
            fot = fotografie_al_minuto(q)
            if len(fot):
                out[chiave].append(float(scarto_relativo(fot).iloc[-1]))
                break
    return out


# --- il calcolo --------------------------------------------------------------------------------------------------------------------
def giorni_del_titolo(s: str) -> dict[date, tuple[float, float, float]] | None:
    """Giorno → (apertura, chiusura, fattore della rettifica), non rettificati, fino al 31 dicembre 2024."""
    from stock.prove.p003 import prepara_titolo
    try:
        df, rett, _ = prepara_titolo(s, FINO, TIPI["raw"], TIPI["az"])
    except Exception:  # noqa: BLE001 — titolo con i dati rotti: resta fuori, si conta
        return None
    g = controlli.date_ny(df.index)
    r = rett.reindex(pd.Index(g)).to_numpy(float)
    return {d: (float(o), float(c), float(x / c)) for d, o, c, x in zip(g, df["open"], df["close"], r) if c > 0 and np.isfinite(x)}


def operazioni(sg: pd.DataFrame, ritardo: int, calendario: list[date], prezzi: dict, spy: dict) -> tuple[list[Operazione], dict]:
    """Le operazioni dei segnali con un ritardo; `prezzi`/`spy`: giorno → (apertura, chiusura, fattore). Conta chi resta fuori."""
    attesa: dict[date, list[tuple]] = {}
    fuori = {"senza ingresso": 0, "uscita oltre il 2024 o senza prezzo": 0}
    for r in sg.itertuples():
        p = primo_istante(r.accettato, ritardo, calendario)
        if p is None:
            fuori["senza ingresso"] += 1
            continue
        attesa.setdefault(p[0], []).append((r, p[1], 0))
    ops = []
    while attesa:
        g = min(attesa)
        lista = attesa.pop(g)
        barre = barre_del_giorno(g, sorted({r.simbolo for r, _, _ in lista} | {"SPY"}))
        for r, dal, tentativi in lista:
            x = cerca_ingresso(barre.get(r.simbolo), dal)
            if x is None:
                k = bisect.bisect_right(calendario, g)
                if tentativi < GIORNI_DI_RICERCA - 1 and k < len(calendario):
                    nuovo = calendario[k]
                    attesa.setdefault(nuovo, []).append((r, pd.Timestamp(alle(nuovo, 4, 0)), tentativi + 1))
                else:
                    fuori["senza ingresso"] += 1
                continue
            t, prezzo = x
            gu = giorno_d_uscita(t, calendario)
            d = prezzi.get(r.simbolo, {})
            if gu is None or gu > FINO or g not in d or gu not in d or g not in spy or gu not in spy:
                fuori["uscita oltre il 2024 o senza prezzo"] += 1
                continue
            sb = barre.get("SPY")
            spy_lordo = float("nan")
            if sb is not None and len(sb.loc[:t]):
                spy_in = float(sb.loc[:t]["open"].iloc[-1])
                spy_lordo = spy[gu][0] * spy[gu][2] / (spy_in * spy[g][2]) - 1
            # la chiusura prima del deposito: l'ultima seduta chiusa prima dell'accettazione
            n = notte(r.accettato, calendario)
            kp = bisect.bisect_left(calendario, n) - 1 if n else -1
            da_prima = float("nan")
            if kp >= 0 and calendario[kp] in d:
                c0 = d[calendario[kp]]
                da_prima = prezzo * d[g][2] / (c0[1] * c0[2]) - 1
            ops.append(Operazione(r.simbolo, r.accettato, t, g, prezzo, d[g][2], gu, d[gu][0], d[gu][2], spy_lordo, da_prima))
    return ops, fuori


def calcola() -> dict:
    from stock.prove.p027 import scarica
    ev = pd.read_csv(QUI / "dati" / "P036_depositi.csv.gz", dtype={"simbolo": str}, keep_default_na=False, na_values=[""])
    ev["accettato"] = pd.to_datetime(ev["accettato"], utc=True)
    ev["giorno_op"] = pd.to_datetime(ev["giorno_op"], errors="coerce").dt.date
    ny = ev["accettato"].dt.tz_convert(NY).dt.date
    ev = ev[(ny >= DAL) & (ny <= FINO)].reset_index(drop=True)
    simboli = sorted(set(ev["simbolo"]))
    print(f"(1) moduli {len(ev)}, titoli {len(simboli)}", flush=True)
    scarica(simboli + ["SPY"], TIPI["raw"], TIPI["az"], TIPI["asof"])
    prezzi, rotti = {}, 0
    for s in simboli:
        x = giorni_del_titolo(s)
        if x is None:
            rotti += 1
        else:
            prezzi[s] = x
    spy = giorni_del_titolo("SPY")
    calendario = sorted(g for g in spy if g >= date(2015, 12, 1))
    # la pulizia della prova 18: il prezzo dell'operazione entro il 50% dalla chiusura del giorno dell'operazione (o del giorno prima)
    def pulito(s: str, g: date | None, p: float) -> bool:
        d = prezzi.get(s)
        if d is None or pd.isna(g) or not p > 0:
            return False
        k = bisect.bisect_right(calendario, g) - 1
        while k >= 0 and calendario[k] not in d:
            k -= 1
        return k >= 0 and abs(p / d[calendario[k]][1] - 1) <= SCARTO_PREZZO
    ok = [pulito(s, g, p) for s, g, p in zip(ev["simbolo"], ev["giorno_op"], ev["prezzo_op"])]
    scartati = len(ev) - sum(ok)
    ev = ev[ok].reset_index(drop=True)
    sg = segnali(ev, calendario)
    print(f"(2) titoli con i prezzi {len(prezzi)} (rotti {rotti}); moduli scartati dalla pulizia {scartati}; segnali {len(sg)}", flush=True)
    tutte, fuori = operazioni(sg, RITARDO, calendario, prezzi, spy)
    ops = scegli_ingressi(tutte)
    print(f"(4) operazioni possibili {len(tutte)}, scelte {len(ops)}; fuori {fuori}", flush=True)
    fuori_seduta = sum(fascia(o.ora_ingresso) != "in seduta" for o in ops)
    if ops and fuori_seduta < 0.1 * len(ops):
        # due depositi su tre arrivano dopo la chiusura: se quasi nessun ingresso è fuori seduta, le barre degli orari estesi non arrivano
        raise SystemExit(f"ingressi fuori seduta {fuori_seduta} su {len(ops)}: mancano le barre degli orari estesi; la prova non si conta")
    letture = {}
    for rit in RITARDI_LETTURA:
        o, _ = operazioni(sg, rit, calendario, prezzi, spy)
        letture[rit] = scegli_ingressi(o)
        print(f"(4) ritardo {rit} minuti: {len(letture[rit])}", flush=True)
    rng = random.Random(SEME)
    campione = rng.sample(ops, min(CAMPIONE, len(ops)))
    misure = scarto_misurato(campione)
    print(f"(5) scarto misurato: in seduta {len(misure['in seduta'])}, fuori seduta {len(misure['fuori seduta'])}", flush=True)
    for k, v in misure.items():
        servono = any((fascia(o.ora_ingresso) == "in seduta") == (k == "in seduta") for o in ops)
        if servono and len(v) < MISURE_MINIME:
            raise SystemExit(f"scarto non misurabile per «{k}»: {len(v)} misure (servono almeno {MISURE_MINIME}); la prova non si conta")
    giorni = [g for g in calendario if DAL <= g <= FINO]
    return {"ops": ops, "giorni": giorni, "misure": misure, "letture": letture, "segnali": len(sg), "moduli": len(ev) + scartati,
            "scartati": scartati, "titoli": len(prezzi), "rotti": rotti, "fuori": fuori, "possibili": len(tutte)}


def _riga_fascia(nome: str, x: list[Operazione], mezzi: dict) -> str:
    if not x:
        return f"| {nome} | 0 | — | — | — | — |"
    lordo = np.array([o.lordo for o in x])
    rel = np.array([o.lordo - o.spy_lordo for o in x if np.isfinite(o.spy_lordo)])
    costo = np.array([mezzi["in seduta" if fascia(o.ora_ingresso) == "in seduta" else "fuori seduta"] + SLIT_IN + SLIT_OUT for o in x])
    prima = np.array([o.da_prima for o in x if np.isfinite(o.da_prima)])
    return (f"| {nome} | {len(x)} | {lordo.mean():+.3%} (t {t_di(lordo):.2f}) | {rel.mean():+.3%} (t {t_di(rel):.2f}) | "
            f"{(lordo - costo).mean():+.3%} | {prima.mean():+.3%} |")


def main():
    c = calcola()
    ops, giorni, m = c["ops"], c["giorni"], c["misure"]
    mezzi = {k: (float(np.median(v)) / 2 if v else 0.0) for k, v in m.items()}
    g = {"costi": conto(ops, giorni, mezzi), "costi doppi": conto(ops, giorni, mezzi, 2.0),
         "senza costi": conto(ops, giorni, mezzi, costi=False), "coperta": conto(ops, giorni, mezzi, coperta=True)}
    gc = g["costi"]
    a, b = gc.index.min(), gc.index.max()
    spy = comprare_e_tenere("SPY", a, b)
    miscela = carica_serie()["P025_miscela"]
    salva_serie("P036_dirigenti_subito", gc)
    comuni = miscela.index.intersection(gc.index)
    salva_serie("P036_miscela", 0.75 * miscela.loc[comuni] + 0.25 * gc.loc[comuni])
    tutte = carica_serie()
    nuova = tutte["P036_miscela"]
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
    lordo = np.array([o.lordo for o in ops])
    fasce = {k: [o for o in ops if fascia(o.ora_ingresso) == k] for k in ("in seduta", "dopo la chiusura", "prima dell'apertura")}
    pb = {k: np.array(v) * 1e4 for k, v in m.items()}
    righe_ritardi = []
    for rit in (1, 2, 5, 15, 60):
        o = ops if rit == RITARDO else c["letture"][rit]
        s = conto(o, giorni, mezzi)
        lo = np.array([x.lordo for x in o]) if o else np.array([np.nan])
        righe_ritardi.append(f"{rit} min: {len(o)} operazioni, a operazione prima dei costi {np.nanmean(lo):+.3%}, Sharpe con i costi "
                             f"{sr(s):.2f}")
    testo = ["# Prova 36 — risultati", "",
             f"Calcolato da `python -m stock.prove.p036` il {datetime.now(UTC):%Y-%m-%d %H:%M} UTC con le regole di "
             f"`P036_dirigenti_subito.md` (committate prima). Dal {a} al {b}. Nel conto dell'asticella: {len(tutte)} serie.", "",
             f"* Moduli {c['moduli']} (scartati dalla pulizia del prezzo {c['scartati']}); titoli con i prezzi {c['titoli']} (rotti "
             f"{c['rotti']}); **segnali {c['segnali']}**; operazioni possibili {c['possibili']}, fuori {c['fuori']}; **scelte "
             f"{len(ops)}** (al massimo 10 insieme), in guadagno prima dei costi {(lordo > 0).mean():.0%}; **a operazione prima dei "
             f"costi {lordo.mean():+.3%}** (t {t_di(lordo):.2f}).",
             f"* **Lo scarto misurato** (campione di {CAMPIONE} ingressi a caso): in seduta {len(pb['in seduta'])} misure, mediana "
             + (f"{np.median(pb['in seduta']):.1f} punti base (media {pb['in seduta'].mean():.1f}, 90° percentile "
                f"{np.percentile(pb['in seduta'], 90):.1f})" if len(pb["in seduta"]) else "—")
             + f"; fuori seduta {len(pb['fuori seduta'])} misure, mediana "
             + (f"{np.median(pb['fuori seduta']):.1f} (media {pb['fuori seduta'].mean():.1f}, 90° percentile "
                f"{np.percentile(pb['fuori seduta'], 90):.1f})" if len(pb["fuori seduta"]) else "—") + ".", "",
             "| | La strategia | Tenere lo SPY |", "|---|---|---|",
             f"| Guadagno totale senza costi / con i costi / costi doppi | {tot(g['senza costi']):+.1%} / {tot(gc):+.1%} / "
             f"{tot(g['costi doppi']):+.1%} | {tot(spy):+.1%} |",
             f"| **1.** Sharpe annuo con i costi | **{sr_c:.2f}** (senza costi {sr(g['senza costi']):.2f}) | {sr(spy):.2f} |",
             f"| **2.** Sharpe corretto (soglia 0,95) | {ast['sharpe_corretto']:.2f} (gruppi {ast['gruppi']}, t {ast['t_sharpe']:.2f}) | — |",
             f"| **3.** Sharpe con i costi doppi (> 0) | {sr_2:.2f} | — |",
             f"| **4.** Trimestri in guadagno (60%) | {sum(x > 0 for x in q)} su {len(q)} ({quota:.0%}) | — |",
             f"| Perdita massima dal picco | {dd(gc):.1%} | {dd(spy):.1%} |",
             f"| Coperta con lo SPY (da leggere) | Sharpe {sr(g['coperta']):.2f}, {tot(g['coperta']):+.1%} | — |",
             f"| Anno per anno | {' '.join(f'{y}: {x:+.1%}' for y, x in anni.items())} | — |",
             f"| **Esito da sola** | **{'passa la ricerca' if da_sola else 'bocciata'}** | |", "",
             f"**Per entrare nella miscela** (giorni in comune dal {comuni.min()} al {comuni.max()}): Sharpe della parte "
             f"{sr(gc.loc[comuni]):.2f}, con i costi doppi {sr(g['costi doppi'].reindex(comuni).dropna()):.2f}; correlazione con la "
             f"miscela {corr:.2f} (soglia 0,3); miscela nuova {sr(nuova):.2f} contro {sr(miscela.loc[comuni]):.2f} della miscela e "
             f"{sr(spy_c):.2f} del tenere lo SPY; **t dello Sharpe della parte {t_parte:.2f} (soglia 1,3)**; **miscela nuova più alta "
             f"nel {vinte:.0%} dei campionamenti (soglia 80%)**. **Esito: "
             f"{'entra nella miscela (prima il revisore, poi la misura in avanti)' if entra else 'non entra'}**", "",
             "**Da leggere accanto (non cambiano l'esito).** Per fascia dell'ingresso:", "",
             "| Fascia | Operazioni | A operazione prima dei costi | Meno lo SPY negli stessi minuti | Dopo scarto e slittamento | "
             "Dalla chiusura prima del deposito all'ingresso |", "|---|---|---|---|---|---|",
             _riga_fascia("tutte", ops, mezzi), *(_riga_fascia(k, v, mezzi) for k, v in fasce.items()), "",
             "Con altri ritardi dopo l'accettazione: " + "; ".join(righe_ritardi) + ".", "",
             "Limite noto: gli orari d'accettazione vengono dagli elenchi dei depositi delle aziende dell'S&P 500 in cache (25 moduli "
             "senza ora). Nel conto: 2 prove (89)."]
    (QUI / "P036_risultati.md").write_text("\n".join(testo) + "\n")
    print("\n".join(testo[-14:]))


if __name__ == "__main__":
    main()
