"""
AdaptationEngine — applica i pesi appresi alle decisioni dell'orchestratore.

Meccanismo concreto (come da specifica):
  * I pesi strategia×regime sono su Firebase (strategy_weights/current),
    aggiornati ogni notte dal learning loop.
  * L'orchestratore moltiplica la propria confidenza per il peso della strategia
    nel regime corrente.
  * Strategie che performano male -> peso -> 0 (progressivamente disattivate).
  * Strategie che performano bene -> peso alto -> più capitale.

ANTI-OVERFITTING (baseline non adattata):
  * Una frazione fissa del capitale (config.BASELINE_CAPITAL_FRACTION, 20%) usa
    SEMPRE peso 1.0 per ogni strategia (configurazione baseline). Questo evita il
    collasso su pattern passati. Il metodo `is_baseline_cycle()` indica quando un
    ciclo va trattato come baseline.
"""
from __future__ import annotations

import random
import time
from typing import Optional

from bot.config import settings
from bot.core.firebase_client import decode_pairs, get_firebase
from bot.core.models import Regime, StrategyRegimeWeight


class AdaptationEngine:
    def __init__(self, firebase=None) -> None:
        self.fb = firebase or get_firebase()
        self._weights: dict[str, float] = {}   # chiave "strategy|regime" -> peso
        self._params: dict[str, dict] = {}     # chiave "SYMBOL|strategy" -> params ottimizzati
        self._passed: set[str] = set()         # coppie "SYMBOL|strategy" che hanno passato OOS
        # PF per-regime dal gate: "SYMBOL|strategy" -> {regime: {"pf", "trades"}}.
        # Alimenta il filtro di regime (non operare dove il gate ha visto perdere).
        self._regime_pf: dict[str, dict] = {}
        # verdetti di deriva (paper vs promessa del gate): frenano size/leva SUBITO,
        # senza aspettare che il gate rivaluti. Ricaricato col registro.
        self._drift: dict = {}
        # calibrazione: quanto la confidenza dei segnali predica davvero l'esito
        self._calibration: dict = {}
        self._has_opt_data: bool = False
        self._generated_specs: dict[str, dict] = {}  # gen_id -> spec (strategie scoperte)
        self.load_weights()
        self.load_params()
        self.load_generated()

    # ------------------------------------------------------------------ #
    def load_weights(self) -> None:
        doc = self.fb.get_doc("strategy_weights", "current") or {}
        self._weights = {}
        for w in doc.get("weights", []):
            key = f"{w['strategy']}|{w['regime']}"
            self._weights[key] = float(w.get("weight", 1.0))

    def save_weights(self, weights: list[StrategyRegimeWeight]) -> None:
        """Salva i pesi ricalcolati + RIENTRO IN PROVA (probation) dei gruppi senza
        trade recenti.

        Senza questo, un gruppo strategia×regime ucciso (peso 0) smette di tradare,
        i suoi trade escono dalla finestra 30g, il gruppo sparisce dal documento e
        weight_for torna al default 1.0: resurrezione DI COLPO a fiducia piena
        ("kill con amnesia"), che costa ~4 perdite piene a ogni giro. Qui invece il
        peso di un gruppo assente dal ricalcolo viene TRASCINATO e recupera
        gradualmente verso 1.0 (WEIGHT_RECOVERY_DAYS): la strategia rientra prima
        coi soli segnali FORTI (peso 0.5 passa la soglia solo a confidence alta),
        e si riabilita del tutto solo col tempo o vincendo. A 1.0 il gruppo viene
        potato (equivale al default). Il merge sta QUI cosi' copre entrambi gli
        scrittori (refresh orario del bot e job notturno)."""
        now = time.time()
        doc = self.fb.get_doc("strategy_weights", "current") or {}
        prev_ts = float(doc.get("updated_at", 0) or 0)
        elapsed_days = max(0.0, (now - prev_ts) / 86400.0) if prev_ts else 0.0
        recovery = max(1e-9, settings.WEIGHT_RECOVERY_DAYS)
        fresh = {(w.strategy, w.regime.value) for w in weights}
        carried: list[StrategyRegimeWeight] = []
        for e in doc.get("weights", []) or []:
            key = (e.get("strategy"), e.get("regime"))
            if key in fresh or not key[0] or not key[1]:
                continue
            w_new = min(1.0, float(e.get("weight", 1.0) or 0.0) + elapsed_days / recovery)
            if w_new >= 1.0:
                continue   # riabilitata: indistinguibile dal default -> pota
            try:
                carried.append(StrategyRegimeWeight(
                    strategy=key[0], regime=Regime(key[1]), weight=round(w_new, 4),
                    win_rate=None, avg_rr=None, sample_size=0))   # 0 = "in prova"
            except ValueError:
                continue   # regime non piu' valido
        self.fb.set_doc("strategy_weights", "current", {
            "weights": [w.model_dump(mode="json") for w in list(weights) + carried],
            "updated_at": now,
        })
        self.load_weights()

    # ------------------------------------------------------------------ #
    def allocation(self, strategy: str, regime: Regime, confidence: float,
                   drift_key: tuple[str, str] | None = None) -> tuple[float, float, str]:
        """(risk_mult, lev_mult, nota): quanto CAPITALE e quanta LEVA merita questo
        trade, guidato SOLO dai dati — mai oltre i cap di sicurezza (applicati poi
        dal risk manager, che puo' solo ridurre).

          * CONVINZIONE: la confidence del segnale (forza degli indicatori, scala
            0-100 validata dal gate). 30 (soglia minima) -> x0.75; 85+ -> x1.25.
          * APPRENDIMENTO: il peso strategia×regime imparato dai trade REALI.
            Nessun peso nel documento (= nessun dato) -> x1.0 NEUTRO: senza dati
            non si devia dal comportamento base, ne' in su ne' in giu'. Col peso:
            0 -> x0.5 (il kill avviene comunque a monte), 1 -> x1.25.

        La leva scala con la RADICE del fattore (piu' cauta della size): amplifica
        sia i guadagni sia le perdite, quindi si muove meno."""
        key = f"{strategy}|{regime.value}"
        w = self._weights.get(key)
        conf = max(0.0, min(1.0, (float(confidence or 0) - 30.0) / 55.0))
        conf_mult = 0.75 + 0.5 * conf
        # CALIBRAZIONE: se la confidenza non predice l'esito, la sua influenza si
        # restringe verso il neutro (1.0). Con trust=0 la size smette di dipendere
        # da un numero che non significa nulla.
        from bot.learning.calibration import confidence_trust
        _trust = confidence_trust(self._calibration)
        if _trust < 1.0:
            conf_mult = 1.0 + (conf_mult - 1.0) * _trust
        learn_mult = 1.0 if w is None else 0.5 + 0.75 * float(w)
        raw = conf_mult * learn_mult
        risk_mult = max(0.5, min(1.5, raw))
        lev_mult = max(0.7, min(1.3, raw ** 0.5))
        note = (f"alloc: convinzione x{conf_mult:.2f}"
                f"{' (calibr. x%.2f)' % _trust if _trust < 1.0 else ''} · learning "
                f"{'x%.2f' % learn_mult if w is not None else 'neutro (nessun dato)'}")
        # DERIVA: se il vissuto contraddice la promessa del gate si frena SUBITO,
        # senza attendere la rivalidazione. Applicato DOPO i cap: e' una riduzione,
        # non puo' mai aumentare l'esposizione.
        if drift_key is not None:
            from bot.learning.drift import weight_factor
            f = weight_factor(self._drift, drift_key[0], drift_key[1])
            if f < 1.0:
                risk_mult *= f
                lev_mult = max(0.5, lev_mult * (f ** 0.5))
                note += f" · DERIVA x{f:.2f}"
        return risk_mult, lev_mult, note

    # ------------------------------------------------------------------ #
    def weight_for(self, strategy: str, regime: Regime, baseline: bool = False) -> float:
        """
        Peso della strategia nel regime. Se `baseline` True (sleeve baseline),
        ritorna sempre 1.0 (configurazione non adattata).
        Default 1.0 quando non ci sono ancora dati di apprendimento.
        """
        if baseline:
            return 1.0
        return self._weights.get(f"{strategy}|{regime.value}", 1.0)

    # ------------------------------------------------------------------ #
    # Parametri ottimizzati per-asset (walk-forward, job autonomo)        #
    # ------------------------------------------------------------------ #
    @staticmethod
    def _robust_only(keys) -> set:
        """Tiene le coppie 'SYMBOL|strategia' robuste. Le strategie BASE devono essere
        passate su >= MIN_COINS_PER_STRATEGY coin distinte (anti-fluke a coin singola).
        Le strategie GENERATE (gen_*) sono coin-specifiche BY DESIGN — scoperte su una
        coin e validate dai loro passaggi OOS — quindi ESENTATE dalla regola cross-coin
        (altrimenti verrebbero scartate tutte). Soglia <= 1 -> nessun filtro."""
        keys = [k for k in keys if "|" in k]
        n = settings.MIN_COINS_PER_STRATEGY
        if n <= 1:
            return set(keys)
        generated = {k for k in keys if k.split("|", 1)[1].startswith("gen_")}
        coins_per_strat: dict[str, set] = {}
        for k in keys:
            sym, strat = k.split("|", 1)
            if not strat.startswith("gen_"):
                coins_per_strat.setdefault(strat, set()).add(sym)
        robust = {s for s, c in coins_per_strat.items() if len(c) >= n}
        return generated | {k for k in keys if k.split("|", 1)[1] in robust}

    def load_params(self) -> None:
        # deriva: si carica sempre, anche quando il registro non e' pronto
        try:
            self._drift = self.fb.get_doc("drift", "current") or {}
        except Exception:  # noqa: BLE001
            self._drift = {}
        try:
            self._calibration = self.fb.get_doc("calibration", "current") or {}
        except Exception:  # noqa: BLE001
            self._calibration = {}
        reg = self.fb.get_doc("strategy_registry", "validated") or {}
        validated = reg.get("validated") or []
        pairs = decode_pairs(reg.get("pairs"))
        # GATE 0) il bot NON va in paper finche' il GATE 1 non e' "ready" (copertura
        # dell'universo >= soglia). Resta FLAT anche se qualche coppia e' gia'
        # validata: e' cio' che promette il Telegram ("GATE 1 SUPERATO -> paper").
        if settings.REQUIRE_GATE1_READY and not reg.get("ready"):
            self._passed = set()
            self._params = {}
            self._has_opt_data = True
            return
        # 1) REGISTRO validato: coppie a >= MIN_PASSES passaggi OOS (le piu' robuste).
        if validated:
            self._passed = self._robust_only(validated)
            self._params = {k: (pairs.get(k, {}).get("last_params", {}) or {}) for k in self._passed}
            self._regime_pf = {k: (pairs.get(k, {}).get("regime_pf", {}) or {}) for k in self._passed}
            self._has_opt_data = True
            return
        # Nessuna coppia a MIN_PASSES passaggi. DEFAULT: il bot resta FLAT — NON si
        # trada su strategie non validate (e' il senso stesso del GATE 1). Solo se
        # BOOTSTRAP_TRADE_UNVALIDATED e' attivo si opera il paper sulle coppie a
        # >= 1 passaggio, per accumulare dati prima della validazione completa.
        if not settings.BOOTSTRAP_TRADE_UNVALIDATED:
            self._passed = set()
            self._params = {}
            self._has_opt_data = True    # dati presenti: solo, nulla e' ancora validato
            return
        # 2) BOOTSTRAP (opt-in): coppie con >= 1 passaggio nel registro (base +
        # generate del run recente). `pairs` e' gia' decodificato.
        recent = {k: r for k, r in pairs.items() if r.get("pass_count", 0) >= 1}
        if recent:
            self._passed = self._robust_only(recent.keys())
            self._params = {k: (recent.get(k, {}).get("last_params", {}) or {}) for k in self._passed}
            self._has_opt_data = True
            return
        # 3) ultima spiaggia: l'ultimo run (strategy_params/current). entries/passed
        # sono CODIFICATI (stringa JSON) -> decode_pairs (retro-compatibile col dict).
        doc = self.fb.get_doc("strategy_params", "current") or {}
        entries = decode_pairs(doc.get("entries"))
        self._passed = self._robust_only(decode_pairs(doc.get("passed")) or [])
        self._params = {k: (entries.get(k, {}).get("params", {}) or {}) for k in self._passed}
        self._has_opt_data = bool(entries)

    def params_for(self, symbol: str) -> dict[str, dict]:
        """{strategy: params} per l'asset (solo coppie ottimizzate)."""
        out: dict[str, dict] = {}
        prefix = f"{symbol}|"
        for key, params in self._params.items():
            if key.startswith(prefix):
                out[key[len(prefix):]] = params
        return out

    def validated_coins(self) -> set[str]:
        """Coin distinte con almeno una coppia validata robusta (GATE 1). È l'universo
        che il bot DEVE valutare a ogni ciclo: sono le uniche coin tradabili, quindi
        lo scan live va allineato a queste (non a un top-N per volume)."""
        return {k.split("|", 1)[0] for k in self._passed}

    # ------------------------------------------------------------------ #
    # Strategie GENERATE (scoperte dal motore di discovery)              #
    # ------------------------------------------------------------------ #
    def load_generated(self) -> None:
        doc = self.fb.get_doc("discovered_strategies", "specs") or {}
        # specs codificate come stringa JSON (limite indici Firestore) -> decode.
        self._generated_specs = decode_pairs(doc.get("specs"))

    def generated_strategies_for(self, symbol: str) -> list:
        """Istanzia le strategie GENERATE che sono validate e abilitate per questo
        asset. Vengono trattate come tutte le altre (gate + pesi del learning)."""
        from bot.strategies.generated import GeneratedStrategy
        out = []
        for gen_id, spec in self._generated_specs.items():
            if self.is_enabled(symbol, gen_id):
                out.append(GeneratedStrategy(spec))
        return out

    def is_enabled(self, symbol: str, strategy: str) -> bool:
        """
        True se la coppia (asset, strategia) è abilitata a operare.
        Quando l'ottimizzazione ha girato, opera SOLO le coppie che hanno passato
        la validazione out-of-sample.
        FAIL-SAFE: se NON ci sono dati di ottimizzazione (registro non caricato:
        errore transitorio, reset, churn) e REQUIRE_VALIDATED_PAIRS è True, il bot
        resta FLAT invece di tradare tutto senza validazione. Solo in bootstrap
        (flag False) si opera coi default in attesa del primo run di ottimizzazione.
        """
        if not self._has_opt_data:
            return not settings.REQUIRE_VALIDATED_PAIRS
        return f"{symbol}|{strategy}" in self._passed

    def regime_ok(self, symbol: str, strategy: str, regime) -> bool:
        """False se il GATE ha visto questa coppia PERDERE nel regime corrente
        (PF < 1 con un campione minimo). FAIL-OPEN: senza dati per-regime (coppia
        non ancora ri-validata, regime mai visto in OOS) non blocca nulla.

        E' il prior che mancava: il gate conosceva il PF per-regime dai suoi trade
        OOS ma non lo esportava, cosi' il bot tradava in sideways coppie che il
        gate stesso sapeva perdere in sideways — e il learning doveva riscoprirlo
        da zero, a spese del paper."""
        if not settings.REGIME_FILTER_ENABLED or regime is None:
            return True
        info = self._regime_pf.get(f"{symbol}|{strategy}", {})
        rk = regime.value if hasattr(regime, "value") else str(regime)
        rec = info.get(rk)
        if not isinstance(rec, dict):
            return True
        try:
            pf, n = float(rec.get("pf", 99)), int(rec.get("trades", 0))
        except (TypeError, ValueError):
            return True
        return not (n >= settings.GATE_REGIME_MIN_TRADES and pf < 1.0)

    def is_baseline_cycle(self, rng: Optional[random.Random] = None) -> bool:
        """
        True con probabilità pari a BASELINE_CAPITAL_FRACTION: in tal caso il ciclo
        usa la configurazione baseline non adattata (riferimento anti-overfitting).
        """
        r = rng or random
        return r.random() < settings.BASELINE_CAPITAL_FRACTION
