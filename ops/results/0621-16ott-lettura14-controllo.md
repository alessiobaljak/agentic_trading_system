# 0621-16ott-lettura14-controllo.req

_eseguito: 2026-10-16 05:41 UTC_

**richiesta:** `controllo`
**eseguito:** `.venv/bin/python -m scripts.controllo`
**esito:** codice 0 in 7.2s

```
[firebase] connesso (Firestore + RTDB)
CONTROLLO AUTOMATICO — generato da ops alle 2026-10-16 05:40 UTC (durata 4377 ms, impostazioni: default repo)
  semaforo SISTEMA: ROSSO    semaforo PAPER: GIALLO
  controllo precedente: 2026-10-16 05:33 UTC
  sezioni fallite: nessuna

ANOMALIE (2):
  [rosso] GATE_IN_RITARDO (sistema): ultimo giro del gate 2 g 11 h fa (valore 212443, soglia 21600)
  [giallo] FRENO_GLOBALE (paper): freno globale da deriva: PF 0,70 vs 2,02 atteso (valore 0.698, soglia 1.212)

LETTURE:
  salute:    Bot vivo (battito 29 s fa), gate 2 g 11 h fa (solo urgenti), 8 posizioni, 1,0% a rischio. 2 avvisi: gate in ritardo, freno globale.
  paper:     647 trade in 29 giorni, 55% vinti, -164,47 USDT (-16,4%). BTC dal primo giorno +8,5% (noi -16,4%). Stop nel 44% delle uscite. Oggi +12,10.
  learning:  Attivo: freno globale, 17 strategie in panchina, keep per coppia 0.35 ×49, 0.5 ×58, 0.65 ×130, 0.75 ×12. Solo misurato: deriva.

LETTURE FIRESTORE DEL BOT (ultime 24 h, quota gratuita 50.000/giorno):
  non misurate in questo documento (le conta solo il bot: vedi il controllo orario)

CAMBIAMENTI DEL LEARNING rispetto al controllo di un'ora fa (precedente: 2026-10-16 05:33 UTC). NON e' il confronto con ieri: quello e' nella STORIA DEL LEARNING, in fondo
  nessuno nell'ultima ora: nessun pezzo del learning ha cambiato decisione

PAPER CONTRO IL CASO (prezzo casuale con le nostre uscite):
  stop 44% (caso 46%) · stop d'ingresso/uscita 48/51% (caso 48.5/51.5%) · massimo toccato mediano 0.77R (caso 0.81R) · vinti 55% (caso 54%)
  fonte del caso: simulazione del 30 set su prezzo casuale, docs/revisione_sospese_30set.md e backlog K4: costanti, non ricalcolate. Vicino al caso = le classi d'uscita sono la forma delle regole, non una diagnosi. R medio (caso -0.067) e primo target (caso 17%): in `trades`

COSA QUESTO CONTROLLO NON PUO' DARE:
  - cosa aspetta il si' del proprietario: vive in docs/backlog.md, non e' un dato del sistema -> leggere docs/backlog.md (gruppo 1 dell'indice)

STORIA DEL LEARNING (foto dello stato scattata dal bot alla prima ora di ogni giorno italiano, RTDB /learning_giorni; da qui in giu' gli orari sono in ora italiana, quelli sopra in UTC):
  foto di ieri 15 ott 00:23, foto di oggi 16 ott 00:28: i confronti «ieri» e «stanotte» qui sotto vengono da queste

COME IMPARA IL TRAILING (il keep e' la parte del guadagno che il trailing blocca quando si arma: con 0,5 tiene meta' del miglior guadagno visto; piu' alto = stop piu' vicino)
  a) COSA HA VISTO IL PAPER: dopo ogni uscita del trailing guarda dove va il prezzo nelle 24 ore dopo
     prematuro = poi e' arrivato al target: usciti troppo presto («da rumore» se lo stop e' scattato su un ritorno indietro piu' piccolo del movimento medio di una candela)
     protetto = poi e' tornato allo stop iniziale: l'uscita ha salvato il guadagno; neutro = ne' l'uno ne' l'altro
     uscite del trailing sulle candele da 15 minuti (le sole che contano per le proposte): 244 verdetti = 120 prematuri (27 da rumore) + 124 protetti; in piu' 26 neutri; 12 su altri timeframe (non contano)
     uscite dopo un incasso parziale (preso almeno il primo target, resto chiuso dallo stop): 56 verdetti (29 prematuri, 27 protetti, 0 neutri), NON usati dalle proposte (se contarli non e' deciso)
     dopo gli stop: 67 rumore (il prezzo e' poi tornato al primo target), 211 inversione (ha continuato contro, o non e' tornato al primo target entro la finestra): nessuna regola li usa ancora
     nuovi ieri (15 ott): trailing 1 prematuro, 4 protetti, 1 neutro · +2 trailing su altri timeframe (non contano per le proposte) · dopo un incasso parziale 2 prematuri, 1 protetto, 0 neutri · stop 6 rumore, 9 inversione
     nuovi stanotte (16 ott): trailing 2 prematuri, 4 protetti, 2 neutri · dopo un incasso parziale 1 prematuro, 0 protetti, 0 neutri · stop 0 rumore, 1 inversione
  b) COSA PROPONE IL PAPER AL GATE (una proposta e' un candidato in piu' che il gate prova sulla storia: il paper propone, il gate sceglie)
     keep per tutte le coppie: 124 protetti su 244 verdetti = 50,8% (serve il 60%): nessuna proposta. Mancano 56 protetti per proporre 0,75 (oppure 66 prematuri per 0,25)
     keep per strategia (servono 5 verdetti della strategia): 4 strategie propongono (gen_ceab7f6a 0,75, gen_4465723e 0,75, gen_4c6df481 0,25 e altre 1). Le piu' vicine:
       gen_684d7623 3 prematuri (1 da rumore) su 5: manca 1 prematuro da rumore per 0,25
       gen_490a90e5 4 protetti su 4: manca 1 protetto per 0,75
       gen_8981d5f2 2 protetti su 4: manca 1 protetto per 0,75
     keep imparato dal bot da solo (vale solo per le coppie senza keep del gate; servono 8 verdetti per strategia, esplorative escluse): nessuna strategia (la piu' avanti ha 6 verdetti su 8)
     scala dei target di incasso dal vissuto (multipli del rischio iniziale: «1/2/3» = incassi a 1, 2 e 3 volte il rischio), ultimo giro del gate (13 ott 20:40): 0.75/1.25/1.75; keep proposto: nessuno
     strategie con una scala propria (almeno 5 trade col massimo guadagno raggiunto misurato): 40
  c) COSA HA SCELTO IL GATE per le 249 validate che il bot opera (per coppia; «non scelto» = coppia non ancora ripassata dal gate: vale il default)
     keep: 0,65 ×130 · 0,5 ×58 · 0,35 ×49 · 0,75 ×12 (default 0,5). Dalle proposte del paper (0,25 e 0,75 esistono solo cosi'): 12
     scala dei target: 1.5/3/5 ×115 · 2/4/6 ×86 · 1/1.5/2.5 ×16 · 1/2/3 ×16 · altre 3 (×16) (default 1.5/3/5); dal vissuto in tutto: 16
     stop spostato al prezzo d'ingresso dopo il primo incasso (break-even): si ×249 (default si)
     cambiato ieri (foto 15 ott 00:23 -> foto 16 ott 00:28): nessuna delle 249 coppie presenti in entrambe le foto ha cambiato keep, scala o break-even
     cambiato stanotte (foto 16 ott 00:28 -> adesso): nessuna delle 249 coppie presenti in entrambe le foto ha cambiato keep, scala o break-even
  d) FUNZIONA? trade chiusi dal 25 set per keep in uso all'ingresso (gruppi NON confrontabili: coppie diverse; misura, non regola)
     keep 0,35: 44 trade · trailing armato in 25 dei 44 trade con referto (56,8%) · 9 prematuri, 9 protetti · R medio -0,08 · tavolo 0,80
     keep 0,5: 384 trade · trailing armato in 221 dei 384 trade con referto (57,6%) · 88 prematuri, 110 protetti · R medio -0,08 · tavolo 0,69
     keep 0,65: 139 trade · trailing armato in 76 dei 139 trade con referto (54,7%) · 41 prematuri, 27 protetti · R medio -0,19 · tavolo 0,71
     keep 0,75: 25 trade · trailing armato in 10 dei 25 trade con referto (40,0%) · 8 prematuri, 1 protetto · R medio -0,27 · tavolo 0,64
     R = guadagno in unita' del rischio iniziale; tavolo = parte del tragitto verso il target lasciata all'uscita trailing (0 = uscito al target, 1 = all'entrata)

COSA IMPARANO LE STRATEGIE (ipotesi dai referti del paper -> varianti giudicate dal gate sulla storia -> promozioni; e intanto declassate, esplorative, panchina, freno)
  IERI (15 ott, giornata intera ora italiana):
     - panchina (strategia×regime con peso sotto 0,5: size ridotta): entrano gen_acea368d|bear_trending (0,4632), gen_be64073c|bear_trending (0,4572), gen_e6ddc613|sideways (0,4572)
     - cooldown (fermo dopo 3 stop di fila) fra le due foto: finiti strategia gen_e6ddc613
  STANOTTE (16 ott dalle 00:00 alle 07:40 ora italiana):
     nulla di nuovo: nessuna ipotesi, variante, promozione, declassata, esplorativa, cambio di panchina o freno
  PER STRATEGIA (le 10 con piu' trade chiusi negli ultimi 7 giorni; R = guadagno in unita' del rischio iniziale):
     gen_5905e08d: 7 trade, 4 vinti, R medio -0,12 · ipotesi conferma_trend, scala_stretta · scala propria 0.75/1/1.25 · 1 validata (1 declassate)
     gen_684d7623: 7 trade, 4 vinti, R medio -0,27 · ipotesi conferma_trend · scala propria 0.5/0.75/1 · 1 validata (1 declassate)
     gen_ceab7f6a: 6 trade, 5 vinti, R medio +0,29 · ipotesi ingresso_vol_ratio · keep proposto 0,75 · scala propria 0.75/1.25/1.75 · 0 validate
     gen_e09c5203: 6 trade, 3 vinti, R medio -0,28 · scala propria 1/1.25/1.5 · 1 validata (1 declassate)
     gen_01fbe76f: 5 trade, 3 vinti, R medio -0,22 · ipotesi controtrend_btc · in panchina con sideways · 1 validata
     gen_8931b93c: 5 trade, 2 vinti, R medio -0,51 · scala propria 0.75/1/1.5 · 1 validata (1 declassate)
     gen_0aa0d29c: 4 trade, 4 vinti, R medio +0,37 · 2 validate
     gen_7100bb59: 4 trade, 3 vinti, R medio -0,06 · 1 validata (1 declassate)
     gen_871647b8: 4 trade, 1 vinto, R medio -0,65 · ipotesi conferma_trend, controtrend_btc · in panchina con bear_trending · scala propria 1.25/1.5/4.5 · 3 validate
     gen_acea368d: 4 trade, 3 vinti, R medio +0,75 · in panchina con bear_trending · scala propria 1/1.5/5 · 1 validata

--- stderr ---
/root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
  return query.where(field_path, op_string, value)
```
