# Controllo dopo la prova 36 — quanto costa davvero comprare fuori seduta

Metodo scritto il 16 novembre 2026, su richiesta del proprietario («misura il costo vero degli acquisti fuori seduta»), **prima di
scaricare le quotazioni e le operazioni di mercato** che servono. **Non è una prova**: non entra nel conto delle prove, e qualunque
cosa mostri **la prova 36 resta bocciata** (regole e costi erano fissati prima, `P036_dirigenti_subito.md`). Serve a sapere se lo
scarto misurato fuori seduta (mediana 103,6 punti base, media 344,6: `P036_risultati.md`) è il costo vero o un difetto della misura
(idea I38 di `REGISTRO.md`).

## I due dubbi

1. **Contato due volte?** La prova 36 entra all'apertura della barra al minuto (il prezzo di un'operazione vera) e aggiunge metà dello
   scarto. Se fuori seduta quell'apertura è di solito già al prezzo di chi vende, metà dello scarto è contata due volte.
2. **Le quotazioni sono il prezzo vero?** Fuori seduta poche borse quotano, e la migliore quotazione può essere molto più larga dei
   prezzi a cui si scambia davvero.

## Il campione

Le operazioni della prova 36 (stesse regole, stessi dati già scaricati): **400 a caso fra quelle fuori seduta** (seme 3602) e, per
confronto, **200 a caso fra quelle in seduta** (seme 3601). Per ognuna, con i dati di Alpaca (tutte le borse):

* **la quotazione al momento dell'ordine**: l'ultima quotazione valida (acquisto e vendita sopra zero, non incrociate) **prima
  dell'inizio del minuto dell'ingresso**, cercata nei 30 secondi prima e, se non c'è, nei 5 minuti prima; da lì il prezzo di mezzo e
  metà dello scarto quotato;
* **dove sta l'apertura della barra**: (apertura − mezzo) / (vendita − mezzo): 1 vuol dire al prezzo di chi vende, 0 al mezzo, −1 al
  prezzo di chi compra;
* **lo scarto effettivo**: per ogni operazione di mercato nel minuto dell'ingresso, la distanza dal prezzo di mezzo della quotazione
  valida in quel momento, divisa per il mezzo; per ogni ingresso la mediana delle sue operazioni (è quanto ha pagato davvero chi ha
  scambiato in quel minuto).

## Il conto di ogni ingresso

Il guadagno **dal prezzo di mezzo** al momento dell'ordine fino all'apertura ufficiale dopo (rettificato come nella prova 36), meno
tre costi diversi, sempre più lo slittamento di 2 + 2 punti base e le commissioni Interactive Brokers su 10'000 dollari:

* **A — metà dello scarto quotato** di quell'ingresso (il costo di un ordine che compra subito al prezzo di chi vende);
* **B — lo scarto effettivo** di quell'ingresso (se nel minuto non ci sono operazioni, l'ingresso resta fuori da B e si conta);
* **C — come la prova 36** (apertura della barra più metà della mediana dello scarto), per confronto.

Si scrivono per fascia (in seduta, dopo la chiusura, prima dell'apertura) e per ora (4:00-6:59, 7:00-9:29, 16:00-16:59,
17:00-17:59, 18:00-19:59): numero, media con il t, mediana.

## Che cosa se ne fa (scritto prima)

* Se A e B fuori seduta sono vicini al costo della prova 36: il costo era vero, la porta degli acquisti dei dirigenti fuori seduta si
  chiude.
* Se A o B danno un guadagno netto sopra zero con t almeno 2 in una fascia: diventa un'idea in coda **che si può solo confermare in
  avanti**, perché è nata dopo aver visto i dati, e con ordini veri o con un conto che riempia gli ordini fuori seduta in modo
  realistico (il demo di Alpaca non lo fa); servirebbe una decisione del proprietario.
* Le quantità esposte (quante azioni ci sono al prezzo di chi vende) non si usano: non è controllato in che unità Alpaca le dà per gli
  anni vecchi.
