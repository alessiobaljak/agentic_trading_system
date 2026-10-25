# Programma 7 — trentottesima prova: le stablecoin che entrano nelle catene (DefiLlama) fra i gettoni delle catene (SC)

Scritto il 25 ottobre 2026, alle 08:07 UTC, **prima di scaricare le serie e prima di qualunque calcolo**. Idea 67 della coda di
`research/REGISTRO.md` (nata dalla prova 95: l'uso delle catene porta un segnale debole; le stablecoin sono la misura più diretta del
denaro che entra). Il controllo di fattibilità ha solo guardato il formato: `stablecoins.llama.fi/stablecoincharts/{catena}` dà un punto al
giorno con il totale in dollari delle stablecoin sulla catena (Solana dal 10 settembre 2021). Nessun rendimento guardato. Stessa mappa
catena → gettone della prova 95 (108 gettoni con il perpetuo).

## 1. Perché, e il dubbio

Le stablecoin che arrivano su una catena sono potere d'acquisto parcheggiato lì: prima o poi compra i gettoni di quella catena, e chi
sposta capitali (ponti, tesorerie, fondi) lo fa prima che i prezzi si muovano. È un flusso di denaro, non un prezzo: un'informazione mai
usata fra le monete (la prova 44 guardava l'offerta totale, solo sul Bitcoin). **Il dubbio scritto prima**: le stablecoin si spostano
anche per gli incentivi (rendimenti dei protocolli) e per i ponti, non per comprare il gettone; DefiLlama può riscrivere la storia; il
gruppo è piccolo e Ethereum pesa molto (il rango lo neutralizza). Probabilità bassa-media.

## 2. La regola (valori fissati qui)

* **Dati**: per ogni catena della prova 95 il totale giornaliero in dollari delle stablecoin ancorate al dollaro sulla catena
  (`totalCirculatingUSD.peggedUSD`), scaricato una volta con l'impronta; stessa scelta fra catene con lo stesso gettone (storia più lunga).
* **Ogni lunedì**, con i dati fino alla domenica: ammessi i gettoni con il perpetuo nel pannello e volume sopra zero la domenica, con il
  totale delle stablecoin presente alla domenica e 30 giorni prima e **almeno 10 milioni di dollari** 30 giorni prima (sotto, il rapporto è
  rumore). **Segnale**: il logaritmo del rapporto fra il totale della domenica e quello di 30 giorni prima (la crescita del denaro parcheggiato
  nell'ultimo mese). Nessun'altra trasformazione.
* **Portafoglio** come la prova 95 (`pesi_banda`, 20/40, pesi inversi alla volatilità per lato, due lati uguali; settimana ferma e contata con
  meno di 20 ammessi); costi delle monete e funding veri; dal lunedì **3 gennaio 2022** al 5 ottobre 2026.
* **Controllo**: il segnale mescolato a caso fra i gettoni ammessi dentro ogni settimana (seme 2026).
* Una prova nel conto (SC): **170**.

## 3. L'esame e cosa si riporta

`terza.esame` dal 3 gennaio 2022 con gli anni pieni 2022-2025, Sharpe corretto rivisto per gruppi e t, `terza.esito`, la regola del
proprietario; il controllo accanto. Descrittivo: ammessi per settimana, correlazione (per ranghi) fra il segnale e il rendimento dei 30
giorni prima del gettone (se alta, è momento), i due lati, per anno.
