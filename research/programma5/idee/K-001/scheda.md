# K-001 — Un modello che mette insieme tutti i segnali, neutrale rispetto al mercato

Scheda scritta il 18 ottobre 2026 **prima di qualunque calcolo** (REGOLE.md, sezioni 7 e 10).

## Perché

Preso da solo, ogni segnale provato dà un vantaggio piccolo o legato a un periodo. Ma molti segnali deboli e diversi,
messi insieme, possono dire qualcosa che nessuno dice da solo; ed è così che lavorano molti fondi quantitativi. Il
rischio è imparare il rumore: per questo il modello è il più semplice possibile (una somma pesata, la regressione «ridge»,
con un solo numero da scegliere), si costruisce solo su C2 e si prova una volta su V2. Ed è **neutrale rispetto al
mercato**: ogni giorno compra le monete che il modello vede più forti delle altre e vende le più deboli, così non guadagna
perché il mercato sale (che è quello che è successo alle idee della fase 2).

## I dati e i segnali (alla chiusura dell'ora 23:00 UTC di ogni giorno, solo dati già noti)

Le 24 monete della fase 2; barre di un'ora (`strumenti/ore.py`), premio, funding, interesse aperto, rapporti long/short
e libro degli ordini (`strumenti/libro.py`). Per ogni moneta, 20 segnali (`strumenti/modello.py`):
scosse z a 1, 4 e 24 ore; rendimento di 3 e 7 giorni in unità di σ; distanza dal massimo e dal minimo dei 30 giorni;
scossa propria rispetto a BTC a 24 ore e a 7 giorni; volume delle 24 ore sul solito (logaritmo); quota di acquisti
aggressivi delle 24 ore; premio sullo spot e la sua variazione nelle 24 ore; funding; variazione dell'interesse aperto
nelle 24 ore; rapporto long/short di tutti i conti e dei conti grandi; squilibrio del libro entro il 2% e il 5% (media
delle 24 ore); liquidità entro l'1% sul solito (logaritmo); volatilità delle 24 ore su quella dei 30 giorni (logaritmo).
Ogni giorno ogni segnale si mette **in scala fra le monete** (meno la media del giorno, diviso la deviazione standard del
giorno, tagliato a ±3); un segnale mancante vale 0.

## L'obiettivo e il modello

Obiettivo: il rendimento delle 24 ore dopo (dall'apertura dell'ora 00:00 alla chiusura dell'ora 23:00, funding compreso)
meno la media delle monete dello stesso giorno, tagliato a ±20%. Modello: regressione ridge senza termine costante; il
peso λ si sceglie fra 1, 10, 100, 1.000 costruendo sul 2024 e misurando sul primo semestre 2025 (il rendimento netto del
portafoglio qui sotto); poi si ricostruisce su tutto C2 con quel λ. I pesi finali si scrivono in `pesi.json` e si
congelano con le impronte.

## Il trade

Ogni giorno alle 00:00 UTC (decisione alla chiusura dell'ora 23:00, almeno 16 monete con la previsione): **long le 4
monete con la previsione più alta, short le 4 con la più bassa**, metà capitale per parte, pesi uguali, tenute 24 ore;
ogni gamba paga un giro intero a mercato (commissione 0,05% per lato e scarto del programma per lato), funding compreso
(`strumenti/portafoglio.py`). Una sola variante (K-001a).

## L'esame

C2: informativo (i pesi vengono da lì). **V2, una volta** (REGOLE.md, sezioni 7 e 10): netto a portafoglio con
l'intervallo al 95% sopra zero e p a una coda ≤ 0,005; positivo a costi doppi; positivo togliendo il giorno migliore;
positivo in tutte e due le metà; contributo positivo su almeno il 60% delle monete con almeno 20 gambe; almeno 200 gambe;
**meglio del caso** (lo stesso portafoglio con le monete prese a caso).
