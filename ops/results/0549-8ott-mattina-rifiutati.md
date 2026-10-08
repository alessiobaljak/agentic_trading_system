# 0549-8ott-mattina-rifiutati.req

_eseguito: 2026-10-08 04:05 UTC_

**richiesta:** `rifiutati`
**eseguito:** `.venv/bin/python -m scripts.rifiutati_report`
**esito:** codice 0 in 2.6s

```
[firebase] connesso (Firestore + RTDB)
SEGNALI RIFIUTATI — ultimi 30 giorni (dal 2026-09-08 UTC): 235 registrati
  motivo                 segnali valutati attesa scaduti  R medio vincenti  mfe med  esiti
  posizione aperta           153      148      5       0    -0.18      45%     0.71  stop 75, trailing 64, orizzonte 9
  cooldown                    59       56      3       0    +0.04      52%     0.90  trailing 27, stop 27, tp 2
  stop troppo largo           15       13      2       0    -0.49      31%     0.68  stop 9, trailing 4
  altro                        5        5      0       0    +0.09      60%     1.32  trailing 3, stop 2
  margine                      2        2      0       0    -0.33      50%     0.67  trailing 1, stop 1
  veto di regime               1        1      0       0    +0.45     100%     0.89  trailing 1

APERTI dal 26/09/2026 13:15 ora italiana (primo rifiutato registrato), per ora d'ingresso: 271 trade con R (0 senza R) · R netto medio -0.10 · R lordo medio -0.00 (su 271 col lordo) · vincenti 57% · mfe mediana 0.81
  fuori dal confronto: 4 entrati prima e usciti dopo, 0 senza ora d'ingresso, 15 esplorativi

REGOLA: un freno si ritara solo se per un motivo i rifiutati hanno R medio > aperti (R netto, stesso periodo) con >= 30 casi valutati.
MARGINE: 2 errori standard della differenza, caso per caso; solo informazione, non entra nel verdetto.
VERDETTO PER MOTIVO:
  posizione aperta       R -0.18 <= aperti -0.10 su 148 casi: il freno tiene [differenza -0.07 ± 0.19, solo informazione]
  cooldown               R +0.04 > aperti -0.10 su 56 casi: il freno si puo' RITARARE (proposta per il gate) [differenza +0.14 ± 0.33, solo informazione]
  stop troppo largo       13/30 valutati: campione insufficiente, nessun verdetto
  altro                    5/30 valutati: campione insufficiente, nessun verdetto
  margine                  2/30 valutati: campione insufficiente, nessun verdetto
  veto di regime           1/30 valutati: campione insufficiente, nessun verdetto

AVVERTENZE: i rifiutati sono prezzo puro (niente fee, slippage, funding) e simulati sulla candela;
gli aperti sono netti di costi ed eseguiti al mark: a parita' di tragitto i rifiutati sembrano ~0,1-0,2 R migliori (vedi R lordo).

--- stderr ---
/root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
  return query.where(field_path, op_string, value)
```
