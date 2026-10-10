# 0569-10ott-mattina-stato.req

_eseguito: 2026-10-10 03:47 UTC_

**richiesta:** `stato`
**eseguito:** `.venv/bin/python -m scripts.state_snapshot --no-write`
**esito:** codice 0 in 4.3s

```
[firebase] connesso (Firestore + RTDB)
# Stato sistema (snapshot)
_Generato: 2026-10-10 03:47 UTC_

## Bot
- stato: **running** (🟢 online)
- regime: sideways
- DRY_RUN: True
- equity: **$890.58**
- ultimo heartbeat: 2026-10-10 03:44 UTC
- stream prezzi: 🟢 attivo

## Ultima decisione
- esito: **⚪ FLAT** (2026-10-10 03:32 UTC)
- motivo: nessun segnale valido sopra soglia
- asset valutati: 77 · segnali: 0

## Posizioni aperte
- ASTERUSDT: short qty=124.53171399549394 @ 0.7169 uPnL=0.03680939568062368 · rischio 0.06% · leva 1.0x
- AVAAIUSDT: short qty=8236.708626091118 @ 0.008786 uPnL=-1.2944134389759698 · rischio 0.16% · leva 2.0x
- BULLAUSDT: short qty=668.5066381873143 @ 0.08517 uPnL=-0.09055557165094759 · rischio 0.11% · leva 2.0x
- UBUSDT: long qty=553.3055806007093 @ 0.14207 uPnL=-0.3862686716743733 · rischio 0.13% · leva 1.0x
- **rischio aperto totale: 0.46%** dell'equity su 4 posizioni

## GATE 1 — Validazione strategie
- stato: **✅ SUPERATO — pronti per il paper trading**
- copertura universo: **77/200 crypto (38%)** · obiettivo ≥ 35%
- coppie validate (>= 3 pass OOS): **236**
- universo scansionato: 0GUSDT, 1000BONKUSDT, 1000FLOKIUSDT, 1000PEPEUSDT, 1000SHIBUSDT, 2ZUSDT, AAVEUSDT, ACEUSDT, ADAUSDT, AEROUSDT, AIAUSDT, AINUSDT, AIOTUSDT, AKEUSDT, ALGOUSDT, APEUSDT, API3USDT, APTUSDT, ARBUSDT, ARKUSDT, ARUSDT, ASTERUSDT, ATOMUSDT, ATUSDT, AUSDT, AVAXUSDT, AVNTUSDT, AXSUSDT, BANKUSDT, BATUSDT, BCHUSDT, BEAMXUSDT, BICOUSDT, BILLUSDT, BNBUSDT, BOMEUSDT, BRUSDT, BTCUSDT, BTRUSDT, BTWUSDT, C98USDT, CAKEUSDT, CAPUSDT, CCUSDT, CHIPUSDT, CHRUSDT, CHZUSDT, COMPUSDT, COTIUSDT, CRVUSDT, CTSIUSDT, CTUSDT, CVCUSDT, CYBERUSDT, DASHUSDT, DOGEUSDT, DOSUSDT, DOTUSDT, EDUUSDT, EIGENUSDT, ENAUSDT, ENJUSDT, ENSOUSDT, ERAUSDT, ETCUSDT, ETHFIUSDT, ETHUSDT, EULUSDT, FARTCOINUSDT, FETUSDT, FILUSDT, FOLKSUSDT, GALAUSDT, GIGGLEUSDT, GMTUSDT, GRAMUSDT, GRASSUSDT, GRIFFAINUSDT, GTCUSDT, GWEIUSDT, HBARUSDT, HEMIUSDT, HUMAUSDT, HUSDT, HYPEUSDT, ICPUSDT, IMXUSDT, INJUSDT, JASMYUSDT, JCTUSDT, JSTUSDT, JTOUSDT, JUPUSDT, KAIAUSDT, KAITOUSDT, KASUSDT, KITEUSDT, LABUSDT, LDOUSDT, LIGHTUSDT, LINKUSDT, LITUSDT, LPTUSDT, LSKUSDT, LTCUSDT, LYNUSDT, MAGICUSDT, MAGMAUSDT, MANAUSDT, MARSCOINUSDT, MERLUSDT, METUSDT, MINAUSDT, MONUSDT, MORPHOUSDT, MOVRUSDT, MUBARAKUSDT, NEARUSDT, NIGHTUSDT, NILUSDT, NMRUSDT, OGNUSDT, ONDOUSDT, ONEUSDT, ONTUSDT, ONUSDT, OPGUSDT, OPNUSDT, OPUSDT, ORCAUSDT, ORDIUSDT, OUSDT, PARTIUSDT, PAXGUSDT, PENDLEUSDT, PENGUUSDT, PHAUSDT, PIXELUSDT, PLUMEUSDT, POLUSDT, PONSUSDT, PROMUSDT, PUMPUSDT, PYTHUSDT, QNTUSDT, QUSDT, RAYSOLUSDT, RENDERUSDT, RIVERUSDT, RLCUSDT, ROSEUSDT, RUNEUSDT, SAGAUSDT, SANDUSDT, SCRUSDT, SEIUSDT, SENTUSDT, SKLUSDT, SKYUSDT, SOLUSDT, SOONUSDT, SPXUSDT, STABLEUSDT, STRKUSDT, STXUSDT, SUIUSDT, SUSDT, SYNUSDT, TAOUSDT, TIAUSDT, TRBUSDT, TRUMPUSDT, TRXUSDT, UAIUSDT, UMAUSDT, UNIUSDT, USELESSUSDT, USUSDT, VELVETUSDT, VETUSDT, VIRTUALUSDT, VVVUSDT, WIFUSDT, WLDUSDT, WLFIUSDT, WUSDT, XAIUSDT, XAUTUSDT, XLMUSDT, XMRUSDT, XPLUSDT, XRPUSDT, ZAMAUSDT, ZECUSDT, ZENUSDT, ZKUSDT, ZROUSDT, 币安人生USDT, 牛来USDT, 龙虾USDT
- aggiornato: 2026-10-10 01:27 UTC

### Salute del registro

- composizione: **1 base** · **2231 generate** (di cui 1895 con almeno una conferma)
- occupazione: 2232/3000 — ok

### Strategie VALIDATE (operate dal bot)
| Coin | Strategia | Passes | PF | PnL OOS | Parametri |
|---|---|---|---|---|---|
| RUNEUSDT | gen_434083c5 | 3 | 1.709 | 148% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.5 |
| MUBARAKUSDT | gen_1f7ead60 | 4 | 2.776 | 114% | scale_r_mults=[2.0, 4.0, 6.0] |
| STXUSDT | gen_00e50229 | 3 | 1.339 | 111% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| UBUSDT | gen_d926b0fd | 3 | 1.779 | 107% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.35 |
| PTBUSDT | gen_684d7623 | 3 | 1.871 | 107% | scale_r_mults=[1.0, 1.5, 2.5], sl_to_breakeven=True, profit_lock_keep=0.65 |
| PARTIUSDT | gen_871647b8 | 4 | 2.226 | 106% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.5 |
| BANKUSDT | gen_2010adf6 | 3 | 1.596 | 104% | scale_r_mults=[1.0, 2.0, 3.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| UBUSDT | gen_92b77c39 | 3 | 1.527 | 97% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| XPINUSDT | gen_f311acf9 | 3 | 3.094 | 96% | scale_r_mults=[1.0, 1.5, 2.5], sl_to_breakeven=True, profit_lock_keep=0.65 |
| SYRUPUSDT | gen_4c6df481 | 4 | 1.544 | 90% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.75 |
| XPINUSDT | gen_2e0818c8 | 3 | 4.045 | 87% | scale_r_mults=[0.75, 1.25, 1.75], sl_to_breakeven=True, profit_lock_keep=0.65 |
| BRUSDT | gen_95fb50ce | 3 | 1.727 | 87% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| STXUSDT | gen_14e1775b | 4 | 1.74 | 87% | scale_r_mults=[2.0, 4.0, 6.0] |
| STXUSDT | gen_68ebd3b9 | 4 | 1.748 | 86% | scale_r_mults=[2.0, 4.0, 6.0] |
| ORCAUSDT | gen_9a383fff | 5 | 1.978 | 82% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True |
| TAUSDT | gen_01fbe76f | 3 | 1.702 | 82% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| ORCAUSDT | gen_e6ddc613 | 5 | 1.94 | 81% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True |
| UBUSDT | gen_fb3229db | 3 | 1.953 | 79% | scale_r_mults=[1.0, 2.0, 3.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| QUSDT | gen_3ee1484b | 4 | 2.814 | 79% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.75 |
| QUSDT | gen_e75ddbfd | 4 | 2.814 | 79% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.75 |
| IDUSDT | gen_6bc43e03 | 4 | 1.502 | 79% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.5 |
| IDUSDT | gen_c5430258 | 4 | 1.502 | 79% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.5 |
| IDUSDT | gen_dd9238bf | 4 | 1.502 | 79% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.5 |
| UBUSDT | gen_f3e1ade7 | 3 | 2.728 | 77% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| TAUSDT | gen_543186c5 | 4 | 2.012 | 76% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| XPINUSDT | gen_c60cc1b9 | 4 | 3.25 | 74% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.35 |
| BULLAUSDT | gen_0eb59b31 | 3 | 2.568 | 72% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.35 |
| UBUSDT | gen_1e8c6a66 | 3 | 1.816 | 72% | scale_r_mults=[1.0, 1.5, 2.5], sl_to_breakeven=True, profit_lock_keep=0.35 |
| UBUSDT | gen_902fb1fd | 3 | 1.816 | 72% | scale_r_mults=[1.0, 1.5, 2.5], sl_to_breakeven=True, profit_lock_keep=0.35 |
| TAUSDT | gen_194e2514 | 3 | 2.013 | 71% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| TAUSDT | gen_1bb04e1a | 3 | 2.013 | 71% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| QUSDT | gen_da608d9f | 4 | 2.444 | 71% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.75 |
| SCRUSDT | gen_116faa2d | 3 | 1.876 | 71% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.35 |
| PARTIUSDT | gen_64263ae7 | 3 | 1.953 | 70% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.5 |
| TAUSDT | gen_fa5179ea | 3 | 1.964 | 70% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| QUSDT | gen_85fadf54 | 4 | 1.86 | 70% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.75 |
| TAUSDT | gen_6e8a4220 | 3 | 2.178 | 70% | scale_r_mults=[1.0, 2.0, 3.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| MUBARAKUSDT | gen_e933160c | 4 | 1.889 | 69% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.35 |
| MUBARAKUSDT | gen_ff3e4154 | 5 | 1.889 | 69% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.35 |
| TAUSDT | gen_b5d63a02 | 3 | 2.089 | 69% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| CROSSUSDT | gen_4e6e1ae0 | 3 | 2.855 | 68% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| ZECUSDT | gen_e6ddc613 | 3 | 1.465 | 68% | scale_r_mults=[1.0, 2.0, 3.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| GPSUSDT | gen_871647b8 | 5 | 1.517 | 64% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.5 |
| PUMPUSDT | gen_1000366e | 3 | 1.936 | 63% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.35 |
| UBUSDT | gen_655a47f5 | 3 | 1.918 | 61% | scale_r_mults=[0.75, 1.25, 1.75], sl_to_breakeven=True, profit_lock_keep=0.65 |
| AVAAIUSDT | gen_c8529192 | 3 | 2.457 | 61% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.35 |
| BULLAUSDT | gen_cec62f22 | 3 | 4.061 | 61% | scale_r_mults=[1.0, 1.5, 2.5], sl_to_breakeven=True, profit_lock_keep=0.5 |
| JUPUSDT | gen_bb762669 | 5 | 1.614 | 60% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.35 |
| MYXUSDT | gen_a5b0e4de | 3 | 3.066 | 60% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.35 |
| SCRUSDT | gen_bd8f158b | 4 | 1.928 | 60% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| UBUSDT | gen_15837112 | 4 | 1.689 | 60% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.35 |
| XPINUSDT | gen_871647b8 | 3 | 2.6 | 59% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.35 |
| PUMPUSDT | gen_ab1d9bb7 | 3 | 1.795 | 59% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.35 |
| KERNELUSDT | gen_96ed157e | 3 | 3.306 | 59% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.35 |
| GRASSUSDT | gen_f4ac85e0 | 3 | 1.568 | 58% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.5 |
| XPINUSDT | gen_9a383fff | 3 | 3.066 | 58% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, p

[... 16423 caratteri omessi (testa e coda conservate) ...]

o_breakeven=True, profit_lock_keep=0.65 |
| PUNDIXUSDT | gen_96c1ed1b | 3 | None | 0% | scale_r_mults=[2.0, 4.0, 6.0] |
| QUSDT | gen_1e7e2564 | 3 | None | 0% | scale_r_mults=[2.0, 4.0, 6.0] |
| RENDERUSDT | gen_1eec02f5 | 3 | None | 0% | scale_r_mults=[1.5, 3.0, 5.0] |
| RENDERUSDT | gen_fe8925b6 | 3 | 2.027 | 0% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.35 |
| SOPHUSDT | gen_42acf37e | 3 | None | 0% | scale_r_mults=[1.5, 3.0, 5.0] |
| STEEMUSDT | gen_4508a416 | 3 | None | 0% | scale_r_mults=[2.0, 4.0, 6.0] |
| STEEMUSDT | gen_addf82da | 3 | None | 0% | scale_r_mults=[2.0, 4.0, 6.0] |
| STXUSDT | gen_d606fde3 | 3 | None | 0% | scale_r_mults=[1.5, 3.0, 5.0] |
| STXUSDT | gen_f5b63594 | 3 | 1.381 | 0% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.5 |
| SUIUSDT | gen_8c9b332f | 3 | None | 0% | scale_r_mults=[1.0, 2.0, 3.0] |
| SUPERUSDT | gen_0eb999b7 | 3 | None | 0% | scale_r_mults=[1.5, 3.0, 5.0] |
| TAUSDT | gen_49c2f657 | 3 | 2.112 | 0% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| TAUSDT | gen_4e6e1ae0 | 3 | 2.15 | 0% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.75 |
| TAUSDT | gen_b028553e | 3 | None | 0% | scale_r_mults=[1.5, 3.0, 5.0] |
| TAUSDT | gen_b0e86c70 | 3 | 2.477 | 0% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.5 |
| TAUSDT | gen_c08c5114 | 3 | 2.962 | 0% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.5 |
| TAUSDT | gen_c647ead7 | 3 | 2.023 | 0% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| THEUSDT | gen_658b2edb | 3 | None | 0% | scale_r_mults=[2.0, 4.0, 6.0] |
| THEUSDT | gen_a640dfa5 | 3 | None | 0% | scale_r_mults=[2.0, 4.0, 6.0] |
| TRUMPUSDT | gen_f156ca1b | 3 | None | 0% | scale_r_mults=[2.0, 4.0, 6.0] |
| UBUSDT | gen_08664b28 | 3 | 1.839 | 0% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.35 |
| UBUSDT | gen_0d7be682 | 3 | None | 0% | scale_r_mults=[2.0, 4.0, 6.0] |
| UBUSDT | gen_2a2898b0 | 3 | None | 0% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True |
| UBUSDT | gen_3b9c62e9 | 3 | None | 0% | scale_r_mults=[1.5, 3.0, 5.0] |
| UBUSDT | gen_5b847426 | 3 | None | 0% | scale_r_mults=[1.5, 3.0, 5.0] |
| UBUSDT | gen_8e475cd9 | 3 | None | 0% | scale_r_mults=[1.5, 3.0, 5.0] |
| UBUSDT | gen_bbe21d3f | 3 | None | 0% | scale_r_mults=[1.5, 3.0, 5.0] |
| UBUSDT | gen_fb7d035a | 3 | None | 0% | scale_r_mults=[1.5, 3.0, 5.0] |
| USELESSUSDT | gen_1623b4cb | 3 | None | 0% | scale_r_mults=[1.5, 3.0, 5.0] |
| USELESSUSDT | gen_96c1ed1b | 3 | 2.06 | 0% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.5 |
| USELESSUSDT | gen_acea368d | 3 | None | 0% | scale_r_mults=[2.0, 4.0, 6.0] |
| USELESSUSDT | gen_e09c5203 | 3 | 1.636 | 0% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.5 |
| VETUSDT | gen_b9c251a1 | 3 | None | 0% | scale_r_mults=[1.0, 1.5, 2.5], sl_to_breakeven=True |
| VETUSDT | gen_fb3d971f | 3 | None | 0% | scale_r_mults=[2.0, 4.0, 6.0] |
| WALUSDT | gen_2b41880d | 3 | None | 0% | scale_r_mults=[2.0, 4.0, 6.0] |
| WALUSDT | gen_cee79cdd | 3 | None | 0% | scale_r_mults=[2.0, 4.0, 6.0] |
| ZORAUSDT | gen_ceab7f6a | 3 | None | 0% | scale_r_mults=[1.5, 3.0, 5.0] |

## Ultimo run di ottimizzazione
_aggiornato: 2026-09-21 12:43 UTC · 1320 coppie valutate, 0 passate in questo run_

_Nessuna coppia ha passato in questo run._

## Dove muoiono le candidate (autopsia del GATE 1)

**strategie base** — 1320 valutazioni, 0 passate (0.00%) · 2026-09-21 12:43 UTC

| Criterio che ferma | Casi | Quota |
|---|---|---|
| consistency | 17 | 1.3% |
| pf_ex_top | 3 | 0.2% |
| holdout | 1 | 0.1% |
| trades | 6 | 0.5% |
| total_return | 1207 | 91.4% |
| recovery | 64 | 4.8% |
| regime | 22 | 1.7% |

- quasi-passaggi (un solo criterio, di poco): **1** — sono i semi delle mutazioni del run successivo

**strategie generate** — 57311 valutazioni, 185 passate (0.32%) · 2026-10-10 01:10 UTC

| Criterio che ferma | Casi | Quota |
|---|---|---|
| consistency | 1216 | 2.1% |
| holdout | 381 | 0.7% |
| pf_ex_top | 380 | 0.7% |
| trades | 2074 | 3.6% |
| total_return | 42188 | 73.9% |
| recovery | 4798 | 8.4% |
| regime | 6089 | 10.7% |

- quasi-passaggi (un solo criterio, di poco): **40** — sono i semi delle mutazioni del run successivo

## Supervisore (taratura automatica)

- ultimo giro: 2026-10-10 03:00 UTC · coppie validate: **258** · GATE 1 pronto: True
- tasso di passaggio misurato: **0.316%**

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
- totale: **440** · vinti: 244 (55%) · PnL realizzato: **-109.42**
- confronto col mercato: noi -10.94% vs BTC buy&hold +9.01% nello stesso periodo → **sotto** il mercato

- costi: **59.51 USDT** su 440 trade (0.14/trade) _(stimati dal modello del gate, non misurati dai fill)_
  - commissioni 33.00 · spread 26.30 · funding +0.21
  - lordo -49.91 → netto -109.42 · **break-even 6.68%** dell'equity
  - piu' costose: DEXEUSDT 3.13 · SYRUPUSDT 3.06 · ZORAUSDT 2.08 · SPXUSDT 2.02 · UBUSDT 1.95
  - ⚠️ Costi operativi elevati: servono 6.68% solo per pareggiare (soglia 1.5%)

| Uscita | Trade | % | PnL |
|---|---|---|---|
| Trailing stop | 194 | 44% | +157.04 |
| Stop loss (prima di qualsiasi TP) | 191 | 43% | -394.87 |
| Scale-out (>=1 TP incassato, residuo a BE) | 39 | 9% | +78.12 |
| Time exit (orizzonte scaduto) | 12 | 3% | +21.55 |
| Take profit (fino all'ultimo gradino) | 4 | 1% | +28.73 |

- gradini raggiunti (su 440 trade): 0 TP: 391 (89%) · 1 TP: 36 (8%) · 2 TP: 9 (2%) · 3 TP: 4 (1%)

- **drawdown di portafoglio: 113.06 USDT** (ritorno -109.42 · recovery -0.97) · max 15 posizioni aperte insieme
  - il gate prometteva recovery ≥ 2.0 per ogni coppia (peggiore in registro: 0.00); il PORTAFOGLIO realizza -0.97
  _uscite in ordine di TEMPO: e' la buca vera, quella che il gate non vede perche' valida una coppia alla volta._

- escursione favorevole (mfe_r, 440 trade): mediana **0.81R** · ≥1R: 38% · ≥1.5R: 15% · ≥3R: 3% · ≥5R: 0%
  _quanto lontano arriva il prezzo, in unità di R: dice se la scala di TP è raggiungibile. Dettaglio: `python -m scripts.mfe_report`_

## Deriva paper vs gate
_il gate promette sulla storia, il paper misura il presente. `drift` = promessa contraddetta -> size/leva frenate subito e fallimento al gate alla prossima passata._

- **globale**: drift · 422 trade · PF vissuto 0.712 vs 2.019 atteso · mfe mediana 0.81R

- **freno globale attivo**: size x0.5 e leva x0.71 (radice) su OGNI trade finche' il PF a 30 giorni resta sotto 0.6 x atteso (motivo: PF 0.71 vs 2.02 atteso · mfe mediana 0.81R < primo TP 1.50R)

| Coppia | Verdetto | Trade | PF vissuto/atteso | Motivo |
|---|---|---|---|---|
| SYRUPUSDT|gen_4c6df481 | drift | 8 | 1.077 / 1.544 | mfe mediana 1.01R < primo TP 2.00R |
| USELESSUSDT|gen_2031005e | watch | 7 | 0.304 / 1.54 | PF 0.30 vs 1.54 atteso · mfe mediana 0.80R < primo TP 2.00R |
| QUSDT|gen_18c839a0 | watch | 6 | 0.535 / 2.883 | PF 0.53 vs 2.88 atteso · mfe mediana 0.91R < primo TP 1.50R |
| FLOCKUSDT|gen_c5194ce4 | watch | 6 | 0.028 / 1.955 | PF 0.03 vs 1.96 atteso · mfe mediana 0.24R < primo TP 0.75R |
| AVAAIUSDT|gen_e50a9211 | watch | 4 | 0.345 / 1.525 | PF 0.35 vs 1.52 atteso |
| PTBUSDT|gen_684d7623 | watch | 4 | 1.377 / 1.871 | mfe mediana 0.53R < primo TP 1.00R |
| HUMAUSDT|gen_fca11c08 | watch | 4 | 0.0 / 1.657 | PF 0.00 vs 1.66 atteso · mfe mediana 0.10R < primo TP 2.00R |
| MUBARAKUSDT|gen_1f7ead60 | watch | 4 | 0.108 / 2.776 | PF 0.11 vs 2.78 atteso · mfe mediana 1.25R < primo TP 2.00R |
| JTOUSDT|gen_f238d283 | watch | 3 | 0.653 / 1.64 | PF 0.65 vs 1.64 atteso |
| FORMUSDT|gen_c647ead7 | watch | 3 | 99.0 / 2.205 | mfe mediana 0.51R < primo TP 0.75R |
| VETUSDT|gen_6d06dca0 | watch | 3 | 0.386 / 1.631 | PF 0.39 vs 1.63 atteso |
| BULLAUSDT|gen_5a52c06b | watch | 3 | 0.213 / 1.801 | PF 0.21 vs 1.80 atteso · mfe mediana 0.52R < primo TP 1.50R |
| STXUSDT|gen_14e1775b | watch | 3 | 0.266 / 1.74 | PF 0.27 vs 1.74 atteso · mfe mediana 0.44R < primo TP 2.00R |
| CATIUSDT|gen_b3e46005 | watch | 3 | 1.519 / 2.605 | PF 1.52 vs 2.60 atteso |
| SYRUPUSDT|gen_af734c68 | watch | 3 | 0.407 / 1.493 | PF 0.41 vs 1.49 atteso · mfe mediana 0.94R < primo TP 1.50R |
| ORCAUSDT|gen_6d06dca0 | watch | 3 | 0.0 / 1.967 | PF 0.00 vs 1.97 atteso · mfe mediana 0.49R < primo TP 1.50R |
| UBUSDT|gen_f3661202 | watch | 3 | 0.923 / 1.679 | PF 0.92 vs 1.68 atteso · mfe mediana 1.03R < primo TP 2.00R |
| PUMPUSDT|gen_13cc61f2 | watch | 2 | 0.375 / 3.302 | PF 0.38 vs 3.30 atteso |
| XPINUSDT|gen_c60cc1b9 | watch | 2 | 0.154 / 3.25 | PF 0.15 vs 3.25 atteso · mfe mediana 1.06R < primo TP 2.00R |
| MUBARAKUSDT|gen_e933160c | watch | 2 | 0.243 / 1.889 | PF 0.24 vs 1.89 atteso |

- serie di perdite (freno SPENTO dal 24 set, solo misura): **gen_fa304106** (11 perdite di fila)

## Calibrazione della confidenza
_la confidenza del segnale modula size e leva: qui si verifica che predica davvero l'esito, invece di darlo per scontato._

- verdetto: **costante** · 422 trade · correlazione None · influenza applicata **x1.0**
- tutte le strategie generate escono a confidenza 60: la calibrazione non puo' misurare nulla finche' la confidenza non varia (422 trade, confidenza 60-60)

| Fascia di confidenza | Trade | Win rate | Esito medio |
|---|---|---|---|
| 60.0–60.0 | 140 | 52% | -0.27% |
| 60.0–60.0 | 140 | 60% | -0.10% |
| 60.0–60.0 | 142 | 52% | -0.58% |

_se l'esito medio CRESCE dalla fascia bassa all'alta, la confidenza ordina correttamente i trade._
```
