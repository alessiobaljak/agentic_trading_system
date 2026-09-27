# 0289-rifiutati-ombra.req

_eseguito: 2026-09-27 05:59 UTC_

**richiesta:** `rifiutati`
**eseguito:** `.venv/bin/python -m scripts.rifiutati_report`
**esito:** codice 0 in 1.7s

```
[firebase] connesso (Firestore + RTDB)
SEGNALI RIFIUTATI — ultimi 30 giorni (dal 2026-08-28 UTC): 34 registrati
  motivo                 segnali valutati attesa scaduti  R medio vincenti  mfe med  esiti
  posizione aperta            21       16      5       0    -0.68      19%     0.15  stop 13, trailing 3
  cooldown                    12       11      1       0    -1.00       0%     0.32  stop 11
  stop troppo largo            1        1      0       0    -1.00       0%     0.62  stop 1

APERTI nello stesso periodo: 102 trade con R calcolabile (8 senza) · R medio -6.80 · vincenti 44% · mfe mediana 0.79

REGOLA: un freno si ritara solo se per un motivo i rifiutati hanno R medio > aperti con >= 30 casi valutati.
VERDETTO PER MOTIVO:
  posizione aperta        16/30 valutati: campione insufficiente, nessun verdetto
  cooldown                11/30 valutati: campione insufficiente, nessun verdetto
  stop troppo largo        1/30 valutati: campione insufficiente, nessun verdetto

AVVERTENZE: i rifiutati sono prezzo puro (niente fee, slippage, funding) e simulati sulla candela;
gli aperti sono netti di costi ed eseguiti al mark: a parita' di tragitto i rifiutati sembrano ~0,1-0,2 R migliori.

--- stderr ---
/root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
  return query.where(field_path, op_string, value)
```
