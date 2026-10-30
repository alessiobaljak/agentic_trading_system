# Programma 7 — settantesima prova: il funding in USDT contro quello in moneta (FM)

Scritto il 30 ottobre 2026 alle 00:23 UTC (ora dell'orologio), **prima di qualunque calcolo**. È l'idea 107 della coda (dalla ricerca
nelle pubblicazioni del 29 ottobre). Fino a qui si è solo contato quanti contratti in moneta hanno il funding nell'archivio di Binance
(49) e letto il formato di un file; nessun funding e nessun prezzo guardato.

## 1. Perché

* **Due clientele sulla stessa moneta.** Sui perpetui in USDT si usa come margine il dollaro digitale: è il contratto di chi cerca la
  leva. Sui perpetui «in moneta» (margine nella moneta stessa, per esempio ADAUSD_PERP) entra soprattutto chi la moneta la tiene già e
  si copre.
* **La fonte**: BitMEX, rapporto sui derivati del secondo trimestre 2026 (letto da un articolo, l'originale non si apre): sul Bitcoin il
  contratto in moneta ha pagato in media il 3,93% l'anno meno di quello in USDT, in 13 trimestri su 14, per la diversa clientela.
* **L'ipotesi**: dove il funding in USDT è molto sopra quello in moneta, a pagare sono gli speculatori a leva, non chi si copre; è la
  parte del funding che G1 vende. Lo scarto dovrebbe isolare meglio di G1 «chi paga la leva perde».
* **I dubbi scritti prima**:
  * uno studio pubblico su 791 perpetui (OctopusTakopi, 2026) trova che il funding di altre piattaforme non aggiunge niente al livello;
    lo scarto potrebbe essere solo il livello del funding in USDT con un altro nome;
  * i contratti in moneta sono 49, quasi tutti monete grandi;
  * il funding in moneta ha la sua base (0,01% ogni 8 ore) come quello in USDT: molte parità.

## 2. La regola (fissata qui)

* **Dati**: il funding dei 49 perpetui in moneta dall'archivio pubblico di Binance (`data/futures/cm/monthly/fundingRate/`), salvato in
  `research/data/cm_funding/` fuori da git, sommato per giorno; il funding in USDT del pannello (`seconda.pannello`).
* **Il segnale**, ogni giorno alle 00:00 come G1: la somma del funding in USDT dei 7 giorni prima meno la somma del funding in moneta
  degli stessi 7 giorni (`sesta.funding_7` per tutti e due), arrotondata a 12 decimali; solo le monete con il funding in moneta in tutti
  e 7 i giorni.
* **Il portafoglio, come G1** (`prima.py`): fra le monete dell'universo di G1 del giorno con il segnale, **short il quinto con lo scarto
  più alto, long il quinto con il più basso**, banda 20/40 (`ventiquattresima.pesi_banda`), pesi secondo l'inverso della volatilità,
  almeno 20 monete con il segnale; ordini limite e costi come G1 (`cinquantaduesima.conto`), funding dei perpetui in USDT (si opera solo
  su quelli).
* **Periodo**: dal 4 gennaio 2021 al 5 ottobre 2026 (`prima.FINE`).
* **Una variante**: nel conto delle prove diventano **229**.

## 3. L'esame

* **Come le prove a portafoglio** (`terza.esame`, `terza.esito`, con il Bitcoin come riferimento): lo Sharpe corretto con l'aggiunta sopra
  0,95, il t contro 3 e la regola del proprietario del 24 ottobre.
* **E in più**: lo Sharpe di FM deve essere sopra quello di **G1 sulle stesse monete e negli stessi giorni** (il segnale di G1, cioè il
  solo funding in USDT, con lo stesso universo ristretto e lo stesso conto). Se non lo è, lo scarto non aggiunge niente al livello del
  funding.
* **Se regge**, passa da un revisore separato prima del paper.
* **Per capire, senza decidere niente**: quante monete hanno il segnale ogni giorno; la correlazione fra lo scarto e il funding in USDT;
  i due lati; per anno; la media dei ranghi di G1 e di FM sulle stesse monete; la correlazione con G1.
