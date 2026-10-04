# 0479-4ott-mattina-report-giornaliero.req

_eseguito: 2026-10-04 06:20 UTC_

**richiesta:** `report-giornaliero`
**eseguito:** `.venv/bin/python -m scripts.report_giornaliero --pubblica`
**esito:** codice 0 in 2.6s

```
[report] backlog: 27 voci in 7 gruppi, aspettano il si' 0 (commit 2966a58)
[firebase] connesso (Firestore + RTDB)
[report] backlog pubblicato: si
[report] report del 2026-10-03 pubblicato: si
REPORT GIORNALIERO del 2026-10-03 (versione 2966a58)

== In breve
  - Paper ieri: 16 trade, +18.22 USDT (+0.869R a trade). Ultimi 7 giorni +15.74 USDT (+0.019R); dal 27 set +0.052R netti a trade su 112.
  - Gate: Un giro e' in corso dalle 04/10 08:15; il precedente era finito alle 04/10 07:38: 20667 valutazioni, 25 passate, durato 1h45.
  - Niente aspetta il tuo sì.
  - Capito: Lettura ufficiale del 3 ott: le declassate (−0,131R su 70) contro le attive (+0,127R su 33) fanno −0,258R con margine ±0,458R → «non si decide» (ops 0445). Il quarto di puntata ha risparmiato 29,04 USDT, ma non si può dire che scelga trade peggiori.

== Il paper ieri
  - Ieri (2026-10-03): 16 trade delle validate, 15 vinti, +18.22 USDT, +0.869R netti a trade. Sul conto (esplorativi e chiusure esterne compresi): 17 trade, +18.85 USDT.
  - Equity 937.41 USDT (-6.26% dall'inizio del paper, il 2026-09-16).
  - Adesso 3 posizioni aperte, rischio aperto 0.62% del capitale, uPnL -1.11 USDT.
  - Ultimi 7 giorni sul conto: 3 in utile, 4 in perdita.
  - Confronto: BTC comprato il primo giorno +11.9%, noi -6.3%.
    periodo | trade | vinti | PnL USDT | R netto | R lordo | costi R
    ieri | 16 | 94% | +18.22 | +0.869R | +0.957R | +0.088R
    7 giorni | 144 | 64% | +15.74 | +0.019R | +0.103R | +0.084R
    dal 27 set | 112 | 65% | +14.47 | +0.052R | +0.131R | +0.079R
    tutto | 247 | 57% | -61.81 | -0.048R | +0.033R | +0.081R

== Come va il gate
  - Un giro e' in corso dalle 04/10 08:15; il precedente era finito alle 04/10 07:38: 20667 valutazioni, 25 passate, durato 1h45.
  - Validate 223 su 76 coin, copertura 38.0%; declassate 169.
  - Ultimi 7 giorni: 68 promosse, 0 rimosse.
  - Il cervello: varianti dai referti 0 create, 0 promosse; intorno 40 madri, 1 promosse.
  - Registro: 1608 coppie su un tetto di 3000.
  - Esplorative: 48 attive, poi validate 3, scartate 327.
  - Fuori campione (le validate guadagnano anche DOPO la scelta? ultimo report del 2026-10-04): Selezione: il motore guadagna ancora dopo la validazione (+0.006R, margine ±0.17R per giornata, 156 segnali): nessun verdetto contro il gate. Esecuzione: non si decide: sugli stessi segnali fanno quasi uguale (differenza +0.03R, margine ±0.10R per giornata). Si rilegge il 14 ott.
  - R1, il gate rigiocato nel passato: 2 date su 26, 144 unita' fatte.

== Cosa ci dicono i dati
  - Ipotesi nate dai referti (le prova il gate sulla storia): gen_bf2be656: scala_stretta — 3 perdite sotto il primo gradino (mfe mediana 0.42 R) (campione 3); gen_bf2be656: solo_short — long 3/3 persi (campione 3); gen_fa304106: solo_long — short 4/4 persi (campione 4); gen_fa304106: solo_short — long 3/3 persi (campione 3); gen_fca11c08: conferma_trend — 6 perdite controtrend (campione 6)
  - Trailing in tutto: 62 prematuri e 59 protetti su 133 verdetti; proposta del paper: nessuna.
     | ieri | 7 giorni | tutto
    INGRESSI |  |  | 
    perdite «mai andate a favore» | 0/1 | 28/52 | 44/82
    latenza segnale → ingresso (s, mediana) | 171 | 156 | 155
    ingresso rispetto al segnale (mediana) | +0.045R | +0.038R | +0.038R
    USCITE E TRAILING |  |  | 
    perdite morte sotto il primo gradino | 1/1 | 24/52 | 38/82
    trailing prematuri / verdetti | 6/10 | 44/86 | 61/131
    trailing protetti / verdetti | 3/10 | 36/86 | 58/131
    arrivati al primo target | 6/16 | 18/144 | 29/247
    massimo a favore (mediana, R) | 1.37 | 0.87 | 0.85
    STOP LOSS |  |  | 
    chiusi a stop | 1/16 | 51/144 | 106/247
    stop seguiti da un rimbalzo (rumore) | 1/1 | 12/51 | 28/106
    massimo contro (mediana, R) | 0.28 | 0.68 | 0.69
    RISCHIO |  |  | 
    rischio effettivo per trade (mediana) | 0.13% | 0.13% | 0.14%
    leva media | 1.19x | 1.23x | 1.34x
    DIREZIONE |  |  | 
    long: trade e R netto | 11 a +0.670R | 76 a -0.081R | 115 a -0.118R
    short: trade e R netto | 5 a +1.308R | 68 a +0.130R | 132 a +0.016R

== Le funzioni servono?
  - Regola (scritta prima dei numeri): sotto 10 trade per gruppo «campione piccolo»; oltre 2 errori standard nel verso atteso «contribuisce», nel verso opposto «va contro»; altrimenti «non si vede ancora». USDT: quanto ha risparmiato (o tolto) la riduzione di size rispetto alla size piena.
  - Origine delle strategie nel paper: casuali 214 trade a -0.067R · intorno 1 trade a +0.292R
    funzione | toccati | altri | differenza | verdetto | USDT
    freno globale da deriva | 166 a -0.033R | 49 a -0.173R | +0.140 ±0.278 | non si vede ancora | +3.16
    panchina dei pesi | 1 a +0.435R | 214 a -0.067R | — | campione piccolo | -0.64
    pesi alti (size e leva in su) | 38 a +0.004R | 18 a -0.084R | +0.088 ±0.568 | non si vede ancora | 
    leva sopra 1x | 47 a +0.026R | 168 a -0.090R | +0.116 ±0.303 | non si vede ancora | 
    tilt di trend e sentiment | 48 a -0.032R | 118 a -0.033R | +0.001 ±0.311 | non si vede ancora | -1.53
    declassate a un quarto | 84 a -0.058R | 131 a -0.070R | +0.012 ±0.250 | non si vede ancora | +5.99
    paper esplorativo | 10 a +0.385R | 215 a -0.065R | +0.450 ±0.419 | contribuisce | 

== Cosa abbiamo capito
  - Note del 2026-10-03:
  - Lettura ufficiale del 3 ott: le declassate (−0,131R su 70) contro le attive (+0,127R su 33) fanno −0,258R con margine ±0,458R → «non si decide» (ops 0445). Il quarto di puntata ha risparmiato 29,04 USDT, ma non si può dire che scelga trade peggiori.
  - Lo «0 promosse» di R1 su 16.000 candidate (ops 0458) è sospetto ma non dimostrato: il gate vero passa lo 0,19% di un mix di 92 strategie (39 casuali nuove, 28 mutazioni dei quasi-passaggi, 25 rivalutate; 44/22.632, ops 0448/0450) e non stampa quante delle 44 siano casuali. Le due date complete sono recenti (17 e 3 set), quindi non è «storia corta». Si decide solo a parità di candidate (R2).
  - R1 lavora 2,5 ore a lancio per costruzione (BUDGET_S): ieri 315 unità in ~2,4 ore di calcolo, poi fermo fino al lancio di stamattina. A 200 monete restano ~36 ore (ops 0458): la lettura del 10 ott non è raggiungibile senza la restrizione alle monete operate.
  - Metà degli stop sono ingressi sbagliati dall'inizio: 51 su 107 (48%) non vanno mai a favore di 0,25R, e dei 7 stop nuovi 5 sono così (ops 0451 vs 0426). Il selettore in ombra non li distingue: p media 0,649 nei vinti contro 0,648 nei persi, correlazione +0,003 su 166 (ops 0445).
  - L'ondata di 10 long del 2 ott è a +4,27 USDT sulle 8 chiuse (ops 0445) e la fascia «6+ posizioni nello stesso verso» è l'unica in R positivo (+0,026 su 11, contro −0,100 su 137 e −0,125 su 90). Su questi numeri l'affollamento non è dove si perde; campione piccolo.
  - Il motore dopo la validazione resta a −0,03R, ora su 130 segnali ±0,18 (ops 0454; ieri 106 ±0,21): il margine si stringe e il numero non si muove.

== Cosa è cambiato nel sistema
  - 03/10 09:03 — R2: le candidate di R1 giudicate dal gate di oggi, all'inizio del prossimo lancio (regola scritta prima dei numeri; R1 si ferma da solo se è più severo del gate)
  - 03/10 08:42 — Controllo del 3 ott: lettura declassate (non si decide), capito, R2 nel gruppo 0; ondate in ora italiana
  - 02/10 21:13 — Affollamento nel report trades (posizioni nello stesso verso, ondate); idee AI con autopsia e varianti dai referti spente (decisione del proprietario)

== Aspetta il tuo sì e prossime letture
  - Aspettano il tuo sì: niente.
  - In lavorazione: R2. Taratura di R1 a parità di candidate: R1 giudica come il gate vero? — SÌ del proprietario il 3 ott: gira all'inizio del prossimo lancio di R1 (finestra del 4 ott, 14:00); R1. Rigiocare il gate nel passato — SÌ del proprietario il 1 ott; dal 2 ott lavora AL POSTO del giro del gate delle 14:00 italiane (sì del 1 ott sera); J2. «Cosa aspetta il sì» in dashboard, senza aggiornarlo a mano — in lavorazione (1 ott); D8. Raccolta dei dati mancanti (punto 4 del 1 ott) — ATTIVA dal riavvio del 1 ott 17:24 («[cattura]» nel log del bot); T2. La curva del vantaggio del segnale — FATTA il 2 ott: «nessun vantaggio misurabile» (ops 0437); la sezione resta nel report mfe e si rilegge col crescere dei trade
    data | cosa si legge | regola
    2026-10-07 | Fuori campione: il problema è il gate o il bot? (report portafoglio) | regole del 7 e 14 ott, diario del 30 set
    2026-10-10 | R1, il gate rigiocato nel passato (prima lettura completa, STIMA: dal 2 ott sulle sole monete operate, ~1/3 del lavoro, 2,5 ore al giorno) | regola R1, diario del 1 ott
    2026-10-10 | Varianti dai referti e ipotesi d'ingresso (J9, I4ter) | backlog archivio
    2026-10-14 | Fuori campione, seconda lettura | regole del 7 e 14 ott
    2026-10-15 | Gruppo di controllo: servono 3 conferme? (K3) | backlog archivio K3
    2026-10-18 | Conferma a maggioranza (J11), sessione oraria (J13), passata a 1 ora (C1) | backlog archivio

== Salute e costi
  - Semafori: sistema verde, paper giallo.
  - Anomalia FRENO_GLOBALE: freno globale da deriva: PF 0,76 vs 2,00 atteso
  - Anomalia SENZA_PROMESSA: 122 validate su 223 senza promessa (last_pf)
  - Riavvii del bot nelle 24 ore: 0.
  - Letture Firestore nelle 24 ore: 7830 (quota gratuita 50.000).
  - Spesa AI di ieri (2026-10-03): nessun dato.
```
