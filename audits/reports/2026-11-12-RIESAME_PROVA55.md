# Riesame della prova 55: C3, un solo punteggio da F5, K2 e M7 (12 novembre 2026)

Auditor: backtest-auditor. Riesame delle prove bocciate di poco (idea 137), riga 2 di `research/riesame/ELENCO.md`.
Nessun audit precedente di C3 (`audits/AUDIT_LOG.md`); il rapporto della prova 28 (componenti K2 e F5 + M7 + K2) l'ho letto solo dopo
aver formato il verdetto, per i problemi tornati.

## Riepilogo e verdetto

**Verdetto sul calcolo pubblicato: FAIL.** Un problema Bloccante secondo la checklist: la prova usa **una settimana oltre il periodo
scritto nelle regole** (le regole dicono «al 5 ottobre 2026», il codice arriva al lunedì 12 ottobre senza tagliare; quella settimana fa
+10,5%). In più un problema Alto: uno dei due motivi del «no» («C3 non migliora F5, 1,88 contro 1,93») **confronta periodi diversi**
(C3 dal 2022, F5 dal 2021) ed è falso sulle stesse settimane.

**Nessun errore trovato cambia il verdetto «no».** Rifatta con il codice di oggi (parità del funding corrette), il funding vero e sul
periodo dichiarato (dal 3 gennaio 2022 al lunedì 5 ottobre 2026, 249 settimane):

| | Sharpe | t | l'anno | discesa | anni positivi | Sharpe corretto: come scritto (soglia 0,95) | con l'aggiunta del 23 ott, prove fino alla 55 | regole di oggi: gruppi (80) | conto delle prove (312) |
|---|---|---|---|---|---|---|---|---|---|
| C3 corretta | 1,87 | 4,10 | +54,2% | −42,7% | 5/5 | 0,00 | 0,86 | **0,75** | 0,54 |
| C3 corretta anche dentro M7 | 1,85 | 4,05 | | | 5/5 | 0,00 | 0,85 | **0,74** | 0,52 |
| C3 come pubblicata (250 settimane, con la settimana in più) | 1,88 | 4,12 | +55,9% | −41,9% | 5/5 | 0,00 | 0,86 | — | — |

Con le regole in vigore oggi (Sharpe corretto da 0,80, ogni anno positivo, t da 3, gruppi di prove simili) C3 passa il t e gli anni ma
**non lo Sharpe corretto: 0,75**. Nessun modo di calcolarlo arriva a 0,80: anche con la settimana in più 0,79, con il taglio dei gruppi a
0,3 al massimo 0,796, con il taglio a 0,7 0,61-0,65, con il conto delle prove 0,54-0,58; e il mazzo delle prove si ferma alla 102, quindi
il numero vero è più basso.

Sul confronto con F5, dopo la correzione delle parità e **sulle stesse settimane**: C3 1,87 contro F5 **1,61** (+0,26), C3 sopra F5 in
19 variazioni dei parametri su 19 e in tutte le entrate ritardate; ma la differenza non è certa (intervallo al 95% da −0,46 a +1,01) e la
discesa di C3 è peggiore (−42,7% contro −26,9%). I tre portafogli separati F5 + M7 + K2 restano sopra (2,10): questa parte del motivo
è vera.

Il residuo delle parità pesa poco su C3 (−0,003 nel funding e in K1, −0,02 dentro M7), a differenza di F5 (−0,09).

## Oggetto

* Strategia: C3, ogni lunedì fra le 100 monete più scambiate un punteggio = media dei ranghi di −funding dei 7 giorni (F5), del segnale
  di K1 (`dodicesima.segnale_k1`) e della previsione di M7 (modello ad alberi, cinque semi), con il funding sempre presente e almeno 2
  ranghi su 3; banda di F5 (entrata nel 20%, uscita oltre il 40%), pesi secondo l'inverso della volatilità dei 30 giorni, ogni lato al
  100%; costi e funding come F5 (`terza.conto`).
* Regole: `research/programma6/CINQUANTACINQUESIMA.md`. Codice: `research/programma6/cinquantacinquesima.py`; componenti `sesta.py`,
  `dodicesima.py`, `ventitreesima.py`, `quattordicesima.py`, `ventiquattresima.py`, `ottava.py`; motori `seconda.py`, `terza.py`;
  esame `asticella.py`. Risultati: `RISULTATI_CINQUANTACINQUESIMA.md`, `risultati_cinquantacinquesima/`.
