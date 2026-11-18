# Prova 39 — l'emissione netta di azioni: comprate le aziende dell'S&P 500 che hanno ridotto di più le azioni, vendute quelle che le hanno aumentate

Regole scritte il 18 novembre 2026 **prima di qualsiasi calcolo** e prima di scaricare i dati (idea I42 di `REGISTRO.md`, dalla ricerca
su GitHub, `IDEE_DA_GITHUB.md`, N5). Si conoscevano le prove 1-38: in particolare la 31 (stessa forma, caduta alla revisione per i
conti della SEC rifatti dopo e per i codici SEC sbagliati) e la 38 (le commissioni minime con 100 posizioni). Contano come **2 prove**
(la strategia da sola, e la miscela con lei): 95 nel conto.

## Perché dovrebbe funzionare

Pontiff e Woodgate, «Share issuance and cross-sectional returns», Journal of Finance 63 (2008); Fama e French, «Dissecting anomalies»,
Journal of Finance 63 (2008): le aziende che riducono il numero di azioni (riacquisti) rendono di più, quelle che lo aumentano (aumenti
di capitale, azioni ai dipendenti, fusioni pagate in azioni) rendono di meno; per Fama e French l'effetto c'è **anche fra le grandi**. La
replica aperta di Chen e Zimmermann lo conferma (t 7,08). Chi conosce l'azienda meglio di tutti (la direzione) compra quando il prezzo è
basso e vende quando è alto. Il ritmo è lento: il portafoglio cambia poco, i costi pesano meno che nella prova 38.

**Sospetti scritti prima:**

* **dopo la pubblicazione** (2008): il nostro 2016-2024 è tutto dopo;
* **2016-2024 è il periodo delle grandi tecnologiche**, che riacquistano molte azioni: una parte del risultato può essere il settore,
  non l'emissione;
* **i numeri della SEC**: si usa solo il numero di azioni scritto in copertina di ogni bilancio (`dei:EntityCommonStockSharesOutstanding`),
  con la **data del deposito**: un valore si usa solo dal giorno dopo il deposito (non i valori rifatti dopo, il difetto bloccante della
  prova 31);
* **i codici SEC del simbolo di allora**: non un solo codice per simbolo (difetto della prova 31), ma il codice dell'azienda che i moduli
  dei dirigenti depositati nei 365 giorni prima legano a quel simbolo;
* **i frazionamenti** cambiano il numero di azioni senza emissione: si tolgono con le azioni societarie di Alpaca.

## I dati

* **Le azioni in circolazione:** i fatti di ogni azienda dalla SEC (`https://data.sec.gov/api/xbrl/companyfacts/CIK##########.json`),
  elemento `dei:EntityCommonStockSharesOutstanding`: per ogni deposito (numero del deposito) e data di riferimento, la somma delle classi;
  si tiene la data del deposito (`filed`). File committato con soli dati pubblici: `dati/P039_azioni.csv.gz`.
* **Il codice SEC del simbolo di allora:** dai moduli 3, 4 e 5 dei dirigenti (`ISSUERCIK`, `ISSUERTRADINGSYMBOL`, data del deposito) già
  in `~/stock_dati/sec/form345/`: alla data della decisione, il codice dell'ultimo modulo con quel simbolo depositato nei 365 giorni
  prima. File committato: `dati/P039_codici.csv.gz`.
* **Prezzi e frazionamenti:** Alpaca, simbolo di allora (come le prove 28-38).

## La regola

* **Quando:** alla chiusura dell'ultimo giorno di borsa di ogni mese, da gennaio 2017 a novembre 2024 (si tiene da febbraio 2017 a
  dicembre 2024); i giorni e la composizione dell'indice da `dati/P028_membri.csv.gz`.
* **Il segnale:** per ogni membro, il numero di azioni dell'ultimo deposito fatto **prima** del giorno della decisione (data di
  riferimento d1), e quello del deposito con la data di riferimento d0 più vicina a 12 mesi prima di d1, fra 9 e 15 mesi prima;
  emissione = log(azioni in d1 / (azioni in d0 × i frazionamenti fra d0 e d1)). Senza i due valori, o con un codice SEC che non si
  trova, il titolo resta fuori quel mese. Se i titoli con il segnale sono meno di 100, quel mese niente.
* **La scelta:** i 50 con l'emissione **più bassa** (hanno ridotto di più le azioni) si comprano, i 50 con la **più alta** si vendono
  allo scoperto (il 20% più basso e il 20% più alto, al massimo 50 ciascuno, come le prove 31 e 38); a pari valore in ordine alfabetico.
* **Quanto:** metà del conto nei comprati e metà nei venduti, a pesi uguali; si ribilancia ogni fine mese.
* **Periodo:** fino al 31 dicembre 2024. Il periodo chiuso non si usa.

## I costi (fissati prima, come le prove 31 e 38)

Metà dello scarto misurato di ogni titolo (`dati/ESITO_CONTROLLI_UNIVERSO.md`), slittamento come nelle prove 28-38, commissioni
Interactive Brokers «fisso», prestito dei venduti allo scoperto 0,5% l'anno. Versione con tutti i costi raddoppiati.

## L'esame (uguale alle prove 28 e 30-38)

**Da sola:** (1) Sharpe annuo con i costi più alto del tenere lo SPY sugli stessi giorni; (2) Sharpe corretto ≥ 0,95 con tutte le
serie del conto; (3) Sharpe sopra zero con i costi doppi; (4) almeno il 60% dei trimestri in guadagno.

**Per entrare nella miscela** (idea I30 rafforzata): Sharpe con i costi sopra zero, anche con i costi doppi; correlazione con la
miscela della prova 25 sotto 0,3; la miscela nuova (tre quarti la miscela, un quarto la parte nuova) con lo Sharpe più alto della
miscela e del tenere lo SPY; il t dello Sharpe della parte almeno 1,3; la miscela nuova più alta in almeno l'80% di 2000 campionamenti
a blocchi di 20 giorni.

Da leggere accanto (non cambiano l'esito): comprati meno venduti mese per mese prima dei costi (media, t, mesi positivi); quanto
cambia il portafoglio ogni mese; l'emissione mediana dei comprati e dei venduti; quanti membri hanno il segnale; l'anno per anno; la
correlazione con QQQ meno SPY (le grandi tecnologiche).

**Se passa uno dei due esami:** revisore separato, poi il periodo chiuso (dal 2 gennaio 2025 al 30 settembre 2026) **una volta**: la
famiglia «conti della SEC» non l'ha ancora usato (la prova 31 si è fermata alla revisione).
