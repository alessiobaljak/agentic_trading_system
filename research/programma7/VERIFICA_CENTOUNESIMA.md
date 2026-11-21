# Verifica della prova 163 (regole in `CENTOUNESIMA.md`), 21 novembre 2026

Modalità verifica: nessun calcolo di risultati, nessun file di dati scaricato (solo piccole richieste di prova alle interfacce, con lettura del
solo numero di righe e delle date; nessun tasso e nessun prezzo guardato). Regole committate: `039e1e3` (21 novembre 2026, 09:50 UTC).

## Esito: NON eseguibile così com'è. Un punto blocca, gli altri vanno chiusi prima del calcolo.

## Cosa risponde davvero ciascuna interfaccia
* **Funding di Hyperliquid** (`fundingHistory`): risponde, 500 righe per richiesta, ogni ora con qualche millisecondo di scarto (esempio
  00:00:00.048). Bitcoin parte dal 12 maggio 2023: copre il 5 giugno 2023. Il codice `settantatreesima.storico` e `funding_hl` si può riusare
  (la tenuta del giorno si calcola con «orario meno 1 minuto», e va tenuta uguale).
* **Candele giornaliere di Hyperliquid** (`candleSnapshot`, `1d`): arrivano fino al 28 marzo 2023 (Bitcoin); anche per kPEPE dal maggio 2023.
  Contengono apertura, massimo, minimo, chiusura.
* **Candele orarie di Hyperliquid** (`1h`): la borsa tiene **solo le ultime 5.000 candele** per intervallo. Oggi le orarie partono dal
  **26 aprile 2026**; chiedendo marzo 2024, marzo 2025 o gennaio 2026 la risposta è vuota. Per intervallo: 15 minuti solo da inizio ottobre
  2026, 4 ore dal 10 agosto 2024, 8 ore e 12 ore e 1 giorno dal marzo 2023.
* **Prezzo di Hyperliquid**: le candele sono di prezzi scambiati (non mark); la risposta non ha un campo mark. Binance dell'archivio: mark
  (`markPriceKlines`) e scambiato (`klines`) a 1 ora, esistenti dal giugno 2023 (controllati Bitcoin 2023-06 ed Ether 2026-10).
* **Funding di Binance** archivio mensile: il file di ottobre 2026 esiste. Tutti gli altri mesi non controllati uno per uno (solo la prova
  dell'interfaccia).
* **Commissione di Hyperliquid**: documentazione pubblica (`hyperliquid.gitbook.io/hyperliquid-docs/trading/fees`, tabella dei livelli sui
  perpetui, livello 0, volume a 14 giorni sotto i 5 milioni): **a mercato (chi prende liquidità) 0,045%**, con ordine limite (chi dà
  liquidità) 0,015%. Confermata la cifra di riserva delle regole. Va scritta con questa fonte.

## Ambiguità e punti non eseguibili

1. **BLOCCANTE: i prezzi orari di Hyperliquid prima del 26 aprile 2026 non esistono.** Il punto 4 chiede un controllo ogni ora con i prezzi
   delle due borse, e la regola dei dati dice «candele orarie di tutte e due le borse»: per 34 dei 41 mesi non è possibile, e le regole non
   dicono cosa fare se mancano. Il controllo della liquidazione e dei giorni a rischio, e il «nessuna liquidazione» dell'esame, dipenderebbero
   da due scale diverse. *Correzione proposta:* «Fino al 25 aprile 2026 compreso il controllo della liquidazione e dei giorni a rischio usa,
   per Hyperliquid, il massimo e il minimo della candela giornaliera (le due borse con lo stesso criterio: per Binance anche il massimo e
   minimo giornaliero del prezzo mark, ricavati dalle candele orarie), prendendo per ogni gamba il lato peggiore, che è conservativo; dal
   26 aprile 2026 si usano le candele orarie; il rapporto dice quanti giorni hanno avuto ciascun criterio.»
2. **Prezzo scambiato contro mark.** Binance dà mark, Hyperliquid solo scambiato: il rendimento delle gambe (punto 5) mischia due prezzi
   diversi. *Correzione:* «Il rendimento e le spese usano il prezzo scambiato (Binance `klines`, Hyperliquid `candleSnapshot`); il mark di
   Binance serve solo per la liquidazione.» (oppure, se si vuole il mark per tutto, il rapporto deve dire che Hyperliquid non lo dà.)
3. **Prezzo di apertura e chiusura del giorno.** Non scritto quale prezzo si usa per aprire, chiudere e calcolare il rendimento. *Correzione:*
   «Il prezzo del giorno D è l'apertura della candela oraria delle 00:00 UTC di D (apertura della candela giornaliera per Hyperliquid prima
   del 26 aprile 2026, che coincide con la 00:00); rendimento di D = apertura di D+1 diviso apertura di D meno 1, per entrambe le borse.»
