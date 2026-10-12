# LINKUSDT — consegna della campagna (Passo 3, protocollo 4.5)

**Esito: nessuna strategia valida trovata per questa moneta.**

Nessuna delle 30 varianti testate in costruzione ha battuto nettamente sia la baseline (a) sia la
(b) con R medio dopo i costi positivo. Non ci sono candidati: la validazione non è stata eseguita e il
periodo di validazione (2022-10-19 → 2023-12-31) è intatto. Niente va al vault per LINKUSDT.

## Dati e periodi

* Costruzione 2020-01-01 → 2022-10-18 (dati dal 2020-01-17), validazione 2022-10-19 → 2023-12-31
  (`periodi_campagna`, voce N003 del log).
* Last e mark allineati con `carica_serie_allineate`; giornate senza mark tolte e dichiarate in
  `fase0_dati.md`; un solo mese sotto la liquidità minima (2020-01), escluso dai segnali.
* Costi: commissione 0,05% per lato, slippage 0,02% per lato, funding storico a 8 ore; rischio 1% per
  trade, leva massima 2, margine isolated.
* Controllo positivo degli strumenti superato prima della prima variante (N007-N008): un lookahead
  dichiarato batte il caso con t 58,9 e crolla a 4,4 col ritardo di una barra.

## Riepilogo delle idee provate (costruzione)

`t (b)` e `t (a)` sono i `t` di `contro_baseline`; la soglia è circa 2,0 per tutte. R medio dopo i costi.

| Variante | Idea (fonte) | TF | Dir. | Trade | R medio | t (a) | t (b) |
|---|---|---|---|---|---|---|---|
| V01 | momentum a una settimana (Liu e Tsyvinski 2018) | 1d | long | 90 | +0,079 | +0,10 | +0,46 |
| V02 | idem | 1d | short | 84 | −0,058 | +0,32 | +0,02 |
| V03 | rottura del massimo a 50 barre (Brock e altri 1992) | 4h | long | 95 | −0,079 | −0,71 | −0,72 |
| V04 | rottura del minimo a 50 barre | 4h | short | 66 | scarto | | |
| V05 | inversione dopo un'ora estrema (Nagel 2012) | 1h | long | 178 | −0,192 | −2,43 | −2,59 |
| V06 | idem | 1h | short | 181 | −0,210 | −2,85 | −3,13 |
| V07 | prima mezz'ora prevede l'ultima (Shen e altri 2022) | 30m | long | 485 | −0,078 | −1,05 | −1,09 |
| V08 | idem | 30m | short | 495 | −0,045 | +0,78 | +0,71 |
| V09 | lunedì (Caporale e Plastun 2019) | 1d | long | 139 | −0,036 | −1,14 | −1,28 |
| V10 | funding estremo alto (Schmeling e altri 2023) | 8h | short | 103 | −0,124 | −1,73 | −1,64 |
| V11 | funding estremo basso | 8h | long | 105 | −0,022 | −0,49 | −0,41 |
| V12 | premio dei volumi alti (Gervais e altri 2001) | 1d | long | 31 | scarto | | |
| V13 | squilibrio di acquisti aggressivi (Chordia e Subrahmanyam 2004) | 1h | long | 990 | −0,046 | −0,16 | −0,24 |
| V14 | squilibrio di vendite aggressive | 1h | short | 949 | −0,045 | +0,14 | +0,13 |
| V15 | rottura di volatilità dall'apertura (Williams 1999) | 1h | long | 327 | +0,044 | +1,16 | +0,86 |
| V16 | idem | 1h | short | 309 | +0,074 | +1,81 | +1,62 |
| V17 | ritracciamento con RSI a 2 (Connors e Alvarez 2008) | 1d | long | 13 | scarto | | |
| V18 | idem | 4h | long | 143 | −0,007 | +0,30 | −0,04 |
| V19 | numero tondo al rialzo (Osler 2003) | 1h | long | 554 | −0,027 | +0,52 | +0,57 |
| V20 | numero tondo al ribasso | 1h | short | 547 | −0,047 | +0,05 | −0,05 |
| V21 | nuovo massimo dell'anno (George e Hwang 2004) | 1d | long | 4 | scarto | | |
| V22 | momentum giornaliero (Zaremba e altri 2021) | 1d | long | 352 | −0,039 | −1,85 | −2,30 |
| V23 | idem | 1d | short | 322 | −0,058 | −1,47 | −1,98 |
| V24 | inversione giornaliera (Kozlowski e altri 2021) | 1d | long | 324 | +0,042 | +1,71 | +2,23 |
| V25 | idem | 1d | short | 353 | +0,007 | +1,24 | +1,73 |
| V26 | continuazione dopo un'ora anomala fino a fine giorno (Caporale e Plastun 2019; Saef e altri 2021) | 1h | long | 159 | +0,040 | +0,79 | +0,62 |
| V27 | idem | 1h | short | 137 | −0,010 | +0,51 | +0,31 |
| V28 | periodicità oraria (Heston e altri 2010) | 1h | long | 7.547 | −0,035 | +1,19 | +1,65 |
| V29 | idem | 1h | short | 7.120 | −0,038 | +1,03 | +1,39 |
| V30 | stretta delle bande (Bollinger 2001) | 1h | long | 83 | +0,037 | +0,58 | +0,61 |
| V31 | idem | 1h | short | 93 | +0,042 | +0,87 | +0,71 |
| R01 | ritocco di V24: uscita dopo 2 barre | 1d | long | 254 | +0,043 | +0,14 | +1,18 |
| R02 | ritocco di V24: stop a 1 ATR | 1d | long | 346 | +0,069 | +1,72 | +2,08 |
| R03 | ritocco di V24: target a 1 ATR | 1d | long | 325 | +0,033 | +1,69 | +1,99 |

