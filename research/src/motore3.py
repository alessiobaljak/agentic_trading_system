"""Il motore di backtest del protocollo 3 (``research/PROTOCOLLO_3.md``, sezioni 6, 7.6-7.8 e 9).

Legge gli array di una variante compilata (``research/src/catalogo3.py``) e simula i trade
candela per candela, nell'ordine della sezione 9.2:

1. posizione aperta: salto oltre lo stop all'apertura, stop, target (stop prima del
   target se cadono nella stessa candela);
2. ordine limit in attesa: esecuzione al prezzo limit se il prezzo lo SUPERA; nella
   candela di esecuzione conta solo lo stop;
3. funding dei regolamenti della candela (9.5);
4. alla chiusura: trailing, uscita a tempo, segnale opposto (uscita all'apertura dopo);
5. alla chiusura, nuovo ingresso solo senza posizione, senza ordine in attesa e senza
   uscita programmata.

Una differenza voluta rispetto al motore del primo protocollo (``motore.py``, che resta
com'e' per le campagne passate): qui ogni trade si simula da solo, dal segnale
all'uscita (``simula_da``). Con capitale fisso e niente interesse composto (9.4) il
risultato di un trade dipende solo dalla candela del segnale; cosi' lo stesso codice
serve al candidato e alle entrate casuali (10.1), che sono trade aperti in candele
scelte a caso.

Il modulo e' puro: niente file, niente rete.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field, replace
from typing import Dict, List, Optional, Tuple

import numpy as np

from research.src.catalogo3 import Compilata, GIORNO_MS, MINUTO_MS

# ---------------------------------------------------------------------------
# costi (sezione 6) e regole (sezione 9.4)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Costi:
    """Commissioni e slippage per lato (sezione 6). Il funding e' sempre quello vero."""

    taker: float = 0.0005
    maker: float = 0.0002
    slippage: float = 0.0001


COSTI_NORMALI = Costi()
#: costi doppi (sezione 6): taker 0,10%, maker 0,04%, slippage 0,02%; funding invariato
COSTI_DOPPI = Costi(taker=0.0010, maker=0.0004, slippage=0.0002)


@dataclass(frozen=True)
class Regole:
    """Dimensione, leva, liquidazione e varianti del motore per le verifiche della Fase 4.

    * ``capitale`` e ``rischio``: rischio per trade sul capitale INIZIALE, senza interesse
      composto (9.4);
    * ``leva_max``: la leva del bot (fatto ``regole_dimensione_bot``); oltre, la
      dimensione si riduce e il trade si conta come ridotto;
    * ``mmr`` e ``importo_mantenimento``: margine di mantenimento di Binance per BTCUSDT;
    * ``serie_stop``: "last", "mark" oppure "last_e_mark" (lo stop scatta se lo tocca
      una delle due: e' quello che fa il bot in paper, fatto ``serie_stop``);
    * ``intrabarra``: "stop_prima" (regola) o "target_prima" (Fase 4, verifica 9);
    * ``ritardo``: candele di ritardo dell'ingresso (9.9);
    * ``scarto_riempimento``: di quanto il prezzo deve superare il limit (0,0005 per la
      verifica 8 della Fase 4).
    """

    capitale: float = 10_000.0
    rischio: float = 0.01
    leva_max: float = 2.0
    mmr: float = 0.004
    importo_mantenimento: float = 0.0
    fattore_liquidazione: float = 0.8
    stop_minimo: float = 0.003
    serie_stop: str = "last_e_mark"
    intrabarra: str = "stop_prima"
    ritardo: int = 0
    scarto_riempimento: float = 0.0

    def __post_init__(self) -> None:
        if self.serie_stop not in ("last", "mark", "last_e_mark"):
            raise ValueError(f"serie_stop sconosciuta: {self.serie_stop!r}")
        if self.intrabarra not in ("stop_prima", "target_prima"):
            raise ValueError(f"intrabarra sconosciuta: {self.intrabarra!r}")
        if self.ritardo not in (0, 1):
            raise ValueError("ritardo: 0 oppure 1 candela (9.9)")


# ---------------------------------------------------------------------------
# il trade e l'esito di una decisione
# ---------------------------------------------------------------------------


