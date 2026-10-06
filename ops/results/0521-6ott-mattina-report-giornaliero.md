# 0521-6ott-mattina-report-giornaliero.req

_eseguito: 2026-10-06 06:22 UTC_

**richiesta:** `report-giornaliero`
**eseguito:** `.venv/bin/python -m scripts.report_giornaliero --pubblica`
**esito:** codice 0 in 3.3s

```
[report] backlog: 29 voci in 7 gruppi, aspettano il si' 1 (commit ecc5247)
[firebase] connesso (Firestore + RTDB)
[report] backlog pubblicato: si
[report] report del 2026-10-05 pubblicato: si
REPORT GIORNALIERO del 2026-10-05 (versione ecc5247)

== In breve
  - Paper ieri: 23 trade, -6.52 USDT (-0.135R a trade). Ultimi 7 giorni -7.89 USDT (-0.106R); dal 27 set -0.037R netti a trade su 155.
  - Gate: Un giro e' in corso dalle 06/10 06:46; il precedente era finito alle 06/10 06:32: 43147 valutazioni, 429 passate, durato 3h28.
  - Aspettano il tuo sì: 1.
  - Capito: Il numero guida è tornato a −0,03R su 182 segnali, margine ±0,17 (ops 0498; ieri +0,006 su 156): la lettura stampata dice già «la promessa non regge dopo la validazione: la prossima modifica va nel gate». Il verdetto resta al 7 ott, ma in tre giorni il numero ha oscillato fra −0,03 e +0,006 senza mai uscire dal margine: è un sistema a zero, non un sistema in calo.

== Il paper ieri
  - Ieri (2026-10-05): 23 trade delle validate, 13 vinti, -6.52 USDT, -0.135R netti a trade. Sul conto (esplorativi e chiusure esterne compresi): 24 trade, -6.38 USDT.
  - Equity 923.36 USDT (-7.66% dall'inizio del paper, il 2026-09-16).
  - Adesso 2 posizioni aperte, rischio aperto 0.27% del capitale, uPnL +1.74 USDT.
  - Ultimi 7 giorni sul conto: 2 in utile, 5 in perdita.
  - Confronto: BTC comprato il primo giorno +13.1%, noi -7.7%.
    periodo | trade | vinti | PnL USDT | R netto | R lordo | costi R
    ieri | 23 | 57% | -6.52 | -0.135R | -0.016R | +0.119R
    7 giorni | 134 | 57% | -7.89 | -0.106R | -0.013R | +0.094R
    dal 27 set | 155 | 61% | -0.96 | -0.037R | +0.056R | +0.092R
    tutto | 290 | 56% | -77.24 | -0.085R | +0.004R | +0.089R

== Come va il gate
  - Un giro e' in corso dalle 06/10 06:46; il precedente era finito alle 06/10 06:32: 43147 valutazioni, 429 passate, durato 3h28.
  - Validate 257 (+22 nel giro) su 82 coin, copertura 41.0%; declassate 173.
  - Ultimi 7 giorni: 65 promosse, 0 rimosse.
  - Il cervello: varianti dai referti 0 create, 0 promosse; intorno 40 madri, 3 promosse.
  - Registro: 1787 coppie su un tetto di 3000.
  - Esplorative: 36 attive, poi validate 4, scartate 405.
  - Fuori campione (le validate guadagnano anche DOPO la scelta? ultimo report del 2026-10-06): Selezione: la promessa non regge dopo la validazione: motore -0.04R (margine ±0.16R per giornata) su 202 segnali. O il gate sceglie coppie buone solo nei giorni su cui le ha provate, o il mercato e' cambiato: da qui non si separano. Per la regola la prossima modifica va nel gate. Esecuzione: non si decide: sugli stessi segnali fanno quasi uguale (differenza +0.04R, margine ±0.07R per giornata). Si rilegge il 14 ott.
  - R1, il gate rigiocato nel passato: 8 date su 26, 597 unita' fatte.

== Cosa ci dicono i dati
  - Ipotesi nate dai referti (le prova il gate sulla storia): gen_bf2be656: scala_stretta — 3 perdite sotto il primo gradino (mfe mediana 0.42 R) (campione 3); gen_bf2be656: solo_short — long 3/3 persi (campione 3); gen_fa304106: conferma_trend — 4 perdite mai andate a favore (classe ingresso) e 0 vinti su 9 (campione 4); gen_fa304106: controtrend_btc — 3/3 persi contro il contesto BTC (campione 3); gen_fa304106: solo_long — short 5/5 persi (campione 5)
  - Trailing in tutto: 74 prematuri e 66 protetti su 155 verdetti; proposta del paper: nessuna.
     | ieri | 7 giorni | tutto
    INGRESSI |  |  | 
    perdite «mai andate a favore» | 5/10 | 29/57 | 52/103
    latenza segnale → ingresso (s, mediana) | 178 | 163 | 159
    ingresso rispetto al segnale (mediana) | +0.012R | +0.027R | +0.027R
    USCITE E TRAILING |  |  | 
    perdite morte sotto il primo gradino | 5/10 | 28/57 | 51/103
    trailing prematuri / verdetti | 8/12 | 38/72 | 73/154
    trailing protetti / verdetti | 3/12 | 26/72 | 66/154
    arrivati al primo target | 2/23 | 11/134 | 31/290
    massimo a favore (mediana, R) | 0.88 | 0.83 | 0.85
    STOP LOSS |  |  | 
    chiusi a stop | 10/23 | 55/134 | 126/290
    stop seguiti da un rimbalzo (rumore) | 0/9 | 11/54 | 30/125
    massimo contro (mediana, R) | 0.41 | 0.76 | 0.70
    RISCHIO |  |  | 
    rischio effettivo per trade (mediana) | 0.15% | 0.13% | 0.14%
    leva media | 1.48x | 1.31x | 1.35x
    DIREZIONE |  |  | 
    long: trade e R netto | 6 a -0.033R | 71 a -0.111R | 131 a -0.141R
    short: trade e R netto | 17 a -0.171R | 63 a -0.102R | 159 a -0.038R

== Le funzioni servono?
  - Regola (scritta prima dei numeri): sotto 10 trade per gruppo «campione piccolo»; oltre 2 errori standard nel verso atteso «contribuisce», nel verso opposto «va contro»; altrimenti «non si vede ancora». USDT: quanto ha risparmiato (o tolto) la riduzione di size rispetto alla size piena.
  - Origine delle strategie nel paper: ai 1 trade a +0.094R · casuali 256 trade a -0.087R · intorno 3 trade a -0.669R
    funzione | toccati | altri | differenza | verdetto | USDT
    freno globale da deriva | 211 a -0.074R | 49 a -0.173R | +0.099 ±0.270 | non si vede ancora | +14.28
    panchina dei pesi | 2 a -0.304R | 258 a -0.091R | — | campione piccolo | -0.07
    pesi alti (size e leva in su) | 55 a -0.150R | 22 a -0.070R | -0.080 ±0.517 | non si vede ancora | 
    leva sopra 1x | 64 a -0.112R | 196 a -0.086R | -0.026 ±0.261 | non si vede ancora | 
    tilt di trend e sentiment | 58 a -0.080R | 153 a -0.072R | -0.008 ±0.277 | non si vede ancora | +0.79
    declassate a un quarto | 115 a -0.114R | 145 a -0.076R | -0.038 ±0.222 | non si vede ancora | +24.73
    paper esplorativo | 12 a +0.247R | 260 a -0.093R | +0.340 ±0.436 | non si vede ancora | 

== Cosa abbiamo capito
  - Note del 2026-10-05:
  - Il numero guida è tornato a −0,03R su 182 segnali, margine ±0,17 (ops 0498; ieri +0,006 su 156): la lettura stampata dice già «la promessa non regge dopo la validazione: la prossima modifica va nel gate». Il verdetto resta al 7 ott, ma in tre giorni il numero ha oscillato fra −0,03 e +0,006 senza mai uscire dal margine: è un sistema a zero, non un sistema in calo.
  - Il gate rigiocato nel passato, su 8 date complete (ops 0502): 6 promosse su 25.631 giudizi, e i loro 45 trade fanno −0,22R contro −0,14R delle bocciate (differenza −0,08 ±0,31, non decide: ne servono 80). Primo indizio diretto che la scelta del gate non è migliore del mucchio; con R2 (0 su 3.600) chiude il quadro: le validate nascono dalla ricerca ripetuta, non da candidate buone.
  - La colonna 0,8/1,6/2,4 chiesta ieri: nel modello semplificato è la scala che perde meno, −0,20R a trade su 291 contro −0,37 (1/1,5/2,5) e −0,86 (2/4/6) (ops 0495). Conferma che il primo incasso è lontano, ma non cambia il segno: anche la scala migliore resta sotto zero in quel modello.
  - Il paper esplorativo non «contribuisce» più: 11 trade a +0,242R contro −0,089R, differenza +0,331 ±0,475 → non si vede ancora (ops 0489; ieri «contribuisce» su 10). Era il limite del campione minimo, come scritto ieri.
  - La prova sul prezzo casuale del 4 ott ha scritto 144 unità in errore, tutte «'cfg'» (ops 0502): conferma la causa dedotta ieri (stato dei worker in un altro modulo), corretta. Gira oggi alle 13:10.
  - Il giro completo della notte è durato 3 h 22 (ops 0492) con 42.274 valutazioni e 421 passate: l'intorno delle quasi-promosse ha generato 213 figlie (riga ORIGINI). È il meccanismo della ricerca ripetuta che gonfia il conto delle prove.
  - La prova sul prezzo casuale, a 1 ora (ops 0506): le stesse 100 strategie nuove sulle 72 monete, giudicate dal gate di oggi, passano 8 volte su 7.200 sulle candele vere e 16 volte su 7.200 sulle stesse candele rimescolate. Per la regola scritta prima: NON SI SA (sotto le 10 passate sul vero il rapporto non si legge). Osservato: sui prezzi senza nessun vantaggio possibile il gate ha promosso il doppio che sui prezzi veri. Inferito: a 1 ora il gate non distingue il rumore dal mercato; con 8 e 16 passate la differenza può essere caso. Chiude il quadro con la prova del 4 ott (0 su 3.600 a 15 minuti) e il gate rigiocato nel passato (promosse −0,22R contro −0,14R): il filtro del gate non aggiunge valore misurabile alle candidate nuove.

== Cosa è cambiato nel sistema
  - 05/10 14:11 — Diario: il giro delle 14:00 e' tornato, il gate rigiocato nel passato e' chiuso
  - 05/10 13:58 — La prova sul prezzo casuale: 8 passate sul vero, 16 sul rimescolato, non si sa per la regola
  - 05/10 08:23 — Controllo del 5 ott: numeri, cosa abbiamo capito, proposta P0 (Passo 0 del protocollo di ricerca)

== Aspetta il tuo sì e prossime letture
  - Aspettano il tuo sì: P0. Il protocollo di ricerca per moneta: Passo 0 (preparazione e parametri) — proposta del 5 ott, aspetta il tuo sì
  - In lavorazione: G7. Il gate sul prezzo casuale: quante strategie passa per caso, a 1 ora? — FATTA il 5 ott: candele vere 8 passate su 7.200 (0,11%), rimescolate 16 su 7.200 (0,22%), rapporto 2,0 → per la regola NON SI SA (meno di 10 passate sul vero), ops 0506; R2. Taratura di R1 a parità di candidate — FATTA il 4 ott: 0 passate su 3.600 → lo 0 di R1 è vero (ops 0485); la scelta del piano è in R1b; R1. Rigiocare il gate nel passato — FERMATA dal proprietario il 4 ott (opzione c, dopo R2): il lancio del 5 ott fa solo la prova sul prezzo casuale (G7) e poi toglie il file «attivo»; il gate torna a 8 giri al giorno. La scelta del gate si legge nel fuori campione del 7 e 14 ott; J2. «Cosa aspetta il sì» in dashboard, senza aggiornarlo a mano — in lavorazione (1 ott); D8. Raccolta dei dati mancanti (punto 4 del 1 ott) — ATTIVA dal riavvio del 1 ott 17:24 («[cattura]» nel log del bot); T2. La curva del vantaggio del segnale — FATTA il 2 ott: «nessun vantaggio misurabile» (ops 0437); la sezione resta nel report mfe e si rilegge col crescere dei trade
    data | cosa si legge | regola
    2026-10-07 | Fuori campione: il problema è il gate o il bot? (report portafoglio) | regole del 7 e 14 ott, diario del 30 set
    2026-10-10 | R1, il gate rigiocato nel passato (prima lettura completa, STIMA: dal 2 ott sulle sole monete operate, ~1/3 del lavoro, 2,5 ore al giorno) | regola R1, diario del 1 ott
    2026-10-10 | Varianti dai referti e ipotesi d'ingresso (J9, I4ter) | backlog archivio
    2026-10-14 | Fuori campione, seconda lettura | regole del 7 e 14 ott
    2026-10-15 | Gruppo di controllo: servono 3 conferme? (K3) | backlog archivio K3
    2026-10-18 | Conferma a maggioranza (J11), sessione oraria (J13), passata a 1 ora (C1) | backlog archivio

== Salute e costi
  - Semafori: sistema giallo, paper giallo.
  - Anomalia FRENO_GLOBALE: freno globale da deriva: PF 0,74 vs 2,02 atteso
  - Anomalia GATE_SFORA: il giro del gate e' durato 3 h 28 (piu' di 3 h)
  - Anomalia SENZA_PROMESSA: 119 validate su 257 senza promessa (last_pf)
  - Riavvii del bot nelle 24 ore: 0.
  - Letture Firestore nelle 24 ore: 8568 (quota gratuita 50.000).
  - Spesa AI di ieri (2026-10-05): nessun dato.
```
