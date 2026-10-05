# 0490-5ott-mattina-stato.req

_eseguito: 2026-10-05 06:04 UTC_

**richiesta:** `stato`
**eseguito:** `.venv/bin/python -m scripts.state_snapshot --no-write`
**esito:** codice 0 in 3.9s

```
[firebase] connesso (Firestore + RTDB)
# Stato sistema (snapshot)
_Generato: 2026-10-05 06:04 UTC_

## Bot
- stato: **running** (🟢 online)
- regime: sideways
- DRY_RUN: True
- equity: **$923.92**
- ultimo heartbeat: 2026-10-05 06:04 UTC
- stream prezzi: 🟢 attivo

## Ultima decisione
- esito: **⚪ FLAT** (2026-10-05 06:02 UTC)
- motivo: parita' backtest: 1 segnali validi aperti
- asset valutati: 76 · segnali: 1 · miglior segnale MUBARAKUSDT gen_1f7ead60 (conf. 60.0/soglia 30)

## Posizioni aperte
- HEMIUSDT: long qty=6740.045420556005 @ 0.005954 uPnL=0.2724743260731982 · rischio 0.05% · leva 1.0x
- MUBARAKUSDT: short qty=454.80881262007244 @ 0.07801 uPnL=0.2529337583086633 · rischio 0.11% · leva 2.0x
- **rischio aperto totale: 0.16%** dell'equity su 2 posizioni

## GATE 1 — Validazione strategie
- stato: **✅ SUPERATO — pronti per il paper trading**
- copertura universo: **77/200 crypto (38%)** · obiettivo ≥ 35%
- coppie validate (>= 3 pass OOS): **235**
- universo scansionato: 0GUSDT, 1000000BOBUSDT, 1000BONKUSDT, 1000FLOKIUSDT, 1000PEPEUSDT, 1000SHIBUSDT, 1INCHUSDT, 2ZUSDT, 4USDT, AAVEUSDT, ACEUSDT, ADAUSDT, AEROUSDT, AINUSDT, AIOUSDT, AKEUSDT, AKTUSDT, ALGOUSDT, ALICEUSDT, ALPINEUSDT, APEUSDT, APTUSDT, ARBUSDT, ARKUSDT, ARUSDT, ASTERUSDT, ATHUSDT, ATOMUSDT, ATUSDT, AVAXUSDT, AXSUSDT, BANKUSDT, BATUSDT, BCHUSDT, BEAMXUSDT, BLESSUSDT, BNBUSDT, BOMEUSDT, BROCCOLI714USDT, BRUSDT, BTCUSDT, BTWUSDT, BULLAUSDT, CAKEUSDT, CAPUSDT, CARVUSDT, CCUSDT, CHIPUSDT, CHZUSDT, CLOUSDT, COAIUSDT, COLLECTUSDT, COTIUSDT, CRVUSDT, CTUSDT, DASHUSDT, DOGEUSDT, DOTUSDT, EIGENUSDT, ENAUSDT, ENJUSDT, ENSUSDT, ESPUSDT, ETCUSDT, ETHFIUSDT, ETHUSDT, EULUSDT, FARTCOINUSDT, FETUSDT, FFUSDT, FIDAUSDT, FILUSDT, GALAUSDT, GIGGLEUSDT, GMTUSDT, GRAMUSDT, GRASSUSDT, GRTUSDT, GTCUSDT, HAEDALUSDT, HBARUSDT, HUMAUSDT, HYPEUSDT, ICPUSDT, IMXUSDT, INITUSDT, INJUSDT, IOTAUSDT, IOUSDT, JSTUSDT, JTOUSDT, JUPUSDT, KAITOUSDT, KITEUSDT, LABUSDT, LAUSDT, LDOUSDT, LINKUSDT, LITUSDT, LSKUSDT, LTCUSDT, LYNUSDT, MAGICUSDT, MAGMAUSDT, MANAUSDT, MARSCOINUSDT, MEGAUSDT, METUSDT, MINAUSDT, MONUSDT, MORPHOUSDT, MOVRUSDT, MUBARAKUSDT, NEARUSDT, NEIROUSDT, NIGHTUSDT, NILUSDT, NMRUSDT, NOMUSDT, ONDOUSDT, ONEUSDT, OPENUSDT, OPNUSDT, OPUSDT, ORCAUSDT, ORDIUSDT, PAXGUSDT, PENDLEUSDT, PENGUUSDT, PHAROSUSDT, PHAUSDT, PLUMEUSDT, POLUSDT, PONSUSDT, PORTALUSDT, PUMPBTCUSDT, PUMPUSDT, PYTHUSDT, QNTUSDT, RAYSOLUSDT, RENDERUSDT, RESOLVUSDT, REUSDT, RIVERUSDT, ROBOUSDT, RUNEUSDT, SAFEUSDT, SAGAUSDT, SANDUSDT, SCRUSDT, SEIUSDT, SENTUSDT, SKYAIUSDT, SKYUSDT, SOLUSDT, SOONUSDT, SPORTFUNUSDT, SPXUSDT, STARUSDT, STRKUSDT, STXUSDT, SUIUSDT, SUPERUSDT, SUSDT, SYNUSDT, SYRUPUSDT, TAKEUSDT, TAOUSDT, TIAUSDT, TOWNSUSDT, TRUMPUSDT, TRXUSDT, TSTUSDT, UNIUSDT, USELESSUSDT, USUSDT, VELVETUSDT, VETUSDT, VIRTUALUSDT, VVVUSDT, WIFUSDT, WLDUSDT, WLFIUSDT, WUSDT, XAUTUSDT, XLMUSDT, XMRUSDT, XPLUSDT, XRPUSDT, XTZUSDT, YFIUSDT, YGGUSDT, ZAMAUSDT, ZECUSDT, ZENUSDT, ZKPUSDT, ZKUSDT, ZROUSDT, 牛来USDT, 龙虾USDT
- aggiornato: 2026-10-05 04:26 UTC

### Salute del registro

- composizione: **1 base** · **2023 generate** (di cui 1685 con almeno una conferma)
- occupazione: 2024/3000 — ok

### Strategie VALIDATE (operate dal bot)
| Coin | Strategia | Passes | PF | PnL OOS | Parametri |
|---|---|---|---|---|---|
| JASMYUSDT | gen_b2f350ff | 4 | 1.603 | 137% | scale_r_mults=[2.0, 4.0, 6.0] |
| TUTUSDT | gen_4465723e | 4 | 1.53 | 125% | scale_r_mults=[1.5, 3.0, 5.0] |
| DOTUSDT | gen_da39a23a | 4 | 1.488 | 118% | scale_r_mults=[1.5, 3.0, 5.0] |
| MUBARAKUSDT | gen_1f7ead60 | 4 | 2.776 | 114% | scale_r_mults=[2.0, 4.0, 6.0] |
| ORCAUSDT | gen_271ab7ec | 4 | 1.851 | 113% | scale_r_mults=[1.0, 2.0, 3.0] |
| ORCAUSDT | gen_871647b8 | 4 | 1.859 | 111% | scale_r_mults=[1.5, 3.0, 5.0] |
| USELESSUSDT | gen_194e2514 | 4 | 2.036 | 108% | scale_r_mults=[2.0, 4.0, 6.0] |
| USELESSUSDT | gen_1bb04e1a | 4 | 2.036 | 108% | scale_r_mults=[2.0, 4.0, 6.0] |
| GPSUSDT | gen_bf1e00d4 | 4 | 1.59 | 103% | scale_r_mults=[1.5, 3.0, 5.0] |
| STXUSDT | gen_b9bf5d01 | 4 | 1.54 | 103% | scale_r_mults=[2.0, 4.0, 6.0] |
| DOTUSDT | gen_d85b1f05 | 4 | 1.483 | 102% | scale_r_mults=[1.5, 3.0, 5.0] |
| PARTIUSDT | gen_871647b8 | 3 | 2.117 | 102% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.5 |
| PROMUSDT | gen_cd5c842f | 4 | 1.628 | 99% | scale_r_mults=[2.0, 4.0, 6.0] |
| ORCAUSDT | gen_5b847426 | 4 | 1.859 | 96% | scale_r_mults=[2.0, 4.0, 6.0] |
| UBUSDT | gen_d926b0fd | 3 | 1.689 | 96% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.35 |
| DEXEUSDT | gen_fa304106 | 4 | 2.06 | 95% | scale_r_mults=[1.5, 3.0, 5.0] |
| PTBUSDT | gen_684d7623 | 3 | 1.76 | 95% | scale_r_mults=[1.0, 1.5, 2.5], sl_to_breakeven=True, profit_lock_keep=0.65 |
| SPXUSDT | gen_725cb5f4 | 4 | 1.708 | 92% | scale_r_mults=[0.75, 1.5, 3.0] |
| ORCAUSDT | gen_7b4a474b | 4 | 2.148 | 89% | scale_r_mults=[1.5, 3.0, 5.0] |
| ORCAUSDT | gen_bbe21d3f | 4 | 1.952 | 87% | scale_r_mults=[1.5, 3.0, 5.0] |
| DEXEUSDT | gen_b31d8b93 | 4 | 1.881 | 87% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True |
| BRUSDT | gen_95fb50ce | 3 | 1.727 | 87% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| STXUSDT | gen_14e1775b | 4 | 1.74 | 87% | scale_r_mults=[2.0, 4.0, 6.0] |
| STXUSDT | gen_68ebd3b9 | 4 | 1.748 | 86% | scale_r_mults=[2.0, 4.0, 6.0] |
| SPXUSDT | gen_ba3a671f | 4 | 1.644 | 84% | scale_r_mults=[0.75, 1.5, 3.0] |
| HEIUSDT | gen_e6ddc613 | 4 | 2.201 | 83% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.5 |
| ORCAUSDT | gen_9a383fff | 5 | 1.978 | 82% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True |
| DOTUSDT | gen_919c110c | 4 | 1.462 | 82% | scale_r_mults=[2.0, 4.0, 6.0] |
| SEIUSDT | gen_4f890271 | 4 | 1.851 | 82% | scale_r_mults=[2.0, 4.0, 6.0] |
| SYRUPUSDT | gen_4c6df481 | 4 | 1.477 | 81% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.75 |
| ORCAUSDT | gen_e6ddc613 | 5 | 1.94 | 81% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True |
| XPINUSDT | gen_2e0818c8 | 3 | 3.809 | 80% | scale_r_mults=[0.75, 1.25, 1.75], sl_to_breakeven=True, profit_lock_keep=0.65 |
| TAUSDT | gen_543186c5 | 3 | 2.012 | 76% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| XPINUSDT | gen_c60cc1b9 | 3 | 3.25 | 74% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.35 |
| QUSDT | gen_da608d9f | 4 | 2.444 | 71% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.75 |
| MUBARAKUSDT | gen_e933160c | 4 | 1.889 | 69% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.35 |
| MUBARAKUSDT | gen_ff3e4154 | 5 | 1.889 | 69% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.35 |
| QUSDT | gen_3ee1484b | 4 | 2.556 | 68% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.75 |
| QUSDT | gen_e75ddbfd | 4 | 2.556 | 68% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.75 |
| QUSDT | gen_85fadf54 | 4 | 1.849 | 67% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.75 |
| IDUSDT | gen_6bc43e03 | 3 | 1.426 | 66% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| IDUSDT | gen_c5430258 | 3 | 1.426 | 66% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| IDUSDT | gen_dd9238bf | 3 | 1.426 | 66% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| SKYAIUSDT | gen_6cf80ae6 | 4 | 2.518 | 65% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True |
| SKYAIUSDT | gen_c202787e | 4 | 2.518 | 65% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True |
| GPSUSDT | gen_871647b8 | 5 | 1.517 | 64% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.5 |
| UBUSDT | gen_15837112 | 3 | 1.773 | 64% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.35 |
| SCRUSDT | gen_bd8f158b | 3 | 2.008 | 62% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| PUMPUSDT | gen_1000366e | 3 | 1.844 | 61% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.35 |
| MYXUSDT | gen_a5b0e4de | 3 | 3.066 | 60% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.35 |
| JUPUSDT | gen_bb762669 | 4 | 1.599 | 58% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.35 |
| NEIROUSDT | gen_413f1bd7 | 3 | 2.132 | 58% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.75 |
| QUSDT | gen_bf2be656 | 4 | 3.527 | 57% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.75 |
| SKYAIUSDT | gen_6191df86 | 4 | 2.751 | 54% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| HUMAUSDT | gen_da39a23a | 4 | 2.242 | 53% | scale_r_mults=[1.0, 1.5, 2.5], sl_to_breakeven=True, profit_lock_keep=0.75 |
| UBUSDT | gen_0ec2c344 | 3 | 1.757 | 53% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.5 |
| UBUSDT | gen_4348f9d4 | 3 | 1.757 | 53% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.5 |
| QUSDT | gen_18c839a0 | 5 | 3.118 | 53% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.75 |
| QUSDT | gen_b1ac5c24 | 4 | 3.118 | 53% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.75 |
| MUBARAKUSDT | gen_f86f7370 | 3 | 2.937 | 52% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.35 |
| CATIUSDT | gen_b3e46005 | 3 | 2.874 | 50% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.5 |
| STXUSDT | gen_a5b0e4de | 3 | 1.449 | 48% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.5 |
| PUMPUSDT | gen_08664b28 | 3 | 1.511 | 47% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.35 |
| GALAUSDT | gen_b9aa9989 | 4 | 1.922 | 46% | scale_r_mults=[1.0, 1.25, 2.0], sl_to_breakeven=True, profit_lock_keep=0.6

[... 12066 caratteri omessi (testa e coda conservate) ...]

| None | 0% | scale_r_mults=[1.0, 2.0, 3.0] |
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
| XPINUSDT | gen_871647b8 | 3 | 2.626 | 0% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.35 |
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
| total_return | 1207 | 91.4% |
| holdout | 1 | 0.1% |
| recovery | 64 | 4.8% |
| consistency | 17 | 1.3% |
| regime | 22 | 1.7% |
| pf_ex_top | 3 | 0.2% |
| trades | 6 | 0.5% |

- quasi-passaggi (un solo criterio, di poco): **1** — sono i semi delle mutazioni del run successivo

**strategie generate** — 42274 valutazioni, 440 passate (1.04%) · 2026-10-05 04:15 UTC

| Criterio che ferma | Casi | Quota |
|---|---|---|
| trades | 1809 | 4.3% |
| holdout | 373 | 0.9% |
| recovery | 3404 | 8.1% |
| consistency | 979 | 2.3% |
| regime | 3975 | 9.5% |
| pf_ex_top | 431 | 1.0% |
| total_return | 30863 | 73.8% |

- quasi-passaggi (un solo criterio, di poco): **40** — sono i semi delle mutazioni del run successivo

## Supervisore (taratura automatica)

- ultimo giro: 2026-10-05 06:03 UTC · coppie validate: **248** · GATE 1 pronto: True
- tasso di passaggio misurato: **1.009%**

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
- totale: **291** · vinti: 165 (57%) · PnL realizzato: **-76.08**
- confronto col mercato: noi -7.61% vs BTC buy&hold +13.35% nello stesso periodo → **sotto** il mercato

- costi: **42.47 USDT** su 291 trade (0.15/trade) _(stimati dal modello del gate, non misurati dai fill)_
  - commissioni 23.96 · spread 18.46 · funding +0.05
  - lordo -33.61 → netto -76.08 · **break-even 4.60%** dell'equity
  - piu' costose: DEXEUSDT 3.03 · SYRUPUSDT 2.56 · SPXUSDT 1.77 · HUMAUSDT 1.69 · ORCAUSDT 1.69
  - ⚠️ Costi operativi elevati: servono 4.60% solo per pareggiare (soglia 1.5%)

| Uscita | Trade | % | PnL |
|---|---|---|---|
| Trailing stop | 132 | 45% | +121.14 |
| Stop loss (prima di qualsiasi TP) | 124 | 43% | -297.75 |
| Scale-out (>=1 TP incassato, residuo a BE) | 26 | 9% | +55.90 |
| Time exit (orizzonte scaduto) | 6 | 2% | +18.93 |
| Take profit (fino all'ultimo gradino) | 3 | 1% | +25.69 |

- gradini raggiunti (su 291 trade): 0 TP: 259 (89%) · 1 TP: 27 (9%) · 2 TP: 2 (1%) · 3 TP: 3 (1%)

- **drawdown di portafoglio: 80.54 USDT** (ritorno -76.08 · recovery -0.94) · max 12 posizioni aperte insieme
  - il gate prometteva recovery ≥ 2.0 per ogni coppia (peggiore in registro: 0.00); il PORTAFOGLIO realizza -0.94
  _uscite in ordine di TEMPO: e' la buca vera, quella che il gate non vede perche' valida una coppia alla volta._

- escursione favorevole (mfe_r, 291 trade): mediana **0.86R** · ≥1R: 41% · ≥1.5R: 15% · ≥3R: 2% · ≥5R: 0%
  _quanto lontano arriva il prezzo, in unità di R: dice se la scala di TP è raggiungibile. Dettaglio: `python -m scripts.mfe_report`_

## Deriva paper vs gate
_il gate promette sulla storia, il paper misura il presente. `drift` = promessa contraddetta -> size/leva frenate subito e fallimento al gate alla prossima passata._

- **globale**: drift · 280 trade · PF vissuto 0.734 vs 2.007 atteso · mfe mediana 0.85R

- **freno globale attivo**: size x0.5 e leva x0.71 (radice) su OGNI trade finche' il PF a 30 giorni resta sotto 0.6 x atteso (motivo: PF 0.73 vs 2.01 atteso · mfe mediana 0.85R < primo TP 1.50R)

| Coppia | Verdetto | Trade | PF vissuto/atteso | Motivo |
|---|---|---|---|---|
| PROMUSDT|gen_cd5c842f | watch | 7 | 4.156 / 1.628 | mfe mediana 1.10R < primo TP 2.00R |
| SPXUSDT|gen_ba3a671f | watch | 7 | 0.047 / 1.644 | PF 0.05 vs 1.64 atteso · mfe mediana 0.33R < primo TP 0.75R |
| USELESSUSDT|gen_2031005e | watch | 7 | 0.304 / 1.54 | PF 0.30 vs 1.54 atteso · mfe mediana 0.80R < primo TP 2.00R |
| SYRUPUSDT|gen_4c6df481 | watch | 7 | 1.376 / 1.477 | mfe mediana 1.01R < primo TP 2.00R |
| DEXEUSDT|gen_fa304106 | watch | 5 | 0.0 / 2.06 | PF 0.00 vs 2.06 atteso · mfe mediana 0.52R < primo TP 1.50R |
| QUSDT|gen_18c839a0 | watch | 5 | 0.936 / 3.118 | PF 0.94 vs 3.12 atteso · mfe mediana 0.91R < primo TP 1.50R |
| DEXEUSDT|gen_b31d8b93 | watch | 4 | 0.149 / 1.881 | PF 0.15 vs 1.88 atteso · mfe mediana 1.23R < primo TP 2.00R |
| GPSUSDT|gen_bf1e00d4 | watch | 4 | 4.936 / 1.59 | mfe mediana 0.90R < primo TP 1.50R |
| AVAAIUSDT|gen_e50a9211 | watch | 4 | 0.345 / 1.525 | PF 0.35 vs 1.52 atteso |
| HUMAUSDT|gen_fca11c08 | watch | 4 | 0.0 / 1.649 | PF 0.00 vs 1.65 atteso · mfe mediana 0.10R < primo TP 2.00R |
| SYRUPUSDT|gen_af734c68 | watch | 3 | 0.407 / 1.493 | PF 0.41 vs 1.49 atteso · mfe mediana 0.94R < primo TP 1.50R |
| FLOCKUSDT|gen_c5194ce4 | watch | 3 | 0.0 / 1.955 | PF 0.00 vs 1.96 atteso · mfe mediana 0.05R < primo TP 0.75R |
| PNUTUSDT|gen_4810faab | watch | 3 | 0.834 / 2.576 | PF 0.83 vs 2.58 atteso · mfe mediana 1.13R < primo TP 2.00R |
| UBUSDT|gen_f3661202 | watch | 3 | 0.923 / 1.679 | PF 0.92 vs 1.68 atteso · mfe mediana 1.03R < primo TP 2.00R |
| JTOUSDT|gen_f238d283 | watch | 3 | 0.653 / 1.64 | PF 0.65 vs 1.64 atteso |
| STXUSDT|gen_b9bf5d01 | watch | 3 | 0.208 / 1.54 | PF 0.21 vs 1.54 atteso · mfe mediana 0.74R < primo TP 2.00R |
| ORCAUSDT|gen_6d06dca0 | watch | 3 | 0.0 / 1.967 | PF 0.00 vs 1.97 atteso · mfe mediana 0.49R < primo TP 1.50R |
| VETUSDT|gen_6d06dca0 | watch | 3 | 0.386 / 1.631 | PF 0.39 vs 1.63 atteso |
| MUBARAKUSDT|gen_1f7ead60 | watch | 3 | 0.051 / 2.776 | PF 0.05 vs 2.78 atteso · mfe mediana 0.21R < primo TP 2.00R |
| MUBARAKUSDT|gen_e933160c | watch | 2 | 0.243 / 1.889 | PF 0.24 vs 1.89 atteso |

- serie di perdite (freno SPENTO dal 24 set, solo misura): **gen_fa304106** (8 perdite di fila)

## Calibrazione della confidenza
_la confidenza del segnale modula size e leva: qui si verifica che predica davvero l'esito, invece di darlo per scontato._

- verdetto: **costante** · 280 trade · correlazione None · influenza applicata **x1.0**
- tutte le strategie generate escono a confidenza 60: la calibrazione non puo' misurare nulla finche' la confidenza non varia (280 trade, confidenza 60-60)

| Fascia di confidenza | Trade | Win rate | Esito medio |
|---|---|---|---|
| 60.0–60.0 | 93 | 56% | -0.19% |
| 60.0–60.0 | 93 | 64% | +0.07% |
| 60.0–60.0 | 94 | 47% | -0.94% |

_se l'esito medio CRESCE dalla fascia bassa all'alta, la confidenza ordina correttamente i trade._
```