@dataclass
class Trade:
    tipo_ingresso: str  # "M" o "L"
    indice_segnale: int
    indice_ingresso: int
    ts_ingresso: int  # apertura della candela di ingresso (o di esecuzione del limit)
    prezzo_ingresso: float
    stop_iniziale: float
    target: Optional[float]
    indice_uscita: int
    ts_uscita: int  # istante dell'uscita: apertura della candela, oppure sua apertura per le uscite dentro la candela
    prezzo_uscita: float
    motivo: str
    quantita: float
    rischio_usdt: float
    commissioni: float
    funding: float
    pnl: float
    r: float
    ridotto: bool
    violazione_liquidazione: bool
    candele_in_posizione: int

    @property
    def long(self) -> bool:
        return self.prezzo_ingresso > self.stop_iniziale


@dataclass
class Esito:
    """Cosa succede dopo una decisione alla chiusura della candela ``indice``.

    ``tipo``: "trade", "stop_troppo_vicino" (a mercato, all'ingresso), "ordine_non_inserito"
    (limit con stop non valido), "limite_non_eseguito", "senza_candela" (finiti i dati o
    buco subito dopo il segnale). ``libero_da``: la prima candela alla cui chiusura la
    variante puo' decidere di nuovo.
    """

    tipo: str
    indice: int
    libero_da: int
    trade: Optional[Trade] = None


# ---------------------------------------------------------------------------
# liquidazione (9.4)
# ---------------------------------------------------------------------------


def prezzo_liquidazione(long: bool, prezzo: float, quantita: float, leva: float, mmr: float,
                        importo_mantenimento: float = 0.0) -> float:
    """Prezzo di liquidazione di Binance in margine isolato (una posizione, modalita' a
    senso unico): (margine + importo di mantenimento - lato x Q x prezzo) / (Q x mmr -
    lato x Q), con margine = Q x prezzo / leva. Per un long con importo zero vale
    prezzo x (1 - 1/leva) / (1 - mmr)."""
    lato = 1.0 if long else -1.0
    margine = quantita * prezzo / leva
    num = margine + importo_mantenimento - lato * quantita * prezzo
    den = quantita * mmr - lato * quantita
    return num / den


# ---------------------------------------------------------------------------
# funding (9.5)
# ---------------------------------------------------------------------------


def _mark_a(serie, t_ms: int) -> float:
    """Il mark price all'istante di un regolamento: l'apertura della candela mark che
    contiene T. SCELTA: su 12h e 1d, dove T puo' cadere dentro la candela, si usa la sua
    apertura; se T cade in un buco, la chiusura dell'ultima candela prima."""
    ts = serie.ts
    j = int(np.searchsorted(ts, t_ms, side="right")) - 1
    if j < 0:
        return float(serie.mark_open[0])
    if ts[j] + serie.durata > t_ms:
        return float(serie.mark_open[j])
    return float(serie.mark_close[j])


def funding_del_trade(serie, long: bool, quantita: float, ts_in: int, modo_in: str,
                      ts_out: int, modo_out: str) -> float:
    """Somma del funding del trade (positivo = incassato), con le regole della 9.5.

    ``modo_in``: "apertura" (ingresso all'apertura della candela che inizia a ``ts_in``)
    o "dentro" (ordine limit eseguito dentro quella candela). ``modo_out``: "apertura"
    (uscita all'apertura della candela che inizia a ``ts_out``), "dentro" (stop, target o
    liquidazione dentro quella candela) o "chiusura" (fine dei dati: alla chiusura).

    Un regolamento si conta pieno se la posizione era aperta prima e dopo T; si conta solo
    se e' un costo quando l'ordine fra T e l'ingresso o l'uscita non si conosce (T dentro
    la candela di un'esecuzione limit o di un'uscita per stop o target).
    """
    d = serie.durata
    f_ts = serie.funding_ts
    if len(f_ts) == 0 or quantita <= 0:
        return 0.0
    lo = int(np.searchsorted(f_ts, ts_in, side="right"))  # T > ts_in
    if modo_out == "apertura":
        hi = int(np.searchsorted(f_ts, ts_out, side="right"))  # T <= ts_out
    else:
        hi = int(np.searchsorted(f_ts, ts_out + d - 1, side="right"))  # T dentro la candela d'uscita
    totale = 0.0
    for j in range(lo, hi):
        t = int(f_ts[j])
        tasso = float(serie.funding_tasso[j])
        dubbio = False
        if modo_in == "dentro" and t < ts_in + d:
            dubbio = True
        if modo_out == "dentro" and t > ts_out:
            dubbio = True
        importo = quantita * _mark_a(serie, t) * tasso * (-1.0 if long else 1.0)
        if dubbio and importo >= 0:
            continue
        totale += importo
    return totale


