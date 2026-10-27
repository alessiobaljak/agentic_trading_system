# Programma 7 — risultati della cinquantunesima prova (N3G: le monete nuove distribuite gratis)

Regole in `CINQUANTUNESIMA.md` (scritte prima). Le 613 operazioni della regola delle monete nuove (prova 32) così come sono.

* **Monete gratis**: 87 eventi, **+12.11% a evento**; le altre: 526, +2.99%.
* **La differenza nello stesso trimestre** (15 trimestri con tutti e due i gruppi, 87 gratis): **+7.87 punti a evento**, p 0.0272 (l'etichetta mescolata a caso 10000 volte dentro il trimestre). Senza l'uscita a +30%: +13.65 punti.
* **Le gratis da sole**: +12.11% (intervallo +5.10%; +18.95%, p 0.0006); mediana +22.88%, vinte 66%; metà +10.07% e +14.10%; senza le 5 migliori +8.90%.
* Per tipo: hodler airdrops +13.46% (43), launchpool +8.44% (41), megadrop +42.80% (3).
* Per anno (gratis / altre): 2021 +0.52% (2) / -1.53% (45), 2022 -4.19% (2) / +2.97% (20), 2023 -3.42% (7) / +7.58% (82), 2024 +13.96% (26) / +6.09% (105), 2025 +14.47% (49) / +2.08% (188), 2026 +12.63% (1) / -0.80% (86).
* Uscite a +30%: gratis 36%, altre 43%. Senza l'uscita: gratis +15.04%, altre +2.68%.

**Esito: la differenza non è sopra zero con p ≤ 0,01 (p 0.0272)** (soglia contando le 34 prove a eventi: 0.00029).

## Cosa abbiamo capito

* **La previsione va nella direzione giusta, e di molto.** Nel mese dopo il 7° giorno, le monete regalate da Binance scendono molto più
  delle altre:
  * la vendita fa +12,1% a evento sulle monete gratis, contro +3,0% sulle altre;
  * senza l'uscita a +30% la differenza è ancora più grande: +15,0% contro +2,7%.

  È il perché scritto prima: chi ha ricevuto la moneta senza pagarla vende.
* **Ma con 87 eventi non si separa dal caso**, contando le prove fatte. Nello stesso trimestre la differenza è di +7,9 punti con p 0,027:
  serviva 0,01, e 0,0003 contando le 34 prove a eventi. Le monete gratis da sole fanno p 0,0006, ma la domanda della prova era se rendono
  di più delle altre, non se N3 funziona anche su di loro.
* **Quasi tutto è 2024-2025**: 75 eventi su 87, +14,0% e +14,5%. Prima del 2024 gli eventi sono 11 e vanno male (2022 −4,2%, 2023
  −3,4%), ma sono troppo pochi per dire qualcosa.

## Esito e misura in avanti

**No** per le regole scritte prima. La regola N3 del bot non cambia, e non si sceglie adesso di pesare di più le monete gratis: sarebbe
decidere sui dati appena visti.

**Misura in avanti, a tavolino**, scritta adesso:
* ogni moneta nuova dal 22 ottobre 2026, il giorno in cui N3 è entrata nel paper del bot, si etichetta gratis o no con la stessa regola;
* quando ci sono **30 eventi gratis nuovi** (circa 6 mesi, al ritmo del 2025), si rifà lo stesso conto senza cambiare niente:
  differenza nello stesso trimestre, etichetta mescolata, p ≤ 0,01;
* se regge, la versione con il peso doppio sulle monete gratis diventa una prova nuova da scrivere prima, poi il revisore separato.
