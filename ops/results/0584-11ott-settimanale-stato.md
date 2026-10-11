# 0584-11ott-settimanale-stato.req

_eseguito: 2026-10-11 03:47 UTC_

**richiesta:** `stato`
**eseguito:** `.venv/bin/python -m scripts.state_snapshot --no-write`
**esito:** codice 0 in 4.0s

```
[firebase] connesso (Firestore + RTDB)
# Stato sistema (snapshot)
_Generato: 2026-10-11 03:47 UTC_

## Bot
- stato: **running** (🟢 online)
- regime: sideways
- DRY_RUN: True
- equity: **$891.26**
- ultimo heartbeat: 2026-10-11 03:45 UTC
- stream prezzi: 🟢 attivo

## Ultima decisione
- esito: **⚪ FLAT** (2026-10-11 03:32 UTC)
- motivo: parita' backtest: 1 segnali validi aperti
- asset valutati: 77 · segnali: 1 · miglior segnale ORCAUSDT gen_902fb1fd (conf. 60.0/soglia 30)

## Posizioni aperte
- AINUSDT: long qty=1163.6671661448097 @ 0.04178 uPnL=-0.24884552084458753 · rischio 0.14% · leva 1.0x
- AVAAIUSDT: long qty=10047.570155653133 @ 0.008838 uPnL=-0.3117203497939882 · rischio 0.15% · leva 1.0x
- GRIFFAINUSDT: long qty=1369.4626636428784 @ 0.017712 uPnL=-0.2381446578090056 · rischio 0.09% · leva 1.0x
- OPENUSDT: short qty=563.1009198608224 @ 0.111 uPnL=0.884986344161428 · rischio 0.12% · leva 1.0x
- ORCAUSDT: long qty=30.00931284328172 @ 2.337 uPnL=0.15268048646361532 · rischio 0.16% · leva 2.0x
- USELESSUSDT: short qty=257.0119474202278 @ 0.1868 uPnL=0.24223826712753488 · rischio 0.13% · leva 1.0x
- **rischio aperto totale: 0.78%** dell'equity su 6 posizioni

## GATE 1 — Validazione strategie
- stato: **✅ SUPERATO — pronti per il paper trading**
- copertura universo: **77/200 crypto (38%)** · obiettivo ≥ 35%
- coppie validate (>= 3 pass OOS): **239**
- universo scansionato: 0GUSDT, 1000BONKUSDT, 1000FLOKIUSDT, 1000PEPEUSDT, 1000SHIBUSDT, AAVEUSDT, ACEUSDT, ACTUSDT, ADAUSDT, AEROUSDT, AGTUSDT, AIAUSDT, AINUSDT, AIOTUSDT, AKEUSDT, ALGOUSDT, ALTUSDT, APEUSDT, API3USDT, APRUSDT, APTUSDT, ARBUSDT, ARPAUSDT, ARUSDT, ASTERUSDT, ATOMUSDT, AVAXUSDT, AXSUSDT, AZTECUSDT, BATUSDT, BBUSDT, BCHUSDT, BELUSDT, BILLUSDT, BNBUSDT, BOMEUSDT, BRETTUSDT, BREVUSDT, BRUSDT, BTCUSDT, BTWUSDT, BULLAUSDT, C98USDT, CAKEUSDT, CAPUSDT, CFXUSDT, CHIPUSDT, CHRUSDT, CKBUSDT, COMPUSDT, COTIUSDT, CRVUSDT, CTSIUSDT, CTUSDT, DASHUSDT, DOGEUSDT, DOSUSDT, DOTUSDT, DUSKUSDT, EDGEUSDT, EDUUSDT, EIGENUSDT, ENAUSDT, ENJUSDT, ENSOUSDT, ERAUSDT, ETCUSDT, ETHFIUSDT, ETHUSDT, FARTCOINUSDT, FETUSDT, FILUSDT, FOLKSUSDT, FRAXUSDT, GALAUSDT, GMTUSDT, GRAMUSDT, GRASSUSDT, GRIFFAINUSDT, GTCUSDT, GWEIUSDT, HBARUSDT, HUMAUSDT, HYPEUSDT, ICPUSDT, IMXUSDT, INJUSDT, IOSTUSDT, JASMYUSDT, JCTUSDT, JSTUSDT, JTOUSDT, JUPUSDT, KAIAUSDT, KAITOUSDT, KITEUSDT, LABUSDT, LAUSDT, LAYERUSDT, LDOUSDT, LINKUSDT, LITUSDT, LPTUSDT, LSKUSDT, LTCUSDT, LUMIAUSDT, LYNUSDT, MAGICUSDT, MAGMAUSDT, MANAUSDT, MANTAUSDT, MARSCOINUSDT, MAVUSDT, METUSDT, MINAUSDT, MONUSDT, MORPHOUSDT, MOVRUSDT, MUBARAKUSDT, NEARUSDT, NEOUSDT, NIGHTUSDT, NILUSDT, NMRUSDT, OGNUSDT, ONDOUSDT, ONEUSDT, ONGUSDT, ONTUSDT, OPGUSDT, OPNUSDT, OPUSDT, ORCAUSDT, ORDIUSDT, OUSDT, PAXGUSDT, PENDLEUSDT, PENGUUSDT, PHAUSDT, PIXELUSDT, PLUMEUSDT, POLUSDT, PONSUSDT, PROMUSDT, PUMPUSDT, PYTHUSDT, QNTUSDT, QTUMUSDT, QUSDT, RAYSOLUSDT, RENDERUSDT, RLCUSDT, RONINUSDT, ROSEUSDT, RVNUSDT, SAGAUSDT, SANDUSDT, SEIUSDT, SENTUSDT, SKLUSDT, SKYUSDT, SOLUSDT, SOONUSDT, STABLEUSDT, STRKUSDT, STXUSDT, SUIUSDT, SUSDT, TAOUSDT, TIAUSDT, TRBUSDT, TRUMPUSDT, TRXUSDT, UNIUSDT, USELESSUSDT, USUSDT, VELODROMEUSDT, VIRTUALUSDT, VTHOUSDT, VVVUSDT, WALUSDT, WIFUSDT, WLDUSDT, WLFIUSDT, WUSDT, XAIUSDT, XAUTUSDT, XLMUSDT, XMRUSDT, XPLUSDT, XRPUSDT, YGGUSDT, ZAMAUSDT, ZECUSDT, ZENUSDT, ZKUSDT, ZROUSDT, 币安人生USDT, 牛来USDT, 龙虾USDT
- aggiornato: 2026-10-11 01:57 UTC

### Salute del registro

- composizione: **1 base** · **2318 generate** (di cui 1982 con almeno una conferma)
- occupazione: 2319/3000 — ok

### Strategie VALIDATE (operate dal bot)
| Coin | Strategia | Passes | PF | PnL OOS | Parametri |
|---|---|---|---|---|---|
| RUNEUSDT | gen_434083c5 | 3 | 1.709 | 148% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.5 |
| STXUSDT | gen_afa705ab | 3 | 1.579 | 135% | scale_r_mults=[0.75, 1.25, 1.75], sl_to_breakeven=True, profit_lock_keep=0.65 |
| MUBARAKUSDT | gen_1f7ead60 | 4 | 2.776 | 114% | scale_r_mults=[2.0, 4.0, 6.0] |
| STXUSDT | gen_00e50229 | 3 | 1.339 | 111% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| UBUSDT | gen_d926b0fd | 3 | 1.779 | 107% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.35 |
| PTBUSDT | gen_684d7623 | 3 | 1.871 | 107% | scale_r_mults=[1.0, 1.5, 2.5], sl_to_breakeven=True, profit_lock_keep=0.65 |
| PARTIUSDT | gen_871647b8 | 4 | 2.226 | 106% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.5 |
| BANKUSDT | gen_2010adf6 | 3 | 1.572 | 101% | scale_r_mults=[1.0, 2.0, 3.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| UBUSDT | gen_d163b751 | 3 | 1.536 | 100% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| UBUSDT | gen_92b77c39 | 3 | 1.527 | 97% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| XPINUSDT | gen_f311acf9 | 3 | 3.094 | 96% | scale_r_mults=[1.0, 1.5, 2.5], sl_to_breakeven=True, profit_lock_keep=0.65 |
| SYRUPUSDT | gen_4c6df481 | 4 | 1.544 | 90% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.75 |
| CAKEUSDT | gen_5787ebed | 3 | 1.607 | 89% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.5 |
| XPINUSDT | gen_2e0818c8 | 3 | 4.045 | 87% | scale_r_mults=[0.75, 1.25, 1.75], sl_to_breakeven=True, profit_lock_keep=0.65 |
| BRUSDT | gen_95fb50ce | 3 | 1.727 | 87% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| TAUSDT | gen_01fbe76f | 3 | 1.714 | 84% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| ORCAUSDT | gen_9a383fff | 5 | 1.978 | 82% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True |
| AINUSDT | gen_d926b0fd | 3 | 1.562 | 81% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| ORCAUSDT | gen_e6ddc613 | 5 | 1.94 | 81% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True |
| UBUSDT | gen_fb3229db | 3 | 1.953 | 79% | scale_r_mults=[1.0, 2.0, 3.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| QUSDT | gen_3ee1484b | 4 | 2.814 | 79% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.75 |
| QUSDT | gen_e75ddbfd | 4 | 2.814 | 79% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.75 |
| IDUSDT | gen_6bc43e03 | 4 | 1.502 | 79% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.5 |
| IDUSDT | gen_c5430258 | 4 | 1.502 | 79% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.5 |
| IDUSDT | gen_dd9238bf | 4 | 1.502 | 79% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.5 |
| UBUSDT | gen_f3e1ade7 | 3 | 2.728 | 77% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| TAUSDT | gen_543186c5 | 4 | 2.012 | 76% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| CROSSUSDT | gen_4e6e1ae0 | 3 | 3.024 | 74% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| XPINUSDT | gen_c60cc1b9 | 4 | 3.25 | 74% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.35 |
| BULLAUSDT | gen_0eb59b31 | 3 | 2.568 | 72% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.35 |
| UBUSDT | gen_1e8c6a66 | 3 | 1.816 | 72% | scale_r_mults=[1.0, 1.5, 2.5], sl_to_breakeven=True, profit_lock_keep=0.35 |
| UBUSDT | gen_902fb1fd | 3 | 1.816 | 72% | scale_r_mults=[1.0, 1.5, 2.5], sl_to_breakeven=True, profit_lock_keep=0.35 |
| QUSDT | gen_da608d9f | 4 | 2.444 | 71% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.75 |
| SCRUSDT | gen_116faa2d | 3 | 1.876 | 71% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.35 |
| PARTIUSDT | gen_64263ae7 | 3 | 1.953 | 70% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.5 |
| QUSDT | gen_85fadf54 | 4 | 1.86 | 70% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.75 |
| TAUSDT | gen_194e2514 | 3 | 1.97 | 70% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| TAUSDT | gen_1bb04e1a | 3 | 1.97 | 70% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| TAUSDT | gen_6e8a4220 | 3 | 2.178 | 70% | scale_r_mults=[1.0, 2.0, 3.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| MUBARAKUSDT | gen_e933160c | 4 | 1.889 | 69% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.35 |
| MUBARAKUSDT | gen_ff3e4154 | 5 | 1.889 | 69% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.35 |
| TAUSDT | gen_b5d63a02 | 3 | 2.089 | 69% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| TAUSDT | gen_fa5179ea | 3 | 1.924 | 69% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| EIGENUSDT | gen_1b7827f3 | 3 | 1.461 | 67% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| ZECUSDT | gen_e6ddc613 | 3 | 1.456 | 67% | scale_r_mults=[1.0, 2.0, 3.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| SAHARAUSDT | gen_66848d49 | 3 | 2.094 | 65% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.35 |
| GPSUSDT | gen_871647b8 | 5 | 1.517 | 64% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.5 |
| HUSDT | gen_ccb40454 | 3 | 1.478 | 62% | scale_r_mults=[1.0, 2.0, 3.0], sl_to_breakeven=True, profit_lock_keep=0.5 |
| SKYAIUSDT | gen_f68b811d | 4 | 2.765 | 62% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.35 |
| AINUSDT | gen_d8656ab7 | 3 | 1.648 | 62% | scale_r_mults=[1.0, 2.0, 3.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| AVAAIUSDT | gen_c8529192 | 3 | 2.457 | 61% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.35 |
| BULLAUSDT | gen_cec62f22 | 3 | 4.061 | 61% | scale_r_mults=[1.0, 1.5, 2.5], sl_to_breakeven=True, profit_lock_keep=0.5 |
| JUPUSDT | gen_bb762669 | 5 | 1.614 | 60% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_break

[... 17710 caratteri omessi (testa e coda conservate) ...]

n_5b9ed454 | 3 | 2.232 | 0% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| PTBUSDT | gen_630b2a40 | 3 | 2.368 | 0% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| PTBUSDT | gen_73033c73 | 3 | 2.067 | 0% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.5 |
| PUMPUSDT | gen_13cc61f2 | 3 | 3.302 | 0% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| PUNDIXUSDT | gen_96c1ed1b | 3 | None | 0% | scale_r_mults=[2.0, 4.0, 6.0] |
| QUSDT | gen_1e7e2564 | 3 | None | 0% | scale_r_mults=[2.0, 4.0, 6.0] |
| RENDERUSDT | gen_1eec02f5 | 3 | None | 0% | scale_r_mults=[1.5, 3.0, 5.0] |
| RENDERUSDT | gen_fe8925b6 | 3 | 2.027 | 0% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.35 |
| SAHARAUSDT | gen_4e1e404e | 3 | 1.445 | 0% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.5 |
| STEEMUSDT | gen_4508a416 | 3 | None | 0% | scale_r_mults=[2.0, 4.0, 6.0] |
| STEEMUSDT | gen_addf82da | 3 | None | 0% | scale_r_mults=[2.0, 4.0, 6.0] |
| STXUSDT | gen_0aa0d29c | 3 | 1.656 | 0% | scale_r_mults=[1.0, 1.5, 2.5], sl_to_breakeven=True, profit_lock_keep=0.65 |
| SUIUSDT | gen_8c9b332f | 3 | None | 0% | scale_r_mults=[1.0, 2.0, 3.0] |
| TAUSDT | gen_49c2f657 | 3 | 2.112 | 0% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
| TAUSDT | gen_4e6e1ae0 | 3 | 2.15 | 0% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.75 |
| TAUSDT | gen_b0e86c70 | 3 | 2.477 | 0% | scale_r_mults=[1.5, 3.0, 5.0], sl_to_breakeven=True, profit_lock_keep=0.5 |
| TAUSDT | gen_c08c5114 | 3 | 2.962 | 0% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.5 |
| TAUSDT | gen_c647ead7 | 3 | 2.023 | 0% | scale_r_mults=[2.0, 4.0, 6.0], sl_to_breakeven=True, profit_lock_keep=0.65 |
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
| ZORAUSDT | gen_ceab7f6a | 3 | None | 0% | scale_r_mults=[1.5, 3.0, 5.0] |

## Ultimo run di ottimizzazione
_aggiornato: 2026-09-21 12:43 UTC · 1320 coppie valutate, 0 passate in questo run_

_Nessuna coppia ha passato in questo run._

## Dove muoiono le candidate (autopsia del GATE 1)

**strategie base** — 1320 valutazioni, 0 passate (0.00%) · 2026-09-21 12:43 UTC

| Criterio che ferma | Casi | Quota |
|---|---|---|
| consistency | 17 | 1.3% |
| regime | 22 | 1.7% |
| trades | 6 | 0.5% |
| holdout | 1 | 0.1% |
| total_return | 1207 | 91.4% |
| pf_ex_top | 3 | 0.2% |
| recovery | 64 | 4.8% |

- quasi-passaggi (un solo criterio, di poco): **1** — sono i semi delle mutazioni del run successivo

**strategie generate** — 66750 valutazioni, 200 passate (0.30%) · 2026-10-11 01:40 UTC

| Criterio che ferma | Casi | Quota |
|---|---|---|
| consistency | 1416 | 2.1% |
| regime | 6943 | 10.4% |
| trades | 1486 | 2.2% |
| holdout | 427 | 0.6% |
| total_return | 50805 | 76.3% |
| pf_ex_top | 286 | 0.4% |
| recovery | 5187 | 7.8% |

- quasi-passaggi (un solo criterio, di poco): **40** — sono i semi delle mutazioni del run successivo

## Supervisore (taratura automatica)

- ultimo giro: 2026-10-11 03:03 UTC · coppie validate: **262** · GATE 1 pronto: True
- tasso di passaggio misurato: **0.294%**

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
- totale: **458** · vinti: 257 (56%) · PnL realizzato: **-109.19**
- confronto col mercato: noi -10.92% vs BTC buy&hold +9.45% nello stesso periodo → **sotto** il mercato

- costi: **61.74 USDT** su 458 trade (0.14/trade) _(stimati dal modello del gate, non misurati dai fill)_
  - commissioni 34.18 · spread 27.38 · funding +0.19
  - lordo -47.45 → netto -109.19 · **break-even 6.93%** dell'equity
  - piu' costose: DEXEUSDT 3.13 · SYRUPUSDT 3.08 · ZORAUSDT 2.37 · GPSUSDT 2.10 · UBUSDT 2.07
  - ⚠️ Costi operativi elevati: servono 6.93% solo per pareggiare (soglia 1.5%)

| Uscita | Trade | % | PnL |
|---|---|---|---|
| Trailing stop | 207 | 45% | +163.59 |
| Stop loss (prima di qualsiasi TP) | 196 | 43% | -401.18 |
| Scale-out (>=1 TP incassato, residuo a BE) | 39 | 9% | +78.12 |
| Time exit (orizzonte scaduto) | 12 | 3% | +21.55 |
| Take profit (fino all'ultimo gradino) | 4 | 1% | +28.73 |

- gradini raggiunti (su 458 trade): 0 TP: 409 (89%) · 1 TP: 36 (8%) · 2 TP: 9 (2%) · 3 TP: 4 (1%)

- **drawdown di portafoglio: 113.19 USDT** (ritorno -109.19 · recovery -0.96) · max 15 posizioni aperte insieme
  - il gate prometteva recovery ≥ 2.0 per ogni coppia (peggiore in registro: 0.00); il PORTAFOGLIO realizza -0.96
  _uscite in ordine di TEMPO: e' la buca vera, quella che il gate non vede perche' valida una coppia alla volta._

- escursione favorevole (mfe_r, 458 trade): mediana **0.82R** · ≥1R: 39% · ≥1.5R: 14% · ≥3R: 3% · ≥5R: 0%
  _quanto lontano arriva il prezzo, in unità di R: dice se la scala di TP è raggiungibile. Dettaglio: `python -m scripts.mfe_report`_

## Deriva paper vs gate
_il gate promette sulla storia, il paper misura il presente. `drift` = promessa contraddetta -> size/leva frenate subito e fallimento al gate alla prossima passata._

- **globale**: drift · 437 trade · PF vissuto 0.719 vs 2.016 atteso · mfe mediana 0.81R

- **freno globale attivo**: size x0.5 e leva x0.71 (radice) su OGNI trade finche' il PF a 30 giorni resta sotto 0.6 x atteso (motivo: PF 0.72 vs 2.02 atteso · mfe mediana 0.81R < primo TP 1.50R)

| Coppia | Verdetto | Trade | PF vissuto/atteso | Motivo |
|---|---|---|---|---|
| SYRUPUSDT|gen_4c6df481 | drift | 9 | 1.092 / 1.544 | mfe mediana 1.01R < primo TP 2.00R |
| QUSDT|gen_18c839a0 | watch | 7 | 0.461 / 2.883 | PF 0.46 vs 2.88 atteso · mfe mediana 0.90R < primo TP 1.50R |
| USELESSUSDT|gen_2031005e | watch | 7 | 0.304 / 1.54 | PF 0.30 vs 1.54 atteso · mfe mediana 0.80R < primo TP 2.00R |
| BULLAUSDT|gen_7ac562e3 | watch | 4 | 0.898 / 1.839 | PF 0.90 vs 1.84 atteso |
| HUMAUSDT|gen_fca11c08 | watch | 4 | 0.0 / 1.657 | PF 0.00 vs 1.66 atteso · mfe mediana 0.10R < primo TP 2.00R |
| AVAAIUSDT|gen_e50a9211 | watch | 4 | 0.345 / 1.525 | PF 0.35 vs 1.52 atteso |
| MUBARAKUSDT|gen_1f7ead60 | watch | 4 | 0.108 / 2.776 | PF 0.11 vs 2.78 atteso · mfe mediana 1.25R < primo TP 2.00R |
| PTBUSDT|gen_684d7623 | watch | 4 | 1.377 / 1.871 | mfe mediana 0.53R < primo TP 1.00R |
| FORMUSDT|gen_c647ead7 | watch | 3 | 99.0 / 2.206 | mfe mediana 0.51R < primo TP 0.75R |
| JTOUSDT|gen_f238d283 | watch | 3 | 0.653 / 1.64 | PF 0.65 vs 1.64 atteso |
| VETUSDT|gen_6d06dca0 | watch | 3 | 0.386 / 1.631 | PF 0.39 vs 1.63 atteso |
| GALAUSDT|gen_b9aa9989 | watch | 3 | 0.54 / 1.922 | PF 0.54 vs 1.92 atteso · mfe mediana 0.55R < primo TP 1.00R |
| UBUSDT|gen_f3661202 | watch | 3 | 0.923 / 1.679 | PF 0.92 vs 1.68 atteso · mfe mediana 1.03R < primo TP 2.00R |
| ORCAUSDT|gen_6d06dca0 | watch | 3 | 0.0 / 1.967 | PF 0.00 vs 1.97 atteso · mfe mediana 0.49R < primo TP 1.50R |
| CATIUSDT|gen_b3e46005 | watch | 3 | 1.519 / 2.605 | PF 1.52 vs 2.60 atteso |
| BULLAUSDT|gen_5a52c06b | watch | 3 | 0.213 / 1.801 | PF 0.21 vs 1.80 atteso · mfe mediana 0.52R < primo TP 1.50R |
| SYRUPUSDT|gen_af734c68 | watch | 3 | 0.407 / 1.493 | PF 0.41 vs 1.49 atteso · mfe mediana 0.94R < primo TP 1.50R |
| MUBARAKUSDT|gen_49c2f657 | watch | 2 | 0.532 / 1.721 | PF 0.53 vs 1.72 atteso |
| MAVIAUSDT|gen_608b892e | watch | 2 | 99.0 / 1.775 | mfe mediana 0.67R < primo TP 1.00R |
| STXUSDT|gen_a5b0e4de | watch | 2 | 0.38 / 1.449 | PF 0.38 vs 1.45 atteso · mfe mediana 1.16R < primo TP 2.00R |

- serie di perdite (freno SPENTO dal 24 set, solo misura): **gen_fa304106** (11 perdite di fila)

## Calibrazione della confidenza
_la confidenza del segnale modula size e leva: qui si verifica che predica davvero l'esito, invece di darlo per scontato._

- verdetto: **costante** · 437 trade · correlazione None · influenza applicata **x1.0**
- tutte le strategie generate escono a confidenza 60: la calibrazione non puo' misurare nulla finche' la confidenza non varia (437 trade, confidenza 60-60)

| Fascia di confidenza | Trade | Win rate | Esito medio |
|---|---|---|---|
| 60.0–60.0 | 145 | 55% | -0.21% |
| 60.0–60.0 | 145 | 59% | -0.09% |
| 60.0–60.0 | 147 | 52% | -0.63% |

_se l'esito medio CRESCE dalla fascia bassa all'alta, la confidenza ordina correttamente i trade._
```
