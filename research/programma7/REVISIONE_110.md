# Revisione separata della prova 110 (vendere le opzioni) — 26 ottobre 2026

Revisore separato (un agente indipendente), dalle 06:37 alle 06:57 UTC. Script e tabelle in `revisione_110/` (scritti per `/tmp/revisore110/`:
i percorsi vanno adattati); gli scambi grezzi delle opzioni di Deribit (202 MB) in `research/data/deribit_opzioni/`, fuori da git.

* **I prezzi veri**: l'archivio pubblico gratuito di Deribit (`history.deribit.com`, scambi delle opzioni scadute dal 2016) per **tutti i 580
  venerdì** (290 BTC, 290 ETH): le opzioni settimanali al prezzo del momento, scambiate fra le 08:00 e le 09:00 (mediana 81 scambi a venerdì).
* **Il premio vero è il 12,7% più basso** di quello stimato con il DVOL a 30 giorni (mediana −13,4%; più basso in 536 venerdì su 580), con tre
  metodi indipendenti (curva della volatilità, mediana degli scambi, valore diretto della coppia di opzioni: 0,864-0,881 del premio stimato).
  Per anno: 0,82-0,84 nel 2021-2023, 0,89-0,96 nel 2024-2026. La differenza è asimmetrica: nelle settimane di crollo la volatilità vera era
  vicina al DVOL o sopra (le perdite restano intere), nelle settimane calme sotto (il guadagno si accorcia).
* **Ricalcolo con i prezzi veri**: **+0,009% a settimana** (p 0,48, Sharpe 0,01), discesa −63%, dal 2023 −0,19% a settimana; il pareggio
  richiede un premio vero almeno all'87,1% di quello stimato, e il premio vero è all'87,3%: **tutto il guadagno della prova nasceva
  dall'approssimazione**.
* **Lo scarto vero**: chi vende a mercato su Deribit incassa in media l'1,2% in meno del prezzo di riferimento (il 3% del codice era prudente);
  con l'1,2% la strategia resta a +0,10% a settimana (p 0,37): non si salva.
* **Il calcolo** del codice è giusto (cinque settimane rifatte a mano, serie riprodotta); il perpetuo Binance alle 08:00 stima bene il prezzo di
  regolamento di Deribit (differenza mediana 0,1%). Errori minori: la serie dello Sharpe corretto spostata di una settimana, i costi doppi vuoti.
* **Dove si potrebbe fare**: Deribit (settimanali BTC/ETH, margine circa il 37% del conto a leva 1); Binance Options (vendita aperta a tutti per
  BTC da agosto 2025 e per ETH da dicembre 2025, secondo le notizie; non verificato dalle pagine ufficiali, la Svizzera non verificata).
* **Giudizio: non regge.** Il margine vero fra premio e pagamento è circa lo 0,25% del prezzo a settimana e i costi se lo mangiano.

**Lezione per il metodo**: ogni prova sulle opzioni d'ora in poi usa i prezzi veri dell'archivio di Deribit, non la volatilità implicita a 30
giorni con la formula: lo scarto fra le due era proprio la misura del guadagno.
