"""RECONCILER — cosa crede il bot contro cosa c'e' davvero sull'exchange.

Il bot tiene uno stato interno delle posizioni. Finche' i due combaciano, tutto
bene; quando divergono, il bot prende decisioni su un mondo che non esiste. In
paper la divergenza e' impossibile per costruzione (nessun exchange), ma coi
soldi veri e' la modalita' di fallimento piu' pericolosa che ci sia: silenziosa,
e ti accorgi solo dal saldo.

Cinque divergenze e cosa fare di ognuna:

  1. POSIZIONE SENZA PROTEZIONE — l'entry e' passata, lo stop no. E' la peggiore:
     una posizione con leva e senza stop puo' perdere senza limite. Si chiude
     subito a mercato, l'uscita costa meno del rischio.
  2. POSIZIONE FANTASMA — il bot crede di averla, Binance dice zero. Chiusa
     altrove (liquidazione, intervento manuale, ordine scaduto). Si riallinea lo
     stato interno e si mette la coin in quarantena: riaprire subito su qualcosa
     che non capiamo e' come minimo prematuro.
  3. ORDINE DUPLICATO — due ordini vivi sulla stessa posizione. Uno va cancellato,
     ma la CAUSA e' un retry andato a buon fine due volte: finche' non e' chiara
     non si apre altro.
  4. EXCHANGE IRRAGGIUNGIBILE — NON si tenta di chiudere. Senza risposte
     affidabili una chiusura al buio puo' duplicare posizioni o fallire a meta':
     si aspetta, si continua a verificare e si avvisa.
  5. SALDO DISCORDANTE — se il saldo reale e' sotto quello atteso oltre la
     tolleranza, qualcosa e' successo fuori dalla nostra contabilita'. Stop
     totale: qualunque altra azione poggerebbe su numeri sbagliati.

PERCHE' RILEVAZIONE E AZIONE SONO SEPARATE. La rilevazione gira in un thread suo
(deve funzionare anche se il loop principale e' bloccato — e' proprio quando
serve di piu'). Le AZIONI che toccano le posizioni no: mutarle da un thread
mentre il loop le itera introdurrebbe una race condition, cioe' un secondo modo
di divergere dalla realta' proprio nel componente che deve impedirlo. Il thread
rileva, pubblica e avvisa; il loop principale applica al tick successivo.
"""
from __future__ import annotations

import threading
import time
from dataclasses import dataclass, field
from typing import Callable, Optional

from bot.config import settings

# tipi di evento (stringhe stabili: finiscono su Firebase e nei log)
MISSING_SL = "missing_sl_tp"
GHOST = "ghost_position"
DUPLICATE = "duplicate_order"
EXCHANGE_DOWN = "exchange_down"
BALANCE_MISMATCH = "balance_mismatch"

# azioni che il loop principale dovra' applicare
CLOSE_NOW = "emergency_close_symbol"
DROP_LOCAL = "drop_local_state"
CANCEL_ORDER = "cancel_order"
WAIT = "wait"
HALT = "halt"


@dataclass
class ExchangeState:
    """Fotografia dell'exchange. `reachable=False` significa "non lo so", che e'
    diverso da "e' vuoto": confonderli farebbe chiudere posizioni sane a ogni
    problema di rete."""
    reachable: bool = True
    positions: dict[str, float] = field(default_factory=dict)      # symbol -> qty
    protective_orders: dict[str, int] = field(default_factory=dict)  # symbol -> quanti SL/TP
    duplicate_orders: dict[str, list] = field(default_factory=dict)  # symbol -> order id
    balance: Optional[float] = None


@dataclass
class Finding:
    event: str
    action: str
    symbol: Optional[str] = None
    detail: dict = field(default_factory=dict)
    critical: bool = False

    def as_dict(self) -> dict:
        return {"event": self.event, "action": self.action, "symbol": self.symbol,
                "detail": self.detail, "critical": self.critical}


def reconcile(internal: dict[str, float], internal_balance: Optional[float],
              ex: ExchangeState) -> list[Finding]:
    """Confronta stato interno ed exchange. Funzione PURA: nessun effetto, nessuna
    chiamata di rete — cosi' ognuno dei cinque scenari e' verificabile a tavolino.

    `internal`: symbol -> quantita' che il bot crede di avere (sempre > 0).
    """
    out: list[Finding] = []

    if not ex.reachable:
        # NON si chiude nulla: senza risposte affidabili una chiusura al buio puo'
        # duplicare posizioni o fallire a meta'. Si aspetta e si avvisa.
        if internal:
            out.append(Finding(EXCHANGE_DOWN, WAIT,
                               detail={"open_positions": sorted(internal)},
                               critical=False))
        return out

    for sym, qty in internal.items():
        real = float(ex.positions.get(sym, 0.0) or 0.0)
        if abs(real) < settings.RECONCILE_QTY_TOLERANCE:
            # il bot crede di avere una posizione che sull'exchange non esiste
            out.append(Finding(GHOST, DROP_LOCAL, sym,
                               {"internal_qty": qty, "exchange_qty": real}, True))
            continue
        if ex.protective_orders.get(sym, 0) <= 0:
            # posizione VIVA e senza stop: e' la divergenza piu' pericolosa
            out.append(Finding(MISSING_SL, CLOSE_NOW, sym,
                               {"exchange_qty": real}, True))
        dups = ex.duplicate_orders.get(sym) or []
        if len(dups) > 1:
            out.append(Finding(DUPLICATE, CANCEL_ORDER, sym, {"order_ids": dups}, True))

    # posizioni sull'exchange che il bot non conosce: non le tocca (potrebbero
    # essere di un altro processo o manuali), ma vanno segnalate — operare senza
    # sapere cosa c'e' aperto significa sbagliare il rischio di portafoglio.
    for sym, qty in ex.positions.items():
        if abs(float(qty or 0.0)) >= settings.RECONCILE_QTY_TOLERANCE and sym not in internal:
            out.append(Finding(GHOST, WAIT, sym,
                               {"internal_qty": 0.0, "exchange_qty": qty,
                                "note": "posizione sconosciuta al bot"}, True))

    if (ex.balance is not None and internal_balance is not None
            and internal_balance > 0):
        gap = (internal_balance - ex.balance) / internal_balance
        if gap > settings.RECONCILE_BALANCE_TOLERANCE:
            out.append(Finding(BALANCE_MISMATCH, HALT, None,
                               {"internal": internal_balance, "exchange": ex.balance,
                                "gap_pct": round(gap * 100, 3)}, True))
    return out


