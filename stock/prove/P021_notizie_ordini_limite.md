# Prova 21 — le azioni con una notizia, entrando con un ordine limite

Regole scritte il 25 ottobre 2026 **prima di qualsiasi calcolo** di questa variante (idea I23 di `REGISTRO.md`; il proprietario: «procedi
con gli ordini limite»), committate prima di lanciare il programma. **Variante nata dopo aver visto la prova 20** (Sharpe 1,29 senza costi,
−0,26 con i costi): va trattata con sospetto. Famiglia: in giornata seguendo l'apertura, periodo chiuso consumato; se passa la ricerca,
revisore separato e poi il demo. Conta come **1 prova** (51).

## Perché

Nella prova 20 il vantaggio prima dei costi c'era (+0,128% a operazione) ma lo scarto all'apertura dei giorni con notizie è largo (23 punti
base di mediana, `P020_scarto_vero.md`). Un ordine limite non paga lo scarto quando viene eseguito; il prezzo da pagare è che non tutti
vengono eseguiti, e spesso restano fuori proprio i casi migliori (quelli che partono senza tornare indietro). **Sospetto scritto prima:**
con le barre al minuto non si sa se un ordine limite sarebbe stato davvero eseguito in coda; la regola del simulatore (eseguito solo se il
prezzo passa oltre il limite) è prudente ma non perfetta.

## La regola

Tutto come la prova 20 (gli stessi 8972 giorni in gioco, la stessa candela di 5 minuti, lo stesso stop, obiettivo 10 volte il rischio,
uscita alle 15:59, il 10% del conto per operazione, al massimo 10 al giorno), **tranne l'ingresso**:

* **Ingresso con un ordine limite** al prezzo di chiusura della candela (9:34), nella direzione della candela, valido **15 minuti** (dalla
  barra delle 9:35 a quella delle 9:49). Si esegue solo se il prezzo passa oltre il limite (per un acquisto: un minimo strettamente sotto;
  per una vendita: un massimo strettamente sopra). Se non si esegue entro le 9:49, niente operazione quel giorno.
* Il rischio R si misura dal prezzo limite.

## I costi (con la misura vera)

* Scarto: **23 punti base** per tutti i titoli (la mediana misurata alle 9:35 nei giorni in gioco), metà a ogni esecuzione a mercato o a
  stop; **gli ordini limite eseguiti non pagano lo scarto**. Slittamento 2 punti base sugli ordini a mercato e sugli stop. Commissioni
  Interactive Brokers «fisso». Costi doppi.

## L'esame

Come la prova 20: (1) Sharpe annuo con i costi più alto del tenere lo SPY e del tenere l'indice a pesi uguali; (2) Sharpe corretto ≥ 0,95;
(3) Sharpe sopra zero con i costi doppi; (4) almeno il 60% dei 32 trimestri in guadagno. Da leggere: quante volte l'ordine limite viene
eseguito, il risultato per operazione e il suo t, e quello che si sarebbe ottenuto nei giorni in cui il limite **non** è stato eseguito
(con l'ingresso a mercato), per vedere se restano fuori i casi migliori.
