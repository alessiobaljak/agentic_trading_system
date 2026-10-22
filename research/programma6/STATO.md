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
| 19 | Il premio del perpetuo sullo spot (media delle 168 ore prima) fra monete: P1 da solo, P2 con il funding | `DICIANNOVESIMA.md` | `RISULTATI_DICIANNOVESIMA.md` | 2 | non valide (corretto 0,33 e 0,31 con 44 prove): P1 Sharpe 1,25, +49,6% l'anno, 6 anni su 6; correlazione con F3 0,83: lo stesso vantaggio misurato con il premio invece del funding; non migliora F3 nemmeno nelle settimane dei pari |
| 20 | La quota del volume a pronti sul totale: S1 il livello (long la più alta), S2 il cambio dei 7 giorni sui 90 (long la salita) | `VENTESIMA.md` | `RISULTATI_VENTESIMA.md` | 2 | non valide: S1 Sharpe 0,59, 3 anni su 6; S2 −0,82 (verso opposto: quando sale la quota del perpetuo la moneta continua) |
| 21 | Gli annunci di Binance (dati nuovi: titoli e ore dal sito): short il perpetuo e long il Bitcoin per 7 giorni dal giorno dopo l'etichetta di monitoraggio (E1) o la rimozione a pronti (E2) | `VENTUNESIMA.md` | `RISULTATI_VENTUNESIMA.md` | 2 a eventi | non valide: E1 −1,06% a evento, E2 −21,2%; due terzi degli eventi vinti, ma pochi esplodono (ALPACA +1796%) |
| 22 | Conferma sulle monete 101-200 dell'ipotesi «la leva che entra continua»: L1 il cambio della quota a pronti, L2 con gli acquisti a mercato | `VENTIDUESIMA.md` | `RISULTATI_VENTIDUESIMA.md` | 2 di conferma | **non confermata, verso opposto**: L1 −47,5% l'anno (Sharpe −1,07), L2 −0,91 sulle 101-200; sulle 100 L1 0,44, L2 0,63 |
| 23 | M6: il modello di M1 con la media dei ranghi di cinque semi (1-5), dati corretti | `VENTITREESIMA.md` | `RISULTATI_VENTITREESIMA.md` | 1 | non valida (corretto 0,16 con 47 prove): Sharpe 1,02, +40,0% l'anno, 5 anni su 5, discesa −47,9%; i semi da soli 1,02-1,16 sui dati corretti. Nel paper come informazione |
| 24 | F5: il segnale di F3 con la banda (entrata nel 20%, uscita sotto il 40%) | `VENTIQUATTRESIMA.md` | `RISULTATI_VENTIQUATTRESIMA.md` | 1 | **la più forte di tutto il lavoro**: Sharpe 1,93, +57,4% l'anno dal 2021, volatilità 29,7%, discesa −31%, ogni anno positivo; spese 4,9% (F3 7,7%); 25 monete per lato; contro il caso media −0,11, massimo 0,79 su 200 (`F5_caso.json`); corretto 0,81 con 48 prove. Nel paper |
| 25 | M7 (M6 con la banda) e F5 + M7 a rischio uguale | `VENTICINQUESIMA.md` | `RISULTATI_VENTICINQUESIMA.md` | 2 | non valide (corretti 0,20 e 0,65 con 50 prove): M7 Sharpe 1,25 (M6 1,08), F5 + M7 1,83, volatilità 24%, ogni anno 2022-2026 positivo. Nel paper come informazione |
| 26 | Il funding che tocca il tetto (Binance accorcia l'intervallo del funding): E3 long con funding negativo, E4 short con funding positivo, 7 giorni contro il Bitcoin | `VENTISEIESIMA.md` | `RISULTATI_VENTISEIESIMA.md` | 2 a eventi | **E4 passa l'esame scritto**: +11,67% a evento (62 eventi su 61 monete), 79% vinti, senza i 5 migliori +7,5%, ogni anno positivo, p 0,0047 (soglia 0,005 per la coppia; 0,0025 contando le 4 prove a eventi: allora no). E3 no (p 0,0166, dipende dalle code). E4 nel paper |
| 27 | Conferma di E4 su Gate.io (eventi senza un passaggio di Binance sulla stessa moneta nei 7 giorni) | `VENTISETTESIMA.md` | `RISULTATI_VENTISETTESIMA.md` | 1 di conferma | **non confermata**: come scritta −4,24% a evento su 456, p 0,67, ma 289 eventi sono cambi in blocco di Gate.io; senza quei giorni (descrittivo, dopo) 114 eventi, +6,00%, 75% vinti, p 0,096. Né conferma né smentita |
| 28 | K2 (K1 con la banda, costruzione) e F5 + M7 + K2 a rischio uguale | `VENTOTTESIMA.md` | `RISULTATI_VENTOTTESIMA.md` | 2 | non valide (corretti 0,47 e 0,76 con 52 prove): K2 Sharpe 1,72 (K1 1,25), le tre insieme 2,11 con volatilità 20,5%, ogni anno 2022-2026 positivo. Nel paper come informazione |
| 29 | M8: il modello di M7 allenato sul rendimento in più della media (tagliato all'1% e al 99%) invece del rango | `VENTINOVESIMA.md` | `RISULTATI_VENTINOVESIMA.md` | 1 | non valida (corretto 0,12 con 53 prove): Sharpe 1,21 contro 1,25 di M7; correlazione con M7 0,47 |
| 30 | N3 su Gate.io: short a 7 giorni dalla quotazione contro il Bitcoin, uscita a +30% (candele a 1 ora) o dopo 30 giorni, monete nuove non ancora perpetuo su Binance | `TRENTESIMA.md` | `RISULTATI_TRENTESIMA.md` | 1 a eventi | **VALIDA**: +7,59% a evento su 449 monete, p 0,0001, ogni anno positivo (dopo aver tolto 182 contratti che non erano monete: azioni, fondi, indici, metalli). Nel paper (su Gate e, con la stessa regola, sulle nuove di Binance) |
| 31 | M7 + M8 a rischio uguale (costruzione) | `TRENTUNESIMA.md` | `RISULTATI_TRENTUNESIMA.md` | 1 | non valida (corretto 0,20 con 54 prove): Sharpe 1,39 contro 1,25 di M7. Nel paper come informazione |
| 32 | La regola N3, identica, sul passato di Binance (monete nuove dal 2021) | `TRENTADUESIMA.md` | `RISULTATI_TRENTADUESIMA.md` | 1 a eventi | **passa l'esame**: +4,29% a evento su 613 monete, p 0,0017; riserva: l'idea dell'uscita era nata su questi dati; 2021 e 2026 leggermente negativi |
| 33 | N3 a portafoglio (5% a operazione, al massimo 20 aperte) e F5 + N3 | `TRENTATREESIMA.md` | `RISULTATI_TRENTATREESIMA.md` | 2 | non valide: N3 a portafoglio Sharpe 0,62, volatilità 33,8%, discesa −47%; F5 + N3 1,45, peggio di F5 da sola (1,93) |
| 34 | Trading con gli indicatori a 4 ore: rottura di Donchian a 20 candele, stop 2 ATR, uscita mobile 3 ATR, al massimo 7 giorni; T1 senza filtro, T2 con il filtro del funding | `TRENTAQUATTRESIMA.md` | `RISULTATI_TRENTAQUATTRESIMA.md` | 2 | non valide: T1 −0,20% a operazione (34.397), T2 +0,01% (15.406); il filtro aggiunge +0,2%, lo short va meglio del long |
| 35 | Contro gli eccessi a 4 ore: RSI sopra 70 e funding alto → short, sotto 30 e funding basso → long, stop 2 ATR, obiettivo RSI 50 | `TRENTACINQUESIMA.md` | `RISULTATI_TRENTACINQUESIMA.md` | 1 | non valida: −0,22% a operazione su 9.785, 47% vinte, metà delle uscite allo stop |
| 36 | T5: tendenza a 1 giorno (9 canali di Donchian, long e short) solo nel verso del funding | `TRENTASEIESIMA.md` | `RISULTATI_TRENTASEIESIMA.md` | 1 | non valida: Sharpe 0,40 (senza filtro 0,15), +3,7% l'anno |
| 37 | T6: T2 con l'entrata a ordine limite | `TRENTASETTESIMA.md` | `RISULTATI_TRENTASETTESIMA.md` | 1 | non valida: +0,05% a operazione (99% eseguite); long −0,28%, short +0,36% |
| 38 | T7: solo short delle rotture verso il basso con il funding alto, conferma sulle 101-200 | `TRENTOTTESIMA.md` | `RISULTATI_TRENTOTTESIMA.md` | 1 di conferma | non confermata: +0,14% a operazione, p 0,40, 2026 −1,1% |
| 39 | T8: tendenza del giorno (media 50 giorni) e ritracciamento a 4 ore (RSI 35/65) con il funding | `TRENTANOVESIMA.md` | `RISULTATI_TRENTANOVESIMA.md` | 1 | non valida: +0,15% a operazione, p 0,32; long −0,46%, short +0,53% |
| 40 | Coppie di monete che si allontanano (z del rapporto a 1 giorno, entrata a 2, uscita a 0,5) | `QUARANTESIMA.md` | `RISULTATI_QUARANTESIMA.md` | 1 | non valida: +0,58% a operazione, p 0,21; 2021 +3,9%, 2025 −1,1%; portafoglio Sharpe 0,34 |
| 41 | U1: short dopo l'arrivo su Upbit delle monete che hanno già il perpetuo | `QUARANTUNESIMA.md` | `RISULTATI_QUARANTUNESIMA.md` | 1 a eventi + 1 | non valida: +2,96% a evento, p 0,070; 2025 +0,1% su 43 |
| 42 | F6: F5 con l'esposizione secondo l'agitazione (Moreira e Muir) | `QUARANTADUESIMA.md` | `RISULTATI_QUARANTADUESIMA.md` | 1 | non valida: Sharpe 1,71 contro 1,93 di F5 |
| 43 | Q1 long 5 minuti dopo la quotazione a pronti, Q2 short 5 minuti dopo monitoraggio o rimozione, per 24 ore | `QUARANTATREESIMA.md` | `RISULTATI_QUARANTATREESIMA.md` | 2 a eventi + 2 | non valide: Q1 +0,03% (p 0,51), Q2 +3,08% (p 0,024) |
| 44 | S1: long il Bitcoin se l'offerta delle stablecoin è cresciuta nella settimana prima | `QUARANTAQUATTRESIMA.md` | `RISULTATI_QUARANTAQUATTRESIMA.md` | 1 | non valida: Sharpe 0,66 (Bitcoin tenuto 0,38), intervallo non sopra zero |
| 45 | Indicatori per il momento d'entrata: I1 F5 con la tendenza d'accordo, I2 N3 sulla prima rottura verso il basso | `QUARANTACINQUESIMA.md` | `RISULTATI_QUARANTACINQUESIMA.md` | 1 + 1 a eventi + 1 | non valide: I1 Sharpe 1,02 (F5 1,93); I2 +3,79% a operazione, p 0,0064, portafoglio 0,88 |
| 46 | Le 17 strategie già pronte di TradingView, valori di serie, a 4 ore e a 1 giorno | `QUARANTASEIESIMA.md` | `RISULTATI_QUARANTASEIESIMA.md` | 34 | nessuna valida: la migliore Supertrend a 1 giorno, Sharpe 0,36 (il Bitcoin tenuto 0,38) |
| 47 | La paura nelle opzioni (DVOL di Deribit): O1 Bitcoin, O2 Ether | `QUARANTASETTESIMA.md` | `RISULTATI_QUARANTASETTESIMA.md` | 2 | non valide: O1 0,29 (Bitcoin tenuto 0,37), O2 0,36 (Ether tenuto 0,15) |
| 48 | R1, il regista: ogni mese solo le strategie con il mese prima positivo | `QUARANTOTTESIMA.md` | `RISULTATI_QUARANTOTTESIMA.md` | 1 | non valida: Sharpe 1,52 contro 1,93 sempre accese |
| 49 | X1 momento delle 3 settimane, X2 dimensione (piccole contro grandi), con la banda | `QUARANTANOVESIMA.md` | `RISULTATI_QUARANTANOVESIMA.md` | 2 | non valide: X1 0,05, X2 0,47 (solo il 2021) |
| 50 | F5 sulle monete 101-150 (conferma) | `CINQUANTESIMA.md` | `RISULTATI_CINQUANTESIMA.md` | conferma | non confermata: Sharpe 0,30; funding +27,7%, spese 15,1% |

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
   poco su F3 e K1 (Sharpe 1,296 → 1,295 e 1,269 → 1,262) ma **molto su M1: 1,35 → 0,79** con solo 41 settimane-moneta
   tolte dall'universo su 29.180: il modello ad alberi è fragile (piccoli cambi nei dati, grandi cambi nel risultato).
   Da qui in avanti i dati sono corretti; quanto M1 cambia con il seme è in `semi_M1.json`.
15. **Il vantaggio del funding non dipende da come lo si misura** (prova 19): con il premio del perpetuo sullo spot, che
   non ha il blocco a 0,01%, lo stesso portafoglio fa Sharpe 1,25 e guadagna in tutti e 6 gli anni; correlazione 0,83 con F3.
   È una conferma che il vantaggio è il prezzo pagato da chi sta long con la leva, non un dettaglio del calcolo del funding;
   non è una strategia in più.
16. **La leva che entra in una moneta continua per una settimana: visto tre volte, in tre dati diversi** (prove 9, 11,
   20): gli acquisti a mercato, la crescita dell'interesse aperto e la quota del perpetuo che sale (contro il volume a
   pronti) vanno tutti nel verso della moneta, al contrario delle regole scritte. Visto dopo il calcolo ogni volta, quindi
   non è una prova; K1 (nel paper) usa le prime due. Il funding alto invece va contro (F3): chi entra con la leva spinge il
   prezzo, chi paga troppo per restarci perde.
   **Provata sulle monete 101-200 (prova 22): non vale, anzi si rovescia** (−47,5% l'anno): sulle monete più piccole la
   leva che entra annuncia la discesa (gonfia e sgonfia). Un andamento visto tre volte sulle stesse monete non è una legge.
17. **Andare short sulle monete piccole senza protezione perde, sempre per lo stesso motivo** (prove 18 e 21): monete
   nuove, monete sotto etichetta, monete che stanno per essere tolte dal listino scendono quasi sempre (due terzi delle volte),
   ma poche esplodono verso l'alto (COAI +2627%, ALPACA +1796%, DEGO +295% in una settimana) e si mangiano tutto. Un'idea
   short sulle piccole va provata solo con un'uscita di protezione e con le candele a 1 ora.
18. **M1 dipende dal seme** (`semi_M1.json`): stesso modello, stessi dati, sei semi: Sharpe 1,35 (il seme della prova),
   0,79, 0,93, 1,12, 1,00, 1,43; media 1,10. Il numero della prova stava sopra la media: il valore atteso è circa 1,1 sui
   dati di prima, e con i dati corretti il seme della prova fa 0,79. Sui dati corretti i semi 1-5 fanno 1,02-1,16 e la loro media (M6) 1,02:
   il valore onesto della famiglia del modello ad alberi è circa 1, non 1,35.
19. **Il segnale del funding vale di più se si cambia meno** (prova 24): con la banda (si entra nel 20%, si esce sotto il
   40%) le posizioni restano finché il funding è ancora alto o basso: giro da 2,12 a 1,35 a settimana, spese dal 7,7% al
   4,9% l'anno, più monete per lato (25 invece di 20), volatilità dal 40% al 30%, e il prezzo rende di più (+37,6% invece
   di circa +27%). Sharpe da 1,28 a 1,93. Il segnale era buono; lo si eseguiva male. La banda aiuta anche il modello (prova 25: da
   1,08 a 1,25) e insieme le due fanno 1,83 con volatilità del 24%. Anche K1 (prova 28: da 1,25 a 1,72); le tre insieme fanno
   2,11 con volatilità del 20,5%.
   Controlli su F5 (`robustezza_F2.md`, ultima sezione): costi tripli 1,60, prime 50 monete 1,28, dalla 51ª alla 100ª
   0,99, senza le cinque monete più pesanti 1,64, cambio il giovedì 1,71; i due lati da soli 0,54 e 0,19.
20. **Quando i long sono così affollati che il funding tocca il tetto, la moneta scende** (prova 26, E4): dopo il
   passaggio a un intervallo più corto con funding positivo, in 7 giorni la moneta fa in mediana −15% rispetto al Bitcoin, in
   79 casi su 100, e scende ancora fino a 28 giorni; vale per le monete appena quotate (35 eventi) e per quelle con più di 60
   giorni (23). Dal lato opposto (short affollati) la moneta sale in media ma per poche esplosioni. È lo stesso vantaggio di
   F3 all'estremo, come evento. 62 eventi sono pochi: lo dirà il paper. Su Gate.io (prova 27) non si conferma: lì molti cambi
   d'intervallo sono decisioni in blocco dell'exchange; senza quelli, stesso verso (+6% a evento, 75% vinti) ma non
   abbastanza (p 0,096).
21. **Le monete appena quotate scendono, e con l'uscita di protezione lo short regge** (prova 30, su Gate.io, su monete mai
   guardate): short a 7 giorni dalla quotazione, uscita a +30%, fa +7,6% a evento su 449 monete (p 0,0001), ogni anno dal
   2023. Senza l'uscita la media è più alta (+11,2%) ma poche esplosioni rendono il rischio inaccettabile: l'uscita
   costa 3-4 punti di media e toglie le code. Attenzione: su Gate.io metà dei contratti nuovi non sono monete (azioni,
   fondi, indici); vanno tolti con il tipo del contratto. Sul passato di Binance la stessa regola, senza toccarla (prova 32),
   fa +4,3% a evento su 613 monete (p 0,0017), più debole nel 2026 (−0,6%). È la lezione della prova 18 messa alla prova sui dati di un altro exchange.
