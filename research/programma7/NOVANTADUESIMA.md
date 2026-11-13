# Prova 154 — la dimensione media dello scambio fra le monete, decisa ogni giorno come G1 (idea 140)

Regole scritte il 13 novembre 2026 (giro delle 00:17) dallo strategy-scout, **prima di ogni calcolo**: nessun risultato guardato. La prova
la esegue strategy-researcher, il giudizio lo dà backtest-auditor. Il numero 154 è libero (ultima nel registro: 153). Non spegne e non
sostituisce niente.

## Il perché forte
* **Dato mai usato.** Le candele di Binance hanno una colonna con il **numero di scambi** (`count`, vedi `research/src/dati.py`):
  nel registro e nel programma 9 (28 ingredienti, `programma9/METODO.md`) non c'è mai stata (`--cerca scambi`, `numero di`, `dimensione
  media`, `impatto`: nessuna prova su questo; la prova 101 usa il volume del perpetuo su quello a pronti, un'altra cosa). Valore in
  dollari diviso numero di scambi = **dimensione media dello scambio**: dice chi sta scambiando (tanti scambi piccoli = piccoli
  risparmiatori, pochi scambi grossi = grandi conti e algoritmi), non solo quanto.
* **Ragione economica**: i piccoli risparmiatori comprano ciò che attira l'attenzione e pagano di più (domanda da lotteria); i grandi
  conti sono più informati. Fonti: Barber, Odean e Zhu, «Do retail trades move markets?», *Review of Financial Studies* 2009 (gli scambi
  dei piccoli sono correlati fra loro e spostano i prezzi); Boehmer, Jones, Zhang e Zhang, «Tracking retail investor activity»,
  *Journal of Finance* 2021 (le azioni con più acquisti dei piccoli rendono meno nelle settimane dopo); Lee e Radhakrishna, *Journal of
  Financial Markets* 2000 (la dimensione dello scambio separa piccoli e grandi). **Avviso onesto**: studi su azioni; sulle crypto la
  dimensione dello scambio è sporca (algoritmi che spezzano gli ordini, prezzo in dollari diverso per moneta): per questo si usa il
  **cambio rispetto alla storia della moneta stessa**, non il livello. Il verso è fissato sotto e **non si rovescia dopo i risultati**.
* **Cosa aggiunge**: G1 misura chi paga per essere affollato (funding); questo misura **chi** sta scambiando. Si guarda la correlazione
  con G1 e F5.

## Dati e universo
* `https://data.binance.vision/data/futures/um/monthly/klines/<SIMBOLO>/1d/<SIMBOLO>-1d-<AAAA-MM>.zip` (con CHECKSUM), colonne
  `quote_volume` e `count`. Gratis. Stima: 100 monete × circa 46 mesi = al massimo 4.600 file da pochi KB (minuti). Periodo: dal 2022
  (come G1: serve la storia di 30 giorni prima). Se le candele già in locale hanno `count`, si usano quelle (nessun scarico).
* Universo, calendario, motore: quelli di G1 (`revisione_g1n/nucleo.py`, `nucleo.universo_giorni`). Moneta-giorno senza `count` o con meno
  di 100 scambi: non ha segnale ed esce dalla classifica del giorno.

## Il segnale (fissato qui)
D = quote_volume / count del giorno (dollari per scambio). Ogni giorno D alle 00:00 UTC, con i dati fino alla fine del giorno D−1:
S = media di D negli ultimi 3 giorni / media di D negli ultimi 30 giorni (variante A) oppure negli ultimi 7 / ultimi 90 (variante B).
**Long il quinto con S più alto** (arrivano scambi più grandi = grandi conti), **short il quinto con S più basso** (arrivano piccoli
risparmiatori), banda 20%/40%, pesi secondo l'inverso della volatilità a 30 giorni, esposizione 2: **come G1** (stessa funzione,
cambia solo il segnale; senza il fattore beta).

## Esecuzione e costi
Ordine all'apertura della barra delle 00:00 UTC dopo il segnale, limite per un'ora e poi a mercato; costi del proprietario: 0,05% a
mercato, 0,02% con ordine limite, scarto 0,01% su BTC, ETH e SOL e 0,02% sulle altre, funding vero. Periodo: dal 1° gennaio 2022 (più
90 giorni di storia) al 4 ottobre 2026 (`an.FINE`).

