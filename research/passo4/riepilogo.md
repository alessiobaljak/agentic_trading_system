# Riepilogo del Passo 4 (protocollo 4.5) — 9 ottobre 2026

Scritto dal coordinamento alle 21:20 UTC, dopo la consegna dell'ultima moneta (ETCUSDT, 20:28 UTC). Fonti: i branch
`research/campagna/<SIMBOLO>` (consegne e log, letti come chiede il Passo 4 punto 3: conteggi, righe d'esito e, per
i candidati, solo trade, p-value, m e segno dell'R medio di validazione).

## Monete completate: 20 su 20

| Moneta | Versione | Varianti | Ritocchi | Scarti | Minuti dal primo all'ultimo voce del log | Candidati in validazione (m) | Esito |
|---|---|---|---|---|---|---|---|
| BTCUSDT | 4.4 | 30 | 5 | 7 | 79 | 1 | un candidato al vault |
| ETHUSDT | 4.4 | 30 | 0 | 4 | 526 (con il ricalcolo del funding) | 0 | nessuna strategia valida |
| SOLUSDT | 4.4 | 30 | 8 | 9 | 351 (con 4 h 20 di attesa di una risposta) | 0 | nessuna strategia valida |
| XRPUSDT | 4.5 | 30 | 3 | 7 | 41 | 1 (5 trade: «non si sa») | nessuna strategia valida |
| DOGEUSDT | 4.5 | 30 | 5 | 15 | 41 | 0 | nessuna strategia valida |
| BNBUSDT | 4.5 | 30 | 5 | 15 | 61 | 1 | un candidato al vault |
| LTCUSDT | 4.5 | 30 | 5 | 6 | 34 | 0 | nessuna strategia valida |
| MATICUSDT | 4.5 | 30 | 8 | 16 | 30 | 0 | nessuna strategia valida |
| BCHUSDT | 4.5 | 30 | 5 | 8 | 26 | 0 | nessuna strategia valida |
| LINKUSDT | 4.5 | 30 | 3 | 4 | 38 | 0 | nessuna strategia valida |
| AVAXUSDT | 4.5 | 30 | 5 | 7 | 41 | 0 | nessuna strategia valida |
| ADAUSDT | 4.5 | 30 | 8 | 11 | 45 | 1 | un candidato al vault («con forti riserve» della campagna) |
| TRBUSDT | 4.5 | 30 | 3 | 14 | 61 | 0 | nessuna strategia valida |
| FILUSDT | 4.5 | 30 | 8 | 9 | 145 (con 1 h 31 di attesa) | 1 (R medio negativo: fallito) | nessuna strategia valida |
| 1000SHIBUSDT | 4.5 | 30 | 3 | 10 | 42 | 0 | nessuna strategia valida |
| DYDXUSDT | 4.5 | 30 | 9 | 9 | 75 | 1 | nessuna strategia valida |
| MASKUSDT | 4.5 | 30 | 5 | 6 | 27 | 1 | nessuna strategia valida |
| FTMUSDT | 4.5 | 30 | 4 | 8 | 27 | 0 | nessuna strategia valida |
| GALAUSDT | 4.5 | 30 | 2 | 7 | 25 | 0 | nessuna strategia valida |
| ETCUSDT | 4.5 | 30 | 7 | 9 | 63 | 0 | nessuna strategia valida |

Totale: 600 varianti, 101 ritocchi, 7 candidati arrivati in validazione, 3 al vault. Le durate sono dal log (prima e
ultima voce), non le ore di sessione.

## Conferma dei candidati (Passo 4 punto 3, con la correzione del 9 ottobre)

| Candidato | Trade in validazione (minimo 30) | m | p-value contro la (b) | Soglia (k/m × 0,10) | R medio dopo i costi in validazione | Esito confermato |
|---|---|---|---|---|---|---|
| BTCUSDT-V10 | 136 | 1 (la prova di processo non aveva candidati validati) | 0,048 | 0,10 | positivo | **va al vault** |
| BNBUSDT-045 | 32 | 1 | 0,031 | 0,10 | positivo | **va al vault** |
| ADAUSDT-037 | 82 | 1 | 0,014 | 0,10 | positivo | **va al vault** |

Riserve scritte dalle campagne stesse (da riportare, non decidono): BTC, il risultato di validazione dipende da pochi
trade; BNB, 32 trade appena sopra il minimo e costi di validazione maggiori dell'R medio; ADA, il risultato di
validazione dipende quasi tutto da 3 trade e la prova dello scettico attribuisce il vantaggio allo stato del mercato
scelto dai filtri. Il vault giudica.

## Altri controlli

* **Errori e test da rieseguire:** nessuna campagna 4.5 ha cambiato `src/` o `CHANGELOG.md` (confronto di ogni branch
  con il principale); la correzione del funding dell'8 ottobre è già stata ricalcolata da ETHUSDT e SOLUSDT, BTCUSDT
  l'aveva già nei suoi dati. Test da rieseguire: nessuno.
* **Regola dei ritocchi della 4.5 per le consegne 4.4** (conteggio meccanico sui soli campi `netta` delle due
  baseline e `r_medio`): BTCUSDT ha **2** varianti nette contro (a) e (b) con R medio non positivo, quindi con la
  regola della 4.5 la sua scelta dei ritocchi sarebbe potuta essere diversa; ETHUSDT ne ha 1 ma non ha fatto ritocchi
  (30 idee nuove), quindi per lei non cambia niente. Il proprietario decide se rifare BTCUSDT (rifarla toglie il suo
  candidato dal vault: resterebbe solo nel conteggio m).
* **Probabilità per moneta del trasferimento** (Passo 6): 0,02 (il più alto fra 0,02 e le quote della prova a placebo,
  0,0041 e 0,0030), da scrivere in `vault/APERTURA.md`.
* **Un indizio, non una prova (da rileggere al Passo 7):** 6 candidati valutabili in validazione, 3 sotto la soglia.
  Se fossero tutti senza vantaggio, con la quota della prova a placebo (3,3%) o quella nominale (10%) ce ne
  aspetteremmo 0,2-0,6.
* **Impostazioni delle sessioni:** ultracode è mancato in tutte le aperture del 9 ottobre tranne l'ultima (ETCUSDT,
  19:15 UTC); causa non nota.

## STOP

Domande al proprietario: (1) campagna di gruppo (Passo 4bis) prima del vault, sì o no; (2) rifare BTCUSDT per la
regola dei ritocchi, sì o no. Il vault si apre solo con «APRI IL VAULT».

## Risposta del proprietario (10 ottobre 2026, circa 05:40 UTC)

«sì alla campagna di gruppo, no a rifare Bitcoin».

1. **Campagna di gruppo (Passo 4bis): sì.** Il coordinamento scrive il testo completo (budget, minimi di trade,
   come si combinano baseline ed errori, asticella, verifiche della Fase 4, giudizio nel vault, monete che muoiono
   durante il vault) e lo porta al proprietario per l'approvazione, prima di qualunque test e prima di aprire la
   sessione. Il vault aspetta la consegna della campagna di gruppo (Passo 5, prerequisiti).
2. **Rifare BTCUSDT: no.** La consegna 4.4 di BTCUSDT resta valida (era già il primo dei tre punti approvati con la
   4.5) e il suo candidato BTCUSDT-V10 resta fra i tre per il vault.
