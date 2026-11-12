# Errori ricorrenti di questo repo (catalogo dell'auditor)

Ogni voce: cosa succede, dove è stato trovato, come cercarlo. La lista cresce e non si accorcia; oltre le 300 righe si
raggruppano gli errori simili senza toglierne nessuno. Aggiornato il 12 novembre 2026 (G1 per il conto vero).

## Dati

1. **Giorno mancante nell'archivio pubblico di Binance.** Il 28 ottobre 2026 manca per tutte le monete (file del giorno 404,
   file mensile di ottobre con 30 righe). Le candele giornaliere lo prendono dall'interfaccia pubblica (`giorni_api`,
   `research/programma6/buchi_archivio.py`; `seconda.candele`, `seconda.py:62-73`). Cercare: giorni mancanti fra la prima
   e l'ultima candela con `buchi_archivio.giorni_mancanti(simbolo, dal)` (sola lettura). Attenzione: il `main` di
   `buchi_archivio` scarica e scrive in `research/data/`: l'auditor non lo esegue. Da controllare anche per le candele
   orarie e da 1 minuto, che non passano da `giorni_api`. **Anche nel 2022** (trovato l'11 nov 2026, prova 28): mancano
   26-28 febbraio (48 monete) e 1-2 aprile 2022 (49 monete); `buchi_archivio` riempie solo dal 1° settembre 2026. Il
   movimento fra l'ultima chiusura prima del buco e la prima apertura dopo si perde (`seconda.rendimenti`) e la moneta esce
   dall'universo del lunedì dopo (uscita implicita all'ultima chiusura). Misura: `audits/repro/prova28_buchi_2026-11-11.py`.
2. **Simboli tolti dal listino tenuti a rendimento zero** (prezzo fermo, volume zero): sembrano posizioni piatte e
   abbassano la volatilità. `research/programma6/controllo_zombi.py`; il pannello azzera il loro funding
   (`seconda.py:133-134`). Cercare: giorni con `quote_volume == 0` e chiusura uguale al giorno prima dentro il periodo.
3. **Funding dell'ultimo mese stimato, non vero.** Dove la candela c'è e il dato di funding no, il pannello mette la media
   dei 90 giorni prima (`riempi_funding`, `seconda.py:88-100`). Cercare: confronto fra `pannello()["funding"]` e
   `seconda.funding_giorni(simbolo)` nei giorni del periodo; i giorni diversi o senza dato vero vanno dichiarati.
   Il funding stimato cambia anche il **segnale** (funding dei 7 giorni), non solo il costo: prova 28, settimana del 12 ott
   2026 di K2 da +0,51% (stimato) a +5,76% (vero). Nei numeri da giudicare fermarsi all'ultima settimana tutta vera.
   Nei mesi coperti un giorno senza regolamento resta a zero (circa 350 giorni-moneta tenuti, 2022-2026).
12. **File di risultati usati come ingredienti e non rigenerati dopo una correzione.** `ventottesima.py:38-40` legge F5 e
    M7 da `risultati_ventiquattresima/` e `risultati_venticinquesima/`; `asticella.le_prove` legge le serie salvate (per la
    prova 28 quelle di prima della correzione delle parità, 1,720 e 2,107 contro 1,78 e 2,15 di oggi). Cercare:
    `pd.read_csv(QUI / "risultati_` negli script delle prove e confrontare con un ricalcolo.

20. **Eventi persi in silenzio dalla lettura oraria di prima del 25 ottobre 2026** (`esecuzione.ore_di`, corretta in `4561064`):
    per le 100 monete con le barre del programma 5 i file mensili non si leggevano, e dove le barre cominciano dopo l'evento
    l'evento spariva come «senza candele a 1 ora». Non solo le 14 monete della revisione 105: nella prova 32 19 eventi (ICP, OP,
    APT, SEI, PENDLE, GALA, SHIB...). La 32 non è stata rifatta (la voce P27 del backlog non la elenca) e il suo file
    `eventi_N3B.csv` lo leggono 113, 33, `programma7/terza|nona|ventottesima|ventinovesima|conto_unico`. Cercare: un contatore
    «senza ore» diverso da zero; file di risultati committati prima del 25 ottobre 13:14 con `ore_di` o `trentaduesima.ore`.
