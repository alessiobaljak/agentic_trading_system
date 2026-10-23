# Programma 7 — la revisione indipendente di G12 e di E4 (23 ottobre 2026)

G12 (prova 70, `QUATTORDICESIMA.md`) aveva passato il suo esame (+13,00% a evento, +1,33 punti su E4) e, per la regola scritta prima,
il bot sarebbe entrato in E4 subito dopo l'evento. Prima del riavvio l'ha ricontrollata un revisore separato (script fuori dal
repository). Ha rifatto G12 (13,00% identico) e E4 dalle candele orarie (11,667% contro 11,668%) e ha trovato:

* **Dati futuri: a posto.** I 62 momenti dell'evento cadono sull'ora piena; l'entrata di G12 è un'ora dopo un regolamento già
  avvenuto; il segno è quello di quel regolamento.
* **Il miglioramento non c'è.** Dei +1,33 punti, 1,22 vengono da **due contratti tolti dal listino il giorno stesso dell'evento**
  (RVV il 10 febbraio 2026, HFT il 7 agosto 2026): E4 vi «entrava» alle 00:00 del giorno dopo in un contratto già chiuso (due
  operazioni impossibili), G12 prendeva il crollo delle ultime ore. Sugli altri 60 eventi: **+0,11 punti** (intervallo −2,69;
  +4,13; p 0,47). Già con 3 ore di ritardo G12 fa peggio di E4, e il bot controlla una volta l'ora. Applicata la regola ai soli
  eventi possibili (+0,11 sotto il punto richiesto), **il bot resta com'è**: il cambio è stato annullato prima del riavvio.
* **Errori dentro E4** (prova 26), ereditati da G12:
  * **LIT, 23 dicembre 2025**: non è un accorciamento dell'intervallo, è una moneta nuova con lo stesso nome (la vecchia era ferma
    da giugno); contava +27,8%.
  * **RVV e HFT**: le due operazioni impossibili qui sopra.
  * **Cinque eventi dopo un funding al minimo negativo** (ARIA, ESPORTS due volte, LYN, REEF): il primo tasso al passo corto è appena
    positivo, quindi la regola li prende fra i «positivi», ma non sono long affollati.
  * **I 14 eventi del 12 ottobre 2023**: un cambio d'ufficio di Binance (tasso 0,005%), non un funding al tetto.

## E4 corretto

Tolti gli errori di dati chiari (LIT e le due operazioni impossibili): **59 eventi, +11,89% a evento, p 0,0067: sopra la soglia di
0,005 della prova 26, quindi E4 non passa più il suo esame scritto** (prima p 0,0047). Solo per capire: senza i cinque eventi dopo il
minimo negativo +10,7% (p 0,018); senza i 14 del 12 ottobre 2023 +12,1% (p 0,019). E4 resta positivo e resta nel paper come
informazione, non come strategia validata.

## Cosa cambia

* Il bot non entra più su contratti che Binance chiude prima della fine della tenuta (`f5.in_chiusura`, data di consegna di
  `exchangeInfo`), né per N3 né per E4 (`bot/portafoglio/eventi.py`, test in `tests/test_paper_eventi.py`).
* Idea nuova in coda: **vendere i perpetui annunciati in chiusura**, con tutti gli annunci di chiusura dei future (più eventi), regole
  scritte prima.
