# Programma 7 — cinquantacinquesima prova: le monete «inelastiche» (corsa più crollo), a settimana (EMI e EWIL)

Scritto il 28 ottobre 2026 alle 04:21 UTC (ora dell'orologio), **prima di qualunque calcolo**. È l'idea 86 della coda, dalla ricerca
nella letteratura del 28 ottobre. La regola è quella dell'articolo, letto nelle pagine 1-17: Li, Liao, Yang e Zhang, «Predictive Crypto
Crashes and Asset Pricing Implications: An Inelastic Market Perspective», bozza del maggio 2026 (ABFER 2026). È una prova a settimana.

## 1. Perché

* **Quando i soldi si muovono lentamente, un colpo fa salti grandi.** Se in una moneta ci sono pochi partecipanti, o lenti, ogni colpo
  la fa salire o scendere molto e poi tornare indietro.
* **Le oscillazioni grandi peggiorano le cose.** La distanza fra chi compra e chi vende si allarga, e una parte dei partecipanti se ne
  va: la moneta continua a scendere nelle settimane dopo.
* **Cosa dice l'articolo**:
  * 4.284 monete dal 2014 al maggio 2024;
  * long il quinto più «elastico», short il più «inelastico» (EMI): **+2,5% a settimana** fuori campione, pesi secondo la
    capitalizzazione, senza costi;
  * long le vincenti elastiche, short le perdenti inelastiche (EWIL): **+3,4% a settimana**.
* **I dubbi scritti prima**:
  * l'articolo non è pubblicato e non è replicato, e non conta i costi;
  * l'effetto potrebbe stare nelle monete piccole, mentre qui ci sono le 100 più scambiate;
  * si sovrappone in parte a MAX (prova 66), alla volatilità e al momento (prova 49), che da noi non reggevano;
  * la ricerca ha già mostrato effetti spariti dopo la pubblicazione (prova 116).

## 2. La misura (come l'articolo, pagine 12-13)

* **Alla fine di ogni settimana** (domenica, giorno l − 1 prima del lunedì l), sulle chiusure giornaliere delle 12 settimane prima (84
  giorni):
  * il minimo P_min con il suo giorno (l'ultimo giorno se ripetuto) e il massimo P_max con il suo giorno;
  * **la salita**: (P / P_min − 1) × 365 / giorni passati dal minimo;
  * **il crollo**: (P / P_max − 1) × 365 / giorni passati dal massimo;
  * P è la chiusura della domenica. Se il minimo o il massimo è proprio la domenica, quella misura vale 0.
* **Il rango d'inelasticità** (InRank):
  * il rango della salita, in grandezza, fra le monete della settimana, diviso per il numero delle monete;
  * il rango del crollo, in grandezza (in valore assoluto), nello stesso modo;
  * la media dei due ranghi, riportata a un rango fra 0 e 1.
* **Universo**: le monete delle 100 più scambiate della settimana (l'universo U del programma 6) con tutte le 84 chiusure.

## 3. Le due regole (due varianti, entrambe dall'articolo)

* **EMI**: long il quinto con l'InRank più basso (elastiche), short il quinto con il più alto (inelastiche).
* **EWIL**: si divide per il rendimento delle 2 settimane prima (dai giorni l − 14 a l − 1) e per l'InRank, al 30%, 40% e 30%. Long le
  monete nel 30% migliore del rendimento e nel 30% più basso dell'InRank; short quelle nel 30% peggiore del rendimento e nel 30% più alto
  dell'InRank. Almeno 2 monete per lato, altrimenti quella settimana niente.
* **Pesi**: l'articolo pesa secondo la capitalizzazione, che nel pannello non c'è. Qui si pesa come F5, con l'inverso della volatilità
  dei 30 giorni e i lati uguali in dollari. Le posizioni si rifanno ogni lunedì da capo, senza banda, come nell'articolo.
* **Costi e funding**: a mercato, come F5 (`terza.conto`).
* **Periodo**: dal 4 gennaio 2021 (`sesta.INIZIO`) all'ultima settimana intera. Per capire si riporta a parte il periodo dopo il
  maggio 2024, fuori dal campione dell'articolo.
* **Due varianti**: nel conto delle prove diventano **213**.

## 4. L'esame

* **Come F5** (`terza.esame`, `terza.esito`): lo Sharpe corretto con l'aggiunta sopra 0,95, e il t contro 3. Vale anche la regola del
  proprietario del 24 ottobre (corretto da 0,90 in su, ogni anno positivo, t sopra 3).
* **Se una variante regge**, passa da un revisore separato.
* **Per capire, senza decidere niente**: il verso opposto; la correlazione con F5; il periodo dal giugno 2024; quante monete per lato.
