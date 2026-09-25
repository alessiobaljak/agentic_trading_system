# 0252-come-procede-controllo.req

_eseguito: 2026-09-25 19:38 UTC_

**richiesta:** `controllo`
**eseguito:** `.venv/bin/python -m scripts.controllo`
**esito:** codice 0 in 4.3s

```
[firebase] connesso (Firestore + RTDB)
CONTROLLO AUTOMATICO — generato da ops alle 2026-09-25 19:38 UTC (durata 2454 ms, impostazioni: default repo)
  semaforo SISTEMA: GIALLO   semaforo PAPER: GIALLO
  controllo precedente: 2026-09-25 19:30 UTC
  sezioni fallite: nessuna

ANOMALIE (4):
  [giallo] FRENO_GLOBALE (paper): freno globale da deriva: PF 0,61 vs 1,87 atteso (valore 0.611, soglia 1.121)
  [giallo] REGISTRO_PIENO (sistema): registro a 2800/3000 coppie (valore 2800.0, soglia 2400.0)
  [giallo] RIAVVII (sistema): 5 riavvii del bot in 24 h (valore 5, soglia 3)
  [giallo] SENZA_PROMESSA (paper): 101 validate su 162 senza promessa (last_pf) (valore 0.623, soglia 0.3)

LETTURE:
  salute:    Bot vivo (battito 10 s fa), gate 13 min fa (solo urgenti), 1 posizioni, 0,2% a rischio. 4 avvisi: freno globale, registro pieno, riavvii.
  paper:     82 trade in 9 giorni, 46% vinti, -63,45 USDT (-6,3%). Stop nel 54% delle uscite. Oggi -15,87.
  learning:  Attivo: freno globale, 5 strategie in panchina. Solo misurato: deriva, calibrazione, 25 verdetti trailing, referti, selettore, ombra AI.

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
