# 0623-18ott-storia-stato.req

_eseguito: 2026-10-18 09:03 UTC_

**richiesta:** `stato`
**eseguito:** `.venv/bin/python -m scripts.state_snapshot --no-write`
**esito:** codice 0 in 4.7s

```
[firebase] connesso (Firestore + RTDB)
# Stato sistema (snapshot)
_Generato: 2026-10-18 09:03 UTC_

## Bot
- stato: **running** (🟢 online)
- regime: sideways
- DRY_RUN: True
- equity: **$825.59**
- ultimo heartbeat: 2026-10-18 09:03 UTC
- stream prezzi: 🟢 attivo

## Ultima decisione
- esito: **⚪ FLAT** (2026-10-18 09:02 UTC)
- motivo: nessun segnale valido sopra soglia
- asset valutati: 80 · segnali: 0

## Posizioni aperte
- AIOUSDT: long qty=1229.506286774789 @ 0.03059 uPnL=0.3373537912210136 · rischio 0.09% · leva 1.0x
- TRUMPUSDT: short qty=47.449206544003246 @ 1.742 uPnL=0.38479662967111306 · rischio 0.23% · leva 1.0x
- XPINUSDT: long qty=35674.84488396719 @ 0.0007115 uPnL=-0.14683312404621585 · rischio 0.11% · leva 2.0x
- **rischio aperto totale: 0.44%** dell'equity su 3 posizioni

## GATE 1 — Validazione strategie
- stato: **✅ SUPERATO — pronti per il paper trading**
- copertura universo: **80/200 crypto (40%)** · obiettivo ≥ 35%
- coppie validate (>= 3 pass OOS): **249**
- universo scansionato: 0GUSDT, 1000BONKUSDT, 1000PEPEUSDT, 1000RATSUSDT, 1000SHIBUSDT, AAVEUSDT, ACEUSDT, ADAUSDT, AEROUSDT, AINUSDT, AKEUSDT, ALGOUSDT, ALTUSDT, APEUSDT, API3USDT, APRUSDT, APTUSDT, ARBUSDT, ARCUSDT, ARUSDT, ARXUSDT, ASTERUSDT, ATOMUSDT, AVAUSDT, AVAXUSDT, AXLUSDT, AXSUSDT, AZTECUSDT, BANKUSDT, BASEDUSDT, BATUSDT, BCHUSDT, BEAMXUSDT, BEATUSDT, BILLUSDT, BLURUSDT, BNBUSDT, BOMEUSDT, BRUSDT, BTCUSDT, BTRUSDT, BTWUSDT, CAKEUSDT, CAPUSDT, CCUSDT, CFXUSDT, CHIPUSDT, CHZUSDT, CKBUSDT, COMPUSDT, COTIUSDT, CRVUSDT, CTKUSDT, CTRUSDT, CTSIUSDT, CTUSDT, CYBERUSDT, DASHUSDT, DATAIPUSDT, DODOXUSDT, DOGEUSDT, DOSUSDT, DOTUSDT, DUSKUSDT, EIGENUSDT, ENAUSDT, ERAUSDT, ETCUSDT, ETHFIUSDT, ETHUSDT, FARTCOINUSDT, FETUSDT, FILUSDT, FLOCKUSDT, GALAUSDT, GPSUSDT, GRAMUSDT, GRASSUSDT, GTCUSDT, GWEIUSDT, HBARUSDT, HUMAUSDT, HYPEUSDT, ICPUSDT, INITUSDT, INJUSDT, IOUSDT, JASMYUSDT, JCTUSDT, JTOUSDT, JUPUSDT, KAIAUSDT, KAITOUSDT, KGENUSDT, LABUSDT, LDOUSDT, LINKUSDT, LITUSDT, LPTUSDT, LSKUSDT, LTCUSDT, LUMIAUSDT, LYNUSDT, MAGICUSDT, MAGMAUSDT, MANTAUSDT, MARSCOINUSDT, MEGAUSDT, METISUSDT, METUSDT, MINAUSDT, MONUSDT, MORPHOUSDT, MOVRUSDT, MUBARAKUSDT, NEARUSDT, NIGHTUSDT, NILUSDT, NMRUSDT, OGNUSDT, ONDOUSDT, ONEUSDT, ONGUSDT, ONUSDT, OPNUSDT, OPUSDT, ORCAUSDT, ORDIUSDT, PARTIUSDT, PAXGUSDT, PENDLEUSDT, PENGUUSDT, PEOPLEUSDT, PHAUSDT, PIXELUSDT, PLUMEUSDT, POLUSDT, PONSUSDT, PROMUSDT, PUMPUSDT, PYTHUSDT, QNTUSDT, QUSDT, RAYSOLUSDT, REDUSDT, RENDERUSDT, RIVERUSDT, RLCUSDT, RSRUSDT, RVNUSDT, SAFEUSDT, SAGAUSDT, SANDUSDT, SEIUSDT, SENTUSDT, SFPUSDT, SKLUSDT, SKYUSDT, SOLUSDT, SOMIUSDT, SOONUSDT, SPXUSDT, STRKUSDT, STXUSDT, SUIUSDT, SUSDT, SYNUSDT, SYRUPUSDT, TAOUSDT, TIAUSDT, TRBUSDT, TRUMPUSDT, TRUTHUSDT, TRXUSDT, UNIUSDT, USELESSUSDT, USUSDT, VETUSDT, VIRTUALUSDT, VVVUSDT, WALUSDT, WIFUSDT, WLDUSDT, WLFIUSDT, WUSDT, XAIUSDT, XAUTUSDT, XLMUSDT, XMRUSDT, XPLUSDT, XRPUSDT, XTZUSDT, ZAMAUSDT, ZECUSDT, ZENUSDT, ZKUSDT, ZROUSDT, 币安人生USDT, 牛来USDT, 龙虾USDT
- aggiornato: 2026-10-13 18:40 UTC

### Salute del registro

- composizione: **0 base** · **2435 generate** (di cui 2100 con almeno una conferma)
- occupazione: 2435/3000 — ok

### Strategie VALIDATE (operate dal bot)
| Coin | Strategia | Passes | PF | PnL OOS | Parametri |
|---|---|---|---|---|---|
| QUSDT | gen_f1e7ff62 | 3 | 2.383 | 192% | scale_r_mults=[1.0, 2.0, 3.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| STXUSDT | gen_0aa0d29c | 3 | 1.663 | 148% | scale_r_mults=[1.0, 1.5, 2.5], sl_to_breakeven=True, profit_lock_keep=0.65 |
| RUNEUSDT | gen_434083c5 | 3 | 1.701 | 146% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.5 |
| UBUSDT | gen_d2a9f9ab | 3 | 3.318 | 138% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.5 |
| STXUSDT | gen_afa705ab | 3 | 1.576 | 136% | scale_r_mults=[0.75, 1.25, 1.75], sl_to_breakeven=True, profit_lock_keep=0.65 |
| CAKEUSDT | gen_b4111d27 | 3 | 1.649 | 120% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| JTOUSDT | gen_94062d5f | 3 | 1.351 | 116% | scale_r_mults=[1.0, 2.0, 3.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| STXUSDT | gen_00e50229 | 3 | 1.339 | 111% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| AINUSDT | gen_5032e290 | 3 | 1.594 | 111% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| AINUSDT | gen_e6dd479a | 3 | 1.594 | 111% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| QUSDT | gen_331ef268 | 3 | 1.785 | 107% | scale_r_mults=[0.75, 1.25, 1.75], sl_to_breakeven=True, profit_lock_keep=0.65 |
| PARTIUSDT | gen_871647b8 | 4 | 2.221 | 107% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.5 |
| PTBUSDT | gen_684d7623 | 3 | 1.871 | 107% | scale_r_mults=[1.0, 1.5, 2.5], sl_to_breakeven=True, profit_lock_keep=0.65 |
| UBUSDT | gen_d926b0fd | 4 | 1.767 | 104% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.35 |
| BANKUSDT | gen_2010adf6 | 3 | 1.586 | 102% | scale_r_mults=[1.0, 2.0, 3.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| XPINUSDT | gen_f311acf9 | 3 | 3.282 | 102% | scale_r_mults=[1.0, 1.5, 2.5], sl_to_breakeven=True, profit_lock_keep=0.65 |
| TRUMPUSDT | gen_d16d1d02 | 3 | 1.591 | 101% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| UBUSDT | gen_d163b751 | 3 | 1.521 | 100% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| UBUSDT | gen_92b77c39 | 3 | 1.502 | 95% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| SYRUPUSDT | gen_4c6df481 | 4 | 1.544 | 90% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.75 |
| XPINUSDT | gen_2e0818c8 | 4 | 4.137 | 89% | scale_r_mults=[0.75, 1.25, 1.75], sl_to_breakeven=True, profit_lock_keep=0.65 |
| UBUSDT | gen_f3e1ade7 | 3 | 2.981 | 88% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| CAKEUSDT | gen_cfe3beb3 | 3 | 1.595 | 87% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.5 |
| BRUSDT | gen_95fb50ce | 3 | 1.727 | 87% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| HUSDT | gen_fb3229db | 3 | 1.61 | 86% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| UBUSDT | gen_fb3229db | 3 | 1.998 | 85% | scale_r_mults=[1.0, 2.0, 3.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| TAUSDT | gen_01fbe76f | 3 | 1.711 | 83% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| AINUSDT | gen_d926b0fd | 3 | 1.541 | 81% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| QUSDT | gen_3ee1484b | 5 | 2.842 | 80% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.75 |
| QUSDT | gen_e75ddbfd | 5 | 2.842 | 80% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.75 |
| UBUSDT | gen_35632db9 | 3 | 2.773 | 79% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.5 |
| SCRUSDT | gen_116faa2d | 3 | 1.962 | 78% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.35 |
| TAUSDT | gen_543186c5 | 4 | 2.012 | 76% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| BULLAUSDT | gen_0eb59b31 | 3 | 2.708 | 76% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.35 |
| SCRUSDT | gen_a524effe | 3 | 1.87 | 76% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.35 |
| IDUSDT | gen_6bc43e03 | 4 | 1.483 | 75% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.5 |
| IDUSDT | gen_c5430258 | 4 | 1.483 | 75% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.5 |
| IDUSDT | gen_dd9238bf | 4 | 1.483 | 75% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.5 |
| XPINUSDT | gen_c60cc1b9 | 4 | 3.25 | 74% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.35 |
| VELVETUSDT | gen_e933160c | 3 | 2.559 | 74% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.35 |
| VELVETUSDT | gen_ff3e4154 | 3 | 2.559 | 74% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.35 |
| SAHARAUSDT | gen_b0d474bb | 3 | 2.086 | 74% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.35 |
| SAHARAUSDT | gen_66848d49 | 3 | 2.228 | 73% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.35 |
| GPSUSDT | gen_871647b8 | 5 | 1.555 | 72% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.5 |
| KERNELUSDT | gen_96ed157e | 3 | 3.627 | 72% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.35 |
| QUSDT | gen_da608d9f | 4 | 2.444 | 71% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.75 |
| HEIUSDT | gen_96efce1b | 3 | 1.491 | 71% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| PARTIUSDT | gen_64263ae7 | 3 | 1.953 | 70% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.5 |
| QUSDT | gen_85fadf54 | 4 | 1.86 | 70% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.75 |
| CROSSUSDT | gen_4e6e1ae0 | 3 | 2.69 | 70% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| EIGENUSDT | gen_1b7827f3 | 3 | 1.475 | 69% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| MUBARAKUSDT | gen_e933160c | 4 | 1.889 | 69% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.35 |
| MUBARAKUSDT | gen_ff3e4154 | 5 | 1.889 | 69% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.35 |
| TAUSDT | gen_194e2514 | 3 | 1.946 | 68% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| TAUSDT | gen_1bb04e1a | 3 | 1.946 | 68% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.65 |


[... 20600 caratteri omessi (testa e coda conservate) ...]

|
| MYXUSDT | gen_8931b93c | 3 | 1.583 | 0% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.5 |
| OPENUSDT | gen_46f0717f | 3 | 2.477 | 0% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| PARTIUSDT | gen_7b4a474b | 3 | 2.213 | 0% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| PENGUUSDT | gen_5b9ed454 | 3 | 2.232 | 0% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| PHAUSDT | gen_bd109329 | 3 | 1.725 | 0% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.35 |
| PTBUSDT | gen_630b2a40 | 3 | 2.368 | 0% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| PTBUSDT | gen_73033c73 | 3 | 2.067 | 0% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.5 |
| PUMPUSDT | gen_13cc61f2 | 3 | 3.302 | 0% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| QUSDT | gen_5905e08d | 3 | 1.856 | 0% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| QUSDT | gen_603e7c77 | 3 | 2.565 | 0% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| QUSDT | gen_f9f8d28d | 3 | 1.783 | 0% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| RENDERUSDT | gen_fe8925b6 | 3 | 2.027 | 0% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.35 |
| SAHARAUSDT | gen_4e1e404e | 3 | 1.445 | 0% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.5 |
| SAHARAUSDT | gen_9d07c7b7 | 3 | 1.618 | 0% | scale_r_mults=[0.75, 1.25, 1.75], sl_to_breakeven=True, profit_lock_keep=0.5 |
| TAUSDT | gen_49c2f657 | 3 | 2.112 | 0% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| TAUSDT | gen_4e6e1ae0 | 3 | 2.15 | 0% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.75 |
| TAUSDT | gen_b0e86c70 | 3 | 2.477 | 0% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.5 |
| TAUSDT | gen_c08c5114 | 3 | 2.962 | 0% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.5 |
| TAUSDT | gen_c647ead7 | 3 | 2.023 | 0% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| TUTUSDT | gen_17b6b561 | 3 | 1.602 | 0% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| UBUSDT | gen_77900c80 | 3 | 3.014 | 0% | scale_r_mults=[1.0, 1.5, 2.5], sl_to_breakeven=True, profit_lock_keep=0.65 |
| USELESSUSDT | gen_96c1ed1b | 3 | 2.06 | 0% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.5 |
| USELESSUSDT | gen_e09c5203 | 3 | 1.636 | 0% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.5 |
| VELVETUSDT | gen_fa304106 | 3 | 1.537 | 0% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.5 |
| XMRUSDT | gen_5642c3d7 | 3 | 1.624 | 0% | scale_r_mults=[0.75, 1.25, 1.75], sl_to_breakeven=True, profit_lock_keep=0.65 |
| XVGUSDT | gen_51d26c6b | 3 | 1.711 | 0% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.65 |

## Ultimo run di ottimizzazione
_aggiornato: 2026-09-21 12:43 UTC · 1320 coppie valutate, 0 passate in questo run_

_Nessuna coppia ha passato in questo run._

## Dove muoiono le candidate (autopsia del GATE 1)

**strategie base** — 1320 valutazioni, 0 passate (0.00%) · 2026-09-21 12:43 UTC

| Criterio che ferma | Casi | Quota |
|---|---|---|
| holdout | 1 | 0.1% |
| pf_ex_top | 3 | 0.2% |
| consistency | 17 | 1.3% |
| trades | 6 | 0.5% |
| regime | 22 | 1.7% |
| recovery | 64 | 4.8% |
| total_return | 1207 | 91.4% |

- quasi-passaggi (un solo criterio, di poco): **1** — sono i semi delle mutazioni del run successivo

**strategie generate** — 34048 valutazioni, 113 passate (0.33%) · 2026-10-13 18:40 UTC

| Criterio che ferma | Casi | Quota |
|---|---|---|
| holdout | 153 | 0.5% |
| pf_ex_top | 242 | 0.7% |
| consistency | 589 | 1.7% |
| trades | 936 | 2.8% |
| regime | 2815 | 8.3% |
| recovery | 2737 | 8.1% |
| total_return | 26463 | 78.0% |

- quasi-passaggi (un solo criterio, di poco): **40** — sono i semi delle mutazioni del run successivo

## Supervisore (taratura automatica)

- ultimo giro: 2026-10-18 09:01 UTC · coppie validate: **278** · GATE 1 pronto: True
- tasso di passaggio misurato: **0.320%**

**Parametri modificati rispetto ai default:**

| Parametro | Valore |
|---|---|
| GATE_WIN_RATE_FLOOR | 0.396614 |

**Ultime decisioni:**

- `none` — GATE 1 superato: il paper opera, la taratura si ferma
- `none` — GATE 1 superato: il paper opera, la taratura si ferma
- `none` — GATE 1 superato: il paper opera, la taratura si ferma
- `none` — GATE 1 superato: il paper opera, la taratura si ferma
- `none` — GATE 1 superato: il paper opera, la taratura si ferma

## Trade chiusi — perché usciamo
- totale: **707** · vinti: 393 (56%) · PnL realizzato: **-174.41**
- confronto col mercato: noi -17.44% vs BTC buy&hold +7.94% nello stesso periodo → **sotto** il mercato

- costi: **85.78 USDT** su 707 trade (0.12/trade) _(stimati dal modello del gate, non misurati dai fill)_
  - commissioni 48.07 · spread 37.40 · funding +0.31
  - lordo -88.62 → netto -174.41 · **break-even 10.39%** dell'equity
  - piu' costose: UBUSDT 3.95 · DEXEUSDT 3.93 · SYRUPUSDT 3.58 · XPINUSDT 2.87 · ZORAUSDT 2.85
  - ⚠️ Costi operativi elevati: servono 10.39% solo per pareggiare (soglia 1.5%)

| Uscita | Trade | % | PnL |
|---|---|---|---|
| Trailing stop | 313 | 44% | +232.33 |
| Stop loss (prima di qualsiasi TP) | 309 | 44% | -588.72 |
| Scale-out (>=1 TP incassato, residuo a BE) | 63 | 9% | +111.76 |
| Time exit (orizzonte scaduto) | 16 | 2% | +37.10 |
| Take profit (fino all'ultimo gradino) | 6 | 1% | +33.12 |

- gradini raggiunti (su 707 trade): 0 TP: 630 (89%) · 1 TP: 61 (9%) · 2 TP: 10 (1%) · 3 TP: 6 (1%)

- **drawdown di portafoglio: 177.44 USDT** (ritorno -174.41 · recovery -0.98) · max 15 posizioni aperte insieme
  - il gate prometteva recovery ≥ 2.0 per ogni coppia (peggiore in registro: 0.00); il PORTAFOGLIO realizza -0.98
  _uscite in ordine di TEMPO: e' la buca vera, quella che il gate non vede perche' valida una coppia alla volta._

- escursione favorevole (mfe_r, 707 trade): mediana **0.78R** · ≥1R: 34% · ≥1.5R: 13% · ≥3R: 3% · ≥5R: 0%
  _quanto lontano arriva il prezzo, in unità di R: dice se la scala di TP è raggiungibile. Dettaglio: `python -m scripts.mfe_report`_

## Deriva paper vs gate
_il gate promette sulla storia, il paper misura il presente. `drift` = promessa contraddetta -> size/leva frenate subito e fallimento al gate alla prossima passata._

- **globale**: drift · 663 trade · PF vissuto 0.709 vs 2.02 atteso · mfe mediana 0.78R

- **freno globale attivo**: size x0.5 e leva x0.71 (radice) su OGNI trade finche' il PF a 30 giorni resta sotto 0.6 x atteso (motivo: PF 0.71 vs 2.02 atteso · mfe mediana 0.78R < primo TP 1.50R)

| Coppia | Verdetto | Trade | PF vissuto/atteso | Motivo |
|---|---|---|---|---|
| PTBUSDT|gen_684d7623 | drift | 11 | 0.987 / 1.871 | PF 0.99 vs 1.87 atteso · mfe mediana 0.53R < primo TP 1.00R |
| SYRUPUSDT|gen_4c6df481 | drift | 11 | 1.044 / 1.544 | mfe mediana 0.81R < primo TP 2.00R |
| TAUSDT|gen_01fbe76f | drift | 10 | 0.697 / 1.711 | PF 0.70 vs 1.71 atteso · mfe mediana 0.87R < primo TP 1.50R |
| USELESSUSDT|gen_e09c5203 | drift | 8 | 0.686 / 1.636 | PF 0.69 vs 1.64 atteso · mfe mediana 1.05R < primo TP 2.00R |
| QUSDT|gen_18c839a0 | drift | 8 | 0.421 / 2.883 | PF 0.42 vs 2.88 atteso · mfe mediana 0.90R < primo TP 1.50R |
| USELESSUSDT|gen_2031005e | watch | 7 | 0.304 / 1.54 | PF 0.30 vs 1.54 atteso · mfe mediana 0.80R < primo TP 2.00R |
| QUSDT|gen_5905e08d | watch | 7 | 0.628 / 1.856 | PF 0.63 vs 1.86 atteso · mfe mediana 0.80R < primo TP 1.50R |
| GPSUSDT|gen_871647b8 | watch | 7 | 2.443 / 1.555 | mfe mediana 1.20R < primo TP 2.00R |
| MYXUSDT|gen_8931b93c | watch | 6 | 0.36 / 1.583 | PF 0.36 vs 1.58 atteso · mfe mediana 0.79R < primo TP 1.50R |
| XPINUSDT|gen_f311acf9 | watch | 5 | 0.029 / 3.282 | PF 0.03 vs 3.28 atteso · mfe mediana 0.40R < primo TP 1.00R |
| STXUSDT|gen_0aa0d29c | watch | 5 | 1.629 / 1.663 | mfe mediana 0.52R < primo TP 1.00R |
| PNUTUSDT|gen_4810faab | watch | 5 | 2.677 / 2.591 | mfe mediana 1.13R < primo TP 2.00R |
| BANKUSDT|gen_7100bb59 | watch | 5 | 0.771 / 1.938 | PF 0.77 vs 1.94 atteso · mfe mediana 0.45R < primo TP 0.75R |
| HEMIUSDT|gen_acea368d | watch | 5 | 1.161 / 1.784 | mfe mediana 0.95R < primo TP 1.50R |
| TRUMPUSDT|gen_d16d1d02 | watch | 5 | 0.769 / 1.591 | PF 0.77 vs 1.59 atteso · mfe mediana 1.08R < primo TP 2.00R |
| SYRUPUSDT|gen_f3b97917 | watch | 5 | 0.708 / 2.064 | PF 0.71 vs 2.06 atteso · mfe mediana 0.92R < primo TP 2.00R |
| UBUSDT|gen_f3661202 | watch | 4 | 0.547 / 1.679 | PF 0.55 vs 1.68 atteso · mfe mediana 1.03R < primo TP 2.00R |
| AVAAIUSDT|gen_e50a9211 | watch | 4 | 0.345 / 1.525 | PF 0.35 vs 1.52 atteso |
| HUMAUSDT|gen_fca11c08 | watch | 4 | 0.0 / 1.657 | PF 0.00 vs 1.66 atteso · mfe mediana 0.10R < primo TP 2.00R |
| MUBARAKUSDT|gen_49c2f657 | watch | 4 | 0.762 / 1.721 | PF 0.76 vs 1.72 atteso · mfe mediana 0.85R < primo TP 1.50R |

- serie di perdite (freno SPENTO dal 24 set, solo misura): **gen_fa304106** (10 perdite di fila), **gen_f311acf9** (4 perdite di fila)

## Calibrazione della confidenza
_la confidenza del segnale modula size e leva: qui si verifica che predica davvero l'esito, invece di darlo per scontato._

- verdetto: **costante** · 663 trade · correlazione None · influenza applicata **x1.0**
- tutte le strategie generate escono a confidenza 60: la calibrazione non puo' misurare nulla finche' la confidenza non varia (663 trade, confidenza 60-60)

| Fascia di confidenza | Trade | Win rate | Esito medio |
|---|---|---|---|
| 60.0–60.0 | 221 | 56% | -0.35% |
| 60.0–60.0 | 221 | 55% | -0.20% |
| 60.0–60.0 | 221 | 55% | -0.44% |

_se l'esito medio CRESCE dalla fascia bassa all'alta, la confidenza ordina correttamente i trade._
```
