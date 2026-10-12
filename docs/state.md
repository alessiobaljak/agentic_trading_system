# Stato sistema (snapshot)
_Generato: 2026-10-12 05:58 UTC_

## Bot
- stato: **running** (🟢 online)
- regime: sideways
- DRY_RUN: True
- equity: **$882.57**
- ultimo heartbeat: 2026-10-12 05:58 UTC
- stream prezzi: 🟢 attivo

## Ultima decisione
- esito: **⚪ FLAT** (2026-10-12 05:47 UTC)
- motivo: parita' backtest: 2 segnali validi aperti
- asset valutati: 75 · segnali: 2 · miglior segnale AINUSDT gen_d926b0fd (conf. 60.0/soglia 30)

## Posizioni aperte
- AINUSDT: long qty=2002.1973774362516 @ 0.04408 uPnL=-0.1616153998745044 · rischio 0.31% · leva 1.0x
- ASTERUSDT: short qty=121.9017408803729 @ 0.724 uPnL=0.37089345727354345 · rischio 0.07% · leva 1.0x
- HEMIUSDT: short qty=14766.106191322535 @ 0.005973 uPnL=0.468066780286866 · rischio 0.14% · leva 1.0x
- PNUTUSDT: short qty=1691.075646580387 @ 0.05207 uPnL=0.2161300796099462 · rischio 0.14% · leva 1.0x
- QUSDT: short qty=1977.288095283001 @ 0.0305 uPnL=-2.2026325069405344 · rischio 0.36% · leva 1.0x
- **rischio aperto totale: 1.03%** dell'equity su 5 posizioni

## GATE 1 — Validazione strategie
- stato: **✅ SUPERATO — pronti per il paper trading**
- copertura universo: **76/200 crypto (38%)** · obiettivo ≥ 35%
- coppie validate (>= 3 pass OOS): **229**
- universo scansionato: 0GUSDT, 1000BONKUSDT, 1000PEPEUSDT, 1000SHIBUSDT, AAVEUSDT, ACEUSDT, ACHUSDT, ACTUSDT, ADAUSDT, AEROUSDT, AINUSDT, AIOTUSDT, AKEUSDT, AKTUSDT, ALGOUSDT, ALTUSDT, APEUSDT, API3USDT, APRUSDT, APTUSDT, ARBUSDT, ARPAUSDT, ARUSDT, ARXUSDT, ASTERUSDT, ATOMUSDT, AUSDT, AVAXUSDT, AVNTUSDT, AXLUSDT, AXSUSDT, AZTECUSDT, BANKUSDT, BATUSDT, BBUSDT, BCHUSDT, BEAMXUSDT, BILLUSDT, BIOUSDT, BNBUSDT, BOMEUSDT, BRUSDT, BTCUSDT, BTWUSDT, BULLAUSDT, C98USDT, CAKEUSDT, CAPUSDT, CCUSDT, CFGUSDT, CFXUSDT, CHIPUSDT, CKBUSDT, COMPUSDT, COTIUSDT, CRVUSDT, CTSIUSDT, CTUSDT, CYBERUSDT, DASHUSDT, DATAIPUSDT, DOGEUSDT, DOSUSDT, DOTUSDT, DUSKUSDT, DYMUSDT, EGLDUSDT, EIGENUSDT, ENAUSDT, ENSUSDT, ERAUSDT, ETCUSDT, ETHFIUSDT, ETHUSDT, FARTCOINUSDT, FETUSDT, FFUSDT, FILUSDT, FLOWUSDT, GALAUSDT, GRAMUSDT, GRASSUSDT, GTCUSDT, HANAUSDT, HBARUSDT, HEMIUSDT, HUMAUSDT, HYPEUSDT, ICPUSDT, INJUSDT, IOUSDT, JCTUSDT, JTOUSDT, JUPUSDT, KAIAUSDT, LABUSDT, LAUSDT, LDOUSDT, LINEAUSDT, LINKUSDT, LITUSDT, LPTUSDT, LSKUSDT, LTCUSDT, LUMIAUSDT, MAGICUSDT, MANAUSDT, MANTAUSDT, MARSCOINUSDT, MEGAUSDT, METISUSDT, METUSDT, MINAUSDT, MONUSDT, MORPHOUSDT, MOVRUSDT, MUBARAKUSDT, NEARUSDT, NEIROUSDT, NEOUSDT, NIGHTUSDT, NILUSDT, NMRUSDT, OGNUSDT, ONDOUSDT, ONEUSDT, ONUSDT, OPUSDT, ORCAUSDT, ORDIUSDT, PAXGUSDT, PENDLEUSDT, PENGUUSDT, PHAUSDT, PIXELUSDT, PLUMEUSDT, POLUSDT, PONSUSDT, PROMUSDT, PUMPUSDT, PYTHUSDT, QNTUSDT, QUSDT, RAYSOLUSDT, RENDERUSDT, RIVERUSDT, RLCUSDT, RONINUSDT, ROSEUSDT, RSRUSDT, RVNUSDT, SAGAUSDT, SANDUSDT, SEIUSDT, SENTUSDT, SKLUSDT, SKYUSDT, SOLUSDT, SOONUSDT, SPXUSDT, STRKUSDT, STXUSDT, SUIUSDT, SUSDT, SYRUPUSDT, TAOUSDT, TIAUSDT, TRBUSDT, TRUMPUSDT, TRXUSDT, UNIUSDT, USELESSUSDT, USUSDT, VANAUSDT, VELODROMEUSDT, VELVETUSDT, VETUSDT, VIRTUALUSDT, VTHOUSDT, VVVUSDT, WALUSDT, WIFUSDT, WLDUSDT, WLFIUSDT, WUSDT, XAUTUSDT, XLMUSDT, XMRUSDT, XPLUSDT, XRPUSDT, XTZUSDT, ZAMAUSDT, ZECUSDT, ZENUSDT, ZESTUSDT, ZKUSDT, ZROUSDT, 币安人生USDT, 牛来USDT, 龙虾USDT
- aggiornato: 2026-10-12 05:49 UTC

