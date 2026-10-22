# Il registro di tutto quello che si è provato (e com'è andato)

Chiesto dal proprietario il 20 ottobre 2026: «traccia tutto quello che stai facendo e provando in un log o diario così da
non ripetere le stesse cose ma soprattutto traccia anche i vari risultati … l'unico motivo per cui ti puoi fermare è se
abbiamo strategie per tutte le crypto e nel momento in cui queste hanno lo stesso riscontro nel paper».

**Le regole del registro**

1. **Prima di ogni idea nuova** si guarda qui: se c'è già (anche con un altro nome), non si rifà; se si rifà diversa, si
   scrive che cosa cambia e perché.
2. **Ogni prova nuova** ha la sua riga **prima** del calcolo (con il file delle regole) e il risultato **dopo**, con i
   numeri e il file da cui vengono. Anche le prove che vanno male: sono quelle che evitano di ripetere.
3. Il **conto delle prove** del programma 6 (quante varianti si sono provate sugli stessi anni) serve allo Sharpe corretto:
   più prove, più alta la soglia, perché fra tante prove qualcuna sembra buona per caso. Si aggiorna qui.
4. Quando si ferma: solo con strategie per tutte le crypto che hanno lo stesso riscontro nel paper (frase del
   proprietario qui sopra). Fino ad allora si continua.

Dettagli di ogni prova nei file indicati; il diario giorno per giorno è `docs/andremo_live.md`.

## 1. Programma 6 (dal 19 ottobre 2026): strategie su indicatori e dati di mercato, 110 prove nel conto

Sharpe = rendimento diviso per quanto oscilla, all'anno. «Corretto» = lo Sharpe corretto per il numero di prove (serve
almeno 0,95). Le regole di ogni prova sono state scritte prima del calcolo.

