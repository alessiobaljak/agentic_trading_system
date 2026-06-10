# scripts/ — automazioni

Helper eseguiti dalle GitHub Actions. I file YAML dei workflow vivono in
`.github/workflows/` (percorso obbligatorio perché GitHub li riconosca), mentre la
logica Python sta qui.

| Workflow (`.github/workflows/`) | Schedule          | Script / comando                     | Scopo |
|---------------------------------|-------------------|--------------------------------------|-------|
| `learning.yml`                  | 02:00 UTC / manual| `python -m bot.learning.learning_loop` | Learning notturno: metriche, pesi, memory_report, insight RAG |
| `monitoring.yml`                | ogni 15 min       | `python -m scripts.monitor`          | Heartbeat + alert Telegram (bot offline / daily loss) |
| `tests.yml`                     | push / PR         | `pytest`                             | Test (incl. safety del risk gate) |
| `backtest.yml`                  | manual            | `python -m backtesting.run`          | GATE 1 — fallisce se non profittevole |

## Secrets richiesti dai workflow
Vedi README principale, sezione 7.1. In sintesi: `FIREBASE_SERVICE_ACCOUNT`,
`FIREBASE_RTDB_URL`, `ANTHROPIC_API_KEY`, `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`.
