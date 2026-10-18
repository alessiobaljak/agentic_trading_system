"""Programma 5: il motore comune (REGOLE.md, sezioni 3-5).

* caricatori dei dati di ``research/data/p5`` (1 minuto, metrics, funding), con il **guardiano dei periodi**: i periodi V,
  R e A di un'idea si caricano solo se la sua regola congelata e i passi precedenti sono nel repository (committati);
* il simulatore di trade a eventi: ingresso all'apertura del minuto dopo la decisione, uscita a stop, target o tempo,
  costi per lato (commissione e scarto di prezzo, raddoppiato nelle esplosioni), funding a ogni regolamento attraversato;
* il caso: stessi trade spostati a un minuto qualunque della stessa moneta e dello stesso mese, con la stessa direzione;
* il bootstrap a blocchi di giorni di calendario e l'esame di un periodo.
"""
from __future__ import annotations

import io
import subprocess
import zipfile
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence

import numpy as np
import pandas as pd

from research.src.dati import funding_da_zip

RADICE = Path(__file__).resolve().parents[3]
DATI = RADICE / "research" / "data" / "p5"
IDEE = RADICE / "research" / "programma5" / "idee"

PERIODI = {
    "C": (date(2020, 1, 1), date(2022, 12, 31)),
    "V": (date(2023, 1, 1), date(2023, 12, 31)),
    "R": (date(2024, 1, 1), date(2026, 9, 30)),
    "A": (date(2026, 10, 1), date(2099, 12, 31)),
}
#: cosa deve essere nel repository prima di caricare un periodo (oltre a C)
PREREQUISITI = {"V": ("congelata.md",), "R": ("congelata.md", "V.md"), "A": ("congelata.md", "V.md", "R.md")}
SCARTO = {"BTCUSDT": 0.0001, "ETHUSDT": 0.0001, "SOLUSDT": 0.0001}
SCARTO_ALTRE = 0.0002
TAKER, MAKER = 0.0005, 0.0002
KLINE = ["open_time", "open", "high", "low", "close", "volume", "close_time", "quote_volume", "count",
         "taker_buy_volume", "taker_buy_quote_volume", "ignore"]
METRICS = ["create_time", "symbol", "sum_open_interest", "sum_open_interest_value",
           "count_toptrader_long_short_ratio", "sum_toptrader_long_short_ratio", "count_long_short_ratio",
           "sum_taker_long_short_vol_ratio"]


class PeriodoChiuso(RuntimeError):
    """Il periodo chiesto non si puo' ancora aprire per questa idea (REGOLE.md, sezione 4)."""


def _committato(percorso: Path) -> bool:
    if not percorso.exists():
        return False
    r = subprocess.run(["git", "log", "-1", "--format=%H", "--", str(percorso.relative_to(RADICE))],
                       cwd=RADICE, capture_output=True, text=True, timeout=30)
    stato = subprocess.run(["git", "status", "--porcelain", "--", str(percorso.relative_to(RADICE))],
                           cwd=RADICE, capture_output=True, text=True, timeout=30)
    return bool(r.stdout.strip()) and not stato.stdout.strip()


def controlla_periodo(periodo: str, idea: Optional[str]) -> None:
    """Il guardiano dei periodi: V, R e A solo con la regola congelata e i passi prima committati."""
    if periodo not in PERIODI:
        raise ValueError(f"periodo sconosciuto: {periodo}")
    if periodo == "C":
        return
    if not idea:
        raise PeriodoChiuso(f"il periodo {periodo} si apre solo per un'idea con la regola congelata")
    for nome in PREREQUISITI[periodo]:
        if not _committato(IDEE / idea / nome):
            raise PeriodoChiuso(f"{idea}: per aprire {periodo} serve {nome} committato e senza modifiche")


def _csv_da_zip(p: Path, nomi: Sequence[str]) -> pd.DataFrame:
    with zipfile.ZipFile(p) as z:
        grezzo = z.read(z.namelist()[0])
    intestazione = 0 if grezzo[:1].isalpha() else None
    df = pd.read_csv(io.BytesIO(grezzo), header=intestazione)
    if intestazione is None:
        df.columns = list(nomi)[:df.shape[1]]
    return df