* Commit (dal remoto: la copia locale è troncata): regole e codice `2b7674b` 2026-10-23 04:23:24; risultati `a4cdea5` 04:37:40 (con
  l'aggiunta all'asticella scritta dopo il calcolo, dichiarato). Correzione delle parità `3eeb522` 05:50:56, dopo la prova.
  Repository locale `ff5f1d5`.
* Configurazione: ordini a mercato all'apertura delle 00:00 UTC del lunedì, tenuta una settimana, costo per giro 0,05% più scarto
  0,01% (BTC, ETH, SOL) o 0,02% (le altre), funding vero per giorno di tenuta. Capitale non dichiarato (rendimenti in frazione, che si
  compongono).
* Periodo dichiarato: dal 3 gennaio 2022 al 5 ottobre 2026 (`CINQUANTACINQUESIMA.md:23`). Scala: candele giornaliere, decisione
  settimanale. Esame dichiarato: `terza.esame` e `terza.esito` sugli anni 2022-2025, Sharpe corretto rivisto di `asticella.py`, soglia
  0,95 (`CINQUANTACINQUESIMA.md:27`).
* Brief: senza giudizi sul risultato; indica però «in particolare il residuo delle parità» e rimanda a `research/riesame/ELENCO.md`,
  riga 2, che contiene la colonna «perché» (motivazione: «tutti e due i motivi hanno un errore noto»). L'ho letta per trovare i file e
  non l'ho usata per il verdetto: segnalato come da regole.
* Nota: la prima versione del mio script `audits/repro/prova55_2026-11-12.py` è finita nel commit `da91124` della sessione principale
  (12:30); l'auditor non ha committato nulla.

## Checklist A–F

Comandi (dalla radice; `<m7>` è una cartella temporanea della sessione):
`PYTHONPATH=. python3 audits/repro/prova28_m7_2026-11-11.py <m7>` (M7 rifatto, 556 secondi), poi
`PYTHONPATH=. python3 audits/repro/prova55_2026-11-12.py <parte> <m7>` con le parti `base`, `m7r`, `m7r_dsr`, `sensibilita`, `tempi`,
`dati`, `rischio`, `zombi`, `senza`; esiti in `audits/repro/prova55_2026-11-12_esito_<parte>.json`.

### A. Dati

| Punto | Esito | Evidenza e comando |
|---|---|---|
| Buchi | **PROBLEMA (Basso)** | 52 monete dell'universo con giorni mancanti fra dicembre 2021 e ottobre 2026: 26-28 febbraio 2022 (48 monete), 1-2 aprile 2022 (49), più tre giorni singoli. Il movimento sopra il buco si perde (`seconda.py:253-260`): C3 perde +0,59 punti nella settimana del 21 febbraio 2022 e +0,34 in quella del 28 marzo, cioè il buco va **contro** C3. Parte `dati`, chiavi `buchi_nell_universo`, `perso_nei_buchi_del_2022`. |
| Duplicati, ordine, orario UTC | OK | Candele grezze delle 411 monete tenute da C3, dal dicembre 2021: nessun orario fuori dalla mezzanotte UTC, nessun duplicato con valori diversi, nessun file fuori ordine (parte `dati`, `candele_grezze`). |
| Valori anomali | OK | Nei giorni tenuti: 0 candele incoerenti, 0 prezzi non positivi, 110 giorni oltre ±50% (il più grande SIREN +269% il 4 aprile 2026): movimenti veri delle monete piccole. |
| Monete tolte dal listino | OK | 15 posizioni tenute in 70 giorni a volume zero (moneta chiusa durante la settimana): il conto prende il prezzo fino alla chiusura e poi resta fermo; LUNA contata a −99,99%. Contributo netto −0,54 punti (parte `zombi`). L'universo del lunedì le esclude (`terza.py:111-112`) e il funding è azzerato (`seconda.py:133-134`). |
| Funding presente e allineato | OK, con una nota | Regolamenti letti dai dati: 0 oltre il minuto; ore 0/8/16, 4/12/20 e orarie; intervalli di 1, 2, 4 e 8 ore (parte `dati`, `funding`). Il regolamento delle 00:00 va al giorno prima (`seconda.py:84`). Giorni tenuti senza il dato vero nel periodo: 1 stimato (febbraio 2022), 231 lasciati a zero (soprattutto 2022: giorni senza regolamento in mesi coperti). |
| Funding stimato dichiarato | **PROBLEMA (Medio)** | Il 23 ottobre le settimane del 28 settembre, 5 e 12 ottobre 2026 avevano il funding stimato (media dei 90 giorni, `seconda.py:88-100`), non dichiarato nei risultati. Il file si riproduce identico fino al 21 settembre; differisce **solo** in quelle 3 settimane: 5 ottobre −5,88% nel file, −0,77% con il dato vero (la stima cambia anche il segnale). Sharpe sulle 250 settimane 1,88 → 1,93 con il funding vero. Oggi le settimane tutte vere arrivano al lunedì 19 ottobre (parte `base`, `funding_stimato_per_lunedi_dal_settembre_2026`). |
| Periodi dichiarati | **PROBLEMA (Bloccante)** | `CINQUANTACINQUESIMA.md:23`: «Dal 3 gennaio 2022 [...] al 5 ottobre 2026». Il codice non taglia la fine: `cinquantacinquesima.py:56-61` passa a `te.esame` tutte le settimane del pannello, fino al lunedì **12 ottobre** (250 settimane invece di 249). La convenzione del repository per «al 5 ottobre 2026» è il lunedì 5 ottobre (`asticella.py:115-118`). La settimana in più fa +10,5% nel file (+11,8% con il funding vero): Sharpe del file 1,83 → 1,88; Sharpe corretto di oggi 0,75 → 0,79. Va a favore di C3; il verdetto era «no» lo stesso. Inizio giusto (`quattordicesima.py:28`). |

