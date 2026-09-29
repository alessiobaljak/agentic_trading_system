# 0350-29set-rifiutati.req

_eseguito: 2026-09-29 06:17 UTC_

**richiesta:** `rifiutati`
**eseguito:** `.venv/bin/python -m scripts.rifiutati_report`
**esito:** codice 0 in 2.0s

```
[firebase] connesso (Firestore + RTDB)
SEGNALI RIFIUTATI — ultimi 30 giorni (dal 2026-08-30 UTC): 67 registrati
  motivo                 segnali valutati attesa scaduti  R medio vincenti  mfe med  esiti
  posizione aperta            40       40      0       0    -0.10      52%     0.83  trailing 21, stop 19
  cooldown                    24       23      1       0    -0.20      48%     0.80  stop 12, trailing 11
  stop troppo largo            3        3      0       0    -1.00       0%     0.62  stop 3

APERTI nello stesso periodo: 160 trade con R calcolabile (8 senza) · R medio -0.21 · vincenti 52% · mfe mediana 0.83

REGOLA: un freno si ritara solo se per un motivo i rifiutati hanno R medio > aperti con >= 30 casi valutati.
VERDETTO PER MOTIVO:
  posizione aperta       R -0.10 > aperti -0.21 su 40 casi: il freno si puo' RITARARE (proposta per il gate)
  cooldown                23/30 valutati: campione insufficiente, nessun verdetto
  stop troppo largo        3/30 valutati: campione insufficiente, nessun verdetto

AVVERTENZE: i rifiutati sono prezzo puro (niente fee, slippage, funding) e simulati sulla candela;
gli aperti sono netti di costi ed eseguiti al mark: a parita' di tragitto i rifiutati sembrano ~0,1-0,2 R migliori.

--- stderr ---
/root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
  return query.where(field_path, op_string, value)
```
