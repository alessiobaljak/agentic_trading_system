# AUDIT COMPLETO DEL SISTEMA
_Ultimo aggiornamento: 2026-08-04 · 226 test verdi · 102 file sorgente_

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
| **Break-even dopo TP1 mai isolato in A/B** | ⚠️ | l'A/B confrontò TP-unico vs scale-out-con-BE: il BE non è mai stato testato da solo. Candidato per lo spazio di ricerca per coppia |
| **Holdout consultato a ogni run** | ⚠️ | rolling mitiga, non azzera il riuso. Il vero OOS finale resta il paper |
| Nessun requisito di profittabilità **per regime** | ⚠️ | il veto live copre, ma una coppia può validarsi vivendo di un solo regime |
| Generatore: solo tecnico single-coin, stesso timeframe | ⚠️ | niente funding/stagionalità/multi-timeframe come feature |
| Diversificazione di portafoglio | 🔴 | vedi §4 — non è compito del gate, ma **nessuno** la fa |

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
| **Correlation guard** | ⛔ **CODICE MORTO** | `bot/risk/correlation_guard.py` esiste, è documentato (max 3 posizioni correlate, soglia 0.85) ma **non è importato da nessun file**. Il bot può aprire 5 posizioni perfettamente correlate senza accorgersene |
| **Macro agent** (flat ±2h su FOMC/CPI/NFP) | ⛔ **CODICE MORTO** | `bot/agents/macro_agent.py`, 0 import. Il bot trada dentro gli eventi macro |
| Esposizione direzionale netta | 🔴 | nessun limite: 5 long su micro-cap correlate = una scommessa sola con size 5x |

> **Correzione a una mia affermazione precedente**: avevo detto che la diversificazione di portafoglio "la fa il cap di correlazione live". **Non è vero**: quel modulo non è collegato. È il difetto più serio emerso da questo audit.

---

## 5. ESECUZIONE LIVE (non attiva — `DRY_RUN=true`)

| Logica | Stato | Note |
|---|---|---|
| Scala TP completa sul book | ✅ | un ordine per gradino, quote corrette, no dust |
| Stop risincronizzato (BE / profit-lock) | ✅ | cancella-e-ripiazza, fallimento segnalato |
| Cancellazione ordini orfani alla chiusura | ✅ | |
| **Conferma dei fill** | 🔴 **BLOCCANTE** | il bot piazza un LIMIT e *assume* il fill: la posizione nasce senza verifica. Se il prezzo scappa, gestisce una posizione inesistente |
| Riconciliazione quantità/prezzi reali | 🔴 | conseguenza del precedente |
| Gestione fill parziali dell'ingresso | 🔴 | non prevista |

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
| Falso "🔴 offline" durante gli scan lunghi | ⚠️ cosmetico (heartbeat >180s) |
| `backtesting/report.py` usato solo da `run.py` | ⚠️ marginale |

---

## 7. PRIORITÀ SUGGERITE

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
