# Prova 41 — «lazy prices»: comprate le aziende dell'S&P 500 che non cambiano il testo dei bilanci, vendute quelle che lo cambiano di più

Regole scritte il 19 novembre 2026 **prima di qualsiasi calcolo** e prima di scaricare i bilanci (idea I40 di `REGISTRO.md`, dalla
ricerca su GitHub, `IDEE_DA_GITHUB.md`, N3). Si conoscevano le prove 1-40: in particolare la 31 e la 39 (stessa forma, dati della SEC) e
la 38 (le commissioni minime con 100 posizioni). Contano come **2 prove** (la strategia da sola, e la miscela con lei): 99 nel conto.

## Perché dovrebbe funzionare

Cohen, Malloy e Nguyen, «Lazy Prices», Journal of Finance 75 (2020), NBER w25084 (prima versione 2018): quando un'azienda cambia molto il
testo del bilancio rispetto a quello dell'anno prima, spesso è una cattiva notizia (rischi nuovi, contenziosi, dirigenti nuovi), ma il
mercato non legge i bilanci e se ne accorge solo nei mesi dopo. Le aziende che non cambiano rendono di più di quelle che cambiano: da 34 a
58 punti base al mese con pesi per capitalizzazione (riassunto NBER, controllato dall'agente di ricerca), di più sulla sezione dei rischi.
È un dato della SEC che pochi lavorano (bisogna leggere migliaia di testi). Il nostro 2017-2024 è per metà prima della pubblicazione su
rivista.

**Sospetti scritti prima:**

* **il formato dei bilanci è cambiato** (dal 2019 il bilancio «inline XBRL», con i dati nascosti dentro il testo): un'azienda che cambia
  formato sembra cambiare il testo anche se non lo ha cambiato; si tolgono i dati nascosti (`ix:header`), ma il rischio resta;
* **l'estrazione del testo è fragile** (tabelle, numeri, impaginazione): si usano solo le parole, non i numeri;
* **solo le grandi**, e lo studio misura l'effetto più forte con pesi per capitalizzazione e sulle sezioni dei rischi; qui il testo intero
  del documento principale, a pesi uguali;
* **dopo la pubblicazione** (2018-2020) l'effetto può essere sparito.

## I dati

* **I bilanci:** per ogni azienda dell'S&P 500 (codice SEC di allora, `dati/P039_codici.csv.gz`), i 10-K e i 10-Q depositati dal 2015 al
  2024 (non le correzioni «/A»), dall'elenco dei depositi della SEC; si scarica il solo **documento principale**.
* **Il testo:** si tolgono i dati nascosti (`<ix:header>`), gli script e gli stili, poi tutti i tag; si decodificano i caratteri speciali;
  minuscole; le **parole** sono le sequenze di almeno 3 lettere (a-z).
* **La somiglianza:** la somiglianza del coseno fra i conteggi delle parole del bilancio e quelli del bilancio **dello stesso tipo**
  (10-K con 10-K, 10-Q con 10-Q) depositato fra 9 e 15 mesi prima, il più vicino a 12 mesi prima (lo studio confronta con lo stesso
  trimestre dell'anno prima). Nel repository va solo la somiglianza di ogni bilancio con la sua data di deposito (`dati/P041_somiglianze.csv.gz`),
  mai i testi. La SEC: al massimo 4 richieste al secondo (ne ammette 10), con l'indirizzo di contatto autorizzato solo dall'ambiente.

## La regola

* **Quando:** alla chiusura dell'ultimo giorno di borsa di ogni mese, da gennaio 2017 a novembre 2024 (si tiene da febbraio 2017 a
  dicembre 2024); i giorni e la composizione dell'indice da `dati/P028_membri.csv.gz`.
* **Il segnale:** la somiglianza del bilancio più recente dell'azienda depositato **prima** del giorno della decisione e non più di 4
  mesi prima; senza un bilancio così, o senza il bilancio dell'anno prima per il confronto, il titolo resta fuori quel mese. Se i titoli
  con il segnale sono meno di 100, quel mese niente.
* **La scelta:** i 50 con la somiglianza **più alta** (non cambiano) si comprano, i 50 con la **più bassa** (cambiano di più) si vendono
  allo scoperto (il 20% più alto e il 20% più basso, al massimo 50 ciascuno, come le prove 31, 38 e 39); a pari valore in ordine
  alfabetico.
* **Quanto:** metà del conto nei comprati e metà nei venduti, a pesi uguali; si ribilancia ogni fine mese.
* **Periodo:** fino al 31 dicembre 2024. Il periodo chiuso non si usa.

## I costi (fissati prima, come le prove 31, 38 e 39)

Metà dello scarto misurato di ogni titolo (`dati/ESITO_CONTROLLI_UNIVERSO.md`), slittamento come nelle prove 28-39, commissioni
Interactive Brokers «fisso», prestito dei venduti allo scoperto 0,5% l'anno. Versione con tutti i costi raddoppiati.

## L'esame (uguale alle prove 28 e 30-40)

**Da sola:** (1) Sharpe annuo con i costi più alto del tenere lo SPY sugli stessi giorni; (2) Sharpe corretto ≥ 0,95 con tutte le
serie del conto; (3) Sharpe sopra zero con i costi doppi; (4) almeno il 60% dei trimestri in guadagno.

**Per entrare nella miscela** (idea I30 rafforzata): Sharpe con i costi sopra zero, anche con i costi doppi; correlazione con la
miscela della prova 25 sotto 0,3; la miscela nuova (tre quarti la miscela, un quarto la parte nuova) con lo Sharpe più alto della
miscela e del tenere lo SPY; il t dello Sharpe della parte almeno 1,3; la miscela nuova più alta in almeno l'80% di 2000 campionamenti
a blocchi di 20 giorni.

Da leggere accanto (non cambiano l'esito): comprati meno venduti mese per mese prima dei costi (media, t, mesi positivi); quanto cambia
il portafoglio ogni mese; la somiglianza mediana dei comprati e dei venduti; la somiglianza mediana per anno (per vedere il cambio di
formato del 2019); comprati meno venduti prima e dopo il 2020; quanti membri hanno il segnale; l'anno per anno.

**Se passa uno dei due esami:** revisore separato, poi il periodo chiuso (dal 2 gennaio 2025 al 30 settembre 2026) **una volta**: la
famiglia «testi della SEC» non l'ha mai usato.
