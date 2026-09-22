# 0150-segnali-attesi-oggi.req

_eseguito: 2026-09-22 17:55 UTC_

**richiesta:** `frequenza`
**eseguito:** `.venv/bin/python -m scripts.signal_frequency`
**esito:** codice 0 in 34.1s

```
[firebase] connesso (Firestore + RTDB)
Conto i trade attesi negli ultimi ~7g su 27 coin (15m, da 2026-09-11)...

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
[backtest] dati da binance: 1057 candele
[backtest] dati da binance: 1057 candele
[backtest] dati da binance: 1057 candele
========================================================
SEGNALI GREZZI negli ultimi ~7 giorni: 94  (~13.4/giorno)
DI CUI APRIBILI dal bot:            64  (~9.1/giorno)
  Il grezzo somma ogni strategia per conto suo; il bot tiene UNA
  posizione per moneta, quindi i segnali sovrapposti sulla stessa coin
  non entrano. E' il secondo numero che va confrontato col paper.

APRIBILI giorno per giorno (UTC):
  2026-09-13   7
  2026-09-14   6
  2026-09-15   4
  2026-09-16   4
  2026-09-17   5
  2026-09-18   7
  2026-09-19   6
  2026-09-20   11
  2026-09-21   14
  Confronta gli ULTIMI giorni coi trade veri del paper: i primi della
  finestra usano le coppie validate di oggi su un registro che allora
  ne aveva meno, quindi sovrastimano.

Per coin (attive):
  ORCAUSDT       15
  STXUSDT        12
  TRUMPUSDT      10
  SPXUSDT        8
  MUBARAKUSDT    6
  QUSDT          6
  VETUSDT        6
  NEIROUSDT      5
  TUTUSDT        5
  DEXEUSDT       4
  PROMUSDT       4
  GPSUSDT        3
  BICOUSDT       2
  HEMIUSDT       2
  SAHARAUSDT     2
  DOTUSDT        1
  EGLDUSDT       1
  SCRUSDT        1
  SYRUPUSDT      1

Per strategia:
  gen_6d06dca0       10
  gen_4465723e       5
  gen_93131ef1       4
  gen_108c996b       4
  gen_ba3a671f       4
  gen_725cb5f4       4
  gen_b9bf5d01       4
  gen_14e1775b       4
  gen_68ebd3b9       4
  gen_0e000630       4
  gen_fa304106       3
  gen_871647b8       3
  gen_d53c153b       3
  gen_5b847426       3
  gen_cd5c842f       3
  gen_18c839a0       3
  gen_bf2be656       3
  gen_f238d283       2
  gen_bf1e00d4       2
  gen_ff3e4154       2
  gen_1f7ead60       2
  gen_9a383fff       2
  gen_e6ddc613       2
  gen_bbe21d3f       2
  gen_6b94025f       2
  gen_b31d8b93       1
  gen_919c110c       1
  gen_36b0e335       1
  gen_1e2af031       1
  gen_2053cba6       1
  gen_f3124a14       1
  gen_e132204b       1
  gen_452d4511       1
  gen_63712f8e       1
  gen_af734c68       1

Lettura: se questo totale e' ~0, il mercato e' tranquillo e lo zero-trade
del live e' CORRETTO. Se e' alto (molti/giorno) ma il live non apre, allora
c'e' qualcosa nel percorso live che sopprime i segnali -> bug da cacciare.
```
