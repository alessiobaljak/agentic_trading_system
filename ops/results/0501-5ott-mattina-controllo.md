# 0501-5ott-mattina-controllo.req

_eseguito: 2026-10-05 06:21 UTC_

**richiesta:** `controllo`
**eseguito:** `.venv/bin/python -m scripts.controllo`
**esito:** codice 0 in 5.7s

```
[firebase] connesso (Firestore + RTDB)
CONTROLLO AUTOMATICO — generato da ops alle 2026-10-05 06:21 UTC (durata 3043 ms, impostazioni: default repo)
  semaforo SISTEMA: GIALLO   semaforo PAPER: GIALLO
  controllo precedente: 2026-10-05 06:00 UTC
  sezioni fallite: nessuna

ANOMALIE (3):
  [giallo] FRENO_GLOBALE (paper): freno globale da deriva: PF 0,73 vs 2,01 atteso (valore 0.734, soglia 1.204)
  [giallo] GATE_SFORA (sistema): il giro del gate e' durato 3 h 22 (piu' di 3 h) (valore 12128, soglia 10800)
  [giallo] SENZA_PROMESSA (paper): 121 validate su 235 senza promessa (last_pf) (valore 0.515, soglia 0.3)

LETTURE:
  salute:    Bot vivo (battito 23 s fa), gate 2 h 05 fa (solo urgenti), 1 posizioni, 0,1% a rischio. 3 avvisi: freno globale, gate lento, validate senza…
  paper:     292 trade in 18 giorni, 57% vinti, -75,94 USDT (-7,6%). BTC dal primo giorno +13,2% (noi -7,6%). Oggi -8,08 (validate -8,22).
  learning:  Attivo: freno globale, 10 strategie in panchina, keep per coppia 0.35 ×27, 0.5 ×17, 0.65 ×23, 0.75 ×14. Solo misurato: deriva, calibrazione.

LETTURE FIRESTORE DEL BOT (ultime 24 h, quota gratuita 50.000/giorno):
  non misurate in questo documento (le conta solo il bot: vedi il controllo orario)

CAMBIAMENTI DEL LEARNING rispetto al controllo di un'ora fa (precedente: 2026-10-05 06:00 UTC). NON e' il confronto con ieri: quello e' nella STORIA DEL LEARNING, in fondo
  nessuno nell'ultima ora: nessun pezzo del learning ha cambiato decisione

PAPER CONTRO IL CASO (prezzo casuale con le nostre uscite):
  stop 44% (caso 46%) · stop d'ingresso/uscita 47/52% (caso 48.5/51.5%) · massimo toccato mediano 0.84R (caso 0.81R) · vinti 56% (caso 54%)
  fonte del caso: simulazione del 30 set su prezzo casuale, docs/revisione_sospese_30set.md e backlog K4: costanti, non ricalcolate. Vicino al caso = le classi d'uscita sono la forma delle regole, non una diagnosi. R medio (caso -0.067) e primo target (caso 17%): in `trades`

COSA QUESTO CONTROLLO NON PUO' DARE:
  - cosa aspetta il si' del proprietario: vive in docs/backlog.md, non e' un dato del sistema -> leggere docs/backlog.md (gruppo 1 dell'indice)

STORIA DEL LEARNING (foto dello stato scattata dal bot alla prima ora di ogni giorno italiano, RTDB /learning_giorni; da qui in giu' gli orari sono in ora italiana, quelli sopra in UTC):
  foto di ieri 4 ott 00:52, foto di oggi 5 ott 00:59: i confronti «ieri» e «stanotte» qui sotto vengono da queste

COME IMPARA IL TRAILING (il keep e' la parte del guadagno che il trailing blocca quando si arma: con 0,5 tiene meta' del miglior guadagno visto; piu' alto = stop piu' vicino)
  a) COSA HA VISTO IL PAPER: dopo ogni uscita del trailing guarda dove va il prezzo nelle 24 ore dopo
     prematuro = poi e' arrivato al target: usciti troppo presto («da rumore» se lo stop e' scattato su un ritorno indietro piu' piccolo del movimento medio di una candela)
     protetto = poi e' tornato allo stop iniziale: l'uscita ha salvato il guadagno; neutro = ne' l'uno ne' l'altro
     uscite del trailing sulle candele da 15 minuti (le sole che contano per le proposte): 113 verdetti = 53 prematuri (9 da rumore) + 60 protetti; in piu' 14 neutri
     uscite dopo un incasso parziale (preso almeno il primo target, resto chiuso dallo stop): 26 verdetti (16 prematuri, 10 protetti, 0 neutri), NON usati dalle proposte (se contarli non e' deciso)
     dopo gli stop: 30 rumore (il prezzo e' poi tornato al primo target), 90 inversione (ha continuato contro, o non e' tornato al primo target entro la finestra): nessuna regola li usa ancora
     nuovi ieri (4 ott): trailing 5 prematuri, 6 protetti, 2 neutri · stop 2 rumore, 4 inversione
     nuovi stanotte (5 ott): trailing 1 prematuro, 2 protetti, 0 neutri · dopo un incasso parziale 1 prematuro, 0 protetti, 0 neutri · stop 0 rumore, 7 inversione
  b) COSA PROPONE IL PAPER AL GATE (una proposta e' un candidato in piu' che il gate prova sulla storia: il paper propone, il gate sceglie)
     keep per tutte le coppie: 60 protetti su 113 verdetti = 53,1% (serve il 60%): nessuna proposta. Mancano 20 protetti per proporre 0,75 (oppure 37 prematuri per 0,25)
     keep per strategia (servono 5 verdetti della strategia): 1 strategie propongono (gen_e59ad90b 0,75). Le piu' vicine:
       gen_490a90e5 4 protetti su 4: manca 1 protetto per 0,75
       gen_fca11c08 3 protetti su 4: manca 1 protetto per 0,75
       gen_18c839a0 2 prematuri (0 da rumore) su 3: mancano 2 prematuri da rumore per 0,25
     keep imparato dal bot da solo (vale solo per le coppie senza keep del gate; servono 8 verdetti per strategia, esplorative escluse): nessuna strategia (la piu' avanti ha 5 verdetti su 8)
     scala dei target di incasso dal vissuto (multipli del rischio iniziale: «1/2/3» = incassi a 1, 2 e 3 volte il rischio), ultimo giro del gate (5 ott 06:15): 0.75/1.25/1.75; keep proposto: nessuno
     strategie con una scala propria (almeno 5 trade col massimo guadagno raggiunto misurato): 15
  c) COSA HA SCELTO IL GATE per le 235 validate che il bot opera (per coppia; «non scelto» = coppia non ancora ripassata dal gate: vale il default)
     keep: non scelto ×154 · 0,35 ×27 · 0,65 ×23 · 0,5 ×17 · 0,75 ×14 (default 0,5). Dalle proposte del paper (0,25 e 0,75 esistono solo cosi'): 14
     scala dei target: 2/4/6 ×121 · 1.5/3/5 ×95 · 1/1.5/2.5 ×7 · 1/2/3 ×5 · altre 4 (×7) (default 1.5/3/5); dal vissuto in tutto: 7
     stop spostato al prezzo d'ingresso dopo il primo incasso (break-even): non scelto ×136 · si ×99 (default si)
     cambiato ieri (foto 4 ott 00:52 -> foto 5 ott 00:59): 3 coppie su 215 hanno cambiato keep, scala o break-even (validate +8 / -1)
       HEIUSDT|gen_e6ddc613: keep default -> 0,5; break-even default -> si
       SKYAIUSDT|gen_98837ec2: keep default -> 0,5
       SYRUPUSDT|gen_f3b97917: keep default -> 0,65; scala 1/1.5/2.5 -> 2/4/6; break-even default -> si
     cambiato stanotte (foto 5 ott 00:59 -> adesso): 3 coppie su 222 hanno cambiato keep, scala o break-even (validate +13 / -1)
       FLOCKUSDT|gen_c5194ce4: keep default -> 0,35; scala 0.75/1.5/4.5 -> 0.75/1.25/1.75; break-even default -> si
       UBUSDT|gen_15837112: scala 1/2/3 -> 1.5/3/5
       XPINUSDT|gen_2e0818c8: scala 1/1.5/2.5 -> 0.75/1.25/1.75
  d) FUNZIONA? trade chiusi dal 25 set per keep in uso all'ingresso (gruppi NON confrontabili: coppie diverse; misura, non regola)
     keep 0,35: 12 trade · trailing armato in 10 dei 12 trade con referto (83,3%) · 3 prematuri, 4 protetti · R medio +0,28 · tavolo 0,76
     keep 0,5: 204 trade · trailing armato in 122 dei 204 trade con referto (59,8%) · 49 prematuri, 55 protetti · R medio -0,09 · tavolo 0,69
     keep 0,65: 8 trade · trailing armato in 5 dei 8 trade con referto (62,5%) · 2 prematuri, 2 protetti · R medio +0,02 · tavolo 0,59
     keep 0,75: 13 trade · trailing armato in 5 dei 13 trade con referto (38,5%) · 5 prematuri, 0 protetti · R medio -0,22 · tavolo 0,58
     R = guadagno in unita' del rischio iniziale; tavolo = parte del tragitto verso il target lasciata all'uscita trailing (0 = uscito al target, 1 = all'entrata)

COSA IMPARANO LE STRATEGIE (ipotesi dai referti del paper -> varianti giudicate dal gate sulla storia -> promozioni; e intanto declassate, esplorative, panchina, freno)
  IERI (4 ott, giornata intera ora italiana):
     - ipotesi nate dai referti 3: gen_bf2be656 scala_stretta «3 perdite sotto il primo gradino (mfe mediana 0.42 R)», gen_bf2be656 solo_short «long 3/3 persi», gen_fa304106 conferma_trend «3 perdite mai andate a favore (classe ingresso) e 0 vinti su 8»
     - validate promosse 8: OPENUSDT|gen_bb762669, AINUSDT|gen_ef115241, PUMPUSDT|gen_08664b28 e altre 5; rimosse 0
     - declassate tornate piene 4: HEIUSDT|gen_e6ddc613, HUMAUSDT|gen_da39a23a, SKYAIUSDT|gen_98837ec2 e altre 1
     - esplorative: entrate 35, promosse a validate 1 (PTBUSDT|gen_684d7623), scartate 56
     - cooldown (fermo dopo 3 stop di fila) fra le due foto: iniziati coin ENAUSDT
  STANOTTE (5 ott dalle 00:00 alle 08:21 ora italiana):
     - validate promosse 13: FORMUSDT|gen_c647ead7, 1000BONKUSDT|gen_86a8b183, AVAAIUSDT|gen_08c22b92 e altre 10; rimosse 0
     - declassate nuove 6 (size ridotta): MUBARAKUSDT|gen_e933160c, MUBARAKUSDT|gen_ff3e4154, QUSDT|gen_da608d9f e altre 3; declassate tornate piene 2: FLOCKUSDT|gen_c5194ce4, QUSDT|gen_85fadf54
     - esplorative: entrate 34, promosse a validate 0, scartate 11
     - cooldown (fermo dopo 3 stop di fila) fra le due foto: finiti coin ENAUSDT
  PER STRATEGIA (le 10 con piu' trade chiusi negli ultimi 7 giorni; R = guadagno in unita' del rischio iniziale):
     gen_bb762669: 8 trade, 6 vinti, R medio +0,29 · scala propria 0.75/1.5/1.75 · 3 validate (1 declassate)
     gen_e59ad90b: 7 trade, 5 vinti, R medio -0,05 · keep proposto 0,75 · scala propria 0.75/1/1.25 · 1 validata (1 declassate)
     gen_ceab7f6a: 6 trade, 3 vinti, R medio -0,27 · scala propria 0.75/1.5/1.75 · 1 validata (1 declassate)
     gen_4c6df481: 4 trade, 3 vinti, R medio +0,19 · in panchina con sideways · scala propria 1/1.25/1.5 · 1 validata
     gen_c5194ce4: 4 trade, 1 vinto, R medio -0,66 · in panchina con high_uncertainty · 1 validata
     gen_f3661202: 4 trade, 3 vinti, R medio +0,02 · 2 validate (1 declassate)
     gen_fb7d035a: 4 trade, 2 vinti, R medio -0,38 · 1 validata (1 declassate)
     gen_4508a416: 3 trade, 2 vinti, R medio -0,06 · 1 validata (1 declassate)
     gen_4810faab: 3 trade, 2 vinti, R medio -0,01 · 1 validata
     gen_658b2edb: 3 trade, 3 vinti, R medio +0,49 · 2 validate (2 declassate)

--- stderr ---
/root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
  return query.where(field_path, op_string, value)
```