### Salute del registro

- composizione: **1 base** · **2264 generate** (di cui 1929 con almeno una conferma)
- occupazione: 2265/3000 — ok

### Strategie VALIDATE (operate dal bot)
| Coin | Strategia | Passes | PF | PnL OOS | Parametri |
|---|---|---|---|---|---|
| QUSDT | gen_f1e7ff62 | 3 | 2.383 | 192% | scale_r_mults=[1.0, 2.0, 3.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| STXUSDT | gen_0aa0d29c | 3 | 1.663 | 148% | scale_r_mults=[1.0, 1.5, 2.5], sl_to_breakeven=True, profit_lock_keep=0.65 |
| RUNEUSDT | gen_434083c5 | 3 | 1.701 | 146% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.5 |
| STXUSDT | gen_afa705ab | 3 | 1.579 | 135% | scale_r_mults=[0.75, 1.25, 1.75], sl_to_breakeven=True, profit_lock_keep=0.65 |
| UBUSDT | gen_d2a9f9ab | 3 | 3.086 | 125% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.5 |
| CAKEUSDT | gen_b4111d27 | 3 | 1.649 | 120% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
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
| UBUSDT | gen_1e8c6a66 | 3 | 1.75 | 68% | scale_r_mults=[1.0, 1.5, 2.5], sl_to_breakeven=True, profit_lock_keep=0.35 |
| UBUSDT | gen_902fb1fd | 3 | 1.75 | 68% | scale_r_mults=[1.0, 1.5, 2.5], sl_to_breakeven=True, profit_lock_keep=0.35 |
| GPSUSDT | gen_871647b8 | 5 | 1.505 | 67% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.5 |
| ZECUSDT | gen_e6ddc613 | 3 | 1.46 | 67% | scale_r_mults=[1.0, 2.0, 3.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| TAUSDT | gen_b5d63a02 | 3 | 2.062 | 67% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| TAUSDT | gen_fa5179ea | 3 | 1.901 | 67% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| TAUSDT | gen_68a8a9c7 | 3 | 2.098 | 66% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| BULLAUSDT | gen_cec62f22 | 3 | 4.492 | 66% | scale_r_mults=[1.0, 1.5, 2.5], sl_to_breakeven=True, profit_lock_keep=0.5 |
| AINUSDT | gen_d8656ab7 | 3 | 1.683 | 66% | scale_r_mults=[1.0, 2.0, 3.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| SKYAIUSDT | gen_624135f0 | 3 | 2.835 | 65% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.5 |
| HUSDT | gen_2255a1d8 | 3 | 1.619 | 63% | scale_r_mults=[0.75, 1.25, 1.75], sl_to_breakeven=True, profit_lock_keep=0.65 |
| SKYAIUSDT | gen_f68b811d | 5 | 2.777 | 63% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.35 |
| HUSDT | gen_ccb40454 | 3 | 1.478 | 62% | scale_r_mults=[1.0, 2.0, 3.0], sl_to_breakeven=True, profit_lock_keep=0.5 |
| UBUSDT | gen_4e6e1ae0 | 3 | 2.958 | 62% | scale_r_mults=[1.0, 2.0, 3.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| XPINUSDT | gen_871647b8 | 3 | 2.654 | 61% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.35 |
| SKYAIUSDT | gen_6191df86 | 5 | 2.98 | 60% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| ARKMUSDT | gen_913d0c3a | 3 | 1.851 | 60% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.35 |
| MYXUSDT | gen_a5b0e4de | 4 | 3.066 | 60% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.35 |
| BULLAUSDT | gen_d2d4ba16 | 3 | 5.779 | 60% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.35 |
| AVAAIUSDT | gen_c8529192 | 3 | 2.426 | 60% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.35 |
| SCRUSDT | gen_bd8f158b | 4 | 1.928 | 60% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| XPINUSDT | gen_9a383fff | 3 | 3.13 | 60% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| QUSDT | gen_0aa0d29c | 3 | 2.312 | 59% | scale_r_mults=[0.75, 1.25, 1.75], sl_to_breakeven=True, profit_lock_keep=0.65 |
| UBUSDT | gen_15837112 | 4 | 1.678 | 59% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.35 |
| BMTUSDT | gen_be64073c | 3 | 2.843 | 58% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| SCRUSDT | gen_0e030446 | 3 | 1.851 | 57% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| XPINUSDT | gen_902fb1fd | 3 | 2.485 | 57% | scale_r_mults=[0.75, 1.25, 1.75], sl_to_breakeven=True, profit_lock_keep=0.65 |
| KERNELUSDT | gen_96ed157e | 3 | 3.078 | 57% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.35 |
| HUMAUSDT | gen_ea57f794 | 3 | 2.088 | 56% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| GRASSUSDT | gen_f4ac85e0 | 3 | 1.53 | 56% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.5 |
| DEXEUSDT | gen_3d4be8c7 | 3 | 1.545 | 55% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| XPINUSDT | gen_6bc43e03 | 3 | 2.251 | 55% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| XPINUSDT | gen_c5430258 | 3 | 2.251 | 55% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| XPINUSDT | gen_dd9238bf | 3 | 2.251 | 55% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| AINUSDT | gen_e70074cc | 3 | 2.541 | 54% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| HUMAUSDT | gen_da39a23a | 5 | 2.258 | 54% | scale_r_mults=[1.0, 1.5, 2.5], sl_to_breakeven=True, profit_lock_keep=0.75 |
| BULLAUSDT | gen_26e8abbf | 3 | 3.81 | 54% | scale_r_mults=[1.0, 2.0, 3.0], sl_to_breakeven=True, profit_lock_keep=0.5 |
| SKYAIUSDT | gen_eb2ece0c | 6 | 3.343 | 53% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.35 |
| SKYAIUSDT | gen_b1f90b17 | 3 | 2.774 | 53% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.5 |
| PUMPUSDT | gen_1000366e | 4 | 1.736 | 52% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.35 |
| MUBARAKUSDT | gen_f86f7370 | 4 | 2.937 | 52% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.35 |
| QUSDT | gen_a3088356 | 3 | 4.107 | 52% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| MITOUSDT | gen_8feb4e23 | 3 | 2.58 | 51% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.5 |
| QUSDT | gen_18c839a0 | 5 | 2.883 | 51% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.75 |
| QUSDT | gen_b1ac5c24 | 4 | 2.883 | 51% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.75 |
| UBUSDT | gen_0ec2c344 | 4 | 1.731 | 51% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.5 |
| UBUSDT | gen_4348f9d4 | 4 | 1.731 | 51% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.5 |
| UBUSDT | gen_ab1d9bb7 | 3 | 1.731 | 51% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.5 |
| UBUSDT | gen_88e12707 | 3 | 1.778 | 51% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| 1000BONKUSDT | gen_86a8b183 | 3 | 1.858 | 50% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.35 |
| SKYAIUSDT | gen_955f400d | 3 | 2.267 | 50% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.5 |
| HEMIUSDT | gen_acea368d | 3 | 1.784 | 50% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.5 |
| HYPEUSDT | gen_f19b67e8 | 3 | 1.624 | 49% | scale_r_mults=[1.0, 1.5, 2.5], sl_to_breakeven=True, profit_lock_keep=0.65 |
| PTBUSDT | gen_dd5bfb74 | 3 | 1.715 | 49% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| MUBARAKUSDT | gen_6d369d09 | 3 | 1.61 | 49% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.5 |
| AINUSDT | gen_057ea246 | 3 | 2.165 | 48% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| QUSDT | gen_331ef268 | 3 | 1.679 | 48% | scale_r_mults=[0.75, 1.25, 1.75], sl_to_breakeven=True, profit_lock_keep=0.65 |
| AVAAIUSDT | gen_08c22b92 | 3 | 1.958 | 48% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| STXUSDT | gen_a5b0e4de | 4 | 1.449 | 48% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.5 |
| PUMPUSDT | gen_ab1d9bb7 | 3 | 1.618 | 48% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.35 |
| AINUSDT | gen_e3f3663c | 3 | 1.943 | 48% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| SKYAIUSDT | gen_0c99400e | 3 | 2.486 | 47% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.35 |
| ZECUSDT | gen_7b4a474b | 3 | 1.413 | 47% | scale_r_mults=[1.0, 1.5, 2.5], sl_to_breakeven=True, profit_lock_keep=0.65 |
| PLUMEUSDT | gen_353f3f19 | 3 | 2.589 | 47% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.35 |
| PLUMEUSDT | gen_e94b056d | 5 | 2.589 | 47% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.35 |
| PUMPUSDT | gen_08664b28 | 4 | 1.519 | 47% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.35 |
| CATIUSDT | gen_b3e46005 | 4 | 2.605 | 47% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.5 |
| GALAUSDT | gen_b9aa9989 | 4 | 1.922 | 46% | scale_r_mults=[1.0, 1.25, 2.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| SAHARAUSDT | gen_cb8176f2 | 3 | 1.932 | 46% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.5 |
| SAHARAUSDT | gen_6b94025f | 6 | 2.111 | 46% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.35 |
| UBUSDT | gen_f6c63753 | 3 | 1.573 | 45% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| AINUSDT | gen_3b9c62e9 | 3 | 1.975 | 45% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| AINUSDT | gen_5b847426 | 3 | 1.975 | 45% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| SCRUSDT | gen_d2dc954d | 3 | 1.89 | 44% | scale_r_mults=[1.0, 1.5, 2.5], sl_to_breakeven=True, profit_lock_keep=0.65 |
| BANKUSDT | gen_2010adf6 | 3 | 1.882 | 44% | scale_r_mults=[1.0, 2.0, 3.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| AKTUSDT | gen_e2504b72 | 3 | 2.311 | 43% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| HOMEUSDT | gen_467d9ee2 | 3 | 1.616 | 43% | scale_r_mults=[1.0, 2.0, 3.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| 1000PEPEUSDT | gen_f9d90376 | 3 | 1.54 | 43% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| UBUSDT | gen_434f29e6 | 3 | 2.062 | 43% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.5 |
| BSVUSDT | gen_c429c4c6 | 3 | 1.67 | 42% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| AKTUSDT | gen_f4c1300a | 3 | 2.355 | 42% | scale_r_mults=[1.0, 2.0, 3.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| UBUSDT | gen_8981d5f2 | 4 | 2.418 | 42% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| BULLAUSDT | gen_5a52c06b | 3 | 1.798 | 42% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| HUMAUSDT | gen_b6536ebe | 3 | 1.966 | 42% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| BANKUSDT | gen_5b7f8f78 | 3 | 2.181 | 42% | scale_r_mults=[1.0, 2.0, 3.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| FORMUSDT | gen_c647ead7 | 4 | 2.214 | 42% | scale_r_mults=[0.75, 1.25, 1.75], sl_to_breakeven=True, profit_lock_keep=0.65 |
| BULLAUSDT | gen_867c4e9c | 3 | 2.346 | 41% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.35 |
| PNUTUSDT | gen_4810faab | 4 | 2.491 | 41% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.5 |
| OPENUSDT | gen_2bb283ca | 4 | 2.605 | 40% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.35 |
| OPENUSDT | gen_bbeaf73b | 3 | 2.605 | 40% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.35 |
| ASTERUSDT | gen_049a08f7 | 3 | 2.105 | 40% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.5 |
| AVAAIUSDT | gen_1eec02f5 | 3 | 1.931 | 40% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.35 |
| ZORAUSDT | gen_d85b1f05 | 3 | 1.876 | 39% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.35 |
| OPENUSDT | gen_d2840ddb | 3 | 3.746 | 39% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| TAOUSDT | gen_82d2c2da | 3 | 1.601 | 39% | scale_r_mults=[1.0, 2.0, 3.0], sl_to_breakeven=True, profit_lock_keep=0.5 |
| XPINUSDT | gen_45e3b02a | 3 | 3.751 | 38% | scale_r_mults=[0.75, 1.25, 1.75], sl_to_breakeven=True, profit_lock_keep=0.65 |
| OPENUSDT | gen_b9bf5d01 | 3 | 2.556 | 38% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| ASTERUSDT | gen_042c5262 | 3 | 2.389 | 38% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.5 |
| ASTERUSDT | gen_96efce1b | 3 | 1.918 | 37% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.5 |
| OPENUSDT | gen_4f25eca9 | 3 | 2.45 | 37% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| OPENUSDT | gen_c7a02fce | 3 | 2.45 | 37% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| GUNUSDT | gen_4f890271 | 3 | 2.02 | 37% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| OPENUSDT | gen_d606fde3 | 3 | 3.352 | 37% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| SAHARAUSDT | gen_60d64cfd | 4 | 2.67 | 37% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.35 |
| DEXEUSDT | gen_73d91a3c | 3 | 1.495 | 36% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| AVAAIUSDT | gen_9758394b | 3 | 1.755 | 36% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.35 |
| BULLAUSDT | gen_99c9c036 | 4 | 2.34 | 36% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| MAVIAUSDT | gen_608b892e | 3 | 1.969 | 35% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| PARTIUSDT | gen_b50fc231 | 3 | 1.549 | 35% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| PUMPUSDT | gen_d06acf60 | 3 | 3.593 | 34% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| SAHARAUSDT | gen_711892bf | 3 | 1.632 | 34% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.5 |
| SAHARAUSDT | gen_1eec02f5 | 4 | 2.19 | 33% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.75 |
| RENDERUSDT | gen_b028553e | 3 | 1.617 | 33% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| BIOUSDT | gen_867c4e9c | 3 | 2.081 | 33% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.5 |
| RENDERUSDT | gen_fdaa6e0b | 4 | 1.846 | 32% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.35 |
| SYRUPUSDT | gen_f3b97917 | 5 | 2.064 | 32% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| AINUSDT | gen_9839aec0 | 3 | 1.407 | 31% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.5 |
| OPENUSDT | gen_14e1775b | 3 | 2.782 | 31% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| BLESSUSDT | gen_bbda6aa7 | 3 | 2.147 | 30% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| MUBARAKUSDT | gen_49c2f657 | 5 | 1.721 | 29% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.75 |
| PUNDIXUSDT | gen_71180be0 | 3 | 2.449 | 29% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.35 |
| SAHARAUSDT | gen_c934a6f7 | 3 | 1.687 | 28% | scale_r_mults=[0.75, 1.25, 1.75], sl_to_breakeven=True, profit_lock_keep=0.5 |
| FLOCKUSDT | gen_2350695a | 4 | 1.673 | 27% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.5 |
| UBUSDT | gen_f3661202 | 4 | 1.679 | 27% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| HEIUSDT | gen_c1b30752 | 3 | 2.759 | 26% | scale_r_mults=[1.0, 1.5, 2.5], sl_to_breakeven=True, profit_lock_keep=0.65 |
| HEIUSDT | gen_c7b5f40d | 3 | 2.759 | 26% | scale_r_mults=[1.0, 1.5, 2.5], sl_to_breakeven=True, profit_lock_keep=0.65 |
| HUMAUSDT | gen_630b2a40 | 4 | 1.83 | 25% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.35 |
| MUBARAKUSDT | gen_1e2af031 | 5 | 2.143 | 25% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.35 |
| ZORAUSDT | gen_722052d4 | 3 | 2.249 | 25% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| SAHARAUSDT | gen_95aff747 | 4 | 1.62 | 24% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.5 |
| 0GUSDT | gen_aa6bb820 | 3 | 1.705 | 24% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.5 |
| SKYAIUSDT | gen_bd109329 | 3 | 1.553 | 24% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.5 |
| MUBARAKUSDT | gen_2053cba6 | 6 | 1.484 | 23% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.75 |
| AINUSDT | gen_ef115241 | 3 | 1.74 | 21% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.35 |
| RAYSOLUSDT | gen_a01bcc1a | 3 | 1.585 | 20% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| TAKEUSDT | gen_cd0132fa | 3 | 1.502 | 20% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.5 |
| ZORAUSDT | gen_f4e37ccc | 3 | 2.593 | 19% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| AIOUSDT | gen_fc644cd2 | 3 | 3.27 | 18% | scale_r_mults=[1.0, 1.5, 2.5], sl_to_breakeven=True, profit_lock_keep=0.5 |
| BULLAUSDT | gen_7ac562e3 | 4 | 1.839 | 17% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True |
| AVAAIUSDT | gen_e50a9211 | 4 | 1.525 | 17% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.5 |
| ASTERUSDT | gen_37836d3c | 3 | 1.666 | 0% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.5 |
| ASTERUSDT | gen_d74845a5 | 3 | 1.774 | 0% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.5 |
| AVAAIUSDT | gen_dbe19eb2 | 3 | 1.525 | 0% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.5 |
| BANKUSDT | gen_7100bb59 | 3 | 1.938 | 0% | scale_r_mults=[0.75, 1.25, 1.75], sl_to_breakeven=True, profit_lock_keep=0.65 |
| BTRUSDT | gen_5a52c06b | 3 | 1.784 | 0% | scale_r_mults=[0.75, 1.25, 1.75], sl_to_breakeven=True, profit_lock_keep=0.65 |
| ENAUSDT | gen_e85db5f1 | 3 | 1.797 | 0% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| HEMIUSDT | gen_c1f71d65 | 3 | 1.54 | 0% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| HIVEUSDT | gen_d91cecd8 | 3 | 2.519 | 0% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.35 |
| HOLOUSDT | gen_f22e08b7 | 3 | 1.842 | 0% | scale_r_mults=[1.0, 2.0, 3.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| HUMAUSDT | gen_60c9259a | 3 | 2.184 | 0% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| HUSDT | gen_22b2cade | 3 | 2.257 | 0% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| HUSDT | gen_5af56024 | 3 | 2.257 | 0% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| IDOLUSDT | gen_5ad54558 | 3 | 2.23 | 0% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.5 |
| IDOLUSDT | gen_931ca7de | 3 | 2.168 | 0% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| IDOLUSDT | gen_c429c4c6 | 3 | 2.852 | 0% | scale_r_mults=[1.0, 1.5, 2.5], sl_to_breakeven=True, profit_lock_keep=0.65 |
| JTOUSDT | gen_94062d5f | 3 | 1.366 | 0% | scale_r_mults=[1.0, 2.0, 3.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
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

**strategie generate** — 46323 valutazioni, 566 passate (1.22%) · 2026-10-12 05:49 UTC

| Criterio che ferma | Casi | Quota |
|---|---|---|
| oos_windows | 108 | 0.2% |
| total_return | 35193 | 76.9% |
| regime | 3640 | 8.0% |
| trades | 1528 | 3.3% |
| recovery | 3690 | 8.1% |
| holdout | 463 | 1.0% |
| consistency | 781 | 1.7% |
| pf | 1 | 0.0% |

- quasi-passaggi (un solo criterio, di poco): **40** — sono i semi delle mutazioni del run successivo

## Supervisore (taratura automatica)

- ultimo giro: 2026-10-12 05:02 UTC · coppie validate: **266** · GATE 1 pronto: True
- tasso di passaggio misurato: **0.305%**

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
- totale: **492** · vinti: 274 (56%) · PnL realizzato: **-117.43**

- costi: **65.78 USDT** su 492 trade (0.13/trade) _(stimati dal modello del gate, non misurati dai fill)_
  - commissioni 36.37 · spread 29.24 · funding +0.17
  - lordo -51.66 → netto -117.43 · **break-even 7.45%** dell'equity
  - piu' costose: DEXEUSDT 3.13 · SYRUPUSDT 3.11 · ZORAUSDT 2.56 · UBUSDT 2.22 · GPSUSDT 2.10
  - ⚠️ Costi operativi elevati: servono 7.45% solo per pareggiare (soglia 1.5%)

| Uscita | Trade | % | PnL |
|---|---|---|---|
| Trailing stop | 216 | 44% | +169.27 |
| Stop loss (prima di qualsiasi TP) | 213 | 43% | -425.42 |
| Scale-out (>=1 TP incassato, residuo a BE) | 46 | 9% | +84.86 |
| Time exit (orizzonte scaduto) | 13 | 3% | +25.12 |
| Take profit (fino all'ultimo gradino) | 4 | 1% | +28.73 |

- gradini raggiunti (su 492 trade): 0 TP: 435 (88%) · 1 TP: 44 (9%) · 2 TP: 9 (2%) · 3 TP: 4 (1%)

- **drawdown di portafoglio: 129.46 USDT** (ritorno -117.43 · recovery -0.91) · max 15 posizioni aperte insieme
  - il gate prometteva recovery ≥ 2.0 per ogni coppia (peggiore in registro: 0.00); il PORTAFOGLIO realizza -0.91
  _uscite in ordine di TEMPO: e' la buca vera, quella che il gate non vede perche' valida una coppia alla volta._

- escursione favorevole (mfe_r, 492 trade): mediana **0.81R** · ≥1R: 39% · ≥1.5R: 15% · ≥3R: 3% · ≥5R: 0%
  _quanto lontano arriva il prezzo, in unità di R: dice se la scala di TP è raggiungibile. Dettaglio: `python -m scripts.mfe_report`_

## Deriva paper vs gate
_il gate promette sulla storia, il paper misura il presente. `drift` = promessa contraddetta -> size/leva frenate subito e fallimento al gate alla prossima passata._

- **globale**: drift · 467 trade · PF vissuto 0.715 vs 2.031 atteso · mfe mediana 0.81R

- **freno globale attivo**: size x0.5 e leva x0.71 (radice) su OGNI trade finche' il PF a 30 giorni resta sotto 0.6 x atteso (motivo: PF 0.72 vs 2.03 atteso · mfe mediana 0.81R < primo TP 1.50R)

| Coppia | Verdetto | Trade | PF vissuto/atteso | Motivo |
|---|---|---|---|---|
| SYRUPUSDT|gen_4c6df481 | drift | 10 | 1.059 / 1.544 | mfe mediana 1.01R < primo TP 2.00R |
| QUSDT|gen_18c839a0 | drift | 8 | 0.421 / 2.883 | PF 0.42 vs 2.88 atteso · mfe mediana 0.90R < primo TP 1.50R |
| USELESSUSDT|gen_2031005e | watch | 7 | 0.304 / 1.54 | PF 0.30 vs 1.54 atteso · mfe mediana 0.80R < primo TP 2.00R |
| AVAAIUSDT|gen_e50a9211 | watch | 4 | 0.345 / 1.525 | PF 0.35 vs 1.52 atteso |
| BULLAUSDT|gen_7ac562e3 | watch | 4 | 0.898 / 1.839 | PF 0.90 vs 1.84 atteso |
| HUMAUSDT|gen_fca11c08 | watch | 4 | 0.0 / 1.657 | PF 0.00 vs 1.66 atteso · mfe mediana 0.10R < primo TP 2.00R |
| BULLAUSDT|gen_5a52c06b | watch | 4 | 0.537 / 1.798 | PF 0.54 vs 1.80 atteso |
| PTBUSDT|gen_684d7623 | watch | 4 | 1.377 / 1.871 | mfe mediana 0.53R < primo TP 1.00R |
| UBUSDT|gen_f3661202 | watch | 3 | 0.923 / 1.679 | PF 0.92 vs 1.68 atteso · mfe mediana 1.03R < primo TP 2.00R |
| ORCAUSDT|gen_6d06dca0 | watch | 3 | 0.0 / 1.967 | PF 0.00 vs 1.97 atteso · mfe mediana 0.49R < primo TP 1.50R |
| VETUSDT|gen_6d06dca0 | watch | 3 | 0.386 / 1.631 | PF 0.39 vs 1.63 atteso |
| GALAUSDT|gen_b9aa9989 | watch | 3 | 0.54 / 1.922 | PF 0.54 vs 1.92 atteso · mfe mediana 0.55R < primo TP 1.00R |
| FORMUSDT|gen_c647ead7 | watch | 3 | 99.0 / 2.214 | mfe mediana 0.51R < primo TP 0.75R |
| JTOUSDT|gen_f238d283 | watch | 3 | 0.653 / 1.64 | PF 0.65 vs 1.64 atteso |
| CATIUSDT|gen_b3e46005 | watch | 3 | 1.519 / 2.605 | PF 1.52 vs 2.60 atteso |
| SYRUPUSDT|gen_af734c68 | watch | 3 | 0.407 / 1.493 | PF 0.41 vs 1.49 atteso · mfe mediana 0.94R < primo TP 1.50R |
| PUMPUSDT|gen_13cc61f2 | watch | 2 | 0.375 / 3.302 | PF 0.38 vs 3.30 atteso |
| OPENUSDT|gen_46f0717f | watch | 2 | 0.447 / 2.477 | PF 0.45 vs 2.48 atteso · mfe mediana 1.10R < primo TP 2.00R |
| SYRUPUSDT|gen_f3b97917 | watch | 2 | 99.0 / 2.064 | mfe mediana 1.16R < primo TP 2.00R |
| QUSDT|gen_85fadf54 | watch | 2 | 0.0 / 1.86 | PF 0.00 vs 1.86 atteso · mfe mediana 0.38R < primo TP 1.50R |

- serie di perdite (freno SPENTO dal 24 set, solo misura): **gen_fa304106** (11 perdite di fila)

## Calibrazione della confidenza
_la confidenza del segnale modula size e leva: qui si verifica che predica davvero l'esito, invece di darlo per scontato._

- verdetto: **costante** · 467 trade · correlazione None · influenza applicata **x1.0**
- tutte le strategie generate escono a confidenza 60: la calibrazione non puo' misurare nulla finche' la confidenza non varia (467 trade, confidenza 60-60)

| Fascia di confidenza | Trade | Win rate | Esito medio |
|---|---|---|---|
| 60.0–60.0 | 155 | 54% | -0.25% |
| 60.0–60.0 | 155 | 57% | -0.18% |
| 60.0–60.0 | 157 | 54% | -0.53% |

_se l'esito medio CRESCE dalla fascia bassa all'alta, la confidenza ordina correttamente i trade._
