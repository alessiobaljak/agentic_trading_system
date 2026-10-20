# Programma 6 — venticinquesima prova: il modello con la banda (M7) e insieme a F5 (F5 + M7)

Scritto il 20 ottobre 2026, mattina, **prima di qualunque calcolo**. Vale `VENTITREESIMA.md` (M6) e `VENTIQUATTRESIMA.md`
(F5) dove qui non si dice altro.

## 1. Perché

* La banda ha portato F3 da Sharpe 1,28 a 1,93 (prova 24): stesso segnale, meno giro, più monete per lato, meno spese.
  Il modello che unisce gli indicatori (M6, prova 23: Sharpe 1,02) cambia posizioni ogni settimana come F3: la stessa banda
  dovrebbe aiutarlo per lo stesso motivo.
* F5 e il modello sono quasi indipendenti (F3 e M6: correlazione 0,23); insieme a rischio uguale oscillano meno (come la
  prova 15, F3 + M1).

## 2. Le regole

* **M7**: la previsione di M6 (media dei ranghi dei cinque semi 1-5, dati corretti) con la banda di F5: long le monete che
  entrano nel 20% più alto e restano finché sono nel 40% più alto, short lo stesso dal basso; pesi secondo l'inverso della
  volatilità dei 30 giorni; costi come M1.
* **F5 + M7**: il capitale diviso fra F5 e M7 a rischio uguale con la volatilità delle 26 settimane prima (come la
  quindicesima prova, `quindicesima.combina`).
* Due prove: nel conto del programma 6 diventano **50**.

## 3. L'esame

Dal **3 gennaio 2022** (il modello parte da lì), `terza.esame` e `terza.esito` con lo Sharpe corretto sulle **50** prove.
Si riportano anche giro e spese di M7 rispetto a M6, e la correlazione fra F5 e M7.

## 4. Se regge

Chi passa l'esame entra nel paper dalla settimana dopo. Chi non passa ma fa meglio della sua versione senza banda (M7 di
M6, F5 + M7 di F5 da sola sugli stessi anni), nel paper si aggiunge come informazione.
