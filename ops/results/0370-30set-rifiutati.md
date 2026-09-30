# 0370-30set-rifiutati.req

_eseguito: 2026-09-30 06:17 UTC_

**richiesta:** `rifiutati`
**eseguito:** `.venv/bin/python -m scripts.rifiutati_report`
**esito:** codice 0 in 2.0s

```
[firebase] connesso (Firestore + RTDB)
SEGNALI RIFIUTATI — ultimi 30 giorni (dal 2026-08-31 UTC): 71 registrati
  motivo                 segnali valutati attesa scaduti  R medio vincenti  mfe med  esiti
  posizione aperta            44       44      0       0    -0.15      50%     0.54  stop 22, trailing 22
  cooldown                    24       24      0       0    -0.14      50%     0.84  trailing 12, stop 12
  stop troppo largo            3        3      0       0    -1.00       0%     0.62  stop 3

APERTI nello stesso periodo: 174 trade con R calcolabile (8 senza) · R medio -0.21 · vincenti 53% · mfe mediana 0.84

REGOLA: un freno si ritara solo se per un motivo i rifiutati hanno R medio > aperti con >= 30 casi valutati.
VERDETTO PER MOTIVO:
  posizione aperta       R -0.15 > aperti -0.21 su 44 casi: il freno si puo' RITARARE (proposta per il gate)
  cooldown                24/30 valutati: campione insufficiente, nessun verdetto
  stop troppo largo        3/30 valutati: campione insufficiente, nessun verdetto

AVVERTENZE: i rifiutati sono prezzo puro (niente fee, slippage, funding) e simulati sulla candela;
gli aperti sono netti di costi ed eseguiti al mark: a parita' di tragitto i rifiutati sembrano ~0,1-0,2 R migliori.

--- stderr ---
/root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
  return query.where(field_path, op_string, value)
```
