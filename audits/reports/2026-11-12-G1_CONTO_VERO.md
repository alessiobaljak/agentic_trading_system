# Audit di G1 nella configurazione per il conto vero (12 novembre 2026)

Auditor: backtest-auditor. Repository locale a `2cf9dd7` (copia troncata: l'ordine dei commit è verificato sul remoto con `gh api`).
Script e numeri: `audits/repro/g1_*2026-11-12*` (elenco in fondo). Nessun file fuori da `audits/` è stato modificato.

## Riepilogo e verdetto

**PASS tecnico, con quattro problemi Alti.** Il risultato è ricalcolato da capo e torna: G1 Sharpe 1,98 (+54,4% l'anno, discesa
−28,8%), il conto a 280 USDT con i minimi di Binance («A», come il bot) 1,90 (+57,8%, −26,8%), ogni anno positivo. Non ho trovato
sguardi nel futuro: 7 giorni rifatti con il pannello tagliato hanno gli stessi pesi; il bot calcola gli stessi pesi della ricerca in
60 giorni su 60. I periodi sono quelli dichiarati. La liquidazione con la leva 5 e il margine unico resta lontana.

PASS vuol dire «tecnicamente credibile», non «da mandare sui soldi veri». **L'esame del proprietario passa solo con l'ipotesi più
favorevole sugli ordini limite**, e quell'ipotesi non corrisponde all'ordine che il conto vero manda davvero:

| Sharpe corretto (N = gruppi, 80; soglia 0,80) | ordine limite come la ricerca | tutto a mercato | limite eseguito solo se il prezzo va oltre dello 0,05% |
|---|---|---|---|
| G1 senza minimi | **0,87** | 0,80 (0,795) | 0,72 |
| A, 280 USDT (la configurazione per il conto vero) | **0,81** | **0,77** | **0,73** |

Con N = 309 (il conto delle prove) tutti stanno fra 0,46 e 0,65. Il t dello Sharpe è sopra 3 in tutti i casi (fra 3,8 e 4,8).

Il brief dava come esame in vigore lo Sharpe corretto da 0,80. Le mie istruzioni dicono 0,90, e il file di regole della prova 57
(`research/programma7/PRIMA.md:27`) dice 0,95. Ho usato 0,80 come richiesto e lo segnalo nelle decisioni. Il brief non conteneva
la motivazione né giudizi sul risultato.

## Oggetto

* **Strategia**: G1, cioè F5 decisa ogni giorno alle 00:00 UTC. Universo: le 100 monete più scambiate del lunedì. Segnale: −funding dei
  7 giorni. Banda 20%/40%, pesi secondo l'inverso della volatilità dei 30 giorni, ogni lato al 100%.
* **Regole**: `research/programma7/PRIMA.md` (prova 57; `3886b87`, 23 ott 06:18 UTC), codice `819853b` (06:19), risultati `bc86fee`
  (06:21), rifatti il 25 ottobre in `92bd849`. Configurazione a capitale piccolo: `research/programma7/OTTANTASEIESIMA.md` (prova 148;
  regole `f85e2dd`, 6 nov 06:04), codice `57b5b04` (06:06), risultati `6cfad80` (06:15). Ricalcolo indipendente
  `research/programma7/revisione_g1n/nucleo.py` (`921ef6b`).
* **Configurazione per il conto vero**: 280 USDT, minimi veri di Binance (`risultati_ottantaseiesima/filtri_binance_2026-11-06.json`),
  ordine limite al prezzo mark per un'ora e poi a mercato, leva 5 con margine unico, eventi spenti, partenza da conto vuoto alla
  mezzanotte UTC (`bot/portafoglio/conto_vero.py:8-35`, `demo_binance.py:13-17,73`).
* **Periodo**: dal 4 gennaio 2021 al 4 ottobre 2026 (2.100 giorni, 300 settimane). Scala: decisione giornaliera; esecuzione sulle
  candele a 1 ora delle 00:00 e delle 01:00; misure settimanali.

## Checklist A–F

Comandi: `CACHE_G1N=<scratchpad>/cache PYTHONPATH=. python3 audits/repro/<script> <parte>` (sotto, solo il nome dello script).

### A. Dati
* **Buchi, duplicati, ordine, orari UTC, valori anomali — PROBLEMA (Medio, già nel catalogo, voce 1).** Script:
  `g1_parte2_2026-11-12.py dati` ed esito `g1_buchi2022_2026-11-12_esito.txt`.
  * Mancano ancora le candele giornaliere del 26-28 febbraio 2022 (48 monete) e dell'1-2 aprile 2022 (49 monete). Le candele a 1 ora
    di quei giorni invece ci sono (24 su 24 per ETH, LUNA, WAVES e KNC), quindi i giorni si potrebbero rifare.
  * Effetti nel pannello: l'universo della settimana del 28 febbraio 2022 scende a 70 monete. Il giro è di 1,50 il 28 febbraio e di
    1,47 il 7 marzo, contro circa 0,25 nei giorni normali. Il movimento perso in quei giorni vale +2,1 punti per G1. Il totale di G1
    è +314 punti, quindi l'effetto è piccolo e va contro la strategia.
  * Altri 81 giorni hanno un buco su una sola moneta.
  * Duplicati e ordine: il pannello tiene una riga per giorno, con l'archivio che vince sull'interfaccia, ed è ordinato
    (`seconda.py:62-73`).
  * Orari: 0 candele giornaliere fuori dalla mezzanotte UTC su un campione di 40 monete.
  * Valori anomali: i rendimenti oltre il 50% tenuti (UNFI +450% il 7 giugno 2022, TRX +96% il 3 dicembre 2024, FTT −75% l'8 novembre
    2022) sono movimenti veri, con pesi piccoli.
* **Funding presente e allineato agli orari veri — OK, con un limite noto.** Script: `g1_parte2... dati` e `g1_funding_2026-11-12.py`.
  * 2.025.134 regolamenti letti dai dati: 0 a più di un minuto dal giro d'ora. Gli intervalli sono di 1, 2, 4 e 8 ore e il giorno di
    tenuta si ricava dall'orario vero (`seconda.py:76-85`).
  * Nel periodo nessun giorno tenuto da G1 ha un funding stimato diverso da zero, tranne 1 nel 2022. L'ultimo mese stimato (catalogo,
    voce 3) è fuori dal periodo, che finisce il 4 ottobre.
  * 282 giorni-moneta tenuti non hanno il dato vero e valgono zero (ICP 131 nel 2022, TLM 74, BNX 28). Il loro effetto non si può
    misurare. È il limite già noto del catalogo, voce 3.
  * 50 giorni tenuti a volume zero hanno il funding azzerato, come previsto da `controllo_zombi`.
