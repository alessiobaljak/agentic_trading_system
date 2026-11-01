# Revisione di G1 con le skill (1° novembre 2026)

Richiesta del proprietario del 1° novembre («lanciale subito»): le skill di revisione su G1, la candidata per i soldi veri, prima di
qualunque passo. Codice delle serie e del rapporto sul rischio: `revisione_skill.py`; uscite in `revisione_skill/`.

## 1. Revisione del backtest (skill `backtest-review`)

| Controllo | Esito | Cosa si è visto |
|---|---|---|
| Dati dal futuro | **PASSA** | Il funding dei 7 giorni usa i giorni di tenuta da g − 7 a g − 1 (`sesta.funding_7`; il regolamento delle 00:00 di g è noto alle 00:09, quando il bot decide); la volatilità usa le chiusure fino a g − 1 (`ottava.sigma_30`); l'universo usa i volumi fino al giorno prima del lunedì (`terza.pannello_settimane`); si entra all'apertura di g. |
| Sopravvissuti | **PASSA** | 892 contratti, anche quelli tolti dal listino (LUNA contata a −99,99%, `programma6/CONTROLLO_PARITA.md`); l'universo di ogni settimana è quello di allora. |
| Adattamento al passato | **NON CHIARO** | Pochi numeri scelti (7 giorni, banda 20/40, volatilità dei 30 giorni, 100 monete), ma la famiglia è nata e si è misurata sugli stessi anni 2021-2026; l'unico controllo su monete mai usate (le 101-200) dà Sharpe 0,75 (prova 137), molto sotto 1,98; l'unico periodo davvero nuovo sono gli 8-9 giorni di paper e demo. |
| Costi | **PASSA** | Commissione a mercato 0,05% più lo scarto di ogni moneta, 0,02% quando l'ordine limite si riempie, funding vero sulle due gambe; tutto a mercato lo Sharpe resta 1,86 (`RISULTATI_PRIMA.md`). Non c'è l'impatto sul prezzo di somme grandi. |
| Dipendenza da un periodo | **PASSA, con una riserva** | Ogni anno positivo (2023 il più debole, +7,6% in `RISULTATI_PRIMA.md`); positivo sia con il Bitcoin in salita sia in discesa (sotto, punto 2); ma la discesa più lunga è durata **354 giorni** sotto il massimo. |
| Dimensione e rischio | **NON CHIARO** | Un lato da 1 per parte (esposizione 2), pesi secondo l'inverso della volatilità; discesa −30,1%; una moneta sola può pesare molto (Tron oggi 9,9% in G1, 30,8% in F5) e il tetto per moneta è già stato provato e bocciato (prova 61). |
| Esecuzione | **PASSA** | Si decide alla chiusura e si entra all'apertura dopo; l'ordine limite conta come eseguito solo se nella prima ora il prezzo passa oltre il limite (allora è riempito per forza), altrimenti si paga il mercato più lo spostamento dell'ora. Il demo lo conferma: 291 ordini limite eseguiti su 301 (`ops/results/0685-1nov-stato.md`). |

**Verdetto: DA SISTEMARE, non da buttare.** Nel codice del backtest non si è trovato nessun errore. I punti aperti non sono
errori, sono limiti: non c'è un periodo davvero nuovo, sulle monete mai usate rende molto meno, e una moneta sola può pesare
troppo. La sistemazione proposta: soldi veri, se il proprietario li chiede, con una somma piccola all'inizio; il confronto ogni
settimana fra il demo e quello che il passato fa aspettare; una regola scritta prima per fermarsi (per esempio una discesa del conto
vero oltre il 30%, la peggiore del passato).

## 2. La separazione del guadagno (skill `residual-edge-analyzer`)

Serie di confronto scelte prima di guardare il risultato (`revisione_skill.py`): il Bitcoin; le 100 monete dell'universo a pesi uguali;
il momento dei 28 giorni fra le monete; reti principali meno (meme + finanza decentralizzata). G1 prima delle spese di scambio (il
funding è dentro), giorni dal 4 gennaio 2021 al 4 ottobre 2026 (2.100 giorni).

* **Il mercato spiega quasi niente di G1**: R² 0,036 (il 3,6% della variazione), beta sul Bitcoin 0,007, sulle 100 monete −0,064.
* **Il guadagno che resta dopo il mercato è 62,4% l'anno**, t 5,14 (errori corretti per la dipendenza fra i giorni), rapporto fra
  questo guadagno e la sua volatilità 2,32; dopo le spese 55,9% l'anno.
* **I settori non lo spiegano**: aggiungendo reti principali meno meme e finanza decentralizzata l'R² passa da 0,036 a 0,037 e il
  guadagno resta 62,3%. Anche il momento non cambia niente (62,5%).
* **Nel tempo**: il guadagno dopo il mercato è positivo nell'89% delle finestre di 182 giorni; nell'ultima finestra (aprile-ottobre
  2026) è 33,8% l'anno, circa la metà della media.
* **Avviso della skill**: tutto è sullo stesso periodo su cui G1 è nato (dentro il campione): il risultato è da confermare fuori.

## 3. Il rapporto sul rischio (skill `risk-report`, G1 dopo le spese)

| Rendimento | Rischio | Rapporti | Code | Stabilità |
|---|---|---|---|---|
| +65,7% l'anno composto; mese medio +4,7%, mediano +2,6% | volatilità 27,4%; **discesa massima −30,1%**; discesa più lunga **354 giorni** | Sharpe 1,98; Sortino 3,18; Calmar 2,18 | giorno peggiore del 5% −1,96% (del 1% −3,29%); media dei giorni oltre il 5% peggiore −2,86%; **curtosi 8,7 (code grasse)**; asimmetria +0,91 | mesi positivi 67%; mesi peggiori dicembre 2023 −12,3%, luglio 2022 −11,7%, marzo 2024 −11,5%; discese oltre il 10%: 8, oltre il 20%: 2 |

