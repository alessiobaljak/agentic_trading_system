# Collaudo del metodo, protocollo 3 — esiti

Sezione 13bis del protocollo. Le regole di dettaglio sono in `regole.md`, committate prima del primo calcolo.
Gli esiti grezzi sono in `esiti/giro<N>/` (una riga JSON per prova), il riepilogo calcolato da `riepilogo.py`.

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

## Le correzioni proposte (da approvare: cambiano il testo approvato)

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

Con le correzioni 1 e 2 la diagnosi della prova A da' 12 p-value sotto 0,10 su 100 (soglia 15). Dopo
l'approvazione si correggono gli strumenti e si rifanno le prove A e B ufficiali da capo.
