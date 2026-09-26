# 0269-controllo-26set-controllo.req

_eseguito: 2026-09-26 06:16 UTC_

**richiesta:** `controllo`
**eseguito:** `.venv/bin/python -m scripts.controllo`
**esito:** codice 0 in 3.7s

```
[firebase] connesso (Firestore + RTDB)
CONTROLLO AUTOMATICO — generato da ops alle 2026-09-26 06:16 UTC (durata 1958 ms, impostazioni: default repo)
  semaforo SISTEMA: GIALLO   semaforo PAPER: GIALLO
  controllo precedente: 2026-09-26 06:02 UTC
  sezioni fallite: nessuna

ANOMALIE (4):
  [giallo] FRENO_GLOBALE (paper): freno globale da deriva: PF 0,61 vs 2,09 atteso (valore 0.615, soglia 1.255)
  [giallo] REGISTRO_PIENO (sistema): registro a 2859/3000 coppie (valore 2859.0, soglia 2400.0)
  [giallo] RIAVVII (sistema): 6 riavvii del bot in 24 h (valore 6, soglia 3)
  [giallo] SENZA_PROMESSA (paper): 115 validate su 182 senza promessa (last_pf) (valore 0.632, soglia 0.3)

LETTURE:
  salute:    Bot vivo (battito 1 min fa), gate 1 h 13 fa (solo urgenti), 2 posizioni, 0,3% a rischio. 4 avvisi: freno globale, registro pieno, riavvii.
  paper:     84 trade in 9 giorni, 46% vinti, -63,73 USDT (-6,4%). Stop nel 54% delle uscite. Oggi -2,25.
  learning:  Attivo: freno globale, 5 strategie in panchina, keep per coppia 0.35 ×6, 0.5 ×1, 0.65 ×2, 0.75 ×6. Solo misurato: deriva, calibrazione.

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