21. **Tenute troncate dal mese non ancora pubblicato**: le prove a eventi scaricano solo i file mensili orari; una tenuta che entra
    in un mese non pubblicato esce «all'ultimo prezzo» (`trentesima.py:112`) prima del termine (prova 32: TEAM, GPRO, PONS a 18-22
    giorni invece di 30; PONS +20% → +61%). Cercare: `giorni` minore della durata senza uscita di protezione, entrate negli ultimi
    45 giorni prima del calcolo.
22. **Contratti su azioni, fondi e TradFi nati dal 2026 e non in `ESCLUSI`** (aggiornato l'ultima volta il 19 ottobre 2026): la
    ricerca li tiene come monete, il bot no (`bot/portafoglio/f5.py:196-202`, tipo del sottostante). Confermati PAYP («Equity
    Perpetual») e QNTX («TradFi»); circa 20 sospetti fra gli eventi della 32; quasi tutti i perpetui nati dopo il 22 ottobre (ABBV,
    PFE, BAC...). Cercare: simboli nuovi del 2026 non in `ESCLUSI`; titoli «Equity Perpetual», «TradFi», «Pre-IPO» negli annunci.

27. **Pari merito nel rango che svuotano un lato** (G1, 12 nov 2026): quando molte monete hanno lo stesso funding dei 7 giorni (il tasso
    di base), `rankdata(method="average")` le mette tutte al centro e un lato resta con 5-9 monete; con l'inverso della volatilita' una
    sola moneta arriva al 43,7% del capitale (BLZ venduta, 5 febbraio 2024; 67 giorni con meno di 10 vendute, 2021 e 2024). Cercare:
    numero di monete per lato e peso massimo per giorno (`audits/repro/g1_esposizione_2026-11-12.py`). Verificato: il 5 febbraio 2024
    63 monete su 100 al funding 0,0021; nel gennaio 2021 la causa e' l'universo piccolo (27 monete: 200 giorni di vita dai dati
    che partono dal 1° gennaio 2020).

## Sguardo nel futuro e tempi

4. **Segnale giornaliero applicato alle ore dello stesso giorno** (trovato il 7 nov 2026 in BTCORA,
   `research/prova_finta_audit/strategia.py:37-39,45`). Un segnale calcolato sulla chiusura del giorno d unito alle ore con
   `ore.index // 24` e spostato di una sola ora: le ore 1-23 usano una chiusura che arriva a mezzanotte. Effetto misurato:
   Sharpe da −1,50 a +5,01. Convenzione giusta del repo: `seconda.py:5-6` (il peso deciso alla chiusura di t vale su t+1).
   Cercare: `// 24`, `// 1440`, `join(`, `map(`, `resample(` fra scale diverse senza `- 1` sul giorno o `shift(1)` sulla
   serie giornaliera prima dell'unione. Un `shift(1)` sulla serie oraria non basta.
5. **La stabilità nei parametri non protegge dallo sguardo nel futuro.** In BTCORA lo Sharpe con lo sguardo restava fra
   4,14 e 5,46 con la media da 16 a 24 giorni. Una prova stabile non è per questo pulita.

13. **Miscela con una gamba che vale zero prima di cominciare.** `quindicesima.combina` calcola la volatilità delle 26
    settimane anche sugli zeri delle settimane senza posizioni: la gamba nuova pesa troppo all'inizio (M7 al 52% invece del
    33% nel primo trimestre 2022). Cercare: `combina(` con serie a `netto == 0` prima della prima posizione.