def blocks_trading(findings: list[Finding]) -> bool:
    """True se una qualunque divergenza critica impone di non aprire altro.

    Volutamente grossolano: davanti a uno stato incerto si smette di aggiungere
    rischio, e si riprende solo dopo un reset esplicito. Un blocco per eccesso
    costa qualche trade mancato; uno per difetto costa il conto.
    """
    return any(f.critical for f in findings)


class Reconciler:
    """Thread di sola RILEVAZIONE: confronta, pubblica, avvisa. Non tocca posizioni.

    Inerte in DRY_RUN, dove non esiste uno stato d'exchange da confrontare: farlo
    girare produrrebbe solo falsi allarmi.
    """

    def __init__(self, fetch: Callable[[], ExchangeState],
                 snapshot: Callable[[], tuple[dict, Optional[float]]],
                 notifier=None, firebase=None, interval_s: Optional[float] = None) -> None:
        self.fetch = fetch
        self.snapshot = snapshot
        self.notifier = notifier
        self.fb = firebase
        self.interval = interval_s or settings.RECONCILE_INTERVAL_SECONDS
        self.findings: list[Finding] = []
        self._stop = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._down_since: Optional[float] = None
        self._last_alert: float = 0.0

    # ---------------------------------------------------------------- #
    def check_once(self, now: Optional[float] = None) -> list[Finding]:
        now = time.time() if now is None else now
        # PRIMA lo stato interno, che e' locale e non puo' fallire per la rete: se
        # lo si perdesse insieme alla lettura dell'exchange, "non riesco a leggere
        # Binance mentre ho tre posizioni aperte" diventerebbe indistinguibile da
        # "va tutto bene" — il silenzio piu' pericoloso possibile.
        try:
            internal, balance = self.snapshot()
        except Exception as exc:  # noqa: BLE001
            print(f"[reconciler] stato interno illeggibile ({exc})")
            internal, balance = {}, None
        try:
            ex = self.fetch()
        except Exception as exc:  # noqa: BLE001
            print(f"[reconciler] exchange non raggiungibile ({exc})")
            ex = ExchangeState(reachable=False)
        findings = reconcile(internal, balance, ex)
        self.findings = findings

        # durata del downtime: serve a distinguere un blip di rete da un problema
        if any(f.event == EXCHANGE_DOWN for f in findings):
            self._down_since = self._down_since or now
        else:
            self._down_since = None

        self._publish(findings, now)
        self._alert(findings, now)
        return findings

    def _publish(self, findings: list[Finding], now: float) -> None:
        if self.fb is None:
            return
        try:
            self.fb.set_rtdb("/reconciliation", {
                "checked_at": now,
                "error": blocks_trading(findings),
                "down_since": self._down_since,
                "findings": [f.as_dict() for f in findings],
            })
        except Exception as exc:  # noqa: BLE001
            print(f"[reconciler] pubblicazione fallita ({exc})")

    def _alert(self, findings: list[Finding], now: float) -> None:
        """Avvisa, ma senza inondare: un problema che dura ore non deve produrre un
        messaggio ogni minuto, o si smette di leggerli — che e' il modo piu' comune
        di rendere inutile un sistema di allarme."""
        if not findings or self.notifier is None:
            return
        if now - self._last_alert < settings.RECONCILE_ALERT_COOLDOWN_S:
            return
        self._last_alert = now
        lines = ["⚠️ <b>RICONCILIAZIONE</b>"]
        for f in findings[:8]:
            lines.append(f"• {f.event}{' ' + f.symbol if f.symbol else ''} → {f.action}")
        if blocks_trading(findings):
            lines.append("Nuove posizioni BLOCCATE fino al reset dalla dashboard.")
        try:
            self.notifier.send("\n".join(lines))
        except Exception:  # noqa: BLE001
            pass

    # ---------------------------------------------------------------- #
    def start(self) -> bool:
        """Avvia il thread. Ritorna False (e non fa nulla) in DRY_RUN."""
        if settings.DRY_RUN or not settings.RECONCILE_ENABLED:
            return False
        if self._thread and self._thread.is_alive():
            return True
        self._stop.clear()
        self._thread = threading.Thread(target=self._loop, name="reconciler", daemon=True)
        self._thread.start()
        return True

    def stop(self) -> None:
        self._stop.set()

    def _loop(self) -> None:
        while not self._stop.is_set():
            self.check_once()
            self._stop.wait(self.interval)
