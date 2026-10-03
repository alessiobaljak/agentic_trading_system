# 0456-3ott-mattina-rifiutati.req

_eseguito: 2026-10-03 06:19 UTC_

**richiesta:** `rifiutati`
**eseguito:** `.venv/bin/python -m scripts.rifiutati_report`
**esito:** codice 0 in 2.0s

```
[firebase] connesso (Firestore + RTDB)
SEGNALI RIFIUTATI — ultimi 30 giorni (dal 2026-09-03 UTC): 109 registrati
  motivo                 segnali valutati attesa scaduti  R medio vincenti  mfe med  esiti
  posizione aperta            68       63      5       0    -0.09      54%     0.91  trailing 34, stop 29
  cooldown                    32       28      4       0    -0.03      54%     0.90  trailing 15, stop 13
  stop troppo largo            6        6      0       0    -0.75      17%     0.81  stop 5, trailing 1
  altro                        3        1      2       0    -1.00       0%     0.27  stop 1

APERTI dal 26/09/2026 13:15 ora italiana (primo rifiutato registrato), per ora d'ingresso: 145 trade con R (0 senza R) · R netto medio -0.08 · R lordo medio +0.01 (su 145 col lordo) · vincenti 61% · mfe mediana 0.85
  fuori dal confronto: 4 entrati prima e usciti dopo, 0 senza ora d'ingresso, 8 esplorativi

REGOLA: un freno si ritara solo se per un motivo i rifiutati hanno R medio > aperti (R netto, stesso periodo) con >= 30 casi valutati.
MARGINE: 2 errori standard della differenza, caso per caso; solo informazione, non entra nel verdetto.
VERDETTO PER MOTIVO:
  posizione aperta       R -0.09 <= aperti -0.08 su 63 casi: il freno tiene [differenza -0.01 ± 0.26, solo informazione]
  cooldown                28/30 valutati: campione insufficiente, nessun verdetto
  stop troppo largo        6/30 valutati: campione insufficiente, nessun verdetto
  altro                    1/30 valutati: campione insufficiente, nessun verdetto

AVVERTENZE: i rifiutati sono prezzo puro (niente fee, slippage, funding) e simulati sulla candela;
gli aperti sono netti di costi ed eseguiti al mark: a parita' di tragitto i rifiutati sembrano ~0,1-0,2 R migliori (vedi R lordo).

--- stderr ---
/root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
  return query.where(field_path, op_string, value)
```
