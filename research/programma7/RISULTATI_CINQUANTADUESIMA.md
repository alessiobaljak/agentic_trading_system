# Programma 7 — risultati della cinquantaduesima prova (KP: il premio coreano fra le monete, ogni giorno)

Regole in `CINQUANTADUESIMA.md` (scritte prima). Dal 4 gennaio 2021 al 19 ottobre 2026, candele giornaliere di Upbit e di Binance.

* 242 perpetui con un mercato in won; monete con il segnale ogni giorno, mediana 40; lo scarto del premio fra il quinto più alto e il più basso, mediana 0.34% (Coinbase, prova 87: 0,15%).
* Operazioni: 2.4 entrate e 2.4 uscite al giorno; una posizione dura in media 9.5 giorni; variazioni 53516, eseguite con il limite 51755.
* **KP: Sharpe 0.31**, +11.0% l'anno, volatilità 35.9%, discesa -61.6%; spese 10.2% l'anno.
* Per anno: 2021 +27.5%, 2022 +41.4%, 2023 -13.1%, 2024 +5.8%, 2025 -23.0%, 2026 +31.8%.
* Il verso opposto (long il premio alto): Sharpe -0.80, -30.8% l'anno.
* Correlazione con G1: -0.21.
* Sharpe corretto con l'aggiunta 0.00 (81 gruppi); t dello Sharpe 0.74; regola del proprietario (corretto ≥ 0,90, ogni anno positivo, t > 3): no.

**Esito: netto con l'intervallo non sopra zero**

## Cosa abbiamo capito

* **Il premio coreano dice qualcosa, nella direzione prevista.**
  * Vendere le monete che i coreani pagano di più e comprare quelle che pagano di meno fa uno Sharpe di 0,31; il verso opposto
    perde (Sharpe −0,80, −30,8% l'anno).
  * Chi compra la moda coreana paga troppo, come dopo l'arrivo su Upbit (prova 41).
  * La differenza di premio fra le monete è più del doppio di quella di Coinbase (0,34% contro 0,15%), perché l'arbitraggio è bloccato.
* **Ma è troppo debole e troppo agitato per guadagnare.**
  * Volatilità 35,9%, discesa −61,6%.
  * Tre anni negativi su sei: 2023 −13,1% e 2025 −23,0%.
  * Spese 10,2% l'anno.
  * Sharpe corretto 0,00 e t 0,74: non si separa dal caso.
* **La correlazione con G1 è negativa** (−0,21): il premio coreano è un'informazione diversa dal funding. Ma da sola non basta, e
  provare adesso a unirla a G1 sarebbe scegliere sui dati appena visti.
* **Esito: no.** Non va nel paper.
