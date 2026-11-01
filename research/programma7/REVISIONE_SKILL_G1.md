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

*(in corso: si aggiunge qui quando arriva)*
