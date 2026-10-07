# Passo 1 — Selezione delle monete di campagna: criterio e passaggi

Branch `research/coordinamento`. Scritto PRIMA di qualunque lettura di dati, come chiede il Passo 1.

## Il criterio (scritto il 7 ottobre 2026, prima dei numeri)

Parametri congelati il 7 ott (`config/parametri.yaml`): finestra del volume 2023-01-01 → 2023-12-31; liquidità
minima 20 milioni USDT al giorno; storia minima 2 anni (listing prima del 2022-01-01); 20 monete di campagna;
3 monete per la prova di processo; fasce di slippage per lato 0,01% / 0,02% / 0,05% / 0,10%.

1. **Base.** I contratti perpetui in USDT di Binance USDS-M che hanno una cartella nell'archivio mensile di
   data.binance.vision (quindi anche i delistati). Si escludono i trimestrali (`BTCUSDT_210326`) e le altre
   valute di quotazione. Fonti: l'indice del bucket (solo nomi di cartelle e file) ed exchangeInfo letto da
   www.binance.com (l'host ufficiale risponde 451 dalla regione del server).
2. **Listing.** `onboardDate` di exchangeInfo per i contratti presenti oggi; per i delistati il primo mese nell'archivio.
   Approssimazione dichiarata: l'archivio parte da gennaio 2020, un contratto più vecchio compare come 2020-01
   (non cambia il filtro: è comunque prima del 2022).
3. **Storia minima.** Listing prima del 2022-01-01.
4. **Dati fino alla fine dell'in-sample.** L'ultimo file mensile è almeno 2023-12. Una moneta morta prima non ha
   né la validazione intera né il vault: è esclusa e contata.
5. **Liquidità.** Volume medio giornaliero in USDT (quote volume delle candele giornaliere) nel 2023, calcolato
   sui giorni presenti, almeno 20 milioni; servono almeno 350 giorni di dati nel 2023 (tolleranza per buchi
   brevi, non per mesi interi).
6. **Ordine e taglio.** Le idonee in ordine di volume 2023 decrescente (a parità, alfabetico); le prime 20 sono
   le monete di campagna. Le altre idonee sono le prime candidate a monete di verifica (regola a parte, Passo 6).
7. **Delisting.** Per i contratti non più negoziati, l'ultimo mese nell'archivio. Resta in questa cartella: le
   schede sul branch principale non lo riportano.
8. **Sopravvivenza.** Si contano le idonee che oggi non sono più negoziate (sono nel conteggio con i loro dati)
   e le escluse per fine dati prima del 2024.
9. **Collegamenti fra contratti.** Al Passo 1 non si applica nessuna cucitura: la selezione usa i simboli del
   2023. Le migrazioni note dopo il 2023 (da verificare sui dati al Passo 5, dove servono) sono elencate in
   `collegamenti.md`.

Nessun prezzo del periodo del vault viene scaricato: dei mesi dopo il 2023 si leggono solo i nomi dei file.

## Esecuzione (7 ottobre 2026, 07:36 ora italiana; `python -m research.src.passo1`, log nel diario)

Numeri da `conteggi.json` e `candidate.csv` (fonte: indice dell'archivio, exchangeInfo da www.binance.com,
candele giornaliere 2023 scaricate con checksum verificato, nessun checksum mancante).

| Passaggio | Numero |
|---|---|
| Contratti perpetui in USDT con una cartella nell'archivio (base, delistati compresi) | 895 |
| Contratti perpetui in USDT su exchangeInfo oggi (di cui negoziati) | 659 (525) |
| Esclusi per listing dal 2022-01-01 in poi | 759 (di cui 755 anche per primo mese di dati dal 2022) |
| Esclusi perché i dati finiscono prima del 2023-12 | 12 (nessuno escluso per ultimo giorno prima del 31/12) |
| Esclusi per volume 2023 sotto 20 milioni USDT/giorno | 26 |
| Esclusi in tutto (una moneta può contare in più motivi) | 795 |
| **Idonee** | **100** |
| Idonee con copertura 2023 sotto 350 giorni (segnalate) | 0 |
| **Monete di campagna (prime 20 per volume 2023)** | **20** |
| Idonee non più negoziate oggi (sopravvivenza: hanno dati, entrano nei conteggi) | 24 |
| Monete di campagna non più negoziate oggi | 2 (MATICUSDT, FTMUSDT) |
| Sospette ridenominazioni: contratti spariti nel 2022-2023 | 9 |
| Contratti nati nel 2022-2023 | 124 |

Le 20 monete di campagna, in ordine di volume 2023 (milioni di USDT al giorno, 365 giorni di dati ciascuna):
BTCUSDT 11.505 · ETHUSDT 5.513 · SOLUSDT 1.104 · XRPUSDT 811 · DOGEUSDT 519 · BNBUSDT 401 · LTCUSDT 382 ·
MATICUSDT 374 · BCHUSDT 339 · LINKUSDT 319 · AVAXUSDT 289 · ADAUSDT 272 · TRBUSDT 258 · FILUSDT 221 ·
1000SHIBUSDT 212 · DYDXUSDT 201 · MASKUSDT 199 · FTMUSDT 199 · GALAUSDT 198 · ETCUSDT 197.
Fasce di slippage: 0,01% BTC, ETH, SOL; 0,02% da XRP a DYDX; 0,05% MASK, FTM, GALA, ETC.
Prova di processo (Passo 2): le prime 3, BTCUSDT, ETHUSDT, SOLUSDT.

**Sopravvivenza (sezione 11).** Le monete idonee ma non più negoziate oggi sono 24 su 100, e due stanno fra le
20 di campagna: MATICUSDT e FTMUSDT, che risultano migrate ad altri simboli dopo il 2023 (ipotesi, da verificare
al Passo 5: vedi `collegamenti.md`). Quante monete «avrebbero superato i filtri ma oggi non hanno dati» non si
può contare: l'archivio è la fonte stessa dei dati, e se un contratto non c'è non lo si vede; i 12 esclusi
per fine dati prima del 2024 sono i contratti morti durante l'in-sample.

**Ridenominazioni.** Nessuna cucitura applicata. Le 9 sparite nel 2022-2023 (1000BTTCUSDT, AKROUSDT, ANCUSDT,
BTTUSDT, DODOUSDT, KEEPUSDT, LUNAUSDT, NUUSDT, YFIIUSDT) non toccano nessuna delle 20 di campagna, che hanno
tutte dati continui dal 2021 o prima fino al 2023-12-31. Interpretazione (inferita, non verificata sui dati):
BTTUSDT → 1000BTTCUSDT è una ridenominazione del 2022 (poi delistata), LUNAUSDT è il vecchio LUNA (il
LUNA2USDT nato nel 2022 è un altro asset), le altre sono delisting. Non cambiano la selezione.