| N. | Prova (file delle regole) | Varianti nel conto | Risultato principale | Esito |
|---|---|---|---|---|
| 1 | 9 famiglie di indicatori a 15 min, 1 ora, 4 ore, 100 monete di oggi (`programma6/METODO.md`) | 9 | Sharpe da −0,37 a 0,69 (compressione 0,69, Supertrend 0,53) | no |
| 2A | Tendenza pubblicata (Zarattini e altri 2025), 9 canali di Donchian (`SECONDA.md`) | 3 | A1 0,53; A2 0,25; A3 (solo BTC) 0,48 | no |
| 2B | Le 9 famiglie a 1 giorno, universo al tempo giusto (`SECONDA.md`) | 9 | da −0,80 a 0,47 (incrocio delle medie 0,47) | no |
| 3 | CTREND, 28 indicatori combinati, long-short fra monete (`TERZA.md`) | 3 | C1 0,39; C2 0,28; C3 0,03 (−79% nel 2024) | no |
| 4 | Rimbalzo dopo i crolli su 440 monete mai usate (`QUARTA.md`) | conferma | +1,77% a trade ma −0,35% nell'ultimo anno; solo crolli di mercato | no |
| 5 | Short dopo il crollo della sola moneta (`QUINTA.md`) | conferma | −0,27% a trade | no |
| 6 | **Funding fra monete** (`SESTA.md`) | 2 | F1 (pesi volume) 0,36; **F2 (pesi uguali) 1,03**, 6 anni su 6 | quasi: corretto 0,66 |
| 7 | F2 sulle monete 101-200 (`SETTIMA.md`) | conferma | Sharpe 0,18 (costi 19% l'anno) | no |
| 8 | **F3: funding fra monete, pesi secondo la volatilità** (`OTTAVA.md`) | 1 | **1,28**, +50,6% l'anno, ogni anno 2021-2026 positivo, sopra il caso | quasi: corretto 0,76; no sulle 101-200 |
| 9 | Acquisti aggressivi (G1) e «lotteria» (G2) fra monete (`NONA.md`) | 2 | G1 −1,17 (verso opposto: chi compra a mercato sale); G2 0,18 | no |
| 10 | CTREND con funding e acquisti fra gli indicatori (`DECIMA.md`) | 1 | 0,43 | no |
| 11 | Posizioni: grandi contro piccoli (P1), interesse aperto (P2) (`UNDICESIMA.md`) | 2 | P1 0,06; P2 −0,94 (verso opposto: la leva che entra continua) | no |
| 12 | **K1: denaro che entra, leva che costa poco** (`DODICESIMA.md`) | 1 | 1,27 dal 2022 — **costruzione** (due versi visti prima) | solo paper |
| 13 | Funding medio del mercato per il Bitcoin (`TREDICESIMA.md`) | 1 | 0,47 contro 0,56 del Bitcoin comprato | no |
| 14 | **M1: modello ad alberi che unisce ~70 ingredienti**; M2 lineare (`QUATTORDICESIMA.md`) | 2 | **M1 1,35**, +50,9% l'anno dal 2022, sopra il caso; M2 0,62 | quasi: corretto 0,59 |
| 15 | **F3 + M1 a rischio uguale** (`QUINDICESIMA.md`) | 1 | **1,69**, +44,8% l'anno, ogni anno 2022-2026 positivo, discesa −33% | quasi: corretto 0,76 |
| 16 | M3: il modello di M1 ogni giorno, con entrata al 20% e uscita al 40% (`SEDICESIMA.md`) | 1 | 0,95 dal 2022, +31,2% l'anno, ma spese 23,8% l'anno (giro 342 volte), 2026 −29%, ultimo anno −4,6%; correlazione con M1 0,64 | no: ogni giorno costa troppo |
| 17 | Sei modelli in gara, scelti ogni volta solo col passato (M4) e la loro media (M5) (`DICIASSETTESIMA.md`) | 2 | M4 0,71 (+30,1% l'anno, 2024 −14,5%), M5 0,95 (+37,7%); la gara sceglie quasi sempre foresta (23 volte) e alberi casuali (17), gli alberi di M1 solo 4 su 63; correlazione con M1 0,79 e 0,85 | no: M1 da solo era meglio, quindi il suo 1,35 dipende anche dalla scelta del modello |
| 18 | Le monete appena quotate: short quelle con 7-60 giorni (N1) o 7-180 (N2), long le 100 grandi (`DICIOTTESIMA.md`) | 2 | N1 −18,5% l'anno (Sharpe −0,26), N2 −22,3% (−0,45), 2025 −66%; la moneta nuova tipica scende (mediana −3,6% a settimana) ma poche esplodono (COAI +2627% in una settimana, MYX +894%, AIA +573%): senza le 20 settimane-moneta migliori la media è −1,6% a settimana | no: la coda verso l'alto uccide lo short |
| 19 | Il premio del perpetuo sullo spot fra monete (P1) e insieme al funding (P2) (`DICIANNOVESIMA.md`) | 2 | **P1 1,25**, +49,6% l'anno, ogni anno 2021-2026 positivo, intervallo sopra zero; P2 1,20; correlazione con F3 0,83 e 0,92 (F3 sugli stessi dati 1,30); nelle 47 settimane dei pari P1 +0,66% a settimana, F3 +0,85% | quasi: corretto 0,33 con 44 prove; è lo stesso vantaggio di F3 misurato in un altro modo, non lo migliora |
| 20 | Il volume a pronti contro quello del perpetuo: livello (S1) e cambio (S2) (`VENTESIMA.md`) | 2 | S1 0,59 (+24,6% l'anno, 3 anni su 6, ultimo anno −11%); S2 −0,82 (−33% l'anno): verso **opposto** a quello scritto — quando la quota del perpetuo sale (entra la leva) la moneta continua a salire, come per l'interesse aperto (prova 11) e gli acquisti a mercato (prova 9) | no |
| 21 | Gli annunci di Binance: short dopo l'etichetta di monitoraggio (E1) e dopo la rimozione a pronti (E2), contro il Bitcoin (`VENTUNESIMA.md`) | 2 a eventi (fuori dallo Sharpe corretto) | E1 −1,06% a evento (88 eventi, 68% vinti, DEGO +295% contro); E2 −21,2% (62 eventi, 69% vinti, ALPACA +1796% in una settimana); la prima reazione (il giorno dell'annuncio) è grande, −11% e −18%, ma non si prende | no: le code verso l'alto |
| 22 | La leva che entra continua: conferma sulle monete 101-200 con il cambio della quota a pronti (L1) e insieme agli acquisti a mercato (L2) (`VENTIDUESIMA.md`) | 2 di conferma | **sulle 101-200 il verso si rovescia**: L1 −47,5% l'anno (Sharpe −1,07), L2 −37,5% (−0,91); sulle 100 (confronto) L1 0,44, L2 0,63 | no: l'ipotesi vista tre volte sulle 100 non vale sulle altre |
| 23 | M6: il modello ad alberi di M1 con la media di cinque semi, sui dati corretti (`VENTITREESIMA.md`) | 1 | **Sharpe 1,02**, +40,0% l'anno dal 2022, positivo in tutti e 5 gli anni, intervallo sopra zero, discesa −47,9%; i semi da soli 1,02-1,16; correlazione con F3 0,23 | non valida: corretto 0,16 con 47 prove; nel paper come informazione |
| 24 | **F5: F3 che cambia meno**, entrata al 20% e uscita al 40% (`VENTIQUATTRESIMA.md`) | 1 | **Sharpe 1,93**, +57,4% l'anno dal 2021, volatilità 29,7%, discesa −31%, ogni anno positivo (2026 +24,9%), giro 1,35 invece di 2,12, spese 4,9% invece di 7,7%; F3 sugli stessi dati 1,28; contro il caso (`F5_caso.json`) media −0,11, massimo 0,79 su 200 | **quasi**: corretto 0,81 con 48 prove, la più vicina; nel paper |
| 25 | M7: il modello M6 con la banda; F5 + M7 a rischio uguale (`VENTICINQUESIMA.md`) | 2 | M7 **1,25** dal 2022 (M6 1,08), spese 5,8% invece di 8,5%, 5 anni su 5; **F5 + M7 1,83**, +44,2% l'anno, volatilità 24,2%, discesa −34,6%, 5 anni su 5 (F5 da sola dal 2022 1,69); correlazione F5-M7 0,31 | quasi: corretti 0,20 e 0,65 con 50 prove; nel paper come informazione |
| 26 | Il funding che tocca il tetto: long dopo il passaggio a un intervallo più corto con funding negativo (E3), short con funding positivo (E4) (`VENTISEIESIMA.md`) | 2 a eventi | **E4: +11,67% a evento in 7 giorni** (62 eventi, 61 monete, 35 settimane), 79% vinti, mediana +15,4%, senza i 5 migliori +7,5%, ogni anno 2023-2026 positivo, quasi tutto dal prezzo (+11,9%, funding +0,2%); p 0,0047. E3: +13,9% ma 38% vinti, senza i 5 migliori +1,7%, p 0,0166 | **E4 passa l'esame scritto** (p ≤ 0,005 per la coppia); contando tutte e 4 le prove a eventi del programma la soglia sarebbe 0,0025 e non la passerebbe: promettente, non dimostrata; nel paper. E3 no |
| 27 | E4 su un altro exchange: la conferma su Gate.io, eventi indipendenti da quelli di Binance (`VENTISETTESIMA.md`) | 1 di conferma | come scritta: 456 eventi, −4,24% a evento, p 0,67; ma 289 eventi sono cambi d'intervallo fatti da Gate in blocco in due giorni. Senza i giorni in blocco (calcolo fatto dopo, descrittivo): 114 eventi, +6,00%, mediana +7,9%, 75% vinti, p 0,096. Primo calcolo con un errore di lettura (secondi di scarto, corretto) | **non confermata**: Gate non conferma e non smentisce; E4 resta nel paper con la nota |
| 28 | K2: K1 con la banda (costruzione); F5 + M7 + K2 a rischio uguale (`VENTOTTESIMA.md`) | 2 | K2 **1,72** dal 2022 (K1 1,25), spese 6,8% invece di 10,0%, 5 anni su 5; **F5 + M7 + K2 2,11**, +43,2% l'anno, volatilità 20,5%, discesa −30,2%, 5 anni su 5 | quasi: corretti 0,47 e 0,76 con 52 prove; costruzioni, nel paper come informazione |
| 29 | M8: il modello di M7 con l'obiettivo «di quanto la moneta fa meglio della media» invece del rango (`VENTINOVESIMA.md`) | 1 | Sharpe 1,21 dal 2022 (M7 1,25 sugli stessi anni), +31,3% l'anno, volatilità 25,9%, discesa −27%, 5 anni su 5; correlazione con M7 solo 0,47 | no: corretto 0,12 con 53 prove; non meglio di M7, non nel paper |
| 30 | **N3: short le monete appena quotate con l'uscita a +30%**, per 30 giorni, sulle monete nuove di Gate.io non ancora su Binance (`TRENTESIMA.md`) | 1 a eventi | **+7,59% a evento** (449 monete, 139 settimane), p 0,0001, mediana +6,5%, 53% vinti, positiva in ogni anno 2023-2026 e nelle due metà, senza i 5 migliori +6,5%; l'uscita scatta nel 44% dei casi; senza l'uscita +11,2% ma con perdite enormi su poche monete. Primo calcolo (+6,23% su 631) con dentro azioni, fondi, indici e metalli di Gate.io: corretto con il tipo dei contratti (`tipi_gate.py`) | **VALIDA**: passa l'esame scritto su dati mai guardati, anche contando tutte e 6 le prove a eventi; nel paper |
| 31 | M7 + M8 a rischio uguale (costruzione) (`TRENTUNESIMA.md`) | 1 | Sharpe **1,39** dal 2022 (M7 da solo 1,25), +35,4% l'anno, volatilità 25,5%, discesa −31%, 5 anni su 5 | no: corretto 0,20 con 54 prove; costruzione, nel paper come informazione |
| 32 | La regola N3 sul passato di Binance, senza cambiare niente (riserva: l'idea dell'uscita era nata su questi dati) (`TRENTADUESIMA.md`) | 1 a eventi | **+4,29% a evento** su 613 monete nuove (207 settimane), p 0,0017, mediana +5,6%, 54% vinti, metà +6,9% e +1,7%, senza i 5 migliori +3,6%; per anno 2021 −1,5%, 2022 +2,3%, 2023 +6,7%, 2024 +7,7%, 2025 +4,6%, 2026 −0,6%; senza l'uscita +4,4% ma p 0,059 | **passa l'esame scritto**, con la riserva (dati non vergini per l'idea dell'uscita) e più debole nel 2026; nel paper in avanti |
| 33 | Le due strategie di Binance in un portafoglio: N3 con il 5% a operazione (al massimo 20) e F5 + N3 a rischio uguale (`TRENTATREESIMA.md`) | 2 | **N3 a portafoglio: Sharpe 0,62**, +20,9% l'anno, volatilità 33,8%, discesa −47%, 2021 −10%, 2026 −12,5%; F5 + N3 1,45 (F5 da sola 1,93); correlazione 0,16 | no: positiva per operazione non vuol dire buona da tenere: le monete nuove arrivano a ondate e le perdite si sommano |
| 34 | Indicatori tecnici con il contesto del funding: rottura di Donchian a 4 ore con stop e uscita mobile, senza filtro (T1) e con il filtro del funding (T2) (`TRENTAQUATTRESIMA.md`) | 2 | T1 −0,197% a operazione su 34.397 (long −0,57%, short +0,19%); T2 +0,014% su 15.406 (long −0,31%, short +0,32%), p 0,48; tenuta media 72 ore; portafogli negativi | no: il filtro del funding aggiunge +0,21% a operazione ma non basta; seguire le rotture verso l'alto perde |
| 35 | Contro gli eccessi: RSI a 4 ore sopra 70 con funding alto → short, sotto 30 con funding basso → long, stop 2 ATR, obiettivo RSI a 50 (`TRENTACINQUESIMA.md`) | 1 | −0,218% a operazione su 9.785 (long −0,41%, short −0,03%), 47% vinte, tenuta media 40 ore, 52% delle uscite allo stop; portafoglio Sharpe −0,47 | no |
| 36 | T5: la tendenza a 1 giorno (regola pubblicata, long e short) solo nel verso del funding, universo delle 100 (`TRENTASEIESIMA.md`) | 1 | Sharpe 0,40, +3,7% l'anno, volatilità 9,4%, 5 anni su 6; senza il filtro 0,15 | no: il filtro migliora (terza volta), l'indicatore porta poco |
| 37 | T6: la rottura a 4 ore con il funding, entrando con l'ordine limite (`TRENTASETTESIMA.md`) | 1 | entrate eseguite 99%; +0,048% a operazione su 15.391 (T2 a mercato +0,014%), p 0,43; long −0,28%, short +0,36% | no: l'ordine limite risparmia poco |
| 38 | T7: solo lo short delle rotture verso il basso dove i long pagano, conferma sulle monete 101-200 (`TRENTOTTESIMA.md`) | 1 di conferma | +0,136% a operazione su 5.499, p 0,40; metà +0,44% e −0,16%; 2026 −1,1%; portafoglio Sharpe −0,61 | **non confermata** |
| 39 | T8: la tendenza del giorno (media dei 50 giorni) e il ritracciamento a 4 ore (RSI 35/65), con il funding, stop 2 ATR e uscita mobile 3 ATR (`TRENTANOVESIMA.md`) | 1 | +0,149% a operazione su 8.720, p 0,32; long −0,46%, short +0,53%; senza le 5 migliori +0,03%; portafoglio Sharpe −0,07 | no |
| 40 | Le coppie di monete che si allontanano: z del rapporto a 1 giorno, entrata a 2, uscita a 0,5, rottura a 4, al massimo 20 giorni (`QUARANTESIMA.md`) | 1 | +0,58% a operazione su 874, p 0,21; in calo ogni anno (2021 +3,9%, 2025 −1,1%); senza le 5 migliori −0,23%; portafoglio Sharpe 0,34, corretto 0,00 | no |
| 41 | U1: lo short dopo l'arrivo su Upbit (mercato in won) delle monete che hanno già il perpetuo su Binance, 2 ore dopo la prima ora, per 7 giorni, contro il Bitcoin, uscita a +30% (`QUARANTUNESIMA.md`) | 1 a eventi + 1 portafoglio | +2,96% a evento su 115 (85 settimane), p 0,070 contro la soglia 0,0014; mediana +6,9%, 70% vinti; metà +5,3% e +0,7%; per anno 2024 +5,3% (17), 2025 +0,1% (43), 2026 +1,3% (36); la fiammata prima dell'entrata +26,6% contro il Bitcoin; portafoglio Sharpe 0,58 | no |
| 42 | F6: F5 con l'esposizione secondo l'agitazione delle 13 settimane prima (0,30/σ, al massimo 2; Moreira e Muir 2017) (`QUARANTADUESIMA.md`) | 1 | Sharpe **1,71** contro 1,93 di F5 sulle stesse settimane, +55,7% l'anno, volatilità 32,5%, discesa −35,6%; esposizione media 1,20; 2021 +65,9% (F5 +122,6%) | no: corretto 0,31 con 65 prove; tenere meno nelle settimane agitate toglie a F5 le sue settimane migliori |
| 43 | Entrare 5 minuti dopo l'annuncio di Binance, per 24 ore contro il Bitcoin: Q1 long dopo la quotazione a pronti di una moneta che ha già il perpetuo (eventi mai guardati), Q2 short dopo l'etichetta di monitoraggio o la rimozione (eventi della prova 21, con la riserva) (`QUARANTATREESIMA.md`) | 2 a eventi + 2 portafogli | **Q1**: +0,03% a evento su 61, p 0,51, mediana −4,95%; nei primi 5 minuti la moneta era già salita del 13,1% (mediana 7,3%). **Q2**: +3,08% su 150 (49 annunci), p 0,024 contro 0,0011, 2026 +1,8% su 82; nei 5 minuti persi −8,75% già fatto; portafogli Sharpe 0,00 e 0,83 | no: le notizie si prezzano in pochi minuti |
| 44 | S1: long il Bitcoin per la settimana se l'offerta totale delle stablecoin (DefiLlama) è cresciuta nella settimana prima, altrimenti niente (`QUARANTAQUATTRESIMA.md`) | 1 | Sharpe 0,66, +29,3% l'anno, discesa −57,9% (il Bitcoin tenuto sulle stesse settimane 0,38, discesa −77,4%); in posizione il 66% delle settimane; più del Bitcoin +8,4% l'anno; 2022 −17,5% | no: intervallo non sopra zero, corretto 0,00 con 68 prove |
| 45 | Gli indicatori per decidere quando entrare (domanda del proprietario): I1 F5 con le entrate nuove solo se la tendenza dei 20 giorni è d'accordo; I2 N3 con l'entrata alla prima chiusura sotto il minimo dei 5 giorni (eventi di N3, con la riserva) (`QUARANTACINQUESIMA.md`) | 1 + 1 a eventi + 1 portafoglio | **I1**: Sharpe 1,02 contro 1,93 di F5, discesa −80,5% (F5 −31%): meno monete per lato (18 invece di 25) e 6 settimane con 0-2 monete short, che arrivano a pesare il 100%. **I2**: +3,79% a operazione su 579 (N3 +4,29%), p 0,0064 contro 0,001; 2026 −5,7%; portafoglio Sharpe 0,88 (N3 0,62), discesa −42,7% | no |
| 46 | Le 17 strategie già pronte di TradingView (le «Built-in Strategies»: MACD, RSI, Supertrend, Bollinger, Parabolic SAR, Keltner, Stocastico, canali, pivot, candele…) con i valori di serie, a 4 ore e a 1 giorno, sulle 100 monete, con i costi veri e senza (`QUARANTASEIESIMA.md`) | 34 | nessuna valida. Le migliori: Supertrend a 1 giorno Sharpe 0,36 con i costi (0,49 senza), +17,8% l'anno, discesa −51%; Price Channel a 1 giorno 0,34. Senza costi molte sembrano buone (Momentum 4 ore +24,6% l'anno, MACD 4 ore +23,6%, Pivot Extension 4 ore +26,5%), con i costi veri diventano −3,0%, +0,9%, −11,2% (spese fino al 38% l'anno). RSI, Stocastico e Bollinger (contro gli eccessi) perdono anche senza costi (da −18% a −33% l'anno) | no: corretto 0,00 con 104 prove |
| 47 | La paura nelle opzioni: long Bitcoin (O1) o Ether (O2) per la settimana se il premio delle opzioni (DVOL² − volatilità realizzata²) è sopra la sua mediana delle 52 settimane prima (`QUARANTASETTESIMA.md`) | 2 | dal 2022-03-28: **O1** Sharpe 0,29 (il Bitcoin tenuto 0,37), in posizione il 37% delle settimane, discesa −36,6% invece di −65,7%; **O2** Sharpe 0,36 (l'Ether tenuto 0,15), discesa −48% invece di −69,5%, 2026 −26,6% | no: intervalli non sopra zero, corretto 0,00 con 106 prove |
| 48 | R1, il regista: ogni mese solo le strategie fra F5, M7, K2 con le 4 settimane prima sopra zero, a rischio uguale (Gupta e Kelly 2019) (`QUARANTOTTESIMA.md`) | 1 | Sharpe 1,52, +33,2% l'anno, discesa −30,5% dal 2022-04 contro 1,93 (+39,9%) di F5 + M7 + K2 sempre accese sulle stesse settimane; spente F5 14 mesi, M7 20, K2 18; 6 mesi tutto fuori; 2023 −8,7% | no: corretto 0,19 con 107 prove; spegnere le strategie che hanno perso nel mese prima toglie i mesi buoni dopo |
| 49 | Il momento delle 3 settimane (X1) e la dimensione, le piccole contro le grandi (X2), fra le 100 monete con la banda di F5 (Liu, Tsyvinski e Wu 2022) (`QUARANTANOVESIMA.md`); prima prova con lo Sharpe corretto rivisto | 2 | **X1** Sharpe 0,05 (2021 −28%, 2022 −36%, 2023 −19%, 2024 +16%, 2025 +57%, 2026 +29%); **X2** Sharpe 0,47, 2021 +134,8% poi 2024 −24,5%, 2025 −30,3%, 2026 −14,9%; correlazioni con F5 0,04 e 0,03 | no: corretto rivisto 0,00 e 0,01 (58 gruppi) |
| 50 | F5 identica sulle monete dalla 101ª alla 150ª, scarto 0,10% (`CINQUANTESIMA.md`) | conferma | Sharpe 0,30, +13,8% l'anno dal 2022-04 (236 settimane), p 0,24; dal funding +27,7% l'anno, dal prezzo +1,2%, spese 15,1% (giro 1,94); ultimo anno −15,1%; correlazione con F5 sulle 100 0,17 | **non confermata**: il funding c'è anche qui, i costi se lo mangiano |
| 51 | F7: F5 sulle monete 101-150 con le variazioni del lunedì a ordine limite all'apertura per un'ora, poi a mercato (`CINQUANTUNESIMA.md`) | 1 | in calcolo | — |

Totale nel conto: 9 + 3 + 9 + 3 + 2 + 1 + 2 + 1 + 2 + 1 + 1 + 2 + 1 + 1 + 2 + 2 + 2 + 2 + 1 + 1 + 2 + 2 + 1 + 1 + 2 + 2 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 2 + 1 + 2 + 34 + 2 + 1 + 2 + 1 = **110** (le conferme 4, 5, 7 non contano: sono una
regola sola su dati non usati). Controlli descrittivi (non contano): `robustezza_F2.md` (F2, F3, M1), `F2_2020.md`,
`F3_caso.md`, `ESECUZIONE.md` (ordini limite: costi di F3 dal 7,7% al 5,3% l'anno).

**L'asticella rivista** (22 ottobre, richiesta del proprietario; `programma6/ASTICELLA.md`, scritta prima del ricalcolo,
risultati in `programma6/RISULTATI_ASTICELLA.md`). Lo Sharpe corretto si calcolava contando le 107 prove una per una; gli
autori del metodo (López de Prado 2019, 2020) prescrivono di contare i **gruppi di prove simili** (correlazione dei rendimenti)
e di usare la varianza degli Sharpe dei gruppi. Con il taglio fissato prima (correlazione media 0,5): **56 gruppi**, deviazione
0,63 invece di 0,77. Sharpe corretto rivisto: **F5 0,87** (prima 0,46), **F5 + M7 + K2 0,90**, F5 + M7 0,76, K2 0,70, F6 0,72,
M7 0,32; nessuna arriva a 0,95 al taglio scelto (al taglio 0,3, solo per capire: F5 + M7 + K2 0,96, F5 0,94). Con l'altra
asticella pubblicata, il t dello Sharpe contro 3,0 (Harvey, Liu e Zhu 2016), passano F5 (4,66), F5 + M7 + K2 (4,62), F6, F5 + M7,
K2, R1, M7 + M8; M7 no (2,73). **Da qui si usa il calcolo rivisto** (gruppi), con la soglia 0,95.

**Il prezzo della ricerca** (21 ottobre): lo Sharpe corretto di F5 (Sharpe 1,93) era 0,815 con 48 prove ed è **0,517** con 67 (`programma6/STATO.md`, lezione 29). Ogni prova nuova sugli stessi anni alza l'asticella anche per le strategie già trovate: le idee nuove vanno scelte per quanto sono probabili, non per quante sono; le conferme su dati non usati non contano.

**Errori trovati e corretti**: universo delle 100 monete di oggi (sopravvissute) → universo mese per mese con i dati di
allora (prova 2); petrolio e azioni nate dal 2026-04 quasi entrati nel paper (`SECONDA.md`, sezione 9); una catena partita
prima della fine dello scarico (`UNDICESIMA.md`, nota); la fuga di informazione dei dati sulle posizioni sulle monete
101-200 (`RISULTATI_QUATTORDICESIMA.md`, correzione); le monete tolte dal listino restano nei file con il prezzo fermo e il volume zero, e
il loro funding era riempito con la media dei 90 giorni prima (58.403 giorni-moneta; 42 settimane-moneta nell'universo
delle 100): corretto dalla diciottesima prova; effetto (`programma6/controllo_zombi.json`): F3 1,296 → 1,295, K1 1,269 →
1,262, **M1 1,35 → 0,79** (il modello ad alberi è fragile).

## 2. Il paper (dal 20 ottobre 2026 per i giorni, dal 26 ottobre per le settimane)

`programma6/paper/REGOLE.md`, aggiornato ogni mattina, in dashboard nella scheda Controllo. Candidate: **F3, K1, M1, F3 +
M1**, più F2, C1, A1. Verdetto a 52 settimane (25 ottobre 2027) e a 104, mai prima. Risultati in `programma6/paper/PAPER.md`.

## 3. Programma 5 (18-19 ottobre 2026): circa 60 idee, nessuna valida

Dettagli in `programma5/STATO.md` e `programma5/idee/`. In breve, per non rifarle:

* **Al minuto, nei crolli e nelle esplosioni** (I-001…I-007): rimbalzo dopo crolli con interesse aperto che cala,
  salite estreme, esplosioni con interesse aperto che cresce, rapporti long/short agli estremi, squilibrio degli acquisti
  aggressivi, regolamento del funding estremo, monete che seguono BTC al minuto: **tutte bruciate** sul 2020-2022.
* **A ore** (I-010…I-020): rimbalzo dopo crolli di qualche ora (I-010, I-017: le più vicine, +2,2% a trade su 2024-2026
  ma p 0,0037 contro 0,0017), rottura del massimo di 60 giorni, volume enorme in discesa, scosse proprie con e senza
  copertura, reti d'acquisto sotto il prezzo (I-016), scalping con ordini limite (I-020): **bruciate**.
* **Fase 2, 2024-2026, 100 monete** (J-001…J-010): continuazioni (J-001, J-002, J-005) positive ma quanto il caso;
  rimbalzi andati male nel secondo semestre 2025; reti nelle code e idee di sessione: **bruciate**.
* **Procedure di scelta mensile** (M-001, M-002, M-003): M-002 bocciata sui dati nuovi; M-001c e M-003 in prova in avanti
  (`programma5/avanti/A.md`), per ora negative.
* **Fattori fra monete a ore** (E-114: volatilità, beta, salti, illiquidità, distanza dal massimo, asimmetria) e **modello
  ridge su 21 segnali** (K-001): **bruciati**.
* **Libro degli ordini** (E-201): nessuna cella promossa.
* **Seconda tornata in avanti** (N-001, N-002, N-003): in corso dal 2026-10-19 (`programma5/avanti/A2.md`).

## 4. Prima del programma 5

* Il **gate** (agosto-ottobre 2026): migliaia di combinazioni ogni 3 ore, lo 0,29% passava, le passate facevano −0,06 R a
  trade in paper; fermato il 13 ottobre (`ops/gate_fermo`, `docs/storia/`).
* **Protocolli di ricerca per moneta** (BTC51 su Bitcoin, LINK6 su LINK con 9 monete di controllo, campagne per moneta e di
  gruppo): nessuna strategia valida; lezioni in `research/campagne/*/lezioni.md` e nella storia del progetto
  (`docs/storia/`).
* **Autopsia delle strategie vecchie** e **scalping sulla volatilità** (18 ottobre): `research/autopsia/`,
  `research/scalping/`.

## 5. Idee in coda (da fare, in quest'ordine; si spostano in sezione 1 quando si provano)

1. ~~Le monete meno liquide con ordini limite~~ → non si fa (20 ottobre): F3 sulle 101-200 prende +31,0% l'anno dal
   funding ma perde −6,6% dal prezzo, con spese del 19,1% e volatilità di circa il 40% (`RISULTATI_OTTAVA.md`); anche con le
   spese ridotte a un terzo (stima) farebbe circa +18% l'anno, Sharpe circa 0,4: non vale una prova.
2. ~~M1 su più orizzonti~~: ogni giorno → prova 16 (no: i costi); ogni 2 settimane non serve più: la banda (prove 24-25)
   toglie il giro in modo migliore.
3. ~~M1 con obiettivo diverso~~ → prova 29 (il modello che unisce M1 e M2 non si fa: M2, lineare, fa 0,62 e la gara dei
   modelli della prova 17 lo sceglie solo 9 volte su 63).
4. ~~Il premio del perpetuo sullo spot fra monete~~ → prova 19.
5. ~~Coppie di monete simili~~ → prova 40 (a 1 giorno: a ore i costi delle quattro operazioni sono troppi).
6. ~~Un regista~~ → prova 48 (con F5, M7, K2).
7. ~~Le monete appena quotate con lo stop~~ → prova 30, su Gate.io (Bybit non è raggiungibile da qui).
8. ~~M1 con più semi~~ → fatto (`programma6/semi_M1.json`, descrittivo): sei semi danno Sharpe da 0,79 a 1,43, media 1,10.
9. ~~Il funding che tocca il tetto~~ → prova 26 (come evento).
10. ~~Il volume a pronti contro quello del perpetuo~~ → prova 20.
11. ~~K1 con la banda~~ → prova 28.
13. ~~M7 e M8 insieme~~ → prova 31.
14. ~~Gli indicatori a 1 giorno nel verso del funding~~ → prova 36 (no: Sharpe 0,40).
15. ~~L'arrivo su Coinbase come conferma di U1~~ → non si fa: U1 non regge (prova 41). Le date di Coinbase sono scaricate (`scarico_coinbase.py`) se serviranno.
16. ~~La paura nelle opzioni~~ → prova 47.
17. ~~Le strategie di TradingView così come sono pubblicate~~ → prova 46 (le 17 già pronte di TradingView); quelle che il proprietario indicherà si provano una per una.
18. ~~Il momento fra monete a 1-4 settimane~~ → prova 49 (X1).
19. ~~La dimensione~~ → prova 49 (X2).
20. ~~Le liquidazioni forzate~~: l'archivio di Binance non ha i file delle liquidazioni dei perpetui USDT-M (controllato il
   22 ottobre: nessun file sotto `liquidationSnapshot`); non si fa.
21. ~~F5 sulle monete dalla 101ª alla 150ª~~ → prova 50 (conferma).
22. ~~F5 sulle 101-150 con gli ordini limite~~ → prova 51 (F7).
12. **Non si cercano le soglie migliori della banda** (20% e 40% vengono dalla prova 16, scelte prima): provarne altre sui
   dati del passato sarebbe cercare il parametro che va meglio per caso, l'errore del primo gate.