# ---------------------------------------------------------------------------
# un trade, dal segnale all'uscita
# ---------------------------------------------------------------------------


def _livello_stop(c: Compilata, i: int, ingresso: float) -> float:
    st = c.variante["stop"]
    long = c.long
    if st["codice"] == "S1":
        a = float(c.atr_stop[i])
        return ingresso - a * st["k"] if long else ingresso + a * st["k"]
    if st["codice"] == "S2":
        return float(c.estremo_s2[i])
    p = st["pct"]
    return ingresso * (1 - p) if long else ingresso * (1 + p)


def _target(c: Compilata, ingresso: float, distanza: float) -> Optional[float]:
    for u in c.variante["uscite"]:
        if u["codice"] == "U1":
            return ingresso + u["k"] * distanza if c.long else ingresso - u["k"] * distanza
    return None


def _uscita(c: Compilata, codice: str) -> Optional[dict]:
    for u in c.variante["uscite"]:
        if u["codice"] == codice:
            return u
    return None


def simula_da(c: Compilata, i: int, regole: Regole, costi: Costi, fine: int,
              forzato: bool = False) -> Esito:
    """Simula la decisione presa alla chiusura della candela ``i`` (segnale vero, oppure
    ``forzato`` per le entrate casuali) fino all'uscita. ``fine`` e' l'ultima candela che
    la simulazione puo' leggere (compresa)."""
    s = c.serie
    v = c.variante
    long = c.long
    sg = 1.0 if long else -1.0
    d = s.durata
    tipo = v["tipo_ingresso"]["codice"]
    rit = regole.ritardo
    slip = costi.slippage

    # ---- ingresso ---------------------------------------------------------
    if tipo == "M":
        e0 = i + 1 + rit
        if e0 > fine or s.ts[e0] != s.ts[i] + (1 + rit) * d:
            # finiti i dati, o manca la candela dopo il segnale: niente trade (SCELTA)
            return Esito("senza_candela", i, min(i + 1, fine + 1))
        ingresso = float(s.open[e0]) * (1 + sg * slip)
        stop = _livello_stop(c, i, ingresso)
        distanza = sg * (ingresso - stop)
        if not (math.isfinite(distanza) and distanza >= regole.stop_minimo * ingresso):
            return Esito("stop_troppo_vicino", i, e0)
        indice_in = e0
        modo_in = "apertura"
        comm_in_tasso = costi.taker
    else:
        lim = v["tipo_ingresso"]
        a = float(c.atr_limite[i])
        prezzo_lim = float(s.close[i]) - sg * lim["k"] * a
        stop = _livello_stop(c, i, prezzo_lim)
        distanza = sg * (prezzo_lim - stop)
        if not (math.isfinite(distanza) and distanza >= regole.stop_minimo * prezzo_lim):
            return Esito("ordine_non_inserito", i, i + 1)
        inizio_ts = int(s.ts[i]) + (1 + rit) * d
        fine_ts = inizio_ts + lim["validita"] * d
        soglia = prezzo_lim * (1 - sg * regole.scarto_riempimento)
        eseguito = None
        ultimo_attivo = i
        j = i + 1
        while j <= fine and s.ts[j] < fine_ts:
            if s.ts[j] >= inizio_ts:
                ultimo_attivo = j
                if (long and s.low[j] < soglia) or (not long and s.high[j] > soglia):
                    eseguito = j
                    break
            j += 1
        if eseguito is None:
            # cancellato alla fine della validita': la variante decide di nuovo alla chiusura
            # dell'ultima candela in cui l'ordine era attivo (9.2, punti 2 e 5)
            return Esito("limite_non_eseguito", i, max(ultimo_attivo, i + 1))
        ingresso = prezzo_lim
        indice_in = eseguito
        modo_in = "dentro"
        comm_in_tasso = costi.maker

    # ---- dimensione, leva, liquidazione (9.4) -----------------------------
    rischio_voluto = regole.capitale * regole.rischio
    quantita = rischio_voluto / distanza
    ridotto = False
    if quantita * ingresso > regole.capitale * regole.leva_max:
        quantita = regole.capitale * regole.leva_max / ingresso
        ridotto = True
    rischio_usdt = quantita * distanza
    liq = prezzo_liquidazione(long, ingresso, quantita, regole.leva_max, regole.mmr,
                              regole.importo_mantenimento)
    distanza_liq = abs(ingresso - liq)
    violazione = distanza > regole.fattore_liquidazione * distanza_liq
    margine = quantita * ingresso / regole.leva_max
    commissioni = quantita * ingresso * comm_in_tasso

    target = _target(c, ingresso, distanza)
    u2 = _uscita(c, "U2")
    u2s = _uscita(c, "U2s")
    u3 = _uscita(c, "U3")
    u4 = _uscita(c, "U4") is not None
    stop_corrente = stop
    estremo = -math.inf if long else math.inf  # massimo (long) o minimo (short) dall'ingresso

    def _basso(t: int) -> float:
        if regole.serie_stop == "last":
            return float(s.low[t])
        if regole.serie_stop == "mark":
            return float(s.mark_low[t])
        return min(float(s.low[t]), float(s.mark_low[t]))

    def _alto(t: int) -> float:
        if regole.serie_stop == "last":
            return float(s.high[t])
        if regole.serie_stop == "mark":
            return float(s.mark_high[t])
        return max(float(s.high[t]), float(s.mark_high[t]))

    def _chiudi(t: int, prezzo_uscita: float, motivo: str, ts_out: int, modo_out: str,
                candele: int, libero: int, liquidato: bool = False) -> Esito:
        comm = commissioni
        fund = funding_del_trade(s, long, quantita, int(s.ts[indice_in]), modo_in, ts_out, modo_out)
        if liquidato:
            pnl = -margine - commissioni + fund
        else:
            comm += quantita * prezzo_uscita * costi.taker
            pnl = sg * quantita * (prezzo_uscita - ingresso) - comm + fund
        tr = Trade(tipo, i, indice_in, int(s.ts[indice_in]), ingresso, stop, target, t, ts_out,
                   prezzo_uscita, motivo, quantita, rischio_usdt, comm, fund, pnl, pnl / rischio_usdt,
                   ridotto, violazione, candele)
        return Esito("trade", i, libero, tr)

    t = indice_in
    candele_chiuse = 0
    while True:
        # ---- 1. uscite dentro la candela t ---------------------------------
        prima = t == indice_in
        # liquidazione sul mark (prudente: prima dello stop)
        if (long and s.mark_low[t] <= liq) or (not long and s.mark_high[t] >= liq):
            return _chiudi(t, liq, "liquidazione", int(s.ts[t]), "dentro", candele_chiuse + 1, t, True)
        if not prima:
            apertura = float(s.open[t])
            if (long and apertura <= stop_corrente) or (not long and apertura >= stop_corrente):
                motivo = "trailing_salto" if stop_corrente != stop else "stop_salto"
                return _chiudi(t, apertura * (1 - sg * slip), motivo, int(s.ts[t]), "apertura",
                               candele_chiuse, t)
        tocca_stop = (_basso(t) <= stop_corrente) if long else (_alto(t) >= stop_corrente)
        tocca_target = False
        if target is not None and not (prima and tipo == "L"):
            tocca_target = (s.high[t] >= target) if long else (s.low[t] <= target)
        if tocca_stop and (not tocca_target or regole.intrabarra == "stop_prima"):
            motivo = "trailing" if stop_corrente != stop else "stop"
            return _chiudi(t, stop_corrente * (1 - sg * slip), motivo, int(s.ts[t]), "dentro",
                           candele_chiuse + 1, t)
        if tocca_target:
            return _chiudi(t, target * (1 - sg * slip), "target", int(s.ts[t]), "dentro",
                           candele_chiuse + 1, t)
        # ---- 4. alla chiusura della candela t ------------------------------
        candele_chiuse += 1
        if u3 is not None:
            estremo = max(estremo, float(s.high[t])) if long else min(estremo, float(s.low[t]))
            a = float(c.atr_trailing[t])
            if math.isfinite(a):
                nuovo = estremo - u3["k"] * a if long else estremo + u3["k"] * a
                stop_corrente = max(stop_corrente, nuovo) if long else min(stop_corrente, nuovo)
        esce = None
        if u2 is not None and candele_chiuse >= u2["n"]:
            esce = "tempo"
        if esce is None and u2s is not None:
            prossima = int(s.ts[t]) + d
            if (prossima % GIORNO_MS) // MINUTO_MS >= 21 * 60:
                esce = "fine_giornata"
        if esce is None and u4 and c.opposto[t]:
            esce = "segnale_opposto"
        if t >= fine:
            # finiti i dati con la posizione aperta: chiusura alla chiusura dell'ultima candela
            return _chiudi(t, float(s.close[t]) * (1 - sg * slip), "fine_dati", int(s.ts[t]), "chiusura",
                           candele_chiuse, fine + 1)
        if esce is not None:
            x = t + 1
            return _chiudi(x, float(s.open[x]) * (1 - sg * slip), esce, int(s.ts[x]), "apertura",
                           candele_chiuse, x)
        t += 1


