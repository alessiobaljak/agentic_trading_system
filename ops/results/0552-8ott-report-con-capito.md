# 0552-8ott-report-con-capito.req

_eseguito: 2026-10-08 04:08 UTC_

**richiesta:** `report-giornaliero`
**eseguito:** `.venv/bin/python -m scripts.report_giornaliero --pubblica`
**esito:** codice 0 in 3.5s

```
[report] backlog: 29 voci in 7 gruppi, aspettano il si' 0 (commit f336b40)
[firebase] connesso (Firestore + RTDB)
[report] backlog pubblicato: si
[report] report del 2026-10-07 pubblicato: si
REPORT GIORNALIERO del 2026-10-07 (versione f336b40)

== In breve
  - Paper ieri: 40 trade, -10.39 USDT (-0.191R a trade). Ultimi 7 giorni -21.80 USDT (-0.144R); dal 27 set -0.095R netti a trade su 220.
  - Gate: Un giro e' in corso dalle 08/10 04:21; il precedente era finito alle 08/10 04:06: 81788 valutazioni, 228 passate, durato 4h47.
  - Niente aspetta il tuo sì.
  - Capito: Il numero guida peggiora ancora, con più segnali: dopo la scelta del gate il motore fa −0,08R a trade su 279 segnali, margine ±0,14R per giornata (ops 0547); ieri −0,05 su 230 (ops 0532). La lettura del 7 ott («la prossima modifica va nel gate») si rafforza invece di attenuarsi; sugli stessi segnali paper e motore restano vicini (+0,03 ±0,06): il problema continua a essere cosa sceglie il gate, non come esegue il bot.

== Il paper ieri
  - Ieri (2026-10-07): 40 trade delle validate, 18 vinti, -10.39 USDT, -0.191R netti a trade. Sul conto (esplorativi e chiusure esterne compresi): 43 trade, -12.95 USDT.
  - Equity 901.92 USDT (-9.81% dall'inizio del paper, il 2026-09-16).
  - Adesso 9 posizioni aperte, rischio aperto 1.32% del capitale, uPnL +1.51 USDT.
  - Ultimi 7 giorni sul conto: 2 in utile, 5 in perdita.
  - Confronto: BTC comprato il primo giorno +9.7%, noi -9.8%.
    periodo | trade | vinti | PnL USDT | R netto | R lordo | costi R
    ieri | 40 | 45% | -10.39 | -0.191R | -0.093R | +0.098R
    7 giorni | 162 | 53% | -21.80 | -0.144R | -0.040R | +0.104R
    dal 27 set | 220 | 57% | -19.15 | -0.095R | +0.002R | +0.097R
    tutto | 355 | 54% | -95.43 | -0.116R | -0.023R | +0.093R

== Come va il gate
  - Un giro e' in corso dalle 08/10 04:21; il precedente era finito alle 08/10 04:06: 81788 valutazioni, 228 passate, durato 4h47.
  - Validate 279 su 84 coin, copertura 42.0%; declassate 182.
  - Ultimi 7 giorni: 84 promosse, 0 rimosse.
  - Il cervello: varianti dai referti 0 create, 0 promosse; intorno 40 madri, 2 promosse.
  - Registro: 1988 coppie su un tetto di 3000.
  - Esplorative: 38 attive, poi validate 4, scartate 468.
  - Fuori campione (le validate guadagnano anche DOPO la scelta? ultimo report del 2026-10-08): Selezione: la promessa non regge dopo la validazione: motore -0.08R (margine ±0.14R per giornata) su 279 segnali. O il gate sceglie coppie buone solo nei giorni su cui le ha provate, o il mercato e' cambiato: da qui non si separano. Per la regola la prossima modifica va nel gate. Esecuzione: non si decide: sugli stessi segnali fanno quasi uguale (differenza +0.03R, margine ±0.06R per giornata). Si rilegge il 14 ott.
  - R1, il gate rigiocato nel passato: 8 date su 26, 597 unita' fatte.

== Cosa ci dicono i dati
  - Ipotesi nate dai referti (le prova il gate sulla storia): gen_8b91ba18: scala_stretta — 3 perdite sotto il primo gradino (mfe mediana 0.62 R) (campione 3); gen_bf2be656: scala_stretta — 3 perdite sotto il primo gradino (mfe mediana 0.42 R) (campione 3); gen_bf2be656: solo_short — long 3/3 persi (campione 3); gen_e59ad90b: conferma_trend — 3 perdite controtrend (campione 3); gen_fa304106: conferma_trend — 4 perdite mai andate a favore (classe ingresso) e 0 vinti su 10 (campione 4)
  - Trailing in tutto: 83 prematuri e 84 protetti su 182 verdetti; proposta del paper: nessuna.
     | ieri | 7 giorni | tutto
    INGRESSI |  |  | 
    perdite «mai andate a favore» | 6/22 | 32/76 | 65/137
    latenza segnale → ingresso (s, mediana) | 190 | 175 | 163
    ingresso rispetto al segnale (mediana) | +0.006R | +0.023R | +0.023R
    USCITE E TRAILING |  |  | 
    perdite morte sotto il primo gradino | 16/22 | 44/76 | 72/137
    trailing prematuri / verdetti | 6/14 | 36/79 | 83/182
    trailing protetti / verdetti | 8/14 | 37/79 | 84/182
    arrivati al primo target | 4/40 | 15/162 | 36/355
    massimo a favore (mediana, R) | 0.55 | 0.75 | 0.81
    STOP LOSS |  |  | 
    chiusi a stop | 22/40 | 74/162 | 160/355
    stop seguiti da un rimbalzo (rumore) | 0/19 | 12/71 | 36/157
    massimo contro (mediana, R) | 0.89 | 0.79 | 0.75
    RISCHIO |  |  | 
    rischio effettivo per trade (mediana) | 0.10% | 0.13% | 0.13%
    leva media | 1.32x | 1.35x | 1.35x
    DIREZIONE |  |  | 
    long: trade e R netto | 31 a -0.442R | 98 a -0.218R | 180 a -0.209R
    short: trade e R netto | 9 a +0.675R | 64 a -0.031R | 175 a -0.016R

== Le funzioni servono?
  - Regola (scritta prima dei numeri): sotto 10 trade per gruppo «campione piccolo»; oltre 2 errori standard nel verso atteso «contribuisce», nel verso opposto «va contro»; altrimenti «non si vede ancora». USDT: quanto ha risparmiato (o tolto) la riduzione di size rispetto alla size piena.
  - Origine delle strategie nel paper: ai 6 trade a -0.232R · casuali 316 trade a -0.106R · intorno 4 trade a -0.774R
    funzione | toccati | altri | differenza | verdetto | USDT
    freno globale da deriva | 277 a -0.106R | 49 a -0.173R | +0.067 ±0.266 | non si vede ancora | +23.54
    panchina dei pesi | 4 a +0.822R | 322 a -0.128R | — | campione piccolo | -2.14
    pesi alti (size e leva in su) | 79 a -0.178R | 30 a -0.006R | -0.172 ±0.503 | non si vede ancora | 
    leva sopra 1x | 86 a -0.146R | 240 a -0.106R | -0.040 ±0.233 | non si vede ancora | 
    tilt di trend e sentiment | 97 a -0.155R | 180 a -0.080R | -0.075 ±0.240 | non si vede ancora | +3.56
    declassate a un quarto | 159 a -0.121R | 167 a -0.112R | -0.009 ±0.208 | non si vede ancora | +48.89
    paper esplorativo | 15 a -0.023R | 326 a -0.116R | +0.093 ±0.454 | non si vede ancora | 

== Cosa abbiamo capito
  - Note del 2026-10-08:
  - Il numero guida peggiora ancora, con più segnali: dopo la scelta del gate il motore fa −0,08R a trade su 279 segnali, margine ±0,14R per giornata (ops 0547); ieri −0,05 su 230 (ops 0532). La lettura del 7 ott («la prossima modifica va nel gate») si rafforza invece di attenuarsi; sugli stessi segnali paper e motore restano vicini (+0,03 ±0,06): il problema continua a essere cosa sceglie il gate, non come esegue il bot.
  - Il giro della notte del gate ha fatto quasi il doppio del lavoro: 81.788 valutazioni contro 45.069 del giro prima, ed è durato 4 h 47 invece di 3 h 21 (ops 0541, ops 0526). Le coin valutate sono 254. Il motivo del raddoppio non è stampato: va capito prima che i giri si accavallino.
  - Lo spazio del registro scende di circa 107 coppie al giorno: ~496 stamattina, ~603 ieri (ops 0541, ops 0526). Di questo passo la soglia d'allarme dei 400 si supera domani (9 ott): la voce D1 del gruppo 5 («solo se serve») sta per servire.
  - Le letture di Firebase sono salite del 40% in un giorno: 12.109 nelle 24 ore contro 8.674 ieri, e 8.456 vengono dai segnali rifiutati (ops 0542, ops 0527). Lontane dalla quota (50.000), ma crescono più in fretta dei trade.
  - Dal 27 set i long perdono −0,190R a trade su 134 e gli short guadagnano +0,027R su 93 (ops 0538): quinta lettura di fila con lo stesso segno. L'unico angolo in utile resta lo short contro il verso di BTC: +0,134R su 48.

== Cosa è cambiato nel sistema
  - 08/10 06:08 — Controllo dell'8 ottobre: numeri, cosa abbiamo capito e backlog
  - 08/10 01:16 — Guardiano 4.4: niente rinvii o hash nei parametri delle pagine web, ricerche web normalizzate
  - 08/10 00:54 — Guardiano 4.4: editori di finanza fra i siti ammessi; lezione di metodo e registro aggiornati
  - 08/10 00:53 — Guardiano, seconda revisione della 4.4: branch, fetch, contenuti vecchi, siti web, exec-path
  - 08/10 00:18 — Protocollo 4.4: limiti dichiarati del guardiano (codice proprio, ricerche web) e pagine web solo da siti di pubblicazioni
  - 08/10 00:17 — Diario, backlog e «cosa abbiamo capito»: la versione 4.4 scritta e rivista, in attesa del si del proprietario
  - 08/10 00:14 — Protocollo 4.4, seconda revisione: pavimento dell'errore, (b) senza ingressi non validi, date con numeri interi, avvio della campagna e criteri della Fase 4 senza scelte libere
  - 07/10 23:05 — Registro delle correzioni: la riga del guardiano 4.4
  - 07/10 23:04 — guardiano 4.4: in campagna niente storia del principale, niente archivio, strumenti in lista bianca
  - 07/10 22:53 — Protocollo di ricerca 4.4 (testo in revisione): stima dei trade e «nettamente» unici, budget per intero, strumenti comuni e schede senza data di listing
  - 07/10 20:29 — Niente costi nelle risposte (CLAUDE.md); diario: rifare le tre campagne con regole cambiate prima del gruppo
  - 07/10 16:57 — Prova di processo completa: tre consegne senza strategie, rapporto sul coordinamento, diario e backlog aggiornati

== Aspetta il tuo sì e prossime letture
  - Aspettano il tuo sì: niente.
  - In lavorazione: P0. Il protocollo di ricerca per moneta — Passi 0, 1 e 2 fatti; il 7 ott il proprietario ha scelto di RIFARE le tre campagne della prova con la versione 4.4 («sì, rifalle con queste quattro modifiche»): stima dei trade unica, «nettamente» unico, minimo 70, budget per intero. Testo 4.4 scritto, rivisto in due giri avversari, sul branch principale (b9659df, c4248a3, 3cffbae): DA RIVEDERE DAL PROPRIETARIO; dopo il suo ok si archiviano i tre branch e si riaprono le tre campagne. La campagna di gruppo resta il passo dopo se anche così non esce niente; G7. Il gate sul prezzo casuale: quante strategie passa per caso, a 1 ora? — FATTA il 5 ott: candele vere 8 passate su 7.200 (0,11%), rimescolate 16 su 7.200 (0,22%), rapporto 2,0 → per la regola NON SI SA (meno di 10 passate sul vero), ops 0506; R2. Taratura di R1 a parità di candidate — FATTA il 4 ott: 0 passate su 3.600 → lo 0 di R1 è vero (ops 0485); la scelta del piano è in R1b; R1. Rigiocare il gate nel passato — FERMATA dal proprietario il 4 ott (opzione c, dopo R2): il lancio del 5 ott fa solo la prova sul prezzo casuale (G7) e poi toglie il file «attivo»; il gate torna a 8 giri al giorno. La scelta del gate si legge nel fuori campione del 7 e 14 ott; J2. «Cosa aspetta il sì» in dashboard, senza aggiornarlo a mano — in lavorazione (1 ott); D8. Raccolta dei dati mancanti (punto 4 del 1 ott) — ATTIVA dal riavvio del 1 ott 17:24 («[cattura]» nel log del bot); T2. La curva del vantaggio del segnale — FATTA il 2 ott: «nessun vantaggio misurabile» (ops 0437); la sezione resta nel report mfe e si rilegge col crescere dei trade
    data | cosa si legge | regola
    2026-10-10 | R1, il gate rigiocato nel passato (prima lettura completa, STIMA: dal 2 ott sulle sole monete operate, ~1/3 del lavoro, 2,5 ore al giorno) | regola R1, diario del 1 ott
    2026-10-10 | Varianti dai referti e ipotesi d'ingresso (J9, I4ter) | backlog archivio
    2026-10-14 | Fuori campione, seconda lettura | regole del 7 e 14 ott
    2026-10-15 | Gruppo di controllo: servono 3 conferme? (K3) | backlog archivio K3
    2026-10-18 | Conferma a maggioranza (J11), sessione oraria (J13), passata a 1 ora (C1) | backlog archivio
    2026-10-26 | Rifiutati contro aperti, finestre uguali (J6) | regola J6

== Salute e costi
  - Semafori: sistema giallo, paper giallo.
  - Anomalia FRENO_GLOBALE: freno globale da deriva: PF 0,72 vs 2,02 atteso
  - Anomalia GATE_SFORA: il giro del gate e' durato 4 h 47 (piu' di 3 h)
  - Anomalia SENZA_PROMESSA: 118 validate su 279 senza promessa (last_pf)
  - Riavvii del bot nelle 24 ore: 0.
  - Letture Firestore nelle 24 ore: 12177 (quota gratuita 50.000).
  - Spesa AI di ieri (2026-10-07): nessun dato.
```
