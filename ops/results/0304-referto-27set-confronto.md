# 0304-referto-27set-confronto.req

_eseguito: 2026-09-27 07:09 UTC_

**richiesta:** `confronto`
**eseguito:** `.venv/bin/python -m scripts.confronto_gate_paper`
**esito:** codice 0 in 301.9s

```
[firebase] connesso (Firestore + RTDB)
==========================================================================
SERIE DI PERDITE: quella in corso e' dentro il carattere del gate?
==========================================================================
PAPER: 112 trade chiusi · persi 59 · serie di perdite piu' lunga finora: 8
       coppie che hanno operato: 58

── SPXUSDT|gen_ba3a671f · scala TP 0.75/1.5/3
[backtest] dati da cache: 62830 candele (SPXUSDT 15m)
                 n    win      PF   PnL/trade   mfe med
  -----------------------------------------------------
  GATE         214    73%    1.07      0.000      0.59R
  PAPER          6    17%    0.05     -2.879      0.33R

  gradini raggiunti (scala 0.75/1.5/3)
                 n     0 TP     1 TP     2 TP     3 TP
  GATE         214      67%      25%       6%       2%
  PAPER          6      83%      17%       0%       0%

  serie consecutive         perdite   vincite
  GATE                            3        15
  PAPER                           5         1

  GATE: finestre di 6 trade consecutivi TUTTI persi: 0 su 209 (0.0%)
  INGRESSI: 5/6 trade del paper hanno un ingresso del gate entro 2 barre · scarto mediano 16 min
     1 SENZA riscontro: qui il paper e il gate non stanno guardando la stessa soglia
  H5 dal 2026-09-16: gate 5 segnali · aperti dal paper: n 5, PF 0.10, WR 40%, pnl medio -0.014, L/S 5/0 · non aperti: n 0, PF 0.00, WR 0%, pnl medio +0.000, L/S 0/0

── USELESSUSDT|gen_2031005e · scala TP 2/4/6
[backtest] dati da cache: 39024 candele (USELESSUSDT 15m)
                 n    win      PF   PnL/trade   mfe med
  -----------------------------------------------------
  GATE         266    48%    0.80     -0.003      0.91R
  PAPER          6    33%    0.20     -4.689      0.80R

  gradini raggiunti (scala 2/4/6)
                 n     0 TP     1 TP     2 TP     3 TP
  GATE         266      89%       8%       2%       1%
  PAPER          6     100%       0%       0%       0%

  serie consecutive         perdite   vincite
  GATE                            8         9
  PAPER                           3         1

  GATE: finestre di 6 trade consecutivi TUTTI persi: 7 su 261 (2.7%)
  INGRESSI: 3/6 trade del paper hanno un ingresso del gate entro 2 barre · scarto mediano 16 min
     3 SENZA riscontro: qui il paper e il gate non stanno guardando la stessa soglia
  H5 dal 2026-09-16: gate 8 segnali · aperti dal paper: n 3, PF 0.35, WR 33%, pnl medio -0.019, L/S 0/3 · non aperti: n 5, PF 0.26, WR 20%, pnl medio -0.024, L/S 0/5

── DEXEUSDT|gen_fa304106 · scala TP 1.5/3/5
[backtest] dati da cache: 61491 candele (DEXEUSDT 15m)
                 n    win      PF   PnL/trade   mfe med
  -----------------------------------------------------
  GATE         137    65%    1.46      0.003      0.91R
  PAPER          5     0%       —     -1.981      0.52R

  gradini raggiunti (scala 1.5/3/5)
                 n     0 TP     1 TP     2 TP     3 TP
  GATE         137      82%      12%       4%       2%
  PAPER          5     100%       0%       0%       0%

  serie consecutive         perdite   vincite
  GATE                            4        11
  PAPER                           5         0

  GATE: finestre di 5 trade consecutivi TUTTI persi: 0 su 133 (0.0%)
  INGRESSI: 2/5 trade del paper hanno un ingresso del gate entro 2 barre · scarto mediano 16 min
     3 SENZA riscontro: qui il paper e il gate non stanno guardando la stessa soglia
  H5 dal 2026-09-16: gate 4 segnali · aperti dal paper: n 2, PF 0.00, WR 0%, pnl medio -0.010, L/S 0/2 · non aperti: n 2, PF 0.44, WR 50%, pnl medio -0.005, L/S 0/2

── PROMUSDT|gen_cd5c842f · scala TP 2/4/6
[backtest] dati da cache: 59375 candele (PROMUSDT 15m)
                 n    win      PF   PnL/trade   mfe med
  -----------------------------------------------------
  GATE         273    59%    1.07      0.000      1.08R
  PAPER          4    75%    5.11      3.219      2.10R

  gradini raggiunti (scala 2/4/6)
                 n     0 TP     1 TP     2 TP     3 TP
  GATE         273      86%       8%       3%       2%
  PAPER          4      50%      25%      25%       0%

  serie consecutive         perdite   vincite
  GATE                            6        11
  PAPER                           1         2

  GATE: finestre di 4 trade consecutivi TUTTI persi: 7 su 270 (2.6%)
  INGRESSI: 3/4 trade del paper hanno un ingresso del gate entro 2 barre · scarto mediano 16 min
     1 SENZA riscontro: qui il paper e il gate non stanno guardando la stessa soglia
  H5 dal 2026-09-16: gate 4 segnali · aperti dal paper: n 3, PF 1.45, WR 67%, pnl medio +0.002, L/S 1/2 · non aperti: n 1, PF inf, WR 100%, pnl medio +0.023, L/S 0/1

── GPSUSDT|gen_bf1e00d4 · scala TP 1.5/3/5
[backtest] dati da cache: 56189 candele (GPSUSDT 15m)
                 n    win      PF   PnL/trade   mfe med
  -----------------------------------------------------
  GATE         182    59%    1.09      0.001      0.82R
  PAPER          4    75%    4.94      2.310      0.90R

  gradini raggiunti (scala 1.5/3/5)
                 n     0 TP     1 TP     2 TP     3 TP
  GATE         182      86%       8%       3%       3%
  PAPER          4      75%       0%      25%       0%

  serie consecutive         perdite   vincite
  GATE                            5         7
  PAPER                           1         2

  GATE: finestre di 4 trade consecutivi TUTTI persi: 4 su 179 (2.2%)
  INGRESSI: 2/4 trade del paper hanno un ingresso del gate entro 2 barre · scarto mediano 17 min
     2 SENZA riscontro: qui il paper e il gate non stanno guardando la stessa soglia
  H5 dal 2026-09-16: gate 3 segnali · aperti dal paper: n 2, PF 0.32, WR 50%, pnl medio -0.008, L/S 2/0 · non aperti: n 1, PF inf, WR 100%, pnl medio +0.006, L/S 1/0

── TUTUSDT|gen_4465723e · scala TP 1.5/3/5
[backtest] dati da cache: 53245 candele (TUTUSDT 15m)
                 n    win      PF   PnL/trade   mfe med
  -----------------------------------------------------
  GATE         326    60%    1.29      0.003      0.84R
  PAPER          4    75%    2.11      1.204      1.36R

  gradini raggiunti (scala 1.5/3/5)
                 n     0 TP     1 TP     2 TP     3 TP
  GATE         326      78%      16%       4%       3%
  PAPER          4      75%      25%       0%       0%

  serie consecutive         perdite   vincite
  GATE                            5        13
  PAPER                           1         3

  GATE: finestre di 4 trade consecutivi TUTTI persi: 9 su 323 (2.8%)
  INGRESSI: 3/4 trade del paper hanno un ingresso del gate entro 2 barre · scarto mediano 16 min
     1 SENZA riscontro: qui il paper e il gate non stanno guardando la stessa soglia
  H5 dal 2026-09-16: gate 6 segnali · aperti dal paper: n 3, PF inf, WR 100%, pnl medio +0.012, L/S 2/1 · non aperti: n 3, PF inf, WR 100%, pnl medio +0.012, L/S 2/1

── HUMAUSDT|gen_fca11c08 · scala TP 2/4/6
[backtest] dati da cache: 46797 candele (HUMAUSDT 15m)
                 n    win      PF   PnL/trade   mfe med
  -----------------------------------------------------
  GATE          76    63%    1.34      0.003      1.24R
  PAPER          4     0%       —     -3.370      0.10R

  gradini raggiunti (scala 2/4/6)
                 n     0 TP     1 TP     2 TP     3 TP
  GATE          76      84%      16%       0%       0%
  PAPER          4     100%       0%       0%       0%

  serie consecutive         perdite   vincite
  GATE                            3         7
  PAPER                           4         0

  GATE: finestre di 4 trade consecutivi TUTTI persi: 0 su 73 (0.0%)
  INGRESSI: 0/4 trade del paper hanno un ingresso del gate entro 2 barre
     4 SENZA riscontro: qui il paper e il gate non stanno guardando la stessa soglia
  H5 dal 2026-09-16: gate 0 segnali · aperti dal paper: n 0, PF 0.00, WR 0%, pnl medio +0.000, L/S 0/0 · non aperti: n 0, PF 0.00, WR 0%, pnl medio +0.000, L/S 0/0

── SUIUSDT|gen_490a90e5 · scala TP 1/2/3
[backtest] dati da cache: 119169 candele (SUIUSDT 15m)
                 n    win      PF   PnL/trade   mfe med
  -----------------------------------------------------
  GATE         782    68%    0.87     -0.001      0.63R
  PAPER          4    75%    1.23      0.110      0.67R

  gradini raggiunti (scala 1/2/3)
                 n     0 TP     1 TP     2 TP     3 TP
  GATE         782      80%      16%       3%       1%
  PAPER          4     100%       0%       0%       0%

  serie consecutive         perdite   vincite
  GATE                            6        16
  PAPER                           1         3

  GATE: finestre di 4 trade consecutivi TUTTI persi: 13 su 779 (1.7%)
  INGRESSI: 2/4 trade del paper hanno un ingresso del gate entro 2 barre · scarto mediano 17 min
     2 SENZA riscontro: qui il paper e il gate non stanno guardando la stessa soglia
  H5 dal 2026-09-16: gate 12 segnali · aperti dal paper: n 2, PF 0.42, WR 50%, pnl medio -0.006, L/S 0/2 · non aperti: n 10, PF 0.71, WR 60%, pnl medio -0.002, L/S 0/10

==========================================================================
TUTTE LE COPPIE INSIEME, IN ORDINE DI TEMPO
  e' il confronto giusto: i trade persi del paper stanno su strategie diverse,
  e un conto solo li vive uno dopo l'altro, non separati per spec.
==========================================================================
  periodo: 2023-05-10 → 2026-09-25
  GATE: 2256 trade · vinti 1417 (63%) · serie di perdite piu' lunga: 7 · vincite di fila piu' lunga: 16
  GATE: finestre di 112 trade consecutivi TUTTI persi: 0 su 2145 (0.0%)
  GATE: finestre di 8 trade consecutivi TUTTI persi: 0 su 2249 (0.0%)
  PAPER: 112 trade · persi 59 · serie di perdite piu' lunga: 8

==========================================================================
H5 — I SEGNALI DEL GATE NEL PERIODO DEL PAPER
  dal 2026-09-16 (PAPER_START=2026-09-16), sulle 8 coppie rigirate
==========================================================================
  aperti dal paper: n 20, PF 0.45, WR 50%, pnl medio -0.007, L/S 10/10
  non aperti:       n 22, PF 0.66, WR 59%, pnl medio -0.004, L/S 3/19
  Lettura: il gate ha promesso su un regime che non c'e' piu'.
  NB: i trade del gate sono simulati sulla storia INTERA, senza holdout:
      sono una promessa, non una prova. E «aperto» e' un abbinamento nel
      tempo, non la certezza che il paper abbia seguito quel segnale.

==========================================================================
Come si legge. Se il gate ha GIA' attraversato serie lunghe quanto
quella in corso, quello che vediamo e' dentro il suo carattere e il
campione non basta per dire altro. Se non ci e' mai andato vicino,
allora la differenza non e' sfortuna e va cercata nel come operiamo.
Questo comando MISURA e basta: non scrive niente.

--- stderr ---
/root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
  return query.where(field_path, op_string, value)
```
