# Programma 6 — i giorni della settimana: conviene stare fermi nel fine settimana? (descrittivo)

Scritto il 23 ottobre 2026, mattina, **prima del calcolo**. Il proprietario: «hai mai pensato di fare un'analisi su quali giorni
fare trading rispetto agli altri? In passato leggevo di non fare mai trading nel weekend».

## 1. Cosa c'è già

Il programma 5 ha provato il calendario come **segnale** (`research/programma5/esplorazione/E-001`, E-103, E-113: comprare in un
giorno o in un'ora fissi; il movimento del fine settimana che continua o torna indietro il lunedì): nessuna cella promossa. Non è
mai stato misurato se **le strategie che abbiamo** guadagnano o perdono nel fine settimana, né se il mercato nel fine settimana è
diverso (meno scambi, prezzi più nervosi).

## 2. Cosa si misura (descrittivo: non è una prova e non entra nel conto)

1. **Il mercato, per giorno della settimana UTC**, dal 4 gennaio 2021 al 4 ottobre 2026: rendimento medio e deviazione del
   Bitcoin e della media a pesi uguali delle 100 monete della settimana; volume rispetto alla media della settimana.
2. **F5 (con la correzione delle parità), giorno per giorno**: i pesi del lunedì tenuti per la settimana; il guadagno di ogni giorno
   è il movimento del prezzo di quel giorno sul prezzo d'entrata del lunedì più il funding di quel giorno (la somma dei 7 giorni
   rifà il lordo della settimana, a meno della deriva dei pesi). Per ogni giorno: media, deviazione, t, quota del totale.
3. **Lo scalping della prova 54** (Z1, Z1b, Z2, Z3, Z4): le operazioni per giorno d'entrata; media netta in R, quota vinte, e i
   giorni feriali contro il fine settimana.

## 3. Cosa farà scattare una prova (fissato qui)

* **F5**: se sabato e domenica insieme hanno un guadagno medio giornaliero **negativo con t ≤ −2**, si scrive una prova «F5 ferma
  nel fine settimana» (chiusura venerdì alle 24:00, riapertura lunedì alle 00:00, con i costi del doppio giro). Altrimenti no:
  chiudere e riaprire ogni settimana costa (lo 0,07% a unità sul giro, più del doppio delle spese di F5).
* **Scalping**: se uno schema, **solo nei giorni feriali**, ha una media netta sopra zero con p ≤ 0,002 (0,01 diviso i 5 schemi),
  diventa un'ipotesi da provare su dati non usati (non sui 2024-2026 da cui viene). Altrimenti no.
