# Programma 7 — la revisione indipendente di G11 (23 ottobre 2026)

G11 (prova 69, `TREDICESIMA.md`) aveva passato l'esame scritto: Sharpe 2,05, Sharpe corretto 0,97. Prima del paper l'ha ricontrollata
un revisore separato, che non aveva scritto il codice (i suoi script sono fuori dal repository). Ha rifatto gli stessi numeri con il
codice del repository (G11 2,046, G1 1,963) e ha trovato:

* **Un errore di conto dimostrato**: le prove del programma 7 (dalla 57 alla 68) non entravano nel calcolo dello Sharpe corretto.
  Corretto (`asticella.serie_programma7`: le prove a portafoglio con la loro serie, quelle a eventi con il portafoglio della prova
  41, il buco del CME con l'1% di rischio a operazione): 73 gruppi, **G11 0,948, sotto la soglia di 0,95**; G1 0,913.
* **Fragilità degli ordini limite**: il vantaggio di G11 su G1 c'è solo con l'ipotesi più favorevole sull'esecuzione. Se il prezzo
  deve andare oltre il livello dello 0,05%: G11 1,79 (spese 18,5%), G1 1,785; dello 0,10%: G11 1,51, G1 1,61; tutto a mercato: G11
  1,89, G1 1,86. A costi tripli G11 1,34 e G1 1,48.
* **Il vantaggio sta nel 2021**: differenza G11 − G1 in punti l'anno 2021 +41,7, 2022 +12,3, 2023 −0,5, 2024 −18,6, 2025 +5,6, 2026
  −5,0; dal 2023 G11 1,60 contro G1 1,81; senza le 5 settimane migliori della differenza il vantaggio scende da +6,3 a +0,3 punti
  l'anno; probabilità che la differenza sia zero o meno: 32%.
* **A posto**: nessun dato futuro nel funding dell'ultimo giorno (tutti i regolamenti sono noti alle 00:00); il risultato non dipende
  da «1 giorno» esatto (con 2 o 3 giorni, o solo l'ultimo regolamento, lo schema è lo stesso).
* **Debolezza del metodo**: lo Sharpe corretto conta i gruppi di prove simili, quindi scegliere la migliore fra varianti molto simili
  (G11 è il 16° membro del gruppo di F5) non costa niente. Va tenuto presente per ogni variante di F5.

**Verdetto: G11 non è validata** (0,948 con il conto corretto) **e non entra nel paper**: non aggiunge niente di dimostrabile a G1,
che nel paper c'è già. Stima prudente del revisore: G11 circa 1,7-1,8 di Sharpe, dal 2023 circa 1,3-1,6; G1 1,76-1,785.
