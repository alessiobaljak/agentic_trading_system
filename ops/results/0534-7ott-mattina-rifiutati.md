# 0534-7ott-mattina-rifiutati.req

_eseguito: 2026-10-07 06:23 UTC_

**richiesta:** `rifiutati`
**eseguito:** `.venv/bin/python -m scripts.rifiutati_report`
**esito:** codice 0 in 2.2s

```
[firebase] connesso (Firestore + RTDB)
SEGNALI RIFIUTATI — ultimi 30 giorni (dal 2026-09-07 UTC): 204 registrati
  motivo                 segnali valutati attesa scaduti  R medio vincenti  mfe med  esiti
  posizione aperta           138      103     35       0    -0.14      48%     0.70  stop 53, trailing 49, orizzonte 1
  cooldown                    45       39      6       0    +0.09      59%     0.97  trailing 23, stop 16
  stop troppo largo           13       12      1       0    -0.44      33%     0.81  stop 8, trailing 4
  altro                        5        4      1       0    -0.11      50%     0.82  stop 2, trailing 2
  margine                      2        0      2       0        —        —        —  
  veto di regime               1        1      0       0    +0.45     100%     0.89  trailing 1

APERTI dal 26/09/2026 13:15 ora italiana (primo rifiutato registrato), per ora d'ingresso: 239 trade con R (0 senza R) · R netto medio -0.10 · R lordo medio -0.00 (su 239 col lordo) · vincenti 59% · mfe mediana 0.82
  fuori dal confronto: 4 entrati prima e usciti dopo, 0 senza ora d'ingresso, 13 esplorativi

REGOLA: un freno si ritara solo se per un motivo i rifiutati hanno R medio > aperti (R netto, stesso periodo) con >= 30 casi valutati.
MARGINE: 2 errori standard della differenza, caso per caso; solo informazione, non entra nel verdetto.
VERDETTO PER MOTIVO:
  posizione aperta       R -0.14 <= aperti -0.10 su 103 casi: il freno tiene [differenza -0.04 ± 0.22, solo informazione]
  cooldown               R +0.09 > aperti -0.10 su 39 casi: il freno si puo' RITARARE (proposta per il gate) [differenza +0.19 ± 0.33, solo informazione]
  stop troppo largo       12/30 valutati: campione insufficiente, nessun verdetto
  altro                    4/30 valutati: campione insufficiente, nessun verdetto
  margine                  0/30 valutati: campione insufficiente, nessun verdetto
  veto di regime           1/30 valutati: campione insufficiente, nessun verdetto

AVVERTENZE: i rifiutati sono prezzo puro (niente fee, slippage, funding) e simulati sulla candela;
gli aperti sono netti di costi ed eseguiti al mark: a parita' di tragitto i rifiutati sembrano ~0,1-0,2 R migliori (vedi R lordo).

--- stderr ---
/root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
  return query.where(field_path, op_string, value)
```
