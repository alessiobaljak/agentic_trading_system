# 0353-controllo-sezioni-nuove.req

_eseguito: 2026-09-29 08:13 UTC_

**richiesta:** `controllo`
**eseguito:** `.venv/bin/python -m scripts.controllo`
**esito:** codice 0 in 4.7s

```
[firebase] connesso (Firestore + RTDB)
CONTROLLO AUTOMATICO — generato da ops alle 2026-09-29 08:13 UTC (durata 2481 ms, impostazioni: default repo)
  semaforo SISTEMA: VERDE    semaforo PAPER: GIALLO
  controllo precedente: 2026-09-29 08:12 UTC
  sezioni fallite: nessuna

ANOMALIE (2):
  [giallo] FRENO_GLOBALE (paper): freno globale da deriva: PF 0,70 vs 2,03 atteso (valore 0.699, soglia 1.219)
  [giallo] SENZA_PROMESSA (paper): 125 validate su 199 senza promessa (last_pf) (valore 0.628, soglia 0.3)

LETTURE:
  salute:    Bot vivo (battito 1 min fa), gate 8 min fa (solo urgenti), 2 posizioni, 0,2% a rischio. 2 avvisi: freno globale, validate senza promessa.
  paper:     175 trade in 12 giorni, 55% vinti, -66,83 USDT (-6,7%). BTC dal primo giorno +10,9% (noi -6,7%). Oggi +1,78 (validate +0,74).
  learning:  Attivo: freno globale, 6 strategie in panchina, keep per coppia 0.35 ×12, 0.5 ×7, 0.65 ×6, 0.75 ×14. Solo misurato: deriva, calibrazione.

LETTURE FIRESTORE DEL BOT (ultime 24 h, quota gratuita 50.000/giorno):
  non misurate in questo documento (le conta solo il bot: vedi il controllo orario)

CAMBIAMENTI DEL LEARNING dal controllo precedente:
  nessuno: nessun pezzo del learning ha cambiato decisione

COSA QUESTO CONTROLLO NON PUO' DARE:
  - cosa aspetta il si' del proprietario: vive in docs/backlog.md, non e' un dato del sistema -> leggere docs/backlog.md (voce F1 per il learning)

STORIA DEL LEARNING (foto dello stato scattata dal bot alla prima ora di ogni giorno italiano, RTDB /learning_giorni; da qui in giu' gli orari sono in ora italiana, quelli sopra in UTC):
  manca la foto del 28 set (bot fermo tutto il giorno o foto non riuscita): confronto «ieri» fra stati non disponibile; la storia parte dal 29 set (foto delle 10:12)
  gli eventi con una data (ipotesi, varianti, promozioni, declassate nuove, esplorative, verdetti) si leggono comunque

COME IMPARA IL TRAILING (il keep e' la parte del guadagno che il trailing blocca quando si arma: con 0,5 tiene meta' del miglior guadagno visto; piu' alto = stop piu' vicino)
  a) COSA HA VISTO IL PAPER: dopo ogni uscita del trailing guarda dove va il prezzo nelle 24 ore dopo
     prematuro = poi e' arrivato al target: usciti troppo presto («da rumore» se lo stop e' scattato su un ritorno indietro piu' piccolo del movimento medio di una candela)
     protetto = poi e' tornato allo stop iniziale: l'uscita ha salvato il guadagno; neutro = ne' l'uno ne' l'altro
     uscite del trailing sulle candele da 15 minuti (le sole che contano per le proposte): 64 verdetti = 26 prematuri (4 da rumore) + 38 protetti; in piu' 7 neutri
     uscite dopo un incasso parziale (preso almeno il primo target, resto chiuso dallo stop): 18 verdetti (11 prematuri, 7 protetti, 0 neutri), NON usati dalle proposte (se contarli non e' deciso)
     dopo gli stop: 23 rumore (il prezzo e' poi tornato al primo target), 53 inversione (ha continuato contro, o non e' tornato al primo target entro la finestra): nessuna regola li usa ancora
     nuovi ieri (28 set): trailing 8 prematuri, 10 protetti, 0 neutri · dopo un incasso parziale 0 prematuri, 3 protetti, 0 neutri · stop 0 rumore, 2 inversione (23 senza data: contati nel giorno di uscita del trade, il verdetto puo' essere del giorno dopo)
     nuovi stanotte (29 set): trailing 1 prematuro, 2 protetti, 0 neutri · dopo un incasso parziale 1 prematuro, 0 protetti, 0 neutri · stop 4 rumore, 1 inversione (9 senza data, come sopra)
  b) COSA PROPONE IL PAPER AL GATE (una proposta e' un candidato in piu' che il gate prova sulla storia: il paper propone, il gate sceglie)
     keep per tutte le coppie: 38 protetti su 64 verdetti = 59,4% (serve il 60%): nessuna proposta. Manca 1 protetto per proporre 0,75 (oppure 31 prematuri per 0,25)
     keep per strategia (servono 5 verdetti della strategia): nessuna propone, su 42 con verdetti. Le piu' vicine:
       gen_490a90e5 4 protetti su 4: manca 1 protetto per 0,75
       gen_fca11c08 3 protetti su 4: manca 1 protetto per 0,75
       gen_2031005e 2 prematuri (1 da rumore) su 3: mancano 2 prematuri da rumore per 0,25
     keep imparato dal bot da solo (vale solo per le coppie senza keep del gate; servono 8 verdetti per strategia, esplorative escluse): nessuna strategia (la piu' avanti ha 4 verdetti su 8)
     scala dei target di incasso dal vissuto (multipli del rischio iniziale: «1/2/3» = incassi a 1, 2 e 3 volte il rischio), ultimo giro del gate (29 set 10:05): 1/1.25/1.75; keep proposto: nessuno
     strategie con una scala propria (almeno 5 trade col massimo guadagno raggiunto misurato): 8
  c) COSA HA SCELTO IL GATE per le 199 validate che il bot opera (per coppia; «non scelto» = coppia non ancora ripassata dal gate: vale il default)
     keep: non scelto ×160 · 0,75 ×14 · 0,35 ×12 · 0,5 ×7 · 0,65 ×6 (default 0,5). Dalle proposte del paper (0,25 e 0,75 esistono solo cosi'): 14
     scala dei target: 2/4/6 ×104 · 1.5/3/5 ×77 · 1/1.5/2.5 ×7 · 1/2/3 ×6 · altre 4 (×5) (default 1.5/3/5); dal vissuto in tutto: 5
     stop spostato al prezzo d'ingresso dopo il primo incasso (break-even): non scelto ×141 · si ×58 (default si)
     cambiato ieri: non disponibile (manca la foto del 28 set)
     cambiato stanotte (foto 29 set 10:12 -> adesso): nessuna delle 199 coppie presenti in entrambe le foto ha cambiato keep, scala o break-even
  d) FUNZIONA? trade chiusi dal 25 set per keep in uso all'ingresso (gruppi NON confrontabili: coppie diverse; misura, non regola)
     keep 0,35: 3 trade · trailing armato in 3 dei 3 trade con referto (100,0%) · 1 prematuro, 2 protetti · R medio +0,47 · tavolo 0,76
     keep 0,5: 111 trade · trailing armato in 68 dei 111 trade con referto (61,3%) · 23 prematuri, 34 protetti · R medio -0,08 · tavolo 0,69
     keep 0,65: 1 trade · trailing armato in 1 dei 1 trade con referto (100,0%) · 1 prematuro, 0 protetti · R medio +0,63 · tavolo 0,75
     keep 0,75: 5 trade · trailing armato in 2 dei 5 trade con referto (40,0%) · 2 prematuri, 0 protetti · R medio -0,14 · tavolo 0,46
     R = guadagno in unita' del rischio iniziale; tavolo = parte del tragitto verso il target lasciata all'uscita trailing (0 = uscito al target, 1 = all'entrata)

COSA IMPARANO LE STRATEGIE (ipotesi dai referti del paper -> varianti giudicate dal gate sulla storia -> promozioni; e intanto declassate, esplorative, panchina, freno)
  IERI (28 set, giornata intera ora italiana):
     - validate promosse 31: AIOUSDT|gen_581d4a68, QUSDT|gen_1e7e2564, THEUSDT|gen_a640dfa5 e altre 28; rimosse 0
     - declassate nuove 121 (size ridotta): ARCUSDT|gen_96c1ed1b, ATOMUSDT|gen_eaa569ba, AVAAIUSDT|gen_14e1775b e altre 118
     - esplorative: entrate 51, promosse a validate 0, scartate 63
     (panchina, cooldown, freno, declassate tornate piene, ipotesi sparite: non disponibili, manca la foto del 28 set)
  STANOTTE (29 set dalle 00:00 alle 10:13 ora italiana):
     - validate promosse 10: PUNDIXUSDT|gen_4810faab, UBUSDT|gen_08664b28, PARTIUSDT|gen_871647b8 e altre 7; rimosse 0
     - declassate nuove 23 (size ridotta): AVAAIUSDT|gen_e50a9211, BANKUSDT|gen_1efbb088, BANKUSDT|gen_fb3d971f e altre 20
     - esplorative: entrate 53, promosse a validate 0, scartate 35
  PER STRATEGIA (le 10 con piu' trade chiusi negli ultimi 7 giorni; R = guadagno in unita' del rischio iniziale):
     gen_fca11c08: 14 trade, 7 vinti, R medio -0,26 · ipotesi conferma_trend · scala propria 0.75/1/1.5 · 0 validate
     gen_490a90e5: 7 trade, 5 vinti, R medio -0,03 · scala propria 0.5/0.75/1 · 0 validate
     gen_cd5c842f: 5 trade, 4 vinti, R medio +0,33 · scala propria 1/1.25/2 · 1 validata (1 declassate)
     gen_4c6df481: 4 trade, 2 vinti, R medio +0,09 · in panchina con sideways · 1 validata
     gen_bb762669: 4 trade, 3 vinti, R medio +0,09 · 2 validate (1 declassate)
     gen_e50a9211: 4 trade, 2 vinti, R medio -0,27 · 1 validata (1 declassate)
     gen_18c839a0: 3 trade, 2 vinti, R medio +0,21 · 1 validata
     gen_2031005e: 3 trade, 2 vinti, R medio +0,72 · in panchina con high_uncertainty · scala propria 0.75/1/1.25 · 0 validate
     gen_35632db9: 3 trade, 2 vinti, R medio -0,06 · 0 validate
     gen_4465723e: 3 trade, 3 vinti, R medio +0,54 · scala propria 1.25/1.5/1.75 · 1 validata (1 declassate)

--- stderr ---
/root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
  return query.where(field_path, op_string, value)
```
