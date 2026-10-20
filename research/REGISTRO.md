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

## 1. Programma 6 (dal 19 ottobre 2026): strategie su indicatori e dati di mercato, 52 prove nel conto

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
| 28 | K2: K1 con la banda (costruzione); F5 + M7 + K2 a rischio uguale (`VENTOTTESIMA.md`) | 2 | in calcolo | — |

Totale nel conto: 9 + 3 + 9 + 3 + 2 + 1 + 2 + 1 + 2 + 1 + 1 + 2 + 1 + 1 + 2 + 2 + 2 + 2 + 1 + 1 + 2 + 2 = **52** (le conferme 4, 5, 7 non contano: sono una
regola sola su dati non usati). Controlli descrittivi (non contano): `robustezza_F2.md` (F2, F3, M1), `F2_2020.md`,
`F3_caso.md`, `ESECUZIONE.md` (ordini limite: costi di F3 dal 7,7% al 5,3% l'anno).

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
3. **M1 con obiettivo diverso**: il rendimento in più della moneta invece del rango, e un modello che unisce M1 e M2.
4. ~~Il premio del perpetuo sullo spot fra monete~~ → prova 19.
5. **Coppie di monete simili** (stessa famiglia, prezzi che si muovono insieme): quando si allontanano, scommettere che si
   riavvicinano, a ore.
6. **Un regista**: un modello che ogni mese decide quanto capitale dare a F3, K1, M1 secondo come sono andate.
7. **Le monete appena quotate con lo stop** (dalla prova 18, quindi **costruzione**: l'idea viene da quello che si è visto):
   short le giovani ma con l'uscita se il prezzo sale del 30% dall'ingresso, con le candele a 1 ora. Sui dati del passato il
   risultato è già in parte noto (senza le code la media è −1,6% a settimana), quindi conta solo sui dati nuovi o su un
   altro exchange (le monete quotate solo su Bybit).
8. ~~M1 con più semi~~ → fatto (`programma6/semi_M1.json`, descrittivo): sei semi danno Sharpe da 0,79 a 1,43, media 1,10.
9. ~~Il funding che tocca il tetto~~ → prova 26 (come evento).
10. ~~Il volume a pronti contro quello del perpetuo~~ → prova 20.
11. ~~K1 con la banda~~ → prova 28.
12. **Non si cercano le soglie migliori della banda** (20% e 40% vengono dalla prova 16, scelte prima): provarne altre sui
   dati del passato sarebbe cercare il parametro che va meglio per caso, l'errore del primo gate.
