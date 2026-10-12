# 0607-12ott-analisi-trade-stato.req

_eseguito: 2026-10-12 18:11 UTC_

**richiesta:** `stato`
**eseguito:** `.venv/bin/python -m scripts.state_snapshot --no-write`
**esito:** codice 0 in 4.6s

```
[firebase] connesso (Firestore + RTDB)
# Stato sistema (snapshot)
_Generato: 2026-10-12 18:11 UTC_

## Bot
- stato: **running** (🟢 online)
- regime: sideways
- DRY_RUN: True
- equity: **$873.79**
- ultimo heartbeat: 2026-10-12 18:10 UTC
- stream prezzi: 🟢 attivo

## Ultima decisione
- esito: **⚪ FLAT** (2026-10-12 18:02 UTC)
- motivo: parita' backtest: 1 segnali validi aperti
- asset valutati: 76 · segnali: 1 · miglior segnale STXUSDT gen_0aa0d29c (conf. 60.0/soglia 30)

## Posizioni aperte
- DEXEUSDT: short qty=46.82137464026086 @ 1.864 uPnL=-0.7008783395789638 · rischio 0.13% · leva 1.0x
- MYXUSDT: long qty=895.1214291406656 @ 0.06584 uPnL=0.5793848134418594 · rischio 0.11% · leva 2.0x
- RENDERUSDT: long qty=14.605762116498804 @ 2.022 uPnL=0.0500950127267341 · rischio 0.13% · leva 1.0x
- STXUSDT: long qty=215.0606372067689 @ 0.4063 uPnL=-0.0230636233048465 · rischio 0.36% · leva 1.0x
- UBUSDT: long qty=684.3948151952912 @ 0.12753 uPnL=1.425772274399739 · rischio 0.32% · leva 1.0x
- ZECUSDT: long qty=0.040982495619924286 @ 1242.64 uPnL=-0.1741174530958693 · rischio 0.13% · leva 1.0x
- **rischio aperto totale: 1.18%** dell'equity su 6 posizioni

## GATE 1 — Validazione strategie
- stato: **✅ SUPERATO — pronti per il paper trading**
- copertura universo: **76/200 crypto (38%)** · obiettivo ≥ 35%
- coppie validate (>= 3 pass OOS): **229**
- universo scansionato: 0GUSDT, 1000BONKUSDT, 1000FLOKIUSDT, 1000PEPEUSDT, 1000SHIBUSDT, AAVEUSDT, ACEUSDT, ADAUSDT, AEROUSDT, AGTUSDT, AINUSDT, AIOTUSDT, AKEUSDT, AKTUSDT, ALGOUSDT, ALTUSDT, APEUSDT, API3USDT, APRUSDT, APTUSDT, ARBUSDT, ARKUSDT, ARPAUSDT, ARUSDT, ARXUSDT, ASTERUSDT, ATOMUSDT, AVAXUSDT, AXLUSDT, AXSUSDT, AZTECUSDT, BANKUSDT, BATUSDT, BCHUSDT, BERAUSDT, BILLUSDT, BNBUSDT, BOMEUSDT, BRUSDT, BTCUSDT, BTRUSDT, BTWUSDT, CAKEUSDT, CAPUSDT, CCUSDT, CFGUSDT, CFXUSDT, CHIPUSDT, CHZUSDT, CKBUSDT, COMPUSDT, COTIUSDT, CRVUSDT, CTKUSDT, CTSIUSDT, CTUSDT, CYBERUSDT, DASHUSDT, DATAIPUSDT, DOGEUSDT, DOSUSDT, DOTUSDT, DYMUSDT, EGLDUSDT, EIGENUSDT, ENAUSDT, ERAUSDT, ETCUSDT, ETHFIUSDT, ETHUSDT, FARTCOINUSDT, FETUSDT, FFUSDT, FILUSDT, FLOWUSDT, GALAUSDT, GRAMUSDT, GRASSUSDT, GTCUSDT, GWEIUSDT, HANAUSDT, HBARUSDT, HEMIUSDT, HUMAUSDT, HYPEUSDT, ICPUSDT, INJUSDT, IOUSDT, JCTUSDT, JSTUSDT, JTOUSDT, JUPUSDT, KAIAUSDT, KGENUSDT, LABUSDT, LAUSDT, LDOUSDT, LINEAUSDT, LINKUSDT, LITUSDT, LPTUSDT, LSKUSDT, LTCUSDT, LUMIAUSDT, MAGICUSDT, MANTAUSDT, MARSCOINUSDT, MEGAUSDT, METISUSDT, METUSDT, MINAUSDT, MONUSDT, MORPHOUSDT, MOVRUSDT, MUBARAKUSDT, NEARUSDT, NEIROUSDT, NEOUSDT, NIGHTUSDT, NILUSDT, NMRUSDT, OGNUSDT, ONDOUSDT, ONEUSDT, ONUSDT, OPUSDT, ORCAUSDT, ORDIUSDT, PAXGUSDT, PENDLEUSDT, PENGUUSDT, PHAUSDT, PIXELUSDT, PLUMEUSDT, POLUSDT, PONSUSDT, PROMUSDT, PUMPUSDT, PYTHUSDT, QNTUSDT, QUSDT, RAYSOLUSDT, REDUSDT, RENDERUSDT, RIVERUSDT, RLCUSDT, ROSEUSDT, RSRUSDT, RVNUSDT, SAGAUSDT, SANDUSDT, SEIUSDT, SENTUSDT, SKLUSDT, SKYUSDT, SNXUSDT, SOLUSDT, SOONUSDT, SPXUSDT, STRKUSDT, STXUSDT, SUIUSDT, SUSDT, SXTUSDT, SYRUPUSDT, TAGUSDT, TAOUSDT, TIAUSDT, TRBUSDT, TRUMPUSDT, TRXUSDT, UAIUSDT, UNIUSDT, USELESSUSDT, USUSDT, VELVETUSDT, VETUSDT, VIRTUALUSDT, VTHOUSDT, VVVUSDT, WALUSDT, WIFUSDT, WLDUSDT, WLFIUSDT, WUSDT, XAUTUSDT, XLMUSDT, XMRUSDT, XPLUSDT, XRPUSDT, XTZUSDT, ZAMAUSDT, ZECUSDT, ZENUSDT, ZESTUSDT, ZKUSDT, ZROUSDT, 币安人生USDT, 牛来USDT, 龙虾USDT
- aggiornato: 2026-10-12 16:35 UTC

### Salute del registro

- composizione: **0 base** · **2323 generate** (di cui 1988 con almeno una conferma)
- occupazione: 2323/3000 — ok

### Strategie VALIDATE (operate dal bot)
| Coin | Strategia | Passes | PF | PnL OOS | Parametri |
|---|---|---|---|---|---|
| QUSDT | gen_f1e7ff62 | 3 | 2.383 | 192% | scale_r_mults=[1.0, 2.0, 3.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| STXUSDT | gen_0aa0d29c | 3 | 1.663 | 148% | scale_r_mults=[1.0, 1.5, 2.5], sl_to_breakeven=True, profit_lock_keep=0.65 |
| RUNEUSDT | gen_434083c5 | 3 | 1.701 | 146% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.5 |
| STXUSDT | gen_afa705ab | 3 | 1.579 | 135% | scale_r_mults=[0.75, 1.25, 1.75], sl_to_breakeven=True, profit_lock_keep=0.65 |
| UBUSDT | gen_d2a9f9ab | 3 | 3.086 | 125% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.5 |
| CAKEUSDT | gen_b4111d27 | 3 | 1.649 | 120% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| JTOUSDT | gen_94062d5f | 3 | 1.351 | 116% | scale_r_mults=[1.0, 2.0, 3.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| STXUSDT | gen_00e50229 | 3 | 1.339 | 111% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| AINUSDT | gen_5032e290 | 3 | 1.594 | 111% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| AINUSDT | gen_e6dd479a | 3 | 1.594 | 111% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| PARTIUSDT | gen_871647b8 | 4 | 2.221 | 107% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.5 |
| PTBUSDT | gen_684d7623 | 3 | 1.871 | 107% | scale_r_mults=[1.0, 1.5, 2.5], sl_to_breakeven=True, profit_lock_keep=0.65 |
| UBUSDT | gen_d926b0fd | 4 | 1.736 | 102% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.35 |
| XPINUSDT | gen_f311acf9 | 3 | 3.148 | 99% | scale_r_mults=[1.0, 1.5, 2.5], sl_to_breakeven=True, profit_lock_keep=0.65 |
| UBUSDT | gen_d163b751 | 3 | 1.51 | 96% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| UBUSDT | gen_92b77c39 | 3 | 1.49 | 91% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| SYRUPUSDT | gen_4c6df481 | 4 | 1.544 | 90% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.75 |
| UBUSDT | gen_f3e1ade7 | 3 | 3.029 | 90% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| XPINUSDT | gen_2e0818c8 | 4 | 4.073 | 88% | scale_r_mults=[0.75, 1.25, 1.75], sl_to_breakeven=True, profit_lock_keep=0.65 |
| CAKEUSDT | gen_cfe3beb3 | 3 | 1.595 | 87% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.5 |
| BRUSDT | gen_95fb50ce | 3 | 1.727 | 87% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| HUSDT | gen_fb3229db | 3 | 1.61 | 86% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| IDUSDT | gen_6bc43e03 | 4 | 1.55 | 85% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.5 |
| IDUSDT | gen_c5430258 | 4 | 1.55 | 85% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.5 |
| IDUSDT | gen_dd9238bf | 4 | 1.55 | 85% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.5 |
| UBUSDT | gen_fb3229db | 3 | 1.998 | 85% | scale_r_mults=[1.0, 2.0, 3.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| TAUSDT | gen_01fbe76f | 3 | 1.711 | 83% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| ORCAUSDT | gen_9a383fff | 5 | 1.978 | 82% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True |
| ORCAUSDT | gen_e6ddc613 | 5 | 1.94 | 81% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True |
| AINUSDT | gen_d926b0fd | 3 | 1.541 | 81% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| QUSDT | gen_3ee1484b | 4 | 2.842 | 80% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.75 |
| QUSDT | gen_e75ddbfd | 4 | 2.842 | 80% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.75 |
| TAUSDT | gen_543186c5 | 4 | 2.012 | 76% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| BULLAUSDT | gen_0eb59b31 | 3 | 2.707 | 76% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.35 |
| XPINUSDT | gen_c60cc1b9 | 4 | 3.25 | 74% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.35 |
| VELVETUSDT | gen_e933160c | 3 | 2.559 | 74% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.35 |
| VELVETUSDT | gen_ff3e4154 | 3 | 2.559 | 74% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.35 |
| SAHARAUSDT | gen_b0d474bb | 3 | 2.086 | 74% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.35 |
| SAHARAUSDT | gen_66848d49 | 3 | 2.228 | 73% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.35 |
| QUSDT | gen_da608d9f | 4 | 2.444 | 71% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.75 |
| SCRUSDT | gen_116faa2d | 3 | 1.876 | 71% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.35 |
| HEIUSDT | gen_96efce1b | 3 | 1.492 | 71% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| PARTIUSDT | gen_64263ae7 | 3 | 1.953 | 70% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.5 |
| QUSDT | gen_85fadf54 | 4 | 1.86 | 70% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.75 |
| CROSSUSDT | gen_4e6e1ae0 | 3 | 2.69 | 70% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| EIGENUSDT | gen_1b7827f3 | 3 | 1.475 | 69% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| MUBARAKUSDT | gen_e933160c | 4 | 1.889 | 69% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.35 |
| MUBARAKUSDT | gen_ff3e4154 | 5 | 1.889 | 69% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.35 |
| TAUSDT | gen_194e2514 | 3 | 1.946 | 68% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| TAUSDT | gen_1bb04e1a | 3 | 1.946 | 68% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| TAUSDT | gen_6e8a4220 | 3 | 2.152 | 68% | scale_r_mults=[1.0, 2.0, 3.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| JUPUSDT | gen_bb762669 | 5 | 1.701 | 68% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.35 |
| UBUSDT | gen_1e8c6a66 | 3 | 1.75 | 68% | scale_r_mults=[1.0, 1.5, 2.

[... 18169 caratteri omessi (testa e coda conservate) ...]

rofit_lock_keep=0.65 |
| HUMAUSDT | gen_60c9259a | 3 | 2.184 | 0% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| HUSDT | gen_22b2cade | 3 | 2.257 | 0% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| HUSDT | gen_5af56024 | 3 | 2.257 | 0% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| IDOLUSDT | gen_5ad54558 | 3 | 2.23 | 0% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.5 |
| IDOLUSDT | gen_931ca7de | 3 | 2.168 | 0% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| IDOLUSDT | gen_c429c4c6 | 3 | 2.852 | 0% | scale_r_mults=[1.0, 1.5, 2.5], sl_to_breakeven=True, profit_lock_keep=0.65 |
| KERNELUSDT | gen_c647ead7 | 3 | 2.131 | 0% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| MYXUSDT | gen_8931b93c | 3 | 1.583 | 0% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.5 |
| OPENUSDT | gen_46f0717f | 3 | 2.477 | 0% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| OPENUSDT | gen_bb762669 | 3 | 2.864 | 0% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.35 |
| PARTIUSDT | gen_7b4a474b | 3 | 2.213 | 0% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| PENGUUSDT | gen_5b9ed454 | 3 | 2.232 | 0% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| PHAUSDT | gen_bd109329 | 3 | 1.725 | 0% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.35 |
| PTBUSDT | gen_630b2a40 | 3 | 2.368 | 0% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| PTBUSDT | gen_73033c73 | 3 | 2.067 | 0% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.5 |
| PUMPUSDT | gen_13cc61f2 | 3 | 3.302 | 0% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| RENDERUSDT | gen_fe8925b6 | 3 | 2.027 | 0% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.35 |
| SAHARAUSDT | gen_4e1e404e | 3 | 1.445 | 0% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.5 |
| TAUSDT | gen_49c2f657 | 3 | 2.112 | 0% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| TAUSDT | gen_4e6e1ae0 | 3 | 2.15 | 0% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.75 |
| TAUSDT | gen_b0e86c70 | 3 | 2.477 | 0% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.5 |
| TAUSDT | gen_c08c5114 | 3 | 2.962 | 0% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.5 |
| TAUSDT | gen_c647ead7 | 3 | 2.023 | 0% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| TUTUSDT | gen_17b6b561 | 3 | 1.602 | 0% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| UBUSDT | gen_08664b28 | 3 | 1.839 | 0% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.35 |
| USELESSUSDT | gen_96c1ed1b | 3 | 2.06 | 0% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.5 |
| USELESSUSDT | gen_e09c5203 | 3 | 1.636 | 0% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.5 |
| XMRUSDT | gen_5642c3d7 | 3 | 1.624 | 0% | scale_r_mults=[0.75, 1.25, 1.75], sl_to_breakeven=True, profit_lock_keep=0.65 |

## Ultimo run di ottimizzazione
_aggiornato: 2026-09-21 12:43 UTC · 1320 coppie valutate, 0 passate in questo run_

_Nessuna coppia ha passato in questo run._

## Dove muoiono le candidate (autopsia del GATE 1)

**strategie base** — 1320 valutazioni, 0 passate (0.00%) · 2026-09-21 12:43 UTC

| Criterio che ferma | Casi | Quota |
|---|---|---|
| consistency | 17 | 1.3% |
| total_return | 1207 | 91.4% |
| trades | 6 | 0.5% |
| regime | 22 | 1.7% |
| recovery | 64 | 4.8% |
| holdout | 1 | 0.1% |
| pf_ex_top | 3 | 0.2% |

- quasi-passaggi (un solo criterio, di poco): **1** — sono i semi delle mutazioni del run successivo

**strategie generate** — 26986 valutazioni, 78 passate (0.29%) · 2026-10-12 16:13 UTC

| Criterio che ferma | Casi | Quota |
|---|---|---|
| consistency | 401 | 1.5% |
| total_return | 21824 | 81.1% |
| trades | 789 | 2.9% |
| regime | 2115 | 7.9% |
| recovery | 1542 | 5.7% |
| holdout | 122 | 0.5% |
| pf_ex_top | 115 | 0.4% |

- quasi-passaggi (un solo criterio, di poco): **40** — sono i semi delle mutazioni del run successivo

## Supervisore (taratura automatica)

- ultimo giro: 2026-10-12 18:01 UTC · coppie validate: **259** · GATE 1 pronto: True
- tasso di passaggio misurato: **0.276%**

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
- totale: **508** · vinti: 282 (56%) · PnL realizzato: **-126.21**
- confronto col mercato: noi -12.62% vs BTC buy&hold +8.92% nello stesso periodo → **sotto** il mercato

- costi: **67.59 USDT** su 508 trade (0.13/trade) _(stimati dal modello del gate, non misurati dai fill)_
  - commissioni 37.36 · spread 30.06 · funding +0.17
  - lordo -58.62 → netto -126.21 · **break-even 7.73%** dell'equity
  - piu' costose: DEXEUSDT 3.27 · SYRUPUSDT 3.11 · ZORAUSDT 2.56 · UBUSDT 2.50 · GPSUSDT 2.10
  - ⚠️ Costi operativi elevati: servono 7.73% solo per pareggiare (soglia 1.5%)

| Uscita | Trade | % | PnL |
|---|---|---|---|
| Trailing stop | 222 | 44% | +171.45 |
| Stop loss (prima di qualsiasi TP) | 221 | 44% | -438.77 |
| Scale-out (>=1 TP incassato, residuo a BE) | 48 | 9% | +87.25 |
| Time exit (orizzonte scaduto) | 13 | 3% | +25.12 |
| Take profit (fino all'ultimo gradino) | 4 | 1% | +28.73 |

- gradini raggiunti (su 508 trade): 0 TP: 449 (88%) · 1 TP: 45 (9%) · 2 TP: 10 (2%) · 3 TP: 4 (1%)

- **drawdown di portafoglio: 129.46 USDT** (ritorno -126.21 · recovery -0.97) · max 15 posizioni aperte insieme
  - il gate prometteva recovery ≥ 2.0 per ogni coppia (peggiore in registro: 0.00); il PORTAFOGLIO realizza -0.97
  _uscite in ordine di TEMPO: e' la buca vera, quella che il gate non vede perche' valida una coppia alla volta._

- escursione favorevole (mfe_r, 508 trade): mediana **0.81R** · ≥1R: 38% · ≥1.5R: 15% · ≥3R: 3% · ≥5R: 0%
  _quanto lontano arriva il prezzo, in unità di R: dice se la scala di TP è raggiungibile. Dettaglio: `python -m scripts.mfe_report`_

## Deriva paper vs gate
_il gate promette sulla storia, il paper misura il presente. `drift` = promessa contraddetta -> size/leva frenate subito e fallimento al gate alla prossima passata._

- **globale**: drift · 483 trade · PF vissuto 0.704 vs 2.027 atteso · mfe mediana 0.8R

- **freno globale attivo**: size x0.5 e leva x0.71 (radice) su OGNI trade finche' il PF a 30 giorni resta sotto 0.6 x atteso (motivo: PF 0.70 vs 2.03 atteso · mfe mediana 0.80R < primo TP 1.50R)

| Coppia | Verdetto | Trade | PF vissuto/atteso | Motivo |
|---|---|---|---|---|
| SYRUPUSDT|gen_4c6df481 | drift | 10 | 1.059 / 1.544 | mfe mediana 1.01R < primo TP 2.00R |
| QUSDT|gen_18c839a0 | drift | 8 | 0.421 / 2.883 | PF 0.42 vs 2.88 atteso · mfe mediana 0.90R < primo TP 1.50R |
| USELESSUSDT|gen_2031005e | watch | 7 | 0.304 / 1.54 | PF 0.30 vs 1.54 atteso · mfe mediana 0.80R < primo TP 2.00R |
| PTBUSDT|gen_684d7623 | watch | 5 | 1.598 / 1.871 | mfe mediana 0.53R < primo TP 1.00R |
| PNUTUSDT|gen_4810faab | watch | 5 | 2.677 / 2.491 | mfe mediana 1.13R < primo TP 2.00R |
| BULLAUSDT|gen_7ac562e3 | watch | 4 | 0.898 / 1.839 | PF 0.90 vs 1.84 atteso |
| BULLAUSDT|gen_5a52c06b | watch | 4 | 0.537 / 1.798 | PF 0.54 vs 1.80 atteso |
| AVAAIUSDT|gen_e50a9211 | watch | 4 | 0.345 / 1.525 | PF 0.35 vs 1.52 atteso |
| USELESSUSDT|gen_e09c5203 | watch | 4 | 0.666 / 1.636 | PF 0.67 vs 1.64 atteso · mfe mediana 1.05R < primo TP 2.00R |
| HUMAUSDT|gen_fca11c08 | watch | 4 | 0.0 / 1.657 | PF 0.00 vs 1.66 atteso · mfe mediana 0.10R < primo TP 2.00R |
| SYRUPUSDT|gen_af734c68 | watch | 3 | 0.407 / 1.493 | PF 0.41 vs 1.49 atteso · mfe mediana 0.94R < primo TP 1.50R |
| UBUSDT|gen_f3661202 | watch | 3 | 0.923 / 1.679 | PF 0.92 vs 1.68 atteso · mfe mediana 1.03R < primo TP 2.00R |
| ORCAUSDT|gen_6d06dca0 | watch | 3 | 0.0 / 1.967 | PF 0.00 vs 1.97 atteso · mfe mediana 0.49R < primo TP 1.50R |
| FORMUSDT|gen_c647ead7 | watch | 3 | 99.0 / 2.214 | mfe mediana 0.51R < primo TP 0.75R |
| GALAUSDT|gen_b9aa9989 | watch | 3 | 0.54 / 1.922 | PF 0.54 vs 1.92 atteso · mfe mediana 0.55R < primo TP 1.00R |
| CATIUSDT|gen_b3e46005 | watch | 3 | 1.519 / 2.605 | PF 1.52 vs 2.60 atteso |
| VETUSDT|gen_6d06dca0 | watch | 3 | 0.386 / 1.631 | PF 0.39 vs 1.63 atteso |
| JTOUSDT|gen_f238d283 | watch | 3 | 0.653 / 1.64 | PF 0.65 vs 1.64 atteso |
| SYRUPUSDT|gen_f3b97917 | watch | 2 | 99.0 / 2.064 | mfe mediana 1.16R < primo TP 2.00R |
| MUBARAKUSDT|gen_e933160c | watch | 2 | 0.243 / 1.889 | PF 0.24 vs 1.89 atteso |

- serie di perdite (freno SPENTO dal 24 set, solo misura): **gen_fa304106** (11 perdite di fila)

## Calibrazione della confidenza
_la confidenza del segnale modula size e leva: qui si verifica che predica davvero l'esito, invece di darlo per scontato._

- verdetto: **costante** · 483 trade · correlazione None · influenza applicata **x1.0**
- tutte le strategie generate escono a confidenza 60: la calibrazione non puo' misurare nulla finche' la confidenza non varia (483 trade, confidenza 60-60)

| Fascia di confidenza | Trade | Win rate | Esito medio |
|---|---|---|---|
| 60.0–60.0 | 161 | 55% | -0.36% |
| 60.0–60.0 | 161 | 56% | -0.16% |
| 60.0–60.0 | 161 | 54% | -0.53% |

_se l'esito medio CRESCE dalla fascia bassa all'alta, la confidenza ordina correttamente i trade._
```
