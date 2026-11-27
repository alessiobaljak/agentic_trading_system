# Audit di F5 nella configurazione del conto vero (27 novembre 2026)

Auditor: backtest-auditor. Codice provato: commit `515a07e` (in `research/` e `bot/` identico a `b7a3a7b`, arrivato durante l'audit),
copiato con `git archive` in una cartella temporanea, perché durante l'audit altre sessioni modificavano `research/programma6/seconda.py`
e altri file della copia di lavoro. Pannello giornaliero congelato alle 02:33 UTC del 27 novembre (ultimo giorno 23 novembre 2026,
744 monete, impronta `9e3cf682a244b7a1`). Script e numeri: `audits/repro/f5_conto_vero_2026-11-27.py` e i suoi esiti
`audits/repro/f5_conto_vero_2026-11-27_esito_<parte>.json`. Nessun file fuori da `audits/` è stato modificato; nessun commit.

Uso dichiarato dei file in modifica da altri agenti: `research/programma6/seconda.py` e `research/programma6/asticella.py` li ho usati
**solo nella versione del commit `515a07e`** (copia congelata), mai quella in modifica; `research/programma6/paper/aggiorna.py` non
l'ho usato. Dei file di `bot/` ho importato solo le funzioni pure di `bot/portafoglio/f5.py` (versione del commit, identica alla copia di
lavoro) e ho letto `conto_vero.py` e `demo_binance.py`.

Indipendenza: il brief conteneva solo oggetto, vincoli e percorsi, nessuna motivazione né giudizio sul risultato. Ho formato il
verdetto prima di leggere gli audit precedenti che toccano F5 (prova 28, G1, prova 55, mazzo, audit del sistema del 26 novembre).

## Riepilogo e verdetto

