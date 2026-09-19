# 0084-frequenza-segnali.req

_eseguito: 2026-09-19 09:04 UTC_

**richiesta:** `frequenza`
**eseguito:** `.venv/bin/python -m scripts.signal_frequency`
**esito:** codice 0 in 15.9s

```
[firebase] connesso (Firestore + RTDB)
Conto i trade attesi negli ultimi ~7g su 24 coin (1h, da 2026-08-31)...

[backtest] dati da binance: 457 candele
[backtest] dati da binance: 457 candele
[backtest] dati da binance: 457 candele
[backtest] dati da binance: 457 candele
[backtest] dati da binance: 457 candele
[backtest] dati da binance: 457 candele
[backtest] dati da binance: 457 candele
[backtest] dati da binance: 457 candele
[backtest] dati da binance: 457 candele
[backtest] dati da binance: 457 candele
[backtest] dati da binance: 457 candele
[backtest] dati da binance: 457 candele
[backtest] dati da binance: 457 candele
[backtest] dati da binance: 457 candele
[backtest] dati da binance: 457 candele
[backtest] dati da binance: 457 candele
[backtest] dati da binance: 457 candele
[backtest] dati da binance: 457 candele
[backtest] dati da binance: 457 candele
[backtest] dati da binance: 457 candele
[backtest] dati da binance: 457 candele
[backtest] dati da binance: 457 candele
[backtest] dati da binance: 457 candele
[backtest] dati da binance: 457 candele
========================================================
TRADE ATTESI negli ultimi ~7 giorni: 22  (~3.1/giorno)

Per coin (attive):
  HEMIUSDT       4
  SKYAIUSDT      4
  DOTUSDT        2
  HEIUSDT        2
  SPXUSDT        2
  BICOUSDT       1
  DEXEUSDT       1
  GPSUSDT        1
  PROMUSDT       1
  SAHARAUSDT     1
  TUTUSDT        1
  USELESSUSDT    1
  ZKUSDT         1

Per strategia:
  gen_e6ddc613       2
  gen_93131ef1       2
  gen_108c996b       2
  gen_98837ec2       2
  gen_f238d283       1
  gen_b31d8b93       1
  gen_d85b1f05       1
  gen_da39a23a       1
  gen_bf1e00d4       1
  gen_cd5c842f       1
  gen_6b94025f       1
  gen_c61d9322       1
  gen_6cf80ae6       1
  gen_eb2ece0c       1
  gen_d53c153b       1
  gen_725cb5f4       1
  gen_4465723e       1
  gen_2031005e       1

Lettura: se questo totale e' ~0, il mercato e' tranquillo e lo zero-trade
del live e' CORRETTO. Se e' alto (molti/giorno) ma il live non apre, allora
c'e' qualcosa nel percorso live che sopprime i segnali -> bug da cacciare.
```
