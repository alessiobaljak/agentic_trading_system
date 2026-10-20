# Programma 6 — ventisettesima prova: E4 su un altro exchange (Gate.io), la conferma

Scritto il 20 ottobre 2026, pomeriggio, **prima di scaricare i prezzi di Gate.io e prima di qualunque calcolo**. Guardato
solo: che l'archivio pubblico di Gate.io (`download.gatedata.org`, bucket S3 `gateio-public-data`) ha il funding applicato
di ogni contratto USDT perpetuo dal 2020 e le candele giornaliere, e che Gate.io accorcia anche lui l'intervallo del funding
(in giugno 2025, sui primi 150 contratti dell'elenco, 2 passaggi a un intervallo più corto).

## 1. Perché

E4 (prova 26) passa l'esame scritto con p 0,0047 su 62 eventi di Binance, ma contando tutte le prove a eventi del programma
la soglia sarebbe 0,0025. Il modo pulito per sapere se è vera è guardare **un altro exchange**, dove gli eventi sono altri: se
l'affollamento dei long che fa scattare il tetto del funding annuncia la discesa, deve valere anche lì.

## 2. La regola (la stessa di E4, sui dati di Gate.io)

* **Dati**: per ogni contratto USDT perpetuo di Gate.io, il funding applicato (`futures_usdt/funding_applies`, ora e tasso
  di ogni regolamento) e le candele giornaliere (`futures_usdt/candlesticks_1d`), mesi dal **2023-01** al **2026-09**;
  impronte SHA-256 dei file scaricati.
* **Evento**: il primo regolamento dopo il quale la distanza fra due regolamenti si accorcia (la distanza fra questo e il
  precedente è minore di quella fra il precedente e quello prima), con il **tasso positivo** a quel regolamento.
  Precisazione scritta prima del calcolo: la distanza di prima deve essere al massimo di 8 ore (l'intervallo più lungo di
  Gate.io); una distanza più lunga è un buco nei dati, non un intervallo, e non conta.
* **Operazione**: short la moneta e long il Bitcoin di Gate.io per lo stesso valore, dall'apertura del giorno dopo (UTC) a
  quella di 7 giorni dopo; costi come E4 (la moneta 0,05% + 0,10% di scarto all'entrata e all'uscita, il Bitcoin 0,05% +
  0,01%); funding di Gate.io dei giorni di tenuta per le due gambe, con il segno. Serve la candela con volume il giorno
  dell'evento.
* **Gli eventi indipendenti**: si tolgono gli eventi di una moneta che ha avuto un passaggio a un intervallo più corto anche
  su Binance (prova 26, di qualsiasi segno) nei 7 giorni prima o dopo: sono lo stesso episodio, non una conferma.

## 3. L'esame

* **Decide** l'insieme degli eventi indipendenti (se sono almeno 30; se meno, decide l'insieme intero e lo si scrive): media
  sopra zero con **p ≤ 0,01** a una coda (una regola sola, già scritta: la soglia delle conferme della settima prova), con il
  bootstrap che rimescola le settimane; positiva nelle due metà degli eventi e senza i 5 eventi migliori.
* Si riportano anche l'insieme intero, la media a 1, 3, 14, 28 giorni e per anno.
* Una prova di conferma, nel registro. Se E4 è confermata, lo si scrive nel paper (`paper/REGOLE.md`) senza cambiare le sue
  regole; se non lo è, E4 resta nel paper ma con la nota.

## 4. Correzioni dopo il primo calcolo (errore di lettura dei dati, 20 ottobre 2026, sera)

Il primo calcolo ha dato 146.297 eventi (146.128 nel 2026) e rendimenti di milioni per cento: un errore di lettura, non un
risultato. Due cause nei dati di Gate.io: (1) dal 2025-2026 l'ora dei regolamenti ha qualche secondo di scarto (28.797
secondi invece di 28.800), e la regola leggeva ogni scarto come «intervallo più corto»; (2) alcuni contratti cambiano scala
del prezzo a metà serie (CAT_USDT a giugno 2026 passa da 0,0000019 a cifre normali). Prima di correggere ho visto
quell'uscita sbagliata, comprese le medie per anno del 2023-2025 (+7,5%, +9,9%, +5,9% sugli eventi indipendenti), che
vanno lette come contaminate. Le correzioni dipendono solo dal formato dei dati:

* le distanze fra regolamenti si confrontano **arrotondate all'ora**;
* un evento non conta se fra il giorno dell'evento e 28 giorni dopo la moneta ha un salto di più di **50 volte** in un giorno
  (in su o in giù, fra chiusure di giorni consecutivi): è un cambio di scala del contratto, non un prezzo vero.

L'esame resta quello della sezione 3. Si riporta quanti eventi toglie ogni correzione.
