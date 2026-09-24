# 0184-portafoglio-24set.req

_eseguito: 2026-09-24 06:36 UTC_

**richiesta:** `portafoglio`
**eseguito:** `.venv/bin/python -m scripts.portafoglio_backtest`
**esito:** codice 0 in 183.8s

```
[firebase] connesso (Firestore + RTDB)
==========================================================================
PORTAFOGLIO: 59 coppie validate su 27 coin, ultimi 60 giorni a 15m
  limiti del bot: max 5 posizioni · una per coin · tetto coin/giorno 1.5% · cooldown 1.00 h · rischio 1%/trade
==========================================================================
[backtest] dati da binance: 6145 candele
  [ 1/27] BICOUSDT         6145 candele · 1 strategie ·   10 trade
[backtest] dati da binance: 6145 candele
  [ 2/27] BULLAUSDT        6145 candele · 1 strategie ·    8 trade
[backtest] dati da binance: 6145 candele
  [ 3/27] DEXEUSDT         6145 candele · 2 strategie ·   21 trade
[backtest] dati da binance: 6145 candele
  [ 4/27] DOTUSDT          6145 candele · 3 strategie ·   23 trade
[backtest] dati da binance: 6145 candele
  [ 5/27] EGLDUSDT         6145 candele · 1 strategie ·   13 trade
[backtest] dati da binance: 6145 candele
  [ 6/27] GPSUSDT          6145 candele · 2 strategie ·   23 trade
[backtest] dati da binance: 6145 candele
  [ 7/27] HEIUSDT          6145 candele · 1 strategie ·    9 trade
[backtest] dati da binance: 6145 candele
  [ 8/27] HEMIUSDT         6145 candele · 2 strategie ·   24 trade
[backtest] dati da binance: 6145 candele
  [ 9/27] JASMYUSDT        6145 candele · 1 strategie ·   12 trade
[backtest] dati da binance: 6145 candele
  [10/27] JTOUSDT          6145 candele · 2 strategie ·   31 trade
[backtest] dati da binance: 6145 candele
  [11/27] MUBARAKUSDT      6145 candele · 4 strategie ·   37 trade
[backtest] dati da binance: 6145 candele
  [12/27] NEIROUSDT        6145 candele · 3 strategie ·   27 trade
[backtest] dati da binance: 6145 candele
  [13/27] ORCAUSDT         6145 candele · 8 strategie ·  106 trade
[backtest] dati da binance: 6145 candele
  [14/27] PROMUSDT         6145 candele · 2 strategie ·   38 trade
[backtest] dati da binance: 6145 candele
  [15/27] QUSDT            6145 candele · 2 strategie ·   32 trade
[backtest] dati da binance: 6145 candele
  [16/27] SAHARAUSDT       6145 candele · 1 strategie ·   17 trade
[backtest] dati da binance: 6145 candele
  [17/27] SCRUSDT          6145 candele · 1 strategie ·   13 trade
[backtest] dati da binance: 6145 candele
  [18/27] SEIUSDT          6145 candele · 1 strategie ·   11 trade
[backtest] dati da binance: 6145 candele
  [19/27] SKYAIUSDT        6145 candele · 5 strategie ·   46 trade
[backtest] dati da binance: 6145 candele
  [20/27] SPXUSDT          6145 candele · 3 strategie ·   56 trade
[backtest] dati da binance: 6145 candele
  [21/27] STXUSDT          6145 candele · 3 strategie ·   33 trade
[backtest] dati da binance: 6145 candele
  [22/27] SYRUPUSDT        6145 candele · 1 strategie ·   19 trade
[backtest] dati da binance: 6145 candele
  [23/27] TRUMPUSDT        6145 candele · 3 strategie ·   30 trade
[backtest] dati da binance: 6145 candele
  [24/27] TUTUSDT          6145 candele · 1 strategie ·   19 trade
[backtest] dati da binance: 6145 candele
  [25/27] USELESSUSDT      6145 candele · 3 strategie ·   70 trade
[backtest] dati da binance: 6145 candele
  [26/27] VETUSDT          6145 candele · 1 strategie ·   35 trade
[backtest] dati da binance: 6145 candele
  [27/27] ZKUSDT           6145 candele · 1 strategie ·    8 trade

coppie simulate 59 · saltate 0 · trade candidati 771

==========================================================================
LE COPPIE INSIEME, IN ORDINE DI TEMPO: senza e con tetto per direzione
==========================================================================
                                         senza tetto    tetto 3%/dir
  ------------------------------------------------------------------
  trade aperti                                   526             520
    saltati: coin_gia_aperta                     209             203
    saltati: max_posizioni                        21              11
    saltati: cooldown                             13              12
    saltati: tetto_coin_giorno                     2               2
    saltati: tetto_direzione                       0              23
    di cui short fermati dal tetto                 0              11
    di cui long fermati dal tetto                  0              12
  trade al giorno (min/media/max)           0/8.6/21        0/8.5/20
  posizioni contemporanee (max/media)           5/2.5           5/2.4
  stessa direzione, max contemporanee               5               4
  quota altre aperte, stessa direzione             51%             50%
  long: n / PnL                          210 / +8208     208 / +8865
  short: n / PnL                         316 / +2178     312 / +3119
  giorni in utile / in perdita               39 / 22         39 / 22
  PnL totale                               +10385.58       +11983.14
  equity finale                             20385.58        21983.14
  max drawdown                                16.25%          16.25%

  i 5 giorni peggiori (senza tetto → con tetto)
    2026-08-26    -832.12  →    -677.39
    2026-08-30    -827.33  →    -894.84
    2026-09-06    -766.05  →    -820.09
    2026-09-23    -666.65  →    -718.89
    2026-09-09    -636.32  →    -681.20

Lettura: con il tetto del 3% per direzione si saltano 23 trade (11 short, 12 long); il PnL passa da +10386 a +11983, il drawdown da 16.25% a 16.25%, le posizioni contemporanee nella stessa direzione da 5 a 4.

[firebase] pubblicazione saltata (400 Property con_tetto contains an invalid nested entity.).
```
