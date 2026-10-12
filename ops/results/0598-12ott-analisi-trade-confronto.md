# 0598-12ott-analisi-trade-confronto.req

_eseguito: 2026-10-12 16:58 UTC_

**richiesta:** `confronto`
**eseguito:** `.venv/bin/python -m scripts.confronto_gate_paper`
**esito:** codice 0 in 268.8s

```
[firebase] connesso (Firestore + RTDB)
==========================================================================
SERIE DI PERDITE: quella in corso e' dentro il carattere del gate?
==========================================================================
PAPER: 506 trade chiusi · persi 226 · serie di perdite piu' lunga finora: 8
       coppie che hanno operato: 228

── ZORAUSDT|gen_ceab7f6a · scala TP 1.5/3/5
[backtest] dati da cache: 42581 candele (ZORAUSDT 15m)
                 n    win      PF   PnL/trade   mfe med
  -----------------------------------------------------
  GATE         333    60%    1.03      0.000      0.84R
  PAPER         15    53%    0.53     -0.240      0.76R

  gradini raggiunti (scala 1.5/3/5)
                 n     0 TP     1 TP     2 TP     3 TP
  GATE         333      80%      15%       4%       1%
  PAPER         15      87%      13%       0%       0%

  serie consecutive         perdite   vincite
  GATE                            5         8
  PAPER                           5         5

  GATE: finestre di 15 trade consecutivi TUTTI persi: 0 su 319 (0.0%)
  INGRESSI: 15/15 trade del paper hanno un ingresso del gate entro 2 barre · scarto mediano 18 min
  H5 dal 2026-09-16: gate 24 segnali · aperti dal paper: n 15, PF 0.56, WR 53%, pnl medio -0.003, L/S 14/1 · non aperti: n 9, PF 1.80, WR 67%, pnl medio +0.005, L/S 8/1

── SYRUPUSDT|gen_4c6df481 · scala TP 2/4/6
[backtest] dati da cache: 50079 candele (SYRUPUSDT 15m)
                 n    win      PF   PnL/trade   mfe med
  -----------------------------------------------------
  GATE         334    58%    1.29      0.003      1.07R
  PAPER         10    50%    1.06      0.048      1.01R

  gradini raggiunti (scala 2/4/6)
                 n     0 TP     1 TP     2 TP     3 TP
  GATE         334      83%      13%       3%       1%
  PAPER         10      90%      10%       0%       0%

  serie consecutive         perdite   vincite
  GATE                            5        11
  PAPER                           2         3

  GATE: finestre di 10 trade consecutivi TUTTI persi: 0 su 325 (0.0%)
  INGRESSI: 8/10 trade del paper hanno un ingresso del gate entro 2 barre · scarto mediano 18 min
     2 SENZA riscontro: qui il paper e il gate non stanno guardando la stessa soglia
  H5 dal 2026-09-16: gate 18 segnali · aperti dal paper: n 8, PF 0.67, WR 50%, pnl medio -0.003, L/S 7/1 · non aperti: n 10, PF 1.15, WR 60%, pnl medio +0.001, L/S 6/4

── PROMUSDT|gen_cd5c842f · scala TP 1.5/3/5
[backtest] dati da cache: 60815 candele (PROMUSDT 15m)
                 n    win      PF   PnL/trade   mfe med
  -----------------------------------------------------
  GATE         288    67%    1.24      0.001      0.88R
  PAPER         10    70%    3.81      1.458      1.17R

  gradini raggiunti (scala 1.5/3/5)
                 n     0 TP     1 TP     2 TP     3 TP
  GATE         288      80%      14%       3%       3%
  PAPER         10      70%      20%       0%      10%

  serie consecutive         perdite   vincite
  GATE                            6        15
  PAPER                           1         4

  GATE: finestre di 10 trade consecutivi TUTTI persi: 0 su 279 (0.0%)
  INGRESSI: 8/10 trade del paper hanno un ingresso del gate entro 2 barre · scarto mediano 18 min
     2 SENZA riscontro: qui il paper e il gate non stanno guardando la stessa soglia
  H5 dal 2026-09-16: gate 11 segnali · aperti dal paper: n 8, PF 2.68, WR 88%, pnl medio +0.008, L/S 3/5 · non aperti: n 3, PF 0.33, WR 33%, pnl medio -0.014, L/S 1/2

── XPLUSDT|gen_e59ad90b · scala TP 1.5/3/5
[backtest] dati da cache: 39803 candele (XPLUSDT 15m)
                 n    win      PF   PnL/trade   mfe med
  -----------------------------------------------------
  GATE         384    64%    1.20      0.002      0.88R
  PAPER         10    60%    0.96     -0.027      0.82R

  gradini raggiunti (scala 1.5/3/5)
                 n     0 TP     1 TP     2 TP     3 TP
  GATE         384      82%      14%       3%       1%
  PAPER         10      90%      10%       0%       0%

  serie consecutive         perdite   vincite
  GATE                            7        19
  PAPER                           2         3

  GATE: finestre di 10 trade consecutivi TUTTI persi: 0 su 375 (0.0%)
  INGRESSI: 10/10 trade del paper hanno un ingresso del gate entro 2 barre · scarto mediano 18 min
  H5 dal 2026-09-16: gate 14 segnali · aperti dal paper: n 10, PF 0.69, WR 40%, pnl medio -0.004, L/S 4/6 · non aperti: n 4, PF 0.00, WR 0%, pnl medio -0.028, L/S 1/3

── TUTUSDT|gen_4465723e · scala TP 1.5/3/5
[backtest] dati da cache: 54685 candele (TUTUSDT 15m)
                 n    win      PF   PnL/trade   mfe med
  -----------------------------------------------------
  GATE         333    60%    1.26      0.002      0.85R
  PAPER          9    78%    2.11      0.699      1.29R

  gradini raggiunti (scala 1.5/3/5)
                 n     0 TP     1 TP     2 TP     3 TP
  GATE         333      78%      16%       4%       3%
  PAPER          9      89%      11%       0%       0%

  serie consecutive         perdite   vincite
  GATE                            5        13
  PAPER                           1         5

  GATE: finestre di 9 trade consecutivi TUTTI persi: 0 su 325 (0.0%)
  INGRESSI: 9/9 trade del paper hanno un ingresso del gate entro 2 barre · scarto mediano 18 min
  H5 dal 2026-09-16: gate 13 segnali · aperti dal paper: n 9, PF 6.37, WR 89%, pnl medio +0.010, L/S 6/3 · non aperti: n 4, PF 2.07, WR 75%, pnl medio +0.005, L/S 3/1

── QUSDT|gen_18c839a0 · scala TP 1.5/3/5
[backtest] dati da cache: 38755 candele (QUSDT 15m)
                 n    win      PF   PnL/trade   mfe med
  -----------------------------------------------------
  GATE          83    72%    1.76      0.005      1.03R
  PAPER          8    50%    0.42     -0.884      0.90R

  gradini raggiunti (scala 1.5/3/5)
                 n     0 TP     1 TP     2 TP     3 TP
  GATE          83      76%      17%       6%       1%
  PAPER          8      88%      12%       0%       0%

  serie consecutive         perdite   vincite
  GATE                            4        12
  PAPER                           3         3

  GATE: finestre di 8 trade consecutivi TUTTI persi: 0 su 76 (0.0%)
  INGRESSI: 6/8 trade del paper hanno un ingresso del gate entro 2 barre · scarto mediano 16 min
     2 SENZA riscontro: qui il paper e il gate non stanno guardando la stessa soglia
  H5 dal 2026-09-16: gate 9 segnali · aperti dal paper: n 6, PF 0.51, WR 67%, pnl medio -0.006, L/S 1/5 · non aperti: n 3, PF 0.88, WR 67%, pnl medio -0.001, L/S 2/1

── SPXUSDT|gen_ba3a671f · scala TP 1.5/3/5
[backtest] dati da cache: 64270 candele (SPXUSDT 15m)
                 n    win      PF   PnL/trade   mfe med
  -----------------------------------------------------
  GATE         214    60%    1.00     -0.000      0.85R
  PAPER          7    14%    0.05     -2.697      0.33R

  gradini raggiunti (scala 1.5/3/5)
                 n     0 TP     1 TP     2 TP     3 TP
  GATE         214      81%      14%       3%       1%
  PAPER          7     100%       0%       0%       0%

  serie consecutive         perdite   vincite
  GATE                            5        12
  PAPER                           5         1

  GATE: finestre di 7 trade consecutivi TUTTI persi: 0 su 208 (0.0%)
  INGRESSI: 6/7 trade del paper hanno un ingresso del gate entro 2 barre · scarto mediano 16 min
     1 SENZA riscontro: qui il paper e il gate non stanno guardando la stessa soglia
  H5 dal 2026-09-16: gate 12 segnali · aperti dal paper: n 6, PF 0.06, WR 17%, pnl medio -0.020, L/S 6/0 · non aperti: n 6, PF 0.78, WR 50%, pnl medio -0.002, L/S 6/0

── USELESSUSDT|gen_2031005e · scala TP 2/4/6
[backtest] dati da cache: 40464 candele (USELESSUSDT 15m)
                 n    win      PF   PnL/trade   mfe med
  -----------------------------------------------------
  GATE         107    48%    0.77     -0.004      0.95R
  PAPER          7    43%    0.30     -3.483      0.80R

  gradini raggiunti (scala 2/4/6)
                 n     0 TP     1 TP     2 TP     3 TP
  GATE         107      87%      11%       1%       1%
  PAPER          7     100%       0%       0%       0%

  serie consecutive         perdite   vincite
  GATE                            5         6
  PAPER                           3         2

  GATE: finestre di 7 trade consecutivi TUTTI persi: 0 su 101 (0.0%)
  INGRESSI: 0/7 trade del paper hanno un ingresso del gate entro 2 barre
     7 SENZA riscontro: qui il paper e il gate non stanno guardando la stessa soglia
  H5 dal 2026-09-16: gate 4 segnali · aperti dal paper: n 0, PF 0.00, WR 0%, pnl medio +0.000, L/S 0/0 · non aperti: n 4, PF 0.93, WR 50%, pnl medio -0.002, L/S 1/3

==========================================================================
TUTTE LE COPPIE INSIEME, IN ORDINE DI TEMPO
  e' il confronto giusto: i trade persi del paper stanno su strategie diverse,
  e un conto solo li vive uno dopo l'altro, non separati per spec.
==========================================================================
  periodo: 2024-12-14 → 2026-10-11
  GATE: 2076 trade · vinti 1272 (61%) · serie di perdite piu' lunga: 9 · vincite di fila piu' lunga: 10
  GATE: finestre di 506 trade consecutivi TUTTI persi: 0 su 1571 (0.0%)
  GATE: finestre di 8 trade consecutivi TUTTI persi: 3 su 2069 (0.1%)
  PAPER: 506 trade · persi 226 · serie di perdite piu' lunga: 8

==========================================================================
H5 — I SEGNALI DEL GATE NEL PERIODO DEL PAPER
  dal 2026-09-16 (PAPER_START=2026-09-16), sulle 8 coppie rigirate
==========================================================================
  aperti dal paper: n 62, PF 0.80, WR 58%, pnl medio -0.002, L/S 41/21
  non aperti:       n 43, PF 0.79, WR 53%, pnl medio -0.002, L/S 28/15
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
```
