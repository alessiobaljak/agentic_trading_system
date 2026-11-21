# Risultati della prova 163: l'arbitraggio del funding fra Binance e Hyperliquid (idea 153)

Eseguita il 21 novembre 2026 da strategy-researcher. Nessun giudizio sulla credibilità (lo dà backtest-auditor).

## Riepilogo
* **Esito secondo il criterio scritto: NON PASSA, per tutte e due le varianti.** (A: netto -9,27% l'anno; B: +1,77% l'anno.)
* Cause scritte nell'esame: in tutte e due **2 liquidazioni** (tutte con il metodo del massimo e minimo giornaliero, nessuna con quello orario);
  l'anno 2025 è negativo (A -51,5%, B -17,6%); t = -0,64 (A) e 0,12 (B); Sharpe corretto per famiglie 0,00 per tutte e due.
* Il lordo del funding c'è (A 11,0% l'anno, B 21,5% sul capitale di 1.000 USDT) ma le spese lo mangiano in parte (A 4,0%, B 11,8%) e il
  prezzo, che dovrebbe annullarsi, non si annulla nei giorni delle liquidazioni (vedi sotto).
* Controllo descrittivo notevole: **solo Bitcoin ed Ether** non ha liquidazioni né giorni a rischio, Sharpe 2,15 (A) e 1,70 (B), t 3,9 e 3,1, ma
  il netto è 2,6% (A) e 1,9% (B) l'anno, cioè sotto il 3% («poco valore»), e il 2026 è a zero (nessun segnale sopra la soglia).
* Dati: 213 monete abbinate come nella prova 73; **156 entrano nell'universo, 57 escono per la regola del rapporto dei prezzi il primo giorno
  comune** (vedi «Anomalie»: la regola, applicata come scritta, taglia quasi tutte le quotazioni nuove).

## La prova come è scritta (citata) e scala di tempo
Regole: `CENTOUNESIMA.md` (commit 8fe0339), valgono la sezione «Chiusura della verifica» e, dove diversa, prevale quella. Citazioni:
* «Per ogni moneta, alla decisione del giorno D (apertura delle 00:00 UTC) si calcola d = media giornaliera di (somma del funding di
  Hyperliquid del giorno − somma del funding di Binance del giorno) sui **L** giorni interi prima di D».
* «Se d > +θ: venduta su Hyperliquid e comprata su Binance; se d < −θ: il contrario; altrimenti nessuna posizione. Pesi uguali [...] Capitale
  diviso a metà fra le due borse».
* «**A (lenta)**: L = 30 giorni, θ = 10% l'anno, decisione solo il primo giorno del mese. **B (settimanale)**: L = 7 giorni, θ = 20% l'anno,
  decisione solo il lunedì.» Capitale 1.000 USDT, trasferimento solo oltre il 10% del capitale (1 USDT), mantenimento 0,5%, giorno a rischio
  sotto il 10%; prima del 26 aprile 2026 massimo e minimo giornalieri, dopo le candele orarie; spese Binance 0,05% + scarto, Hyperliquid
  0,045% (fonte: tabella delle commissioni dei perpetui nella documentazione di Hyperliquid) + scarto.
* Scala di tempo: giornaliera (decisione alle 00:00 UTC, margine controllato ogni giorno sul lato peggiore prima del 26 aprile 2026, ogni ora
  dopo), esame sulle serie settimanali (lunedì-domenica). Periodo: dal 5 giugno 2023 al 31 ottobre 2026, chiusura il 1° novembre.
* Esame: netto positivo; ogni anno positivo; t almeno 3; Sharpe corretto per famiglie almeno 0,80; nessuna liquidazione; netto almeno 3% l'anno.

## Implementazione (file, commit)
* Dati: `research/programma7/centounesima_dati.py` (funding di Hyperliquid con `fundingHistory`, candele `candleSnapshot` 1d e 1h; archivio mensile
  di Binance: funding, candele giornaliere, prezzo mark a 1 ora; pausa adattiva fra le richieste; ripresa dai file scaricati). Dati in
  `research/data/centounesima/` (non committati). Impronte e conti dei file: `risultati_centounesima/impronte_dati.json`.
* Calcolo: `research/programma7/centounesima.py`. Deterministico (nessun seme). Commit dei registri: f87c200 (HEAD al momento del calcolo;
  i due script risultavano già committati e identici).
* Scarico: 213 monete con funding, candele giornaliere e orarie di Hyperliquid (migliaia di richieste a 500 righe per il funding, circa 6 ore con
  la pausa di 1,8 secondi; almeno 4 risposte «troppe richieste» contate nei passi successivi al primo); Binance 19.788 file scaricati e 7.050 mesi non esistenti (404, mesi prima
  della quotazione).