4. **Capitale e trasferimento da 1 USDT: il risultato dipende da un numero che non c'è.** Il costo fisso di 1 USDT al giorno, se il
   trasferimento avviene ogni giorno, sono circa 365 USDT l'anno: con 1.000 USDT è il 36% l'anno e uccide la prova; con 100.000 è nullo. Non
   si dice il capitale in USDT, né se si trasferisce ogni giorno o solo quando c'è uno squilibrio. *Correzione (da far decidere):* «Capitale
   iniziale 1.000 USDT (come il demo); si trasferisce solo se la differenza fra il margine di una borsa e la metà supera il 10% del capitale
   corrente; ogni trasferimento costa 1 USDT.» Alternativa senza soglia: dire che il capitale è 10.000 USDT.
5. **Capitale fisso o composto.** Non scritto se il valore delle gambe resta fisso al capitale iniziale o segue il patrimonio, né se ogni
   giorno si riportano le gambe al peso uguale (e se quel riequilibrio paga spese). Il punto 6 dice «riequilibrio quando cambia il numero di
   monete», ma il numero cambia solo alle decisioni. *Correzione:* «Le gambe si aprono alla decisione con valore = patrimonio totale (margini
   più guadagni) diviso il numero di monete scelte, e restano con le quote fisse fino alla decisione dopo (nessun riequilibrio giornaliero);
   alla decisione si riportano al peso uguale, pagando le spese solo sul valore scambiato.»
6. **Giorno della decisione e primo giorno.** «Primo giorno del mese» e «lunedì»: l'apertura delle 00:00 UTC di quel giorno, sì. Ma la
   prima decisione della variante A è il 1° luglio 2023 (il 5 giugno non è il primo del mese e servono 30 giorni di storia; a giugno 2023 nessuna
   posizione), mentre la B parte lunedì 5 giugno 2023 (era un lunedì). *Correzione:* scrivere queste due date e che il 2023 della A
   «da giugno» ha giugno a zero.
7. **Storia mancante e buchi.** Non scritto cosa fa il segnale se in uno dei L giorni manca ogni pagamento di una delle due borse, o se la
   moneta ha meno di L giorni di storia. *Correzione:* «Una moneta è candidata a D solo se in ognuno dei L giorni prima di D ci sono almeno
   un pagamento su Hyperliquid e uno su Binance; altrimenti nessuna posizione quella volta. Un giorno senza prezzi di una delle due borse
   mentre la posizione è aperta: la posizione si chiude all'ultima apertura disponibile e il giorno si segnala nel rapporto.»
8. **Universo: «30 giorni interi di funding e prezzi su tutte e due».** Non è chiaro se i 30 giorni siano consecutivi né se valgano per la
   moneta o per il giorno (il caso è già deciso dal punto 7, ma la frase dell'universo no). Inoltre il metodo di `settantatreesima.funding_hl`
   passa tutte le 235 monete di `meta`, cioè anche le 56 marcate `isDelisted`; le regole dicono «quotate oggi». *Correzione:* «Si escludono
   le monete con `isDelisted` vero; l'elenco finale (nome Hyperliquid, simbolo Binance, primo giorno con 30 giorni interi di dati su
   entrambe) si scrive nel rapporto prima dei risultati.»
9. **Scala del prezzo nell'abbinamento.** `funding_hl` per un nome senza `k` prova sia `XUSDT` sia `1000XUSDT`: se una moneta Hyperliquid senza
   `k` finisse su un contratto Binance «1000…», i prezzi differiscono di mille volte e le gambe non sono più sulla stessa quantità.
   *Correzione:* «Dopo l'abbinamento, il rapporto fra i prezzi di chiusura del primo giorno comune deve stare fra 0,9 e 1,1 (per `k`: fra
   0,9 e 1,1 dopo il fattore 1000 già nel nome); altrimenti la moneta è tolta dall'universo e scritta nell'elenco.»
10. **Funding: orario e segno.** La regola 5 dice «orari dopo l'apertura di D fino all'apertura di D+1 compresa», ma i pagamenti hanno
    millisecondi di scarto (Hyperliquid 00:00:00.048; Binance simile) e la regola 1 usa «prima delle 00:00». Va fissata la convenzione.
    *Correzione:* «Un pagamento con orario t appartiene al giorno ((t − 1 minuto) diviso un giorno), come in `settantatreesima.funding_hl`:
    quello delle 00:00 di D+1 conta per il giorno D e nella regola 1 per i giorni prima di D+1.» Inoltre scrivere: funding incassato dalla
    gamba venduta e pagato dalla comprata quando il tasso è positivo, valore = quota della gamba × tasso del pagamento (come nel motore di G1).
    Binance con ogni 1, 4 e 8 ore: si sommano i pagamenti veri del giorno, nessuna ipotesi sulla cadenza.
11. **Unità del segnale.** d è «media giornaliera» in frazione del valore, in unità di tasso; θ 0,0274% = 10%/365. Va scritto che d e θ sono
    nella stessa unità (frazione al giorno), e che Binance dei mesi dopo il 31 ottobre 2026 non si usa. *Correzione:* una riga con l'unità.
