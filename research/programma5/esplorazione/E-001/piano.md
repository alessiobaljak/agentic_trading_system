# E-001 — Esplorazione a ore sul periodo C

Piano scritto e committato il 18 ottobre 2026 **prima del calcolo** (REGOLE.md, sezione 6bis). Solo periodo C
(2020-01-01 → 2022-12-31); le 12 monete del programma.

## Perché

Le idee a 1 minuto (I-005, I-006, I-007) hanno un lordo vicino a zero: a pochi minuti il prezzo non dice abbastanza da
pagare 0,12-0,14% di costi. Qui si guarda **da 1 ora a 7 giorni**, dove i movimenti sono più grandi dei costi, e si
provano molte famiglie di segnali insieme, per trovare quelle con un guadagno lordo grande e costante (anni, monete).

## I dati

Barre di un'ora fatte dalle candele da 1 minuto (`motore5.minuti`): apertura del primo minuto, chiusura dell'ultimo,
massimo, minimo, volume e acquisti aggressivi sommati; un'ora vale solo con almeno 50 minuti presenti. Dal file `metrics`
(interesse aperto e rapporti long/short) l'ultimo valore noto alla fine dell'ora; il funding a ogni regolamento, noto dal
regolamento. σ = deviazione standard dei rendimenti orari (logaritmici) delle 720 ore prima (30 giorni), con almeno 500
ore valide.

## Come si misura un segnale

* Si decide alla **chiusura dell'ora t**; si entra all'**apertura dell'ora t+1**; si esce alla **chiusura dell'ora
  t+h**. Rendimento `d × (chiusura/apertura − 1)` meno il funding pagato nel tenere (`d` = +1 long, −1 short).
* Il verso «segue» è definito per ogni famiglia (sotto); il verso «contro» è il suo opposto (stesso numero col segno
  cambiato). Si riportano tutti e due: è come provare il doppio delle celle, ed è contato.
* Dopo un evento, nessun altro della stessa cella sulla stessa moneta per max(finestra, h) ore.
* **Lordo**: media a trade. **Contro il caso**: lordo meno la media, nella stessa moneta e nello stesso mese, del
  rendimento a h ore con lo stesso verso, su tutte le ore (come gli ingressi a caso del programma). **t**: per gruppi di
  giorni di calendario (i trade dello stesso giorno, anche su monete diverse, insieme). Per anno e per moneta.
* I costi non si tolgono qui (sono 0,12% a giro per BTC, ETH e SOL e 0,14% per le altre, il doppio a costi doppi): li
  tiene il criterio di promozione.

## Le famiglie (≈ 353 celle, ≈ 706 contando i due versi)

| Famiglia | Segnale alla chiusura dell'ora t | «Segue» | Valori | h (ore) |
|---|---|---|---|---|
| F1 scossa | z = ln(C_t/C_{t−w}) / (σ√w), \|z\| ≥ k; su e giù separati | verso della scossa | w 1, 4, 24; k 3, 4, 5 | 1, 4, 12, 24, 72 |
| F2 scossa + interesse aperto | come F1 con k = 3, e la variazione dell'interesse aperto nelle stesse w ore nel 20% più alto («oi su») o più basso («oi giù») dei 30 giorni prima | verso della scossa | w 1, 4 | 1, 4, 12, 24, 72 |
| F3 scossa propria (non BTC) | residuo e = r_w − β·r_w(BTC), β e σ_e dalle 720 ore prima; \|e\|/(σ_e√w) ≥ k | verso del residuo | w 1, 4, 24; k 3, 4 | 1, 4, 12, 24, 72 |
| F4 scossa di BTC sulle altre | z di BTC ≥ k (su o giù), si tratta la moneta | verso di BTC | w 1, 4; k 3, 4 | 1, 4, 12, 24, 72 |
| F5 rottura | chiusura sopra il massimo (sotto il minimo) delle N·24 ore prima | verso della rottura | N 5, 20, 60 | 24, 72, 168 |
| F6 funding | ultimo funding (a 8 ore) nel 10% più alto/basso dei 90 giorni prima, deciso al regolamento | long se alto | — | 24, 72, 168 |
| F7 rapporti long/short | alle 00:00 UTC, il rapporto nel 10% più alto/basso dei 30 giorni prima (un valore al giorno) | long se alto | tutti i conti; conti grandi (posizioni); conti grandi (conti) | 24, 72 |
| F8 acquisti aggressivi | quota di volume comprato aggressivamente nelle ultime w ore nel 5% più alto/basso dei 30 giorni | long se alta | w 1, 4, 24 | 1, 4, 24 |
| F9 volume | volume dell'ora ≥ k volte la mediana delle 720 ore prima | verso dell'ora | k 5, 10 | 1, 4, 24 |
| F10 calma poi rottura | escursione delle 24 ore prima < 0,5 volte la sua mediana dei 30 giorni, e chiusura oltre il massimo/minimo di quelle 24 ore | verso della rottura | — | 4, 24, 72 |
| F11 calendario | ogni ora del giorno UTC (long 1 ora); ogni giorno della settimana (long 24 ore dalle 00:00) | long | 24 + 7 celle | 1 / 24 |
| F12 tendenza | alle 00:00, il segno del rendimento degli ultimi N giorni | verso della tendenza | N 3, 7, 30 | 24, 168 |
| F13 prezzo e interesse aperto | alle 00:00, rendimento delle 24 ore con \|z\| ≥ 1, e variazione dell'interesse aperto delle 24 ore su o giù (4 combinazioni) | verso del prezzo | — | 24, 72 |

Il file `metrics` c'è da settembre 2020 per BTC e da dicembre 2021 per le altre: F2, F7 e F13 su C hanno di fatto BTC
2020-2022 e le altre il 2022. Dichiarato.

## I criteri di promozione a idea (tutti)

1. \|lordo\| ≥ **0,30%** a trade e, nello stesso verso, contro il caso ≥ **0,25%**;
2. stesso segno in **ognuno degli anni** 2020, 2021, 2022 che hanno almeno 20 trade;
3. stesso segno su almeno il **70%** delle monete con almeno 10 trade, e almeno **6** monete;
4. \|t\| ≥ **3** (gruppi di giorni);
5. almeno **100** trade.

Le celle promosse della stessa famiglia diventano **una** idea con al massimo 3 varianti (le più forti per t); al
massimo 5 idee per esplorazione, le più forti per t. Ogni idea promossa ha poi la sua scheda e passa dal motore a minuti
su C (costi, caso, bootstrap) e dall'esame di sempre (REGOLE.md, sezione 5). Se nessuna cella passa, si scrive e si
passa alla prossima esplorazione.
