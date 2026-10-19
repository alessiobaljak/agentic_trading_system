# Programma 6 — strategie di trading dagli indicatori tecnici, provate con le finestre che avanzano

Scritto il 19 ottobre 2026, prima di qualunque calcolo, dopo l'indicazione del proprietario:

> «comprare e tenere 12 ore non è trading [...] quello che devi fare è trovare delle strategie [...] partendo credo dagli
> indicatori tecnici [...] il passato è pubblico per tutti ed è la base sul quale tutti i backtest lavorano [...] il punto
> non è riprovare ma riprovare con metodo e non a caso [...] io non voglio aspettare dati nuovi [...] lavora con tutti i
> dati a disposizione dal passato ad oggi [...] usa limit o margin, tutte le crypto del future binance [...] se serve capire
> come prima impara, documentati».

Le prove sui dati nuovi del programma 5 continuano da sole in sottofondo, ma il programma 6 non le aspetta.

## 1. Cosa si cerca

Strategie di **trading** nel senso classico: un ingresso deciso da indicatori tecnici (medie, canali, RSI, Bande di
Bollinger, MACD, ATR, ADX, Supertrend…), un'uscita con **stop**, **obiettivo** e **stop che segue il prezzo**, long e
short, ordini a mercato o **limite**, sui perpetui USDT-M di Binance, su più monete, che guadagnano dopo i costi e lo
fanno **in modo ripetibile nel tempo**.

## 2. Il metodo: le finestre che avanzano (Pardo, 1992 e 2008)

Il passato si usa tutto, ma **mai** per giudicare una strategia sugli stessi dati con cui è stata scelta:

1. per ogni famiglia di strategie c'è una **griglia piccola** di valori, scritta prima;
2. su una finestra di costruzione di **12 mesi** si misura ogni combinazione su tutte le monete insieme, e si sceglie con
   una regola fissata prima (sezione 4);
3. la combinazione scelta si applica **così com'è** ai **3 mesi dopo**, che la scelta non ha visto;
4. si sposta tutto avanti di 3 mesi e si ripete, dal 2020 a oggi;
5. il risultato è la **somma dei soli tratti di 3 mesi «dopo»**: è quello che avrebbe guadagnato chi avesse seguito la
   famiglia con questo metodo, scegliendo ogni volta solo col passato.

Così si usa tutto il passato, con metodo, e quello che si misura è il metodo di scelta, non una regola fortunata.

## 3. Le difese contro l'auto-inganno

* **Lo Sharpe corretto per i tentativi** (Deflated Sharpe Ratio, Bailey e López de Prado 2014): il risultato dei tratti
  «dopo» deve battere il massimo atteso per caso dato il numero di famiglie e combinazioni provate.
* **La probabilità di sovra-adattamento** (PBO con la validazione combinatoria simmetrica, Bailey, Borwein, López de Prado
  e Zhu 2015): quanto spesso la combinazione migliore nella costruzione finisce nella metà peggiore fuori. Sopra il 50% la
  scelta non vale niente.
* **Stabilità**: la combinazione scelta non deve saltare a caso da una finestra all'altra; si sceglie il centro di una
  zona buona (la media dei vicini nella griglia), non il picco isolato.
* **Costi veri**: commissione 0,05% a mercato e 0,02% con ordine limite, scarto di prezzo 0,01% (BTC, ETH, SOL) e 0,02%
  (le altre), funding a ogni regolamento; ordine limite eseguito solo se il prezzo **attraversa** il livello; nella stessa
  candela, se toccati stop e obiettivo, vale lo **stop**.
* **Niente dati futuri**: gli indicatori si calcolano alla chiusura della candela e si opera dalla candela dopo.
* Tutto si registra, anche le famiglie che non vanno.

## 4. La regola di scelta in ogni finestra di costruzione

Per ogni combinazione: il netto in R (multipli del rischio iniziale) per trade su tutte le monete; vale solo con almeno
**100 trade** nella finestra e positivo su almeno il 50% delle monete con almeno 5 trade. Si sceglie la combinazione con il
**netto medio per trade dei vicini** (la combinazione e quelle a un passo nella griglia) più alto; se nessuna è positiva,
nei 3 mesi dopo la famiglia **non opera**.

## 5. La leva e la dimensione

Ogni trade rischia una frazione fissa del capitale fra ingresso e stop (1%); la leva è quella che ne viene, con un tetto di
5 volte. La leva non crea il vantaggio: moltiplica guadagni e perdite. Il risultato si riporta in R e in rendimento del
capitale con il tetto di leva. `DRY_RUN` resta vero: niente soldi veri.

## 6. Quando una strategia è valida

Per una famiglia, sui tratti «dopo» dal 2021 al 2026-10:
1. netto positivo con l'intervallo al 95% sopra zero (bootstrap a blocchi di giorni);
2. **Sharpe corretto** per tutte le combinazioni provate nel programma con probabilità ≥ 95%;
3. **PBO** sotto il 50%;
4. positiva in almeno **4 anni su 6** e nell'ultimo anno (2025-10 → 2026-10);
5. positiva a costi doppi;
6. positiva su almeno il 55% delle monete con almeno 20 trade.

Le fonti consultate (19 ottobre 2026): Pardo (via Wikipedia e il podcast Algo Advantage, n. 35); Bailey e López de Prado,
«The Deflated Sharpe Ratio» (SSRN 2460551); Bailey, Borwein, López de Prado e Zhu, «The Probability of Backtest
Overfitting» (SSRN 2326253); Gerritsen et al. 2020 sulle regole tecniche su Bitcoin (le rotture di canale danno lo Sharpe
più alto, le medie mobili no); Annals of Operations Research 2019 (fuori campione negativo su Bitcoin, positivo su altre
monete); Journal of International Financial Markets 2022 (i costi riducono molto le regole buone); Mroziewicz e
Ślepaczuk 2026 (il risultato dipende molto dalla lunghezza delle finestre: per questo la lunghezza è fissata qui prima).
