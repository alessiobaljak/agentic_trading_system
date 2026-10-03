# 0460-3ott-mattina-report-giornaliero.req

_eseguito: 2026-10-03 06:19 UTC_

**richiesta:** `report-giornaliero`
**eseguito:** `.venv/bin/python -m scripts.report_giornaliero --pubblica`
**esito:** codice 0 in 2.7s

```
[report] backlog: 26 voci in 7 gruppi, aspettano il si' 0 (commit 2363f87)
[firebase] connesso (Firestore + RTDB)
[report] backlog pubblicato: si
[report] report del 2026-10-02 pubblicato: si
REPORT GIORNALIERO del 2026-10-02 (versione 2363f87)

== In breve
  - Paper ieri: 23 trade, +3.48 USDT (-0.168R a trade). Ultimi 7 giorni -16.58 USDT (-0.116R); dal 27 set -0.085R netti a trade su 96.
  - Gate: Un giro e' in corso dalle 03/10 08:14; il precedente era finito alle 03/10 07:31: 22632 valutazioni, 44 passate, durato 1h56.
  - Niente aspetta il tuo sì.
  - Capito: T2: i segnali del paper non hanno un vantaggio misurabile sul caso. Il prezzo dopo 1, 4, 12 e 24 ore dall'ingresso non si distingue da ingressi a caso sulla stessa moneta e direzione, nelle 12 ore dopo (201 trade, 15 giornate; a 4 ore −0,001 mosse tipiche, margine ±0,13, cioè circa ±0,5%; ops 0437). Per la regola il lavoro sui take profit si ferma (T1 congelata): il problema è l'ingresso o il gate (R1).

== Il paper ieri
  - Ieri (2026-10-02): 23 trade delle validate, 12 vinti, +3.48 USDT, -0.168R netti a trade. Sul conto (esplorativi e chiusure esterne compresi): 23 trade, +3.48 USDT.
  - Equity 929.04 USDT (-7.10% dall'inizio del paper, il 2026-09-16).
  - Adesso 5 posizioni aperte, rischio aperto 0.65% del capitale, uPnL +4.40 USDT.
  - Ultimi 7 giorni sul conto: 4 in utile, 3 in perdita.
  - Confronto: BTC comprato il primo giorno +11.7%, noi -7.1%.
    periodo | trade | vinti | PnL USDT | R netto | R lordo | costi R
    ieri | 23 | 52% | +3.48 | -0.168R | -0.092R | +0.076R
    7 giorni | 149 | 58% | -16.58 | -0.116R | -0.031R | +0.085R
    dal 27 set | 96 | 60% | -3.75 | -0.085R | -0.007R | +0.077R
    tutto | 231 | 54% | -80.03 | -0.124R | -0.044R | +0.081R

== Come va il gate
  - Un giro e' in corso dalle 03/10 08:14; il precedente era finito alle 03/10 07:31: 22632 valutazioni, 44 passate, durato 1h56.
  - Validate 216 su 72 coin, copertura 36.0%; declassate 173.
  - Ultimi 7 giorni: 91 promosse, 0 rimosse.
  - Il cervello: varianti dai referti 0 create, 0 promosse; intorno 11 madri, 0 promosse.
  - Registro: 1527 coppie su un tetto di 3000.
  - Esplorative: 47 attive, poi validate 2, scartate 294.
  - Fuori campione (le validate guadagnano anche DOPO la scelta? ultimo report del 2026-10-03): Selezione: la promessa non regge dopo la validazione: motore -0.03R (margine ±0.18R per giornata) su 130 segnali. O il gate sceglie coppie buone solo nei giorni su cui le ha provate, o il mercato e' cambiato: da qui non si separano. Per la regola la prossima modifica va nel gate. Esecuzione: non si decide: sugli stessi segnali fanno quasi uguale (differenza +0.02R, margine ±0.11R per giornata). Si rilegge il 14 ott.
  - R1, il gate rigiocato nel passato: 2 date su 26, 400 unita' fatte.

== Cosa ci dicono i dati
  - Ipotesi nate dai referti (le prova il gate sulla storia): gen_fa304106: solo_long — short 4/4 persi (campione 4); gen_fa304106: solo_short — long 3/3 persi (campione 3); gen_fca11c08: conferma_trend — 6 perdite controtrend (campione 6)
  - Trailing in tutto: 56 prematuri e 55 protetti su 120 verdetti; proposta del paper: nessuna.
     | ieri | 7 giorni | tutto
    INGRESSI |  |  | 
    perdite «mai andate a favore» | 7/11 | 33/62 | 44/81
    latenza segnale → ingresso (s, mediana) | 158 | 155 | 155
    ingresso rispetto al segnale (mediana) | +0.035R | +0.031R | +0.031R
    USCITE E TRAILING |  |  | 
    perdite morte sotto il primo gradino | 4/11 | 29/62 | 37/81
    trailing prematuri / verdetti | 6/10 | 41/84 | 55/119
    trailing protetti / verdetti | 4/10 | 38/84 | 55/119
    arrivati al primo target | 2/23 | 13/149 | 23/231
    massimo a favore (mediana, R) | 0.77 | 0.82 | 0.82
    STOP LOSS |  |  | 
    chiusi a stop | 10/23 | 61/149 | 105/231
    stop seguiti da un rimbalzo (rumore) | 1/9 | 14/60 | 26/104
    massimo contro (mediana, R) | 0.67 | 0.78 | 0.78
    RISCHIO |  |  | 
    rischio effettivo per trade (mediana) | 0.13% | 0.14% | 0.14%
    leva media | 1.43x | 1.23x | 1.35x
    DIREZIONE |  |  | 
    long: trade e R netto | 14 a -0.180R | 75 a -0.226R | 104 a -0.217R
    short: trade e R netto | 9 a -0.149R | 74 a -0.004R | 127 a -0.046R

== Le funzioni servono?
  - Regola (scritta prima dei numeri): sotto 10 trade per gruppo «campione piccolo»; oltre 2 errori standard nel verso atteso «contribuisce», nel verso opposto «va contro»; altrimenti «non si vede ancora». USDT: quanto ha risparmiato (o tolto) la riduzione di size rispetto alla size piena.
  - Origine delle strategie nel paper: casuali 198 trade a -0.106R · intorno 1 trade a +0.292R
    funzione | toccati | altri | differenza | verdetto | USDT
    freno globale da deriva | 150 a -0.082R | 49 a -0.173R | +0.091 ±0.277 | non si vede ancora | +10.84
    panchina dei pesi | 1 a +0.435R | 198 a -0.107R | — | campione piccolo | -0.64
    pesi alti (size e leva in su) | 34 a -0.040R | 16 a -0.248R | +0.208 ±0.516 | non si vede ancora | 
    leva sopra 1x | 43 a -0.006R | 156 a -0.131R | +0.125 ±0.277 | non si vede ancora | 
    tilt di trend e sentiment | 45 a -0.107R | 105 a -0.071R | -0.036 ±0.306 | non si vede ancora | -1.14
    declassate a un quarto | 70 a -0.131R | 129 a -0.090R | -0.041 ±0.245 | non si vede ancora | +29.04
    paper esplorativo | 8 a +0.346R | 199 a -0.104R | — | campione piccolo | 

== Cosa abbiamo capito
  - Note del 2026-10-02:
  - T2: i segnali del paper non hanno un vantaggio misurabile sul caso. Il prezzo dopo 1, 4, 12 e 24 ore dall'ingresso non si distingue da ingressi a caso sulla stessa moneta e direzione, nelle 12 ore dopo (201 trade, 15 giornate; a 4 ore −0,001 mosse tipiche, margine ±0,13, cioè circa ±0,5%; ops 0437). Per la regola il lavoro sui take profit si ferma (T1 congelata): il problema è l'ingresso o il gate (R1).
  - Anteprima del fuori campione girata: dopo la scelta del gate il motore fa −0,03R a trade su 106 segnali, ±0,21 (ops 0429), ieri +0,06 su 89 (ops 0387). La regola del 7-14 ott («motore ≤ 0 con almeno 80 segnali → la prossima modifica va nel gate») oggi scatterebbe; il verdetto resta alla data.
  - Prima dei costi il paper dal 27 set è quasi a zero: +0,013R a trade su 81, costi 0,078R (ops 0420); e il modello dei costi è un po' ottimista rispetto a Binance: commissioni 0,08% contro 0,10%, ~0,012R a trade (C5).
  - Dal 27 set si perde soprattutto col mercato neutro: −0,317R su 39 trade, contro +0,357R su 25 a favore del trend (ops 0420; margine non stampato).

== Cosa è cambiato nel sistema
  - 02/10 21:13 — Affollamento nel report trades (posizioni nello stesso verso, ondate); idee AI con autopsia e varianti dai referti spente (decisione del proprietario)
  - 02/10 17:05 — diario: punto di verifica di R1 dopo 5 date (criterio scritto prima dei numeri)
  - 02/10 14:48 — diario: prima finestra di R1 (giro saltato, R1 lavora, 0 passate su 14.150 candidate)
  - 02/10 09:33 — R1 sulle sole monete operate (una lettura del registro, piano ristretto una volta); C5 approvata per dopo il 14 ott
  - 02/10 08:48 — Controllo del 2 ott: capito, diario, letture (R1 verso il 20 ott), report che taglia a fine parola, D8 attiva
  - 02/10 08:21 — T2: primo esito «nessun vantaggio misurabile» (ops 0437); T1 congelata dalla regola
  - 02/10 08:13 — backlog C5 e diario: costi per trade contro Binance (commissioni 0,08% contro 0,10%, funding per scadenza vera)
  - 02/10 08:13 — T2: curva del vantaggio del segnale nel report mfe (caso solo DOPO il segnale, punto dove la curva smette di salire); cache letta dal file che copre i giorni (non dai file corti di A5)
  - 02/10 07:42 — T2: regola della curva del vantaggio scritta prima dei numeri (sì del proprietario)
  - 02/10 07:30 — backlog: T2 (curva del vantaggio del segnale, aspetta il sì) e revisione di T1 su come costruire i TP
  - 02/10 07:14 — backlog T1: la misura dei TP delle posizioni aperte (ops 0419)
  - 02/10 07:12 — mfe: i TP delle posizioni aperte sono raggiungibili? distanza in % e quota storica (ingresso casuale, 96 candele, prima dello stop) dalla cache del gate in sola lettura

== Aspetta il tuo sì e prossime letture
  - Aspettano il tuo sì: niente.
  - In lavorazione: R1. Rigiocare il gate nel passato — SÌ del proprietario il 1 ott; dal 2 ott lavora AL POSTO del giro del gate delle 14:00 italiane (sì del 1 ott sera); J2. «Cosa aspetta il sì» in dashboard, senza aggiornarlo a mano — in lavorazione (1 ott); D8. Raccolta dei dati mancanti (punto 4 del 1 ott) — ATTIVA dal riavvio del 1 ott 17:24 («[cattura]» nel log del bot); T2. La curva del vantaggio del segnale — FATTA il 2 ott: «nessun vantaggio misurabile» (ops 0437); la sezione resta nel report mfe e si rilegge col crescere dei trade
    data | cosa si legge | regola
    2026-10-03 | Declassate contro attive (report trades, DECLASSATE) | regola del 3 ott, diario del 30 set
    2026-10-07 | Fuori campione: il problema è il gate o il bot? (report portafoglio) | regole del 7 e 14 ott, diario del 30 set
    2026-10-10 | R1, il gate rigiocato nel passato (prima lettura completa, STIMA: dal 2 ott sulle sole monete operate, ~1/3 del lavoro, 2,5 ore al giorno) | regola R1, diario del 1 ott
    2026-10-10 | Varianti dai referti e ipotesi d'ingresso (J9, I4ter) | backlog archivio
    2026-10-14 | Fuori campione, seconda lettura | regole del 7 e 14 ott
    2026-10-15 | Gruppo di controllo: servono 3 conferme? (K3) | backlog archivio K3

== Salute e costi
  - Semafori: sistema verde, paper giallo.
  - Anomalia FRENO_GLOBALE: freno globale da deriva: PF 0,72 vs 2,01 atteso
  - Anomalia SENZA_PROMESSA: 123 validate su 216 senza promessa (last_pf)
  - Riavvii del bot nelle 24 ore: 1.
  - Letture Firestore nelle 24 ore: 6899 (quota gratuita 50.000).
  - Spesa AI di ieri (2026-10-02): 1.86 $ in 29 chiamate — ai-hypotheses 1.37 $, ai-autopsia 0.49 $, ai-connettivita 0.00 $
```