R medio per anno, R medio senza i 3 trade migliori, buy and hold per anno (long e short), percentile
fra le simulazioni casuali, blocco del bootstrap e dettagli delle baseline sono nelle voci `risultato`
del log.

## Cosa si è capito (osservato in costruzione, non validato)

* **Dopo un'ora estrema LINK continua, non torna indietro** (osservato): sia il long dopo un'ora a −3
  deviazioni sia lo short dopo +3 perdono contro il caso in tutti e tre gli anni (t −2,59 e −3,13).
  La continuazione presa direttamente (V26, V27, fino a fine giorno) però non batte il caso (t +0,62
  e +0,31): il segnale contrario non è diventato un vantaggio.
* **Il giorno dopo un ribasso LINK tende a rimbalzare** (osservato): V24 batte la (b) (t 2,23) ma non la
  (a) (t 1,71); nessuno dei tre ritocchi batte la (a). Il rimbalzo vive nei giorni in cui scende tutto il
  mercato (con BTC in discesa nello stesso giorno R medio da +0,06 a +0,09; con BTC in salita −0,05:
  N013), e la stessa regola su BTC è più debole (t 0,86: N016). Inferito: è in buona parte l'inversione
  giornaliera del mercato, più ampia su LINK.
* **Il funding alto non è un segnale di vendita** in costruzione (V10, t −1,64): nel 2021 accompagnava
  il rialzo (R medio dello short −0,22).
* **Sulle ore e mezz'ore (V07, V08, V13, V14, V28, V29) i costi pesano quanto il movimento**: R medi fra
  −0,03 e −0,08, vicini al costo del giro (0,04-0,06 R).

## Rischi noti e limiti

* I-14 e I-15 sono state scelte dopo aver visto i fallimenti di I-13 e I-03 (dichiarato in `ipotesi.md`
  e nel log, N011): la vicinanza di V24 alla soglia è la parte più probabilmente fortunata dei risultati.
* Le varianti a 4h, 8h e 1d hanno stop in ATR oltre il 6% che il bot rifiuta: non sarebbero eseguibili
  dal bot così come sono (nessuna è candidato, quindi non conta per il paper).
* Il periodo di costruzione è dominato da un forte rialzo (2020-2021) e da un ribasso (2022): tre anni,
  con anni a pochi trade per le varianti lente.
* Potenza bassa (sezione 11): un vantaggio vero ma piccolo (R medio 0,03-0,05) con 300 trade resta
  sotto la soglia; la famiglia V24 è un esempio di questo limite o di rumore, e il protocollo non lo
  distingue senza validazione.

## Budget e asticella

* Varianti testate: **30 su 30** (27 da idee nuove, 3 ritocchi), più 4 scarti sotto i 70 trade che non
  consumano budget. 17 idee, 27 famiglie testate (i 3 ritocchi stanno nella
  famiglia di V24, che ne ha quindi 3 su un massimo di 5). Le idee con fonte sono state dichiarate
  esaurite prima dei ritocchi (N014); i ritocchi hanno seguito l'ordine della regola 6 (V24 prima ogni
  volta, `codice/ordine.py`).
* Candidati: 0. Asticella (Benjamini-Hochberg al 10%): non applicabile, m = 0. Nessun p-value di
  validazione. Esito provvisorio, da confermare dal coordinamento al Passo 4: nessun candidato.
* Criterio del vault, trade attesi in paper, eseguibilità nel bot, previsione per vault e
  trasferimento: non applicabili (nessun candidato).

## Misure di processo

Dal log (`codice/misure.py`), con le date prese dall'orologio della macchina.

* Durata dalla prima all'ultima voce del log: dalle 14:29:42 alle 15:07 UTC circa del 9 ottobre 2026
  (37,5 minuti alla voce N016; nessuna pausa: la sessione non ha aspettato risposte). Lo scarico dei
  dati (oltre 10 minuti per BTCUSDT) è dentro questo intervallo.
* Minuti dalla registrazione della prima variante all'ultimo risultato, per idea: I-01 0,1; I-02 0,1;
  I-03 0,7; I-04 1,3; I-05 0,0; I-06 0,1; I-07 0,0 (solo scarto); I-08 0,9; I-09 0,6; I-10 0,1; I-11
  0,7; I-12 0,0 (solo scarto); I-13 0,1; I-14 5,2 (con i 3 ritocchi); I-15 0,7; I-16 1,9; I-17 0,6.
  Sono i tempi di calcolo: la scrittura delle ipotesi viene prima e non è misurata dal log.
* Spiegazioni concorrenti scritte in `ipotesi.md`: 10 per ognuna delle 17 idee (le sei «noiose» con
  forma generale nella sezione comune e la previsione declinata per idea).
* Varianti diventate candidati in Fase 2: 0 da idee nuove, 0 da ritocchi.
* Varianti che hanno battuto nettamente la (a) e la (b) con R medio dopo i costi non positivo: 0.
  Varianti nette solo contro la (b): 2 (V24 e R02, entrambe con R medio positivo ma non nette contro
  la (a)).
* Previsioni: 21 corrette, 9 sbagliate (sbagliate soprattutto per eccesso di prudenza sul segno: V05,
  V06, V22, V23 sono andate peggio del previsto).
* Rifiuti del guardiano: 5, tutti per la forma dei comandi o dei siti (N002, N004, N005, N010, N012),
  nessuno aggirato.
