# 0361-30set-stato.req

_eseguito: 2026-09-30 06:12 UTC_

**richiesta:** `stato`
**eseguito:** `.venv/bin/python -m scripts.state_snapshot --no-write`
**esito:** codice 0 in 3.5s

```
[firebase] connesso (Firestore + RTDB)
# Stato sistema (snapshot)
_Generato: 2026-09-30 06:12 UTC_

## Bot
- stato: **running** (🟢 online)
- regime: sideways
- DRY_RUN: True
- equity: **$931.35**
- ultimo heartbeat: 2026-09-30 06:12 UTC
- stream prezzi: 🟢 attivo

## Ultima decisione
- esito: **⚪ FLAT** (2026-09-30 06:02 UTC)
- motivo: parita' backtest: 1 segnali validi aperti
- asset valutati: 70 · segnali: 1 · miglior segnale STXUSDT gen_a5b0e4de (conf. 60.0/soglia 30)

## Posizioni aperte
- MUBARAKUSDT: long qty=396.75413495171176 @ 0.06124 uPnL=-0.5401582678381875 · rischio 0.13% · leva 1.0x
- STXUSDT: short qty=295.94977582462303 @ 0.3147 uPnL=0.2359020060435664 · rischio 0.16% · leva 1.0x
- **rischio aperto totale: 0.28%** dell'equity su 2 posizioni

## GATE 1 — Validazione strategie
- stato: **✅ SUPERATO — pronti per il paper trading**
- copertura universo: **70/200 crypto (35%)** · obiettivo ≥ 35%
- coppie validate (>= 3 pass OOS): **202**
- universo scansionato: 0GUSDT, 1000BONKUSDT, 1000FLOKIUSDT, 1000PEPEUSDT, 1000SHIBUSDT, 1INCHUSDT, 2ZUSDT, 4USDT, AAVEUSDT, ACEUSDT, ADAUSDT, AEROUSDT, AINUSDT, AKEUSDT, ALGOUSDT, ALICEUSDT, ALLOUSDT, APEUSDT, API3USDT, APRUSDT, APTUSDT, ARBUSDT, ARKUSDT, ARUSDT, ARXUSDT, ASTERUSDT, ATOMUSDT, AVAXUSDT, AXSUSDT, AZTECUSDT, BABYUSDT, BANKUSDT, BCHUSDT, BEATUSDT, BERAUSDT, BIOUSDT, BNBUSDT, BOMEUSDT, BRUSDT, BTCUSDT, BTWUSDT, CAKEUSDT, CAPUSDT, CCUSDT, CELOUSDT, CFGUSDT, CHIPUSDT, CHZUSDT, COMPUSDT, COTIUSDT, CRVUSDT, CVXUSDT, DASHUSDT, DATAIPUSDT, DEEPUSDT, DOGEUSDT, DOTUSDT, DYDXUSDT, EDENUSDT, EDGEUSDT, EGLDUSDT, EIGENUSDT, ENAUSDT, ENSUSDT, ESPORTSUSDT, ETCUSDT, ETHFIUSDT, ETHUSDT, FARTCOINUSDT, FETUSDT, FFUSDT, FILUSDT, FLOCKUSDT, FLOWUSDT, GALAUSDT, GIGGLEUSDT, GPSUSDT, GRAMUSDT, GRASSUSDT, GRTUSDT, GUSDT, HBARUSDT, HEMIUSDT, HUMAUSDT, HYPEUSDT, ICPUSDT, INITUSDT, INJUSDT, IOSTUSDT, IOTAUSDT, JASMYUSDT, JSTUSDT, JTOUSDT, JUPUSDT, KAITOUSDT, KASUSDT, KITEUSDT, KMNOUSDT, KSMUSDT, LABUSDT, LDOUSDT, LINKUSDT, LITUSDT, LSKUSDT, LTCUSDT, LUMIAUSDT, LYNUSDT, MANAUSDT, MARSCOINUSDT, METUSDT, MEWUSDT, MINAUSDT, MONUSDT, MORPHOUSDT, MOVRUSDT, MUBARAKUSDT, NEARUSDT, NEIROUSDT, NIGHTUSDT, NILUSDT, NMRUSDT, NOMUSDT, ONDOUSDT, ONEUSDT, ONGUSDT, OPNUSDT, OPUSDT, ORDIUSDT, PAXGUSDT, PENDLEUSDT, PENGUUSDT, PEOPLEUSDT, PHAROSUSDT, PHAUSDT, PLUMEUSDT, POLUSDT, PONSUSDT, PROMUSDT, PUMPUSDT, PYTHUSDT, QNTUSDT, QUSDT, RAREUSDT, RAVEUSDT, RAYSOLUSDT, RENDERUSDT, REUSDT, REZUSDT, RIVERUSDT, ROSEUSDT, RUNEUSDT, SAGAUSDT, SANDUSDT, SEIUSDT, SKYUSDT, SNXUSDT, SOLUSDT, SOONUSDT, SPKUSDT, SPXUSDT, STRKUSDT, STXUSDT, SUIUSDT, SUSHIUSDT, SYRUPUSDT, TAKEUSDT, TAOUSDT, TIAUSDT, TRBUSDT, TRIAUSDT, TRUMPUSDT, TRXUSDT, TUTUSDT, UAIUSDT, UBUSDT, UNIUSDT, USELESSUSDT, USUSDT, VETUSDT, VIRTUALUSDT, VTHOUSDT, VVVUSDT, WIFUSDT, WLDUSDT, WLFIUSDT, WUSDT, XAUTUSDT, XLMUSDT, XMRUSDT, XPLUSDT, XRPUSDT, YBUSDT, ZAMAUSDT, ZECUSDT, ZENUSDT, ZESTUSDT, ZROUSDT, 币安人生USDT, 牛来USDT, 龙虾USDT
- aggiornato: 2026-09-30 06:08 UTC

### Salute del registro

- composizione: **1 base** · **1531 generate** (di cui 1190 con almeno una conferma)
- occupazione: 1532/3000 — ok

### Strategie VALIDATE (operate dal bot)
| Coin | Strategia | Passes | PF | PnL OOS | Parametri |
|---|---|---|---|---|---|
| HEIUSDT | gen_e6ddc613 | 4 | 2.441 | 212% | scale_r_mults=[2.0, 4.0, 6.0] |
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
| PROMUSDT | gen_cd5c842f | 4 | 1.628 | 99% | scale_r_mults=[2.0, 4.0, 6.0] |
| PARTIUSDT | gen_871647b8 | 3 | 2.066 | 98% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.5 |
| ORCAUSDT | gen_5b847426 | 4 | 1.859 | 96% | scale_r_mults=[2.0, 4.0, 6.0] |
| DEXEUSDT | gen_fa304106 | 4 | 2.06 | 95% | scale_r_mults=[1.5, 3.0, 5.0] |
| QUSDT | gen_85fadf54 | 3 | 2.482 | 94% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.75 |
| SPXUSDT | gen_725cb5f4 | 4 | 1.708 | 92% | scale_r_mults=[0.75, 1.5, 3.0] |
| ORCAUSDT | gen_7b4a474b | 4 | 2.148 | 89% | scale_r_mults=[1.5, 3.0, 5.0] |
| ORCAUSDT | gen_bbe21d3f | 4 | 1.952 | 87% | scale_r_mults=[1.5, 3.0, 5.0] |
| DEXEUSDT | gen_b31d8b93 | 4 | 1.881 | 87% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True |
| STXUSDT | gen_14e1775b | 4 | 1.74 | 87% | scale_r_mults=[2.0, 4.0, 6.0] |
| STXUSDT | gen_68ebd3b9 | 4 | 1.748 | 86% | scale_r_mults=[2.0, 4.0, 6.0] |
| SPXUSDT | gen_ba3a671f | 4 | 1.644 | 84% | scale_r_mults=[0.75, 1.5, 3.0] |
| QUSDT | gen_3ee1484b | 3 | 3.072 | 82% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.75 |
| QUSDT | gen_e75ddbfd | 3 | 3.072 | 82% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.75 |
| ORCAUSDT | gen_9a383fff | 5 | 1.978 | 82% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True |
| DOTUSDT | gen_919c110c | 4 | 1.462 | 82% | scale_r_mults=[2.0, 4.0, 6.0] |
| SEIUSDT | gen_4f890271 | 4 | 1.851 | 82% | scale_r_mults=[2.0, 4.0, 6.0] |
| ORCAUSDT | gen_e6ddc613 | 5 | 1.94 | 81% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True |
| SYRUPUSDT | gen_4c6df481 | 3 | 1.445 | 76% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.75 |
| QUSDT | gen_da608d9f | 3 | 2.646 | 76% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.75 |
| XPINUSDT | gen_c60cc1b9 | 3 | 3.492 | 75% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.35 |
| MUBARAKUSDT | gen_e933160c | 3 | 1.868 | 67% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.35 |
| MUBARAKUSDT | gen_ff3e4154 | 4 | 1.868 | 67% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.35 |
| TAUSDT | gen_543186c5 | 3 | 1.81 | 65% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| SKYAIUSDT | gen_6cf80ae6 | 4 | 2.518 | 65% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True |
| SKYAIUSDT | gen_c202787e | 4 | 2.518 | 65% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True |
| GPSUSDT | gen_871647b8 | 4 | 1.517 | 64% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.5 |
| SKYAIUSDT | gen_6191df86 | 3 | 3.06 | 60% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| SCRUSDT | gen_bd8f158b | 3 | 1.915 | 59% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| NEIROUSDT | gen_413f1bd7 | 3 | 2.132 | 58% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.75 |
| QUSDT | gen_bf2be656 | 4 | 3.527 | 57% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.75 |
| JUPUSDT | gen_bb762669 | 3 | 1.565 | 56% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.35 |
| QUSDT | gen_18c839a0 | 4 | 3.23 | 55% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.75 |
| QUSDT | gen_b1ac5c24 | 3 | 3.23 | 55% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.75 |
| UBUSDT | gen_15837112 | 3 | 1.844 | 54% | scale_r_mults=[1.0, 2.0, 3.0], sl_to_breakeven=True, profit_lock_keep=0.35 |
| HUMAUSDT | gen_da39a23a | 3 | 2.24 | 53% | scale_r_mults=[1.0, 1.5, 2.5], sl_to_breakeven=True, profit_lock_keep=0.75 |
| CATIUSDT | gen_b3e46005 | 3 | 2.802 | 49% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.5 |
| SAHARAUSDT | gen_6b94025f | 4 | 2.199 | 49% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.35 |
| PLUMEUSDT | gen_e94b056d | 3 | 2.716 | 48% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.35 |
| STXUSDT | gen_a5b0e4de | 3 | 1.449 | 48% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.5 |
| GALAUSDT | gen_b9aa9989 | 3 | 1.922 | 46% | scale_r_mults=[1.0, 1.25, 2.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| UBUSDT | gen_0ec2c344 | 3 | 1.674 | 46% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.5 |
| UBUSDT | gen_4348f9d4 | 3 | 1.674 | 46% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.5 |
| SKYAIUSDT | gen_f68b811d | 3 | 2.294 | 46% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.35 |
| UBUSDT | gen_887d87df | 3 | 2.601 | 45% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.5 |
| SKYAIUSDT | gen_98837ec2 | 4 | 2.214 | 44% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True |
| UBUSDT | gen_8981d5f2 | 3 | 2.453 | 43% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| MUBARAKUSDT | gen_49c2f657 | 3 | 2.438 | 41% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.75 |
| HEMIUSDT | gen_108c996b | 4 | 1.986 | 40% | scale_r_mults=[2.0, 4.0, 6.0] |
| HEMIUSDT | gen_93131ef1 | 4 | 1.986 | 40% | scale_r_mults=[2.0, 4.0, 6.0] |
| OPENUSDT | gen_2bb283ca | 3 | 2.578 | 39% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.35 |
| SAHARAUSDT | gen_60d64cfd | 3 | 2.715 | 37% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.35 |
| MUBARAKUSDT | gen_2053cba6 | 4 | 1.979 | 35% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.75 |
| SAHARAUSDT | gen_1eec02f5 | 3 | 1.974 | 30% | 

[... 7716 caratteri omessi (testa e coda conservate) ...]

gen_b2f350ff | 3 | None | 0% | scale_r_mults=[2.0, 4.0, 6.0] |
| SKYAIUSDT | gen_752132bc | 3 | None | 0% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True |
| SKYAIUSDT | gen_ead1fe8a | 3 | None | 0% | scale_r_mults=[2.0, 4.0, 6.0] |
| SOPHUSDT | gen_42acf37e | 3 | None | 0% | scale_r_mults=[1.5, 3.0, 5.0] |
| SPXUSDT | gen_d03ff6d4 | 3 | None | 0% | scale_r_mults=[1.5, 3.0, 5.0] |
| STEEMUSDT | gen_4508a416 | 3 | None | 0% | scale_r_mults=[2.0, 4.0, 6.0] |
| STEEMUSDT | gen_addf82da | 3 | None | 0% | scale_r_mults=[2.0, 4.0, 6.0] |
| STXUSDT | gen_c7a02fce | 3 | None | 0% | scale_r_mults=[2.0, 4.0, 6.0] |
| STXUSDT | gen_d606fde3 | 3 | None | 0% | scale_r_mults=[1.5, 3.0, 5.0] |
| SUIUSDT | gen_8c9b332f | 3 | None | 0% | scale_r_mults=[1.0, 2.0, 3.0] |
| SUPERUSDT | gen_0eb999b7 | 3 | None | 0% | scale_r_mults=[1.5, 3.0, 5.0] |
| SYRUPUSDT | gen_98d56766 | 3 | None | 0% | scale_r_mults=[1.5, 3.0, 5.0] |
| SYRUPUSDT | gen_f3b97917 | 3 | None | 0% | scale_r_mults=[1.0, 1.5, 2.5] |
| TAUSDT | gen_b028553e | 3 | None | 0% | scale_r_mults=[1.5, 3.0, 5.0] |
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

## Ultimo run di ottimizzazione
_aggiornato: 2026-09-21 12:43 UTC · 1320 coppie valutate, 0 passate in questo run_

_Nessuna coppia ha passato in questo run._

## Dove muoiono le candidate (autopsia del GATE 1)

**strategie base** — 1320 valutazioni, 0 passate (0.00%) · 2026-09-21 12:43 UTC

| Criterio che ferma | Casi | Quota |
|---|---|---|
| recovery | 64 | 4.8% |
| total_return | 1207 | 91.4% |
| trades | 6 | 0.5% |
| holdout | 1 | 0.1% |
| regime | 22 | 1.7% |
| pf_ex_top | 3 | 0.2% |
| consistency | 17 | 1.3% |

- quasi-passaggi (un solo criterio, di poco): **1** — sono i semi delle mutazioni del run successivo

**strategie generate** — 24503 valutazioni, 49 passate (0.20%) · 2026-09-30 05:09 UTC

| Criterio che ferma | Casi | Quota |
|---|---|---|
| recovery | 1378 | 5.6% |
| total_return | 19566 | 80.0% |
| trades | 1601 | 6.5% |
| holdout | 68 | 0.3% |
| regime | 1356 | 5.5% |
| pf_ex_top | 195 | 0.8% |
| consistency | 290 | 1.2% |

- quasi-passaggi (un solo criterio, di poco): **40** — sono i semi delle mutazioni del run successivo

## Supervisore (taratura automatica)

- ultimo giro: 2026-09-30 06:01 UTC · coppie validate: **213** · GATE 1 pronto: True
- tasso di passaggio misurato: **0.190%**

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
- totale: **189** · vinti: 106 (56%) · PnL realizzato: **-68.65**
- confronto col mercato: noi -6.86% vs BTC buy&hold +9.83% nello stesso periodo → **sotto** il mercato

- costi: **29.66 USDT** su 189 trade (0.16/trade) _(stimati dal modello del gate, non misurati dai fill)_
  - commissioni 17.13 · spread 12.54 · funding -0.01
  - lordo -38.99 → netto -68.65 · **break-even 3.18%** dell'equity
  - piu' costose: DEXEUSDT 2.88 · SYRUPUSDT 1.75 · SPXUSDT 1.65 · ORCAUSDT 1.59 · USELESSUSDT 1.45
  - ⚠️ Costi operativi elevati: servono 3.18% solo per pareggiare (soglia 1.5%)

| Uscita | Trade | % | PnL |
|---|---|---|---|
| Trailing stop | 84 | 44% | +89.30 |
| Stop loss (prima di qualsiasi TP) | 83 | 44% | -236.68 |
| Scale-out (>=1 TP incassato, residuo a BE) | 19 | 10% | +44.48 |
| Take profit (fino all'ultimo gradino) | 2 | 1% | +20.78 |
| Time exit (orizzonte scaduto) | 1 | 1% | +13.48 |

- gradini raggiunti (su 189 trade): 0 TP: 167 (88%) · 1 TP: 19 (10%) · 2 TP: 1 (1%) · 3 TP: 2 (1%)

- **drawdown di portafoglio: 80.16 USDT** (ritorno -68.65 · recovery -0.86) · max 9 posizioni aperte insieme
  - il gate prometteva recovery ≥ 2.0 per ogni coppia (peggiore in registro: 0.00); il PORTAFOGLIO realizza -0.86
  _uscite in ordine di TEMPO: e' la buca vera, quella che il gate non vede perche' valida una coppia alla volta._

- escursione favorevole (mfe_r, 189 trade): mediana **0.87R** · ≥1R: 44% · ≥1.5R: 16% · ≥3R: 2% · ≥5R: 1%
  _quanto lontano arriva il prezzo, in unità di R: dice se la scala di TP è raggiungibile. Dettaglio: `python -m scripts.mfe_report`_

## Deriva paper vs gate
_il gate promette sulla storia, il paper misura il presente. `drift` = promessa contraddetta -> size/leva frenate subito e fallimento al gate alla prossima passata._

- **globale**: drift · 182 trade · PF vissuto 0.698 vs 2.024 atteso · mfe mediana 0.85R

- **freno globale attivo**: size x0.5 e leva x0.71 (radice) su OGNI trade finche' il PF a 30 giorni resta sotto 0.6 x atteso (motivo: PF 0.70 vs 2.02 atteso · mfe mediana 0.85R < primo TP 1.50R)

| Coppia | Verdetto | Trade | PF vissuto/atteso | Motivo |
|---|---|---|---|---|
| USELESSUSDT|gen_2031005e | watch | 7 | 0.304 / 1.54 | PF 0.30 vs 1.54 atteso · mfe mediana 0.80R < primo TP 2.00R |
| PROMUSDT|gen_cd5c842f | watch | 7 | 4.156 / 1.628 | mfe mediana 1.10R < primo TP 2.00R |
| SPXUSDT|gen_ba3a671f | watch | 6 | 0.052 / 1.644 | PF 0.05 vs 1.64 atteso · mfe mediana 0.33R < primo TP 0.75R |
| DEXEUSDT|gen_fa304106 | watch | 5 | 0.0 / 2.06 | PF 0.00 vs 2.06 atteso · mfe mediana 0.52R < primo TP 1.50R |
| QUSDT|gen_18c839a0 | watch | 4 | 0.585 / 3.23 | PF 0.59 vs 3.23 atteso |
| SYRUPUSDT|gen_4c6df481 | watch | 4 | 1.256 / 1.445 | mfe mediana 1.30R < primo TP 2.00R |
| AVAAIUSDT|gen_e50a9211 | watch | 4 | 0.345 / 1.525 | PF 0.35 vs 1.52 atteso |
| GPSUSDT|gen_bf1e00d4 | watch | 4 | 4.936 / 1.59 | mfe mediana 0.90R < primo TP 1.50R |
| DEXEUSDT|gen_b31d8b93 | watch | 4 | 0.149 / 1.881 | PF 0.15 vs 1.88 atteso · mfe mediana 1.23R < primo TP 2.00R |
| STXUSDT|gen_b9bf5d01 | watch | 3 | 0.208 / 1.54 | PF 0.21 vs 1.54 atteso · mfe mediana 0.74R < primo TP 2.00R |
| VETUSDT|gen_6d06dca0 | watch | 3 | 0.386 / 1.631 | PF 0.39 vs 1.63 atteso |
| JTOUSDT|gen_f238d283 | watch | 3 | 0.653 / 1.64 | PF 0.65 vs 1.64 atteso |
| SYRUPUSDT|gen_af734c68 | watch | 3 | 0.407 / 1.493 | PF 0.41 vs 1.49 atteso · mfe mediana 0.94R < primo TP 1.50R |
| ORCAUSDT|gen_6d06dca0 | watch | 3 | 0.0 / 1.967 | PF 0.00 vs 1.97 atteso · mfe mediana 0.49R < primo TP 1.50R |
| GALAUSDT|gen_b9aa9989 | watch | 2 | 0.415 / 1.922 | PF 0.41 vs 1.92 atteso |
| MUBARAKUSDT|gen_1f7ead60 | watch | 2 | 0.0 / 2.776 | PF 0.00 vs 2.78 atteso · mfe mediana 0.21R < primo TP 2.00R |
| MUBARAKUSDT|gen_49c2f657 | watch | 2 | 0.532 / 2.438 | PF 0.53 vs 2.44 atteso |
| SPXUSDT|gen_725cb5f4 | watch | 2 | 0.136 / 1.708 | PF 0.14 vs 1.71 atteso · mfe mediana 0.52R < primo TP 0.75R |
| USELESSUSDT|gen_194e2514 | watch | 1 | 0.0 / 2.036 | PF 0.00 vs 2.04 atteso · mfe mediana 0.67R < primo TP 2.00R |
| SYRUPUSDT|gen_b7d57ce7 | watch | 1 | 0.0 / 1.527 | PF 0.00 vs 1.53 atteso · mfe mediana 0.43R < primo TP 2.00R |

- serie di perdite (freno SPENTO dal 24 set, solo misura): **gen_fa304106** (6 perdite di fila)

## Calibrazione della confidenza
_la confidenza del segnale modula size e leva: qui si verifica che predica davvero l'esito, invece di darlo per scontato._

- verdetto: **costante** · 182 trade · correlazione None · influenza applicata **x1.0**
- tutte le strategie generate escono a confidenza 60: la calibrazione non puo' misurare nulla finche' la confidenza non varia (182 trade, confidenza 60-60)

| Fascia di confidenza | Trade | Win rate | Esito medio |
|---|---|---|---|
| 60.0–60.0 | 60 | 70% | +0.17% |
| 60.0–60.0 | 60 | 55% | -0.21% |
| 60.0–60.0 | 62 | 40% | -1.33% |

_se l'esito medio CRESCE dalla fascia bassa all'alta, la confidenza ordina correttamente i trade._
```
