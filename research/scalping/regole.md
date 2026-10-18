# Scalping sulla volatilità: le regole della prima analisi, scritte prima dei numeri

Scritte dal coordinamento il 18 ottobre 2026, **prima di scaricare i dati e di qualunque calcolo**, dopo il sì del
proprietario («ok procedi con l'analisi sullo scalping»). Per il proprietario lo scalping è «sfruttare la volatilità»;
l'autopsia delle strategie vecchie (`research/autopsia/risultati.md`) dice che nei momenti agitati i costi pesano tre volte
meno ma le regole vecchie lì non funzionano.

**La domanda**: quando il prezzo «esplode» in pochi minuti, nei minuti dopo continua o torna indietro, e di quanto rispetto
al costo di un giro (entrata e uscita)?

**Cosa non è**: non è una ricerca di strategie. Non si prova nessuna regola di trading con stop e target; si misura cosa fa
il prezzo dopo un'esplosione. Le idee che ne escono sono ipotesi da confermare sul 2023 (validazione) e poi sui dati in
avanti (`docs/proposta_ripartenza.md`, sezione 3.2). I dati 2020-2022 di queste monete, a 1 minuto, diventano «già visti»
per chi progetta.

## I dati

* Candele da 1 minuto (prezzo di scambio, perpetui USDT-M) di **BTCUSDT, ETHUSDT, SOLUSDT, XRPUSDT, BNBUSDT, DOGEUSDT**,
  dall'archivio pubblico di Binance (`data.binance.vision`), con il controllo del CHECKSUM, **dal 2020-01-01 (o dal primo
  mese disponibile) al 2022-12-31**. Nessun dato del 2023 o successivo.
* Un minuto mancante resta mancante: le finestre che lo attraversano non si usano.

## L'esplosione (l'evento)

* Alla chiusura del minuto t: **movimento degli ultimi 5 minuti** = |ln(chiusura_t / chiusura_{t−5})|.
* **Il suo metro**: la mediana dello stesso movimento sulle 1.440 finestre di 5 minuti che finiscono nelle 24 ore prima di t
  (niente dati futuri).
* **Evento di livello m** se il movimento supera m volte il metro, con **m = 4, 8, 16** (tre livelli, contati a parte).
* Dopo un evento, nessun altro evento della stessa moneta e dello stesso livello per **60 minuti**.
* **Direzione** dell'evento: il segno del movimento (salita o discesa).

## Cosa si misura dopo l'evento

L'entrata immaginaria è all'apertura del minuto t+1 (subito dopo l'evento: si decide alla chiusura di t, come farebbe il
bot).

1. **Movimento in avanti** a h = 1, 3, 5, 15, 30, 60 minuti dall'entrata, in %, con il segno della direzione dell'evento:
   positivo = **continua**, negativo = **torna indietro**.
2. **Massimo a favore e massimo contro** nei 15 minuti dopo l'entrata, in %, nella direzione dell'evento.
3. **Quota di eventi** in cui |movimento a h| supera il costo di un giro.

## I costi di un giro (scritti prima)

Commissioni di Binance al livello base (taker 0,05%, maker 0,02% per lato) e scarto di prezzo per lato della fascia della
moneta (`research/src/controllo4.py`, `MONETE_CONTROLLO`: BTC, ETH, SOL 0,01%; XRP, DOGE, BNB 0,02%):

| Come si entra e si esce | BTC, ETH, SOL | XRP, DOGE, BNB |
|---|---|---|
| a mercato e a mercato | 0,12% | 0,14% |
| entrata limite, uscita a mercato | 0,08% | 0,09% |
| limite e limite (esecuzione non garantita) | 0,04% | 0,04% |

Lo scarto di prezzo della fascia è misurato sul 2023 ed è ottimista per il 2020-2021 (`docs/storia/README.md`, sezione 5,
punto 2): si riporta anche il risultato a costi doppi.

## Il confronto con il caso

Per ogni moneta e ogni anno, tanti minuti presi a caso (seme 2026) fra quelli **senza** evento di livello 4 nei 60 minuti
prima, quanti sono gli eventi di livello 4, con un segno a caso: è il movimento «senza informazione», atteso vicino a zero.
Serve a vedere se un risultato è dell'esplosione o della deriva del periodo.

## Come si legge

* **Incertezza**: gli eventi dello stesso giorno sono legati. Bootstrap a blocchi di giorni, 2.000 ricampionamenti, seme
  2026: intervallo al 95% della media del movimento con il segno.
* Per ogni livello m e orizzonte h, su tutte le monete insieme e per moneta:
  * **«continua più del costo»** se l'intervallo sta tutto sopra il costo a mercato della moneta;
  * **«torna indietro più del costo»** se sta tutto sotto il costo cambiato di segno;
  * **«non paga un giro»** altrimenti, dicendo se l'intervallo esclude almeno lo zero (c'è una direzione, ma troppo
    piccola) o no.
* Si riporta anche per anno (2020, 2021, 2022) e per direzione dell'evento (salita, discesa). **Nessun'altra divisione**:
  niente ore del giorno, niente giorni della settimana, niente soglie diverse da quelle scritte qui.

## Analisi B: la volatilità di fondo, non solo le esplosioni

Ogni 5 minuti (finestre che non si sovrappongono), per ogni moneta: il rendimento dei 5 minuti dopo con il segno dei 5
minuti prima, diviso per **decili della volatilità dell'ultima ora** (deviazione dei rendimenti a 1 minuto dei 60 minuti
prima, percentile fra le ore dei 30 giorni prima). Media in %, con lo stesso bootstrap a blocchi di giorni, e confronto
con il costo: nei momenti agitati i movimenti brevi continuano o tornano indietro, e abbastanza da pagare un giro?

## Cosa si scrive nei risultati

Tutti i numeri delle tabelle con la loro fonte (file dei risultati, script), il numero di eventi per livello e moneta, le
versioni di Python e numpy, e le impronte SHA-256 dei file scaricati.
