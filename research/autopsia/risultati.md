# Autopsia delle strategie vecchie: i risultati

Calcolati il 18 ottobre 2026 dalle 14:07 alle 14:10 UTC, dopo le regole (`regole.md`, commit `7dbb624e` delle 14:05).
Python 3.11.17 e numpy 1.26.4 (non le versioni delle sessioni di ricerca: per misure descrittive non conta). Script:
`autopsia.py` (misure 1-6) e `aggiunte.py` (due analisi aggiunte dopo i primi numeri, dichiarate sotto). Numeri:
`riepilogo.json` e `aggiunte.json`. Il file dei trade (`varianti.jsonl`, 110 MB) non è nel repository: lo rifà
`python3 -m research.autopsia.autopsia varianti` in circa due minuti, con lo stesso seme.

**I dati**: 73 varianti delle ricerche su BTC (41) e su LINK (32), rieseguite sul solo periodo di costruzione
(gennaio 2020 - settembre 2022), con gli stessi risultati dei log (controllo: BTC V-004 176 trade e −0,06 R, LINK V-004 174
trade e +0,128 R, come in `research/campagne/*/log.jsonl`); **19.429 trade** delle strategie e **388.580 trade a caso**
(20 simulazioni per variante, stesse uscite, stessa larghezza di stop, stessi costi). Più i 668 trade del paper sulle
coppie validate (586 con tutti i campi necessari).

## In una pagina

| Domanda | Strategie | A caso | Differenza (intervallo al 95%) | Cosa vuol dire |
|---|---|---|---|---|
| 1. Il prezzo va subito contro? | 46,3% | 49,7% | −3,4 punti (−4,6; −2,2) | le strategie indovinano la direzione **un poco** meglio del caso |
| 2. Entriamo dopo che il prezzo si è già mosso? (4 candele prima, in R) | +0,38 R | −0,02 R | +0,40 (+0,23; +0,56) | sì, entriamo in ritardo; ma vedi sotto: non è questo che fa perdere |
| 3. Restituiamo il guadagno? (trade che toccano +1 R) | 61% restituito | 61% | 0,0 | **no**: le uscite fanno quello che farebbero su trade a caso |
| 4. Lo stop ci butta fuori e poi il prezzo va dalla nostra parte? | 13,7% | 13,4% | +0,1 punti (−1,6; +2,2) | **no**: gli stop non sono troppo stretti rispetto al caso |
| 5. Quanto costano? | 0,059 R a trade | 0,058 R | 0,0 | come il caso |
| Risultato dopo i costi | +0,002 R | −0,037 R | +0,039 (+0,018; +0,060) | un vantaggio vero sul caso, ma di 4 centesimi di R: meno di quanto serve |

**La volatilità** (domanda 6), per fasce dalla più calma (Q1) alla più agitata (Q5) delle 24 candele prima del segnale:

| Fascia | Costo in R | Strategie, R dopo i costi | A caso | Differenza (intervallo al 95%) |
|---|---|---|---|---|
| Q1 calma | 0,087 | +0,055 | −0,033 | **+0,088** (+0,030; +0,147) |
| Q2 | 0,063 | −0,014 | −0,060 | +0,045 (+0,001; +0,091) |
| Q3 | 0,062 | +0,016 | −0,017 | +0,033 (−0,018; +0,086) |
| Q4 | 0,044 | −0,000 | −0,043 | +0,043 (+0,006; +0,081) |
| Q5 agitata | **0,031** | −0,066 | −0,050 | **−0,015** (−0,057; +0,023) |

## Cosa abbiamo capito

1. **Uscite, stop e trailing non sono il problema.** Su 19.429 trade restituiscono il guadagno e prendono gli stop
   esattamente come trade a caso con le stesse uscite (domande 3 e 4). Cambiarli non crea un vantaggio: lo diceva già
   l'analisi del paper del 12 ottobre (`docs/analisi_trade_16set_12ott.md`), ora lo dicono anche le ricerche.