* **Periodi uguali a quelli dichiarati — OK.** `analisi.py:22` (dal 4 gennaio al 5 ottobre 2026 escluso) coincide con `PRIMA.md:22`
  e con `OTTANTASEIESIMA.md:28`.

### B. Sguardo nel futuro e tempi
* **Segnale alla chiusura ed esecuzione dopo — OK.**
  * Il peso deciso alle 00:00 di d usa le chiusure fino a d−1 e il funding fino al regolamento delle 00:00 di d (`nucleo.py:76-78`).
  * Il limite si giudica sull'ora 00-01 di d e l'eventuale mercato si fa all'apertura delle 01:00 (`nucleo.py:189-217`).
  * Pannello tagliato rifatto con l'universo ricalcolato (`g1_2026-11-12.py taglio`): 7 giorni su 7 con differenza 0,0 e universo
    uguale.
  * Ritardo di un'ora (catalogo, voce 14; `g1_ritardo_2026-11-12.py`): tutto a mercato alle 01:00, con il movimento dalle 00:00 col
    suo segno, dà G1 1,85 e A 1,86. Il risultato non viene dall'entrare nell'istante della decisione.
* **Indicatori senza dati futuri — OK.** Finestre solo all'indietro (`nucleo.py:76-89`); la normalizzazione è un rango del giorno; non
  ci sono spostamenti negativi.
* **Più scale di tempo — OK.** Le candele orarie servono solo per l'esecuzione, dopo la decisione. Non c'è nessuna unione fra scale
  per il segnale.
