# E-003 — Valore relativo fra le monete, periodo C

Piano scritto e committato il 18 ottobre 2026 **prima del calcolo** (REGOLE.md, sezione 6bis). Solo periodo C
(2020-01-01 → 2022-12-31); le 12 monete del programma; barre di un'ora (`strumenti/ore.py`, come E-001).

## Perché

Un segnale di direzione su una moneta porta con sé il movimento di tutto il mercato: nel 2021 (rialzo) e nel 2022
(ribasso) lo stesso segnale cambia segno, ed è il motivo più comune per cui una cella di E-001 non regge in tutti gli anni.
Un trade **relativo** (una moneta contro BTC, o le monete forti contro le deboli) toglie il mercato e lascia solo quello che
è proprio della moneta: lì possono esserci eccessi che tornano indietro (chi vende una moneta sola per fretta) o notizie che
si diffondono piano (continuazione). È anche la base di molte strategie dei fondi sulle cripto.

## Le famiglie

**G1 — scossa propria coperta con BTC** (11 monete, non BTC). Come F3 di E-001: residuo e = r_w − β·r_w(BTC), β e σ_e
delle 720 ore prima; evento se e/(σ_e√w) ≥ k o ≤ −k. Il trade è **coperto**: la moneta nel verso d, BTC nel verso −d per
β volte il valore. Rendimento a h ore: d·[(moneta) − β·(BTC)], funding delle due gambe compreso. w 1, 4, 24; k 2, 3, 4;
su e giù; h 1, 4, 12, 24, 72 (**90 celle**). Pausa max(w, h) per moneta.

**G2 — classifica fra le monete** (portafoglio). A ogni decisione (ogni h ore, allineate all'ora 00:00 UTC; per h 72 e
168 ogni 3 e 7 giorni dalle 00:00 del primo giorno del periodo) si mettono in fila le monete che hanno dati (almeno 8) per
il rendimento delle ultime w ore; «segue»: long le 3 prime, short le 3 ultime, pesi uguali, metà capitale per parte.
Rendimento a h ore per unità di capitale = (media delle 3 prime − media delle 3 ultime) / 2, funding compreso. w 1, 4, 24,
72, 168 × h 1, 4, 24, 72, 168 (25 celle), e lo stesso con il **residuo** rispetto a BTC al posto del rendimento (25 celle,
BTC escluso dalla fila): **50 celle**.

**G3 — classifica per funding**: alla decisione delle 00:00 (ogni h ore come G2), fila per l'ultimo funding (a 8 ore);
«segue» = long i 3 con il funding più alto, short i 3 più bassi. h 24, 72, 168 (**3 celle**).

**G4 — classifica per interesse aperto**: fila per la variazione dell'interesse aperto delle ultime w ore; «segue» = long
le 3 con la crescita più alta. w 24, 72; h 24, 72 (**4 celle**; di fatto solo 2022, dichiarato).

**G5 — classifica per volume**: fila per il volume delle ultime 24 ore diviso la mediana dei 30 giorni prima; «segue» =
long le 3 con il volume più alto rispetto al solito, short le 3 più basse. h 24, 72 (**2 celle**).

**G6 — le altre monete insieme contro BTC**: s_w = media dei rendimenti di w ore delle 11 monete − rendimento di BTC;
z = s_w / (σ_s√w) con σ_s dalle 720 ore prima (rendimenti orari della differenza); evento se z ≥ k o ≤ −k; «segue» = long
il paniere e short BTC se è salito, al contrario se è sceso; metà capitale per parte. w 4, 24, 72; k 2, 3; su e giù; h 4,
24, 72 (**36 celle**).

In tutto **185 celle**, il doppio contando i due versi.

## Statistica e criteri di promozione

Come E-001 (t per gruppi di giorni, per anno). **Contro il caso**: per G1, lordo meno la media del rendimento coperto a h
ore nella stessa moneta e nello stesso mese, con lo stesso verso; per G2-G6 il caso è già zero per costruzione (un
portafoglio long-short a caso rende in media zero), quindi contro il caso = lordo. **Per moneta**: per G1 il lordo della
moneta; per G2-G5 il contributo della moneta quando è nel portafoglio, d·(rendimento della moneta − media di tutte le
monete in fila); per G6, BTC non si divide: il criterio delle monete non si applica e si chiede invece il segno giusto in
ognuno dei 3 anni con almeno 20 trade (già richiesto) e |t| ≥ 3.5.

Costi di un giro: G1 ≈ 0,14% + β·0,12% ≈ 0,26% (due gambe); G2-G6 ≈ 0,13% per unità di capitale. Una cella è promossa se:

1. |lordo| ≥ **0,50%** (G1) o ≥ **0,30%** (G2-G6) a trade, e contro il caso ≥ **0,40%** (G1) o ≥ 0,30% (G2-G6), nello
   stesso verso;
2. stesso segno in **ognuno degli anni** 2020, 2021, 2022 con almeno 20 trade;
3. stesso segno su almeno il **70%** delle monete con almeno 10 trade, almeno **6** (G1-G5);
4. |t| ≥ **3** (G6: 3,5);
5. almeno **100** trade.

Le celle promosse vicine diventano **una** idea con al massimo 3 varianti, che passa dal motore a minuti (con le due gambe:
da aggiungere al motore, con test) e dall'esame di sempre.