### B. Sguardo nel futuro e tempi

| Punto | Esito | Evidenza e comando |
|---|---|---|
| Segnale alla chiusura, esecuzione dopo | OK | Funding dei 7 giorni fino al regolamento delle 00:00 del lunedì (`sesta.py:31-32`), acquisti e interesse aperto fino alla domenica (`nona.py:33`, `undicesima.py:62`), volatilità fino alla domenica (`ottava.py:35`), universo con i dati fino alla domenica e l'apertura del lunedì (`terza.py:99-117`); rendimento dall'apertura del lunedì (`terza.py:138`). **Prova del taglio** (pesi rifatti con un pannello che si ferma alla domenica più l'apertura del lunedì) su sei lunedì dal 2022 al 2026: differenza massima **0,0** per C3, F5 e K2; M7 seme 1 il 7 aprile 2025: **0,0** su 100 monete (parte `tempi`). |
| Prezzo realistico | OK, con una nota (Basso) | Si entra all'apertura delle 00:00, lo stesso istante del regolamento usato nel segnale (catalogo, voce 14). Entrata all'01:00 (candele orarie, 99,8% delle posizioni coperte): C3 **1,84** (F5 1,58); alle 04:00 1,72 (1,52); un giorno dopo 1,59 (1,31). Il risultato non dipende dall'istante esatto, ma ogni ora costa. |
| Indicatori senza dati futuri | OK | Solo finestre all'indietro; ranghi fra le monete dello stesso lunedì (`terza.py:149-164`, `quattordicesima.py:101-110`); il modello si allena sulle settimane prima (`quattordicesima.py:171`, `u < w0`), l'ultima finisce all'apertura del lunedì della decisione. |
| Più scale di tempo | OK | Dati giornalieri letti al giorno `lun - 1` (domenica) per ogni lunedì (`quattordicesima.py:122-123`, `dodicesima.py:28`); nessuna unione fra scale diverse nel conto. |
| Stop e obiettivo nella stessa candela | Non si applica | Nessuno stop né obiettivo: tenuta di una settimana. |
| Solo candele chiuse | OK | Vedi sopra; nota per live-path-reviewer sotto. |

### C. Esecuzione e costi

| Punto | Esito | Evidenza e comando |
|---|---|---|
| Commissioni coerenti con l'ordine | OK | Solo ordini a mercato: 0,05% (`research/programma6/motore.py:23`, `seconda.py:288-290`), il valore confermato dal proprietario il 7 novembre; la tariffa base di Binance per i perpetui è «da verificare» sulla pagina ufficiale (non verificata da qui). |
| Scarto di prezzo | OK | 0,01% BTC, ETH, SOL; 0,02% le altre (`motore5.py:47-48`), su ogni giro di peso (`terza.py:302-305`). A costi doppi la media settimanale resta positiva (+0,95% contro +1,04%). Nessun ordine limite. |
| Funding con il segno giusto | OK | `terza.py:304,307`: netto = lordo − spese − peso × funding; chi è comprato paga il funding positivo, chi è venduto lo incassa. C3 incassa +15,2% l'anno di funding. |
| Leva, margine, liquidazione | OK (eccezione documentata) | Leva lorda 2,0 sempre (100% comprato + 100% venduto). Liquidazione non modellata, ma: giorno peggiore **−7,79%** (31 ottobre 2022), poi −7,34% (3 novembre 2025) e −6,53% (26 febbraio 2024); settimana peggiore con tutti i minimi dei comprati e tutti i massimi dei venduti insieme (limite prudente, comprende gli estremi dentro il giorno) −62,5% (settimana del 6 ottobre 2025). Con il margine unico la liquidazione resta lontana (parte `rischio`). |
| Filtri del conto vero | **PROBLEMA (Medio)** | Capitale non dichiarato. Con `bot/portafoglio/filtri_conto_vero.json`: a 280 USDT il 51% degli ordini è sotto il minimo (19% del valore); conto simulato a 280 USDT fissi **1,53** (55% degli ordini saltati), che si compone 1,81; a 1.000 USDT fissi 1,91, che si compone 1,86; tutti 5 anni su 5. Il 14,6% degli ordini è su monete senza filtro oggi (minimo 5 USDT supposto). |
| Dimensionamento e limiti fissi | **PROBLEMA (Medio)** | Rendimenti che si compongono (implicito). Leva 2 sotto `MAX_LEVERAGE` 5 (`bot/risk/hard_limits.py:17`). Ma **7 giorni sotto −5%** (`DAILY_LOSS_LIMIT`, `hard_limits.py:21`) non simulati; una moneta arriva al **21,8%** del capitale (ASTER, 20 luglio 2026), 68 settimane con una moneta sopra il 10%, senza stop, contro il 3% a operazione (`hard_limits.py:18`). F5 arriva al 43,7%. |

### D. Misure

| Punto | Esito | Evidenza e comando |
|---|---|---|
| Annualizzazione | OK | 52 settimane (`terza.py:340-341`); «l'anno» = media settimanale × 52. |
| Riporti | **PROBLEMA (Basso)** | La prova riporta Sharpe, rendimento, volatilità, discesa, anni, spese, giro, correlazione. Calcolati qui (periodo dichiarato, corretta): Sortino 3,08; discesa più lunga 57 settimane; settimane positive 61%; rapporto fra settimane vinte e perse 1,97; media a settimana +1,04% contro spese 0,095%; comprati +16,6% l'anno, venduti +39,4%; 27,5 monete per lato; nessuna settimana senza posizioni; esposizione lorda 2,0. |
| Concentrazione | OK | Le 5 settimane migliori fanno il 19,8% del guadagno (senza di loro Sharpe 1,61); i 3 mesi migliori il 27,3%. |
| Per anno e per clima | OK, con una nota | Per anno: 2022 +63,1%, 2023 +20,1%, 2024 +33,6%, 2025 +79,9%, 2026 +81,0%. Clima (Bitcoin nel mese sopra +5% rialzo, sotto −5% ribasso, altrimenti laterale; definizione di `audits/repro/prova28_2026-11-11.py:303-316`): C3 Sharpe **0,34** nei mesi di rialzo (106 settimane), 4,54 laterale (68), 2,34 ribasso (75); F5 0,37, 3,62, 2,33. Il guadagno viene dai mesi senza un forte rialzo. |

### E. Eccesso di adattamento e conto delle prove

| Punto | Esito | Evidenza e comando |
|---|---|---|
| Varianti contate | OK (registro completo) | Riga 55 del registro: 1 prova (`python3 -m research.src.registro --prova 55`); nel conto di allora 118 (`CINQUANTACINQUESIMA.md:23`), oggi **312** (`--riepilogo`). Nessun file di varianti in `research/trials/` per il programma 6 (non previsto). |
| Esame calcolato come scritto | OK, tranne il periodo | `terza.esame` con `inizio` 3 gennaio 2022 e anni pieni 2022-2025 (`cinquantacinquesima.py:61`, `quattordicesima.py:28-29`), `terza.esito` con soglia 0,95 (`terza.py:370-386`) e lo Sharpe corretto della sezione 3 di `ASTICELLA.md` (`asticella.py:188`), quello in vigore quando le regole sono state scritte. Rifatto oggi: **0,00** (65 gruppi, deviazione 2,56), identico. L'aggiunta del 23 ottobre (scritta dopo questo calcolo, dichiarato) dà 0,86. Tutte le altre condizioni dell'esame passano (intervallo sopra zero, 4 anni su 5, ultimo anno, costi doppi, trimestri 4/2/3/4, più del Bitcoin +57,6% l'anno). |
| Correzione per il numero di prove (regole di oggi) | **PROBLEMA (Alto, vedi Problemi)** | Mazzo di `asticella` di oggi (137 serie, 80 gruppi, 69 nella varianza con l'aggiunta), C3 sostituita con la serie corretta: **0,752** sul periodo dichiarato; 0,786 con la settimana in più; taglio 0,3: 0,762 (0,796); taglio 0,7: 0,610 (0,652); N = 312: 0,539 (0,582); senza l'aggiunta 0,000. Con M7 corretto anche dentro: 0,737. Il gruppo di C3 ha 28 prove (tutta la famiglia del funding: F3, F5, K1, K2, F5 + M7 + K2, G1, G11, G1N...). Parti `base` e `m7r_dsr`. |
| Sensibilità ±10% e ±20% | OK | 19 variazioni (entrata 16-24%, uscita 32-48%, volatilità 24-36 giorni, segnali 6-8 giorni, universo 80-120, tutti e tre i ranghi presenti): C3 fra **1,76 e 2,09**, sempre 5 anni su 5; sopra F5 con lo stesso cambio in 19 su 19 (da +0,23 a +0,68). I valori della prova non sono i migliori (uscita al 48%: 2,08). Nessun picco isolato. |
| Parametri liberi e operazioni | OK | 13.628 posizioni moneta-settimana e 17.171 variazioni di peso in 249 settimane; parametri: banda (2), finestre (2), universo, minimo dei ranghi, più M7 (67 ingredienti, iperparametri fissati nella prova 14). |
| Scelte fatte dopo aver visto i risultati | **PROBLEMA (Alto, vedi Problemi)** | (1) C3 unisce «le tre strategie migliori del programma» (`CINQUANTACINQUESIMA.md:4`), scelte dopo averle viste; (2) K1, uno dei tre ingredienti, è **costruzione** sugli stessi anni: due versi su tre girati dopo averli visti perdere (`DODICESIMA.md:9-11`), e le regole di C3 non lo dicono; senza K1, C3 fa 1,73 (parte `senza`); (3) la riserva di `ASTICELLA.md:68-70` nomina C3: l'aggiunta del 23 ottobre «non può validare le candidate già viste». |
| Finestre che avanzano | OK | Le regole non le prevedono per C3; M7 è allenato a finestre che avanzano (156 settimane, ogni 4), verificato con la prova del taglio. |

### F. Riproducibilità e parità

| Punto | Esito | Evidenza e comando |
|---|---|---|
| Riproduzione | OK | Codice della prova (funding senza arrotondamento, come in `2b7674b`) e dati di oggi: la serie salvata si riproduce **identica in 247 settimane su 250**; le 3 diverse sono le settimane col funding allora stimato (differenza massima 5,1 punti). Le mie funzioni coincidono con quelle della ricerca (controlli `k1_uguale_a_dodicesima`, `f7_uguale_a_sesta`, `pesi_C3_uguali_al_codice_della_prova_di_oggi`: veri). M7 rifatto da zero: diverso dal file della prova 25 solo nelle stesse 3 settimane. Sharpe corretto come scritto (0,00) e con l'aggiunta (0,86) riprodotti. |
| Commit prima dei risultati | OK | Copia locale troncata (catalogo, voce 17); dal remoto: regole e codice 04:23:24, risultati 04:37:40 del 23 ottobre. 14 minuti non escludono calcoli locali prima, ma il calcolo è deterministico e riprodotto. |
| Parità ricerca, paper, demo, bot | Non si applica | C3 non è nel paper né nel demo né nel bot (`grep` di `C3` in `bot/portafoglio/`: nessun risultato). |

## Problemi

| # | Severità | Problema | Come riprodurlo | Correzione suggerita alla sessione principale |
|---|---|---|---|---|
| 1 | **Bloccante** | **Periodo oltre quello dichiarato.** Regole: «al 5 ottobre 2026» (`CINQUANTACINQUESIMA.md:23`); codice: nessun taglio della fine (`cinquantacinquesima.py:56-61`), esame su 250 settimane fino al lunedì 12 ottobre. La settimana in più fa +10,5% (file) / +11,8% (funding vero): Sharpe del file 1,83 → 1,88, Sharpe corretto di oggi 0,75 → 0,79. Non cambia il «no». | Parte `base`: chiavi `periodi.dichiarato_al_2026-10-05` e `periodi.della_prova_al_2026-10-12`; settimana per settimana nel file `risultati_cinquantacinquesima/settimane_C3.csv.gz` (ultima riga). | Accanto ai risultati (senza toccarli) scrivere i numeri sul periodo dichiarato; nelle prove nuove con una fine scritta, tagliare nel codice (`df.index <= FINE`) prima di `te.esame`. Non rifare la prova per altri fini. |
| 2 | **Alto** | **Confronto con F5 su periodi diversi.** «C3 non migliora F5 (Sharpe 1,88 contro 1,93)» (`RISULTATI_CINQUANTACINQUESIMA.md:19`, riga 55 di `research/REGISTRO.md`, `programma6/STATO.md:65`): 1,88 è C3 dal 2022 (250 settimane), 1,93 è F5 dal 2021 (302 settimane). Sulle stesse settimane F5 fa **1,66-1,69** (file della prova 24) e **1,61-1,66** dopo la correzione delle parità: C3 è sopra di 0,17-0,28, in 19 variazioni su 19 e in tutte le entrate ritardate. La differenza però non è certa (intervallo al 95% da −0,46 a +1,01, 25% dei ricampionamenti sotto zero) e la discesa di C3 è peggiore (−42,7% contro −26,9%). Resta vero che C3 rende meno dei tre portafogli separati (2,10). Il «no» non cambia: dipende dallo Sharpe corretto. | Parte `base`: `F5_come_nel_verdetto`, `periodi.*.corretta.F5_stesse_settimane`, `bootstrap_differenza_sharpe_C3_meno_F5`; parte `sensibilita`, `riassunto`. | Nota accanto alla riga 55 del registro e a `STATO.md`: «sulle stesse settimane C3 1,87 contro F5 1,61 (dopo le parità); C3 non batte F5 + M7 + K2 (2,10); discesa −43% contro −27%». Nei verdetti, confrontare sempre sulle stesse settimane. |
| 3 | **Alto** | **Con le regole di oggi il «no» regge, a 0,05 dalla soglia, e C3 non è comunque validabile sul passato.** Sharpe corretto 0,75 (0,74 con M7 corretto), sotto 0,80; nessun metodo arriva a 0,80 (massimo 0,796 con la settimana in più e il taglio a 0,3). Il mazzo delle prove si ferma alla 102 (`asticella.py:211-235`), quindi il numero vero è più basso. In più, scritto prima: `ASTICELLA.md:68-70` nomina C3 fra le candidate già viste che l'aggiunta del 23 ottobre (senza la quale lo Sharpe corretto è 0,00) non può validare; e K1, un terzo del punteggio, è costruzione sugli stessi anni (`DODICESIMA.md:9-11`), cosa che le regole di C3 non dichiarano (senza K1: 1,73). | Parte `base`, `periodi.*.corretta.sharpe_corretto` e `regola_di_oggi_*`; parti `m7r_dsr` e `senza`. | Non promuovere C3 sul passato e non ritoccarla. Se interessa, misurarla solo in avanti accanto a F5 + M7 + K2 (decisione della sessione principale per il paper; soglia di Alessio). |
| 4 | Medio | **Funding stimato non dichiarato** nelle settimane del 28 settembre, 5 e 12 ottobre 2026 (catalogo, voce 3): la settimana del 5 ottobre passa da −5,88% a −0,77% con il dato vero; Sharpe sulle 250 settimane 1,88 → 1,93. La stima è andata contro C3. | Parte `base`, `riproduzione` e `funding_stimato_per_lunedi_dal_settembre_2026`. | Nei numeri da giudicare fermarsi all'ultima settimana con il funding tutto vero, o dichiararlo. |
| 5 | Medio | **Residuo delle parità ancora dentro M7.** La correzione del 23 ottobre arrotonda solo `sesta.funding_7`; gli ingredienti di funding del modello (`quattordicesima.py:69`, somme mobili; `:132`) hanno ancora il residuo, che decide l'ordine delle parità nei ranghi. Arrotondandoli cambia il **17,6%** delle previsioni di M7 (4.441 su 25.270): C3 1,874 → 1,851; M7 1,214 → 1,243; F5 + M7 + K2 2,096 → 2,109. `CONTROLLO_PARITA.md:28-29` diceva «pesano poco»: sullo Sharpe è vero (±0,03), sulle posizioni no. Tocca anche la misura a tavolino di F5 + M7 + K2 decisa l'11 novembre. | Parte `m7r` (scrive `Pm_r.npy` nella cartella data). | Una variante di M7 con gli ingredienti arrotondati a 12 decimali, accanto all'originale; dire nella misura a tavolino quale M7 si usa. |
| 6 | Medio | **Mazzo dello Sharpe corretto incompleto** (catalogo, voce 32): `serie_programma7` arriva alla prova 102; le prove a portafoglio dopo non ci sono. Gli 0,75 di C3 sono un massimo. | `asticella.py:211-235`. | Aggiungere le serie delle prove dopo la 102 al mazzo (la sessione principale), prima della prossima decisione sulla soglia. |
| 7 | Medio | **Capitale e filtri non dichiarati** (catalogo, voce 15): a 280 USDT fissi 1,53 (55% degli ordini saltati); a 1.000 USDT 1,91. | Parte `rischio`, `filtri` e `conto_vero_C3`. | Dichiarare il capitale in ogni prova a portafoglio. |
| 8 | Medio | **Limiti fissi non simulati**: 7 giorni sotto −5% (peggiore −7,79%) che fermerebbero il bot; una moneta fino al 21,8% del capitale senza stop. | Parte `rischio`, `perdita_peggiore_C3`, `peso_massimo_di_una_moneta`. | Decisione già aperta (Alessio): se la perdita giornaliera del 5% vale per i portafogli. |
| 9 | Basso | Buchi del 2022 non riempiti (catalogo, voce 1): −0,93 punti in tutto, contro C3. | Parte `dati`, `perso_nei_buchi_del_2022`. | Estendere `buchi_archivio` a tutto il periodo (scrive in `research/data/`: lo fa la sessione principale). |
| 10 | Basso | Entrata all'istante del regolamento usato nel segnale (catalogo, voce 14): 01:00 1,84; 04:00 1,72; un giorno dopo 1,59. | Parte `tempi`. | Riportarlo accanto al numero; nessun ritocco. |
| 11 | Basso | File di ingredienti di prima delle correzioni (catalogo, voce 12): `cinquantacinquesima.py:62-65` legge F5 + M7 + K2 e F5 dai file di prima delle parità; il mazzo di `asticella` usa «24 F5» e «55 C3» di prima. | Parte `base`, `F5_come_nel_verdetto`. | Rigenerare le serie in file accanto, senza toccare i risultati scritti. |
| 12 | Basso | Riporti incompleti nella prova (Sortino, durata della discesa, concentrazione, clima); il guadagno viene dai mesi senza un forte rialzo del Bitcoin (0,34 nei mesi di rialzo). | Parte `base`, `misure_C3_corretta_dichiarato`, `climi_C3_corretta`. | Aggiungerli ai rapporti delle prove a portafoglio. |

## Problemi tornati da audit precedenti

Nessun audit precedente su C3. Dal catalogo (`audits/KNOWN_PITFALLS.md`): voce 1 (buchi del 2022) **presente** (problema 9); voce 3
(funding dell'ultimo mese stimato) **presente** (problema 4); voce 12 (file di risultati non rigenerati) **presente** (problema 11);
voce 14 (entrata all'istante) **presente** (problema 10); voce 15 (capitale e limiti) **presente** (problemi 7-8); voci 16 e 30 (modo di
contare le prove, dipendenza dall'aggiunta) **presenti**: calcolati tutti i modi; voce 32 (mazzo incompleto) **presente** (problema 6);
voce 2 (monete tolte dal listino) gestita; voce 13 solo nel confronto F5 + M7 + K2; voci 4, 6, 7, 8, 9, 10 non presenti. La prova è del 23
ottobre, prima del catalogo (7 novembre): non è un ritorno dopo una correzione, ma gli stessi problemi trovati l'11 novembre nella prova
28 (le sue componenti) valgono anche qui.

## Segnalazioni per live-path-reviewer

* Nessun codice di C3 nel bot: niente da rivedere oggi.
* Se C3 entrasse un giorno nel paper o nel demo: il segnale di K1 usa l'interesse aperto delle 23:55 della domenica e la quota di
  acquisti della candela della domenica, che alle 00:05 non sono ancora nell'archivio; M7 va riallenato ogni 4 settimane con cinque semi;
  il funding delle 00:00 del lunedì va letto prima di decidere (come fa F5, `pesi_del_lunedi`); circa 55 monete con 17 mila variazioni
  in 249 settimane, metà sotto il valore minimo a 280 USDT.

## Decisioni per Alessio

1. C3 fa 0,75 con la soglia a 0,80 («0,90 non è un muro», 8 novembre): vale «qualche punto sotto» anche per una prova che le regole
   scritte prima (`ASTICELLA.md:68-70`) dichiarano non validabile con l'aggiunta del 23 ottobre e che contiene K1, costruzione sugli stessi
   anni? Il mio consiglio: no; è nella stessa famiglia di F5 e sotto F5 + M7 + K2 (2,10), che si misura già a tavolino.
2. Se l'esclusione della famiglia del funding dal riesame vale anche per le miscele e per i punteggi uniti (C3 sta nel gruppo di F5, con
   28 prove): domanda già aperta dall'11 novembre.
3. Costi: usati quelli confermati il 7 novembre (0,05% a mercato, scarto 0,01% e 0,02%). Perdita giornaliera del 5% nei portafogli:
   decisione già aperta (C3 la supera 7 volte).

## Domande aperte

1. «Al 5 ottobre 2026» di `CINQUANTACINQUESIMA.md:23` voleva dire l'ultimo lunedì 5 ottobre (convenzione di `asticella.periodo`, quella
   che ho usato) o l'ultima settimana disponibile? Se la seconda, il problema 1 scende a una frase da correggere nelle regole, ma il
   codice resta senza fine e la regola andava scritta così.
2. La riserva del 23 ottobre (`ASTICELLA.md:68-70`: le candidate già viste, C3 compresa, non diventano validate con l'aggiunta) vale
   ancora con la regola del 9 e dell'11 novembre (0,80 con i gruppi di prove simili, che usa proprio l'aggiunta)?
3. Il motivo del «no» della riga 55 del registro («un punteggio unico rende meno di F5 da sola») è falso sulle stesse settimane: la
   sessione principale lo corregge con una nota accanto (consigliato), o resta com'è?

Raccomandazione: non ritoccare C3 e non rifarla sugli stessi dati per salvarla. Il riesame non ha trovato errori che abbiano abbassato il
verdetto di allora: con tutte le correzioni il «no» resta; è cambiato solo il perché (non «peggio di F5», ma «Sharpe corretto 0,75 sotto
0,80, costruzione in parte, sotto i tre portafogli separati»).

## File dell'audit

* Script: `audits/repro/prova55_2026-11-12.py` (parti `base`, `m7r`, `m7r_dsr`, `sensibilita`, `tempi`, `dati`, `rischio`, `zombi`,
  `senza`), con `audits/repro/prova28_m7_2026-11-11.py <m7>` prima; usa le funzioni di `prova28_2026-11-11.py`,
  `prova28_tempi_2026-11-11.py`, `prova28_buchi_2026-11-11.py`, `prova28_conto_vero_2026-11-11.py`. Eseguire con
  `PYTHONPATH=<radice del repository>`. `m7r_dsr` vuole `Pm_r.npy` scritto da `m7r`.
* Esiti: `audits/repro/prova55_2026-11-12_esito_{base,m7r,m7r_dsr,sensibilita,tempi,dati,rischio,zombi,senza}.json`.
