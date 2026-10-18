# E-005 — Scalping con ordini limite in entrata e in uscita, periodo C

Piano scritto e committato il 18 ottobre 2026 **prima del calcolo** (REGOLE.md, sezione 6bis). Solo periodo C; le 12
monete; candele da 1 minuto e barre di un'ora (`strumenti/ore.py`).

## Perché

Le idee a eventi rari (il rimbalzo dopo i crolli) hanno un guadagno grande a trade ma pochi trade: non si possono
dimostrare con la storia che c'è (I-017). I segnali frequenti hanno invece un vantaggio piccolo (E-002: un ordine limite a
2σ sotto il prezzo rende in media +0,14% lordo in 15 minuti su 17.725 trade, t 5,7; E-003: il ritorno fra monete a 1 ora
−0,025%, t −9,3), più piccolo del costo a mercato. Lo scalping vero vive di questo: **entrare e uscire con ordini limite**
(commissione 0,02% per lato, niente scarto), così il costo di un giro scende da 0,12-0,14% a 0,04%, e anche un vantaggio
piccolo ma frequente può pagare. Il rischio è la selezione avversa: l'ordine d'uscita si esegue solo se il prezzo torna,
e quando non torna si esce a mercato in perdita.

## La regola (per cella)

* All'inizio di ogni ora t un ordine limite d'**acquisto** a `L = P·exp(−k·σ)` (o di **vendita** a `L = P·exp(+k·σ)`), P
  chiusura dell'ora prima, σ dei rendimenti orari delle 720 ore fino all'ora prima; vale 60 minuti.
* **Esecuzione prudente** dell'ingresso: solo se il prezzo attraversa L (minimo strettamente sotto per l'acquisto, massimo
  strettamente sopra per la vendita), al prezzo L, commissione 0,02%, niente scarto.
* **Uscita a limite** a `T = L·exp(+m·σ)` per il long (`L·exp(−m·σ)` per lo short), messa subito dopo l'esecuzione: si
  esegue solo dal minuto **dopo** quello dell'ingresso (dentro il minuto dell'ingresso non si sa l'ordine dei prezzi) e
  solo se il prezzo attraversa T; al prezzo T, commissione 0,02%, niente scarto.
* Se T non si esegue entro H minuti dall'ingresso: **uscita a mercato** alla chiusura del minuto H, commissione 0,05% e
  scarto doppio. Funding se il trade attraversa un regolamento. Dopo l'uscita, ordini nuovi dall'ora seguente.
* Il risultato è **netto** (costi compresi); a costi doppi si raddoppiano commissioni e scarto.

## Le celle (54)

Lato (acquisto, vendita) × k (1, 2, 3) × m (0,5, 1, 2) × H (15, 60, 240 minuti).

## Statistica e criteri di promozione

Come E-002, ma sul **netto**: t per gruppi di giorni, per anno, per moneta; contro il caso = netto meno la media del
rendimento a H minuti con lo stesso verso nella stessa moneta e nello stesso mese (solo indicativo: l'uscita a limite cambia
la distribuzione). Una cella è promossa se, tutto insieme: netto ≥ **+0,05%** a trade; netto a costi doppi > 0; t ≥ **3**;
netto positivo in **ognuno degli anni** con almeno 20 trade; positivo su almeno il **70%** delle monete con almeno 10
trade (almeno 6); almeno **100** trade. Le celle promosse dello stesso lato diventano **una** idea con al massimo 3
varianti (le più forti per t), che passa dal motore a minuti (con l'uscita a limite, da aggiungere al motore con test) e
dall'esame (REGOLE.md, 5 e 6ter). Siccome questo è parente di I-016 (ordini d'acquisto sotto il prezzo, positivo su V),
**tutto il lato acquisto** è parente di un V positivo (prudente: anche k 1 e 2): se promosso, va con la prova solo su R
(6ter, punto 3). Il lato vendita no.
