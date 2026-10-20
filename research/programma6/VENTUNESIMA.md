# Programma 6 — ventunesima prova: gli annunci di Binance (E1, E2)

Scritto il 20 ottobre 2026, **prima di qualunque calcolo sui prezzi** (contati solo gli eventi dai titoli degli annunci).
Fonte nuova: nessuna prova del programma 5 o 6 ha mai usato gli annunci.

## 1. Perché

* **E1, l'etichetta di monitoraggio** (dal luglio 2023): Binance la mette alle monete che rischiano di essere tolte dal
  listino (volatilità, poco volume, progetto fermo). Chi le tiene ha un motivo per uscire nelle settimane dopo (paura della
  rimozione, fondi che non possono tenere monete etichettate), e chi compra ha un motivo per non entrare: una spinta a
  vendere che dura più della reazione del primo giorno.
* **E2, la rimozione dal listino a pronti** («Binance Will Delist ...»): fino al giorno della rimozione chi ha la moneta su
  Binance deve venderla o spostarla; il perpetuo, se c'è, segue.
* Le quotazioni a pronti di monete che avevano già il perpetuo sarebbero la terza idea, ma con il perpetuo attivo sono 28
  eventi in tutto: troppo pochi, non si provano.
* Eventi contati dai titoli (`annunci.py`), con il perpetuo attivo e con volume il giorno dell'annuncio: E1 **88** (26
  annunci; 1 nel 2023, 10 nel 2024, 27 nel 2025, 50 nel 2026), E2 **63** (1 nel 2023, 12 nel 2024, 17 nel 2025, 33 nel 2026).

## 2. La regola (uguale per E1 e E2)

* Per ogni moneta dell'annuncio con il perpetuo contro USDT attivo (candela con volume il giorno dell'annuncio, giorno UTC):
  **short il perpetuo all'apertura del giorno dopo l'annuncio** (si perde la prima reazione: si cerca quello che viene dopo)
  e **long il Bitcoin** per lo stesso valore; si chiude tutto all'apertura di **7 giorni dopo**. Se la moneta viene tolta
  dal listino dei futures prima, vale il prezzo fermo dell'archivio (quello del regolamento).
* Costi: la moneta 0,05% di commissione più 0,10% di scarto all'entrata e all'uscita; il Bitcoin 0,05% più 0,01%; il funding
  dei giorni di tenuta, con il segno, per tutte e due le gambe (dati corretti del 20 ottobre).
* Rendimento di un evento: (rendimento del Bitcoin − rendimento della moneta) − costi − funding, sul valore di una gamba.

## 3. L'esame

* Media dei rendimenti degli eventi sopra zero con **p ≤ 0,005** a una coda (due prove: 0,01 diviso 2), con il bootstrap
  che rimescola gli **annunci** (le monete dello stesso annuncio si muovono insieme), 10.000 ripetizioni, seme 2026;
* media sopra zero nella prima e nella seconda metà degli eventi (per data);
* media sopra zero senza i 5 eventi migliori.
* Si riportano anche (senza decidere niente): la media a 1, 3, 14 e 28 giorni, la quota di eventi vinti, la media della
  prima reazione (dall'apertura del giorno dell'annuncio all'apertura del giorno dopo).
* Due prove a eventi: non entrano nello Sharpe corretto del programma 6 (che è per i portafogli), ma si contano nel
  registro (`research/REGISTRO.md`).
