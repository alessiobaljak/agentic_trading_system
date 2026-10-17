# Collaudo del metodo, protocollo 4: le regole di dettaglio

Scritto dal coordinamento il 17 ottobre 2026, **prima di qualunque calcolo delle prove** (sezione 13bis del
protocollo: «i dettagli che il testo lascia aperti si scrivono in `collaudo_4/regole.md` e si committano prima
del primo calcolo»). Il testo che decide e' `research/PROTOCOLLO_4.md`; qui ci sono solo i dettagli che il testo
non fissa. Si approvano insieme agli esiti allo STOP del Passo 0. File del coordinamento: la sessione di ricerca
non lo legge (sezione 12).

Parte 1: le scelte degli strumenti, che valgono anche per la ricerca. Parte 2: i dettagli delle prove.

## Parte 1 — Le scelte degli strumenti

**Restano uguali** le scelte 1-25 della Parte 1 di `research/collaudo_3/regole.md` (indicatori, riscaldamento e
buchi, motore, statistiche), approvate con il collaudo del protocollo 3, con queste differenze:

1. **Costi e margine di LINKUSDT** (sezioni 6 e 9.4; `statistica4.REGOLE_LINK`, `COSTI_LINK`, `COSTI_DOPPI_LINK`):
   slippage 0,02% a lato (0,04% a costi doppi), margine di mantenimento 1%, il piu' alto dei livelli di Binance
   fino a 20.000 USDT di valore della posizione (capitale 10.000 × leva 2), con l'importo di mantenimento a 0
   (prudente). Per le monete di controllo la loro fascia di slippage e il loro margine (`controllo4.MONETE_CONTROLLO`,
   `MARGINE_CONTROLLO`). Sostituisce la scelta 12 (che parlava del margine di BTCUSDT).
2. **Funding per i segnali** (7.2; `catalogo3.Serie.funding_segnale`, `dati.serie_4`): E11 e F4 guardano il tasso
   riportato a 8 ore, tasso × 8 ÷ ore dell'intervallo, con le ore lette dal file di Binance di ogni regolamento; il
   risultato dei trade usa il tasso vero. Nel 2020-2023 LINKUSDT ha sempre l'intervallo di 8 ore; SOLUSDT ha 2 e 4 ore
   per 101 regolamenti nel novembre 2022 (`research/passo0_4/fatti_monete.json`).
3. **Fine della serie** (9.6; `dati.serie_4_con_conteggi`): la serie finisce all'ultima candela con volume sopra zero;
   le candele in coda a volume zero si tolgono con `Serie.fino_a`, che toglie anche il funding regolato dopo. Una
   candela a volume zero in mezzo alla serie resta. Nel 2020-2023 nessuna delle 10 monete ha candele ferme in coda.
4. **Robustezza (verifica 1, `statistica4.mosse_robustezza_4`)**: stesse mosse e stessi arrotondamenti della scelta 21;
   se dopo l'arrotondamento il valore non cambia, si sposta di un passo dell'arrotondamento nella direzione dello
   spostamento del 20% (per un valore negativo il −20% va verso lo zero; per lo zero la direzione e' quella della
   mossa). Uno spostamento che da' un valore non valido (periodo o candele sotto 1, multiplo o percentuale non
   positivi, soglia di RSI o stocastico fuori da 0-100) o una variante impossibile si riporta e non si prova.
5. **Blocchi (verifica 3, `statistica4.BLOCCHI_4`)**: dall'inizio al 2020-09-30; 2020-10-01 → 2021-05-31;
   2021-06-01 → 2022-01-31; 2022-02-01 → 2022-09-30; stesse regole della scelta 22.
