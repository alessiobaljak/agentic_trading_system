# Errori ricorrenti di questo repo (catalogo dell'auditor)

Ogni voce: cosa succede, dove è stato trovato, come cercarlo. La lista cresce e non si accorcia; oltre le 300 righe si
raggruppano gli errori simili senza toglierne nessuno. Aggiornato il 28 novembre 2026 (G1 a 250 USDT: voci 53-56; prima il 27 novembre, prova 168: voci 50-52 e note alle voci 3, 26, 29, 49; F5 sul conto vero: voci 44-49; prima, il 15
novembre, prova 157: margine delle coperture a pronti;
prova 161: settimane legate fra loro, limiti del bot su una gamba sola).

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
   **27 nov 2026 (F5)**: per 50 monete i file orari mensili non hanno quei giorni; l'interfaccia `www.binance.com/fapi/v1/klines`
   (raggiungibile da qui) sì: 237 giorni-moneta riempiti in una cartella temporanea, F5 1,880 → 1,872 (−1,2 punti);
   `audits/repro/f5_conto_vero_2026-11-27.py buchi`.
2. **Simboli tolti dal listino tenuti a rendimento zero** (prezzo fermo, volume zero): sembrano posizioni piatte e
   abbassano la volatilità. `research/programma6/controllo_zombi.py`; il pannello azzera il loro funding
   (`seconda.py:133-134`). Cercare: giorni con `quote_volume == 0` e chiusura uguale al giorno prima dentro il periodo.
3. **Funding dell'ultimo mese stimato, non vero.** Dove la candela c'è e il dato di funding no, il pannello mette la media
   dei 90 giorni prima (`riempi_funding`, `seconda.py:88-100`). Cercare: confronto fra `pannello()["funding"]` e
   `seconda.funding_giorni(simbolo)` nei giorni del periodo; i giorni diversi o senza dato vero vanno dichiarati.
   Il funding stimato cambia anche il **segnale** (funding dei 7 giorni), non solo il costo: prova 28, settimana del 12 ott
   2026 di K2 da +0,51% (stimato) a +5,76% (vero). Nei numeri da giudicare fermarsi all'ultima settimana tutta vera.
   Nei mesi coperti un giorno senza regolamento resta a zero (circa 350 giorni-moneta tenuti, 2022-2026).
   27 nov 2026 (prova 168): le serie di G1, G11 e G1 neutra salvate il 25 ottobre (ingredienti della variante A) hanno il funding dal
   1° al 4 ottobre 2026 stimato, anche nel segnale: ultima settimana di G1 +0,36% contro +1,08% vero (rifatta con ottobre stimato
   +0,41%); `audits/repro/prova168_2026-11-27.py ultima`.
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
35. **Fine del periodo scritta nelle regole e non nel codice** (prova 55, 12 nov 2026): `CINQUANTACINQUESIMA.md:23` «al 5 ottobre
    2026», `cinquantacinquesima.py:56-61` passa a `te.esame` tutte le settimane del pannello (fino al 12 ottobre): una settimana in
    piu', +10,5%, Sharpe 1,83 → 1,88. Convenzione del repository: «al <lunedi'>» = ultimo lunedi' (`asticella.periodo`). Cercare:
    «al <data>» nelle regole e `te.esame(df, ...)` o `numeri_settimana(...)` senza `df.index <= FINE`; per la checklist e' Bloccante.