# ---------------------------------------------------------------------------
# la variante su un periodo
# ---------------------------------------------------------------------------


@dataclass
class Risultato:
    trade: List[Trade]
    inizio: int
    fine: int
    contatori: Dict[str, int] = field(default_factory=dict)


def esegui(c: Compilata, regole: Regole = Regole(), costi: Costi = COSTI_NORMALI,
           inizio: int = 0, fine: Optional[int] = None) -> Risultato:
    """Esegue la variante: decisioni alle chiusure delle candele da ``inizio`` a ``fine``
    (indici), una posizione alla volta (7.8). La simulazione legge al massimo fino a
    ``fine``."""
    n = len(c.serie)
    if fine is None:
        fine = n - 1
    trade: List[Trade] = []
    cont = {"segnali": 0, "ordini_inseriti": 0, "ordini_eseguiti": 0, "ordini_cancellati": 0,
            "ordini_non_inseriti": 0, "stop_troppo_vicini": 0, "senza_candela": 0}
    tipo = c.variante["tipo_ingresso"]["codice"]
    i = inizio
    while i <= fine:
        if not c.segnale[i]:
            i += 1
            continue
        cont["segnali"] += 1
        es = simula_da(c, i, regole, costi, fine)
        if es.tipo == "trade":
            trade.append(es.trade)
            if tipo == "L":
                cont["ordini_inseriti"] += 1
                cont["ordini_eseguiti"] += 1
        elif es.tipo == "limite_non_eseguito":
            cont["ordini_inseriti"] += 1
            cont["ordini_cancellati"] += 1
        elif es.tipo == "ordine_non_inserito":
            cont["ordini_non_inseriti"] += 1
        elif es.tipo == "stop_troppo_vicino":
            cont["stop_troppo_vicini"] += 1
        else:
            cont["senza_candela"] += 1
        i = max(es.libero_da, i + 1)
    return Risultato(trade, inizio, fine, cont)


