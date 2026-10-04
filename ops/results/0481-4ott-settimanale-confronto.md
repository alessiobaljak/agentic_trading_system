# 0481-4ott-settimanale-confronto.req

_eseguito: 2026-10-04 07:19 UTC_

**richiesta:** `confronto`
**eseguito:** `.venv/bin/python -m scripts.confronto_gate_paper`
**esito:** codice 0 in 325.4s

```
[firebase] connesso (Firestore + RTDB)
==========================================================================
SERIE DI PERDITE: quella in corso e' dentro il carattere del gate?
==========================================================================
PAPER: 265 trade chiusi · persi 114 · serie di perdite piu' lunga finora: 8
       coppie che hanno operato: 127

── SPXUSDT|gen_ba3a671f · scala TP 0.75/1.5/3
[backtest] dati da cache: 63598 candele (SPXUSDT 15m)
                 n    win      PF   PnL/trade   mfe med
  -----------------------------------------------------
  GATE         217    72%    1.01      0.000      0.58R
  PAPER          7    14%    0.05     -2.697      0.33R

  gradini raggiunti (scala 0.75/1.5/3)
                 n     0 TP     1 TP     2 TP     3 TP
  GATE         217      67%      25%       6%       2%
  PAPER          7      86%      14%       0%       0%

  serie consecutive         perdite   vincite
  GATE                            3        15
  PAPER                           5         1

  GATE: finestre di 7 trade consecutivi TUTTI persi: 0 su 211 (0.0%)
  INGRESSI: 7/7 trade del paper hanno un ingresso del gate entro 2 barre · scarto mediano 16 min
  H5 dal 2026-09-16: gate 9 segnali · aperti dal paper: n 7, PF 0.16, WR 43%, pnl medio -0.012, L/S 7/0 · non aperti: n 2, PF 0.20, WR 50%, pnl medio -0.009, L/S 2/0

── PROMUSDT|gen_cd5c842f · scala TP 2/4/6
[backtest] dati da cache: 60143 candele (PROMUSDT 15m)
                 n    win      PF   PnL/trade   mfe med
  -----------------------------------------------------
  GATE         275    59%    1.08      0.001      1.08R
  PAPER          7    71%    4.16      1.995      1.10R

  gradini raggiunti (scala 2/4/6)
                 n     0 TP     1 TP     2 TP     3 TP
  GATE         275      87%       8%       3%       2%
  PAPER          7      71%      14%      14%       0%

  serie consecutive         perdite   vincite
  GATE                            6        11
  PAPER                           1         4

  GATE: finestre di 7 trade consecutivi TUTTI persi: 0 su 269 (0.0%)
  INGRESSI: 5/7 trade del paper hanno un ingresso del gate entro 2 barre · scarto mediano 17 min
     2 SENZA riscontro: qui il paper e il gate non stanno guardando la stessa soglia
  H5 dal 2026-09-16: gate 6 segnali · aperti dal paper: n 5, PF 2.62, WR 80%, pnl medio +0.005, L/S 3/2 · non aperti: n 1, PF inf, WR 100%, pnl medio +0.023, L/S 0/1

── USELESSUSDT|gen_2031005e · scala TP 2/4/6
[backtest] dati da cache: 39792 candele (USELESSUSDT 15m)
                 n    win      PF   PnL/trade   mfe med
  -----------------------------------------------------
  GATE         106    47%    0.76     -0.004      0.95R
  PAPER          7    43%    0.30     -3.483      0.80R

  gradini raggiunti (scala 2/4/6)
                 n     0 TP     1 TP     2 TP     3 TP
  GATE         106      88%      10%       1%       1%
  PAPER          7     100%       0%       0%       0%

  serie consecutive         perdite   vincite
  GATE                            5         6
  PAPER                           3         2

  GATE: finestre di 7 trade consecutivi TUTTI persi: 0 su 100 (0.0%)
  INGRESSI: 0/7 trade del paper hanno un ingresso del gate entro 2 barre
     7 SENZA riscontro: qui il paper e il gate non stanno guardando la stessa soglia
  H5 dal 2026-09-16: gate 3 segnali · aperti dal paper: n 0, PF 0.00, WR 0%, pnl medio +0.000, L/S 0/0 · non aperti: n 3, PF 0.48, WR 33%, pnl medio -0.015, L/S 1/2

── SUIUSDT|gen_490a90e5 · scala TP 1/2/3
[backtest] dati da cache: 119937 candele (SUIUSDT 15m)
                 n    win      PF   PnL/trade   mfe med
  -----------------------------------------------------
  GATE         292    64%    0.65     -0.003      0.61R
  PAPER          7    71%    1.34      0.173      0.62R

  gradini raggiunti (scala 1/2/3)
                 n     0 TP     1 TP     2 TP     3 TP
  GATE         292      83%      14%       2%       1%
  PAPER          7      86%      14%       0%       0%

  serie consecutive         perdite   vincite
  GATE                            4        11
  PAPER                           1         3

  GATE: finestre di 7 trade consecutivi TUTTI persi: 0 su 286 (0.0%)
  INGRESSI: 0/7 trade del paper hanno un ingresso del gate entro 2 barre
     7 SENZA riscontro: qui il paper e il gate non stanno guardando la stessa soglia
  H5 dal 2026-09-16: gate 2 segnali · aperti dal paper: n 0, PF 0.00, WR 0%, pnl medio +0.000, L/S 0/0 · non aperti: n 2, PF 0.45, WR 50%, pnl medio -0.006, L/S 0/2

── XPLUSDT|gen_e59ad90b · scala TP 1.5/3/5
[backtest] dati da cache: 39131 candele (XPLUSDT 15m)
                 n    win      PF   PnL/trade   mfe med
  -----------------------------------------------------
  GATE         380    64%    1.23      0.002      0.89R
  PAPER          6    67%    1.15      0.117      0.86R

  gradini raggiunti (scala 1.5/3/5)
                 n     0 TP     1 TP     2 TP     3 TP
  GATE         380      82%      14%       3%       1%
  PAPER          6      83%      17%       0%       0%

  serie consecutive         perdite   vincite
  GATE                            7        19
  PAPER                           1         3

  GATE: finestre di 6 trade consecutivi TUTTI persi: 2 su 375 (0.5%)
  INGRESSI: 6/6 trade del paper hanno un ingresso del gate entro 2 barre · scarto mediano 18 min
  H5 dal 2026-09-16: gate 10 segnali · aperti dal paper: n 6, PF 0.99, WR 50%, pnl medio -0.000, L/S 2/4 · non aperti: n 4, PF 0.00, WR 0%, pnl medio -0.028, L/S 1/3

── SYRUPUSDT|gen_4c6df481 · scala TP 2/4/6
[backtest] dati da cache: 49407 candele (SYRUPUSDT 15m)
                 n    win      PF   PnL/trade   mfe med
  -----------------------------------------------------
  GATE         331    58%    1.34      0.003      1.07R
  PAPER          6    67%    2.90      0.926      1.27R

  gradini raggiunti (scala 2/4/6)
                 n     0 TP     1 TP     2 TP     3 TP
  GATE         331      83%      12%       3%       2%
  PAPER          6      83%      17%       0%       0%

  serie consecutive         perdite   vincite
  GATE                            5        11
  PAPER                           2         3

  GATE: finestre di 6 trade consecutivi TUTTI persi: 0 su 326 (0.0%)
  INGRESSI: 5/6 trade del paper hanno un ingresso del gate entro 2 barre · scarto mediano 18 min
     1 SENZA riscontro: qui il paper e il gate non stanno guardando la stessa soglia
  H5 dal 2026-09-16: gate 15 segnali · aperti dal paper: n 5, PF 1.00, WR 60%, pnl medio -0.000, L/S 4/1 · non aperti: n 10, PF 1.19, WR 60%, pnl medio +0.002, L/S 6/4

── TUTUSDT|gen_4465723e · scala TP 1.5/3/5
[backtest] dati da cache: 54013 candele (TUTUSDT 15m)
                 n    win      PF   PnL/trade   mfe med
  -----------------------------------------------------
  GATE         329    60%    1.26      0.002      0.85R
  PAPER          6    83%    2.39      1.004      1.36R

  gradini raggiunti (scala 1.5/3/5)
                 n     0 TP     1 TP     2 TP     3 TP
  GATE         329      78%      16%       4%       3%
  PAPER          6      83%      17%       0%       0%

  serie consecutive         perdite   vincite
  GATE                            5        13
  PAPER                           1         5

  GATE: finestre di 6 trade consecutivi TUTTI persi: 0 su 324 (0.0%)
  INGRESSI: 6/6 trade del paper hanno un ingresso del gate entro 2 barre · scarto mediano 17 min
  H5 dal 2026-09-16: gate 9 segnali · aperti dal paper: n 6, PF inf, WR 100%, pnl medio +0.013, L/S 4/2 · non aperti: n 3, PF inf, WR 100%, pnl medio +0.012, L/S 2/1

── JUPUSDT|gen_bb762669 · scala TP 1.5/3/5
[backtest] dati da cache: 93719 candele (JUPUSDT 15m)
                 n    win      PF   PnL/trade   mfe med
  -----------------------------------------------------
  GATE         205    62%    1.10      0.001      0.85R
  PAPER          5   100%       —      2.351      1.50R

  gradini raggiunti (scala 1.5/3/5)
                 n     0 TP     1 TP     2 TP     3 TP
  GATE         205      83%      12%       4%       1%
  PAPER          5      60%      20%      20%       0%

  serie consecutive         perdite   vincite
  GATE                            4         8
  PAPER                           0         5

  GATE: finestre di 5 trade consecutivi TUTTI persi: 0 su 201 (0.0%)
  INGRESSI: 4/5 trade del paper hanno un ingresso del gate entro 2 barre · scarto mediano 18 min
     1 SENZA riscontro: qui il paper e il gate non stanno guardando la stessa soglia
  H5 dal 2026-09-16: gate 7 segnali · aperti dal paper: n 4, PF inf, WR 100%, pnl medio +0.017, L/S 1/3 · non aperti: n 3, PF inf, WR 100%, pnl medio +0.016, L/S 1/2

==========================================================================
TUTTE LE COPPIE INSIEME, IN ORDINE DI TEMPO
  e' il confronto giusto: i trade persi del paper stanno su strategie diverse,
  e un conto solo li vive uno dopo l'altro, non separati per spec.
==========================================================================
  periodo: 2023-05-08 → 2026-10-03
  GATE: 2135 trade · vinti 1318 (62%) · serie di perdite piu' lunga: 10 · vincite di fila piu' lunga: 13
  GATE: finestre di 265 trade consecutivi TUTTI persi: 0 su 1871 (0.0%)
  GATE: finestre di 8 trade consecutivi TUTTI persi: 3 su 2128 (0.1%)
  PAPER: 265 trade · persi 114 · serie di perdite piu' lunga: 8

==========================================================================
H5 — I SEGNALI DEL GATE NEL PERIODO DEL PAPER
  dal 2026-09-16 (PAPER_START=2026-09-16), sulle 8 coppie rigirate
==========================================================================
  aperti dal paper: n 33, PF 1.36, WR 70%, pnl medio +0.003, L/S 21/12
  non aperti:       n 28, PF 0.80, WR 57%, pnl medio -0.002, L/S 13/15
  Lettura: non distinguibile con questo campione.
  NB: i trade del gate sono simulati sulla storia INTERA, senza holdout:
      sono una promessa, non una prova. E «aperto» e' un abbinamento nel
      tempo, non la certezza che il paper abbia seguito quel segnale.

==========================================================================
Come si legge. Se il gate ha GIA' attraversato serie lunghe quanto
quella in corso, quello che vediamo e' dentro il suo carattere e il
campione non basta per dire altro. Se non ci e' mai andato vicino,
allora la differenza non e' sfortuna e va cercata nel come operiamo.
Questo comando MISURA e basta: non scrive niente.
```
