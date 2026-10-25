# Programma 7 — ventiseiesima prova: G1 neutra al mercato (G1N)

Scritto il 25 ottobre 2026, alle 06:20 UTC, **prima di qualunque calcolo**. Idea 50 della coda di `research/REGISTRO.md`. Vale
`PRIMA.md` (G1) e `VENTIQUATTRESIMA.md` (F5N) dove qui non si dice altro.

## 1. Perché

G1 è la strategia sul conto demo di Binance e la candidata ai soldi veri (`docs/backlog.md`, P26). Su F5 la neutralità al beta
(prova 86) ha tagliato le perdite nelle 15 settimane peggiori da −7,9% a −5,9% a costo di 3 punti l'anno, e il merito era della
neutralità e non del peso del lato long (il 120/80 faceva peggio). Con soldi veri la discesa massima conta più del rendimento medio:
serve sapere se succede lo stesso a G1, che decide ogni giorno. **La riserva**: è una variante vista (di F5N); G1 e F5 hanno
correlazione 0,80, quindi è probabile che il risultato sia lo stesso.

## 2. La regola (valori fissati qui)

* Segnale, universo del giorno, banda 20/40 e pesi 1/volatilità: **identici a G1** (`prima.py`), decisione ogni giorno alle 00:00.
* **Beta di ogni moneta, ricalcolato ogni giorno**: la pendenza dei rendimenti giornalieri sulla media giornaliera dell'universo del
  giorno, sui **90 giorni** prima (almeno 45); 1 dove manca (`ventiquattresima.beta_delle_monete`, applicata ai giorni).
* **Scalatura dei lati** come F5N: long × a = 2·βS/(βL+βS), short × b = 2·βL/(βL+βS), a e b fra 0,5 e 1,5, esposizione lorda al 200%.
* Esecuzione con gli ordini limite come G1 (`cinquantaseiesima.spese_a_limite`), funding vero; dal 4 gennaio 2021 al 5 ottobre 2026.
* Due serie nel conto: **G1N** e il **peso fisso 120/80** (controllo): nel conto diventano **156**.

## 3. L'esame

Come G1: le settimane dal conto giornaliero, `terza.esame` dal 4 gennaio 2021, Sharpe corretto con l'aggiunta e il t, la decisione
del proprietario del 24 ottobre; confronto con G1 sulle stesse settimane (Sharpe 1,96 con gli ordini limite), le 15 settimane peggiori
di G1 rifatte con G1N, βL e βS medi, a e b medi, spese.
