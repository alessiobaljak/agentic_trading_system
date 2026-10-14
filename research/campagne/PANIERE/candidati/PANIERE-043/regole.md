# Candidato PANIERE-043 — tutte le monete in ritardo dopo un giorno forte al rialzo di Bitcoin

Famiglia PANIERE-028 (C1-1,5 long), ritocco 2 (ritocco di PANIERE-042). Idea C della seconda edizione. Codice:
`codice/ritardo.py`, parametri nella registrazione PANIERE-043 del log (copia in `codice/ritocchi.json`).

* **Monete**: le 80 di `monete.csv`, una regola per tutte; timeframe 1 giorno (candele UTC del last, chiuse).
* **Direzione**: long.
* **Ingresso**: alla chiusura del giorno `t`, se (1) il rendimento di Bitcoin del giorno supera 1,25 volte la
  deviazione standard dei suoi 60 rendimenti giornalieri precedenti (almeno 40 finiti; `paniere.giorno_forte_ultimo`)
  e (2) il rendimento del giorno della moneta è strettamente sotto quello di Bitcoin (moneta liquida quel mese, con
  il rendimento del giorno). Ordine limite alla chiusura del giorno `t`, valido il giorno `t+1`, riempito se il
  minimo di `t+1` va sotto il prezzo (motore, terreno della seconda edizione).
* **Stop**: chiusura del giorno di segnale meno 2,5 ATR(20).
* **Uscita**: «chiudi» alla chiusura della terza barra in posizione, eseguito a mercato all'apertura del giorno
  dopo; stop; tetto di 60 barre.
* **Dimensione e leva**: rischio 1% per trade, leva massima 2, isolated; maker 0,02% all'ingresso, taker 0,05% più
  lo scarto della fascia all'uscita.
* **Filtri**: nessuno della variante; filtro di liquidità di `gruppo.py`.
* **Motivo economico**: lo stesso di PANIERE-040 (ipotesi.md, idea C).
* **Da sapere**: è il migliore di più ritocchi sugli stessi dati, con la stessa coppia di modifiche di PANIERE-040;
  stop circa il 22% del prezzo, oltre il tetto del 6% del bot.