36. **Residuo delle parita' del funding** (`CONTROLLO_PARITA.md`, 23 ott): la differenza di somme cumulate o mobili lascia circa 1e-17,
    che decide l'ordine delle monete con lo stesso funding (circa il 6% per settimana) e non a caso. Corretto solo in `sesta.funding_7`
    (dalla prova 57); **non** negli ingredienti di M7 (`quattordicesima.py:69,132`: arrotondandoli cambia il 17,6% delle previsioni,
    C3 −0,02, M7 +0,03) ne' nelle prove fino alla 56. Effetto per strategia molto diverso: F5 −0,09, C3 −0,003. Cercare: `cumsum`,
    `rolling(...).sum()` del funding usati in un rango senza `np.round(..., 12)`; misura: `audits/repro/prova55_2026-11-12.py m7r`.

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
    Anche nelle prove a eventi orari (prova 96, 12 nov): entrata all'apertura dell'ora dopo il segnale; con 1-5 minuti di ritardo
    (minuti dell'archivio giornaliero) +0,61% → +0,57-0,58%, con 15 minuti +0,47%. `audits/repro/prova96_2026-11-12.py entrata`.

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
    **27 nov 2026 (F5)**: il paper del bot conta a limite il 100% (66 su 66 il 16 novembre, 64 su 64 il 23); sul demo di G1 a mercato circa
    il 27% del valore in regime e il 60% alla partenza da vuoto (`gate2/reports/2026-11-12-G1-funding-commissioni.md:66-67`); F5 senza
    minimi 1,94 (al tocco) / 1,88 (a mercato) / 1,81 (oltre 0,05%: costo per unità 0,10%, più che a mercato) / 1,69 (0,10%).
    **27 nov 2026 (prova 168)**: l'esame in vigore passa solo al tocco (A/B 0,847/0,852); tutto a mercato 0,791/0,791, oltre lo 0,05%
    0,743/0,732, con il 27% a mercato del demo (media dei due costi, ottimistica) 0,833/0,837. Parti `costi`, `misto` dello script.
28. **Conto a capitale fisso con i minimi: non neutrale e rumoroso** (prova 148): gli ordini saltati fanno derivare l'esposizione
    netta fra −20% e +25% (fino a +47%); la differenza con G1 e' rumore (+30 punti nel 2021, −15 nel 2025), il capitale non e'
    monotono (250 USDT 1,83, 225 USDT 1,89). Leggere ogni «x% di G1» con ±0,1 di Sharpe.
33. **Strategia sugli eventi macro dentro la finestra vietata dai limiti fissi** (prova 96, 12 nov 2026): `hard_limits.py:29`
    `MACRO_FLAT_HOURS` = 2 ore fuori dal mercato prima e dopo un evento macro; la prova entra un'ora dopo il comunicato della Fed e
    il guadagno sta in quell'ora (alla prima ora permessa p da 0,02 a 0,18). Cercare: prove su riunioni, dati macro, comunicati con
    entrata entro 2 ore dall'evento; rifarle con l'entrata dopo la finestra.

40. **Margine della gamba venduta contato senza le perdite chiuse** (prova 157, 15 nov 2026): `novantacinquesima.py:64-76` confronta la sola
    perdita aperta della quantita' rimasta (`L = Q * (P - Pe)`) con la riserva accresciuta delle vendite (`Rc += e`) e dimentica la perdita
    chiusa `q * (P - Pe)` della parte ridotta; scatta a margine zero, senza mantenimento, una volta al giorno. Il margine vero va sotto zero
    (BTC 335 aperture, −22% del nozionale), la leva supera 5 per 987 giorni, 9 liquidazioni nella giornata; il conto pubblicato guadagna
    di piu' (10,5% contro 7,3% con un margine possibile) perche' tiene fino a 2,3 volte il nozionale. Cercare: `riserva`, `Rc`, `margine`
    in ogni prova coperta (pronti contro perpetuo, trimestrali come la 159) o a leva; rifare con il portafoglio dei future a patrimonio
    (`audits/repro/prova157_2026-11-15.py margine`, convalida a 1e-16; esempio minimo `esempio`). Il pronti nel portafoglio a pronti
    non fa da margine.
41. **Massimo del giorno del prezzo scambiato al posto del mark** (prova 157): le liquidazioni le decide il prezzo mark; il massimo del
    pannello ha picchi che il mark non ha (BTC +36,2% sull'apertura il 26 luglio 2021). L'archivio del mark orario
    (`data/futures/um/monthly/markPriceKlines/<S>/1h/`) manca di 216 ore su BTC (fra cui 24-27 luglio 2021) e 72 su ETH: riempire col prezzo
    scambiato orario (piu' severo) e dirlo. Scarico in cartella temporanea: `audits/repro/prova157_2026-11-15.py scarica <cartella>`.
43. **Limiti fissi del bot che vedono una gamba sola di una copertura** (prova 161): la perdita giornaliera del 5% (`hard_limits.py:21`)
    sul solo portafoglio dei future scatta in 224-338 giorni per moneta (sul patrimonio 1-2); la leva massima 2 in alta volatilita'
    (`hard_limits.py:33-37`) e' sotto la leva che la regola accetta (2,2, nella giornata 3,27). Un limite che chiude il perpetuo lascia il
    pronti scoperto. Cercare: strategie con due gambe su portafogli diversi; misura `audits/repro/prova161_2026-11-15.py limiti_bot`.
    Da misurare anche la quota del guadagno dal tasso di base del funding (0,01% ogni 8 ore, fissato dalla borsa): 161 il 29-30%,
    senza il 2022 diventa negativo (`... tasso_base`).
44. **Posizioni sotto il minimo che il bot non chiude** (F5 sul conto vero, 27 nov 2026): `demo_binance.ordini_del_giorno`
    (`demo_binance.py:280`) e il resto a mercato (`:1420`) saltano ogni ordine sotto la quantità o il valore minimo, anche le chiusure
    che Binance accetterebbe come «solo riduzione» (testo dell'errore −4164, da verificare). In una strategia a settimana su un conto
    piccolo restano posizioni non volute (F5 a 280 USDT: 2.132 settimane-moneta, circa 7 per lunedì) e la coda costa: TUT venduta per
    3,69 USDT il 3 agosto 2026, +1.049% in una settimana, −13,8% del capitale; partenza del 29 settembre 2025 → −35,7% e stop sul conto
    (con le chiusure permesse −20,6%). La prova 28 aveva l'ipotesi opposta (chiusure sempre fatte). Cercare: simulazioni a capitale
    dichiarato con una sola delle due ipotesi; rifarle con tutte e due (`audits/repro/f5_conto_vero_2026-11-27.py polvere`, `conto`).
45. **Strategia scelta per un conto piccolo con i numeri della ricerca senza minimi** (F5, decisione del 25 nov 2026): citati Sharpe 1,88
    e «meno variazioni sotto il minimo»; con i filtri veri a 280 USDT 1,40-1,57 (81-84% del suo Sharpe; G1 nella prova 148 il 96%),
    2026 fra −5% e +1% l'anno, discesa −32/−33%; a 1.000 USDT regge. Il numero di variazioni saltate (61% contro 90%) non dice l'effetto.
    Cercare: proposte o decisioni per capitali sotto i 1.000 USDT senza una prova a capitale dichiarato con le regole scritte prima.

53. **Il capitale del conto vero simulato in un modo solo** (G1 a 250 USDT, 28 nov 2026): oltre 600 USDT di valore il conto vero non manda
    ordini (`conto_vero.py:127,811`) finché non c'è un capitale nuovo, che chiude tutto e riapre da zero (`demo_binance.parti_da_zero`).
    Simulato come una riduzione senza chiusura G1 fa 1,75, come il bot (chiusura e riapertura) 1,91; capitale fisso 250 1,86, che si compone
    senza tetto 1,95; capitali fissi da 200 a 400 fra 1,56 e 1,88, non in ordine. Riportare sempre le basi (fissa, tetto come il bot,
    composta) e leggere ogni differenza sotto 0,15 come rumore. `audits/repro/g1_conto_vero_250_2026-11-28.py conto`, `rumore`.
54. **«Chiusure solo riduzione» con due significati** (prova 148 contro questo audit): la A2 della 148 permette sotto il valore minimo
    tutte le riduzioni (`ottantaseiesima.py:81-82`) e conclude «permettere le chiusure peggiora» (1,83 contro 1,90); permettendo solo le
    chiusure a zero il conto migliora in 8 capitali su 9 (da +0,01 a +0,11) e la polvere sparisce. Cercare: `riduce` contro `obi == 0` nei
    simulatori; dire sempre quale delle due.
55. **Monete col minimo alto sotto-tenute nei conti piccoli** (G1 a 250 USDT): il Bitcoin (50 USDT, passo 0,001) è tenuto per il 7,7% del
    peso voluto, ETH, BCH, LTC, ETC e LINK (20 USDT) per il 45%, le altre per il 90%; sono le monete meno volatili, cioè quelle col peso
    più grande nell'inverso della volatilità, e il conto si sposta sulle più volatili. Esposizione netta fino a −45%/+40% (G1 la tiene a
    zero): settimana peggiore −13,0% contro −7,5% (21-27 marzo 2022, netta fra −17% e −38%). Misura: `... mancanti`.
56. **Demo a un capitale diverso da quello del conto vero** (G1, 28 nov 2026): il demo gira a 1.000 USDT, il conto vero a 250; a 1.000 il
    portafoglio vero si scosta da quello voluto di circa il 10% del conto, a 250 di circa il 45%, e lo scarto giornaliero dalla ricerca
    raddoppia o triplica. La prova in avanti del demo non misura la configurazione da promuovere. Controllo utile: il simulatore a 1.000
    dalla partenza dell'8 novembre rifà gli ordini «sotto il minimo» del demo (23 nov 34 contro 31, 26 nov 52 contro 48;
    `ops/results/*stato*.md`, riga «ultima decisione»): convalida il simulatore sul bot vero (`... avanti`).

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
    Metodo (12 nov): i tagli 0,3 e 0,7 vanno sempre riportati (`ASTICELLA.md:35,46-48`); la miscela F5 + M7 + K2 fa 0,839 / 0,755.

24. **La p di un mescolamento a strati dipende dagli strati** (metodo, prova 113): trimestre 0,027, mese 0,007, settimana 0,0027.
    Lo strato si sceglie nelle regole, mai dopo; gli altri si riportano solo «per capire» e non fanno passare una prova.

29. **Soglia dell'esame cambiata dopo il risultato** (G1): `PRIMA.md:27` diceva 0,95; dopo lo 0,86 la soglia e' passata a 0,90 e poi a
    0,80 (brief del 12 nov). Dirlo sempre accanto all'esito, con la soglia scritta prima e quella del brief.
    27 nov 2026 (prova 168): non la soglia ma la regola (V simmetrica e settimane efficaci) decisa dopo i numeri: 0,702/0,722 con la
    regola scritta nelle regole della prova, 0,842/0,852 con quella nuova.
30. **L'esito dello Sharpe corretto dipende dall'«aggiunta» del 23 ottobre** (V senza i gruppi con t sotto −3): senza, G1 ha 0,0000
    invece di 0,87. Riportare tutti e due.
    Prova 161 (15 nov): 1,00 con l'aggiunta (asticella 1,885), 0,0000 senza (asticella 10,16), e 1,00 anche per «sempre dentro»: il
    valore non ha vie di mezzo e non distingue il segnale. Controllo: rifare sempre con la versione banale della strategia
    (`audits/repro/prova161_2026-11-15.py corretti`).
31. **Controllo su «giorni a caso» più calmi degli eventi** (prova 96, 12 nov 2026): le medie di 46 giorni senza riunione hanno la
    dispersione dei giorni calmi (1,48% contro 2,05% per operazione), e «nessuna delle 2.000 estrazioni arriva alla media» sembra una p
    di zero; a pari dispersione la quota è 0,95%. Cercare: `quota_caso`, `estrazioni` di giorni senza evento citate a sostegno;
    confrontare le deviazioni e riportare la quota a pari dispersione (`audits/repro/prova96_2026-11-12.py controllo`).
32. **Prove non nel mazzo dello Sharpe corretto**: `asticella.serie_programma7` (`asticella.py:211-265`) ha le prove a eventi del
    programma 7 fino alla 74 e quelle a portafoglio fino alla 102; la 96 manca, e le prove a portafoglio dopo la 102 (12 nov, prova 55).
    Lo Sharpe corretto calcolato con questo mazzo e' un massimo. Cercare: il numero della prova nelle liste di `serie_programma7`.
    **12 nov (commit `78235da`)**: completato fino alla 152, ma restano fuori 27 varianti contate senza serie (108, 111, CC della 110)
    contro `ASTICELLA.md:31-32` (le prove senza serie contano ognuna come un gruppo a se'), e la 151; dentro le conferme 50 e 106 che il
    registro non conta. Confronto prova per prova: `audits/repro/mazzo_2026-11-12.py copertura` (somma della riga «Totale nel conto»).
37. **Variante sbagliata da un file di eventi con la colonna del filtro** (mazzo, 12 nov 2026): `asticella.py:341-346` legge interi
    `eventi_P9C.csv` e `eventi_P9C_lunga.csv`, la regola delle prove 81 e 82 e' il funding >= 0,0001 (`programma9/terza.py:31-32`);
    la 82 diventa identica alla 75. Cercare: file con colonne `funding_8h`, `gruppo`, `gratis`, `bandiera`, `tipo` letti senza il filtro
    della regola; doppioni esatti nel mazzo (`mazzo_2026-11-12.py copertura`, `gemelle`); media di `r` contro la riga del registro.
38. **`asticella.corretto_rivisto` con le sole serie della prova** conta il mazzo fino alla 48 (56 famiglie): prova 152 0,88 invece di
    0,744; la 153 (`novantunesima.py:253`) lo chiama cosi'. Cercare: `corretto_rivisto(` senza `serie_nuove()` nel primo argomento.
39. **Etichetta della settimana spostata**: 110 SS vende il venerdi' g0 e chiude il venerdi' dopo, etichetta `g0 - 4` (il lunedi' prima:
    una settimana in anticipo; `quarantottesima.py:131`); 139 CF tre settimane di domenica (`settantasettesima.py:69`, rapporto del
    lunedi' + 6). Cercare: indice `% 7 != 4`; correlazione con serie vicine piu' alta a una settimana che alla stessa
    (`mazzo_2026-11-12.py allinea`).
34. **Confronto fra strategie su periodi diversi nel verdetto** (prova 55, 12 nov 2026): «C3 non migliora F5, 1,88 contro 1,93» mette
    C3 dal 2022 (250 settimane) contro F5 dal 2021 (302); sulle stesse settimane F5 fa 1,69 (1,61 dopo le parita') e C3 e' sopra.
    Cercare: Sharpe di un'altra prova citati nel verdetto e presi da un altro `RISULTATI_*.md` o `esame.json` con un `inizio` diverso;
    rifare sempre sulle stesse settimane (`audits/repro/prova55_2026-11-12.py base`, `F5_come_nel_verdetto`).
42. **Settimane legate fra loro nelle strategie a incasso quasi fisso** (coperture del funding, prova 161, 15 nov 2026): t = Sharpe ×
    radice di settimane/52 (`terza.py:340-342`) presume settimane indipendenti; con il funding che resta alto o basso per mesi la
    correlazione a una settimana e' 0,76. t da 8,65 a 3,24 (13 settimane di ritardo), 2,81 (26), 2,52 (52); Sharpe l'anno da 3,6 a circa
    0,9-1,0; la famiglia risulta la piu' alta del mazzo (3,29). Lo Sharpe corretto con le settimane efficaci resta 0,97-0,99 (non e'
    l'autocorrelazione a saturarlo, e' la volatilita' quasi nulla). Cercare: volatilita' annua sotto il 3%, `w.autocorr(1)` sopra 0,3,
    serie usate in miscele pesate sulla volatilita'. Misura: `audits/repro/prova161_2026-11-15.py robustezza_t`.
    27 nov 2026: il segnale (correlazione a una settimana sopra 0,3) non scatta per G1 (0,19), ma il t robusto di G1 con 4 ritardi
    e' 3,72 contro 4,73. Da oggi `asticella.esame` scrive il t robusto accanto per ogni prova.
46. **Il numero dell'esame «alla scelta» dipende da quale scelta** (F5, 27 nov 2026, decisione del 23 novembre): N alla prova in cui la
    strategia è nata (24: 0,959), a quella che ne ha cambiato l'esecuzione (56: 0,899), alla scelta per i soldi veri (N di oggi: 0,506);
    una configurazione mai registrata (F5 a 280 USDT) come «variante» prende N di oggi (0,13-0,24). Riportare sempre i tre e chiedere.
    Misura: `audits/repro/f5_conto_vero_2026-11-27.py corretto` (mazzo tagliato per numero di prova).
47. **Lunedì saltati in una strategia a settimana** (F5): con i pesi di una settimana prima Sharpe 1,09 contro 1,88; un lunedì su 4
    saltato 1,49. Il conto vero salta la settimana se è bloccato quando arriva la decisione (`conto_vero.py:851`). Cercare: una validità
    lunga della decisione (8 giorni e 2 ore) letta come «il ritardo non costa» (`... tempi`).

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
    Il 27 novembre `data.binance.vision` e `www.binance.com/fapi/v1/klines` (candele) rispondevano da qui.
48. **Resti della virgola mobile contati come posizioni** (simulatore dell'audit di F5, 27 nov 2026): sommando e togliendo quantità
    sul passo restano 1e-16 che sembrano posizioni (6.065 settimane-moneta di «polvere» invece di 2.132). Dopo ogni ordine riportare le
    quantità sulla griglia del passo e azzerare i valori sotto 1e-9.
49. **Cartella temporanea con le cache di audit vecchi**: il 27 novembre la cartella temporanea della sessione aveva `cache/ore.pkl` del
    12 novembre (G1, altro formato) e lo script l'ha letto come suo. Usare sempre una cartella di cache con il nome dell'audit; e con
    altre sessioni che modificano `research/` durante l'audit, provare il codice del commit copiato con `git archive` e un pannello
    congelato (`audits/repro/f5_conto_vero_2026-11-27.py --codice --pannello`).
    **Attenzione** (27 nov): `costruisci_pannello` di un commit vecchio scrive in `seconda.PANNELLO`; con `research/data` collegata nella
    copia del commit sovrascriverebbe il pannello vero: spostare `PANNELLO` prima della chiamata
    (`audits/repro/prova168_pannello_commit_2026-11-27.py`, con il controllo che l'uscita non sia in `research/data`).
50. **La V simmetrica toglie da V la famiglia della candidata** (esame dal 27 nov 2026; prova 168): la famiglia di G1 (46 serie, t sopra +3)
    esce da V e la candidata si abbassa la soglia: 168 B 0,852 → 0,822 con la famiglia in V, A 0,842 → 0,810, G1 0,765 → 0,724. Riportare
    sempre i due numeri: `audits/repro/prova168_2026-11-27.py esame` (`esame_con(..., famiglia_in_v=True)`).
51. **Esito dell'esame che cambia nell'intorno anche con lo Sharpe stabile** (prova 168): con ±10% e ±20% dei parametri Sharpe di B fra 1,91
    e 2,22 (nessun picco isolato), probabilità fra 0,72 e 0,89, 5 vicini su 24 sotto 0,80 (anche l'universo a 90 monete, −10%). Per un esito
    a pochi centesimi dalla soglia rifare la probabilità nell'intorno con V e N fermi (`... sensi`).
52. **Limite prudente ora per ora per il rischio nel giorno** (metodo, prova 168): tutti i lunghi al minimo e i corti al massimo della stessa
    ora (B −47,5% il 10 ottobre 2025 alle 21:00) sta fra quello giornaliero (−62,6%) e le chiusure orarie (−0,6%); serve per lo stop del
    conto, non decide la liquidazione (margine unico, lorda 2: circa −95%). `... ore_rischio`; il minuto del prezzo mark resta da misurare.
