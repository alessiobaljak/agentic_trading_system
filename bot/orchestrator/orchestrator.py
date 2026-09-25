"""
Orchestratore — chiamato ad ogni candela 15m chiusa.

Flusso:
  1. Raccoglie i segnali delle strategie ATTIVE nel regime corrente.
  2. Costruisce l'input strutturato (prompt.py) con il memory_report.
  3. Chiama Claude e valida l'output con Pydantic (OrchestratorDecision).
  4. ADATTAMENTO: moltiplica la confidenza per il peso strategia×regime
     (dal learning loop). Strategie con peso 0 vengono di fatto disattivate.

Fallback senza API: se ANTHROPIC_API_KEY non è impostata, usa un ensemble
deterministico dei segnali pesati dal learning (così il paper trading gira
senza spesa LLM). Il comportamento è documentato in docs/orchestrator.md.
"""
from __future__ import annotations

import json
import time
from typing import Optional

from bot.agents.regime_detector import RegimeDetector
from bot.config import settings
from bot.core.models import (
    AssetSnapshot, Direction, MemoryReport, OrchestratorDecision, Regime,
)
from bot.learning.adaptation import AdaptationEngine
from bot.orchestrator.prompt import SYSTEM_PROMPT, build_user_message
from bot.strategies import get_all_strategies
from bot.strategies.base import StrategyContext


#: secondi per timeframe, per l'orologio delle strategie native a 1 ora
_TF_SECS = {"1m": 60, "5m": 300, "15m": 900, "30m": 1800, "1h": 3600, "4h": 14400, "1d": 86400}

#: I MOTIVI dei rifiuti, normalizzati (25 set 2026, docs/controllo_schema.md §3.5).
#: Le righe «[rifiuto]» restano com'erano nel log; qui si CONTANO per motivo,
#: per ciclo e nelle ultime 24 ore, e i conteggi vanno in /decision_status. Sono
#: le prime parole della riga, ridotte a nove classi: cosi' il controllo orario
#: puo' dire «12 cooldown, 3 margine» senza leggere il journal.
#: «esplorative al tetto» (25 set 2026, F1bis) e' il rifiuto di un segnale
#: esplorativo quando ESPLORATIVE_MAX_APERTE posizioni esplorative sono gia'
#: aperte: contato a parte, cosi' si vede quante volte il tetto ha morso.
MOTIVI_RIFIUTO = ("cooldown", "tetto per coin", "peso sotto soglia", "strategia spenta",
                  "veto di regime", "margine", "rischio direzionale", "stop troppo largo",
                  "esplorative al tetto", "altro")


def motivo_rifiuto(testo: str) -> str:
    """La classe di un motivo di rifiuto, dalle sue prime parole. Pura."""
    t = str(testo or "").lower()
    if "cooldown" in t:
        return "cooldown"
    if "tetto per coin" in t:
        return "tetto per coin"
    if "spenta" in t:
        return "strategia spenta"
    if "peso" in t:
        return "peso sotto soglia"
    if "veto di regime" in t:
        return "veto di regime"
    if "margine" in t:
        return "margine"
    if "rischio direzionale" in t:
        return "rischio direzionale"
    if "stop troppo largo" in t:
        return "stop troppo largo"
    if "esplorative al tetto" in t:
        return "esplorative al tetto"
    return "altro"


