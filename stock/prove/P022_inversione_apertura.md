# Prova 22 — l'inversione dopo l'apertura, a 5 passi (SPY e QQQ)

Regole scritte il 25 ottobre 2026 **prima di qualsiasi calcolo** su questa idea (idea I25 di `REGISTRO.md`: la «Reversal Strategy 5
Step Entry Checklist» di Riley Coleman, schermate mandate dal proprietario; «sì, procedi con la prova 22 in autonomia»), committate
prima di lanciare il programma. Si conoscevano le prove 1-21, in particolare la 17: la direzione della prima candela finisce allo stop
circa l'80% dei giorni.

**Famiglia:** regole in giornata **contro** il movimento dell'apertura (comprare dopo una discesa che si ferma su un livello, vendere
dopo una salita che si ferma). È una famiglia diversa da quella delle prove 2 e 17, che seguono il movimento: se la prova passa la
ricerca e il revisore, il periodo chiuso (gennaio 2025 → settembre 2026) si apre **una volta** per questa famiglia e conta come una
prova. Contano come **2 prove** (SPY e QQQ), più le **4 varianti** di robustezza qui sotto: in tutto 6 nel conto.

## Perché dovrebbe funzionare

Nei primi 30-40 minuti arrivano tutti gli ordini accumulati nella notte: il prezzo spesso esagera in una direzione e poi torna indietro
quando quegli ordini finiscono. La prova 17 lo suggerisce dal lato opposto: seguire la prima candela finiva allo stop circa l'80% dei
giorni. Un livello toccato più volte nei giorni prima raccoglie ordini in attesa, che fermano la discesa. **Sospetto scritto prima:**
gli esempi dell'autore sono scelti da lui, senza nessun conteggio; i passi a occhio (livello, rottura, figura) scritti come regole
fisse possono non essere quello che fa lui; gli studi sulla testa e spalle trovano poca informazione (Lo, Mamaysky, Wang, *Journal of
Finance* 55, 2000); la gestione dello stop «con l'esperienza» non si può provare e qui è sostituita da stop e obiettivo fissi.

## Le regole (descritte per gli acquisti; le vendite allo scoperto sono lo specchio esatto: massimi al posto dei minimi)

Prezzi al minuto di Alpaca, solo la seduta (9:30-16:00 di New York), 2016-2024. Le ore sono quelle d'inizio della barra.

**Passo 1, il livello (grafico a 15 minuti).** Con le barre da 15 minuti delle **5 sedute prima** (oggi escluso): un *minimo di
oscillazione* è una barra con il minimo più basso delle 2 barre prima (strettamente) e non più alto delle 2 barre dopo. Una **zona di
supporto** è una coppia di minimi di oscillazione distanti almeno 4 barre (un'ora) e con prezzi diversi al massimo dello 0,1%: la zona
va dal più basso al più alto dei due. Le linee di tendenza oblique **non** si usano (non c'è un modo unico di tracciarle).

**Passo 2, la discesa si rompe (grafico a 1 minuto).** I minimi e massimi di oscillazione a 1 minuto si definiscono come sopra, con 2
barre per lato (un minimo si conosce solo 2 barre dopo). Servono, in quest'ordine:
* la **testa** T: un minimo di oscillazione che è anche il minimo più basso della seduta fino a lì;
* la **spalla sinistra** S1: l'ultimo minimo di oscillazione prima di T, più alto di T, al massimo 30 minuti prima di T;
* il **massimo più basso** H: il massimo più alto delle barre fra S1 e T (escluse);
* la **rottura**: la prima barra dopo T che chiude sopra H, senza che nel frattempo il prezzo sia sceso sotto T.

**Il prezzo arriva sul livello.** Il minimo di T è dentro una zona di supporto o poco sotto: fra il fondo della zona meno lo 0,15% e la
cima della zona. Prima di T, oggi, almeno una chiusura a 1 minuto sopra la cima di quella zona (il prezzo ci è arrivato dall'alto).

**Passo 3, l'orario.** La barra di T comincia fra le **9:40 e le 10:10** (le inversioni «intorno alle 9:45 e alle 10:00»).

**Passo 4, la testa e spalle.** La **spalla destra** S2: un minimo di oscillazione dopo la barra della rottura, più alto di T. Se ce
n'è più d'uno, vale il più recente già conosciuto.

**Passo 5, l'ingresso.** Alla chiusura di una barra che (a) viene almeno 2 barre dopo S2 (quando S2 è conosciuta), (b) chiude sopra
la sua apertura e sopra il massimo della barra prima (la candela forte di conferma), (c) comincia entro le **10:59**, e senza che dopo
T il prezzo sia sceso sotto T: si compra a mercato all'apertura della barra dopo, con il 98% del conto, azioni intere, **senza leva**
(l'autore usa i future, con la leva: qui conta lo Sharpe, che la leva non cambia, a parte i costi).
* **Stop:** 1 centesimo sotto S2, al tocco, valido già nella barra dell'ingresso.
* **Obiettivo** («l'altro capo dell'intervallo»): il massimo più alto della seduta dall'apertura fino a T, a ordine limite (solo se il
  prezzo passa oltre). Se alla chiusura della barra di conferma il prezzo è già sopra l'obiettivo, non si entra.
* **Fine giornata:** se né lo stop né l'obiettivo sono stati toccati, si esce a mercato all'apertura dell'ultima barra della seduta.
* **Una sola operazione al giorno:** il primo segnale valido, acquisto o vendita.

**Giorni esclusi, costi:** come la prova 17 (chiusure anticipate, giorni con minuti mancanti; metà della mediana dello scarto
misurato, 0,5 punti base di slittamento, Interactive Brokers «fisso», costi doppi, capitale 100'000 dollari).

## Le prove di robustezza (solo da leggere, non per scegliere; contano nel registro)

Per ogni titolo: (a) **senza il passo 1** (nessuna zona: solo testa e spalle in orario), per sapere se il livello aggiunge qualcosa;
(b) **orario largo** (testa fra le 9:35 e le 11:30, ingresso entro le 11:59), per sapere se l'orario conta. E, dalle stesse operazioni
della regola principale, il risultato dei soli acquisti e delle sole vendite e anno per anno.

## L'esame

Per ogni titolo: (1) Sharpe annuo con i costi più alto del tenere lo SPY e del tenere lo stesso titolo; (2) Sharpe corretto ≥ 0,95 con
tutte le serie del conto; (3) Sharpe sopra zero con i costi doppi; (4) almeno il 60% dei 32 trimestri in guadagno (un trimestre senza
operazioni non conta come guadagno). Accanto, da leggere: numero di operazioni, guadagno medio a operazione e il suo t. Se passa:
revisore separato, poi il periodo chiuso una volta. Se non passa: bocciata nel registro.
