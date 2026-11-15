# Risultati della prova 161 (NOVANTANOVESIMA): il funding coperto su Bitcoin ed Ether con il margine vero

Eseguita il 15 novembre 2026. Dati completi: `risultati_novantanovesima/esame.json`, `giorni_{A,B}.csv.gz`, `settimane_{A,B}.csv.gz` (colonna `netto`,
indice il lunedì in giorni dall'epoca), i controlli `giorni_{A,B}_limite.csv.gz` e `giorni_{A,B}_passi1000.csv.gz`.

## Riepilogo
Secondo l'esame scritto prima la prova è **promettente**: le quattro condizioni e «nessuna liquidazione» passano per tutte e due le varianti.
Ma il numero è basso: **+6,5% l'anno (A) e +6,3% (B) sul capitale, 63-65 USDT l'anno su 1.000; dal 2022 solo +3,4% e +3,1% (31-34 USDT)**.
Il 2021 vale 22% da solo. Nessuna liquidazione, margine rifornito 49 volte in A e 31 in B. La prova è quasi la stessa serie della 157
(correlazione settimanale 0,98-0,99): conta come la stessa idea, non come un'idea nuova. Sharpe corretto 1,00 (valore al tetto, come nella 157:
numero meccanico, non misura i rischi di borsa e di dollaro digitale). Il giudizio sulla credibilità spetta a backtest-auditor.

