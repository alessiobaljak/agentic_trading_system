# 0580-10ott-mattina-controllo.req

_eseguito: 2026-10-10 04:06 UTC_

**richiesta:** `controllo`
**eseguito:** `.venv/bin/python -m scripts.controllo`
**esito:** codice 0 in 5.6s

```
[firebase] connesso (Firestore + RTDB)
CONTROLLO AUTOMATICO — generato da ops alle 2026-10-10 04:06 UTC (durata 3225 ms, impostazioni: default repo)
  semaforo SISTEMA: GIALLO   semaforo PAPER: GIALLO
  controllo precedente: 2026-10-10 03:40 UTC
  sezioni fallite: nessuna

ANOMALIE (2):
  [giallo] FRENO_GLOBALE (paper): freno globale da deriva: PF 0,71 vs 2,02 atteso (valore 0.712, soglia 1.211)
  [giallo] GATE_SFORA (sistema): il giro del gate e' durato 3 h 46 (piu' di 3 h) (valore 13619, soglia 10800)

LETTURE:
  salute:    Bot vivo (battito 16 s fa), gate 2 h 56 fa (completa), 4 posizioni, 0,5% a rischio. 2 avvisi: freno globale, gate lento.
  paper:     440 trade in 23 giorni, 55% vinti, -109,42 USDT (-10,9%). BTC dal primo giorno +9,0% (noi -10,9%). Stop nel 44% delle uscite. Oggi -3,50.
  learning:  Attivo: freno globale, 12 strategie in panchina, keep per coppia 0.35 ×43, 0.5 ×45, 0.65 ×76, 0.75 ×14. Solo misurato: deriva, calibrazione.

LETTURE FIRESTORE DEL BOT (ultime 24 h, quota gratuita 50.000/giorno):
  non misurate in questo documento (le conta solo il bot: vedi il controllo orario)

CAMBIAMENTI DEL LEARNING rispetto al controllo di un'ora fa (precedente: 2026-10-10 03:40 UTC). NON e' il confronto con ieri: quello e' nella STORIA DEL LEARNING, in fondo
  nessuno nell'ultima ora: nessun pezzo del learning ha cambiato decisione

PAPER CONTRO IL CASO (prezzo casuale con le nostre uscite):
  stop 44% (caso 46%) · stop d'ingresso/uscita 45/54% (caso 48.5/51.5%) · massimo toccato mediano 0.80R (caso 0.81R) · vinti 55% (caso 54%)
  fonte del caso: simulazione del 30 set su prezzo casuale, docs/revisione_sospese_30set.md e backlog K4: costanti, non ricalcolate. Vicino al caso = le classi d'uscita sono la forma delle regole, non una diagnosi. R medio (caso -0.067) e primo target (caso 17%): in `trades`

COSA QUESTO CONTROLLO NON PUO' DARE:
  - cosa aspetta il si' del proprietario: vive in docs/backlog.md, non e' un dato del sistema -> leggere docs/backlog.md (gruppo 1 dell'indice)

STORIA DEL LEARNING (foto dello stato scattata dal bot alla prima ora di ogni giorno italiano, RTDB /learning_giorni; da qui in giu' gli orari sono in ora italiana, quelli sopra in UTC):
  foto di ieri 9 ott 00:33, foto di oggi 10 ott 00:38: i confronti «ieri» e «stanotte» qui sotto vengono da queste

COME IMPARA IL TRAILING (il keep e' la parte del guadagno che il trailing blocca quando si arma: con 0,5 tiene meta' del miglior guadagno visto; piu' alto = stop piu' vicino)
  a) COSA HA VISTO IL PAPER: dopo ogni uscita del trailing guarda dove va il prezzo nelle 24 ore dopo
     prematuro = poi e' arrivato al target: usciti troppo presto («da rumore» se lo stop e' scattato su un ritorno indietro piu' piccolo del movimento medio di una candela)
     protetto = poi e' tornato allo stop iniziale: l'uscita ha salvato il guadagno; neutro = ne' l'uno ne' l'altro
     uscite del trailing sulle candele da 15 minuti (le sole che contano per le proposte): 172 verdetti = 84 prematuri (19 da rumore) + 88 protetti; in piu' 19 neutri
     uscite dopo un incasso parziale (preso almeno il primo target, resto chiuso dallo stop): 39 verdetti (20 prematuri, 19 protetti, 0 neutri), NON usati dalle proposte (se contarli non e' deciso)
     dopo gli stop: 38 rumore (il prezzo e' poi tornato al primo target), 149 inversione (ha continuato contro, o non e' tornato al primo target entro la finestra): nessuna regola li usa ancora
     nuovi ieri (9 ott): trailing 7 prematuri, 6 protetti, 2 neutri · dopo un incasso parziale 2 prematuri, 3 protetti, 0 neutri · stop 1 rumore, 7 inversione
     nuovi stanotte (10 ott): trailing 2 prematuri, 0 protetti, 0 neutri · stop 0 rumore, 1 inversione
  b) COSA PROPONE IL PAPER AL GATE (una proposta e' un candidato in piu' che il gate prova sulla storia: il paper propone, il gate sceglie)
     keep per tutte le coppie: 88 protetti su 172 verdetti = 51,2% (serve il 60%): nessuna proposta. Mancano 38 protetti per proporre 0,75 (oppure 48 prematuri per 0,25)
     keep per strategia (servono 5 verdetti della strategia): 2 strategie propongono (gen_4465723e 0,75, gen_e59ad90b 0,75). Le piu' vicine:
       gen_490a90e5 4 protetti su 4: manca 1 protetto per 0,75
       gen_4c6df481 3 prematuri (3 da rumore) su 4: manca 1 prematuro da rumore per 0,25
       gen_8c9b332f 3 prematuri (1 da rumore) su 4: manca 1 prematuro da rumore per 0,25
     keep imparato dal bot da solo (vale solo per le coppie senza keep del gate; servono 8 verdetti per strategia, esplorative escluse): nessuna strategia (la piu' avanti ha 5 verdetti su 8)
     scala dei target di incasso dal vissuto (multipli del rischio iniziale: «1/2/3» = incassi a 1, 2 e 3 volte il rischio), ultimo giro del gate (10 ott 03:10): 0.75/1.25/1.75; keep proposto: nessuno
     strategie con una scala propria (almeno 5 trade col massimo guadagno raggiunto misurato): 27
  c) COSA HA SCELTO IL GATE per le 236 validate che il bot opera (per coppia; «non scelto» = coppia non ancora ripassata dal gate: vale il default)
     keep: 0,65 ×76 · non scelto ×58 · 0,5 ×45 · 0,35 ×43 · 0,75 ×14 (default 0,5). Dalle proposte del paper (0,25 e 0,75 esistono solo cosi'): 14
     scala dei target: 1.5/3/5 ×104 · 2/4/6 ×97 · 1/1.5/2.5 ×17 · 1/2/3 ×10 · altre 2 (×8) (default 1.5/3/5); dal vissuto in tutto: 8
     stop spostato al prezzo d'ingresso dopo il primo incasso (break-even): si ×187 · non scelto ×49 (default si)
     cambiato ieri (foto 9 ott 00:33 -> foto 10 ott 00:38): 1 coppie su 214 hanno cambiato keep, scala o break-even (validate +22 / -24)
       UBUSDT|gen_53b10d52: keep default -> 0,35
     cambiato stanotte (foto 10 ott 00:38 -> adesso): nessuna delle 236 coppie presenti in entrambe le foto ha cambiato keep, scala o break-even
  d) FUNZIONA? trade chiusi dal 25 set per keep in uso all'ingresso (gruppi NON confrontabili: coppie diverse; misura, non regola)
     keep 0,35: 19 trade · trailing armato in 13 dei 19 trade con referto (68,4%) · 4 prematuri, 6 protetti · R medio -0,00 · tavolo 0,80
     keep 0,5: 309 trade · trailing armato in 178 dei 309 trade con referto (57,6%) · 72 prematuri, 85 protetti · R medio -0,07 · tavolo 0,68
     keep 0,65: 41 trade · trailing armato in 23 dei 41 trade con referto (56,1%) · 12 prematuri, 7 protetti · R medio -0,21 · tavolo 0,72
     keep 0,75: 16 trade · trailing armato in 6 dei 16 trade con referto (37,5%) · 6 prematuri, 0 protetti · R medio -0,27 · tavolo 0,61
     R = guadagno in unita' del rischio iniziale; tavolo = parte del tragitto verso il target lasciata all'uscita trailing (0 = uscito al target, 1 = all'entrata)

COSA IMPARANO LE STRATEGIE (ipotesi dai referti del paper -> varianti giudicate dal gate sulla storia -> promozioni; e intanto declassate, esplorative, panchina, freno)
  IERI (9 ott, giornata intera ora italiana):
     - validate promosse 22: HUMAUSDT|gen_60c9259a, IDOLUSDT|gen_931ca7de, AINUSDT|gen_d8656ab7 e altre 19; rimosse 23: ENAUSDT|gen_bb762669, DOTUSDT|gen_919c110c, SEIUSDT|gen_4f890271 e altre 20
     - declassate nuove 8 (size ridotta): AINUSDT|gen_ef115241, BTRUSDT|gen_5a52c06b, BULLAUSDT|gen_5a52c06b e altre 5; declassate tornate piene 2: AVAAIUSDT|gen_08c22b92, UBUSDT|gen_53b10d52
     - esplorative: entrate 47, promosse a validate 0, scartate 55
     - panchina (strategia×regime con peso sotto 0,5: size ridotta): nessuna entra; escono gen_5a52c06b|bear_trending (0,6117)
  STANOTTE (10 ott dalle 00:00 alle 06:06 ora italiana):
     - ipotesi nate dai referti 1: gen_ceab7f6a ingresso_vol_ratio «4 perdite d'ingresso su 5 con volume sotto la media (vol_ratio < 1) (mediana 0.71), vinti mediana 1.03»
     - esplorative: entrate 15, promosse a validate 0, scartate 0
  PER STRATEGIA (le 10 con piu' trade chiusi negli ultimi 7 giorni; R = guadagno in unita' del rischio iniziale):
     gen_ceab7f6a: 8 trade, 2 vinti, R medio -0,71 · ipotesi ingresso_vol_ratio · in panchina con sideways · scala propria 0.5/0.75/1.5 · 1 validata (1 declassate)
     gen_c647ead7: 6 trade, 4 vinti, R medio -0,23 · scala propria 0.5/0.75/1 · 3 validate (2 declassate)
     gen_96c1ed1b: 5 trade, 2 vinti, R medio -0,22 · scala propria 0.75/1.25/3.5 · 2 validate (2 declassate)
     gen_1eec02f5: 4 trade, 3 vinti, R medio +0,07 · 4 validate (2 declassate)
     gen_684d7623: 4 trade, 3 vinti, R medio -0,03 · 1 validata (1 declassate)
     gen_9a383fff: 4 trade, 2 vinti, R medio -0,30 · scala propria 0.75/1.25/1.5 · 3 validate (2 declassate)
     gen_e59ad90b: 4 trade, 2 vinti, R medio -0,40 · ipotesi conferma_trend · in panchina con bear_trending · keep proposto 0,75 · scala propria 0.75/1/1.25 · 0 validate
     gen_fa304106: 4 trade, 0 vinti, R medio -1,08 · ipotesi conferma_trend, controtrend_btc, scala_stretta, solo_long, solo_short · in panchina con bear_trending, bull_trending, high_uncertainty, sideways · scala propria 0.5/0.75/1 · 0 validate
     gen_4465723e: 3 trade, 2 vinti, R medio +0,04 · keep proposto 0,75 · scala propria 1.25/1.5/1.75 · 0 validate
     gen_4c6df481: 3 trade, 1 vinto, R medio -0,63 · in panchina con sideways · scala propria 1/1.25/1.5 · 1 validata

--- stderr ---
/root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
  return query.where(field_path, op_string, value)
```
