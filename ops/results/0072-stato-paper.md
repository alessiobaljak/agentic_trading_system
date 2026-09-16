# 0072-stato-paper.req

_eseguito: 2026-09-16 16:09 UTC_

**richiesta:** `stato`
**eseguito:** `.venv/bin/python -m scripts.state_snapshot --no-write`
**esito:** codice 0 in 2.9s

```
[firebase] connesso (Firestore + RTDB)
# Stato sistema (snapshot)
_Generato: 2026-09-16 16:09 UTC_

## Bot
- stato: **running** (🟢 online)
- regime: sideways
- DRY_RUN: True
- equity: **$1,000.00**
- ultimo heartbeat: 2026-09-16 16:09 UTC
- stream prezzi: 🟢 attivo

## Ultima decisione
- esito: **⚪ FLAT** (2026-09-16 16:00 UTC)
- motivo: nessun segnale valido sopra soglia
- asset valutati: 16 · segnali: 0

## Posizioni aperte
- SPXUSDT: long qty=441.5011037527594 @ 0.453 uPnL=-1.1655845723848801 · rischio 0.39% · leva 2.0x
- **rischio aperto totale: 0.39%** dell'equity su 1 posizioni

## GATE 1 — Validazione strategie
- stato: **✅ SUPERATO — pronti per il paper trading**
- copertura universo: **19/156 crypto (12%)** · obiettivo ≥ 35%
- coppie validate (>= 3 pass OOS): **35**
- universo scansionato: 1000BONKUSDT, 1000FLOKIUSDT, 1000LUNCUSDT, 1000PEPEUSDT, 1000SHIBUSDT, AAVEUSDT, ACEUSDT, ADAUSDT, AEROUSDT, AINUSDT, ALGOUSDT, APTUSDT, ARBUSDT, ARCUSDT, ARKUSDT, ARUSDT, ASTRUSDT, ATOMUSDT, AVAAIUSDT, AVAXUSDT, AXLUSDT, AXSUSDT, BANKUSDT, BCHUSDT, BICOUSDT, BNBUSDT, BOMEUSDT, BRUSDT, BTCUSDT, BTRUSDT, BULLAUSDT, CAKEUSDT, CHZUSDT, COTIUSDT, CROSSUSDT, CRVUSDT, CVCUSDT, DASHUSDT, DEXEUSDT, DODOXUSDT, DOGEUSDT, DOTUSDT, DYMUSDT, EGLDUSDT, EIGENUSDT, ENAUSDT, ENSUSDT, ETCUSDT, ETHFIUSDT, ETHUSDT, FARTCOINUSDT, FETUSDT, FILUSDT, FLOCKUSDT, FORMUSDT, GALAUSDT, GPSUSDT, GUSDT, HBARUSDT, HEIUSDT, HEMIUSDT, HIVEUSDT, HOLOUSDT, HOMEUSDT, HUSDT, HYPEUSDT, ICPUSDT, IDOLUSDT, INJUSDT, IOSTUSDT, IOTAUSDT, JTOUSDT, JUPUSDT, KAITOUSDT, KASUSDT, KAVAUSDT, KOMAUSDT, LAUSDT, LDOUSDT, LINKUSDT, LSKUSDT, LTCUSDT, MINAUSDT, MORPHOUSDT, MTLUSDT, MUBARAKUSDT, NEARUSDT, NEIROUSDT, NOTUSDT, ONDOUSDT, ONGUSDT, OPUSDT, ORDIUSDT, PAXGUSDT, PENDLEUSDT, PENGUUSDT, PEOPLEUSDT, PLAYUSDT, PNUTUSDT, POLUSDT, POLYXUSDT, PORTALUSDT, POWRUSDT, PROMUSDT, PUMPUSDT, PUNDIXUSDT, PYTHUSDT, RAYSOLUSDT, RENDERUSDT, REZUSDT, RIFUSDT, RONINUSDT, SAGAUSDT, SANDUSDT, SEIUSDT, SKYAIUSDT, SKYUSDT, SOLUSDT, SOPHUSDT, SPXUSDT, STEEMUSDT, STRKUSDT, STXUSDT, SUIUSDT, SUSHIUSDT, SYNUSDT, TAOUSDT, TIAUSDT, TLMUSDT, TRBUSDT, TRUMPUSDT, TRXUSDT, TUSDT, TUTUSDT, UNIUSDT, USDCUSDT, USELESSUSDT, VELVETUSDT, VETUSDT, VIRTUALUSDT, VTHOUSDT, VVVUSDT, WIFUSDT, WLDUSDT, WLFIUSDT, WUSDT, XLMUSDT, XMRUSDT, XPLUSDT, XRPUSDT, ZECUSDT, ZENUSDT, ZILUSDT, ZKUSDT, ZORAUSDT, ZROUSDT
- aggiornato: 2026-09-16 15:44 UTC

### Salute del registro

- composizione: **1960 base** · **469 generate** (di cui 469 con almeno una conferma)
- occupazione: 2429/3000 — ok

### Strategie VALIDATE (operate dal bot)
| Coin | Strategia | Passes | PF | PnL OOS | Parametri |
|---|---|---|---|---|---|
| HEIUSDT | gen_e6ddc613 | 3 | 2.444 | 211% | scale_r_mults=[2.0, 4.0, 6.0] |
| JASMYUSDT | gen_b2f350ff | 3 | 1.608 | 137% | scale_r_mults=[2.0, 4.0, 6.0] |
| VETUSDT | gen_6d06dca0 | 3 | 1.636 | 128% | scale_r_mults=[2.0, 4.0, 6.0] |
| DOTUSDT | gen_d85b1f05 | 3 | 1.559 | 125% | scale_r_mults=[1.5, 3.0, 5.0] |
| DOTUSDT | gen_da39a23a | 3 | 1.5 | 123% | scale_r_mults=[1.5, 3.0, 5.0] |
| ORCAUSDT | gen_271ab7ec | 3 | 1.81 | 110% | scale_r_mults=[1.0, 2.0, 3.0] |
| SKYAIUSDT | gen_6cf80ae6 | 3 | 2.996 | 109% | scale_r_mults=[2.0, 4.0, 6.0] |
| ORCAUSDT | gen_e6ddc613 | 3 | 1.803 | 108% | scale_r_mults=[1.5, 3.0, 5.0] |
| PROMUSDT | gen_cd5c842f | 3 | 1.724 | 108% | scale_r_mults=[2.0, 4.0, 6.0] |
| ORCAUSDT | gen_9a383fff | 3 | 1.844 | 108% | scale_r_mults=[1.5, 3.0, 5.0] |
| GPSUSDT | gen_bf1e00d4 | 3 | 1.557 | 107% | scale_r_mults=[1.5, 3.0, 5.0] |
| ORCAUSDT | gen_871647b8 | 3 | 1.798 | 106% | scale_r_mults=[1.5, 3.0, 5.0] |
| STXUSDT | gen_b9bf5d01 | 3 | 1.54 | 103% | scale_r_mults=[2.0, 4.0, 6.0] |
| ORCAUSDT | gen_7b4a474b | 3 | 2.221 | 100% | scale_r_mults=[1.5, 3.0, 5.0] |
| SKYAIUSDT | gen_c61d9322 | 3 | 2.443 | 96% | scale_r_mults=[2.0, 4.0, 6.0] |
| SPXUSDT | gen_ba3a671f | 3 | 1.505 | 94% | scale_r_mults=[1.5, 3.0, 5.0] |
| ORCAUSDT | gen_5b847426 | 3 | 1.812 | 93% | scale_r_mults=[2.0, 4.0, 6.0] |
| ORCAUSDT | gen_bbe21d3f | 3 | 1.897 | 84% | scale_r_mults=[1.5, 3.0, 5.0] |
| SKYAIUSDT | gen_98837ec2 | 3 | 2.4 | 83% | scale_r_mults=[2.0, 4.0, 6.0] |
| PROMUSDT | gen_452d4511 | 3 | 2.347 | 82% | scale_r_mults=[2.0, 4.0, 6.0] |
| MUBARAKUSDT | gen_ff3e4154 | 3 | 1.684 | 81% | scale_r_mults=[2.0, 4.0, 6.0] |
| USELESSUSDT | gen_194e2514 | 3 | 1.541 | 77% | scale_r_mults=[2.0, 4.0, 6.0] |
| USELESSUSDT | gen_1bb04e1a | 3 | 1.541 | 77% | scale_r_mults=[2.0, 4.0, 6.0] |
| DEXEUSDT | gen_fa304106 | 3 | 1.785 | 77% | scale_r_mults=[1.5, 3.0, 5.0] |
| BICOUSDT | gen_f238d283 | 3 | 1.518 | 76% | scale_r_mults=[1.5, 3.0, 5.0] |
| JTOUSDT | gen_f238d283 | 3 | 1.426 | 72% | scale_r_mults=[1.5, 3.0, 5.0] |
| SKYAIUSDT | gen_eb2ece0c | 3 | 3.173 | 71% | scale_r_mults=[2.0, 4.0, 6.0] |
| ORCAUSDT | gen_6d06dca0 | 3 | 1.907 | 68% | scale_r_mults=[1.5, 3.0, 5.0] |
| EGLDUSDT | gen_36b0e335 | 3 | 1.49 | 60% | scale_r_mults=[1.5, 3.0, 5.0] |
| SPXUSDT | gen_d53c153b | 3 | 1.817 | 58% | scale_r_mults=[1.5, 3.0, 5.0] |
| NEIROUSDT | gen_f3124a14 | 3 | 1.575 | 56% | scale_r_mults=[1.5, 3.0, 5.0] |
| NEIROUSDT | gen_d53c153b | 3 | 1.773 | 47% | scale_r_mults=[1.0, 2.0, 3.0] |
| SYRUPUSDT | gen_af734c68 | 3 | 1.856 | 43% | scale_r_mults=[2.0, 4.0, 6.0] |
| MUBARAKUSDT | gen_2053cba6 | 3 | 1.463 | 29% | scale_r_mults=[2.0, 4.0, 6.0] |
| ZKUSDT | gen_98837ec2 | 3 | 1.476 | 22% | scale_r_mults=[2.0, 4.0, 6.0] |

## Ultimo run di ottimizzazione
_aggiornato: 2026-09-16 15:44 UTC · 1248 coppie valutate, 0 passate in questo run_

_Nessuna coppia ha passato in questo run._

## Dove muoiono le candidate (autopsia del GATE 1)

**strategie base** — 1248 valutazioni, 0 passate (0.00%) · 2026-09-16 15:44 UTC

| Criterio che ferma | Casi | Quota |
|---|---|---|
| regime | 32 | 2.6% |
| total_return | 1107 | 88.7% |
| holdout | 2 | 0.2% |
| recovery | 71 | 5.7% |
| trades | 9 | 0.7% |
| consistency | 17 | 1.4% |
| pf_ex_top | 10 | 0.8% |

- quasi-passaggi (un solo criterio, di poco): **4** — sono i semi delle mutazioni del run successivo

**strategie generate** — 76140 valutazioni, 163 passate (0.21%) · 2026-09-16 14:29 UTC

| Criterio che ferma | Casi | Quota |
|---|---|---|
| holdout | 530 | 0.7% |
| regime | 11427 | 15.0% |
| total_return | 52712 | 69.4% |
| win_rate | 7 | 0.0% |
| recovery | 6326 | 8.3% |
| trades | 1655 | 2.2% |
| consistency | 2150 | 2.8% |
| pf_ex_top | 1170 | 1.5% |

- quasi-passaggi (un solo criterio, di poco): **40** — sono i semi delle mutazioni del run successivo

## Supervisore (taratura automatica)

- ultimo giro: 2026-09-16 16:03 UTC · coppie validate: **35** · GATE 1 pronto: True
- tasso di passaggio misurato: **0.211%**

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

## Trade chiusi
_nessun trade chiuso._

## Deriva paper vs gate
_nessun verdetto ancora: servono trade chiusi su coppie validate._

## Calibrazione della confidenza
_la confidenza del segnale modula size e leva: qui si verifica che predica davvero l'esito, invece di darlo per scontato._

- verdetto: **insufficient** · 0 trade · correlazione None · influenza applicata **x1.0**
- servono 30 trade, ce ne sono 0


--- stderr ---
/root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
  return query.where(field_path, op_string, value)
```
