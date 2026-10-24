# Lo stato delle azioni

Da leggere per primo, dopo `README.md`. Aggiornato il 24 ottobre 2026.

## Cosa ha deciso il proprietario

* Mercato: **America** (24 ottobre).
* Obiettivo: il profitto; prima le prove sul passato, poi il paper su un conto demo, poi (solo su sua richiesta esplicita) i soldi
  veri. Nessuna strategia imposta: in giornata o su più giorni, ingressi, uscite e indicatori li sceglie la sessione (24 ottobre).
* Titoli: per ora le **10 azioni più grandi**, poi si vedrà se allargare (24 ottobre).
* Le richieste delle crypto (per esempio il trading in giornata) non valgono qui: le azioni partono da zero (24 ottobre).
* Prezzi storici: conto demo gratuito di **Alpaca** (Trading API), chiavi messe dal proprietario nell'ambiente con i nomi
  `ALPACA_API_KEY_ID` e `ALPACA_API_SECRET_KEY` (24 ottobre). Mai scriverle, stamparle o committarle.

## Cosa aspetta il proprietario

1. **La piattaforma del demo**: Interactive Brokers (serve un deposito su un conto vero, che non verrà usato) o Saxo (gratis, prezzi
   in ritardo di 15 minuti). Confronto in `piattaforme.md`.
2. **Il sì o no alle proposte di `METODO.md`**: le 10 azioni *di allora* più SPY e QQQ nelle prove sul passato; l'indice come
   asticella; il periodo chiuso (gennaio 2025 → settembre 2026); le condizioni per il demo e per i soldi veri.

## Cosa si può fare senza aspettare

* Il programma che scarica i prezzi da Alpaca e li controlla (frazionamenti, buchi, orari), senza committare i dati.
* Il simulatore con i costi di `METODO.md`, sezione 5, provato su casi costruiti a mano (non sui prezzi veri: quelli si guardano solo
  dentro una prova registrata).
* Nessuna prova di strategia finché il proprietario non ha risposto al punto 2.
