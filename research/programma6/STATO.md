# Programma 6 — stato e registro delle prove

Aggiornato il 19 ottobre 2026. Il metodo è in `METODO.md`; ogni prova ha le sue regole scritte e committate **prima**
del calcolo, e i suoi risultati in un file a parte. `DRY_RUN` resta vero: niente soldi veri.

## Le prove

| N. | Cosa | Regole | Risultati | Prove nel conto | Esito |
|---|---|---|---|---|---|
| 1 | 9 famiglie di indicatori (rotture, medie, Supertrend, RSI, Bollinger, compressione, MACD+ADX, Keltner, spinta RSI) a 15 minuti, 1 ora, 4 ore; 100 monete di settembre 2026; finestre di 12 + 3 mesi dal 2021 | `METODO.md` | `RISULTATI.md` | 9 | nessuna valida; migliori compressione (+0,093 R a trade) e Supertrend (+0,056) |
| 2A | La regola pubblicata di Zarattini, Pagani e Barbon (2025): 9 canali di Donchian, volatilità al 25%, 20 monete più liquide; universo mese per mese fra tutti i 892 perpetui | `SECONDA.md` | `RISULTATI_SECONDA.md` | 3 | nessuna valida; A1 Sharpe 0,53 dal 2021, 0,25 dopo l'articolo |
| 2B | Le 9 famiglie della prova 1 a 1 giorno, prime 50 monete mese per mese | `SECONDA.md` | `RISULTATI_SECONDA.md` | 9 | nessuna valida; migliore l'incrocio delle medie (+0,097 R, 5 anni su 5) |
| 3 | CTREND di Fieberg e altri (JFQA 2025): 28 indicatori, regressioni sulle 52 settimane prima, long-short fra le 100 monete più scambiate; dal giugno 2022 | `TERZA.md` | `RISULTATI_TERZA.md` | 3 | nessuna valida; C1 Sharpe 0,39 (−79% nel 2024, +69% nel 2025, +103% nel 2026) |
| 4 | Conferma della regola congelata I-017c4 del programma 5 (long dopo un crollo di 4 ore) sulle 537 monete mai usate, a 1 ora | `QUARTA.md` | `RISULTATI_QUARTA.md` | conferma di una regola sola | non confermata: +1,77% a trade (p 0,007) ma −0,35% nell'ultimo anno e −2,0% sui crolli della sola moneta |
| 5 | Short dopo il crollo della sola moneta (z4 ≤ −5 con il Bitcoin sopra −3), 12 ore, sulle 100 monete del programma 5 | `QUINTA.md` | `RISULTATI_QUINTA.md` | conferma di una regola sola | non confermata: −0,27% a trade (553 trade, p 0,66); il ribasso che continua vale +0,18% lordo, meno dei costi |
| 6 | Il funding fra monete: long il quinto col funding dei 7 giorni più basso, short il più alto, fra le 100 più scambiate, ogni settimana dal 2021 | `SESTA.md` | `RISULTATI_SESTA.md` | 2 | **F2 (pesi uguali) la migliore di tutto il lavoro**: +47,5% l'anno, Sharpe 1,03, intervallo sopra zero, 6 anni su 6, a costi doppi, beta col Bitcoin −0,03; non passa solo lo Sharpe corretto (0,66 con 26 prove). F1 (pesi per volume) Sharpe 0,36 |
| 7 | Conferma di F2, identica, sulle monete dalla 101ª alla 200ª per volume, scarto 0,10% | `SETTIMA.md` | `RISULTATI_SETTIMA.md` | conferma di una regola sola | non confermata: +8,3% l'anno, Sharpe 0,18, p 0,37; le spese (18,8% l'anno) si mangiano quasi tutto; −52,5% nell'ultimo anno |
| 8 | F3: il funding fra monete con i pesi inversamente proporzionali alla volatilità dei 30 giorni prima; esame sulle 100 più scambiate e conferma sulle 101-200 | `OTTAVA.md` | `RISULTATI_OTTAVA.md` | 1 | **la più forte di tutto il lavoro sulle 100 monete**: +50,6% l'anno, Sharpe 1,28, positiva in tutti gli anni 2021-2026 e nelle 18 settimane del 2020, funding +31,6% e prezzo +26,7%; non valida: Sharpe corretto 0,76 (27 prove) e sulle 101-200 Sharpe 0,13 (spese 19% l'anno) |
| 9 | G1 (quota di acquisti a mercato dei 7 giorni) e G2 (salto giornaliero più alto dei 30 giorni) fra monete, long il meno affollato | `NONA.md` | `RISULTATI_NONA.md` | 2 | non valide: G1 −47,8% l'anno (Sharpe −1,17, 0 anni su 6: il verso è il contrario, chi ha molti acquisti aggressivi continua a salire); G2 Sharpe 0,18. Il rovescio di G1, solo descrittivo: +30,3% sulle 100 grandi, −15,9% sulle 101-200 |
| 10 | C4: CTREND con 30 indicatori (i 28 più il funding e gli acquisti a mercato dei 7 giorni), verso e peso stimati dalla regressione | `DECIMA.md` | `RISULTATI_DECIMA.md` | 1 | non valida: Sharpe 0,43 (C1 0,39), −68% nel 2024; la rete elastica tiene funding e acquisti in 119 e 183 settimane su 216 ma i 28 indicatori di tendenza dominano |
| 11 | Le posizioni (dati metrics, dal 2022): P1 grandi contro piccoli (si seguono i conti grandi), P2 crescita dell'interesse aperto in 7 giorni (si va contro) | `UNDICESIMA.md` | `RISULTATI_UNDICESIMA.md` | 2 | non valide: P1 +1,5% l'anno, Sharpe 0,06; P2 −30,7% l'anno, Sharpe −0,94: la leva che entra **continua** (verso opposto a quello scritto) |
| 12 | K1: denaro che entra e leva che costa poco (media dei ranghi di −funding, +acquisti a mercato, +crescita dell'interesse aperto) | `DODICESIMA.md` | `RISULTATI_DODICESIMA.md` | 1 | **costruzione, non prova** (due versi visti prima): dal 2022 +37,6% l'anno, Sharpe 1,27, discesa massima −31%, 2023 −0,3%; correlazione con F3 0,39. La prova è il paper |
| 13 | Il funding medio del mercato (terzo più basso delle 52 settimane: long Bitcoin; più alto: short) | `TREDICESIMA.md` | `RISULTATI_TREDICESIMA.md` | 1 | non valida: Sharpe 0,47 contro 0,56 del Bitcoin sempre comprato; il funding conta fra le monete, non per il mercato intero |
| 14 | Un modello che impara ogni 4 settimane, solo dal passato, come unire ~70 ingredienti (28 indicatori, rendimenti, volatilità, funding, acquisti a mercato, volume, legame col Bitcoin, posizioni, stato del mercato): M1 alberi, M2 lineare | `QUATTORDICESIMA.md` | `RISULTATI_QUATTORDICESIMA.md` | 2 | **M1: +50,9% l'anno dal 2022, Sharpe 1,35**, intervallo sopra zero, 4 anni su 5 (2024 −5%), sopra il caso (`caso_M1.json`), quasi indipendente da F3 (0,17) e K1 (0,03); non passa lo Sharpe corretto (0,59 con 36 prove). M2 Sharpe 0,62. Sulle 101-200 una fuga di informazione dai dati sulle posizioni (trovata e corretta: senza, Sharpe circa 0). M1 nel paper |
| 15 | F3 e M1 insieme, il capitale diviso a rischio uguale (volatilità delle 26 settimane prima) | `QUINDICESIMA.md` | `RISULTATI_QUINDICESIMA.md` | 1 | **la più forte di tutto il lavoro**: dal 2022 +44,8% l'anno, volatilità 26,6%, Sharpe 1,69, discesa massima −33%, positiva in ogni anno 2022-2026 e in 13 trimestri su 16, a costi doppi; non passa lo Sharpe corretto (0,76 con 37 prove). Con K1 (solo informazione) Sharpe 1,87. Nel paper |
| 16 | M3: il modello di M1 ogni giorno (entrata al 20%, uscita al 40%) | `SEDICESIMA.md` | `RISULTATI_SEDICESIMA.md` | 1 | non valida: Sharpe 0,95, +31,2% l'anno, ma spese 23,8% e funding 13,7% l'anno, 2026 −29%, ultimo anno −4,6%; correlazione con M1 0,64 |
| 17 | Sei modelli in gara (alberi, alberi bassi, foresta, alberi casuali, lineare, rete neurale), scelti ogni 4 settimane sulle 12 settimane tenute da parte (M4) o mediati (M5) | `DICIASSETTESIMA.md` | `RISULTATI_DICIASSETTESIMA.md` | 2 | non valide: M4 Sharpe 0,71 (+30,1% l'anno, 2024 −14,5%), M5 0,95 (+37,7%); scelti foresta 23 volte, alberi casuali 17, lineare 9, alberi bassi 8, gli alberi di M1 4, la rete 2 |
| 18 | Le monete appena quotate: short quelle di 7-60 giorni (N1) o 7-180 (N2), long le 100 grandi | `DICIOTTESIMA.md` | `RISULTATI_DICIOTTESIMA.md` | 2 | non valide: N1 −18,5% l'anno, N2 −22,3%; la tipica scende (mediana −3,6% a settimana) ma poche esplodono (COAI +2627% in una settimana) |

## Il paper (dal 20 ottobre 2026)

`paper/REGOLE.md`, aggiornato ogni mattina da `paper/aggiorna.sh` (routine «Programmi 5 e 6»): **F3**, **K1** e **M1** sono le
candidate principali, con F2, C1 e A1; verdetto a 52 e 104 settimane. Le posizioni della settimana in corso sono in
`paper/PAPER.md`.

**Esecuzione** (`ESECUZIONE.md`, descrittivo): il cambio del lunedì di F3 con un ordine limite al prezzo d'apertura (poi a
mercato dopo un'ora) è eseguito nel 98% dei casi e porta i costi dal 7,7% al 5,3% l'anno.

## Cosa abbiamo imparato (con la fonte)

1. **Le 100 monete di oggi sono le sopravvissute**: scegliere l'universo con il volume di settembre 2026 regala un
   vantaggio che chi operava allora non aveva. Dalla prova 2 l'universo si sceglie con i soli dati di allora, fra tutte
   le monete dell'archivio, anche quelle tolte dal listino (`SECONDA.md`, sezione 1).
2. **Seguire il prezzo di una moneta da sola** dà al massimo uno Sharpe intorno a 0,5 nel 2021-2026 (prove 1 e 2).
3. **La tendenza fra monete** va e viene: Sharpe 1,5-2,0 dopo l'aprile 2025 in tutte e tre le varianti della prova 3,
   ma −79% nel 2024, quando il lato short (le monete più deboli) è salito di più nel rialzo di fine anno
   (`risultati_terza/settimane_C1.csv.gz`: lato short −219% annualizzato nel secondo semestre 2024).
4. **La soglia dopo 24 prove**: con la dispersione degli Sharpe delle prove (circa 0,4) lo Sharpe atteso per caso del
   migliore di 24 è circa 0,76; per lo Sharpe corretto al 95% con 4-6 anni serve circa **1,5**. Una strategia a indicatori
   da Sharpe 0,5-0,7 non lo raggiunge, e ogni prova in più sugli stessi anni alza la soglia. Per questo la prova 4 è una
   **conferma su monete mai usate**, non una ricerca nuova.
5. **Il rimbalzo dopo i crolli è del mercato, non della moneta** (prova 4): sulle monete mai usate i crolli della sola
   moneta continuano a scendere (−2,0% a trade), quelli di tutto il mercato rimbalzano (+3,8%) ma in 84 giorni soltanto,
   con il 56% del guadagno in 5 giorni e il crollo più grande (10 ottobre 2025) al contrario.
6. **Il crollo della sola moneta non è un segnale nemmeno al contrario** (prova 5): sulle 100 monete grandi lo short
   dopo il crollo fa +0,18% lordo e −0,27% netto; il −2,0% del long sulle monete piccole veniva dai costi e dalle monete
   che crollano e spariscono.
7. **Il funding fra monete è la cosa più forte trovata** (prove 6 e 7): sulle 100 monete più scambiate, comprare quelle
   col funding più basso e vendere quelle col più alto rende sia per il funding incassato (+40% l'anno) sia per il prezzo
   (+15%), in ogni anno dal 2021; ma sulle monete più piccole non si ripete (costi più alti, prezzo contro). È la candidata
   principale da misurare in paper. Sulle 18 settimane del 2020 mai guardate (4-5 monete per lato) va al contrario: −0,375% a
   settimana, funding +0,60%, prezzo −0,81% (`F2_2020.md`).
   F3 contro il caso (`F3_caso.md`): con il segnale mescolato fra le monete lo stesso portafoglio fa Sharpe −0,37 in
   media e al massimo 0,64 su 200 ripetizioni; F3 fa 1,30.
8. **Gli acquisti aggressivi fra monete dicono il contrario del funding** (prova 9): le monete con molti acquisti a mercato
   continuano a salire rispetto alle altre (il rovescio della regola scritta fa +30,3% l'anno sulle 100 grandi, descrittivo);
   il funding alto invece rientra. Anche qui solo fra le monete liquide.
9. **Il denaro che entra anticipa, la leva cara rientra** (prove 9 e 11): gli acquisti a mercato e la crescita
   dell'interesse aperto fra monete vanno nel verso della moneta (chi ne ha di più sale di più), il funding alto va contro.
   I due versi «di continuazione» li ho visti dopo il calcolo: valgono solo come ipotesi da provare sui dati nuovi.
10. **Un modello che impara da solo come unire gli indicatori trova un vantaggio diverso dal funding** (prova 14): M1 ha
   legame 0,17 con F3 e 0,03 con K1; gli ingredienti che pesano di più nell'ultimo modello sono l'età della moneta, la
   volatilità di 30 giorni, il rendimento giornaliero peggiore del mese, la crescita dell'interesse aperto in un giorno, il
   rendimento del Bitcoin di 30 giorni. **Attenzione ai dati che esistono solo per alcune monete**: la loro presenza può
   raccontare il futuro (la fuga trovata sulle monete 101-200).
11. **Il carry** (comprato a pronti, venduto il perpetuo) dal 2025 non rende (Borri, Liu, Tsyvinski e Wu 2025, sezione
   3.6: Sharpe 6,45 dal 2020, 4,06 dal 2024, negativo nel 2025), e il proprietario non lo vuole: non si prova.
12. **Scegliere il modello in base a come è andato di recente non aiuta** (prova 17): la gara fra sei modelli fa peggio
   di M1 da solo (0,71 contro 1,35), e la media dei sei fa 0,95. Il 1,35 di M1 dipende anche dalla scelta del modello: è un
   motivo in più per non fidarsi del numero prima del paper.
13. **Le monete nuove: la tipica scende, ma la media sale** (prova 18): mediana −3,6% a settimana, ma il 3,25% delle
   settimane-moneta fa più del +50% e lo 0,95% più del +100%. Andare short senza protezione perde (−18,5% l'anno); la coda
   verso l'alto è il rischio, non il caso raro.
14. **Le monete tolte dal listino restano nei file dell'archivio con il prezzo fermo e il volume zero** (controllo del 20
   ottobre, `controllo_zombi.json`): 58.403 giorni-moneta, il funding riempito con la media di prima. Sulle candidate pesa
   poco (F3 Sharpe 1,296 → 1,295, K1 1,269 → 1,262); da qui in avanti è corretto.

## Dati (fuori da git, con le impronte nel repository)

* `research/data/p6/`: candele a 15 minuti, 1 ora e 4 ore delle 100 monete, fatte dai minuti verificati del programma 5.
* `research/data/p6g/`: candele giornaliere e funding di tutti i 892 perpetui USDT-M dell'archivio
  (`scarico_giorni.json`); controllo contro le ore verificate: 125.808 giorni, chiusure oltre lo 0,1% in 2 giorni
  (`risultati_seconda/controllo_dati.json`).
* `research/data/p6h/`: candele a 1 ora delle 537 monete mai usate (`scarico_ore.json`).