**FAIL per la configurazione che il codice del conto vero esegue oggi (F5 a 280-300 USDT, tetto del codice 300).** La strategia in sé
è pulita: rifatta da capo torna identica alla ricerca (Sharpe 1,88, +55,3% l'anno, discesa −26,9%, ogni anno positivo), nessun dato
del futuro (17 lunedì su 17 uguali con il pannello tagliato), le funzioni del paper del bot danno gli stessi pesi della ricerca in 307
lunedì su 307. Ma **il risultato della ricerca non vale per il conto vero a 280 USDT**: la ricerca esegue ordini che il conto vero
rifiuterebbe (il 61% delle variazioni è sotto i minimi di Binance) e, rifatto con i filtri veri, cambia l'esito dell'esame:

| F5, 4 gen 2021 – 5 ott 2026 (301 settimane) | Sharpe | 2026 (l'anno) | discesa | probabilità che non sia fortuna (N alla prova 24) | t |
|---|---|---|---|---|---|
| ricerca, senza minimi, a mercato | **1,88** | +22% | −26,9% | **0,96** | 4,52 |
| 280 USDT come il bot, a mercato | 1,53 | +1% | −32,0% | 0,82 | 3,68 |
| 280 USDT, limite eseguito se il prezzo lo passa anche di poco | 1,57 | +1% | −31,9% | 0,84 | 3,78 |
| 280 USDT, limite eseguito solo oltre lo 0,05% | **1,48** | **−1%** | −32,5% | **0,79** | 3,57 |
| 280 USDT, limite eseguito solo oltre lo 0,10% | 1,40 | −5% | −32,9% | 0,72 | 3,36 |
| 300 USDT come il bot (limite: 0 / 0,05% / 0,10%) | 1,74 / 1,64 / 1,55 | +2% / 0% / −4% | −27/−29% | 0,92 / 0,88 / 0,83 | 3,7-4,2 |
| 1.000 USDT come il bot (limite: 0 / 0,05% / 0,10%) | 1,93 / 1,80 / 1,69 | +25% / +22% / +18% | −27/−29% | 0,96 / 0,94 / 0,89 | 4,0-4,6 |

In più, **il bot non chiude le posizioni rimaste sotto il valore minimo** (salta anche le chiusure, che Binance accetterebbe come
«solo riduzione»): a 280 USDT in media 7 posizioni così ogni lunedì. Una di queste, una vendita di 3,69 USDT su TUT, il 3 agosto 2026
ha perso il 13,8% del capitale in una settimana (TUT +1.049%, movimento vero). Un conto a 280 USDT partito il 29 settembre 2025 arriva a
**−35,7% dal massimo il 31 agosto 2026: lo stop sul conto sarebbe scattato**; lo stesso conto con le chiusure «solo riduzione» resta a
−20,6%.

**A 1.000 USDT il risultato regge** (PASS tecnico per quella taglia, con gli Alti sotto), ma il codice oggi non accetta un capitale
sopra i 300 USDT (`bot/portafoglio/conto_vero.py:121`). PASS o FAIL qui dicono «tecnicamente credibile» o no, non «da promuovere».

Il numero dell'esame è calcolato come dice la decisione del 23 novembre (una volta sola, con le famiglie di prove fatte fino a quando
la strategia è stata scelta): per F5 la scelta può essere la prova 24 (0,96), la prova 56 (quando il paper è passato agli ordini limite:
0,90) o il 25 novembre (N di oggi: 0,51); la configurazione a 280 USDT non è mai stata una prova registrata. La scelta è del proprietario
(decisioni sotto).

## Oggetto

* **Strategia**: F5 (prova 24, `research/programma6/VENTIQUATTRESIMA.md`): ogni lunedì alle 00:00 UTC le 100 monete più scambiate
  (mediana del volume dei 30 giorni almeno 2 milioni di USDT, almeno 200 giorni di vita), segnale −funding dei 7 giorni prima (con il
  regolamento delle 00:00 del lunedì), comprate fra il 20% con il segnale più alto, vendute fra il 20% più basso, si esce oltre il 40%
  (la banda), pesi secondo l'inverso della volatilità dei 30 giorni, ogni lato al 100% del conto. Correzione delle parità del 23 ottobre
  (`sesta.funding_7` arrotondato, `research/programma6/sesta.py:25-32`, `CONTROLLO_PARITA.md`).
* **Regole e risultati** (ordine verificato sul remoto con `gh api`, la copia locale è troncata): regole `b1c68a7` (20 ott 08:21 UTC),
  codice `76f491a` (08:22), risultati `0969f60` (09:42). Le regole furono scritte prima. Esame scritto allora: `terza.esito` con lo
  Sharpe corretto da 0,95 su 48 prove; F5 fece 0,81 e **non lo passò** (`RISULTATI_VENTIQUATTRESIMA.md:11`), entrò nel paper «come
  informazione» (regole, sezione 4).
* **Paper del bot**: `bot/portafoglio/f5.py` (funzioni pure `universo` :100, `sigma_30` :119, `funding_7` :132, `pesi_banda` :137;
  decisione il lunedì dalle 00:05, attesa del regolamento delle 00:00 per il 90% delle monete :531; ordini simulati a limite al mark per
  un'ora :73).
* **Conto vero** (spento): `bot/portafoglio/conto_vero.py` legge `data/paper_f5.json` (:129-131), decisione valida 8 giorni e 2 ore
  (:131), capitale massimo 300 USDT (:121), niente ordini nuovi oltre 600 USDT (:122), stop a −35% dal massimo o sotto il 65% del
  capitale (:123-124), somma dei pesi al massimo 2 e 60% per moneta (:125-126), leva 5 (:120) con margine unico `CROSSED`
  (`demo_binance.py:1214`); esegue con `demo_binance.ribilancia`: ordine `LIMIT` `GTC` al prezzo mark (`demo_binance.py:1334`), dopo
  un'ora il resto a mercato (`:1369-1445`); quantità arrotondate al passo verso zero e ordini saltati sotto la quantità o il valore
  minimo, chiusure comprese (`:267-286`, `:1420`); filtri veri dal 6 novembre (`bot/portafoglio/filtri_conto_vero.json`: 522 monete,
  516 con minimo 5 USDT, BTC 50 USDT con passo 0,001, ETH, LTC, BCH, LINK 20 USDT). Partenza da conto vuoto alla prima decisione di F5
  dopo l'accensione (`conto_vero.py:845-857`).
* **Configurazione provata**: 280, 300 e 1.000 USDT (anche 200, 250, 500, 2.000 per capire), capitale fisso (come la prova 148) e che
  si compone (come il bot), ordini a mercato o a limite con margini 0 / 0,05% / 0,10% / 0,20%, chiusure come il bot o «solo riduzione»
  permesse, partenza a conto vuoto il 4 gennaio 2021 e in 20-21 lunedì diversi (uno per trimestre).
* **Periodo**: dal 4 gennaio 2021 (regole, sezione 3) al 5 ottobre 2026 (fine del mazzo, `asticella.periodo`): 301 settimane; le 300
  citate il 25 novembre finiscono il 28 settembre (stessi numeri: 1,882). Scala: decisione settimanale su candele giornaliere; candele
  da 1 ora del lunedì per i costi a limite, i tempi d'entrata e lo stop.

## Checklist A–F

Comando di ogni parte (dalla radice): `python3 -I audits/repro/f5_conto_vero_2026-11-27.py <parte> --codice <copia di 515a07e>
--pannello <pannello congelato> --cache <cartella temporanea>`. Sotto: solo il nome della parte. La copia: `git archive 515a07e
research/programma5 research/programma6 research/programma7 research/src research/__init__.py bot/__init__.py bot/portafoglio
bot/config.py | tar -x` più `research/programma8` e `programma9`, con `research/data` collegato in sola lettura.

### A. Dati
* **Buchi, duplicati, ordine, UTC, anomali — PROBLEMA (Basso, misurato).** Parte `dati`; buchi riempiti a parte (sotto).
  * File grezzi delle 435 monete tenute: 0 doppioni, 0 fuori ordine, 0 candele fuori dalla mezzanotte UTC; 0 candele incoerenti
    (massimo sotto il minimo, apertura o chiusura fuori dal giorno).
  * Giorni tenuti senza candela: 97 giorni-moneta (26-27 febbraio 2022 20 monete, 1-2 aprile 2022 26 monete, 1-5 febbraio 2023 una);
    le monete escono dall'universo del lunedì dopo (catalogo, voce 1). I file orari mensili non hanno quei giorni; l'interfaccia
    pubblica di Binance sì: scaricati 237 giorni-moneta nella cartella della cache e rifatta F5 (parte `buchi`): Sharpe 1,880 → 1,872,
    +55,3% → +55,1% l'anno, 12 settimane cambiate, −1,2 punti in tutto. Il buco favoriva F5 di poco.
  * Monete tolte dal listino tenute a prezzo fermo: 82 giorni-moneta (18 monete: LUNA, FTT, FTM, MATIC, WAVES, OM...), rendimento 0 e
    funding 0 (catalogo, voce 2). Effetto trascurabile.
  * Valori anomali sui giorni tenuti: 36 giorni oltre +100% o sotto −60% (LUNA −99% il 12 maggio 2022, tenuta comprata al 3,7%; FTT;
    OM −84% il 13 aprile 2025; SIREN, ESPORTS, TUT nel 2026): movimenti veri con volumi coerenti, non errori.
* **Funding presente e allineato agli orari veri — OK.** Parte `dati`.
  * Regolamenti letti dai dati: 0 a più di un minuto dal giro d'ora; intervalli di 1, 2, 4 e 8 ore (56.071, 2.491, 1.061.145,
    974.578), sommati per giorno di tenuta (`seconda.py:84`: quello delle 00:00 va alla domenica, cioè al segnale).
  * Giorni tenuti senza dato vero (stimati o a zero): 47 giorni-moneta su 106.477, quasi tutti attorno a una chiusura del contratto.
  * Ultimo giorno di tenuta con dato vero: 31 ottobre 2026. Il periodo dell'esame (fino al 5 ottobre) è tutto vero; le settimane di
    novembre del pannello hanno il funding stimato (catalogo, voce 3) e non si usano per giudicare.
* **Periodi uguali a quelli dichiarati — OK.** Le regole dicono «dal 4 gennaio 2021» e nessuna fine; uso la fine del mazzo (5 ottobre
  2026) e riporto anche 28 settembre, 12 e 19 ottobre (parte `base`): 1,882 / 1,880 / 1,906 / 1,914. Nessun giorno oltre quelli usati
  dall'esame del repository.

### B. Sguardo nel futuro e tempi
* **Segnale alla chiusura, esecuzione dopo — PROBLEMA (Medio, catalogo voce 14).** La ricerca entra all'apertura delle 00:00 del lunedì
  (`terza.py:138`), lo stesso istante della decisione; il conto vero manda gli ordini dopo il paper (00:09 nei log del bot, più 9-14
  minuti secondo l'audit del sistema) e il resto a mercato un'ora dopo. Parte `tempi`, candele da 1 ora per tutte le 15.211 coppie
  tenute: entrata alle 01:00 **1,82**, alle 02:00 1,81, alle 04:00 1,75 (contro 1,88).
* **Indicatori senza dati futuri — OK.** Parte `taglio`: 17 lunedì (14 a caso, il primo e gli ultimi due) rifatti con il pannello fermo
  alla domenica più l'apertura del lunedì e sette giorni vuoti: differenza massima dei pesi 0,0 in tutti. Volatilità dei 30 giorni
  sulle chiusure fino alla domenica (`ottava.py:26-41`), funding dei 7 giorni fino al regolamento delle 00:00 (`sesta.py:31-32`), rango
  fra le monete della settimana (`ventiquattresima.py:34`), nessuna finestra centrata né normalizzazione sull'intera serie.
* **Più scale di tempo — OK.** Settimana = rendimenti giornalieri composti dall'apertura del lunedì a quella del lunedì dopo
  (`terza.py:136-140`); funding dei giorni di tenuta dal lunedì alla domenica. Le ore servono solo ai costi e ai tempi.
* **Stop e obiettivo nella stessa candela — non si applica** (F5 non ha stop per posizione). Lo stop del conto (−35%) non è nella
  ricerca: misurato sotto (C, rischio).
* **Decide solo su candele chiuse — OK.** Ricerca e paper usano la domenica chiusa e l'apertura del lunedì; il paper aspetta il
  regolamento delle 00:00 (`f5.py:531`). Nessuna segnalazione sul bot per questo punto.

### C. Esecuzione e costi
* **Commissioni — OK, da verificare sul conto vero.** 0,05% a mercato e 0,02% a limite (`research/programma6/motore.py:23`,
  `bot/portafoglio/f5.py:52`), come la decisione del proprietario del 7 novembre e la tariffa base dei perpetui di Binance; nessun
  documento di Binance nel repository; il demo paga 0,04% a mercato (`gate2/reports/2026-11-23-G1.md:70`).
* **Scarto e ordini limite — PROBLEMA (Alto).** Parte `costi`.
  * Scarto 0,01% su BTC, ETH, SOL e 0,02% sulle altre (`motore5.py:47-48`), mai misurato sui libri del 2021: con lo 0,10% fuori dalle
    prime 50 Sharpe 1,76; costi doppi 1,71, tripli 1,55.
  * La ricerca di F5 conta tutto a mercato (0,07% per unità scambiata). Il modello a limite della prova 56 esegue l'ordine se il prezzo
    va oltre il livello anche di poco (`cinquantaseiesima.py:30`): 98% eseguiti, Sharpe **1,94**. Chiedendo che il prezzo vada oltre
    dello 0,05%: 95% eseguiti, ma il costo medio sale allo **0,10%** per unità (più che a mercato: gli ordini non eseguiti sono quelli
    in cui il prezzo è scappato), Sharpe **1,81**; oltre lo 0,10% 1,69; oltre lo 0,20% 1,50.
  * Il paper del bot conta eseguiti a limite il 100% degli ordini (66 su 66 il 16 novembre, 64 su 64 il 23:
    `ops/results/0745-16nov-log-ribilancio-1000.md`, `0768-23nov-log-ribilancio-1000.md`). Il conto vero manda un limite `GTC` al
    mark, che si esegue subito a mercato quando il mark è oltre il prezzo opposto: sul demo di G1 circa il 27% del valore in regime e
    circa il 60% nel giorno della partenza da vuoto (`gate2/reports/2026-11-12-G1-funding-commissioni.md:66-67`). F5 non ha un demo:
    la sua quota vera non è misurata.
* **Funding a ogni regolamento con il segno giusto — OK.** `terza.py:307`: netto = lordo − spese − peso × funding (chi è comprato paga
  il funding positivo, chi è venduto lo incassa). Applicato al peso del lunedì e non alla posizione che deriva: con la deriva +0,09%
  l'anno, Sharpe 1,88 → 1,89 (parte `avanti`).
* **Leva, margine, liquidazione — OK (lontana).** Leva 5, margine unico, esposizione lorda 2 volte il conto: la liquidazione arriva
  solo con una perdita di circa il 95-99% del conto (mantenimento fra lo 0,4% e il 2,5% del nozionale, da verificare moneta per
  moneta). Parte `rischio`: giorno peggiore −10,1% (11 febbraio 2021, da apertura ad apertura), 11 giorni sotto −5%, 1 sotto −10%;
  limite prudente (tutti i comprati al minimo e tutti i venduti al massimo dello stesso giorno) −60,1% il 10 ottobre 2025: anche questo
  è lontano dalla liquidazione.
* **Passi, prezzi e minimi — PROBLEMA (Bloccante per 280-300 USDT).** Parte `conto` (simulatore controllato: senza minimi rifà la
  ricerca, Sharpe 1,880 contro 1,880, differenza media settimanale 9e-7).
  * La ricerca non dichiara il capitale e non ha minimi. A 280 USDT salta il **61%** delle variazioni (sotto i 5 USDT o sotto un passo),
    a 300 il 58%, a 1.000 il 31%. Monete volute e mai aperte a 280 USDT: BTC 112 settimane, BCH 103, LINK 92, AVAX 88, ETC 88, ETH 83,
    AXS 61, AAVE 59. Esposizione netta del conto fra −31% e +35% (la ricerca parte da zero ogni lunedì).
  * Numeri nella tabella del riepilogo; per anno a 280 USDT con il limite allo 0,05%: 2021 +130%, 2022 +38%, 2023 +18%, 2024 +58%, 2025
    +37%, **2026 −1%** (l'anno; composto −5,3% fino al 5 ottobre). Con due settimane in più (fino al 19 ottobre) il 2026 diventa +9%:
    l'esito «ogni anno positivo» a 280 USDT dipende da due settimane.
  * Con le chiusure «solo riduzione» permesse (Binance le esenta dal minimo secondo il testo del suo errore −4164, da verificare):
    280 USDT 1,63 / 1,68 / 1,58 / 1,48 (mercato, limite 0 / 0,05% / 0,10%), 2026 fra +12% e +18%; 300 USDT 1,61-1,82.
  * Con il conto che si compone (come il bot) a 280 USDT 1,76: ma solo perché il conto supera presto i 600 USDT (maggio 2021), dove il
    bot smette di fare ordini (`conto_vero.py:122`). Per giudicare la taglia vale il capitale fisso.
  * Partenze a conto vuoto in 20 lunedì (uno per trimestre), un anno dopo: a 280 USDT +43,8% in media contro +47,7% senza minimi,
    peggio in 12 su 20; l'ultima (29 settembre 2025) **+8,2% contro +37,3%**.
* **Posizioni sotto il minimo che il bot non chiude — PROBLEMA (Alto).** Parte `polvere`. Il bot salta anche le chiusure sotto il
  minimo (`demo_binance.py:280`, `:1420`): a 280 USDT 2.132 settimane-moneta con una posizione non voluta (in media 3,6 vendute e 3,4
  comprate per lunedì). Nel 2026 contano −16,5 punti contro la ricerca, quasi tutti da TUT: venduta per 3,69 USDT il 3 agosto 2026,
  +1.049% nella settimana (da 0,0176 a 0,2019, volume di 2,3 miliardi il 9 agosto) = −13,8% del capitale. Partenza il 29 settembre 2025:
  massimo il 3 novembre 2025, poi **−35,7% il 31 agosto 2026** (a mercato −36,9%, con lo stop già il 19 agosto): lo stop sul conto scatta; con le
  chiusure permesse −20,6%, senza minimi −26,1%.
* **Dimensionamento e limiti fissi — PROBLEMA (Medio, eccezione dichiarata).** Il conto vero non usa `bot/risk/hard_limits.py`
  (`conto_vero.py`, docstring). F5 li supererebbe: posizioni fino al 44% (contro il 3% a operazione, `hard_limits.py:18`), 11 giorni
  oltre la perdita del 5% (`:21`), posizioni tenute sopra gli eventi macro (`:29`). Limiti propri del conto vero: peso massimo al lunedì
  43,7% (BLZ venduta, 5 febbraio 2024), con la deriva della settimana **44,8%** (8 febbraio 2024), mai oltre il 60%; somma mai oltre 2;
  25 giorni con una moneta oltre il 30%; 12 lunedì con meno di 10 monete in un lato (gennaio-marzo 2021; 22 gennaio - 5 febbraio 2024,
  5-7 vendute: parità al funding di base, catalogo voce 27).

### D. Misure
* **Annualizzazione — OK.** 52 settimane (`terza.py:336-343`); nessuno `sqrt(252)` in `research/programma6`, `programma7`, `bot/`.
* **Riporti — OK** (parte `misure`). Ricerca: 301 settimane, +55,3% l'anno (composto +66,1%), volatilità 29,4%, Sharpe 1,88, Sortino
  3,32, discesa −26,9% (sul percorso giornaliero −28,2%, 24 marzo 2024), discesa più lunga 37 settimane, 118 settimane negative,
  peggiore −14,7% (26 febbraio 2024). Sempre investita: 50,5 monete in media, giro 1,36 volte il conto a settimana, spese 4,9% l'anno.
  Operazioni (una moneta da quando entra a quando esce da un lato): 4.301, durata media 3,5 settimane, +0,034% del conto prima delle
  spese, spesa 0,005%, netto +0,029%; vincenti 55%, fattore di profitto 1,18. Correlazione con il Bitcoin −0,10.
* **Concentrazione — PROBLEMA (Medio).** Le 5 settimane migliori fanno il 22,5% della somma dei rendimenti, i 3 mesi migliori il 27,6%
  (aprile 2021 +41,9 punti, marzo 2021 +23,7, dicembre 2024 +22,6); 21 mesi negativi su 70. A 280 USDT 28,7% e 36,0%.
* **Anni e climi — PROBLEMA (Medio).** Clima di ogni settimana dal rendimento del Bitcoin dei 91 giorni prima del lunedì (sopra +15%
  rialzo, sotto −15% ribasso, altrimenti laterale; definizione scritta prima del calcolo): rialzo 115 settimane, +98,7% l'anno, Sharpe
  2,72; laterale 108, +33,8%, 1,42; **ribasso 78, +21,0%, 0,90**. A 280 USDT nel ribasso Sharpe 0,23-0,26 (+7% l'anno). Anni (composto):
  2021 +209%, 2022 +35%, 2023 +32%, 2024 +86%, 2025 +61%, 2026 +15% (fino al 5 ottobre).

### E. Eccesso di adattamento e conto delle prove
* **Varianti dell'idea — OK, contate dal registro.** `python3 -m research.src.registro --riepilogo`: 168 prove, conto 340; F5 è una
  prova (riga 24, conto 1). La famiglia del funding fra monete nel mazzo di oggi ha 46 serie (F2, F3, F5, F6, F9, F5T, F5N, F5C, K1, K2, C3, G1 e
  le sue varianti, le miscele: parte `corretto`). Le varianti di F5 provate dopo (42, 45, 51, 53, 56, 61, 86, 89, 92, 168, 169) non
  l'hanno sostituita. `research/trials/` non ha voci per le prove fino alla 150 (non esisteva).
* **Probabilità che non sia fortuna — PROBLEMA (Alto, decisione del proprietario).** Parte `corretto` (`asticella.gruppi` e
  `terza.sharpe_corretto` del commit, taglio 0,5; fra parentesi i tagli 0,3 e 0,7):
  * N fino alla prova 24 (32 famiglie, dispersione 0,55; nessun gruppo con t sotto −3, quindi con e senza l'aggiunta del 23 ottobre è
    uguale): ricerca **0,959** (0,962 / 0,931); 280 USDT 0,72-0,84; 300 USDT 0,83-0,92; 1.000 USDT 0,89-0,96; 280 con le chiusure
    permesse 0,85-0,88. La serie vecchia del mazzo (prima delle parità) 0,966.
  * N fino alla prova 56 (65 famiglie): ricerca 0,899; 280 USDT 0,55-0,71; 1.000 USDT 0,79-0,91. Senza l'aggiunta 0,00 per tutte.
  * N di oggi (200 famiglie): ricerca 0,506 (0,616 / 0,447); 280 USDT 0,13-0,24; 1.000 USDT 0,33-0,55.
  * t: ricerca 4,52; con le settimane legate fra loro (Newey e West, 4 ritardi) 3,83, con 13 ritardi 3,76; 280 USDT 3,36-3,78, con 4
    ritardi 2,80-3,15 (sotto 3 con il limite allo 0,05% o peggio).
* **Sensibilità ±10% e ±20% — PROBLEMA (Medio).** Parte `sensi`: nessun crollo, ma F5 sta in cima al suo intorno. Entrata 0,16-0,24:
  1,80-1,90; uscita 0,32 / 0,36 / 0,44 / 0,48: 1,58 / 1,76 / 1,83 / 1,50; insieme ±20%: 1,48 / 1,58; funding di 5 / 6 / 8 / 9 giorni:
  1,79 / 1,74 / 1,73 / **1,40** (2026 negativo); volatilità di 24-36 giorni 1,86-1,90; universo di 80 / 90 / 110 / 120 monete: 1,74 /
  1,65 / 1,84 / 1,77. Media delle varianti circa 1,73: da attendersi meno di 1,88 in avanti.
* **Parametri contro operazioni — OK.** 5 parametri (entrata, uscita, giorni del funding, giorni della volatilità, monete) contro 301
  settimane e 4.301 operazioni; le regole non fissano un minimo di operazioni.
* **Validazione a finestre — non prevista** dalle regole.

### F. Riproducibilità e parità
* **Rifatta dal commit — OK.** Parte `base`: identica alla serie salvata dopo le parità (`risultati_controllo_parita/settimane_F5.csv.gz`)
  in 299 settimane su 302; le 3 diverse (28 settembre, 5 e 12 ottobre 2026) avevano il funding stimato, oggi vero (5 ottobre: −4,48%
  stimato, +0,28% vero). Sharpe al 5 ottobre: salvata 1,848, oggi 1,880. La serie della prova 24 di prima delle parità differisce in
  108 settimane (1,913). I test `tests/test_paper_f5.py`, `test_conto_vero_f5.py`, `test_conto_vero.py`: 123 passati.
* **Stesso calcolo del segnale in ricerca, paper e conto vero — OK sulla logica, NON VERIFICABILE sui dati veri.**
  * Parte `parita`: le funzioni pure del paper del bot, con gli stessi dati del pannello, danno gli stessi pesi della ricerca in 307
    lunedì su 307 (differenza massima 1e-16) e lo stesso universo; il conto vero legge i pesi del paper (stesso file).
  * Non coperti dal confronto: il bot sceglie i contratti da exchangeInfo (tipo del sottostante, contratti in chiusura entro 8 giorni,
    giorno di quotazione), la ricerca dall'elenco `ESCLUSI` e dalla prima candela; dal 14 dicembre un contratto su azioni (BEUSDT) entra
    nell'universo della ricerca e non in quello del bot (audit del sistema, motore-2).
  * Parte `avanti`: paper del bot (dai log della macchina) contro la ricerca nelle stesse 4 settimane: 26 ottobre −1,41% / +0,56%;
    2 novembre +2,60% / +2,47%; 9 novembre +4,76% / +3,45%; 16 novembre −0,24% / −2,65%; in tutto +5,7% / +3,8%. Il funding di novembre
    della ricerca è stimato, quindi il confronto non decide; nessun confronto di gate2-reconciler per F5; nessun demo di F5.

## Problemi

| # | Severità | Cosa | Come riprodurlo | Correzione suggerita alla sessione principale |
|---|---|---|---|---|
| 1 | **Bloccante** (per 280-300 USDT) | Il risultato usato per scegliere F5 per il conto piccolo (Sharpe 1,88, ogni anno positivo) non ha capitale né minimi: a 280 USDT il conto vero rifiuterebbe il 61% delle variazioni. Con i filtri veri: Sharpe 1,40-1,57, 2026 fra −5% e +1% l'anno, discesa −32/−33%, probabilità (N alla 24) 0,72-0,84 secondo come si eseguono i limiti; a 300 USDT 1,55-1,74, 2026 fra −4% e +2%. A 1.000 USDT regge (1,69-1,93). | parti `conto`, `corretto` | Prima dell'accensione una prova con le regole scritte prima: F5 a 280 e 300 USDT con i filtri di oggi, partenza vuota di lunedì, limite con i margini 0 / 0,05% / 0,10% e chiusure come il bot e «solo riduzione» (backlog P36, P37 ordini-2 e ordini-6). Decidere la taglia con il proprietario. |
| 2 | **Alto** | Posizioni sotto il minimo che il bot non chiude: 2.132 settimane-moneta a 280 USDT; TUT il 3 agosto 2026 −13,8% del capitale in una settimana; partenza del 29 settembre 2025: −35,7% e stop sul conto; con le chiusure permesse −20,6%. | parti `polvere`, `rischio`, `orario` | Mandare le chiusure sotto il minimo come «solo riduzione» dopo averlo verificato sul demo (live-path-reviewer); fino ad allora dichiararlo nel piano del conto vero. |
| 3 | **Alto** | Ordini limite: l'esame a 280 USDT passa o no secondo come si eseguono. La ricerca conta tutto a mercato, la prova 56 il 98% a limite, il paper del bot il 100%; il conto vero manda un `GTC` al mark che può eseguirsi subito a mercato. Con il margine dello 0,05% il costo per unità passa dallo 0,05% (al tocco) allo 0,10% (a mercato 0,07%) e Sharpe scende a 1,81 (senza minimi) e 1,48 (280). F5 non ha mai mandato un ordine vero. | parte `costi`; log 0745, 0768 | Misurare su ordini veri la quota a limite di un ribilancio del lunedì (per esempio sul demo, con F5 a capitale piccolo o con l'estratto delle esecuzioni di G1, backlog P33) e usare quel numero nell'esame. |
| 4 | **Alto** | Il numero dell'esame dipende da quale «scelta» si conta: N alla prova 24 0,96, alla 56 0,90, oggi 0,51; la configurazione a 280 USDT non è mai stata una prova (come variante, con N di oggi: 0,13-0,24). L'esame scritto prima per F5 era 0,95 e F5 non lo passò (0,81): la soglia di oggi (0,80) è venuta dopo (catalogo voce 29). | parte `corretto` | Chiedere al proprietario quale N vale per F5 e per la sua configurazione del conto vero; scriverlo in `allocazione/REGOLE.md` e nel registro. |
| 5 | **Alto** | Il perché della decisione del 25 novembre («F5 fa meno variazioni sotto il minimo») è vero nel conto (61% contro il 90% di G1 nella prova 148) ma non nell'effetto: a 280 USDT F5 tiene l'81-84% del suo Sharpe, G1 nella prova 148 il 96% (simulatori diversi, rumore di ±0,1: catalogo voce 28). | parte `conto`; `research/programma7/RISULTATI_OTTANTASEIESIMA.md` | Rifare F5 e G1 a 280 USDT con lo stesso simulatore prima di confrontarle per il conto piccolo. |
| 6 | **Alto** | Concentrazione da parità: 12 lunedì con meno di 10 monete in un lato, peso fino al 43,7% (44,8% con la deriva, BLZ venduta, febbraio 2024); un +100% di quella moneta costa il 44% del conto, oltre lo stop del −35%, con le posizioni tenute 7 giorni senza stop per moneta. | parti `rischio`, `avanti` | Risposta alla domanda 1 del revisore del percorso degli ordini; decidere con il proprietario un tetto per moneta o un minimo di monete per lato (idea 97 del registro). |
| 7 | Medio | Entrata all'istante della decisione: alle 01:00 1,82, alle 02:00 1,81, alle 04:00 1,75. | parte `tempi` | Nei numeri per il conto vero usare l'entrata alle 01:00. |
| 8 | Medio | Lunedì saltati: con i pesi di una settimana prima Sharpe 1,09, con un lunedì su 4 saltato 1,49. Un blocco sopra il lunedì salta la settimana (test `test_p5`). | parte `tempi` | Segnalato al revisore del percorso degli ordini (181). |
| 9 | Medio | Dipende dal clima: nel ribasso Sharpe 0,90 (a 280 USDT 0,23-0,26); i 3 mesi migliori fanno il 27,6% (a 280 il 36%). | parte `misure` | Dirlo nel piano del conto vero; misurare in avanti per clima. |
| 10 | Medio | Sensibilità: funding a 9 giorni 1,40 con il 2026 negativo; uscita ±20% 1,50-1,58; universo a 90 monete 1,65. F5 sta in cima all'intorno. | parte `sensi` | Attendersi in avanti circa 1,7, non 1,9. |
| 11 | Medio | Parità con i dati veri non dimostrata: paper del bot e ricerca differiscono fino a 2,4 punti a settimana nelle 4 settimane in avanti (funding di novembre stimato nella ricerca); universo del bot da exchangeInfo, della ricerca da `ESCLUSI` (contratti su azioni dal 14 dicembre). | parte `avanti` | Quando esce il file del funding di novembre, confronto settimanale di F5 da parte di gate2-reconciler. |
| 12 | Medio | Stop sul conto vicino alle discese di F5: discesa giornaliera fino a −28,2% (ricerca) e −29,7/−30,1% (280) contro lo stop a −35%. Sulle chiusure orarie scatta in 0 partenze su 21 per ricerca e 1.000 USDT, in 1 su 21 a 280 (29 settembre 2025 → 19 agosto 2026); con il limite prudente dell'ora (tutti agli estremi della stessa ora) in 20-21 su 21 (19 maggio 2021, 3 gennaio e 5 marzo 2024, 10 ottobre 2025). Il minuto non è misurabile qui. | parti `rischio`, `orario` | Decidere con il proprietario se lo stop a −35% va bene per F5; misurare il 10 ottobre 2025 con le candele da 1 minuto del prezzo mark. |
| 13 | Medio | Limiti fissi del vecchio sistema non applicati (posizioni fino al 44%, 11 giorni oltre −5%); tetto dei 600 USDT: con i rendimenti di F5 il conto lo passa in 1-2 anni e smette di fare ordini. | parte `rischio`; `conto_vero.py:122` | Decisione del proprietario; dire nel piano cosa succede oltre i 600 USDT. |
| 14 | Basso | Buchi del 2022 nell'archivio: riempiti dall'interfaccia di Binance, Sharpe 1,880 → 1,872 (−1,2 punti). | parte `buchi` | Riempire il pannello con `buchi_archivio --dal 2020-01-01` (P37 motore-6). |
| 15 | Basso | Scarto delle altre mai misurato (0,10% fuori dalle prime 50: 1,76). | parte `costi` | Usare le misure dello scarto del bot (`/misure/scarto`) appena ci sono abbastanza giorni. |
| 16 | Basso | Risultati non monotoni con il capitale (250: 1,56; 280: 1,53; 300: 1,69; 500: 1,97; 1.000: 1,87): rumore di ±0,1-0,15. | parte `conto` | Leggere ogni numero per taglia con quell'errore. |
| 17 | Basso | La F5 del mazzo è quella di prima delle parità (1,913 contro 1,880): sul numero dell'esame +0,007. | parte `corretto` | P35 (già nel backlog). |

## Problemi tornati da audit precedenti

* **Capitale e minimi non dichiarati** (audit della prova 28, 11 novembre, problema 4 Medio, catalogo voce 15): tornato, e qui pesa di
  più perché F5 è la strategia del conto vero.
* **Binance accetta la «solo riduzione» sotto il minimo?** (prova 28, domanda 3): ancora senza risposta; da questa domanda dipende il
  problema 2.
* **Limite `GTC` al mark che si esegue a mercato** (audit di G1, 12 novembre, Alto 1, catalogo voce 26): il codice è uguale
  (`demo_binance.py:1334`), vale anche per F5.
* **Concentrazione da parità** (G1, Alto 3, catalogo voce 27): stessa moneta, stesso giorno (BLZ, 5 febbraio 2024, 43,7%).
* **Soglia cambiata dopo il risultato** (catalogo voce 29): F5 non passò il suo esame scritto (0,81 contro 0,95).
* **Entrata all'istante della decisione** (catalogo voce 14) e **buchi del 2022** (voce 1): ancora presenti, ora misurati per F5.
* Coerente con l'audit del sistema del 26 novembre (`audits/reports/2026-11-26-AUDIT_SISTEMA.md`): punti_ciechi-3 (questo audit),
  ordini-2 (minimi a 280), ordini-3 e ordini-7 (prezzo e finestra del paper), ordini-6 (solo riduzione), motore-2 (azioni), esame (t con
  le settimane legate).

## Segnalazioni per live-path-reviewer

1. `demo_binance.py:280` e `:1420`: le chiusure sotto il minimo si saltano anche quando sono «solo riduzione»; per F5 a 280 USDT
   restano in media 7 posizioni non volute per settimana, con una perdita di coda già vista (TUT, −13,8% in una settimana).
2. `demo_binance.py:1334`: limite `GTC` al mark: si esegue subito a mercato quando il mark passa il prezzo opposto; il paper conta il
   100% a limite. Da decidere: ordine che resta solo nel libro o costo a mercato nell'esame.
3. `conto_vero.py:851`: dopo un blocco il lunedì già scritto nel file conta come fatto e la settimana salta; per F5 tenere i pesi di
   una settimana prima vale Sharpe 1,09 contro 1,88.
4. `demo_binance.py:1237`: il controllo del margine azzera il giorno e riapre a metà settimana con i pesi del lunedì (182): un
   ribilancio che la ricerca non fa.
5. `conto_vero.py:122`: oltre i 600 USDT niente ordini nuovi; con F5 succede in 1-2 anni.
6. Il peso massimo per moneta di F5 con la deriva della settimana (domanda 1 del revisore): 44,8% (BLZ, 8 febbraio 2024), mai oltre il
   60%; i limiti si controllano solo il lunedì, ma sul passato non sarebbero mai scattati.

## Decisioni per Alessio

1. **Quale numero dell'esame vale per F5**: con le prove fino alla 24 (0,96), fino alla 56 (0,90) o con quelle di oggi (0,51)? E la
   configurazione a 280 USDT, mai provata con regole scritte prima, conta come variante (con le prove di oggi: 0,13-0,24)?
2. **La taglia del conto**: a 280 USDT F5 perde circa un quinto dello Sharpe e il 2026 è vicino a zero; a 300 un decimo; da 500-1.000
   USDT è come la ricerca. Il codice oggi non accetta più di 300 USDT.
3. **Le chiusure «solo riduzione» sotto il minimo**: permetterle (serve una prova con le regole scritte prima, una verifica sul demo e il
   revisore del percorso degli ordini)?
4. **Il costo degli ordini limite nell'esame**: a mercato, limite eseguito al tocco, o limite con un margine dello 0,05%? Oggi l'esito a
   280 USDT cambia con questa scelta.
5. **Commissioni e scarto** confermati il 7 novembre (0,05% e 0,02%; 0,01% su BTC, ETH, SOL, 0,02% sulle altre): restano? Il conto
   vero paga 0,05% a mercato, il demo 0,04%.
6. **«Ogni anno positivo» con un anno a metà** (2026: 40 settimane): a 280 USDT l'esito cambia con due settimane in più.
7. **Lo stop a −35% e i limiti fissi del vecchio sistema** con F5 (posizioni fino al 44%, giorni oltre −5%): confermati?
8. Restano aperte quelle degli audit di prima (minimo di anni e di operazioni; soglia di G1; perdita giornaliera del 5% da simulare).

## Domande aperte

1. Binance accetta sui perpetui in USDT un ordine «solo riduzione» sotto il valore minimo (testo dell'errore −4164)? Va provato sul
   demo prima di cambiare il codice.
2. Che quota degli ordini del lunedì di F5 si eseguirebbe davvero a limite con un `GTC` al mark? F5 non ha un demo; il demo di G1
   (circa 73% del valore a limite in regime, circa 40% nel giorno della partenza da vuoto) è una stima accettabile?
3. Il «conto piccolo» della decisione del 25 novembre è 280 o 300 USDT (domanda 2 del revisore del percorso degli ordini, ancora
   aperta)? A 300 USDT i numeri sono migliori di un decimo di Sharpe.
4. Chi confronta ogni settimana il paper di F5 con la ricerca quando esce il funding vero di novembre? Oggi gate2-reconciler guarda
   solo G1.
5. Il proprietario vuole F5 sul conto vero sapendo che a 280 USDT, con le regole del bot di oggi, un conto partito il 29 settembre 2025
   avrebbe toccato lo stop a −35% nell'agosto 2026?

## Elenco degli esiti

`audits/repro/f5_conto_vero_2026-11-27_esito_` + `base`, `ore`, `dati`, `buchi` (scarica dall'interfaccia pubblica di Binance nella
cartella della cache), `taglio`, `parita`, `tempi`, `costi`, `conto` (con `fino_al_19_ottobre`), `rischio`, `orario`, `polvere`,
`avanti`, `misure`, `sensi`, `corretto` (`.json`). Ordine: `base` e `ore` prima (cache), `conto` prima di `misure` e `corretto`. Tutti i
numeri del rapporto escono da queste parti; i dati scaricati restano nella cartella temporanea della sessione.
