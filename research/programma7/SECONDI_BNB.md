# In quanti secondi si muove il BNB dopo gli annunci di Launchpool e Megadrop (misura descrittiva, idea 84)

Script `secondi_bnb.py`, 67 annunci della prova 115, scambi del perpetuo del BNB (archivio pubblico di Binance), prezzo rispetto all'ultimo scambio prima della pubblicazione. Non è una prova: non entra nel conto.

| Secondi dalla pubblicazione | Media | Mediana | Quota del movimento dei 5 minuti (media) |
|---|---|---|---|
| -60 | -0.015% | +0.012% | -2% |
| -10 | +0.003% | +0.000% | 0% |
| -5 | -0.000% | +0.000% | -0% |
| +0 | +0.000% | +0.000% | 0% |
| +1 | +0.025% | +0.000% | 3% |
| +2 | +0.132% | +0.002% | 14% |
| +5 | +0.630% | +0.370% | 66% |
| +10 | +0.689% | +0.444% | 72% |
| +20 | +0.831% | +0.525% | 87% |
| +30 | +0.941% | +0.644% | 99% |
| +60 | +0.968% | +0.735% | 102% |
| +120 | +0.930% | +0.728% | 98% |
| +300 | +0.951% | +0.590% | 100% |

## Cosa abbiamo capito

* **La finestra è di 2-5 secondi.**
  * Prima della pubblicazione il prezzo non si muove (−0,015% nel minuto prima): nessuno lo sa in anticipo, e l'ora degli annunci è
    esatta.
  * Dopo 1 secondo è fatto il 3% del movimento dei 5 minuti, dopo 2 secondi il 14%, dopo 5 secondi il 66%, dopo 30 secondi tutto.
* **Cosa ci vorrebbe per prenderlo.** Chi entrasse entro 1-2 secondi dalla pubblicazione prenderebbe circa +0,8% in media (dal 2° al
  60° secondo), prima dei costi. Servono:
  * leggere l'annuncio nell'istante in cui esce, non ogni minuto come fa oggi il bot;
  * una macchina vicina ai server di Binance, a Tokyo (la voce P29 del backlog);
  * battere gli altri programmi che fanno la stessa gara: in 5 secondi hanno già preso due terzi del movimento.
* **Vale la pena?** Per i soli annunci di Launchpool no: sono circa 11 l'anno, con +0,8% su una posizione, prima di costi che in un
  movimento così veloce sono alti. Il discorso cambierebbe solo per tutti gli annunci di Binance insieme (quotazioni, regali, chiusure),
  ed è un mestiere diverso, una gara di velocità contro chi lo fa di professione. Resta in coda come idea 84, da riprendere solo se si
  decide di costruire una macchina veloce.