22. **Una regola valida per operazione può essere cattiva da tenere** (prova 33): N3 su Binance fa +4,3% a operazione
   (p 0,0017), ma come portafoglio (5% a operazione) fa Sharpe 0,62 con volatilità del 34% e discesa del 47%: le monete nuove
   arrivano a ondate nei periodi di euforia e le perdite si sommano. Si giudica sempre anche il portafoglio, giorno per giorno.
23. **Gli indicatori tecnici a 4 ore non hanno vantaggio dopo i costi, nemmeno con il funding** (prove 34 e 35): la
   rottura del prezzo fa +0,01% a operazione con il filtro del funding (−0,20% senza), il ritorno dagli eccessi −0,22%.
   Il funding funziona sulle settimane e fra monete, non come segnale d'entrata a ore: chi paga troppo perde nel tempo, ma
   l'ora giusta per entrare non la dice né lui né l'indicatore. A 1 giorno (prova 36) la tendenza nel verso del funding fa 0,40 (senza
   filtro 0,15): il funding migliora sempre l'indicatore, ma l'indicatore porta poco.
24. **In tutte le prove a 4 ore lo short guadagna e il long perde, qualunque sia l'indicatore** (prove 34, 37, 39:
   short +0,19%, +0,36%, +0,53% a operazione; long −0,57%, −0,28%, −0,46%). Non è il segnale: dal 2021 la maggior parte delle
   altcoin è scesa, e chi le vendeva guadagnava comunque (in più incassa il funding). È l'andamento del mercato di questi anni,
   non un vantaggio su cui contare; sulle monete 101-200 (prova 38) non si conferma.
