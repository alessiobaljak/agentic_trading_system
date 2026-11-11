# Prova 150 — l'asimmetria dei rendimenti: vendere le monete «a lotteria», comprare quelle con le cadute improvvise (idea 143)

Regole scritte l'11 novembre 2026, **prima di ogni calcolo**, dallo strategy-scout; la prova la esegue strategy-researcher, il
giudizio lo dà backtest-auditor. Nessun risultato è stato guardato.

## Il perché forte
* **Dato mai usato**: le candele da 1 minuto (17 GB) sono state usate per gli ingressi in giornata, mai per misurare la *forma* dei
  rendimenti dentro il giorno. Controllo nel registro: `--cerca asimmetria`, `--cerca lotteria` (solo la prova 9, G2, sul giorno
  migliore del mese), `--cerca salto`: nessuna prova sull'asimmetria calcolata dai minuti.
* **Studio serio**: Amaya, Christoffersen, Jacobs e Vasquez, *Journal of Financial Economics* 2015: l'asimmetria realizzata della
  settimana (calcolata da rendimenti intraday) predice al contrario i rendimenti della settimana dopo (i titoli con salite improvvise
  rendono meno, quelli con cadute improvvise rendono di più). Ragione economica (Kumar, *Journal of Finance* 2009; Bali, Cakici e
  Whitelaw 2011): il pubblico al dettaglio paga troppo i biglietti della lotteria. Avviso: è un fattore pubblicato su dati di azioni;
  sulle crypto non so di una conferma solida sui perpetui, e potrebbe essere in gran parte il funding di G1 con un altro nome.
  La prova serve anche a saperlo: si riporta la correlazione col segnale di G1.
* Differenza dalle prove già chiuse: il giorno migliore (idea 116/G2) usa un solo numero del giorno; la volatilità e il beta
  (prove 52 e 124) usano la grandezza, non il segno dei salti; qui conta la terza potenza dei rendimenti da 5 minuti.

## Dati e universo
Candele da 1 minuto dei perpetui di Binance, rese a 5 minuti (ultima chiusura di ogni blocco di 5); le 100 monete più scambiate della
settimana, come G1 (`programma7/PRIMA.md`); funding vero.

## Il segnale (fissato qui)
Ogni giorno alle 00:00 UTC, per ogni moneta, con i 7 giorni prima (fino alle 00:00 escluse):
RS = radice(n) × somma(r³) / (somma(r²))^1,5, con r il rendimento logaritmico a 5 minuti e n il numero dei blocchi.
Si ordinano le monete: **long il quinto con RS più basso, short il quinto con RS più alto**. Banda 20%/40%, pesi secondo l'inverso
della volatilità dei 30 giorni prima, ogni lato al 100%: tutto come G1, cambia solo il segnale.

## Esecuzione e costi
Ordine all'apertura della barra dopo il segnale (00:00 stessa mezzanotte: il segnale usa solo dati fino alla mezzanotte). Come G1:
ordine limite 0,02% valido un'ora, poi a mercato (0,05%) all'apertura delle 01:00; si riporta anche tutto a mercato. Scarto di
prezzo 0,01% su BTC, ETH e SOL e 0,02% sulle altre; funding vero. Monete senza almeno 5 giorni di minuti completi nella finestra:
fuori dall'universo del giorno.

## Periodo e varianti
Dal 4 gennaio 2021 al 31 ottobre 2026, anno per anno. **Due varianti**, sole, scelte prima: finestra di 7 giorni (principale, come
Amaya e coautori) e finestra di 30 giorni (controllo: se l'effetto è vero deve esserci anche con meno rumore). Conta **2 prove**
nel conto (da 306 a 308 dopo la 149, o dal valore aggiornato dalla sessione principale). Nessun'altra variante dopo aver visto i
risultati: una nuova è una prova nuova.

## L'esame (regole approvate dal proprietario il 9 novembre)
Passa se: netto dopo i costi positivo; ogni anno positivo; t almeno 3; Sharpe corretto almeno 0,80 (con il conto aggiornato). Se
passa, va a backtest-auditor. Controlli obbligatori da riportare: correlazione dei rendimenti giornalieri con G1 e correlazione dei
due segnali (rango) nelle 100 monete; il risultato di una miscela 50/50 con G1 sugli stessi giorni (solo informativo); giro e spese
l'anno; lato long e lato short separati.

## Cosa si consegna
`RISULTATI_OTTANTOTTESIMA.md` (tabella delle 2 varianti: rendimento l'anno, Sharpe, anni positivi, t, Sharpe corretto, giro, spese,
correlazioni), codice `ottantottesima.py`, ogni variante in `research/trials/`.
