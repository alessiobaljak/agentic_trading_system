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
8. **Gli acquisti aggressivi fra monete dicono il contrario del funding** (prova 9): le monete con molti acquisti a mercato
   continuano a salire rispetto alle altre (il rovescio della regola scritta fa +30,3% l'anno sulle 100 grandi, descrittivo);
   il funding alto invece rientra. Anche qui solo fra le monete liquide.
9. **Il carry** (comprato a pronti, venduto il perpetuo) dal 2025 non rende (Borri, Liu, Tsyvinski e Wu 2025, sezione
   3.6: Sharpe 6,45 dal 2020, 4,06 dal 2024, negativo nel 2025), e il proprietario non lo vuole: non si prova.

## Dati (fuori da git, con le impronte nel repository)

* `research/data/p6/`: candele a 15 minuti, 1 ora e 4 ore delle 100 monete, fatte dai minuti verificati del programma 5.
* `research/data/p6g/`: candele giornaliere e funding di tutti i 892 perpetui USDT-M dell'archivio
  (`scarico_giorni.json`); controllo contro le ore verificate: 125.808 giorni, chiusure oltre lo 0,1% in 2 giorni
  (`risultati_seconda/controllo_dati.json`).
* `research/data/p6h/`: candele a 1 ora delle 537 monete mai usate (`scarico_ore.json`).
