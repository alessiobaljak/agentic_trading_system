# Programma 7 — trentanovesima prova: la speculazione rispetto all'uso, il volume del perpetuo su quello a pronti (VS)

Scritto il 25 ottobre 2026, alle 08:17 UTC, **prima di scaricare i volumi a pronti e prima di qualunque calcolo**. Idea 69 della coda di
`research/REGISTRO.md`. I prezzi a pronti della prova 97 non hanno il volume: si rifà lo scarico (stessi file mensili dell'archivio di
Binance) salvando il volume in dollari, per le monete che entrano nell'universo delle 100 più scambiate. Nessun rendimento guardato.

## 1. Perché, e il dubbio

Quando il volume del perpetuo di una moneta supera di molto quello a pronti, la moneta è in mano a chi usa la leva e non a chi la
compra per tenerla: è la stessa famiglia di «chi paga la leva perde» (funding, posizioni aperte), ma misurata con un dato che nessuna prova
ha usato, il rapporto fra i due mercati. L'ipotesi: le monete più «speculative» rendono meno delle meno speculative. **Il dubbio scritto
prima**: le posizioni aperte (prova 11) e il funding al cambio non hanno retto; il rapporto dipende anche dall'età del perpetuo e dal fatto
che il pronti di Binance è solo una parte del pronti mondiale; è una cugina, non una famiglia nuova. Probabilità bassa-media.

## 2. La regola (valori fissati qui)

* **Segnale**, ogni lunedì con i dati fino alla domenica: il logaritmo del rapporto fra il volume in dollari del perpetuo nei 7 giorni e
  quello a pronti (coppia `BASE USDT`) negli stessi 7 giorni; ammesse le monete dell'universo della settimana (le 100 più scambiate, come
  F5) con il pronti presente in tutti e 7 i giorni e volume a pronti sopra zero.
* **Portafoglio** come F5 (`pesi_banda` 20/40, pesi inversi alla volatilità, due lati uguali): **short** chi entra nel 20% più alto del
  rapporto (più speculativo), **long** chi entra nel 20% più basso; costi e funding veri; dal 4 gennaio 2021 al 5 ottobre 2026; settimana
  ferma e contata con meno di 20 ammesse.
* **Controllo**: il segnale mescolato fra le monete ammesse dentro ogni settimana (seme 2026).
* Una prova nel conto (VS): **171**.

## 3. L'esame e cosa si riporta

`terza.esame` dal 4 gennaio 2021 (anni pieni 2021-2025), Sharpe corretto rivisto per gruppi e t, `terza.esito`, la regola del proprietario;
il controllo accanto. Descrittivo: ammesse per settimana, correlazione (per ranghi) del segnale con il funding dei 7 giorni (se alta, è il
funding con un altro nome) e con il rendimento dei 7 giorni prima; i due lati; per anno.