2. **Le strategie hanno un po' di direzione, ma poca.** Vanno subito contro il 46% delle volte invece del 50%, e fanno
   0,04 R a trade più del caso (su BTC 0,07, su LINK zero). È un vantaggio vero, ma più piccolo dei costi più il margine
   che l'esame chiede.
3. **Entriamo in ritardo, ma il ritardo non è il problema.** Le strategie entrano dopo un movimento di +0,38 R nella loro
   direzione (il caso quasi zero), e i trade entrati dopo un movimento più grande vanno **meglio**, non peggio: terzo con
   il movimento più grande −0,029 → +0,061 R per le strategie, −0,055 → +0,031 per il caso (analisi aggiunta 1). Nel
   2020-2022, su BTC e LINK, un movimento di poche candele tendeva a continuare: è una proprietà del mercato, che anche il
   caso incassa.
4. **La volatilità taglia i costi**, come pensa il proprietario: da 0,087 R a trade nella fascia più calma a 0,031 nella
   più agitata, quasi tre volte meno. Nel paper ancora di più: da 0,155 a 0,038 R (analisi aggiunta 2).
5. **Ma le strategie vecchie perdono il loro piccolo vantaggio proprio quando il prezzo si muove tanto.** Battono il caso
   nella calma (+0,088 R) e non nella fascia più agitata (−0,015; su LINK −0,062, sotto zero anche l'intervallo). Nei
   momenti agitati perde anche il caso prima dei costi (−0,019 R). Le regole del catalogo sono pensate per un mercato
   normale: nei momenti di forte volatilità servono regole diverse, fatte apposta.

**Per costruire strategie migliori, in breve:** cercare nei momenti di forte volatilità, dove i costi pesano tre volte
meno; con ingressi pensati per quei momenti, perché quelli vecchi lì non funzionano; senza perdere tempo sulle uscite.

## Le due analisi aggiunte dopo i primi numeri (dichiarate)

Le regole non le prevedevano; le ho aggiunte dopo aver visto la tabella, quindi valgono come indicazioni.

1. **Il ritardo costa?** Per ogni variante, i suoi trade divisi in tre parti per il movimento delle 4 candele prima del
   segnale (stessi tagli per il caso). R dopo i costi, media sulle varianti: strategie −0,029 / −0,027 / +0,061; caso
   −0,055 / −0,037 / +0,031. Differenza fra il terzo alto e il basso: strategie +0,091 (+0,035; +0,149), caso +0,087
   (+0,057; +0,116). `aggiunte.json`, «ritardo».
2. **Il paper** (586 trade delle coppie validate con i campi necessari, esplorativi esclusi): R dopo i costi −0,110,
   prima −0,019, costo 0,088 (come `ops/results/0622`); tocca +1 R il 33% dei trade, e nessuno di questi chiude sotto zero
   prima dei costi (il break-even dopo il primo gradino); per fasce di ATR all'ingresso (dal più calmo al più agitato,
   circa 110 trade ciascuna): costo 0,155 / 0,110 / 0,079 / 0,058 / 0,038 R; R dopo i costi −0,187 / −0,190 / +0,024 /
   −0,156 / −0,025, con circa ±0,1 R di incertezza per fascia (stima). `aggiunte.json`, «paper».

## Limiti

* Due monete, un periodo (2020-2022, un rialzo e un ribasso), e le regole del catalogo da 30 minuti a 4 ore: lo scalping
  a 1-15 minuti non è ancora guardato.
* Le fasce di volatilità per i primi 60 giorni di dati non si calcolano (dettaglio che le regole non fissavano: con meno
  di 365 giorni di storia si usa quella disponibile, almeno 60 giorni).
* Questi dati, ora, sono «già visti» da chi progetterà le strategie nuove: le idee che ne escono si confermano solo su
  dati che arrivano dopo.