12. **Margine: definizione.** «metà capitale ± guadagni e perdite ± funding e spese» non dice se le perdite non realizzate contano (devono,
    per la liquidazione) e quando il funding entra nel margine (a ogni pagamento orario o a fine giorno). *Correzione:* «Il margine di una
    borsa in ogni ora = deposito + risultato non realizzato delle sue gambe + funding incassato meno pagato fino a quell'ora − spese pagate; il
    mantenimento = 0,5% del valore corrente delle sue gambe (valore all'ora, non all'apertura).»
13. **Il trasferimento con un giorno di ritardo.** Non scritto su quale margine si calcola la metà (quello di D o quello di D+1 al momento
    dell'arrivo) né se il trasferimento è possibile da una borsa in liquidazione. *Correzione:* «Alla decisione di D l'importo è la differenza fra il
    margine di D e la metà del totale di D; entra nel margine della borsa ricevente alla decisione di D+1 e intanto è tolto dal margine della
    borsa che lo manda (non è in nessuno dei due).»
14. **Liquidazione: seguito.** «L'altra gamba si chiude alla decisione dopo»: per la variante A può essere fino a 30 giorni dopo, con una
    gamba scoperta (rischio sul prezzo). Non dice se, dopo una liquidazione, la moneta può rientrare, né se «la decisione dopo» è quella
    giornaliera del trasferimento o quella della variante. Siccome l'esame chiede nessuna liquidazione, il punto pesa poco. *Correzione:* «Si
    chiude alla prossima apertura delle 00:00 UTC (non alla prossima decisione della variante), la moneta può rientrare solo alla decisione
    successiva della variante; la prova comunque non passa.»
15. **Giorni a rischio.** Scritto «margine sotto il 10% del valore delle sue gambe»: non dice se il 10% è calcolato sul valore all'ora né se si
    conta il giorno una volta anche con più ore. *Correzione:* «Si conta il giorno se in almeno un'ora (o, prima del 26 aprile 2026, con il lato
    peggiore del giorno) il margine scende sotto il 10% del valore corrente delle gambe di quella borsa.»
16. **Spese: formula.** «Si paga solo sul valore scambiato» ma non dice se lo scarto di prezzo vale su ogni gamba a ogni scambio e come
    si somma. *Correzione:* «Per ogni scambio di valore V su una borsa si paga V × (commissione + scarto della moneta): Binance 0,05% +
    0,01% (BTC, ETH, SOL) o 0,02% (le altre); Hyperliquid 0,045% + lo stesso scarto, in 0,01% e 0,02%; scambi: apertura, chiusura, cambio di
    lato (due scambi: chiusura e apertura), variazione di quota alla decisione, chiusura per liquidazione (più la perdita del 1%); il tutto
    all'apertura della decisione.» Con questa formula un giro completo vale circa 0,23% (BTC, ETH, SOL) e 0,27% (le altre): le regole dicono
    «circa 0,28%», va corretto o spiegato (stesso ordine di grandezza, non cambia le soglie).
17. **Ultimo giorno.** Non scritto cosa succede alle posizioni aperte al 31 ottobre 2026. *Correzione:* «Le posizioni aperte si chiudono
    all'apertura del 1° novembre 2026 pagando le spese, o non si chiudono e le spese di uscita non si contano: scegliere; si propone di
    chiuderle (conservativo).»
18. **Serie settimanali e anni.** «Come nelle prove 157-162» rimanda a codice, ma le settimane e gli anni vanno scritti: *Correzione:* «Settimane
    lunedì-domenica, rendimento della settimana = somma dei rendimenti giornalieri netti; anni di calendario; 2023 dal 5 giugno (per la A, giugno
    2023 è a zero e conta); t = Sharpe settimanale annualizzato × radice(settimane/52).»
19. **Controlli descrittivi.** «Le prime 30 monete per volume»: non è detto volume dove, quando. *Correzione:* «Volume in USDT medio giornaliero su
    Binance nei 30 giorni prima di ogni decisione, prime 30 a quella data (descrittivo, non cambia le posizioni).»

## Punti verificati e a posto
* Segno: d > soglia → venduta su Hyperliquid, comprata su Binance (incassa d); funzione `funding_hl` abbina le monete come scritto.
* Soglie 10% e 20% l'anno corrispondono a 0,0274% e 0,0548% al giorno (diviso 365).
* Esame, famiglie (`asticella.corretto_famiglie(nuove, candidate)`, serie settimanali nette in `nuove`) e file consegnati sono eseguibili;
  sono già scritte le due sole varianti.
* Binance archivio mensile: i file orari mark e scambiato e il funding (fino a ottobre 2026) rispondono.
* Rischio piattaforma e sopravvivenza (solo monete di oggi): già scritti nelle regole.

## Domande aperte (testuali)
1. Quale capitale in USDT (punto 4) e quale regola per il trasferimento da 1 USDT: ogni giorno, oppure solo oltre una soglia di squilibrio?
2. Il controllo della liquidazione prima del 26 aprile 2026 con il massimo e il minimo giornaliero di Hyperliquid (punto 1) va bene come
   regola scritta prima, sapendo che è più severo di un controllo orario?
3. Le posizioni aperte al 31 ottobre 2026 si chiudono pagando le spese (punto 17)?
4. Si escludono le monete già ritirate da Hyperliquid (`isDelisted`) dall'universo (punto 8)?
