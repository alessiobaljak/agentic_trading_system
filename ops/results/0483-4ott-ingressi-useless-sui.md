# 0483-4ott-ingressi-useless-sui.req

_eseguito: 2026-10-04 08:25 UTC_

**richiesta:** `ingressi`
**eseguito:** `.venv/bin/python -m scripts.ingressi_report`
**esito:** codice 0 in 736.1s

```
[firebase] connesso (Firestore + RTDB)
==========================================================================
INGRESSI DEL PAPER, TRADE PER TRADE: dove il motore non entra, e perche'
==========================================================================
PAPER: 265 trade chiusi su 127 coppie · rigirate 127 · tolleranza 2 barre · deadline 720s

── PROMUSDT|gen_cd5c842f · 7 trade · 15m · scala 2/4/6 · BE si · keep globale
[backtest] cache riusata (tagliata da 2026-10-04): 60143 candele (PROMUSDT 15m)
[backtest] dati da cache: 60143 candele (PROMUSDT 15m)
  motore: 275 trade sulla storia intera, 5 dal primo trade del paper · cooldown 4 barre
  #1  19 Sep 22:30 UTC  short entry 5.286  pnl +10.48 USDT (take_profit)
       ABBINATO: motore alla barra 19 Sep 22:30 (+0 min), direzione uguale
  #2  21 Sep 08:30 UTC  short entry 4.964  pnl -3.13 USDT (stop_loss)
       ABBINATO: motore alla barra 21 Sep 08:30 (+0 min), direzione uguale
  #3  25 Sep 02:00 UTC  long  entry 5.473  pnl +1.05 USDT (trailing_stop)
       ABBINATO: motore alla barra 25 Sep 02:00 (+0 min), direzione uguale
  #4  26 Sep 21:15 UTC  short entry 6.327  pnl +4.48 USDT (scale_out)
       REGOLA_NON_SCATTA · IGNOTO: stessi valori e la regola non scatta neanche sui valori del paper
       regola sul frame del motore: k-1 no · k no · k+1 no · con 199 candele si · sui valori del paper no · regime motore high_uncertainty / paper high_uncertainty
  #5  28 Sep 01:30 UTC  long  entry 6.208  pnl +1.61 USDT (trailing_stop)
       ABBINATO: motore alla barra 28 Sep 01:30 (+0 min), direzione uguale
  #6  28 Sep 16:30 UTC  long  entry 6.271  pnl +0.77 USDT (trailing_stop)
       ABBINATO: motore alla barra 28 Sep 16:30 (+0 min), direzione uguale
  #7  29 Sep 01:15 UTC  long  entry 6.315  pnl -1.30 USDT (stop_loss)
       MOTORE_IN_POSIZIONE: dentro il trade del 28 Sep 16:30 (long, uscito 29 Sep 01:15, guadagno dedotto, +1.04%): cascata di un'uscita diversa, non della regola d'ingresso
  ABBINATI 5/7 · «come il bot» (da 200 barre prima del paper): 5/7 abbinati, 5 trade del motore
  [39s]

── SPXUSDT|gen_ba3a671f · 7 trade · 15m · scala 0.75/1.5/3 · BE si · keep globale
[backtest] cache riusata (tagliata da 2026-10-04): 63598 candele (SPXUSDT 15m)
[backtest] dati da cache: 63598 candele (SPXUSDT 15m)
  motore: 217 trade sulla storia intera, 9 dal primo trade del paper · cooldown 4 barre
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
  #7  02 Oct 17:30 UTC  long  entry 0.4334  pnl -1.61 USDT (stop_loss)
       ABBINATO: motore alla barra 02 Oct 17:30 (+0 min), direzione uguale
  ABBINATI 7/7 · «come il bot» (da 200 barre prima del paper): 7/7 abbinati, 9 trade del motore
  [80s]

── SUIUSDT|gen_490a90e5 · 7 trade · 15m · scala 1/2/3 · BE si · keep globale
[backtest] cache riusata (tagliata da 2026-10-04): 119937 candele (SUIUSDT 15m)
[backtest] dati da cache: 119937 candele (SUIUSDT 15m)
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
  [154s]

── USELESSUSDT|gen_2031005e · 7 trade · 15m · scala 2/4/6 · BE si · keep globale
[backtest] cache riusata (tagliata da 2026-10-04): 39792 candele (USELESSUSDT 15m)
[backtest] dati da cache: 39792 candele (USELESSUSDT 15m)
  motore: 106 trade sulla storia intera, 2 dal primo trade del paper · cooldown 4 barre
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
  [178s]

── SYRUPUSDT|gen_4c6df481 · 6 trade · 15m · scala 2/4/6 · BE si · keep 0.75
[backtest] cache riusata (tagliata da 2026-10-04): 49407 candele (SYRUPUSDT 15m)
[backtest] dati da cache: 49407 candele (SYRUPUSDT 15m)
  motore: 331 trade sulla storia intera, 6 dal primo trade del paper · cooldown 4 barre
  #1  26 Sep 09:45 UTC  long  entry 0.2194  pnl +2.54 USDT (scale_out)
       ABBINATO: motore alla barra 26 Sep 09:45 (+0 min), direzione uguale
  #2  27 Sep 06:15 UTC  short entry 0.2212  pnl -1.41 USDT (stop_loss)
       REGOLA_NON_SCATTA · IGNOTO: stessi valori e la regola non scatta neanche sui valori del paper
       regola sul frame del motore: k-1 no · k no · k+1 no · con 199 candele si · sui valori del paper no · regime motore sideways / paper sideways
  #3  27 Sep 09:00 UTC  long  entry 0.2202  pnl -1.51 USDT (stop_loss)
       ABBINATO: motore alla barra 27 Sep 09:00 (+0 min), direzione uguale
  #4  27 Sep 23:45 UTC  short entry 0.2174  pnl +1.13 USDT (trailing_stop)
       ABBINATO: motore all

[... 15425 caratteri omessi (testa e coda conservate) ...]

no a 24 Sep 13:30): la barra del paper e' la 2ª di 4
  #4  26 Sep 20:45 UTC  long  entry 0.0117  pnl +0.56 USDT (trailing_stop)
       ABBINATO: motore alla barra 26 Sep 20:45 (+0 min), direzione uguale
  ABBINATI 3/4 · «come il bot» (da 200 barre prima del paper): 3/4 abbinati, 4 trade del motore
  [676s]

── HUMAUSDT|gen_771790b1 · 4 trade · 15m · scala 2/4/6 · BE si · keep globale
[backtest] cache riusata (tagliata da 2026-10-04): 47565 candele (HUMAUSDT 15m)
[backtest] dati da cache: 47565 candele (HUMAUSDT 15m)
  motore: 139 trade sulla storia intera, 5 dal primo trade del paper · cooldown 4 barre
  #1  25 Sep 08:45 UTC  short entry 0.02629  pnl +1.49 USDT (trailing_stop)
       ABBINATO: motore alla barra 25 Sep 08:45 (+0 min), direzione uguale
  #2  28 Sep 00:30 UTC  short entry 0.02934  pnl +0.87 USDT (trailing_stop)
       ABBINATO: motore alla barra 28 Sep 00:30 (+0 min), direzione uguale
  #3  30 Sep 14:15 UTC  short entry 0.03099  pnl -1.11 USDT (stop_loss)
       ABBINATO: motore alla barra 30 Sep 14:15 (+0 min), direzione uguale
  #4  02 Oct 04:45 UTC  short entry 0.03438  pnl -1.00 USDT (stop_loss)
       ABBINATO: motore alla barra 02 Oct 04:45 (+0 min), direzione uguale
  ABBINATI 4/4 · «come il bot» (da 200 barre prima del paper): 4/4 abbinati, 4 trade del motore
  [705s]

── HUMAUSDT|gen_fca11c08 · 4 trade · 15m · scala 2/4/6 · BE si · keep globale
[backtest] dati da cache: 47565 candele (HUMAUSDT 15m)
[backtest] dati da cache: 47565 candele (HUMAUSDT 15m)
  motore: 194 trade sulla storia intera, 2 dal primo trade del paper · cooldown 4 barre
  #1  25 Sep 10:30 UTC  short entry 0.02677  pnl -2.60 USDT (stop_loss)
       REGOLA_NON_SCATTA · IGNOTO: stessi valori e la regola non scatta neanche sui valori del paper
       regola sul frame del motore: k-1 no · k no · k+1 no · con 199 candele no · sui valori del paper no · regime motore high_uncertainty / paper high_uncertainty
  #2  26 Sep 10:45 UTC  short entry 0.02762  pnl -4.05 USDT (stop_loss)
       REGOLA_NON_SCATTA · IGNOTO: stessi valori e la regola non scatta neanche sui valori del paper
       regola sul frame del motore: k-1 no · k no · k+1 no · con 199 candele no · sui valori del paper no · regime motore bull_trending / paper bull_trending
  #3  26 Sep 13:30 UTC  short entry 0.02865  pnl -3.99 USDT (stop_loss)
       REGOLA_NON_SCATTA · IGNOTO: stessi valori e la regola non scatta neanche sui valori del paper
       regola sul frame del motore: k-1 no · k no · k+1 no · con 199 candele no · sui valori del paper no · regime motore bull_trending / paper bull_trending
  #4  26 Sep 15:00 UTC  short entry 0.02956  pnl -2.83 USDT (stop_loss)
       REGOLA_NON_SCATTA · IGNOTO: stessi valori e la regola non scatta neanche sui valori del paper
       regola sul frame del motore: k-1 no · k no · k+1 no · con 199 candele no · sui valori del paper no · regime motore bull_trending / paper bull_trending
  ABBINATI 0/4 · «come il bot» (da 200 barre prima del paper): 0/4 abbinati, 0 trade del motore
  [735s]

==========================================================================
RIASSUNTO
==========================================================================
  trade classificati: 94 · abbinati 54 (57%) · «come il bot» 57%
  per classe:
    ABBINATO                54
    MOTORE_IN_POSIZIONE      3
    MOTORE_IN_COOLDOWN       1
    REGOLA_NON_SCATTA       36
  REGOLA_NON_SCATTA per sotto-motivo:
    IGNOTO                  36
  per coppia (abbinati/trade):
    SUIUSDT|gen_490a90e5                0/7   (  0%) · come il bot 0/7
    USELESSUSDT|gen_2031005e            0/7   (  0%) · come il bot 0/7
    ORCAUSDT|gen_fca11c08               0/5   (  0%) · come il bot 0/5
    DOTUSDT|gen_fca11c08                0/4   (  0%) · come il bot 0/4
    HUMAUSDT|gen_fca11c08               0/4   (  0%) · come il bot 0/4
    DEXEUSDT|gen_b31d8b93               1/4   ( 25%) · come il bot 1/4
    DEXEUSDT|gen_fa304106               2/5   ( 40%) · come il bot 2/5
    AVAAIUSDT|gen_e50a9211              2/4   ( 50%) · come il bot 2/4
    PROMUSDT|gen_cd5c842f               5/7   ( 71%) · come il bot 5/7
    GPSUSDT|gen_bf1e00d4                3/4   ( 75%) · come il bot 3/4
    JUPUSDT|gen_bb762669                4/5   ( 80%) · come il bot 4/5
    SYRUPUSDT|gen_4c6df481              5/6   ( 83%) · come il bot 5/6
    ENAUSDT|gen_bb762669                4/4   (100%) · come il bot 4/4
    HUMAUSDT|gen_771790b1               4/4   (100%) · come il bot 4/4
    QUSDT|gen_18c839a0                  5/5   (100%) · come il bot 5/5
    SPXUSDT|gen_ba3a671f                7/7   (100%) · come il bot 7/7
    TUTUSDT|gen_4465723e                6/6   (100%) · come il bot 6/6
    XPLUSDT|gen_e59ad90b                6/6   (100%) · come il bot 6/6
  coppie con piu' non abbinati: SUIUSDT|gen_490a90e5 (7), USELESSUSDT|gen_2031005e (7), ORCAUSDT|gen_fca11c08 (5), DOTUSDT|gen_fca11c08 (4), HUMAUSDT|gen_fca11c08 (4), DEXEUSDT|gen_fa304106 (3), DEXEUSDT|gen_b31d8b93 (3), PROMUSDT|gen_cd5c842f (2), AVAAIUSDT|gen_e50a9211 (2), SYRUPUSDT|gen_4c6df481 (1)
  non rigirate: 109
    TSTUSDT|gen_a640dfa5: tempo (budget)
    UBUSDT|gen_fb7d035a: tempo (budget)
    ZORAUSDT|gen_ceab7f6a: tempo (budget)
    BULLAUSDT|gen_7ac562e3: tempo (budget)
    CROSSUSDT|gen_d606fde3: tempo (budget)
    FLOCKUSDT|gen_c5194ce4: tempo (budget)
    JTOUSDT|gen_f238d283: tempo (budget)
    MITOUSDT|gen_8b91ba18: tempo (budget)
    ORCAUSDT|gen_6d06dca0: tempo (budget)
    PNUTUSDT|gen_4810faab: tempo (budget)
    STXUSDT|gen_b9bf5d01: tempo (budget)
    SYRUPUSDT|gen_af734c68: tempo (budget)
    THEUSDT|gen_658b2edb: tempo (budget)
    USELESSUSDT|gen_c0fd1d91: tempo (budget)
    VETUSDT|gen_6d06dca0: tempo (budget)
    AIOUSDT|gen_581d4a68: tempo (budget)
    BANKUSDT|gen_fb3d971f: tempo (budget)
    BICOUSDT|gen_f238d283: tempo (budget)
    BMTUSDT|gen_cee79cdd: tempo (budget)
    BTRUSDT|gen_8981d5f2: tempo (budget)
    DEXEUSDT|gen_887d87df: tempo (budget)
    DOTUSDT|gen_919c110c: tempo (budget)
    EPICUSDT|gen_dfb554f7: tempo (budget)
    GALAUSDT|gen_b9aa9989: tempo (budget)
    GPSUSDT|gen_871647b8: tempo (budget)
    HEMIUSDT|gen_f001d778: tempo (budget)
    HUMAUSDT|gen_a32bee42: tempo (budget)
    MUBARAKUSDT|gen_1f7ead60: tempo (budget)
    MUBARAKUSDT|gen_2053cba6: tempo (budget)
    MUBARAKUSDT|gen_49c2f657: tempo (budget)
    NEIROUSDT|gen_f3124a14: tempo (budget)
    QUSDT|gen_85fadf54: tempo (budget)
    QUSDT|gen_bf2be656: tempo (budget)
    SEIUSDT|gen_4f890271: tempo (budget)
    SPXUSDT|gen_725cb5f4: tempo (budget)
    STEEMUSDT|gen_4508a416: tempo (budget)
    STXUSDT|gen_14e1775b: tempo (budget)
    SUPERUSDT|gen_0eb999b7: tempo (budget)
    SYRUPUSDT|gen_98d56766: tempo (budget)
    TRUMPUSDT|gen_93131ef1: tempo (budget)
    UBUSDT|gen_f3661202: tempo (budget)
    USELESSUSDT|gen_194e2514: tempo (budget)
    XMRUSDT|gen_35632db9: tempo (budget)
    ZORAUSDT|gen_2c248ee9: tempo (budget)
    ARCUSDT|gen_96c1ed1b: tempo (budget)
    ATOMUSDT|gen_eaa569ba: tempo (budget)
    AVAAIUSDT|gen_14e1775b: tempo (budget)
    AXSUSDT|gen_b922252e: tempo (budget)
    BANKUSDT|gen_87fce2d2: tempo (budget)
    BANKUSDT|gen_8e475cd9: tempo (budget)
    BMTUSDT|gen_571cdda2: tempo (budget)
    BTRUSDT|gen_9a383fff: tempo (budget)
    BULLAUSDT|gen_902fb1fd: tempo (budget)
    CVCUSDT|gen_7b4a474b: tempo (budget)
    DEXEUSDT|gen_10f540ba: tempo (budget)
    DOTUSDT|gen_9588ad8e: tempo (budget)
    GPSUSDT|gen_8a66a70b: tempo (budget)
    GRIFFAINUSDT|gen_de018454: tempo (budget)
    HEIUSDT|gen_e6ddc613: tempo (budget)
    HEMIUSDT|gen_6bc43e03: tempo (budget)
    HEMIUSDT|gen_f4c1300a: tempo (budget)
    HEMIUSDT|gen_f695fd53: tempo (budget)
    HOMEUSDT|gen_116faa2d: tempo (budget)
    JASMYUSDT|gen_b2f350ff: tempo (budget)
    JTOUSDT|gen_35632db9: tempo (budget)
    MUBARAKUSDT|gen_658b2edb: tempo (budget)
    MUBARAKUSDT|gen_cf6a181e: tempo (budget)
    MUBARAKUSDT|gen_e933160c: tempo (budget)
    MUBARAKUSDT|gen_ff3e4154: tempo (budget)
    NEIROUSDT|gen_e132204b: tempo (budget)
    OPENUSDT|gen_f3661202: tempo (budget)
    ORCAUSDT|gen_9a383fff: tempo (budget)
    ORCAUSDT|gen_cb8176f2: tempo (budget)
    PENGUUSDT|gen_a32bee42: tempo (budget)
    PHAUSDT|gen_2b41880d: tempo (budget)
    PHAUSDT|gen_c5194ce4: tempo (budget)
    PHAUSDT|gen_fa304106: tempo (budget)
    PLUMEUSDT|gen_902fb1fd: tempo (budget)
    QUSDT|gen_cde82a91: tempo (budget)
    RAYSOLUSDT|gen_fa304106: tempo (budget)
    RENDERUSDT|gen_acfd527a: tempo (budget)
    SAHARAUSDT|gen_6b94025f: tempo (budget)
    SAHARAUSDT|gen_95aff747: tempo (budget)
    SCRUSDT|gen_bd8f158b: tempo (budget)
    SKYAIUSDT|gen_6191df86: tempo (budget)
    SKYAIUSDT|gen_c61d9322: tempo (budget)
    SOLUSDT|gen_f3124a14: tempo (budget)
    SOPHUSDT|gen_42acf37e: tempo (budget)
    SPXUSDT|gen_d53c153b: tempo (budget)
    STXUSDT|gen_a5b0e4de: tempo (budget)
    STXUSDT|gen_acfd527a: tempo (budget)
    SUIUSDT|gen_8c9b332f: tempo (budget)
    SYRUPUSDT|gen_b7d57ce7: tempo (budget)
    SYRUPUSDT|gen_f3b97917: tempo (budget)
    TAUSDT|gen_4e6e1ae0: tempo (budget)
    TAUSDT|gen_b028553e: tempo (budget)
    TAUSDT|gen_bf2be656: tempo (budget)
    UBUSDT|gen_5b847426: tempo (budget)
    UBUSDT|gen_8931b93c: tempo (budget)
    VETUSDT|gen_b2f350ff: tempo (budget)
    VETUSDT|gen_b9c251a1: tempo (budget)
    VETUSDT|gen_fca11c08: tempo (budget)
    XPINUSDT|gen_ba0c8feb: tempo (budget)
    XPINUSDT|gen_c60cc1b9: tempo (budget)
    XPLUSDT|gen_a220b439: tempo (budget)
    XPLUSDT|gen_b437a671: tempo (budget)
    XRPUSDT|gen_50905b4a: tempo (budget)
    XRPUSDT|gen_a22411e3: tempo (budget)
    ZKUSDT|gen_98837ec2: tempo (budget)

LETTURA: 54/94 ingressi abbinati (57%): la regola non scatta e i dati non spiegano perche' (36 su 40 non abbinati) — da guardare a mano.
  NB: i trade del motore sono simulati sulla storia intera, senza holdout; «stop» del
      motore e' dedotto (il SimTrade non porta il motivo). Questo comando misura e basta.
[ingressi] finito in 735s
```
