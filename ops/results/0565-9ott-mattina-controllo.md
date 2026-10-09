# 0565-9ott-mattina-controllo.req

_eseguito: 2026-10-09 04:05 UTC_

**richiesta:** `controllo`
**eseguito:** `.venv/bin/python -m scripts.controllo`
**esito:** codice 0 in 5.6s

```
[firebase] connesso (Firestore + RTDB)
CONTROLLO AUTOMATICO — generato da ops alle 2026-10-09 04:05 UTC (durata 3092 ms, impostazioni: default repo)
  semaforo SISTEMA: GIALLO   semaforo PAPER: GIALLO
  controllo precedente: 2026-10-09 03:34 UTC
  sezioni fallite: nessuna

ANOMALIE (2):
  [giallo] FRENO_GLOBALE (paper): freno globale da deriva: PF 0,70 vs 2,02 atteso (valore 0.699, soglia 1.213)
  [giallo] GATE_SFORA (sistema): il giro del gate e' durato 3 h 47 (piu' di 3 h) (valore 13674, soglia 10800)

LETTURE:
  salute:    Bot vivo (battito 7 s fa), gate 2 h 58 fa (completa), 9 posizioni, 1,2% a rischio. 2 avvisi: freno globale, gate lento.
  paper:     417 trade in 22 giorni, 55% vinti, -111,28 USDT (-11,0%). BTC dal primo giorno +8,5% (noi -11,0%). Oggi -3,78 (validate -4,08).
  learning:  Attivo: freno globale, 12 strategie in panchina, keep per coppia 0.35 ×38, 0.5 ×40, 0.65 ×64, 0.75 ×14. Solo misurato: deriva, calibrazione.

LETTURE FIRESTORE DEL BOT (ultime 24 h, quota gratuita 50.000/giorno):
  non misurate in questo documento (le conta solo il bot: vedi il controllo orario)

CAMBIAMENTI DEL LEARNING rispetto al controllo di un'ora fa (precedente: 2026-10-09 03:34 UTC). NON e' il confronto con ieri: quello e' nella STORIA DEL LEARNING, in fondo
  - cooldown OPENUSDT finito

PAPER CONTRO IL CASO (prezzo casuale con le nostre uscite):
  stop 45% (caso 46%) · stop d'ingresso/uscita 45/54% (caso 48.5/51.5%) · massimo toccato mediano 0.80R (caso 0.81R) · vinti 54% (caso 54%)
  fonte del caso: simulazione del 30 set su prezzo casuale, docs/revisione_sospese_30set.md e backlog K4: costanti, non ricalcolate. Vicino al caso = le classi d'uscita sono la forma delle regole, non una diagnosi. R medio (caso -0.067) e primo target (caso 17%): in `trades`

COSA QUESTO CONTROLLO NON PUO' DARE:
  - cosa aspetta il si' del proprietario: vive in docs/backlog.md, non e' un dato del sistema -> leggere docs/backlog.md (gruppo 1 dell'indice)

STORIA DEL LEARNING (foto dello stato scattata dal bot alla prima ora di ogni giorno italiano, RTDB /learning_giorni; da qui in giu' gli orari sono in ora italiana, quelli sopra in UTC):
  foto di ieri 8 ott 00:23, foto di oggi 9 ott 00:33: i confronti «ieri» e «stanotte» qui sotto vengono da queste

COME IMPARA IL TRAILING (il keep e' la parte del guadagno che il trailing blocca quando si arma: con 0,5 tiene meta' del miglior guadagno visto; piu' alto = stop piu' vicino)
  a) COSA HA VISTO IL PAPER: dopo ogni uscita del trailing guarda dove va il prezzo nelle 24 ore dopo
     prematuro = poi e' arrivato al target: usciti troppo presto («da rumore» se lo stop e' scattato su un ritorno indietro piu' piccolo del movimento medio di una candela)
     protetto = poi e' tornato allo stop iniziale: l'uscita ha salvato il guadagno; neutro = ne' l'uno ne' l'altro
     uscite del trailing sulle candele da 15 minuti (le sole che contano per le proposte): 160 verdetti = 76 prematuri (16 da rumore) + 84 protetti; in piu' 17 neutri
     uscite dopo un incasso parziale (preso almeno il primo target, resto chiuso dallo stop): 34 verdetti (18 prematuri, 16 protetti, 0 neutri), NON usati dalle proposte (se contarli non e' deciso)
     dopo gli stop: 38 rumore (il prezzo e' poi tornato al primo target), 142 inversione (ha continuato contro, o non e' tornato al primo target entro la finestra): nessuna regola li usa ancora
     nuovi ieri (8 ott): trailing 7 prematuri, 4 protetti, 1 neutro · dopo un incasso parziale 1 prematuro, 3 protetti, 0 neutri · stop 1 rumore, 17 inversione
     nuovi stanotte (9 ott): trailing 1 prematuro, 2 protetti, 0 neutri · stop 1 rumore, 1 inversione
  b) COSA PROPONE IL PAPER AL GATE (una proposta e' un candidato in piu' che il gate prova sulla storia: il paper propone, il gate sceglie)
     keep per tutte le coppie: 84 protetti su 160 verdetti = 52,5% (serve il 60%): nessuna proposta. Mancano 30 protetti per proporre 0,75 (oppure 50 prematuri per 0,25)
     keep per strategia (servono 5 verdetti della strategia): 2 strategie propongono (gen_4465723e 0,75, gen_e59ad90b 0,75). Le piu' vicine:
       gen_490a90e5 4 protetti su 4: manca 1 protetto per 0,75
       gen_4c6df481 3 prematuri (3 da rumore) su 4: manca 1 prematuro da rumore per 0,25
       gen_902fb1fd 2 protetti su 4: manca 1 protetto per 0,75
     keep imparato dal bot da solo (vale solo per le coppie senza keep del gate; servono 8 verdetti per strategia, esplorative escluse): nessuna strategia (la piu' avanti ha 5 verdetti su 8)
     scala dei target di incasso dal vissuto (multipli del rischio iniziale: «1/2/3» = incassi a 1, 2 e 3 volte il rischio), ultimo giro del gate (9 ott 03:06): 0.75/1.25/1.75; keep proposto: nessuno
     strategie con una scala propria (almeno 5 trade col massimo guadagno raggiunto misurato): 25
  c) COSA HA SCELTO IL GATE per le 238 validate che il bot opera (per coppia; «non scelto» = coppia non ancora ripassata dal gate: vale il default)
     keep: non scelto ×82 · 0,65 ×64 · 0,5 ×40 · 0,35 ×38 · 0,75 ×14 (default 0,5). Dalle proposte del paper (0,25 e 0,75 esistono solo cosi'): 14
     scala dei target: 2/4/6 ×104 · 1.5/3/5 ×103 · 1/1.5/2.5 ×17 · 0.75/1.25/1.75 (dal vissuto) ×6 · altre 3 (×8) (default 1.5/3/5); dal vissuto in tutto: 8
     stop spostato al prezzo d'ingresso dopo il primo incasso (break-even): si ×169 · non scelto ×69 (default si)
     cambiato ieri (foto 8 ott 00:23 -> foto 9 ott 00:33): 2 coppie su 205 hanno cambiato keep, scala o break-even (validate +33 / -74)
       BULLAUSDT|gen_99c9c036: keep 0,5 -> 0,65; scala 0.75/1.25/1.75 -> 2/4/6
       SKYAIUSDT|gen_eb2ece0c: scala 1.5/3/5 -> 2/4/6
     cambiato stanotte (foto 9 ott 00:33 -> adesso): nessuna delle 238 coppie presenti in entrambe le foto ha cambiato keep, scala o break-even
  d) FUNZIONA? trade chiusi dal 25 set per keep in uso all'ingresso (gruppi NON confrontabili: coppie diverse; misura, non regola)
     keep 0,35: 17 trade · trailing armato in 12 dei 17 trade con referto (70,6%) · 4 prematuri, 5 protetti · R medio +0,01 · tavolo 0,80
     keep 0,5: 292 trade · trailing armato in 167 dei 292 trade con referto (57,2%) · 63 prematuri, 81 protetti · R medio -0,09 · tavolo 0,69
     keep 0,65: 37 trade · trailing armato in 20 dei 37 trade con referto (54,1%) · 11 prematuri, 5 protetti · R medio -0,25 · tavolo 0,72
     keep 0,75: 16 trade · trailing armato in 6 dei 16 trade con referto (37,5%) · 6 prematuri, 0 protetti · R medio -0,27 · tavolo 0,61
     R = guadagno in unita' del rischio iniziale; tavolo = parte del tragitto verso il target lasciata all'uscita trailing (0 = uscito al target, 1 = all'entrata)

COSA IMPARANO LE STRATEGIE (ipotesi dai referti del paper -> varianti giudicate dal gate sulla storia -> promozioni; e intanto declassate, esplorative, panchina, freno)
  IERI (8 ott, giornata intera ora italiana):
     - ipotesi nate dai referti 1: gen_fa304106 scala_stretta «3 perdite sotto il primo gradino (mfe mediana 0.60 R)»
     - validate promosse 33: ASTERUSDT|gen_d74845a5, TAUSDT|gen_c08c5114, HUSDT|gen_22b2cade e altre 30; rimosse 71: ENAUSDT|gen_99c9c036, PROMUSDT|gen_cd5c842f, ZKUSDT|gen_98837ec2 e altre 68
     - declassate nuove 11 (size ridotta): FLOCKUSDT|gen_c5194ce4, IDOLUSDT|gen_c429c4c6, KERNELUSDT|gen_c647ead7 e altre 8; declassate tornate piene 1: ZORAUSDT|gen_f4e37ccc
     - esplorative: entrate 58, promosse a validate 0, scartate 60
     - panchina (strategia×regime con peso sotto 0,5: size ridotta): entrano gen_5a52c06b|bear_trending (0,4572); escono gen_c5194ce4|high_uncertainty (0,548)
  STANOTTE (9 ott dalle 00:00 alle 06:05 ora italiana):
     - esplorative: entrate 17, promosse a validate 0, scartate 1
     - panchina (strategia×regime con peso sotto 0,5: size ridotta): nessuna entra; escono gen_5a52c06b|bear_trending (0,6088)
  PER STRATEGIA (le 10 con piu' trade chiusi negli ultimi 7 giorni; R = guadagno in unita' del rischio iniziale):
     gen_ceab7f6a: 7 trade, 2 vinti, R medio -0,70 · in panchina con sideways · scala propria 0.5/0.75/1.5 · 1 validata (1 declassate)
     gen_c647ead7: 6 trade, 4 vinti, R medio -0,23 · scala propria 0.5/0.75/1 · 3 validate (2 declassate)
     gen_4c6df481: 5 trade, 3 vinti, R medio -0,07 · in panchina con sideways · scala propria 1/1.25/1.5 · 1 validata
     gen_96c1ed1b: 5 trade, 3 vinti, R medio +0,14 · scala propria 0.75/1.25/3.5 · 2 validate (2 declassate)
     gen_e59ad90b: 5 trade, 2 vinti, R medio -0,53 · ipotesi conferma_trend · in panchina con bear_trending · keep proposto 0,75 · scala propria 0.75/1/1.25 · 0 validate
     gen_684d7623: 4 trade, 3 vinti, R medio -0,03 · 1 validata
     gen_9a383fff: 4 trade, 2 vinti, R medio -0,30 · scala propria 0.75/1.25/1.5 · 3 validate (2 declassate)
     gen_bb762669: 4 trade, 2 vinti, R medio +0,10 · scala propria 0.75/1.5/1.75 · 3 validate (2 declassate)
     gen_fa304106: 4 trade, 0 vinti, R medio -1,08 · ipotesi conferma_trend, controtrend_btc, scala_stretta, solo_long, solo_short · in panchina con bear_trending, bull_trending, high_uncertainty, sideways · scala propria 0.5/0.75/1 · 0 validate
     gen_1eec02f5: 3 trade, 2 vinti, R medio -0,04 · 4 validate (2 declassate)

--- stderr ---
/root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
  return query.where(field_path, op_string, value)
```
