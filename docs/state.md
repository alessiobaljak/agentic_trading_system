# Stato sistema (snapshot)
_Generato: 2026-09-14 23:08 UTC_

## Bot
- stato: **running** (🟢 online)
- regime: bull_trending
- DRY_RUN: True
- equity: **$1,000.00**
- ultimo heartbeat: 2026-09-14 23:07 UTC
- stream prezzi: 🟡 candele REST

## Ultima decisione
- esito: **⚪ FLAT** (2026-09-14 23:03 UTC)
- motivo: nessun segnale valido sopra soglia
- asset valutati: 100 · segnali: 0

## GATE 1 — Validazione strategie
- stato: **🔄 in corso**
- copertura universo: **1/159 crypto (1%)** · obiettivo ≥ 35%
- coppie validate (>= 3 pass OOS): **8**
- universo scansionato: 1000BONKUSDT, 1000FLOKIUSDT, 1000PEPEUSDT, 1000SHIBUSDT, AAVEUSDT, ACEUSDT, ADAUSDT, AEROUSDT, AINUSDT, ALGOUSDT, ALTUSDT, ANKRUSDT, API3USDT, APTUSDT, ARBUSDT, ARKUSDT, ARUSDT, ATOMUSDT, AVAAIUSDT, AVAXUSDT, AXSUSDT, BABYUSDT, BANKUSDT, BBUSDT, BCHUSDT, BERAUSDT, BICOUSDT, BNBUSDT, BOMEUSDT, BRUSDT, BTCUSDT, BTRUSDT, BULLAUSDT, BUSDT, CAKEUSDT, CHZUSDT, COTIUSDT, CRVUSDT, CVCUSDT, DASHUSDT, DEXEUSDT, DOGEUSDT, DOTUSDT, EGLDUSDT, EIGENUSDT, ENAUSDT, ENSUSDT, ESPORTSUSDT, ETCUSDT, ETHFIUSDT, ETHUSDT, FARTCOINUSDT, FETUSDT, FILUSDT, FLOCKUSDT, FORMUSDT, GALAUSDT, GLMUSDT, GPSUSDT, GRASSUSDT, GRIFFAINUSDT, HBARUSDT, HEMIUSDT, HIVEUSDT, HUSDT, HYPEUSDT, ICPUSDT, INJUSDT, IOSTUSDT, IOTAUSDT, IOTXUSDT, JTOUSDT, JUPUSDT, KAITOUSDT, KASUSDT, KAVAUSDT, KNCUSDT, KOMAUSDT, LAUSDT, LDOUSDT, LINKUSDT, LSKUSDT, LTCUSDT, MINAUSDT, MORPHOUSDT, MOVRUSDT, MTLUSDT, MUBARAKUSDT, NEARUSDT, NEIROUSDT, NEOUSDT, NOTUSDT, ONDOUSDT, ONGUSDT, OPUSDT, ORDIUSDT, PAXGUSDT, PENDLEUSDT, PENGUUSDT, PEOPLEUSDT, PNUTUSDT, POLUSDT, POLYXUSDT, POWRUSDT, PROMUSDT, PUMPUSDT, PUNDIXUSDT, PYTHUSDT, RAYSOLUSDT, REDUSDT, RENDERUSDT, REZUSDT, RONINUSDT, SAGAUSDT, SANDUSDT, SEIUSDT, SKYUSDT, SOLUSDT, SOLVUSDT, SOPHUSDT, SPXUSDT, STEEMUSDT, STRKUSDT, STXUSDT, SUIUSDT, SYNUSDT, TAOUSDT, THETAUSDT, TIAUSDT, TRUMPUSDT, TRXUSDT, TUSDT, TUTUSDT, UBUSDT, UNIUSDT, USDCUSDT, USELESSUSDT, VELVETUSDT, VETUSDT, VIRTUALUSDT, VTHOUSDT, VVVUSDT, WALUSDT, WAXPUSDT, WIFUSDT, WLDUSDT, WLFIUSDT, WUSDT, XLMUSDT, XMRUSDT, XPINUSDT, XPLUSDT, XRPUSDT, XTZUSDT, ZECUSDT, ZENUSDT, ZILUSDT, ZORAUSDT, ZROUSDT
- aggiornato: 2026-09-14 21:39 UTC

### Salute del registro