14. **Entrata all'istante della decisione.** Le prove settimanali entrano all'apertura delle 00:00 del lunedì, lo stesso
    istante della chiusura della domenica e del regolamento delle 00:00 usato nel segnale. Controllo: entrata all'01:00 e alle
    04:00 con le candele orarie (`esecuzione.ore_di`) e un giorno dopo (`audits/repro/prova28_tempi_2026-11-11.py`). Prova
    28: miscela 2,15 → 2,11 (01:00) → 1,89 (un giorno dopo).

## Costi

6. **Funding caricato e mai applicato** (BTCORA, `strategia.py:26` contro `strategia.py:43-50`). Cercare: una colonna
   `funding` letta e non sottratta nel conto; confrontare con le regole della prova.
7. **Scarto di prezzo assente**: costo = sola commissione. Valori del repo: `motore5.SCARTO` (0,01% BTC/ETH/SOL, 0,02% le
   altre, `research/programma5/strumenti/motore5.py:47-48`).

15. **Capitale non dichiarato e limiti fissi non simulati nelle prove a portafoglio.** Con il valore minimo dell'ordine
    (`bot/portafoglio/filtri_conto_vero.json`) la prova 28 a 280 USDT fissi scende da 2,22 a 1,53 (71% delle variazioni
    saltate); a 1.000 USDT 2,17. La perdita giornaliera del 5% (`hard_limits.DAILY_LOSS_LIMIT`) e il 3% a operazione non sono
    mai simulati nei portafogli (K2: 3 giorni sotto −5%). Modello: `audits/repro/prova28_conto_vero_2026-11-11.py`.

23. **Perdite oltre il 100% nei numeri «senza l'uscita» delle vendite allo scoperto a leva 1**: manca la liquidazione (prova 113:
    30 eventi su 632 sotto −100%, il peggiore −246%; la differenza «senza uscita» scende da +13,6 a +9,4 punti fermando la perdita
    a −100%). Cercare: `r_senza < -1` e numeri «per capire» citati a sostegno del perché.

26. **Ordine limite della ricerca contro ordine limite del conto vero** (G1, 12 nov 2026): la ricerca paga lo 0,02% su ogni limite il
    cui prezzo passa l'apertura delle 00:00 (98% degli ordini); il bot manda `LIMIT` `GTC` al prezzo mark verso le 00:05
    (`bot/portafoglio/demo_binance.py:1332`), che si esegue subito, a commissione da ordine a mercato, quando il mark e' oltre il
    prezzo migliore opposto; il demo li conta tutti «a limite». A 280 USDT lo Sharpe corretto passa da 0,81 a 0,77 (tutto a mercato)
    e 0,73 (limite solo oltre lo 0,05%). Cercare: `spese_limite(` con `oltre=0` nei numeri d'esame; rifare sempre con `oltre` 0,0005 e
    0,001 e tutto a mercato (`audits/repro/g1_corretto_varianti_2026-11-12.py`).
28. **Conto a capitale fisso con i minimi: non neutrale e rumoroso** (prova 148): gli ordini saltati fanno derivare l'esposizione
    netta fra −20% e +25% (fino a +47%); la differenza con G1 e' rumore (+30 punti nel 2021, −15 nel 2025), il capitale non e'
    monotono (250 USDT 1,83, 225 USDT 1,89). Leggere ogni «x% di G1» con ±0,1 di Sharpe.

## Misure

8. **Annualizzazione con 252 giorni** invece di 365 (BTCORA, `strategia.py:49`). Al 7 nov 2026 nessun'altra occorrenza
   in `research/`, `bot/`, `backtesting/`: `grep -rn "sqrt(252)" --include=*.py research/ bot/ backtesting/`.
9. **«Rendimento» come somma dei rendimenti semplici** senza dichiarare il capitale fisso (BTCORA, `strategia.py:48,58`:
   somma +207,9%, composto +630,7%). Una somma di rendimenti orari a valore costante implica ritocchi ogni ora non costati.
