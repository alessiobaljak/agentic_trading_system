# 0323-28set-controllo.req

_eseguito: 2026-09-28 05:34 UTC_

**richiesta:** `controllo`
**eseguito:** `.venv/bin/python -m scripts.controllo`
**esito:** codice 0 in 4.0s

```
[firebase] connesso (Firestore + RTDB)
CONTROLLO AUTOMATICO — generato da ops alle 2026-09-28 05:34 UTC (durata 2360 ms, impostazioni: default repo)
  semaforo SISTEMA: GIALLO   semaforo PAPER: GIALLO
  controllo precedente: 2026-09-28 05:21 UTC
  sezioni fallite: nessuna

ANOMALIE (3):
  [giallo] FRENO_GLOBALE (paper): freno globale da deriva: PF 0,67 vs 2,10 atteso (valore 0.672, soglia 1.257)
  [giallo] RIAVVII (sistema): 5 riavvii del bot in 24 h (valore 5, soglia 3)
  [giallo] SENZA_PROMESSA (paper): 131 validate su 192 senza promessa (last_pf) (valore 0.682, soglia 0.3)

LETTURE:
  salute:    Bot vivo (battito 19 s fa), gate 30 min fa (solo urgenti), 4 posizioni, 0,7% a rischio. 3 avvisi: freno globale, riavvii, validate senza pr…
  paper:     142 trade in 11 giorni, 52% vinti, -69,10 USDT (-6,9%). Stop nel 48% delle uscite. Oggi +4,82.
  learning:  Attivo: freno globale, 6 strategie in panchina, keep per coppia 0.35 ×9, 0.5 ×2, 0.65 ×1, 0.75 ×14. Solo misurato: deriva, calibrazione.

CAMBIAMENTI DEL LEARNING dal controllo precedente:
  nessuno: nessun pezzo del learning ha cambiato decisione

COSA QUESTO CONTROLLO NON PUO' DARE:
  - battito dell'agente ops: vive in git (ops/heartbeat.md), non su Firebase -> leggere ops/heartbeat.md nel repo
  - benchmark BTC buy&hold dal primo giorno del paper: servono le candele di Binance (GitHub non le raggiunge): qui solo l'anello orario /btc_history di 200 punti -> comando ops `stato` sulla VPS (state_snapshot col confronto col mercato)
  - cosa aspetta il si' del proprietario: vive in docs/backlog.md, non e' un dato del sistema -> leggere docs/backlog.md (voce F1 per il learning)

--- stderr ---
/root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
  return query.where(field_path, op_string, value)
```