* **Stop e obiettivo nella stessa candela — non si applica.** G1 non ha stop per moneta. Lo stop sul conto (−35% dal massimo) non è
  simulato; non sarebbe mai scattato: il minimo dentro il giorno, nel caso «tutto il mercato al minimo o al massimo», è il 69-71% del
  massimo (`g1_parte2... rischio`).
* **Decisione su candele chiuse — OK.** Ho rieseguito `parita_bot` con il codice del bot di oggi (`parita_g1_2026-11-12.py`): la
  candela in corso, messa a un valore falso, non cambia niente. Una segnalazione per live-path-reviewer è sotto.

### C. Esecuzione e costi
* **Commissioni coerenti con il tipo di ordine — PROBLEMA (Alto, problema 1).**
  * Valori: `TAKER` 0,05% e `MAKER` 0,02% (`nucleo.py:16`), scarto di prezzo 0,01% e 0,02% (`nucleo.py:19-20`), confermati dal
    proprietario il 7 novembre. Restano da verificare con la fascia vera del conto.
  * La ricerca conta come eseguito con la commissione da ordine limite ogni ordine il cui prezzo passa l'apertura delle 00:00: il
    97,9% (114.549 su 117.037).
  * Il conto vero manda invece un ordine limite che resta aperto, al prezzo mark, verso le 00:05 (`demo_binance.py:1332`,
    `"timeInForce": "GTC"`), e non un ordine che resta solo nel libro. Quando il mark è oltre il miglior prezzo opposto, l'ordine si
    esegue subito e paga la commissione da ordine a mercato.
  * Il demo conta questi ordini come «eseguiti a limite» (607 su 642, `ops/results/0735-12nov-stato-ribilancio-1000.md:60`) senza
    distinguere le due commissioni.
  * Quanto pesa: le quattro varianti in `g1_2026-11-12.py sensibilita` e `g1_corretto_varianti_2026-11-12.py`.

    | Variante | A a 280 USDT | G1 |
    |---|---|---|
    | Ordine limite come la ricerca | 1,90 | 1,98 |
    | Tutto a mercato | 1,83 | 1,87 |
    | Limite solo se il prezzo va oltre dello 0,05% | 1,79 | 1,78 |
    | Limite solo se il prezzo va oltre dello 0,1% | 1,69 | 1,59, e il 2023 diventa −0,9% |

    Il risultato resta buono, ma l'esame cambia esito (tabella del riepilogo).
* **Scarto di prezzo e limite eseguito solo se il prezzo supera il livello — OK.**
  * `spese_limite` usa il confronto stretto (`lo < o`, `nucleo.py:211`), con `oltre` pari a 0 nella prova. Le prove con `oltre` sono
    sopra.
  * L'ordine non eseguito paga la commissione da ordine a mercato, lo scarto e il movimento contro fino alle 01:00
    (`nucleo.py:216-217`).
* **Funding a ogni regolamento, con il segno giusto — OK.**
  * `fund = x @ F` si sottrae: chi ha comprato paga il funding positivo, chi ha venduto lo incassa (`nucleo.py:175-178`;
    `ottantaseiesima.py:113-116`).
  * È applicato per giorno di tenuta con tutti i regolamenti veri. Il funding incassato da A vale +23,4% l'anno.
* **Leva, margine e liquidazione — OK con evidenza.** La liquidazione non è simulata, ma la perdita peggiore resta lontana
  (`g1_parte2... rischio`):
  * leva 5 e margine unico (`demo_binance.py:73,1212`); esposizione lorda di A fino a 2,47 volte il capitale, quindi margine iniziale
    sotto il 50%;
  * perdita peggiore possibile in un giorno, con ogni moneta al suo estremo sfavorevole nello stesso momento (un limite alto): G1
    −59,9% (10 ottobre 2025), A −52,6% (19 maggio 2021);
  * caso «tutto il mercato insieme»: −13,9%;
  * peggior giorno vero: −8,5%;
  * con il margine unico, la liquidazione richiede di perdere circa il 95% del conto.
