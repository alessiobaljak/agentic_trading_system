# 0566-9ott-mattina-report-giornaliero.req

_eseguito: 2026-10-09 04:05 UTC_

**richiesta:** `report-giornaliero`
**eseguito:** `.venv/bin/python -m scripts.report_giornaliero --pubblica`
**esito:** codice 0 in 3.1s

```
[report] backlog: 31 voci in 7 gruppi, aspettano il si' 0 (commit b693658)
[firebase] connesso (Firestore + RTDB)
[report] backlog pubblicato: si
[report] report del 2026-10-08 pubblicato: si
REPORT GIORNALIERO del 2026-10-08 (versione b693658)

== In breve
  - Paper ieri: 39 trade, -15.36 USDT (-0.149R a trade). Ultimi 7 giorni -27.29 USDT (-0.121R); dal 27 set -0.103R netti a trade su 259.
  - Gate: Un giro e' in corso dalle 09/10 03:22; il precedente era finito alle 09/10 03:06: 60984 valutazioni, 180 passate, durato 3h47.
  - Niente aspetta il tuo sì.
  - Capito: Il numero guida peggiora ancora, con più segnali: dopo la scelta del gate il motore fa −0,08R a trade su 279 segnali, margine ±0,14R per giornata (ops 0547); ieri −0,05 su 230 (ops 0532). La lettura del 7 ott («la prossima modifica va nel gate») si rafforza invece di attenuarsi; sugli stessi segnali paper e motore restano vicini (+0,03 ±0,06): il problema continua a essere cosa sceglie il gate, non come esegue il bot.

== Il paper ieri
  - Ieri (2026-10-08): 39 trade delle validate, 21 vinti, -15.36 USDT, -0.149R netti a trade. Sul conto (esplorativi e chiusure esterne compresi): 41 trade, -12.51 USDT.
  - Equity 890.11 USDT (-10.99% dall'inizio del paper, il 2026-09-16).
  - Adesso 9 posizioni aperte, rischio aperto 1.16% del capitale, uPnL +2.18 USDT.
  - Ultimi 7 giorni sul conto: 1 in utile, 6 in perdita.
  - Confronto: BTC comprato il primo giorno +8.2%, noi -11.0%.
    periodo | trade | vinti | PnL USDT | R netto | R lordo | costi R
    ieri | 39 | 54% | -15.36 | -0.149R | -0.071R | +0.078R
    7 giorni | 186 | 54% | -27.29 | -0.121R | -0.020R | +0.101R
    dal 27 set | 259 | 57% | -34.51 | -0.103R | -0.009R | +0.094R
    tutto | 394 | 54% | -110.79 | -0.120R | -0.028R | +0.091R

== Come va il gate
  - Un giro e' in corso dalle 09/10 03:22; il precedente era finito alle 09/10 03:06: 60984 valutazioni, 180 passate, durato 3h47.
  - Validate 238 su 78 coin, copertura 39.0%; declassate 122.
  - Ultimi 7 giorni: 110 promosse, 71 rimosse.
  - Il cervello: varianti dai referti 0 create, 0 promosse; intorno 40 madri, 4 promosse.
  - Registro: 1845 coppie su un tetto di 3000.
  - Esplorative: 42 attive, poi validate 4, scartate 502.
  - Fuori campione (le validate guadagnano anche DOPO la scelta? ultimo report del 2026-10-09): Selezione: la promessa non regge dopo la validazione: motore -0.08R (margine ±0.12R per giornata) su 322 segnali. O il gate sceglie coppie buone solo nei giorni su cui le ha provate, o il mercato e' cambiato: da qui non si separano. Per la regola la prossima modifica va nel gate. Esecuzione: non si decide: sugli stessi segnali fanno quasi uguale (differenza +0.03R, margine ±0.06R per giornata). Si rilegge il 14 ott.
  - R1, il gate rigiocato nel passato: 8 date su 26, 597 unita' fatte.

== Cosa ci dicono i dati
  - Ipotesi nate dai referti (le prova il gate sulla storia): gen_8b91ba18: scala_stretta — 3 perdite sotto il primo gradino (mfe mediana 0.62 R) (campione 3); gen_bf2be656: scala_stretta — 3 perdite sotto il primo gradino (mfe mediana 0.42 R) (campione 3); gen_bf2be656: solo_short — long 3/3 persi (campione 3); gen_e59ad90b: conferma_trend — 3 perdite controtrend (campione 3); gen_fa304106: conferma_trend — 4 perdite mai andate a favore (classe ingresso) e 0 vinti su 11 (campione 4)
  - Trailing in tutto: 91 prematuri e 91 protetti su 198 verdetti; proposta del paper: nessuna.
     | ieri | 7 giorni | tutto
    INGRESSI |  |  | 
    perdite «mai andate a favore» | 7/18 | 35/85 | 72/155
    latenza segnale → ingresso (s, mediana) | 182 | 178 | 166
    ingresso rispetto al segnale (mediana) | +0.013R | +0.021R | +0.021R
    USCITE E TRAILING |  |  | 
    perdite morte sotto il primo gradino | 11/18 | 50/85 | 83/155
    trailing prematuri / verdetti | 6/14 | 41/89 | 90/198
    trailing protetti / verdetti | 8/14 | 41/89 | 92/198
    arrivati al primo target | 4/39 | 19/186 | 40/394
    massimo a favore (mediana, R) | 0.58 | 0.73 | 0.80
    STOP LOSS |  |  | 
    chiusi a stop | 16/39 | 81/186 | 176/394
    stop seguiti da un rimbalzo (rumore) | 1/13 | 12/78 | 37/173
    massimo contro (mediana, R) | 0.66 | 0.72 | 0.74
    RISCHIO |  |  | 
    rischio effettivo per trade (mediana) | 0.13% | 0.13% | 0.13%
    leva media | 1.28x | 1.34x | 1.34x
    DIREZIONE |  |  | 
    long: trade e R netto | 29 a -0.293R | 119 a -0.220R | 209 a -0.221R
    short: trade e R netto | 10 a +0.267R | 67 a +0.055R | 185 a +0.002R

== Le funzioni servono?
  - Regola (scritta prima dei numeri): sotto 10 trade per gruppo «campione piccolo»; oltre 2 errori standard nel verso atteso «contribuisce», nel verso opposto «va contro»; altrimenti «non si vede ancora». USDT: quanto ha risparmiato (o tolto) la riduzione di size rispetto alla size piena.
  - Origine delle strategie nel paper: ai 6 trade a -0.232R · casuali 349 trade a -0.112R · intorno 5 trade a -0.831R
    funzione | toccati | altri | differenza | verdetto | USDT
    freno globale da deriva | 311 a -0.116R | 49 a -0.173R | +0.057 ±0.263 | non si vede ancora | +24.72
    panchina dei pesi | 8 a +0.057R | 352 a -0.128R | — | campione piccolo | -1.46
    pesi alti (size e leva in su) | 89 a -0.150R | 36 a -0.111R | -0.039 ±0.446 | non si vede ancora | 
    leva sopra 1x | 95 a -0.126R | 265 a -0.123R | -0.003 ±0.222 | non si vede ancora | 
    tilt di trend e sentiment | 115 a -0.169R | 196 a -0.085R | -0.084 ±0.222 | non si vede ancora | +3.34
    declassate a un quarto | 177 a -0.101R | 183 a -0.146R | +0.045 ±0.197 | non si vede ancora | +39.24
    paper esplorativo | 18 a +0.149R | 360 a -0.124R | +0.273 ±0.449 | non si vede ancora | 

== Cosa abbiamo capito
  - Note del 2026-10-08:
  - Il numero guida peggiora ancora, con più segnali: dopo la scelta del gate il motore fa −0,08R a trade su 279 segnali, margine ±0,14R per giornata (ops 0547); ieri −0,05 su 230 (ops 0532). La lettura del 7 ott («la prossima modifica va nel gate») si rafforza invece di attenuarsi; sugli stessi segnali paper e motore restano vicini (+0,03 ±0,06): il problema continua a essere cosa sceglie il gate, non come esegue il bot.
  - Il giro della notte del gate ha fatto quasi il doppio del lavoro: 81.788 valutazioni contro 45.069 del giro prima, ed è durato 4 h 47 invece di 3 h 21 (ops 0541, ops 0526). Le coin valutate sono 254. Il motivo del raddoppio non è stampato: va capito prima che i giri si accavallino.
  - Lo spazio del registro scende di circa 107 coppie al giorno: ~496 stamattina, ~603 ieri (ops 0541, ops 0526). Di questo passo la soglia d'allarme dei 400 si supera domani (9 ott): la voce D1 del gruppo 5 («solo se serve») sta per servire.
  - Le letture di Firebase sono salite del 40% in un giorno: 12.109 nelle 24 ore contro 8.674 ieri, e 8.456 vengono dai segnali rifiutati (ops 0542, ops 0527). Lontane dalla quota (50.000), ma crescono più in fretta dei trade.
  - Dal 27 set i long perdono −0,190R a trade su 134 e gli short guadagnano +0,027R su 93 (ops 0538): quinta lettura di fila con lo stesso segno. L'unico angolo in utile resta lo short contro il verso di BTC: +0,134R su 48.

== Cosa è cambiato nel sistema
  - 08/10 22:33 — Backlog e diario: scenario «solo il candidato BTC» e correzione di una stima
  - 08/10 20:48 — Backlog e diario: analisi «17 monete o rilanciare le 3»
  - 08/10 16:08 — Diario e backlog: ricalcolo di ETHUSDT finito, nessun esito cambia
  - 08/10 15:50 — Campagne: correzione sulla regola di ultracode (la causa non era il modello passato)
  - 08/10 15:37 — Campagne: il modello si eredita, non si passa (altrimenti ultracode non passa)
  - 08/10 13:40 — Diario e backlog: tre consegne con la versione 4.4, un candidato al vault
  - 08/10 12:18 — Campagne: ogni nuova sessione con Opus 5.5 e ultracode (richiesta del proprietario)
  - 08/10 12:16 — Diario e backlog: il proprietario risponde sì alla domanda di Solana sui ritocchi
  - 08/10 11:37 — Diario: Solana ancora ferma sulla domanda
  - 08/10 10:34 — Diario e backlog: Bitcoin consegna con un candidato, correzione del funding sul principale, Solana ferma su una domanda
  - 08/10 10:32 — Ricerca: funding arrotondato al secondo nel caricatore (correzione di src)
  - 08/10 07:20 — Diario: Bitcoin e Solana riaperte, lezione sull'avvio delle sessioni

== Aspetta il tuo sì e prossime letture
  - Aspettano il tuo sì: niente.
  - In lavorazione: P0. Il protocollo di ricerca per moneta — versione 4.4 approvata l'8 ott; le tre campagne BTCUSDT, ETHUSDT e SOLUSDT rifatte e CONSEGNATE l'8 ott: BTCUSDT con un candidato al vault (esito provvisorio, p-value 0,048), ETHUSDT e SOLUSDT nessuna strategia valida. ALLO STOP: il proprietario decide come proseguire (altre 17 monete con la 4.5, oppure meno monete per arrivare prima al vault). Rilettura di ETHUSDT con il caricatore del funding corretto FATTA l'8 ott (16:07 ora di Roma, commit f66fcf0 sul suo branch): 38 risultati su 72 cambiano di poco, nessun esito cambia; G7. Il gate sul prezzo casuale: quante strategie passa per caso, a 1 ora? — FATTA il 5 ott: candele vere 8 passate su 7.200 (0,11%), rimescolate 16 su 7.200 (0,22%), rapporto 2,0 → per la regola NON SI SA (meno di 10 passate sul vero), ops 0506; R2. Taratura di R1 a parità di candidate — FATTA il 4 ott: 0 passate su 3.600 → lo 0 di R1 è vero (ops 0485); la scelta del piano è in R1b; R1. Rigiocare il gate nel passato — FERMATA dal proprietario il 4 ott (opzione c, dopo R2): il lancio del 5 ott fa solo la prova sul prezzo casuale (G7) e poi toglie il file «attivo»; il gate torna a 8 giri al giorno. La scelta del gate si legge nel fuori campione del 7 e 14 ott; J2. «Cosa aspetta il sì» in dashboard, senza aggiornarlo a mano — in lavorazione (1 ott); D8. Raccolta dei dati mancanti (punto 4 del 1 ott) — ATTIVA dal riavvio del 1 ott 17:24 («[cattura]» nel log del bot); T2. La curva del vantaggio del segnale — FATTA il 2 ott: «nessun vantaggio misurabile» (ops 0437); la sezione resta nel report mfe e si rilegge col crescere dei trade
    data | cosa si legge | regola
    2026-10-10 | R1, il gate rigiocato nel passato (prima lettura completa, STIMA: dal 2 ott sulle sole monete operate, ~1/3 del lavoro, 2,5 ore al giorno) | regola R1, diario del 1 ott
    2026-10-10 | Varianti dai referti e ipotesi d'ingresso (J9, I4ter) | backlog archivio
    2026-10-14 | Fuori campione, seconda lettura | regole del 7 e 14 ott
    2026-10-15 | Gruppo di controllo: servono 3 conferme? (K3) | backlog archivio K3
    2026-10-18 | Conferma a maggioranza (J11), sessione oraria (J13), passata a 1 ora (C1) | backlog archivio
    2026-10-26 | Rifiutati contro aperti, finestre uguali (J6) | regola J6

== Salute e costi
  - Semafori: sistema giallo, paper giallo.
  - Anomalia FRENO_GLOBALE: freno globale da deriva: PF 0,70 vs 2,02 atteso
  - Anomalia GATE_SFORA: il giro del gate e' durato 3 h 47 (piu' di 3 h)
  - Riavvii del bot nelle 24 ore: 0.
  - Letture Firestore nelle 24 ore: 14588 (quota gratuita 50.000).
  - Spesa AI di ieri (2026-10-08): nessun dato.
```
