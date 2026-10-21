# Programma 6 — trentacinquesima prova: contro gli eccessi, con l'indicatore RSI e il funding (T3)

Scritto il 21 ottobre 2026, mattina, **prima del calcolo**, dopo la prova 34 (la rottura del prezzo, cioè andare con la
folla, perde; lo short va meglio del long; il filtro del funding aggiunge circa +0,2% a operazione).

## 1. Perché

F3 e F5 dicono che la parte affollata (chi paga il funding alto) perde nelle settimane dopo. Un indicatore che misura
l'eccesso di prezzo (l'RSI, forza relativa) dice **quando** la folla ha esagerato. Insieme: si vende quando una moneta è
salita troppo **e** i long pagano molto, si compra quando è scesa troppo **e** pagano gli short. È il verso contrario alla
prova 34 e coerente con il vantaggio del funding.

## 2. La regola (valori classici, fissati qui)

* Monete, candele a 4 ore, costi, funding e periodo come la prova 34 (`TRENTAQUATTRESIMA.md`).
* **RSI a 14 candele** (media di Wilder) sulle chiusure a 4 ore.
* **Short**: l'RSI passa sopra **70** (sotto 70 alla candela prima) e il funding dei 7 giorni è nel **40% più alto**
  dell'universo. **Long**: l'RSI passa sotto **30** e il funding è nel **40% più basso**.
* **Entrata** all'apertura della candela dopo. **Uscite**: stop a **2 ATR** dal prezzo d'entrata (al livello, o all'apertura
  se saltato); **obiettivo**: quando l'RSI torna a **50** si esce all'apertura della candela dopo; al massimo **42 candele**.
* Una prova: nel conto del programma 6 diventano **59**.

## 3. L'esame

Come la prova 34: per operazione (media sopra zero con **p ≤ 0,01**, una variante, bootstrap sulle settimane d'entrata,
due metà, senza le 5 migliori) **e** come portafoglio (5% a operazione, al massimo 20 aperte; `terza.esame`, Sharpe corretto
sulle **59** prove). Si riportano long e short separati.
