# 0417-1ott-report-testo.req

_eseguito: 2026-10-01 15:25 UTC_

**richiesta:** `report-giornaliero`
**eseguito:** `.venv/bin/python -m scripts.report_giornaliero --pubblica`
**esito:** codice 0 in 2.7s

```
[report] backlog: 22 voci in 7 gruppi, aspettano il si' 0 (commit f393c3f)
[firebase] connesso (Firestore + RTDB)
[report] backlog pubblicato: si
[report] report del 2026-09-30 pubblicato: si
REPORT GIORNALIERO del 2026-09-30 (versione f393c3f)

== In breve
  - Paper ieri: 14 trade, -2.18 USDT (-0.109R a trade). Ultimi 7 giorni -24.89 USDT (-0.079R); dal 27 set +0.043R netti a trade su 58.
  - Gate: Ultimo giro: in_corso (solo urgenti), finito alle 01/10 16:38, durato 2h13: 28798 valutazioni, 52 passate.
  - Niente aspetta il tuo sì.
  - Capito: Il bot esegue quasi come il motore: sugli stessi 79 segnali la differenza è +0,05R con margine ±0,16R (ops 0387). Un difetto grosso di esecuzione è quasi escluso; il problema sembra prima del bot.

== Il paper ieri
  - Ieri (2026-09-30): 14 trade delle validate, 9 vinti, -2.18 USDT, -0.109R netti a trade. Sul conto (esplorativi e chiusure esterne compresi): 14 trade, -2.18 USDT.
  - Equity 921.96 USDT (-7.80% dall'inizio del paper, il 2026-09-16).
  - Adesso 1 posizioni aperte, rischio aperto 0.16% del capitale, uPnL -0.26 USDT.
  - Ultimi 7 giorni sul conto: 2 in utile, 5 in perdita.
  - Confronto: BTC comprato il primo giorno +11.1%, noi -7.8%.
    periodo | trade | vinti | PnL USDT | R netto | R lordo | costi R
    ieri | 14 | 64% | -2.18 | -0.109R | -0.032R | +0.077R
    7 giorni | 151 | 61% | -24.89 | -0.079R | +0.003R | +0.082R
    dal 27 set | 58 | 69% | +2.65 | +0.043R | +0.120R | +0.077R
    tutto | 193 | 55% | -73.64 | -0.086R | -0.005R | +0.081R

== Come va il gate
  - Ultimo giro: in_corso (solo urgenti), finito alle 01/10 16:38, durato 2h13: 28798 valutazioni, 52 passate.
  - Validate 208 su 71 coin, copertura 35.5%; declassate 162.
  - Ultimi 7 giorni: 106 promosse, 0 rimosse.
  - Il cervello: varianti dai referti 3 create, 0 promosse; intorno 3 madri, 0 promosse.
  - Registro: 1328 coppie su un tetto di 3000.
  - Esplorative: 46 attive, poi validate 0, scartate 205.
  - Fuori campione (le validate guadagnano anche DOPO la scelta? ultimo report del 2026-10-01): Selezione: il motore guadagna ancora dopo la validazione (+0.06R, margine ±0.18R per giornata, 89 segnali): nessun verdetto contro il gate. Esecuzione: non si decide: la differenza sta dentro il margine (differenza +0.05R, margine ±0.16R per giornata); servono circa 766 accoppiati (oggi 79) se resta questa. Si rilegge il 14 ott.

== Cosa ci dicono i dati
  - Ipotesi nate dai referti (le prova il gate sulla storia): gen_fa304106: solo_long — short 4/4 persi (campione 4); gen_fa304106: solo_short — long 3/3 persi (campione 3); gen_fca11c08: conferma_trend — 6 perdite controtrend (campione 6)
  - Trailing in tutto: 47 prematuri e 49 protetti su 105 verdetti; proposta del paper: nessuna.
     | ieri | 7 giorni | tutto
    INGRESSI |  |  | 
    perdite «mai andate a favore» | 2/5 | 32/59 | 33/61
    latenza segnale → ingresso (s, mediana) | 159 | 154 | 154
    ingresso rispetto al segnale (mediana) | non ancora raccolto | non ancora raccolto | non ancora raccolto
    USCITE E TRAILING |  |  | 
    perdite morte sotto il primo gradino | 3/5 | 27/59 | 28/61
    trailing prematuri / verdetti | 6/8 | 41/91 | 47/103
    trailing protetti / verdetti | 2/8 | 41/91 | 47/103
    arrivati al primo target | 0/14 | 13/151 | 21/193
    massimo a favore (mediana, R) | 0.83 | 0.86 | 0.85
    STOP LOSS |  |  | 
    chiusi a stop | 5/14 | 59/151 | 86/193
    stop seguiti da un rimbalzo (rumore) | 0/4 | 14/58 | 24/85
    massimo contro (mediana, R) | 0.81 | 0.69 | 0.69
    RISCHIO |  |  | 
    rischio effettivo per trade (mediana) | 0.13% | 0.14% | 0.14%
    leva media | 1.14x | 1.17x | 1.35x
    DIREZIONE |  |  | 
    long: trade e R netto | 9 a -0.101R | 64 a -0.169R | 82 a -0.195R
    short: trade e R netto | 5 a -0.124R | 87 a -0.013R | 111 a -0.005R

== Le funzioni servono?
  - Regola (scritta prima dei numeri): sotto 10 trade per gruppo «campione piccolo»; oltre 2 errori standard nel verso atteso «contribuisce», nel verso opposto «va contro»; altrimenti «non si vede ancora». USDT: quanto ha risparmiato (o tolto) la riduzione di size rispetto alla size piena.
  - Origine delle strategie nel paper: casuali 167 trade a -0.115R
    funzione | toccati | altri | differenza | verdetto | USDT
    freno globale da deriva | 118 a -0.091R | 49 a -0.173R | +0.082 ±0.286 | non si vede ancora | +12.80
    panchina dei pesi | 1 a +0.435R | 166 a -0.118R | — | campione piccolo | -0.64
    pesi alti (size e leva in su) | 22 a -0.028R | 15 a -0.326R | +0.298 ±0.567 | non si vede ancora | 
    leva sopra 1x | 31 a +0.015R | 136 a -0.145R | +0.160 ±0.324 | non si vede ancora | 
    tilt di trend e sentiment | 33 a -0.080R | 85 a -0.096R | +0.016 ±0.343 | non si vede ancora | -0.65
    declassate a un quarto | 47 a -0.096R | 120 a -0.123R | +0.027 ±0.280 | non si vede ancora | +19.93
    paper esplorativo | 8 a +0.346R | 167 a -0.115R | — | campione piccolo | 

== Cosa abbiamo capito
  - Note del 2026-10-01:
  - Il bot esegue quasi come il motore: sugli stessi 79 segnali la differenza è +0,05R con margine ±0,16R (ops 0387). Un difetto grosso di esecuzione è quasi escluso; il problema sembra prima del bot.
  - Dopo la scelta del gate le validate rendono poco anche nel motore: +0,06R a trade su 89 segnali, ±0,18 (ops 0387), contro le +0,18 promesse. È un indizio, non ancora un verdetto (letture 7-14 ott).
  - Il paper per ora non si distingue da un prezzo casuale con le stesse uscite: 54% di vinti contro 54%, 46% di stop contro 46% (ops 0401, K4). Le classi dei referti descrivono la forma delle uscite, non una diagnosi.
  - Stop giornaliero e freno di serie non avrebbero aiutato: sul gate tolgono soprattutto i rimbalzi (stop 3%: −11.615 e drawdown da 11,7% a 20,3%, ops 0405).
  - Nessuna funzione ha ancora un contributo dimostrato oltre il margine; l'ombra AI (spenta) avrebbe evitato trade a −0,10R contro +0,23R di quelli che approvava, diff −0,33 ±0,36 (ops 0409).

== Cosa è cambiato nel sistema
  - 01/10 17:25 — report-giornaliero: stampa anche il testo del report pubblicato
  - 01/10 16:36 — Dati mancanti (D8): versione, promessa del gate, dopo l'uscita, motore sullo stesso segnale, percorso dello stop, qualità d'ingresso, scarti silenziosi, riga del giorno, storia del gate; solo raccolta, nessuna decisione 
  - 01/10 16:15 — diario: stella polare, J2, report giornaliero
  - 01/10 16:14 — Report giornaliero: nove sezioni fisse calcolate dalla macchina dopo ogni giro del gate, prima scheda della dashboard; capito.md e letture.md come fonti
  - 01/10 16:07 — funzioni servono: rischio effettivo in percentuale del capitale; prima lettura nel diario
  - 01/10 16:06 — Le funzioni servono? confronto d'esito per funzione nel report trades (freno, panchina, pesi, leva, tilt, declassate, esplorative, ombra AI, origine)
  - 01/10 15:55 — J2: il backlog in dashboard senza copie a mano (letto da docs/backlog.md e pubblicato dopo ogni giro del gate)
  - 01/10 15:49 — CLAUDE.md: la stella polare e il passo di ogni giorno (cosa ci avvicina, cosa abbiamo capito)
  - 01/10 13:28 — R1: il gate rigiocato nel passato (scripts/replay_gate.py), solo file locali, a pezzi nelle pause del gate
  - 01/10 13:16 — H3/H4: rigioco su paper e portafoglio nel diario e nel backlog, restano parcheggiate
  - 01/10 13:09 — controllo: il rimando al backlog punta al gruppo 1 dell'indice nuovo
  - 01/10 13:09 — H3/H4 come what-if: stop giornaliero e freno di serie rigiocati sul paper (trades) e sul portafoglio del motore (portafoglio), solo misura

== Aspetta il tuo sì e prossime letture
  - Aspettano il tuo sì: niente.
  - In lavorazione: R1. Rigiocare il gate nel passato — SÌ del proprietario il 1 ott: strumento pronto, prova piccola lanciata alle 13:49 (ops 0407); J2. «Cosa aspetta il sì» in dashboard, senza aggiornarlo a mano — in lavorazione (1 ott); D8. Raccolta dei dati mancanti (punto 4 del 1 ott) — scritta, ATTENDE IL RIAVVIO DEL BOT
    data | cosa si legge | regola
    2026-10-03 | Declassate contro attive (report trades, DECLASSATE) | regola del 3 ott, diario del 30 set
    2026-10-07 | Fuori campione: il problema è il gate o il bot? (report portafoglio) | regole del 7 e 14 ott, diario del 30 set
    2026-10-08 | R1, il gate rigiocato nel passato (prima lettura completa, stima) | regola R1, diario del 1 ott
    2026-10-10 | Varianti dai referti e ipotesi d'ingresso (J9, I4ter) | backlog archivio
    2026-10-14 | Fuori campione, seconda lettura | regole del 7 e 14 ott
    2026-10-15 | Gruppo di controllo: servono 3 conferme? (K3) | backlog archivio K3

== Salute e costi
  - Semafori: sistema verde, paper giallo.
  - Anomalia FRENO_GLOBALE: freno globale da deriva: PF 0,68 vs 2,02 atteso
  - Anomalia SENZA_PROMESSA: 124 validate su 208 senza promessa (last_pf)
  - Riavvii del bot nelle 24 ore: 2.
  - Letture Firestore nelle 24 ore: 350 (quota gratuita 50.000).
  - Spesa AI di ieri (2026-09-30): 2.80 $ in 57 chiamate — ai-hypotheses 1.54 $, ai-autopsia 0.56 $, ai-universe 0.46 $, ai-shadow 0.24 $, ai-connettivita 0.00 $
```
