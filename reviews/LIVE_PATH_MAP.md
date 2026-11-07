# Mappa del percorso degli ordini

Prima versione: 7 nov 2026, dal codice del commit `b29f5713` (branch `claude/brave-albattani-1b12fv`).
**Copertura parziale**: solo i limiti fissi (`bot/risk/`) e la lettura dei parametri della dashboard. Le parti segnate
«da verificare» si completano con la revisione completa del percorso (non ancora fatta).

## 1. File e cartelle del percorso

| Parte | Dove | Stato in questa mappa |
|---|---|---|
| Limiti fissi | `bot/risk/hard_limits.py` (57 righe) | mappato |
| Interruttori (perdita del giorno, stop di fila, eventi macro) | `bot/risk/circuit_breakers.py` | mappato |
| Gestore del rischio (precedenza e ultimo cancello) | `bot/risk/risk_manager.py` | mappato |
| Pulsante che chiude tutto (vecchio bot) | `bot/risk/kill_switch.py`, `bot/main.py:860-872`, `:1585` | in parte |
| Altri controlli di rischio | `bot/risk/daily_cap.py`, `correlation_guard.py`, `portafoglio.py`, `setup_check.py` | da verificare |
| Parametri della dashboard | `bot/main.py:610-619`, `bot/core/models.py:187-196`, `firebase/firestore.rules:32-41`, `dashboard/app/lib/hardLimits.ts` | mappato |
| G1 sul demo | `bot/portafoglio/demo_binance.py` | solo le costanti |
| Esecuzione degli ordini | `bot/execution/` | da verificare |
| Paper F5/G1 | `bot/portafoglio/f5.py` | da verificare |
| Configurazione | `bot/config.py` | solo le voci di rischio |

## 2. Limiti fissi (`bot/risk/hard_limits.py`)

| Invariante | Valore | Riga | Dove si applica |
|---|---|---|---|
| Leva massima | `MAX_LEVERAGE = 5.0` | `:17` | `safety_leverage_cap` `:46`; `risk_manager.py:77,83,93` (precedenza, leva intera); `risk_manager.py:212-214` (ultimo cancello) |
| Rischio per operazione | `MAX_RISK_PER_TRADE = 0.03` | `:18` | `safety_risk_cap` `:53-57`; `risk_manager.py:79,94,215-217` |
| Perdita giornaliera massima | `DAILY_LOSS_LIMIT = 0.05` | `:21` | `circuit_breakers.py:79` (fermo del giorno), `:57-58` (messaggio) |
| Stop di fila prima della pausa | `CONSECUTIVE_SL_LIMIT = 6` | `:25` | `circuit_breakers.py:85` |
| Durata della pausa | `CONSECUTIVE_SL_PAUSE = 2 h` | `:26` | `circuit_breakers.py:86` (la nota a `:88` dice «4h»: testo sbagliato) |
| Rischio dimezzato in alta volatilità | `HIGH_VOL_SIGMA = 3.0`, `HIGH_VOL_SIZE_FACTOR = 0.5` | `:27-28` | `safety_risk_cap` |
| Finestra senza posizioni attorno agli eventi macro | `MACRO_FLAT_HOURS = 2.0` | `:29` | `circuit_breakers.py:92-101` |
| Leva ridotta con la volatilità | 3σ→2x, 2σ→3x, 1.5σ→4x | `:33-37` | `safety_leverage_cap` `:40-50`: sotto 1.5σ il tetto è `MAX_LEVERAGE` |

Il numero massimo di posizioni NON sta qui: `settings.MAX_OPEN_POSITIONS` (`bot/config.py:176`, da variabile d'ambiente,
predefinito 5), applicato a `bot/main.py:1741`.

**Test che fanno da guardia** (devono restare verdi, e il loro fallimento è un allarme, non un test da correggere):
`tests/test_risk.py:32` (leva 10 chiesta → 5, con `MAX_LEVERAGE == 5.0` scritto nel test), `:41` (rischio 3%), `:75`
(fermo del giorno a −6%), `:84` (nessun fermo a −2,1%), `:94` (pausa dopo 6 stop), `:103` (ultimo cancello);
`tests/test_sizing.py:104` (leva fra 1 e 5 anche con il moltiplicatore 1,3).

