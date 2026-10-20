# Programma 6 — ventiseiesima prova: il funding che tocca il tetto (E3, E4)

Scritto il 20 ottobre 2026, mezzogiorno, **prima di qualunque calcolo sui prezzi** (contati solo gli eventi e il segno del
funding dai file del funding). Idea 9 della coda di `research/REGISTRO.md`.

## 1. Perché

* Binance accorcia l'intervallo del funding di una moneta (da 8 a 4 o 1 ora) quando il funding tocca il limite: è il segno
  di un affollamento estremo da una parte. Dai file del funding (il cambio della colonna dell'intervallo), sulle monete del
  pannello: **356** passaggi a un intervallo più corto; con il funding **negativo** al passaggio (gli short pagano) **279**
  (1 nel 2021, 4 nel 2022, 21 nel 2023, 6 nel 2024, 114 nel 2025, 133 nel 2026), **positivo** 63 (24 nel 2023, 18 nel 2024,
  15 nel 2025, 6 nel 2026), zero 14.
* F3 e F5 dicono che fra monete chi paga il funding perde e chi lo riceve guadagna. Qui lo stesso all'estremo, come evento:
  * **E3**: funding negativo al passaggio (short affollati, pagano molto): **long la moneta**. In più il lato long ha la
    coda a favore (le salite improvvise degli short costretti a chiudere, che nelle prove 18 e 21 uccidevano lo short).
  * **E4**: funding positivo al passaggio (long affollati): **short la moneta**.

## 2. La regola

* Il momento dell'evento è il primo regolamento con l'intervallo più corto; si entra all'**apertura del giorno dopo**
  (giorno UTC), si esce all'apertura di **7 giorni dopo**. Serve la candela con volume il giorno dell'evento.
* E3: long la moneta e short il Bitcoin per lo stesso valore; E4: short la moneta e long il Bitcoin.
* Costi come la ventunesima prova (la moneta 0,05% + 0,10% di scarto all'entrata e all'uscita, il Bitcoin 0,05% + 0,01%) e
  il funding vero dei giorni di tenuta per le due gambe, con il segno.

## 3. L'esame

Come la ventunesima prova (`ventunesima.esame`): media degli eventi sopra zero con **p ≤ 0,005** a una coda, ma il bootstrap
rimescola le **settimane** (gli eventi della stessa settimana si muovono insieme), positiva nelle due metà degli eventi e
senza i 5 eventi migliori. Si riportano anche la media a 1, 3, 14 e 28 giorni e per anno. Due prove a eventi, nel registro.
