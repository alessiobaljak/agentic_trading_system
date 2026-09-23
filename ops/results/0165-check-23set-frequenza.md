# 0165-check-23set-frequenza.req

_eseguito: 2026-09-23 06:04 UTC_

**richiesta:** `frequenza`
**eseguito:** `.venv/bin/python -m scripts.signal_frequency`
**esito:** codice 0 in 102.8s

```
[firebase] connesso (Firestore + RTDB)
Conto i trade attesi negli ultimi ~7g su 27 coin (15m, da 2026-09-12)...

[backtest] ATTENZIONE BICOUSDT: solo serie PARZIALE disponibile (1081 candele, ultima 2026-09-23) — non cacheata
[backtest] ATTENZIONE BULLAUSDT: solo serie PARZIALE disponibile (1081 candele, ultima 2026-09-23) — non cacheata
[backtest] ATTENZIONE DEXEUSDT: solo serie PARZIALE disponibile (1081 candele, ultima 2026-09-23) — non cacheata
[backtest] ATTENZIONE DOTUSDT: solo serie PARZIALE disponibile (1081 candele, ultima 2026-09-23) — non cacheata
[backtest] ATTENZIONE EGLDUSDT: solo serie PARZIALE disponibile (1081 candele, ultima 2026-09-23) — non cacheata
[backtest] ATTENZIONE GPSUSDT: solo serie PARZIALE disponibile (1081 candele, ultima 2026-09-23) — non cacheata
[backtest] ATTENZIONE HEIUSDT: solo serie PARZIALE disponibile (1081 candele, ultima 2026-09-23) — non cacheata
[backtest] ATTENZIONE HEMIUSDT: solo serie PARZIALE disponibile (1081 candele, ultima 2026-09-23) — non cacheata
[backtest] ATTENZIONE JASMYUSDT: solo serie PARZIALE disponibile (1081 candele, ultima 2026-09-23) — non cacheata
[backtest] ATTENZIONE JTOUSDT: solo serie PARZIALE disponibile (1081 candele, ultima 2026-09-23) — non cacheata
[backtest] ATTENZIONE MUBARAKUSDT: solo serie PARZIALE disponibile (1081 candele, ultima 2026-09-23) — non cacheata
[backtest] ATTENZIONE NEIROUSDT: solo serie PARZIALE disponibile (1081 candele, ultima 2026-09-23) — non cacheata
[backtest] ATTENZIONE ORCAUSDT: solo serie PARZIALE disponibile (1081 candele, ultima 2026-09-23) — non cacheata
[backtest] ATTENZIONE PROMUSDT: solo serie PARZIALE disponibile (1081 candele, ultima 2026-09-23) — non cacheata
[backtest] ATTENZIONE QUSDT: solo serie PARZIALE disponibile (1081 candele, ultima 2026-09-23) — non cacheata
[backtest] ATTENZIONE SAHARAUSDT: solo serie PARZIALE disponibile (1081 candele, ultima 2026-09-23) — non cacheata
[backtest] ATTENZIONE SCRUSDT: solo serie PARZIALE disponibile (1081 candele, ultima 2026-09-23) — non cacheata
[backtest] ATTENZIONE SEIUSDT: solo serie PARZIALE disponibile (1081 candele, ultima 2026-09-23) — non cacheata
[backtest] ATTENZIONE SKYAIUSDT: solo serie PARZIALE disponibile (1081 candele, ultima 2026-09-23) — non cacheata
[backtest] ATTENZIONE SPXUSDT: solo serie PARZIALE disponibile (1081 candele, ultima 2026-09-23) — non cacheata
[backtest] ATTENZIONE STXUSDT: solo serie PARZIALE disponibile (1081 candele, ultima 2026-09-23) — non cacheata
[backtest] ATTENZIONE SYRUPUSDT: solo serie PARZIALE disponibile (1081 candele, ultima 2026-09-23) — non cacheata
[backtest] ATTENZIONE TRUMPUSDT: solo serie PARZIALE disponibile (1081 candele, ultima 2026-09-23) — non cacheata
[backtest] ATTENZIONE TUTUSDT: solo serie PARZIALE disponibile (1081 candele, ultima 2026-09-23) — non cacheata
[backtest] ATTENZIONE USELESSUSDT: solo serie PARZIALE disponibile (1081 candele, ultima 2026-09-23) — non cacheata
[backtest] ATTENZIONE VETUSDT: solo serie PARZIALE disponibile (1081 candele, ultima 2026-09-23) — non cacheata
[backtest] ATTENZIONE ZKUSDT: solo serie PARZIALE disponibile (1081 candele, ultima 2026-09-23) — non cacheata
========================================================
SEGNALI GREZZI negli ultimi ~7 giorni: 89  (~12.7/giorno)
DI CUI APRIBILI dal bot:            69  (~9.9/giorno)
  Il grezzo somma ogni strategia per conto suo; il bot tiene UNA
  posizione per moneta, quindi i segnali sovrapposti sulla stessa coin
  non entrano. E' il secondo numero che va confrontato col paper.

APRIBILI giorno per giorno (UTC):
  2026-09-14   6
  2026-09-15   3
  2026-09-16   6
  2026-09-17   7
  2026-09-18   11
  2026-09-19   5
  2026-09-20   9
  2026-09-21   15
  2026-09-22   6
  2026-09-23   1   (oggi, parziale: fino all'ultima candela)
  Confronta gli ULTIMI giorni coi trade veri del paper: i primi della
  finestra usano le coppie validate di oggi su un registro che allora
  ne aveva meno, quindi sovrastimano.

Per coin (attive):
  STXUSDT        12
  TRUMPUSDT      9
  MUBARAKUSDT    8
  USELESSUSDT    7
  VETUSDT        7
  SPXUSDT        6
  NEIROUSDT      5
  PROMUSDT       5
  TUTUSDT        5
  DEXEUSDT       4
  ORCAUSDT       4
  QUSDT          4
  SYRUPUSDT      4
  GPSUSDT        3
  HEMIUSDT       2
  DOTUSDT        1
  EGLDUSDT       1
  JTOUSDT        1
  SAHARAUSDT     1

Per strategia:
  gen_6d06dca0       11
  gen_2031005e       7
  gen_4465723e       5
  gen_93131ef1       4
  gen_108c996b       4
  gen_e132204b       4
  gen_b9bf5d01       4
  gen_14e1775b       4
  gen_68ebd3b9       4
  gen_af734c68       4
  gen_fa304106       3
  gen_2053cba6       3
  gen_cd5c842f       3
  gen_ba3a671f       3
  gen_725cb5f4       3
  gen_0e000630       3
  gen_bf1e00d4       2
  gen_ff3e4154       2
  gen_1f7ead60       2
  gen_452d4511       2
  gen_18c839a0       2
  gen_bf2be656       2
  gen_b31d8b93       1
  gen_919c110c       1
  gen_36b0e335       1
  gen_871647b8       1
  gen_f238d283       1
  gen_1e2af031       1
  gen_f3124a14       1
  gen_6b94025f       1

Lettura: se questo totale e' ~0, il mercato e' tranquillo e lo zero-trade
del live e' CORRETTO. Se e' alto (molti/giorno) ma il live non apre, allora
c'e' qualcosa nel percorso live che sopprime i segnali -> bug da cacciare.
```
