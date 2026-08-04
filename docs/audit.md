# AUDIT COMPLETO DEL SISTEMA
_Ultimo aggiornamento: 2026-08-04 (post blocchi A-D) · 249 test verdi_

> **Blocchi A, B, C, D implementati.** Le voci risolte sono marcate ✅ RISOLTO
> con il riferimento al commit. Restano aperte solo le voci elencate in §7.

Stato di **ogni** logica, fase e attività. Legenda:
**✅ verificato** · **⚠️ funziona con riserve** · **🔴 difetto/mancante** · **⛔ codice morto**

---

## 1. GATE 1 — validazione delle strategie

| Logica | Stato | Note |
|---|---|---|
| Walk-forward su finestre train/OOS | ✅ | `optimizer.optimize_symbol` |
| Holdout finale mai visto dalla selezione | ✅ | 45g rolling, esclusi da train e finestre |
| Pass onesto (solo con ≥24h dati nuovi) | ✅ | fail-closed: senza `data_end` non conta |
| Criteri: PF≥1.25, ≥30 trade, ritorno≥15%, ogni finestra positiva | ✅ | `passes_gate` |
| **Continuità**: ritorno/maxDD ≥ 2 | ✅ | rende operativo "profitto continuo" |
| Score = ritorno − drawdown (+PF) | ✅ | preferisce curve lisce a parità di guadagno |
| **Recency**: parametri pesati sul presente (emivita 180g) | ✅ | pesa la *selezione*, non i criteri |
| Scala TP per coppia (classiche, via grid) | ✅ | `rr` morto sostituito dalla scala |
| Scala TP per coppia (generate) | ✅ | in `discover`, solo sui passer |
| PF per-regime esportato | ✅ | alimenta il veto live |
| Auto-purge dopo 2 fallimenti consecutivi | ✅ | |
| Parità gate ↔ paper (costi, uscite, orizzonte) | ✅ | moduli condivisi, verificata riga per riga |
| Break-even dopo TP1 | ✅ RISOLTO | `sl_to_breakeven` nella griglia [True, False], validato per coppia (C1) |
| **Holdout consultato a ogni run** | ⚠️ | rolling mitiga, non azzera il riuso. Il vero OOS finale resta il paper |
| Profittabilità per regime | ✅ RISOLTO | `GATE_REGIME_MIN_PF`: nessun regime può essere un buco conclamato (C2) |
| Generatore: feature di condizione | ✅ RISOLTO | volatilità, ADX, volume, sessione oraria (C3). Restano fuori: funding e multi-timeframe |
| Diversificazione di portafoglio | ✅ RISOLTO | correlation guard collegato + tetto direzionale (blocco A) |

**Traiettoria attuale**: 3%→28% copertura in 3 giorni, ~3 coppie promosse per run su 1432 valutate. Profili plausibili (PF 1.37–1.55, 94–305 trade), non più i PF 4+ della lotteria.

---

## 2. PAPER (GATE 2) — fedeltà dell'esecuzione

| Logica | Stato | Note |
|---|---|---|
| Costi identici al gate (fee, spread per liquidità, funding con segno) | ✅ | `bot/core/costs.py` |
| Fill sulle ombre (wick) | ✅ | allineato al gate e a Binance reale |
| Stream prezzi + replay ordinato del percorso | ✅ | `bookTicker`, invariante di fedeltà verificata |
| Fallback su candele REST per simbolo | ✅ | degradazione automatica |
| Contabilità: realizzo parziale, margine liberato, nessun doppio conteggio | ✅ | testato |
| Scala TP congelata all'ingresso, persistita | ✅ | una passata non cambia i TP di un trade aperto |
| Orizzonte 96 barre = gate | ✅ | |
| `mfe_r` registrato su ogni trade | ✅ | abilita drift e taratura scala |
| **Slippage d'ingresso non modellato** | ⚠️ | il gate entra a chiusura candela, il live pochi secondi dopo. Mitigato dal costo fisso, non misurato |
| **Calibrazione costi dal vissuto** | 🔴 | impossibile in DRY_RUN: il paper *simula* i costi con lo stesso modello. Disponibile solo in live |

---

## 3. LEARNING — cosa si adatta e con che ritmo

| Cosa | Chi lo adatta | Ritmo | Stato |
|---|---|---|---|
| Pesi strategia×regime | learning (paper) | ogni trade chiuso | ✅ |
| Leva | learning | ogni apertura | ✅ |
| Rischio/size | learning | ogni apertura | ✅ |
| `keep` del trailing | learning (verdetti controfattuali) | orario | ✅ |
| Panchina strategia / cooldown coin | automatico su serie di stop | immediato | ✅ |
| Scala TP | **gate** | per passata | ✅ |
| Veto di regime | **gate** → prior immediato | per passata | ✅ |
| **Deriva paper→gate** | drift detector | ogni refresh | ✅ |
| Probation (rientro graduale dopo kill) | learning | giornaliero | ✅ |
| Quota baseline non adattata (20%) | anti-overfitting | — | ✅ |
| **Parametri d'ingresso (soglie RSI/BB/ADX, `atr_mult_stop`)** | solo gate, mai paper | per passata | ⚠️ **by design**: tararli sul paper lo consumerebbe come training set |
| Sentiment come segnale d'ingresso | — | — | ⚠️ solo riduzione size; non validato né validabile (manca storico) |

