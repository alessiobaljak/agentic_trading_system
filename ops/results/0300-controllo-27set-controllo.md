# 0300-controllo-27set-controllo.req

_eseguito: 2026-09-27 06:16 UTC_

**richiesta:** `controllo`
**eseguito:** `.venv/bin/python -m scripts.controllo`
**esito:** codice 0 in 4.1s

```
[firebase] connesso (Firestore + RTDB)
CONTROLLO AUTOMATICO — generato da ops alle 2026-09-27 06:16 UTC (durata 2300 ms, impostazioni: default repo)
  semaforo SISTEMA: GIALLO   semaforo PAPER: GIALLO
  controllo precedente: 2026-09-27 05:33 UTC
  sezioni fallite: nessuna

ANOMALIE (3):
  [giallo] FRENO_GLOBALE (paper): freno globale da deriva: PF 0,62 vs 2,10 atteso (valore 0.616, soglia 1.259)
  [giallo] REGISTRO_PIENO (sistema): registro a 2745/3000 coppie (valore 2745.0, soglia 2400.0)
  [giallo] SENZA_PROMESSA (paper): 137 validate su 212 senza promessa (last_pf) (valore 0.646, soglia 0.3)

LETTURE:
  salute:    Bot vivo (battito 2 min fa), gate 1 h 57 fa (solo urgenti), 4 posizioni, 0,9% a rischio. 3 avvisi: freno globale, registro pieno, validate…
  paper:     110 trade in 10 giorni, 48% vinti, -73,39 USDT (-7,2%). Stop nel 52% delle uscite. Oggi +3,59.
  learning:  Attivo: freno globale, 5 strategie in panchina, keep per coppia 0.35 ×10, 0.5 ×2, 0.65 ×2, 0.75 ×13. Solo misurato: deriva, calibrazione.

CAMBIAMENTI DEL LEARNING dal controllo precedente:
  - cooldown AVAAIUSDT finito
  - cooldown VETUSDT finito

COSA QUESTO CONTROLLO NON PUO' DARE:
  - battito dell'agente ops: vive in git (ops/heartbeat.md), non su Firebase -> leggere ops/heartbeat.md nel repo
  - benchmark BTC buy&hold dal primo giorno del paper: servono le candele di Binance (GitHub non le raggiunge): qui solo l'anello orario /btc_history di 200 punti -> comando ops `stato` sulla VPS (state_snapshot col confronto col mercato)
  - cosa aspetta il si' del proprietario: vive in docs/backlog.md, non e' un dato del sistema -> leggere docs/backlog.md (voce F1 per il learning)

--- stderr ---
/root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
  return query.where(field_path, op_string, value)
```
