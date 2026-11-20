# Prova 42 — gli attivisti: comprare in seduta dopo il deposito del modulo 13D alla SEC, coperti con l'IWM, per 20 sedute

Regole scritte il 19 novembre 2026 **prima di qualsiasi calcolo** e prima di scaricare l'elenco dei depositi (idea I43 di
`REGISTRO.md`, dalla ricerca su GitHub, `IDEE_DA_GITHUB.md`, N6). Si conoscevano le prove 1-41: in particolare la 36 (il vantaggio di un
deposito alla SEC vive fra la pubblicazione e l'apertura dopo, dove lo scarto è grande), il controllo P036b (dopo la chiusura lo scarto
pagato davvero è di circa 20 punti base per lato sulle grandi), la 27 e la 34 (le aziende piccole: filtri e costi). Contano come **2
prove** (la strategia da sola, e la miscela con lei): 103 nel conto (la prova 43 è stata calcolata prima).

## Perché dovrebbe funzionare

Chi compra più del 5% di un'azienda quotata con l'intenzione di influenzarla deve depositare il modulo 13D alla SEC entro 10 giorni (dal
febbraio 2024, 5 giorni lavorativi). Brav, Jiang, Partnoy e Thomas, «Hedge Fund Activism, Corporate Governance, and Firm Performance»,
Journal of Finance 63 (2008): intorno al deposito il titolo rende circa il 7% più del mercato fra 20 giorni prima e 20 giorni dopo, una
parte sale ancora **dopo** il deposito, e non torna indietro nei mesi seguenti (Bebchuk, Brav e Jiang, Columbia Law Review 115, 2015).
Il motivo: l'attivista cambia davvero l'azienda (dividendi, vendite di rami, posti nel consiglio), e il mercato non lo prezza tutto il
primo giorno. È un dato pubblico della SEC, con l'ora vera della pubblicazione.

**La domanda della prova:** quanto rende chi compra **in seduta** (dove lo scarto è piccolo) o **all'asta d'apertura** dopo la
pubblicazione, cioè senza la parte che sale subito fuori seduta, e tiene 20 sedute coperto con il fondo delle aziende piccole?

**Sospetti scritti prima:**

* **non tutti i 13D sono attivisti**: lo depositano anche chi compra un'azienda (accordi di voto prima di una fusione: il prezzo è già
  fermo a quello dell'offerta), i fondi di investimento privati, i soci che superano il 5% per altri motivi. Lo studio li ha scelti a
  mano; qui si prendono tutti i primi depositi (non le correzioni «/A»): l'effetto sarà diluito;
* **il salto avviene alla pubblicazione**, spesso dopo la chiusura: chi entra in seduta o all'apertura dopo arriva tardi (è la lezione
  della prova 36). Resta da vedere se dopo c'è ancora una salita;
* **lo studio va dal 2001 al 2006**; il nostro 2016-2024 è molto dopo la pubblicazione, e gli attivisti oggi sono seguiti da servizi a
  pagamento che leggono la SEC in pochi secondi;
* **le aziende prese di mira sono piccole**: lo scarto è più largo di quello delle 500 grandi; da qui i filtri e lo scarto misurato.

## I dati (da `stock/dati/attivisti.py`, dati pubblici della SEC, niente prezzi)

* **I depositi:** gli indici trimestrali della SEC (`edgar/full-index/AAAA/QTRn/form.gz`), i moduli di tipo esattamente «SC 13D» (non
  «SC 13D/A») depositati dal 4 gennaio 2016 al 29 novembre 2024; per ognuno l'intestazione del deposito (`…-index-headers.html`):
  **l'ora di accettazione**, l'azienda oggetto (codice SEC) e chi deposita. Si scarta un deposito in cui chi deposita è l'azienda
  oggetto stessa.
* **L'ora:** l'ora di accettazione della SEC, che è il momento in cui il deposito diventa pubblico. Prima del calcolo sui prezzi si
  verifica su un campione di depositi che l'ora dell'intestazione sia quella di New York, confrontandola con l'elenco dei depositi
  dell'azienda (`acceptanceDateTime`, l'ora usata nella prova 36); l'esito si scrive qui sotto prima del calcolo.
* **Il simbolo di allora:** dai moduli dei dirigenti (3, 4, 5) dell'azienda oggetto (`azioni_circolazione.codici_dei_moduli`): i
  periodi in cui l'azienda ha usato ogni simbolo (dal primo all'ultimo modulo di fila con quel simbolo, `dati/sec_simboli.csv.gz`); vale
  il periodo **iniziato per ultimo prima del giorno del 13D**, se non è finito più di 365 giorni prima; senza simbolo il deposito resta
  fuori (e si conta), come quello con un simbolo senza prezzi.
* Nel repository va solo l'elenco dei depositi con l'ora, il codice e il simbolo (`dati/sec_attivisti.csv.gz`), mai i prezzi. La SEC: al
  massimo 4 richieste al secondo, con l'indirizzo di contatto solo dall'ambiente (il segreto `SEC_CONTATTO` del repository).

