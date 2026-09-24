# 0188-portafoglio-dopo-audit.req

_eseguito: 2026-09-24 07:20 UTC_

**richiesta:** `portafoglio`
**eseguito:** `.venv/bin/python -m scripts.portafoglio_backtest`
**esito:** codice 0 in 121.2s

```
[firebase] connesso (Firestore + RTDB)
==========================================================================
PORTAFOGLIO: 59 coppie validate su 27 coin, dal 2026-07-26 (60 giorni) a 15m
  limiti del bot: max 5 posizioni · una per coin · tetto coin/giorno 1.5% · cooldown 1.00 h · rischio 1%/trade
==========================================================================
[backtest] dati da cache: 6145 candele (BICOUSDT 15m)
  [ 1/27] BICOUSDT         6145 candele · 1 strategie ·   10 trade
[backtest] dati da cache: 6145 candele (BULLAUSDT 15m)
  [ 2/27] BULLAUSDT        6145 candele · 1 strategie ·    8 trade
[backtest] dati da cache: 6145 candele (DEXEUSDT 15m)
  [ 3/27] DEXEUSDT         6145 candele · 2 strategie ·   21 trade
[backtest] dati da cache: 6145 candele (DOTUSDT 15m)
  [ 4/27] DOTUSDT          6145 candele · 3 strategie ·   23 trade
[backtest] dati da cache: 6145 candele (EGLDUSDT 15m)
  [ 5/27] EGLDUSDT         6145 candele · 1 strategie ·   13 trade
[backtest] dati da cache: 6145 candele (GPSUSDT 15m)
  [ 6/27] GPSUSDT          6145 candele · 2 strategie ·   23 trade
[backtest] dati da cache: 6145 candele (HEIUSDT 15m)
  [ 7/27] HEIUSDT          6145 candele · 1 strategie ·    9 trade
[backtest] dati da cache: 6145 candele (HEMIUSDT 15m)
  [ 8/27] HEMIUSDT         6145 candele · 2 strategie ·   24 trade
[backtest] dati da cache: 6145 candele (JASMYUSDT 15m)
  [ 9/27] JASMYUSDT        6145 candele · 1 strategie ·   12 trade
[backtest] dati da cache: 6145 candele (JTOUSDT 15m)
  [10/27] JTOUSDT          6145 candele · 2 strategie ·   31 trade
[backtest] dati da cache: 6145 candele (MUBARAKUSDT 15m)
  [11/27] MUBARAKUSDT      6145 candele · 4 strategie ·   37 trade
[backtest] dati da cache: 6145 candele (NEIROUSDT 15m)
  [12/27] NEIROUSDT        6145 candele · 3 strategie ·   27 trade
[backtest] dati da cache: 6145 candele (ORCAUSDT 15m)
  [13/27] ORCAUSDT         6145 candele · 8 strategie ·  106 trade
[backtest] dati da cache: 6145 candele (PROMUSDT 15m)
  [14/27] PROMUSDT         6145 candele · 2 strategie ·   38 trade
[backtest] dati da cache: 6145 candele (QUSDT 15m)
  [15/27] QUSDT            6145 candele · 2 strategie ·   32 trade
[backtest] dati da cache: 6145 candele (SAHARAUSDT 15m)
  [16/27] SAHARAUSDT       6145 candele · 1 strategie ·   17 trade
[backtest] dati da cache: 6145 candele (SCRUSDT 15m)
  [17/27] SCRUSDT          6145 candele · 1 strategie ·   13 trade
[backtest] dati da cache: 6145 candele (SEIUSDT 15m)
  [18/27] SEIUSDT          6145 candele · 1 strategie ·   11 trade
[backtest] dati da cache: 6145 candele (SKYAIUSDT 15m)
  [19/27] SKYAIUSDT        6145 candele · 5 strategie ·   46 trade
[backtest] dati da cache: 6145 candele (SPXUSDT 15m)
  [20/27] SPXUSDT          6145 candele · 3 strategie ·   56 trade
[backtest] dati da cache: 6145 candele (STXUSDT 15m)
  [21/27] STXUSDT          6145 candele · 3 strategie ·   33 trade
[backtest] dati da cache: 6145 candele (SYRUPUSDT 15m)
  [22/27] SYRUPUSDT        6145 candele · 1 strategie ·   19 trade
[backtest] dati da cache: 6145 candele (TRUMPUSDT 15m)
  [23/27] TRUMPUSDT        6145 candele · 3 strategie ·   30 trade
[backtest] dati da cache: 6145 candele (TUTUSDT 15m)
  [24/27] TUTUSDT          6145 candele · 1 strategie ·   19 trade
[backtest] dati da cache: 6145 candele (USELESSUSDT 15m)
  [25/27] USELESSUSDT      6145 candele · 3 strategie ·   70 trade
[backtest] dati da cache: 6145 candele (VETUSDT 15m)
  [26/27] VETUSDT          6145 candele · 1 strategie ·   35 trade
[backtest] dati da cache: 6145 candele (ZKUSDT 15m)
  [27/27] ZKUSDT           6145 candele · 1 strategie ·    8 trade

coppie simulate 59 · saltate 0 · trade candidati 771

==========================================================================
LE COPPIE INSIEME, IN ORDINE DI TEMPO: i limiti di portafoglio, uno sull'altro
==========================================================================
                                         senza limiti   tetto dir 3%   + stop gg 3%     + netto 2R
  ------------------------------------------------------------------------------------------------
  trade aperti                                    526            490            457            419
    saltati: coin_gia_aperta                      209            196            187            182
    saltati: max_posizioni                         21              9              9              6
    saltati: cooldown                              13             10             10              7
    saltati: tetto_coin_giorno                      2              2              1              1
    saltati: tetto_direzione                        0             64             63             38
    saltati: tetto_giorno                           0              0             44             38
    saltati: netto_r                                0              0              0             80
    di cui short fermati dal tetto dir.              0             38             37             12
    di cui long fermati dal tetto dir.              0             26             26             26
    giorni fermati dallo stop giorno                0              0              9              7
  trade al giorno (min/media/max)            0/8.6/21       0/8.0/19       0/7.5/19       0/6.9/18
  posizioni contemporanee (max/media)           5/2.5          5/2.2          5/2.2          5/2.1
  stessa direzione, max contemporanee               5              3              3              3
  quota altre aperte, stessa direzione            51%            48%            49%            41%
  long: n / PnL                           210 / +8208    200 / +7857    184 / +7129    176 / +6674
  short: n / PnL                          316 / +2178    290 / +1807     273 / +509     243 / +932
  giorni in utile / in perdita                39 / 22        37 / 24        36 / 24        35 / 25
  diversification ratio                          0.17           0.17           0.16           0.16
  PnL totale                                +10385.58       +9664.47       +7638.05       +7606.59
  equity finale                              20385.58       19664.47       17638.05       17606.59
  max drawdown                                 16.25%         17.01%         14.88%         16.15%

  i 5 giorni peggiori (senza limiti → le altre colonne)
    2026-08-26    -832.12  →    -213.29    -187.16     -13.74
    2026-08-30    -827.33  →    -825.21    -548.82    -540.13
    2026-09-06    -766.05  →    -759.94    -451.26    -441.27
    2026-09-23    -666.65  →    -643.07    -635.43    -634.29
    2026-09-09    -636.32  →    -630.48    -558.58    -552.12

  win rate dopo k perdite di fila (per strategia, sui 771 trade candidati; incondizionato 63.7%)
    k       n       WR      diff       t
    1     172    68.6%     +4.9p    1.34
    2      51    51.0%    -12.7p   -1.89
    3      25    76.0%    +12.3p    1.28
    4       6    33.3%    -30.4p   -1.55
    5       4     0.0%    -63.7p   -2.65
  dopo 4 perdite: WR 33.3% su 6 (incondizionato 63.7%, t -1.55)

  diversification ratio 0.17 su 46 coppie che hanno chiuso trade (1 = una scommessa sola, 0 = si annullano): le coppie si compensano molto fra loro.

Lettura: tetto dir 3%: salta 36 trade in piu'; il PnL passa da +10386 a +9664, il drawdown da 16.25% a 17.01%; + stop gg 3%: salta 33 trade in piu'; il PnL passa da +9664 a +7638, il drawdown da 17.01% a 14.88%; + netto 2R: salta 38 trade in piu'; il PnL passa da +7638 a +7607, il drawdown da 14.88% a 16.15%.

[firebase] pubblicato portfolio/backtest.
```
