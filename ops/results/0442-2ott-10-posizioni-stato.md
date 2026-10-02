# 0442-2ott-10-posizioni-stato.req

_eseguito: 2026-10-02 18:53 UTC_

**richiesta:** `stato`
**eseguito:** `.venv/bin/python -m scripts.state_snapshot --no-write`
**esito:** codice 0 in 3.8s

```
[firebase] connesso (Firestore + RTDB)
# Stato sistema (snapshot)
_Generato: 2026-10-02 18:53 UTC_

## Bot
- stato: **running** (🟢 online)
- regime: sideways
- DRY_RUN: True
- equity: **$924.87**
- ultimo heartbeat: 2026-10-02 18:52 UTC
- stream prezzi: 🟢 attivo

## Ultima decisione
- esito: **⚪ FLAT** (2026-10-02 18:47 UTC)
- motivo: parita' backtest: 13 segnali validi aperti
- asset valutati: 71 · segnali: 33 · miglior segnale PENGUUSDT gen_a32bee42 (conf. 60.0/soglia 30)

## Posizioni aperte
- ARCUSDT: long qty=834.0550968450942 @ 0.07009 uPnL=0.11355762109040643 · rischio 0.09% · leva 1.0x
- BMTUSDT: long qty=3959.168682086346 @ 0.01843 uPnL=0.10984011960133933 · rischio 0.13% · leva 1.0x
- DOTUSDT: long qty=44.31741525173759 @ 1.1518 uPnL=-0.2424106588687705 · rischio 0.13% · leva 1.0x
- GPSUSDT: long qty=9090.53324767289 @ 0.010174 uPnL=0.8416627514218795 · rischio 0.22% · leva 1.0x
- HOMEUSDT: long qty=8511.115342711922 @ 0.005624 uPnL=0.19574629896546708 · rischio 0.13% · leva 1.0x
- JUPUSDT: short qty=110.7622690613319 @ 0.3344 uPnL=2.8193400781532167 · rischio 0.18% · leva 1.0x
- PENGUUSDT: long qty=4200.8129756998 @ 0.008716 uPnL=0.21937488439803815 · rischio 0.13% · leva 1.0x
- SAHARAUSDT: long qty=10254.694008407141 @ 0.009019 uPnL=-0.08659980541327462 · rischio 0.12% · leva 1.0x
- UBUSDT: long qty=428.2412065160066 @ 0.13348 uPnL=-0.08127234034079232 · rischio 0.09% · leva 1.0x
- USELESSUSDT: long qty=126.84707889233678 @ 0.2249 uPnL=-0.07427332128418887 · rischio 0.13% · leva 1.0x
- XPINUSDT: long qty=112105.55789312001 @ 0.000825 uPnL=-0.2601306790161263 · rischio 0.21% · leva 1.0x
- **rischio aperto totale: 1.55%** dell'equity su 11 posizioni

## GATE 1 — Validazione strategie
- stato: **✅ SUPERATO — pronti per il paper trading**
- copertura universo: **71/200 crypto (36%)** · obiettivo ≥ 35%
- coppie validate (>= 3 pass OOS): **212**
- universo scansionato: 0GUSDT, 1000BONKUSDT, 1000FLOKIUSDT, 1000PEPEUSDT, 1000SHIBUSDT, 2ZUSDT, AAVEUSDT, ACEUSDT, ADAUSDT, AEROUSDT, AGTUSDT, AKEUSDT, ALGOUSDT, ALICEUSDT, ALLOUSDT, APEUSDT, APTUSDT, ARBUSDT, ARKUSDT, ARUSDT, ARXUSDT, ASTERUSDT, ATHUSDT, ATOMUSDT, AVAXUSDT, AXSUSDT, BANKUSDT, BATUSDT, BCHUSDT, BERAUSDT, BILLUSDT, BIOUSDT, BLUAIUSDT, BNBUSDT, BOMEUSDT, BRUSDT, BTCUSDT, BTWUSDT, CAKEUSDT, CAPUSDT, CCUSDT, CHIPUSDT, CHZUSDT, CKBUSDT, COTIUSDT, CRVUSDT, CTUSDT, CVXUSDT, CYSUSDT, DASHUSDT, DATAIPUSDT, DEXEUSDT, DOGEUSDT, DOTUSDT, DYDXUSDT, EGLDUSDT, EIGENUSDT, ENAUSDT, ENJUSDT, ENSUSDT, ESPORTSUSDT, ETCUSDT, ETHFIUSDT, ETHUSDT, FARTCOINUSDT, FETUSDT, FFUSDT, FIGHTUSDT, FILUSDT, FLOCKUSDT, GALAUSDT, GIGGLEUSDT, GMTUSDT, GRAMUSDT, GRASSUSDT, GRTUSDT, GTCUSDT, HBARUSDT, HEIUSDT, HUMAUSDT, HYPEUSDT, ICPUSDT, ILVUSDT, IMXUSDT, INJUSDT, IOTAUSDT, JASMYUSDT, JSTUSDT, JTOUSDT, JUPUSDT, KAITOUSDT, KASUSDT, KITEUSDT, LABUSDT, LAUSDT, LDOUSDT, LINKUSDT, LITUSDT, LSKUSDT, LTCUSDT, LYNUSDT, MAGICUSDT, MAGMAUSDT, MANAUSDT, MARSCOINUSDT, MEGAUSDT, METUSDT, MINAUSDT, MONUSDT, MORPHOUSDT, MOVEUSDT, MOVRUSDT, MUBARAKUSDT, NEARUSDT, NEIROUSDT, NEOUSDT, NIGHTUSDT, NILUSDT, NMRUSDT, NOMUSDT, ONDOUSDT, ONEUSDT, ONGUSDT, OPNUSDT, OPUSDT, ORDIUSDT, PAXGUSDT, PENDLEUSDT, PENGUUSDT, PEOPLEUSDT, PHAROSUSDT, PHAUSDT, PLUMEUSDT, POLUSDT, PONSUSDT, POWERUSDT, PROMUSDT, PUMPBTCUSDT, PUMPUSDT, PYTHUSDT, QNTUSDT, QUSDT, RAYSOLUSDT, RENDERUSDT, RESOLVUSDT, REUSDT, RIVERUSDT, RUNEUSDT, SAGAUSDT, SANDUSDT, SCRUSDT, SEIUSDT, SKYUSDT, SOLUSDT, SOONUSDT, SOPHUSDT, SPKUSDT, SPXUSDT, STRKUSDT, STXUSDT, SUIUSDT, SUPERUSDT, SYNUSDT, SYRUPUSDT, TAOUSDT, TIAUSDT, TRBUSDT, TRUMPUSDT, TRUTHUSDT, TRXUSDT, TUTUSDT, UAIUSDT, UNIUSDT, USDCUSDT, USELESSUSDT, USUSDT, VELVETUSDT, VETUSDT, VIRTUALUSDT, VTHOUSDT, VVVUSDT, WIFUSDT, WLDUSDT, WLFIUSDT, WUSDT, XAUTUSDT, XLMUSDT, XMRUSDT, XPLUSDT, XRPUSDT, YGGUSDT, ZAMAUSDT, ZECUSDT, ZENUSDT, ZETAUSDT, ZKUSDT, ZROUSDT, 币安人生USDT, 牛来USDT, 龙虾USDT
- aggiornato: 2026-10-02 18:17 UTC

### Salute del registro

- composizione: **1 base** · **1808 generate** (di cui 1468 con almeno una conferma)
- occupazione: 1809/3000 — ok

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
| PARTIUSDT | gen_871647b8 | 3 | 2.177 | 104% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.5 |
| GPSUSDT | gen_bf1e00d4 | 4 | 1.59 | 103% | scale_r_mults=[1.5, 3.0, 5.0] |
| STXUSDT | gen_b9bf5d01 | 4 | 1.54 | 103% | scale_r_mults=[2.0, 4.0, 6.0] |
| DOTUSDT | gen_d85b1f05 | 4 | 1.483 | 102% | scale_r_mults=[1.5, 3.0, 5.0] |
| PROMUSDT | gen_cd5c842f | 4 | 1.628 | 99% | scale_r_mults=[2.0, 4.0, 6.0] |
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
| ORCAUSDT | gen_9a383fff | 5 | 1.978 | 82% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True |
| DOTUSDT | gen_919c110c | 4 | 1.462 | 82% | scale_r_mults=[2.0, 4.0, 6.0] |
| SEIUSDT | gen_4f890271 | 4 | 1.851 | 82% | scale_r_mults=[2.0, 4.0, 6.0] |
| ORCAUSDT | gen_e6ddc613 | 5 | 1.94 | 81% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True |
| SYRUPUSDT | gen_4c6df481 | 3 | 1.453 | 78% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.75 |
| QUSDT | gen_3ee1484b | 3 | 2.764 | 77% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.75 |
| QUSDT | gen_e75ddbfd | 3 | 2.764 | 77% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.75 |
| XPINUSDT | gen_c60cc1b9 | 3 | 3.134 | 72% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.35 |
| QUSDT | gen_da608d9f | 3 | 2.444 | 71% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.75 |
| TAUSDT | gen_543186c5 | 3 | 1.928 | 70% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| MUBARAKUSDT | gen_e933160c | 3 | 1.889 | 69% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.35 |
| MUBARAKUSDT | gen_ff3e4154 | 5 | 1.889 | 69% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.35 |
| IDUSDT | gen_6bc43e03 | 3 | 1.416 | 65% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| IDUSDT | gen_c5430258 | 3 | 1.416 | 65% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| IDUSDT | gen_dd9238bf | 3 | 1.416 | 65% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| SKYAIUSDT | gen_6cf80ae6 | 4 | 2.518 | 65% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True |
| SKYAIUSDT | gen_c202787e | 4 | 2.518 | 65% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True |
| GPSUSDT | gen_871647b8 | 4 | 1.517 | 64% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.5 |
| SKYAIUSDT | gen_6191df86 | 4 | 3.086 | 60% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| SCRUSDT | gen_bd8f158b | 3 | 1.915 | 59% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| NEIROUSDT | gen_413f1bd7 | 3 | 2.132 | 58% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.75 |
| QUSDT | gen_bf2be656 | 4 | 3.527 | 57% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.75 |
| JUPUSDT | gen_bb762669 | 4 | 1.564 | 56% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.35 |
| QUSDT | gen_18c839a0 | 4 | 3.213 | 55% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.75 |
| QUSDT | gen_b1ac5c24 | 3 | 3.213 | 55% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.75 |
| UBUSDT | gen_15837112 | 3 | 1.847 | 54% | scale_r_mults=[1.0, 2.0, 3.0], sl_to_breakeven=True, profit_lock_keep=0.35 |
| HUMAUSDT | gen_da39a23a | 4 | 2.24 | 53% | scale_r_mults=[1.0, 1.5, 2.5], sl_to_breakeven=True, profit_lock_keep=0.75 |
| MUBARAKUSDT | gen_f86f7370 | 3 | 2.889 | 51% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.35 |
| SAHARAUSDT | gen_6b94025f | 5 | 2.22 | 49% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.35 |
| STXUSDT | gen_a5b0e4de | 3 | 1.449 | 48% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.5 |
| PLUMEUSDT | gen_e94b056d | 3 | 2.67 | 47% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.35 |
| CATIUSDT | gen_b3e46005 | 3 | 2.706 | 46% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.5 |
| GALAUSDT | gen_b9aa9989 | 4 | 1.922 | 46% | scale_r_mults=[1.0, 1.25, 2.0], sl_to_breakeven=True, profit_lock_

[... 9940 caratteri omessi (testa e coda conservate) ...]

 |
| STEEMUSDT | gen_4508a416 | 3 | None | 0% | scale_r_mults=[2.0, 4.0, 6.0] |
| STEEMUSDT | gen_addf82da | 3 | None | 0% | scale_r_mults=[2.0, 4.0, 6.0] |
| STXUSDT | gen_c7a02fce | 3 | None | 0% | scale_r_mults=[2.0, 4.0, 6.0] |
| STXUSDT | gen_d606fde3 | 3 | None | 0% | scale_r_mults=[1.5, 3.0, 5.0] |
| SUIUSDT | gen_8c9b332f | 3 | None | 0% | scale_r_mults=[1.0, 2.0, 3.0] |
| SUPERUSDT | gen_0eb999b7 | 3 | None | 0% | scale_r_mults=[1.5, 3.0, 5.0] |
| SYRUPUSDT | gen_98d56766 | 3 | None | 0% | scale_r_mults=[1.5, 3.0, 5.0] |
| SYRUPUSDT | gen_f3b97917 | 3 | None | 0% | scale_r_mults=[1.0, 1.5, 2.5] |
| TAUSDT | gen_4e6e1ae0 | 3 | 2.15 | 0% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.75 |
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
| pf_ex_top | 3 | 0.2% |
| trades | 6 | 0.5% |
| holdout | 1 | 0.1% |
| total_return | 1207 | 91.4% |
| consistency | 17 | 1.3% |
| regime | 22 | 1.7% |
| recovery | 64 | 4.8% |

- quasi-passaggi (un solo criterio, di poco): **1** — sono i semi delle mutazioni del run successivo

**strategie generate** — 22632 valutazioni, 40 passate (0.18%) · 2026-10-02 17:09 UTC

| Criterio che ferma | Casi | Quota |
|---|---|---|
| pf_ex_top | 67 | 0.3% |
| trades | 802 | 3.5% |
| consistency | 203 | 0.9% |
| total_return | 19307 | 85.5% |
| holdout | 53 | 0.2% |
| regime | 1057 | 4.7% |
| recovery | 1103 | 4.9% |

- quasi-passaggi (un solo criterio, di poco): **27** — sono i semi delle mutazioni del run successivo

## Supervisore (taratura automatica)

- ultimo giro: 2026-10-02 18:04 UTC · coppie validate: **223** · GATE 1 pronto: True
- tasso di passaggio misurato: **0.167%**

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
- totale: **236** · vinti: 130 (55%) · PnL realizzato: **-77.36**
- confronto col mercato: noi -7.74% vs BTC buy&hold +11.15% nello stesso periodo → **sotto** il mercato

- costi: **34.74 USDT** su 236 trade (0.15/trade) _(stimati dal modello del gate, non misurati dai fill)_
  - commissioni 19.87 · spread 14.87 · funding -0.01
  - lordo -42.62 → netto -77.36 · **break-even 3.76%** dell'equity
  - piu' costose: DEXEUSDT 2.88 · SYRUPUSDT 2.26 · SPXUSDT 1.77 · ORCAUSDT 1.69 · QUSDT 1.62
  - ⚠️ Costi operativi elevati: servono 3.76% solo per pareggiare (soglia 1.5%)

| Uscita | Trade | % | PnL |
|---|---|---|---|
| Stop loss (prima di qualsiasi TP) | 105 | 44% | -268.24 |
| Trailing stop | 105 | 44% | +106.16 |
| Scale-out (>=1 TP incassato, residuo a BE) | 21 | 9% | +50.65 |
| Time exit (orizzonte scaduto) | 3 | 1% | +13.30 |
| Take profit (fino all'ultimo gradino) | 2 | 1% | +20.78 |

- gradini raggiunti (su 236 trade): 0 TP: 212 (90%) · 1 TP: 21 (9%) · 2 TP: 1 (0%) · 3 TP: 2 (1%)

- **drawdown di portafoglio: 80.54 USDT** (ritorno -77.36 · recovery -0.96) · max 9 posizioni aperte insieme
  - il gate prometteva recovery ≥ 2.0 per ogni coppia (peggiore in registro: 0.00); il PORTAFOGLIO realizza -0.96
  _uscite in ordine di TEMPO: e' la buca vera, quella che il gate non vede perche' valida una coppia alla volta._

- escursione favorevole (mfe_r, 236 trade): mediana **0.84R** · ≥1R: 40% · ≥1.5R: 15% · ≥3R: 2% · ≥5R: 0%
  _quanto lontano arriva il prezzo, in unità di R: dice se la scala di TP è raggiungibile. Dettaglio: `python -m scripts.mfe_report`_

## Deriva paper vs gate
_il gate promette sulla storia, il paper misura il presente. `drift` = promessa contraddetta -> size/leva frenate subito e fallimento al gate alla prossima passata._

- **globale**: drift · 228 trade · PF vissuto 0.7 vs 2.025 atteso · mfe mediana 0.82R

- **freno globale attivo**: size x0.5 e leva x0.71 (radice) su OGNI trade finche' il PF a 30 giorni resta sotto 0.6 x atteso (motivo: PF 0.70 vs 2.02 atteso · mfe mediana 0.82R < primo TP 1.50R)

| Coppia | Verdetto | Trade | PF vissuto/atteso | Motivo |
|---|---|---|---|---|
| USELESSUSDT|gen_2031005e | watch | 7 | 0.304 / 1.54 | PF 0.30 vs 1.54 atteso · mfe mediana 0.80R < primo TP 2.00R |
| SPXUSDT|gen_ba3a671f | watch | 7 | 0.047 / 1.644 | PF 0.05 vs 1.64 atteso · mfe mediana 0.33R < primo TP 0.75R |
| PROMUSDT|gen_cd5c842f | watch | 7 | 4.156 / 1.628 | mfe mediana 1.10R < primo TP 2.00R |
| SYRUPUSDT|gen_4c6df481 | watch | 6 | 2.903 / 1.453 | mfe mediana 1.27R < primo TP 2.00R |
| QUSDT|gen_18c839a0 | watch | 5 | 0.936 / 3.213 | PF 0.94 vs 3.21 atteso · mfe mediana 0.91R < primo TP 1.50R |
| DEXEUSDT|gen_fa304106 | watch | 5 | 0.0 / 2.06 | PF 0.00 vs 2.06 atteso · mfe mediana 0.52R < primo TP 1.50R |
| GPSUSDT|gen_bf1e00d4 | watch | 4 | 4.936 / 1.59 | mfe mediana 0.90R < primo TP 1.50R |
| DEXEUSDT|gen_b31d8b93 | watch | 4 | 0.149 / 1.881 | PF 0.15 vs 1.88 atteso · mfe mediana 1.23R < primo TP 2.00R |
| AVAAIUSDT|gen_e50a9211 | watch | 4 | 0.345 / 1.525 | PF 0.35 vs 1.52 atteso |
| ORCAUSDT|gen_6d06dca0 | watch | 3 | 0.0 / 1.967 | PF 0.00 vs 1.97 atteso · mfe mediana 0.49R < primo TP 1.50R |
| SYRUPUSDT|gen_af734c68 | watch | 3 | 0.407 / 1.493 | PF 0.41 vs 1.49 atteso · mfe mediana 0.94R < primo TP 1.50R |
| JTOUSDT|gen_f238d283 | watch | 3 | 0.653 / 1.64 | PF 0.65 vs 1.64 atteso |
| VETUSDT|gen_6d06dca0 | watch | 3 | 0.386 / 1.631 | PF 0.39 vs 1.63 atteso |
| STXUSDT|gen_b9bf5d01 | watch | 3 | 0.208 / 1.54 | PF 0.21 vs 1.54 atteso · mfe mediana 0.74R < primo TP 2.00R |
| SPXUSDT|gen_725cb5f4 | watch | 2 | 0.136 / 1.708 | PF 0.14 vs 1.71 atteso · mfe mediana 0.52R < primo TP 0.75R |
| MUBARAKUSDT|gen_1f7ead60 | watch | 2 | 0.0 / 2.776 | PF 0.00 vs 2.78 atteso · mfe mediana 0.21R < primo TP 2.00R |
| GALAUSDT|gen_b9aa9989 | watch | 2 | 0.415 / 1.922 | PF 0.41 vs 1.92 atteso |
| QUSDT|gen_85fadf54 | watch | 2 | 0.0 / 2.482 | PF 0.00 vs 2.48 atteso · mfe mediana 0.38R < primo TP 1.50R |
| UBUSDT|gen_f3661202 | watch | 2 | 0.546 / 1.858 | PF 0.55 vs 1.86 atteso · mfe mediana 1.16R < primo TP 2.00R |
| MUBARAKUSDT|gen_49c2f657 | watch | 2 | 0.532 / 2.261 | PF 0.53 vs 2.26 atteso |

- serie di perdite (freno SPENTO dal 24 set, solo misura): **gen_fa304106** (7 perdite di fila)

## Calibrazione della confidenza
_la confidenza del segnale modula size e leva: qui si verifica che predica davvero l'esito, invece di darlo per scontato._

- verdetto: **costante** · 228 trade · correlazione None · influenza applicata **x1.0**
- tutte le strategie generate escono a confidenza 60: la calibrazione non puo' misurare nulla finche' la confidenza non varia (228 trade, confidenza 60-60)

| Fascia di confidenza | Trade | Win rate | Esito medio |
|---|---|---|---|
| 60.0–60.0 | 76 | 55% | -0.33% |
| 60.0–60.0 | 76 | 63% | -0.02% |
| 60.0–60.0 | 76 | 43% | -1.13% |

_se l'esito medio CRESCE dalla fascia bassa all'alta, la confidenza ordina correttamente i trade._
```