## La regola

* **Quando si sa:** l'ora di accettazione **più 2 minuti** (come la prova 36).
* **L'ingresso:**
  * se quel momento cade **in seduta, fra le 9:30 e le 15:57** di New York di un giorno di borsa: all'apertura della prima barra al
    minuto (Alpaca, tutte le borse, simbolo di allora) che inizia almeno 2 minuti dopo l'accettazione, fino alle 15:59; se fino alle
    15:59 non c'è una barra, come il caso dopo;
  * altrimenti (prima delle 9:30, dopo le 15:57, giorni senza borsa): **all'apertura ufficiale** (l'asta d'apertura, il prezzo «open»
    della barra al giorno) della prima seduta dopo.
* **I filtri** (come la prova 27, sul giorno di borsa prima dell'ingresso): chiusura di almeno **5 dollari** e mediana dei dollari
  scambiati nelle 20 sedute prima di almeno **2 milioni**.
* **L'uscita:** alla **chiusura ufficiale** (l'asta di chiusura) della **20ª seduta dopo** quella dell'ingresso. Se il titolo sparisce
  dal listino prima, all'ultimo prezzo come nelle prove 27-41.
* **La copertura:** con ogni acquisto si vende allo scoperto **lo stesso valore di IWM** (il fondo delle aziende piccole), con gli
  stessi momenti di ingresso e di uscita.
* **Quanto:** il **2,5%** del valore del conto all'inizio del giorno dell'ingresso nel titolo e il 2,5% venduto in IWM; al massimo **20
  posizioni** insieme (al più il 100% del conto fra comprato e venduto: niente leva oltre a quella delle prove 31-41); oltre, si salta,
  in ordine d'arrivo (a pari ora, in ordine alfabetico); azioni intere. **Al massimo un ingresso per azienda**: un 13D che arriva mentre
  la posizione sullo stesso titolo è aperta non cambia niente.
* **Periodo:** i depositi dal 4 gennaio 2016 al 29 novembre 2024, uscite entro il 31 dicembre 2024. Il periodo chiuso non si usa.

## I costi (fissati prima, come la prova 36)

* **In seduta:** metà dello scarto misurato sulle quotazioni migliori di Alpaca (tutte le borse) per un campione di **500 ingressi in
  seduta** estratti a caso (seme 42), l'ultima quotazione valida prima della fine del minuto dell'ingresso (`stock/dati/scarto.py`); la
  mediana si applica a tutti gli ingressi in seduta. Per IWM: metà della mediana dello scarto misurato **negli stessi minuti del
  campione** (aggiunta del 20 novembre, prima del calcolo: IWM non è in `dati/ESITO_CONTROLLI_UNIVERSO.md`, che le regole citavano).
* **Alle aste** (apertura e chiusura ufficiali): nessuno scarto.
* **Slittamento** 2 punti base per lato; commissioni Interactive Brokers «fisso» (0,005 dollari ad azione, minimo 1 dollaro, massimo
  l'1%); prestito di IWM venduto allo scoperto 0,5% l'anno. Versione con tutti i costi raddoppiati.

## L'esame (uguale alle prove 28 e 30-41)

**Da sola:** (1) Sharpe annuo con i costi più alto del tenere lo SPY e del tenere l'IWM sugli stessi giorni; (2) Sharpe corretto ≥ 0,95
con tutte le serie del conto; (3) Sharpe sopra zero con i costi doppi; (4) almeno il 60% dei trimestri in guadagno.

**Per entrare nella miscela** (idea I30 rafforzata): Sharpe con i costi sopra zero, anche con i costi doppi; correlazione con la
miscela della prova 25 sotto 0,3; la miscela nuova (tre quarti la miscela, un quarto la parte nuova) con lo Sharpe più alto della
miscela e del tenere lo SPY; il t dello Sharpe della parte almeno 1,3; la miscela nuova più alta in almeno l'80% di 2000 campionamenti a
blocchi di 20 giorni.

Da leggere accanto (non cambiano l'esito): il guadagno medio per evento meno l'IWM, prima e dopo i costi, con il t; lo stesso per
gli ingressi in seduta e per quelli all'apertura; **quanto è già salito il titolo** fra la chiusura prima dell'accettazione e
l'ingresso (la parte persa); quanti depositi per anno e per fascia d'ora, quanti scartati da ogni filtro e quanti saltati per i posti;
le aziende dell'S&P 500 a parte; l'anno per anno.

**Se passa uno dei due esami:** revisore separato, poi il periodo chiuso (dal 2 gennaio 2025 al 30 settembre 2026) **una volta**: la
famiglia «attivisti» non l'ha mai usato (dal 18 dicembre 2024 la SEC dovrebbe chiamare il modulo «SCHEDULE 13D», da verificare
allora: va preso anche quel nome).
