# 0338-29set-controllo.req

_eseguito: 2026-09-29 06:05 UTC_

**richiesta:** `controllo`
**eseguito:** `.venv/bin/python -m scripts.controllo`
**esito:** codice 0 in 4.5s

```
[firebase] connesso (Firestore + RTDB)
CONTROLLO AUTOMATICO — generato da ops alle 2026-09-29 06:05 UTC (durata 2489 ms, impostazioni: default repo)
  semaforo SISTEMA: VERDE    semaforo PAPER: GIALLO
  controllo precedente: 2026-09-29 05:06 UTC
  sezioni fallite: nessuna

ANOMALIE (2):
  [giallo] FRENO_GLOBALE (paper): freno globale da deriva: PF 0,70 vs 2,04 atteso (valore 0.697, soglia 1.221)
  [giallo] SENZA_PROMESSA (paper): 125 validate su 199 senza promessa (last_pf) (valore 0.628, soglia 0.3)

LETTURE:
  salute:    Bot vivo (battito 4 s fa), gate 57 min fa (completa), 1 posizioni, 0,1% a rischio. 2 avvisi: freno globale, validate senza promessa.
  paper:     174 trade in 12 giorni, 55% vinti, -67,34 USDT (-6,7%). BTC dal primo giorno +9,8% (noi -6,7%). Oggi +1,27 (validate +0,24).
  learning:  Attivo: freno globale, 6 strategie in panchina, keep per coppia 0.35 ×12, 0.5 ×7, 0.65 ×6, 0.75 ×14. Solo misurato: deriva, calibrazione.

LETTURE FIRESTORE DEL BOT (ultime 24 h, quota gratuita 50.000/giorno):
  non misurate in questo documento (le conta solo il bot: vedi il controllo orario)

CAMBIAMENTI DEL LEARNING dal controllo precedente:
  nessuno: nessun pezzo del learning ha cambiato decisione

COSA QUESTO CONTROLLO NON PUO' DARE:
  - cosa aspetta il si' del proprietario: vive in docs/backlog.md, non e' un dato del sistema -> leggere docs/backlog.md (voce F1 per il learning)

--- stderr ---
/root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
  return query.where(field_path, op_string, value)
```