Beta sul Bitcoin −0,07; correlazione con il Bitcoin sui 30 giorni fra −0,71 e +0,50, mediana −0,16. Segnalati dalla skill: la
curtosi sopra 5 (giorni estremi più frequenti di quanto dice la volatilità). Sharpe sotto 3 e asimmetria positiva: niente di sospetto.

## 4. Il controllo dei dati (skill `data-scrub`, sui dati che G1 usa)

Sulle 199.486 coppie giorno-moneta dell'universo: 174 senza apertura o chiusura (0,09%), 279 con volume zero (0,14%), 24 giorni sopra
+100% e 39 sotto −50% (crolli e salite vere, come LUNA), nessun funding mancante, 223 giorni con il funding oltre il 3% in un giorno,
28 salti oltre l'1% fra la chiusura e l'apertura dopo. Pochi e non cambiano il risultato.

## 5. La critica avversaria (skill `strategy-critique`, revisore separato)

Un revisore separato (un agente che non conosceva le conclusioni sopra) con la skill `strategy-critique`; i suoi calcoli sono nella
cartella di lavoro della sessione, non nel repository. **Il suo verdetto: oggi no ai soldi veri; sì con condizioni, solo con G1 e senza
gli eventi.** I punti, con quelli che ho ricontrollato io:

1. **Lo Sharpe corretto di G1 oggi è 0,86, sotto lo 0,90 della regola del proprietario** — *ricontrollato*: `RISULTATI_PRIMA.md`, rifatto
   il 25 ottobre con 80 gruppi di prove, dice 0,86; `REVISIONE_G1N.md` 0,860. Il registro e i messaggi al proprietario dicevano ancora
   0,94 (il valore del 23 ottobre): **errore mio**. Il calo viene dal numero delle prove che cresce, cioè proprio il caso di cui il
   proprietario ha detto il 24 ottobre «non bocciare 0,91 se ogni anno si alza la soglia»: decide lui.
2. **Il guadagno dipende da due periodi**: il 57% da 2 semestri su 12 (primo del 2021, secondo del 2024); dal 2022 lo Sharpe è 1,72, e
   senza le 10 settimane migliori 1,12 (calcolo del revisore).
3. **La parte stabile è il funding, e negli ultimi due anni viene dai casi estremi**: nel 2026 il 56% del funding incassato viene da
   monete con il funding sopra lo 0,3% al giorno (nel 2024 il 20%); il lato comprato tiene le monete che tutti vendono (l'8 novembre
   2022, FTT −75%, −3,1% del capitale). Se Binance cambia i tetti del funding, il guadagno recente cala (calcolo del revisore).
4. **Concentrazione**: TRX fino al 29,3% del lato comprato; 67 giorni con meno di 10 monete vendute (calcolo del revisore).
5. **I crolli dentro la giornata e il tipo di margine**: il 19 maggio 2021 e il 10 ottobre 2025 tutte le monete comprate hanno toccato
   −18% o peggio; con il margine isolato a leva 5 il lato comprato sarebbe stato liquidato. *Ricontrollato*: il demo imposta la leva 5
   (`bot/portafoglio/demo_binance.py`, riga 319) ma non il tipo di margine. Il backtest usa le candele giornaliere e non vede le chiusure
   forzate dentro la giornata.
6. **Gli eventi oggi peggiorano il conto** — *ricontrollato*: N3 dal 1° luglio 2025 fa **−2,30% a evento su 213** (mediana −6,97%, vinte
   44%). E4 non ha un'uscita di protezione: GAS il 25 ottobre 2023 −133% in 7 giorni (*ricontrollato* in `eventi_E4.csv`). Lo Sharpe 3,41
   degli eventi in `CONTO_UNICO.md` viene dal rendimento spalmato sui giorni; contato tutto al giorno di uscita il revisore trova 1,39.
7. **Il rischio della borsa**: tutto il capitale su Binance (il furto del 29 ottobre, backlog P26).
8. **Quanti soldi regge**: fino a circa 1 milione; con 5.000 USDT il 27% degli ordini è sotto il minimo di Binance (`REVISIONE_G1N.md`).
9. **Troppi che fanno la stessa cosa**: il funding normale incassato è fra il 13% e il 19% l'anno dal 2021 al 2026, non si vede ancora
   un calo; il rischio è che tutti escano insieme.
10. **Il bot e il backtest**: togliere l'interruttore del demo ferma gli ordini ma non chiude le posizioni; non c'è uno stop sulla
    perdita del conto; nessuno confronta ogni giorno le posizioni vere con i pesi; il bot decide alle 00:17-00:21 al prezzo del momento.

**Le sue condizioni per il sì** (solo G1): il proprietario accetta per iscritto lo 0,86; margine incrociato impostato dal codice e
controllato, esposizione non oltre il 200%; un tetto per moneta e almeno 10 monete per lato, con il costo misurato prima sul passato
(la prova 61 ha già trovato che il tetto del 10% alza la discesa: va rifatto con le monete minime per lato); un interruttore che chiude
tutto, uno stop automatico sulla perdita del conto (per esempio −20%) e il confronto ogni giorno fra posizioni e pesi; almeno 10.000
USDT ma non più di quanto si può perdere, con prelievi regolari; gli eventi solo sul demo finché N3 non torna positivo sugli eventi nuovi.

