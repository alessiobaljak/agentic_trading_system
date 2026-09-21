# 0120-gen6d06-stato.req

_eseguito: 2026-09-21 05:16 UTC_

**richiesta:** `stato`
**eseguito:** `.venv/bin/python -m scripts.state_snapshot --no-write`
**esito:** codice 0 in 3.6s

```
[firebase] connesso (Firestore + RTDB)
# Stato sistema (snapshot)
_Generato: 2026-09-21 05:16 UTC_

## Bot
- stato: **running** (🟢 online)
- regime: sideways
- DRY_RUN: True
- equity: **$983.88**
- ultimo heartbeat: 2026-09-21 05:14 UTC
- stream prezzi: 🟢 attivo

## Ultima decisione
- esito: **⚪ FLAT** (2026-09-21 05:01 UTC)
- motivo: nessun segnale valido sopra soglia
- asset valutati: 25 · segnali: 0

## Posizioni aperte
- GPSUSDT: long qty=7682.3142838174645 @ 0.010285 uPnL=5.372916496167303 · rischio 0.41% · leva 2.0x
- QUSDT: short qty=7712.19822572642 @ 0.025391 uPnL=1.5794526150247816 · rischio 0.31% · leva 2.0x
- STXUSDT: long qty=602.2008214716856 @ 0.3269 uPnL=-3.835757284370027 · rischio 0.54% · leva 2.0x
- TUTUSDT: long qty=9163.189613351007 @ 0.02148 uPnL=-1.9152229771159912 · rischio 0.50% · leva 2.0x
- **rischio aperto totale: 1.76%** dell'equity su 4 posizioni

## GATE 1 — Validazione strategie
- stato: **✅ SUPERATO — pronti per il paper trading**
- copertura universo: **26/164 crypto (16%)** · obiettivo ≥ 35%
- coppie validate (>= 3 pass OOS): **56**
- universo scansionato: 0GUSDT, 1000BONKUSDT, 1000FLOKIUSDT, 1000LUNCUSDT, 1000PEPEUSDT, 1000SHIBUSDT, AAVEUSDT, ACEUSDT, ADAUSDT, AEROUSDT, AGLDUSDT, AINUSDT, ALGOUSDT, APTUSDT, ARBUSDT, ARKUSDT, ARUSDT, ASTERUSDT, ATOMUSDT, AVAAIUSDT, AVAUSDT, AVAXUSDT, AXSUSDT, B2USDT, BANKUSDT, BCHUSDT, BERAUSDT, BNBUSDT, BOMEUSDT, BRUSDT, BTCUSDT, BULLAUSDT, CAKEUSDT, CELRUSDT, CFXUSDT, CHZUSDT, COMPUSDT, COTIUSDT, CRVUSDT, CTSIUSDT, CUSDT, CYBERUSDT, DASHUSDT, DEXEUSDT, DOGEUSDT, DOTUSDT, DRIFTUSDT, EGLDUSDT, EIGENUSDT, ENAUSDT, ENSUSDT, EPICUSDT, ETCUSDT, ETHFIUSDT, ETHUSDT, FARTCOINUSDT, FETUSDT, FILUSDT, FLOCKUSDT, FUSDT, GALAUSDT, GPSUSDT, GRTUSDT, GUNUSDT, GUSDT, HBARUSDT, HEIUSDT, HEMIUSDT, HOMEUSDT, HUSDT, HYPEUSDT, ICPUSDT, INJUSDT, IOSTUSDT, IOTAUSDT, JSTUSDT, JTOUSDT, JUPUSDT, KAITOUSDT, KASUSDT, KMNOUSDT, LAUSDT, LDOUSDT, LINKUSDT, LSKUSDT, LTCUSDT, LUNA2USDT, MANTAUSDT, MASKUSDT, MINAUSDT, MITOUSDT, MORPHOUSDT, MUBARAKUSDT, MUSDT, MYXUSDT, NEARUSDT, NEIROUSDT, NILUSDT, ONDOUSDT, ONEUSDT, ONGUSDT, OPUSDT, ORDIUSDT, PAXGUSDT, PENDLEUSDT, PENGUUSDT, PEOPLEUSDT, PLUMEUSDT, POLUSDT, PROMUSDT, PROVEUSDT, PTBUSDT, PUMPUSDT, PYTHUSDT, QUSDT, RAYSOLUSDT, RENDERUSDT, REZUSDT, SAGAUSDT, SANDUSDT, SEIUSDT, SKLUSDT, SKYUSDT, SOLUSDT, SOLVUSDT, SOPHUSDT, SPXUSDT, STGUSDT, STRKUSDT, STXUSDT, SUIUSDT, SUSDT, SUSHIUSDT, SYNUSDT, TAOUSDT, TIAUSDT, TRUMPUSDT, TRXUSDT, TUSDT, TUTUSDT, UBUSDT, UNIUSDT, USELESSUSDT, USTCUSDT, USUALUSDT, VELVETUSDT, VETUSDT, VIRTUALUSDT, VTHOUSDT, VVVUSDT, WIFUSDT, WLDUSDT, WLFIUSDT, WUSDT, XLMUSDT, XMRUSDT, XPLUSDT, XRPUSDT, XTZUSDT, ZECUSDT, ZENUSDT, ZILUSDT, ZKUSDT, ZROUSDT
- aggiornato: 2026-09-21 03:45 UTC

### Salute del registro

- composizione: **2008 base** · **667 generate** (di cui 667 con almeno una conferma)
- occupazione: 2675/3000 — ok

### Strategie VALIDATE (operate dal bot)
| Coin | Strategia | Passes | PF | PnL OOS | Parametri |
|---|---|---|---|---|---|
| HEIUSDT | gen_e6ddc613 | 3 | 2.441 | 212% | scale_r_mults=[2.0, 4.0, 6.0] |
| JASMYUSDT | gen_b2f350ff | 3 | 1.603 | 137% | scale_r_mults=[2.0, 4.0, 6.0] |
| VETUSDT | gen_6d06dca0 | 3 | 1.631 | 126% | scale_r_mults=[2.0, 4.0, 6.0] |
| TUTUSDT | gen_4465723e | 3 | 1.522 | 126% | scale_r_mults=[1.5, 3.0, 5.0] |
| DOTUSDT | gen_d85b1f05 | 3 | 1.562 | 123% | scale_r_mults=[1.5, 3.0, 5.0] |
| DOTUSDT | gen_da39a23a | 3 | 1.488 | 118% | scale_r_mults=[1.5, 3.0, 5.0] |
| MUBARAKUSDT | gen_1f7ead60 | 3 | 2.776 | 114% | scale_r_mults=[2.0, 4.0, 6.0] |
| GPSUSDT | gen_bf1e00d4 | 3 | 1.587 | 114% | scale_r_mults=[1.5, 3.0, 5.0] |
| ORCAUSDT | gen_271ab7ec | 3 | 1.851 | 113% | scale_r_mults=[1.0, 2.0, 3.0] |
| ORCAUSDT | gen_e6ddc613 | 3 | 1.862 | 113% | scale_r_mults=[1.5, 3.0, 5.0] |
| ORCAUSDT | gen_9a383fff | 3 | 1.909 | 112% | scale_r_mults=[1.5, 3.0, 5.0] |
| ORCAUSDT | gen_871647b8 | 3 | 1.859 | 111% | scale_r_mults=[1.5, 3.0, 5.0] |
| SKYAIUSDT | gen_6cf80ae6 | 3 | 3.08 | 111% | scale_r_mults=[2.0, 4.0, 6.0] |
| ORCAUSDT | gen_7b4a474b | 3 | 2.293 | 103% | scale_r_mults=[1.5, 3.0, 5.0] |
| STXUSDT | gen_b9bf5d01 | 3 | 1.54 | 103% | scale_r_mults=[2.0, 4.0, 6.0] |
| PROMUSDT | gen_cd5c842f | 3 | 1.628 | 99% | scale_r_mults=[2.0, 4.0, 6.0] |
| SKYAIUSDT | gen_c61d9322 | 3 | 2.511 | 99% | scale_r_mults=[2.0, 4.0, 6.0] |
| DEXEUSDT | gen_b31d8b93 | 3 | 1.952 | 98% | scale_r_mults=[1.5, 3.0, 5.0] |
| ORCAUSDT | gen_5b847426 | 3 | 1.859 | 96% | scale_r_mults=[2.0, 4.0, 6.0] |
| DOTUSDT | gen_919c110c | 3 | 1.492 | 96% | scale_r_mults=[2.0, 4.0, 6.0] |
| DEXEUSDT | gen_fa304106 | 3 | 2.06 | 95% | scale_r_mults=[1.5, 3.0, 5.0] |
| GPSUSDT | gen_871647b8 | 3 | 1.491 | 94% | scale_r_mults=[2.0, 4.0, 6.0] |
| SPXUSDT | gen_725cb5f4 | 3 | 1.708 | 92% | scale_r_mults=[0.75, 1.5, 3.0] |
| ORCAUSDT | gen_bbe21d3f | 3 | 1.952 | 87% | scale_r_mults=[1.5, 3.0, 5.0] |
| STXUSDT | gen_14e1775b | 3 | 1.74 | 87% | scale_r_mults=[2.0, 4.0, 6.0] |
| STXUSDT | gen_68ebd3b9 | 3 | 1.748 | 86% | scale_r_mults=[2.0, 4.0, 6.0] |
| SKYAIUSDT | gen_98837ec2 | 3 | 2.471 | 85% | scale_r_mults=[2.0, 4.0, 6.0] |
| SPXUSDT | gen_ba3a671f | 3 | 1.644 | 84% | scale_r_mults=[0.75, 1.5, 3.0] |
| SEIUSDT | gen_4f890271 | 3 | 1.851 | 82% | scale_r_mults=[2.0, 4.0, 6.0] |
| MUBARAKUSDT | gen_ff3e4154 | 3 | 1.668 | 81% | scale_r_mults=[2.0, 4.0, 6.0] |
| USELESSUSDT | gen_194e2514 | 3 | 1.541 | 77% | scale_r_mults=[2.0, 4.0, 6.0] |
| USELESSUSDT | gen_1bb04e1a | 3 | 1.541 | 77% | scale_r_mults=[2.0, 4.0, 6.0] |
| BICOUSDT | gen_f238d283 | 3 | 1.518 | 76% | scale_r_mults=[1.5, 3.0, 5.0] |
| PROMUSDT | gen_452d4511 | 3 | 2.146 | 75% | scale_r_mults=[2.0, 4.0, 6.0] |
| SKYAIUSDT | gen_eb2ece0c | 3 | 3.299 | 73% | scale_r_mults=[2.0, 4.0, 6.0] |
| JTOUSDT | gen_f238d283 | 3 | 1.426 | 72% | scale_r_mults=[1.5, 3.0, 5.0] |
| USELESSUSDT | gen_2031005e | 3 | 1.54 | 72% | scale_r_mults=[2.0, 4.0, 6.0] |
| ORCAUSDT | gen_6d06dca0 | 3 | 1.967 | 70% | scale_r_mults=[1.5, 3.0, 5.0] |
| TRUMPUSDT | gen_0e000630 | 3 | 2.223 | 66% | scale_r_mults=[2.0, 4.0, 6.0] |
| SPXUSDT | gen_d53c153b | 3 | 1.824 | 58% | scale_r_mults=[1.5, 3.0, 5.0] |
| NEIROUSDT | gen_f3124a14 | 3 | 1.572 | 56% | scale_r_mults=[1.5, 3.0, 5.0] |
| EGLDUSDT | gen_36b0e335 | 3 | 1.455 | 56% | scale_r_mults=[1.5, 3.0, 5.0] |
| NEIROUSDT | gen_d53c153b | 3 | 1.808 | 49% | scale_r_mults=[1.0, 2.0, 3.0] |
| QUSDT | gen_bf2be656 | 3 | 3.106 | 48% | scale_r_mults=[0.75, 2.0, 3.0] |
| NEIROUSDT | gen_e132204b | 3 | 1.524 | 44% | scale_r_mults=[1.5, 3.0, 5.0] |
| SAHARAUSDT | gen_6b94025f | 3 | 2.205 | 44% | scale_r_mults=[1.0, 2.0, 3.0] |
| QUSDT | gen_18c839a0 | 3 | 2.443 | 44% | scale_r_mults=[1.0, 1.5, 2.5] |
| SCRUSDT | gen_63712f8e | 3 | 2.302 | 43% | scale_r_mults=[1.0, 2.0, 3.0] |
| HEMIUSDT | gen_108c996b | 3 | 1.986 | 40% | scale_r_mults=[2.0, 4.0, 6.0] |
| HEMIUSDT | gen_93131ef1 | 3 | 1.986 | 40% | scale_r_mults=[2.0, 4.0, 6.0] |
| SYRUPUSDT | gen_af734c68 | 3 | 1.726 | 38% | scale_r_mults=[2.0, 4.0, 6.0] |
| MUBARAKUSDT | gen_2053cba6 | 3 | 1.446 | 28% | scale_r_mults=[2.0, 4.0, 6.0] |
| MUBARAKUSDT | gen_1e2af031 | 3 | 1.771 | 24% | scale_r_mults=[2.0, 4.0, 6.0] |
| TRUMPUSDT | gen_108c996b | 3 | 1.732 | 24% | scale_r_mults=[2.0, 4.0, 6.0] |
| TRUMPUSDT | gen_93131ef1 | 3 | 1.732 | 24% | scale_r_mults=[2.0, 4.0, 6.0] |
| ZKUSDT | gen_98837ec2 | 3 | 1.476 | 22% | scale_r_mults=[2.0, 4.0, 6.0] |

## Ultimo run di ottimizzazione
_aggiornato: 2026-09-21 03:45 UTC · 1312 coppie valutate, 1 passate in questo run_

| Coin | Strategia | PF | PnL OOS | Trade | Win |
|---|---|---|---|---|---|
| GRTUSDT | mean_reversion | 1.563 | 70% | 178 | 47% |

## Dove muoiono le candidate (autopsia del GATE 1)

**strategie base** — 1312 valutazioni, 1 passate (0.08%) · 2026-09-21 03:45 UTC

| Criterio che ferma | Casi | Quota |
|---|---|---|
| consistency | 19 | 1.4% |
| regime | 37 | 2.8% |
| holdout | 3 | 0.2% |
| recovery | 77 | 5.9% |
| pf_ex_top | 12 | 0.9% |
| trades | 8 | 0.6% |
| total_return | 1155 | 88.1% |

- quasi-passaggi (un solo criterio, di poco): **3** — sono i semi delle mutazioni del run successivo

**strategie generate** — 114062 valutazioni, 340 passate (0.30%) · 2026-09-21 02:56 UTC

| Criterio che ferma | Casi | Quota |
|---|---|---|
| win_rate | 20 | 0.0% |
| holdout | 980 | 0.9% |
| pf_ex_top | 1703 | 1.5% |
| trades | 1345 | 1.2% |
| consistency | 3405 | 3.0% |
| total_return | 77543 | 68.2% |
| recovery | 10421 | 9.2% |
| regime | 18305 | 16.1% |

- quasi-passaggi (un solo criterio, di poco): **40** — sono i semi delle mutazioni del run successivo

## Supervisore (taratura automatica)

- ultimo giro: 2026-09-21 05:04 UTC · coppie validate: **56** · GATE 1 pronto: True
- tasso di passaggio misurato: **0.296%**

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
- totale: **21** · vinti: 5 (24%) · PnL realizzato: **-23.24**
- confronto col mercato: noi -2.32% vs BTC buy&hold +7.38% nello stesso periodo → **sotto** il mercato

- costi: **6.41 USDT** su 21 trade (0.30/trade) _(stimati dal modello del gate, non misurati dai fill)_
  - commissioni 3.33 · spread 3.12 · funding -0.04
  - lordo -16.83 → netto -23.24 · **break-even 0.65%** dell'equity
  - piu' costose: DEXEUSDT 1.91 · SPXUSDT 0.96 · SYRUPUSDT 0.63 · ORCAUSDT 0.62 · VETUSDT 0.54

| Uscita | Trade | % | PnL |
|---|---|---|---|
| Stop loss (prima di qualsiasi TP) | 16 | 76% | -49.95 |
| Scale-out (>=1 TP incassato, residuo a BE) | 3 | 14% | +5.93 |
| Take profit (fino all'ultimo gradino) | 2 | 10% | +20.78 |

- gradini raggiunti (su 21 trade): 0 TP: 16 (76%) · 1 TP: 3 (14%) · 3 TP: 2 (10%)

- **drawdown di portafoglio: 23.24 USDT** (ritorno -23.24 · recovery -1.00) · max 4 posizioni aperte insieme
  _uscite in ordine di TEMPO: e' la buca vera, quella che il gate non vede perche' valida una coppia alla volta._

- escursione favorevole (mfe_r, 21 trade): mediana **0.74R** · ≥1R: 38% · ≥1.5R: 29% · ≥3R: 10% · ≥5R: 5%
  _quanto lontano arriva il prezzo, in unità di R: dice se la scala di TP è raggiungibile. Dettaglio: `python -m scripts.mfe_report`_

## Deriva paper vs gate
_il gate promette sulla storia, il paper misura il presente. `drift` = promessa contraddetta -> size/leva frenate subito e fallimento al gate alla prossima passata._

- **globale**: watch · 21 trade · PF vissuto 0.535 vs 1.894 atteso · mfe mediana 0.74R

| Coppia | Verdetto | Trade | PF vissuto/atteso | Motivo |
|---|---|---|---|---|
| DEXEUSDT|gen_fa304106 | watch | 4 | 0.0 / 2.06 | PF 0.00 vs 2.06 atteso · mfe mediana 0.52R < primo TP 1.50R |
| SPXUSDT|gen_ba3a671f | watch | 3 | 0.0 / 1.644 | PF 0.00 vs 1.64 atteso · mfe mediana 0.30R < primo TP 0.75R |
| SYRUPUSDT|gen_af734c68 | watch | 2 | 0.0 / 1.726 | PF 0.00 vs 1.73 atteso · mfe mediana 0.94R < primo TP 2.00R |
| DEXEUSDT|gen_b31d8b93 | watch | 2 | 0.37 / 1.952 | PF 0.37 vs 1.95 atteso |
| VETUSDT|gen_6d06dca0 | watch | 2 | 0.0 / 1.631 | PF 0.00 vs 1.63 atteso |
| ORCAUSDT|gen_6d06dca0 | watch | 2 | 0.0 / 1.967 | PF 0.00 vs 1.97 atteso · mfe mediana 1.05R < primo TP 1.50R |
| TUTUSDT|gen_4465723e | watch | 1 | 0.0 / 1.522 | PF 0.00 vs 1.52 atteso · mfe mediana 0.69R < primo TP 1.50R |
| STXUSDT|gen_b9bf5d01 | watch | 1 | 0.0 / 1.54 | PF 0.00 vs 1.54 atteso · mfe mediana 0.74R < primo TP 2.00R |

## Calibrazione della confidenza
_la confidenza del segnale modula size e leva: qui si verifica che predica davvero l'esito, invece di darlo per scontato._

- verdetto: **insufficient** · 21 trade · correlazione None · influenza applicata **x1.0**
- servono 30 trade, ce ne sono 21

| Fascia di confidenza | Trade | Win rate | Esito medio |
|---|---|---|---|
| 60.0–60.0 | 7 | 29% | -0.59% |
| 60.0–60.0 | 7 | 29% | -0.80% |
| 60.0–60.0 | 7 | 14% | -1.95% |

_se l'esito medio CRESCE dalla fascia bassa all'alta, la confidenza ordina correttamente i trade._


--- stderr ---
/root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
  return query.where(field_path, op_string, value)
```
