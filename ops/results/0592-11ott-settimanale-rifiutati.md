# 0592-11ott-settimanale-rifiutati.req

_eseguito: 2026-10-11 04:00 UTC_

**richiesta:** `rifiutati`
**eseguito:** `.venv/bin/python -m scripts.rifiutati_report`
**esito:** codice 0 in 3.2s

```
[firebase] connesso (Firestore + RTDB)
SEGNALI RIFIUTATI — ultimi 30 giorni (dal 2026-09-11 UTC): 306 registrati
  motivo                 segnali valutati attesa scaduti  R medio vincenti  mfe med  esiti
  posizione aperta           202      201      1       0    -0.08      47%     0.75  stop 94, trailing 89, orizzonte 17, tp 1
  cooldown                    65       65      0       0    +0.22      58%     0.97  trailing 33, stop 27, orizzonte 3, tp 2
  stop troppo largo           18       18      0       0    -0.25      33%     0.66  stop 12, trailing 4, orizzonte 2
  altro                       15       15      0       0    +0.05      47%     0.76  stop 8, trailing 6, orizzonte 1
  veto di regime               4        4      0       0    -0.27      50%     0.80  stop 2, trailing 2
  margine                      2        2      0       0    -0.33      50%     0.67  trailing 1, stop 1

APERTI dal 26/09/2026 13:15 ora italiana (primo rifiutato registrato), per ora d'ingresso: 344 trade con R (0 senza R) · R netto medio -0.09 · R lordo medio +0.01 (su 344 col lordo) · vincenti 58% · mfe mediana 0.80
  fuori dal confronto: 4 entrati prima e usciti dopo, 0 senza ora d'ingresso, 21 esplorativi

REGOLA: un freno si ritara solo se per un motivo i rifiutati hanno R medio > aperti (R netto, stesso periodo) con >= 30 casi valutati.
MARGINE: 2 errori standard della differenza, caso per caso; solo informazione, non entra nel verdetto.
VERDETTO PER MOTIVO:
  posizione aperta       R -0.08 > aperti -0.09 su 201 casi: il freno si puo' RITARARE (proposta per il gate) [differenza +0.00 ± 0.17, solo informazione]
  cooldown               R +0.22 > aperti -0.09 su 65 casi: il freno si puo' RITARARE (proposta per il gate) [differenza +0.30 ± 0.32, solo informazione]
  stop troppo largo       18/30 valutati: campione insufficiente, nessun verdetto
  altro                   15/30 valutati: campione insufficiente, nessun verdetto
  veto di regime           4/30 valutati: campione insufficiente, nessun verdetto
  margine                  2/30 valutati: campione insufficiente, nessun verdetto

AVVERTENZE: i rifiutati sono prezzo puro (niente fee, slippage, funding) e simulati sulla candela;
gli aperti sono netti di costi ed eseguiti al mark: a parita' di tragitto i rifiutati sembrano ~0,1-0,2 R migliori (vedi R lordo).

--- stderr ---
/root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
  return query.where(field_path, op_string, value)
```
