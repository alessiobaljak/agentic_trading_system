# Programma 7 — terza prova: le monete nuove dal primo giorno (G4)

Scritto il 23 ottobre 2026, mattina, **prima del calcolo**. Idea 4 di `METODO.md` (eventi), dopo la lezione di G2: in giornata
servono movimenti grandi a operazione, e le monete appena quotate ne hanno.

## 1. Perché

Le monete nuove dei perpetui scendono nelle prime settimane (chi le ha ricevute gratis o comprate prima della quotazione vende):
N3, lo short al 7° giorno di vita contro il Bitcoin, fa +4,29% a evento su 613 monete di Binance (prova 32, p 0,0017). Il 7° giorno
è stato fissato su Gate.io per evitare i primi giorni più agitati; ma se la discesa comincia subito, entrando al **1° giorno** se ne
prende di più, e le monete nuove arrivano quasi ogni giorno (632 in 5 anni e 9 mesi, prova 32). **Riserva:** N3 è stata vista;
cambiare il giorno d'ingresso dopo averla vista è una variante, quindi è una prova nel conto e si giudica come una prova nuova.

## 2. La regola (tutto come la prova 32 tranne il giorno d'ingresso)

* Monete: i perpetui USDT di Binance con la prima candela giornaliera fra il 1 gennaio 2021 e il 10 settembre 2026 (esclusi i
  contratti che non sono monete), volume non zero il giorno prima dell'ingresso.
* **Ingresso all'apertura del giorno dopo il primo giorno di quotazione** (età 1 giorno invece di 7): short la moneta e long il
  Bitcoin per lo stesso valore. Uscita a +30% della moneta (candele a 1 ora, 1% di scarto) o dopo 30 giorni; costi e funding come
  la prova 32.
* Si riporta anche la versione senza l'uscita a +30% (solo per capire) e il confronto evento per evento con N3 (le stesse monete
  al 7° giorno).
* Una prova a eventi: nel conto diventano **122**.

## 3. L'esame

Come la prova 32 (`trentesima.esame`): media per evento sopra zero con **p ≤ 0,01** (bootstrap sulle settimane d'ingresso),
positiva nelle due metà e senza i 5 eventi migliori.
