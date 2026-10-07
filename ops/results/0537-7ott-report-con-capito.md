# 0537-7ott-report-con-capito.req

_eseguito: 2026-10-07 06:26 UTC_

**richiesta:** `report-giornaliero`
**eseguito:** `.venv/bin/python -m scripts.report_giornaliero --pubblica`
**esito:** codice 0 in 3.8s

```
[report] backlog: 29 voci in 7 gruppi, aspettano il si' 0 (commit b593dfc)
[firebase] connesso (Firestore + RTDB)
[report] backlog pubblicato: si
[report] report del 2026-10-06 pubblicato: si
REPORT GIORNALIERO del 2026-10-06 (versione b593dfc)

== In breve
  - Paper ieri: 25 trade, -7.80 USDT (-0.303R a trade). Ultimi 7 giorni -13.59 USDT (-0.127R); dal 27 set -0.074R netti a trade su 180.
  - Gate: Un giro e' in corso dalle 07/10 07:06; il precedente era finito alle 07/10 06:51: 45069 valutazioni, 456 passate, durato 3h21.
  - Niente aspetta il tuo sì.
  - Capito: Il numero guida resta sotto zero mentre il margine si stringe: −0,04R su 202 segnali ±0,16 (ops 0517; il 3 ott −0,03 su 130 ±0,18). La lettura ufficiale è domani: con questi numeri la regola («motore ≤ 0 con almeno 80 segnali») scatterebbe, e la lettura stampata lo dice già. Non è più un'oscillazione: in quattro giorni non è mai andato oltre +0,006.

== Il paper ieri
  - Ieri (2026-10-06): 25 trade delle validate, 13 vinti, -7.80 USDT, -0.303R netti a trade. Sul conto (esplorativi e chiusure esterne compresi): 25 trade, -7.80 USDT.
  - Equity 912.77 USDT (-8.72% dall'inizio del paper, il 2026-09-16).
  - Adesso 13 posizioni aperte, rischio aperto 2.05% del capitale, uPnL -0.89 USDT.
  - Ultimi 7 giorni sul conto: 2 in utile, 5 in perdita.
  - Confronto: BTC comprato il primo giorno +11.1%, noi -8.7%.
    periodo | trade | vinti | PnL USDT | R netto | R lordo | costi R
    ieri | 25 | 52% | -7.80 | -0.303R | -0.177R | +0.126R
    7 giorni | 136 | 57% | -13.59 | -0.127R | -0.024R | +0.103R
    dal 27 set | 180 | 60% | -8.76 | -0.074R | +0.023R | +0.097R
    tutto | 315 | 56% | -85.04 | -0.105R | -0.013R | +0.092R

== Come va il gate
  - Un giro e' in corso dalle 07/10 07:06; il precedente era finito alle 07/10 06:51: 45069 valutazioni, 456 passate, durato 3h21.
  - Validate 279 (+22 nel giro) su 84 coin, copertura 42.0%; declassate 182.
  - Ultimi 7 giorni: 84 promosse, 0 rimosse.
  - Il cervello: varianti dai referti 0 create, 0 promosse; intorno 40 madri, 2 promosse.
  - Registro: 1900 coppie su un tetto di 3000.
  - Esplorative: 36 attive, poi validate 4, scartate 442.
  - Fuori campione (le validate guadagnano anche DOPO la scelta? ultimo report del 2026-10-07): Selezione: la promessa non regge dopo la validazione: motore -0.05R (margine ±0.14R per giornata) su 230 segnali. O il gate sceglie coppie buone solo nei giorni su cui le ha provate, o il mercato e' cambiato: da qui non si separano. Per la regola la prossima modifica va nel gate. Esecuzione: non si decide: sugli stessi segnali fanno quasi uguale (differenza +0.05R, margine ±0.07R per giornata). Si rilegge il 14 ott.
  - R1, il gate rigiocato nel passato: 8 date su 26, 597 unita' fatte.

== Cosa ci dicono i dati
  - Ipotesi nate dai referti (le prova il gate sulla storia): gen_8b91ba18: scala_stretta — 3 perdite sotto il primo gradino (mfe mediana 0.62 R) (campione 3); gen_bf2be656: scala_stretta — 3 perdite sotto il primo gradino (mfe mediana 0.42 R) (campione 3); gen_bf2be656: solo_short — long 3/3 persi (campione 3); gen_e59ad90b: conferma_trend — 3 perdite controtrend (campione 3); gen_fa304106: conferma_trend — 4 perdite mai andate a favore (classe ingresso) e 0 vinti su 10 (campione 4)
  - Trailing in tutto: 79 prematuri e 77 protetti su 171 verdetti; proposta del paper: nessuna.
     | ieri | 7 giorni | tutto
    INGRESSI |  |  | 
    perdite «mai andate a favore» | 7/12 | 28/59 | 59/115
    latenza segnale → ingresso (s, mediana) | 179 | 166 | 161
    ingresso rispetto al segnale (mediana) | +0.028R | +0.028R | +0.028R
    USCITE E TRAILING |  |  | 
    perdite morte sotto il primo gradino | 5/12 | 31/59 | 56/115
    trailing prematuri / verdetti | 4/13 | 36/73 | 77/168
    trailing protetti / verdetti | 9/13 | 31/73 | 76/168
    arrivati al primo target | 1/25 | 11/136 | 32/315
    massimo a favore (mediana, R) | 0.55 | 0.82 | 0.84
    STOP LOSS |  |  | 
    chiusi a stop | 12/25 | 57/136 | 138/315
    stop seguiti da un rimbalzo (rumore) | 5/12 | 12/57 | 36/138
    massimo contro (mediana, R) | 0.86 | 0.73 | 0.71
    RISCHIO |  |  | 
    rischio effettivo per trade (mediana) | 0.11% | 0.13% | 0.13%
    leva media | 1.32x | 1.33x | 1.35x
    DIREZIONE |  |  | 
    long: trade e R netto | 18 a -0.238R | 76 a -0.112R | 149 a -0.154R
    short: trade e R netto | 7 a -0.470R | 60 a -0.145R | 166 a -0.059R

== Le funzioni servono?
  - Regola (scritta prima dei numeri): sotto 10 trade per gruppo «campione piccolo»; oltre 2 errori standard nel verso atteso «contribuisce», nel verso opposto «va contro»; altrimenti «non si vede ancora». USDT: quanto ha risparmiato (o tolto) la riduzione di size rispetto alla size piena.
  - Origine delle strategie nel paper: ai 5 trade a -0.068R · casuali 285 trade a -0.110R · intorno 3 trade a -0.669R
    funzione | toccati | altri | differenza | verdetto | USDT
    freno globale da deriva | 244 a -0.103R | 49 a -0.173R | +0.070 ±0.267 | non si vede ancora | +19.38
    panchina dei pesi | 2 a -0.304R | 291 a -0.114R | — | campione piccolo | -0.07
    pesi alti (size e leva in su) | 68 a -0.131R | 27 a -0.196R | +0.065 ±0.459 | non si vede ancora | 
    leva sopra 1x | 76 a -0.089R | 217 a -0.124R | +0.035 ±0.244 | non si vede ancora | 
    tilt di trend e sentiment | 78 a -0.129R | 166 a -0.091R | -0.038 ±0.247 | non si vede ancora | +0.51
    declassate a un quarto | 139 a -0.129R | 154 a -0.103R | -0.026 ±0.210 | non si vede ancora | +37.52
    paper esplorativo | 13 a +0.146R | 293 a -0.115R | +0.261 ±0.449 | non si vede ancora | 

== Cosa abbiamo capito
  - Note del 2026-10-06:
  - Il numero guida resta sotto zero mentre il margine si stringe: −0,04R su 202 segnali ±0,16 (ops 0517; il 3 ott −0,03 su 130 ±0,18). La lettura ufficiale è domani: con questi numeri la regola («motore ≤ 0 con almeno 80 segnali») scatterebbe, e la lettura stampata lo dice già. Non è più un'oscillazione: in quattro giorni non è mai andato oltre +0,006.
  - Il registro cresce da solo mentre il paper resta fermo: 257 validate su 82 monete (ops 0511), erano 235 ieri e 223 sabato. La spinta è l'«intorno» delle quasi-promosse: 204 figlie nel giro della notte, 3 promosse. Spazio nel registro ~758 coppie: di questo passo (stima: ~100 coppie al giorno fra validate e in attesa) l'allarme dei 400 arriva fra 3-4 giorni, non settimane.
  - Dal 27 set il lordo è ancora positivo (+0,037R su 162) e i costi (0,093R) lo rovesciano in −0,057R (ops 0508): è la terza lettura di fila con lo stesso segno. Sui long si perde (−0,110R su 85), sugli short si pareggia (+0,002 su 77); il regime neutro resta il peggiore (−0,182R su 93).
  - Nei 7 giorni il trailing ha chiuso troppo presto 38 volte e ha protetto 26 (ops 0521): seconda settimana con i prematuri sopra i protetti. La regola del referto settimanale (due settimane di fila → proporre di allentare il keep) si applica domenica, non prima.
  - Le letture di Firebase salgono: 8.444 nelle 24 ore (ops 0512; il 4 ott 7.763), quasi tutte dai rifiutati (4.843). Lontano dalla quota (50.000), ma la tendenza va tenuta d'occhio.
  - Lettura ufficiale del 7 ott, selezione: «la prossima modifica va nel gate». Il motore, dopo la validazione, fa −0,05R a trade su 230 segnali, margine ±0,14R per giornata (ops 0532): la regola scritta il 30 set («almeno 80 segnali e motore ≤ 0») scatta. Esecuzione: non si decide (stessi 200 segnali: paper −0,09R, motore −0,04R, differenza +0,05 ±0,07). È la conferma formale di quello che le tre prove avevano già detto: il problema non è il bot, è come nascono le strategie. La direzione presa (il protocollo di ricerca) è quella che la regola indica. Seconda lettura il 14 ott.
  - Il registro del gate si riempie più in fretta del previsto: spazio per ~603 coppie (ops 0526; ieri 758, sabato 1.021). Di questo passo l'allarme dei 400 scatta fra 1-2 giorni: 456 passate nell'ultimo giro, 238 figlie dell'intorno. Il gate produce più coppie di quante il registro possa tenere, mentre il paper peggiora (−88,03 USDT, ops 0524).
  - Tredici posizioni aperte insieme stamattina (ops 0535; massimo precedente 12) e 48 rifiuti «posizione già aperta» in 24 ore (ops 0533): i segnali abbondano, la qualità no. Dal 27 set il lordo è a +0,007R a trade (quasi zero) e i costi 0,098R (ops 0523): il paper perde esattamente i costi.
  - Sui long si perde (−0,163R su 112 dal 27 set), sugli short si pareggia (+0,004 su 85) (ops 0523): quarta lettura di fila con lo stesso segno. Non è una regola (uscite e ingressi non si toccano), ma è una cosa capita: le strategie long del gate sono peggio delle short in questo mercato.
  - L'universo «al 31 dicembre 2023» è molto più piccolo di quello che il gate usa oggi: su 895 contratti perpetui in USDT con dati, solo 100 hanno due anni di storia, dati fino a fine 2023 e almeno 20 milioni di USDT al giorno nel 2023 (research/universo/conteggi.json, branch di coordinamento). 759 sono nati dopo il 2022. Il gate lavora sulle prime 200 per volume di oggi: in gran parte monete senza storia abbastanza lunga per un giudizio.
  - Il bias di sopravvivenza è misurato, non solo dichiarato: 24 delle 100 idonee oggi non sono più negoziate, e 2 stanno fra le 20 di campagna (MATIC, FTM). Con un universo «di oggi» quelle 24 sparirebbero e il periodo chiuso sembrerebbe migliore di quello che era.

== Cosa è cambiato nel sistema
  - 07/10 08:25 — Controllo del 7 ott: lettura ufficiale del fuori campione (la prossima modifica va nel gate), numeri e cosa abbiamo capito
  - 07/10 07:41 — Diario, backlog e capito: Passo 0 approvato e Passo 1 fatto (allo STOP)
  - 07/10 07:40 — Passo 1: le schede delle 20 monete di campagna (solo informazioni al 2023-12-31)
  - 07/10 07:37 — Passo 1: selezione corretta dopo la revisione avversaria (scheda senza indizi sul delisting, fine dati al giorno, nessun filtro non dichiarato, sospette ridenominazioni, indice senza troncamenti silenziosi)
  - 07/10 07:11 — Passo 1: test da capo a fondo della selezione su un mondo finto (senza rete)
  - 07/10 07:10 — Passo 0 congelato (ok del proprietario, 7 ott); Passo 1: modulo della selezione delle monete con i suoi test
  - 06/10 23:07 — Caricatore dati: ripiego per la lista dei contratti, verifica del checksum remoto, elenco dell'archivio (solo coordinamento)
  - 06/10 23:02 — Passo 0 del protocollo di ricerca: motore, caricatore dati, statistica, guardiano, fatti dal bot e parametri (bozza allo STOP)
  - 06/10 21:51 — Protocollo di ricerca 4.3 approvato: file operativo, eccezione per i branch research/, Passo 0 in corso
  - 06/10 08:23 — Controllo del 6 ott: numeri e cosa abbiamo capito; il Passo 0 aspetta ancora il si'

== Aspetta il tuo sì e prossime letture
  - Aspettano il tuo sì: niente.
  - In lavorazione: P0. Il protocollo di ricerca per moneta — Passo 0 FATTO e APPROVATO il 7 ott (parametri congelati); Passo 1 FATTO il 7 ott (20 monete di campagna sul branch research/coordinamento, schede sul principale), allo STOP: aspetta la conferma della lista; poi Passo 2 (prova di processo su BTC, ETH, SOL); G7. Il gate sul prezzo casuale: quante strategie passa per caso, a 1 ora? — FATTA il 5 ott: candele vere 8 passate su 7.200 (0,11%), rimescolate 16 su 7.200 (0,22%), rapporto 2,0 → per la regola NON SI SA (meno di 10 passate sul vero), ops 0506; R2. Taratura di R1 a parità di candidate — FATTA il 4 ott: 0 passate su 3.600 → lo 0 di R1 è vero (ops 0485); la scelta del piano è in R1b; R1. Rigiocare il gate nel passato — FERMATA dal proprietario il 4 ott (opzione c, dopo R2): il lancio del 5 ott fa solo la prova sul prezzo casuale (G7) e poi toglie il file «attivo»; il gate torna a 8 giri al giorno. La scelta del gate si legge nel fuori campione del 7 e 14 ott; J2. «Cosa aspetta il sì» in dashboard, senza aggiornarlo a mano — in lavorazione (1 ott); D8. Raccolta dei dati mancanti (punto 4 del 1 ott) — ATTIVA dal riavvio del 1 ott 17:24 («[cattura]» nel log del bot); T2. La curva del vantaggio del segnale — FATTA il 2 ott: «nessun vantaggio misurabile» (ops 0437); la sezione resta nel report mfe e si rilegge col crescere dei trade
    data | cosa si legge | regola
    2026-10-07 | Fuori campione: il problema è il gate o il bot? — LETTA il 7 ott: SELEZIONE → «la prossima modifica va nel gate» (motore dopo la validazione −0,05R su 230 segnali, margine ±0,14R per giornata, ≥ 80 segnali e ≤ 0); ESECUZIONE → non si decide (stessi segnali: paper −0,09R, motore −0,04R, differenza +0,05 ±0,07 per giornata, dentro il margine); ops 0532. Si conferma il 14 ott | regole del 7 e 14 ott, diario del 30 set
    2026-10-10 | R1, il gate rigiocato nel passato (prima lettura completa, STIMA: dal 2 ott sulle sole monete operate, ~1/3 del lavoro, 2,5 ore al giorno) | regola R1, diario del 1 ott
    2026-10-10 | Varianti dai referti e ipotesi d'ingresso (J9, I4ter) | backlog archivio
    2026-10-14 | Fuori campione, seconda lettura | regole del 7 e 14 ott
    2026-10-15 | Gruppo di controllo: servono 3 conferme? (K3) | backlog archivio K3
    2026-10-18 | Conferma a maggioranza (J11), sessione oraria (J13), passata a 1 ora (C1) | backlog archivio

== Salute e costi
  - Semafori: sistema giallo, paper giallo.
  - Anomalia FRENO_GLOBALE: freno globale da deriva: PF 0,73 vs 2,02 atteso
  - Anomalia GATE_SFORA: il giro del gate e' durato 3 h 21 (piu' di 3 h)
  - Anomalia SENZA_PROMESSA: 118 validate su 279 senza promessa (last_pf)
  - Riavvii del bot nelle 24 ore: 0.
  - Letture Firestore nelle 24 ore: 8857 (quota gratuita 50.000).
  - Spesa AI di ieri (2026-10-06): nessun dato.
```