## Varianti (fissate, al massimo 2)
A: 3 giorni su 30. B: 7 giorni su 90. Nessun'altra, nessuna dopo i risultati. Contano **2 prove** (314 → 316; una sola famiglia con G1
solo se la correlazione dei rendimenti supera il `TAGLIO` di `programma6/asticella.py`). **Controlli descrittivi, non varianti**: il
segnale al contrario (solo per capire il verso, non per sceglierlo); correlazione con G1 e F5; rendimento per anno e per lato.

## L'esame (regole approvate dal proprietario il 9 novembre; conto del 12 novembre)
Passa se: netto dopo i costi positivo; **ogni anno positivo** (2022, 2023, 2024, 2025, 2026 parziale); t almeno 3; **Sharpe corretto
almeno 0,80 con `asticella.corretto_famiglie`** (mazzo completo, `programma6/MAZZO_ASTICELLA.md`; con 314 prove e 191 famiglie
l'asticella è alta: dirlo nei risultati, non toccarla). Non passa se il lato long o quello short da soli fanno meno di zero senza i 10
giorni migliori. Se passa: backtest-auditor, poi la sessione principale decide il paper.

## Cosa si consegna
`RISULTATI_NOVANTADUESIMA.md` (file scaricati e mancanti, giorni e monete, rendimento netto per anno e lato, Sharpe, t, Sharpe corretto
per famiglie, correlazione con G1 e F5, controllo al contrario, giro e spese), `novantaduesima.py`, le varianti in `research/trials/`.

## Regole corrette il 13 novembre 2026 dopo la verifica, prima di ogni calcolo (sessione principale)
La verifica di strategy-researcher ha trovato 9 punti da chiudere; nessun segnale è stato calcolato. Le letture che valgono:
1. **`count`**: i caricatori ufficiali lo scartano; il ricercatore scrive un lettore di `count` dentro `novantaduesima.py`, sugli stessi
   file e con le stesse regole di `seconda.candele` (`research/data/p6g/<SIMBOLO>/giorni/`, l'archivio vince, gli stessi giorni
   dall'interfaccia pubblica); i caricatori ufficiali non si toccano. Si controlla su 3 monete che volume e chiusura letti dal lettore
   nuovo coincidano con quelli di `seconda.candele`.
2. Un giorno con `count` mancante o zero è un giorno senza dato.
3. **Finestre**: media dei giorni validi nella finestra; la moneta ha segnale solo se almeno metà dei giorni di ciascuna finestra è
   valida (A: 2 su 3 e 15 su 30; B: 4 su 7 e 45 su 90).
4. **Periodo**: primo giorno di conto il 1° gennaio 2022, con la storia presa dal 2021; nessun segnale prima che la finestra lunga
   abbia i suoi giorni validi.
5. **Universo e quinti**: le monete dell'universo settimanale di G1 che hanno anche il segnale; i quinti si contano su quelle; sotto
   `MIN_MONETE` (20) il giorno resta senza posizioni.
6. **Pesi**: il ciclo di `nucleo.pesi` si ricopia nel file della prova cambiando solo il segnale (`ct = S` al posto di `-funding7`);
   inverso della volatilità a 30 giorni, banda, `W` (non `WN`) ed esposizione come G1.
7. **Verso**: `ct = S`, cioè long le monete con lo scambio medio cresciuto di più, short quelle con lo scambio medio sceso di più.
8. **Esecuzione e periodo**: `nucleo.spese_limite` come G1 (`oltre` 0); fine `an.FINE` esclusa (ultimo giorno il 4 ottobre 2026); il
   2026 parziale conta come anno per «ogni anno positivo».
9. **Esame**: serie settimanali nette (`asticella.settimanale`), statistiche con `nucleo.numeri(per_anno=52)`; A e B entrano insieme
   come prove nuove in `asticella.corretto_famiglie`; una variante passa se lei sola rispetta tutte le condizioni; il conto delle prove
   resta 314 → 316. Correlazioni con G1 e F5 dalle serie del mazzo (`MAZZO_ASTICELLA.md`).