* **Passi, prezzi e valore minimo — OK, con i limiti dichiarati.**
  * La prova 148 arrotonda al passo e salta gli ordini sotto il minimo (`ottantaseiesima.py:79-91`). Ricalcolata: 136.849 ordini
    voluti, 122.958 saltati, 13.891 eseguiti, uguali al rapporto.
  * Usa i filtri di oggi anche per il passato (dichiarato, `OTTANTASEIESIMA.md:89`).
  * Il passo di prezzo non è simulato: il limite è al prezzo d'apertura esatto. L'effetto è trascurabile.
* **Dimensionamento e limiti fissi — PROBLEMA (Alto, problema 3).**
  * La prova 148 dichiara un capitale fisso (`OTTANTASEIESIMA.md:33`). Il conto vero invece usa il valore del conto, che sale e
    scende (`conto_vero.py:31-33`).
  * I limiti fissi di `bot/risk/hard_limits.py` non governano G1. `conto_vero.py:34-35` dice «non c'entrano». I casi nel periodo:
    * 4 giorni di G1 e 6 di A oltre la perdita giornaliera del 5% (`DAILY_LOSS_LIMIT`, `hard_limits.py:21`);
    * 65 giorni-moneta (G1) con una sola moneta che in un giorno può costare più del 3% del capitale (`MAX_RISK_PER_TRADE`,
      `hard_limits.py:18`);
    * una moneta arriva al 43,7% del capitale (BLZ venduta, 5 febbraio 2024).

### D. Misure
* **Annualizzazione — OK.** 52 settimane e 365 giorni (`nucleo.py:240`, `analisi.py:73`).
* **Numeri da riportare — OK nel ricalcolo** (`g1_parte2... misure` e `rischio`). La prova 148 riporta solo Sharpe, rendimento,
  discesa, anni, ordini, spese ed esposizione; il resto l'ho calcolato io.

  | | G1 | A, 280 USDT |
  |---|---|---|
  | Sharpe | 1,98 | 1,90 |
  | Sortino | 3,87 | 3,57 |
  | Discesa più grande, settimanale | −28,8% | −26,8% |
  | Discesa più grande, giornaliera | −30,1% | −27,8% |
  | Durata della discesa | 355 giorni (21 nov 2023 → 10 nov 2024) | 256 giorni |
  | Esposizione lorda media | 2,0 | 1,94 |
  | Spese l'anno | 6,4% | 4,1% |
  | Guadagno lordo l'anno | — | 38,6% |

  Per A, un ordine rende in media lo 0,024% del capitale e costa lo 0,0017%.
* **Concentrazione — OK.** I 5 giorni migliori fanno il 15-16% del guadagno. I 3 mesi migliori fanno il 29% (aprile 2021 da solo
  +42 punti su +314). I mesi positivi sono 48 su 70 per G1 e 46 su 70 per A.
* **Per anno e per clima di mercato — OK, con una nota.**
  * Il clima l'ho definito io: il Bitcoin nel mese oltre +10% è rialzo, sotto −10% ribasso, altrimenti laterale.
  * G1 nei mesi di rialzo (21) fa +20% l'anno, con lo Sharpe giornaliero 0,74. Nei mesi laterali (34) +69% e 2,55. Nei mesi di
    ribasso (15) +70% e 2,52. Quando il mercato sale, G1 rende poco.
  * Anni di G1: 2021 +110%, 2022 +31,7%, 2023 **+8,2%**, 2024 +68%, 2025 +72,5%, 2026 +29,5%.

### E. Eccesso di adattamento e conto delle prove
* **Varianti contate — OK.** Il registro dice 309 prove (`python3 -m research.src.registro --riepilogo`). Il conto per gruppi dà 80
  gruppi da 137 serie più 18 prove senza serie (`asticella.gruppi`).
