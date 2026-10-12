# Campagna di gruppo — lezioni sulle monete del gruppo (idee provate, risultati)

Resta in questa cartella fino al Passo 7. Numeri: `consegna.md` e `log.jsonl`.

* **Nessuna delle 15 idee provate ha un vantaggio distinguibile dal caso** sulle 80 monete, in costruzione
  (fino al 2023-01-16), con l'esame di gruppo.
* **Momento e rotture su 1d (I-01, I-02, I-10, I-17 per il calendario).** Sembrano buone contro ingressi casuali
  indipendenti (percentile 99,5-100), non contro le sfasate: i loro trade cadono negli stessi giorni su tutte le
  monete (rialzi comuni 2020-2021) e il 2022 è negativo. La rottura long fa 0,110 R ma -0,033 senza i 30 trade
  migliori.
* **Continuazione dopo un giorno anomalo (I-03), lunedì (I-08), lotteria (I-11), ritracciamento (I-12), candele
  (I-24), funding alto (I-05), inversione con volume (I-04):** nessun segnale; il lunedì è peggio del caso (t -1,37).
* **Il residuo rispetto a BTC su 3 settimane (I-26) non continua:** lo short perde (R -0,093, t -1,33): le monete
  rimaste indietro rispetto a BTC recuperano.
* **Ritardo da BTC a 1 ora (I-07).** La moneta che non ha seguito un'ora forte di BTC recupera nelle ore dopo
  (circa +0,04-0,09 R prima dei costi), ma un giro a 1 ora costa 0,05-0,07 R: dopo i costi resta fra 0 e +0,03 R. Con
  5 ritocchi il t arriva a 2,06 (soglia 2,16), mai netto.
* **Rientro del residuo rispetto a BTC a 4 ore (I-19).** L'effetto più grande e più stabile fra le varianti (R dopo
  i costi da +0,017 a +0,089, le tre prove degli estremi sempre superate, 2022 sempre negativo), ma concentrato nei
  giorni di vendite generali: pochi blocchi indipendenti. Il t più alto è 1,89 (soglia 2,07).
* **Costi per timeframe** (stop a 2 ATR, mediana fra le monete): 1d 0,012 R a giro, 4h 0,034 R, 1h 0,072 R. Sotto
  le 4 ore i costi decidono quasi tutto per vantaggi di questa taglia.
