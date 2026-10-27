# Programma 7 — risultati della cinquantesima prova (LQ: comprare dopo le cascate di vendite forzate, in giornata)

Regole in `CINQUANTESIMA.md` (scritte prima). Periodo 1° dicembre 2021 – 24 ottobre 2026, le 100 monete più scambiate di ogni settimana, candele a 1 ora e a 1 minuto e interesse aperto a 5 minuti dell'archivio di Binance.

* **I segnali**: 13636 ore con il prezzo giù almeno del 5%; di queste 13602 con i dati sulle posizioni (34 senza, saltate). Con le posizioni giù almeno del 5% (LQ): 2307; con le posizioni in salita (C1): 4664.
* **LQ: 2279 operazioni** su 332 monete in 553 giorni; uscite: tempo 93%, protezione 7%.
* **+0.15% a operazione** dopo i costi (intervallo -0.52%; +0.83%, p 0.3321); mediana +0.54%, vinte 56%; metà -0.20% e +0.49%; senza le 5 migliori +0.07%. Prezzo +0.27%, costi 0.14%, funding -0.018%; con i costi doppi +0.01%; coperta con il Bitcoin -0.16%.
* Per anno: 2021 -3.40% (126), 2022 -1.30% (433), 2023 +0.98% (718), 2024 +1.33% (479), 2025 +0.91% (225), 2026 -0.74% (298).
* I 5 giorni migliori fanno il 304% della somma: 2024-12-09 +261.5, 2023-08-17 +211.3, 2025-10-10 +200.8, 2023-03-03 +176.4, 2024-06-07 +166.1 (somme delle operazioni, in punti).
* **Tutto il mercato** (il Bitcoin giù almeno del 3% nella stessa ora): 627 operazioni, +0.14% a operazione, mediana +1.38%, vinte 63%. **La moneta da sola**: 1652 operazioni, +0.15% a operazione, mediana +0.34%, vinte 54%.
* **C1, il crollo con le posizioni in salita**: 4256 operazioni, -0.36% a operazione, mediana -0.03%, vinte 50%. **C2, il crollo senza condizione sulle posizioni**: 12334 operazioni, -0.15% a operazione, mediana +0.21%, vinte 52%. **Il caso** (ore a caso negli stessi giorni-moneta): 2279 operazioni, -1.40% a operazione, mediana -0.49%, vinte 43%.
* Altre uscite: dopo 1 ore 2307 operazioni, -0.17% a operazione, mediana +0.22%, vinte 54%; dopo 24 ore 2224 operazioni, +0.54% a operazione, mediana +0.75%, vinte 55%.
* Portafoglio (5% a operazione, al massimo 20 aperte), dal 6 dicembre 2021: Sharpe -0.00, -0.0% l'anno, volatilità 12.1%, discesa -23.6%; Sharpe corretto 0.00 (81 gruppi), t -0.01.

**Esito delle operazioni: media non sopra zero con p ≤ 0,01 (p 0.3321)** (soglia contando le 33 prove a eventi: 0.00030). **Portafoglio: netto con l'intervallo non sopra zero**.

## Il controllo dal 2023 (dichiarato nelle regole, sezione 1bis, prima dei risultati)

* **LQ dal 1° gennaio 2023**, fuori dal periodo già usato da I-001 del programma 5: 1.720 operazioni, **+0,77% a operazione, p 0,0079**.
  Passa la soglia scritta per una prova sola (p ≤ 0,01), ma **non quella di tutte le prove a eventi** (0,0003). Il 2026 è negativo
  (−0,74% su 298), e il guadagno sta in pochi giorni: i 5 giorni migliori fanno il 304% della somma di tutto il periodo. Nello stesso
  periodo C1 fa +0,11% e C2 +0,24%.

## Cosa abbiamo capito

* **L'interesse aperto distingue davvero i crolli.** Il prezzo, prima dei costi, va così:
  * dopo un crollo con le posizioni in calo (LQ): +0,27% in 4 ore;
  * dopo un crollo con le posizioni in salita (C1): −0,28%;
  * tutti i crolli insieme (C2): −0,04%.

  È la direzione prevista: chi è costretto a vendere spinge il prezzo troppo in basso, chi vende per scelta no. È lo stesso ordine che
  aveva visto I-001 (+0,11% contro −0,02%).
* **Ma il rimbalzo è piccolo e tutto del mercato.**
  * Coperta con il Bitcoin, la regola fa −0,16%.
  * Il guadagno viene da pochi crolli di tutto il mercato (9 dicembre 2024, 17 agosto 2023, 10 ottobre 2025, 3 marzo 2023, 7 giugno
    2024).
  * Nel dicembre 2021 e nel 2022, anni di discesa, le cascate continuavano: −3,40% e −1,30% a operazione.
* **Il caso perde molto** (−1,40% a operazione): nei giorni di crollo comprare a un'ora qualunque è peggio che comprare subito dopo la
  cascata. Il momento conta, come nelle prove 75 e 78, ma non basta a pagare i costi con margine.
* **Esito: no.** Non va nel paper. L'idea è la stessa di I-001, provata due volte, e non regge con le soglie del metodo. Quello che si
  è visto (le uscite a 24 ore, il periodo dal 2023) non diventa una variante nuova: sarebbe scegliere sui dati già guardati.
