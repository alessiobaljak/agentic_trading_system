# 0524-7ott-mattina-stato.req

_eseguito: 2026-10-07 06:05 UTC_

**richiesta:** `stato`
**eseguito:** `.venv/bin/python -m scripts.state_snapshot --no-write`
**esito:** codice 0 in 4.1s

```
[firebase] connesso (Firestore + RTDB)
# Stato sistema (snapshot)
_Generato: 2026-10-07 06:05 UTC_

## Bot
- stato: **running** (🟢 online)
- regime: bear_trending
- DRY_RUN: True
- equity: **$912.77**
- ultimo heartbeat: 2026-10-07 06:04 UTC
- stream prezzi: 🟢 attivo

## Ultima decisione
- esito: **⚪ FLAT** (2026-10-07 06:03 UTC)
- motivo: parita' backtest: 2 segnali validi aperti
- asset valutati: 82 · segnali: 2 · miglior segnale SYRUPUSDT gen_f3b97917 (conf. 60.0/soglia 30)

## Posizioni aperte
- ASTERUSDT: long qty=129.2215281858454 @ 0.7102 uPnL=0.017970759440055842 · rischio 0.19% · leva 1.0x
- BULLAUSDT: long qty=1104.9941937598555 @ 0.08275 uPnL=-0.6639818957935448 · rischio 0.13% · leva 1.0x
- DOTUSDT: long qty=24.093507639014316 @ 1.1206 uPnL=0.08019127071437099 · rischio 0.06% · leva 1.0x
- GPSUSDT: long qty=5157.114681237295 @ 0.010428 uPnL=-0.4166507373438815 · rischio 0.09% · leva 1.0x
- HEIUSDT: long qty=472.9230383346043 @ 0.13144 uPnL=-0.19003567801986485 · rischio 0.13% · leva 1.0x
- HEMIUSDT: short qty=6317.54332134194 @ 0.00561 uPnL=0.1803543892595565 · rischio 0.13% · leva 1.0x
- JASMYUSDT: long qty=5951.937691972191 @ 0.0049 uPnL=0.43006996049121243 · rischio 0.09% · leva 1.0x
- PUNDIXUSDT: long qty=489.6700179373608 @ 0.11453 uPnL=-0.14616431273124464 · rischio 0.08% · leva 2.0x
- RSRUSDT: short qty=4829.617484106275 @ 0.001815 uPnL=0.8159679557844194 · rischio 0.05% · leva 1.0x
- SCRUSDT: long qty=3669.457389747597 @ 0.02501 uPnL=0.2662260400107709 · rischio 0.32% · leva 1.0x
- SYRUPUSDT: long qty=693.0902526160455 @ 0.23877 uPnL=-0.5215161069315419 · rischio 0.32% · leva 2.0x
- VETUSDT: long qty=5422.230086686115 @ 0.008272 uPnL=-0.266111747079953 · rischio 0.09% · leva 1.0x
- XPINUSDT: long qty=213674.34066958653 @ 0.000859 uPnL=-0.5116893436935039 · rischio 0.37% · leva 2.0x
- **rischio aperto totale: 2.05%** dell'equity su 13 posizioni

## GATE 1 — Validazione strategie
- stato: **✅ SUPERATO — pronti per il paper trading**
- copertura universo: **84/200 crypto (42%)** · obiettivo ≥ 35%
- coppie validate (>= 3 pass OOS): **279**
- universo scansionato: 0GUSDT, 1000BONKUSDT, 1000FLOKIUSDT, 1000LUNCUSDT, 1000PEPEUSDT, 1000SHIBUSDT, 2ZUSDT, 4USDT, AAVEUSDT, ACEUSDT, ADAUSDT, AEROUSDT, AIAUSDT, AINUSDT, AKEUSDT, AKTUSDT, ALGOUSDT, ALICEUSDT, APEUSDT, API3USDT, APRUSDT, APTUSDT, ARBUSDT, ARKUSDT, ARPAUSDT, ARUSDT, ARXUSDT, ASRUSDT, ASTERUSDT, ATOMUSDT, AVAXUSDT, AVNTUSDT, AXSUSDT, BANDUSDT, BANKUSDT, BASEDUSDT, BCHUSDT, BEAMXUSDT, BEATUSDT, BERAUSDT, BIOUSDT, BNBUSDT, BOMEUSDT, BRUSDT, BTCUSDT, BTWUSDT, BULLAUSDT, C98USDT, CAKEUSDT, CAPUSDT, CARVUSDT, CCUSDT, CHIPUSDT, CHZUSDT, CLOUSDT, COLLECTUSDT, COTIUSDT, CRVUSDT, CTSIUSDT, CTUSDT, CYBERUSDT, DASHUSDT, DIAUSDT, DOGEUSDT, DOTUSDT, EDENUSDT, EDUUSDT, EGLDUSDT, EIGENUSDT, ENAUSDT, ENJUSDT, ENSUSDT, ESPUSDT, ETCUSDT, ETHFIUSDT, ETHUSDT, FARTCOINUSDT, FETUSDT, FILUSDT, FLUIDUSDT, FLUXUSDT, GALAUSDT, GIGGLEUSDT, GRAMUSDT, GRASSUSDT, GRIFFAINUSDT, GTCUSDT, GUSDT, HBARUSDT, HOMEUSDT, HUMAUSDT, HYPEUSDT, ICPUSDT, INJUSDT, IOTAUSDT, JSTUSDT, JTOUSDT, JUPUSDT, KAITOUSDT, KAVAUSDT, LABUSDT, LDOUSDT, LINKUSDT, LITUSDT, LPTUSDT, LSKUSDT, LTCUSDT, LYNUSDT, MAGICUSDT, MAGMAUSDT, MANAUSDT, MARSCOINUSDT, METUSDT, MINAUSDT, MIRAUSDT, MONUSDT, MORPHOUSDT, MOVRUSDT, MUBARAKUSDT, MYXUSDT, NEARUSDT, NIGHTUSDT, NILUSDT, NMRUSDT, NOMUSDT, OGNUSDT, ONDOUSDT, ONEUSDT, OPNUSDT, OPUSDT, ORCAUSDT, ORDIUSDT, PARTIUSDT, PAXGUSDT, PENDLEUSDT, PENGUUSDT, PEOPLEUSDT, PHAUSDT, PLUMEUSDT, POLUSDT, PONSUSDT, PROMUSDT, PUMPUSDT, PYTHUSDT, QNTUSDT, QUSDT, RAYSOLUSDT, RENDERUSDT, RESOLVUSDT, REUSDT, RIVERUSDT, RLCUSDT, RUNEUSDT, RVNUSDT, SAGAUSDT, SANDUSDT, SCRUSDT, SEIUSDT, SENTUSDT, SKYUSDT, SOLUSDT, SOONUSDT, SPXUSDT, STRKUSDT, STXUSDT, SUIUSDT, SUSDT, SYNUSDT, TAOUSDT, THETAUSDT, TIAUSDT, TRBUSDT, TRUMPUSDT, TRXUSDT, TUTUSDT, UMAUSDT, UNIUSDT, USELESSUSDT, USUSDT, VELVETUSDT, VIRTUALUSDT, VTHOUSDT, VVVUSDT, WIFUSDT, WLDUSDT, WLFIUSDT, WUSDT, XAUTUSDT, XLMUSDT, XMRUSDT, XPLUSDT, XRPUSDT, ZAMAUSDT, ZECUSDT, ZENUSDT, ZKCUSDT, ZKUSDT, ZROUSDT, 牛来USDT, 龙虾USDT
- aggiornato: 2026-10-07 05:06 UTC

### Salute del registro

- composizione: **1 base** · **2232 generate** (di cui 1896 con almeno una conferma)
- occupazione: 2233/3000 — ok

### Strategie VALIDATE (operate dal bot)
| Coin | Strategia | Passes | PF | PnL OOS | Parametri |
|---|---|---|---|---|---|
| JASMYUSDT | gen_b2f350ff | 4 | 1.603 | 137% | scale_r_mults=[2.0, 4.0, 6.0] |
| TUTUSDT | gen_4465723e | 4 | 1.53 | 125% | scale_r_mults=[1.5, 3.0, 5.0] |
| DOTUSDT | gen_da39a23a | 4 | 1.488 | 118% | scale_r_mults=[1.5, 3.0, 5.0] |
| MUBARAKUSDT | gen_1f7ead60 | 4 | 2.776 | 114% | scale_r_mults=[2.0, 4.0, 6.0] |
| RUNEUSDT | gen_f22e08b7 | 3 | 1.544 | 113% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.5 |
| ORCAUSDT | gen_271ab7ec | 4 | 1.851 | 113% | scale_r_mults=[1.0, 2.0, 3.0] |
| ORCAUSDT | gen_871647b8 | 4 | 1.859 | 111% | scale_r_mults=[1.5, 3.0, 5.0] |
| STXUSDT | gen_00e50229 | 3 | 1.339 | 111% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| USELESSUSDT | gen_194e2514 | 4 | 2.036 | 108% | scale_r_mults=[2.0, 4.0, 6.0] |
| USELESSUSDT | gen_1bb04e1a | 4 | 2.036 | 108% | scale_r_mults=[2.0, 4.0, 6.0] |
| PTBUSDT | gen_684d7623 | 3 | 1.871 | 107% | scale_r_mults=[1.0, 1.5, 2.5], sl_to_breakeven=True, profit_lock_keep=0.65 |
| UBUSDT | gen_d926b0fd | 3 | 1.789 | 103% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.35 |
| GPSUSDT | gen_bf1e00d4 | 4 | 1.59 | 103% | scale_r_mults=[1.5, 3.0, 5.0] |
| STXUSDT | gen_b9bf5d01 | 4 | 1.54 | 103% | scale_r_mults=[2.0, 4.0, 6.0] |
| DOTUSDT | gen_d85b1f05 | 4 | 1.483 | 102% | scale_r_mults=[1.5, 3.0, 5.0] |
| PARTIUSDT | gen_871647b8 | 4 | 2.117 | 102% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.5 |
| PROMUSDT | gen_cd5c842f | 4 | 1.628 | 99% | scale_r_mults=[2.0, 4.0, 6.0] |
| ORCAUSDT | gen_5b847426 | 4 | 1.859 | 96% | scale_r_mults=[2.0, 4.0, 6.0] |
| DEXEUSDT | gen_fa304106 | 4 | 2.06 | 95% | scale_r_mults=[1.5, 3.0, 5.0] |
| SPXUSDT | gen_725cb5f4 | 4 | 1.708 | 92% | scale_r_mults=[0.75, 1.5, 3.0] |
| SYRUPUSDT | gen_4c6df481 | 4 | 1.544 | 90% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.75 |
| ORCAUSDT | gen_7b4a474b | 4 | 2.148 | 89% | scale_r_mults=[1.5, 3.0, 5.0] |
| ORCAUSDT | gen_bbe21d3f | 4 | 1.952 | 87% | scale_r_mults=[1.5, 3.0, 5.0] |
| DEXEUSDT | gen_b31d8b93 | 4 | 1.881 | 87% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True |
| BRUSDT | gen_95fb50ce | 3 | 1.727 | 87% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| STXUSDT | gen_14e1775b | 4 | 1.74 | 87% | scale_r_mults=[2.0, 4.0, 6.0] |
| STXUSDT | gen_68ebd3b9 | 4 | 1.748 | 86% | scale_r_mults=[2.0, 4.0, 6.0] |
| XPINUSDT | gen_2e0818c8 | 3 | 4.01 | 85% | scale_r_mults=[0.75, 1.25, 1.75], sl_to_breakeven=True, profit_lock_keep=0.65 |
| IDUSDT | gen_6bc43e03 | 3 | 1.537 | 84% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.5 |
| IDUSDT | gen_c5430258 | 3 | 1.537 | 84% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.5 |
| IDUSDT | gen_dd9238bf | 3 | 1.537 | 84% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.5 |
| SPXUSDT | gen_ba3a671f | 4 | 1.644 | 84% | scale_r_mults=[0.75, 1.5, 3.0] |
| HEIUSDT | gen_e6ddc613 | 4 | 2.201 | 83% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.5 |
| ORCAUSDT | gen_9a383fff | 5 | 1.978 | 82% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True |
| DOTUSDT | gen_919c110c | 4 | 1.462 | 82% | scale_r_mults=[2.0, 4.0, 6.0] |
| SEIUSDT | gen_4f890271 | 4 | 1.851 | 82% | scale_r_mults=[2.0, 4.0, 6.0] |
| ORCAUSDT | gen_e6ddc613 | 5 | 1.94 | 81% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True |
| TAUSDT | gen_543186c5 | 4 | 2.012 | 76% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| TAUSDT | gen_01fbe76f | 3 | 1.649 | 75% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| BULLAUSDT | gen_0eb59b31 | 3 | 2.623 | 74% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.35 |
| XPINUSDT | gen_c60cc1b9 | 4 | 3.25 | 74% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.35 |
| QUSDT | gen_3ee1484b | 4 | 2.537 | 71% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.75 |
| QUSDT | gen_e75ddbfd | 4 | 2.537 | 71% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.75 |
| QUSDT | gen_da608d9f | 4 | 2.444 | 71% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.75 |
| QUSDT | gen_85fadf54 | 4 | 1.86 | 70% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.75 |
| MUBARAKUSDT | gen_e933160c | 4 | 1.889 | 69% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.35 |
| MUBARAKUSDT | gen_ff3e4154 | 5 | 1.889 | 69% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.35 |
| CROSSUSDT | gen_4e6e1ae0 | 3 | 2.63 | 67% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| UBUSDT | gen_1e8c6a66 | 3 | 1.757 | 66% | scale_r_mults=[1.0, 1.5, 2.5], sl_to_breakeven=True, profit_lock_keep=0.35 |
| UBUSDT | gen_902fb1fd | 3 | 1.757 | 66% | scale_r_mults=[1.0, 1.5, 2.5], sl_to_breakeven=True, profit_lock_keep=0.35 |
| SKYAIUSDT | gen_6cf80ae6 | 4 | 2.518 | 65% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True |
| SKYAIUSDT | gen_c202787e | 4 | 2.518 | 65% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True |
| TAUSDT | gen_b5d63a02 | 3 | 2.022 | 65% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| GPSUSDT | gen_871647b8 | 5 | 1.517 | 64% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.5 |
| SCRUSDT | gen_bd8f158b | 4 | 2.035 | 63% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep

[... 18667 caratteri omessi (testa e coda conservate) ...]

c9b332f | 3 | None | 0% | scale_r_mults=[1.0, 2.0, 3.0] |
| SUPERUSDT | gen_0eb999b7 | 3 | None | 0% | scale_r_mults=[1.5, 3.0, 5.0] |
| SYRUPUSDT | gen_98d56766 | 3 | None | 0% | scale_r_mults=[1.5, 3.0, 5.0] |
| TAUSDT | gen_4e6e1ae0 | 3 | 2.15 | 0% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.75 |
| TAUSDT | gen_b028553e | 3 | None | 0% | scale_r_mults=[1.5, 3.0, 5.0] |
| TAUSDT | gen_b0e86c70 | 3 | 2.477 | 0% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.5 |
| TAUSDT | gen_c647ead7 | 3 | 2.023 | 0% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| THEUSDT | gen_658b2edb | 3 | None | 0% | scale_r_mults=[2.0, 4.0, 6.0] |
| THEUSDT | gen_a640dfa5 | 3 | None | 0% | scale_r_mults=[2.0, 4.0, 6.0] |
| TRUMPUSDT | gen_f156ca1b | 3 | None | 0% | scale_r_mults=[2.0, 4.0, 6.0] |
| TSTUSDT | gen_a640dfa5 | 3 | None | 0% | scale_r_mults=[2.0, 4.0, 6.0] |
| UBUSDT | gen_08664b28 | 3 | 1.839 | 0% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.35 |
| UBUSDT | gen_0d7be682 | 3 | None | 0% | scale_r_mults=[2.0, 4.0, 6.0] |
| UBUSDT | gen_2a2898b0 | 3 | None | 0% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True |
| UBUSDT | gen_3b9c62e9 | 3 | None | 0% | scale_r_mults=[1.5, 3.0, 5.0] |
| UBUSDT | gen_4e6e1ae0 | 3 | 2.957 | 0% | scale_r_mults=[1.0, 2.0, 3.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| UBUSDT | gen_53b10d52 | 3 | None | 0% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True |
| UBUSDT | gen_5b847426 | 3 | None | 0% | scale_r_mults=[1.5, 3.0, 5.0] |
| UBUSDT | gen_8e475cd9 | 3 | None | 0% | scale_r_mults=[1.5, 3.0, 5.0] |
| UBUSDT | gen_bbe21d3f | 3 | None | 0% | scale_r_mults=[1.5, 3.0, 5.0] |
| UBUSDT | gen_fb7d035a | 3 | None | 0% | scale_r_mults=[1.5, 3.0, 5.0] |
| USELESSUSDT | gen_1623b4cb | 3 | None | 0% | scale_r_mults=[1.5, 3.0, 5.0] |
| USELESSUSDT | gen_68a8a9c7 | 3 | None | 0% | scale_r_mults=[2.0, 4.0, 6.0] |
| USELESSUSDT | gen_96c1ed1b | 3 | 2.06 | 0% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.5 |
| USELESSUSDT | gen_acea368d | 3 | None | 0% | scale_r_mults=[2.0, 4.0, 6.0] |
| USELESSUSDT | gen_c0fd1d91 | 3 | None | 0% | scale_r_mults=[1.5, 3.0, 5.0] |
| USELESSUSDT | gen_e09c5203 | 3 | 1.636 | 0% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.5 |
| USELESSUSDT | gen_fa5179ea | 3 | None | 0% | scale_r_mults=[2.0, 4.0, 6.0] |
| VETUSDT | gen_b2f350ff | 3 | None | 0% | scale_r_mults=[2.0, 4.0, 6.0] |
| VETUSDT | gen_b9c251a1 | 3 | None | 0% | scale_r_mults=[1.0, 1.5, 2.5], sl_to_breakeven=True |
| VETUSDT | gen_fb3d971f | 3 | None | 0% | scale_r_mults=[2.0, 4.0, 6.0] |
| WALUSDT | gen_2b41880d | 3 | None | 0% | scale_r_mults=[2.0, 4.0, 6.0] |
| WALUSDT | gen_cee79cdd | 3 | None | 0% | scale_r_mults=[2.0, 4.0, 6.0] |
| XPLUSDT | gen_e59ad90b | 3 | None | 0% | scale_r_mults=[1.5, 3.0, 5.0] |
| ZKUSDT | gen_c61d9322 | 3 | None | 0% | scale_r_mults=[2.0, 4.0, 6.0] |
| ZORAUSDT | gen_2c248ee9 | 3 | None | 0% | scale_r_mults=[1.5, 3.0, 5.0] |
| ZORAUSDT | gen_ceab7f6a | 3 | None | 0% | scale_r_mults=[1.5, 3.0, 5.0] |
| ZORAUSDT | gen_f4e37ccc | 3 | 2.788 | 0% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.65 |

## Ultimo run di ottimizzazione
_aggiornato: 2026-09-21 12:43 UTC · 1320 coppie valutate, 0 passate in questo run_

_Nessuna coppia ha passato in questo run._

## Dove muoiono le candidate (autopsia del GATE 1)

**strategie base** — 1320 valutazioni, 0 passate (0.00%) · 2026-09-21 12:43 UTC

| Criterio che ferma | Casi | Quota |
|---|---|---|
| regime | 22 | 1.7% |
| total_return | 1207 | 91.4% |
| pf_ex_top | 3 | 0.2% |
| holdout | 1 | 0.1% |
| trades | 6 | 0.5% |
| recovery | 64 | 4.8% |
| consistency | 17 | 1.3% |

- quasi-passaggi (un solo criterio, di poco): **1** — sono i semi delle mutazioni del run successivo

**strategie generate** — 45069 valutazioni, 496 passate (1.10%) · 2026-10-07 04:51 UTC

| Criterio che ferma | Casi | Quota |
|---|---|---|
| regime | 3685 | 8.3% |
| total_return | 34168 | 76.7% |
| trades | 1189 | 2.7% |
| holdout | 472 | 1.1% |
| pf_ex_top | 361 | 0.8% |
| consistency | 1011 | 2.3% |
| recovery | 3687 | 8.3% |

- quasi-passaggi (un solo criterio, di poco): **40** — sono i semi delle mutazioni del run successivo

## Supervisore (taratura automatica)

- ultimo giro: 2026-10-07 06:03 UTC · coppie validate: **297** · GATE 1 pronto: True
- tasso di passaggio misurato: **1.069%**

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
- totale: **345** · vinti: 193 (56%) · PnL realizzato: **-88.03**
- confronto col mercato: noi -8.80% vs BTC buy&hold +11.28% nello stesso periodo → **sotto** il mercato

- costi: **49.41 USDT** su 345 trade (0.14/trade) _(stimati dal modello del gate, non misurati dai fill)_
  - commissioni 27.63 · spread 21.72 · funding +0.05
  - lordo -38.62 → netto -88.03 · **break-even 5.41%** dell'equity
  - piu' costose: DEXEUSDT 3.03 · SYRUPUSDT 2.56 · ZORAUSDT 1.94 · SPXUSDT 1.91 · USELESSUSDT 1.81
  - ⚠️ Costi operativi elevati: servono 5.41% solo per pareggiare (soglia 1.5%)

| Uscita | Trade | % | PnL |
|---|---|---|---|
| Trailing stop | 156 | 45% | +132.90 |
| Stop loss (prima di qualsiasi TP) | 150 | 43% | -329.92 |
| Scale-out (>=1 TP incassato, residuo a BE) | 30 | 9% | +64.37 |
| Time exit (orizzonte scaduto) | 6 | 2% | +18.93 |
| Take profit (fino all'ultimo gradino) | 3 | 1% | +25.69 |

- gradini raggiunti (su 345 trade): 0 TP: 309 (90%) · 1 TP: 28 (8%) · 2 TP: 5 (1%) · 3 TP: 3 (1%)

- **drawdown di portafoglio: 88.03 USDT** (ritorno -88.03 · recovery -1.00) · max 12 posizioni aperte insieme
  - il gate prometteva recovery ≥ 2.0 per ogni coppia (peggiore in registro: 0.00); il PORTAFOGLIO realizza -1.00
  _uscite in ordine di TEMPO: e' la buca vera, quella che il gate non vede perche' valida una coppia alla volta._

- escursione favorevole (mfe_r, 345 trade): mediana **0.82R** · ≥1R: 39% · ≥1.5R: 14% · ≥3R: 3% · ≥5R: 0%
  _quanto lontano arriva il prezzo, in unità di R: dice se la scala di TP è raggiungibile. Dettaglio: `python -m scripts.mfe_report`_

## Deriva paper vs gate
_il gate promette sulla storia, il paper misura il presente. `drift` = promessa contraddetta -> size/leva frenate subito e fallimento al gate alla prossima passata._

- **globale**: drift · 332 trade · PF vissuto 0.726 vs 2.024 atteso · mfe mediana 0.82R

- **freno globale attivo**: size x0.5 e leva x0.71 (radice) su OGNI trade finche' il PF a 30 giorni resta sotto 0.6 x atteso (motivo: PF 0.73 vs 2.02 atteso · mfe mediana 0.82R < primo TP 1.50R)

| Coppia | Verdetto | Trade | PF vissuto/atteso | Motivo |
|---|---|---|---|---|
| PROMUSDT|gen_cd5c842f | drift | 9 | 3.732 / 1.628 | mfe mediana 1.10R < primo TP 2.00R |
| USELESSUSDT|gen_2031005e | watch | 7 | 0.304 / 1.54 | PF 0.30 vs 1.54 atteso · mfe mediana 0.80R < primo TP 2.00R |
| SPXUSDT|gen_ba3a671f | watch | 7 | 0.047 / 1.644 | PF 0.05 vs 1.64 atteso · mfe mediana 0.33R < primo TP 0.75R |
| SYRUPUSDT|gen_4c6df481 | watch | 7 | 1.376 / 1.544 | mfe mediana 1.01R < primo TP 2.00R |
| QUSDT|gen_18c839a0 | watch | 5 | 0.936 / 2.883 | PF 0.94 vs 2.88 atteso · mfe mediana 0.91R < primo TP 1.50R |
| GPSUSDT|gen_bf1e00d4 | watch | 5 | 5.631 / 1.59 | mfe mediana 0.90R < primo TP 1.50R |
| DEXEUSDT|gen_fa304106 | watch | 5 | 0.0 / 2.06 | PF 0.00 vs 2.06 atteso · mfe mediana 0.52R < primo TP 1.50R |
| SPXUSDT|gen_725cb5f4 | watch | 4 | 0.39 / 1.708 | PF 0.39 vs 1.71 atteso · mfe mediana 0.47R < primo TP 0.75R |
| DEXEUSDT|gen_b31d8b93 | watch | 4 | 0.149 / 1.881 | PF 0.15 vs 1.88 atteso · mfe mediana 1.23R < primo TP 2.00R |
| MUBARAKUSDT|gen_1f7ead60 | watch | 4 | 0.108 / 2.776 | PF 0.11 vs 2.78 atteso · mfe mediana 1.25R < primo TP 2.00R |
| AVAAIUSDT|gen_e50a9211 | watch | 4 | 0.345 / 1.525 | PF 0.35 vs 1.52 atteso |
| HUMAUSDT|gen_fca11c08 | watch | 4 | 0.0 / 1.657 | PF 0.00 vs 1.66 atteso · mfe mediana 0.10R < primo TP 2.00R |
| PTBUSDT|gen_684d7623 | watch | 4 | 1.377 / 1.871 | mfe mediana 0.53R < primo TP 1.00R |
| SYRUPUSDT|gen_af734c68 | watch | 3 | 0.407 / 1.493 | PF 0.41 vs 1.49 atteso · mfe mediana 0.94R < primo TP 1.50R |
| ORCAUSDT|gen_6d06dca0 | watch | 3 | 0.0 / 1.967 | PF 0.00 vs 1.97 atteso · mfe mediana 0.49R < primo TP 1.50R |
| FORMUSDT|gen_c647ead7 | watch | 3 | 99.0 / 2.224 | mfe mediana 0.51R < primo TP 0.75R |
| JTOUSDT|gen_f238d283 | watch | 3 | 0.653 / 1.64 | PF 0.65 vs 1.64 atteso |
| VETUSDT|gen_6d06dca0 | watch | 3 | 0.386 / 1.631 | PF 0.39 vs 1.63 atteso |
| STXUSDT|gen_b9bf5d01 | watch | 3 | 0.208 / 1.54 | PF 0.21 vs 1.54 atteso · mfe mediana 0.74R < primo TP 2.00R |
| FLOCKUSDT|gen_c5194ce4 | watch | 3 | 0.0 / 1.955 | PF 0.00 vs 1.96 atteso · mfe mediana 0.05R < primo TP 0.75R |

- serie di perdite (freno SPENTO dal 24 set, solo misura): **gen_fa304106** (10 perdite di fila)

## Calibrazione della confidenza
_la confidenza del segnale modula size e leva: qui si verifica che predica davvero l'esito, invece di darlo per scontato._

- verdetto: **costante** · 332 trade · correlazione None · influenza applicata **x1.0**
- tutte le strategie generate escono a confidenza 60: la calibrazione non puo' misurare nulla finche' la confidenza non varia (332 trade, confidenza 60-60)

| Fascia di confidenza | Trade | Win rate | Esito medio |
|---|---|---|---|
| 60.0–60.0 | 110 | 56% | -0.13% |
| 60.0–60.0 | 110 | 62% | -0.09% |
| 60.0–60.0 | 112 | 47% | -0.85% |

_se l'esito medio CRESCE dalla fascia bassa all'alta, la confidenza ordina correttamente i trade._
```
