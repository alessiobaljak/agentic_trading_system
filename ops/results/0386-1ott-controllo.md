# 0386-1ott-controllo.req

_eseguito: 2026-10-01 06:05 UTC_

**richiesta:** `controllo`
**eseguito:** `.venv/bin/python -m scripts.controllo`
**esito:** codice 0 in 5.4s

```
[firebase] connesso (Firestore + RTDB)
CONTROLLO AUTOMATICO — generato da ops alle 2026-10-01 06:05 UTC (durata 2755 ms, impostazioni: default repo)
  semaforo SISTEMA: VERDE    semaforo PAPER: GIALLO
  controllo precedente: 2026-10-01 05:20 UTC
  sezioni fallite: nessuna

ANOMALIE (2):
  [giallo] FRENO_GLOBALE (paper): freno globale da deriva: PF 0,70 vs 2,02 atteso (valore 0.698, soglia 1.213)
  [giallo] SENZA_PROMESSA (paper): 124 validate su 208 senza promessa (last_pf) (valore 0.596, soglia 0.3)

LETTURE:
  salute:    Bot vivo (battito 0 s fa), gate 1 h 12 fa (solo urgenti), 4 posizioni, 0,5% a rischio. 2 avvisi: freno globale, validate senza promessa.
  paper:     204 trade in 14 giorni, 57% vinti, -70,82 USDT (-7,1%). BTC dal primo giorno +11,2% (noi -7,1%). Oggi +0,15 (validate -0,15).
  learning:  Attivo: freno globale, 8 strategie in panchina, keep per coppia 0.35 ×14, 0.5 ×11, 0.65 ×10, 0.75 ×14. Solo misurato: deriva, calibrazione.

LETTURE FIRESTORE DEL BOT (ultime 24 h, quota gratuita 50.000/giorno):
  non misurate in questo documento (le conta solo il bot: vedi il controllo orario)

CAMBIAMENTI DEL LEARNING rispetto al controllo di un'ora fa (precedente: 2026-10-01 05:20 UTC). NON e' il confronto con ieri: quello e' nella STORIA DEL LEARNING, in fondo
  nessuno nell'ultima ora: nessun pezzo del learning ha cambiato decisione

PAPER CONTRO IL CASO (prezzo casuale con le nostre uscite):
  stop 44% (caso 46%) · stop d'ingresso/uscita 47/52% (caso 48.5/51.5%) · massimo toccato mediano 0.85R (caso 0.81R) · vinti 56% (caso 54%)
  fonte del caso: simulazione del 30 set su prezzo casuale, docs/revisione_sospese_30set.md e backlog K4: costanti, non ricalcolate. Vicino al caso = le classi d'uscita sono la forma delle regole, non una diagnosi. R medio (caso -0.067) e primo target (caso 17%): in `trades`

COSA QUESTO CONTROLLO NON PUO' DARE:
  - cosa aspetta il si' del proprietario: vive in docs/backlog.md, non e' un dato del sistema -> leggere docs/backlog.md (voce F1 per il learning)

STORIA DEL LEARNING (foto dello stato scattata dal bot alla prima ora di ogni giorno italiano, RTDB /learning_giorni; da qui in giu' gli orari sono in ora italiana, quelli sopra in UTC):
  foto di ieri 30 set 00:20, foto di oggi 1 ott 00:16: i confronti «ieri» e «stanotte» qui sotto vengono da queste

COME IMPARA IL TRAILING (il keep e' la parte del guadagno che il trailing blocca quando si arma: con 0,5 tiene meta' del miglior guadagno visto; piu' alto = stop piu' vicino)
  a) COSA HA VISTO IL PAPER: dopo ogni uscita del trailing guarda dove va il prezzo nelle 24 ore dopo
     prematuro = poi e' arrivato al target: usciti troppo presto («da rumore» se lo stop e' scattato su un ritorno indietro piu' piccolo del movimento medio di una candela)
     protetto = poi e' tornato allo stop iniziale: l'uscita ha salvato il guadagno; neutro = ne' l'uno ne' l'altro
     uscite del trailing sulle candele da 15 minuti (le sole che contano per le proposte): 78 verdetti = 35 prematuri (6 da rumore) + 43 protetti; in piu' 10 neutri
     uscite dopo un incasso parziale (preso almeno il primo target, resto chiuso dallo stop): 19 verdetti (11 prematuri, 8 protetti, 0 neutri), NON usati dalle proposte (se contarli non e' deciso)
     dopo gli stop: 24 rumore (il prezzo e' poi tornato al primo target), 61 inversione (ha continuato contro, o non e' tornato al primo target entro la finestra): nessuna regola li usa ancora
     nuovi ieri (30 set): trailing 6 prematuri, 2 protetti, 3 neutri · dopo un incasso parziale 0 prematuri, 1 protetto, 0 neutri · stop 1 rumore, 5 inversione
     nuovi stanotte (1 ott): nessuno
  b) COSA PROPONE IL PAPER AL GATE (una proposta e' un candidato in piu' che il gate prova sulla storia: il paper propone, il gate sceglie)
     keep per tutte le coppie: 43 protetti su 78 verdetti = 55,1% (serve il 60%): nessuna proposta. Mancano 10 protetti per proporre 0,75 (oppure 30 prematuri per 0,25)
     keep per strategia (servono 5 verdetti della strategia): nessuna propone, su 51 con verdetti. Le piu' vicine:
       gen_490a90e5 4 protetti su 4: manca 1 protetto per 0,75
       gen_fca11c08 3 protetti su 4: manca 1 protetto per 0,75
       gen_2031005e 2 prematuri (1 da rumore) su 3: mancano 2 prematuri da rumore per 0,25
     keep imparato dal bot da solo (vale solo per le coppie senza keep del gate; servono 8 verdetti per strategia, esplorative escluse): nessuna strategia (la piu' avanti ha 4 verdetti su 8)
     scala dei target di incasso dal vissuto (multipli del rischio iniziale: «1/2/3» = incassi a 1, 2 e 3 volte il rischio), ultimo giro del gate (1 ott 06:52): 1/1.25/1.75; keep proposto: nessuno
     strategie con una scala propria (almeno 5 trade col massimo guadagno raggiunto misurato): 11
  c) COSA HA SCELTO IL GATE per le 208 validate che il bot opera (per coppia; «non scelto» = coppia non ancora ripassata dal gate: vale il default)
     keep: non scelto ×159 · 0,35 ×14 · 0,75 ×14 · 0,5 ×11 · 0,65 ×10 (default 0,5). Dalle proposte del paper (0,25 e 0,75 esistono solo cosi'): 14
     scala dei target: 2/4/6 ×111 · 1.5/3/5 ×79 · 1/1.5/2.5 ×7 · 1/2/3 ×6 · altre 4 (×5) (default 1.5/3/5); dal vissuto in tutto: 5
     stop spostato al prezzo d'ingresso dopo il primo incasso (break-even): non scelto ×140 · si ×68 (default si)
     cambiato ieri (foto 30 set 00:20 -> foto 1 ott 00:16): 2 coppie su 197 hanno cambiato keep, scala o break-even (validate +5 / -2)
       AVAAIUSDT|gen_e50a9211: keep default -> 0,5; break-even default -> si
       PLUMEUSDT|gen_e94b056d: keep 0,75 -> 0,35
     cambiato stanotte (foto 1 ott 00:16 -> adesso): nessuna delle 202 coppie presenti in entrambe le foto ha cambiato keep, scala o break-even (validate +6 / -0)
  d) FUNZIONA? trade chiusi dal 25 set per keep in uso all'ingresso (gruppi NON confrontabili: coppie diverse; misura, non regola)
     keep 0,35: 4 trade · trailing armato in 4 dei 4 trade con referto (100,0%) · 2 prematuri, 2 protetti · R medio +0,47 · tavolo 0,73
     keep 0,5: 134 trade · trailing armato in 83 dei 134 trade con referto (61,9%) · 31 prematuri, 39 protetti · R medio -0,06 · tavolo 0,70
     keep 0,65: 4 trade · trailing armato in 2 dei 4 trade con referto (50,0%) · 1 prematuro, 1 protetto · R medio -0,24 · tavolo 0,75
     keep 0,75: 7 trade · trailing armato in 3 dei 7 trade con referto (42,9%) · 2 prematuri, 0 protetti · R medio -0,15 · tavolo 0,46
     R = guadagno in unita' del rischio iniziale; tavolo = parte del tragitto verso il target lasciata all'uscita trailing (0 = uscito al target, 1 = all'entrata)

COSA IMPARANO LE STRATEGIE (ipotesi dai referti del paper -> varianti giudicate dal gate sulla storia -> promozioni; e intanto declassate, esplorative, panchina, freno)
  IERI (30 set, giornata intera ora italiana):
     - validate promosse 5: USELESSUSDT|gen_e09c5203, SCRUSDT|gen_bd8f158b, STXUSDT|gen_a5b0e4de e altre 2; rimosse 0
     - declassate nuove 20 (size ridotta): AIOUSDT|gen_581d4a68, BMTUSDT|gen_571cdda2, BMTUSDT|gen_cee79cdd e altre 17; declassate tornate piene 2: AVAAIUSDT|gen_e50a9211, PLUMEUSDT|gen_e94b056d
     - esplorative: entrate 49, promosse a validate 0, scartate 56
  STANOTTE (1 ott dalle 00:00 alle 08:05 ora italiana):
     - ipotesi nate dai referti 1: gen_fa304106 solo_short «long 3/3 persi»
     - varianti dalle ipotesi: create 1: gen_fa304106 solo_short (variante gen_45579407); bocciate 1: gen_fa304106 solo_short (variante gen_45579407)
     - validate promosse 6: ZORAUSDT|gen_f4e37ccc, USELESSUSDT|gen_96c1ed1b, TAUSDT|gen_4e6e1ae0 e altre 3; rimosse 0
     - declassate nuove 2 (size ridotta): NEIROUSDT|gen_413f1bd7, UBUSDT|gen_08664b28
     - esplorative: entrate 34, promosse a validate 0, scartate 23
     - panchina (strategia×regime con peso sotto 0,5: size ridotta): entrano gen_fa304106|high_uncertainty (0,4935)
  PER STRATEGIA (le 10 con piu' trade chiusi negli ultimi 7 giorni; R = guadagno in unita' del rischio iniziale):
     gen_fca11c08: 14 trade, 7 vinti, R medio -0,26 · ipotesi conferma_trend · scala propria 0.75/1/1.5 · 0 validate
     gen_490a90e5: 7 trade, 5 vinti, R medio -0,03 · scala propria 0.5/0.75/1 · 0 validate
     gen_bb762669: 5 trade, 4 vinti, R medio +0,17 · scala propria 0.75/1.5/1.75 · 2 validate (1 declassate)
     gen_cd5c842f: 5 trade, 4 vinti, R medio +0,33 · scala propria 1/1.25/2 · 1 validata (1 declassate)
     gen_4465723e: 4 trade, 4 vinti, R medio +0,49 · scala propria 0.75/1.5/1.75 · 1 validata (1 declassate)
     gen_4c6df481: 4 trade, 2 vinti, R medio +0,09 · in panchina con sideways · 1 validata
     gen_658b2edb: 4 trade, 4 vinti, R medio +0,49 · 2 validate (2 declassate)
     gen_e50a9211: 4 trade, 2 vinti, R medio -0,27 · 1 validata
     gen_e59ad90b: 4 trade, 3 vinti, R medio +0,26 · 1 validata (1 declassate)
     gen_35632db9: 3 trade, 2 vinti, R medio -0,06 · 0 validate

--- stderr ---
/root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
  return query.where(field_path, op_string, value)
```
