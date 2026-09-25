# 0245-controllo-prova.req

_eseguito: 2026-09-25 08:51 UTC_

**richiesta:** `controllo`
**eseguito:** `.venv/bin/python -m scripts.controllo`
**esito:** codice 0 in 3.8s

```
[firebase] connesso (Firestore + RTDB)
CONTROLLO AUTOMATICO — generato da ops alle 2026-09-25 08:51 UTC (durata 2002 ms, impostazioni: default repo)
  semaforo SISTEMA: GIALLO   semaforo PAPER: GIALLO
  controllo precedente: 2026-09-25 08:33 UTC
  sezioni fallite: nessuna

ANOMALIE (2):
  [giallo] CONTROLLO_LENTO (sistema): il controllo ha impiegato 2002 ms (valore 2002, soglia 2000)
  [giallo] FRENO_GLOBALE (paper): freno globale da deriva: PF 0,59 vs 1,87 atteso (valore 0.587, soglia 1.121)

LETTURE:
  salute:    Bot vivo (battito 27 s fa), gate 1 h 23 fa, 4 posizioni, 0,0% a rischio. 2 avvisi: controllo lento, freno globale.
  paper:     60 trade in 8 giorni, 40% vinti, -58,36 USDT (-5,8%). Stop nel 60% delle uscite. Oggi -10,78.
  learning:  Attivo: freno globale, 4 strategie in panchina, 3 cooldown. Solo misurato: deriva, calibrazione, 19 verdetti trailing, referti, selettore.

CAMBIAMENTI DEL LEARNING dal controllo precedente:
  - cooldown HEIUSDT finito

COSA QUESTO CONTROLLO NON PUO' DARE:
  - battito dell'agente ops: vive in git (ops/heartbeat.md), non su Firebase -> leggere ops/heartbeat.md nel repo
  - benchmark BTC buy&hold dal primo giorno del paper: servono le candele di Binance (GitHub non le raggiunge): qui solo l'anello orario /btc_history di 200 punti -> comando ops `stato` sulla VPS (state_snapshot col confronto col mercato)
  - cosa aspetta il si' del proprietario: vive in docs/backlog.md, non e' un dato del sistema -> leggere docs/backlog.md (voce F1 per il learning)

--- stderr ---
/root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
  return query.where(field_path, op_string, value)
```
