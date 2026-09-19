# 0085-frequenza-15m.req

_eseguito: 2026-09-19 09:17 UTC_

**richiesta:** `frequenza`
**eseguito:** `.venv/bin/python -m scripts.signal_frequency`
**esito:** codice 0 in 29.0s

```
[firebase] connesso (Firestore + RTDB)
Conto i trade attesi negli ultimi ~7g su 24 coin (15m, da 2026-09-08)...

[backtest] dati da binance: 1057 candele
[backtest] dati da binance: 1057 candele
[backtest] dati da binance: 1057 candele
[backtest] dati da binance: 1057 candele
[backtest] dati da binance: 1057 candele
[backtest] dati da binance: 1057 candele
[backtest] dati da binance: 1057 candele
[backtest] dati da binance: 1057 candele
[backtest] dati da binance: 1057 candele
[backtest] dati da binance: 1057 candele
[backtest] dati da binance: 1057 candele
[backtest] dati da binance: 1057 candele
[backtest] dati da binance: 1057 candele
[backtest] dati da binance: 1057 candele
[backtest] dati da binance: 1057 candele
[backtest] dati da binance: 1057 candele
[backtest] dati da binance: 1057 candele
[backtest] dati da binance: 1057 candele
[backtest] dati da binance: 1057 candele
[backtest] dati da binance: 1057 candele
[backtest] dati da binance: 1057 candele
[backtest] dati da binance: 1057 candele
[backtest] dati da binance: 1057 candele
[backtest] dati da binance: 1057 candele
========================================================
TRADE ATTESI negli ultimi ~7 giorni: 71  (~10.1/giorno)

Per coin (attive):
  ORCAUSDT       14
  USELESSUSDT    8
  SPXUSDT        7
  SKYAIUSDT      5
  PROMUSDT       4
  SAHARAUSDT     4
  STXUSDT        4
  SYRUPUSDT      4
  GPSUSDT        3
  TUTUSDT        3
  DEXEUSDT       2
  HEMIUSDT       2
  MUBARAKUSDT    2
  NEIROUSDT      2
  DOTUSDT        1
  HEIUSDT        1
  JASMYUSDT      1
  JTOUSDT        1
  QUSDT          1
  VETUSDT        1
  ZKUSDT         1

Per strategia:
  gen_2031005e       6
  gen_6b94025f       4
  gen_af734c68       4
  gen_bf1e00d4       3
  gen_e6ddc613       3
  gen_5b847426       3
  gen_bbe21d3f       3
  gen_6d06dca0       3
  gen_452d4511       3
  gen_ba3a671f       3
  gen_725cb5f4       3
  gen_4465723e       3
  gen_ff3e4154       2
  gen_f3124a14       2
  gen_9a383fff       2
  gen_871647b8       2
  gen_98837ec2       2
  gen_c61d9322       2
  gen_b9bf5d01       2
  gen_b31d8b93       1
  gen_fa304106       1
  gen_919c110c       1
  gen_93131ef1       1
  gen_108c996b       1
  gen_b2f350ff       1
  gen_f238d283       1
  gen_cd5c842f       1
  gen_18c839a0       1
  gen_6cf80ae6       1
  gen_eb2ece0c       1
  gen_d53c153b       1
  gen_14e1775b       1
  gen_68ebd3b9       1
  gen_194e2514       1
  gen_1bb04e1a       1

Lettura: se questo totale e' ~0, il mercato e' tranquillo e lo zero-trade
del live e' CORRETTO. Se e' alto (molti/giorno) ma il live non apre, allora
c'e' qualcosa nel percorso live che sopprime i segnali -> bug da cacciare.
```
