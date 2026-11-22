# La mappa delle liquidazioni di Hyperliquid (idea 151 del registro)

Regole scritte il 22 novembre 2026 alle 08:30 UTC dalla sessione principale, **prima di guardare qualunque dato raccolto per una prova**.
Il proprietario (22 novembre): «Fai 1 e 2 insieme» (la 2 è questa raccolta) e «le idee le devi provare in automatico».

## Il perché
Su Hyperliquid ogni posizione aperta, il suo valore e il prezzo a cui verrebbe liquidata sono pubblici (interfaccia `info`, richiesta
`clearinghouseState`). Su Binance e sulle altre borse no: lì le mappe delle liquidazioni che si vedono in giro sono stime. Dove molte
liquidazioni si ammassano vicino al prezzo, le vendite o gli acquisti forzati sono prevedibili prima che succedano; la prova 112
guardava le cascate dopo, non la mappa prima. Lo storico non esiste: va raccolto da oggi.

## Cosa si raccoglie (`liquidazioni.py`, chiamato dalla raccolta delle notizie a ogni giro)
1. **I conti**: ogni lunedì al primo giro (e il 22 novembre, la prima volta) dalla classifica pubblica
   (`stats-data.hyperliquid.xyz/Mainnet/leaderboard`) i **600 conti più grandi** per valore fra quelli con almeno **1 milione di dollari
   di volume nel mese**; l'elenco va in `hyperliquid/liquidazioni_conti_AAAA-MM-GG.json` e non cambia fino al lunedì dopo.
2. **A ogni giro** (ogni 4 ore e al mattino): per ogni conto le posizioni aperte di almeno 10.000 dollari (sotto, lo 0,1% del valore
   totale nella prima lettura) con moneta, quantità con il segno, valore, prezzo d'entrata, prezzo di liquidazione (se c'è), leva e tipo
   di margine; il valore del conto; i prezzi medi delle monete in quel momento (`allMids`); l'ora d'inizio e di fine della lettura. Una
   riga per giro in `hyperliquid/liquidazioni_AAAA-MM.jsonl.gz`. Un giro saltato o un conto non letto si conta e non si ricostruisce.
3. Prima lettura (22 novembre, 08:09 UTC): 600 conti su 600 in 108 secondi, 3.564 posizioni di cui 2.230 con il prezzo di liquidazione
   (2.337 posizioni sopra i 10.000 dollari, 99,9% del valore, 2,82 miliardi di dollari in tutto).

## La prova (le linee fissate ora; le regole intere si scrivono e si committano prima della prima analisi)
4. **Quando**: dopo almeno **3 mesi** di raccolta (circa 500 giri). Fino ad allora nessuno guarda la relazione fra la mappa e i prezzi.
5. **Il segnale**, per ogni moneta che ha anche il perpetuo su Binance e per ogni giro: il valore delle posizioni corte con il prezzo di
   liquidazione entro il +X% dal prezzo (acquisti forzati sopra) meno quello delle lunghe entro il −X% (vendite forzate sotto), diviso per
   il volume giornaliero della moneta; X fissato nelle regole intere (5% e 10% come varianti).
6. **L'ipotesi scritta prima**: il prezzo va verso il lato con più liquidazioni vicine («calamita»: chi è dall'altra parte ha interesse a
   spingerlo lì e le liquidazioni, una volta toccate, si alimentano da sole). Si misura il rendimento del perpetuo di Binance nelle 4 e
   nelle 24 ore dopo il giro, fra le monete (lungo il lato con più acquisti forzati vicini, corto l'altro) e nel tempo.
7. Esame come sempre: Sharpe corretto per famiglie 0,80, t da 3, spese confermate dal proprietario; nel conto delle prove quando si fa.
