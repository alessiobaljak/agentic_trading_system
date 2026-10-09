# BCHUSDT — Lezioni di metodo proposte (solo metodo e trappole dei dati)

1. **La (b) con uno stop ancorato a un prezzo fisso del giorno ha un'altra scala.** Con lo stop
   all'apertura del giorno (rottura di volatilità), gli ingressi casuali presto nella giornata
   hanno lo stop vicinissimo all'entrata: i costi in R esplodono e la (b) vale circa −0,19 R contro
   −0,05 delle altre varianti orarie. Il pavimento dell'errore diventa grande e il confronto
   perde potenza. Chi disegna una variante così lo sappia prima; non è un errore della (b).
2. **Un filtro nato dallo studio dei fallimenti può non filtrare nulla.** Il filtro «sotto la media
   a 50 ore» sulla rottura short di Williams ha tolto 13 trade su 327, perché la condizione
   d'ingresso lo implicava già. Prima di registrare un ritocco con un filtro, vale la pena
   ragionare (non contare: la conta va fatta una volta sola, sulle regole registrate) se il filtro
   è già implicito nell'ingresso.
3. **Il controllo positivo va fatto su entrambe le direzioni e sui timeframe usati.** Il primo
   controllo copriva solo il long su 1h; il secondo (short su 1d e 4h) ha confermato che gli
   strumenti vedono un vantaggio anche lì. Costa pochi secondi.
4. **Le uscite dei comandi in background non si leggono.** Il guardiano rifiuta la lettura della
   cartella temporanea della sessione: gli script lunghi devono scrivere il loro resoconto dentro
   `data/insample/<SIMBOLO>/`.
5. **Lo slippage della scheda è del 2023.** Per BCHUSDT il 2020 e il 2022 avevano un volume medio
   nella fascia di 0,05% per lato, contro 0,02% della scheda: in costruzione i costi sono
   sottostimati e il test a costi doppi (0,04%) non arriva alla fascia vera. Andrebbe considerata
   una prova con lo slippage della fascia di ogni anno, decisa prima delle campagne.
6. **Le soglie in percentile mobile danno pochi trade su 1d.** Quattro idee giornaliere su sei sono
   state scartate al primo tentativo (23-67 trade): con 1.022 giorni di costruzione, una regola
   giornaliera che entra meno di una volta ogni 15 giorni non arriva a 70. Conviene stimarlo a
   mente prima di scrivere la variante (non con la conta, che si fa una volta sola).
