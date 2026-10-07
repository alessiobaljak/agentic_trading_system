# 0535-7ott-mattina-controllo.req

_eseguito: 2026-10-07 06:24 UTC_

**richiesta:** `controllo`
**eseguito:** `.venv/bin/python -m scripts.controllo`
**esito:** codice 0 in 5.5s

```
[firebase] connesso (Firestore + RTDB)
CONTROLLO AUTOMATICO — generato da ops alle 2026-10-07 06:23 UTC (durata 3110 ms, impostazioni: default repo)
  semaforo SISTEMA: GIALLO   semaforo PAPER: GIALLO
  controllo precedente: 2026-10-07 06:19 UTC
  sezioni fallite: nessuna

ANOMALIE (3):
  [giallo] FRENO_GLOBALE (paper): freno globale da deriva: PF 0,73 vs 2,02 atteso (valore 0.726, soglia 1.214)
  [giallo] GATE_SFORA (sistema): il giro del gate e' durato 3 h 21 (piu' di 3 h) (valore 12066, soglia 10800)
  [giallo] SENZA_PROMESSA (paper): 118 validate su 279 senza promessa (last_pf) (valore 0.423, soglia 0.3)

LETTURE:
  salute:    Bot vivo (battito 32 s fa), gate 1 h 32 fa (solo urgenti), 13 posizioni, 2,1% a rischio. 3 avvisi: freno globale, gate lento, validate senz…
  paper:     345 trade in 20 giorni, 56% vinti, -88,03 USDT (-8,7%). BTC dal primo giorno +11,1% (noi -8,7%). Oggi -5,99 (validate -4,74).
  learning:  Attivo: freno globale, 14 strategie in panchina, keep per coppia 0.35 ×36, 0.5 ×34, 0.65 ×44, 0.75 ×14, 1 cooldown. Solo misurato: deriva.

LETTURE FIRESTORE DEL BOT (ultime 24 h, quota gratuita 50.000/giorno):
  non misurate in questo documento (le conta solo il bot: vedi il controllo orario)

CAMBIAMENTI DEL LEARNING rispetto al controllo di un'ora fa (precedente: 2026-10-07 06:19 UTC). NON e' il confronto con ieri: quello e' nella STORIA DEL LEARNING, in fondo
  nessuno nell'ultima ora: nessun pezzo del learning ha cambiato decisione

PAPER CONTRO IL CASO (prezzo casuale con le nostre uscite):
  stop 44% (caso 46%) · stop d'ingresso/uscita 47/52% (caso 48.5/51.5%) · massimo toccato mediano 0.82R (caso 0.81R) · vinti 55% (caso 54%)
  fonte del caso: simulazione del 30 set su prezzo casuale, docs/revisione_sospese_30set.md e backlog K4: costanti, non ricalcolate. Vicino al caso = le classi d'uscita sono la forma delle regole, non una diagnosi. R medio (caso -0.067) e primo target (caso 17%): in `trades`

COSA QUESTO CONTROLLO NON PUO' DARE:
  - cosa aspetta il si' del proprietario: vive in docs/backlog.md, non e' un dato del sistema -> leggere docs/backlog.md (gruppo 1 dell'indice)

STORIA DEL LEARNING (foto dello stato scattata dal bot alla prima ora di ogni giorno italiano, RTDB /learning_giorni; da qui in giu' gli orari sono in ora italiana, quelli sopra in UTC):
  foto di ieri 6 ott 00:07, foto di oggi 7 ott 00:14: i confronti «ieri» e «stanotte» qui sotto vengono da queste

COME IMPARA IL TRAILING (il keep e' la parte del guadagno che il trailing blocca quando si arma: con 0,5 tiene meta' del miglior guadagno visto; piu' alto = stop piu' vicino)
  a) COSA HA VISTO IL PAPER: dopo ogni uscita del trailing guarda dove va il prezzo nelle 24 ore dopo
     prematuro = poi e' arrivato al target: usciti troppo presto («da rumore» se lo stop e' scattato su un ritorno indietro piu' piccolo del movimento medio di una candela)
     protetto = poi e' tornato allo stop iniziale: l'uscita ha salvato il guadagno; neutro = ne' l'uno ne' l'altro
     uscite del trailing sulle candele da 15 minuti (le sole che contano per le proposte): 136 verdetti = 64 prematuri (14 da rumore) + 72 protetti; in piu' 16 neutri
     uscite dopo un incasso parziale (preso almeno il primo target, resto chiuso dallo stop): 29 verdetti (17 prematuri, 12 protetti, 0 neutri), NON usati dalle proposte (se contarli non e' deciso)
     dopo gli stop: 36 rumore (il prezzo e' poi tornato al primo target), 108 inversione (ha continuato contro, o non e' tornato al primo target entro la finestra): nessuna regola li usa ancora
     nuovi ieri (6 ott): trailing 5 prematuri, 5 protetti, 1 neutro · dopo un incasso parziale 0 prematuri, 1 protetto, 0 neutri · stop 5 rumore, 8 inversione
     nuovi stanotte (7 ott): trailing 2 prematuri, 5 protetti, 0 neutri · dopo un incasso parziale 1 prematuro, 0 protetti, 0 neutri · stop 1 rumore, 6 inversione
  b) COSA PROPONE IL PAPER AL GATE (una proposta e' un candidato in piu' che il gate prova sulla storia: il paper propone, il gate sceglie)
     keep per tutte le coppie: 72 protetti su 136 verdetti = 52,9% (serve il 60%): nessuna proposta. Mancano 24 protetti per proporre 0,75 (oppure 44 prematuri per 0,25)
     keep per strategia (servono 5 verdetti della strategia): 1 strategie propongono (gen_e59ad90b 0,75). Le piu' vicine:
       gen_4465723e 2 protetti su 4: manca 1 protetto per 0,75
       gen_490a90e5 4 protetti su 4: manca 1 protetto per 0,75
       gen_4c6df481 3 prematuri (3 da rumore) su 4: manca 1 prematuro da rumore per 0,25
     keep imparato dal bot da solo (vale solo per le coppie senza keep del gate; servono 8 verdetti per strategia, esplorative escluse): nessuna strategia (la piu' avanti ha 5 verdetti su 8)
     scala dei target di incasso dal vissuto (multipli del rischio iniziale: «1/2/3» = incassi a 1, 2 e 3 volte il rischio), ultimo giro del gate (7 ott 06:51): 0.75/1.25/1.75; keep proposto: nessuno
     strategie con una scala propria (almeno 5 trade col massimo guadagno raggiunto misurato): 19
  c) COSA HA SCELTO IL GATE per le 279 validate che il bot opera (per coppia; «non scelto» = coppia non ancora ripassata dal gate: vale il default)
     keep: non scelto ×151 · 0,65 ×44 · 0,35 ×36 · 0,5 ×34 · 0,75 ×14 (default 0,5). Dalle proposte del paper (0,25 e 0,75 esistono solo cosi'): 14
     scala dei target: 2/4/6 ×135 · 1.5/3/5 ×113 · 1/1.5/2.5 ×14 · 1/2/3 ×8 · altre 3 (×9) (default 1.5/3/5); dal vissuto in tutto: 9
     stop spostato al prezzo d'ingresso dopo il primo incasso (break-even): si ×145 · non scelto ×134 (default si)
     cambiato ieri (foto 6 ott 00:07 -> foto 7 ott 00:14): 2 coppie su 232 hanno cambiato keep, scala o break-even (validate +25 / -3)
       BULLAUSDT|gen_99c9c036: keep default -> 0,5; scala 1/1.75/3 -> 0.75/1.25/1.75
       SKYAIUSDT|gen_ead1fe8a: keep default -> 0,35; break-even default -> si
     cambiato stanotte (foto 7 ott 00:14 -> adesso): 4 coppie su 255 hanno cambiato keep, scala o break-even (validate +24 / -2)
       FLOCKUSDT|gen_2350695a: keep default -> 0,5; break-even default -> si
       IDUSDT|gen_6bc43e03: keep 0,65 -> 0,5
       IDUSDT|gen_c5430258: keep 0,65 -> 0,5
       IDUSDT|gen_dd9238bf: keep 0,65 -> 0,5
  d) FUNZIONA? trade chiusi dal 25 set per keep in uso all'ingresso (gruppi NON confrontabili: coppie diverse; misura, non regola)
     keep 0,35: 12 trade · trailing armato in 10 dei 12 trade con referto (83,3%) · 3 prematuri, 4 protetti · R medio +0,28 · tavolo 0,77
     keep 0,5: 246 trade · trailing armato in 142 dei 246 trade con referto (57,7%) · 57 prematuri, 67 protetti · R medio -0,11 · tavolo 0,69
     keep 0,65: 19 trade · trailing armato in 12 dei 19 trade con referto (63,2%) · 6 prematuri, 4 protetti · R medio -0,14 · tavolo 0,70
     keep 0,75: 13 trade · trailing armato in 5 dei 13 trade con referto (38,5%) · 5 prematuri, 0 protetti · R medio -0,22 · tavolo 0,58
     R = guadagno in unita' del rischio iniziale; tavolo = parte del tragitto verso il target lasciata all'uscita trailing (0 = uscito al target, 1 = all'entrata)

COSA IMPARANO LE STRATEGIE (ipotesi dai referti del paper -> varianti giudicate dal gate sulla storia -> promozioni; e intanto declassate, esplorative, panchina, freno)
  IERI (6 ott, giornata intera ora italiana):
     - ipotesi nate dai referti 1: gen_fa304106 controtrend_btc «3/3 persi contro il contesto BTC»
     - validate promosse 25: RENDERUSDT|gen_fe8925b6, PUMPUSDT|gen_13cc61f2, KERNELUSDT|gen_c647ead7 e altre 22; rimosse 0
     - declassate nuove 2 (size ridotta): BRUSDT|gen_95fb50ce, OPENUSDT|gen_bb762669; declassate tornate piene 2: BULLAUSDT|gen_99c9c036, SKYAIUSDT|gen_ead1fe8a
     - esplorative: entrate 37, promosse a validate 1 (OPENUSDT|gen_b9bf5d01), scartate 46
     - panchina (strategia×regime con peso sotto 0,5: size ridotta): entrano gen_ceab7f6a|sideways (0,4581), gen_fa304106|bull_trending (0,4935)
  STANOTTE (7 ott dalle 00:00 alle 08:23 ora italiana):
     - ipotesi nate dai referti 2: gen_8b91ba18 scala_stretta «3 perdite sotto il primo gradino (mfe mediana 0.62 R)», gen_e59ad90b conferma_trend «3 perdite controtrend»
     - validate promosse 24: UBUSDT|gen_4e6e1ae0, BULLAUSDT|gen_5a52c06b, IDOLUSDT|gen_5ad54558 e altre 21; rimosse 0
     - declassate nuove 10 (size ridotta): 1000BONKUSDT|gen_86a8b183, AVAAIUSDT|gen_08c22b92, ENAUSDT|gen_e85db5f1 e altre 7; declassate tornate piene 1: FLOCKUSDT|gen_2350695a
     - esplorative: entrate 31, promosse a validate 0, scartate 18
     - panchina (strategia×regime con peso sotto 0,5: size ridotta): entrano gen_8b91ba18|bull_trending (0,4581), gen_e59ad90b|bear_trending (0,4578)
     - cooldown (fermo dopo 3 stop di fila) fra le due foto: iniziati coin BMTUSDT
  PER STRATEGIA (le 10 con piu' trade chiusi negli ultimi 7 giorni; R = guadagno in unita' del rischio iniziale):
     gen_ceab7f6a: 8 trade, 3 vinti, R medio -0,49 · in panchina con sideways · scala propria 0.5/0.75/1.5 · 1 validata (1 declassate)
     gen_bb762669: 6 trade, 3 vinti, R medio -0,06 · scala propria 0.75/1.5/1.75 · 3 validate (2 declassate)
     gen_e59ad90b: 6 trade, 3 vinti, R medio -0,38 · ipotesi conferma_trend · in panchina con bear_trending · keep proposto 0,75 · scala propria 0.75/1/1.25 · 1 validata (1 declassate)
     gen_c647ead7: 5 trade, 4 vinti, R medio -0,07 · scala propria 0.5/0.75/1 · 3 validate (1 declassate)
     gen_4c6df481: 4 trade, 3 vinti, R medio +0,19 · in panchina con sideways · scala propria 1/1.25/1.5 · 1 validata
     gen_684d7623: 4 trade, 3 vinti, R medio -0,03 · 1 validata
     gen_fa304106: 4 trade, 0 vinti, R medio -1,04 · ipotesi conferma_trend, controtrend_btc, solo_long, solo_short · in panchina con bear_trending, bull_trending, high_uncertainty, sideways · scala propria 0.5/0.75/1 · 3 validate (3 declassate)
     gen_fb7d035a: 4 trade, 2 vinti, R medio +0,01 · scala propria 0.75/1/3.25 · 1 validata (1 declassate)
     gen_4465723e: 3 trade, 2 vinti, R medio -0,05 · scala propria 1.25/1.5/1.75 · 1 validata (1 declassate)
     gen_8981d5f2: 3 trade, 3 vinti, R medio +0,32 · 2 validate (1 declassate)

--- stderr ---
/root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
  return query.where(field_path, op_string, value)
```