6. **Mercati forti (verifica 3bis, `statistica4.mercati_forti`)**: i semestri solari (gennaio-giugno, luglio-dicembre)
   sulle candele giornaliere di LINKUSDT della costruzione; variazione = chiusura dell'ultima candela del semestre ÷
   apertura della prima − 1 (il primo semestre parte dalla prima candela, il 2020-01-17; l'ultimo e' luglio-settembre
   2022). Un trade sta nel semestre della sua candela d'ingresso; i trade dei semestri fra −30% e +30% non contano.
7. **Trade estremi (verifica 4, `statistica4.senza_i_migliori_4`)**: le entrate casuali sono le stesse 1.000 della Fase
   2 (stesso generatore, stesso seme, `entrate_casuali_con_trade`: l'osservatore registra solo); da ognuna si tolgono i
   suoi trade migliori, il 5% arrotondato per eccesso, come dal candidato. Vantaggio = R medio del candidato − media
   degli R medi delle simulazioni; supera se il candidato senza i migliori resta positivo, il vantaggio intero e'
   positivo e quello senza i migliori e' almeno la meta' di quello intero.
8. **Verifica 12 (`controllo4.verifica_12_su_serie`)**: su ogni moneta di controllo la serie dalla sua prima candela al
   2022-09-30, la variante senza modifiche, i costi e il margine della moneta, le sue 1.000 entrate casuali (seme 2026,
   stessa larghezza di stop della variante su quella moneta). «Batte il caso» = R medio strettamente maggiore della media
   delle sue entrate casuali, con almeno 30 trade; se le entrate casuali sono impossibili, la moneta non batte. La media
   dell'R medio si calcola fra le monete con almeno 30 trade.
9. **Controllo della Fase 3 (`controllo4.controllo_fase3_su_serie`)**: le due varianti senza altre modifiche, ognuna sul
   suo timeframe; contano le monete in cui tutte e due hanno almeno 30 trade, almeno 5; differenza = media fra quelle
   monete dell'R medio della variante nuova − la stessa media della variante da cui differisce; supera con almeno 0,05 R.
10. **Validazione sulle monete di controllo (`controllo4.validazione_controllo_su_serie`)**: serie dal 2020-01-01 al
    2023-12-31, decisioni solo dal 2022-10-01 (gli indicatori arrivano gia' calcolati, come per LINKUSDT in validazione);
    contano le monete con almeno 20 trade e con le entrate casuali possibili, almeno 5; vantaggio di una moneta = suo
    R medio − media delle sue entrate casuali; supera se la media fra queste monete del vantaggio e' almeno 0,1 R e la
    media dell'R medio e' positiva. La media a costi doppi si riporta.
11. **Canale delle richieste**: il coordinamento esegue una richiesta solo se la verifica e' registrata nel log della
    ricerca in un commit precedente a quello della richiesta, sulla specifica registrata; risponde con il solo esito
    (`{"supera": ...}`) e tiene i numeri in `research/monete_di_controllo_4/<ID>.json` sul branch principale. Per la
    validazione, dopo l'esecuzione unica, risponde anche con i numeri.

## Parte 2 — Le prove

### Dati

- Le candele vere della costruzione (fino al 2022-09-30) di LINKUSDT e delle 9 monete di controllo, dai file mensili di
  data.binance.vision con il CHECKSUM verificato (`research/passo0_4/scarica_dati.py`, impronte in
  `research/passo0_4/fatti_monete.json`), caricate con `dati.serie_4`.

### Le serie senza vantaggio (13bis.1)

- Per ogni moneta e ogni timeframe 30 serie, semi da 1 a 30, costruite come nel protocollo 3 (`collaudo_3/regole.md`,
  Parte 2: movimenti relativi in logaritmo, candele girate o no alla pari, prezzo dalla prima chiusura vera, orari, buchi,
  volume e funding veri), con una differenza: **il lancio di ogni candela** e' il bit piu' alto di SplitMix64 applicato a
  (seme × 0x9E3779B97F4A7C15) xor (crc32 della moneta << 32) xor (numero della candela dall'epoca = apertura ÷ durata)
  (`collaudo.py`, `_lanci`). Con lo stesso seme monete diverse si girano in modo indipendente (prova sul codice: 52%
  di lanci uguali fra BTCUSDT ed ETHUSDT su 1.000 ore), e la stessa ora della stessa moneta si gira sempre allo stesso
  modo.

### Prova A (13bis.2)

- **A.1-A.2** Come nel protocollo 3 (estrazione con seme 2026, la variante numero i sulla serie (i mod 30) + 1 del suo
  timeframe, sotto 150 trade stimati si scarta, le entrate casuali impossibili si sostituiscono con le estrazioni
  successive), sulle serie di LINKUSDT; la stima dei trade con `REGOLE_LINK`.
- **A.3** Fase 2 completa con `statistica4.fase2_4` (costi e margine di LINKUSDT); per chi la supera, `fase4_4` con le
  serie dello stesso seme dei timeframe adiacenti e con la serie giornaliera dello stesso seme per la 3bis.
- **A.4 Passa se** al massimo 5 varianti su 100 superano la Fase 2 **e** al massimo 15 hanno un p-value sotto 0,10.
- **A.6 La verifica 12 senza vantaggio**: per tutte le 100 varianti finte, sulle serie senza direzione delle 9 monete di
  controllo del timeframe della variante con lo stesso seme. Si contano quelle che battono il caso su almeno 7 monete
  su 9: se sono piu' di 17, STOP. Si riportano anche quante superano la verifica 12 intera e la distribuzione di
  «battono».
- **A.5 Informazioni:** distribuzione dei p-value per decimi, R medio delle 100, R medio delle entrate casuali.

### Prova B (13bis.3)

- **B.1-B.5** Come nel protocollo 3 (regole B1, B2, B3; vantaggio costruito una candela dopo l'altra con ritorno in 240
  candele; P = 0 / 0,6 / 1,2, riserva 1,8; segnali uguali; soglie 3 su 30 e 80%; salita delle entrate casuali oltre 0,05
  R = STOP), sulle serie a 1h di LINKUSDT e con `fase2_4`.
- **B.6 La verifica 12 con il vantaggio**: per B1 e B2, con P = 0,6 e 1,2 inserito sulle serie a 1h delle 9 monete di
  controllo (semi da 1 a 10: la prova k usa la serie k di ogni moneta), la verifica 12. **Passa se** con P = 1,2 passa
  in almeno 8 prove su 10 per ciascuna regola; P = 0,6 si riporta.

### Prova C (13bis.4)

Dopo il vault, prima del paper (D5): al Passo 0 il bot non sa eseguire nessuna variante del catalogo
(`config/bot_4.md`, punto 3).

### Tempo, versioni e impronte

- Prima del lancio si stima il tempo; oltre 24 ore, STOP. **Prova sul codice fatta prima di committare queste regole**
  (17 ottobre, per i tempi e per controllare i lanci, detta qui per trasparenza): la regola B1 sulla serie 1 di
  LINKUSDT senza vantaggio con la funzione della prova A (832 trade, R medio −0,026, p 0,330, verifica 12: 5 monete su 9,
  56 secondi) e la prova B.6 di B1 con seme 1 e P = 1,2 (9 monete su 9, media +0,436 R, supera, 42 secondi). Nessuna
  regola qui sotto e' stata scelta dopo averle viste; la prova B.6 di B1, seme 1, P = 1,2 si rifa' nel giro vero.
- Il collaudo gira con Python, numpy e scipy nelle versioni della macchina delle sessioni di ricerca (Passo 0, punto 8),
  scritte in `parametri_4.yaml` e in `esiti.md`.
- Gli esiti grezzi in `esiti/giro<N>/`; in `esiti.md` i numeri, «passa» o «non passa» e le impronte SHA-256 degli
  strumenti (`collaudo.py impronte`). Se uno strumento cambia dopo il collaudo, prima di usarlo si rifanno A e B.