**Anello chiuso**: gate promette → paper misura → drift frena subito e accusa → gate rivaluta su storia aggiornata → parametri nuovi. La freccia di ritorno esiste ora in entrambi i sensi.

---

## 4. RISCHIO — 🔴 la sezione con i buchi veri

| Controllo | Stato | Note |
|---|---|---|
| Hard cap leva/size non modificabili | ✅ | `hard_limits.py`, fuori dalla portata di config/LLM/Firebase |
| Stop-loss obbligatorio (no ATR → nessun trade) | ✅ | |
| Circuit breaker giornaliero −5% | ✅ | verificato sul campo il 30/07 |
| Pausa dopo N stop consecutivi | ✅ | |
| Kill switch a prezzi freschi | ✅ | |
| Cap posizioni aperte (5) | ✅ | |
| Cap margine per posizione | ✅ | |
| **Correlation guard** | ✅ RISOLTO | collegato al percorso di apertura, cache prezzi 30 min, fail-open senza storico (A1) |
| **Macro agent** | ✅ RIMOSSO | `upcoming_high_impact_events()` era un placeholder che ritornava `[]`: collegarlo non avrebbe fatto nulla. Il bot **non** si mette flat sugli eventi macro — serve una fonte di calendario (A3) |
| Esposizione direzionale netta | ✅ RISOLTO | `MAX_DIRECTIONAL_RISK_PCT` 3%: somma il rischio vero nello stesso verso, usa lo stop ORIGINALE (A2) |

> **Correzione a una mia affermazione precedente**: avevo detto che la diversificazione di portafoglio "la fa il cap di correlazione live". **Non è vero**: quel modulo non è collegato. È il difetto più serio emerso da questo audit.

---

## 5. ESECUZIONE LIVE (non attiva — `DRY_RUN=true`)

| Logica | Stato | Note |
|---|---|---|
| Scala TP completa sul book | ✅ | un ordine per gradino, quote corrette, no dust |
| Stop risincronizzato (BE / profit-lock) | ✅ | cancella-e-ripiazza, fallimento segnalato |
| Cancellazione ordini orfani alla chiusura | ✅ | |
| **Conferma dei fill (ingresso)** | ✅ RISOLTO | attesa + riconciliazione qty/prezzo reali; sotto soglia si chiude il residuo (B1) |
| Riconciliazione quantità/prezzi (ingresso) | ✅ RISOLTO | entry = prezzo medio eseguito → R e scala TP corretti |
| Fill parziali dell'ingresso | ✅ RISOLTO | sopra soglia riconcilia, sotto chiude il residuo |

---

## 6. INFRASTRUTTURA E OSSERVABILITÀ

| Elemento | Stato |
|---|---|
| WAL sui trade chiusi (mai persi) | ✅ |
| Ripristino posizioni dopo restart | ✅ |
| Retry su 429 + pacing | ✅ |
| Snapshot automatico con diagnosi (uscite, gradini, mfe, deriva) | ✅ |
| Dashboard: operatività, equity, learning, trailing, sentiment | ✅ |
| 9 workflow GitHub (test, optimize, discover, learning, snapshot, monitoring…) | ✅ |
| 226 test | ✅ |
| Falso "🔴 offline" | ✅ RISOLTO | soglia 180s → 900s (D1) |
| `backtesting/report.py` usato solo da `run.py` | ⚠️ marginale |

---

## 7. COSA RESTA APERTO (dopo A-D)

| Voce | Stato | Nota |
|---|---|---|
| **Fill delle USCITE in live** | 🔴 **bloccante** | TP/SL scattati sull'exchange sono ancora *dedotti* dal prezzo, non letti. Va chiuso prima del reale |
| Calibrazione costi dal vissuto | 🔴 | impossibile in DRY_RUN (il paper simula coi costi del modello). Disponibile dopo i fill reali |
| Flat sugli eventi macro | 🔴 | serve una fonte di calendario economico |
| Slippage d'ingresso | ⚠️ | non modellato, mitigato dal costo fisso |
| Holdout consultato ogni run | ⚠️ | rolling mitiga, non azzera. Il vero OOS resta il paper |
| Generatore: funding e multi-timeframe | ⚠️ | le feature di condizione ci sono, queste no |

## 8. PRIORITÀ STORICHE (blocchi A-D — completati)

**Blocco A — rischio (il più urgente, indipendente dal resto)**
1. Collegare il **correlation guard** al percorso di apertura
2. Limite di **esposizione direzionale netta**
3. Decidere sul **macro agent**: collegarlo o rimuoverlo (codice morto documentato = trappola)

**Blocco B — prima del live**
4. **Conferma dei fill** + riconciliazione (bloccante assoluto)
5. Calibrazione costi dal vissuto reale (possibile solo dopo il 4)

**Blocco C — qualità del gate, dopo il primo paper pulito**
6. Break-even nello spazio di ricerca per coppia
7. Requisito di profittabilità per-regime nella validazione
8. Feature non tecniche nel generatore (funding, stagionalità, multi-timeframe)

**Blocco D — cosmetico**
9. Soglia heartbeat per il falso "offline"