25. **Le coppie di monete che si allontanano e poi si riavvicinano funzionavano nel 2021 e non più** (prova 40): +3,9% a
   operazione per le entrate del 2021, +1,0% nel 2022, +0,2% nel 2023, poi zero o sotto (2025 −1,1%); sull'intero periodo
   +0,58% con p 0,21. Quando la distanza torna (un'operazione su tre) si guadagna il 10%, ma in un caso su quattro la coppia
   si rompe (−6,4%) e in uno su tre il tempo scade in perdita (−4,8%). Le monete simili oggi si separano più spesso di quanto
   si riavvicinino: il mercato delle altcoin si è diviso in storie diverse.
26. **L'arrivo su Upbit fa salire la moneta prima che si possa vendere, e dopo scende poco e sempre meno** (prova 41): dalle
   24 ore prima dell'arrivo all'entrata (2 ore dopo) la moneta sale in media del 26,6% più del Bitcoin (mediana 18,9%); nei
   7 giorni dopo lo short fa +2,96% a evento (p 0,07), ma nel 2025, l'anno con più eventi (43), +0,1%. Come per gli annunci
   di Binance (prova 21), il grosso del movimento è nella prima reazione, che non si prende.
27. **Per F5 le settimane agitate sono le migliori** (prova 42): tenere meno quando il mercato oscilla (il metodo di
   Moreira e Muir, che funziona sui fattori di borsa) porta lo Sharpe da 1,93 a 1,71; nel 2021, l'anno più agitato, F5 fa
   +122,6% e la versione prudente +65,9%. Il funding fra monete guadagna di più quando le monete sono più diverse fra loro,
   cioè proprio nei periodi agitati: ridurre lì vuol dire tagliare il guadagno, non il rischio.
28. **Le notizie di Binance si prezzano in pochi minuti** (prova 43, candele a 1 minuto): dopo l'annuncio di una quotazione
   a pronti la moneta sale del 13,1% nei primi 5 minuti (mediana 7,3%), poi nelle 24 ore dopo non guadagna niente (mediana
   −5%: torna un po' indietro); dopo un annuncio cattivo scende dell'8,75% nei primi 5 minuti e poi ancora del 3% circa, non
   abbastanza per passare l'esame. Nell'ora prima dell'annuncio quasi niente (+1,0% e +0,2%): l'ora di pubblicazione è
   giusta. Per prendere il movimento bisogna essere più veloci di 1 minuto, contro programmi professionali che leggono gli
   annunci in millisecondi: non è un vantaggio che possiamo avere.
29. **Ogni prova in più allontana F5 dalla soglia** (calcolo del 21 ottobre, stesso metodo di sempre, `terza.sharpe_corretto`):
   lo Sharpe di F5 resta 1,93 su 302 settimane, ma il suo Sharpe corretto scende da **0,815** con le 48 prove della ventiquattresima
   a **0,517** con le 67 di oggi, perché il conto è più lungo e gli Sharpe delle prove sono più sparsi (deviazione da 0,69 a
   0,80: le prove a indicatori e a eventi negative allargano la forbice). Conseguenza: cercare ancora sugli stessi anni rende
   più difficile dimostrare F5 con il passato; la prova pulita di F5 sono i dati nuovi (il paper, dal 26 ottobre le
   settimane) o dati indipendenti. Non si cambia il metodo per far passare F5: sarebbe l'errore del primo gate.
30. **Il denaro che entra in stablecoin aiuta a tenere il Bitcoin, ma poco** (prova 44): stare long solo nelle settimane dopo
   una crescita dell'offerta porta lo Sharpe da 0,38 (Bitcoin tenuto sempre) a 0,66 e la discesa da −77% a −58%, soprattutto
   perché nel 2022 l'offerta calava; ma il Bitcoin resta il Bitcoin (volatilità 45%) e il guadagno in più non è distinguibile
   dal caso.
31. **Gli indicatori per scegliere il momento d'entrata non migliorano le strategie che funzionano** (prova 45). In F5 il
   filtro della tendenza toglie proprio il guadagno: F5 compra le monete che nessuno vuole e vende quelle affollate, cioè va
   contro la tendenza; chiedere che la tendenza sia d'accordo lascia meno monete (18 per lato invece di 25), a volte una sola,
   e lo Sharpe scende da 1,93 a 1,02. In N3 aspettare la prima rottura verso il basso lascia il guadagno per operazione quasi
   uguale (+3,8% invece di +4,3%) e il portafoglio un po' meglio (Sharpe 0,88 invece di 0,62, discesa −43% invece di −47%),
   ma non abbastanza, e il 2026 resta negativo.
32. **Le strategie già pronte di TradingView: senza costi sembrano buone, con i costi no** (prova 46, 17 strategie × 2
   candele). Lo Strategy Tester di serie non conta commissioni e scarto: Momentum a 4 ore fa +24,6% l'anno senza costi e −3,0% con
   i costi veri (spese 23,1% l'anno), MACD a 4 ore +23,6% → +0,9%, Pivot Extension a 4 ore +26,5% → −11,2% (spese 38,1%). Le
   migliori con i costi seguono la tendenza a 1 giorno (Supertrend 0,36, Price Channel 0,34): quanto tenere il Bitcoin (0,38),
   con discese oltre il 50%. Quelle contro gli eccessi (RSI, Stocastico, Bollinger) perdono anche senza costi: dal 2021 nel
   crypto andare contro i movimenti forti è costato caro.
33. **Il premio delle opzioni non dice quando tenere Bitcoin o Ether** (prova 47): stare dentro solo nelle settimane con il
   premio sopra la sua mediana dimezza la discesa peggiore (Bitcoin −37% invece di −66%), ma guadagna meno (Sharpe 0,29 contro
   0,37 del Bitcoin tenuto); per l'Ether va meglio dell'Ether tenuto (0,36 contro 0,15), ma non abbastanza da distinguersi dal caso.
   Come per le stablecoin (prova 44): i segnali sul mercato intero riducono le perdite, non danno un vantaggio dimostrabile.
34. **Le strategie buone si tengono accese** (prova 48): il regista che spegne per un mese le strategie con il mese prima
   negativo porta F5 + M7 + K2 da Sharpe 1,93 a 1,52; i mesi negativi di queste strategie non annunciano altri mesi negativi
   (2023: −8,7% con il regista). Come per F5 nelle settimane agitate (lezione 27): togliere esposizione dopo una perdita taglia il
   recupero, non il rischio.
35. **L'asticella si usava in modo troppo severo, e ora si usa come prescrivono gli autori** (`ASTICELLA.md`,
   `RISULTATI_ASTICELLA.md`): contando le prove una per una (107), varianti quasi uguali pesavano come idee diverse e le regole
   che perdono per costruzione allargavano la forbice. Contando i gruppi di prove simili (56) F5 sale da 0,46 a **0,87** e
   F5 + M7 + K2 a **0,90**: molto probabilmente non sono fortuna, ma non al 95%. Con il t dello Sharpe contro 3,0 (l'altra
   asticella pubblicata) passano. Il verdetto finale resta del paper, che è acceso nel bot.
36. **I fattori pubblicati per le cripto non reggono fra le 100 monete dei perpetui dal 2021** (prova 49): il momento delle
   3 settimane (Liu, Tsyvinski e Wu 2022, dati fino al 2020) perde tre anni e guadagna tre (Sharpe 0,05): dipende dalla fase
   del mercato; le piccole battono le grandi solo nel 2021, l'anno dell'euforia delle altcoin (+134,8%), poi perdono ogni anno.
   Il funding fra monete (F5) resta l'unica cosa che guadagna in tutti gli anni.
37. **Oltre le 100 il funding fra monete c'è ancora, ma i costi lo mangiano** (prova 50): sulle monete 101-150 F5 incassa il
   27,7% l'anno dal funding e il prezzo non lo toglie (+1,2%), ma con lo scarto dello 0,10% e il giro più alto (1,94 contro
   1,35 fra le 100: la lista cambia di più) le spese sono il 15,1% l'anno e l'ultimo anno è negativo. Per usarlo su più monete
   serve un'esecuzione più economica, non un segnale diverso.

## Dati (fuori da git, con le impronte nel repository)

* `research/data/p6/`: candele a 15 minuti, 1 ora e 4 ore delle 100 monete, fatte dai minuti verificati del programma 5.
* `research/data/p6g/`: candele giornaliere e funding di tutti i 892 perpetui USDT-M dell'archivio
  (`scarico_giorni.json`); controllo contro le ore verificate: 125.808 giorni, chiusure oltre lo 0,1% in 2 giorni
  (`risultati_seconda/controllo_dati.json`).
* `research/data/p6h/`: candele a 1 ora delle 537 monete mai usate (`scarico_ore.json`).
