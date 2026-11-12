# Prova 153 — il libro degli ordini fra le monete, deciso ogni giorno come G1 (idea 139)

Regole scritte il 12 novembre 2026 (giro delle 08:17) dallo strategy-scout, **prima di ogni calcolo**: nessun risultato è stato guardato
(solo un controllo di esistenza dei file). La prova la esegue strategy-researcher, il giudizio lo dà backtest-auditor. Il numero 153 è
libero (ultima nel registro: 152). Non spegne e non sostituisce niente.

## Il perché forte
* **Dato usato poco e mai così.** Il libro degli ordini (archivio `bookDepth` di Binance: ogni 30 secondi il valore in USDT degli ordini
  fermi entro l'1, 2, 3, 4 e 5% sopra e sotto il prezzo) è stato provato solo nel programma 5, fase 4 (`programma5/REGOLE.md` sezione 10,
  `STATO.md`): **24 monete, a ore, nel tempo** (E-201, nessuna promossa; il libro sottile in salita dava +10,9% in 12 ore su 24 casi).
  Mai **fra le monete, ogni giorno, su 100 monete, con il metodo di G1** (`--cerca libro`, `--cerca profondità`, `--cerca bookDepth`:
  nessuna prova del registro). Non è un indicatore sul prezzo: dice dove aspettano i compratori e i venditori grandi.
* **Ragione economica**: gli ordini fermi lontani dal prezzo (fino al 5%) sono di chi ha un'opinione o deve comprare o vendere molto
  senza muovere il prezzo; se quasi tutto il denaro in attesa è dal lato dei compratori, c'è un assorbimento di vendite che il prezzo
  ancora non mostra. Fonti: Cao, Hansch e Wang, «The information content of an open limit order book», *Journal of Futures Markets*
  2009 (la parte del libro lontana dal prezzo prevede i rendimenti brevi); Cont, Kukanov e Stoikov, «The price impact of order book
  events», *Journal of Financial Econometrics* 2014 (lo squilibrio spiega il prezzo, ma a orizzonti di secondi e minuti).
  **Avviso onesto**: gli studi sono su azioni e a orizzonti brevi; a un giorno sui perpetui crypto il verso non è un fatto, è una
  scommessa; i grandi ordini fermi possono anche essere esche che spariscono (il verso potrebbe essere il contrario). Il verso è
  fissato qui sotto e **non si rovescia dopo aver visto i risultati**.
* **Cosa cerca di aggiungere**: G1 usa il funding (chi paga per essere affollato); questo segnale misura l'affollamento dei soli ordini
  fermi, un'altra cosa, calcolata sulle stesse 100 monete con lo stesso motore. Si guarda anche la correlazione con G1 (vedi sotto).

## Dati e universo
* Archivio pubblico gratuito `https://data.binance.vision/data/futures/um/daily/bookDepth/<SIMBOLO>/<SIMBOLO>-bookDepth-<AAAA-MM-GG>.zip`
  (con il file CHECKSUM accanto), colonne `timestamp, percentage, depth, notional`, livelli ±1..5%, circa 2.880 rilevazioni al giorno.
  **Periodo disponibile: dal 2 gennaio 2023** (il file del 31 dicembre 2022 non esiste; verificati il 2 gennaio 2023, il 1 giugno 2023,
  il 1 giugno 2024 e il 1 novembre 2026). Il riassunto giornaliero si tiene con lo strumento di `programma5/strumenti/libro.py`
  (misure a ore, impronte in `libro_impronte.json`); i file grezzi non si tengono.
* Universo, calendario e motore: quelli di G1 (`PRIMA.md`, `revisione_g1n/nucleo.py`, `nucleo.universo_giorni`: le 100 monete più
  scambiate, fissate ogni settimana). Si scaricano solo i file delle monete dell'universo di ogni settimana (stima: decine di migliaia
  di file da circa 0,5 MB; se non basta il tempo, lo si scrive e si riduce lo scarico alle 60 monete più scambiate **per tutta la
  prova**, dichiarandolo, non a pezzi). Giorni o monete con meno di 2.000 rilevazioni: la moneta quel giorno non si prova.

## Il segnale (fissato qui)
Ogni giorno D alle 00:00 UTC, per ogni moneta, con i dati del giorno D−1 (00:00-24:00 UTC, noti alla fine del giorno):
S = media delle rilevazioni di (acquisti − vendite) / (acquisti + vendite), dove acquisti = notional del lato sotto il prezzo e vendite
= quello sopra, entro il 5% (variante A) o entro l'1% (variante B). **Long il quinto con S più alto, short il quinto con S più basso**,
banda 20%/40%, pesi secondo l'inverso della volatilità a 30 giorni, ogni lato al 100% (esposizione 2): **come G1** (stessa funzione,
cambia solo il segnale).

## Esecuzione e costi
Ordine all'apertura della barra delle 00:00 UTC (dopo il segnale), limite per un'ora e poi a mercato; costi confermati dal proprietario:
0,05% a mercato, 0,02% con ordine limite, scarto di prezzo 0,01% su BTC, ETH e SOL e 0,02% sulle altre, funding vero, come G1.
Periodo: dal 2 gennaio 2023 (più 30 giorni per la volatilità) al 4 ottobre 2026 (fine di G1, `an.FINE`).

## Varianti (fissate, al massimo 2)
A: squilibrio entro il 5%. B: squilibrio entro l'1% (vicino al prezzo, più dei piccoli che dei grandi). Nessun altro valore, nessuna
variante dopo i risultati. Conta **2 prove** (un'unica famiglia con G1 solo se la correlazione dei rendimenti giornalieri supera il
`TAGLIO` di `programma6/asticella.py`; altrimenti famiglia nuova): conto di 312 a 314 prima dell'esame. **Controlli obbligatori,
descrittivi, non varianti**: il segnale al contrario (per sapere se il verso è sbagliato, **non** per sceglierlo); la correlazione con G1
e con F5; il rendimento per anno e per lato.

## L'esame (regole approvate dal proprietario il 9 novembre)
Passa se: netto dopo i costi positivo; **ogni anno positivo** (2023, 2024, 2025, 2026; il 2023 e il 2026 sono anni parziali: si segnano);
t almeno 3; Sharpe corretto almeno 0,80 con il conto per famiglie (`programma6/asticella.py`, esempio `audits/repro/prova28_2026-11-11.py`
voce 11). Non passa se il lato long o il lato short da soli fanno meno di zero senza i 10 giorni migliori. **Limite onesto**: 3,75
anni di storia; con il conto delle famiglie l'asticella è alta, il verdetto «dati troppo corti» è possibile e si scrive come tale.
Se passa: backtest-auditor, poi la sessione principale decide il paper; demo e soldi veri solo con l'ok del proprietario.

## Cosa si consegna
`RISULTATI_NOVANTUNESIMA.md` (giorni e monete usati, file scaricati e mancanti, rendimento netto l'anno, Sharpe, t, Sharpe corretto,
lato long e short, correlazione con G1 e F5, controllo al contrario, giro e spese), codice `novantunesima.py`, le varianti in
`research/trials/`, le impronte dei file. Se mancano i dati per un periodo lungo: lo si scrive e non si inventa.
