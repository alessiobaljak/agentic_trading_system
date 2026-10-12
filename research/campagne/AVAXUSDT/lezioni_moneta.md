# Lezioni sulla moneta AVAXUSDT (costruzione 2020-09 → 2022-12)

Osservato sui soli dati di costruzione; il periodo di validazione non è stato usato.

## Cosa non ha funzionato (nessun vantaggio misurabile contro l'ingresso casuale)

* Momento di serie a 14 giorni, long e short (I-01); forza relativa contro BTC (I-11); rotture di
  canale di Donchian (I-02): rendono quanto la (b) nella stessa direzione, cioè il trend di fondo
  (rialzo 2021, ribasso 2022). Lo short a 14 giorni batte la (b) (t 2,12) ma non la (a).
* Ritorno verso la media con RSI(2) (I-03), funding estremo in entrambe le direzioni (I-04), ritardo
  rispetto a BTC (I-05), lunedì (I-07), rottura della volatilità del giorno (I-09), compressione di
  Bollinger (I-10), volume anomalo (I-12), inversione dopo salti orari (I-13), squilibrio degli
  ordini aggressivi (I-14): nessuno vicino alla soglia.

## Cosa abbiamo capito

1. **Continuazione dopo una barra di 4 ore in forte rialzo (V-14).** Dopo una barra oltre 2
   deviazioni standard il long nelle 24 ore dopo fa R 0,20 su 113 trade, contro −0,017 del caso
   (t 2,68), positivo nel 2020, 2021 e 2022, robusto a ±20% dei parametri, ancora netto a costi
   doppi, anche con BTC calmo. Ma col ritardo di una barra il `t` scende a 1,33 (serviva 1,34):
   l'effetto si concentra nelle prime barre. Scartato dalla regola del ritardo, non per un errore
   trovato. Il rendimento medio dopo i segnali è +0,33%, +1,09%, +0,52%, +0,48%, +0,56% nelle
   barre 1-5 contro +0,07% di una barra qualsiasi; la mediana dei trade è vicina a zero: pochi
   trade grandi.
2. **L'effetto non è simmetrico.** Dopo un crollo di 4 ore oltre 2 deviazioni lo short perde più
   del caso (V-15, R −0,18, t −1,74), e dopo un'ora oltre +3 deviazioni lo short perde più del
   caso (V-28): i rialzi forti continuano, i crolli forti rimbalzano un po'. Osservato, non provato.
3. **Momento infragiornaliero a 30 minuti.** Il segno del giorno UTC fino alle 23:30 predice la
   mezz'ora dopo in entrambe le direzioni (circa +0,065 R lordi a trade) e continua anche dopo la
   mezzanotte; l'ora in sé non è speciale. Ma il vantaggio lordo è grande quanto i costi (0,06 R a
   giro con stop di 2 ATR): netto quasi zero, negativo a costi doppi. Cinque ritocchi con filtri
   presi dai fallimenti non lo cambiano.
4. **Funding negativo nel 2022** accompagnava il ribasso: il long dopo funding negativo perde più
   del caso (t −1,29).

## Rischi noti dei dati

* Mark mancante per giorni interi (luglio 2021, 31 luglio e 2 ottobre 2022, 24 febbraio 2023).
* Volume dell'autunno 2020 sotto 20 milioni al giorno (ottobre e dicembre esclusi) e slippage della
  scheda ottimista per il 2020 e per giugno-luglio 2021.
