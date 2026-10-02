# 0431-2ott-mattina-rifiutati.req

_eseguito: 2026-10-02 06:17 UTC_

**richiesta:** `rifiutati`
**eseguito:** `.venv/bin/python -m scripts.rifiutati_report`
**esito:** codice 0 in 1.8s

```
[firebase] connesso (Firestore + RTDB)
SEGNALI RIFIUTATI — ultimi 30 giorni (dal 2026-09-02 UTC): 86 registrati
  motivo                 segnali valutati attesa scaduti  R medio vincenti  mfe med  esiti
  posizione aperta            52       49      3       0    -0.13      51%     0.60  trailing 25, stop 24
  cooldown                    28       26      2       0    -0.14      50%     0.84  trailing 13, stop 13
  stop troppo largo            6        5      1       0    -1.00       0%     0.64  stop 5

APERTI dal 26/09/2026 13:15 ora italiana (primo rifiutato registrato), per ora d'ingresso: 123 trade con R (0 senza R) · R netto medio -0.09 · R lordo medio -0.01 (su 123 col lordo) · vincenti 60% · mfe mediana 0.85
  fuori dal confronto: 4 entrati prima e usciti dopo, 0 senza ora d'ingresso, 8 esplorativi

REGOLA: un freno si ritara solo se per un motivo i rifiutati hanno R medio > aperti (R netto, stesso periodo) con >= 30 casi valutati.
MARGINE: 2 errori standard della differenza, caso per caso; solo informazione, non entra nel verdetto.
VERDETTO PER MOTIVO:
  posizione aperta       R -0.13 <= aperti -0.09 su 49 casi: il freno tiene [differenza -0.04 ± 0.30, solo informazione]
  cooldown                26/30 valutati: campione insufficiente, nessun verdetto
  stop troppo largo        5/30 valutati: campione insufficiente, nessun verdetto

AVVERTENZE: i rifiutati sono prezzo puro (niente fee, slippage, funding) e simulati sulla candela;
gli aperti sono netti di costi ed eseguiti al mark: a parita' di tragitto i rifiutati sembrano ~0,1-0,2 R migliori (vedi R lordo).

--- stderr ---
/root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
  return query.where(field_path, op_string, value)
```
