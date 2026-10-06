# 0520-6ott-mattina-controllo.req

_eseguito: 2026-10-06 06:22 UTC_

**richiesta:** `controllo`
**eseguito:** `.venv/bin/python -m scripts.controllo`
**esito:** codice 0 in 5.6s

```
[firebase] connesso (Firestore + RTDB)
CONTROLLO AUTOMATICO — generato da ops alle 2026-10-06 06:21 UTC (durata 3185 ms, impostazioni: default repo)
  semaforo SISTEMA: GIALLO   semaforo PAPER: GIALLO
  controllo precedente: 2026-10-06 06:09 UTC
  sezioni fallite: nessuna

ANOMALIE (3):
  [giallo] FRENO_GLOBALE (paper): freno globale da deriva: PF 0,74 vs 2,02 atteso (valore 0.742, soglia 1.21)
  [giallo] GATE_SFORA (sistema): il giro del gate e' durato 3 h 28 (piu' di 3 h) (valore 12503, soglia 10800)
  [giallo] SENZA_PROMESSA (paper): 119 validate su 257 senza promessa (last_pf) (valore 0.463, soglia 0.3)

LETTURE:
  salute:    Bot vivo (battito 12 s fa), gate 1 h 49 fa (solo urgenti), 3 posizioni, 0,3% a rischio. 3 avvisi: freno globale, gate lento, validate senza…
  paper:     311 trade in 19 giorni, 57% vinti, -75,97 USDT (-7,6%). BTC dal primo giorno +12,7% (noi -7,6%). Stop nel 44% delle uscite. Oggi -1,72.
  learning:  Attivo: freno globale, 10 strategie in panchina, keep per coppia 0.35 ×32, 0.5 ×24, 0.65 ×35, 0.75 ×14, 2 cooldown. Solo misurato: deriva.

LETTURE FIRESTORE DEL BOT (ultime 24 h, quota gratuita 50.000/giorno):
  non misurate in questo documento (le conta solo il bot: vedi il controllo orario)

CAMBIAMENTI DEL LEARNING rispetto al controllo di un'ora fa (precedente: 2026-10-06 06:09 UTC). NON e' il confronto con ieri: quello e' nella STORIA DEL LEARNING, in fondo
  nessuno nell'ultima ora: nessun pezzo del learning ha cambiato decisione

PAPER CONTRO IL CASO (prezzo casuale con le nostre uscite):
  stop 44% (caso 46%) · stop d'ingresso/uscita 46/53% (caso 48.5/51.5%) · massimo toccato mediano 0.84R (caso 0.81R) · vinti 56% (caso 54%)
  fonte del caso: simulazione del 30 set su prezzo casuale, docs/revisione_sospese_30set.md e backlog K4: costanti, non ricalcolate. Vicino al caso = le classi d'uscita sono la forma delle regole, non una diagnosi. R medio (caso -0.067) e primo target (caso 17%): in `trades`

COSA QUESTO CONTROLLO NON PUO' DARE:
  - cosa aspetta il si' del proprietario: vive in docs/backlog.md, non e' un dato del sistema -> leggere docs/backlog.md (gruppo 1 dell'indice)

STORIA DEL LEARNING (foto dello stato scattata dal bot alla prima ora di ogni giorno italiano, RTDB /learning_giorni; da qui in giu' gli orari sono in ora italiana, quelli sopra in UTC):
  foto di ieri 5 ott 00:59, foto di oggi 6 ott 00:07: i confronti «ieri» e «stanotte» qui sotto vengono da queste

COME IMPARA IL TRAILING (il keep e' la parte del guadagno che il trailing blocca quando si arma: con 0,5 tiene meta' del miglior guadagno visto; piu' alto = stop piu' vicino)
  a) COSA HA VISTO IL PAPER: dopo ogni uscita del trailing guarda dove va il prezzo nelle 24 ore dopo
     prematuro = poi e' arrivato al target: usciti troppo presto («da rumore» se lo stop e' scattato su un ritorno indietro piu' piccolo del movimento medio di una candela)
     protetto = poi e' tornato allo stop iniziale: l'uscita ha salvato il guadagno; neutro = ne' l'uno ne' l'altro
     uscite del trailing sulle candele da 15 minuti (le sole che contano per le proposte): 122 verdetti = 60 prematuri (12 da rumore) + 62 protetti; in piu' 16 neutri
     uscite dopo un incasso parziale (preso almeno il primo target, resto chiuso dallo stop): 27 verdetti (16 prematuri, 11 protetti, 0 neutri), NON usati dalle proposte (se contarli non e' deciso)
     dopo gli stop: 30 rumore (il prezzo e' poi tornato al primo target), 98 inversione (ha continuato contro, o non e' tornato al primo target entro la finestra): nessuna regola li usa ancora
     nuovi ieri (5 ott): trailing 5 prematuri, 4 protetti, 1 neutro · dopo un incasso parziale 1 prematuro, 1 protetto, 0 neutri · stop 0 rumore, 11 inversione
     nuovi stanotte (6 ott): trailing 3 prematuri, 0 protetti, 1 neutro · stop 0 rumore, 4 inversione
  b) COSA PROPONE IL PAPER AL GATE (una proposta e' un candidato in piu' che il gate prova sulla storia: il paper propone, il gate sceglie)
     keep per tutte le coppie: 62 protetti su 122 verdetti = 50,8% (serve il 60%): nessuna proposta. Mancano 28 protetti per proporre 0,75 (oppure 33 prematuri per 0,25)
     keep per strategia (servono 5 verdetti della strategia): 1 strategie propongono (gen_e59ad90b 0,75). Le piu' vicine:
       gen_490a90e5 4 protetti su 4: manca 1 protetto per 0,75
       gen_4c6df481 3 prematuri (3 da rumore) su 4: manca 1 prematuro da rumore per 0,25
       gen_cd5c842f 2 protetti su 4: manca 1 protetto per 0,75
     keep imparato dal bot da solo (vale solo per le coppie senza keep del gate; servono 8 verdetti per strategia, esplorative escluse): nessuna strategia (la piu' avanti ha 5 verdetti su 8)
     scala dei target di incasso dal vissuto (multipli del rischio iniziale: «1/2/3» = incassi a 1, 2 e 3 volte il rischio), ultimo giro del gate (6 ott 06:32): 0.75/1.25/1.75; keep proposto: nessuno
     strategie con una scala propria (almeno 5 trade col massimo guadagno raggiunto misurato): 15
  c) COSA HA SCELTO IL GATE per le 257 validate che il bot opera (per coppia; «non scelto» = coppia non ancora ripassata dal gate: vale il default)
     keep: non scelto ×152 · 0,65 ×35 · 0,35 ×32 · 0,5 ×24 · 0,75 ×14 (default 0,5). Dalle proposte del paper (0,25 e 0,75 esistono solo cosi'): 14
     scala dei target: 2/4/6 ×130 · 1.5/3/5 ×104 · 1/1.5/2.5 ×9 · 1/2/3 ×7 · altre 3 (×7) (default 1.5/3/5); dal vissuto in tutto: 7
     stop spostato al prezzo d'ingresso dopo il primo incasso (break-even): non scelto ×135 · si ×122 (default si)
     cambiato ieri (foto 5 ott 00:59 -> foto 6 ott 00:07): 3 coppie su 222 hanno cambiato keep, scala o break-even (validate +13 / -1)
       FLOCKUSDT|gen_c5194ce4: keep default -> 0,35; scala 0.75/1.5/4.5 -> 0.75/1.25/1.75; break-even default -> si
       UBUSDT|gen_15837112: scala 1/2/3 -> 1.5/3/5
       XPINUSDT|gen_2e0818c8: scala 1/1.5/2.5 -> 0.75/1.25/1.75
     cambiato stanotte (foto 6 ott 00:07 -> adesso): 2 coppie su 232 hanno cambiato keep, scala o break-even (validate +25 / -3)
       BULLAUSDT|gen_99c9c036: keep default -> 0,5; scala 1/1.75/3 -> 0.75/1.25/1.75
       SKYAIUSDT|gen_ead1fe8a: keep default -> 0,35; break-even default -> si
  d) FUNZIONA? trade chiusi dal 25 set per keep in uso all'ingresso (gruppi NON confrontabili: coppie diverse; misura, non regola)
     keep 0,35: 12 trade · trailing armato in 10 dei 12 trade con referto (83,3%) · 3 prematuri, 4 protetti · R medio +0,28 · tavolo 0,77
     keep 0,5: 220 trade · trailing armato in 130 dei 220 trade con referto (59,1%) · 53 prematuri, 58 protetti · R medio -0,09 · tavolo 0,69
     keep 0,65: 11 trade · trailing armato in 8 dei 11 trade con referto (72,7%) · 5 prematuri, 2 protetti · R medio +0,08 · tavolo 0,68
     keep 0,75: 13 trade · trailing armato in 5 dei 13 trade con referto (38,5%) · 5 prematuri, 0 protetti · R medio -0,22 · tavolo 0,58
     R = guadagno in unita' del rischio iniziale; tavolo = parte del tragitto verso il target lasciata all'uscita trailing (0 = uscito al target, 1 = all'entrata)

COSA IMPARANO LE STRATEGIE (ipotesi dai referti del paper -> varianti giudicate dal gate sulla storia -> promozioni; e intanto declassate, esplorative, panchina, freno)
  IERI (5 ott, giornata intera ora italiana):
     - validate promosse 13: FORMUSDT|gen_c647ead7, 1000BONKUSDT|gen_86a8b183, AVAAIUSDT|gen_08c22b92 e altre 10; rimosse 0
     - declassate nuove 6 (size ridotta): MUBARAKUSDT|gen_e933160c, MUBARAKUSDT|gen_ff3e4154, QUSDT|gen_da608d9f e altre 3; declassate tornate piene 2: FLOCKUSDT|gen_c5194ce4, QUSDT|gen_85fadf54
     - esplorative: entrate 53, promosse a validate 0, scartate 52
     - cooldown (fermo dopo 3 stop di fila) fra le due foto: finiti coin ENAUSDT
  STANOTTE (6 ott dalle 00:00 alle 08:21 ora italiana):
     - ipotesi nate dai referti 1: gen_fa304106 controtrend_btc «3/3 persi contro il contesto BTC»
     - validate promosse 25: RENDERUSDT|gen_fe8925b6, PUMPUSDT|gen_13cc61f2, KERNELUSDT|gen_c647ead7 e altre 22; rimosse 0
     - declassate nuove 2 (size ridotta): BRUSDT|gen_95fb50ce, OPENUSDT|gen_bb762669; declassate tornate piene 2: BULLAUSDT|gen_99c9c036, SKYAIUSDT|gen_ead1fe8a
     - esplorative: entrate 31, promosse a validate 1 (OPENUSDT|gen_b9bf5d01), scartate 16
     - cooldown (fermo dopo 3 stop di fila) fra le due foto: iniziati coin RAYSOLUSDT, strategia gen_fa304106
  PER STRATEGIA (le 10 con piu' trade chiusi negli ultimi 7 giorni; R = guadagno in unita' del rischio iniziale):
     gen_bb762669: 7 trade, 4 vinti, R medio +0,02 · scala propria 0.75/1.5/1.75 · 3 validate (2 declassate)
     gen_ceab7f6a: 7 trade, 3 vinti, R medio -0,40 · scala propria 0.5/1.5/1.75 · 1 validata (1 declassate)
     gen_e59ad90b: 5 trade, 4 vinti, R medio +0,06 · keep proposto 0,75 · scala propria 0.75/1/1.25 · 1 validata (1 declassate)
     gen_4c6df481: 4 trade, 3 vinti, R medio +0,19 · in panchina con sideways · scala propria 1/1.25/1.5 · 1 validata
     gen_f3661202: 4 trade, 3 vinti, R medio +0,02 · 2 validate (1 declassate)
     gen_fa304106: 4 trade, 0 vinti, R medio -1,04 · ipotesi conferma_trend, controtrend_btc, solo_long, solo_short · in panchina con bear_trending, high_uncertainty, sideways · scala propria 0.5/0.75/1 · 3 validate (3 declassate)
     gen_fb7d035a: 4 trade, 2 vinti, R medio -0,38 · 1 validata (1 declassate)
     gen_8981d5f2: 3 trade, 3 vinti, R medio +0,32 · 2 validate (1 declassate)
     gen_a32bee42: 3 trade, 2 vinti, R medio -0,03 · 2 validate (2 declassate)
     gen_a640dfa5: 3 trade, 1 vinto, R medio -0,55 · scala propria 1/1.25/1.5 · 2 validate (2 declassate)

--- stderr ---
/root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
  return query.where(field_path, op_string, value)
```
