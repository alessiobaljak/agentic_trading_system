# Errori ricorrenti di questo repo (catalogo dell'auditor)

Ogni voce: cosa succede, dove è stato trovato, come cercarlo. La lista cresce e non si accorcia; oltre le 300 righe si
raggruppano gli errori simili senza toglierne nessuno. Aggiornato il 7 novembre 2026.

## Dati

1. **Giorno mancante nell'archivio pubblico di Binance.** Il 28 ottobre 2026 manca per tutte le monete (file del giorno 404,
   file mensile di ottobre con 30 righe). Le candele giornaliere lo prendono dall'interfaccia pubblica (`giorni_api`,
   `research/programma6/buchi_archivio.py`; `seconda.candele`, `seconda.py:62-73`). Cercare: giorni mancanti fra la prima
   e l'ultima candela con `buchi_archivio.giorni_mancanti(simbolo, dal)` (sola lettura). Attenzione: il `main` di
   `buchi_archivio` scarica e scrive in `research/data/`: l'auditor non lo esegue. Da controllare anche per le candele
   orarie e da 1 minuto, che non passano da `giorni_api`.
2. **Simboli tolti dal listino tenuti a rendimento zero** (prezzo fermo, volume zero): sembrano posizioni piatte e
   abbassano la volatilità. `research/programma6/controllo_zombi.py`; il pannello azzera il loro funding
   (`seconda.py:133-134`). Cercare: giorni con `quote_volume == 0` e chiusura uguale al giorno prima dentro il periodo.
3. **Funding dell'ultimo mese stimato, non vero.** Dove la candela c'è e il dato di funding no, il pannello mette la media
   dei 90 giorni prima (`riempi_funding`, `seconda.py:88-100`). Cercare: confronto fra `pannello()["funding"]` e
   `seconda.funding_giorni(simbolo)` nei giorni del periodo; i giorni diversi o senza dato vero vanno dichiarati.

## Sguardo nel futuro e tempi

4. **Segnale giornaliero applicato alle ore dello stesso giorno** (trovato il 7 nov 2026 in BTCORA,
   `research/prova_finta_audit/strategia.py:37-39,45`). Un segnale calcolato sulla chiusura del giorno d unito alle ore con
   `ore.index // 24` e spostato di una sola ora: le ore 1-23 usano una chiusura che arriva a mezzanotte. Effetto misurato:
   Sharpe da −1,50 a +5,01. Convenzione giusta del repo: `seconda.py:5-6` (il peso deciso alla chiusura di t vale su t+1).
   Cercare: `// 24`, `// 1440`, `join(`, `map(`, `resample(` fra scale diverse senza `- 1` sul giorno o `shift(1)` sulla
   serie giornaliera prima dell'unione. Un `shift(1)` sulla serie oraria non basta.
5. **La stabilità nei parametri non protegge dallo sguardo nel futuro.** In BTCORA lo Sharpe con lo sguardo restava fra
   4,14 e 5,46 con la media da 16 a 24 giorni. Una prova stabile non è per questo pulita.

## Costi

6. **Funding caricato e mai applicato** (BTCORA, `strategia.py:26` contro `strategia.py:43-50`). Cercare: una colonna
   `funding` letta e non sottratta nel conto; confrontare con le regole della prova.
7. **Scarto di prezzo assente**: costo = sola commissione. Valori del repo: `motore5.SCARTO` (0,01% BTC/ETH/SOL, 0,02% le
   altre, `research/programma5/strumenti/motore5.py:47-48`).

## Misure

8. **Annualizzazione con 252 giorni** invece di 365 (BTCORA, `strategia.py:49`). Al 7 nov 2026 nessun'altra occorrenza
   in `research/`, `bot/`, `backtesting/`: `grep -rn "sqrt(252)" --include=*.py research/ bot/ backtesting/`.
9. **«Rendimento» come somma dei rendimenti semplici** senza dichiarare il capitale fisso (BTCORA, `strategia.py:48,58`:
   somma +207,9%, composto +630,7%). Una somma di rendimenti orari a valore costante implica ritocchi ogni ora non costati.
10. **Valore mancante dell'indicatore trattato come segnale**: `close > media` con la media ancora mancante dà falso, quindi
    «venduto» (BTCORA, `strategia.py:34-35,39`: 19 giorni venduti all'inizio, circa 31 punti di effetto). Cercare:
    confronti con colonne `rolling(...)` senza `min_periods`/`dropna`/posizione nulla iniziale.

## Procedura dell'audit

11. **Il comando che rigenera i risultati spesso li riscrive** (BTCORA, `strategia.py:59`) e alcuni script di controllo
    scrivono fuori da `audits/` (`controllo_giorni.main` scrive `risultati_seconda/controllo_dati.json`; `buchi_archivio.main`
    scarica e scrive in `research/data/`). L'auditor importa le funzioni e le chiama senza il `main`, in uno script dentro
    `audits/repro/`.