def stima_trade(c: Compilata, regole: Regole = Regole(), inizio: int = 0,
                fine: Optional[int] = None) -> Dict[str, int]:
    """Stima dei trade (8.4): ingressi e uscite simulati, SOLO il conteggio. Per gli
    ingressi limit contano solo gli ordini eseguiti. Nessun risultato in R esce da qui."""
    r = esegui(c, regole, COSTI_NORMALI, inizio, fine)
    lunghi = sum(1 for t in r.trade if t.long)
    return {"trade": len(r.trade), "long": lunghi, "short": len(r.trade) - lunghi,
            "ordini_inseriti": r.contatori["ordini_inseriti"],
            "ordini_eseguiti": r.contatori["ordini_eseguiti"]}


# ---------------------------------------------------------------------------
# metriche (9.7)
# ---------------------------------------------------------------------------


def _anno(ts_ms: int) -> int:
    import datetime as _dt
    return _dt.datetime.fromtimestamp(ts_ms / 1000, tz=_dt.timezone.utc).year


def drawdown_r(r: List[float]) -> float:
    """Drawdown massimo della somma cumulata degli R (negativo o zero)."""
    picco = 0.0
    cum = 0.0
    peggiore = 0.0
    for x in r:
        cum += x
        picco = max(picco, cum)
        peggiore = min(peggiore, cum - picco)
    return peggiore


def profit_factor(r: List[float]) -> float:
    vinte = sum(x for x in r if x > 0)
    perse = -sum(x for x in r if x < 0)
    if perse == 0:
        return math.inf if vinte > 0 else 0.0
    return vinte / perse


