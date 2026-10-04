# 0477-4ott-mattina-controllo.req

_eseguito: 2026-10-04 06:20 UTC_

**richiesta:** `controllo`
**eseguito:** `.venv/bin/python -m scripts.controllo`
**esito:** codice 0 in 5.0s

```
[firebase] connesso (Firestore + RTDB)
CONTROLLO AUTOMATICO — generato da ops alle 2026-10-04 06:20 UTC (durata 2670 ms, impostazioni: default repo)
  semaforo SISTEMA: VERDE    semaforo PAPER: GIALLO
  controllo precedente: 2026-10-04 05:55 UTC
  sezioni fallite: nessuna

ANOMALIE (2):
  [giallo] FRENO_GLOBALE (paper): freno globale da deriva: PF 0,76 vs 2,00 atteso (valore 0.759, soglia 1.203)
  [giallo] SENZA_PROMESSA (paper): 122 validate su 223 senza promessa (last_pf) (valore 0.547, soglia 0.3)

LETTURE:
  salute:    Bot vivo (battito 30 s fa), gate 41 min fa (solo urgenti), 3 posizioni, 0,6% a rischio. 2 avvisi: freno globale, validate senza promessa.
  paper:     264 trade in 17 giorni, 57% vinti, -62,59 USDT (-6,3%). BTC dal primo giorno +12,1% (noi -6,3%). Oggi -4,38 (validate -4,63).
  learning:  Attivo: freno globale, 10 strategie in panchina, keep per coppia 0.35 ×23, 0.5 ×16, 0.65 ×15, 0.75 ×14. Solo misurato: deriva, calibrazione.

LETTURE FIRESTORE DEL BOT (ultime 24 h, quota gratuita 50.000/giorno):
  non misurate in questo documento (le conta solo il bot: vedi il controllo orario)

CAMBIAMENTI DEL LEARNING rispetto al controllo di un'ora fa (precedente: 2026-10-04 05:55 UTC). NON e' il confronto con ieri: quello e' nella STORIA DEL LEARNING, in fondo
  nessuno nell'ultima ora: nessun pezzo del learning ha cambiato decisione

PAPER CONTRO IL CASO (prezzo casuale con le nostre uscite):
  stop 43% (caso 46%) · stop d'ingresso/uscita 47/52% (caso 48.5/51.5%) · massimo toccato mediano 0.84R (caso 0.81R) · vinti 56% (caso 54%)
  fonte del caso: simulazione del 30 set su prezzo casuale, docs/revisione_sospese_30set.md e backlog K4: costanti, non ricalcolate. Vicino al caso = le classi d'uscita sono la forma delle regole, non una diagnosi. R medio (caso -0.067) e primo target (caso 17%): in `trades`

COSA QUESTO CONTROLLO NON PUO' DARE:
  - cosa aspetta il si' del proprietario: vive in docs/backlog.md, non e' un dato del sistema -> leggere docs/backlog.md (gruppo 1 dell'indice)

STORIA DEL LEARNING (foto dello stato scattata dal bot alla prima ora di ogni giorno italiano, RTDB /learning_giorni; da qui in giu' gli orari sono in ora italiana, quelli sopra in UTC):
  foto di ieri 3 ott 00:45, foto di oggi 4 ott 00:52: i confronti «ieri» e «stanotte» qui sotto vengono da queste

COME IMPARA IL TRAILING (il keep e' la parte del guadagno che il trailing blocca quando si arma: con 0,5 tiene meta' del miglior guadagno visto; piu' alto = stop piu' vicino)
  a) COSA HA VISTO IL PAPER: dopo ogni uscita del trailing guarda dove va il prezzo nelle 24 ore dopo
     prematuro = poi e' arrivato al target: usciti troppo presto («da rumore» se lo stop e' scattato su un ritorno indietro piu' piccolo del movimento medio di una candela)
     protetto = poi e' tornato allo stop iniziale: l'uscita ha salvato il guadagno; neutro = ne' l'uno ne' l'altro
     uscite del trailing sulle candele da 15 minuti (le sole che contano per le proposte): 104 verdetti = 49 prematuri (9 da rumore) + 55 protetti; in piu' 13 neutri
     uscite dopo un incasso parziale (preso almeno il primo target, resto chiuso dallo stop): 25 verdetti (15 prematuri, 10 protetti, 0 neutri), NON usati dalle proposte (se contarli non e' deciso)
     dopo gli stop: 28 rumore (il prezzo e' poi tornato al primo target), 80 inversione (ha continuato contro, o non e' tornato al primo target entro la finestra): nessuna regola li usa ancora
     nuovi ieri (3 ott): trailing 3 prematuri, 2 protetti, 2 neutri · dopo un incasso parziale 3 prematuri, 1 protetto, 0 neutri · stop 3 rumore, 0 inversione
     nuovi stanotte (4 ott): trailing 2 prematuri, 3 protetti, 1 neutro · stop 0 rumore, 1 inversione
  b) COSA PROPONE IL PAPER AL GATE (una proposta e' un candidato in piu' che il gate prova sulla storia: il paper propone, il gate sceglie)
     keep per tutte le coppie: 55 protetti su 104 verdetti = 52,9% (serve il 60%): nessuna proposta. Mancano 19 protetti per proporre 0,75 (oppure 34 prematuri per 0,25)
     keep per strategia (servono 5 verdetti della strategia): nessuna propone, su 62 con verdetti. Le piu' vicine:
       gen_490a90e5 4 protetti su 4: manca 1 protetto per 0,75
       gen_fca11c08 3 protetti su 4: manca 1 protetto per 0,75
       gen_18c839a0 2 prematuri (0 da rumore) su 3: mancano 2 prematuri da rumore per 0,25
     keep imparato dal bot da solo (vale solo per le coppie senza keep del gate; servono 8 verdetti per strategia, esplorative escluse): nessuna strategia (la piu' avanti ha 5 verdetti su 8)
     scala dei target di incasso dal vissuto (multipli del rischio iniziale: «1/2/3» = incassi a 1, 2 e 3 volte il rischio), ultimo giro del gate (4 ott 07:38): 0.75/1.25/1.75; keep proposto: nessuno
     strategie con una scala propria (almeno 5 trade col massimo guadagno raggiunto misurato): 13
  c) COSA HA SCELTO IL GATE per le 223 validate che il bot opera (per coppia; «non scelto» = coppia non ancora ripassata dal gate: vale il default)
     keep: non scelto ×155 · 0,35 ×23 · 0,5 ×16 · 0,65 ×15 · 0,75 ×14 (default 0,5). Dalle proposte del paper (0,25 e 0,75 esistono solo cosi'): 14
     scala dei target: 2/4/6 ×118 · 1.5/3/5 ×86 · 1/1.5/2.5 ×8 · 1/2/3 ×6 · altre 4 (×5) (default 1.5/3/5); dal vissuto in tutto: 5
     stop spostato al prezzo d'ingresso dopo il primo incasso (break-even): non scelto ×137 · si ×86 (default si)
     cambiato ieri (foto 3 ott 00:45 -> foto 4 ott 00:52): nessuna delle 212 coppie presenti in entrambe le foto ha cambiato keep, scala o break-even (validate +4 / -0)
     cambiato stanotte (foto 4 ott 00:52 -> adesso): 3 coppie su 215 hanno cambiato keep, scala o break-even (validate +8 / -1)
       HEIUSDT|gen_e6ddc613: keep default -> 0,5; break-even default -> si
       SKYAIUSDT|gen_98837ec2: keep default -> 0,5
       SYRUPUSDT|gen_f3b97917: keep default -> 0,65; scala 1/1.5/2.5 -> 2/4/6; break-even default -> si
  d) FUNZIONA? trade chiusi dal 25 set per keep in uso all'ingresso (gruppi NON confrontabili: coppie diverse; misura, non regola)
     keep 0,35: 7 trade · trailing armato in 7 dei 7 trade con referto (100,0%) · 3 prematuri, 3 protetti · R medio +0,66 · tavolo 0,76
     keep 0,5: 184 trade · trailing armato in 111 dei 184 trade con referto (60,3%) · 44 prematuri, 51 protetti · R medio -0,07 · tavolo 0,70
     keep 0,65: 6 trade · trailing armato in 4 dei 6 trade con referto (66,7%) · 2 prematuri, 2 protetti · R medio +0,14 · tavolo 0,59
     keep 0,75: 12 trade · trailing armato in 5 dei 12 trade con referto (41,7%) · 5 prematuri, 0 protetti · R medio -0,14 · tavolo 0,58
     R = guadagno in unita' del rischio iniziale; tavolo = parte del tragitto verso il target lasciata all'uscita trailing (0 = uscito al target, 1 = all'entrata)

COSA IMPARANO LE STRATEGIE (ipotesi dai referti del paper -> varianti giudicate dal gate sulla storia -> promozioni; e intanto declassate, esplorative, panchina, freno)
  IERI (3 ott, giornata intera ora italiana):
     - validate promosse 4: TAUSDT|gen_c647ead7, BRUSDT|gen_95fb50ce, XPINUSDT|gen_ba0c8feb e altre 1; rimosse 0
     - declassate nuove 10 (size ridotta): AVAAIUSDT|gen_dbe19eb2, AVAAIUSDT|gen_e50a9211, GALAUSDT|gen_b9aa9989 e altre 7
     - esplorative: entrate 46, promosse a validate 2 (TAUSDT|gen_c647ead7, UBUSDT|gen_d926b0fd), scartate 41
     - cooldown (fermo dopo 3 stop di fila) fra le due foto: finiti strategia gen_c5194ce4
  STANOTTE (4 ott dalle 00:00 alle 08:20 ora italiana):
     - ipotesi nate dai referti 2: gen_bf2be656 scala_stretta «3 perdite sotto il primo gradino (mfe mediana 0.42 R)», gen_bf2be656 solo_short «long 3/3 persi»
     - validate promosse 8: OPENUSDT|gen_bb762669, AINUSDT|gen_ef115241, PUMPUSDT|gen_08664b28 e altre 5; rimosse 0
     - declassate tornate piene 4: HEIUSDT|gen_e6ddc613, HUMAUSDT|gen_da39a23a, SKYAIUSDT|gen_98837ec2 e altre 1
     - esplorative: entrate 42, promosse a validate 1 (PTBUSDT|gen_684d7623), scartate 17
  PER STRATEGIA (le 10 con piu' trade chiusi negli ultimi 7 giorni; R = guadagno in unita' del rischio iniziale):
     gen_bb762669: 7 trade, 6 vinti, R medio +0,49 · scala propria 0.75/1.5/1.75 · 3 validate (1 declassate)
     gen_e59ad90b: 6 trade, 4 vinti, R medio +0,06 · scala propria 0.75/1/1.25 · 1 validata (1 declassate)
     gen_4c6df481: 5 trade, 3 vinti, R medio +0,04 · in panchina con sideways · scala propria 1/1.25/1.5 · 1 validata
     gen_c5194ce4: 4 trade, 1 vinto, R medio -0,66 · in panchina con high_uncertainty · 1 validata (1 declassate)
     gen_ceab7f6a: 4 trade, 2 vinti, R medio -0,19 · 1 validata (1 declassate)
     gen_fb7d035a: 4 trade, 2 vinti, R medio -0,38 · 1 validata (1 declassate)
     gen_fca11c08: 4 trade, 3 vinti, R medio +0,26 · ipotesi conferma_trend · scala propria 0.75/1/1.5 · 0 validate
     gen_490a90e5: 3 trade, 2 vinti, R medio -0,05 · scala propria 0.5/0.75/1 · 0 validate
     gen_658b2edb: 3 trade, 3 vinti, R medio +0,49 · 2 validate (2 declassate)
     gen_771790b1: 3 trade, 1 vinto, R medio -0,52 · 1 validata (1 declassate)

--- stderr ---
/root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
  return query.where(field_path, op_string, value)
```
