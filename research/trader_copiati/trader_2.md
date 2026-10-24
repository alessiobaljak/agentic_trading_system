# Trader da copiare n. 2 (profilo e 45 schermate mandati dal proprietario il 24 ottobre 2026)

Profilo (365 giorni, dalla schermata): ROI +726,58%, guadagno +37.782 USDT, Sharpe 3,49, discesa massima 11,70%, 507 posizioni vinte
su 518 (97,88%), 341 giorni di trading, leva 10-20 dichiarata, saldo di margine 20.000 USDT, 888 copiatori. Monete: ZEC 15,7%, ETH
12,1%, 1000PEPE 9,6%, LAB 5,9%, BEAT, UB, RAVE, AKE, ESPORTS, FOLKS e altre (39%).

Dati: 178 posizioni chiuse (dal 27 giugno al 23 ottobre 2026; 3 schermate erano doppie), trascritte da tre lettori separati e
**controllate tutte sui prezzi a 1 minuto di Binance**: per ognuna il prezzo d'entrata e quello d'uscita stanno nelle candele dei
minuti in cui era aperta (178 su 178), con l'ora delle schermate letta come ora italiana (UTC+2). Programma:
`analisi_trader2.py`, tabella: `trader2_posizioni.csv`. Descrittivo, non entra nel conto delle prove.

## Cosa fa

* **Scalping sulle monete piccole e nuove che si muovono molto**: 47 monete (LAB 26 posizioni, AKE 19, ZEC 16, TUT, TAC, Q, IRYS,
  ESPORTS, EVAA, BTR...), leva 5 su 128 posizioni, 50 su ZEC. Posizione tipica circa 1.300 dollari.
* **Durata: 3 minuti** (mediana; un quarto sotto il minuto, il 90% sotto 3 ore e mezza).
* **Short (103) sulle fiammate**: la moneta è già salita molto nelle 24 ore prima (mediana +76%, un quarto sopra +129%) e sta
  salendo ancora negli ultimi 15 minuti (mediana +3,9%), con il volume 5 volte il normale. Esce appena scende del 5% circa.
* **Long (75) sulle discese**: moneta scesa nelle 24 ore (mediana −19%) e ancora in calo nei 15 minuti prima (−1,8%); esce a +3%.
* Opera a tutte le ore (da mezzanotte alle 23 UTC).

## I conti

* **Vinte 170 su 178 (95,5%)**, ma: vinte +26.351 dollari, **perse −13.533 in 8 posizioni**. Le 8 perse da sole si mangiano metà
  dei guadagni: MARSCOIN −4.390 (short tenuto un giorno, la moneta +46% contro), BR −3.085 (short tenuto **5 giorni**, la moneta è
  salita del **361%** contro), PUMPBTC −2.217 (+102% contro), IN −1.757, ZEC −1.195.
* **Le vinte durano 2 minuti, le perse 10 ore** (mediane): chiude subito i guadagni e tiene le perdite sperando che tornino.
  Esempio: IRYS il 23 ottobre, short a ~0,19 alle 19:10 UTC; in 13 minuti la moneta arriva a **0,50**; la tiene, crolla a 0,09,
  chiude a +3.798. A 0,50 perdeva circa 13.000 dollari su un conto di 20.000.
* Netto delle 178: **+12.818 dollari in 4 mesi**, positivo ogni mese da luglio.

## Cosa vuol dire

* La quota di vinte (95-98%) è il segno di questo stile, non di un vantaggio: tante piccole vincite e poche perdite enormi. La
  discesa massima dell'11,7% del profilo non conta le perdite tenute aperte (IRYS a 0,50 non risulta da nessuna parte).
* **L'idea sotto è sensata e non l'abbiamo mai provata così**: le fiammate delle monete piccole rientrano in pochi minuti (chi
  vende quando tutti comprano fa da controparte, ed è pagato per il rischio). Noi abbiamo provato lo short il giorno dopo una salita
  del 30% (prova 62: −2,7% a evento) e le salite estreme al minuto sul 2020-2022 (programma 5), mai le fiammate dentro la giornata
  sulle monete piccole del 2025-2026 con un'uscita rapida e una protezione.
* Si prova come regola fissa sul passato **che lui non ha toccato** (gennaio 2025 – maggio 2026, tutte le monete), con regole
  scritte prima e una protezione obbligatoria (lui non ce l'ha: è quello che lo fa saltare prima o poi).

## La prova sul passato (prova 75, `research/programma7/RISULTATI_DICIOTTESIMA.md`)

La sua idea come regola fissa, su tutte le monete tranne le 30 più grandi, dal gennaio 2025 al 26 giugno 2026 (prima dei suoi trade
che abbiamo visto): 3.494 operazioni su 405 monete.

* **Con la protezione a +30%: −0,88% a operazione.** Vince l'83% delle volte (+4,8%), ma il 15% finisce alla protezione (−30%).
* **Senza protezione, come fa lui** (si tiene finché scende del 5%, al massimo 7 giorni): +1,65% a operazione e 97% di vinte, ma
  non sicuro (p 0,074); e le tre peggiori fanno −1.511%, −972%, −628%: monete salite di 10-15 volte dopo l'entrata. Con il 5% del
  conto a operazione, **una sola settimana perde il 154% del conto**.
* **Il momento conta**: entrare a caso negli stessi giorni sulle stesse monete fa −9,43% a operazione. Lui sa scegliere il minuto;
  ma il guadagno di ogni volta (+5%) è più piccolo del rischio che la fiammata continui.
* Quindi il suo +37.782 in un anno è vero ma è il premio di un'assicurazione venduta: guadagna poco quasi sempre e prima o poi
  arriva la moneta che sale di 10 volte. Con 20.000 dollari di margine, una sola di quelle azzera il conto.

## La versione senza protezione con posizioni piccole (prova 76, `research/programma7/RISULTATI_DICIANNOVESIMA.md`)

Correzione di quanto scritto sopra: la frase «una settimana perde il 154% del conto» vale con il 5% del conto a operazione; con
l'1% la stessa regola senza protezione, nel gennaio 2025 – giugno 2026, arriva a 1,57 volte il conto con la discesa peggiore del 34%
(conto descrittivo). Per questo l'abbiamo provata sul serio, con regole scritte prima, sul 2023-2024 (anni mai usati): **393
operazioni, +0,30% a operazione (p 0,36), 2024 negativo, il conto con l'1% a operazione +1% in due anni.** Il vantaggio del
2025-2026 non si ripete: era di quel periodo, con molte più fiammate. Non va nel paper.
