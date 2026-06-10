# Architettura

Documento di riferimento delle scelte architetturali. Per la panoramica e il
setup vedi il `README.md` alla radice.

## Principi guida
1. **Auto-apprendimento prima di tutto.** Il sistema non ha regole fisse: il
   motore di apprendimento (`bot/learning`) ricalcola ogni notte i pesi
   strategia×regime e l'orchestratore vi si adatta. Vedi `docs/learning.md`.
2. **Sicurezza non bypassabile.** Gli hard cap e i circuit breaker
   (`bot/risk/hard_limits.py`) sono nel codice, mai su Firebase, mai nel prompt
   LLM. Ogni ordine passa dal `final_gate`. Vedi `docs/risk.md`.
3. **Stesso codice in paper e live.** L'execution gira identica in `DRY_RUN`
   (GATE 2 paper) e in live; cambia solo il flag. Niente percorsi separati che
   possano divergere.
4. **Espandibilità.** Le strategie derivano da una classe astratta + registry:
   aggiungerne una è un solo file (`docs` e `README` lo spiegano).
5. **Degradazione graceful.** Ogni agente dati e Firebase hanno fallback: senza
   chiavi il sistema gira comunque (in-memory / sintetico) per test e sviluppo.

## Flusso dati (runtime)
```
PriceAgent ─┐
SentimentAgent ─┤
OnChainAgent ─┼─> MarketScanner ──> AssetSelector ──> {3-5 asset}
MacroAgent ─┘                                              │
                                                           v
RegimeDetector ──> regime ─────────────────────────> Orchestrator
                                                           │ (Claude + memory_report + weights)
                                                           v
                                                   OrchestratorDecision
                                                           │
                          user_risk_settings ──> RiskManager.resolve_effective_params
                                                           │
                                                   RiskManager.final_gate  <── circuit breakers
                                                           │ (approved)
                                                           v
                                                   ExecutionEngine (DRY_RUN/live)
                                                           │
                              ┌────────────────────────────┤
                              v                            v
                     Firebase RTDB (/positions)     ClosedTrade ──> TradeLogger (Firestore)
                                                           │
                                          (notte 02:00) LearningLoop ──> memory_report + weights
                                                           │
                                                           └──> (giorno dopo) Orchestrator si adatta
```

## Moduli e responsabilità
| Modulo | Responsabilità |
|--------|----------------|
| `bot/core` | modelli Pydantic (contratto), indicatori, client Firebase |
| `bot/agents` | acquisizione dati, scanner, regime detector |
| `bot/strategies` | 8 strategie + base astratta + registry |
| `bot/risk` | hard limits, precedenza, final gate, circuit breaker, correlation guard |
| `bot/orchestrator` | prompt + chiamata LLM + validazione + adattamento |
| `bot/learning` | trade logger, metriche, pesi, learning loop, adaptation |
| `bot/execution` | ordini, trailing/scale-out, stato RTDB, notifier |
| `backtesting` | GATE 1: simulazione storica + liquidazioni + validazione learning |
| `dashboard` | UI Vercel: stato, equity, heatmap, pesi, insight, risk control, kill switch |
| `scripts` + `.github/workflows` | learning notturno + monitoring + test + backtest |

## Perché queste tecnologie
- **Python 3.11** per il bot: ecosistema dati/TA maturo.
- **Pydantic v2** per validare i confini (output LLM, settings, trade): un dato
  malformato non entra nel sistema.
- **Firebase** (Firestore + RTDB): Firestore per storia/memoria queryabile, RTDB
  per stato live a bassa latenza letto dalla dashboard.
- **Next.js 14 su Vercel**: deploy serverless, lettura diretta di Firebase.
- **GitHub Actions** per i job schedulati: nessuna infrastruttura aggiuntiva.

Vedi anche: `docs/risk.md`, `docs/learning.md`, `docs/firebase_schema.md`,
`docs/deployment.md`, `docs/data_sources.md`, `docs/orchestrator.md`.