10. **Valore mancante dell'indicatore trattato come segnale**: `close > media` con la media ancora mancante dà falso, quindi
    «venduto» (BTCORA, `strategia.py:34-35,39`: 19 giorni venduti all'inizio, circa 31 punti di effetto). Cercare:
    confronti con colonne `rolling(...)` senza `min_periods`/`dropna`/posizione nulla iniziale.

16. **Due modi di contare le prove nello Sharpe corretto.** `asticella.corretto_rivisto` usa N = gruppi di prove simili
    (80 all'11 nov 2026); le prove 149-151 usano N = conto delle prove (`n_prove=N_PROVE`, 308-309) con la varianza dei
    gruppi. Per F5 + M7 + K2: 0,89 contro 0,75, con la soglia a 0,80 in mezzo. Calcolare sempre tutti e due e dire quale
    vale per le regole della prova. Cercare: `te.sharpe_corretto(` con e senza `n_prove=`.

24. **La p di un mescolamento a strati dipende dagli strati** (metodo, prova 113): trimestre 0,027, mese 0,007, settimana 0,0027.
    Lo strato si sceglie nelle regole, mai dopo; gli altri si riportano solo «per capire» e non fanno passare una prova.

29. **Soglia dell'esame cambiata dopo il risultato** (G1): `PRIMA.md:27` diceva 0,95; dopo lo 0,86 la soglia e' passata a 0,90 e poi a
    0,80 (brief del 12 nov). Dirlo sempre accanto all'esito, con la soglia scritta prima e quella del brief.
30. **L'esito dello Sharpe corretto dipende dall'«aggiunta» del 23 ottobre** (V senza i gruppi con t sotto −3): senza, G1 ha 0,0000
    invece di 0,87. Riportare tutti e due.

## Procedura dell'audit

11. **Il comando che rigenera i risultati spesso li riscrive** (BTCORA, `strategia.py:59`) e alcuni script di controllo
    scrivono fuori da `audits/` (`controllo_giorni.main` scrive `risultati_seconda/controllo_dati.json`; `buchi_archivio.main`
    scarica e scrive in `research/data/`). L'auditor importa le funzioni e le chiama senza il `main`, in uno script dentro
    `audits/repro/`.
17. **La copia locale del repository è troncata** (`git rev-parse --is-shallow-repository` → true; storia dal 30 ottobre
    2026): l'ordine fra regole e risultati si verifica sul remoto con
    `gh api "repos/{owner}/{repo}/commits?path=<file>" --jq '.[] | "\(.sha[0:7]) \(.commit.committer.date)"'`.
18. **Mai `grep -r` su `research/`** senza escludere `research/data/` (17 GB): il comando non finisce. Cercare su file o
    cartelle precise.
19. **Prova del taglio** (metodo, non errore): rifare i pesi di un lunedì con un pannello che si ferma alla domenica più
    l'apertura del lunedì e sette giorni vuoti, e confrontarli con il calcolo intero; con i modelli, sostituire anche le
    letture dei dati di posizione (`undicesima.pannello_metrics`, `quattordicesima._taker_ls`). Funzioni pronte:
    `audits/repro/prova28_2026-11-11.py` (`tagliato`, `prova_taglio`) e `prova28_tempi_2026-11-11.py` (`taglio_m7`).
25. **Candele orarie mancanti nella copia locale** (11 nov 2026): `research/data/p6` non c'è e `research/data/p6h` ha 511 simboli.
    Per rifare una prova su candele orarie si scaricano i file mensili dall'archivio pubblico di Binance in una cartella temporanea
    della sessione (`audits/repro/prova113_2026-11-11.py scarica <cartella>`, lettore `_lettore`), mai in `research/data/`.
    L'interfaccia `fapi` di Binance (elenco dei contratti) è bloccata da qui: si chiede alla sessione principale (canale della macchina).
