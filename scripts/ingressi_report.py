"""IL PAPER ENTRA DOVE ENTRA IL GATE? — trade per trade (27 set 2026, backlog J12).

Il referto settimanale del 27 set (ops 0304, `scripts/confronto_gate_paper.py`)
dice che sulle 8 coppie piu' operate solo 20 trade del paper su 37 (54%) hanno
un ingresso del motore entro 2 barre. Un numero cosi' si legge in due modi
opposti — «il bot apre su una soglia diversa dal gate» oppure «il motore era
gia' dentro un trade precedente e non poteva rientrare» — e finche' resta un
numero solo non si sa quale dei due sia. Il proprietario vuole aprirlo: per OGNI
trade del paper, quale candela lo ha aperto, e PERCHE' il motore (la stessa
spec, sulla stessa storia) non entra li'.

LE CLASSI, calcolate in quest'ordine, una sola per trade:
  1. ABBINATO            il motore entra entro 2 barre (stesso metro di ops 0304:
                         `_accoppia`, ogni trade del motore usato una volta sola);
  2. MOTORE_IN_POSIZIONE il motore era ANCORA DENTRO un trade di quella coppia:
                         non e' la regola d'ingresso, e' la coda di un'uscita
                         diversa (cascata);
  3. MOTORE_IN_COOLDOWN  il motore stava saltando le barre dopo uno stop
                         (`cooldown_bars`, la stessa regola del bot);
  4. REGOLA_NON_SCATTA   il motore era libero, ma la regola sul suo frame NON
                         scatta a quella candela (ne' alle due vicine). Qui si
                         scava: indicatori del motore contro quelli che il bot ha
                         scritto sul trade (`indicators_at_entry`), regime, contesto;
  5. ABBINATO_LONTANO    un ingresso del motore fra 2 e 8 barre (latenza/confine);
  6. SENZA_MOTORE        spec non piu' nel registro, o candele mancanti.

I SOTTO-MOTIVI della classe 4, per dire DOVE differiscono le due parti:
  INDICATORI_DIVERSI  i valori non combaciano (> 5%): il bot costruisce gli
                      indicatori sulle ultime 200 candele (`price_agent.build_snapshot`),
                      il motore sulla storia intera — e' il WARMUP;
  PREZZO_VIVO         indicatori uguali, ma il bot decide sul prezzo VIVO di qualche
                      secondo dopo la chiusura, il motore sulla chiusura: con
                      quel prezzo la regola del motore scatterebbe;
  REGIME_DIVERSO      la strategia non e' attiva nel regime che il motore vede;
  CONTESTO_BTC        la spec guarda BTC o la 1h, e li' le due parti non vedono lo
                      stesso (o il contesto manca da una parte);
  REGOLA_DIVERSA      stessi valori, regola che scatta per il paper e non per il
                      motore: un BUG, non un dato;
  SEGNALE_SENZA_TRADE la regola del motore scatta anche li', ma nessun trade: il
                      setup non era tradabile (stop oltre MAX_STOP_PCT) oppure
                      quel segnale e' gia' abbinato a un altro trade del paper;
  IGNOTO              il trade non porta gli indicatori, o niente di sopra spiega.

LA SECONDA PASSATA («come il bot», `--finestra-bot`): il motore rigirato SOLO
sulle candele da 200 barre prima del periodo del paper. Toglie il warmup
(indicatori nati da poche candele, come nel bot) MA toglie anche la coda dei
trade precedenti: per il warmup puro c'e' la colonna «regola con 199 candele»,
calcolata trade per trade con `compute_snapshot` sulle stesse candele che il
bot vede.

COSA NON DICE: se il paper ha fatto bene ad aprire. Misura solo se paper e gate
guardano la stessa soglia. Un trade del motore non porta il motivo dell'uscita:
«stop» qui e' DEDOTTO (perdita chiusa prima dell'orizzonte).

SOLA LETTURA: legge i trade, il registro e le spec, rigira il motore, stampa.
Si ferma da sola a `--budget` secondi (720, sotto i 900 del canale ops) e
stampa cio' che ha misurato. Senza Firebase esce con 0 e lo dice.

Uso:
    .venv/bin/python -m scripts.ingressi_report
    .venv/bin/python -m scripts.ingressi_report --coppie 8 --budget 0
"""
from __future__ import annotations

import argparse
import bisect
import datetime as dt
import time
from collections import Counter, defaultdict
from datetime import date
from types import SimpleNamespace

from backtesting.data_loader import load_candles
from backtesting.engine import HORIZON_BARS, cooldown_bars
from backtesting.optimizer import WalkForwardOptimizer
from bot.agents.regime_detector import RegimeDetector
from bot.config import settings, timeframe_hours
from bot.core.firebase_client import decode_pairs, get_firebase
from bot.core.indicators import compute_indicator_frame, compute_snapshot
from bot.core.models import AssetSnapshot, IndicatorSnapshot
from bot.execution.exit_logic import breakeven_after_tp1, ladder_multiples, lock_keep
from bot.learning.trade_logger import TradeLogger
from bot.risk.setup_check import analizza_setup
from bot.strategies.base import StrategyContext
from bot.strategies.generated import MARKET_SYMBOL
# I MATTONI CONDIVISI con il referto settimanale: lo stesso rigiro del motore e lo
# stesso abbinamento, cosi' il 54% di ops 0304 e i numeri di qui sono lo stesso
# metro. Riscriverli qui vorrebbe dire misurare due cose diverse e chiamarle uguali.
from scripts.confronto_gate_paper import _accoppia, _costruisci, _ts, trade_del_gate

#: le classi, nell'ordine in cui si decidono e si stampano
CLASSI = ("ABBINATO", "MOTORE_IN_POSIZIONE", "MOTORE_IN_COOLDOWN", "REGOLA_NON_SCATTA",
          "ABBINATO_LONTANO", "SENZA_MOTORE")
#: i sotto-motivi della classe REGOLA_NON_SCATTA
SOTTO_MOTIVI = ("INDICATORI_DIVERSI", "PREZZO_VIVO", "REGIME_DIVERSO", "CONTESTO_BTC",
                "REGOLA_DIVERSA", "SEGNALE_SENZA_TRADE", "IGNOTO")
