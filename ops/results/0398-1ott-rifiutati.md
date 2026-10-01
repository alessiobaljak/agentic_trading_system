# 0398-1ott-rifiutati.req

_eseguito: 2026-10-01 06:18 UTC_

**richiesta:** `rifiutati`
**eseguito:** `.venv/bin/python -m scripts.rifiutati_report`
**esito:** codice 0 in 2.0s

```
[firebase] connesso (Firestore + RTDB)
SEGNALI RIFIUTATI — ultimi 30 giorni (dal 2026-09-01 UTC): 74 registrati
  motivo                 segnali valutati attesa scaduti  R medio vincenti  mfe med  esiti
  posizione aperta            46       45      1       0    -0.13      51%     0.54  trailing 23, stop 22
  cooldown                    25       25      0       0    -0.17      48%     0.80  stop 13, trailing 12
  stop troppo largo            3        3      0       0    -1.00       0%     0.62  stop 3

APERTI nello stesso periodo: 189 trade con R calcolabile (8 senza) · R medio -0.20 · vincenti 53% · mfe mediana 0.84

REGOLA: un freno si ritara solo se per un motivo i rifiutati hanno R medio > aperti con >= 30 casi valutati.
VERDETTO PER MOTIVO:
  posizione aperta       R -0.13 > aperti -0.20 su 45 casi: il freno si puo' RITARARE (proposta per il gate)
  cooldown                25/30 valutati: campione insufficiente, nessun verdetto
  stop troppo largo        3/30 valutati: campione insufficiente, nessun verdetto

AVVERTENZE: i rifiutati sono prezzo puro (niente fee, slippage, funding) e simulati sulla candela;
gli aperti sono netti di costi ed eseguiti al mark: a parita' di tragitto i rifiutati sembrano ~0,1-0,2 R migliori.

--- stderr ---
/root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
  return query.where(field_path, op_string, value)
```
