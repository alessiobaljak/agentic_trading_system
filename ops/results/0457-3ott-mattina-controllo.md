# 0457-3ott-mattina-controllo.req

_eseguito: 2026-10-03 06:19 UTC_

**richiesta:** `controllo`
**eseguito:** `.venv/bin/python -m scripts.controllo`
**esito:** codice 0 in 4.9s

```
[firebase] connesso (Firestore + RTDB)
CONTROLLO AUTOMATICO — generato da ops alle 2026-10-03 06:19 UTC (durata 2711 ms, impostazioni: default repo)
  semaforo SISTEMA: VERDE    semaforo PAPER: GIALLO
  controllo precedente: 2026-10-03 05:49 UTC
  sezioni fallite: nessuna

ANOMALIE (2):
  [giallo] FRENO_GLOBALE (paper): freno globale da deriva: PF 0,72 vs 2,01 atteso (valore 0.717, soglia 1.205)
  [giallo] SENZA_PROMESSA (paper): 123 validate su 216 senza promessa (last_pf) (valore 0.569, soglia 0.3)

LETTURE:
  salute:    Bot vivo (battito 3 s fa), gate 47 min fa (solo urgenti), 5 posizioni, 0,7% a rischio. 2 avvisi: freno globale, validate senza promessa.
  paper:     246 trade in 16 giorni, 56% vinti, -73,68 USDT (-7,1%). BTC dal primo giorno +11,7% (noi -7,1%). Stop nel 44% delle uscite. Oggi +3,38.
  learning:  Attivo: freno globale, 10 strategie in panchina, keep per coppia 0.35 ×17, 0.5 ×14, 0.65 ×13, 0.75 ×14. Solo misurato: deriva, calibrazione.

LETTURE FIRESTORE DEL BOT (ultime 24 h, quota gratuita 50.000/giorno):
  non misurate in questo documento (le conta solo il bot: vedi il controllo orario)

CAMBIAMENTI DEL LEARNING rispetto al controllo di un'ora fa (precedente: 2026-10-03 05:49 UTC). NON e' il confronto con ieri: quello e' nella STORIA DEL LEARNING, in fondo
  - cooldown USELESSUSDT finito

PAPER CONTRO IL CASO (prezzo casuale con le nostre uscite):
  stop 44% (caso 46%) · stop d'ingresso/uscita 48/51% (caso 48.5/51.5%) · massimo toccato mediano 0.84R (caso 0.81R) · vinti 55% (caso 54%)
  fonte del caso: simulazione del 30 set su prezzo casuale, docs/revisione_sospese_30set.md e backlog K4: costanti, non ricalcolate. Vicino al caso = le classi d'uscita sono la forma delle regole, non una diagnosi. R medio (caso -0.067) e primo target (caso 17%): in `trades`

COSA QUESTO CONTROLLO NON PUO' DARE:
  - cosa aspetta il si' del proprietario: vive in docs/backlog.md, non e' un dato del sistema -> leggere docs/backlog.md (gruppo 1 dell'indice)

STORIA DEL LEARNING (foto dello stato scattata dal bot alla prima ora di ogni giorno italiano, RTDB /learning_giorni; da qui in giu' gli orari sono in ora italiana, quelli sopra in UTC):
  foto di ieri 2 ott 00:28, foto di oggi 3 ott 00:45: i confronti «ieri» e «stanotte» qui sotto vengono da queste

COME IMPARA IL TRAILING (il keep e' la parte del guadagno che il trailing blocca quando si arma: con 0,5 tiene meta' del miglior guadagno visto; piu' alto = stop piu' vicino)
  a) COSA HA VISTO IL PAPER: dopo ogni uscita del trailing guarda dove va il prezzo nelle 24 ore dopo
     prematuro = poi e' arrivato al target: usciti troppo presto («da rumore» se lo stop e' scattato su un ritorno indietro piu' piccolo del movimento medio di una candela)
     protetto = poi e' tornato allo stop iniziale: l'uscita ha salvato il guadagno; neutro = ne' l'uno ne' l'altro
     uscite del trailing sulle candele da 15 minuti (le sole che contano per le proposte): 95 verdetti = 44 prematuri (8 da rumore) + 51 protetti; in piu' 10 neutri
     uscite dopo un incasso parziale (preso almeno il primo target, resto chiuso dallo stop): 22 verdetti (13 prematuri, 9 protetti, 0 neutri), NON usati dalle proposte (se contarli non e' deciso)
     dopo gli stop: 26 rumore (il prezzo e' poi tornato al primo target), 79 inversione (ha continuato contro, o non e' tornato al primo target entro la finestra): nessuna regola li usa ancora
     nuovi ieri (2 ott): trailing 6 prematuri, 4 protetti, 0 neutri · dopo un incasso parziale 1 prematuro, 1 protetto, 0 neutri · stop 0 rumore, 10 inversione
     nuovi stanotte (3 ott): trailing 0 prematuri, 1 protetto, 0 neutri · dopo un incasso parziale 1 prematuro, 0 protetti, 0 neutri · stop 1 rumore, 0 inversione
  b) COSA PROPONE IL PAPER AL GATE (una proposta e' un candidato in piu' che il gate prova sulla storia: il paper propone, il gate sceglie)
     keep per tutte le coppie: 51 protetti su 95 verdetti = 53,7% (serve il 60%): nessuna proposta. Mancano 15 protetti per proporre 0,75 (oppure 33 prematuri per 0,25)
     keep per strategia (servono 5 verdetti della strategia): nessuna propone, su 56 con verdetti. Le piu' vicine:
       gen_490a90e5 4 protetti su 4: manca 1 protetto per 0,75
       gen_fca11c08 3 protetti su 4: manca 1 protetto per 0,75
       gen_18c839a0 2 prematuri (0 da rumore) su 3: mancano 2 prematuri da rumore per 0,25
     keep imparato dal bot da solo (vale solo per le coppie senza keep del gate; servono 8 verdetti per strategia, esplorative escluse): nessuna strategia (la piu' avanti ha 5 verdetti su 8)
     scala dei target di incasso dal vissuto (multipli del rischio iniziale: «1/2/3» = incassi a 1, 2 e 3 volte il rischio), ultimo giro del gate (3 ott 07:31): 0.75/1.25/1.75; keep proposto: nessuno
     strategie con una scala propria (almeno 5 trade col massimo guadagno raggiunto misurato): 13
  c) COSA HA SCELTO IL GATE per le 216 validate che il bot opera (per coppia; «non scelto» = coppia non ancora ripassata dal gate: vale il default)
     keep: non scelto ×158 · 0,35 ×17 · 0,5 ×14 · 0,75 ×14 · 0,65 ×13 (default 0,5). Dalle proposte del paper (0,25 e 0,75 esistono solo cosi'): 14
     scala dei target: 2/4/6 ×116 · 1.5/3/5 ×81 · 1/1.5/2.5 ×7 · 1/2/3 ×6 · altre 5 (×6) (default 1.5/3/5); dal vissuto in tutto: 6
     stop spostato al prezzo d'ingresso dopo il primo incasso (break-even): non scelto ×139 · si ×77 (default si)
     cambiato ieri (foto 2 ott 00:28 -> foto 3 ott 00:45): 1 coppie su 209 hanno cambiato keep, scala o break-even (validate +3 / -0)
       PNUTUSDT|gen_4810faab: keep default -> 0,5; break-even default -> si
     cambiato stanotte (foto 3 ott 00:45 -> adesso): nessuna delle 212 coppie presenti in entrambe le foto ha cambiato keep, scala o break-even (validate +4 / -0)
  d) FUNZIONA? trade chiusi dal 25 set per keep in uso all'ingresso (gruppi NON confrontabili: coppie diverse; misura, non regola)
     keep 0,35: 6 trade · trailing armato in 6 dei 6 trade con referto (100,0%) · 2 prematuri, 3 protetti · R medio +0,40 · tavolo 0,75
     keep 0,5: 169 trade · trailing armato in 100 dei 169 trade con referto (59,2%) · 38 prematuri, 47 protetti · R medio -0,10 · tavolo 0,70
     keep 0,65: 5 trade · trailing armato in 3 dei 5 trade con referto (60,0%) · 2 prematuri, 1 protetto · R medio +0,11 · tavolo 0,53
     keep 0,75: 11 trade · trailing armato in 5 dei 11 trade con referto (45,5%) · 5 prematuri, 0 protetti · R medio -0,15 · tavolo 0,58
     R = guadagno in unita' del rischio iniziale; tavolo = parte del tragitto verso il target lasciata all'uscita trailing (0 = uscito al target, 1 = all'entrata)

COSA IMPARANO LE STRATEGIE (ipotesi dai referti del paper -> varianti giudicate dal gate sulla storia -> promozioni; e intanto declassate, esplorative, panchina, freno)
  IERI (2 ott, giornata intera ora italiana):
     - validate promosse 3: MUBARAKUSDT|gen_f86f7370, RENDERUSDT|gen_fdaa6e0b, SKYAIUSDT|gen_4cadc09b; rimosse 0
     - declassate nuove 2 (size ridotta): UBUSDT|gen_887d87df, USELESSUSDT|gen_e09c5203; declassate tornate piene 1: PNUTUSDT|gen_4810faab
     - esplorative: entrate 38, promosse a validate 0, scartate 58
     - cooldown (fermo dopo 3 stop di fila) fra le due foto: iniziati strategia gen_c5194ce4; finiti coin TAUSDT
  STANOTTE (3 ott dalle 00:00 alle 08:19 ora italiana):
     - validate promosse 4: TAUSDT|gen_c647ead7, BRUSDT|gen_95fb50ce, XPINUSDT|gen_ba0c8feb e altre 1; rimosse 0
     - declassate nuove 10 (size ridotta): AVAAIUSDT|gen_dbe19eb2, AVAAIUSDT|gen_e50a9211, GALAUSDT|gen_b9aa9989 e altre 7
     - esplorative: entrate 46, promosse a validate 2 (TAUSDT|gen_c647ead7, UBUSDT|gen_d926b0fd), scartate 14
     - cooldown (fermo dopo 3 stop di fila) fra le due foto: finiti strategia gen_c5194ce4
  PER STRATEGIA (le 10 con piu' trade chiusi negli ultimi 7 giorni; R = guadagno in unita' del rischio iniziale):
     gen_fca11c08: 9 trade, 4 vinti, R medio -0,32 · ipotesi conferma_trend · scala propria 0.75/1/1.5 · 0 validate
     gen_bb762669: 7 trade, 6 vinti, R medio +0,21 · scala propria 0.75/1/1.5 · 2 validate (1 declassate)
     gen_4c6df481: 6 trade, 4 vinti, R medio +0,32 · in panchina con sideways · scala propria 1/1.25/1.5 · 1 validata
     gen_e59ad90b: 6 trade, 4 vinti, R medio +0,06 · scala propria 0.75/1/1.25 · 1 validata (1 declassate)
     gen_658b2edb: 4 trade, 4 vinti, R medio +0,49 · 2 validate (2 declassate)
     gen_a640dfa5: 4 trade, 4 vinti, R medio +0,53 · 2 validate (2 declassate)
     gen_c5194ce4: 4 trade, 1 vinto, R medio -0,66 · in panchina con high_uncertainty · 1 validata (1 declassate)
     gen_cd5c842f: 4 trade, 3 vinti, R medio +0,29 · scala propria 1/1.25/2 · 1 validata (1 declassate)
     gen_e50a9211: 4 trade, 2 vinti, R medio -0,27 · 1 validata (1 declassate)
     gen_4465723e: 3 trade, 3 vinti, R medio +0,53 · scala propria 0.75/1.5/1.75 · 1 validata (1 declassate)

--- stderr ---
/root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
  return query.where(field_path, op_string, value)
```