## Varianti provate
**2** (A e B), solo quelle scritte. Registro: `research/trials/centounesima.csv` (2 righe, esito «non passa» tutte e due). Nessuna variante fallita
o interrotta. I controlli descrittivi (solo Bitcoin ed Ether, prime 30 per volume e le altre, spese con ordine limite, senza la moneta
migliore) non sono varianti e non sono registrati come tali; stanno in `risultati_centounesima/esame.json`.

## Risultati
Universo e primo giorno utile di ogni moneta: `risultati_centounesima/universo.csv` (156 monete, 31 già ritirate da Hyperliquid incluse). Serie:
`giorni_A.csv.gz`, `giorni_B.csv.gz`, `settimane_A.csv.gz`, `settimane_B.csv.gz` (colonna `netto`, indice = giorno del lunedì, come le prove 157-162).
Rendimenti sul patrimonio del giorno; «periodo()» fa partire le settimane dal 26 giugno 2023 (A) e dal 12 giugno 2023 (B) e le ferma al 5 ottobre 2026.

| | A (30 giorni, 10%, mensile) | B (7 giorni, 20%, lunedì) |
|---|---|---|
| giorni / settimane dell'esame | 1.245 / 172 | 1.245 / 174 |
| netto annuo sul capitale | -9,27% | +1,77% |
| 2023 (da giugno) / 2024 / 2025 / 2026 (a ottobre) | +13,42% / +7,75% / -51,49% / +5,25% | +28,94% / +3,97% / -17,59% / +3,58% |
| funding lordo annuo (2023/24/25/26) | 11,0% (16,4/12,4/7,0/10,4) | 21,5% (36,1/16,6/20,1/19,2) |
| spese annue (2023/24/25/26) | 4,0% (2,9/4,7/4,1/3,8) | 11,8% (7,4/12,5/12,4/13,1) |
| prezzo (lordo senza funding) annuo | -16,2% (2025: -54,3%) | -8,0% (2025: -25,2%) |
| Sharpe settimanale / Sharpe 365 giorni | -0,35 / -0,35 | 0,06 / 0,05 |
| t settimanale | -0,64 | 0,12 |
| Sharpe corretto per famiglie (mazzo 285 serie, 199 famiglie, con A e B in `nuove`) | 0,00 | 0,00 |
| discesa massima (giornaliera / settimanale) | -55,2% / -55,2% | -55,1% / -54,7% |
| liquidazioni (massimo e minimo giornaliero / orario) | 2 / 0 (Binance, 11 luglio e 10 ottobre 2025) | 2 / 0 (Binance, 10 ottobre e 20 novembre 2025) |
| giorni a rischio (giornaliero / orario) | 2 / 0 | 2 / 0 |
| trasferimenti fra le borse (1 USDT ciascuno) | 65 | 93 |
| decisioni, ingressi, cambi di lato | 40, 628, 52 | 178, 1.239, 49 |
| monete in posizione, media | 28,7 | 14,5 |
| giorni fermi | 67 | 26 |
| esame | non passa (netto negativo, anni, t, Sharpe corretto, liquidazioni) | non passa (anni, t, Sharpe corretto, liquidazioni) |

Condizioni dell'esame: A: netto positivo no; ogni anno positivo no; t da 3 no; Sharpe corretto da 0,80 no; nessuna liquidazione no. B: netto positivo sì;
ogni anno positivo no; t da 3 no; Sharpe corretto da 0,80 no; nessuna liquidazione no; netto da 3% no (1,77%).

Il giorno delle liquidazioni pesa quasi tutto (giorni e perdite): A -18,2% (11 luglio 2025) e -43,1% (10 ottobre 2025); B -37,3% (10 ottobre 2025) e
-27,8% (20 novembre 2025). Descrizione, non variante: togliendo quei due giorni per variante il netto annuo sarebbe +8,7% (A) e +20,9% (B)
e il prezzo lordo +1,9% e +11,1%; ma il criterio scritto è «nessuna liquidazione» e quei giorni non si tolgono.

### Controlli descrittivi (non sono varianti; nessuno cambia l'esito)
Netto annuo / Sharpe settimanale / t / discesa giornaliera / liquidazioni / giorni a rischio / spese annue; anni 2023-2026:

