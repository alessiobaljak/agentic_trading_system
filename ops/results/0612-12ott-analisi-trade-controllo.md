# 0612-12ott-analisi-trade-controllo.req

_eseguito: 2026-10-12 19:07 UTC_

**richiesta:** `controllo`
**eseguito:** `.venv/bin/python -m scripts.controllo`
**esito:** codice 0 in 6.3s

```
[firebase] connesso (Firestore + RTDB)
CONTROLLO AUTOMATICO — generato da ops alle 2026-10-12 19:07 UTC (durata 3751 ms, impostazioni: default repo)
  semaforo SISTEMA: VERDE    semaforo PAPER: GIALLO
  controllo precedente: 2026-10-12 18:58 UTC
  sezioni fallite: nessuna

ANOMALIE (1):
  [giallo] FRENO_GLOBALE (paper): freno globale da deriva: PF 0,71 vs 2,03 atteso (valore 0.709, soglia 1.216)

LETTURE:
  salute:    Bot vivo (battito 14 s fa), gate 17 min fa (completa), 4 posizioni, 0,8% a rischio. 1 avviso: freno globale.
  paper:     511 trade in 26 giorni, 56% vinti, -123,77 USDT (-12,4%). BTC dal primo giorno +8,8% (noi -12,4%). Oggi -0,60 (validate -2,02).
  learning:  Attivo: freno globale, 11 strategie in panchina, keep per coppia 0.35 ×48, 0.5 ×53, 0.65 ×113, 0.75 ×12, 1 cooldown. Solo misurato: deriva.

LETTURE FIRESTORE DEL BOT (ultime 24 h, quota gratuita 50.000/giorno):
  non misurate in questo documento (le conta solo il bot: vedi il controllo orario)

CAMBIAMENTI DEL LEARNING rispetto al controllo di un'ora fa (precedente: 2026-10-12 18:58 UTC). NON e' il confronto con ieri: quello e' nella STORIA DEL LEARNING, in fondo
  nessuno nell'ultima ora: nessun pezzo del learning ha cambiato decisione

PAPER CONTRO IL CASO (prezzo casuale con le nostre uscite):
  stop 44% (caso 46%) · stop d'ingresso/uscita 46/54% (caso 48.5/51.5%) · massimo toccato mediano 0.80R (caso 0.81R) · vinti 55% (caso 54%)
  fonte del caso: simulazione del 30 set su prezzo casuale, docs/revisione_sospese_30set.md e backlog K4: costanti, non ricalcolate. Vicino al caso = le classi d'uscita sono la forma delle regole, non una diagnosi. R medio (caso -0.067) e primo target (caso 17%): in `trades`

COSA QUESTO CONTROLLO NON PUO' DARE:
  - cosa aspetta il si' del proprietario: vive in docs/backlog.md, non e' un dato del sistema -> leggere docs/backlog.md (gruppo 1 dell'indice)

STORIA DEL LEARNING (foto dello stato scattata dal bot alla prima ora di ogni giorno italiano, RTDB /learning_giorni; da qui in giu' gli orari sono in ora italiana, quelli sopra in UTC):
  foto di ieri 11 ott 00:44, foto di oggi 12 ott 00:52: i confronti «ieri» e «stanotte» qui sotto vengono da queste

COME IMPARA IL TRAILING (il keep e' la parte del guadagno che il trailing blocca quando si arma: con 0,5 tiene meta' del miglior guadagno visto; piu' alto = stop piu' vicino)
  a) COSA HA VISTO IL PAPER: dopo ogni uscita del trailing guarda dove va il prezzo nelle 24 ore dopo
     prematuro = poi e' arrivato al target: usciti troppo presto («da rumore» se lo stop e' scattato su un ritorno indietro piu' piccolo del movimento medio di una candela)
     protetto = poi e' tornato allo stop iniziale: l'uscita ha salvato il guadagno; neutro = ne' l'uno ne' l'altro
     uscite del trailing sulle candele da 15 minuti (le sole che contano per le proposte): 198 verdetti = 100 prematuri (24 da rumore) + 98 protetti; in piu' 22 neutri
     uscite dopo un incasso parziale (preso almeno il primo target, resto chiuso dallo stop): 48 verdetti (25 prematuri, 23 protetti, 0 neutri), NON usati dalle proposte (se contarli non e' deciso)
     dopo gli stop: 47 rumore (il prezzo e' poi tornato al primo target), 172 inversione (ha continuato contro, o non e' tornato al primo target entro la finestra): nessuna regola li usa ancora
     nuovi ieri (11 ott): trailing 3 prematuri, 6 protetti, 2 neutri · dopo un incasso parziale 0 prematuri, 2 protetti, 0 neutri · stop 6 rumore, 10 inversione
     nuovi stanotte (12 ott): trailing 9 prematuri, 2 protetti, 0 neutri · dopo un incasso parziale 5 prematuri, 2 protetti, 0 neutri · stop 3 rumore, 7 inversione
  b) COSA PROPONE IL PAPER AL GATE (una proposta e' un candidato in piu' che il gate prova sulla storia: il paper propone, il gate sceglie)
     keep per tutte le coppie: 98 protetti su 198 verdetti = 49,5% (serve il 60%): nessuna proposta. Mancano 52 protetti per proporre 0,75 (oppure 47 prematuri per 0,25)
     keep per strategia (servono 5 verdetti della strategia): 4 strategie propongono (gen_ceab7f6a 0,75, gen_4465723e 0,75, gen_4c6df481 0,25 e altre 1). Le piu' vicine:
       gen_490a90e5 4 protetti su 4: manca 1 protetto per 0,75
       gen_8c9b332f 3 prematuri (1 da rumore) su 4: manca 1 prematuro da rumore per 0,25
       gen_902fb1fd 2 protetti su 4: manca 1 protetto per 0,75
     keep imparato dal bot da solo (vale solo per le coppie senza keep del gate; servono 8 verdetti per strategia, esplorative escluse): nessuna strategia (la piu' avanti ha 6 verdetti su 8)
     scala dei target di incasso dal vissuto (multipli del rischio iniziale: «1/2/3» = incassi a 1, 2 e 3 volte il rischio), ultimo giro del gate (12 ott 20:50): 0.75/1.25/2; keep proposto: nessuno
     strategie con una scala propria (almeno 5 trade col massimo guadagno raggiunto misurato): 30
  c) COSA HA SCELTO IL GATE per le 229 validate che il bot opera (per coppia; «non scelto» = coppia non ancora ripassata dal gate: vale il default)
     keep: 0,65 ×113 · 0,5 ×53 · 0,35 ×48 · 0,75 ×12 · non scelto ×3 (default 0,5). Dalle proposte del paper (0,25 e 0,75 esistono solo cosi'): 12
     scala dei target: 1.5/3/5 ×110 · 2/4/6 ×77 · 1/2/3 ×15 · 1/1.5/2.5 ×14 · altre 2 (×13) (default 1.5/3/5); dal vissuto in tutto: 13
     stop spostato al prezzo d'ingresso dopo il primo incasso (break-even): si ×229 (default si)
     cambiato ieri (foto 11 ott 00:44 -> foto 12 ott 00:52): 1 coppie su 208 hanno cambiato keep, scala o break-even (validate +22 / -30)
       MAVIAUSDT|gen_608b892e: scala 1/1.5/2.5 -> 1.5/3/5
     cambiato stanotte (foto 12 ott 00:52 -> adesso): 2 coppie su 205 hanno cambiato keep, scala o break-even (validate +24 / -25)
       SAHARAUSDT|gen_b0d474bb: scala 1/2/3 -> 2/4/6
       ZORAUSDT|gen_f4e37ccc: scala 1.5/3/5 -> 2/4/6
  d) FUNZIONA? trade chiusi dal 25 set per keep in uso all'ingresso (gruppi NON confrontabili: coppie diverse; misura, non regola)
     keep 0,35: 32 trade · trailing armato in 20 dei 32 trade con referto (62,5%) · 8 prematuri, 7 protetti · R medio -0,04 · tavolo 0,80
     keep 0,5: 339 trade · trailing armato in 197 dei 339 trade con referto (58,1%) · 80 prematuri, 94 protetti · R medio -0,07 · tavolo 0,68
     keep 0,65: 64 trade · trailing armato in 37 dei 64 trade con referto (57,8%) · 20 prematuri, 11 protetti · R medio -0,17 · tavolo 0,71
     keep 0,75: 21 trade · trailing armato in 7 dei 21 trade con referto (33,3%) · 7 prematuri, 0 protetti · R medio -0,35 · tavolo 0,58
     R = guadagno in unita' del rischio iniziale; tavolo = parte del tragitto verso il target lasciata all'uscita trailing (0 = uscito al target, 1 = all'entrata)

COSA IMPARANO LE STRATEGIE (ipotesi dai referti del paper -> varianti giudicate dal gate sulla storia -> promozioni; e intanto declassate, esplorative, panchina, freno)
  IERI (11 ott, giornata intera ora italiana):
     - ipotesi nate dai referti 1: gen_4c6df481 scala_stretta «3 perdite sotto il primo gradino (mfe mediana 0.79 R)»
     - validate promosse 22: STXUSDT|gen_0aa0d29c, PHAUSDT|gen_bd109329, PARTIUSDT|gen_7b4a474b e altre 19; rimosse 23: FORMUSDT|gen_1eec02f5 (vissuta 14,2 giorni), TRUMPUSDT|gen_93131ef1, TRUMPUSDT|gen_108c996b e altre 20
     - declassate nuove 12 (size ridotta): HEMIUSDT|gen_c1f71d65, HUMAUSDT|gen_60c9259a, IDOLUSDT|gen_931ca7de e altre 9; declassate tornate piene 4: GPSUSDT|gen_871647b8, OPENUSDT|gen_4f25eca9, OPENUSDT|gen_b9bf5d01 e altre 1
     - esplorative: entrate 46, promosse a validate 0, scartate 47
     - panchina (strategia×regime con peso sotto 0,5: size ridotta): nessuna entra; escono gen_ceab7f6a|sideways (0,5491)
     - ipotesi non piu' nei referti 1: gen_ceab7f6a|ingresso_vol_ratio
  STANOTTE (12 ott dalle 00:00 alle 21:07 ora italiana):
     - validate promosse 24: JTOUSDT|gen_94062d5f, BANKUSDT|gen_7100bb59, DEXEUSDT|gen_3d4be8c7 e altre 21; rimosse 25: AIOUSDT|gen_581d4a68 (vissuta 14,1 giorni), QUSDT|gen_bf2be656, QUSDT|gen_1e7e2564 (vissuta 14,1 giorni) e altre 22
     - declassate nuove 6 (size ridotta): BANKUSDT|gen_7100bb59, BMTUSDT|gen_be64073c, PARTIUSDT|gen_64263ae7 e altre 3; declassate tornate piene 2: BULLAUSDT|gen_5a52c06b, RAYSOLUSDT|gen_a01bcc1a
     - esplorative: entrate 56, promosse a validate 0, scartate 56
     - cooldown (fermo dopo 3 stop di fila) fra le due foto: iniziati coin BANKUSDT
     - ipotesi non piu' nei referti 2: gen_fa304106|conferma_trend, gen_fa304106|solo_short
  PER STRATEGIA (le 10 con piu' trade chiusi negli ultimi 7 giorni; R = guadagno in unita' del rischio iniziale):
     gen_ceab7f6a: 9 trade, 5 vinti, R medio -0,19 · ipotesi ingresso_vol_ratio · keep proposto 0,75 · scala propria 0.75/1.25/1.75 · 0 validate
     gen_c647ead7: 6 trade, 4 vinti, R medio -0,23 · scala propria 0.5/0.75/1 · 3 validate (2 declassate)
     gen_96c1ed1b: 5 trade, 2 vinti, R medio -0,22 · scala propria 0.75/1.25/3.5 · 1 validata (1 declassate)
     gen_1eec02f5: 4 trade, 3 vinti, R medio +0,20 · scala propria 1/1.25/2.25 · 2 validate
     gen_5a52c06b: 4 trade, 2 vinti, R medio -0,17 · 2 validate (1 declassate)
     gen_684d7623: 4 trade, 3 vinti, R medio -0,01 · 1 validata (1 declassate)
     gen_9a383fff: 4 trade, 2 vinti, R medio -0,30 · scala propria 0.75/1.25/1.5 · 2 validate (1 declassate)
     gen_e09c5203: 4 trade, 2 vinti, R medio -0,06 · 1 validata (1 declassate)
     gen_fa304106: 4 trade, 1 vinto, R medio -0,68 · ipotesi controtrend_btc, scala_stretta, solo_long · in panchina con bear_trending, bull_trending, high_uncertainty, sideways · scala propria 0.5/0.75/1 · 0 validate
     gen_18c839a0: 3 trade, 0 vinti, R medio -1,06 · scala propria 1/1.25/1.5 · 1 validata (1 declassate)

--- stderr ---
/root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
  return query.where(field_path, op_string, value)
```