- composizione: **1992 base** · **417 generate** (di cui 417 con almeno una conferma)
- occupazione: 2409/3000 — ok

### Strategie VALIDATE (operate dal bot)
| Coin | Strategia | Passes | PF | PnL OOS | Parametri |
|---|---|---|---|---|---|
| ORCAUSDT | gen_271ab7ec | 3 | 1.81 | 110% | scale_r_mults=[1.0, 2.0, 3.0] |
| ORCAUSDT | gen_e6ddc613 | 3 | 1.799 | 108% | scale_r_mults=[1.5, 3.0, 5.0] |
| ORCAUSDT | gen_9a383fff | 3 | 1.84 | 107% | scale_r_mults=[1.5, 3.0, 5.0] |
| ORCAUSDT | gen_871647b8 | 3 | 1.795 | 106% | scale_r_mults=[1.5, 3.0, 5.0] |
| ORCAUSDT | gen_7b4a474b | 3 | 2.215 | 100% | scale_r_mults=[1.5, 3.0, 5.0] |
| ORCAUSDT | gen_5b847426 | 3 | 1.807 | 92% | scale_r_mults=[2.0, 4.0, 6.0] |
| ORCAUSDT | gen_bbe21d3f | 3 | 1.89 | 84% | scale_r_mults=[1.5, 3.0, 5.0] |
| ORCAUSDT | gen_6d06dca0 | 3 | 1.9 | 67% | scale_r_mults=[1.5, 3.0, 5.0] |

## Ultimo run di ottimizzazione
_aggiornato: 2026-09-14 21:39 UTC · 1272 coppie valutate, 0 passate in questo run_

_Nessuna coppia ha passato in questo run._

## Dove muoiono le candidate (autopsia del GATE 1)

**strategie base** — 1272 valutazioni, 0 passate (0.00%) · 2026-09-14 21:39 UTC

| Criterio che ferma | Casi | Quota |
|---|---|---|
| regime | 34 | 2.7% |
| pf_ex_top | 11 | 0.9% |
| holdout | 3 | 0.2% |
| total_return | 1122 | 88.2% |
| trades | 7 | 0.6% |
| recovery | 77 | 6.1% |
| consistency | 18 | 1.4% |

- quasi-passaggi (un solo criterio, di poco): **4** — sono i semi delle mutazioni del run successivo

**strategie generate** — 76608 valutazioni, 176 passate (0.23%) · 2026-09-14 20:20 UTC

| Criterio che ferma | Casi | Quota |
|---|---|---|
| regime | 11850 | 15.5% |
| pf_ex_top | 1049 | 1.4% |
| holdout | 529 | 0.7% |
| total_return | 53348 | 69.8% |
| recovery | 6551 | 8.6% |
| consistency | 2132 | 2.8% |
| trades | 966 | 1.3% |
| win_rate | 7 | 0.0% |

- quasi-passaggi (un solo criterio, di poco): **40** — sono i semi delle mutazioni del run successivo

## Supervisore (taratura automatica)

- ultimo giro: 2026-09-14 23:01 UTC · coppie validate: **8** · GATE 1 pronto: False
- tasso di passaggio misurato: **0.226%**

**Parametri modificati rispetto ai default:**

| Parametro | Valore |
|---|---|
| GATE_WIN_RATE_FLOOR | 0.396614 |

**Ultime decisioni:**

- `none` — solo 0.5 giorni senza validate: si aspetta (2 giorni) prima di toccare qualcosa
- `none` — solo 0.4 giorni senza validate: si aspetta (2 giorni) prima di toccare qualcosa
- `none` — solo 0.4 giorni senza validate: si aspetta (2 giorni) prima di toccare qualcosa
- `none` — solo 0.3 giorni senza validate: si aspetta (2 giorni) prima di toccare qualcosa
- `none` — solo 0.3 giorni senza validate: si aspetta (2 giorni) prima di toccare qualcosa

## Trade chiusi
_nessun trade chiuso._

## Deriva paper vs gate
_nessun verdetto ancora: servono trade chiusi su coppie validate._

## Calibrazione della confidenza
_la confidenza del segnale modula size e leva: qui si verifica che predica davvero l'esito, invece di darlo per scontato._

- verdetto: **insufficient** · 0 trade · correlazione None · influenza applicata **x1.0**
- servono 30 trade, ce ne sono 0
