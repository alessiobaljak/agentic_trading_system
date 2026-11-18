# Controllo dopo la prova 40 — ci sono le date di pagamento per tutti gli anni?

Metodo scritto il 18 novembre 2026, **dopo** aver visto il risultato della prova 40 e **prima** di guardare i dati scaricati. **Non è
una prova**: la prova 40 resta com'è (bocciata). Il risultato della prova 40 dice che la strategia nel 2017, 2018 e 2019 ha reso quasi
zero (+0,0%, +0,0%, +0,2%), cioè non è quasi mai entrata, e che i dividendi trovati sono 8'662 (circa 15'000 attesi dal 2015 al 2024:
circa 400 aziende che pagano quattro volte l'anno). Il sospetto: Alpaca non dà la data di pagamento per i dividendi degli anni vecchi, il
programma li scarta (`alpaca.dividendi_pagati` tiene solo quelli con la data) e la misura resta vuota.

## Come

* Con i dividendi già scaricati dal lavoro della prova 40 (`~/stock_dati/p040/dividendi.csv.gz`, la memoria del lavoro di GitHub):
  quanti per anno di pagamento, e quanti dividendi per anno ci sono nell'archivio delle azioni societarie delle prove (con la sola data
  di stacco), per gli stessi simboli.
* **Un anno è «senza dati»** se ha meno della metà dei dividendi con la data di pagamento rispetto a quelli dell'archivio per la data di
  stacco.
* Solo sugli anni con dati, e dal primo giorno con 252 giorni di dati prima: lo SPY nei giorni sopra e sotto la mediana (la regola della
  prova 40), la differenza con il t, e lo Sharpe della regola contro lo SPY. **Da leggere**: un risultato qui non promuove niente; se la
  differenza avesse un t sopra 2, servirebbe una prova nuova (con le date di pagamento da un'altra fonte per gli anni vecchi), che conta
  nel registro.
