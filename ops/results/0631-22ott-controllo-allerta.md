# 0631-22ott-controllo-allerta.req

_eseguito: 2026-10-22 05:26 UTC_

**richiesta:** `controllo`
**eseguito:** `.venv/bin/python -m scripts.controllo`
**esito:** codice 0 in 7.4s

```
[firebase] connesso (Firestore + RTDB)
CONTROLLO AUTOMATICO — generato da ops alle 2026-10-22 05:26 UTC (durata 4846 ms, impostazioni: default repo)
  semaforo SISTEMA: ROSSO    semaforo PAPER: GIALLO
  controllo precedente: 2026-10-22 05:16 UTC
  sezioni fallite: nessuna

ANOMALIE (2):
  [rosso] GATE_IN_RITARDO (sistema): ultimo giro del gate 8 g 10 h fa (valore 729970, soglia 21600)
  [giallo] FRENO_GLOBALE (paper): freno globale da deriva: PF 0,72 vs 2,02 atteso (valore 0.721, soglia 1.212)

LETTURE:
  salute:    Bot vivo (battito 29 s fa), gate 8 g 10 h fa (solo urgenti), 0 posizioni, 0,0% a rischio. 2 avvisi: gate in ritardo, freno globale.
  paper:     784 trade in 35 giorni, 55% vinti, -182,75 USDT (-18,3%). BTC dal primo giorno +9,2% (noi -18,3%). Oggi nessun trade.
  learning:  Attivo: freno globale, 16 strategie in panchina, keep per coppia 0.35 ×49, 0.5 ×58, 0.65 ×130, 0.75 ×12. Solo misurato: deriva.

LETTURE FIRESTORE DEL BOT (ultime 24 h, quota gratuita 50.000/giorno):
  non misurate in questo documento (le conta solo il bot: vedi il controllo orario)

CAMBIAMENTI DEL LEARNING rispetto al controllo di un'ora fa (precedente: 2026-10-22 05:16 UTC). NON e' il confronto con ieri: quello e' nella STORIA DEL LEARNING, in fondo
  nessuno nell'ultima ora: nessun pezzo del learning ha cambiato decisione

PAPER CONTRO IL CASO (prezzo casuale con le nostre uscite):
  stop 44% (caso 46%) · stop d'ingresso/uscita 50/50% (caso 48.5/51.5%) · massimo toccato mediano 0.76R (caso 0.81R) · vinti 55% (caso 54%)
  fonte del caso: simulazione del 30 set su prezzo casuale, docs/revisione_sospese_30set.md e backlog K4: costanti, non ricalcolate. Vicino al caso = le classi d'uscita sono la forma delle regole, non una diagnosi. R medio (caso -0.067) e primo target (caso 17%): in `trades`

COSA QUESTO CONTROLLO NON PUO' DARE:
  - cosa aspetta il si' del proprietario: vive in docs/backlog.md, non e' un dato del sistema -> leggere docs/backlog.md (gruppo 1 dell'indice)

STORIA DEL LEARNING (foto dello stato scattata dal bot alla prima ora di ogni giorno italiano, RTDB /learning_giorni; da qui in giu' gli orari sono in ora italiana, quelli sopra in UTC):
  foto di ieri 21 ott 00:08, foto di oggi 22 ott 00:14: i confronti «ieri» e «stanotte» qui sotto vengono da queste

COME IMPARA IL TRAILING (il keep e' la parte del guadagno che il trailing blocca quando si arma: con 0,5 tiene meta' del miglior guadagno visto; piu' alto = stop piu' vicino)
  a) COSA HA VISTO IL PAPER: dopo ogni uscita del trailing guarda dove va il prezzo nelle 24 ore dopo
     prematuro = poi e' arrivato al target: usciti troppo presto («da rumore» se lo stop e' scattato su un ritorno indietro piu' piccolo del movimento medio di una candela)
     protetto = poi e' tornato allo stop iniziale: l'uscita ha salvato il guadagno; neutro = ne' l'uno ne' l'altro
     uscite del trailing sulle candele da 15 minuti (le sole che contano per le proposte): 284 verdetti = 135 prematuri (35 da rumore) + 149 protetti; in piu' 33 neutri; 21 su altri timeframe (non contano)
     uscite dopo un incasso parziale (preso almeno il primo target, resto chiuso dallo stop): 74 verdetti (37 prematuri, 37 protetti, 0 neutri), NON usati dalle proposte (se contarli non e' deciso)
     dopo gli stop: 84 rumore (il prezzo e' poi tornato al primo target), 260 inversione (ha continuato contro, o non e' tornato al primo target entro la finestra): nessuna regola li usa ancora
     nuovi ieri (21 ott): trailing 0 prematuri, 3 protetti, 1 neutro · dopo un incasso parziale 0 prematuri, 1 protetto, 0 neutri · stop 0 rumore, 4 inversione
     nuovi stanotte (22 ott): trailing 0 prematuri, 0 protetti, 1 neutro
  b) COSA PROPONE IL PAPER AL GATE (una proposta e' un candidato in piu' che il gate prova sulla storia: il paper propone, il gate sceglie)
     keep per tutte le coppie: 149 protetti su 284 verdetti = 52,5% (serve il 60%): nessuna proposta. Mancano 54 protetti per proporre 0,75 (oppure 89 prematuri per 0,25)
     keep per strategia (servono 5 verdetti della strategia): 6 strategie propongono (gen_01fbe76f 0,75, gen_ceab7f6a 0,75, gen_4465723e 0,75 e altre 3). Le piu' vicine:
       gen_684d7623 3 prematuri (1 da rumore) su 5: manca 1 prematuro da rumore per 0,25
       gen_490a90e5 4 protetti su 4: manca 1 protetto per 0,75
       gen_8981d5f2 2 protetti su 4: manca 1 protetto per 0,75
     keep imparato dal bot da solo (vale solo per le coppie senza keep del gate; servono 8 verdetti per strategia, esplorative escluse): nessuna strategia (la piu' avanti ha 7 verdetti su 8)
     scala dei target di incasso dal vissuto (multipli del rischio iniziale: «1/2/3» = incassi a 1, 2 e 3 volte il rischio), ultimo giro del gate (13 ott 20:40): 0.75/1.25/1.75; keep proposto: nessuno
     strategie con una scala propria (almeno 5 trade col massimo guadagno raggiunto misurato): 49
  c) COSA HA SCELTO IL GATE per le 249 validate che il bot opera (per coppia; «non scelto» = coppia non ancora ripassata dal gate: vale il default)
     keep: 0,65 ×130 · 0,5 ×58 · 0,35 ×49 · 0,75 ×12 (default 0,5). Dalle proposte del paper (0,25 e 0,75 esistono solo cosi'): 12
     scala dei target: 1.5/3/5 ×115 · 2/4/6 ×86 · 1/1.5/2.5 ×16 · 1/2/3 ×16 · altre 3 (×16) (default 1.5/3/5); dal vissuto in tutto: 16
     stop spostato al prezzo d'ingresso dopo il primo incasso (break-even): si ×249 (default si)
     cambiato ieri (foto 21 ott 00:08 -> foto 22 ott 00:14): nessuna delle 249 coppie presenti in entrambe le foto ha cambiato keep, scala o break-even
     cambiato stanotte (foto 22 ott 00:14 -> adesso): nessuna delle 249 coppie presenti in entrambe le foto ha cambiato keep, scala o break-even
  d) FUNZIONA? trade chiusi dal 25 set per keep in uso all'ingresso (gruppi NON confrontabili: coppie diverse; misura, non regola)
     keep 0,35: 60 trade · trailing armato in 34 dei 60 trade con referto (56,7%) · 12 prematuri, 13 protetti · R medio -0,04 · tavolo 0,78
     keep 0,5: 424 trade · trailing armato in 244 dei 424 trade con referto (57,5%) · 95 prematuri, 123 protetti · R medio -0,07 · tavolo 0,69
     keep 0,65: 213 trade · trailing armato in 116 dei 213 trade con referto (54,5%) · 59 prematuri, 47 protetti · R medio -0,17 · tavolo 0,69
     keep 0,75: 28 trade · trailing armato in 12 dei 28 trade con referto (42,9%) · 9 prematuri, 2 protetti · R medio -0,24 · tavolo 0,67
     R = guadagno in unita' del rischio iniziale; tavolo = parte del tragitto verso il target lasciata all'uscita trailing (0 = uscito al target, 1 = all'entrata)

COSA IMPARANO LE STRATEGIE (ipotesi dai referti del paper -> varianti giudicate dal gate sulla storia -> promozioni; e intanto declassate, esplorative, panchina, freno)
  IERI (21 ott, giornata intera ora italiana):
     - ipotesi nate dai referti 2: gen_be64073c conferma_trend «3 perdite controtrend», gen_be64073c controtrend_btc «3/3 persi contro il contesto BTC»
     - panchina (strategia×regime con peso sotto 0,5: size ridotta): nessuna entra; escono gen_1f7ead60|high_uncertainty (0,7624), gen_2031005e|high_uncertainty (0,7717), gen_fa304106|sideways (0,7666)
     - cooldown (fermo dopo 3 stop di fila) fra le due foto: finiti strategia gen_0aa0d29c
  STANOTTE (22 ott dalle 00:00 alle 07:26 ora italiana):
     nulla di nuovo: nessuna ipotesi, variante, promozione, declassata, esplorativa, cambio di panchina o freno
  PER STRATEGIA (le 10 con piu' trade chiusi negli ultimi 7 giorni; R = guadagno in unita' del rischio iniziale):
     gen_d16d1d02: 7 trade, 5 vinti, R medio +0,20 · ipotesi scala_stretta · scala propria 1/1.25/1.5 · 1 validata
     gen_01fbe76f: 5 trade, 4 vinti, R medio +0,21 · keep proposto 0,75 · scala propria 1/1.25/1.5 · 1 validata
     gen_4c6df481: 4 trade, 0 vinti, R medio -1,08 · ipotesi scala_stretta · in panchina con sideways · keep proposto 0,25 · scala propria 0.75/1/2 · 1 validata (1 declassate)
     gen_5a52c06b: 4 trade, 3 vinti, R medio +0,46 · ipotesi conferma_trend · scala propria 1.5/1.75/2 · 2 validate (1 declassate)
     gen_7027edb8: 4 trade, 3 vinti, R medio +0,06 · 0 validate
     gen_7100bb59: 4 trade, 3 vinti, R medio -0,06 · scala propria 0.5/0.75/1 · 1 validata (1 declassate)
     gen_8931b93c: 4 trade, 2 vinti, R medio -0,34 · ipotesi conferma_trend · keep proposto 0,75 · scala propria 0.75/1/1.25 · 1 validata (1 declassate)
     gen_be64073c: 4 trade, 1 vinto, R medio -0,65 · ipotesi conferma_trend, controtrend_btc · in panchina con bear_trending · 1 validata (1 declassate)
     gen_c934a6f7: 4 trade, 3 vinti, R medio +0,12 · 2 validate
     gen_0aa0d29c: 3 trade, 0 vinti, R medio -1,03 · ipotesi solo_long · scala propria 0.5/0.75/1 · 2 validate

--- stderr ---
/root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
  return query.where(field_path, op_string, value)
```
