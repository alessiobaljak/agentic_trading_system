# 0182-check-24set-frequenza.req

_eseguito: 2026-09-24 06:15 UTC_

**richiesta:** `frequenza`
**eseguito:** `.venv/bin/python -m scripts.signal_frequency`
**esito:** codice 0 in 103.4s

```
[firebase] connesso (Firestore + RTDB)
Conto i trade attesi negli ultimi ~7g su 27 coin (15m, da 2026-09-13)...

[backtest] ATTENZIONE BICOUSDT: solo serie PARZIALE disponibile (1081 candele, ultima 2026-09-24) — non cacheata
[backtest] ATTENZIONE BULLAUSDT: solo serie PARZIALE disponibile (1081 candele, ultima 2026-09-24) — non cacheata
[backtest] ATTENZIONE DEXEUSDT: solo serie PARZIALE disponibile (1081 candele, ultima 2026-09-24) — non cacheata
[backtest] ATTENZIONE DOTUSDT: solo serie PARZIALE disponibile (1081 candele, ultima 2026-09-24) — non cacheata
[backtest] ATTENZIONE EGLDUSDT: solo serie PARZIALE disponibile (1081 candele, ultima 2026-09-24) — non cacheata
[backtest] ATTENZIONE GPSUSDT: solo serie PARZIALE disponibile (1081 candele, ultima 2026-09-24) — non cacheata
[backtest] ATTENZIONE HEIUSDT: solo serie PARZIALE disponibile (1081 candele, ultima 2026-09-24) — non cacheata
[backtest] ATTENZIONE HEMIUSDT: solo serie PARZIALE disponibile (1081 candele, ultima 2026-09-24) — non cacheata
[backtest] ATTENZIONE JASMYUSDT: solo serie PARZIALE disponibile (1081 candele, ultima 2026-09-24) — non cacheata
[backtest] ATTENZIONE JTOUSDT: solo serie PARZIALE disponibile (1081 candele, ultima 2026-09-24) — non cacheata
[backtest] ATTENZIONE MUBARAKUSDT: solo serie PARZIALE disponibile (1081 candele, ultima 2026-09-24) — non cacheata
[backtest] ATTENZIONE NEIROUSDT: solo serie PARZIALE disponibile (1081 candele, ultima 2026-09-24) — non cacheata
[backtest] ATTENZIONE ORCAUSDT: solo serie PARZIALE disponibile (1081 candele, ultima 2026-09-24) — non cacheata
[backtest] ATTENZIONE PROMUSDT: solo serie PARZIALE disponibile (1081 candele, ultima 2026-09-24) — non cacheata
[backtest] ATTENZIONE QUSDT: solo serie PARZIALE disponibile (1081 candele, ultima 2026-09-24) — non cacheata
[backtest] ATTENZIONE SAHARAUSDT: solo serie PARZIALE disponibile (1081 candele, ultima 2026-09-24) — non cacheata
[backtest] ATTENZIONE SCRUSDT: solo serie PARZIALE disponibile (1081 candele, ultima 2026-09-24) — non cacheata
[backtest] ATTENZIONE SEIUSDT: solo serie PARZIALE disponibile (1081 candele, ultima 2026-09-24) — non cacheata
[backtest] ATTENZIONE SKYAIUSDT: solo serie PARZIALE disponibile (1081 candele, ultima 2026-09-24) — non cacheata
[backtest] ATTENZIONE SPXUSDT: solo serie PARZIALE disponibile (1081 candele, ultima 2026-09-24) — non cacheata
[backtest] ATTENZIONE STXUSDT: solo serie PARZIALE disponibile (1081 candele, ultima 2026-09-24) — non cacheata
[backtest] ATTENZIONE SYRUPUSDT: solo serie PARZIALE disponibile (1081 candele, ultima 2026-09-24) — non cacheata
[backtest] ATTENZIONE TRUMPUSDT: solo serie PARZIALE disponibile (1081 candele, ultima 2026-09-24) — non cacheata
[backtest] ATTENZIONE TUTUSDT: solo serie PARZIALE disponibile (1081 candele, ultima 2026-09-24) — non cacheata
[backtest] ATTENZIONE USELESSUSDT: solo serie PARZIALE disponibile (1081 candele, ultima 2026-09-24) — non cacheata
[backtest] ATTENZIONE VETUSDT: solo serie PARZIALE disponibile (1081 candele, ultima 2026-09-24) — non cacheata
[backtest] ATTENZIONE ZKUSDT: solo serie PARZIALE disponibile (1081 candele, ultima 2026-09-24) — non cacheata
========================================================
SEGNALI GREZZI negli ultimi ~7 giorni: 95  (~13.6/giorno)
DI CUI APRIBILI dal bot:            70  (~10.0/giorno)
  Il grezzo somma ogni strategia per conto suo; il bot tiene UNA
  posizione per moneta, quindi i segnali sovrapposti sulla stessa coin
  non entrano. E' il secondo numero che va confrontato col paper.

APRIBILI giorno per giorno (UTC):
  2026-09-15   3
  2026-09-16   6
  2026-09-17   7
  2026-09-18   11
  2026-09-19   5
  2026-09-20   9
  2026-09-21   15
  2026-09-22   5
  2026-09-23   9
  2026-09-24   0   (oggi, parziale: fino all'ultima candela)
  Confronta gli ULTIMI giorni coi trade veri del paper: i primi della
  finestra usano le coppie validate di oggi su un registro che allora
  ne aveva meno, quindi sovrastimano.

Per coin (attive):
  STXUSDT        12
  TRUMPUSDT      11
  SPXUSDT        10
  MUBARAKUSDT    7
  USELESSUSDT    7
  VETUSDT        7
  DEXEUSDT       5
  PROMUSDT       5
  QUSDT          5
  TUTUSDT        5
  DOTUSDT        4
  NEIROUSDT      4
  SYRUPUSDT      4
  GPSUSDT        3
  ORCAUSDT       3
  JTOUSDT        2
  EGLDUSDT       1

Per strategia:
  gen_6d06dca0       10
  gen_2031005e       7
  gen_ba3a671f       5
  gen_725cb5f4       5
  gen_4465723e       5
  gen_fa304106       4
  gen_b9bf5d01       4
  gen_14e1775b       4
  gen_68ebd3b9       4
  gen_af734c68       4
  gen_93131ef1       4
  gen_108c996b       4
  gen_e132204b       3
  gen_cd5c842f       3
  gen_18c839a0       3
  gen_0e000630       3
  gen_919c110c       2
  gen_bf1e00d4       2
  gen_f238d283       2
  gen_ff3e4154       2
  gen_2053cba6       2
  gen_1f7ead60       2
  gen_452d4511       2
  gen_bf2be656       2
  gen_b31d8b93       1
  gen_d85b1f05       1
  gen_da39a23a       1
  gen_36b0e335       1
  gen_871647b8       1
  gen_1e2af031       1
  gen_f3124a14       1

Lettura: se questo totale e' ~0, il mercato e' tranquillo e lo zero-trade
del live e' CORRETTO. Se e' alto (molti/giorno) ma il live non apre, allora
c'e' qualcosa nel percorso live che sopprime i segnali -> bug da cacciare.
```
