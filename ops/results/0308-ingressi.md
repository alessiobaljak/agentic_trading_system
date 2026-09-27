# 0308-ingressi.req

_eseguito: 2026-09-27 11:54 UTC_

**richiesta:** `ingressi`
**eseguito:** `.venv/bin/python -m scripts.ingressi_report`
**esito:** codice 0 in 764.9s

```
[firebase] connesso (Firestore + RTDB)
==========================================================================
INGRESSI DEL PAPER, TRADE PER TRADE: dove il motore non entra, e perche'
==========================================================================
PAPER: 123 trade chiusi su 61 coppie · rigirate 61 · tolleranza 2 barre · deadline 720s

── SPXUSDT|gen_ba3a671f · 6 trade · 15m · scala 0.75/1.5/3 · BE si · keep globale
[backtest] dati da cache: 62830 candele (SPXUSDT 15m)
[backtest] dati da cache: 62830 candele (SPXUSDT 15m)
  motore: 214 trade sulla storia intera, 5 dal primo trade del paper · cooldown 4 barre
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
       SENZA_MOTORE: candela del paper non nei dati del motore
  ABBINATI 5/6 · «come il bot» (da 200 barre prima del paper): 5/6 abbinati, 5 trade del motore
  [37s]

── SUIUSDT|gen_490a90e5 · 6 trade · 15m · scala 1/2/3 · BE si · keep globale
[backtest] dati da cache: 119169 candele (SUIUSDT 15m)
[backtest] dati da cache: 119169 candele (SUIUSDT 15m)
  motore: 782 trade sulla storia intera, 2 dal primo trade del paper · cooldown 4 barre
  #1  25 Sep 10:45 UTC  short entry 1.069  pnl -1.93 USDT (stop_loss)
       ABBINATO: motore alla barra 25 Sep 10:45 (+0 min), direzione uguale
  #2  25 Sep 12:00 UTC  short entry 1.131  pnl +0.70 USDT (trailing_stop)
       ABBINATO: motore alla barra 25 Sep 12:15 (+15 min), direzione uguale
  #3  25 Sep 12:15 UTC  short entry 1.135  pnl +0.55 USDT (trailing_stop)
       REGOLA_NON_SCATTA · SEGNALE_SENZA_TRADE: la regola scatta ma quel segnale e' gia' abbinato a un altro trade del paper
       regola sul frame del motore: k-1 si · k si · k+1 no · con 199 candele si · sui valori del paper si · regime motore bull_trending / paper bull_trending
  #4  25 Sep 13:30 UTC  short entry 1.127  pnl +1.12 USDT (trailing_stop)
       MOTORE_IN_POSIZIONE: dentro il trade del 25 Sep 12:15 (short, uscito 25 Sep 13:45, guadagno dedotto, +0.86%): cascata di un'uscita diversa, non della regola d'ingresso
  #5  27 Sep 06:15 UTC  short entry 1.198  pnl -1.59 USDT (stop_loss)
       SENZA_MOTORE: candela del paper non nei dati del motore
  #6  27 Sep 08:30 UTC  short entry 1.269  pnl +1.64 USDT (scale_out)
       SENZA_MOTORE: candela del paper non nei dati del motore
  ABBINATI 2/6 · «come il bot» (da 200 barre prima del paper): 2/6 abbinati, 2 trade del motore
  [106s]

── USELESSUSDT|gen_2031005e · 6 trade · 15m · scala 2/4/6 · BE si · keep globale
[backtest] dati da cache: 39024 candele (USELESSUSDT 15m)
[backtest] dati da cache: 39024 candele (USELESSUSDT 15m)
  motore: 266 trade sulla storia intera, 5 dal primo trade del paper · cooldown 4 barre
  #1  21 Sep 08:30 UTC  short entry 0.2548  pnl -8.25 USDT (stop_loss)
       ABBINATO: motore alla barra 21 Sep 08:30 (+0 min), direzione uguale
  #2  21 Sep 08:45 UTC  short entry 0.2651  pnl -8.65 USDT (stop_loss)
       MOTORE_IN_POSIZIONE: dentro il trade del 21 Sep 08:30 (short, uscito 21 Sep 09:00, stop dedotto, -4.18%): cascata di un'uscita diversa, non della regola d'ingresso
  #3  21 Sep 09:15 UTC  short entry 0.2765  pnl -8.97 USDT (stop_loss)
       MOTORE_IN_COOLDOWN: cooldown di 4 barre dopo lo stop del 21 Sep 09:00 (fino a 21 Sep 10:00): la barra del paper e' la 1ª di 4
  #4  21 Sep 10:15 UTC  short entry 0.2862  pnl +5.11 USDT (trailing_stop)
       ABBINATO: motore alla barra 21 Sep 10:15 (+0 min), direzione uguale
  #5  22 Sep 08:00 UTC  short entry 0.3014  pnl -9.14 USDT (stop_loss)
       ABBINATO: motore alla barra 22 Sep 08:00 (+0 min), direzione uguale
  #6  25 Sep 12:45 UTC  short entry 0.307  pnl +1.76 USDT (trailing_stop)
       MOTORE_IN_COOLDOWN: cooldown di 4 barre dopo lo stop del 25 Sep 11:45 (fino a 25 Sep 12:45): la barra del paper e' la 4ª di 4
  ABBINATI 3/6 · «come il bot» (da 200 barre prima del paper): 3/6 abbinati, 5 trade del motore
  [128s]

── DEXEUSDT|gen_fa304106 · 5 trade · 15m · scala 1.5/3/5 · BE si · keep globale
[backtest] dati da cache: 61491 candele (DEXEUSDT 15m)
[backtest] dati da cache: 61491 candele (DEXEUSDT 15m)
  motore: 137 trade sulla storia intera, 4 dal primo trade del paper · cooldown 4 barre
  #1  17 Sep 10:15 UTC  short entry 1.794  pnl -2.02 USDT (stop_loss)
       ABBINATO: motore alla barra 17 Sep 10:30 (+15 min), direzione uguale
  #2  19 Sep 11:00 UTC  short entry 1.854  pnl -2.01 USDT (stop_loss)
       ABBINATO: motore alla barra 19 Sep 11:00 (+0 min), direzione uguale
  #3  20 Sep 16:00 UTC  short entry 1.839  pnl -2.17 USDT (stop_loss)
       REGOLA_NON_SCATTA · PREZZO_VIVO: stessi indicatori; col prezzo del paper (1.839) la regola scatta, con la chiusura (1.838) no
       regola sul frame del motore: k-1 no · k no · k+1 no · con 199 candele si · sui valori del paper si · regime motore bear_trending / paper bear_trending
  #4  21 Sep 01:30 UTC  long  entry 1.861  pnl -2.21 USDT (stop_loss)
       REGOLA_NON_SCATTA · PREZZO_VIVO: stessi indicatori; col prezzo del paper (1.861) la regola scatta, con la chiusura (1.862) no
       regola sul frame del motore: k-1 no · k no · k+1 no · con 199 candele si · sui valori del paper si · regime motore sideways / paper sideways
  #5  24 Sep 00:00 UTC  short entry 1.885  pnl -1.50 USDT (stop_loss)
       MOTORE_IN_POSIZIONE: dentro il trade del 23 Sep 23:45 (short, uscito 24 Sep 05:00, stop dedotto, -1.63%): cascata di un'uscita diversa, non della regola d'ingresso
  ABBINATI 2/5 · «come il bot» (da 200 barre prima del paper): 2/5 abbinati, 4 trade del motore
  [163s]

── ORCAUSDT|gen_fca11c08 · 5 trade · 15m · scala 1.5/3/5 · BE si · keep globale
[backtest] dati da cache: 63205 candele (ORCAUSDT 15m)
[backtest] dati da cache: 63205 candele (ORCAUSDT 15m)
  motore: 484 trade sulla storia intera, 2 dal primo trade del paper · cooldown 4 barre
  #1  25 Sep 08:45 UTC  short entry 1.615  pnl -1.61 USDT (stop_loss)
       ABBINATO: motore alla barra 25 Sep 08:45 (+0 min), direzione uguale
  #2  25 Sep 20:30 UTC  short entry 1.672  pnl +1.97 USDT (trailing_stop)
       ABBINATO: motore alla barra 25 Sep 20:30 (+0 min), direzione uguale
  #3  26 Sep 15:45 UTC  short entry 1.661  pnl +0.26 USDT (trailing_stop)
       SENZA_MOTORE: candela del paper non nei dati del motore
  #4  27 Sep 08:45 UTC  short entry 1.743  pnl -2.60 USDT (stop_loss)
       SENZA_MOTORE: candela del paper non nei dati del motore
  #5  27 Sep 10:45 UTC  short entry 1.837  pnl +0.61 USDT (trailing_stop)
       SENZA_MOTORE: candela del paper non nei dati del motore
  ABBINATI 2/5 · «come il bot» (da 200 barre prima del paper): 2/5 abbinati, 2 trade del motore
  [200s]

── DEXEUSDT|gen_b31d8b93 · 4 trade · 15m · scala 2/4/6 · BE si · keep globale
[backtest] dati da cache: 61491 candele (DEXEUSDT 15m)
[backtest] dati da cache: 61491 candele (DEXEUSDT 15m)
  motore: 112 trade sulla storia intera, 1 dal primo trade del paper · cooldown 4 barre
  #1  18 Sep 22:00 UTC  long  entry 1.863  pnl -2.41 USDT (stop_loss)
       REGOLA_NON_SCATTA · PREZZO_VIVO: stessi indicatori; col prezzo del paper (1.863) la regola scatta, con la chiusura (1.859) no
       regola sul frame del motore: k-1 no · k no · k+1 no · con 199 candele si · sui valori del paper si · regime motore bull_trending / paper bull_trending
  #2  19 Sep 20:15 UTC  long  entry 1.873  pnl +0.89 USDT (scale_out)
       ABBINATO: motore alla barra 19 Sep 20:15 (+0 min), direzione uguale
  #3  24 Sep 08:30 UTC  long  entry 1.919  pnl -1.70 USDT (stop_loss)
       REGOLA_NON_SCATTA · PREZZO_VIVO: stessi indicatori; col prezzo del paper (1.919) la regola scatta, con la chiusura (1.917) no
       regola sul frame del motore: k-1 no · k no · k+1 no · con 199 candele si · sui valori del paper si · regime motore sideways / paper sideways
  #4  26 Sep 23:45 UTC  short entry 1.926  pnl -1.88 USDT (stop_loss)
       SENZA_MOTORE: candela del paper non nei dati del motore
  ABBINATI 1/4 · «come il bot» (da 200 barre prima del paper): 1/4 abbinati, 1 trade del motore
  [236s]

── GPSUSDT|gen_bf1e00d4 · 4 trade · 15m · scala 1.5/3/5 · BE si · keep globale
[backtest] dati da cache: 56189 candele (GPSUSDT 15m)
[backtest] dati da cache: 56189 candele (GPSUSDT 15m)
  motore: 182 trade sulla storia intera, 3 dal primo trade del paper · cooldown 4 barre
  #1  18 Sep 03:00 UTC  long  entry 0.01059  pnl +10.30 USDT (take_profit)
       ABBINATO: motore alla barra 18 Sep 03:00 (+0 min), direzione uguale
  #2  24 Sep 08:45 UTC  long  entry 0.01174  pnl -2.35 USDT (stop_loss)
       ABBINATO: motore alla barra 24 Sep 08:45 (+0 min), direzione uguale
  #3  24 Sep 13:00 UTC  long  entry 0.01133  pnl +0.73 USDT (trailing_stop)
       MOTORE_IN_COOLDOWN: cooldown di 4 barre dopo lo stop del 24 Sep 12:30 (fino a 24 Sep 13:30): la barra del paper e' la 2ª di 4
  #4  26 Sep 20:45 UTC  long  entry 0.0117  pnl +0.56 USDT (trailing_stop)
       SENZA_MOTORE: candela del paper non nei dati del motore
  ABBINATI 2/4 · «come il bot» (da 200 barre prima del paper): 2/4 abbinati, 3 trade del motore
  [268s]

── HUMAUSDT|gen_fca11c08 · 4 trade · 15m · scala 2/4/6 · BE si · keep globale
[backtest] dati da cache: 46797 candele (HUMAUSDT 15m)
[backtest] dati da cache: 46797 candele (HUMAUSDT 15m)
  motore: 409 trade sulla storia intera, 1 dal primo trade del paper · c

[... 4422 caratteri omessi (testa e coda conservate) ...]

RE: candela del paper non nei dati del motore
  ABBINATI 1/3 · «come il bot» (da 200 barre prima del paper): 1/3 abbinati, 1 trade del motore
  [477s]

── JTOUSDT|gen_f238d283 · 3 trade · 15m · scala 1/2/3 · BE si · keep 0.65
[backtest] dati da cache: 98169 candele (JTOUSDT 15m)
[backtest] dati da cache: 98169 candele (JTOUSDT 15m)
  motore: 145 trade sulla storia intera, 3 dal primo trade del paper · cooldown 4 barre
  #1  24 Sep 14:15 UTC  short entry 0.4848  pnl +1.37 USDT (trailing_stop)
       ABBINATO: motore alla barra 24 Sep 14:15 (+0 min), direzione uguale
  #2  25 Sep 09:15 UTC  short entry 0.5225  pnl -4.44 USDT (stop_loss)
       ABBINATO: motore alla barra 25 Sep 09:15 (+0 min), direzione uguale
  #3  25 Sep 10:45 UTC  short entry 0.5481  pnl +1.52 USDT (trailing_stop)
       ABBINATO: motore alla barra 25 Sep 11:00 (+15 min), direzione uguale
  ABBINATI 3/3 · «come il bot» (da 200 barre prima del paper): 3/3 abbinati, 3 trade del motore
  [531s]

── ORCAUSDT|gen_6d06dca0 · 3 trade · 15m · scala 1.5/3/5 · BE si · keep globale
[backtest] dati da cache: 63205 candele (ORCAUSDT 15m)
[backtest] dati da cache: 63205 candele (ORCAUSDT 15m)
  motore: 93 trade sulla storia intera, 0 dal primo trade del paper · cooldown 4 barre
  #1  18 Sep 03:30 UTC  short entry 1.42  pnl -3.02 USDT (stop_loss)
       REGOLA_NON_SCATTA · IGNOTO: stessi valori e la regola non scatta neanche sui valori del paper
       regola sul frame del motore: k-1 no · k no · k+1 no · con 199 candele no · sui valori del paper no · regime motore bull_trending / paper bull_trending
  #2  20 Sep 16:30 UTC  short entry 1.438  pnl -2.99 USDT (stop_loss)
       REGOLA_NON_SCATTA · IGNOTO: stessi valori e la regola non scatta neanche sui valori del paper
       regola sul frame del motore: k-1 no · k no · k+1 no · con 199 candele no · sui valori del paper no · regime motore bear_trending / paper bear_trending
  #3  27 Sep 07:30 UTC  short entry 1.694  pnl -1.43 USDT (stop_loss)
       SENZA_MOTORE: candela del paper non nei dati del motore
  ABBINATI 0/3 · «come il bot» (da 200 barre prima del paper): 0/3 abbinati, 0 trade del motore
  [567s]

── STXUSDT|gen_b9bf5d01 · 3 trade · 15m · scala 2/4/6 · BE si · keep globale
[backtest] dati da cache: 126087 candele (STXUSDT 15m)
[backtest] dati da cache: 126087 candele (STXUSDT 15m)
  motore: 301 trade sulla storia intera, 4 dal primo trade del paper · cooldown 4 barre
  #1  19 Sep 00:30 UTC  long  entry 0.2843  pnl -3.59 USDT (stop_loss)
       ABBINATO: motore alla barra 19 Sep 00:30 (+0 min), direzione uguale
  #2  21 Sep 00:30 UTC  long  entry 0.3269  pnl -5.55 USDT (stop_loss)
       REGOLA_NON_SCATTA · PREZZO_VIVO: stessi indicatori; col prezzo del paper (0.3269) la regola scatta, con la chiusura (0.3267) no
       regola sul frame del motore: k-1 no · k no · k+1 no · con 199 candele si · sui valori del paper si · regime motore bull_trending / paper bull_trending
  #3  21 Sep 12:30 UTC  long  entry 0.3313  pnl +1.90 USDT (trailing_stop)
       ABBINATO: motore alla barra 21 Sep 12:30 (+0 min), direzione uguale
  ABBINATI 2/3 · «come il bot» (da 200 barre prima del paper): 2/3 abbinati, 3 trade del motore
  [639s]

── SYRUPUSDT|gen_af734c68 · 3 trade · 15m · scala 1.5/3/5 · BE si · keep globale
[backtest] dati da cache: 48639 candele (SYRUPUSDT 15m)
[backtest] dati da cache: 48639 candele (SYRUPUSDT 15m)
  motore: 145 trade sulla storia intera, 6 dal primo trade del paper · cooldown 4 barre
  #1  17 Sep 21:45 UTC  short entry 0.2065  pnl -1.89 USDT (stop_loss)
       ABBINATO: motore alla barra 17 Sep 21:45 (+0 min), direzione uguale
  #2  18 Sep 08:45 UTC  short entry 0.2127  pnl -2.01 USDT (stop_loss)
       ABBINATO: motore alla barra 18 Sep 08:45 (+0 min), direzione uguale
  #3  21 Sep 11:30 UTC  short entry 0.2356  pnl +1.59 USDT (trailing_stop)
       ABBINATO: motore alla barra 21 Sep 11:30 (+0 min), direzione uguale
  ABBINATI 3/3 · «come il bot» (da 200 barre prima del paper): 3/3 abbinati, 4 trade del motore
  [667s]

── VETUSDT|gen_6d06dca0 · 3 trade · 15m · scala 2/4/6 · BE si · keep globale
[backtest] dati da cache: 165985 candele (VETUSDT 15m)
[backtest] dati da cache: 165985 candele (VETUSDT 15m)
  motore: 227 trade sulla storia intera, 0 dal primo trade del paper · cooldown 4 barre
  #1  18 Sep 03:45 UTC  short entry 0.007585  pnl -3.24 USDT (stop_loss)
       REGOLA_NON_SCATTA · IGNOTO: stessi valori e la regola non scatta neanche sui valori del paper
       regola sul frame del motore: k-1 no · k no · k+1 no · con 199 candele no · sui valori del paper no · regime motore bull_trending / paper bull_trending
  #2  19 Sep 04:00 UTC  short entry 0.008292  pnl -5.51 USDT (stop_loss)
       REGOLA_NON_SCATTA · IGNOTO: stessi valori e la regola non scatta neanche sui valori del paper
       regola sul frame del motore: k-1 no · k no · k+1 no · con 199 candele no · sui valori del paper no · regime motore high_uncertainty / paper high_uncertainty
  #3  23 Sep 03:30 UTC  short entry 0.009713  pnl +3.38 USDT (trailing_stop)
       REGOLA_NON_SCATTA · IGNOTO: stessi valori e la regola non scatta neanche sui valori del paper
       regola sul frame del motore: k-1 no · k no · k+1 no · con 199 candele no · sui valori del paper no · regime motore bull_trending / paper bull_trending
  ABBINATI 0/3 · «come il bot» (da 200 barre prima del paper): 0/3 abbinati, 0 trade del motore
  [763s]

==========================================================================
RIASSUNTO
==========================================================================
  trade classificati: 70 · abbinati 36 (51%) · «come il bot» 53%
  per classe:
    ABBINATO                36
    MOTORE_IN_POSIZIONE      5
    MOTORE_IN_COOLDOWN       3
    REGOLA_NON_SCATTA       11
    SENZA_MOTORE            15
  REGOLA_NON_SCATTA per sotto-motivo:
    PREZZO_VIVO              5
    SEGNALE_SENZA_TRADE      1
    IGNOTO                   5
  per coppia (abbinati/trade):
    HUMAUSDT|gen_fca11c08               0/4   (  0%) · come il bot 1/4
    SUIUSDT|gen_490a90e5                2/6   ( 33%) · come il bot 2/6
    DEXEUSDT|gen_b31d8b93               1/4   ( 25%) · come il bot 1/4
    DEXEUSDT|gen_fa304106               2/5   ( 40%) · come il bot 2/5
    ORCAUSDT|gen_6d06dca0               0/3   (  0%) · come il bot 0/3
    ORCAUSDT|gen_fca11c08               2/5   ( 40%) · come il bot 2/5
    USELESSUSDT|gen_2031005e            3/6   ( 50%) · come il bot 3/6
    VETUSDT|gen_6d06dca0                0/3   (  0%) · come il bot 0/3
    DOTUSDT|gen_fca11c08                1/3   ( 33%) · come il bot 1/3
    GPSUSDT|gen_bf1e00d4                2/4   ( 50%) · come il bot 2/4
    PROMUSDT|gen_cd5c842f               3/4   ( 75%) · come il bot 3/4
    SPXUSDT|gen_ba3a671f                5/6   ( 83%) · come il bot 5/6
    STXUSDT|gen_b9bf5d01                2/3   ( 67%) · come il bot 2/3
    TUTUSDT|gen_4465723e                3/4   ( 75%) · come il bot 3/4
    JTOUSDT|gen_f238d283                3/3   (100%) · come il bot 3/3
    QUSDT|gen_18c839a0                  4/4   (100%) · come il bot 4/4
    SYRUPUSDT|gen_af734c68              3/3   (100%) · come il bot 3/3
  coppie con piu' non abbinati: SUIUSDT|gen_490a90e5 (4), HUMAUSDT|gen_fca11c08 (4), USELESSUSDT|gen_2031005e (3), DEXEUSDT|gen_fa304106 (3), ORCAUSDT|gen_fca11c08 (3), DEXEUSDT|gen_b31d8b93 (3), ORCAUSDT|gen_6d06dca0 (3), VETUSDT|gen_6d06dca0 (3), GPSUSDT|gen_bf1e00d4 (2), DOTUSDT|gen_fca11c08 (2)
  non rigirate: 44
    AVAAIUSDT|gen_e50a9211: tempo (budget)
    BICOUSDT|gen_f238d283: tempo (budget)
    BULLAUSDT|gen_7ac562e3: tempo (budget)
    MITOUSDT|gen_8b91ba18: tempo (budget)
    MUBARAKUSDT|gen_1f7ead60: tempo (budget)
    MUBARAKUSDT|gen_2053cba6: tempo (budget)
    NEIROUSDT|gen_f3124a14: tempo (budget)
    SYRUPUSDT|gen_4c6df481: tempo (budget)
    USELESSUSDT|gen_c0fd1d91: tempo (budget)
    ATOMUSDT|gen_eaa569ba: tempo (budget)
    CROSSUSDT|gen_d606fde3: tempo (budget)
    DEXEUSDT|gen_887d87df: tempo (budget)
    DOTUSDT|gen_919c110c: tempo (budget)
    ENAUSDT|gen_bb762669: tempo (budget)
    GPSUSDT|gen_871647b8: tempo (budget)
    HEIUSDT|gen_e6ddc613: tempo (budget)
    HUMAUSDT|gen_771790b1: tempo (budget)
    HUMAUSDT|gen_a32bee42: tempo (budget)
    JTOUSDT|gen_35632db9: tempo (budget)
    JUPUSDT|gen_bb762669: tempo (budget)
    MUBARAKUSDT|gen_49c2f657: tempo (budget)
    MUBARAKUSDT|gen_ff3e4154: tempo (budget)
    NEIROUSDT|gen_e132204b: tempo (budget)
    QUSDT|gen_bf2be656: tempo (budget)
    QUSDT|gen_cde82a91: tempo (budget)
    RENDERUSDT|gen_acfd527a: tempo (budget)
    SAHARAUSDT|gen_6b94025f: tempo (budget)
    SEIUSDT|gen_4f890271: tempo (budget)
    SKYAIUSDT|gen_c61d9322: tempo (budget)
    STXUSDT|gen_14e1775b: tempo (budget)
    STXUSDT|gen_acfd527a: tempo (budget)
    SYRUPUSDT|gen_b7d57ce7: tempo (budget)
    TAUSDT|gen_bf2be656: tempo (budget)
    THEUSDT|gen_658b2edb: tempo (budget)
    TSTUSDT|gen_a640dfa5: tempo (budget)
    VETUSDT|gen_b2f350ff: tempo (budget)
    VETUSDT|gen_fca11c08: tempo (budget)
    XMRUSDT|gen_35632db9: tempo (budget)
    XPLUSDT|gen_a220b439: tempo (budget)
    XPLUSDT|gen_b437a671: tempo (budget)
    XPLUSDT|gen_e59ad90b: tempo (budget)
    XRPUSDT|gen_50905b4a: tempo (budget)
    ZKUSDT|gen_98837ec2: tempo (budget)
    ZORAUSDT|gen_2c248ee9: tempo (budget)

LETTURA: 36/70 ingressi abbinati (51%): la maggior parte non e' rigirabile (15 su 34 non abbinati) — spec fuori dal registro o candele mancanti: prima i dati, poi la regola.
  NB: i trade del motore sono simulati sulla storia intera, senza holdout; «stop» del
      motore e' dedotto (il SimTrade non porta il motivo). Questo comando misura e basta.
[ingressi] finito in 763s

--- stderr ---
/root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
  return query.where(field_path, op_string, value)
```
