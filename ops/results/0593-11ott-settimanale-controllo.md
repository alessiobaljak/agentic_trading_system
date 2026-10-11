# 0593-11ott-settimanale-controllo.req

_eseguito: 2026-10-11 04:00 UTC_

**richiesta:** `controllo`
**eseguito:** `.venv/bin/python -m scripts.controllo`
**esito:** codice 0 in 6.0s

```
[firebase] connesso (Firestore + RTDB)
CONTROLLO AUTOMATICO — generato da ops alle 2026-10-11 04:00 UTC (durata 3237 ms, impostazioni: default repo)
  semaforo SISTEMA: GIALLO   semaforo PAPER: GIALLO
  controllo precedente: 2026-10-11 03:45 UTC
  sezioni fallite: nessuna

ANOMALIE (2):
  [giallo] FRENO_GLOBALE (paper): freno globale da deriva: PF 0,72 vs 2,02 atteso (valore 0.719, soglia 1.21)
  [giallo] GATE_SFORA (sistema): il giro del gate e' durato 4 h 18 (piu' di 3 h) (valore 15506, soglia 10800)

LETTURE:
  salute:    Bot vivo (battito 33 s fa), gate 2 h 19 fa (completa), 6 posizioni, 0,8% a rischio. 2 avvisi: freno globale, gate lento.
  paper:     458 trade in 24 giorni, 56% vinti, -109,19 USDT (-10,9%). BTC dal primo giorno +9,5% (noi -10,9%). Stop nel 44% delle uscite. Oggi -2,11.
  learning:  Attivo: freno globale, 12 strategie in panchina, keep per coppia 0.35 ×44, 0.5 ×52, 0.65 ×85, 0.75 ×14. Solo misurato: deriva, calibrazione.

LETTURE FIRESTORE DEL BOT (ultime 24 h, quota gratuita 50.000/giorno):
  non misurate in questo documento (le conta solo il bot: vedi il controllo orario)

CAMBIAMENTI DEL LEARNING rispetto al controllo di un'ora fa (precedente: 2026-10-11 03:45 UTC). NON e' il confronto con ieri: quello e' nella STORIA DEL LEARNING, in fondo
  nessuno nell'ultima ora: nessun pezzo del learning ha cambiato decisione

PAPER CONTRO IL CASO (prezzo casuale con le nostre uscite):
  stop 44% (caso 46%) · stop d'ingresso/uscita 45/54% (caso 48.5/51.5%) · massimo toccato mediano 0.81R (caso 0.81R) · vinti 55% (caso 54%)
  fonte del caso: simulazione del 30 set su prezzo casuale, docs/revisione_sospese_30set.md e backlog K4: costanti, non ricalcolate. Vicino al caso = le classi d'uscita sono la forma delle regole, non una diagnosi. R medio (caso -0.067) e primo target (caso 17%): in `trades`

COSA QUESTO CONTROLLO NON PUO' DARE:
  - cosa aspetta il si' del proprietario: vive in docs/backlog.md, non e' un dato del sistema -> leggere docs/backlog.md (gruppo 1 dell'indice)

STORIA DEL LEARNING (foto dello stato scattata dal bot alla prima ora di ogni giorno italiano, RTDB /learning_giorni; da qui in giu' gli orari sono in ora italiana, quelli sopra in UTC):
  foto di ieri 10 ott 00:38, foto di oggi 11 ott 00:44: i confronti «ieri» e «stanotte» qui sotto vengono da queste

COME IMPARA IL TRAILING (il keep e' la parte del guadagno che il trailing blocca quando si arma: con 0,5 tiene meta' del miglior guadagno visto; piu' alto = stop piu' vicino)
  a) COSA HA VISTO IL PAPER: dopo ogni uscita del trailing guarda dove va il prezzo nelle 24 ore dopo
     prematuro = poi e' arrivato al target: usciti troppo presto («da rumore» se lo stop e' scattato su un ritorno indietro piu' piccolo del movimento medio di una candela)
     protetto = poi e' tornato allo stop iniziale: l'uscita ha salvato il guadagno; neutro = ne' l'uno ne' l'altro
     uscite del trailing sulle candele da 15 minuti (le sole che contano per le proposte): 183 verdetti = 90 prematuri (21 da rumore) + 93 protetti; in piu' 20 neutri
     uscite dopo un incasso parziale (preso almeno il primo target, resto chiuso dallo stop): 39 verdetti (20 prematuri, 19 protetti, 0 neutri), NON usati dalle proposte (se contarli non e' deciso)
     dopo gli stop: 39 rumore (il prezzo e' poi tornato al primo target), 155 inversione (ha continuato contro, o non e' tornato al primo target entro la finestra): nessuna regola li usa ancora
     nuovi ieri (10 ott): trailing 6 prematuri, 2 protetti, 1 neutro · stop 0 rumore, 7 inversione
     nuovi stanotte (11 ott): trailing 2 prematuri, 3 protetti, 0 neutri · stop 1 rumore, 0 inversione
  b) COSA PROPONE IL PAPER AL GATE (una proposta e' un candidato in piu' che il gate prova sulla storia: il paper propone, il gate sceglie)
     keep per tutte le coppie: 93 protetti su 183 verdetti = 50,8% (serve il 60%): nessuna proposta. Mancano 42 protetti per proporre 0,75 (oppure 50 prematuri per 0,25)
     keep per strategia (servono 5 verdetti della strategia): 4 strategie propongono (gen_4465723e 0,75, gen_4c6df481 0,25, gen_ceab7f6a 0,75 e altre 1). Le piu' vicine:
       gen_490a90e5 4 protetti su 4: manca 1 protetto per 0,75
       gen_8c9b332f 3 prematuri (1 da rumore) su 4: manca 1 prematuro da rumore per 0,25
       gen_902fb1fd 2 protetti su 4: manca 1 protetto per 0,75
     keep imparato dal bot da solo (vale solo per le coppie senza keep del gate; servono 8 verdetti per strategia, esplorative escluse): nessuna strategia (la piu' avanti ha 5 verdetti su 8)
     scala dei target di incasso dal vissuto (multipli del rischio iniziale: «1/2/3» = incassi a 1, 2 e 3 volte il rischio), ultimo giro del gate (11 ott 03:40): 0.75/1.25/1.75; keep proposto: nessuno
     strategie con una scala propria (almeno 5 trade col massimo guadagno raggiunto misurato): 27
  c) COSA HA SCELTO IL GATE per le 239 validate che il bot opera (per coppia; «non scelto» = coppia non ancora ripassata dal gate: vale il default)
     keep: 0,65 ×85 · 0,5 ×52 · 0,35 ×44 · non scelto ×44 · 0,75 ×14 (default 0,5). Dalle proposte del paper (0,25 e 0,75 esistono solo cosi'): 14
     scala dei target: 1.5/3/5 ×110 · 2/4/6 ×90 · 1/1.5/2.5 ×18 · 1/2/3 ×12 · altre 2 (×9) (default 1.5/3/5); dal vissuto in tutto: 9
     stop spostato al prezzo d'ingresso dopo il primo incasso (break-even): si ×204 · non scelto ×35 (default si)
     cambiato ieri (foto 10 ott 00:38 -> foto 11 ott 00:44): 1 coppie su 219 hanno cambiato keep, scala o break-even (validate +19 / -17)
       SAHARAUSDT|gen_66848d49: keep 0,65 -> 0,35
     cambiato stanotte (foto 11 ott 00:44 -> adesso): nessuna delle 238 coppie presenti in entrambe le foto ha cambiato keep, scala o break-even (validate +1 / -0)
  d) FUNZIONA? trade chiusi dal 25 set per keep in uso all'ingresso (gruppi NON confrontabili: coppie diverse; misura, non regola)
     keep 0,35: 21 trade · trailing armato in 14 dei 21 trade con referto (66,7%) · 4 prematuri, 6 protetti · R medio -0,04 · tavolo 0,80
     keep 0,5: 317 trade · trailing armato in 183 dei 317 trade con referto (57,7%) · 73 prematuri, 88 protetti · R medio -0,07 · tavolo 0,68
     keep 0,65: 47 trade · trailing armato in 29 dei 47 trade con referto (61,7%) · 16 prematuri, 9 protetti · R medio -0,12 · tavolo 0,73
     keep 0,75: 18 trade · trailing armato in 7 dei 18 trade con referto (38,9%) · 7 prematuri, 0 protetti · R medio -0,23 · tavolo 0,58
     R = guadagno in unita' del rischio iniziale; tavolo = parte del tragitto verso il target lasciata all'uscita trailing (0 = uscito al target, 1 = all'entrata)

COSA IMPARANO LE STRATEGIE (ipotesi dai referti del paper -> varianti giudicate dal gate sulla storia -> promozioni; e intanto declassate, esplorative, panchina, freno)
  IERI (10 ott, giornata intera ora italiana):
     - ipotesi nate dai referti 1: gen_ceab7f6a ingresso_vol_ratio «4 perdite d'ingresso su 5 con volume sotto la media (vol_ratio < 1) (mediana 0.71), vinti mediana 1.03»
     - validate promosse 19: PENGUUSDT|gen_5b9ed454, PTBUSDT|gen_73033c73, HUSDT|gen_2255a1d8 e altre 16; rimosse 16: STXUSDT|gen_14e1775b, HEIUSDT|gen_9a383fff (vissuta 14,1 giorni), STXUSDT|gen_68ebd3b9 e altre 13
     - declassate nuove 14 (size ridotta): ASTERUSDT|gen_37836d3c, ASTERUSDT|gen_d74845a5, HUMAUSDT|gen_da39a23a e altre 11; declassate tornate piene 3: 1000BONKUSDT|gen_86a8b183, PNUTUSDT|gen_4810faab, SAHARAUSDT|gen_66848d49
     - esplorative: entrate 61, promosse a validate 0, scartate 59
  STANOTTE (11 ott dalle 00:00 alle 06:00 ora italiana):
     - validate promosse 1: STXUSDT|gen_0aa0d29c; rimosse 0
     - esplorative: entrate 16, promosse a validate 0, scartate 9
  PER STRATEGIA (le 10 con piu' trade chiusi negli ultimi 7 giorni; R = guadagno in unita' del rischio iniziale):
     gen_ceab7f6a: 9 trade, 4 vinti, R medio -0,41 · ipotesi ingresso_vol_ratio · in panchina con sideways · keep proposto 0,75 · scala propria 0.75/1.25/1.5 · 1 validata (1 declassate)
     gen_c647ead7: 6 trade, 4 vinti, R medio -0,23 · scala propria 0.5/0.75/1 · 3 validate (2 declassate)
     gen_96c1ed1b: 5 trade, 2 vinti, R medio -0,22 · scala propria 0.75/1.25/3.5 · 2 validate (2 declassate)
     gen_1eec02f5: 4 trade, 3 vinti, R medio +0,07 · 4 validate (2 declassate)
     gen_4c6df481: 4 trade, 2 vinti, R medio -0,15 · in panchina con sideways · keep proposto 0,25 · scala propria 1/1.25/2 · 1 validata (1 declassate)
     gen_684d7623: 4 trade, 3 vinti, R medio -0,03 · 1 validata (1 declassate)
     gen_8b91ba18: 4 trade, 2 vinti, R medio -0,26 · ipotesi scala_stretta · in panchina con bull_trending · scala propria 0.75/1.25/1.5 · 0 validate
     gen_9a383fff: 4 trade, 2 vinti, R medio -0,30 · scala propria 0.75/1.25/1.5 · 2 validate (1 declassate)
     gen_e59ad90b: 4 trade, 2 vinti, R medio -0,40 · ipotesi conferma_trend · in panchina con bear_trending · keep proposto 0,75 · scala propria 0.75/1/1.25 · 0 validate
     gen_fa304106: 4 trade, 0 vinti, R medio -1,08 · ipotesi conferma_trend, controtrend_btc, scala_stretta, solo_long, solo_short · in panchina con bear_trending, bull_trending, high_uncertainty, sideways · scala propria 0.5/0.75/1 · 0 validate

--- stderr ---
/root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
  return query.where(field_path, op_string, value)
```