class Orchestrator:
    DECISION_THRESHOLD = 30  # confidenza aggiustata minima per agire (fallback)

    def __init__(self, adaptation: Optional[AdaptationEngine] = None) -> None:
        self.adaptation = adaptation or AdaptationEngine()
        self.strategies = get_all_strategies()
        # per il regime PER-COIN in parita' col backtest (stesso detector del bt)
        self.regime_detector = RegimeDetector()
        # esito dell'ULTIMA decisione (osservabilità): pubblicato su Firebase da main
        self.last_status: dict = {}
        # I RIFIUTI del ciclo (25 set 2026, backlog H5): i segnali scartati QUI
        # (peso sotto soglia, veto di regime) non arrivavano mai a main, quindi
        # ne' al log ne' a /decision_status: da fuori non si potevano contare.
        # Si accumulano per ciclo e si stampano in blocco (max _MAX_RIFIUTI_LOG
        # righe), una riga per (coin, strategia).
        self._rifiuti_ciclo: list[str] = []
        self._rifiuti_visti: set = set()
        # I CONTEGGI dei rifiuti per motivo (25 set 2026, contratto §3.5): del
        # ciclo in corso e della finestra scorrevole di 24 ore. Vivono in RAM e
        # si azzerano al riavvio: `rifiuti_24h_dal` dice da quando conta, cosi'
        # il lettore non scambia «2 rifiuti» dopo un riavvio per una giornata
        # calma. Ci passano anche gli scarti di `TradingBot._try_open`
        # (`conta_scarto`), cosi' il contatore e' uno solo.
        self._rifiuti_conteggio: dict[str, int] = {}
        self._rifiuti_24h_lista: list[tuple[float, str]] = []
        self.rifiuti_24h_dal: float = time.time()

    #: righe «[rifiuto]» stampate per ciclo; oltre, una riga «... e altri N».
    #: Con 160 coppie un regime sfavorevole puo' scartarne decine a ogni candela:
    #: senza tetto il log del bot diventerebbe illeggibile.
    _MAX_RIFIUTI_LOG = 20

    def conta_scarto(self, motivo: str, now: float | None = None) -> None:
        """Conta un rifiuto (per motivo normalizzato) nel ciclo e nelle 24 ore.
        Non stampa: la riga «[rifiuto]» la scrive chi rifiuta."""
        classe = motivo_rifiuto(motivo)
        self._rifiuti_conteggio[classe] = self._rifiuti_conteggio.get(classe, 0) + 1
        self._rifiuti_24h_lista.append((time.time() if now is None else now, classe))

    def nuovo_ciclo(self) -> None:
        """Azzera i conteggi del ciclo: da chiamare all'inizio di ogni decisione."""
        self._rifiuti_conteggio = {}

    def rifiuti_ciclo(self) -> list[dict]:
        """[{motivo, n}] del ciclo in corso, dal piu' frequente."""
        return [{"motivo": m, "n": n} for m, n in
                sorted(self._rifiuti_conteggio.items(), key=lambda kv: (-kv[1], kv[0]))]

    def rifiuti_24h(self, now: float | None = None) -> list[dict]:
        """[{motivo, n}] delle ultime 24 ore (finestra scorrevole in RAM)."""
        now = time.time() if now is None else now
        self._rifiuti_24h_lista = [(t, m) for t, m in self._rifiuti_24h_lista if now - t <= 86400]
        conta: dict[str, int] = {}
        for _t, m in self._rifiuti_24h_lista:
            conta[m] = conta.get(m, 0) + 1
        return [{"motivo": m, "n": n} for m, n in sorted(conta.items(), key=lambda kv: (-kv[1], kv[0]))]

    def _rifiuto(self, symbol: str, strategy: str, motivo: str) -> None:
        """Registra un rifiuto del ciclo (una riga per coppia, stampa a fine ciclo)."""
        key = (symbol, strategy)
        if key in self._rifiuti_visti:
            return
        self._rifiuti_visti.add(key)
        self._rifiuti_ciclo.append(f"[rifiuto] {symbol} {strategy}: {motivo}")
        self.conta_scarto(motivo)

    def _stampa_rifiuti(self) -> None:
        """Stampa i rifiuti accumulati (prime _MAX_RIFIUTI_LOG righe, poi il conto)
        e svuota l'accumulo, cosi' il ciclo dopo riparte da zero."""
        righe = self._rifiuti_ciclo
        for r in righe[:self._MAX_RIFIUTI_LOG]:
            print(r)
        if len(righe) > self._MAX_RIFIUTI_LOG:
            print(f"[rifiuto] ... e altri {len(righe) - self._MAX_RIFIUTI_LOG}")
        self._rifiuti_ciclo = []
        self._rifiuti_visti = set()

    def _record_status(self, regime: Regime, n_assets: int, signals: list[dict],
                       outcome: str, reason: str,
                       decision: Optional[OrchestratorDecision] = None) -> None:
        best = signals[0] if signals else None
        self.last_status = {
            "ts": time.time(),
            "regime": regime.value,
            "assets_evaluated": n_assets,
            "signals_found": len(signals),
            "best_symbol": best["symbol"] if best else None,
            "best_strategy": best["strategy"] if best else None,
            "best_confidence": round(float(best["confidence"]), 1) if best else None,
            "best_adjusted": round(float(best["adjusted_confidence"]), 1) if best else None,
            "threshold": self.DECISION_THRESHOLD,
            "outcome": outcome,            # "flat" | "decided"
            "reason": reason,
            "chosen_asset": decision.asset if decision else None,
            "chosen_strategy": decision.strategy if decision else None,
        }

    # ------------------------------------------------------------------ #
    def collect_signals(
        self, assets: dict[str, AssetSnapshot], regime: Regime,
        disabled: Optional[set] = None, boundary: Optional[float] = None,
    ) -> list[dict]:
        """
        Raccoglie i segnali delle strategie attive nel regime corrente.
        Per OGNI asset istanzia le strategie con i PARAMETRI OTTIMIZZATI per quel
        coin (walk-forward) e opera solo le coppie (asset, strategia) che hanno
        passato la validazione out-of-sample. Le strategie in `disabled` (messe in
        panchina dall'adattamento real-time dopo perdite consecutive) sono saltate.
        """
        disabled = disabled or set()
        ctx_global = StrategyContext(all_assets=assets, regime=regime)
        signals = []
        # ciclo nuovo: i rifiuti del giro precedente sono gia' stati stampati
        self._rifiuti_ciclo, self._rifiuti_visti = [], set()
        for sym, asset in assets.items():
            # PARITA' COL BACKTEST: il regime e' rilevato PER-COIN dai dati di quella
            # coin (come engine.run_strategy), non l'unico macro-BTC. Cosi' su ogni
            # coin scattano le stesse strategie del GATE 1. Fuori parita': macro unico.
            if settings.BACKTEST_PARITY:
                coin_regime = self.regime_detector.detect(asset)
                asset.regime = coin_regime
                ctx = StrategyContext(all_assets=assets, regime=coin_regime)
            else:
                coin_regime = regime
                ctx = ctx_global
            params_by_strat = self.adaptation.params_for(sym)
            # strategie base (6) + strategie GENERATE validate per questo asset
            strategies = get_all_strategies(params_by_strat)
            strategies += self.adaptation.generated_strategies_for(sym)
            # + le ESPLORATIVE (25 set 2026, F1bis): i quasi-passaggi scelti dal
            # gate, marcati `esplorativa` sull'oggetto. Vuoto fuori dal paper.
            strategies += self.adaptation.esplorative_for(sym)
            for strat in strategies:
                if strat.name in disabled:
                    continue
                esplorativa = bool(getattr(strat, "esplorativa", False))
                # OGNI STRATEGIA SUL SUO OROLOGIO (22 set 2026, strategie native a
                # 1 ora): una spec a 1h decide UNA volta per candela oraria, non
                # quattro volte come se fosse a 15m — nel backtest e' valutata a
                # ogni sua candela, e la parita' vuole lo stesso dal vivo.
                # `boundary` e' l'apertura della candela del bot appena chiusa:
                # se non cade su una chiusura della candela della strategia, si
                # salta. Senza `boundary` (chiamate legacy) non si filtra.
                if boundary is not None:
                    _tf_s = _TF_SECS.get(getattr(strat, "timeframe", None) or "", 0)
                    if _tf_s and int(boundary) % _tf_s != 0:
                        continue
                if not strat.is_active_in(coin_regime):
                    continue
                # una validata passa da `is_enabled` (registro); un'esplorativa
                # non e' nel registro validato per definizione: passa dal suo
                if esplorativa:
                    if not self.adaptation.is_esplorativa(sym, strat.name):
                        continue
                elif not self.adaptation.is_enabled(sym, strat.name):
                    continue
                # filtro di regime informato dal gate: non si opera una coppia nel
                # regime in cui il gate l'ha vista perdere (fail-open senza dati)
                if not self.adaptation.regime_ok(sym, strat.name, coin_regime):
                    # nel log SOLO se c'era davvero un segnale da scartare: una
                    # coppia vetata che non avrebbe sparato non e' un rifiuto, e
                    # contarla gonfierebbe proprio il numero che H5 vuole. Le
                    # strategie sono senza stato: generarlo qui non cambia nulla.
                    if strat.generate_signal(asset, ctx) is not None:
                        self._rifiuto(sym, strat.name,
                                      f"veto di regime ({coin_regime.value})")
                    continue
                sig = strat.generate_signal(asset, ctx)
                if sig is None:
                    continue
                weight = self.adaptation.weight_for(strat.name, coin_regime)
                signals.append({
                    "strategy": sig.strategy, "symbol": sig.symbol,
                    "direction": sig.direction.value, "confidence": sig.confidence,
                    "adjusted_confidence": sig.confidence * weight,
                    "weight": weight, "reasoning": sig.reasoning,
                    "coin_regime": coin_regime,   # per il tilt di trend (decide_all)
                    # SL/TP della STRATEGIA: stessi del backtest -> il risk manager
                    # li usa invece dei default fissi (parità GATE 1 <-> paper).
                    "suggested_stop": sig.suggested_stop,
                    "suggested_target": sig.suggested_target,
                    # il paper esplorativo (25 set 2026): decide_all da' la
                    # precedenza alle validate e applica il tetto di aperte
                    "esplorativa": esplorativa,
                })
        signals.sort(key=lambda s: s["adjusted_confidence"], reverse=True)
        return signals

    # ------------------------------------------------------------------ #
    def decide(
        self,
        assets: dict[str, AssetSnapshot],
        regime: Regime,
        memory_report: Optional[MemoryReport] = None,
        recent_trades: Optional[list[dict]] = None,
        macro_events: Optional[list[dict]] = None,
        disabled: Optional[set] = None,
    ) -> Optional[OrchestratorDecision]:
        self.nuovo_ciclo()
        signals = self.collect_signals(assets, regime, disabled=disabled)
        # il paper esplorativo vive SOLO in parita' (`decide_all`, un segnale per
        # coin): qui si sceglie il migliore globale e un quasi-passaggio non deve
        # mai vincere sulle validate (25 set 2026, F1bis)
        signals = [s for s in signals if not s.get("esplorativa")]
        self._stampa_rifiuti()          # i veti di regime del giro
        if not signals:
            self._record_status(regime, len(assets), signals, "flat",
                                "nessun segnale dalle strategie attive in questo regime")
            return None

        if settings.ANTHROPIC_API_KEY:
            decision = self._decide_llm(
                list(assets.values()), signals, regime, memory_report,
                recent_trades or [], macro_events,
            )
        else:
            decision = self._decide_fallback(signals)

        if decision is None:
            best_adj = signals[0]["adjusted_confidence"]
            self._record_status(
                regime, len(assets), signals, "flat",
                f"miglior segnale {best_adj:.0f} sotto soglia {self.DECISION_THRESHOLD} "
                "(o LLM ha scelto flat)")
            return None

        # --- adattamento: aggiusta la confidenza col peso del learning ---
        weight = self.adaptation.weight_for(decision.strategy, regime)
        decision.adjusted_confidence = decision.confidence * weight
        # strategia di fatto disattivata in questo regime
        if weight <= 0.0:
            self._record_status(regime, len(assets), signals, "flat",
                                f"{decision.strategy} disattivata dal learning (peso 0)")
            return None
        self._record_status(regime, len(assets), signals, "decided",
                            "segnale valido sopra soglia", decision)
        return decision

    # ------------------------------------------------------------------ #
    @staticmethod
    def _trend_align(regime: Optional[Regime], direction: str) -> float:
        """+1 se la direzione e' IN TREND, -1 se CONTROtrend, 0 se regime neutro
        (sideways/incertezza). Usato per il tilt di size sul trend."""
        if regime == Regime.BULL_TRENDING:
            return 1.0 if direction == Direction.LONG.value else -1.0
        if regime == Regime.BEAR_TRENDING:
            return 1.0 if direction == Direction.SHORT.value else -1.0
        return 0.0

    # ------------------------------------------------------------------ #
    def decide_all(
        self, assets: dict[str, AssetSnapshot], regime: Regime,
        disabled: Optional[set] = None, boundary: Optional[float] = None,
        esplorative_aperte: int = 0,
    ) -> list[OrchestratorDecision]:
        """PARITA' COL BACKTEST: ritorna UNA decisione per OGNI coin con un segnale
        valido (sopra soglia, peso>0), prendendo la strategia migliore per quella
        coin. Niente LLM, niente 'scegli il migliore globale': come il backtest che
        apre ogni segnale indipendentemente. Vincolo conto reale: 1 posizione/coin.

        IL PAPER ESPLORATIVO (25 set 2026, F1bis), due regole sole:
          (a) una VALIDATA vince sempre: se sulla coin una strategia validata ha
              prodotto un segnale, i segnali esplorativi di quella coin cadono
              (anche se il segnale validato viene poi rifiutato per peso);
          (b) al massimo ESPLORATIVE_MAX_APERTE posizioni esplorative aperte
              insieme: `esplorative_aperte` sono quelle gia' aperte (le passa
              main), le decisioni di questo ciclo si sommano; oltre, rifiuto
              «esplorative al tetto», contato come gli altri."""
        self.nuovo_ciclo()
        signals = self.collect_signals(assets, regime, disabled=disabled, boundary=boundary)
        decisions: list[OrchestratorDecision] = []
        seen: set = set()
        coin_con_validata = {s["symbol"] for s in signals if not s.get("esplorativa")}
        n_esplorative = int(esplorative_aperte or 0)
        for s in signals:  # ordinati per adjusted_confidence desc
            if s.get("esplorativa") and s["symbol"] in coin_con_validata:
                continue        # regola (a): la validata ha la precedenza, senza rifiuto
            if s["weight"] <= 0.0:
                self._rifiuto(s["symbol"], s["strategy"],
                              f"peso {s['weight']:.2f} (strategia spenta dal learning)")
                continue
            if s["adjusted_confidence"] < self.DECISION_THRESHOLD:
                self._rifiuto(s["symbol"], s["strategy"],
                              f"peso {s['weight']:.2f}: confidenza "
                              f"{s['adjusted_confidence']:.0f} < soglia "
                              f"{self.DECISION_THRESHOLD}")
                continue
            if s["symbol"] in seen:
                continue
            if s.get("esplorativa"):
                if n_esplorative >= settings.ESPLORATIVE_MAX_APERTE:
                    self._rifiuto(s["symbol"], s["strategy"],
                                  f"esplorative al tetto ({settings.ESPLORATIVE_MAX_APERTE} aperte)")
                    continue    # regola (b)
                n_esplorative += 1
            seen.add(s["symbol"])
            # TREND come contesto: modula la SIZE (non un veto). Il controtrend
            # (rispetto a trend della coin 60% + mercato 40%) apre piu' piccolo;
            # in-trend resta pieno. size_multiplier<=1 -> puo' solo ridurre.
            size_mult = 1.0
            if settings.TREND_TILT_ENABLED:
                align = (0.6 * self._trend_align(s.get("coin_regime"), s["direction"])
                         + 0.4 * self._trend_align(regime, s["direction"]))
                size_mult = max(settings.TREND_TILT_FLOOR,
                                1.0 + settings.TREND_TILT_STRENGTH * min(0.0, align))
            d = OrchestratorDecision(
                asset=s["symbol"], strategy=s["strategy"],
                direction=Direction(s["direction"]), size_multiplier=size_mult,
                confidence=s["confidence"], reasoning=s.get("reasoning", ""),
                suggested_stop=s.get("suggested_stop"),
                suggested_target=s.get("suggested_target"),
                esplorativa=bool(s.get("esplorativa")))
            d.adjusted_confidence = s["adjusted_confidence"]
            decisions.append(d)
        self._stampa_rifiuti()
        self._record_status(
            regime, len(assets), signals, "decided" if decisions else "flat",
            f"parita' backtest: {len(decisions)} segnali validi aperti" if decisions
            else "nessun segnale valido sopra soglia",
            decisions[0] if decisions else None)
        return decisions

    # ------------------------------------------------------------------ #
    def _decide_llm(
        self, assets, signals, regime, memory_report, recent_trades, macro_events
    ) -> Optional[OrchestratorDecision]:
        try:
            import anthropic

            from bot.ai.client import _headers
            client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY,
                                         default_headers=_headers())
            user_msg = build_user_message(
                assets, signals, regime, memory_report, recent_trades, macro_events
            )
            resp = client.messages.create(
                model=settings.ANTHROPIC_MODEL,
                max_tokens=600,
                system=SYSTEM_PROMPT,
                messages=[{"role": "user", "content": user_msg}],
            )
            text = resp.content[0].text.strip()
            start, end = text.find("{"), text.rfind("}")
            data = json.loads(text[start:end + 1])
            if float(data.get("size_multiplier", 0)) <= 0:
                return None  # l'LLM ha scelto di stare flat
            return OrchestratorDecision(**{
                "asset": data["asset"], "strategy": data["strategy"],
                "direction": Direction(data["direction"]),
                "size_multiplier": float(data["size_multiplier"]),
                "confidence": float(data["confidence"]),
                "reasoning": data.get("reasoning", ""),
            })
        except Exception as exc:  # noqa: BLE001
            print(f"[orchestrator] LLM fallito ({exc}) -> fallback deterministico")
            return self._decide_fallback(signals)

    def _decide_fallback(self, signals: list[dict]) -> Optional[OrchestratorDecision]:
        """Ensemble deterministico: prende il segnale con confidenza aggiustata massima."""
        best = signals[0]
        if best["adjusted_confidence"] < 30:   # soglia minima per agire
            return None
        # size proporzionale alla confidenza aggiustata (0..1)
        size_mult = max(0.0, min(1.0, best["adjusted_confidence"] / 100.0))
        return OrchestratorDecision(
            asset=best["symbol"], strategy=best["strategy"],
            direction=Direction(best["direction"]),
            size_multiplier=size_mult, confidence=best["confidence"],
            reasoning=f"[fallback] {best['reasoning']} (peso={best['weight']:.2f})",
            suggested_stop=best.get("suggested_stop"),
            suggested_target=best.get("suggested_target"),
        )
