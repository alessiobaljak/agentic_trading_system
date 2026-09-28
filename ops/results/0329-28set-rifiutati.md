# 0329-28set-rifiutati.req

_eseguito: 2026-09-28 05:40 UTC_

**richiesta:** `rifiutati`
**eseguito:** `.venv/bin/python -m scripts.rifiutati_report`
**esito:** codice 0 in 3.0s

```
[firebase] connesso (Firestore + RTDB)
SEGNALI RIFIUTATI — ultimi 30 giorni (dal 2026-08-29 UTC): 55 registrati
  motivo                 segnali valutati attesa scaduti  R medio vincenti  mfe med  esiti
  posizione aperta            31       31      0       0    -0.20      45%     0.40  stop 17, trailing 14
  cooldown                    22       22      0       0    -0.24      46%     0.79  stop 12, trailing 10
  stop troppo largo            2        2      0       0    -1.00       0%     0.88  stop 2

APERTI nello stesso periodo: 134 trade con R calcolabile (8 senza) · R medio -0.26 · vincenti 49% · mfe mediana 0.82

REGOLA: un freno si ritara solo se per un motivo i rifiutati hanno R medio > aperti con >= 30 casi valutati.
VERDETTO PER MOTIVO:
  posizione aperta       R -0.20 > aperti -0.26 su 31 casi: il freno si puo' RITARARE (proposta per il gate)
  cooldown                22/30 valutati: campione insufficiente, nessun verdetto
  stop troppo largo        2/30 valutati: campione insufficiente, nessun verdetto

AVVERTENZE: i rifiutati sono prezzo puro (niente fee, slippage, funding) e simulati sulla candela;
gli aperti sono netti di costi ed eseguiti al mark: a parita' di tragitto i rifiutati sembrano ~0,1-0,2 R migliori.

--- stderr ---
/root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
  return query.where(field_path, op_string, value)
```
