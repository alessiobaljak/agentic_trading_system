# 0122-gen6d06-gate-vs-paper.req

_eseguito: 2026-09-21 05:16 UTC_

**richiesta:** `gate-vs-paper`
**eseguito:** `.venv/bin/python -m scripts.gate_vs_paper`
**esito:** codice 0 in 33.8s

```
[firebase] connesso (Firestore + RTDB)
[gvp] nessuna coppia indicata -> scelta automatica: DEXEUSDT|gen_fa304106 (4 trade chiusi dal paper, e' quella con piu' materiale)
[gvp] DEXEUSDT|gen_fa304106 · scala TP 1.5/3/5 · quote (0.3, 0.3, 0.4)
[gvp] registro: PF 2.06 · 96 trade · win 57% · pnl +94.8% · pass 3
[gvp] spec: features=['bb_touch', 'ema_cross', 'vwap_momentum'] atr_mult_stop=2.5 rr=1.5 min_adx=20.0 volume_mult=0.0
[backtest] dati da cache: 60915 candele (DEXEUSDT 15m)
[gvp] candele: 60915 da 2024-12-24 a 2026-09-20

sorgente                      n  mediana>=0.5R  >=1R>=1.5R  >=2R  >=3R  >=4R  >=5R
----------------------------------------------------------------------------------
GATE finestre OOS            96     1.69    74%    68%    54%    40%    18%     8%     6%
GATE holdout                  9     2.29    89%    67%    56%    56%    33%    22%    11%
PAPER (vissuto)               4     0.52    50%     0%     0%     0%     0%     0%     0%

GATE OOS: PF 2.060 · win 57% · ritorno +94.8% · maxDD 13.8%
GATE holdout: PF 3.536 · win 67% · ritorno +13.5%
PAPER: 4 trade · win 0% · PnL -8.41 USDT

GATE finestre OOS — chi fa il risultato (fasce sulla scala 1.5/3/5):
  fascia                      trade  % trade         PnL  % del PnL
  < 1.5R (nessun gradino)        44      46%      -0.858       -90%
  1.5R–3R                        35      36%       0.893        94%
  3R–5R                          11      11%       0.413        44%
  >= 5R (corsa piena)             6       6%       0.499        53%
  TOTALE                         96     100%       0.948       100%

GATE holdout — chi fa il risultato (fasce sulla scala 1.5/3/5):
  fascia                      trade  % trade         PnL  % del PnL
  < 1.5R (nessun gradino)         4      44%      -0.036       -27%
  1.5R–3R                         2      22%       0.051        38%
  3R–5R                           2      22%       0.077        57%
  >= 5R (corsa piena)             1      11%       0.043        32%
  TOTALE                          9     100%       0.135       100%

PAPER (vissuto) — chi fa il risultato (fasce sulla scala 1.5/3/5):
  fascia                      trade  % trade         PnL  % del PnL
  < 1.5R (nessun gradino)         4     100%      -8.407       100%
  TOTALE                          4     100%      -8.407       100%

Come si legge: se nel GATE la fascia di CODA (l'ultima) porta la quota
dominante del PnL e nel PAPER quella fascia e' vuota, il vantaggio
validato non si sta ripetendo — e nessuna scala di TP puo' recuperarlo,
perche' il prezzo non ci arriva. Campioni piccoli non decidono: guarda n.

--- stderr ---
/root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
  return query.where(field_path, op_string, value)
```
