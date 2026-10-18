# Autopsia delle strategie vecchie: le regole, scritte prima dei numeri

Scritte dal coordinamento il 18 ottobre 2026, **prima di qualunque calcolo**, dopo la richiesta del proprietario:
«non capisco perché non provi a capire come costruire strategie migliori, perché non capisci cosa è andato storto nelle
centinaia di strategie vecchie»; e, sullo scalping, «non è una questione di aprire più trade ma di sfruttare la
volatilità». Commit di queste regole prima del primo calcolo; chi legge i risultati può controllare l'ordine nella storia
di git.

## A cosa serve, e cosa non è

* **Serve a capire perché le strategie perdono**, una domanda alla volta, e a separare i difetti propri delle strategie
  dal comportamento normale del prezzo: per ogni misura, lo stesso numero calcolato su **trade a caso** con le stesse
  uscite, la stessa larghezza di stop e gli stessi costi. Una cosa che il caso fa uguale non è un difetto della strategia.
* **Non è una ricerca di strategie.** Nessuna variante nuova si prova qui. Le idee che ne escono sono ipotesi per la
  ricerca futura, da confermare solo su dati che arrivano dopo (`docs/proposta_ripartenza.md`, sezione 3.2). I dati usati
  qui (costruzione 2020-2022 di BTCUSDT e LINKUSDT, trade del paper fino al 18 ottobre) diventano dati «già visti» per chi
  progetta: lo si dichiara.

## I dati

1. **Le varianti delle ricerche BTC51 e LINK6**: tutte quelle con un risultato di Fase 2 nel log (40 di BTC51, 32 di
   LINK6), con la specifica registrata (`research/campagne/BTC51/log.jsonl`, `research/campagne/LINK6/log.jsonl`),
   rieseguite con gli strumenti congelati (`research/src/catalogo3.py`, `motore3.py`, `statistica3.py`) **solo sul
   periodo di costruzione** (dal 2020-01-01 o dalla prima candela al 2022-09-30): regole e costi del protocollo 3 per BTC
   (`Regole()`, `COSTI_NORMALI`), del protocollo 4 per LINK (`REGOLE_LINK`, `COSTI_LINK`). Nessun dato di validazione o
   del periodo chiuso viene caricato.
2. **Il controllo**: per ogni variante, 20 simulazioni di entrate casuali dello stesso motore
   (`statistica3.entrate_casuali`, seme 2026, larghezze di stop del candidato), con i trade registrati.
3. **I 707 trade del paper** (`ops/results/archivio_20261018/firestore/trades.json.gz`), con i campi che il bot ha
   registrato; come controllo per il paper, le misure «contro il caso» già calcolate dalla macchina (`ops/results/0622`,
   sezione «paper contro prezzo casuale»).

## Le domande e le misure

R = la distanza fra il prezzo d'ingresso e lo stop iniziale. Le misure sulle candele usano le candele del timeframe della
variante, fino all'uscita (e dopo, solo per la misura 4).

| N. | Domanda | Misura |
|---|---|---|
| 1 | **Direzione**: il prezzo va subito contro? | quale arriva prima, −0,5 R o +0,5 R (minimi e massimi delle candele dopo l'ingresso); se tutti e due nella stessa candela, il trade è «non deciso» e si esclude |
| 2 | **Ritardo**: entriamo dopo che il movimento è già avvenuto? | il movimento del prezzo nelle 4 e nelle 12 candele prima del segnale, nella direzione del trade, in R |
| 3 | **Uscita**: restituiamo il guadagno? | per i trade che toccano almeno +1 R: quota del massimo a favore restituita all'uscita, e quota di quei trade che chiudono a zero o sotto (in R prima dei costi) |
| 4 | **Stop**: lo stop ci butta fuori e poi il prezzo va dalla nostra parte? | per i trade usciti allo stop: il prezzo, nelle H candele dopo l'uscita (H = durata mediana dei trade della variante), tocca l'ingresso + 1 R nella direzione del trade? |
| 5 | **Costi**: quanto pesano? | costo medio in R = R con i costi normali − R senza commissioni e scivolamento (funding uguale), per lo stesso ingresso |
| 6 | **Volatilità**: le strategie rendono di più quando il prezzo si muove tanto? | volatilità alla candela del segnale = deviazione dei rendimenti delle 24 candele prima; il suo percentile fra le candele dei 365 giorni prima (niente dati futuri); cinque fasce (Q1 calma … Q5 agitata). Per fascia: R medio dopo i costi, R prima dei costi, costo in R |

## Come si leggono

* **Unità**: la variante. I trade di una stessa variante non sono indipendenti; gli intervalli si calcolano con un
  bootstrap sulle varianti (2.000 ricampionamenti, seme 2026), BTC e LINK insieme e separati.
* **Un difetto è «proprio delle strategie»** se la differenza fra la strategia e il suo caso, mediata sulle varianti, ha
  l'intervallo al 95% che non contiene lo zero. Altrimenti è «comportamento del prezzo»: il caso fa lo stesso, e
  correggerlo non crea un vantaggio.
* **Volatilità (domanda 6)**: si riporta, fascia per fascia, la differenza strategia − caso in R dopo i costi, e il costo
  in R. La domanda «sfruttare la volatilità» ha risposta sì se nella fascia Q5 la differenza strategia − caso è positiva
  con l'intervallo sopra zero; e si riporta comunque se il **costo in R** scende con la volatilità (atteso: i costi sono
  fissi in percentuale, lo stop cresce con la volatilità).
* **Famiglie** (tendenza, ritorno alla media, funding, volume, orari e range): solo descrittive, troppe poche varianti
  per un test.
* **Il paper**: le stesse domande dove i campi registrati lo permettono (massimo e minimo a favore, chi viene prima,
  cosa succede dopo l'uscita, costi in R, volatilità all'ingresso se registrata), confrontate con le misure contro il caso
  di `ops/results/0622`. Il paper si legge come diagnosi, non come prova.
* Ogni numero nei risultati ha la sua fonte (file e riga dello script). Le versioni di Python e numpy si scrivono nei
  risultati (questa macchina non è quella delle sessioni di ricerca: per misure descrittive la differenza non conta, e lo si
  dice).