#: tolleranza dell'abbinamento, in barre (la stessa di ops 0304)
TOL_BARRE = 2
#: oltre la tolleranza e fino a qui: «lontano»
LONTANO_BARRE = 8
#: sopra questa differenza relativa due indicatori sono «diversi»
SOGLIA_DIFF = 0.05
#: le candele che il bot chiede a Binance per costruire gli indicatori
#: (`price_agent.build_snapshot`: limit=200, l'ultima in formazione viene tolta)
FINESTRA_BOT = 200
#: gli indicatori confrontati fra motore e paper
CAMPI_INDICATORI = ("rsi", "adx", "stoch_k", "atr", "ema_fast", "ema_slow",
                    "bb_upper", "bb_lower", "volume", "volume_sma", "close")
#: deadline propria, sotto i 900 s del canale ops
BUDGET_S = 720.0
#: sopra questa quota di abbinati la parita' degli ingressi «regge» (obiettivo J12)
OBIETTIVO_ABBINATI = 0.80


def di(msg: str = "") -> None:
    """Stampa SUBITO: un processo ucciso dal timeout del canale ops non lascia
    una riga se stdout accumula a blocchi."""
    print(msg, flush=True)


def _campo(t, nome: str, default=None):
    """Un campo da un SimTrade o da un dict (i test usano dict)."""
    if isinstance(t, dict):
        return t.get(nome, default)
    return getattr(t, nome, default)


def _f(v, default: float = 0.0) -> float:
    try:
        return float(v) if v is not None else default
    except (TypeError, ValueError):
        return default


def _quando(ts: float) -> str:
    if not ts or ts <= 0:
        return "?"
    return f"{dt.datetime.fromtimestamp(ts, dt.timezone.utc):%d %b %H:%M}"


