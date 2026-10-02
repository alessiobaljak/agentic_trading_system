# 0438-2ott-report-con-capito.req

_eseguito: 2026-10-02 06:49 UTC_

**richiesta:** `report-giornaliero`
**eseguito:** `.venv/bin/python -m scripts.report_giornaliero --pubblica`
**esito:** codice 0 in 2.7s

```
[report] backlog: 25 voci in 7 gruppi, aspettano il si' 1 (commit 2f51c15)
[firebase] connesso (Firestore + RTDB)
[report] backlog pubblicato: si
[report] report del 2026-10-01 pubblicato: si
REPORT GIORNALIERO del 2026-10-01 (versione 2f51c15)

== In breve
  - Paper ieri: 15 trade, -9.87 USDT (-0.448R a trade). Ultimi 7 giorni -35.93 USDT (-0.121R); dal 27 set -0.058R netti a trade su 73.
  - Gate: Un giro e' in corso dalle 02/10 08:48; il precedente era finito alle 02/10 07:50: 27104 valutazioni, 33 passate, durato 2h03.
  - Aspettano il tuo sì: 1.
  - Capito: T2: i segnali del paper non hanno un vantaggio misurabile sul caso. Il prezzo dopo 1, 4, 12 e 24 ore dall'ingresso non si distingue da ingressi a caso sulla stessa moneta e direzione, nelle 12 ore dopo (201 trade, 15 giornate; a 4 ore −0,001 mosse tipiche, margine ±0,13, cioè circa ±0,5%; ops 0437). Per la regola il lavoro sui take profit si ferma (T1 congelata): il problema è l'ingresso o il gate (R1).

== Il paper ieri
  - Ieri (2026-10-01): 15 trade delle validate, 6 vinti, -9.87 USDT, -0.448R netti a trade. Sul conto (esplorativi e chiusure esterne compresi): 16 trade, -9.57 USDT.
  - Equity 922.78 USDT (-7.72% dall'inizio del paper, il 2026-09-16).
  - Adesso 4 posizioni aperte, rischio aperto 0.83% del capitale, uPnL -0.83 USDT.
  - Ultimi 7 giorni sul conto: 3 in utile, 4 in perdita.
  - Confronto: BTC comprato il primo giorno +13.5%, noi -7.7%.
    periodo | trade | vinti | PnL USDT | R netto | R lordo | costi R
    ieri | 15 | 40% | -9.87 | -0.448R | -0.368R | +0.080R
    7 giorni | 155 | 59% | -35.93 | -0.121R | -0.040R | +0.081R
    dal 27 set | 73 | 63% | -7.23 | -0.058R | +0.019R | +0.078R
    tutto | 208 | 54% | -83.51 | -0.118R | -0.037R | +0.081R

== Come va il gate
  - Un giro e' in corso dalle 02/10 08:48; il precedente era finito alle 02/10 07:50: 27104 valutazioni, 33 passate, durato 2h03.
  - Validate 212 su 71 coin, copertura 35.5%; declassate 163.
  - Ultimi 7 giorni: 110 promosse, 0 rimosse.
  - Il cervello: varianti dai referti 3 create, 0 promosse; intorno 7 madri, 0 promosse.
  - Registro: 1421 coppie su un tetto di 3000.
  - Esplorative: 48 attive, poi validate 0, scartate 242.
  - Fuori campione (le validate guadagnano anche DOPO la scelta? ultimo report del 2026-10-02): Selezione: la promessa non regge dopo la validazione: motore -0.03R (margine ±0.21R per giornata) su 106 segnali. O il gate sceglie coppie buone solo nei giorni su cui le ha provate, o il mercato e' cambiato: da qui non si separano. Per la regola la prossima modifica va nel gate. Esecuzione: non si decide: sugli stessi segnali fanno quasi uguale (differenza +0.03R, margine ±0.13R per giornata). Si rilegge il 14 ott.
  - R1, il gate rigiocato nel passato: 0 date su 26, 85 unita' fatte.

== Cosa ci dicono i dati
  - Ipotesi nate dai referti (le prova il gate sulla storia): gen_fa304106: solo_long — short 4/4 persi (campione 4); gen_fa304106: solo_short — long 3/3 persi (campione 3); gen_fca11c08: conferma_trend — 6 perdite controtrend (campione 6)
  - Trailing in tutto: 49 prematuri e 52 protetti su 110 verdetti; proposta del paper: nessuna.
     | ieri | 7 giorni | tutto
    INGRESSI |  |  | 
    perdite «mai andate a favore» | 4/9 | 33/64 | 37/70
    latenza segnale → ingresso (s, mediana) | 155 | 154 | 154
    ingresso rispetto al segnale (mediana) | -0.103R | -0.103R | -0.103R
    USCITE E TRAILING |  |  | 
    perdite morte sotto il primo gradino | 5/9 | 31/64 | 33/70
    trailing prematuri / verdetti | 1/5 | 39/89 | 48/108
    trailing protetti / verdetti | 4/5 | 42/89 | 51/108
    arrivati al primo target | 0/15 | 12/155 | 21/208
    massimo a favore (mediana, R) | 0.49 | 0.84 | 0.84
    STOP LOSS |  |  | 
    chiusi a stop | 9/15 | 64/155 | 95/208
    stop seguiti da un rimbalzo (rumore) | 1/8 | 15/63 | 25/94
    massimo contro (mediana, R) | 0.96 | 0.80 | 0.80
    RISCHIO |  |  | 
    rischio effettivo per trade (mediana) | 0.13% | 0.14% | 0.14%
    leva media | 1.27x | 1.19x | 1.34x
    DIREZIONE |  |  | 
    long: trade e R netto | 8 a -0.460R | 66 a -0.194R | 90 a -0.224R
    short: trade e R netto | 7 a -0.435R | 89 a -0.067R | 118 a -0.036R

== Le funzioni servono?
  - Regola (scritta prima dei numeri): sotto 10 trade per gruppo «campione piccolo»; oltre 2 errori standard nel verso atteso «contribuisce», nel verso opposto «va contro»; altrimenti «non si vede ancora». USDT: quanto ha risparmiato (o tolto) la riduzione di size rispetto alla size piena.
  - Origine delle strategie nel paper: casuali 177 trade a -0.119R
    funzione | toccati | altri | differenza | verdetto | USDT
    freno globale da deriva | 128 a -0.098R | 49 a -0.173R | +0.075 ±0.284 | non si vede ancora | +8.04
    panchina dei pesi | 1 a +0.435R | 176 a -0.122R | — | campione piccolo | -0.64
    pesi alti (size e leva in su) | 25 a -0.048R | 16 a -0.248R | +0.200 ±0.548 | non si vede ancora | 
    leva sopra 1x | 34 a -0.003R | 143 a -0.146R | +0.143 ±0.308 | non si vede ancora | 
    tilt di trend e sentiment | 37 a -0.118R | 91 a -0.090R | -0.028 ±0.339 | non si vede ancora | -1.72
    declassate a un quarto | 52 a -0.127R | 125 a -0.115R | -0.012 ±0.273 | non si vede ancora | +20.64
    paper esplorativo | 8 a +0.346R | 177 a -0.119R | — | campione piccolo | 

== Cosa abbiamo capito
  - Note del 2026-10-02:
  - T2: i segnali del paper non hanno un vantaggio misurabile sul caso. Il prezzo dopo 1, 4, 12 e 24 ore dall'ingresso non si distingue da ingressi a caso sulla stessa moneta e direzione, nelle 12 ore dopo (201 trade, 15 giornate; a 4 ore −0,001 mosse tipiche, margine ±0,13, cioè circa ±0,5%; ops 0437). Per la regola il lavoro sui take profit si ferma (T1 congelata): il problema è l'ingresso o il gate (R1).
  - Anteprima del fuori campione girata: dopo la scelta del gate il motore fa −0,03R a trade su 106 segnali, ±0,21 (ops 0429), ieri +0,06 su 89 (ops 0387). La regola del 7-14 ott («motore ≤ 0 con almeno 80 segnali → la prossima modifica va nel gate») oggi scatterebbe; il verdetto resta alla data.
  - Prima dei costi il paper dal 27 set è quasi a zero: +0,013R a trade su 81, costi 0,078R (ops 0420); e il modello dei costi è un po' ottimista rispetto a Binance: commissioni 0,08% contro 0,10%, ~0,012R a trade (C5).
  - Dal 27 set si perde soprattutto col mercato neutro: −0,317R su 39 trade, contro +0,357R su 25 a favore del trend (ops 0420; margine non stampato).

== Cosa è cambiato nel sistema
  - 02/10 08:48 — Controllo del 2 ott: capito, diario, letture (R1 verso il 20 ott), report che taglia a fine parola, D8 attiva
  - 02/10 08:21 — T2: primo esito «nessun vantaggio misurabile» (ops 0437); T1 congelata dalla regola
  - 02/10 08:13 — backlog C5 e diario: costi per trade contro Binance (commissioni 0,08% contro 0,10%, funding per scadenza vera)
  - 02/10 08:13 — T2: curva del vantaggio del segnale nel report mfe (caso solo DOPO il segnale, punto dove la curva smette di salire); cache letta dal file che copre i giorni (non dai file corti di A5)
  - 02/10 07:42 — T2: regola della curva del vantaggio scritta prima dei numeri (sì del proprietario)
  - 02/10 07:30 — backlog: T2 (curva del vantaggio del segnale, aspetta il sì) e revisione di T1 su come costruire i TP
  - 02/10 07:14 — backlog T1: la misura dei TP delle posizioni aperte (ops 0419)
  - 02/10 07:12 — mfe: i TP delle posizioni aperte sono raggiungibili? distanza in % e quota storica (ingresso casuale, 96 candele, prima dello stop) dalla cache del gate in sola lettura
  - 02/10 07:01 — backlog T1: i take profit non si adattano al singolo trade (verifica del 2 ott)
  - 01/10 19:54 — R1 al posto del giro del gate delle 12 UTC finché R1 è attivo (sì del proprietario); R1 conta il giro dopo e aspetta fino a 8 ore
  - 01/10 18:13 — dashboard: il report non andava in errore con le righe salvate come {valori} (Firestore non accetta liste annidate); vista separata dalla lettura
  - 01/10 17:26 — report: col giro del gate in corso dice «in corso» e mostra i numeri del giro precedente

== Aspetta il tuo sì e prossime letture
  - Aspettano il tuo sì: C5. Costi allineati a quelli veri di Binance (verifica del 2 ott, richiesta del proprietario)
  - In lavorazione: R1. Rigiocare il gate nel passato — SÌ del proprietario il 1 ott; dal 2 ott lavora AL POSTO del giro del gate delle 14:00 italiane (sì del 1 ott sera); J2. «Cosa aspetta il sì» in dashboard, senza aggiornarlo a mano — in lavorazione (1 ott); D8. Raccolta dei dati mancanti (punto 4 del 1 ott) — ATTIVA dal riavvio del 1 ott 17:24 («[cattura]» nel log del bot); T2. La curva del vantaggio del segnale — FATTA il 2 ott: «nessun vantaggio misurabile» (ops 0437); la sezione resta nel report mfe e si rilegge col crescere dei trade
    data | cosa si legge | regola
    2026-10-03 | Declassate contro attive (report trades, DECLASSATE) | regola del 3 ott, diario del 30 set
    2026-10-07 | Fuori campione: il problema è il gate o il bot? (report portafoglio) | regole del 7 e 14 ott, diario del 30 set
    2026-10-10 | Varianti dai referti e ipotesi d'ingresso (J9, I4ter) | backlog archivio
    2026-10-14 | Fuori campione, seconda lettura | regole del 7 e 14 ott
    2026-10-15 | Gruppo di controllo: servono 3 conferme? (K3) | backlog archivio K3
    2026-10-18 | Conferma a maggioranza (J11), sessione oraria (J13), passata a 1 ora (C1) | backlog archivio

== Salute e costi
  - Semafori: sistema verde, paper giallo.
  - Anomalia FRENO_GLOBALE: freno globale da deriva: PF 0,69 vs 2,03 atteso
  - Anomalia SENZA_PROMESSA: 123 validate su 212 senza promessa (last_pf)
  - Riavvii del bot nelle 24 ore: 2.
  - Letture Firestore nelle 24 ore: 365 (quota gratuita 50.000).
  - Spesa AI di ieri (2026-10-01): 2.07 $ in 31 chiamate — ai-hypotheses 1.53 $, ai-autopsia 0.55 $
```