def _ms(x: pd.Series) -> pd.Series:
    """Tempi in millisecondi (alcuni file recenti di Binance sono in microsecondi)."""
    x = pd.to_numeric(x)
    return x.where(x < 10 ** 14, x // 1000)


def _file(simbolo: str, tipo: str) -> List[Path]:
    cartella = DATI / simbolo / tipo
    return sorted(p for p in cartella.glob("*.zip") if p.with_suffix(".zip.ok").exists())


def _dentro(nome: str, inizio: date, fine: date) -> bool:
    """Il file (mensile o giornaliero) tocca il periodo?"""
    parti = nome.rsplit(".", 1)[0].split("-")
    try:
        if len(parti[-1]) == 2 and len(parti[-2]) == 4 and len(parti[-3]) == 4:   # ...-AAAA-MM-GG
            g = date(int(parti[-3]), int(parti[-2]), int(parti[-1]))
            return inizio <= g <= fine
        a, m = int(parti[-2]), int(parti[-1])
        primo = date(a, m, 1)
        ultimo = date(a + (m == 12), (m % 12) + 1, 1)
        return primo <= fine and ultimo > inizio
    except (ValueError, IndexError):
        return False


def _ms_giorno(g: date) -> int:
    return int(datetime(g.year, g.month, g.day, tzinfo=timezone.utc).timestamp() * 1000)


def minuti(simbolo: str, periodo: str, idea: Optional[str] = None, storia_giorni: int = 3) -> pd.DataFrame:
    """Candele da 1 minuto del periodo, piu' ``storia_giorni`` giorni prima (per le misure che guardano indietro:
    stanno sempre prima del periodo, quindi niente dati futuri). Indice = minuto dall'epoca, griglia senza buchi.
    La colonna ``periodo`` dice quali minuti sono del periodo (le decisioni si prendono solo li')."""
    controlla_periodo(periodo, idea)
    inizio, fine = PERIODI[periodo]
    da = date.fromordinal(inizio.toordinal() - storia_giorni)
    parti = [_csv_da_zip(p, KLINE) for p in _file(simbolo, "klines") if _dentro(p.name, da, fine)]
    if not parti:
        return pd.DataFrame()
    df = pd.concat(parti, ignore_index=True)
    df["open_time"] = _ms(df["open_time"])
    df = df[(df["open_time"] >= _ms_giorno(da)) & (df["open_time"] < _ms_giorno(fine) + 86_400_000)]
    df["minuto"] = df["open_time"] // 60_000
    df = df.drop_duplicates("minuto").set_index("minuto").sort_index()
    df = df[["open", "high", "low", "close", "volume", "quote_volume", "taker_buy_volume"]].astype(float)
    df = df.reindex(np.arange(df.index.min(), df.index.max() + 1))
    df["periodo"] = (df.index >= _ms_giorno(inizio) // 60_000)
    return df


def metrics(simbolo: str, periodo: str, idea: Optional[str] = None, storia_giorni: int = 3) -> pd.DataFrame:
    """Il file metrics ogni 5 minuti; indice = minuto in cui il valore e' noto (l'orario del file, preso come fine
    dei 5 minuti); righe doppie tolte, ordinate."""
    controlla_periodo(periodo, idea)
    inizio, fine = PERIODI[periodo]
    da = date.fromordinal(inizio.toordinal() - storia_giorni)
    parti = []
    for p in _file(simbolo, "metrics"):
        if _dentro(p.name, da, fine):
            try:
                parti.append(_csv_da_zip(p, METRICS))
            except (ValueError, zipfile.BadZipFile, pd.errors.EmptyDataError):
                continue
    if not parti:
        return pd.DataFrame()
    df = pd.concat(parti, ignore_index=True)
    t = pd.to_datetime(df["create_time"], utc=True, errors="coerce")
    df = df[t.notna()].copy()
    df["minuto"] = (t[t.notna()].astype("int64") // 60_000_000_000).astype(np.int64)
    df = df.drop_duplicates("minuto").set_index("minuto").sort_index()
    cols = [c for c in METRICS[2:] if c in df.columns]
    return df[cols].apply(pd.to_numeric, errors="coerce")


def funding(simbolo: str) -> pd.DataFrame:
    """Tutti i regolamenti del funding: minuto, intervallo in ore, tasso. Il tasso e' noto solo al regolamento."""
    righe = []
    for p in _file(simbolo, "funding"):
        righe += funding_da_zip(p)
    if not righe:
        return pd.DataFrame(columns=["ore", "tasso"])
    df = pd.DataFrame(righe, columns=["ts", "ore", "tasso"])
    df["minuto"] = df["ts"] // 60_000
    return df.drop_duplicates("minuto").set_index("minuto").sort_index()[["ore", "tasso"]]


# ---------------------------------------------------------------------------
# simulatore
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Uscita:
    """Come si esce: dopo ``minuti`` minuti, oppure prima a ``stop`` o ``target`` (frazioni del prezzo d'ingresso)."""

    minuti: int
    stop: Optional[float] = None
    target: Optional[float] = None


def scarto(simbolo: str) -> float:
    return SCARTO.get(simbolo, SCARTO_ALTRE)


def simula(df: pd.DataFrame, simbolo: str, decisioni: np.ndarray, direzioni: np.ndarray, uscita: Uscita,
           fund: Optional[pd.DataFrame] = None, esplosione: Optional[np.ndarray] = None,
           commissione: float = TAKER) -> pd.DataFrame:
    """Trade a eventi. ``decisioni``: posizioni (0..n-1) dei minuti alla cui chiusura si decide; ``direzioni``: +1
    long, -1 short. Ingresso all'apertura del minuto dopo; uscita alla chiusura del minuto ``uscita.minuti`` dopo
    l'ingresso, o prima allo stop o al target (se nella stessa candela, prima lo stop). Rendimento in frazione del
    valore della posizione, netto di commissioni, scarto di prezzo (doppio dove ``esplosione`` e' vero) e funding."""
    o, h, l, c = (df[k].to_numpy(float) for k in ("open", "high", "low", "close"))
    minuto = df.index.to_numpy()
    n = len(c)
    s = scarto(simbolo)
    f_min = fund.index.to_numpy() if fund is not None and len(fund) else np.array([], dtype=np.int64)
    f_tasso = fund["tasso"].to_numpy(float) if fund is not None and len(fund) else np.array([])
    righe = []
    for k, (t, d) in enumerate(zip(decisioni, direzioni)):
        e = int(t) + 1
        fine = e + uscita.minuti - 1
        if fine >= n or not np.isfinite(o[e]):
            continue
        p0 = o[e]
        prezzo, motivo, uscito = np.nan, "tempo", fine
        for j in range(e, fine + 1):
            if not (np.isfinite(h[j]) and np.isfinite(l[j])):
                continue
            if uscita.stop is not None:
                livello = p0 * (1 - d * uscita.stop)
                if (d > 0 and l[j] <= livello) or (d < 0 and h[j] >= livello):
                    prezzo, motivo, uscito = livello, "stop", j
                    break
            if uscita.target is not None:
                livello = p0 * (1 + d * uscita.target)
                if (d > 0 and h[j] >= livello) or (d < 0 and l[j] <= livello):
                    prezzo, motivo, uscito = livello, "target", j
                    break
        if motivo == "tempo":
            prezzo = c[fine]
            if not np.isfinite(prezzo):
                continue
        lordo = d * (prezzo / p0 - 1)
        sc = s * (2.0 if esplosione is not None and esplosione[k] else 1.0)
        costo = 2 * (commissione + sc)
        fund_costo = 0.0
        if len(f_min):
            a, b = np.searchsorted(f_min, minuto[e], "right"), np.searchsorted(f_min, minuto[uscito], "right")
            fund_costo = d * float(np.sum(f_tasso[a:b]))   # long paga il tasso positivo
        righe.append({"simbolo": simbolo, "decisione": int(t), "minuto": int(minuto[t]), "direzione": int(d),
                      "lordo": lordo, "costo": costo, "funding": fund_costo,
                      "netto": lordo - costo - fund_costo, "netto_doppio": lordo - 2 * costo - fund_costo,
                      "motivo": motivo})
    return pd.DataFrame(righe)


def caso(df: pd.DataFrame, simbolo: str, trade: pd.DataFrame, uscita: Uscita, fund=None, ripetizioni: int = 20,
         seme: int = 2026, commissione: float = TAKER) -> pd.DataFrame:
    """Gli stessi trade a minuti presi a caso della stessa moneta e dello stesso mese, con la stessa direzione."""
    if trade.empty:
        return trade
    rng = np.random.default_rng(seme)
    minuto = df.index.to_numpy()
    mese = pd.to_datetime(minuto * 60, unit="s").to_period("M").astype(str).to_numpy()
    validi = df["periodo"].to_numpy() & np.isfinite(df["open"].to_numpy(float))
    per_mese: Dict[str, np.ndarray] = {}
    for m in np.unique(mese[validi]):
        per_mese[m] = np.flatnonzero(validi & (mese == m))
    mese_trade = mese[trade["decisione"].to_numpy()]
    risultati = []
    for r in range(ripetizioni):
        dec = np.array([rng.choice(per_mese[m]) for m in mese_trade])
        sim = simula(df, simbolo, dec, trade["direzione"].to_numpy(), uscita, fund, commissione=commissione)
        sim["ripetizione"] = r
        risultati.append(sim)
    return pd.concat(risultati, ignore_index=True)


# ---------------------------------------------------------------------------
# statistica
# ---------------------------------------------------------------------------

def bootstrap_giorni(valori: np.ndarray, minuti_trade: np.ndarray, n: int = 2000, seme: int = 2026) -> dict:
    """Media, intervallo al 95% e p a una coda (media <= 0) con bootstrap a blocchi di giorni di calendario."""
    v = np.asarray(valori, float)
    ok = np.isfinite(v)
    v, g = v[ok], (np.asarray(minuti_trade)[ok] // 1440)
    if len(v) < 5:
        return {"n": int(len(v)), "media": float("nan"), "basso": float("nan"), "alto": float("nan"), "p": float("nan")}
    unici, inv = np.unique(g, return_inverse=True)
    somme, conti = np.bincount(inv, weights=v), np.bincount(inv)
    rng = np.random.default_rng(seme)
    medie = np.empty(n)
    for b in range(n):
        idx = rng.integers(0, len(unici), len(unici))
        medie[b] = somme[idx].sum() / conti[idx].sum()
    return {"n": int(len(v)), "giorni": int(len(unici)), "media": float(v.mean()),
            "basso": float(np.percentile(medie, 2.5)), "alto": float(np.percentile(medie, 97.5)),
            "p": float((np.sum(medie <= 0) + 1) / (n + 1))}


def esame(trade: pd.DataFrame, trade_caso: Optional[pd.DataFrame] = None, n_boot: int = 2000) -> dict:
    """I numeri di un periodo: netto, netto a costi doppi, per anno, per moneta, contro il caso."""
    if trade.empty:
        return {"trade": 0}
    m = trade["minuto"].to_numpy()
    out = {"trade": int(len(trade)),
           "netto": bootstrap_giorni(trade["netto"].to_numpy(), m, n_boot),
           "netto_doppio": bootstrap_giorni(trade["netto_doppio"].to_numpy(), m, n_boot),
           "lordo": float(trade["lordo"].mean()), "costo": float(trade["costo"].mean()),
           "funding": float(trade["funding"].mean())}
    anni = pd.to_datetime(m * 60, unit="s").year
    out["per_anno"] = {int(a): {"trade": int((anni == a).sum()), "netto": float(trade["netto"][anni == a].mean())}
                       for a in sorted(set(anni))}
    out["per_moneta"] = {s: {"trade": int(len(g)), "netto": float(g["netto"].mean())}
                         for s, g in trade.groupby("simbolo")}
    if trade_caso is not None and not trade_caso.empty:
        out["caso_netto"] = float(trade_caso["netto"].mean())
        out["contro_caso"] = float(trade["netto"].mean() - trade_caso["netto"].mean())
    return out
