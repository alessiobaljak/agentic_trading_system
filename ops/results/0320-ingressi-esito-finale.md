# 0320-ingressi-esito-finale.req

_eseguito: 2026-09-27 20:49 UTC_

**richiesta:** `ingressi-esito`
**eseguito:** `.venv/bin/python -m scripts.ingressi_report --esito`
**esito:** codice 0 in 1.4s

```
[ingressi] referto /root/agentic_trading_system/data/ingressi_ultimo.txt · scritto 2026-09-27 20:46:52 UTC · processo 1785970 finito
--------------------------------------------------------------------------
[firebase] connesso (Firestore + RTDB)
[ingressi] su file, pid 1785970, avvio 2026-09-27 19:56:23 UTC
/root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
  return query.where(field_path, op_string, value)
==========================================================================
INGRESSI DEL PAPER, TRADE PER TRADE: dove il motore non entra, e perche'
==========================================================================
PAPER: 135 trade chiusi su 66 coppie · rigirate 66 · tolleranza 2 barre · deadline nessuna

── SUIUSDT|gen_490a90e5 · 7 trade · 15m · scala 1/2/3 · BE si · keep globale
[backtest] cache ESTESA di 176 candele (invece di riscaricarne 119344) (SUIUSDT 15m)
[backtest] dati da cache: 119344 candele (SUIUSDT 15m)
  motore: 292 trade sulla storia intera, 0 dal primo trade del paper · cooldown 4 barre
  #1  25 Sep 10:45 UTC  short entry 1.069  pnl -1.93 USDT (stop_loss)
       REGOLA_NON_SCATTA · IGNOTO: stessi valori e la regola non scatta neanche sui valori del paper
       regola sul frame del motore: k-1 no · k no · k+1 no · con 199 candele no · sui valori del paper no · regime motore bull_trending / paper bull_trending
  #2  25 Sep 12:00 UTC  short entry 1.131  pnl +0.70 USDT (trailing_stop)
       REGOLA_NON_SCATTA · IGNOTO: stessi valori e la regola non scatta neanche sui valori del paper
       regola sul frame del motore: k-1 no · k no · k+1 no · con 199 candele no · sui valori del paper no · regime motore bull_trending / paper bull_trending
  #3  25 Sep 12:15 UTC  short entry 1.135  pnl +0.55 USDT (trailing_stop)
       REGOLA_NON_SCATTA · IGNOTO: stessi valori e la regola non scatta neanche sui valori del paper
       regola sul frame del motore: k-1 no · k no · k+1 no · con 199 candele no · sui valori del paper no · regime motore bull_trending / paper bull_trending
  #4  25 Sep 13:30 UTC  short entry 1.127  pnl +1.12 USDT (trailing_stop)
       REGOLA_NON_SCATTA · IGNOTO: stessi valori e la regola non scatta neanche sui valori del paper
       regola sul frame del motore: k-1 no · k no · k+1 no · con 199 candele no · sui valori del paper no · regime motore bull_trending / paper bull_trending
  #5  27 Sep 06:15 UTC  short entry 1.198  pnl -1.59 USDT (stop_loss)
       REGOLA_NON_SCATTA · IGNOTO: stessi valori e la regola non scatta neanche sui valori del paper
       regola sul frame del motore: k-1 no · k no · k+1 no · con 199 candele no · sui valori del paper no · regime motore sideways / paper sideways
  #6  27 Sep 08:30 UTC  short entry 1.269  pnl +1.64 USDT (scale_out)
       REGOLA_NON_SCATTA · IGNOTO: stessi valori e la regola non scatta neanche sui valori del paper
       regola sul frame del motore: k-1 no · k no · k+1 no · con 199 candele no · sui valori del paper no · regime motore bull_trending / paper bull_trending
  #7  27 Sep 09:00 UTC  short entry 1.256  pnl +0.73 USDT (trailing_stop)
       REGOLA_NON_SCATTA · IGNOTO: stessi valori e la regola non scatta neanche sui valori del paper
       regola sul frame del motore: k-1 no · k no · k+1 no · con 199 candele no · sui valori del paper no · regime motore bull_trending / paper bull_trending
  ABBINATI 0/7 · «come il bot» (da 200 barre prima del paper): 0/7 abbinati, 0 trade del motore
  [75s]

── USELESSUSDT|gen_2031005e · 7 trade · 15m · scala 2/4/6 · BE si · keep globale
[backtest] cache ESTESA di 176 candele (invece di riscaricarne 39199) (USELESSUSDT 15m)
[backtest] dati da cache: 39199 candele (USELESSUSDT 15m)
  motore: 105 trade sulla storia intera, 1 dal primo trade del paper · cooldown 4 barre
  #1  21 Sep 08:30 UTC  short entry 0.2548  pnl -8.25 USDT (stop_loss)
       REGOLA_NON_SCATTA · IGNOTO: stessi valori e la regola non scatta neanche sui valori del paper
       regola sul frame del motore: k-1 no · k no · k+1 no · con 199 candele no · sui valori del paper no · regime motore high_uncertainty / paper high_uncertainty
  #2  21 Sep 08:45 UTC  short entry 0.2651  pnl -8.65 USDT (stop_loss)
       REGOLA_NON_SCATTA · IGNOTO: stessi valori e la regola non scatta neanche sui valori del paper
       regola sul frame del motore: k-1 no · k no · k+1 no · con 199 candele no · sui valori del paper no · regime motore high_uncertainty / paper high_uncertainty
  #3  21 Sep 09:15 UTC  short entry 0.2765  pnl -8.97 USDT (stop_loss)
       REGOLA_NON_SCATTA · IGNOTO: stessi valori e la regola non scatta neanche sui valori del paper
       regola sul frame del motore: k-1 no · k no · k+1 no · con 199 candele no · sui valori del paper no · regime motore high_uncertainty / paper high_uncertainty
  #4  21 Sep 10:15 UTC  short entry 0.2862  pnl +5.11 USDT (trailing_stop)
       REGOLA_NON_SCATTA · IGNOTO: stessi valori e la regola non scatta neanche sui valori del paper
       regola sul frame del motore: k-1 no · k no · k+1 no · con 199 candele no · sui valori del paper no · regime motore bull_trending / paper high_uncertainty
  #5  22 Sep 08:00 UTC  short entry 0.3014  pnl -9.14 USDT (stop_loss)
       REGOLA_NON_SCATTA · IGNOTO: stessi valori e la regola non scatta neanche sui valori del paper
       regola sul frame del motore: k-1 no · k no · k+1 no · con 199 candele no · sui valori del paper no · regime motore high_uncertainty / paper high_uncertainty
  #6  25 Sep 12:45 UTC  short entry 0.307  pnl +1.76 USDT (trailing_stop)
       REGOLA_NON_SCATTA · IGNOTO: stessi valori e la regola non scatta neanche sui valori del paper
       regola sul frame del motore: k-1 no · k no · k+1 no · con 199 candele no · sui valori del paper no · regime motore bull_trending / paper bull_trending
  #7  27 Sep 11:15 UTC  short entry 0.3028  pnl +3.75 USDT (trailing_stop)
       REGOLA_NON_SCATTA · IGNOTO: stessi valori e la regola non scatta neanche sui valori del paper
       regola sul frame del motore: k-1 no · k no · k+1 no · con 199 candele no · sui valori del paper no · regime motore bull_trending / paper bull_trending
  ABBINATI 0/7 · «come il bot» (da 200 barre prima del paper): 0/7 abbinati, 1 trade del motore
  [100s]

── SPXUSDT|gen_ba3a671f · 6 trade · 15m · scala 0.75/1.5/3 · BE si · keep globale
[backtest] cache ESTESA di 176 candele (invece di riscaricarne 63005) (SPXUSDT 15m)
[backtest] dati da cache: 63005 candele (SPXUSDT 15m)
  motore: 215 trade sulla storia intera, 6 dal primo trade del paper · cooldown 4 barre
  #1  16 Sep 15:30 UTC  long  entry 0.453  pnl -4.19 USDT (stop_loss)
       ABBINATO: motore alla barra 16 Sep 15:30 (+0 min), direzione uguale
  #2  20 Sep 02:45 UTC  long  entry 0.4626  pnl -4.83 USDT (stop_loss)
       ABBINATO: motore alla barra 20 Sep 02:45 (+0 min), direzione uguale
  #3  20 Sep 08:15 UTC  long  entry 0.4539  pnl -3.53 USDT (stop_loss)
       ABBINATO: motore alla barra 20 Sep 08:15 (+0 min), direzione uguale
  #4  23 Sep 10:15 UTC  long  entry 0.4953  pnl -4.42 USDT (stop_loss)
       ABBINATO: motore alla barra 23 Sep 10:15 (+0 min), direzione uguale
  #5  23 Sep 16:00 UTC  long  entry 0.4571  pnl -1.24 USDT (stop_loss)
       ABBINATO: motore alla barra 23 Sep 16:00 (+0 min), direzione uguale
  #6  26 Sep 20:45 UTC  long  entry 0.448  pnl +0.94 USDT (scale_out)
       ABBINATO: motore alla barra 26 Sep 20:45 (+0 min), direzione uguale
  ABBINATI 6/6 · «come il bot» (da 200 barre prima del paper): 6/6 abbinati, 6 trade del motore
  [137s]

── DEXEUSDT|gen_fa304106 · 5 trade · 15m · scala 1.5/3/5 · BE si · keep globale
[backtest] cache ESTESA di 176 candele (invece di riscaricarne 61666) (DEXEUSDT 15m)
[backtest] dati da cache: 61666 candele (DEXEUSDT 15m)
  motore: 137 trade sulla storia intera, 4 dal primo trade del paper · cooldown 4 barre
  #1  17 Sep 10:15 UTC  short entry 1.794  pnl -2.02 USDT (stop_loss)
       ABBINATO: motore alla barra 17 Sep 10:30 (+15 min), direzione uguale
  #2  19 Sep 11:00 UTC  short entry 1.854  pnl -2.01 USDT (stop_loss)
       ABBINATO: motore alla barra 19 Sep 11:00 (+0 min), direzione uguale
  #3  20 Sep 16:00 UTC  short entry 1.839  pnl -2.17 USDT (stop_loss)
       REGOLA_NON_SCATTA · IGNOTO: stessi valori e la regola non scatta neanche sui valori del paper
       regola sul frame del motore: k-1 no · k no · k+1 no · con 199 candele si · sui valori del paper no · regime motore bear_trending / paper bear_trending
  #4  21 Sep 01:30 UTC  long  entry 1.861  pnl -2.21 USDT (stop_loss)
       REGOLA_NON_SCATTA · IGNOTO: stessi valori e la regola non scatta neanche sui valori del paper
       regola sul frame del motore: k-1 no · k no · k+1 no · con 199 candele si · sui valori del paper no · regime motore sideways / paper sideways
  #5  24 Sep 00:00 UTC  short entry 1.885  pnl -1.50 USDT (stop_loss)
       MOTORE_IN_POSIZIONE: dentro il trade del 23 Sep 23:45 (short, uscito 24 Sep 05:00, stop dedotto, -1.63%): cascata di un'uscita diversa, non della regola d'ingresso
  ABBINATI 2/5 · «come il bot» (da 200 barre prima del paper): 2/5 abbinati, 4 trade del motore
  [174s]

── ORCAUSDT|gen_fca11c08 · 5 trade · 15m · scala 1.5/3/5 · BE si · keep globale
[backtest] cache ESTESA di 81 candele (invece di riscaricarne 63380) (ORCAUSDT 15m)
[backtest] dati da cache: 63380 candele (ORCAUSDT 15m)
  motore: 222 trade sulla storia intera, 1 dal primo trade del paper · cooldown 4 barre
  #1  25 Sep 08:45 UTC  short entry 1.615  pnl -1.61 USDT (stop_loss)
       REGOLA_NON_SCATTA · IGNOTO: stessi valori e la regola non scatta neanche sui valori del paper
       regola sul frame del motore: k-1 no · k no · k+1 no · con 199 candele no · sui valori del paper no · regime motore bull_trending / paper bull_trending
  #2  25 Sep 20:30 UTC  short entry 1.672  pnl +1.97 USDT (trailing_stop)
       REGOLA_NON_SCA

[... 45842 caratteri omessi (testa e coda conservate) ...]

41 candele (XPLUSDT 15m)
  motore: 27 trade sulla storia intera, 0 dal primo trade del paper · cooldown 4 barre
  #1  24 Sep 23:30 UTC  short entry 0.1119  pnl -3.47 USDT (stop_loss)
       REGOLA_NON_SCATTA · IGNOTO: stessi valori e la regola non scatta neanche sui valori del paper
       regola sul frame del motore: k-1 no · k no · k+1 no · con 199 candele no · sui valori del paper no · regime motore bull_trending / paper bull_trending
  ABBINATI 0/1 · «come il bot» (da 200 barre prima del paper): 0/1 abbinati, 0 trade del motore
  [2704s]

── XPLUSDT|gen_b437a671 · 1 trade · 15m · scala 2/4/6 · BE si · keep globale
[backtest] dati da cache: 38541 candele (XPLUSDT 15m)
[backtest] dati da cache: 38541 candele (XPLUSDT 15m)
  motore: 186 trade sulla storia intera, 0 dal primo trade del paper · cooldown 4 barre
  #1  25 Sep 07:15 UTC  short entry 0.1164  pnl -3.46 USDT (stop_loss)
       REGOLA_NON_SCATTA · IGNOTO: stessi valori e la regola non scatta neanche sui valori del paper
       regola sul frame del motore: k-1 no · k no · k+1 no · con 199 candele no · sui valori del paper no · regime motore bull_trending / paper bull_trending
  ABBINATI 0/1 · «come il bot» (da 200 barre prima del paper): 0/1 abbinati, 0 trade del motore
  [2726s]

── XPLUSDT|gen_e59ad90b · 1 trade · 15m · scala 1.5/3/5 · BE si · keep globale
[backtest] dati da cache: 38541 candele (XPLUSDT 15m)
[backtest] dati da cache: 38541 candele (XPLUSDT 15m)
  motore: 375 trade sulla storia intera, 1 dal primo trade del paper · cooldown 4 barre
  #1  26 Sep 16:00 UTC  short entry 0.1177  pnl +3.89 USDT (scale_out)
       ABBINATO: motore alla barra 26 Sep 16:00 (+0 min), direzione uguale
  ABBINATI 1/1 · «come il bot» (da 200 barre prima del paper): 1/1 abbinati, 1 trade del motore
  [2749s]

── XRPUSDT|gen_50905b4a · 1 trade · 15m · scala globale · BE si · keep globale
[backtest] cache ESTESA di 179 candele (invece di riscaricarne 166163) (XRPUSDT 15m)
[backtest] dati da cache: 166163 candele (XRPUSDT 15m)
  motore: 291 trade sulla storia intera, 1 dal primo trade del paper · cooldown 4 barre
  #1  26 Sep 18:45 UTC  long  entry 1.524  pnl -0.39 USDT (stop_loss)
       ABBINATO: motore alla barra 26 Sep 18:45 (+0 min), direzione uguale
  ABBINATI 1/1 · «come il bot» (da 200 barre prima del paper): 1/1 abbinati, 1 trade del motore
  [2850s]

── XRPUSDT|gen_a22411e3 · 1 trade · 15m · scala 1.5/3/5 · BE si · keep globale
[backtest] dati da cache: 166163 candele (XRPUSDT 15m)
[backtest] dati da cache: 166163 candele (XRPUSDT 15m)
  motore: 401 trade sulla storia intera, 1 dal primo trade del paper · cooldown 4 barre
  #1  27 Sep 13:00 UTC  long  entry 1.523  pnl +0.32 USDT (trailing_stop)
       ABBINATO: motore alla barra 27 Sep 13:00 (+0 min), direzione uguale
  ABBINATI 1/1 · «come il bot» (da 200 barre prima del paper): 1/1 abbinati, 1 trade del motore
  [2954s]

── ZKUSDT|gen_98837ec2 · 1 trade · 15m · scala 2/4/6 · BE si · keep globale
[backtest] cache ESTESA di 180 candele (invece di riscaricarne 79912) (ZKUSDT 15m)
[backtest] dati da cache: 79912 candele (ZKUSDT 15m)
  motore: 97 trade sulla storia intera, 1 dal primo trade del paper · cooldown 4 barre
  #1  24 Sep 08:15 UTC  long  entry 0.01146  pnl -1.23 USDT (stop_loss)
       ABBINATO: motore alla barra 24 Sep 08:15 (+0 min), direzione uguale
  ABBINATI 1/1 · «come il bot» (da 200 barre prima del paper): 1/1 abbinati, 1 trade del motore
  [3004s]

── ZORAUSDT|gen_2c248ee9 · 1 trade · 15m · scala 1.5/3/5 · BE si · keep globale
[backtest] cache riusata (tagliata da 2026-09-27): 41141 candele (ZORAUSDT 15m)
[backtest] dati da cache: 41141 candele (ZORAUSDT 15m)
  motore: 65 trade sulla storia intera, 0 dal primo trade del paper · cooldown 4 barre
  #1  25 Sep 13:30 UTC  long  entry 0.008816  pnl +0.34 USDT (trailing_stop)
       REGOLA_NON_SCATTA · IGNOTO: stessi valori e la regola non scatta neanche sui valori del paper
       regola sul frame del motore: k-1 no · k no · k+1 no · con 199 candele si · sui valori del paper no · regime motore bull_trending / paper bull_trending
  ABBINATI 0/1 · «come il bot» (da 200 barre prima del paper): 0/1 abbinati, 0 trade del motore
  [3029s]

==========================================================================
RIASSUNTO
==========================================================================
  trade classificati: 135 · abbinati 62 (46%) · «come il bot» 47%
  per classe:
    ABBINATO                62
    MOTORE_IN_POSIZIONE      4
    MOTORE_IN_COOLDOWN       1
    REGOLA_NON_SCATTA       67
    SENZA_MOTORE             1
  REGOLA_NON_SCATTA per sotto-motivo:
    IGNOTO                  67
  per coppia (abbinati/trade):
    SUIUSDT|gen_490a90e5                0/7   (  0%) · come il bot 0/7
    USELESSUSDT|gen_2031005e            0/7   (  0%) · come il bot 0/7
    ORCAUSDT|gen_fca11c08               0/5   (  0%) · come il bot 0/5
    DOTUSDT|gen_fca11c08                0/4   (  0%) · come il bot 0/4
    HUMAUSDT|gen_fca11c08               0/4   (  0%) · come il bot 0/4
    DEXEUSDT|gen_b31d8b93               1/4   ( 25%) · come il bot 1/4
    DEXEUSDT|gen_fa304106               2/5   ( 40%) · come il bot 2/5
    JTOUSDT|gen_f238d283                0/3   (  0%) · come il bot 0/3
    SYRUPUSDT|gen_af734c68              0/3   (  0%) · come il bot 0/3
    VETUSDT|gen_6d06dca0                0/3   (  0%) · come il bot 0/3
    AVAAIUSDT|gen_e50a9211              0/2   (  0%) · come il bot 0/2
    BICOUSDT|gen_f238d283               0/2   (  0%) · come il bot 0/2
    BULLAUSDT|gen_7ac562e3              0/2   (  0%) · come il bot 0/2
    DEXEUSDT|gen_887d87df               0/2   (  0%) · come il bot 0/2
    ORCAUSDT|gen_6d06dca0               1/3   ( 33%) · come il bot 1/3
    GPSUSDT|gen_bf1e00d4                3/4   ( 75%) · come il bot 3/4
    HEMIUSDT|gen_6bc43e03               0/1   (  0%) · come il bot 0/1
    JUPUSDT|gen_bb762669                0/1   (  0%) · come il bot 0/1
    MITOUSDT|gen_8b91ba18               1/2   ( 50%) · come il bot 1/2
    MUBARAKUSDT|gen_49c2f657            0/1   (  0%) · come il bot 1/1
    MUBARAKUSDT|gen_ff3e4154            0/1   (  0%) · come il bot 0/1
    NEIROUSDT|gen_f3124a14              1/2   ( 50%) · come il bot 1/2
    PROMUSDT|gen_cd5c842f               3/4   ( 75%) · come il bot 3/4
    QUSDT|gen_cde82a91                  0/1   (  0%) · come il bot 0/1
    RENDERUSDT|gen_acfd527a             0/1   (  0%) · come il bot 0/1
    SKYAIUSDT|gen_c61d9322              0/1   (  0%) · come il bot 0/1
    SPXUSDT|gen_d53c153b                0/1   (  0%) · come il bot 0/1
    STXUSDT|gen_14e1775b                0/1   (  0%) · come il bot 1/1
    STXUSDT|gen_acfd527a                0/1   (  0%) · come il bot 0/1
    STXUSDT|gen_b9bf5d01                2/3   ( 67%) · come il bot 2/3
    SYRUPUSDT|gen_4c6df481              2/3   ( 67%) · come il bot 2/3
    SYRUPUSDT|gen_b7d57ce7              0/1   (  0%) · come il bot 0/1
    THEUSDT|gen_658b2edb                0/1   (  0%) · come il bot 0/1
    XPLUSDT|gen_a220b439                0/1   (  0%) · come il bot 0/1
    XPLUSDT|gen_b437a671                0/1   (  0%) · come il bot 0/1
    ZORAUSDT|gen_2c248ee9               0/1   (  0%) · come il bot 0/1
    ATOMUSDT|gen_eaa569ba               1/1   (100%) · come il bot 1/1
    CROSSUSDT|gen_d606fde3              1/1   (100%) · come il bot 1/1
    DOTUSDT|gen_919c110c                1/1   (100%) · come il bot 1/1
    ENAUSDT|gen_bb762669                1/1   (100%) · come il bot 1/1
    GPSUSDT|gen_871647b8                1/1   (100%) · come il bot 1/1
    HEIUSDT|gen_e6ddc613                1/1   (100%) · come il bot 1/1
    HUMAUSDT|gen_771790b1               1/1   (100%) · come il bot 1/1
    HUMAUSDT|gen_a32bee42               1/1   (100%) · come il bot 1/1
    JTOUSDT|gen_35632db9                1/1   (100%) · come il bot 1/1
    MUBARAKUSDT|gen_1f7ead60            2/2   (100%) · come il bot 2/2
    MUBARAKUSDT|gen_2053cba6            2/2   (100%) · come il bot 2/2
    NEIROUSDT|gen_e132204b              1/1   (100%) · come il bot 1/1
    QUSDT|gen_18c839a0                  4/4   (100%) · come il bot 4/4
    QUSDT|gen_bf2be656                  1/1   (100%) · come il bot 1/1
    SAHARAUSDT|gen_6b94025f             1/1   (100%) · come il bot 1/1
    SEIUSDT|gen_4f890271                1/1   (100%) · come il bot 1/1
    SOLUSDT|gen_f3124a14                1/1   (100%) · come il bot 1/1
    SPXUSDT|gen_ba3a671f                6/6   (100%) · come il bot 6/6
    TAUSDT|gen_bf2be656                 1/1   (100%) · come il bot 1/1
    TRUMPUSDT|gen_93131ef1              1/1   (100%) · come il bot 1/1
    TSTUSDT|gen_a640dfa5                2/2   (100%) · come il bot 2/2
    TUTUSDT|gen_4465723e                4/4   (100%) · come il bot 4/4
    USELESSUSDT|gen_c0fd1d91            2/2   (100%) · come il bot 2/2
    VETUSDT|gen_b2f350ff                1/1   (100%) · come il bot 1/1
    VETUSDT|gen_fca11c08                1/1   (100%) · come il bot 1/1
    XMRUSDT|gen_35632db9                2/2   (100%) · come il bot 2/2
    XPLUSDT|gen_e59ad90b                1/1   (100%) · come il bot 1/1
    XRPUSDT|gen_50905b4a                1/1   (100%) · come il bot 1/1
    XRPUSDT|gen_a22411e3                1/1   (100%) · come il bot 1/1
    ZKUSDT|gen_98837ec2                 1/1   (100%) · come il bot 1/1
  coppie con piu' non abbinati: SUIUSDT|gen_490a90e5 (7), USELESSUSDT|gen_2031005e (7), ORCAUSDT|gen_fca11c08 (5), DOTUSDT|gen_fca11c08 (4), HUMAUSDT|gen_fca11c08 (4), DEXEUSDT|gen_fa304106 (3), DEXEUSDT|gen_b31d8b93 (3), JTOUSDT|gen_f238d283 (3), SYRUPUSDT|gen_af734c68 (3), VETUSDT|gen_6d06dca0 (3)

LETTURA: 62/135 ingressi abbinati (46%): la regola non scatta e i dati non spiegano perche' (67 su 73 non abbinati) — da guardare a mano.
  NB: i trade del motore sono simulati sulla storia intera, senza holdout; «stop» del
      motore e' dedotto (il SimTrade non porta il motivo). Questo comando misura e basta.
[ingressi] finito in 3029s
```