## La prova come è scritta e scala di tempo
`NOVANTANOVESIMA.md` (dd1399d) con le letture della sezione finale (df973b9): Bitcoin ed Ether metà del capitale ciascuno; pronti più perpetuo
venduto; dentro se la media del funding degli ultimi N giorni è sopra zero (A: 30, B: 90); due portafogli (pronti, future); margine al 60% del
valore del perpetuo, rifornito a pronti all'apertura sotto il 45% fino al 60%; liquidazione con il massimo orario del prezzo mark, mantenimento 0,5%;
patrimonio totale composto; riequilibrio solo al rientro. Scala: conto giornaliero da apertura ad apertura (2.100 giorni, dal 4 gennaio 2021 al 4 ottobre 2026,
uscita all'apertura del 5), esame sulle 300 settimane (composte dai giorni).

## Implementazione
`research/programma7/novantanovesima.py` (usa `novantacinquesima.segnale`, `novantanovesima_dati`, `seconda.pannello`, `terza.esame`,
`asticella.corretto_famiglie`; non modifica nulla della 157). Commit del codice: nessuno (non richiesto); regole e dati al commit df973b9.
Mark: 216 ore riempite col prezzo scambiato su BTC e 72 su ETH; nessuna ora rimasta vuota.

## Varianti provate
2 (A, B), più i controlli descrittivi (ordini limite, sempre dentro, passi veri a 1.000 USDT: non sono varianti). Registro: `research/trials/novantanovesima.csv`.

## Risultati (capitale 1.000 USDT iniziali, composto)
| | A (30) | B (90) |
|---|---|---|
| Giorni | 2.100 | 2.100 |
| Rendimento l'anno (composto / media settimanale per 52) | +6,47% / +6,27% | +6,28% / +6,09% |
| USDT l'anno su 1.000 (composto) | 64,7 | 62,8 |
| Dal 2022 (248 settimane; media per 52 / composto) | +3,36% / +3,42% (33,6 USDT), Sharpe 5,23 | +3,14% / +3,19% (31,4 USDT), Sharpe 5,21 |
| Sharpe su 52 settimane / t | 3,60 / 8,65 | 3,51 / 8,43 |
| Sharpe corretto (195-196 famiglie) | 1,00 | 1,00 |
| Discesa massima settimanale (giornaliera) | −0,31% (−0,33%) | −0,27% (−0,29%) |
| Peggiore settimana | −0,14% | −0,08% |
| Mesi positivi | 62 su 70 | 62 su 70 |
| Giorni (dentro positivi / dentro negativi / fuori) | 1.657 / 338 / 105 | 1.679 / 380 / 41 |
| Costo medio l'anno (sul capitale) | 0,28% | 0,15% |
| Patrimonio finale su 1.000 | 1.434,6 | 1.419,3 |
| Rifornimenti del margine (BTC + ETH), valore venduto | 22 + 27 = 49, 2.441 USDT | 8 + 23 = 31, 1.551 USDT |
| Liquidazioni | 0 | 0 |
| Margine minimo all'apertura (prima del rifornimento) BTC / ETH | 31,7% / 34,9% | 31,7% / 35,0% |
| Giorni dentro BTC / ETH; ingressi | 1.949 / 1.898; 5 e 6 | 2.055 / 1.947; 2 e 3 |

Anno per anno, calendario, in USDT su 1.000 iniziali (funding / base / spese / rifornimenti venduti, numero) e rendimento:
* A: 2021 +22,2% (225,2 / +0,8 / 4,1 / 778, 17); 2022 +0,7% (15,4 / −0,1 / 6,9 / 192, 4); 2023 +4,9% (62,4 / −0,6 / 1,3 / 608, 12);
  2024 +7,3% (96,8 / +0,5 / 2,9 / 619, 12); 2025 +2,7% (37,4 / +0,1 / 0,2 / 101, 2); 2026 al 4 ottobre +0,9% (17,3 / 0,0 / 5,0 / 144, 2).
* B: 2021 +22,2% (224,0 / +0,5 / 2,7 / 661, 14); 2022 +1,0% (12,6 / +0,2 / 1,1 / 0, 0); 2023 +3,7% (46,7 / −0,5 / 0,4 / 192, 4);
  2024 +7,3% (93,6 / +0,5 / 0,9 / 423, 8); 2025 +2,7% (36,9 / +0,1 / 0,2 / 100, 2); 2026 +0,7% (15,3 / 0,0 / 5,3 / 176, 3).
Anni dell'esame (media settimanale per 52, anno del lunedì), A: 20,2% / 0,68% / 4,78% / 7,01% / 2,60% / 1,11%; B: 20,1% / 0,95% / 3,63% / 6,99% / 2,58% / 0,92%.
Il guadagno è tutto funding; la base netta è vicino a zero.

Controlli descrittivi (rendimento l'anno composto): ordini limite A +6,57%, B +6,33%; **passi veri a 1.000 USDT (file dei filtri del repository, non di oggi)**
A +6,08%, B +5,91%, nessuna liquidazione, nessun ingresso bloccato, rifornimenti 16+26 (A) e 6+22 (B); sempre dentro +5,80% (Sharpe 3,27, 1 ingresso per moneta,
con passi veri +5,42%). Il segnale sul funding aggiunge circa 0,5-0,7 punti l'anno ma costa fino a 11 ingressi.
Soglia di capitale della gamba del Bitcoin (0,001 BTC minimo, valore minimo 50 USDT, due monete, metà ciascuna): **circa 271 USDT al prezzo del 4 ottobre 2026 (84.754) e circa 399 USDT al massimo del periodo (124.659)**.
Salita massima del prezzo a pronti in una posizione aperta: BTC +327% (A, 2021), ETH +391%; leva del perpetuo mai sopra 3,2 all'apertura, mai sopra il limite fisso 5.
Correlazioni (A / B): con G1 giorni 0,05 / 0,05, settimane 0,15 / 0,16; con Bitcoin giorni 0,03 / 0,04, settimane 0,25 / 0,24; con la prova 97 (settimane) 0,94 / 0,94;
con la prova 157 (settimane) 0,98 / 0,99 (la 157 senza margine faceva +10,5%). Gruppo di famiglia: 97 CC, 157 A, 157 B, 161 A, 161 B.

## Variante migliore e sensibilità
A e B sono quasi uguali (differenza 0,2 punti); per la regola della 157 vale la lenta (B), con meno ingressi e rifornimenti. Nessun'altra variante provata: la sensibilità
a N non è stata misurata (non prevista).

## Esito secondo l'esame scritto prima
Netto positivo: sì. Ogni anno positivo (anno del lunedì, 2021 e 2026 parziali): sì in A e in B (anno più basso 0,68% e 0,92%, di poco). t almeno 3: sì (8,65 e 8,43).
Sharpe corretto almeno 0,80: sì (1,00 e 1,00). Nessuna liquidazione: sì. **Nessun criterio manca.** Valore economico: 63-65 USDT l'anno su 1.000 (31-34 dal 2022).

## Anomalie e possibili errori di motore o dati
* Il mark manca per 216 ore (BTC) e 72 (ETH), riempite col prezzo scambiato come da regole; fra queste il 26 luglio 2021 (+36% in un giorno): la liquidazione lì
  non poteva scattare con il margine del 60% (il minimo di margine è 31,7% prima del rifornimento).
* Sharpe corretto 1,00 al tetto: come nella 157, per t molto alto il valore è meccanico (voce 30 del catalogo).
* Il file dei filtri del repository, non l'exchangeInfo di oggi; il minimo di valore 50 USDT per Bitcoin è quello del file (da verificare sulla macchina).
* Nessun errore del motore visto; il patrimonio finale si ricostruisce dalla somma dei netti (differenza 0).

## Varianti non previste che proporrei (non eseguite)
Pronti come garanzia nel portafoglio dei future (modalità a garanzia multipla); soglia di rifornimento meno alta (45% fa 49 rifornimenti e 2.441 USDT venduti: molti passi per il bot).

## Domande aperte
1. Lo 0,5% di mantenimento e le chiusure forzate dei guadagni nei crolli vanno letti dalla macchina; i risultati non li misurano.
2. Per i soldi veri il bot non ha la gamba a pronti né i trasferimenti fra portafogli; 49 rifornimenti in 5,75 anni.
3. Conta come idea nuova o come la 157 corretta (correlazione 0,98-0,99; stesso gruppo)?

## Letture che ho dovuto scegliere (oltre alle chiuse)
* Rendimento l'anno: media settimanale per 52 per l'esame (come la 157), composto per i USDT; «dal 2022» dalle settimane dal lunedì 3 gennaio 2022.
* Il rifornimento arrotonda per eccesso solo con i passi veri; senza passi nessun arrotondamento; ordini di riduzione senza valore minimo.
* Base = variazione del patrimonio − funding + spese (residuo esatto); per moneta solo funding e spese (i trasferimenti fra monete rendono la base per moneta non separabile).
* Margine minimo «all'apertura» = quello prima del rifornimento. Riequilibrio: sempre fatto prima dell'ingresso, anche se l'altra moneta resta fuori.
* Liquidazione dentro la giornata: solo le ore dopo l'apertura con il massimo del mark; il controllo all'apertura è sul mark delle 00:00 dopo il regolamento.
* Costo medio annuo = media giornaliera delle spese su patrimonio per 365.
