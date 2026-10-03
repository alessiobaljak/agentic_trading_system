# 0446-3ott-mattina-stato.req

_eseguito: 2026-10-03 06:04 UTC_

**richiesta:** `stato`
**eseguito:** `.venv/bin/python -m scripts.state_snapshot --no-write`
**esito:** codice 0 in 3.6s

```
[firebase] connesso (Firestore + RTDB)
# Stato sistema (snapshot)
_Generato: 2026-10-03 06:04 UTC_

## Bot
- stato: **running** (🟢 online)
- regime: sideways
- DRY_RUN: True
- equity: **$929.04**
- ultimo heartbeat: 2026-10-03 06:04 UTC
- stream prezzi: 🟢 attivo

## Ultima decisione
- esito: **⚪ FLAT** (2026-10-03 06:02 UTC)
- motivo: nessun segnale valido sopra soglia
- asset valutati: 71 · segnali: 0

## Posizioni aperte
- BANKUSDT: long qty=3188.3130897620417 @ 0.02913 uPnL=0.58689056529616 · rischio 0.08% · leva 1.0x
- BMTUSDT: long qty=2771.418077460442 @ 0.01843 uPnL=1.6762770309164174 · rischio 0.13% · leva 1.0x
- DOTUSDT: long qty=44.31741525173759 @ 1.1518 uPnL=0.018984202845325468 · rischio 0.13% · leva 1.0x
- JUPUSDT: short qty=110.7622690613319 @ 0.3344 uPnL=2.111741717846569 · rischio 0.18% · leva 1.0x
- QUSDT: long qty=1262.4604914669678 @ 0.021996 uPnL=-0.1634343876418107 · rischio 0.13% · leva 1.0x
- **rischio aperto totale: 0.65%** dell'equity su 5 posizioni

## GATE 1 — Validazione strategie
- stato: **✅ SUPERATO — pronti per il paper trading**
- copertura universo: **72/200 crypto (36%)** · obiettivo ≥ 35%
- coppie validate (>= 3 pass OOS): **216**
- universo scansionato: 0GUSDT, 1000BONKUSDT, 1000FLOKIUSDT, 1000PEPEUSDT, 1000SHIBUSDT, 2ZUSDT, 4USDT, AAVEUSDT, ACEUSDT, ADAUSDT, AEROUSDT, AGTUSDT, AKEUSDT, ALGOUSDT, ALICEUSDT, ALLOUSDT, APEUSDT, APTUSDT, ARBUSDT, ARKUSDT, ARUSDT, ARXUSDT, ASTERUSDT, ATHUSDT, ATOMUSDT, AVAXUSDT, AXSUSDT, BANKUSDT, BATUSDT, BCHUSDT, BEATUSDT, BERAUSDT, BILLUSDT, BIOUSDT, BNBUSDT, BOMEUSDT, BRUSDT, BTCUSDT, BTWUSDT, CAKEUSDT, CAPUSDT, CCUSDT, CHIPUSDT, CHZUSDT, COMPUSDT, COTIUSDT, CRVUSDT, CTUSDT, CVXUSDT, DASHUSDT, DATAIPUSDT, DEXEUSDT, DOGEUSDT, DOTUSDT, DYDXUSDT, EGLDUSDT, EIGENUSDT, ENAUSDT, ENJUSDT, ENSUSDT, ESPORTSUSDT, ETCUSDT, ETHFIUSDT, ETHUSDT, EVAAUSDT, FARTCOINUSDT, FETUSDT, FFUSDT, FILUSDT, FLOCKUSDT, FORMUSDT, GALAUSDT, GIGGLEUSDT, GMTUSDT, GRAMUSDT, GRASSUSDT, GRTUSDT, GTCUSDT, GUSDT, HBARUSDT, HEMIUSDT, HUMAUSDT, HYPEUSDT, ICPUSDT, ILVUSDT, IMXUSDT, INITUSDT, INJUSDT, JASMYUSDT, JSTUSDT, JTOUSDT, JUPUSDT, KAITOUSDT, KASUSDT, KITEUSDT, LABUSDT, LDOUSDT, LINKUSDT, LITUSDT, LPTUSDT, LSKUSDT, LTCUSDT, LYNUSDT, MAGICUSDT, MAGMAUSDT, MANAUSDT, MARSCOINUSDT, MEGAUSDT, METUSDT, MINAUSDT, MONUSDT, MORPHOUSDT, MOVEUSDT, MOVRUSDT, MUBARAKUSDT, NEARUSDT, NEIROUSDT, NEOUSDT, NIGHTUSDT, NILUSDT, NMRUSDT, NOMUSDT, ONDOUSDT, ONEUSDT, OPGUSDT, OPNUSDT, OPUSDT, ORDIUSDT, PAXGUSDT, PENDLEUSDT, PENGUUSDT, PEOPLEUSDT, PHAROSUSDT, PHAUSDT, PLUMEUSDT, POLUSDT, PONSUSDT, POWERUSDT, PROMUSDT, PUMPBTCUSDT, PUMPUSDT, PYTHUSDT, QNTUSDT, QUSDT, RAYSOLUSDT, RENDERUSDT, RESOLVUSDT, REUSDT, RIVERUSDT, RUNEUSDT, SAGAUSDT, SANDUSDT, SCRUSDT, SEIUSDT, SKYUSDT, SOLUSDT, SOONUSDT, SPKUSDT, SPXUSDT, STRKUSDT, STXUSDT, SUIUSDT, SUPERUSDT, SYNUSDT, SYRUPUSDT, TAOUSDT, THETAUSDT, TIAUSDT, TRBUSDT, TRUMPUSDT, TRUTHUSDT, TRXUSDT, TUTUSDT, UAIUSDT, UNIUSDT, USELESSUSDT, USUSDT, VELVETUSDT, VETUSDT, VIRTUALUSDT, VTHOUSDT, VVVUSDT, WIFUSDT, WLDUSDT, WLFIUSDT, WUSDT, XAUTUSDT, XLMUSDT, XMRUSDT, XPLUSDT, XRPUSDT, YGGUSDT, ZAMAUSDT, ZECUSDT, ZENUSDT, ZKUSDT, ZROUSDT, 币安人生USDT, 牛来USDT, 龙虾USDT
- aggiornato: 2026-10-03 05:31 UTC

### Salute del registro

- composizione: **1 base** · **1865 generate** (di cui 1526 con almeno una conferma)
- occupazione: 1866/3000 — ok

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
| PARTIUSDT | gen_871647b8 | 3 | 2.145 | 105% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.5 |
| GPSUSDT | gen_bf1e00d4 | 4 | 1.59 | 103% | scale_r_mults=[1.5, 3.0, 5.0] |
| STXUSDT | gen_b9bf5d01 | 4 | 1.54 | 103% | scale_r_mults=[2.0, 4.0, 6.0] |
| DOTUSDT | gen_d85b1f05 | 4 | 1.483 | 102% | scale_r_mults=[1.5, 3.0, 5.0] |
| UBUSDT | gen_d926b0fd | 3 | 1.726 | 100% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.35 |
| PROMUSDT | gen_cd5c842f | 4 | 1.628 | 99% | scale_r_mults=[2.0, 4.0, 6.0] |
| ORCAUSDT | gen_5b847426 | 4 | 1.859 | 96% | scale_r_mults=[2.0, 4.0, 6.0] |
| DEXEUSDT | gen_fa304106 | 4 | 2.06 | 95% | scale_r_mults=[1.5, 3.0, 5.0] |
| QUSDT | gen_85fadf54 | 3 | 2.482 | 94% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.75 |
| SPXUSDT | gen_725cb5f4 | 4 | 1.708 | 92% | scale_r_mults=[0.75, 1.5, 3.0] |
| ORCAUSDT | gen_7b4a474b | 4 | 2.148 | 89% | scale_r_mults=[1.5, 3.0, 5.0] |
| ORCAUSDT | gen_bbe21d3f | 4 | 1.952 | 87% | scale_r_mults=[1.5, 3.0, 5.0] |
| DEXEUSDT | gen_b31d8b93 | 4 | 1.881 | 87% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True |
| BRUSDT | gen_95fb50ce | 3 | 1.727 | 87% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
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
| XPINUSDT | gen_c60cc1b9 | 3 | 3.25 | 74% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.35 |
| QUSDT | gen_da608d9f | 3 | 2.444 | 71% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.75 |
| TAUSDT | gen_543186c5 | 3 | 1.928 | 70% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| MUBARAKUSDT | gen_e933160c | 3 | 1.889 | 69% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.35 |
| MUBARAKUSDT | gen_ff3e4154 | 5 | 1.889 | 69% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.35 |
| SKYAIUSDT | gen_6cf80ae6 | 4 | 2.518 | 65% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True |
| SKYAIUSDT | gen_c202787e | 4 | 2.518 | 65% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True |
| GPSUSDT | gen_871647b8 | 4 | 1.517 | 64% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.5 |
| IDUSDT | gen_6bc43e03 | 3 | 1.407 | 64% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| IDUSDT | gen_c5430258 | 3 | 1.407 | 64% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| IDUSDT | gen_dd9238bf | 3 | 1.407 | 64% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| SCRUSDT | gen_bd8f158b | 3 | 1.951 | 61% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| SKYAIUSDT | gen_6191df86 | 4 | 3.086 | 60% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| UBUSDT | gen_15837112 | 3 | 1.935 | 60% | scale_r_mults=[1.0, 2.0, 3.0], sl_to_breakeven=True, profit_lock_keep=0.35 |
| NEIROUSDT | gen_413f1bd7 | 3 | 2.132 | 58% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.75 |
| QUSDT | gen_bf2be656 | 4 | 3.527 | 57% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.75 |
| JUPUSDT | gen_bb762669 | 4 | 1.564 | 56% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.35 |
| QUSDT | gen_18c839a0 | 4 | 3.213 | 55% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.75 |
| QUSDT | gen_b1ac5c24 | 3 | 3.213 | 55% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.75 |
| HUMAUSDT | gen_da39a23a | 4 | 2.24 | 53% | scale_r_mults=[1.0, 1.5, 2.5], sl_to_breakeven=True, profit_lock_keep=0.75 |
| XPINUSDT | gen_ba0c8feb | 3 | 3.092 | 53% | scale_r_mults=[0.75, 1.25, 1.75], sl_to_breakeven=True, profit_lock_keep=0.65 |
| MUBARAKUSDT | gen_f86f7370 | 3 | 2.889 | 51% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.35 |
| UBUSDT | gen_0ec2c344 | 3 | 1.712 | 50% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.5 |
| UBUSDT | gen_4348f9d4 | 3 | 1.712 | 50% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.5 |
| SAHARAUSDT | gen_6b94025f | 5 | 2.22 | 49% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.35 |
| STXUSDT | gen_a5b0e4de | 3 | 1.449 | 48% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.5 |
| PLUMEUSDT | gen_e94b056d | 3 | 2.67 | 47% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.35 |
| GALAUSDT | gen_b9aa9989 | 4 | 1.922 | 46% | scale_r_mults=[1.0, 1.25, 2.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| SKYAIUSDT | gen_f68b811d | 3 | 2.294 | 46% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.35 |
| UBUSDT | gen_887d87df | 3 | 2.601 | 45% | scale_r_mults=[1.5, 3.0, 5.0], sl_t

[... 9737 caratteri omessi (testa e coda conservate) ...]

_r_mults=[2.0, 4.0, 6.0] |
| STXUSDT | gen_c7a02fce | 3 | None | 0% | scale_r_mults=[2.0, 4.0, 6.0] |
| STXUSDT | gen_d606fde3 | 3 | None | 0% | scale_r_mults=[1.5, 3.0, 5.0] |
| SUIUSDT | gen_8c9b332f | 3 | None | 0% | scale_r_mults=[1.0, 2.0, 3.0] |
| SUPERUSDT | gen_0eb999b7 | 3 | None | 0% | scale_r_mults=[1.5, 3.0, 5.0] |
| SYRUPUSDT | gen_98d56766 | 3 | None | 0% | scale_r_mults=[1.5, 3.0, 5.0] |
| SYRUPUSDT | gen_f3b97917 | 3 | None | 0% | scale_r_mults=[1.0, 1.5, 2.5] |
| TAUSDT | gen_4e6e1ae0 | 3 | 2.15 | 0% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.75 |
| TAUSDT | gen_b028553e | 3 | None | 0% | scale_r_mults=[1.5, 3.0, 5.0] |
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
| recovery | 64 | 4.8% |
| regime | 22 | 1.7% |
| pf_ex_top | 3 | 0.2% |
| trades | 6 | 0.5% |
| holdout | 1 | 0.1% |
| total_return | 1207 | 91.4% |
| consistency | 17 | 1.3% |

- quasi-passaggi (un solo criterio, di poco): **1** — sono i semi delle mutazioni del run successivo

**strategie generate** — 22632 valutazioni, 44 passate (0.19%) · 2026-10-03 05:31 UTC

| Criterio che ferma | Casi | Quota |
|---|---|---|
| pf_ex_top | 248 | 1.1% |
| regime | 1172 | 5.2% |
| recovery | 1439 | 6.4% |
| holdout | 45 | 0.2% |
| trades | 1364 | 6.0% |
| total_return | 18091 | 80.1% |
| consistency | 229 | 1.0% |

- quasi-passaggi (un solo criterio, di poco): **40** — sono i semi delle mutazioni del run successivo

## Supervisore (taratura automatica)

- ultimo giro: 2026-10-03 06:01 UTC · coppie validate: **227** · GATE 1 pronto: True
- tasso di passaggio misurato: **0.184%**

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
- totale: **246** · vinti: 138 (56%) · PnL realizzato: **-73.68**
- confronto col mercato: noi -7.37% vs BTC buy&hold +11.74% nello stesso periodo → **sotto** il mercato

- costi: **35.76 USDT** su 246 trade (0.14/trade) _(stimati dal modello del gate, non misurati dai fill)_
  - commissioni 20.40 · spread 15.34 · funding +0.01
  - lordo -37.93 → netto -73.68 · **break-even 3.85%** dell'equity
  - piu' costose: DEXEUSDT 2.88 · SYRUPUSDT 2.26 · SPXUSDT 1.77 · ORCAUSDT 1.69 · QUSDT 1.62
  - ⚠️ Costi operativi elevati: servono 3.85% solo per pareggiare (soglia 1.5%)

| Uscita | Trade | % | PnL |
|---|---|---|---|
| Trailing stop | 111 | 45% | +110.21 |
| Stop loss (prima di qualsiasi TP) | 107 | 43% | -270.73 |
| Scale-out (>=1 TP incassato, residuo a BE) | 23 | 9% | +52.76 |
| Time exit (orizzonte scaduto) | 3 | 1% | +13.30 |
| Take profit (fino all'ultimo gradino) | 2 | 1% | +20.78 |

- gradini raggiunti (su 246 trade): 0 TP: 220 (89%) · 1 TP: 23 (9%) · 2 TP: 1 (0%) · 3 TP: 2 (1%)

- **drawdown di portafoglio: 80.54 USDT** (ritorno -73.68 · recovery -0.91) · max 9 posizioni aperte insieme
  - il gate prometteva recovery ≥ 2.0 per ogni coppia (peggiore in registro: 0.00); il PORTAFOGLIO realizza -0.91
  _uscite in ordine di TEMPO: e' la buca vera, quella che il gate non vede perche' valida una coppia alla volta._

- escursione favorevole (mfe_r, 246 trade): mediana **0.85R** · ≥1R: 41% · ≥1.5R: 15% · ≥3R: 2% · ≥5R: 0%
  _quanto lontano arriva il prezzo, in unità di R: dice se la scala di TP è raggiungibile. Dettaglio: `python -m scripts.mfe_report`_

## Deriva paper vs gate
_il gate promette sulla storia, il paper misura il presente. `drift` = promessa contraddetta -> size/leva frenate subito e fallimento al gate alla prossima passata._

- **globale**: drift · 238 trade · PF vissuto 0.717 vs 2.009 atteso · mfe mediana 0.84R

- **freno globale attivo**: size x0.5 e leva x0.71 (radice) su OGNI trade finche' il PF a 30 giorni resta sotto 0.6 x atteso (motivo: PF 0.72 vs 2.01 atteso · mfe mediana 0.84R < primo TP 1.50R)

| Coppia | Verdetto | Trade | PF vissuto/atteso | Motivo |
|---|---|---|---|---|
| SPXUSDT|gen_ba3a671f | watch | 7 | 0.047 / 1.644 | PF 0.05 vs 1.64 atteso · mfe mediana 0.33R < primo TP 0.75R |
| PROMUSDT|gen_cd5c842f | watch | 7 | 4.156 / 1.628 | mfe mediana 1.10R < primo TP 2.00R |
| USELESSUSDT|gen_2031005e | watch | 7 | 0.304 / 1.54 | PF 0.30 vs 1.54 atteso · mfe mediana 0.80R < primo TP 2.00R |
| SYRUPUSDT|gen_4c6df481 | watch | 6 | 2.903 / 1.453 | mfe mediana 1.27R < primo TP 2.00R |
| QUSDT|gen_18c839a0 | watch | 5 | 0.936 / 3.213 | PF 0.94 vs 3.21 atteso · mfe mediana 0.91R < primo TP 1.50R |
| DEXEUSDT|gen_fa304106 | watch | 5 | 0.0 / 2.06 | PF 0.00 vs 2.06 atteso · mfe mediana 0.52R < primo TP 1.50R |
| GPSUSDT|gen_bf1e00d4 | watch | 4 | 4.936 / 1.59 | mfe mediana 0.90R < primo TP 1.50R |
| DEXEUSDT|gen_b31d8b93 | watch | 4 | 0.149 / 1.881 | PF 0.15 vs 1.88 atteso · mfe mediana 1.23R < primo TP 2.00R |
| AVAAIUSDT|gen_e50a9211 | watch | 4 | 0.345 / 1.525 | PF 0.35 vs 1.52 atteso |
| STXUSDT|gen_b9bf5d01 | watch | 3 | 0.208 / 1.54 | PF 0.21 vs 1.54 atteso · mfe mediana 0.74R < primo TP 2.00R |
| SYRUPUSDT|gen_af734c68 | watch | 3 | 0.407 / 1.493 | PF 0.41 vs 1.49 atteso · mfe mediana 0.94R < primo TP 1.50R |
| VETUSDT|gen_6d06dca0 | watch | 3 | 0.386 / 1.631 | PF 0.39 vs 1.63 atteso |
| ORCAUSDT|gen_6d06dca0 | watch | 3 | 0.0 / 1.967 | PF 0.00 vs 1.97 atteso · mfe mediana 0.49R < primo TP 1.50R |
| JTOUSDT|gen_f238d283 | watch | 3 | 0.653 / 1.64 | PF 0.65 vs 1.64 atteso |
| SPXUSDT|gen_725cb5f4 | watch | 2 | 0.136 / 1.708 | PF 0.14 vs 1.71 atteso · mfe mediana 0.52R < primo TP 0.75R |
| USELESSUSDT|gen_194e2514 | watch | 2 | 0.0 / 2.036 | PF 0.00 vs 2.04 atteso · mfe mediana 0.67R < primo TP 2.00R |
| MUBARAKUSDT|gen_49c2f657 | watch | 2 | 0.532 / 2.261 | PF 0.53 vs 2.26 atteso |
| GALAUSDT|gen_b9aa9989 | watch | 2 | 0.415 / 1.922 | PF 0.41 vs 1.92 atteso |
| UBUSDT|gen_f3661202 | watch | 2 | 0.546 / 1.679 | PF 0.55 vs 1.68 atteso · mfe mediana 1.16R < primo TP 2.00R |
| MUBARAKUSDT|gen_1f7ead60 | watch | 2 | 0.0 / 2.776 | PF 0.00 vs 2.78 atteso · mfe mediana 0.21R < primo TP 2.00R |

- serie di perdite (freno SPENTO dal 24 set, solo misura): **gen_fa304106** (7 perdite di fila)

## Calibrazione della confidenza
_la confidenza del segnale modula size e leva: qui si verifica che predica davvero l'esito, invece di darlo per scontato._

- verdetto: **costante** · 238 trade · correlazione None · influenza applicata **x1.0**
- tutte le strategie generate escono a confidenza 60: la calibrazione non puo' misurare nulla finche' la confidenza non varia (238 trade, confidenza 60-60)

| Fascia di confidenza | Trade | Win rate | Esito medio |
|---|---|---|---|
| 60.0–60.0 | 79 | 57% | -0.31% |
| 60.0–60.0 | 79 | 63% | +0.00% |
| 60.0–60.0 | 80 | 45% | -1.05% |

_se l'esito medio CRESCE dalla fascia bassa all'alta, la confidenza ordina correttamente i trade._
```
