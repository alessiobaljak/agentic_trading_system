# Motore di apprendimento (il cuore)

Il sistema **non** ha regole fisse. Impara dai trade chiusi, riconosce quali
strategie funzionano in quali regimi e adatta il proprio comportamento.

## Componenti
- `bot/learning/trade_logger.py` — registra ogni trade chiuso su Firestore con
  TUTTO il contesto d'entrata (indicatori, sentiment, F&G, funding, regime,
  confidenza dichiarata).
- `bot/learning/metrics.py` — metriche segmentate + calcolo dei pesi dinamici.
- `bot/learning/learning_loop.py` — job notturno (02:00 UTC) che produce
  `memory_report` e i pesi.
- `bot/learning/adaptation.py` — applica i pesi alle decisioni (con baseline
  anti-overfitting).

## Learning loop notturno (passi)
1. Legge i trade degli ultimi **30/60/90** giorni da Firebase.
2. Calcola metriche **segmentate**:
   - win rate per strategia, e **per strategia × regime**
   - R:R realizzato medio per strategia
   - PnL per asset, win rate per fascia oraria
   - condizioni dei peggiori drawdown (cosa accomunava i trade perdenti)
   - correlazione tra **confidenza dichiarata** e **PnL reale** (Pearson)
3. Genera un `memory_report` JSON (uno per finestra) su `memory/{30,60,90}`.
4. Calcola i **pesi dinamici** per strategia × regime.
5. Salva i pesi su `strategy_weights/current`.
6. Il giorno dopo l'orchestratore riceve `memory/30` nel prompt e si adatta.
7. La domenica genera un **insight narrativo** via Claude → `insights/` (RAG).

## Calcolo dei pesi (`metrics.compute_weights`)
Per ogni coppia (strategia, regime):
- `sample < MIN_TRADES_PER_WEIGHT (5)` → peso **neutro 1.0** (dati insufficienti).
- altrimenti il peso deriva dal win rate con mappatura lineare:
  - win_rate ≤ **0.35** → peso **0.0** (strategia disattivata in quel regime)
  - win_rate ≥ **0.60** → peso **1.0**
  - in mezzo: interpolazione lineare
- piccolo aggiustamento dal R:R realizzato.

Esempio concreto: una strategia che ha perso **8 dei 10** trade in `sideways`
(win_rate 0.2) riceve peso **0** in `sideways` → di fatto disattivata lì finché le
condizioni non cambiano. Verificato in `tests/test_learning.py`.

## Adattamento (`AdaptationEngine`)
- L'orchestratore **moltiplica** la propria confidenza per
  `weight_for(strategy, regime)`.
- Peso `0` → la decisione viene scartata (strategia disattivata).
- Pesi alti → più capitale verso quella strategia.

### Anti-overfitting: baseline non adattata
Una frazione fissa del capitale (`BASELINE_CAPITAL_FRACTION = 20%`) gira **sempre**
con configurazione baseline (peso 1.0 per tutte le strategie), come riferimento e
per non collassare su pattern passati. `AdaptationEngine.is_baseline_cycle()`
seleziona quando un ciclo è baseline; `weight_for(..., baseline=True)` ignora i
pesi appresi.

## Validazione sui dati storici
Il backtester (GATE 1) dà i propri trade simulati a `compute_weights` e mostra i
pesi risultanti nel report HTML: così il learning loop è validato **prima** del
paper trading. Vedi `backtesting/engine.py::validate_learning`.
