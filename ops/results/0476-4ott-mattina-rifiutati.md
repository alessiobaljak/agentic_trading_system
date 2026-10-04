# 0476-4ott-mattina-rifiutati.req

_eseguito: 2026-10-04 06:20 UTC_

**richiesta:** `rifiutati`
**eseguito:** `.venv/bin/python -m scripts.rifiutati_report`
**esito:** codice 0 in 2.4s

```
[firebase] connesso (Firestore + RTDB)
SEGNALI RIFIUTATI — ultimi 30 giorni (dal 2026-09-04 UTC): 117 registrati
  motivo                 segnali valutati attesa scaduti  R medio vincenti  mfe med  esiti
  posizione aperta            74       73      1       0    +0.01      56%     0.92  trailing 40, stop 32, orizzonte 1
  cooldown                    32       32      0       0    +0.07      59%     0.96  trailing 19, stop 13
  stop troppo largo            6        6      0       0    -0.75      17%     0.81  stop 5, trailing 1
  altro                        4        4      0       0    -0.11      50%     0.82  stop 2, trailing 2
  veto di regime               1        1      0       0    +0.45     100%     0.89  trailing 1

APERTI dal 26/09/2026 13:15 ora italiana (primo rifiutato registrato), per ora d'ingresso: 161 trade con R (0 senza R) · R netto medio -0.03 · R lordo medio +0.06 (su 161 col lordo) · vincenti 62% · mfe mediana 0.86
  fuori dal confronto: 4 entrati prima e usciti dopo, 0 senza ora d'ingresso, 10 esplorativi

REGOLA: un freno si ritara solo se per un motivo i rifiutati hanno R medio > aperti (R netto, stesso periodo) con >= 30 casi valutati.
MARGINE: 2 errori standard della differenza, caso per caso; solo informazione, non entra nel verdetto.
VERDETTO PER MOTIVO:
  posizione aperta       R +0.01 > aperti -0.03 su 73 casi: il freno si puo' RITARARE (proposta per il gate) [differenza +0.04 ± 0.27, solo informazione]
  cooldown               R +0.07 > aperti -0.03 su 32 casi: il freno si puo' RITARARE (proposta per il gate) [differenza +0.09 ± 0.36, solo informazione]
  stop troppo largo        6/30 valutati: campione insufficiente, nessun verdetto
  altro                    4/30 valutati: campione insufficiente, nessun verdetto
  veto di regime           1/30 valutati: campione insufficiente, nessun verdetto

AVVERTENZE: i rifiutati sono prezzo puro (niente fee, slippage, funding) e simulati sulla candela;
gli aperti sono netti di costi ed eseguiti al mark: a parita' di tragitto i rifiutati sembrano ~0,1-0,2 R migliori (vedi R lordo).

--- stderr ---
/root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
  return query.where(field_path, op_string, value)
```
