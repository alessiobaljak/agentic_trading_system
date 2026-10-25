# Programma 7 — quarantaduesima prova: cavalcare la fiammata invece di venderla (G26)

Scritto il 25 ottobre 2026, alle 09:04 UTC, **prima di scaricare le candele del 2021-2022 e prima di qualunque calcolo su quel
periodo**. Idea 74 della coda di `research/REGISTRO.md`, dal proprietario (25 ottobre): guardando le schermate del trader n. 2 ha notato
che apre più posizioni brevi sulla stessa moneta nello stesso giorno, «come per dire so che sale e continuo a sfruttare questo trend».

## 1. Perché, e cosa sappiamo già

Il controllo sui dati del trader (`research/trader_copiati/trader2_posizioni.csv`, descrittivo): metà delle sue 178 posizioni sono
ripetute sulla stessa moneta nello stesso giorno (36 coppie moneta-giorno, 32 sempre dallo stesso lato) e fanno 9.089 dei suoi 12.818
dollari. Ma **non segue la salita: la vende a ogni ondata**. Nel 96% dei casi la posizione successiva entra a un prezzo più alto della
prima (mediana +16,6% contro di lui); su IRYS il 23 ottobre vende sei volte da 0,041 a 0,198 mentre la moneta va fino a 0,50. Vendere
ogni ondata è la prova 75 (che ammetteva già le ripetizioni: 3.494 operazioni in 1.480 coppie moneta-giorno): con la protezione perde
(−0,88% a operazione), senza è fragile (prova 76 sul 2023-2024: +0,30%, p 0,36).

La lettura del proprietario è l'opposto: **se la moneta sta salendo forte, comprarla e restare finché la salita continua**, rientrando a
ogni nuovo slancio. Il perché: le monete che esplodono attirano altri compratori a ondate (l'attenzione si autoalimenta), e nelle fiammate
che non rientrano (il 15% nella prova 75, quelle che arrivano a +30% oltre l'entrata) il guadagno è grande. **Il dubbio scritto prima**:
nella prova 75 l'84% delle fiammate scende del 5% prima di salire del 30%, quindi chi compra perde spesso; l'aritmetica della prova 75
(lo specchio delle sue uscite) dà un risultato vicino a zero; il guadagno deve venire tutto dalle poche corse lunghe, e le prove 77-78
sulle fiammate e sui crolli in giornata hanno perso. Probabilità bassa.

## 2. La regola (valori fissati qui)

* **Periodo della decisione: 1° gennaio 2021 – 31 dicembre 2022**, mai usato per le fiammate (la prova 75 usa il 2025-2026, la 76 il
  2023-2024, il trader l'estate-autunno 2026).
* **Universo, giorni candidati, candele a 1 minuto e segnale identici alla prova 75** (`diciottesima.candidati` e `segnali`, le 30
  monete più grandi del periodo tolte): chiusura del minuto almeno 1,5 volte l'apertura di 24 ore prima, almeno 1,04 volte quella di 14
  minuti prima, volume dei 15 minuti almeno 5 volte la mediana delle 24 ore prima.
* **Entrata: long** all'apertura del minuto dopo il segnale.
* **Uscita: stop che segue il prezzo al 10% sotto il massimo raggiunto dall'entrata** (all'inizio −10% dall'entrata; si alza con ogni
  nuovo massimo dei minuti, non si abbassa mai); uscita al livello meno l'1% di scarto, quando il minimo del minuto lo tocca; **al massimo
  24 ore**, poi all'apertura del minuto. Il 10% è il doppio della ritirata tipica di un'ondata (il trader esce a −5%): fissato qui, non
  cercato.
* **Ripetizioni come il trader**: una posizione per moneta, rientro con un segnale nuovo almeno 15 minuti dopo l'uscita.
* **Costi**: a mercato in entrata e in uscita (`seconda.costi_moneta`); funding del giorno diviso per le ore tenute (il long paga se è
  positivo).
* **Controllo**: le stesse uscite con le entrate a minuti presi a caso negli stessi giorni-moneta (come la prova 75).
* **Descrittivo, non decide**: la stessa regola sul 2023-2024 e sul gennaio 2025 – giugno 2026 (periodi già usati per le fiammate); per
  ordine nel giorno (la prima entrata contro le successive); quante operazioni oltre +50% e quanto pesano.
* Una prova a eventi: nel conto **174**, le prove a eventi **30**.

## 3. L'esame

Come la prova 75 (`trentesima.esame`, bootstrap sulle settimane): media per operazione sopra zero con **p ≤ 0,01**, positiva nelle due
metà e **senza le 5 migliori** (decisivo: una regola che vive di poche corse lunghe deve reggere anche senza di loro); contando le 30
prove a eventi la soglia è 0,00033. Si riportano anche il conto con l'1% a operazione e la discesa peggiore.
