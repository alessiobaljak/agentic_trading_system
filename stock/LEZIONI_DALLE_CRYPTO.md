# Le lezioni delle crypto da portare sulle azioni

Scritto il 24 ottobre 2026 dalla sessione delle crypto, per la sessione «trading stock». Le fonti sono nel repository; qui il
succo. Per i dettagli: `research/REGISTRO.md` (le 137 prove delle crypto), `research/programma6/STATO.md` (le lezioni numerate),
`docs/storia/` (la storia del progetto e gli errori da non ripetere).

## Il metodo (quello che ha funzionato)

1. **Le regole si scrivono prima di guardare i risultati** (un file per prova, committato prima del calcolo, e la riga nel
   registro). Il primo sistema (il «gate», agosto-ottobre 2026) provava migliaia di combinazioni e teneva le migliori: sul passato
   sembravano ottime, in paper hanno perso (784 operazioni, −18,3%).
2. **Si contano tutte le prove**, anche quelle bocciate, e l'asticella dipende da quante: lo **Sharpe corretto per i tentativi**
   (Bailey e López de Prado 2014), contando i **gruppi di prove simili** (López de Prado 2019-2020) e lasciando fuori dalla
   dispersione le prove che perdono di sicuro (`research/programma6/ASTICELLA.md`). Soglia 0,95; accanto il t dello Sharpe contro
   3 (Harvey, Liu e Zhu 2016).
3. **Un revisore separato** (una sessione che non ha scritto il codice) ricontrolla ogni strategia promettente prima del paper. Il
   23 ottobre tre revisioni hanno trovato tre errori veri: le parità decise da un arrotondamento, prove dimenticate nel conto, dati
   sbagliati in una strategia a eventi (`research/programma6/CONTROLLO_PARITA.md`, `research/programma7/REVISIONE_G11.md`,
   `REVISIONE_G12.md`).
4. **Il paper è una conferma**, mai un modo per scegliere.

## Gli errori tipici (da cercare sempre)

* **Dati del futuro**: un dato usato prima che fosse disponibile (l'ora esatta di pubblicazione conta).
* **Titoli sopravvissuti**: l'universo deve essere quello di allora, con i titoli poi tolti dal listino e il loro ultimo prezzo.
* **Costi**: commissioni, scarto fra acquisto e vendita (va misurato, non inventato), e per gli ordini limite l'ipotesi di
  esecuzione (se il prezzo tocca appena il livello, l'ordine si esegue davvero?).
* **Operazioni impossibili**: entrare in un titolo sospeso o già tolto dal listino.
* **Scegliere la migliore fra varianti simili**: il conto per gruppi non la punisce; trattare le varianti con sospetto.

## Cosa abbiamo imparato sui mercati (da verificare sulle azioni, non da copiare)

* Le regole di **indicatori tecnici** sul prezzo, da sole e dentro la giornata, perdono dopo i costi (decine di prove, scalping
  compreso): il movimento di un giorno è quasi tutto caso, e il costo di ogni operazione è sicuro.
* I vantaggi che reggono vengono da **ragioni economiche**: chi paga un premio per una posizione affollata (il funding fra le
  monete, F5), i **flussi forzati** e gli **eventi** (le monete appena quotate che scendono). Sulle azioni gli equivalenti studiati
  sono i premi per il rischio e i flussi (per esempio i fattori pubblicati, gli eventi di indice, le date di bilancio), da provare
  con lo stesso metodo e con il sospetto che i fattori pubblicati su dati vecchi non reggano più (sulle crypto momento, dimensione e
  «giorno migliore del mese» non reggevano).
* **Decidere più spesso non aiuta da solo**: conta quanto è lento il segnale rispetto ai costi.
* **Gli ordini limite** abbassano i costi, ma il vantaggio stimato dipende dall'ipotesi di esecuzione: va misurato sul conto demo.