| controllo | A | B |
|---|---|---|
| solo Bitcoin ed Ether | +2,55% / 2,15 / 3,91 / -1,4% / 0 / 0 / 1,05%; +4,3, +5,7, +0,5, 0,0 | +1,85% / 1,70 / 3,10 / -0,4% / 0 / 0 / 1,29%; +6,6, +2,4, +0,2, 0,0 |
| prime 30 per volume (Binance, 30 giorni prima) | -7,20% / -0,30 / -0,55 / -44,6% / 1 / 1 / 5,6%; +10,4, +10,1, -42,0, +1,6 | -1,37% / -0,07 / -0,14 / -33,7% / 2 / 7 / 10,9%; +26,1, +7,1, -34,0, +8,6 |
| le altre (fuori dalle prime 30) | -9,43% / -0,35 / -0,63 / -57,1% / 2 / 3 / 4,2%; +18,9, +5,0, -52,6, +5,6 | -0,33% / 0,00 / 0,01 / -58,1% / 2 / 3 / 12,3%; +29,8, +0,4, -21,3, +3,1 |
| spese con ordine limite (Binance 0,02%, Hyperliquid 0,015%, scarto invariato) | -8,34% / -0,32 / -0,58 / -54,8% / 2 / 2 / 3,1% | +6,12% / 0,19 / 0,35 / -54,0% / 2 / 2 / 7,4% (2025 ancora -12,9%) |
| senza la moneta migliore | senza MAVIA: -13,41% / -0,51 / -0,93 | senza MAVIA: -14,93% / -0,54 / -0,99 |
| correlazione con G1 (settimane comuni 171 e 173; giorni) | -0,20 (giorni -0,15) | -0,15 (giorni -0,09) |

Contributo alla somma dei guadagni in USDT: la moneta migliore è MAVIA (A +124 USDT, B +517 USDT su 1.000 di capitale: da sola più della metà del
netto positivo di B); poi kPEPE, FTM, DOGE, CFX (A) e FTM, MOVE, CFX, APE (B). Peggiori: A OMNI -107, HYPER -100, ZORA -40; B TNSR -156, ZORA -156, CAKE -101.

## Variante migliore e sua sensibilità alle varianti vicine
Per l'esame nessuna delle due è migliore: tutte e due non passano. La B ha il netto più alto (+1,77% contro -9,27%) ma con t 0,12 e 2025 a -17,6%.
Le varianti vicine non si sono provate (regola: solo A e B). Dai controlli descrittivi: le spese con ordine limite alzano la B a +6,1%
(il 2025 resta negativo) e lasciano la A negativa; senza la moneta migliore tutte e due diventano negative; solo Bitcoin ed Ether è l'unico
sottoinsieme senza liquidazioni.

## Anomalie e possibili errori di motore o dati
1. **Regola del rapporto dei prezzi il primo giorno comune (punto 9 della chiusura): taglia 57 monete su 213**, quasi tutte quotazioni recenti
   (ZRO 1,58; TIA 0,78; TON 1,20; BOME 2,19; TRUMP 2,53; WLFI 0,46; LIT 0,15; PENGU 0,65; ZK 0,64 ...). Il primo giorno comune è il giorno di quotazione,
   quando i due prezzi possono essere molto diversi: non è un errore di scala (come il caso 1000x che la regola voleva prendere), quindi la
   regola scritta esclude monete valide. L'ho applicata come scritta. Elenco intero con i rapporti: `esame.json` campo `esclusi`.
2. **Le liquidazioni vengono tutte dal metodo giornaliero** (massimo e minimo di ogni moneta nello stesso istante, più severo di quello orario;
   Hyperliquid prima del 26 aprile 2026 non dà le candele orarie). Nei giorni delle liquidazioni la perdita è realizzata al prezzo estremo
   del giorno sulla gamba liquidata mentre l'altra gamba, coperta, si chiude all'apertura dopo (prezzi tornati vicino): il prezzo non si
   compensa, ed è la fonte quasi intera della perdita (10 ottobre 2025: il minimo del giorno è circa -60% su molte monete, l'apertura dopo circa -25/-30%: la gamba
   coperta guadagna meno di quanto la gamba liquidata ha perso).
   Per il solo periodo con candele orarie (dal 26 aprile 2026 al 31 ottobre) zero liquidazioni e zero giorni a rischio.
3. **Ultimo giorno**: il file mensile di Binance di novembre non esiste; l'apertura del 1° novembre è la chiusura del 31 ottobre (Binance e
   Hyperliquid); il pagamento del funding delle 00:00 del 1° novembre non è contato né per Binance né per Hyperliquid (lettura 8).
4. Buchi di prezzo con posizione aperta: 10 chiusure forzate in A (STRAX 16 marzo 2024, FTM 13 gennaio 2025, ILV, RDNT, OMNI, OM ...) e 7 in B
   (FTM, RDNT, OMNI, OM, MAVIA 6 maggio 2026, ZEREBRO 6 maggio 2026 ...): chiusi all'ultimo prezzo con le spese, come scritto.
5. MAVIA: contributo molto grande (B +517 USDT su 1.000): un evento singolo (probabile squilibrio di prezzo fra le due borse), non verificato; vale
   il controllo «senza la moneta migliore».
6. Le serie settimanali di `periodo()` finiscono il 5 ottobre 2026 (limite del metodo): le ultime 4 settimane di ottobre contano per il netto annuo
   e gli anni, non per Sharpe e t.
