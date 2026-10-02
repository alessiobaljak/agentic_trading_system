# 0432-2ott-mattina-controllo.req

_eseguito: 2026-10-02 06:17 UTC_

**richiesta:** `controllo`
**eseguito:** `.venv/bin/python -m scripts.controllo`
**esito:** codice 0 in 4.7s

```
[firebase] connesso (Firestore + RTDB)
CONTROLLO AUTOMATICO — generato da ops alle 2026-10-02 06:17 UTC (durata 2436 ms, impostazioni: default repo)
  semaforo SISTEMA: VERDE    semaforo PAPER: GIALLO
  controllo precedente: 2026-10-02 05:30 UTC
  sezioni fallite: nessuna

ANOMALIE (2):
  [giallo] FRENO_GLOBALE (paper): freno globale da deriva: PF 0,69 vs 2,03 atteso (valore 0.694, soglia 1.219)
  [giallo] SENZA_PROMESSA (paper): 123 validate su 212 senza promessa (last_pf) (valore 0.58, soglia 0.3)

LETTURE:
  salute:    Bot vivo (battito 27 s fa), gate 27 min fa (solo urgenti), 4 posizioni, 0,8% a rischio. 2 avvisi: freno globale, validate senza promessa.
  paper:     224 trade in 15 giorni, 55% vinti, -77,22 USDT (-7,7%). BTC dal primo giorno +14,0% (noi -7,7%). Stop nel 46% delle uscite. Oggi +3,32.
  learning:  Attivo: freno globale, 10 strategie in panchina, keep per coppia 0.35 ×16, 0.5 ×14, 0.65 ×10, 0.75 ×14, 3 cooldown. Solo misurato: deriva.

LETTURE FIRESTORE DEL BOT (ultime 24 h, quota gratuita 50.000/giorno):
  non misurate in questo documento (le conta solo il bot: vedi il controllo orario)

CAMBIAMENTI DEL LEARNING rispetto al controllo di un'ora fa (precedente: 2026-10-02 05:30 UTC). NON e' il confronto con ieri: quello e' nella STORIA DEL LEARNING, in fondo
  - cooldown AIOUSDT attivo
  - cooldown HUMAUSDT attivo

PAPER CONTRO IL CASO (prezzo casuale con le nostre uscite):
  stop 46% (caso 46%) · stop d'ingresso/uscita 46/53% (caso 48.5/51.5%) · massimo toccato mediano 0.84R (caso 0.81R) · vinti 54% (caso 54%)
  fonte del caso: simulazione del 30 set su prezzo casuale, docs/revisione_sospese_30set.md e backlog K4: costanti, non ricalcolate. Vicino al caso = le classi d'uscita sono la forma delle regole, non una diagnosi. R medio (caso -0.067) e primo target (caso 17%): in `trades`

COSA QUESTO CONTROLLO NON PUO' DARE:
  - cosa aspetta il si' del proprietario: vive in docs/backlog.md, non e' un dato del sistema -> leggere docs/backlog.md (gruppo 1 dell'indice)

STORIA DEL LEARNING (foto dello stato scattata dal bot alla prima ora di ogni giorno italiano, RTDB /learning_giorni; da qui in giu' gli orari sono in ora italiana, quelli sopra in UTC):
  foto di ieri 1 ott 00:16, foto di oggi 2 ott 00:28: i confronti «ieri» e «stanotte» qui sotto vengono da queste

COME IMPARA IL TRAILING (il keep e' la parte del guadagno che il trailing blocca quando si arma: con 0,5 tiene meta' del miglior guadagno visto; piu' alto = stop piu' vicino)
  a) COSA HA VISTO IL PAPER: dopo ogni uscita del trailing guarda dove va il prezzo nelle 24 ore dopo
     prematuro = poi e' arrivato al target: usciti troppo presto («da rumore» se lo stop e' scattato su un ritorno indietro piu' piccolo del movimento medio di una candela)
     protetto = poi e' tornato allo stop iniziale: l'uscita ha salvato il guadagno; neutro = ne' l'uno ne' l'altro
     uscite del trailing sulle candele da 15 minuti (le sole che contano per le proposte): 87 verdetti = 38 prematuri (6 da rumore) + 49 protetti; in piu' 10 neutri
     uscite dopo un incasso parziale (preso almeno il primo target, resto chiuso dallo stop): 20 verdetti (12 prematuri, 8 protetti, 0 neutri), NON usati dalle proposte (se contarli non e' deciso)
     dopo gli stop: 25 rumore (il prezzo e' poi tornato al primo target), 71 inversione (ha continuato contro, o non e' tornato al primo target entro la finestra): nessuna regola li usa ancora
     nuovi ieri (1 ott): trailing 3 prematuri, 3 protetti, 0 neutri · stop 1 rumore, 8 inversione
     nuovi stanotte (2 ott): trailing 0 prematuri, 3 protetti, 0 neutri · dopo un incasso parziale 1 prematuro, 0 protetti, 0 neutri · stop 0 rumore, 2 inversione
  b) COSA PROPONE IL PAPER AL GATE (una proposta e' un candidato in piu' che il gate prova sulla storia: il paper propone, il gate sceglie)
     keep per tutte le coppie: 49 protetti su 87 verdetti = 56,3% (serve il 60%): nessuna proposta. Mancano 8 protetti per proporre 0,75 (oppure 36 prematuri per 0,25)
     keep per strategia (servono 5 verdetti della strategia): nessuna propone, su 54 con verdetti. Le piu' vicine:
       gen_490a90e5 4 protetti su 4: manca 1 protetto per 0,75
       gen_bb762669 2 protetti su 4: manca 1 protetto per 0,75
       gen_fca11c08 3 protetti su 4: manca 1 protetto per 0,75
     keep imparato dal bot da solo (vale solo per le coppie senza keep del gate; servono 8 verdetti per strategia, esplorative escluse): nessuna strategia (la piu' avanti ha 4 verdetti su 8)
     scala dei target di incasso dal vissuto (multipli del rischio iniziale: «1/2/3» = incassi a 1, 2 e 3 volte il rischio), ultimo giro del gate (2 ott 07:50): 0.75/1.25/1.75; keep proposto: nessuno
     strategie con una scala propria (almeno 5 trade col massimo guadagno raggiunto misurato): 13
  c) COSA HA SCELTO IL GATE per le 212 validate che il bot opera (per coppia; «non scelto» = coppia non ancora ripassata dal gate: vale il default)
     keep: non scelto ×158 · 0,35 ×16 · 0,5 ×14 · 0,75 ×14 · 0,65 ×10 (default 0,5). Dalle proposte del paper (0,25 e 0,75 esistono solo cosi'): 14
     scala dei target: 2/4/6 ×113 · 1.5/3/5 ×81 · 1/1.5/2.5 ×7 · 1/2/3 ×6 · altre 4 (×5) (default 1.5/3/5); dal vissuto in tutto: 5
     stop spostato al prezzo d'ingresso dopo il primo incasso (break-even): non scelto ×139 · si ×73 (default si)
     cambiato ieri (foto 1 ott 00:16 -> foto 2 ott 00:28): nessuna delle 202 coppie presenti in entrambe le foto ha cambiato keep, scala o break-even (validate +7 / -0)
     cambiato stanotte (foto 2 ott 00:28 -> adesso): 1 coppie su 209 hanno cambiato keep, scala o break-even (validate +3 / -0)
       PNUTUSDT|gen_4810faab: keep default -> 0,5; break-even default -> si
  d) FUNZIONA? trade chiusi dal 25 set per keep in uso all'ingresso (gruppi NON confrontabili: coppie diverse; misura, non regola)
     keep 0,35: 5 trade · trailing armato in 5 dei 5 trade con referto (100,0%) · 2 prematuri, 3 protetti · R medio +0,43 · tavolo 0,75
     keep 0,5: 149 trade · trailing armato in 88 dei 149 trade con referto (59,1%) · 33 prematuri, 44 protetti · R medio -0,11 · tavolo 0,70
     keep 0,65: 5 trade · trailing armato in 3 dei 5 trade con referto (60,0%) · 2 prematuri, 1 protetto · R medio +0,11 · tavolo 0,53
     keep 0,75: 10 trade · trailing armato in 4 dei 10 trade con referto (40,0%) · 3 prematuri, 0 protetti · R medio -0,25 · tavolo 0,53
     R = guadagno in unita' del rischio iniziale; tavolo = parte del tragitto verso il target lasciata all'uscita trailing (0 = uscito al target, 1 = all'entrata)

COSA IMPARANO LE STRATEGIE (ipotesi dai referti del paper -> varianti giudicate dal gate sulla storia -> promozioni; e intanto declassate, esplorative, panchina, freno)
  IERI (1 ott, giornata intera ora italiana):
     - ipotesi nate dai referti 1: gen_fa304106 solo_short «long 3/3 persi»
     - varianti dalle ipotesi: create 1: gen_fa304106 solo_short (variante gen_45579407); bocciate 1: gen_fa304106 solo_short (variante gen_45579407)
     - validate promosse 7: ZORAUSDT|gen_f4e37ccc, USELESSUSDT|gen_96c1ed1b, TAUSDT|gen_4e6e1ae0 e altre 4; rimosse 0
     - declassate nuove 2 (size ridotta): NEIROUSDT|gen_413f1bd7, UBUSDT|gen_08664b28
     - esplorative: entrate 81, promosse a validate 0, scartate 79
     - panchina (strategia×regime con peso sotto 0,5: size ridotta): entrano gen_b2f350ff|sideways (0,4572), gen_c0fd1d91|high_uncertainty (0,4572), gen_fa304106|high_uncertainty (0,4572)
     - cooldown (fermo dopo 3 stop di fila) fra le due foto: iniziati coin TAUSDT
  STANOTTE (2 ott dalle 00:00 alle 08:17 ora italiana):
     - validate promosse 3: MUBARAKUSDT|gen_f86f7370, RENDERUSDT|gen_fdaa6e0b, SKYAIUSDT|gen_4cadc09b; rimosse 0
     - declassate nuove 2 (size ridotta): UBUSDT|gen_887d87df, USELESSUSDT|gen_e09c5203; declassate tornate piene 1: PNUTUSDT|gen_4810faab
     - esplorative: entrate 41, promosse a validate 0, scartate 19
     - cooldown (fermo dopo 3 stop di fila) fra le due foto: iniziati coin AIOUSDT, coin BULLAUSDT, coin HUMAUSDT; finiti coin TAUSDT
  PER STRATEGIA (le 10 con piu' trade chiusi negli ultimi 7 giorni; R = guadagno in unita' del rischio iniziale):
     gen_fca11c08: 14 trade, 7 vinti, R medio -0,26 · ipotesi conferma_trend · scala propria 0.75/1/1.5 · 0 validate
     gen_490a90e5: 7 trade, 5 vinti, R medio -0,03 · scala propria 0.5/0.75/1 · 0 validate
     gen_bb762669: 7 trade, 5 vinti, R medio +0,01 · scala propria 0.75/1/1.5 · 2 validate (1 declassate)
     gen_4c6df481: 5 trade, 3 vinti, R medio +0,20 · in panchina con sideways · scala propria 1/1.25/2.25 · 1 validata
     gen_cd5c842f: 5 trade, 4 vinti, R medio +0,33 · scala propria 1/1.25/2 · 1 validata (1 declassate)
     gen_e59ad90b: 5 trade, 4 vinti, R medio +0,28 · scala propria 0.75/1/2.5 · 1 validata (1 declassate)
     gen_4465723e: 4 trade, 4 vinti, R medio +0,49 · scala propria 0.75/1.5/1.75 · 1 validata (1 declassate)
     gen_658b2edb: 4 trade, 4 vinti, R medio +0,49 · 2 validate (2 declassate)
     gen_771790b1: 4 trade, 2 vinti, R medio -0,17 · 1 validata (1 declassate)
     gen_a640dfa5: 4 trade, 4 vinti, R medio +0,53 · 2 validate (2 declassate)

--- stderr ---
/root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
  return query.where(field_path, op_string, value)
```