# --------------------------------------------------------------------------- #
# Funzioni pure: la candela del paper, la finestra di un trade del motore      #
# --------------------------------------------------------------------------- #
def barra_del_paper(t: dict, tf_s: float) -> float:
    """L'APERTURA della candela chiusa che ha prodotto il segnale del paper.

    Dal 26 set il trade porta `signal_candle_ts`, il confine della candela
    CHIUSA (= apertura di quella in formazione): la candela del segnale apre una
    barra prima. Prima di allora c'e' solo `entry_time`, qualche secondo dopo il
    confine: si scende al confine e si torna indietro di una barra. E' la stessa
    convenzione del motore, che data il trade con `candles[i].open_time`, la
    barra alla cui chiusura nasce il segnale."""
    sc = t.get("signal_candle_ts")
    if sc is not None:
        try:
            return float(sc) - tf_s
        except (TypeError, ValueError):
            pass
    te = _ts(t.get("entry_time"))
    if te <= 0:
        return 0.0
    return (te // tf_s) * tf_s - tf_s


def finestra_trade(g, tf_s: float) -> tuple[float, float]:
    """(apertura della candela d'ingresso, apertura della candela d'uscita) di un
    trade del motore: resta dentro da `entry_ts` per `bars_held` barre."""
    e = _f(_campo(g, "entry_ts", 0.0))
    return e, e + max(0, int(_campo(g, "bars_held", 0) or 0)) * tf_s


def uscita_dedotta(g) -> str:
    """Il motivo dell'uscita di un trade del motore, DEDOTTO: il SimTrade non lo
    porta. Perdita chiusa prima dell'orizzonte = stop (base, o alzato dopo il
    primo gradino e tornato indietro); all'orizzonte = chiusura d'ufficio;
    guadagno = TP o lock in guadagno."""
    barre = int(_campo(g, "bars_held", 0) or 0)
    if barre >= HORIZON_BARS:
        return "orizzonte"
    return "stop" if _f(_campo(g, "pnl_pct", 0.0)) <= 0 else "guadagno"


def in_cooldown_dopo(g, tf_s: float, cd_barre: int) -> tuple[float, float] | None:
    """La finestra (uscita, fine cooldown] che il motore salta dopo QUESTO trade,
    o None se non ne apre una: il motore aspetta solo dopo uno stop in perdita
    (`engine.run_strategy`: `was_stop and pnl_pct <= 0`)."""
    if cd_barre <= 0 or uscita_dedotta(g) != "stop":
        return None
    _e, u = finestra_trade(g, tf_s)
    return u, u + cd_barre * tf_s


# --------------------------------------------------------------------------- #
# Il confronto degli indicatori                                                #
# --------------------------------------------------------------------------- #
def diff_indicatori(motore, paper, campi=CAMPI_INDICATORI, soglia: float = SOGLIA_DIFF) -> list[dict]:
    """I campi in cui motore e paper differiscono piu' di `soglia` (relativa al
    piu' grande dei due in modulo). Un valore presente da una parte sola conta
    come differenza («mancante»): e' il caso del warmup piu' brutale, un
    indicatore che da una parte non e' ancora nato. Accetta IndicatorSnapshot o
    dict da una parte e dall'altra."""
    out: list[dict] = []
    for c in campi:
        a = _campo(motore, c) if motore is not None else None
        b = _campo(paper, c) if paper is not None else None
        if a is None and b is None:
            continue
        if a is None or b is None:
            out.append({"campo": c, "motore": a, "paper": b, "diff": None})
            continue
        a, b = float(a), float(b)
        base = max(abs(a), abs(b))
        d = abs(a - b) / base if base > 0 else 0.0
        if d > soglia:
            out.append({"campo": c, "motore": a, "paper": b, "diff": d})
    return out


def regime_del_paper(t: dict) -> str:
    """`regime_at_entry` come lo scrive il paper («sideways», o «Regime.SIDEWAYS»
    nei trade piu' vecchi): sempre in minuscolo e senza prefisso."""
    return str(t.get("regime_at_entry") or "").strip().split(".")[-1].lower()


def sotto_motivo(diag: dict) -> tuple[str, str]:
    """(sotto-motivo, dettaglio) per un trade in REGOLA_NON_SCATTA, dalla
    diagnosi alla barra. L'ordine e' quello del docstring del modulo: prima le
    spiegazioni che si vedono nei numeri, poi quelle di contesto, e «bug» solo
    quando i valori combaciano e la regola no. Funzione pura: nessuna lettura."""
    if diag.get("scatta_motore_k"):
        if diag.get("tradabile") is False:
            return "SEGNALE_SENZA_TRADE", "la regola scatta ma il setup non e' tradabile (stop oltre MAX_STOP_PCT)"
        return "SEGNALE_SENZA_TRADE", "la regola scatta ma quel segnale e' gia' abbinato a un altro trade del paper"
    diffs = diag.get("diffs") or []
    if diag.get("indicatori_paper") is None:
        return "IGNOTO", "il trade non porta `indicators_at_entry`: niente da confrontare"
    if diffs:
        campi = ", ".join(f"{d['campo']} {_num(d['motore'])}/{_num(d['paper'])}" for d in diffs[:6])
        extra = "; con 199 candele la regola scatta" if diag.get("scatta_bot200") else ""
        return "INDICATORI_DIVERSI", f"motore/paper: {campi}{extra}"
    if diag.get("scatta_prezzo_vivo"):
        return "PREZZO_VIVO", (f"stessi indicatori; col prezzo del paper ({_num(diag.get('prezzo_paper'))}) "
                               f"la regola scatta, con la chiusura ({_num(diag.get('prezzo_motore'))}) no")
    if diag.get("attiva_nel_regime") is False:
        return "REGIME_DIVERSO", (f"strategia non attiva nel regime del motore "
                                  f"({diag.get('regime_motore')}; paper: {diag.get('regime_paper')})")
    ctx = diag.get("contesto") or {}
    if ctx.get("usa_mercato") or ctx.get("usa_htf"):
        pezzi = []
        if ctx.get("usa_mercato"):
            pezzi.append(f"BTC market_up motore {ctx.get('market_up_motore')} / paper {ctx.get('market_up_paper')}")
        if ctx.get("usa_htf"):
            d1 = ctx.get("diffs_1h") or []
            pezzi.append("1h " + (", ".join(f"{d['campo']} {_num(d['motore'])}/{_num(d['paper'])}" for d in d1[:4])
                                  if d1 else "uguale"))
        return "CONTESTO_BTC", "; ".join(pezzi)
    if diag.get("scatta_paper_valori"):
        return "REGOLA_DIVERSA", "stessi valori: la regola scatta sui valori del paper e non sul frame del motore"
    return "IGNOTO", "stessi valori e la regola non scatta neanche sui valori del paper"


def _num(v) -> str:
    if v is None:
        return "—"
    try:
        x = float(v)
    except (TypeError, ValueError):
        return str(v)
    return f"{x:.4g}"


# --------------------------------------------------------------------------- #
# IL CLASSIFICATORE (puro: trade del paper, trade del motore, una diagnosi)    #
# --------------------------------------------------------------------------- #
_VUOTO = SimpleNamespace(entry_ts=0.0)


def _abbina_uno(p: dict, gtrades, usati: set, tol: float):
    """Il trade del motore non ancora usato piu' vicino a `p` entro `tol`, con la
    STESSA funzione di ops 0304 (`_accoppia`): i gia' usati diventano un trade
    vuoto (entry_ts 0), che `_accoppia` salta. NB: `_accoppia` misura lo scarto
    da `entry_time` del paper (qualche secondo dopo il confine della candela),
    non dalla candela del segnale: con 2 barre di tolleranza entrano le barre
    k, k+1 e k+2 del motore e NON la k-1. E' il metro del referto, si tiene."""
    gt = [g if i not in usati else _VUOTO for i, g in enumerate(gtrades)]
    r = _accoppia([p], gt, tol)
    return r[0] if r else None


def classifica_coppia(ptrades: list[dict], gtrades, tf_s: float, cd_barre: int,
                      diagnosi=None) -> list[dict]:
    """Una riga per trade del paper: classe, dettaglio, e la diagnosi se serve.

    `diagnosi(p, barra_ts)` viene chiamata SOLO per i trade che arrivano alla
    classe 4 (e' la parte cara: snapshot e regola); ritorna il dict che legge
    `sotto_motivo`, o None se la candela non c'e' (-> SENZA_MOTORE). Due passate
    sull'abbinamento: prima i vicini per tutti (cosi' un trade lontano non ruba
    il segnale vicino di un trade successivo), poi i lontani fra i rimasti."""
    tol = TOL_BARRE * tf_s
    righe: list[dict] = []
    usati: set = set()
    for p in ptrades:
        b = barra_del_paper(p, tf_s)
        r = {"paper": p, "barra_ts": b, "classe": None, "sotto": None, "dettaglio": "",
             "delta_min": None, "stessa_direzione": None, "motore": None}
        if b <= 0:
            r.update(classe="SENZA_MOTORE", dettaglio="trade senza `entry_time` leggibile")
        else:
            m = _abbina_uno(p, gtrades, usati, tol)
            if m is not None:
                i, delta = m
                usati.add(i)
                g = gtrades[i]
                dir_p = str(p.get("direction") or "").lower()
                dir_g = str(_campo(g, "direction", "") or "").lower()
                # lo scarto e' fra la candela del segnale del paper e quella del
                # motore: con `entry_time` sarebbe sempre +15 min per costruzione
                r.update(classe="ABBINATO", motore=g,
                         delta_min=(_f(_campo(g, "entry_ts")) - b) / 60.0,
                         stessa_direzione=(dir_p == dir_g),
                         dettaglio=(f"motore alla barra {_quando(_f(_campo(g, 'entry_ts')))} "
                                    f"({(_f(_campo(g, 'entry_ts')) - b) / 60.0:+.0f} min), direzione "
                                    f"{'uguale' if dir_p == dir_g else 'DIVERSA (' + dir_g + ')'}"))
        righe.append(r)

    for r in righe:
        if r["classe"] is not None:
            continue
        p, b = r["paper"], r["barra_ts"]
        # 2) il motore era ancora dentro un trade di questa coppia
        dentro = None
        for g in gtrades:
            e, u = finestra_trade(g, tf_s)
            if e > 0 and e < b <= u:
                dentro = g
                break
        if dentro is not None:
            e, u = finestra_trade(dentro, tf_s)
            r.update(classe="MOTORE_IN_POSIZIONE", motore=dentro,
                     dettaglio=(f"dentro il trade del {_quando(e)} ({_campo(dentro, 'direction')}, "
                                f"uscito {_quando(u)}, {uscita_dedotta(dentro)} dedotto, "
                                f"{_f(_campo(dentro, 'pnl_pct')) * 100:+.2f}%): cascata di un'uscita "
                                f"diversa, non della regola d'ingresso"))
            continue
        # 3) il motore stava saltando le barre dopo uno stop
        cd = None
        for g in gtrades:
            w = in_cooldown_dopo(g, tf_s, cd_barre)
            if w and w[0] < b <= w[1]:
                cd = (g, w)
                break
        if cd is not None:
            g, (u, fine) = cd
            r.update(classe="MOTORE_IN_COOLDOWN", motore=g,
                     dettaglio=(f"cooldown di {cd_barre} barre dopo lo stop del {_quando(u)} "
                                f"(fino a {_quando(fine)}): la barra del paper e' la "
                                f"{int((b - u) // tf_s)}ª di {cd_barre}"))
            continue
        # 4) libero e fermo: la regola sul frame del motore non scatta?
        diag = None
        if diagnosi is not None:
            try:
                diag = diagnosi(p, b)
            except Exception as exc:  # noqa: BLE001
                diag = {"errore": str(exc)}
        if diag is None:
            r.update(classe="SENZA_MOTORE", dettaglio="candela del paper non nei dati del motore")
            continue
        if diag.get("errore"):
            r.update(classe="SENZA_MOTORE", dettaglio=f"diagnosi fallita: {diag['errore']}")
            continue
        r["diagnosi"] = diag
        scatta_vicino = any(diag.get("scatta_motore", {}).values())
        if not scatta_vicino or diag.get("scatta_motore_k"):
            # non scatta a k ne' vicino -> classe 4; scatta a k senza trade -> anche
            # classe 4 (SEGNALE_SENZA_TRADE): il motore lo vede ma non entra
            sotto, det = sotto_motivo(diag)
            r.update(classe="REGOLA_NON_SCATTA", sotto=sotto, dettaglio=det)
            continue
        # 5) scatta a una barra vicina: c'e' un ingresso del motore fra 2 e 8 barre?
        m = _abbina_uno(p, gtrades, usati, LONTANO_BARRE * tf_s)
        if m is not None:
            i, _d = m
            usati.add(i)
            g = gtrades[i]
            r.update(classe="ABBINATO_LONTANO", motore=g,
                     delta_min=(_f(_campo(g, "entry_ts")) - b) / 60.0,
                     dettaglio=(f"motore alla barra {_quando(_f(_campo(g, 'entry_ts')))} "
                                f"({(_f(_campo(g, 'entry_ts')) - b) / 60.0:+.0f} min, "
                                f"{abs(_f(_campo(g, 'entry_ts')) - b) / tf_s:.0f} barre): latenza o confine"))
            continue
        sotto, det = sotto_motivo(diag)
        r.update(classe="REGOLA_NON_SCATTA", sotto=sotto,
                 dettaglio=det + " (scatta a una barra vicina, senza trade del motore entro 8 barre)")
    return righe


# --------------------------------------------------------------------------- #
# La diagnosi alla barra: cosa vede il motore, cosa ha visto il bot            #
# --------------------------------------------------------------------------- #
class Diagnosta:
    """Costruisce per una coppia lo snapshot del motore a una barra e valuta la
    regola come `engine.run_strategy` (stesso `_snapshot_from_frame`, stessa 1h
    reale, stesso `RegimeDetector`, stesso contesto BTC), poi confronta con cio'
    che il bot ha scritto sul trade. Tutto in fail-open: un errore torna come
    `errore` e il trade finisce in SENZA_MOTORE, non ferma la coppia."""

    def __init__(self, bt, make, symbol: str, candles, frame, tf_name: str,
                 ctx_by_ts=None, ladder=None):
        self.bt, self.make, self.symbol = bt, make, symbol
        self.candles, self.frame, self.tf = candles, frame, tf_name
        self.ctx_by_ts, self.ladder = ctx_by_ts, ladder
        self.ts = [c.open_time.timestamp() for c in candles]
        self.htf = bt._htf_for(symbol, candles)
        self.rilevatore = RegimeDetector()

    def indice(self, ts: float) -> int | None:
        i = bisect.bisect_left(self.ts, ts - 1.0)
        if i < len(self.ts) and abs(self.ts[i] - ts) < 1.0:
            return i
        return None

    def snapshot_motore(self, k: int) -> AssetSnapshot:
        snap = self.bt._snapshot_from_frame(self.symbol, self.frame, k, htf=self.htf)
        snap.regime = self.rilevatore.detect(snap)
        return snap

    def _ctx(self, snap, k: int):
        assets = {self.symbol: snap}
        ctx_snap = None
        if self.ctx_by_ts:
            ctx_snap = self.ctx_by_ts.get(self.candles[k].open_time)
            if ctx_snap is not None:
                assets[ctx_snap.symbol] = ctx_snap
        return StrategyContext(assets, snap.regime), ctx_snap

    def segnale(self, strategy, snap, k: int):
        ctx, _ = self._ctx(snap, k)
        if not strategy.is_active_in(snap.regime):
            return None
        return strategy.generate_signal(snap, ctx)

    def snapshot_bot(self, k: int, prezzo: float) -> AssetSnapshot:
        """Gli indicatori COME LI COSTRUISCE IL BOT: `compute_snapshot` sulle
        ultime 199 candele chiuse (200 chieste, l'ultima in formazione tolta), la
        1h dalle candele orarie chiuse a quell'istante, il prezzo vivo del paper."""
        chiuse = self.candles[max(0, k - (FINESTRA_BOT - 2)): k + 1]
        ind = {self.tf: compute_snapshot(chiuse, self.tf)}
        fine = self.candles[k].open_time + dt.timedelta(seconds=timeframe_hours(self.tf) * 3600)
        hc = [c for c in self.bt._resample_1h(self.candles[max(0, k - 4 * (FINESTRA_BOT + 8)): k + 1])
              if c.open_time + dt.timedelta(hours=1) <= fine][-(FINESTRA_BOT - 1):]
        if hc:
            ind["1h"] = compute_snapshot(hc, "1h")
        ind.setdefault(settings.ORCHESTRATOR_TIMEFRAME, ind[self.tf])
        snap = AssetSnapshot(symbol=self.symbol, price=prezzo, indicators=ind)
        snap.regime = self.rilevatore.detect(snap)
        return snap

    @staticmethod
    def snapshot_dal_trade(symbol: str, t: dict) -> AssetSnapshot | None:
        """Lo snapshot ricostruito da `indicators_at_entry` del trade, col prezzo
        d'ingresso del paper: e' cio' su cui il bot ha deciso."""
        ind_raw = t.get("indicators_at_entry")
        if not isinstance(ind_raw, dict) or not ind_raw:
            return None
        ind = {}
        for tf, d in ind_raw.items():
            if isinstance(d, dict):
                try:
                    ind[tf] = IndicatorSnapshot(**{**d, "timeframe": d.get("timeframe") or tf})
                except Exception:  # noqa: BLE001
                    continue
        if not ind:
            return None
        prezzo = _f(t.get("entry_price"), 0.0) or _f(_campo(ind.get(next(iter(ind))), "close"), 0.0)
        snap = AssetSnapshot(symbol=symbol, price=prezzo, indicators=ind)
        return snap

    def __call__(self, t: dict, barra_ts: float) -> dict | None:
        k = self.indice(barra_ts)
        if k is None or k < 1 or k >= len(self.candles) - 1:
            return None
        strategy = self.make()
        out: dict = {"k": k, "scatta_motore": {}, "diffs": [], "contesto": {}}
        snaps = {}
        for j in (k - 1, k, k + 1):
            snaps[j] = self.snapshot_motore(j)
            out["scatta_motore"][j - k] = self.segnale(strategy, snaps[j], j) is not None
        snap = snaps[k]
        out["scatta_motore_k"] = out["scatta_motore"][0]
        out["regime_motore"] = getattr(snap.regime, "value", str(snap.regime))
        out["regime_paper"] = regime_del_paper(t)
        out["attiva_nel_regime"] = strategy.is_active_in(snap.regime)
        out["prezzo_motore"] = float(snap.price)
        out["prezzo_paper"] = _f(t.get("entry_price"), 0.0)
        # il setup: se la regola scatta, era tradabile?
        if out["scatta_motore_k"]:
            sig = self.segnale(strategy, snap, k)
            stop = getattr(sig, "suggested_stop", None) if sig is not None else None
            out["tradabile"] = bool(analizza_setup(float(snap.price), stop, self.ladder)["tradabile"]) if stop else True
        # gli indicatori del motore contro quelli scritti dal bot sul trade
        ind_m = snap.ind(self.tf)
        ind_raw = t.get("indicators_at_entry") if isinstance(t.get("indicators_at_entry"), dict) else None
        ind_p = (ind_raw or {}).get(self.tf)
        out["indicatori_paper"] = ind_p if isinstance(ind_p, dict) else None
        out["diffs"] = diff_indicatori(ind_m, ind_p) if isinstance(ind_p, dict) else []
        # la regola col prezzo VIVO del paper sugli indicatori del motore
        if out["prezzo_paper"] > 0 and not out["scatta_motore_k"]:
            vivo = snap.model_copy(update={"price": out["prezzo_paper"]})
            out["scatta_prezzo_vivo"] = self.segnale(strategy, vivo, k) is not None
        # la regola sui valori scritti dal bot (senza contesto BTC: non e' sul trade)
        ricostruito = self.snapshot_dal_trade(self.symbol, t)
        if ricostruito is not None:
            ricostruito.regime = snap.regime
            try:
                out["scatta_paper_valori"] = strategy.generate_signal(
                    ricostruito, StrategyContext({self.symbol: ricostruito}, snap.regime)) is not None
            except Exception:  # noqa: BLE001
                out["scatta_paper_valori"] = None
        # la regola con 199 candele, come il bot (il warmup PURO, trade per trade)
        try:
            bot_snap = self.snapshot_bot(k, out["prezzo_paper"] or float(snap.price))
            ctx, _ = self._ctx(bot_snap, k)
            out["scatta_bot200"] = strategy.generate_signal(bot_snap, ctx) is not None
            out["diffs_bot200"] = diff_indicatori(ind_m, bot_snap.ind(self.tf))
        except Exception:  # noqa: BLE001
            out["scatta_bot200"] = None
        # il contesto: BTC e la 1h, se la spec li guarda
        usa_m = bool(getattr(strategy, "usa_mercato", False))
        usa_h = bool(getattr(strategy, "usa_htf", False))
        ctx_info = {"usa_mercato": usa_m, "usa_htf": usa_h}
        if usa_m:
            _c, ctx_snap = self._ctx(snap, k)
            m = ctx_snap.ind("1h") if ctx_snap is not None else None
            ctx_info["market_up_motore"] = (None if m is None or m.ema_fast is None or m.ema_slow is None
                                            else (1.0 if m.ema_fast > m.ema_slow else 0.0))
            feats = t.get("feats_at_entry") if isinstance(t.get("feats_at_entry"), dict) else {}
            ctx_info["market_up_paper"] = feats.get("market_up")
        if usa_h:
            p1h = (ind_raw or {}).get("1h")
            ctx_info["diffs_1h"] = (diff_indicatori(snap.ind("1h"), p1h, campi=("ema_fast", "ema_slow", "close"))
                                    if isinstance(p1h, dict) else [])
        out["contesto"] = ctx_info
        return out


# --------------------------------------------------------------------------- #
# Il motore per una coppia: storia intera (come ops 0304) e «come il bot»      #
# --------------------------------------------------------------------------- #
def trade_del_motore(symbol: str, strategy: str, spec, ladder, args, ctx_by_ts=None):
    """I trade del motore su TUTTA la storia. Senza contesto BTC e' esattamente
    `trade_del_gate` di ops 0304; con una spec che guarda il mercato si passa il
    contesto come fa il gate (`optimize.py`), altrimenti quella spec non
    produrrebbe nessun segnale e ogni suo trade del paper sembrerebbe orfano."""
    if ctx_by_ts is None:
        return trade_del_gate(symbol, strategy, spec, ladder, args)
    make = lambda: _costruisci(spec, strategy, ladder)  # noqa: E731
    if make() is None:
        return None, "definizione della strategia non piu' nel registro"
    candles = load_candles(symbol, args.interval, args.start, args.end or date.today().isoformat(),
                           prefer=args.source, allow_synthetic=False)
    if len(candles) < 300:
        return None, f"solo {len(candles)} candele"
    frame = compute_indicator_frame(candles)
    opt = WalkForwardOptimizer(n_windows=1, interval=args.interval)
    st = opt.bt.run_strategy(make(), symbol, candles, frame=frame, context_by_ts=ctx_by_ts)
    return sorted(st.trades, key=lambda t: _f(getattr(t, "entry_ts", 0))), None


def finestra_come_il_bot(bt, make, symbol: str, candles, barre: list[int], ctx_by_ts=None):
    """Il motore rigirato SOLO da `FINESTRA_BOT` barre prima della prima candela
    del paper fino a un orizzonte dopo l'ultima: indicatori giovani come nel bot,
    e niente coda dei trade precedenti. Ritorna i trade, in ordine di tempo."""
    if not barre:
        return []
    lo = max(0, min(barre) - FINESTRA_BOT)
    hi = min(len(candles), max(barre) + HORIZON_BARS + 2)
    sub = candles[lo:hi]
    if len(sub) < FINESTRA_BOT + 2:
        return []
    st = bt.run_strategy(make(), symbol, sub, frame=compute_indicator_frame(sub),
                         context_by_ts=ctx_by_ts)
    return sorted(st.trades, key=lambda t: _f(getattr(t, "entry_ts", 0)))


# --------------------------------------------------------------------------- #
# Riassunto e lettura                                                          #
# --------------------------------------------------------------------------- #
def riassunto(righe_per_coppia: dict[str, list[dict]]) -> dict:
    """Conteggi per classe e sotto-motivo, quota di abbinati totale e per
    coppia, le 10 coppie con piu' trade non abbinati. Funzione pura."""
    classi: Counter = Counter()
    sotto: Counter = Counter()
    per_coppia: dict[str, dict] = {}
    for key, righe in righe_per_coppia.items():
        n = len(righe)
        ab = sum(1 for r in righe if r.get("classe") == "ABBINATO")
        per_coppia[key] = {"n": n, "abbinati": ab, "non": n - ab,
                           "quota": (ab / n) if n else 0.0}
        for r in righe:
            classi[r.get("classe") or "?"] += 1
            if r.get("classe") == "REGOLA_NON_SCATTA":
                sotto[r.get("sotto") or "IGNOTO"] += 1
    n = sum(classi.values())
    ab = classi.get("ABBINATO", 0)
    top = sorted(per_coppia.items(), key=lambda kv: (-kv[1]["non"], -kv[1]["n"], kv[0]))[:10]
    return {"n": n, "abbinati": ab, "quota": (ab / n) if n else 0.0,
            "classi": dict(classi), "sotto": dict(sotto), "per_coppia": per_coppia,
            "top_non_abbinati": [k for k, _v in top if _v["non"] > 0]}


def lettura(r: dict, quota_finestra_bot: float | None = None) -> str:
    """LA FRASE, generata da regole: la classe che pesa di piu' fra i NON
    abbinati decide la lettura. Non dice mai «e' sicuro»: e' un campione di
    giorni."""
    n = r.get("n", 0)
    if not n:
        return "nessun trade del paper classificato: niente da leggere."
    quota = r.get("quota", 0.0)
    testa = f"{r.get('abbinati', 0)}/{n} ingressi abbinati ({quota * 100:.0f}%)"
    if quota >= OBIETTIVO_ABBINATI:
        return f"{testa}: la parita' degli ingressi regge (obiettivo ≥ {OBIETTIVO_ABBINATI * 100:.0f}%)."
    classi = {k: v for k, v in (r.get("classi") or {}).items() if k != "ABBINATO" and v}
    if not classi:
        return f"{testa}: nessun non abbinato da spiegare."
    magg = max(classi.items(), key=lambda kv: (kv[1], kv[0]))[0]
    quante = classi[magg]
    non = sum(classi.values())
    coda = f" ({quante} su {non} non abbinati)"
    if magg == "MOTORE_IN_POSIZIONE":
        return (f"{testa}: la divergenza e' una CASCATA DALLE USCITE{coda} — il motore era ancora "
                f"dentro un trade precedente; la regola d'ingresso non e' in discussione, "
                f"il punto sono le uscite diverse fra paper e motore.")
    if magg == "MOTORE_IN_COOLDOWN":
        return (f"{testa}: il motore stava in COOLDOWN dopo uno stop{coda} — il bot rientra dove "
                f"il motore aspetta: da verificare il cooldown del bot (COOLDOWN_HOURS, barre "
                f"della strategia) contro `cooldown_bars` del motore.")
    if magg == "ABBINATO_LONTANO":
        return (f"{testa}: gli ingressi ci sono ma spostati di 2-8 barre{coda} — latenza o "
                f"confine di candela, non una soglia diversa.")
    if magg == "SENZA_MOTORE":
        return (f"{testa}: la maggior parte non e' rigirabile{coda} — spec fuori dal registro o "
                f"candele mancanti: prima i dati, poi la regola.")
    sotto = r.get("sotto") or {}
    if not sotto:
        return f"{testa}: la regola non scatta sul frame del motore{coda}, senza sotto-motivo."
    ms = max(sotto.items(), key=lambda kv: (kv[1], kv[0]))[0]
    if ms == "INDICATORI_DIVERSI":
        fb = ""
        if quota_finestra_bot is not None:
            fb = (f"; col motore «come il bot» (finestra corta) gli abbinati salgono a "
                  f"{quota_finestra_bot * 100:.0f}%" if quota_finestra_bot > quota
                  else f"; la finestra corta non li alza ({quota_finestra_bot * 100:.0f}%)")
        return (f"{testa}: e' il WARMUP{coda} — il bot costruisce gli indicatori su 200 candele, "
                f"il motore sulla storia intera, e i valori non combaciano{fb}.")
    if ms == "PREZZO_VIVO":
        return (f"{testa}: e' il PREZZO VIVO{coda} — stessi indicatori, ma il bot decide sul "
                f"prezzo di qualche secondo dopo la chiusura, il motore sulla chiusura.")
    if ms == "REGOLA_DIVERSA":
        return (f"{testa}: stessi valori, regola diversa{coda} — e' un BUG fra "
                f"GeneratedStrategy nel bot e nel motore, da cercare nel codice, non nei dati.")
    if ms == "CONTESTO_BTC":
        return (f"{testa}: e' il CONTESTO{coda} — la spec guarda BTC o la 1h e le due parti "
                f"non vedono lo stesso contesto.")
    if ms == "REGIME_DIVERSO":
        return f"{testa}: e' il REGIME{coda} — il motore vede un regime in cui la strategia non opera."
    if ms == "SEGNALE_SENZA_TRADE":
        return (f"{testa}: il motore vede lo stesso segnale ma non lo apre{coda} — setup non "
                f"tradabile o segnale gia' abbinato: e' il filtro del setup, non la regola.")
    return f"{testa}: la regola non scatta e i dati non spiegano perche'{coda} — da guardare a mano."


def _riga_trade(i: int, r: dict) -> list[str]:
    p = r["paper"]
    esito = _f(p.get("pnl"), 0.0)
    testa = (f"  #{i:<2} {_quando(r['barra_ts'])} UTC  {str(p.get('direction') or '?'):<5} "
             f"entry {_num(p.get('entry_price'))}  pnl {esito:+.2f} USDT ({p.get('exit_reason') or '?'})")
    classe = r.get("classe") or "?"
    if r.get("sotto"):
        classe += f" · {r['sotto']}"
    righe = [testa, f"       {classe}: {r.get('dettaglio', '')}"]
    d = r.get("diagnosi")
    if d and r.get("classe") == "REGOLA_NON_SCATTA":
        sm = d.get("scatta_motore") or {}
        righe.append(f"       regola sul frame del motore: k-1 {_sn(sm.get(-1))} · k {_sn(sm.get(0))} · "
                     f"k+1 {_sn(sm.get(1))} · con 199 candele {_sn(d.get('scatta_bot200'))} · "
                     f"sui valori del paper {_sn(d.get('scatta_paper_valori'))} · regime motore "
                     f"{d.get('regime_motore')} / paper {d.get('regime_paper') or '?'}")
    return righe


def _sn(v) -> str:
    return "?" if v is None else ("si" if v else "no")


# --------------------------------------------------------------------------- #
# main                                                                         #
# --------------------------------------------------------------------------- #
def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--interval", default=settings.ORCHESTRATOR_TIMEFRAME)
    ap.add_argument("--start", default="2022-01-01")
    ap.add_argument("--end", default=None)
    ap.add_argument("--source", default="binance")
    ap.add_argument("--coppie", type=int, default=0,
                    help="quante coppie, dalle piu' operate in giu' (0 = tutte)")
    ap.add_argument("--budget", type=float, default=BUDGET_S,
                    help="secondi prima di fermarsi da soli (0 = mai)")
    ap.add_argument("--finestra-bot", dest="finestra_bot", action=argparse.BooleanOptionalAction,
                    default=True, help="seconda passata del motore sulla finestra corta")
    args = ap.parse_args()
    t0 = time.time()
    deadline = (t0 + float(args.budget)) if args.budget > 0 else 0.0

    fb = get_firebase()
    tutti = [t for t in (TradeLogger(fb).all_since(0.0) or [])
             if t.get("symbol") and t.get("strategy")]
    per_coppia: dict[str, list[dict]] = defaultdict(list)
    for t in tutti:
        per_coppia[f"{t['symbol']}|{t['strategy']}"].append(t)
    if not per_coppia:
        di("[ingressi] nessun trade del paper (o nessun Firebase): niente da classificare.")
        return 0
    specs = decode_pairs((fb.get_doc("discovered_strategies", "specs") or {}).get("specs"))
    pairs = decode_pairs((fb.get_doc("strategy_registry", "validated") or {}).get("pairs"))

    scelte = sorted(per_coppia.items(), key=lambda kv: (-len(kv[1]), kv[0]))
    if args.coppie > 0:
        scelte = scelte[: args.coppie]
    di("=" * 74)
    di("INGRESSI DEL PAPER, TRADE PER TRADE: dove il motore non entra, e perche'")
    di("=" * 74)
    di(f"PAPER: {len(tutti)} trade chiusi su {len(per_coppia)} coppie · rigirate {len(scelte)} · "
       f"tolleranza {TOL_BARRE} barre · deadline {'nessuna' if not deadline else f'{args.budget:.0f}s'}")

    righe_per_coppia: dict[str, list[dict]] = {}
    finestra: dict[str, tuple[int, int]] = {}
    saltate: list[tuple[str, str]] = []
    btc_ctx: dict = {}     # interval -> contesto BTC (costruito solo se una spec lo chiede)

    for key, ptr in scelte:
        if deadline and time.time() > deadline:
            saltate.append((key, "tempo (budget)"))
            continue
        symbol, strategy = key.split("|", 1)
        ptr_ord = sorted(ptr, key=lambda t: _ts(t.get("entry_time")))
        spec = specs.get(strategy)
        sparams = (pairs.get(key) or {}).get("last_params") or {}
        ladder = ladder_multiples(sparams)
        iv = (spec or {}).get("timeframe") or args.interval
        tf_s = timeframe_hours(iv) * 3600.0
        cd_barre = cooldown_bars(settings.COOLDOWN_HOURS, timeframe_hours(iv))
        a = SimpleNamespace(**{**vars(args), "interval": iv})
        scala = "/".join(f"{m:g}" for m in ladder) if ladder else "globale"
        di(f"\n── {key} · {len(ptr_ord)} trade · {iv} · scala {scala} · BE "
           f"{'si' if breakeven_after_tp1(sparams) else 'no'} · keep {lock_keep(sparams) or 'globale'}"
           + ("" if spec else " · SPEC NON NEL REGISTRO"))
        try:
            make = lambda spec=spec, strategy=strategy, ladder=ladder: _costruisci(spec, strategy, ladder)  # noqa: E731,E501
            strat = make()
            ctx = None
            if strat is not None and getattr(strat, "usa_mercato", False):
                if iv not in btc_ctx:
                    try:
                        bc = load_candles(MARKET_SYMBOL, iv, args.start, args.end or date.today().isoformat(),
                                          prefer=args.source, allow_synthetic=False)
                        opt0 = WalkForwardOptimizer(n_windows=1, interval=iv)
                        btc_ctx[iv] = opt0.bt.build_context(MARKET_SYMBOL, bc) if len(bc) >= 200 else {}
                    except Exception as exc:  # noqa: BLE001
                        di(f"  contesto BTC non caricato: {exc}")
                        btc_ctx[iv] = {}
                ctx = btc_ctx.get(iv) or None
                di(f"  la spec guarda il MERCATO: motore con contesto BTC "
                   f"({'caricato' if ctx else 'NON disponibile'})")
            gtrades, errore = trade_del_motore(symbol, strategy, spec, ladder, a, ctx_by_ts=ctx)
            if errore:
                di(f"  MOTORE: non rigirabile ({errore})")
                righe_per_coppia[key] = [
                    {"paper": p, "barra_ts": barra_del_paper(p, tf_s), "classe": "SENZA_MOTORE",
                     "sotto": None, "dettaglio": errore} for p in ptr_ord]
                saltate.append((key, errore))
                for i, r in enumerate(righe_per_coppia[key], 1):
                    for line in _riga_trade(i, r):
                        di(line)
                continue
            candles = load_candles(symbol, iv, args.start, args.end or date.today().isoformat(),
                                   prefer=args.source, allow_synthetic=False)
            frame = compute_indicator_frame(candles)
            opt = WalkForwardOptimizer(n_windows=1, interval=iv)
            tf_name = strat.timeframe if hasattr(strat, "timeframe") else iv
            diag = Diagnosta(opt.bt, make, symbol, candles, frame, tf_name, ctx_by_ts=ctx, ladder=ladder)
            righe = classifica_coppia(ptr_ord, gtrades, tf_s, cd_barre, diagnosi=diag)
            righe_per_coppia[key] = righe
            prima = min((r["barra_ts"] for r in righe if r["barra_ts"] > 0), default=0.0)
            n_periodo = sum(1 for g in gtrades if _f(getattr(g, "entry_ts", 0)) >= prima - tf_s)
            di(f"  motore: {len(gtrades)} trade sulla storia intera, {n_periodo} dal primo trade del paper · "
               f"cooldown {cd_barre} barre")
            for i, r in enumerate(righe, 1):
                for line in _riga_trade(i, r):
                    di(line)
            ab = sum(1 for r in righe if r["classe"] == "ABBINATO")
            riga = f"  ABBINATI {ab}/{len(righe)}"
            if args.finestra_bot:
                barre = [diag.indice(r["barra_ts"]) for r in righe]
                barre = [b for b in barre if b is not None]
                g2 = finestra_come_il_bot(opt.bt, make, symbol, candles, barre, ctx_by_ts=ctx)
                ab2 = len(_accoppia(ptr_ord, g2, TOL_BARRE * tf_s)) if g2 else 0
                finestra[key] = (ab2, len(righe))
                riga += (f" · «come il bot» (da {FINESTRA_BOT} barre prima del paper): "
                         f"{ab2}/{len(righe)} abbinati, {len(g2)} trade del motore")
            di(riga)
        except Exception as exc:  # noqa: BLE001
            di(f"  ERRORE su questa coppia ({exc}): saltata")
            saltate.append((key, str(exc)))
            righe_per_coppia.setdefault(key, [
                {"paper": p, "barra_ts": barra_del_paper(p, tf_s), "classe": "SENZA_MOTORE",
                 "sotto": None, "dettaglio": f"errore: {exc}"} for p in ptr_ord])
        di(f"  [{time.time() - t0:.0f}s]")

    r = riassunto(righe_per_coppia)
    q_fb = None
    if finestra:
        tot = sum(n for _a, n in finestra.values())
        q_fb = (sum(a for a, _n in finestra.values()) / tot) if tot else None
    di("\n" + "=" * 74)
    di("RIASSUNTO")
    di("=" * 74)
    di(f"  trade classificati: {r['n']} · abbinati {r['abbinati']} ({r['quota'] * 100:.0f}%)"
       + (f" · «come il bot» {q_fb * 100:.0f}%" if q_fb is not None else ""))
    di("  per classe:")
    for c in CLASSI:
        if r["classi"].get(c):
            di(f"    {c:<22}{r['classi'][c]:>4}")
    if r["sotto"]:
        di("  REGOLA_NON_SCATTA per sotto-motivo:")
        for s in SOTTO_MOTIVI:
            if r["sotto"].get(s):
                di(f"    {s:<22}{r['sotto'][s]:>4}")
    di("  per coppia (abbinati/trade):")
    for key, v in sorted(r["per_coppia"].items(), key=lambda kv: (-kv[1]["non"], kv[0])):
        fbk = finestra.get(key)
        di(f"    {key:<34}{v['abbinati']:>3}/{v['n']:<3} ({v['quota'] * 100:>3.0f}%)"
           + (f" · come il bot {fbk[0]}/{fbk[1]}" if fbk else ""))
    if r["top_non_abbinati"]:
        di("  coppie con piu' non abbinati: " + ", ".join(
            f"{k} ({r['per_coppia'][k]['non']})" for k in r["top_non_abbinati"]))
    if saltate:
        di(f"  non rigirate: {len(saltate)}")
        for key, err in saltate:
            di(f"    {key}: {err}")
    di(f"\nLETTURA: {lettura(r, q_fb)}")
    di("  NB: i trade del motore sono simulati sulla storia intera, senza holdout; «stop» del")
    di("      motore e' dedotto (il SimTrade non porta il motivo). Questo comando misura e basta.")
    di(f"[ingressi] finito in {time.time() - t0:.0f}s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
