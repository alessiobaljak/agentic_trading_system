# 0500-5ott-mattina-rifiutati.req

_eseguito: 2026-10-05 06:21 UTC_

**richiesta:** `rifiutati`
**eseguito:** `.venv/bin/python -m scripts.rifiutati_report`
**esito:** codice 0 in 2.4s

```
[firebase] connesso (Firestore + RTDB)
SEGNALI RIFIUTATI — ultimi 30 giorni (dal 2026-09-05 UTC): 131 registrati
  motivo                 segnali valutati attesa scaduti  R medio vincenti  mfe med  esiti
  posizione aperta            83       83      0       0    -0.02      55%     0.91  trailing 45, stop 37, orizzonte 1
  cooldown                    33       33      0       0    +0.03      58%     0.94  trailing 19, stop 14
  stop troppo largo           10        9      1       0    -0.48      33%     0.99  stop 6, trailing 3
  altro                        4        4      0       0    -0.11      50%     0.82  stop 2, trailing 2
  veto di regime               1        1      0       0    +0.45     100%     0.89  trailing 1

APERTI dal 26/09/2026 13:15 ora italiana (primo rifiutato registrato), per ora d'ingresso: 187 trade con R (0 senza R) · R netto medio -0.06 · R lordo medio +0.03 (su 187 col lordo) · vincenti 60% · mfe mediana 0.87
  fuori dal confronto: 4 entrati prima e usciti dopo, 0 senza ora d'ingresso, 12 esplorativi

REGOLA: un freno si ritara solo se per un motivo i rifiutati hanno R medio > aperti (R netto, stesso periodo) con >= 30 casi valutati.
MARGINE: 2 errori standard della differenza, caso per caso; solo informazione, non entra nel verdetto.
VERDETTO PER MOTIVO:
  posizione aperta       R -0.02 > aperti -0.06 su 83 casi: il freno si puo' RITARARE (proposta per il gate) [differenza +0.05 ± 0.25, solo informazione]
  cooldown               R +0.03 > aperti -0.06 su 33 casi: il freno si puo' RITARARE (proposta per il gate) [differenza +0.10 ± 0.36, solo informazione]
  stop troppo largo        9/30 valutati: campione insufficiente, nessun verdetto
  altro                    4/30 valutati: campione insufficiente, nessun verdetto
  veto di regime           1/30 valutati: campione insufficiente, nessun verdetto

AVVERTENZE: i rifiutati sono prezzo puro (niente fee, slippage, funding) e simulati sulla candela;
gli aperti sono netti di costi ed eseguiti al mark: a parita' di tragitto i rifiutati sembrano ~0,1-0,2 R migliori (vedi R lordo).

--- stderr ---
/root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
  return query.where(field_path, op_string, value)
```