def metriche(ris: Risultato, serie=None) -> Dict[str, object]:
    """Le metriche della sezione 9.7. Gli arrotondamenti (R a tre decimali, percentuali a
    due) si fanno quando si scrive il report, non qui."""
    tr = ris.trade
    r = [t.r for t in tr]
    n = len(r)
    out: Dict[str, object] = {"trade": n}
    if serie is not None and ris.fine >= ris.inizio:
        candele = ris.fine - ris.inizio + 1
        durata_mesi = (int(serie.ts[ris.fine]) + serie.durata - int(serie.ts[ris.inizio])) / (GIORNO_MS * 365.25 / 12)
        out["trade_al_mese"] = n / durata_mesi if durata_mesi > 0 else 0.0
        out["tempo_in_posizione"] = sum(t.candele_in_posizione for t in tr) / candele
    vinc = [x for x in r if x > 0]
    perd = [x for x in r if x <= 0]
    out["r_medio"] = sum(r) / n if n else 0.0
    out["profit_factor"] = profit_factor(r)
    out["vincenti"] = len(vinc) / n if n else 0.0
    out["r_medio_vincenti"] = sum(vinc) / len(vinc) if vinc else 0.0
    out["r_medio_perdenti"] = sum(perd) / len(perd) if perd else 0.0
    out["drawdown_max_r"] = drawdown_r(r)
    per_anno: Dict[int, float] = {}
    for t in tr:
        a = _anno(t.ts_uscita)
        per_anno[a] = per_anno.get(a, 0.0) + t.r
    out["r_per_anno"] = dict(sorted(per_anno.items()))
    out["ridotti"] = sum(1 for t in tr if t.ridotto)
    out["violazioni_liquidazione"] = sum(1 for t in tr if t.violazione_liquidazione)
    out["liquidazioni"] = sum(1 for t in tr if t.motivo == "liquidazione")
    out["motivi"] = {m: sum(1 for t in tr if t.motivo == m) for m in sorted({t.motivo for t in tr})}
    cont = ris.contatori
    if cont.get("ordini_inseriti", 0):
        out["ordini_inseriti"] = cont["ordini_inseriti"]
        out["ordini_eseguiti"] = cont["ordini_eseguiti"]
        out["ordini_cancellati"] = cont["ordini_cancellati"]
        out["esecuzione"] = cont["ordini_eseguiti"] / cont["ordini_inseriti"]
    return out


# ---------------------------------------------------------------------------
# test di troncamento (9.8)
# ---------------------------------------------------------------------------


def test_troncamento(variante: dict, serie, inizio: int, fine: int, n_istanti: int = 200,
                     seme: int = 2026, solo_catalogo: bool = True) -> List[str]:
    """Per ``n_istanti`` istanti scelti a caso fra ``inizio`` e ``fine`` (seme fisso) si
    ricalcolano indicatori e segnali con i soli dati fino a quell'istante: devono
    coincidere con quelli calcolati sull'intera serie. Restituisce le differenze (lista
    vuota = test superato)."""
    from research.src.catalogo3 import compila

    piena = compila(variante, serie, solo_catalogo=solo_catalogo)
    rng = np.random.default_rng(seme)
    candidati = np.arange(inizio, fine + 1)
    k = min(n_istanti, len(candidati))
    istanti = np.sort(rng.choice(candidati, size=k, replace=False))
    differenze: List[str] = []
    nomi = ("segnale", "ammessa", "opposto", "atr_stop", "atr_limite", "atr_trailing", "estremo_s2")
    for t in istanti:
        t = int(t)
        corta = compila(variante, serie.fino_a(t), solo_catalogo=solo_catalogo)
        for nome in nomi:
            a, b = getattr(piena, nome), getattr(corta, nome)
            if a is None and b is None:
                continue
            a = np.asarray(a)[: t + 1]
            b = np.asarray(b)
            uguali = (np.array_equal(a, b, equal_nan=True) if a.dtype.kind == "f"
                      else np.array_equal(a, b))
            if not uguali:
                diverse = np.flatnonzero(~((a == b) | (np.isnan(a) & np.isnan(b)))
                                         if a.dtype.kind == "f" else a != b)
                differenze.append(f"istante {t}: '{nome}' diverso in {len(diverse)} candele (prima: {int(diverse[0])})")
    return differenze


# pytest raccoglie le funzioni che si chiamano test_*: questa e' una funzione del motore (9.8),
# non un test, anche quando un file di test la importa con il suo nome
test_troncamento.__test__ = False
