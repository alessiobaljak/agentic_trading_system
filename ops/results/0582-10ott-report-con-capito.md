# 0582-10ott-report-con-capito.req

_eseguito: 2026-10-10 04:08 UTC_

**richiesta:** `report-giornaliero`
**eseguito:** `.venv/bin/python -m scripts.report_giornaliero --pubblica`
**esito:** codice 0 in 3.8s

```
[report] backlog: 31 voci in 7 gruppi, aspettano il si' 0 (commit 90e8832)
[firebase] connesso (Firestore + RTDB)
[report] backlog pubblicato: si
[report] report del 2026-10-09 pubblicato: si
REPORT GIORNALIERO del 2026-10-09 (versione 90e8832)

== In breve
  - Paper ieri: 24 trade, +1.28 USDT (+0.171R a trade). Ultimi 7 giorni -29.49 USDT (-0.077R); dal 27 set -0.080R netti a trade su 283.
  - Gate: Un giro e' in corso dalle 10/10 03:27; il precedente era finito alle 10/10 03:10: 57311 valutazioni, 185 passate, durato 3h46.
  - Niente aspetta il tuo sì.
  - Capito: Il numero guida migliora un poco ma resta sotto zero: dopo la scelta del gate il motore fa −0,05R a trade su 351 segnali, ±0,11R per giornata (ops 0577); ieri −0,08 su 322 ±0,12. Con la regola del 14 ott («motore ≤ 0 con almeno 80 segnali») la lettura direbbe ancora «la prossima modifica va nel gate»; sugli stessi segnali paper e motore restano vicini (+0,02 ±0,05).

== Il paper ieri
  - Ieri (2026-10-09): 24 trade delle validate, 15 vinti, +1.28 USDT, +0.171R netti a trade. Sul conto (esplorativi e chiusure esterne compresi): 25 trade, +1.58 USDT.
  - Equity 890.58 USDT (-10.94% dall'inizio del paper, il 2026-09-16).
  - Adesso 4 posizioni aperte, rischio aperto 0.46% del capitale, uPnL -0.76 USDT.
  - Ultimi 7 giorni sul conto: 1 in utile, 6 in perdita.
  - Confronto: BTC comprato il primo giorno +9.1%, noi -10.9%.
    periodo | trade | vinti | PnL USDT | R netto | R lordo | costi R
    ieri | 24 | 62% | +1.28 | +0.171R | +0.257R | +0.086R
    7 giorni | 187 | 56% | -29.49 | -0.077R | +0.024R | +0.102R
    dal 27 set | 283 | 57% | -33.23 | -0.080R | +0.014R | +0.093R
    tutto | 418 | 55% | -109.52 | -0.101R | -0.010R | +0.091R

== Come va il gate
  - Un giro e' in corso dalle 10/10 03:27; il precedente era finito alle 10/10 03:10: 57311 valutazioni, 185 passate, durato 3h46.
  - Validate 236 su 77 coin, copertura 38.5%; declassate 105.
  - Ultimi 7 giorni: 129 promosse, 94 rimosse.
  - Il cervello: varianti dai referti 0 create, 0 promosse; intorno 0 madri, 0 promosse.
  - Registro: 1881 coppie su un tetto di 3000.
  - Esplorative: 38 attive, poi validate 4, scartate 540.
  - Fuori campione (le validate guadagnano anche DOPO la scelta? ultimo report del 2026-10-10): Selezione: la promessa non regge dopo la validazione: motore -0.05R (margine ±0.11R per giornata) su 351 segnali. O il gate sceglie coppie buone solo nei giorni su cui le ha provate, o il mercato e' cambiato: da qui non si separano. Per la regola la prossima modifica va nel gate. Esecuzione: non si decide: sugli stessi segnali fanno quasi uguale (differenza +0.02R, margine ±0.05R per giornata). Si rilegge il 14 ott.
  - R1, il gate rigiocato nel passato: 8 date su 26, 597 unita' fatte.

== Cosa ci dicono i dati
  - Ipotesi nate dai referti (le prova il gate sulla storia): gen_8b91ba18: scala_stretta — 3 perdite sotto il primo gradino (mfe mediana 0.62 R) (campione 3); gen_bf2be656: scala_stretta — 3 perdite sotto il primo gradino (mfe mediana 0.42 R) (campione 3); gen_bf2be656: solo_short — long 3/3 persi (campione 3); gen_ceab7f6a: ingresso_vol_ratio — 4 perdite d'ingresso su 5 con volume sotto la media (vol_ratio < 1) (mediana 0.71),…; gen_e59ad90b: conferma_trend — 3 perdite controtrend (campione 3)
  - Trailing in tutto: 101 prematuri e 98 protetti su 217 verdetti; proposta del paper: nessuna.
     | ieri | 7 giorni | tutto
    INGRESSI |  |  | 
    perdite «mai andate a favore» | 4/9 | 32/83 | 76/164
    latenza segnale → ingresso (s, mediana) | 177 | 179 | 168
    ingresso rispetto al segnale (mediana) | +0.000R | +0.012R | +0.013R
    USCITE E TRAILING |  |  | 
    perdite morte sotto il primo gradino | 5/9 | 51/83 | 88/164
    trailing prematuri / verdetti | 7/11 | 45/95 | 100/216
    trailing protetti / verdetti | 4/11 | 43/95 | 98/216
    arrivati al primo target | 6/24 | 23/187 | 46/418
    massimo a favore (mediana, R) | 1.04 | 0.76 | 0.81
    STOP LOSS |  |  | 
    chiusi a stop | 8/24 | 79/187 | 184/418
    stop seguiti da un rimbalzo (rumore) | 1/6 | 11/77 | 38/182
    massimo contro (mediana, R) | 0.56 | 0.71 | 0.72
    RISCHIO |  |  | 
    rischio effettivo per trade (mediana) | 0.13% | 0.13% | 0.13%
    leva media | 1.21x | 1.31x | 1.33x
    DIREZIONE |  |  | 
    long: trade e R netto | 16 a +0.566R | 121 a -0.120R | 225 a -0.161R
    short: trade e R netto | 8 a -0.619R | 66 a +0.001R | 193 a -0.028R

== Le funzioni servono?
  - Regola (scritta prima dei numeri): sotto 10 trade per gruppo «campione piccolo»; oltre 2 errori standard nel verso atteso «contribuisce», nel verso opposto «va contro»; altrimenti «non si vede ancora». USDT: quanto ha risparmiato (o tolto) la riduzione di size rispetto alla size piena.
  - Origine delle strategie nel paper: ai 6 trade a -0.232R · casuali 372 trade a -0.093R · intorno 5 trade a -0.831R
    funzione | toccati | altri | differenza | verdetto | USDT
    freno globale da deriva | 334 a -0.095R | 49 a -0.173R | +0.078 ±0.262 | non si vede ancora | +22.32
    panchina dei pesi | 9 a +0.083R | 374 a -0.109R | — | campione piccolo | -1.62
    pesi alti (size e leva in su) | 96 a -0.165R | 39 a -0.058R | -0.107 ±0.420 | non si vede ancora | 
    leva sopra 1x | 102 a -0.142R | 281 a -0.091R | -0.051 ±0.215 | non si vede ancora | 
    tilt di trend e sentiment | 120 a -0.120R | 214 a -0.080R | -0.040 ±0.220 | non si vede ancora | +1.50
    declassate a un quarto | 194 a -0.079R | 189 a -0.131R | +0.052 ±0.191 | non si vede ancora | +32.05
    paper esplorativo | 18 a +0.149R | 383 a -0.105R | +0.254 ±0.449 | non si vede ancora | 

== Cosa abbiamo capito
  - Note del 2026-10-10:
  - Il numero guida migliora un poco ma resta sotto zero: dopo la scelta del gate il motore fa −0,05R a trade su 351 segnali, ±0,11R per giornata (ops 0577); ieri −0,08 su 322 ±0,12. Con la regola del 14 ott («motore ≤ 0 con almeno 80 segnali») la lettura direbbe ancora «la prossima modifica va nel gate»; sugli stessi segnali paper e motore restano vicini (+0,02 ±0,05).
  - Una giornata buona non cambia il quadro: ieri le validate hanno fatto +0,171R a trade su 24, trainate dai long (+0,566R su 16) mentre gli short hanno perso (−0,619R su 8) (ops 0581). Dal 27 set i long restano a −0,140R su 176 e gli short a +0,004R su 111 (ops 0568): un giorno su 23 non sposta il segno.
  - Lo spazio del registro torna a scendere a ondate: ~444 coppie (ieri ~537, ops 0571 e 0556): 93 in meno in un giorno; con questo passo l'allarme dei 400 arriva fra uno e due giorni.
  - Le letture di Firebase crescono come previsto ieri: 16.811 nelle 24 ore, di cui 13.241 dai segnali rifiutati (ops 0572); ieri 14.521: +2.290, contro i ~2.400 stimati. La quota gratuita (50.000) si toccherebbe in circa due settimane.
  - Il protocollo di ricerca ha finito le campagne: 20 monete su 20, 600 varianti, 7 candidati in validazione, 3 confermati per il vault (BTCUSDT, BNBUSDT, ADAUSDT), tutti fragili per dichiarazione delle campagne stesse; 3 su 6 valutabili sotto la soglia contro 0,2-0,6 attesi per puro caso: un indizio, lo decide il vault (research/passo4/riepilogo.md, branch di coordinamento).
  - L'esame delle campagne non scambia il rumore per vantaggio, nemmeno sui prezzi veri. 1.479 strategie senza vantaggio (regole da manuale spostate nel tempo, 80 monete fuori dalla lista, solo fino al 2023) giudicate come una campagna: «nette» lo 0,41% (soglia scritta prima 3%, dichiarato 0-2%); p sotto 0,10 in validazione il 3,26% (soglia 13%, dichiarato 6-11%) (research/taratura/placebo/risultati.md, branch di coordinamento).
  - L'esame è più severo di quanto dice, e costa potenza. Il t delle strategie finte ha deviazione standard 0,815 invece di 1: un vantaggio piccolo ma vero passa meno spesso del previsto. Non si allenta l'esame guardando questi numeri; la risposta già scritta è la campagna di gruppo, che somma i trade di più monete.

== Cosa è cambiato nel sistema
  - 10/10 06:07 — Controllo del 10 ottobre: numeri e cosa abbiamo capito
  - 09/10 23:19 — Diario e backlog: tutte e 20 le monete consegnate, tre candidati confermati per il vault
  - 09/10 21:16 — Diario: DYDXUSDT, GALAUSDT e FTMUSDT consegnate; aperta l'ultima, ETCUSDT
  - 09/10 20:16 — Diario: MASKUSDT e FILUSDT consegnate; aperte FTMUSDT e GALAUSDT
  - 09/10 19:37 — Protocollo 4.5: in validazione serve anche R medio dopo i costi positivo (si' del proprietario)
  - 09/10 19:17 — Diario: TRBUSDT e 1000SHIBUSDT consegnate, FILUSDT ferma su una domanda, aperte DYDXUSDT e MASKUSDT
  - 09/10 18:16 — Diario: ADAUSDT consegnata con un candidato; aperta 1000SHIBUSDT
  - 09/10 17:17 — Diario: BCHUSDT, LINKUSDT e AVAXUSDT consegnate; aperte ADAUSDT, TRBUSDT e FILUSDT
  - 09/10 16:18 — Diario: BNBUSDT, MATICUSDT e LTCUSDT consegnate; aperte BCHUSDT, LINKUSDT e AVAXUSDT
  - 09/10 15:17 — Diario: XRPUSDT e DOGEUSDT consegnate, aperte LTCUSDT e MATICUSDT
  - 09/10 14:17 — Diario: 4.5 approvata, tre campagne aperte, test di GitHub di nuovo verdi
  - 09/10 14:12 — Protocollo 4.5 approvato; guardiano senza --no-walk; data del backlog con l'apostrofo

== Aspetta il tuo sì e prossime letture
  - Aspettano il tuo sì: niente.
  - In lavorazione: P0. Il protocollo di ricerca per moneta — versione 4.5 (approvata il 9 ott). TUTTE E 20 LE MONETE HANNO CONSEGNATO il 9 ott: 3 candidati confermati per il vault (BTCUSDT, BNBUSDT, ADAUSDT; riepilogo in research/passo4/riepilogo.md sul branch di coordinamento). ALLO STOP del Passo 4: il proprietario decide (1) la campagna di gruppo prima del vault, (2) se rifare BTCUSDT per la regola dei ritocchi; il vault si apre solo con «APRI IL VAULT»; G7. Il gate sul prezzo casuale: quante strategie passa per caso, a 1 ora? — FATTA il 5 ott: candele vere 8 passate su 7.200 (0,11%), rimescolate 16 su 7.200 (0,22%), rapporto 2,0 → per la regola NON SI SA (meno di 10 passate sul vero), ops 0506; R2. Taratura di R1 a parità di candidate — FATTA il 4 ott: 0 passate su 3.600 → lo 0 di R1 è vero (ops 0485); la scelta del piano è in R1b; R1. Rigiocare il gate nel passato — FERMATA dal proprietario il 4 ott (opzione c, dopo R2): il lancio del 5 ott fa solo la prova sul prezzo casuale (G7) e poi toglie il file «attivo»; il gate torna a 8 giri al giorno. La scelta del gate si legge nel fuori campione del 7 e 14 ott; J2. «Cosa aspetta il sì» in dashboard, senza aggiornarlo a mano — in lavorazione (1 ott); D8. Raccolta dei dati mancanti (punto 4 del 1 ott) — ATTIVA dal riavvio del 1 ott 17:24 («[cattura]» nel log del bot); T2. La curva del vantaggio del segnale — FATTA il 2 ott: «nessun vantaggio misurabile» (ops 0437); la sezione resta nel report mfe e si rilegge col crescere dei trade
    data | cosa si legge | regola
    2026-10-10 | R1, il gate rigiocato nel passato — ANNULLATA: fermato dal proprietario il 4 ott; il lancio del 5 ott ha fatto solo la prova sul prezzo casuale (G7, ops 0506) e il file «attivo» è stato tolto. Non c'è niente da leggere (nota del controllo del 9 ott) | regola R1, diario del 1 ott
    2026-10-10 | Varianti dai referti e ipotesi d'ingresso (J9, I4ter) | backlog archivio
    2026-10-14 | Fuori campione, seconda lettura | regole del 7 e 14 ott
    2026-10-15 | Gruppo di controllo: servono 3 conferme? (K3) | backlog archivio K3
    2026-10-18 | Conferma a maggioranza (J11), sessione oraria (J13), passata a 1 ora (C1) | backlog archivio
    2026-10-26 | Rifiutati contro aperti, finestre uguali (J6) | regola J6

== Salute e costi
  - Semafori: sistema giallo, paper giallo.
  - Anomalia FRENO_GLOBALE: freno globale da deriva: PF 0,71 vs 2,02 atteso
  - Anomalia GATE_SFORA: il giro del gate e' durato 3 h 46 (piu' di 3 h)
  - Riavvii del bot nelle 24 ore: 0.
  - Letture Firestore nelle 24 ore: 16878 (quota gratuita 50.000).
  - Spesa AI di ieri (2026-10-09): nessun dato.
```