7. Lo scarico del funding di Hyperliquid è durato circa 6 ore (nessun seme dallo storico di prima: la cache della prova 73 non c'era); il limite di richieste ha imposto una pausa adattiva.

## Varianti non previste che proporrei (non eseguite)
* Universo con il rapporto dei prezzi calcolato non il primo giorno comune ma, per esempio, il primo giorno con 30 giorni di dati (la regola attuale esclude
  57 monete valide; vedi anomalia 1).
* Margine controllato sempre con la candela oraria (non disponibile per Hyperliquid prima del 26 aprile 2026: servirebbe un'altra fonte di prezzi).
* Solo le monete più grandi (Bitcoin ed Ether come unica scelta con soglia più bassa) per evitare le liquidazioni: nei controlli rende 1,9-2,6% l'anno, sotto il 3%.
* Margine con più di metà del capitale su Binance, o leva minore (capitale doppio rispetto alle gambe).

## Domande aperte
1. La regola del punto 9 (rapporto dei prezzi il primo giorno comune fra 0,9 e 1,1) doveva escludere le monete quotate da poco? Come scritta ne taglia 57.
2. La perdita sulla gamba liquidata va presa al prezzo estremo del giorno (come scritto, «lato peggiore») e la gamba coperta si chiude all'apertura dopo: è
   l'intenzione? Con il minimo giornaliero questo rende le liquidazioni di ottobre 2025 molto più costose di una liquidazione vera.
3. Il funding delle 00:00 del 1° novembre non è nei dati di Binance (file di novembre assente) e non l'ho contato nemmeno per Hyperliquid: va bene?

## Letture delle regole che ho dovuto scegliere
1. Trasferimento: importo = scarto del margine di una borsa dalla metà del totale (comprese le somme già in viaggio); parte dalla borsa più ricca, costo di 1 USDT tolto
   da quella borsa, arriva alla 00:00 del giorno dopo; soglia = 10% del patrimonio del momento (non solo 1.000 USDT iniziali); il trasferimento si fa ogni giorno
   (anche senza posizioni) se lo scarto supera la soglia.
2. «Una liquidazione di una gamba»: con il margine per borsa (conto unico per tutte le gambe della borsa) sono liquidate tutte le gambe di quella borsa; le gambe
   dell'altra borsa si chiudono alla 00:00 successiva e le monete restano ferme fino alla decisione dopo (se la 00:00 successiva è una decisione, la moneta può rientrare in quella).
3. Liquidazione: chiusura al prezzo peggiore del passo (giorno o ora) con la perdita del 1% del valore della gamba; nessuna commissione in più.
4. Ordine nel giorno: le spese si pagano alla decisione (apertura), il margine si controlla dopo; il funding entra a fine giorno prima del 26 aprile 2026
   (somma dei pagamenti del giorno) e ora per ora dopo; il rendimento del giorno è la variazione del patrimonio fra due aperture diviso il patrimonio dell'apertura.
5. Margine = deposito + guadagni (anche non realizzati) al prezzo peggiore + funding − spese; i guadagni non realizzati usano per Binance il prezzo mark rapportato
   all'apertura scambiata (approssimazione) e per Hyperliquid il prezzo scambiato; funding = quota fissa della gamba × tasso (come in G1).
6. Dopo le 00:00 del 26 aprile 2026 il controllo orario usa il massimo (gamba corta) e il minimo (gamba lunga) di ogni candela oraria, non l'apertura o la chiusura
   (più severo); i buchi orari ripiegano sul massimo e minimo del giorno.
7. «Almeno 30 giorni interi» per l'universo: 30 giorni validi (funding e prezzi su tutte e due) strettamente prima della decisione, anche non consecutivi; la
   finestra L deve avere tutti i giorni validi; vale per A e B.
8. Funding dell'ultimo giorno: i pagamenti con orario dal 1° novembre 00:00 non esistono per Binance, quindi non ho contato né quello di Binance né quello di Hyperliquid.
9. Rapporto dei prezzi dell'abbinamento calcolato sull'apertura del primo giorno comune (non sulla chiusura).
10. Costo di chiusura del 1° novembre sommato al 31 ottobre; la serie finisce il 31 ottobre.
11. Con ordine limite: Binance 0,02% (come il resto del repo), Hyperliquid 0,015% (tabella pubblica), scarto invariato.
12. Prime 30 per volume: volume in USDT medio giornaliero su Binance nei 30 giorni prima, calcolato a ogni decisione; «le altre» = le monete non fra le prime 30 a quella data.
13. Rebalance alla decisione: la gamba che continua nello stesso verso paga solo la differenza di valore (valore corrente contro nuova quota) su ciascuna borsa; il pagamento
   per variazione di quota e la nuova quota usano il patrimonio prima delle spese di quel giorno.
