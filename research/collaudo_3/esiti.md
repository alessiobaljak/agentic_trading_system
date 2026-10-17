# Collaudo del metodo, protocollo 3 — esiti

Sezione 13bis del protocollo. Le regole di dettaglio sono in `regole.md`, committate prima del primo calcolo e
aggiornate prima del secondo giro con le correzioni approvate. Gli esiti grezzi di ogni giro sono in `esiti/giro<N>/`
(una riga JSON per prova), il riepilogo calcolato da `riepilogo.py <N>`.

## Esito: il metodo passa il collaudo (terzo giro, 17 ottobre 2026)

| Prova | Primo giro (16 ott) | Secondo giro (17 ott, con le correzioni) | Terzo giro (17 ott, caricatore corretto) |
|---|---|---|---|
| A — prezzi senza vantaggio | non passa (21 p-value sotto 0,10 su 100) | **passa** (13 su 100, soglia 15; 0 varianti oltre la Fase 2, soglia 5) | **passa** (11 su 100; 0 oltre la Fase 2) |
| B — vantaggio inserito apposta | passa per due regole su tre | **passa** per tutte e tre | **passa** per tutte e tre |
| C — parita' con il bot | non eseguibile | dopo il vault, prima del paper (scelta del proprietario del 17 ott) | idem |

## Terzo giro: 17 ottobre 2026, dalle 07:49:26 alle 08:16:09 UTC

Dopo la correzione del caricatore per i buchi del solo mark (`PROTOCOLLO_3.md`, 9.6 e appendice 3, punto 6; si' del
proprietario alle 07:38 UTC): `dati.py` e' cambiato, quindi si rifanno A e B (13bis.5). Strumenti al commit `0bbf0389`
(`esiti/giro3/commit.txt`), impronte SHA-256 (`esiti/giro3/impronte.json`), **che da qui valgono per la ricerca**:

| File | SHA-256 |
|---|---|
| `research/src/catalogo3.py` | `a9c7e99613d159db92833822716c06e4913d8cc6db80c88421527269b4dc5b06` |
| `research/src/motore3.py` | `84d3700cb1633711bb11db31ae9555f938897a4fd3fce1a3a56452281d9cf6c3` |
| `research/src/statistica3.py` | `f6921986cf9da18330047e46b09919b125c545adc3ba87c39ee9c88dfc7c1c7a` |
| `research/src/statistica.py` | `e42edc0082ff0e52b8d1e1a65493f912c98fd7fbf083bf53dbe0d742ef95b7a1` |
| `research/src/dati.py` | `440e6ef0a2e00c85d5329b2b9f09d03fb424d7f43d1cef0bd911c31dae43080c` |
| `research/src/guardiano.py` | `b83825094acc41f5ede7cf2af9d30cc35ef2bd03108b25447df6fe8e1cec993b` |
| `research/config/parametri_3.yaml` | `85b0e7bb443b123edbc4a9618c8475dd031e73e88d8b92f4d7e7c7734c31a2f8` |
| `research/collaudo_3/collaudo.py` | `cc4056ef92a85b6c61e0bcecb1d4c62479bae4cba53289d30f18fe261754b7cb` |
| `research/collaudo_3/regole.md` | `3e623b78765f01ee476dfa12641511ba710d14d1b0d42d432881b0735c0de93c` |

### Prova A: **passa**