## 3. Interruttori (`bot/risk/circuit_breakers.py`)

- Stato in RTDB `/risk_state`: caricato a `bot/main.py:516`, salvato da `_persist_risk_state` (`bot/main.py:2157-2158`).
- `register_trade_result` (`:72-90`) è chiamato a ogni chiusura: `bot/main.py:1523` (uscite della strategia) e
  `:1549` (chiusure manuali). Un'eccezione lì dentro esce da `trading_cycle` e salta il resto del ciclo, compreso il
  pulsante che chiude tutto a `bot/main.py:1585` (eccezione presa solo dal ciclo principale a `bot/main.py:2603-2607`, che la stampa e la conta).
- Il controllo entra nel cancello finale: `risk_manager.py:220`.
- **Interruttore in configurazione (preesistente)**: con `BACKTEST_PARITY=true` (variabile d'ambiente, `bot/config.py:672`)
  `blocking_reason` torna sempre `None` (`circuit_breakers.py:50-52`) e salta il tetto delle posizioni (`bot/main.py:1741`).

## 4. Parametri della dashboard

Catena: dashboard (`dashboard/app/components/RiskControl.tsx:55,108`) → Firestore `user_risk_settings/current` →
`read_user_risk` (`bot/main.py:610-619`, riletto prima di ogni trade) → `RiskSettings` (`bot/core/models.py:187-196`:
solo `leverage`, `risk_per_trade`, `updated_at`, `updated_by`; i campi in più si scartano) → `risk_manager.py:63-94`.

| Controllo | Dove | Comportamento |
|---|---|---|
| Dashboard | `dashboard/app/lib/hardLimits.ts:13-17` | taglia a 1-5x e 0,5-3% prima di scrivere (comodità, non sicurezza) |
| Regole Firestore | `firebase/firestore.rules:32-41` | scrittura solo del proprietario, leva 1-5, rischio (0, 3%]; **non limita gli altri campi**; utente `REPLACE_WITH_YOUR_FIREBASE_UID` (`:27`): regole pubblicate da confermare con Alessio |
| Bot | `bot/main.py:616-619` | documento illeggibile → valori predefiniti in silenzio (2x, 1%) |
| Bot | `risk_manager.py:77-80`, `:212-217` | valore oltre il limite → **tagliato con una nota**, non rifiutato con un allarme (preesistente) |

Il bot usa l'Admin SDK: le regole di Firestore non lo limitano (`firebase/firestore.rules:6-8`).

## 5. Limiti propri di G1 sul demo (`bot/portafoglio/demo_binance.py`)

Costanti nel codice, **fuori da `hard_limits.py`**, non lette da `hard_limits`: leva `LEVA = 5` (`:73`, inviata a Binance a
`:639`), stop sul conto `STOP_CONTO = 0.35` dal massimo (`:78`, controllo a `:702`), quota degli eventi `QUOTA_EVENTI = 0.05` (`:71`).
Pulsante che chiude tutto del demo: RTDB `/commands/demo_binance_chiudi_tutto` (`:84`, letto a `:490`) oppure il file
`ops/demo_binance_chiudi_tutto` (`:88`, funziona senza Firebase); esecuzione in `chiudi_tutto` (`:452`).

## 6. Paper, demo e conto vero (da verificare nella revisione completa)

- `DRY_RUN` da variabile d'ambiente, predefinito vero: `bot/config.py:64`.
- Il client del demo rifiuta ogni indirizzo diverso da `demo-fapi.binance.com`: `demo_binance.py:64-65,96-99`.

## 7. Da completare nella revisione completa

Ordini (passi, minimi, identificativi, solo riduzione, leva e margine), stop registrati su Binance, ricostruzione dello
stato all'avvio, flussi in tempo reale, errori delle interfacce, pulsante che chiude tutto del vecchio bot quando Firebase
non risponde, `daily_cap.py` e `correlation_guard.py`, paper F5/G1, separazione completa fra paper, demo e conto vero.

## Storia degli invarianti

- 7 nov 2026: nessun invariante cambiato nel codice. Una modifica proposta (leva massima 10, perdita giornaliera dalla
  dashboard) ha avuto REQUEST CHANGES: `reviews/reports/2026-11-07-limiti-leva-perdita-giornaliera.md`.
