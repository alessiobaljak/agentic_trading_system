# 0564-9ott-mattina-rifiutati.req

_eseguito: 2026-10-09 04:05 UTC_

**richiesta:** `rifiutati`
**eseguito:** `.venv/bin/python -m scripts.rifiutati_report`
**esito:** codice 0 in 2.8s

```
[firebase] connesso (Firestore + RTDB)
SEGNALI RIFIUTATI — ultimi 30 giorni (dal 2026-09-09 UTC): 294 registrati
  motivo                 segnali valutati attesa scaduti  R medio vincenti  mfe med  esiti
  posizione aperta           197      186     11       0    -0.11      47%     0.75  stop 92, trailing 84, orizzonte 9, tp 1
  cooldown                    62       60      2       0    +0.18      55%     0.93  trailing 28, stop 27, orizzonte 3, tp 2
  stop troppo largo           17       15      2       0    -0.10      40%     0.99  stop 9, trailing 4, orizzonte 2
  altro                       14       11      3       0    -0.50      27%     0.44  stop 8, trailing 3
  veto di regime               2        2      0       0    +0.46     100%     0.92  trailing 2
  margine                      2        2      0       0    -0.33      50%     0.67  trailing 1, stop 1

APERTI dal 26/09/2026 13:15 ora italiana (primo rifiutato registrato), per ora d'ingresso: 306 trade con R (0 senza R) · R netto medio -0.11 · R lordo medio -0.02 (su 306 col lordo) · vincenti 56% · mfe mediana 0.80
  fuori dal confronto: 4 entrati prima e usciti dopo, 0 senza ora d'ingresso, 18 esplorativi

REGOLA: un freno si ritara solo se per un motivo i rifiutati hanno R medio > aperti (R netto, stesso periodo) con >= 30 casi valutati.
MARGINE: 2 errori standard della differenza, caso per caso; solo informazione, non entra nel verdetto.
VERDETTO PER MOTIVO:
  posizione aperta       R -0.11 > aperti -0.11 su 186 casi: il freno si puo' RITARARE (proposta per il gate) [differenza +0.00 ± 0.18, solo informazione]
  cooldown               R +0.18 > aperti -0.11 su 60 casi: il freno si puo' RITARARE (proposta per il gate) [differenza +0.29 ± 0.34, solo informazione]
  stop troppo largo       15/30 valutati: campione insufficiente, nessun verdetto
  altro                   11/30 valutati: campione insufficiente, nessun verdetto
  veto di regime           2/30 valutati: campione insufficiente, nessun verdetto
  margine                  2/30 valutati: campione insufficiente, nessun verdetto

AVVERTENZE: i rifiutati sono prezzo puro (niente fee, slippage, funding) e simulati sulla candela;
gli aperti sono netti di costi ed eseguiti al mark: a parita' di tragitto i rifiutati sembrano ~0,1-0,2 R migliori (vedi R lordo).

--- stderr ---
/root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
  return query.where(field_path, op_string, value)
```
