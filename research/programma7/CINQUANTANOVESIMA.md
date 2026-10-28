# Programma 7 — cinquantanovesima prova: l'inclinazione delle opzioni sul Bitcoin, ogni giorno (RR)

Scritto il 28 ottobre 2026 alle 20:22 UTC (ora dell'orologio), **prima di scaricare le operazioni sulle opzioni e prima di qualunque
calcolo**. Fino a qui si è contato solo quante operazioni ci sono in due ore di un giorno (3.653 il 4 marzo 2024, con la volatilità
implicita di ognuna). È l'idea 88 della coda, dalla ricerca nella letteratura del 28 ottobre. È trading di ogni giorno, sul solo
Bitcoin.

## 1. Perché

* **Chi sa qualcosa usa la leva delle opzioni.** Chi ha un'informazione sul prezzo la usa comprando opzioni lontane dal prezzo di oggi,
  perché costano poco e rendono molto. Se c'è una spinta a comprare opzioni che guadagnano in caso di salita, la loro volatilità
  implicita sale rispetto a quella delle opzioni che proteggono dalla discesa. La differenza fra le due è l'«inclinazione»: misura da
  che parte guardano quelli che pagano.
* **Cosa dice la letteratura**:
  * Neo 2026, tesi di dottorato alla Singapore Management University, dati di Deribit dal 2021 al 2025: l'inclinazione a 90 giorni prevede
    il Bitcoin, ma da sola ha t 1,91 e si indebolisce dal 2024;
  * Alexander, Deng, Feng e Wan 2023, *Journal of Financial Markets*: le opzioni lontane dal prezzo portano informazione sulla
    direzione, soprattutto nel 2021.
* **La direzione scritta prima**: long il Bitcoin quando l'inclinazione è sopra la sua mediana dei 90 giorni prima (le opzioni da
  salita più care del solito), short quando è sotto.
* **I dubbi scritti prima**:
  * un solo lavoro, una tesi non pubblicata, con un segnale debole che si indebolisce;
  * le prove sul solo Bitcoin non hanno mai battuto il Bitcoin tenuto (prove 13, 47, 72, 99);
  * l'inclinazione si ricostruisce dalle operazioni, non dal listino completo.

## 2. La misura (fissata qui)

* **Le operazioni**: quelle sulle opzioni del Bitcoin di Deribit (`history.deribit.com`, archivio pubblico) fra le 22:00 e le 24:00 UTC di
  ogni giorno, dal 1° aprile 2021 al 25 ottobre 2026, salvate in `research/data/deribit_rr/` fuori da git.
* **Per ogni operazione**:
  * la scadenza e il prezzo d'esercizio si leggono dal nome dello strumento;
  * il tempo alla scadenza è in anni;
  * il delta si calcola con la formula di Black e Scholes, con la volatilità implicita dell'operazione, il prezzo dell'indice e il
    tasso zero.
* **Si tengono**:
  * le operazioni con la scadenza fra **20 e 45 giorni** (l'inclinazione a circa un mese, la più scambiata);
  * le opzioni d'acquisto con il delta fra 0,15 e 0,35;
  * le opzioni di vendita con il delta fra −0,35 e −0,15.
* **L'inclinazione del giorno d**: la mediana della volatilità implicita delle opzioni d'acquisto meno quella delle opzioni di
  vendita, con almeno 5 operazioni per parte; altrimenti il giorno manca.

## 3. La regola

* **Il segnale per il giorno d + 1** (dalle 00:00 UTC): l'inclinazione del giorno d meno la mediana delle inclinazioni dei 90 giorni da
  d − 90 a d − 1, con almeno 45 giorni validi. Sopra zero long il perpetuo del Bitcoin, sotto zero short. Se manca, si resta come il
  giorno prima.
* **Costi e funding**: il costo a mercato del Bitcoin del programma 6 a ogni cambio di verso (uscita ed entrata); il funding del giorno.
* **Una prova a portafoglio**: nel conto delle prove diventano **216**.

## 4. L'esame

* **Come le prove a portafoglio** (`terza.esame`, `terza.esito`, con il Bitcoin come riferimento): lo Sharpe corretto con l'aggiunta
  sopra 0,95, il t contro 3 e la regola del proprietario del 24 ottobre.
* **Se regge**, passa da un revisore separato.
* **Per capire, senza decidere niente**:
  * la versione solo long (long sopra, fuori sotto) contro il Bitcoin tenuto;
  * la correlazione fra il segnale e il rendimento del giorno dopo e della settimana dopo;
  * per anno; quanti giorni mancano.
