# Programma 7 — risultati della cinquantatreesima prova (BL: il BNB dopo gli annunci di Launchpool e Megadrop)

Regole in `CINQUANTATREESIMA.md` (scritte prima). Candele a 1 minuto di Binance, dal 22 ottobre 2020 al 24 ottobre 2026.

* 67 annunci, **65 operazioni** (long il BNB e short il Bitcoin per 24 ore, 5 minuti dopo l'annuncio).
* **+0.60% a evento** dopo i costi (intervallo -0.64%; +2.12%, p 0.1927); mediana +0.03%, vinte 52%; metà +0.91% e +0.30%; senza le 5 migliori -0.37%.
* **Il controllo** (minuti a caso 30-60 giorni prima, lontani dagli annunci): 325 operazioni, -0.37% a operazione.
* Per anno: 2020 -1.74% (6), 2021 +1.77% (14), 2022 +0.75% (3), 2023 +1.64% (10), 2024 +0.32% (22), 2025 +0.08% (9), 2026 -1.73% (1).
* Per tipo: launchpool +0.66% (62), megadrop -0.56% (3).
* Tenuta di 72 ore: +0.73%. Il BNB da solo nelle 24 ore: +1.18% (il Bitcoin +0.35%). Il BNB contro il Bitcoin nel primo minuto dopo l'annuncio: +0.915%; nei primi 5 minuti: +0.978%.

**Esito: media non sopra zero con p ≤ 0,01 (p 0.1927)** (soglia contando le 35 prove a eventi: 0.00029).

## Cosa abbiamo capito

* **La domanda di BNB c'è, ma dura un minuto.** Il BNB sale sul Bitcoin:
  * nel primo minuto dopo l'annuncio: +0,92%;
  * nei primi 5 minuti: +0,98%;
  * da lì in poi, nelle 24 ore, solo +0,60% dopo i costi (p 0,19), con la mediana a zero e in perdita senza i 5 eventi migliori.

  Il perché scritto prima era giusto: per avere le monete regalate bisogna bloccare BNB, e l'annuncio fa comprare BNB. Ma il prezzo si
  aggiusta subito, e lo prende chi legge l'annuncio in pochi secondi.
* **Il controllo** (minuti a caso lontani dagli annunci) fa −0,37%, quindi l'evento resta un po' sopra, ma non abbastanza per separarlo
  dal caso.
* **Il minuto dell'annuncio va letto con prudenza**: la candela comincia all'inizio del minuto della pubblicazione, che può essere fino a
  59 secondi prima. Una parte di quel +0,92% potrebbe venire da chi ha saputo prima, ma il movimento è comunque tutto lì.
* **Esito: no.** Non va nel paper. Per prendere il primo minuto servirebbero la lettura degli annunci al secondo e una macchina vicina a
  Binance (la domanda sul passaggio ad AWS, voce P29 del backlog). È un altro mestiere, quello di chi fa a gara di velocità, e lo si
  scrive nella coda come idea da riguardare solo con i dati degli scambi al secondo (idea 84).
