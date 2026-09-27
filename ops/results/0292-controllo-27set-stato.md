# 0292-controllo-27set-stato.req

_eseguito: 2026-09-27 06:12 UTC_

**richiesta:** `stato`
**eseguito:** `.venv/bin/python -m scripts.state_snapshot --no-write`
**esito:** codice 0 in 3.7s

```
[firebase] connesso (Firestore + RTDB)
# Stato sistema (snapshot)
_Generato: 2026-09-27 06:12 UTC_

## Bot
- stato: **running** (🟢 online)
- regime: sideways
- DRY_RUN: True
- equity: **$927.56**
- ultimo heartbeat: 2026-09-27 06:12 UTC
- stream prezzi: 🟢 attivo

## Ultima decisione
- esito: **⚪ FLAT** (2026-09-27 06:02 UTC)
- motivo: parita' backtest: 1 segnali validi aperti
- asset valutati: 68 · segnali: 1 · miglior segnale USELESSUSDT gen_c0fd1d91 (conf. 60.0/soglia 30)

## Posizioni aperte
- DEXEUSDT: short qty=95.9790753853185 @ 1.926 uPnL=-0.6725573218544764 · rischio 0.17% · leva 2.0x
- SPXUSDT: short qty=205.7129544450182 @ 0.4509 uPnL=0.12667035836383192 · rischio 0.17% · leva 1.0x
- USELESSUSDT: short qty=323.3943628730866 @ 0.28682 uPnL=-0.8855246570544522 · rischio 0.25% · leva 1.0x
- XPLUSDT: short qty=552.0809442934599 @ 0.11765 uPnL=3.0871812105253253 · rischio 0.33% · leva 1.0x
- **rischio aperto totale: 0.92%** dell'equity su 4 posizioni

## GATE 1 — Validazione strategie
- stato: **✅ SUPERATO — pronti per il paper trading**
- copertura universo: **68/200 crypto (34%)** · obiettivo ≥ 35%
- coppie validate (>= 3 pass OOS): **212**
- universo scansionato: 0GUSDT, 1000BONKUSDT, 1000FLOKIUSDT, 1000PEPEUSDT, 1000SATSUSDT, 1000SHIBUSDT, 2ZUSDT, 4USDT, AAVEUSDT, ACEUSDT, ADAUSDT, AEROUSDT, AKEUSDT, ALGOUSDT, ALLOUSDT, APTUSDT, ARBUSDT, ARKUSDT, ARUSDT, ASTERUSDT, ATOMUSDT, AVAXUSDT, AVNTUSDT, AXSUSDT, BABYUSDT, BASEDUSDT, BBUSDT, BCHUSDT, BEATUSDT, BILLUSDT, BIOUSDT, BNBUSDT, BOMEUSDT, BROCCOLI714USDT, BRUSDT, BTCUSDT, BTWUSDT, BULLAUSDT, C98USDT, CAKEUSDT, CCUSDT, CFGUSDT, CFXUSDT, CHIPUSDT, CHZUSDT, CLANKERUSDT, CLOUSDT, COMPUSDT, COTIUSDT, COWUSDT, CRVUSDT, DASHUSDT, DOGEUSDT, DOGSUSDT, DOTUSDT, DYDXUSDT, EDGEUSDT, EGLDUSDT, EIGENUSDT, ENAUSDT, ENJUSDT, ENSUSDT, EPICUSDT, ESPUSDT, ETCUSDT, ETHFIUSDT, ETHUSDT, FARTCOINUSDT, FETUSDT, FILUSDT, FLOCKUSDT, FLOWUSDT, FORMUSDT, GALAUSDT, GIGGLEUSDT, GRAMUSDT, GRASSUSDT, GWEIUSDT, HBARUSDT, HEIUSDT, HUMAUSDT, HUSDT, HYPEUSDT, ICPUSDT, INJUSDT, INUSDT, IOSTUSDT, IOTAUSDT, IOUSDT, JELLYJELLYUSDT, JTOUSDT, JUPUSDT, KAITOUSDT, KASUSDT, KITEUSDT, KMNOUSDT, LABUSDT, LAUSDT, LDOUSDT, LINKUSDT, LITUSDT, LPTUSDT, LSKUSDT, LTCUSDT, LYNUSDT, MAGMAUSDT, MARSCOINUSDT, METUSDT, MINAUSDT, MONUSDT, MORPHOUSDT, MOVRUSDT, MUBARAKUSDT, NEARUSDT, NEIROUSDT, NILUSDT, NOMUSDT, ONDOUSDT, ONEUSDT, OPGUSDT, OPUSDT, ORDIUSDT, PAXGUSDT, PENDLEUSDT, PENGUUSDT, PHAUSDT, PLUMEUSDT, POLUSDT, PONSUSDT, PROMUSDT, PTBUSDT, PUMPUSDT, PYTHUSDT, QNTUSDT, QUSDT, RAREUSDT, RAYSOLUSDT, RENDERUSDT, RESOLVUSDT, REUSDT, REZUSDT, RIVERUSDT, RUNEUSDT, SAGAUSDT, SANDUSDT, SEIUSDT, SKYUSDT, SOLUSDT, SOONUSDT, SPELLUSDT, SPKUSDT, SPXUSDT, STEEMUSDT, STRKUSDT, STXUSDT, SUIUSDT, SUPERUSDT, SUSDT, SYNUSDT, SYRUPUSDT, TAIKOUSDT, TAKEUSDT, TAOUSDT, TIAUSDT, TLMUSDT, TNSRUSDT, TRIAUSDT, TRUMPUSDT, TRUSTUSDT, TRXUSDT, TUSDT, TUTUSDT, UAIUSDT, UNIUSDT, USELESSUSDT, USUSDT, VELODROMEUSDT, VETUSDT, VIRTUALUSDT, VTHOUSDT, VVVUSDT, WAXPUSDT, WIFUSDT, WLDUSDT, WLFIUSDT, WUSDT, XAIUSDT, XAUTUSDT, XLMUSDT, XMRUSDT, XPLUSDT, XRPUSDT, ZAMAUSDT, ZECUSDT, ZENUSDT, ZETAUSDT, ZKUSDT, ZROUSDT, 牛来USDT, 龙虾USDT
- aggiornato: 2026-09-27 06:09 UTC

### Salute del registro

- composizione: **1344 base** · **1371 generate** (di cui 1371 con almeno una conferma)
- occupazione: 2715/3000 — ok

### Strategie VALIDATE (operate dal bot)
| Coin | Strategia | Passes | PF | PnL OOS | Parametri |
|---|---|---|---|---|---|
| HEIUSDT | gen_e6ddc613 | 4 | 2.441 | 212% | scale_r_mults=[2.0, 4.0, 6.0] |
| JASMYUSDT | gen_b2f350ff | 4 | 1.603 | 137% | scale_r_mults=[2.0, 4.0, 6.0] |
| VETUSDT | gen_6d06dca0 | 4 | 1.631 | 126% | scale_r_mults=[2.0, 4.0, 6.0] |
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
| ORCAUSDT | gen_5b847426 | 4 | 1.859 | 96% | scale_r_mults=[2.0, 4.0, 6.0] |
| DEXEUSDT | gen_fa304106 | 4 | 2.06 | 95% | scale_r_mults=[1.5, 3.0, 5.0] |
| SPXUSDT | gen_725cb5f4 | 4 | 1.708 | 92% | scale_r_mults=[0.75, 1.5, 3.0] |
| ORCAUSDT | gen_7b4a474b | 4 | 2.148 | 89% | scale_r_mults=[1.5, 3.0, 5.0] |
| ORCAUSDT | gen_bbe21d3f | 4 | 1.952 | 87% | scale_r_mults=[1.5, 3.0, 5.0] |
| DEXEUSDT | gen_b31d8b93 | 4 | 1.881 | 87% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True |
| STXUSDT | gen_14e1775b | 4 | 1.74 | 87% | scale_r_mults=[2.0, 4.0, 6.0] |
| STXUSDT | gen_68ebd3b9 | 4 | 1.748 | 86% | scale_r_mults=[2.0, 4.0, 6.0] |
| SPXUSDT | gen_ba3a671f | 4 | 1.644 | 84% | scale_r_mults=[0.75, 1.5, 3.0] |
| ORCAUSDT | gen_9a383fff | 4 | 1.978 | 82% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True |
| DOTUSDT | gen_919c110c | 4 | 1.462 | 82% | scale_r_mults=[2.0, 4.0, 6.0] |
| SEIUSDT | gen_4f890271 | 4 | 1.851 | 82% | scale_r_mults=[2.0, 4.0, 6.0] |
| ORCAUSDT | gen_e6ddc613 | 4 | 1.94 | 81% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True |
| USELESSUSDT | gen_2031005e | 4 | 1.54 | 72% | scale_r_mults=[2.0, 4.0, 6.0] |
| ORCAUSDT | gen_6d06dca0 | 4 | 1.967 | 70% | scale_r_mults=[1.5, 3.0, 5.0] |
| SYRUPUSDT | gen_4c6df481 | 3 | 1.401 | 69% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.75 |
| MUBARAKUSDT | gen_ff3e4154 | 4 | 1.864 | 68% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.35 |
| SKYAIUSDT | gen_6cf80ae6 | 4 | 2.518 | 65% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True |
| SKYAIUSDT | gen_c202787e | 3 | 2.518 | 65% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True |
| GPSUSDT | gen_871647b8 | 3 | 1.511 | 65% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.5 |
| SPXUSDT | gen_d53c153b | 4 | 1.824 | 58% | scale_r_mults=[1.5, 3.0, 5.0] |
| SKYAIUSDT | gen_6191df86 | 3 | 2.889 | 58% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| QUSDT | gen_bf2be656 | 3 | 3.527 | 57% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.75 |
| BICOUSDT | gen_f238d283 | 4 | 1.484 | 57% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True |
| JUPUSDT | gen_bb762669 | 3 | 1.582 | 56% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.35 |
| NEIROUSDT | gen_f3124a14 | 4 | 1.572 | 56% | scale_r_mults=[1.5, 3.0, 5.0] |
| EGLDUSDT | gen_36b0e335 | 4 | 1.455 | 56% | scale_r_mults=[1.5, 3.0, 5.0] |
| HUMAUSDT | gen_da39a23a | 3 | 2.308 | 54% | scale_r_mults=[1.0, 1.5, 2.5], sl_to_breakeven=True, profit_lock_keep=0.75 |
| QUSDT | gen_0ada82e9 | 3 | 2.699 | 54% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.75 |
| QUSDT | gen_7f8adcde | 3 | 2.699 | 54% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.75 |
| QUSDT | gen_18c839a0 | 4 | 3.143 | 53% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.75 |
| QUSDT | gen_a12226f7 | 3 | 3.143 | 53% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.75 |
| NEIROUSDT | gen_d53c153b | 4 | 1.808 | 49% | scale_r_mults=[1.0, 2.0, 3.0] |
| SAHARAUSDT | gen_6b94025f | 4 | 2.213 | 48% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.35 |
| JTOUSDT | gen_f238d283 | 4 | 1.64 | 47% | scale_r_mults=[1.0, 2.0, 3.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| SKYAIUSDT | gen_f68b811d | 3 | 2.288 | 46% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.35 |
| SKYAIUSDT | gen_98837ec2 | 4 | 2.214 | 44% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True |
| SCRUSDT | gen_63712f8e | 3 | 2.284 | 42% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.75 |
| HEMIUSDT | gen_108c996b | 4 | 1.986 | 40% | scale_r_mults=[2.0, 4.0, 6.0] |
| HEMIUSDT | gen_93131ef1 | 4 | 1.986 | 40% | scale_r_mults=[2.0, 4.0, 6.0] |
| PROMUSDT | gen_452d4511 | 4 | 1.888 | 39% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True |
| MUBARAKUSDT | gen_49c2f657 | 3 | 2.261 | 38% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.75 |
| JTOUSDT | gen_35632db9 | 3 | 1.49 | 38% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.35 |
| SAHARAUSDT | gen_60d64cfd | 3 | 2.731 | 38% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.35 |
| TRUMPUSDT | gen_0e000630 | 4 | 1.831 | 36% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.75 |
| OPENUSDT | gen_2bb283ca | 3 | 2.382 | 34% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.35 |
| PLUMEUSDT | gen_e94b056d | 3 | 2.219 | 34% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.75 |
| MUBARAKUSDT | gen_2053cba6 | 4 | 1.863 | 32% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.75 |
| SKYAIUSDT | gen_eb2ece0c | 4 | 2.514 | 27% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.35 |
| TRUMPUSDT | gen_108c996b | 4 | 1.732 | 24% | scale_r_mults=[2.0, 4.0, 6.0] |
| TRUMPUSDT | gen_93131ef1 | 4 | 1.732 | 24% | scale_r_mults=[2.0, 4.0, 6.0] |
| FLOCKUSDT | gen_f3124a14 | 3 | 1.996 | 24% | scale_r_mults=[1.0, 2.0, 3.0], sl_to_breakeven=True, profit_lock_keep=0.75 |
| SAHARAUSDT | gen_95aff747 | 3 | 1.608 | 23% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.5 |
| MU

[... 8477 caratteri omessi (testa e coda conservate) ...]

, 6.0] |
| STXUSDT | gen_acfd527a | 3 | None | 0% | scale_r_mults=[2.0, 4.0, 6.0] |
| STXUSDT | gen_c7a02fce | 3 | None | 0% | scale_r_mults=[2.0, 4.0, 6.0] |
| STXUSDT | gen_d606fde3 | 3 | None | 0% | scale_r_mults=[1.5, 3.0, 5.0] |
| SUIUSDT | gen_490a90e5 | 3 | None | 0% | scale_r_mults=[1.0, 2.0, 3.0] |
| SUIUSDT | gen_8c9b332f | 3 | None | 0% | scale_r_mults=[1.0, 2.0, 3.0] |
| SUPERUSDT | gen_0eb999b7 | 3 | None | 0% | scale_r_mults=[1.5, 3.0, 5.0] |
| SYRUPUSDT | gen_98d56766 | 3 | None | 0% | scale_r_mults=[1.5, 3.0, 5.0] |
| SYRUPUSDT | gen_b7d57ce7 | 3 | 1.527 | 0% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True |
| SYRUPUSDT | gen_f3b97917 | 3 | None | 0% | scale_r_mults=[1.0, 1.5, 2.5] |
| TAUSDT | gen_b028553e | 3 | None | 0% | scale_r_mults=[1.5, 3.0, 5.0] |
| TAUSDT | gen_bf2be656 | 3 | None | 0% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True |
| THEUSDT | gen_658b2edb | 3 | None | 0% | scale_r_mults=[2.0, 4.0, 6.0] |
| TRUMPUSDT | gen_452d4511 | 3 | None | 0% | scale_r_mults=[2.0, 4.0, 6.0] |
| TRUMPUSDT | gen_8c450b67 | 3 | None | 0% | scale_r_mults=[2.0, 4.0, 6.0] |
| TRUMPUSDT | gen_f156ca1b | 3 | None | 0% | scale_r_mults=[2.0, 4.0, 6.0] |
| TSTUSDT | gen_a640dfa5 | 3 | None | 0% | scale_r_mults=[2.0, 4.0, 6.0] |
| USELESSUSDT | gen_1623b4cb | 3 | None | 0% | scale_r_mults=[1.5, 3.0, 5.0] |
| USELESSUSDT | gen_68a8a9c7 | 3 | None | 0% | scale_r_mults=[2.0, 4.0, 6.0] |
| USELESSUSDT | gen_acea368d | 3 | None | 0% | scale_r_mults=[2.0, 4.0, 6.0] |
| USELESSUSDT | gen_c0fd1d91 | 3 | None | 0% | scale_r_mults=[1.5, 3.0, 5.0] |
| USELESSUSDT | gen_fa5179ea | 3 | None | 0% | scale_r_mults=[2.0, 4.0, 6.0] |
| VETUSDT | gen_b2f350ff | 3 | None | 0% | scale_r_mults=[2.0, 4.0, 6.0] |
| VETUSDT | gen_b9c251a1 | 3 | None | 0% | scale_r_mults=[1.0, 1.5, 2.5], sl_to_breakeven=True |
| VETUSDT | gen_f3124a14 | 3 | None | 0% | scale_r_mults=[1.5, 3.0, 5.0] |
| VETUSDT | gen_fb3d971f | 3 | None | 0% | scale_r_mults=[2.0, 4.0, 6.0] |
| VETUSDT | gen_fca11c08 | 3 | None | 0% | scale_r_mults=[1.5, 3.0, 5.0] |
| WALUSDT | gen_2b41880d | 3 | None | 0% | scale_r_mults=[2.0, 4.0, 6.0] |
| WALUSDT | gen_cee79cdd | 3 | None | 0% | scale_r_mults=[2.0, 4.0, 6.0] |
| WALUSDT | gen_f238d283 | 3 | None | 0% | scale_r_mults=[2.0, 4.0, 6.0] |
| XMRUSDT | gen_35632db9 | 3 | None | 0% | scale_r_mults=[1.5, 3.0, 5.0] |
| XPLUSDT | gen_0a991220 | 3 | None | 0% | scale_r_mults=[1.5, 3.0, 5.0] |
| XPLUSDT | gen_2f405402 | 3 | None | 0% | scale_r_mults=[1.5, 3.0, 5.0] |
| XPLUSDT | gen_a220b439 | 3 | None | 0% | scale_r_mults=[1.5, 3.0, 5.0] |
| XPLUSDT | gen_b437a671 | 3 | None | 0% | scale_r_mults=[2.0, 4.0, 6.0] |
| XPLUSDT | gen_d32ec7de | 3 | None | 0% | scale_r_mults=[2.0, 4.0, 6.0] |
| XPLUSDT | gen_e59ad90b | 3 | None | 0% | scale_r_mults=[1.5, 3.0, 5.0] |
| XRPUSDT | gen_a22411e3 | 3 | None | 0% | scale_r_mults=[1.5, 3.0, 5.0] |
| ZKUSDT | gen_c61d9322 | 3 | None | 0% | scale_r_mults=[2.0, 4.0, 6.0] |
| ZORAUSDT | gen_2c248ee9 | 3 | None | 0% | scale_r_mults=[1.5, 3.0, 5.0] |

## Ultimo run di ottimizzazione
_aggiornato: 2026-09-21 12:43 UTC · 1320 coppie valutate, 0 passate in questo run_

_Nessuna coppia ha passato in questo run._

## Dove muoiono le candidate (autopsia del GATE 1)

**strategie base** — 1320 valutazioni, 0 passate (0.00%) · 2026-09-21 12:43 UTC

| Criterio che ferma | Casi | Quota |
|---|---|---|
| holdout | 1 | 0.1% |
| pf_ex_top | 3 | 0.2% |
| trades | 6 | 0.5% |
| consistency | 17 | 1.3% |
| recovery | 64 | 4.8% |
| total_return | 1207 | 91.4% |
| regime | 22 | 1.7% |

- quasi-passaggi (un solo criterio, di poco): **1** — sono i semi delle mutazioni del run successivo

**strategie generate** — 1577 valutazioni, 5 passate (0.32%) · 2026-09-27 06:09 UTC

| Criterio che ferma | Casi | Quota |
|---|---|---|
| holdout | 8 | 0.5% |
| consistency | 65 | 4.1% |
| pf_ex_top | 39 | 2.5% |
| total_return | 976 | 62.1% |
| recovery | 232 | 14.8% |
| trades | 145 | 9.2% |
| regime | 107 | 6.8% |

- quasi-passaggi (un solo criterio, di poco): **21** — sono i semi delle mutazioni del run successivo

## Supervisore (taratura automatica)

- ultimo giro: 2026-09-27 06:02 UTC · coppie validate: **214** · GATE 1 pronto: True
- tasso di passaggio misurato: **0.247%**

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
- totale: **111** · vinti: 53 (48%) · PnL realizzato: **-73.79**
- confronto col mercato: noi -7.38% vs BTC buy&hold +11.64% nello stesso periodo → **sotto** il mercato

- costi: **20.58 USDT** su 111 trade (0.18/trade) _(stimati dal modello del gate, non misurati dai fill)_
  - commissioni 11.78 · spread 8.80 · funding -0.00
  - lordo -53.21 → netto -73.79 · **break-even 2.22%** dell'equity
  - piu' costose: DEXEUSDT 2.29 · SPXUSDT 1.39 · QUSDT 1.25 · SYRUPUSDT 1.23 · ORCAUSDT 1.21
  - ⚠️ Costi operativi elevati: servono 2.22% solo per pareggiare (soglia 1.5%)

| Uscita | Trade | % | PnL |
|---|---|---|---|
| Stop loss (prima di qualsiasi TP) | 58 | 52% | -191.35 |
| Trailing stop | 40 | 36% | +55.89 |
| Scale-out (>=1 TP incassato, residuo a BE) | 10 | 9% | +27.41 |
| Take profit (fino all'ultimo gradino) | 2 | 2% | +20.78 |
| Time exit (orizzonte scaduto) | 1 | 1% | +13.48 |

- gradini raggiunti (su 111 trade): 0 TP: 98 (88%) · 1 TP: 10 (9%) · 2 TP: 1 (1%) · 3 TP: 2 (2%)

- **drawdown di portafoglio: 78.97 USDT** (ritorno -73.79 · recovery -0.93) · max 9 posizioni aperte insieme
  - il gate prometteva recovery ≥ 2.0 per ogni coppia (peggiore in registro: 0.00); il PORTAFOGLIO realizza -0.93
  _uscite in ordine di TEMPO: e' la buca vera, quella che il gate non vede perche' valida una coppia alla volta._

- escursione favorevole (mfe_r, 111 trade): mediana **0.82R** · ≥1R: 37% · ≥1.5R: 16% · ≥3R: 4% · ≥5R: 1%
  _quanto lontano arriva il prezzo, in unità di R: dice se la scala di TP è raggiungibile. Dettaglio: `python -m scripts.mfe_report`_

## Deriva paper vs gate
_il gate promette sulla storia, il paper misura il presente. `drift` = promessa contraddetta -> size/leva frenate subito e fallimento al gate alla prossima passata._

- **globale**: drift · 110 trade · PF vissuto 0.616 vs 2.098 atteso · mfe mediana 0.84R

- **freno globale attivo**: size x0.5 e leva x0.71 (radice) su OGNI trade finche' il PF a 30 giorni resta sotto 0.6 x atteso (motivo: PF 0.62 vs 2.10 atteso · mfe mediana 0.84R < primo TP 1.50R)

| Coppia | Verdetto | Trade | PF vissuto/atteso | Motivo |
|---|---|---|---|---|
| SPXUSDT|gen_ba3a671f | watch | 6 | 0.052 / 1.644 | PF 0.05 vs 1.64 atteso · mfe mediana 0.33R < primo TP 0.75R |
| USELESSUSDT|gen_2031005e | watch | 6 | 0.196 / 1.54 | PF 0.20 vs 1.54 atteso · mfe mediana 0.80R < primo TP 2.00R |
| DEXEUSDT|gen_fa304106 | watch | 5 | 0.0 / 2.06 | PF 0.00 vs 2.06 atteso · mfe mediana 0.52R < primo TP 1.50R |
| QUSDT|gen_18c839a0 | watch | 4 | 0.585 / 3.143 | PF 0.59 vs 3.14 atteso |
| GPSUSDT|gen_bf1e00d4 | watch | 4 | 4.936 / 1.59 | mfe mediana 0.90R < primo TP 1.50R |
| SYRUPUSDT|gen_af734c68 | watch | 3 | 0.407 / 1.493 | PF 0.41 vs 1.49 atteso · mfe mediana 0.94R < primo TP 1.50R |
| STXUSDT|gen_b9bf5d01 | watch | 3 | 0.208 / 1.54 | PF 0.21 vs 1.54 atteso · mfe mediana 0.74R < primo TP 2.00R |
| DEXEUSDT|gen_b31d8b93 | watch | 3 | 0.217 / 1.881 | PF 0.22 vs 1.88 atteso · mfe mediana 1.23R < primo TP 2.00R |
| JTOUSDT|gen_f238d283 | watch | 3 | 0.653 / 1.64 | PF 0.65 vs 1.64 atteso |
| VETUSDT|gen_6d06dca0 | watch | 3 | 0.386 / 1.631 | PF 0.39 vs 1.63 atteso |
| MUBARAKUSDT|gen_1f7ead60 | watch | 2 | 0.0 / 2.776 | PF 0.00 vs 2.78 atteso · mfe mediana 0.21R < primo TP 2.00R |
| ORCAUSDT|gen_6d06dca0 | watch | 2 | 0.0 / 1.967 | PF 0.00 vs 1.97 atteso · mfe mediana 1.05R < primo TP 1.50R |
| SEIUSDT|gen_4f890271 | watch | 1 | 99.0 / 1.851 | mfe mediana 1.09R < primo TP 2.00R |
| NEIROUSDT|gen_e132204b | watch | 1 | 0.0 / 1.284 | PF 0.00 vs 1.28 atteso · mfe mediana 0.62R < primo TP 1.50R |
| ZKUSDT|gen_98837ec2 | watch | 1 | 0.0 / 1.439 | PF 0.00 vs 1.44 atteso · mfe mediana 0.13R < primo TP 2.00R |
| HEIUSDT|gen_e6ddc613 | watch | 1 | 0.0 / 2.441 | PF 0.00 vs 2.44 atteso · mfe mediana 0.88R < primo TP 2.00R |
| STXUSDT|gen_14e1775b | watch | 1 | 99.0 / 1.74 | mfe mediana 1.15R < primo TP 2.00R |
| MUBARAKUSDT|gen_ff3e4154 | watch | 1 | 0.0 / 1.864 | PF 0.00 vs 1.86 atteso · mfe mediana 0.84R < primo TP 1.50R |
| SKYAIUSDT|gen_c61d9322 | watch | 1 | 99.0 / 2.069 | mfe mediana 1.13R < primo TP 2.00R |
| JUPUSDT|gen_bb762669 | watch | 1 | 99.0 / 1.582 | mfe mediana 0.79R < primo TP 1.50R |

- serie di perdite (freno SPENTO dal 24 set, solo misura): **gen_fa304106** (5 perdite di fila)

## Calibrazione della confidenza
_la confidenza del segnale modula size e leva: qui si verifica che predica davvero l'esito, invece di darlo per scontato._

- verdetto: **costante** · 110 trade · correlazione None · influenza applicata **x1.0**
- tutte le strategie generate escono a confidenza 60: la calibrazione non puo' misurare nulla finche' la confidenza non varia (110 trade, confidenza 60-60)

| Fascia di confidenza | Trade | Win rate | Esito medio |
|---|---|---|---|
| 60.0–60.0 | 36 | 61% | -0.05% |
| 60.0–60.0 | 36 | 47% | -0.96% |
| 60.0–60.0 | 38 | 37% | -1.43% |

_se l'esito medio CRESCE dalla fascia bassa all'alta, la confidenza ordina correttamente i trade._


--- stderr ---
/root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
  return query.where(field_path, op_string, value)
```
