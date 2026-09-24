# 0211-confronto-h5.req

_eseguito: 2026-09-24 19:26 UTC_

**richiesta:** `confronto`
**eseguito:** `.venv/bin/python -m scripts.confronto_gate_paper`
**esito:** codice 0 in 368.5s

```
[firebase] connesso (Firestore + RTDB)
==========================================================================
SERIE DI PERDITE: quella in corso e' dentro il carattere del gate?
==========================================================================
PAPER: 53 trade chiusi · persi 31 · serie di perdite piu' lunga finora: 8
       coppie che hanno operato: 23

── DEXEUSDT|gen_fa304106 · scala TP 1.5/3/5
[backtest] dati da cache: 61299 candele (DEXEUSDT 15m)
                 n    win      PF   PnL/trade   mfe med
  -----------------------------------------------------
  GATE         137    65%    1.48      0.003      0.91R
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
  H5 dal 2026-09-16: gate 4 segnali · aperti dal paper: n 2, PF 0.00, WR 0%, pnl medio -0.010, L/S 0/2 · non aperti: n 2, PF 2.70, WR 50%, pnl medio +0.002, L/S 0/2

── SPXUSDT|gen_ba3a671f · scala TP 0.75/1.5/3
[backtest] dati da cache: 62638 candele (SPXUSDT 15m)
                 n    win      PF   PnL/trade   mfe med
  -----------------------------------------------------
  GATE         214    73%    1.07      0.000      0.59R
  PAPER          5     0%       —     -3.643      0.30R

  gradini raggiunti (scala 0.75/1.5/3)
                 n     0 TP     1 TP     2 TP     3 TP
  GATE         214      67%      25%       6%       2%
  PAPER          5     100%       0%       0%       0%

  serie consecutive         perdite   vincite
  GATE                            3        15
  PAPER                           5         0

  GATE: finestre di 5 trade consecutivi TUTTI persi: 0 su 210 (0.0%)
  INGRESSI: 5/5 trade del paper hanno un ingresso del gate entro 2 barre · scarto mediano 16 min
  H5 dal 2026-09-16: gate 5 segnali · aperti dal paper: n 5, PF 0.10, WR 40%, pnl medio -0.014, L/S 5/0 · non aperti: n 0, PF 0.00, WR 0%, pnl medio +0.000, L/S 0/0

── USELESSUSDT|gen_2031005e · scala TP 2/4/6
[backtest] dati da cache: 38832 candele (USELESSUSDT 15m)
                 n    win      PF   PnL/trade   mfe med
  -----------------------------------------------------
  GATE          99    60%    1.12      0.002      1.07R
  PAPER          5    20%    0.15     -5.980      0.20R

  gradini raggiunti (scala 2/4/6)
                 n     0 TP     1 TP     2 TP     3 TP
  GATE          99      87%      10%       2%       1%
  PAPER          5     100%       0%       0%       0%

  serie consecutive         perdite   vincite
  GATE                            5        10
  PAPER                           3         1

  GATE: finestre di 5 trade consecutivi TUTTI persi: 1 su 95 (1.1%)
  INGRESSI: 0/5 trade del paper hanno un ingresso del gate entro 2 barre
     5 SENZA riscontro: qui il paper e il gate non stanno guardando la stessa soglia
  H5 dal 2026-09-16: gate 0 segnali · aperti dal paper: n 0, PF 0.00, WR 0%, pnl medio +0.000, L/S 0/0 · non aperti: n 0, PF 0.00, WR 0%, pnl medio +0.000, L/S 0/0

── QUSDT|gen_18c839a0 · scala TP 1.5/3/5
[backtest] dati da cache: 37027 candele (QUSDT 15m)
                 n    win      PF   PnL/trade   mfe med
  -----------------------------------------------------
  GATE          75    73%    1.91      0.006      1.03R
  PAPER          4    75%    0.59     -0.571      1.42R

  gradini raggiunti (scala 1.5/3/5)
                 n     0 TP     1 TP     2 TP     3 TP
  GATE          75      76%      16%       7%       1%
  PAPER          4      75%      25%       0%       0%

  serie consecutive         perdite   vincite
  GATE                            4        12
  PAPER                           1         2

  GATE: finestre di 4 trade consecutivi TUTTI persi: 2 su 72 (2.8%)
  INGRESSI: 1/4 trade del paper hanno un ingresso del gate entro 2 barre · scarto mediano 16 min
     3 SENZA riscontro: qui il paper e il gate non stanno guardando la stessa soglia
  H5 dal 2026-09-16: gate 1 segnali · aperti dal paper: n 1, PF inf, WR 100%, pnl medio +0.005, L/S 0/1 · non aperti: n 0, PF 0.00, WR 0%, pnl medio +0.000, L/S 0/0

── GPSUSDT|gen_bf1e00d4 · scala TP 1.5/3/5
[backtest] dati da cache: 55997 candele (GPSUSDT 15m)
                 n    win      PF   PnL/trade   mfe med
  -----------------------------------------------------
  GATE         181    60%    1.10      0.001      0.82R
  PAPER          3    67%    4.70      2.894      0.81R

  gradini raggiunti (scala 1.5/3/5)
                 n     0 TP     1 TP     2 TP     3 TP
  GATE         181      86%       8%       3%       3%
  PAPER          3      67%       0%      33%       0%

  serie consecutive         perdite   vincite
  GATE                            5         7
  PAPER                           1         1

  GATE: finestre di 3 trade consecutivi TUTTI persi: 9 su 179 (5.0%)
  INGRESSI: 1/3 trade del paper hanno un ingresso del gate entro 2 barre · scarto mediano 16 min
     2 SENZA riscontro: qui il paper e il gate non stanno guardando la stessa soglia
  H5 dal 2026-09-16: gate 2 segnali · aperti dal paper: n 1, PF inf, WR 100%, pnl medio +0.008, L/S 1/0 · non aperti: n 1, PF inf, WR 100%, pnl medio +0.006, L/S 1/0

── DEXEUSDT|gen_b31d8b93 · scala TP 2/4/6
[backtest] dati da cache: 61299 candele (DEXEUSDT 15m)
                 n    win      PF   PnL/trade   mfe med
  -----------------------------------------------------
  GATE         112    56%    1.51      0.005      1.04R
  PAPER          3    33%    0.22     -1.072      1.23R

  gradini raggiunti (scala 2/4/6)
                 n     0 TP     1 TP     2 TP     3 TP
  GATE         112      84%       6%       5%       4%
  PAPER          3      67%      33%       0%       0%

  serie consecutive         perdite   vincite
  GATE                            5         7
  PAPER                           1         1

  GATE: finestre di 3 trade consecutivi TUTTI persi: 15 su 110 (13.6%)
  INGRESSI: 1/3 trade del paper hanno un ingresso del gate entro 2 barre · scarto mediano 16 min
     2 SENZA riscontro: qui il paper e il gate non stanno guardando la stessa soglia
  H5 dal 2026-09-16: gate 1 segnali · aperti dal paper: n 1, PF inf, WR 100%, pnl medio +0.017, L/S 1/0 · non aperti: n 0, PF 0.00, WR 0%, pnl medio +0.000, L/S 0/0

── VETUSDT|gen_6d06dca0 · scala TP 2/4/6
[backtest] dati da cache: 165793 candele (VETUSDT 15m)
                 n    win      PF   PnL/trade   mfe med
  -----------------------------------------------------
  GATE         630    49%    0.84     -0.002      0.97R
  PAPER          3    33%    0.39     -1.789      1.58R

  gradini raggiunti (scala 2/4/6)
                 n     0 TP     1 TP     2 TP     3 TP
  GATE         630      88%       9%       2%       1%
  PAPER          3     100%       0%       0%       0%

  serie consecutive         perdite   vincite
  GATE                            9         7
  PAPER                           2         1

  GATE: finestre di 3 trade consecutivi TUTTI persi: 84 su 628 (13.4%)
  INGRESSI: 3/3 trade del paper hanno un ingresso del gate entro 2 barre · scarto mediano 16 min
  H5 dal 2026-09-16: gate 7 segnali · aperti dal paper: n 3, PF 0.93, WR 67%, pnl medio -0.001, L/S 0/3 · non aperti: n 4, PF 0.39, WR 50%, pnl medio -0.006, L/S 0/4

── STXUSDT|gen_b9bf5d01 · scala TP 2/4/6
[backtest] dati da cache: 125703 candele (STXUSDT 15m)
                 n    win      PF   PnL/trade   mfe med
  -----------------------------------------------------
  GATE         300    56%    1.24      0.002      1.05R
  PAPER          3    33%    0.21     -2.413      0.74R

  gradini raggiunti (scala 2/4/6)
                 n     0 TP     1 TP     2 TP     3 TP
  GATE         300      84%      12%       2%       3%
  PAPER          3     100%       0%       0%       0%

  serie consecutive         perdite   vincite
  GATE                            8         7
  PAPER                           2         1

  GATE: finestre di 3 trade consecutivi TUTTI persi: 22 su 298 (7.4%)
  INGRESSI: 2/3 trade del paper hanno un ingresso del gate entro 2 barre · scarto mediano 17 min
     1 SENZA riscontro: qui il paper e il gate non stanno guardando la stessa soglia
  H5 dal 2026-09-16: gate 4 segnali · aperti dal paper: n 2, PF 0.57, WR 50%, pnl medio -0.004, L/S 2/0 · non aperti: n 2, PF 2.14, WR 50%, pnl medio +0.015, L/S 2/0

==========================================================================
TUTTE LE COPPIE INSIEME, IN ORDINE DI TEMPO
  e' il confronto giusto: i trade persi del paper stanno su strategie diverse,
  e un conto solo li vive uno dopo l'altro, non separati per spec.
==========================================================================
  periodo: 2022-01-05 → 2026-09-23
  GATE: 1748 trade · vinti 1006 (58%) · serie di perdite piu' lunga: 6 · vincite di fila piu' lunga: 19
  GATE: finestre di 53 trade consecutivi TUTTI persi: 0 su 1696 (0.0%)
  GATE: finestre di 8 trade consecutivi TUTTI persi: 0 su 1741 (0.0%)
  PAPER: 53 trade · persi 31 · serie di perdite piu' lunga: 8

==========================================================================
H5 — I SEGNALI DEL GATE NEL PERIODO DEL PAPER
  dal 2026-09-16 (PAPER_START=2026-09-16), sulle 8 coppie rigirate
==========================================================================
  aperti dal paper: n 15, PF 0.50, WR 53%, pnl medio -0.005, L/S 9/6
  non aperti:       n 9, PF 1.23, WR 56%, pnl medio +0.002, L/S 3/6
  Lettura: il difetto e' nel percorso live, non nel mercato.
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
