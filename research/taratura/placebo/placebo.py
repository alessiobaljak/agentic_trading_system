"""La prova a placebo dell'esame della Fase 2 (regole in ``regole.md``, scritte prima dei numeri).

Domanda: sui prezzi VERI, l'esame con cui una campagna promuove un candidato
(«batte nettamente» la baseline (a) e la (b) con R medio dopo i costi positivo)
promuove strategie senza vantaggio piu' spesso di quanto dichiara la sezione 11
del protocollo? La taratura del 7 ott 2026 e' stata fatta su serie inventate;
qui si usano le candele vere, con la loro persistenza di regime.

Una strategia placebo e' una regola d'ingresso da manuale calcolata sui prezzi
veri, i cui ingressi sono poi SPOSTATI nel tempo di uno sfasamento circolare
casuale: i grappoli di segnali restano com'erano (stessa forma, stessa densita'),
ma non cadono piu' nei momenti in cui la regola li aveva messi. Per costruzione
non ha nessun vantaggio sul prezzo: il suo valore atteso e' quello di entrate
casuali con la stessa uscita. Se l'esame la promuove, la promuove per caso.

Il giudizio usa gli strumenti delle campagne, senza scorciatoie:
``motore.esegui``, ``motore.simula_baseline_casuale`` (200 simulazioni, semi
0..199), ``motore.barre_vietate_segnale_non_valido``, ``motore.durata_media_barre``,
``statistica.lunghezza_blocco``, ``statistica.baseline_da_trade`` e
``statistica.contro_baseline`` (2000 ricampionamenti, seme 0).

Funzioni pure tranne ``valuta_moneta`` (legge le candele dal disco). Gli
indicatori si calcolano una volta sull'intera serie del periodo, in modo
CAUSALE (il valore alla barra i usa solo le barre 0..i): la strategia li legge
all'indice della barra corrente, quindi non vede mai il futuro.
"""

from __future__ import annotations

import math
import zlib
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path
from typing import Dict, FrozenSet, List, Optional, Sequence, Tuple

import numpy as np

from research.src import dati, statistica
from research.src.motore import (
    Candela,
    Parametri,
    Segnale,
    barre_vietate_segnale_non_valido,
    durata_media_barre,
    esegui,
    simula_baseline_casuale,
)

#: barre iniziali di ogni periodo senza segnali: SMA50 e MACD (26 + 9) sono pronti dopo 50 barre
RISCALDAMENTO = 60
#: barre di costruzione messe davanti alla validazione per gli indicatori (senza segnali)
PREFISSO_VALIDAZIONE = 200
#: le sei regole d'ingresso da manuale e la loro uscita (regole.md, punto 3)
REGOLE = ("incrocio_medie", "rsi", "rottura_20", "bollinger", "macd", "momento_10")
USCITA_DELLA_REGOLA = {
    "incrocio_medie": "atr", "rottura_20": "atr", "macd": "atr",
    "rsi": "tempo", "bollinger": "tempo", "momento_10": "tempo",
}
DIREZIONI = ("long", "short")
TIMEFRAME = ("1h", "4h")
MS_BARRA = {"1h": 3_600_000, "4h": 14_400_000}
#: uscita a tempo: barre di permanenza (1 giorno a 1h, 2 giorni a 4h)
BARRE_USCITA_TEMPO = {"1h": 24, "4h": 12}
#: lo sfasamento lascia fuori solo 30 giorni attorno allo zero (revisione del 9 ott: con d fra L/4 e 3L/4
#: si toglievano proprio gli sfasamenti vicini ai periodi in cui la regola scatta, e la placebo ereditava
#: uno scarto di segno opposto al tempismo della regola)
SFASAMENTO_MINIMO = {"1h": 720, "4h": 180}
#: Fase 0 punto 3: un mese con volume medio giornaliero in USDT sotto questa soglia non apre posizioni
LIQUIDITA_MINIMA_USDT_GIORNO = 20_000_000
TRADE_MINIMI_COSTRUZIONE = 70
TRADE_MINIMI_VALIDAZIONE = 30
SIMULAZIONI = 200
RICAMPIONAMENTI = 2000


