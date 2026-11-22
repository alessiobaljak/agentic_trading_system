# Prova 46 — le dimissioni del capo: vendere allo scoperto il giorno dopo l'annuncio, per 20 sedute, coperti con lo SPY

Regole scritte il 22 novembre 2026 **prima di qualsiasi calcolo** (idea I54 di `REGISTRO.md`, **idea del proprietario**: «se è dimesso,
perché non vai short il giorno dopo, tanto lo sai»). Il caso che l'ha fatta nascere: Nvidia, dimissioni dell'amministratore delegato
annunciate prima dell'apertura del 12 novembre 2026; −8,2% all'apertura, poi da 165,27 dollari alla chiusura del 12 a 125,60 alla
chiusura del 20 (−24%, `avanti/diario.csv`), mentre il QQQ perdeva l'11,6% negli stessi giorni (Yahoo) e il 17 c'erano i conti del
trimestre. Un caso visto dopo non è una regola: qui si misura **su tutti i casi dell'S&P 500 dal 2016 al 2024**. Si conoscevano le
prove 1-45, in particolare la 28 (il tono delle notizie: sulle grandi nessun vantaggio) e la 36 (il vantaggio dei depositi vive fuori
seduta). Contano come **2 prove** (la strategia da sola, e la miscela con lei).

## Perché potrebbe funzionare, e perché no

* **A favore:** quando il capo se ne va all'improvviso, il mercato non sa subito quanto valga l'azienda senza di lui (chi lo sostituisce,
  perché è andato via, cosa verrà fuori dopo): le cattive notizie possono uscire a rate, e chi tiene il titolo (fondi grandi) vende in
  più giorni. Gli studi sulle uscite forzate trovano rendimenti negativi intorno all'annuncio (Warner, Watts e Wruck, Journal of Financial
  Economics 20, 1988; Huson, Malatesta e Parrino, JFE 74, 2004).
* **Contro (sospetti scritti prima):** (1) in media l'annuncio è già nel prezzo il primo giorno, e la sostituzione di un capo che andava
  male può essere una buona notizia; (2) molte uscite sono pensionamenti annunciati da mesi, non sorprese; (3) le notizie che parlano di
  dimissioni non sono sempre dimissioni (un capo di un'altra azienda, un'intervista, una voce smentita): la scelta con le parole sarà
  sporca; (4) pochi casi grandi possono fare il risultato (come Nvidia).

## I dati

* **Le notizie:** l'archivio di Alpaca (fonte Benzinga, `stock/dati/notizie.py`, nella memoria del lavoro di GitHub, mai nel
  repository), 2016-2024: ora di pubblicazione, simboli, titolo e riassunto.
* **La scelta delle notizie** (fissata qui, solo con le parole, senza guardare i prezzi):
  * il testo nomina il capo: «CEO» o «chief executive» (maiuscole e minuscole uguali);
  * e un'uscita: resign / resigns / resigned / resignation, steps down / step down / stepped down / stepping down, ousted / ousts,
    fired, terminated, departs / departure / departing, exits / exiting, leaves / leaving / to leave;
  * **non** un pensionamento: niente «retire», «retires», «retiring», «retirement»; **non** un ex capo: niente «former CEO»,
    «ex-CEO»;
  * la notizia ha **al massimo 3 simboli**, e **esattamente uno** di questi è un membro dell'S&P 500 quel giorno
    (`dati/P028_membri.csv.gz`); con due o più membri la notizia resta fuori e si conta (chiusa prima del calcolo, 22 novembre);
  * per azienda conta **la prima notizia**; le altre nei 60 giorni dopo non contano.
* **I prezzi:** barre al giorno di Alpaca con i dividendi e i frazionamenti (simbolo di allora, come le prove 31-41); lo SPY.

## La regola

* **Il giorno dell'annuncio:** se la notizia esce in un giorno di borsa prima delle 16:00 di New York, è quel giorno; altrimenti il
  primo giorno di borsa dopo.
* **L'ingresso, «il giorno dopo»:** alla **chiusura ufficiale** (asta di chiusura) del giorno di borsa **dopo** il giorno
  dell'annuncio si vende allo scoperto il titolo e si compra lo stesso valore di SPY.
* **L'uscita:** alla chiusura ufficiale della **20ª seduta** dopo l'ingresso (come le prove 10, 36 e 42); se il titolo sparisce prima,
  all'ultima chiusura.
* **Quanto:** il **10%** del conto all'inizio del giorno d'ingresso nel titolo venduto e il 10% in SPY; al massimo **10 posizioni**
  insieme (in ordine d'arrivo, a pari ora alfabetico); azioni intere; una posizione aperta sullo stesso titolo blocca.
* **Periodo:** annunci dal 4 gennaio 2016 al 30 novembre 2024, uscite entro il 31 dicembre 2024. Il periodo chiuso non si usa.

## I costi (fissati prima)

Alle aste nessuno scarto; slittamento 2 punti base per lato su tutti e quattro gli ordini; commissioni Interactive Brokers «fisso»;
prestito del titolo venduto allo scoperto **3% l'anno** (più delle prove 31-41, perché dopo una brutta notizia il prestito costa di più).
Versione con tutti i costi raddoppiati.

## L'esame (uguale alle prove 28 e 30-45)

**Da sola:** (1) Sharpe annuo con i costi più alto del tenere lo SPY sugli stessi giorni; (2) Sharpe corretto ≥ 0,95 con tutte le
serie del conto; (3) Sharpe sopra zero con i costi doppi; (4) almeno il 60% dei trimestri in guadagno.

**Per entrare nella miscela** (idea I30 rafforzata): Sharpe con i costi sopra zero, anche con i costi doppi; correlazione con la
miscela della prova 25 sotto 0,3; la miscela nuova (tre quarti la miscela, un quarto la parte nuova) con lo Sharpe più alto della
miscela e del tenere lo SPY; il t dello Sharpe della parte almeno 1,3; la miscela nuova più alta in almeno l'80% di 2000 campionamenti a
blocchi di 20 giorni.

**La risposta alla domanda del proprietario** (da leggere, è il motivo della prova): per tutti gli annunci, il titolo meno lo SPY
**dall'ingresso a 1, 5, 10 e 20 sedute**, media, mediana, t e quota in calo; lo stesso **dalla chiusura prima dell'annuncio
all'ingresso** (quanto era già successo); il guadagno senza il caso più grande; gli annunci con «effective immediately» nel testo a
parte; quante notizie scelte per anno e **quante per ogni parola trovata** (per vedere quanto è sporca la scelta; i titoli delle
notizie non si pubblicano, sono coperti da licenza: correzione del 22 novembre, prima del calcolo).

**Se passa uno dei due esami:** revisore separato, poi il periodo chiuso (dal 2 gennaio 2025 al 30 settembre 2026) una volta: la
famiglia «notizie sulle persone» non l'ha mai usato.
