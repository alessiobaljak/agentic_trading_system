# Programma 7 — quarta prova: il long in giornata delle monete con il funding più negativo (G3)

Scritto il 23 ottobre 2026, **prima del calcolo**. Idea 3 di `METODO.md`, lo specchio di G2 (prova 58). Il 23 ottobre l'avevo
scartata con un numero sbagliato (avevo attribuito a F5 i lati di C3): in F5 è il lato **long** a rendere di più (+42,8% l'anno
contro +16,2% dello short, prova 24). **Riserva:** G2 ha mostrato che dentro la giornata il vantaggio del funding non c'era dal lato
short nemmeno prima dei costi (−0,022 R); qui si vede se il lato long, quello forte di F5, si comporta diversamente.

## 1. La regola (lo specchio esatto di G2, `SECONDA.md`)

* **Le monete del giorno** (alle 00:00 UTC): fra le 100 della settimana, il 20% con il funding dei 7 giorni più basso (la soglia
  d'entrata del lato long di F5), con la volatilità dei 30 giorni disponibile.
* **L'entrata**: dalle 01:00 alle 20:00 UTC, la prima candela da 1 ora che **chiude sopra l'apertura del giorno**; long a mercato
  all'apertura dell'ora dopo. Una sola operazione per moneta al giorno.
* **Lo stop**: il minimo del giorno fino all'entrata (almeno lo 0,2% sotto l'entrata); a mercato, al livello o all'apertura se il
  prezzo ci salta oltre. **L'obiettivo**: due volte la distanza dello stop sopra l'entrata, a ordine limite. Stop e obiettivo nella
  stessa ora: vale lo stop. **Uscita a tempo** alle 00:00 del giorno dopo, a mercato.
* Costi, funding (il long paga un terzo del funding del giorno per ogni regolamento delle 08:00 e delle 16:00 che attraversa, e
  incassa se è negativo), dimensione (0,5% di rischio, tetto 20%), candele e periodo come G2. Nel conto diventano **123**.

## 2. L'esame

Come G2: per operazione media netta sopra zero con p ≤ 0,01 (bootstrap sui giorni), positiva nelle due metà e senza i 5 giorni
migliori; come portafoglio `terza.esame` e `terza.esito`, Sharpe corretto con l'aggiunta del 23 ottobre, soglia 0,95.
