# Orchestratore LLM

Chiamato ad ogni candela **15m** chiusa. Decide al più un trade per ciclo (o
flat).

## Input (`bot/orchestrator/prompt.py`)
- indicatori 15m/1h degli asset selezionati
- sentiment LunarCrush, Fear & Greed, funding rate
- eventi macro prossime 4h
- **memory_report** del learning loop (metriche segmentate + pesi)
- ultimi 20 trade da Firebase
- segnali grezzi delle strategie attive nel regime corrente

> **Sicurezza**: nel prompt NON entrano mai gli hard limit (5x/3%/circuit
> breaker). L'LLM sceglie *cosa* fare; i limiti assoluti sono applicati dopo dal
> `RiskManager` e l'LLM non può ragionarci sopra né bypassarli.

## Output (validato Pydantic — `OrchestratorDecision`)
```json
{ "asset": "BTCUSDT", "strategy": "trend_following", "direction": "long",
  "size_multiplier": 0.0-1.0, "confidence": 0-100, "reasoning": "..." }
```
`size_multiplier=0` ⇒ flat. Un output malformato viene scartato (niente trade).

## Adattamento
Dopo la decisione, l'orchestratore calcola
`adjusted_confidence = confidence × weight_for(strategy, regime)`. Se il peso è
`0` (strategia disattivata dal learning in quel regime) la decisione viene
scartata. Vedi `docs/learning.md`.

## Fallback senza API key
Se `ANTHROPIC_API_KEY` non è impostata (o la chiamata fallisce), l'orchestratore
usa un **ensemble deterministico**: prende il segnale di strategia con
`adjusted_confidence` massima sopra una soglia minima, con size proporzionale alla
confidenza. Questo permette di far girare il **paper trading senza spesa LLM** e i
test offline. Il comportamento è coperto in `bot/orchestrator/orchestrator.py`.
