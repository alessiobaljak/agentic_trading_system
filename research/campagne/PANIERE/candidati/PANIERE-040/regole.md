# Candidato PANIERE-040 — le 20 monete più in ritardo dopo un giorno forte al rialzo di Bitcoin

Famiglia PANIERE-032 (C2-1,5 long), ritocco 2 (ritocco di PANIERE-039). Idea C della seconda edizione. Codice:
`codice/ritardo.py`, parametri nella registrazione PANIERE-040 del log (copia in `codice/ritocchi.json`).

* **Monete**: le 80 di `monete.csv`, una regola per tutte; timeframe 1 giorno (candele UTC del last, chiuse).
* **Direzione**: long.
* **Ingresso**: alla chiusura del giorno `t`, se (1) il rendimento di Bitcoin del giorno supera 1,25 volte la
  deviazione standard dei suoi 60 rendimenti giornalieri precedenti (almeno 40 finiti; `paniere.giorno_forte_ultimo`
  sulle chiusure di BTCUSDT delle righe del paniere) e (2) la moneta è fra le 20 monete del paniere con il
  rendimento del giorno più lontano sotto quello di Bitcoin (solo monete con rendimento del giorno, liquide quel
  mese, BTCUSDT escluso; parità alfabetica). Ordine limite alla chiusura del giorno `t`, valido il giorno `t+1`,
  riempito se il minimo di `t+1` va sotto il prezzo (motore, terreno della seconda edizione).
* **Stop**: chiusura del giorno di segnale meno 2,5 ATR(20) (media semplice dei true range delle ultime 20 barre).
* **Uscita**: «chiudi» alla chiusura della terza barra in posizione (la barra d'ingresso conta 1), eseguito a mercato
  all'apertura del giorno dopo; stop; tetto di 60 barre (non scatta mai prima).
* **Dimensione e leva**: regole del bot e di `parametri_2.yaml`: rischio 1% del capitale per trade, leva massima 2,
  isolated; commissione maker 0,02% all'ingresso, taker 0,05% più lo scarto della fascia della moneta all'uscita.
* **Filtri**: nessuno della variante; il filtro di liquidità (mesi sotto 20 milioni di USDT al giorno) lo applica
  `gruppo.py` a tutte le varianti.
* **Motivo economico** (ipotesi.md, idea C): dopo un giorno forte di Bitcoin i flussi passano con ritardo alle
  altre monete, meno liquide e meno seguite, e quelle rimaste indietro recuperano nei giorni dopo.
* **Da sapere**: è il migliore di più ritocchi sugli stessi dati; lo stop a 2,5 ATR giornalieri (circa il 22% del
  prezzo in mediana) è molto oltre il tetto del 6% del bot: così com'è il bot non può eseguirlo.
