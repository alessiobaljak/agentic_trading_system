# 0126-confronto-completo.req

_eseguito: 2026-09-21 06:46 UTC_

**richiesta:** `confronto`
**eseguito:** `.venv/bin/python -m scripts.confronto_gate_paper`
**esito:** codice 0 in 394.2s

```
[firebase] connesso (Firestore + RTDB)
==========================================================================
SERIE DI PERDITE: quella in corso e' dentro il carattere del gate?
==========================================================================
PAPER: 21 trade chiusi · persi 16 · serie di perdite piu' lunga finora: 6
       coppie che hanno operato: 12

── DEXEUSDT|gen_fa304106 · scala TP 1.5/3/5
[backtest] dati da cache: 60915 candele (DEXEUSDT 15m)
                 n    win      PF   PnL/trade   mfe med
  -----------------------------------------------------
  GATE         137    52%    1.51      0.005      1.43R
  PAPER          4     0%       —     -2.102      0.52R

  gradini raggiunti (scala 1.5/3/5)
                 n     0 TP     1 TP     2 TP     3 TP
  GATE         137      51%      31%      11%       7%
  PAPER          4     100%       0%       0%       0%

  serie consecutive         perdite   vincite
  GATE                            6         7
  PAPER                           4         0

  GATE: finestre di 4 trade consecutivi TUTTI persi: 6 su 134 (4.5%)
  INGRESSI: 0/4 trade del paper hanno un ingresso del gate entro 2 barre
     4 SENZA riscontro: qui il paper e il gate non stanno guardando la stessa soglia

── SPXUSDT|gen_ba3a671f · scala TP 0.75/1.5/3
[backtest] dati da cache: 62254 candele (SPXUSDT 15m)
                 n    win      PF   PnL/trade   mfe med
  -----------------------------------------------------
  GATE         228    64%    1.34      0.003      0.96R
  PAPER          3     0%       —     -4.184      0.30R

  gradini raggiunti (scala 0.75/1.5/3)
                 n     0 TP     1 TP     2 TP     3 TP
  GATE         228      36%      27%      26%      10%
  PAPER          3     100%       0%       0%       0%

  serie consecutive         perdite   vincite
  GATE                            7        12
  PAPER                           3         0

  GATE: finestre di 3 trade consecutivi TUTTI persi: 9 su 226 (4.0%)
  INGRESSI: 0/3 trade del paper hanno un ingresso del gate entro 2 barre
     3 SENZA riscontro: qui il paper e il gate non stanno guardando la stessa soglia

── ORCAUSDT|gen_6d06dca0 · scala TP 1.5/3/5
[backtest] dati da cache: 62629 candele (ORCAUSDT 15m)
                 n    win      PF   PnL/trade   mfe med
  -----------------------------------------------------
  GATE         298    41%    0.91     -0.001      1.02R
  PAPER          2     0%       —     -3.005      1.05R

  gradini raggiunti (scala 1.5/3/5)
                 n     0 TP     1 TP     2 TP     3 TP
  GATE         298      60%      26%      11%       3%
  PAPER          2     100%       0%       0%       0%

  serie consecutive         perdite   vincite
  GATE                           11         7
  PAPER                           2         0

  GATE: finestre di 2 trade consecutivi TUTTI persi: 107 su 297 (36.0%)
  INGRESSI: 0/2 trade del paper hanno un ingresso del gate entro 2 barre
     2 SENZA riscontro: qui il paper e il gate non stanno guardando la stessa soglia

── DEXEUSDT|gen_b31d8b93 · scala TP 1.5/3/5
[backtest] dati da cache: 60915 candele (DEXEUSDT 15m)
                 n    win      PF   PnL/trade   mfe med
  -----------------------------------------------------
  GATE         119    53%    1.63      0.008      1.22R
  PAPER          2    50%    0.37     -0.760      2.03R

  gradini raggiunti (scala 1.5/3/5)
                 n     0 TP     1 TP     2 TP     3 TP
  GATE         119      60%      25%       8%       7%
  PAPER          2      50%      50%       0%       0%

  serie consecutive         perdite   vincite
  GATE                            5         6
  PAPER                           1         1

  GATE: finestre di 2 trade consecutivi TUTTI persi: 27 su 118 (22.9%)
  INGRESSI: 0/2 trade del paper hanno un ingresso del gate entro 2 barre
     2 SENZA riscontro: qui il paper e il gate non stanno guardando la stessa soglia

── VETUSDT|gen_6d06dca0 · scala TP 2/4/6
[backtest] dati da cache: 165409 candele (VETUSDT 15m)
                 n    win      PF   PnL/trade   mfe med
  -----------------------------------------------------
  GATE         735    34%    0.90     -0.001      0.95R
  PAPER          2     0%       —     -4.373      1.58R

  gradini raggiunti (scala 2/4/6)
                 n     0 TP     1 TP     2 TP     3 TP
  GATE         735      71%      20%       5%       3%
  PAPER          2     100%       0%       0%       0%

  serie consecutive         perdite   vincite
  GATE                           13         7
  PAPER                           2         0

  GATE: finestre di 2 trade consecutivi TUTTI persi: 330 su 734 (45.0%)
  INGRESSI: 0/2 trade del paper hanno un ingresso del gate entro 2 barre
     2 SENZA riscontro: qui il paper e il gate non stanno guardando la stessa soglia

── SYRUPUSDT|gen_af734c68 · scala TP 2/4/6
[backtest] dati da cache: 48063 candele (SYRUPUSDT 15m)
                 n    win      PF   PnL/trade   mfe med
  -----------------------------------------------------
  GATE         133    38%    0.98     -0.000      1.07R
  PAPER          2     0%       —     -1.949      0.94R

  gradini raggiunti (scala 2/4/6)
                 n     0 TP     1 TP     2 TP     3 TP
  GATE         133      62%      23%      10%       5%
  PAPER          2     100%       0%       0%       0%

  serie consecutive         perdite   vincite
  GATE                           13         6
  PAPER                           2         0

  GATE: finestre di 2 trade consecutivi TUTTI persi: 57 su 132 (43.2%)
  INGRESSI: 0/2 trade del paper hanno un ingresso del gate entro 2 barre
     2 SENZA riscontro: qui il paper e il gate non stanno guardando la stessa soglia

── PROMUSDT|gen_cd5c842f · scala TP 2/4/6
[backtest] dati da cache: 58799 candele (PROMUSDT 15m)
                 n    win      PF   PnL/trade   mfe med
  -----------------------------------------------------
  GATE         260    42%    1.80      0.007      1.53R
  PAPER          1   100%       —     10.478      5.96R

  gradini raggiunti (scala 2/4/6)
                 n     0 TP     1 TP     2 TP     3 TP
  GATE         260      61%      25%       9%       5%
  PAPER          1       0%       0%     100%       0%

  serie consecutive         perdite   vincite
  GATE                           10         6
  PAPER                           0         1

  GATE: finestre di 1 trade consecutivi TUTTI persi: 150 su 260 (57.7%)
  INGRESSI: 0/1 trade del paper hanno un ingresso del gate entro 2 barre
     1 SENZA riscontro: qui il paper e il gate non stanno guardando la stessa soglia

── BICOUSDT|gen_f238d283 · scala TP 1.5/3/5
[backtest] dati da cache: 104399 candele (BICOUSDT 15m)
                 n    win      PF   PnL/trade   mfe med
  -----------------------------------------------------
  GATE         396    39%    1.09      0.001      0.91R
  PAPER          1   100%       —      1.169      2.36R

  gradini raggiunti (scala 1.5/3/5)
                 n     0 TP     1 TP     2 TP     3 TP
  GATE         396      65%      22%      10%       3%
  PAPER          1       0%     100%       0%       0%

  serie consecutive         perdite   vincite
  GATE                           10         5
  PAPER                           0         1

  GATE: finestre di 1 trade consecutivi TUTTI persi: 242 su 396 (61.1%)
  INGRESSI: 0/1 trade del paper hanno un ingresso del gate entro 2 barre
     1 SENZA riscontro: qui il paper e il gate non stanno guardando la stessa soglia

==========================================================================
TUTTE LE COPPIE INSIEME, IN ORDINE DI TEMPO
  e' il confronto giusto: i trade persi del paper stanno su strategie diverse,
  e un conto solo li vive uno dopo l'altro, non separati per spec.
==========================================================================
  periodo: 2022-01-05 → 2026-09-19
  GATE: 2306 trade · vinti 964 (42%) · serie di perdite piu' lunga: 15 · vincite di fila piu' lunga: 10
  GATE: finestre di 21 trade consecutivi TUTTI persi: 0 su 2286 (0.0%)
  GATE: finestre di 6 trade consecutivi TUTTI persi: 132 su 2301 (5.7%)
  PAPER: 21 trade · persi 16 · serie di perdite piu' lunga: 6

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
