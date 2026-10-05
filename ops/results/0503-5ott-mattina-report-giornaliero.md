# 0503-5ott-mattina-report-giornaliero.req

_eseguito: 2026-10-05 06:21 UTC_

**richiesta:** `report-giornaliero`
**eseguito:** `.venv/bin/python -m scripts.report_giornaliero --pubblica`
**esito:** codice 0 in 2.9s

```
[report] backlog: 28 voci in 7 gruppi, aspettano il si' 0 (commit 2671584)
[firebase] connesso (Firestore + RTDB)
[report] backlog pubblicato: si
[report] report del 2026-10-04 pubblicato: si
REPORT GIORNALIERO del 2026-10-04 (versione 2671584)

== In breve
  - Paper ieri: 20 trade, -8.92 USDT (-0.417R a trade). Ultimi 7 giorni +5.56 USDT (-0.019R); dal 27 set -0.019R netti a trade su 132.
  - Gate: Un giro e' in corso dalle 05/10 06:26; il precedente era finito alle 05/10 06:15: 42274 valutazioni, 421 passate, durato 3h22.
  - Niente aspetta il tuo sì.
  - Capito: La stella polare è passata da −0,03R su 130 segnali (ops 0454) a +0,006R su 156, margine ±0,17 (ops 0474), per una giornata sola: il 3 ott 16 trade delle validate, 15 vinti, +0,869R a trade (ops 0479). Il numero oscilla intorno a zero dentro il margine: oggi la regola del 7 ott («motore ≤ 0 con almeno 80 segnali → la modifica va nel gate») non scatterebbe, ieri sì. Il verdetto del 7 ott può dipendere da un giorno buono o cattivo: per questo c'è la conferma del 14.

== Il paper ieri
  - Ieri (2026-10-04): 20 trade delle validate, 9 vinti, -8.92 USDT, -0.417R netti a trade. Sul conto (esplorativi e chiusure esterne compresi): 22 trade, -9.65 USDT.
  - Equity 923.92 USDT (-7.61% dall'inizio del paper, il 2026-09-16).
  - Adesso 1 posizioni aperte, rischio aperto 0.05% del capitale, uPnL +0.25 USDT.
  - Ultimi 7 giorni sul conto: 2 in utile, 5 in perdita.
  - Confronto: BTC comprato il primo giorno +12.9%, noi -7.6%.
    periodo | trade | vinti | PnL USDT | R netto | R lordo | costi R
    ieri | 20 | 45% | -8.92 | -0.417R | -0.282R | +0.136R
    7 giorni | 132 | 62% | +5.56 | -0.019R | +0.068R | +0.087R
    dal 27 set | 132 | 62% | +5.56 | -0.019R | +0.068R | +0.087R
    tutto | 267 | 56% | -70.73 | -0.080R | +0.006R | +0.086R

== Come va il gate
  - Un giro e' in corso dalle 05/10 06:26; il precedente era finito alle 05/10 06:15: 42274 valutazioni, 421 passate, durato 3h22.
  - Validate 235 (+12 nel giro) su 77 coin, copertura 38.5%; declassate 173.
  - Ultimi 7 giorni: 50 promosse, 0 rimosse.
  - Il cervello: varianti dai referti 0 create, 0 promosse; intorno 40 madri, 1 promosse.
  - Registro: 1697 coppie su un tetto di 3000.
  - Esplorative: 37 attive, poi validate 3, scartate 367.
  - Fuori campione (le validate guadagnano anche DOPO la scelta? ultimo report del 2026-10-05): Selezione: la promessa non regge dopo la validazione: motore -0.03R (margine ±0.17R per giornata) su 182 segnali. O il gate sceglie coppie buone solo nei giorni su cui le ha provate, o il mercato e' cambiato: da qui non si separano. Per la regola la prossima modifica va nel gate. Esecuzione: non si decide: sugli stessi segnali fanno quasi uguale (differenza +0.02R, margine ±0.08R per giornata). Si rilegge il 14 ott.
  - R1, il gate rigiocato nel passato: 8 date su 26, 597 unita' fatte.

== Cosa ci dicono i dati
  - Ipotesi nate dai referti (le prova il gate sulla storia): gen_bf2be656: scala_stretta — 3 perdite sotto il primo gradino (mfe mediana 0.42 R) (campione 3); gen_bf2be656: solo_short — long 3/3 persi (campione 3); gen_fa304106: conferma_trend — 3 perdite mai andate a favore (classe ingresso) e 0 vinti su 8 (campione 3); gen_fa304106: solo_long — short 5/5 persi (campione 5); gen_fa304106: solo_short — long 3/3 persi (campione 3)
  - Trailing in tutto: 67 prematuri e 64 protetti su 144 verdetti; proposta del paper: nessuna.
     | ieri | 7 giorni | tutto
    INGRESSI |  |  | 
    perdite «mai andate a favore» | 3/11 | 26/50 | 47/93
    latenza segnale → ingresso (s, mediana) | 163 | 158 | 156
    ingresso rispetto al segnale (mediana) | +0.000R | +0.031R | +0.031R
    USCITE E TRAILING |  |  | 
    perdite morte sotto il primo gradino | 8/11 | 24/50 | 46/93
    trailing prematuri / verdetti | 3/8 | 38/77 | 65/141
    trailing protetti / verdetti | 5/8 | 33/77 | 63/141
    arrivati al primo target | 0/20 | 12/132 | 29/267
    massimo a favore (mediana, R) | 0.81 | 0.86 | 0.84
    STOP LOSS |  |  | 
    chiusi a stop | 10/20 | 48/132 | 116/267
    stop seguiti da un rimbalzo (rumore) | 2/10 | 11/48 | 30/116
    massimo contro (mediana, R) | 0.83 | 0.70 | 0.70
    RISCHIO |  |  | 
    rischio effettivo per trade (mediana) | 0.13% | 0.13% | 0.14%
    leva media | 1.35x | 1.24x | 1.34x
    DIREZIONE |  |  | 
    long: trade e R netto | 10 a -0.431R | 74 a -0.084R | 125 a -0.147R
    short: trade e R netto | 10 a -0.403R | 58 a +0.063R | 142 a -0.019R

== Le funzioni servono?
  - Regola (scritta prima dei numeri): sotto 10 trade per gruppo «campione piccolo»; oltre 2 errori standard nel verso atteso «contribuisce», nel verso opposto «va contro»; altrimenti «non si vede ancora». USDT: quanto ha risparmiato (o tolto) la riduzione di size rispetto alla size piena.
  - Origine delle strategie nel paper: casuali 238 trade a -0.082R · intorno 3 trade a -0.669R
    funzione | toccati | altri | differenza | verdetto | USDT
    freno globale da deriva | 192 a -0.068R | 49 a -0.173R | +0.105 ±0.273 | non si vede ancora | +11.51
    panchina dei pesi | 2 a -0.304R | 239 a -0.087R | — | campione piccolo | -0.07
    pesi alti (size e leva in su) | 50 a -0.120R | 20 a -0.116R | -0.004 ±0.511 | non si vede ancora | 
    leva sopra 1x | 59 a -0.083R | 182 a -0.091R | +0.008 ±0.272 | non si vede ancora | 
    tilt di trend e sentiment | 53 a -0.042R | 139 a -0.077R | +0.035 ±0.290 | non si vede ancora | -0.55
    declassate a un quarto | 100 a -0.091R | 141 a -0.088R | -0.003 ±0.232 | non si vede ancora | +16.42
    paper esplorativo | 12 a +0.247R | 241 a -0.089R | +0.336 ±0.437 | non si vede ancora | 

== Cosa abbiamo capito
  - Note del 2026-10-04:
  - La stella polare è passata da −0,03R su 130 segnali (ops 0454) a +0,006R su 156, margine ±0,17 (ops 0474), per una giornata sola: il 3 ott 16 trade delle validate, 15 vinti, +0,869R a trade (ops 0479). Il numero oscilla intorno a zero dentro il margine: oggi la regola del 7 ott («motore ≤ 0 con almeno 80 segnali → la modifica va nel gate») non scatterebbe, ieri sì. Il verdetto del 7 ott può dipendere da un giorno buono o cattivo: per questo c'è la conferma del 14.
  - Entriamo un po' peggio del segnale: ingresso a +0,038R rispetto alla chiusura della candela del segnale, con 155 secondi di ritardo (mediane, dato D8 raccolto dal 1 ott; ops 0479). È circa metà dei costi stimati a trade (0,081R): non spiega le perdite da solo, ma pesa.
  - A 1 ora il gate passa il 2,2% delle prove (218 su 9.840, ops 0468) contro lo 0,12% a 15 minuti (25 su 20.667, ops 0470), ma le due quote NON si confrontano: la passata a 1 ora rivaluta soprattutto spec già note a 1 ora (259 su 328, riga ORIGINI di ops 0468), cioè coppie già passate, mentre il giro «solo urgenti» a 15 minuti è quasi tutto candidate nuove. Il «diciotto volte» scritto stamattina era soprattutto composizione (corretto alle 09:30). La domanda giusta, a parità di candidate, la fa G7 (sì del 4 ott).
  - Primo verdetto «contribuisce» nelle funzioni: i quasi-passaggi operati a un quarto (paper esplorativo) fanno +0,385R su 10 trade contro −0,065R delle validate, differenza +0,450 ±0,419 (ops 0465). È al limite del campione minimo (10) e il metro dice 100 trade; ma va nella stessa direzione di T2: oggi la scelta del gate non aggiunge un vantaggio misurabile.
  - T2 su 240 trade (ieri 207): a 1 ora i segnali vanno leggermente contro, −0,080 mosse tipiche, margine [−0,184; +0,013] (ops 0471). Ancora «nessun vantaggio misurabile», ma la prima ora è la più vicina a «peggio del caso».
  - USELESS e SUI a «0 su 7» non sono un difetto di oggi: tutti i 14 trade sono short, aperti fra il 21 e il 27 set (l'ultimo alle 11:15 UTC), e il motore non li riproduce nemmeno sui valori registrati dal paper (classe IGNOTO, ops 0483). È la firma del difetto della sessione oraria corretto il 27 set alle 19:40 UTC (J13: l'ora del processo al posto di quella della candela, fuori sessione era ammesso solo lo short). Sulle 18 coppie rigirate, tutti i 20 trade non riprodotti visibili sono di prima della correzione, e dopo la correzione nessun trade rigirato ha la regola che non scatta (7 abbinati, 1 col motore ancora dentro il trade prima; ops 0483). Quei 20 trade fanno −33,57 USDT, circa metà della perdita totale del paper (−62,59, ops 0466). Che le due spec usino la sessione è molto probabile ma non verificato.
  - R2: le 50 candidate casuali di R1 del 17 set, giudicate dal gate di OGGI sulle 72 monete operate, passano 0 volte su 3.600 (ops 0485). Lo 0 di R1 è vero: una candidata nuova a caso non passa quasi mai, nemmeno nel gate di produzione (R1 ha la sua prima promossa al 20 ago, 1 su 9.050 giudizi). Le 223 validate quindi non vengono da candidate «fortunate al primo colpo», ma dalla ricerca ripetuta giro dopo giro (mutazioni dei quasi-passaggi, rivalutazioni): è lì che il numero delle prove cresce senza essere contato.

== Cosa è cambiato nel sistema
  - 04/10 18:16 — Report mfe: colonna 0,8/1,6/2,4 solo misura nella tabella delle scale (domanda del proprietario)
  - 04/10 18:04 — R1 fermata dal proprietario (opzione c): il lancio del 5 ott fa solo la prova sul prezzo casuale, poi toglie il file attivo
  - 04/10 14:33 — CLAUDE.md: niente sigle del backlog col proprietario
  - 04/10 13:57 — G7: l'unita' usa lo stato del modulo che la lancia (R1 gira come __main__); R2 fatta, scelta R1b
  - 04/10 10:26 — USELESS e SUI trade per trade: residuo del difetto della sessione (prima del 27 set)
  - 04/10 09:21 — Referto settimanale del 4 ott
  - 04/10 09:13 — G7: il gate sul prezzo casuale a 1 ora, nel lancio di R1 dopo R2
  - 04/10 08:24 — Controllo del 4 ott: numeri, cosa abbiamo capito, proposta G7 (il gate sul prezzo casuale)

== Aspetta il tuo sì e prossime letture
  - Aspettano il tuo sì: niente.
  - In lavorazione: G7. Il gate sul prezzo casuale: quante strategie passa per caso, a 1 ora? — SÌ del proprietario il 4 ott; il primo lancio (4 ott) non ha fatto prove per un difetto mio, corretto: gira al lancio del 5 ott, 13:10; R2. Taratura di R1 a parità di candidate — FATTA il 4 ott: 0 passate su 3.600 → lo 0 di R1 è vero (ops 0485); la scelta del piano è in R1b; R1. Rigiocare il gate nel passato — FERMATA dal proprietario il 4 ott (opzione c, dopo R2): il lancio del 5 ott fa solo la prova sul prezzo casuale (G7) e poi toglie il file «attivo»; il gate torna a 8 giri al giorno. La scelta del gate si legge nel fuori campione del 7 e 14 ott; J2. «Cosa aspetta il sì» in dashboard, senza aggiornarlo a mano — in lavorazione (1 ott); D8. Raccolta dei dati mancanti (punto 4 del 1 ott) — ATTIVA dal riavvio del 1 ott 17:24 («[cattura]» nel log del bot); T2. La curva del vantaggio del segnale — FATTA il 2 ott: «nessun vantaggio misurabile» (ops 0437); la sezione resta nel report mfe e si rilegge col crescere dei trade
    data | cosa si legge | regola
    2026-10-07 | Fuori campione: il problema è il gate o il bot? (report portafoglio) | regole del 7 e 14 ott, diario del 30 set
    2026-10-10 | R1, il gate rigiocato nel passato (prima lettura completa, STIMA: dal 2 ott sulle sole monete operate, ~1/3 del lavoro, 2,5 ore al giorno) | regola R1, diario del 1 ott
    2026-10-10 | Varianti dai referti e ipotesi d'ingresso (J9, I4ter) | backlog archivio
    2026-10-14 | Fuori campione, seconda lettura | regole del 7 e 14 ott
    2026-10-15 | Gruppo di controllo: servono 3 conferme? (K3) | backlog archivio K3
    2026-10-18 | Conferma a maggioranza (J11), sessione oraria (J13), passata a 1 ora (C1) | backlog archivio

== Salute e costi
  - Semafori: sistema giallo, paper giallo.
  - Anomalia FRENO_GLOBALE: freno globale da deriva: PF 0,73 vs 2,01 atteso
  - Anomalia GATE_SFORA: il giro del gate e' durato 3 h 22 (piu' di 3 h)
  - Anomalia SENZA_PROMESSA: 121 validate su 235 senza promessa (last_pf)
  - Riavvii del bot nelle 24 ore: 0.
  - Letture Firestore nelle 24 ore: 7269 (quota gratuita 50.000).
  - Spesa AI di ieri (2026-10-04): 0.10 $ in 1 chiamate — ai-learning 0.10 $
```