| Misura | Valore | Soglia |
|---|---|---|
| Varianti finte con la Fase 2 completa | 100 (473 estratte; una, la numero 309, sostituita perche' le entrate casuali non trovano posto, sotto) | 100 |
| Superano la Fase 2 | **0** | al massimo 5 |
| p-value sotto 0,10 | **11** | al massimo 15 (attese circa 10) |
| p-value per decimi | 11, 10, 13, 13, 6, 9, 9, 16, 6, 7 | circa 10 ciascuno |
| R medio delle varianti / delle loro entrate casuali | −0,071 / −0,081 | — |

La variante 309 (15m, rottura della banda di Bollinger, stop al minimo delle ultime 5 candele, target a 3 R, 602 trade):
con la regola della stessa larghezza di stop, in 4 milioni di giri nessuna strategia a caso ha fatto 602 trade senza
sovrapporli, perche' i suoi stop larghi cadono in momenti rari e i trade durano a lungo. Per le regole della prova A
(punto A.2) e' riportata a parte e sostituita; nella ricerca lo stesso caso e' uno STOP con domanda all'utente
(`regole.md`, punto 20).

### Prova B: **passa** per tutte e tre le regole

| Regola | Senza vantaggio: superano (soglia ≤ 3 su 30) | Prove ad almeno 0,35 R: superano (soglia 80%) | Prove con R fra 0,2 e 0,35: superano | R medio netto per P = 0 / 0,6 / 1,2 |
|---|---|---|---|---|
| B1 (long, a mercato) | 0 | 24 su 24 | 7 su 7 | −0,087 / +0,134 / +0,395 |
| B2 (short, a mercato) | 0 | 28 su 28 | 4 su 4 | −0,080 / +0,149 / +0,418 |
| B3 (long, limit) | 0 | 30 su 30 | 11 su 11 | −0,036 / +0,190 / +0,458 |

Con un vantaggio inserito di almeno 0,2 R netti superano 104 prove su 104; senza vantaggio 0 su 90 (p-value sotto 0,10:
13 su 90). La riserva P = 1,8 non e' servita; i segnali inseriti sono quelli trovati in tutte le 270 prove; le entrate
casuali con il vantaggio salgono di −0,004 / +0,003 / −0,032 R (STOP oltre +0,05).


**Esiti del Passo 0 approvati dal proprietario il 17 ottobre 2026 alle 07:15 UTC** («Sì apri la sessione»): strumenti e
parametri congelati con le impronte del secondo giro (sotto), sostituite da quelle del terzo giro dopo la correzione del
caricatore (sopra).

## Secondo giro: 17 ottobre 2026, dalle 06:28:38 alle 06:49:23 UTC

Con le correzioni approvate dal proprietario il 17 ottobre alle 06:11 UTC (`PROTOCOLLO_3.md`, appendice 3): entrate
casuali con la stessa larghezza di stop del candidato, serie con la direzione di ogni candela girata a caso, ampiezze
del vantaggio 0 / 0,6 / 1,2 (riserva 1,8). Strumenti al commit `a5223944` (`esiti/giro2/commit.txt`), impronte
SHA-256 (`esiti/giro2/impronte.json`):

| File | SHA-256 |
|---|---|
| `research/src/catalogo3.py` | `a9c7e99613d159db92833822716c06e4913d8cc6db80c88421527269b4dc5b06` |
| `research/src/motore3.py` | `84d3700cb1633711bb11db31ae9555f938897a4fd3fce1a3a56452281d9cf6c3` |
| `research/src/statistica3.py` | `f6921986cf9da18330047e46b09919b125c545adc3ba87c39ee9c88dfc7c1c7a` |
| `research/src/statistica.py` | `e42edc0082ff0e52b8d1e1a65493f912c98fd7fbf083bf53dbe0d742ef95b7a1` |
| `research/src/dati.py` | `b37c63dc6e233f8aa6b2fb527a0b8fc418dc0e3356f8842ea100e714f2df7e62` |
| `research/src/guardiano.py` | `b83825094acc41f5ede7cf2af9d30cc35ef2bd03108b25447df6fe8e1cec993b` |
| `research/config/parametri_3.yaml` | `85b0e7bb443b123edbc4a9618c8475dd031e73e88d8b92f4d7e7c7734c31a2f8` |
| `research/collaudo_3/collaudo.py` | `e5f1eb83971406712dcd119204850cda43e27a4003a6476796323b2dd37eec97` |
| `research/collaudo_3/regole.md` | `0b9e4fd29f3e63d0c7551b304a1f298e94a1414074ea0a7f62cb1e3ec8be346e` |

Queste impronte valgono per tutta la ricerca (13bis.5): se uno strumento cambia, prima di usarlo si rifanno le prove
A e B.

### Prova A — direzioni a caso: **passa**

| Misura | Valore | Soglia |
|---|---|---|
| Varianti finte con la Fase 2 completa | 100 (486 estratte, 386 scartate sotto 150 trade stimati, nessuna con entrate casuali impossibili) | 100 |
| Superano la Fase 2 | **0** | al massimo 5 |
| p-value sotto 0,10 | **13** | al massimo 15 (attese circa 10) |
| p-value per decimi | 13, 13, 9, 9, 13, 11, 8, 8, 9, 7 | circa 10 ciascuno |
| p-value piu' piccolo | 0,004 | — |
| R medio delle 100 varianti | −0,076 | atteso negativo per i costi |
| R medio delle loro entrate casuali | −0,084 | atteso uguale (nel primo giro la distanza era 0,027 R, ora 0,008) |
| Varianti per timeframe | 15m 42, 30m 23, 1h 23, 2h 10, 4h 1, 8h 1 | — |

### Prova B — vantaggio inserito apposta: **passa** per tutte e tre le regole

| Regola | Senza vantaggio: superano (soglia ≤ 3 su 30) | Prove ad almeno 0,35 R: superano (soglia 80%) | Prove con R fra 0,2 e 0,35: superano | R medio netto per P = 0 / 0,6 / 1,2 | Entrate casuali con il vantaggio (STOP oltre +0,05 R) |
|---|---|---|---|---|---|
| B1 (long, a mercato) | 0 | 27 su 27 | 6 su 6 | −0,080 / +0,140 / +0,408 | −0,002 R |
| B2 (short, a mercato) | 0 | 27 su 27 | 8 su 8 | −0,081 / +0,152 / +0,419 | +0,006 R |
| B3 (long, limit) | 0 | 29 su 29 | 17 su 17 | −0,035 / +0,192 / +0,468 | −0,030 R |

- Con P = 1,2 almeno 27 serie su 30 arrivano a 0,35 R per ogni regola: la riserva (P = 1,8) non e' servita.
- I segnali trovati sulle serie con il vantaggio sono esattamente quelli a cui e' stato dato (tutte le 270 prove).
- Senza vantaggio i p-value sotto 0,10 sono 4, 5 e 2 su 30: 11 su 90, in linea con il caso.
- Per B3 gli ordini limit eseguiti sono il 63% in media.
- Ogni prova con un vantaggio inserito di almeno 0,2 R netti supera la Fase 2 (114 su 114); senza vantaggio nessuna.

## Primo giro: 16 ottobre 2026, dalle 21:01:39 alle 21:10:39 UTC

Strumenti al commit `dd2ef133` (`esiti/giro1/commit.txt`), impronte SHA-256 in `esiti/giro1/impronte.json`:

| File | SHA-256 |
|---|---|
| `research/src/catalogo3.py` | `a9c7e99613d159db92833822716c06e4913d8cc6db80c88421527269b4dc5b06` |
| `research/src/motore3.py` | `84d3700cb1633711bb11db31ae9555f938897a4fd3fce1a3a56452281d9cf6c3` |
| `research/src/statistica3.py` | `2ae383907969c4e00aa57b95a3c6f19961e2439fa2bd00af23f40717b197f894` |
| `research/src/statistica.py` | `e42edc0082ff0e52b8d1e1a65493f912c98fd7fbf083bf53dbe0d742ef95b7a1` |
| `research/src/dati.py` | `b37c63dc6e233f8aa6b2fb527a0b8fc418dc0e3356f8842ea100e714f2df7e62` |
| `research/src/guardiano.py` | `b83825094acc41f5ede7cf2af9d30cc35ef2bd03108b25447df6fe8e1cec993b` |
| `research/config/parametri_3.yaml` | `d813d8492730f9b89d174392aa7d5d24754b7af40e96388368c775b756f98861` |
| `research/collaudo_3/collaudo.py` | `d004479574b2b65b4c6f56250208fcecc945deea67e7b42dd6e0ec37ecfd7478` |
| `research/collaudo_3/regole.md` | `ee33784e4aa75aaef18d683a1e8c6c2962ad64f9e43ed43d1571856b5a0a9274` |

### Prova A — prezzi rimescolati: **non passa**

| Misura | Valore | Soglia |
|---|---|---|
| Varianti finte con la Fase 2 completa | 100 (511 estratte, 411 scartate sotto 150 trade stimati, nessuna con entrate casuali impossibili) | 100 |
| Superano la Fase 2 | **0** | al massimo 5 |
| p-value sotto 0,10 | **21** | al massimo 15 (attese circa 10) |
| p-value per decimi (da 0-0,1 a 0,9-1) | 21, 12, 19, 8, 8, 8, 6, 6, 5, 7 | circa 10 ciascuno |
| R medio delle 100 varianti | −0,081 | atteso negativo per i costi |
| R medio delle loro entrate casuali | −0,108 | atteso uguale a quello delle varianti |
| Varianti per timeframe | 15m 41, 30m 24, 1h 24, 2h 9, 4h 1, 8h 1 | — |

Il metodo non promuove nessuna variante finta, ma il p-value **non e' tarato**: sui prezzi rimescolati, dove
nessuna regola puo' prevedere il futuro, le varianti battono le proprie entrate casuali in media di 0,027 R a
trade, e i p-value piccoli sono il doppio del dovuto.

### Prova B — vantaggio inserito apposta: B1 e B3 passano, B2 non si puo' valutare

| Regola | Senza vantaggio: superano (soglia ≤ 3 su 30) | Con vantaggio, prove ad almeno 0,35 R: superano | Prove con R fra 0,2 e 0,35: superano | Entrate casuali: quanto salgono con il vantaggio (STOP oltre 0,05 R) | Esito |
|---|---|---|---|---|---|
| B1 (long, a mercato) | 0 | 4 su 4 | 26 su 26 | +0,005 R | passa |
| B2 (short, a mercato) | 0 | **nessuna prova arriva a 0,35 R** | 28 su 28 | +0,010 R | non valutabile |
| B3 (long, limit) | 0 | 9 su 9 | 32 su 32 | −0,012 R | passa |

- R medio netto per ampiezza del vantaggio P (0 / 0,3 / 0,6 / 0,9): B1 −0,083 / +0,032 / +0,150 / +0,274;
  B2 −0,100 / +0,010 / +0,136 / +0,263; B3 −0,033 / +0,074 / +0,191 / +0,317. Il vantaggio inserito rende
  circa un terzo dell'ampiezza P: molti trade escono per stop prima che lo spostamento si accumuli. Per questo
  pochissime prove arrivano a 0,35 R, e per B2 nessuna, anche con la riserva P = 0,9 (fatta per tutte e tre).
- I segnali trovati sulle serie con il vantaggio sono esattamente quelli a cui e' stato dato (tutte le 360 prove).
- Con P = 0 i p-value sotto 0,10 sono 6 su 30 (B1), 1 su 30 (B2), 3 su 30 (B3): 10 su 90, in linea con il caso.
- Per B3 gli ordini limit eseguiti sono il 55% in media.

In sostanza: ogni volta che il vantaggio vero arriva ad almeno 0,2 R netti, la Fase 2 lo trova (86 prove su 86);
senza vantaggio non promuove niente. La soglia di 0,35 R della regola B.4 era troppo alta per il vantaggio che la
costruzione della prova riesce a inserire.

### Prova C — parita' con il bot: non eseguita

Il bot oggi non sa eseguire nessuna variante del catalogo come la scrive il protocollo (`config/bot_3.md`,
punto 3). Si chiede all'utente allo STOP (regole.md, Prova C).

## La causa del difetto della prova A (diagnosi, non prove ufficiali)

Prove di diagnosi sulle stesse 100 varianti (script e dettagli in `diagnosi/`):

| Diagnosi | p-value sotto 0,10 | sotto 0,023 |
|---|---|---|
| Prova ufficiale | 21 | 7 |
| Serie senza la tendenza di fondo (rendimento medio per candela portato a zero) | 21 | — |
| Costi a zero | 15 | — |
| Senza tendenza e costi a zero | 17 | — |
| Entrate casuali con la stessa larghezza di stop del candidato (5 fasce) | 17 | 4 |
| Serie con la direzione di ogni candela girata a caso (volatilita' al suo posto) | 22 | 6 |
| Tutte e due le ultime | **12** | 4 |

- La tendenza di fondo (BTC quasi triplicato nella costruzione) **non** e' la causa.
- La causa e' la **larghezza dello stop**. Le varianti entrano in momenti in cui lo stop e' piu' largo del solito
  (dopo candele grandi, soprattutto con lo stop S2 al minimo o massimo delle ultime candele): pagano meno costi
  per ogni R (0,012 R in media) e soffrono meno le regole prudenti del motore (uscita all'apertura se la candela
  salta lo stop, stop prima del target nella stessa candela). Le entrate casuali entrano in momenti qualsiasi,
  con stop di larghezza media, e perdono di piu'. Sulle serie rimescolate l'effetto e' piu' forte che sui prezzi
  veri, perche' il rimescolamento toglie il legame fra volatilita' passata e futura.

- Il difetto si concentra nelle varianti che usano il volume (segnale E12: 8 su 21 sotto 0,10; conferma C1: 7 su
  16): scelgono le candele anomale, dopo le quali lo stop e' largo.
- Non c'e' informazione dal passato al futuro sulle serie rimescolate (`diagnosi/avanti.py`): il difetto non
  viene da un errore che faccia guardare il futuro, ma da come si confronta il candidato con il caso.

## Le correzioni (approvate dal proprietario il 17 ottobre 2026 alle 06:11 UTC)

1. **Sezione 10.1 — entrate casuali con la stessa larghezza di stop.** La strategia che entra a caso entra piu'
   o meno spesso secondo la larghezza dello stop di quel momento, cosi' che i suoi trade abbiano la stessa
   distribuzione di larghezze del candidato (5 fasce, ai quinti delle larghezze dei trade del candidato). Il
   confronto giudica allora il momento d'ingresso, non i costi piu' bassi di uno stop largo. La soglia di 0,2 R
   dopo i costi resta quella, sull'R vero.
2. **Sezione 13bis.1 — serie senza vantaggio piu' vicine al mercato vero.** Invece di mescolare l'ordine delle
   candele, si gira a caso la direzione di ogni candela (salto, corpo, massimo e minimo, mark compreso), con il
   seme della serie: la volatilita' resta dove era (periodi calmi e periodi agitati), la direzione diventa
   imprevedibile e la tendenza sparisce.
3. **Sezione 13bis.3 — vantaggio inserito piu' grande.** Il vantaggio inserito rende circa un terzo di P: con
   P = 0 / 0,3 / 0,6 (riserva 0,9) quasi nessuna prova arriva a 0,35 R. Ampiezze nuove: 0 / 0,6 / 1,2, riserva
   1,8.

Con le correzioni 1 e 2 la diagnosi della prova A dava 12 p-value sotto 0,10 su 100 (soglia 15); il secondo giro
ufficiale, con gli strumenti corretti, ne ha dati 13 (sopra).