# ---------------------------------------------------------------------------
# Indicatori causali (numpy, una passata)
# ---------------------------------------------------------------------------


def _sma(x: np.ndarray, n: int) -> np.ndarray:
    out = np.full(x.size, np.nan)
    if x.size >= n:
        c = np.cumsum(np.insert(x, 0, 0.0))
        out[n - 1:] = (c[n:] - c[:-n]) / n
    return out


def _ema(x: np.ndarray, n: int) -> np.ndarray:
    out = np.full(x.size, np.nan)
    if x.size < n:
        return out
    a = 2.0 / (n + 1)
    out[n - 1] = x[:n].mean()
    for i in range(n, x.size):
        out[i] = a * x[i] + (1 - a) * out[i - 1]
    return out


def _rsi(close: np.ndarray, n: int = 14) -> np.ndarray:
    out = np.full(close.size, np.nan)
    if close.size <= n:
        return out
    d = np.diff(close)
    su, giu = np.clip(d, 0, None), np.clip(-d, 0, None)
    m_su, m_giu = su[:n].mean(), giu[:n].mean()
    for i in range(n, close.size):
        if i > n:
            m_su = (m_su * (n - 1) + su[i - 1]) / n
            m_giu = (m_giu * (n - 1) + giu[i - 1]) / n
        out[i] = 100.0 if m_giu == 0 else 100.0 - 100.0 / (1.0 + m_su / m_giu)
    return out


def atr_semplice(candele: Sequence[Candela], n: int = 14) -> np.ndarray:
    """ATR come media semplice degli ultimi ``n`` true range (il valore alla barra i usa le barre i-n..i)."""
    h = np.array([c.high for c in candele])
    l = np.array([c.low for c in candele])
    c = np.array([c.close for c in candele])
    tr = np.empty(h.size)
    tr[0] = h[0] - l[0]
    if h.size > 1:
        prec = c[:-1]
        tr[1:] = np.maximum(h[1:] - l[1:], np.maximum(np.abs(h[1:] - prec), np.abs(l[1:] - prec)))
    return _sma(tr, n)


def segnali_regola(candele: Sequence[Candela], regola: str, direzione: str) -> np.ndarray:
    """Maschera booleana delle barre in cui la regola da manuale scatta (alla chiusura della barra)."""
    close = np.array([c.close for c in candele])
    high = np.array([c.high for c in candele])
    low = np.array([c.low for c in candele])
    n = close.size
    s = np.zeros(n, dtype=bool)
    lungo = direzione == "long"
    with np.errstate(invalid="ignore"):
        if regola == "incrocio_medie":
            a, b = _sma(close, 20), _sma(close, 50)
            sopra = a > b
            s[1:] = (sopra[1:] & ~sopra[:-1]) if lungo else (~sopra[1:] & sopra[:-1])
            s &= ~np.isnan(b)
            s[1:] &= ~np.isnan(b[:-1])
        elif regola == "rsi":
            r = _rsi(close, 14)
            if lungo:
                s[1:] = (r[:-1] < 30) & (r[1:] >= 30)
            else:
                s[1:] = (r[:-1] > 70) & (r[1:] <= 70)
        elif regola == "rottura_20":
            for i in range(20, n):
                if lungo:
                    s[i] = close[i] > high[i - 20:i].max()
                else:
                    s[i] = close[i] < low[i - 20:i].min()
        elif regola == "bollinger":
            m = _sma(close, 20)
            sd = np.full(n, np.nan)
            for i in range(19, n):
                sd[i] = close[i - 19:i + 1].std()
            s = (close < m - 2 * sd) if lungo else (close > m + 2 * sd)
        elif regola == "macd":
            linea = _ema(close, 12) - _ema(close, 26)
            valida = ~np.isnan(linea)
            seg = np.full(n, np.nan)
            if valida.sum() >= 9:
                primo = int(np.argmax(valida))
                seg[primo:] = _ema(linea[primo:], 9)
            sopra = linea > seg
            pronto = ~np.isnan(seg)
            s[1:] = ((sopra[1:] & ~sopra[:-1]) if lungo else (~sopra[1:] & sopra[:-1])) & pronto[1:] & pronto[:-1]
        elif regola == "momento_10":
            roc = np.full(n, np.nan)
            roc[10:] = close[10:] / close[:-10] - 1.0
            pos = roc > 0
            neg = roc < 0
            pronto = ~np.isnan(roc)
            if lungo:
                s[1:] = pos[1:] & ~pos[:-1] & pronto[:-1]
            else:
                s[1:] = neg[1:] & ~neg[:-1] & pronto[:-1]
        else:
            raise ValueError(f"regola sconosciuta: {regola}")
    s = np.nan_to_num(s, nan=False).astype(bool)
    return s


