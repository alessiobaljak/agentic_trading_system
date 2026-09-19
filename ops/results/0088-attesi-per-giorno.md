# 0088-attesi-per-giorno.req

_eseguito: 2026-09-19 12:02 UTC_

**richiesta:** `frequenza`
**eseguito:** `.venv/bin/python -m scripts.signal_frequency`
**esito:** codice 0 in 17.5s

```
[firebase] connesso (Firestore + RTDB)
Conto i trade attesi negli ultimi ~7g su 24 coin (15m, da 2026-09-08)...

[backtest] dati da cache: 1057 candele (BICOUSDT 15m)
[backtest] dati da cache: 1057 candele (DEXEUSDT 15m)
[backtest] dati da cache: 1057 candele (DOTUSDT 15m)
[backtest] dati da cache: 1057 candele (EGLDUSDT 15m)
[backtest] dati da cache: 1057 candele (GPSUSDT 15m)
[backtest] dati da cache: 1057 candele (HEIUSDT 15m)
[backtest] dati da cache: 1057 candele (HEMIUSDT 15m)
[backtest] dati da cache: 1057 candele (JASMYUSDT 15m)
[backtest] dati da cache: 1057 candele (JTOUSDT 15m)
[backtest] dati da cache: 1057 candele (MUBARAKUSDT 15m)
[backtest] dati da cache: 1057 candele (NEIROUSDT 15m)
[backtest] dati da cache: 1057 candele (ORCAUSDT 15m)
[backtest] dati da cache: 1057 candele (PROMUSDT 15m)
[backtest] dati da cache: 1057 candele (QUSDT 15m)
[backtest] dati da cache: 1057 candele (SAHARAUSDT 15m)
[backtest] dati da cache: 1057 candele (SEIUSDT 15m)
[backtest] dati da cache: 1057 candele (SKYAIUSDT 15m)
[backtest] dati da cache: 1057 candele (SPXUSDT 15m)
[backtest] dati da cache: 1057 candele (STXUSDT 15m)
[backtest] dati da cache: 1057 candele (SYRUPUSDT 15m)
[backtest] dati da cache: 1057 candele (TUTUSDT 15m)
[backtest] dati da cache: 1057 candele (USELESSUSDT 15m)
[backtest] dati da cache: 1057 candele (VETUSDT 15m)
[backtest] dati da cache: 1057 candele (ZKUSDT 15m)
========================================================
SEGNALI GREZZI negli ultimi ~7 giorni: 68  (~9.7/giorno)
DI CUI APRIBILI dal bot:            44  (~6.3/giorno)
  Il grezzo somma ogni strategia per conto suo; il bot tiene UNA
  posizione per moneta, quindi i segnali sovrapposti sulla stessa coin
  non entrano. E' il secondo numero che va confrontato col paper.

APRIBILI giorno per giorno (UTC):
  2026-09-10   5
  2026-09-11   5
  2026-09-12   5
  2026-09-13   10
  2026-09-14   3
  2026-09-15   3
  2026-09-16   4
  2026-09-17   6
  2026-09-18   3
  Confronta gli ULTIMI giorni coi trade veri del paper: i primi della
  finestra usano le coppie validate di oggi su un registro che allora
  ne aveva meno, quindi sovrastimano.

Per coin (attive):
  ORCAUSDT       14
  USELESSUSDT    8
  SPXUSDT        6
  SKYAIUSDT      5
  NEIROUSDT      4
  SAHARAUSDT     4
  STXUSDT        4
  GPSUSDT        3
  SYRUPUSDT      3
  TUTUSDT        3
  DEXEUSDT       2
  HEMIUSDT       2
  MUBARAKUSDT    2
  DOTUSDT        1
  HEIUSDT        1
  JASMYUSDT      1
  JTOUSDT        1
  PROMUSDT       1
  QUSDT          1
  VETUSDT        1
  ZKUSDT         1

Per strategia:
  gen_2031005e       6
  gen_6b94025f       4
  gen_bf1e00d4       3
  gen_e6ddc613       3
  gen_5b847426       3
  gen_bbe21d3f       3
  gen_6d06dca0       3
  gen_ba3a671f       3
  gen_725cb5f4       3
  gen_af734c68       3
  gen_4465723e       3
  gen_ff3e4154       2
  gen_f3124a14       2
  gen_d53c153b       2
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
  gen_14e1775b       1
  gen_68ebd3b9       1
  gen_194e2514       1
  gen_1bb04e1a       1

Lettura: se questo totale e' ~0, il mercato e' tranquillo e lo zero-trade
del live e' CORRETTO. Se e' alto (molti/giorno) ma il live non apre, allora
c'e' qualcosa nel percorso live che sopprime i segnali -> bug da cacciare.
```