* **Sharpe corretto — PROBLEMA (Alto, problemi 1 e 2).** Con N = gruppi (decisione dell'11 novembre) e la varianza «con l'aggiunta»
  del 23 ottobre: G1 0,867 (il registro dice 0,86) e A 0,814.
  * Con la varianza di tutti i gruppi, senza l'aggiunta, sono 0,0000: l'esito dipende dall'aggiunta. È il metodo scritto, ma va
    saputo.
  * Con N = 309: 0,65 e 0,57.
  * Le varianti di esecuzione sono nella tabella del riepilogo.
* **Sensibilità ±10% e ±20% — OK sullo Sharpe, PROBLEMA (Medio) sugli anni** (`g1_2026-11-12.py sensibilita`, 18 varianti).
  * Lo Sharpe di G1 sta fra 1,68 e 2,09, quello di A fra 1,52 e 2,08: non è un picco isolato.
  * Ma «ogni anno positivo» cade in 4 varianti su 18 di G1. Il 2023 va a −3,0% con l'entrata al 24%, il 2023 a −6,6% con il funding
    dei 6 giorni, un anno negativo con l'universo di 80 e di 90 monete. A cade in 1 variante su 18.
  * Il 2023 è l'anno debole (+8,2%).
  * Il capitale per A non è monotono (`RISULTATI_OTTANTASEIESIMA.md:84-86`: 250 USDT 1,83, 225 USDT 1,89): c'è rumore di ±0,05-0,1
    dovuto all'arrotondamento ai minimi.
* **Parametri liberi contro operazioni — OK.** 6 valori fissati prima (20%, 40%, 7, 30, 100 e 2 milioni), 117.037 variazioni, 300
  settimane.
* **Validazione a finestre — non prevista dalle regole.**

### F. Riproducibilità e parità
* **Rieseguito — OK** (`g1_2026-11-12.py base`). Senza seme, perché il calcolo è deterministico.
  * G1: 1,9815 contro 1,981 di `RISULTATI_OTTANTASEIESIMA.md`.
  * A: 1,8987 contro 1,90.
  * Rispetto a `giorni.csv.gz` committato, 12 giorni differiscono al massimo di 3e-5, dopo il nuovo scaricamento delle candele
    orarie dell'11 novembre.
* **Parità fra ricerca e bot — OK** (`parita_g1_2026-11-12.py`, che riesegue `parita_bot` con il codice di oggi del bot,
  `f5.py@953606a`). Su 60 giorni l'universo è uguale in tutti e 60, la differenza massima dei pesi di G1 è 5,6e-17 e nessun lato è
  cambiato.
* **Non verificato da qui:** che i dati del bot (interfaccia di Binance) siano gli stessi dell'archivio. È compito di
  gate2-reconciler.

## Problemi

1. **Alto: l'esame passa solo con l'ipotesi sugli ordini limite che il conto vero non replica.**
   * La ricerca paga la commissione da ordine limite sul 98% degli ordini, eseguiti al prezzo d'apertura delle 00:00. Il conto vero
     manda un ordine limite che resta aperto (`GTC`) al prezzo mark verso le 00:05 (`demo_binance.py:1304,1332`), e quell'ordine può
     eseguirsi subito come ordine a mercato. Il demo non distingue le due commissioni.
   * A 280 USDT lo Sharpe corretto è 0,81 con l'ipotesi della ricerca, 0,77 tutto a mercato e 0,73 con il limite eseguito solo se il
     prezzo va oltre dello 0,05%. La soglia è 0,80.
   * Come riprodurlo: `g1_corretto_varianti_2026-11-12.py`.
   * Correzione suggerita alla sessione principale: dal demo, la commissione pagata diviso il valore scambiato
     (`/fapi/v1/income` COMMISSION, già letto da `953606a`) dà la quota vera di ordini eseguiti con la commissione da ordine limite.
     Si rifà l'esame con quella quota, scritta prima di guardare il risultato. In alternativa si valuta un ordine che resta solo nel
     libro, ma anche lì l'esecuzione va misurata: vale la prova con `oltre`.
2. **Alto: la soglia dell'esame è cambiata dopo il risultato.**
   * `PRIMA.md:27` fissava lo Sharpe corretto a 0,95. G1 ha fatto 0,86 ed è stata scritta «non validata» (registro, prova 57).
   * La soglia è poi diventata 0,90 (P26), poi 0,80 (brief di oggi). A 280 USDT passa di 0,014.
   * Non è un errore di calcolo: è una decisione del proprietario (24 ottobre e 8 novembre), ma l'esame non è più quello scritto
     prima. Va detto così ad Alessio.
3. **Alto: rischio di concentrazione e limiti fissi che non valgono per G1.**
   * Un lato resta con poche monete per due cause verificate: i pari merito nel rango (5 febbraio 2024: 63 monete su 100 con lo
     stesso funding dei 7 giorni, 0,0021) e l'universo piccolo all'inizio del 2021 (27 monete il 5 gennaio 2021): 67 giorni con meno di 10 monete vendute (minimo
     5), 58 con meno di 10 comprate, nel 2021 e nel 2024.
   * Una sola moneta arriva al 43,7% del capitale (BLZ venduta, 5 febbraio 2024; `g1_esposizione_2026-11-12_esito.json`,
     `g1_lati_2026-11-12_esito.txt`). In 764 giorni una moneta pesa più del 10%.
   * Fra le monete vendute tenute da A, 1.131 volte il massimo del giorno è salito di oltre il 20% sopra l'apertura e 99 volte di oltre
     il 50% (massimo +145%).
   * Un rialzo del 100% su una moneta venduta al 44% costerebbe il 44% del conto prima che lo stop sul conto (controllato ogni minuto)
     possa agire.
   * La perdita giornaliera del 5% e il 3% a posizione di `hard_limits.py` non si applicano (`conto_vero.py:34-35`). Nel passato non è
     successo, ma è il rischio che la storia non ha mostrato.
   * Correzione suggerita: una decisione di Alessio (sotto). Un tetto per moneta esiste già nel nucleo (`tetto_lato`,
     `nucleo.py:134`): andrebbe provato come variante con regole scritte prima, non aggiunto ora.
4. **Alto, per chi confronta: il funding incassato dal demo negli ultimi giorni è sotto quello del paper.** Il 10 novembre +0,27%
   contro +0,42%, l'11 novembre +0,20% contro +0,36% (`ops/results/0735-12nov-stato-ribilancio-1000.md:78-86`). Il funding è più di
   metà del guadagno lordo di A (+23,4% su +38,6% l'anno). Non è nel mio perimetro: lo passo a gate2-reconciler prima di qualunque
   passo verso i soldi veri.
5. **Medio: i buchi del 2022 nell'archivio giornaliero sono ancora nel pannello** (catalogo, voce 1). L'universo della settimana del
   28 febbraio 2022 scende a 70 monete, con due giri da 1,5 e +2,1 punti persi. Le candele orarie ci sono: correzione suggerita,
   ricostruire quei giorni dalle ore. L'effetto è piccolo e contro la strategia.
6. **Medio: «ogni anno positivo» è fragile.** Il 2023 a +8,2% diventa negativo in 4 varianti su 18 con i parametri a ±10-20%, e con
   il limite più severo dello 0,1%.
7. **Medio: A non è neutrale come G1.**
   * Con il capitale fisso e gli ordini saltati, l'esposizione netta di A oscilla fra −20% e +25% (5° e 95° percentile), fino a
     +47%. In 67 giorni supera il 30%.
   * Il guadagno in più di A su G1 (+3,3 punti l'anno) non viene dal mercato (pendenza sul Bitcoin 0,001). È rumore: +30 punti nel
     2021, −15 nel 2025.
   * Il «96% di G1» della prova 148 va letto con un margine di ±0,1 di Sharpe.
8. **Basso:**
   * la prova 148 ha corretto il simulatore dopo il primo calcolo (dichiarato, `RISULTATI_OTTANTASEIESIMA.md:96-108`);
   * il capitale fisso contro il conto che si compone (dichiarato);
   * il paper del bot giudica gli ordini limite sulle candele mark (`f5.py:64-73`) e non sugli scambi;
   * il demo oggi lavora a 1.000 USDT, non a 280 (`ops/results/0735-...:61`).

## Problemi tornati da audit precedenti

Non c'erano audit precedenti di G1. Sono tornati tre errori del catalogo:
* voce 1: i buchi del 2022, ancora nel pannello;
* voce 15: i limiti fissi non simulati, e qui nemmeno applicati dal codice del conto vero;
* voce 16: i due modi di contare le prove. Il proprietario l'11 novembre ha scelto i gruppi; riporto anche N = 309 solo per capire.

Le voci 3 (funding stimato) e 14 (entrata all'istante della decisione) sono state controllate e qui non pesano.

## Segnalazioni per live-path-reviewer

* `demo_binance.py:1332` (ereditato da `conto_vero.py`): l'ordine limite `GTC` al prezzo mark può eseguirsi subito come ordine a
  mercato. La ricerca assume la commissione da ordine limite. Serve sapere se è voluto, o se serve un ordine che resta solo nel libro
  (con i rifiuti da gestire), e registrare per ogni esecuzione se è stata eseguita come ordine limite o a mercato (il campo `maker` di
  `/fapi/v1/userTrades`).
* `f5.py:123-125`: `funding_7` somma `funding_giorni.get(d, 0.0)`. Se alle 00:05 il regolamento delle 00:00 non è ancora pubblicato
  dall'interfaccia, vale zero senza avviso e il segnale cambia. Da controllare che il bot aspetti o segnali il dato mancante.
* Lo stop sul conto è controllato ogni minuto, ma una moneta venduta che pesa fino al 44% può salire più dello stop in meno di un
  minuto. Lo stop non protegge dalle perdite concentrate.

## Decisioni per Alessio

1. **Quale esame vale per G1 sui soldi veri**: 0,95 (le regole scritte prima), 0,90 o 0,80. E se lo si giudica con l'ordine limite
   come la ricerca o con la quota di commissioni vere misurata sul demo. A 280 USDT l'esito cambia fra 0,77 e 0,81.
2. **Un tetto per moneta o una perdita giornaliera massima per G1** sul conto vero. Oggi una moneta può arrivare al 44% del capitale e
   i limiti fissi non si applicano. Se sì, va provato prima come variante con regole scritte.
3. **I valori di commissione e scarto per i soldi veri**: 0,05% e 0,02% (confermati il 7 novembre). Da confrontare con la fascia vera
   del conto (sconto con BNB o no) e con la commissione per ordine misurata sul demo.
4. **Il capitale**: la prova 148 dice che sotto circa 220 USDT G1 rende chiaramente meno. Dopo una discesa come la peggiore del
   passato (−28%), 280 USDT diventano circa 200. Va deciso se aggiungere capitale o fermarsi a quella soglia.

## Domande aperte

1. Qual è la quota vera di ordini eseguiti come ordine limite sul demo, dalla commissione pagata diviso il valore scambiato? Senza
   questo numero l'esame a 0,80 della configurazione a 280 USDT non si può dire passato.
2. Perché il funding incassato dal demo il 10 e l'11 novembre è circa il 40% sotto quello del paper sulle stesse posizioni? Va chiesto
   a gate2-reconciler.
3. La soglia 0,80 del brief è una decisione scritta del proprietario? In `CLAUDE.md` c'è la decisione dell'11 novembre sul metodo (i
   gruppi), non sulla soglia. Le mie istruzioni dicono 0,90 e `PRIMA.md` dice 0,95.
4. Il demo deve tornare a 280 USDT prima dei soldi veri, o si parte con 1.000? I numeri di questo audit valgono per 280.

## File dell'audit
* `audits/repro/g1_2026-11-12.py` (parti `base`, `taglio`, `sensibilita`) con esiti `g1_2026-11-12_esito_{base,taglio,sensibilita}.json`
* `audits/repro/g1_parte2_2026-11-12.py` (`dati`, `rischio`, `misure`) con esiti `g1_parte2_2026-11-12_esito_*.json`
* `audits/repro/g1_funding_2026-11-12.py`, `g1_esposizione_2026-11-12.py`, `g1_corretto_varianti_2026-11-12.py`,
  `g1_ritardo_2026-11-12.py` con i loro esiti; `g1_lati_2026-11-12_esito.txt`, `g1_buchi2022_2026-11-12_esito.txt`
* `audits/repro/parita_g1_2026-11-12.py` con `parita_g1_2026-11-12/parita_bot.json`