# ---------------------------------------------------------------------------
# Lo sfasamento: stessi grappoli, momenti sbagliati
# ---------------------------------------------------------------------------


def seme_di(*parti: object) -> int:
    """Seme riproducibile da un'etichetta (crc32 del testo): niente dipende dall'ordine di esecuzione."""
    return zlib.crc32("|".join(str(p) for p in parti).encode())


def sposta(indici: Sequence[int], inizio: int, fine: int, seme: int, minimo: int) -> Tuple[FrozenSet[int], int]:
    """Sposta gli indici in [inizio, fine) di uno sfasamento circolare d uniforme in [m, L - m].

    L = fine - inizio; m = min(``minimo``, L // 4), almeno 1. Mediato su tutti gli sfasamenti, ogni barra
    e' coperta lo stesso numero di volte: la placebo e' in media un ingresso uniforme, come la (b).
    Si toglie solo un intorno dello zero (``minimo`` barre, 30 giorni), dove la placebo erediterebbe il
    tempismo della regola. Ritorna gli indici spostati e lo sfasamento; quelli fuori da [inizio, fine)
    si ignorano.
    """
    L = fine - inizio
    if L < 4:
        raise ValueError("periodo troppo corto per uno sfasamento")
    m = max(1, min(int(minimo), L // 4))
    rng = np.random.default_rng(seme)
    d = int(rng.integers(m, L - m + 1))
    dentro = [int(i) for i in indici if inizio <= int(i) < fine]
    return frozenset(inizio + ((i - inizio + d) % L) for i in dentro), d


# ---------------------------------------------------------------------------
# Strategie per il motore
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Uscita:
    tipo: str  # "atr": stop 1,5 ATR e target 2,5 ATR; "tempo": stop 2 ATR e chiusura dopo ``barre`` barre
    barre: int
    ms_barra: int


def calcolo_segnale(atr: np.ndarray, direzione: str, uscita: Uscita, primo_ammesso: int,
                    illiquida: Optional[np.ndarray] = None):
    """La funzione che, date le barre chiuse, calcola il segnale della variante SENZA condizione d'ingresso.

    Nessun segnale nel riscaldamento (barre prima di ``primo_ammesso``) e nelle barre dei mesi sotto la
    liquidita' minima (``illiquida``, Fase 0 punto 3): cosi' la placebo e la (a) non entrano li', e
    ``barre_vietate_segnale_non_valido`` le vieta da sola alla (b), come in campagna.
    """
    lato = 1.0 if direzione == "long" else -1.0

    def alla_barra(storia) -> Optional[Segnale]:
        i = len(storia) - 1
        if i < primo_ammesso or (illiquida is not None and illiquida[i]):
            return None
        a = atr[i]
        if not np.isfinite(a) or a <= 0:
            return None
        prezzo = storia[-1].close
        if uscita.tipo == "atr":
            return Segnale(direzione, prezzo - lato * 1.5 * a, prezzo + lato * 2.5 * a)
        return Segnale(direzione, prezzo - lato * 2.0 * a, None)

    return alla_barra


def fabbrica(ingressi: Optional[FrozenSet[int]], segnale_alla_barra, uscita: Uscita, indice_di: Dict[int, int]):
    """La funzione che crea la strategia: entra alle barre di ``ingressi`` (None = a ogni barra libera).

    ``indice_di`` porta dal ``ts`` di apertura all'indice della barra: l'uscita a tempo conta le BARRE
    tenute (dalla barra d'ingresso a quella corrente, comprese), non le ore, cosi' un buco nei dati non la
    allunga ne' la accorcia.
    """

    def crea():
        def strategia(storia, posizione):
            if posizione is not None:
                if uscita.tipo == "tempo":
                    tenute = (len(storia) - 1) - indice_di[posizione.ts_entrata] + 1
                    if tenute >= uscita.barre:
                        return "chiudi"
                return None
            if ingressi is None or (len(storia) - 1) in ingressi:
                return segnale_alla_barra(storia)
            return None
        return strategia

    return crea


def fabbrica_casuale(segnale_alla_barra, uscita: Uscita, indice_di: Dict[int, int]):
    """``crea_casuale(ingressi)`` per ``simula_baseline_casuale``: stesso segnale, stessa uscita."""

    def crea_casuale(ingressi: FrozenSet[int]):
        return fabbrica(ingressi, segnale_alla_barra, uscita, indice_di)()

    return crea_casuale


# ---------------------------------------------------------------------------
# Il giudizio di un periodo
# ---------------------------------------------------------------------------


def parametri_moneta(slippage: float) -> Parametri:
    """I parametri delle campagne (parametri.yaml), con la fascia di slippage della moneta."""
    return Parametri(
        commissione_per_lato=0.0005,
        slippage_per_lato=float(slippage),
        rischio_per_trade=0.01,
        leva_max=2.0,
        modalita_margine="isolated",
        tasso_margine_mantenimento=0.025,
        margine_minimo_da_liquidazione=0.8,
        capitale_iniziale=1000.0,
        riempimento_intrabarra="stop_prima",
        moltiplicatore_costi=1.0,
        ritardo_barre=0,
    )


def _unisci_vietate(*liste: Sequence[Tuple[int, int]]) -> List[Tuple[int, int]]:
    tutte = sorted(v for lista in liste for v in lista if v[1] > v[0])
    unite: List[Tuple[int, int]] = []
    for a, b in tutte:
        if unite and a <= unite[-1][1]:
            unite[-1] = (unite[-1][0], max(unite[-1][1], b))
        else:
            unite.append((a, b))
    return unite


def giudica(candele: List[Candela], ingressi: FrozenSet[int], atr: np.ndarray, direzione: str, uscita: Uscita,
            primo_ammesso: int, parametri: Parametri, minimo_trade: int, con_baseline_a: bool,
            illiquida: Optional[np.ndarray] = None) -> Dict[str, object]:
    """Esegue la placebo e, se ha abbastanza trade, la giudica come una campagna (sezione 8).

    Un errore dentro una sola placebo non ferma le altre: finisce nella sua riga (``errore``).
    """
    try:
        return _giudica(candele, ingressi, atr, direzione, uscita, primo_ammesso, parametri, minimo_trade,
                        con_baseline_a, illiquida)
    except Exception as e:  # noqa: BLE001 - si registra e si conta, non si perde
        return {"giudicata": False, "errore": f"{type(e).__name__}: {str(e)[:300]}"}


def _giudica(candele, ingressi, atr, direzione, uscita, primo_ammesso, parametri, minimo_trade, con_baseline_a,
             illiquida) -> Dict[str, object]:
    indice_di = {c.ts: k for k, c in enumerate(candele)}
    segnale = calcolo_segnale(atr, direzione, uscita, primo_ammesso, illiquida)
    ris = esegui(candele, None, None, [], fabbrica(ingressi, segnale, uscita, indice_di)(), parametri)
    trades = ris.trades
    esito: Dict[str, object] = {"n_trade": len(trades), "n_ingressi": len(ingressi),
                                "segnali_non_validi": ris.n_segnali_non_validi, "n_buchi_dati": ris.n_buchi_dati,
                                "violazioni_liquidazione": sum(1 for t in trades if t.violazione_liquidazione)}
    if len(trades) < minimo_trade:
        esito["giudicata"] = False
        return esito
    r = [t.r for t in trades]  # il motore chiude una posizione alla volta: gia' in ordine di uscita
    blocco = statistica.lunghezza_blocco([t.ts_entrata for t in trades], [t.ts_uscita for t in trades])
    vietate = _unisci_vietate([(0, primo_ammesso)],
                              barre_vietate_segnale_non_valido(candele, lambda: segnale, parametri))
    durata = durata_media_barre(trades, uscita.ms_barra)
    esito.update({"giudicata": True, "r_medio": float(np.mean(r)), "blocco": int(blocco),
                  "n_blocchi": int(len(r) // blocco), "durata_media": int(durata),
                  "quota_barre_vietate": round(sum(b - a for a, b in vietate) / len(candele), 4)})
    try:
        base_b = simula_baseline_casuale(candele, fabbrica_casuale(segnale, uscita, indice_di), len(trades), durata,
                                         parametri, barre_vietate=vietate, n_simulazioni=SIMULAZIONI, primo_seme=0)
    except ValueError as e:  # la (b) non si costruisce: la variante e' non valutabile (sezione 8)
        esito.update({"valutabile_b": False, "motivo_non_valutabile": str(e)[:200]})
        return esito
    cb = statistica.contro_baseline(r, blocco, base_b, n=RICAMPIONAMENTI, seme=0)
    esito.update({
        "valutabile_b": bool(cb.get("valutabile", True)),
        "b_media": float(base_b["media"]),
        "netta_b": bool(cb["netta"]),
        "t_b": float(cb["t"]) if math.isfinite(cb["t"]) else None,
        "p_b": float(cb["p_value"]),
        "percentile_b": float(statistica.percentile_del_candidato(float(np.mean(r)), base_b["valori"])),
    })
    if not esito["valutabile_b"]:
        esito["motivo_non_valutabile"] = "meno di 3 blocchi interi o errore infinito"
    if con_baseline_a:
        ris_a = esegui(candele, None, None, [], fabbrica(None, segnale, uscita, indice_di)(), parametri)
        ta = ris_a.trades
        if len(ta) >= 2:
            blocco_a = statistica.lunghezza_blocco([t.ts_entrata for t in ta], [t.ts_uscita for t in ta])
            base_a = statistica.baseline_da_trade([t.r for t in ta], blocco_a, n=RICAMPIONAMENTI, seme=0)
            ca = statistica.contro_baseline(r, blocco, base_a, n=RICAMPIONAMENTI, seme=0)
            esito.update({"a_media": float(base_a["media"]), "netta_a": bool(ca["netta"]),
                          "valutabile_a": bool(base_a["valutabile"])})
        else:
            esito.update({"netta_a": False, "valutabile_a": False})
        esito["candidato"] = bool(esito["netta_a"] and esito["netta_b"] and esito["r_medio"] > 0
                                  and esito["violazioni_liquidazione"] == 0)
    return esito


# ---------------------------------------------------------------------------
# Una moneta, un timeframe: tutte le placebo
# ---------------------------------------------------------------------------


def _mesi_attesi(primo_mese: date) -> List[Tuple[int, int]]:
    return list(dati.mesi_del_periodo(primo_mese, dati.FINE_IN_SAMPLE))


def mesi_illiquidi(simbolo: str, primo_mese: date, radice: Path) -> Dict[str, float]:
    """Volume medio giornaliero in USDT per mese («AAAA-MM» -> media), dai quote_volume a 1 ora.

    Fase 0 punto 3: un mese e' sotto la soglia se la media giornaliera del volume in USDT e' sotto
    ``LIQUIDITA_MINIMA_USDT_GIORNO``. I giorni sono UTC; la media e' sui giorni con dati.
    """
    per_giorno: Dict[str, float] = {}
    for percorso in dati._percorsi_presenti(simbolo, "klines", "1h", primo_mese, dati.FINE_IN_SAMPLE, radice):
        for ts, v in dati.volume_usdt_da_zip(percorso).items():
            giorno = (date(1970, 1, 1) + timedelta(milliseconds=int(ts))).isoformat()
            per_giorno[giorno] = per_giorno.get(giorno, 0.0) + float(v)
    per_mese: Dict[str, List[float]] = {}
    for giorno, v in per_giorno.items():
        per_mese.setdefault(giorno[:7], []).append(v)
    return {m: float(np.mean(vs)) for m, vs in per_mese.items()}


def _maschera_illiquida(candele: Sequence[Candela], media_mese: Dict[str, float]) -> np.ndarray:
    out = np.zeros(len(candele), dtype=bool)
    for k, c in enumerate(candele):
        mese = (date(1970, 1, 1) + timedelta(milliseconds=int(c.ts))).isoformat()[:7]
        out[k] = media_mese.get(mese, 0.0) < LIQUIDITA_MINIMA_USDT_GIORNO
    return out


def carica_periodi(simbolo: str, primo_mese: date, timeframe: str, radice: Path) -> Dict[str, object]:
    """Candele di costruzione e di validazione (con il prefisso per gli indicatori), mai oltre il 2023-12-31.

    Solleva ValueError se mancano file mensili fra il primo mese e il 2023-12 o se la serie e' vuota:
    una moneta non si perde in silenzio.
    """
    per = dati.periodi_campagna(primo_mese)
    attesi = _mesi_attesi(per["inizio"])
    presenti = dati._percorsi_presenti(simbolo, "klines", "1h", per["inizio"], per["fine_validazione"], radice)
    if len(presenti) != len(attesi):
        raise ValueError(f"{simbolo}: {len(presenti)} file mensili su {len(attesi)} attesi")
    ore = dati.carica_candele(simbolo, "1h", per["inizio"], per["fine_validazione"], radice=radice)
    if not ore:
        raise ValueError(f"{simbolo}: nessuna candela a 1 ora su disco")
    serie = ore if timeframe == "1h" else dati.aggrega_candele(ore, timeframe)
    costr = [c for c in serie if c.close_ts <= per["fine_costruzione_ts"]]
    valid = [c for c in serie if c.ts >= per["inizio_validazione_ts"]]
    prefisso = costr[-PREFISSO_VALIDAZIONE:]
    return {"periodi": per, "costruzione": costr, "validazione": prefisso + valid, "inizio_valid": len(prefisso)}


def valuta_moneta(simbolo: str, primo_mese: date, slippage: float, timeframe: str, radice: Path,
                  sfasamento_k: int = 0) -> List[Dict[str, object]]:
    """Tutte le placebo di una moneta a un timeframe: 6 regole x 2 direzioni, costruzione e validazione."""
    p = carica_periodi(simbolo, primo_mese, timeframe, radice)
    media_mese = mesi_illiquidi(simbolo, p["periodi"]["inizio"], radice)
    parametri = parametri_moneta(slippage)
    esiti: List[Dict[str, object]] = []
    for nome_periodo, candele, primo in (("costruzione", p["costruzione"], RISCALDAMENTO),
                                         ("validazione", p["validazione"], p["inizio_valid"])):
        base = {"simbolo": simbolo, "timeframe": timeframe, "periodo": nome_periodo, "sfasamento_k": sfasamento_k,
                "barre": len(candele), "prima_barra": candele[0].ts if candele else None,
                "ultima_barra": candele[-1].ts if candele else None}
        if len(candele) - primo < 100:
            esiti.append({**base, "regola": None, "direzione": None, "giudicata": False,
                          "errore": "periodo con meno di 100 barre utilizzabili"})
            continue
        atr = atr_semplice(candele)
        illiquida = _maschera_illiquida(candele, media_mese)
        for regola in REGOLE:
            uscita = Uscita(USCITA_DELLA_REGOLA[regola], BARRE_USCITA_TEMPO[timeframe], MS_BARRA[timeframe])
            for direzione in DIREZIONI:
                maschera = segnali_regola(candele, regola, direzione)
                originali = np.flatnonzero(maschera)
                seme = seme_di(simbolo, timeframe, regola, direzione, nome_periodo, sfasamento_k)
                ingressi, d = sposta(originali, primo, len(candele) - 1, seme, SFASAMENTO_MINIMO[timeframe])
                minimo = TRADE_MINIMI_COSTRUZIONE if nome_periodo == "costruzione" else TRADE_MINIMI_VALIDAZIONE
                esito = giudica(candele, ingressi, atr, direzione, uscita, primo, parametri, minimo,
                                con_baseline_a=(nome_periodo == "costruzione"), illiquida=illiquida)
                esito.update({**base, "regola": regola, "direzione": direzione, "uscita": uscita.tipo,
                              "sfasamento": d, "segnali_originali": int(originali.size),
                              "quota_barre_illiquide": round(float(illiquida[primo:].mean()), 4)})
                esiti.append(esito)
    return esiti
