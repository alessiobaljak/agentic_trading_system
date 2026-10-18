# I-020 — Scalping a limite: reti d'acquisto a 3σ con uscita a limite

Scheda scritta il 18 ottobre 2026 **prima del calcolo di questa idea nel motore a minuti** (REGOLE.md, sezioni 6, 6bis e
6ter).

## Da dove viene, e perché la prova è solo R

Dall'esplorazione **E-005** (`research/programma5/esplorazione/E-005/risultati.md`): 5 celle promosse su 54, tutte dal lato
dell'acquisto con k = 3; le 3 più forti per t sono le varianti qui sotto. È parente di I-016 (ordini d'acquisto sotto il
prezzo), che su V ha dato un netto positivo: per la regola 6ter (punto 3, e il piano di E-005) V qui è **costruzione** e
la prova è **R da solo**, con la soglia severa. Le tre varianti sono fissate **adesso**, prima di V: V non sceglie niente.

## Perché

È scalping nel senso del proprietario, sfruttare la volatilità: un ordine fermo 3σ sotto il prezzo si esegue solo quando
qualcuno vende in fretta (stop, liquidazioni, panico) attraverso il libro; si rivende subito con un ordine fermo poco
sopra (0,5-1σ), che si esegue quando il prezzo torna. Tutti e due i lati pagano la commissione bassa (0,02%) e niente
scarto: un giro costa 0,04% invece di 0,12-0,14%. Si guadagna fornendo liquidità a chi la chiede di colpo; si perde quando
il prezzo non torna (uscita a mercato dopo H minuti).

## La regola (`strumenti/scalping.py`, `per_moneta_i020`)

* **Monete**: le 12 del programma; barre di un'ora (`strumenti/ore.py`) per il livello, candele da 1 minuto per le
  esecuzioni.
* All'inizio di ogni ora t: ordine limite d'acquisto a `L = P·exp(−3σ)`, P chiusura dell'ora t−1, σ dei rendimenti orari
  delle 720 ore fino all'ora t−1 (almeno 500); vale 60 minuti.
* **Ingresso** solo se il minimo di un minuto è strettamente sotto L; prezzo L; commissione 0,02%; niente scarto.
* **Uscita a limite** a `T = L·exp(m·σ)`, valida dal minuto dopo l'ingresso, eseguita solo se il massimo di un minuto è
  strettamente sopra T; prezzo T; commissione 0,02%. Se non si esegue entro H minuti dall'ingresso: a mercato alla
  chiusura del minuto H (0,05% e scarto doppio). Funding se il trade attraversa un regolamento. Mentre il trade è aperto,
  nessun ordine nuovo sulla moneta.
* **Il caso** (`scalping.caso_doppio`): ingresso all'apertura di un minuto qualunque della stessa moneta e dello stesso
  mese, stessa σ, stesso target, stessa tenuta, stessi costi; 20 ripetizioni.

## Le varianti (giudicate insieme) e la prova

| Variante | k | m | H (minuti) | In E-005 (netto, trade, t) |
|---|---|---|---|---|
| I-020a | 3 | 0,5 | 60 | +0,192%, 6.821, 7,00 |
| I-020b | 3 | 0,5 | 240 | +0,208%, 6.649, 6,83 |
| I-020c | 3 | 1 | 240 | +0,321%, 6.121, 5,57 |

**Prova su R, una volta** (`esame.json`): netto con l'intervallo al 95% sopra zero; p a una coda ≤ 0,005 / 3; positivo in
almeno 2 dei 3 anni; positivo a costi doppi; positivo togliendo il giorno migliore; positivo su almeno il 60% delle monete
con almeno 20 trade (almeno 3); almeno 100 trade.
