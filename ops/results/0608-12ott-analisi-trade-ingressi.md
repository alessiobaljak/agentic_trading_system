# 0608-12ott-analisi-trade-ingressi.req

_eseguito: 2026-10-12 18:24 UTC_

**richiesta:** `ingressi`
**eseguito:** `.venv/bin/python -m scripts.ingressi_report`
**esito:** codice 0 in 763.7s

```
[firebase] connesso (Firestore + RTDB)
==========================================================================
INGRESSI DEL PAPER, TRADE PER TRADE: dove il motore non entra, e perche'
==========================================================================
PAPER: 508 trade chiusi su 229 coppie · rigirate 229 · tolleranza 2 barre · deadline 720s

── ZORAUSDT|gen_ceab7f6a · 15 trade · 15m · scala globale · BE si · keep globale
[backtest] dati da cache: 42581 candele (ZORAUSDT 15m)
[backtest] dati da cache: 42581 candele (ZORAUSDT 15m)
  motore: 333 trade sulla storia intera, 16 dal primo trade del paper · cooldown 4 barre
  #1  01 Oct 07:00 UTC  long  entry 0.007958  pnl -1.32 USDT (stop_loss)
       ABBINATO: motore alla barra 01 Oct 07:00 (+0 min), direzione uguale
  #2  01 Oct 21:30 UTC  long  entry 0.007785  pnl +1.17 USDT (scale_out)
       ABBINATO: motore alla barra 01 Oct 21:30 (+0 min), direzione uguale
  #3  02 Oct 06:45 UTC  long  entry 0.007922  pnl +0.90 USDT (trailing_stop)
       ABBINATO: motore alla barra 02 Oct 06:45 (+0 min), direzione uguale
  #4  03 Oct 21:15 UTC  long  entry 0.007726  pnl -1.69 USDT (stop_loss)
       ABBINATO: motore alla barra 03 Oct 21:15 (+0 min), direzione uguale
  #5  04 Oct 10:00 UTC  long  entry 0.00776  pnl +0.37 USDT (trailing_stop)
       ABBINATO: motore alla barra 04 Oct 10:00 (+0 min), direzione uguale
  #6  05 Oct 03:00 UTC  long  entry 0.007747  pnl -1.55 USDT (stop_loss)
       ABBINATO: motore alla barra 05 Oct 03:00 (+0 min), direzione uguale
  #7  05 Oct 23:15 UTC  long  entry 0.007676  pnl -0.97 USDT (stop_loss)
       ABBINATO: motore alla barra 05 Oct 23:15 (+0 min), direzione uguale
  #8  06 Oct 13:15 UTC  long  entry 0.00771  pnl -1.13 USDT (stop_loss)
       ABBINATO: motore alla barra 06 Oct 13:15 (+0 min), direzione uguale
  #9  08 Oct 02:45 UTC  long  entry 0.0072  pnl -0.50 USDT (stop_loss)
       ABBINATO: motore alla barra 08 Oct 02:45 (+0 min), direzione uguale
  #10 08 Oct 18:45 UTC  short entry 0.006897  pnl -0.58 USDT (time_exit)
       ABBINATO: motore alla barra 08 Oct 18:45 (+0 min), direzione uguale
  #11 09 Oct 19:15 UTC  long  entry 0.006983  pnl +0.08 USDT (trailing_stop)
       ABBINATO: motore alla barra 09 Oct 19:15 (+0 min), direzione uguale
  #12 10 Oct 18:00 UTC  long  entry 0.007293  pnl +0.50 USDT (trailing_stop)
       ABBINATO: motore alla barra 10 Oct 18:00 (+0 min), direzione uguale
  #13 10 Oct 22:45 UTC  long  entry 0.007318  pnl +0.32 USDT (trailing_stop)
       ABBINATO: motore alla barra 10 Oct 22:45 (+0 min), direzione uguale
  #14 11 Oct 09:30 UTC  long  entry 0.007295  pnl +0.11 USDT (trailing_stop)
       ABBINATO: motore alla barra 11 Oct 09:30 (+0 min), direzione uguale
  #15 11 Oct 21:00 UTC  long  entry 0.007301  pnl +0.68 USDT (scale_out)
       ABBINATO: motore alla barra 11 Oct 21:00 (+0 min), direzione uguale
  ABBINATI 15/15 · «come il bot» (da 200 barre prima del paper): 15/15 abbinati, 16 trade del motore
  [34s]

── PROMUSDT|gen_cd5c842f · 10 trade · 15m · scala globale · BE si · keep globale
[backtest] dati da cache: 60983 candele (PROMUSDT 15m)
[backtest] dati da cache: 60983 candele (PROMUSDT 15m)
  motore: 288 trade sulla storia intera, 10 dal primo trade del paper · cooldown 4 barre
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
       MOTORE_IN_POSIZIONE: dentro il trade del 28 Sep 16:30 (long, uscito 29 Sep 01:15, guadagno dedotto, +1.03%): cascata di un'uscita diversa, non della regola d'ingresso
  #8  05 Oct 09:00 UTC  short entry 6.141  pnl +0.95 USDT (trailing_stop)
       ABBINATO: motore alla barra 05 Oct 09:00 (+0 min), direzione uguale
  #9  07 Oct 02:15 UTC  short entry 5.186  pnl -0.76 USDT (stop_loss)
       ABBINATO: motore alla barra 07 Oct 02:15 (+0 min), direzione uguale
  #10 07 Oct 20:15 UTC  short entry 5.594  pnl +0.42 USDT (trailing_stop)
       ABBINATO: motore alla barra 07 Oct 20:15 (+0 min), direzione uguale
  ABBINATI 8/10 · «come il bot» (da 200 barre prima del paper): 8/10 abbinati, 9 trade del motore
  [77s]

── SYRUPUSDT|gen_4c6df481 · 10 trade · 15m · scala 2/4/6 · BE si · keep 0.75
[backtest] cache ESTESA di 169 candele (invece di riscaricarne 50247) (SYRUPUSDT 15m)
[backtest] dati da cache: 50247 candele (SYRUPUSDT 15m)
  motore: 335 trade sulla storia intera, 10 dal primo trade del paper · cooldown 4 barre
  #1  26 Sep 09:45 UTC  long  entry 0.2194  pnl +2.54 USDT (scale_out)
       ABBINATO: motore alla barra 26 Sep 09:45 (+0 min), direzione uguale
  #2  27 Sep 06:15 UTC  short entry 0.2212  pnl -1.41 USDT (stop_loss)
       REGOLA_NON_SCATTA · IGNOTO: stessi valori e la regola non scatta neanche sui valori del paper
       regola sul frame del motore: k-1 no · k no · k+1 no · con 199 candele si · sui valori del paper no · regime motore sideways / paper sideways
  #3  27 Sep 09:00 UTC  long  entry 0.2202  pnl -1.51 USDT (stop_loss)
       ABBINATO: motore alla barra 27 Sep 09:00 (+0 min), direzione uguale
  #4  27 Sep 23:45 UTC  short entry 0.2174  pnl +1.13 USDT (trailing_stop)
       ABBINATO: motore alla barra 27 Sep 23:45 (+0 min), direzione uguale
  #5  02 Oct 01:15 UTC  long  entry 0.2344  pnl +1.37 USDT (trailing_stop)
       ABBINATO: motore alla barra 02 Oct 01:15 (+0 min), direzione uguale
  #6  02 Oct 04:45 UTC  long  entry 0.2361  pnl +3.44 USDT (trailing_stop)
       ABBINATO: motore alla barra 02 Oct 04:45 (+0 min), direzione uguale
  #7  04 Oct 05:30 UTC  long  entry 0.2558  pnl -3.24 USDT (stop_loss)
       ABBINATO: motore alla barra 04 Oct 05:30 (+0 min), direzione uguale
  #8  08 Oct 10:45 UTC  long  entry 0.2297  pnl -1.71 USDT (stop_loss)
       ABBINATO: motore alla barra 08 Oct 10:45 (+0 min), direzione uguale
  #9  10 Oct 15:00 UTC  long  entry 0.2299  pnl +0.12 USDT (trailing_stop)
       ABBINATO: motore alla barra 10 Oct 15:00 (+0 min), direzione uguale
  #10 11 Oct 12:00 UTC  short entry 0.2335  pnl -0.24 USDT (stop_loss)
       ABBINATO: motore alla barra 11 Oct 12:00 (+0 min), direzione uguale
  ABBINATI 9/10 · «come il bot» (da 200 barre prima del paper): 9/10 abbinati, 10 trade del motore
  [112s]

── XPLUSDT|gen_e59ad90b · 10 trade · 15m · scala globale · BE si · keep globale
[backtest] cache ESTESA di 169 candele (invece di riscaricarne 39971) (XPLUSDT 15m)
[backtest] dati da cache: 39971 candele (XPLUSDT 15m)
  motore: 384 trade sulla storia intera, 10 dal primo trade del paper · cooldown 4 barre
  #1  26 Sep 16:00 UTC  short entry 0.1177  pnl +3.89 USDT (scale_out)
       ABBINATO: motore alla barra 26 Sep 16:00 (+0 min), direzione uguale
  #2  28 Sep 01:00 UTC  long  entry 0.1056  pnl -3.76 USDT (stop_loss)
       ABBINATO: motore alla barra 28 Sep 01:00 (+0 min), direzione uguale
  #3  29 Sep 01:00 UTC  long  entry 0.09625  pnl +0.51 USDT (trailing_stop)
       ABBINATO: motore alla barra 29 Sep 01:00 (+0 min), direzione uguale
  #4  29 Sep 12:30 UTC  short entry 0.09996  pnl +0.47 USDT (trailing_stop)
       ABBINATO: motore alla barra 29 Sep 12:30 (+0 min), direzione uguale
  #5  01 Oct 07:15 UTC  short entry 0.09586  pnl +0.37 USDT (trailing_stop)
       ABBINATO: motore alla barra 01 Oct 07:15 (+0 min), direzione uguale
  #6  02 Oct 09:45 UTC  short entry 0.09834  pnl -0.78 USDT (stop_loss)
       ABBINATO: motore alla barra 02 Oct 09:45 (+0 min), direzione uguale
  #7  04 Oct 00:00 UTC  short entry 0.09556  pnl +0.44 USDT (trailing_stop)
       ABBINATO: motore alla barra 04 Oct 00:00 (+0 min), direzione uguale
  #8  04 Oct 21:15 UTC  short entry 0.09629  pnl +0.46 USDT (trailing_stop)
       ABBINATO: motore alla barra 04 Oct 21:15 (+0 min), direzione uguale
  #9  06 Oct 07:45 UTC  long  entry 0.09215  pnl -0.89 USDT (stop_loss)
       ABBINATO: motore alla barra 06 Oct 07:45 (+0 min), direzione uguale
  #10 07 Oct 00:30 UTC  long  entry 0.08981  pnl -0.98 USDT (stop_loss)
       ABBINATO: motore alla barra 07 Oct 00:30 (+0 min), direzione uguale
  ABBINATI 10/10 · «come il bot» (da 200 barre prima del paper): 10/10 abbinati, 10 trade del motore
  [139s]

── TUTUSDT|gen_4465723e · 9 trade · 15m · scala globale · BE si · keep globale
[backtest] cache ESTESA di 169 candele (invece di riscaricarne 54853) (TUTUSDT 15m)
[backtest] dati da cache: 54853 candele (TUTUSDT 15m)
  motore: 333 trade sulla storia intera, 12 dal primo trade del paper · cooldown 4 barre
  #1  18 Sep 05:00 UTC  long  entry 0.02133  pnl -4.34 USDT (stop_loss)
       ABBINATO: motore alla barra 18 Sep 05:00 (+0 min), direzione uguale
  #2  20 Sep 14:00 UTC  long  entry 0.02148  pnl +4.96 USDT (scale_out)
       ABBINATO: motore alla barra 20 Sep 14:00 (+0 min), direzione uguale
  #3  25 Sep 02:30 UTC  short entry 0.02598  pnl +2.31 USDT (trailing_stop)
       ABBINATO: motore alla barra 25 Sep 02:30 (+0 min), direzione uguale
  #4  26 Sep 13:15 UTC  long  entry 0.02573  pnl +1.88 USDT (trailing_stop)
       ABBINATO: motore alla barra 26 Sep 13:15 (+0 min), direzione 

[... 23749 caratteri omessi (testa e coda conservate) ...]

4c6df481              9/10  ( 90%) · come il bot 9/10
    ENAUSDT|gen_bb762669                6/6   (100%) · come il bot 6/6
    HUMAUSDT|gen_771790b1               5/5   (100%) · come il bot 5/5
    QUSDT|gen_18c839a0                  8/8   (100%) · come il bot 8/8
    TUTUSDT|gen_4465723e                9/9   (100%) · come il bot 9/9
    XPLUSDT|gen_e59ad90b               10/10  (100%) · come il bot 10/10
    ZORAUSDT|gen_ceab7f6a              15/15  (100%) · come il bot 15/15
  coppie con piu' non abbinati: SUIUSDT|gen_490a90e5 (7), USELESSUSDT|gen_2031005e (7), ORCAUSDT|gen_fca11c08 (5), DEXEUSDT|gen_fa304106 (3), PROMUSDT|gen_cd5c842f (2), SYRUPUSDT|gen_4c6df481 (1), SPXUSDT|gen_ba3a671f (1), FLOCKUSDT|gen_c5194ce4 (1), GPSUSDT|gen_bf1e00d4 (1), MITOUSDT|gen_8b91ba18 (1)
  non rigirate: 211
    PTBUSDT|gen_684d7623: tempo (budget)
    SPXUSDT|gen_725cb5f4: tempo (budget)
    UBUSDT|gen_fb7d035a: tempo (budget)
    AVAAIUSDT|gen_e50a9211: tempo (budget)
    BULLAUSDT|gen_5a52c06b: tempo (budget)
    BULLAUSDT|gen_7ac562e3: tempo (budget)
    DEXEUSDT|gen_b31d8b93: tempo (budget)
    DOTUSDT|gen_fca11c08: tempo (budget)
    EPICUSDT|gen_dfb554f7: tempo (budget)
    HEMIUSDT|gen_f001d778: tempo (budget)
    HUMAUSDT|gen_fca11c08: tempo (budget)
    MUBARAKUSDT|gen_1f7ead60: tempo (budget)
    STEEMUSDT|gen_4508a416: tempo (budget)
    THEUSDT|gen_658b2edb: tempo (budget)
    TSTUSDT|gen_a640dfa5: tempo (budget)
    USELESSUSDT|gen_c0fd1d91: tempo (budget)
    USELESSUSDT|gen_e09c5203: tempo (budget)
    AIOUSDT|gen_581d4a68: tempo (budget)
    BANKUSDT|gen_fb3d971f: tempo (budget)
    BTRUSDT|gen_8981d5f2: tempo (budget)
    CATIUSDT|gen_b3e46005: tempo (budget)
    CROSSUSDT|gen_d606fde3: tempo (budget)
    FORMUSDT|gen_c647ead7: tempo (budget)
    GALAUSDT|gen_b9aa9989: tempo (budget)
    GPSUSDT|gen_871647b8: tempo (budget)
    HEIUSDT|gen_9a383fff: tempo (budget)
    HUMAUSDT|gen_a32bee42: tempo (budget)
    JTOUSDT|gen_f238d283: tempo (budget)
    ORCAUSDT|gen_6d06dca0: tempo (budget)
    PHAUSDT|gen_fa304106: tempo (budget)
    SEIUSDT|gen_4f890271: tempo (budget)
    STXUSDT|gen_14e1775b: tempo (budget)
    STXUSDT|gen_b9bf5d01: tempo (budget)
    SUIUSDT|gen_8c9b332f: tempo (budget)
    SUPERUSDT|gen_0eb999b7: tempo (budget)
    SYRUPUSDT|gen_af734c68: tempo (budget)
    UBUSDT|gen_f3661202: tempo (budget)
    VETUSDT|gen_6d06dca0: tempo (budget)
    VETUSDT|gen_b9c251a1: tempo (budget)
    ZORAUSDT|gen_2c248ee9: tempo (budget)
    1000PEPEUSDT|gen_f9d90376: tempo (budget)
    AINUSDT|gen_ef115241: tempo (budget)
    AIOUSDT|gen_fc644cd2: tempo (budget)
    AKTUSDT|gen_f4c1300a: tempo (budget)
    ARCUSDT|gen_96c1ed1b: tempo (budget)
    ARKMUSDT|gen_913d0c3a: tempo (budget)
    ASTERUSDT|gen_96efce1b: tempo (budget)
    AVAAIUSDT|gen_08c22b92: tempo (budget)
    AXSUSDT|gen_b922252e: tempo (budget)
    B2USDT|gen_ddb3def9: tempo (budget)
    BICOUSDT|gen_f238d283: tempo (budget)
    BMTUSDT|gen_571cdda2: tempo (budget)
    BMTUSDT|gen_cee79cdd: tempo (budget)
    BRUSDT|gen_95fb50ce: tempo (budget)
    CVCUSDT|gen_7b4a474b: tempo (budget)
    DEXEUSDT|gen_887d87df: tempo (budget)
    DOTUSDT|gen_60c9259a: tempo (budget)
    DOTUSDT|gen_919c110c: tempo (budget)
    FORMUSDT|gen_1eec02f5: tempo (budget)
    GPSUSDT|gen_8a66a70b: tempo (budget)
    GRIFFAINUSDT|gen_de018454: tempo (budget)
    HEMIUSDT|gen_71f018a9: tempo (budget)
    HEMIUSDT|gen_acea368d: tempo (budget)
    HEMIUSDT|gen_c1f71d65: tempo (budget)
    HEMIUSDT|gen_f695fd53: tempo (budget)
    HOMEUSDT|gen_116faa2d: tempo (budget)
    HUSDT|gen_22b2cade: tempo (budget)
    IDOLUSDT|gen_5ad54558: tempo (budget)
    JASMYUSDT|gen_b2f350ff: tempo (budget)
    KERNELUSDT|gen_c647ead7: tempo (budget)
    MAVIAUSDT|gen_608b892e: tempo (budget)
    MUBARAKUSDT|gen_2053cba6: tempo (budget)
    MUBARAKUSDT|gen_49c2f657: tempo (budget)
    MUBARAKUSDT|gen_e933160c: tempo (budget)
    MUBARAKUSDT|gen_ff3e4154: tempo (budget)
    NEIROUSDT|gen_f3124a14: tempo (budget)
    OPENUSDT|gen_2bb283ca: tempo (budget)
    OPENUSDT|gen_46f0717f: tempo (budget)
    OPENUSDT|gen_f3661202: tempo (budget)
    PLUMEUSDT|gen_353f3f19: tempo (budget)
    PLUMEUSDT|gen_902fb1fd: tempo (budget)
    PUMPUSDT|gen_13cc61f2: tempo (budget)
    PUNDIXUSDT|gen_96c1ed1b: tempo (budget)
    QUSDT|gen_85fadf54: tempo (budget)
    QUSDT|gen_bf2be656: tempo (budget)
    RAYSOLUSDT|gen_fa304106: tempo (budget)
    SAHARAUSDT|gen_66848d49: tempo (budget)
    SAHARAUSDT|gen_6b94025f: tempo (budget)
    SCRUSDT|gen_bd8f158b: tempo (budget)
    SOPHUSDT|gen_42acf37e: tempo (budget)
    STXUSDT|gen_a5b0e4de: tempo (budget)
    SYRUPUSDT|gen_98d56766: tempo (budget)
    SYRUPUSDT|gen_f3b97917: tempo (budget)
    TAUSDT|gen_01fbe76f: tempo (budget)
    THEUSDT|gen_a640dfa5: tempo (budget)
    TRUMPUSDT|gen_93131ef1: tempo (budget)
    UBUSDT|gen_0d7be682: tempo (budget)
    UBUSDT|gen_5b847426: tempo (budget)
    USELESSUSDT|gen_194e2514: tempo (budget)
    USELESSUSDT|gen_96c1ed1b: tempo (budget)
    VETUSDT|gen_b2f350ff: tempo (budget)
    XMRUSDT|gen_35632db9: tempo (budget)
    XPINUSDT|gen_c60cc1b9: tempo (budget)
    ZKUSDT|gen_98837ec2: tempo (budget)
    0GUSDT|gen_aa6bb820: tempo (budget)
    1000BONKUSDT|gen_86a8b183: tempo (budget)
    AINUSDT|gen_b6546b33: tempo (budget)
    AINUSDT|gen_d926b0fd: tempo (budget)
    ASTERUSDT|gen_b0e86c70: tempo (budget)
    ASTERUSDT|gen_d74845a5: tempo (budget)
    ATOMUSDT|gen_eaa569ba: tempo (budget)
    AVAAIUSDT|gen_14e1775b: tempo (budget)
    AVAAIUSDT|gen_1eec02f5: tempo (budget)
    AVAAIUSDT|gen_8b91ba18: tempo (budget)
    BANKUSDT|gen_7100bb59: tempo (budget)
    BANKUSDT|gen_87fce2d2: tempo (budget)
    BANKUSDT|gen_8e475cd9: tempo (budget)
    BTRUSDT|gen_8aec28c6: tempo (budget)
    BTRUSDT|gen_9a383fff: tempo (budget)
    BULLAUSDT|gen_32ccfe0c: tempo (budget)
    BULLAUSDT|gen_902fb1fd: tempo (budget)
    CROSSUSDT|gen_4e6e1ae0: tempo (budget)
    CVCUSDT|gen_4c4dac5f: tempo (budget)
    CVCUSDT|gen_8c9b332f: tempo (budget)
    CVCUSDT|gen_cb4d9121: tempo (budget)
    DEXEUSDT|gen_10f540ba: tempo (budget)
    DEXEUSDT|gen_3d4be8c7: tempo (budget)
    DEXEUSDT|gen_b9c251a1: tempo (budget)
    DOTUSDT|gen_9588ad8e: tempo (budget)
    FLOCKUSDT|gen_2350695a: tempo (budget)
    FLOCKUSDT|gen_33de4c13: tempo (budget)
    GPSUSDT|gen_ec2b5fda: tempo (budget)
    GRASSUSDT|gen_f4ac85e0: tempo (budget)
    GUNUSDT|gen_4f890271: tempo (budget)
    HEIUSDT|gen_e6ddc613: tempo (budget)
    HEMIUSDT|gen_4c6df481: tempo (budget)
    HEMIUSDT|gen_6bc43e03: tempo (budget)
    HEMIUSDT|gen_93131ef1: tempo (budget)
    HEMIUSDT|gen_f4c1300a: tempo (budget)
    HUMAUSDT|gen_630b2a40: tempo (budget)
    HUMAUSDT|gen_da39a23a: tempo (budget)
    HYPEUSDT|gen_f19b67e8: tempo (budget)
    IDOLUSDT|gen_931ca7de: tempo (budget)
    IDUSDT|gen_6bc43e03: tempo (budget)
    IDUSDT|gen_fa304106: tempo (budget)
    JTOUSDT|gen_35632db9: tempo (budget)
    JUPUSDT|gen_938d15dc: tempo (budget)
    MITOUSDT|gen_08387bbe: tempo (budget)
    MUBARAKUSDT|gen_658b2edb: tempo (budget)
    MUBARAKUSDT|gen_cf6a181e: tempo (budget)
    MYXUSDT|gen_a5b0e4de: tempo (budget)
    NEIROUSDT|gen_e132204b: tempo (budget)
    ORCAUSDT|gen_271ab7ec: tempo (budget)
    ORCAUSDT|gen_902fb1fd: tempo (budget)
    ORCAUSDT|gen_9a383fff: tempo (budget)
    ORCAUSDT|gen_cb8176f2: tempo (budget)
    ORCAUSDT|gen_fb3d971f: tempo (budget)
    PENGUUSDT|gen_a32bee42: tempo (budget)
    PHAUSDT|gen_2b41880d: tempo (budget)
    PHAUSDT|gen_c5194ce4: tempo (budget)
    PLUMEUSDT|gen_e94b056d: tempo (budget)
    PUMPUSDT|gen_08664b28: tempo (budget)
    PUMPUSDT|gen_1000366e: tempo (budget)
    QUSDT|gen_1f224994: tempo (budget)
    QUSDT|gen_cde82a91: tempo (budget)
    QUSDT|gen_f1e7ff62: tempo (budget)
    RAYSOLUSDT|gen_a01bcc1a: tempo (budget)
    RENDERUSDT|gen_1eec02f5: tempo (budget)
    RENDERUSDT|gen_acfd527a: tempo (budget)
    RENDERUSDT|gen_fdaa6e0b: tempo (budget)
    RSRUSDT|gen_b2f350ff: tempo (budget)
    SAHARAUSDT|gen_1eec02f5: tempo (budget)
    SAHARAUSDT|gen_95aff747: tempo (budget)
    SAHARAUSDT|gen_9839aec0: tempo (budget)
    SAHARAUSDT|gen_cb8176f2: tempo (budget)
    SKYAIUSDT|gen_6191df86: tempo (budget)
    SKYAIUSDT|gen_6cf80ae6: tempo (budget)
    SKYAIUSDT|gen_98837ec2: tempo (budget)
    SKYAIUSDT|gen_bd109329: tempo (budget)
    SKYAIUSDT|gen_c61d9322: tempo (budget)
    SOLUSDT|gen_f3124a14: tempo (budget)
    SPXUSDT|gen_64263ae7: tempo (budget)
    SPXUSDT|gen_d03ff6d4: tempo (budget)
    SPXUSDT|gen_d53c153b: tempo (budget)
    STXUSDT|gen_acfd527a: tempo (budget)
    SYRUPUSDT|gen_b7d57ce7: tempo (budget)
    SYRUPUSDT|gen_f6c63753: tempo (budget)
    TAUSDT|gen_4e6e1ae0: tempo (budget)
    TAUSDT|gen_543186c5: tempo (budget)
    TAUSDT|gen_b028553e: tempo (budget)
    TAUSDT|gen_bf2be656: tempo (budget)
    TAUSDT|gen_c647ead7: tempo (budget)
    UBUSDT|gen_08664b28: tempo (budget)
    UBUSDT|gen_2a2898b0: tempo (budget)
    UBUSDT|gen_8931b93c: tempo (budget)
    UBUSDT|gen_f3e1ade7: tempo (budget)
    UBUSDT|gen_f78ae361: tempo (budget)
    USELESSUSDT|gen_acea368d: tempo (budget)
    VETUSDT|gen_fca11c08: tempo (budget)
    XPINUSDT|gen_2e0818c8: tempo (budget)
    XPINUSDT|gen_6bc43e03: tempo (budget)
    XPINUSDT|gen_902fb1fd: tempo (budget)
    XPINUSDT|gen_9a383fff: tempo (budget)
    XPINUSDT|gen_ba0c8feb: tempo (budget)
    XPINUSDT|gen_f311acf9: tempo (budget)
    XPLUSDT|gen_a220b439: tempo (budget)
    XPLUSDT|gen_b437a671: tempo (budget)
    XRPUSDT|gen_50905b4a: tempo (budget)
    XRPUSDT|gen_a22411e3: tempo (budget)
    ZECUSDT|gen_1623b4cb: tempo (budget)
    ZECUSDT|gen_e6ddc613: tempo (budget)

LETTURA: 102/133 ingressi abbinati (77%): la regola non scatta e i dati non spiegano perche' (25 su 31 non abbinati) — da guardare a mano.
  NB: i trade del motore sono simulati sulla storia intera, senza holdout; «stop» del
      motore e' dedotto (il SimTrade non porta il motivo). Questo comando misura e basta.
[ingressi] finito in 762s
```
