# Programma 7 — trentatreesima prova: l'uso vero delle catene (le commissioni pagate dagli utenti, DefiLlama) fra i gettoni delle catene (CF)

Scritto il 25 ottobre 2026, alle 07:49 UTC, **prima di scaricare le commissioni e prima di qualunque calcolo**. Idea 64 della coda di
`research/REGISTRO.md`. Il controllo di fattibilità fatto prima ha contato solo gli abbinamenti: delle 421 catene di DefiLlama, 141 hanno
il gettone quotato come perpetuo nel nostro pannello (con qualche doppione: due catene con lo stesso gettone); la serie delle
commissioni di Solana parte dal 14 febbraio 2022, un punto al giorno. Nessun rendimento guardato.

## 1. Perché, e il dubbio

L'uso reale di una catena (le commissioni che gli utenti pagano ai protocolli e alla catena stessa) è domanda del suo gettone: paga il
gas, muove le tesorerie, attira chi costruisce. I prezzi dei gettoni delle catene dovrebbero seguire l'uso con ritardo, perché chi
investe guarda i prezzi e non le commissioni. È un dato di **fondamentali**, pubblico, che nessuna prova ha toccato (gli sblocchi della
74 e le stablecoin della 44 sono altro). **Il dubbio scritto prima**: le commissioni in dollari salgono anche solo perché sale il prezzo
del gettone o perché c'è euforia (quindi il segnale potrebbe essere momento travestito, e il momento fra monete non regge: prove 49 e 66);
DefiLlama riscrive la storia quando aggiunge un protocollo nuovo (le commissioni del passato di una catena possono essere state
«riempite» dopo: una fuga dal futuro che non si può togliere, da dichiarare); il gruppo è piccolo nei primi mesi. Probabilità bassa-media.

## 2. La regola (valori fissati qui)

* **Dati**: per ogni catena di DefiLlama il totale giornaliero delle commissioni (`api.llama.fi/overview/fees/{catena}`, `dailyFees`),
  scaricato una volta e salvato con l'impronta. Quando due catene hanno lo stesso gettone si tiene quella con la storia più lunga (a pari
  storia, quella con il totale più grande).
* **Ogni lunedì** (00:00 UTC), con i dati fino alla domenica: ammessi i gettoni con il perpetuo nel pannello e il volume sopra zero la
  domenica, con le commissioni presenti in almeno 80 dei 90 giorni precedenti i 7 di segnale e con la media di quei 90 giorni sopra zero.
  **Segnale**: la somma delle commissioni dei 7 giorni fino alla domenica divisa per la media giornaliera dei 90 giorni prima moltiplicata
  per 7 (quanto l'uso di questa settimana supera il solito). Nessun'altra trasformazione.
* **Portafoglio** come F5 (`programma6/ventiquattresima.pesi_banda`): long chi entra nel 20% più alto del segnale (resta finché è nel 40%),
  short chi entra nel 20% più basso, pesi inversi alla volatilità dei 30 giorni per lato, i due lati uguali in dollari; tenuta dal lunedì al
  lunedì, costi delle monete e funding veri (`terza.conto`). Con meno di 20 gettoni ammessi la settimana è ferma e si conta.
* **Periodo**: dal lunedì 2 maggio 2022 (i primi 90 giorni di storia) al 5 ottobre 2026. **Controllo**: lo stesso segnale mescolato a caso fra
  i gettoni ammessi dentro ogni settimana (seme 2026).
* Una prova nel conto (CF): **165**.

## 3. L'esame e cosa si riporta

`terza.esame` dal 2 maggio 2022 con gli anni pieni 2023-2025, Sharpe corretto rivisto per gruppi e t, `terza.esito`, la regola del
proprietario del 24 ottobre; il controllo mescolato accanto. Per capire (descrittivo): quanti gettoni ammessi per settimana, la
correlazione fra il segnale e il rendimento dei 7 giorni prima del gettone (se è alta, il segnale è momento), i due lati separati, e il
rendimento per anno.
