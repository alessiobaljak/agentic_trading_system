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
   di volume nel mese**; l'elenco va in `hyperliquid/liquidazioni_conti_AAAA-MM-GG.json` e non cambia fino al lunedì dopo. **Dal 30
   novembre 2026** i 600 con più posizioni aperte fra i primi 1.500 (nota del 27 novembre, sotto).
2. **A ogni giro** (ogni 4 ore e al mattino): per ogni conto le posizioni aperte di almeno 10.000 dollari (sotto, lo 0,1% del valore
   totale nella prima lettura) con moneta, quantità con il segno, valore, prezzo d'entrata, prezzo di liquidazione (se c'è), leva e tipo
   di margine; il valore del conto; i prezzi medi delle monete in quel momento (`allMids`: nella riga della mappa solo le monete con
   posizioni; tutti, con `metaAndAssetCtxs`, nel file del mercato dal 27 novembre); l'ora d'inizio e di fine della lettura. Una
   riga per giro in `hyperliquid/liquidazioni_AAAA-MM.jsonl.gz`. Un giro saltato o un conto non letto si conta e non si ricostruisce.
3. Prima lettura (22 novembre, 08:09 UTC): 600 conti su 600 in 108 secondi, 3.564 posizioni di cui 2.230 con il prezzo di liquidazione
   (2.337 posizioni sopra i 10.000 dollari, 99,9% del valore, 2,82 miliardi di dollari in tutto).

### Cambi alla raccolta, scritti prima di ogni analisi della mappa
* **27 novembre 2026, 04:03 UTC (audit del 26 novembre, problemi raccolta-4 e raccolta-7).** Nessuno ha ancora guardato la relazione fra
  la mappa e i prezzi (punto 4).
  * **La scelta dei 600 conti, da lunedì 30 novembre 2026.** Con la scelta per valore in classifica (punto 1) metà dei conti non ha
    posizioni a leva: il valore in classifica comprende anche il saldo a pronti. Nel giro del 26 novembre alle 20:18 il conto a leva
    (`clearinghouseState`) valeva zero per 225 conti su 600, meno di 10.000 dollari per 24, fra 10.000 e 100.000 per 44; il rapporto
    mediano fra conto a leva e valore in classifica era 0,029; 271 conti non avevano posizioni salvate; le posizioni della mappa (1,19
    miliardi di dollari lunghe, 1,61 corte) erano il 19% e il 26% dell'interesse aperto di Hyperliquid (6,15 miliardi). Fonte: verifica
    dell'audit del 26 novembre (`audits/reports/2026-11-26-AUDIT_SISTEMA.md`). **Dal 30 novembre**: fra i conti della classifica con
    almeno 1 milione di dollari di volume nel mese (come prima) si leggono le posizioni dei **primi 1.500 per valore in classifica** e si
    tengono i **600 con più posizioni aperte in dollari** (somma dei valori di tutte le posizioni, anche sotto i 10.000 dollari; a parità
    il più grande in classifica). La lettura dura al più 4 minuti, classifica compresa, a 6 letture al secondo; se Hyperliquid rifiuta una
    lettura (troppe richieste) tutti si fermano 2 secondi e quel conto si riprova una volta. Se il tempo finisce prima, si sceglie fra
    quelli letti; se se ne sono letti meno di 600, si completa con i non letti nell'ordine della classifica. Prova dal vivo del 27
    novembre alle 04:33 (fuori dal repository): **1.228 candidati letti su 1.500 in 239 secondi**, 30 rifiuti e 4 conti non letti, 600
    scelti su 600 con posizioni aperte (con la scelta di prima 329); Hyperliquid oggi accetta circa 300-360 letture al minuto, quindi i
    1.500 interi non stanno nei 4 minuti, ma i conti oltre il posto 1.200 portavano il 2,8% delle posizioni dei 600 scelti. Il file `liquidazioni_conti_AAAA-MM-GG.json` scrive in testa la regola, i
    candidati letti e le ore della lettura, e per ogni conto il posto in classifica, le posizioni aperte e il conto a leva alla scelta. Le
    posizioni lette per la scelta fanno da giro di quel lunedì (nella riga del giro c'è `letto_nella_scelta`): niente seconda lettura. La
    settimana dal 23 al 29 novembre resta con l'elenco già scelto (punto 1).
  * **Il mercato a ogni giro, dal 27 novembre.** Una riga per giro in `hyperliquid/mercato_AAAA-MM.jsonl.gz` con le risposte intere di
    `allMids` (tutti i prezzi medi, anche delle coppie a pronti) e di `metaAndAssetCtxs` (per ognuno dei circa 235 perpetui: interesse
    aperto, funding, premio, volume del giorno, prezzo di riferimento, dell'oracolo e del giorno prima), con l'ora di lettura di ognuna.
    L'interesse aperto giro per giro non si può recuperare dopo (funding, premio, prezzi e volumi sì: `fundingHistory`, `candleSnapshot`).
    Una riga pesa circa 21 KB compressa (prova del 27 novembre: 97.786 byte, 21.379-21.595 compressi), circa 5 MB al mese. Un errore nel
    salvare il mercato non ferma la riga della mappa.
  * **Per la prova (punti 4-7)**: i conti prima e dopo il 30 novembre sono scelti in due modi. Le regole intere diranno, prima della prima
    analisi, se la prova tiene anche i giri dal 22 al 29 novembre; quanta parte dell'interesse aperto vede la mappa, moneta per moneta e
    giro per giro, si misura con il file del mercato.

## La prova (le linee fissate ora; le regole intere si scrivono e si committano prima della prima analisi)
4. **Quando**: dopo almeno **3 mesi** di raccolta (circa 500 giri). Fino ad allora nessuno guarda la relazione fra la mappa e i prezzi.
5. **Il segnale**, per ogni moneta che ha anche il perpetuo su Binance e per ogni giro: il valore delle posizioni corte con il prezzo di
   liquidazione entro il +X% dal prezzo (acquisti forzati sopra) meno quello delle lunghe entro il −X% (vendite forzate sotto), diviso per
   il volume giornaliero della moneta; X fissato nelle regole intere (5% e 10% come varianti).
6. **L'ipotesi scritta prima**: il prezzo va verso il lato con più liquidazioni vicine («calamita»: chi è dall'altra parte ha interesse a
   spingerlo lì e le liquidazioni, una volta toccate, si alimentano da sole). Si misura il rendimento del perpetuo di Binance nelle 4 e
   nelle 24 ore dopo il giro, fra le monete (lungo il lato con più acquisti forzati vicini, corto l'altro) e nel tempo.
7. Esame come sempre: Sharpe corretto per famiglie 0,80, t da 3, spese confermate dal proprietario; nel conto delle prove quando si fa.
