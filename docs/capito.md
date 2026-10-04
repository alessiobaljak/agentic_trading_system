# Cosa abbiamo capito — una sezione per giorno

La stella polare (CLAUDE.md, 1 ott 2026): ogni giorno il sistema deve essere un passo più vicino
all'obiettivo, e non solo in profitto: conta ciò che abbiamo CAPITO (come perdiamo, perché entriamo
in ritardo, perché il trailing chiude presto, quali idee funzionano dopo il gate). Ogni mattina il
controllo giornaliero aggiunge qui IN CIMA una sezione `## AAAA-MM-GG` con 2-5 punti, ognuno con il
numero e la sua fonte; se non c'è niente di nuovo lo scrive. La macchina pubblica l'ultima sezione
nel report giornaliero in dashboard (sezione «Cosa abbiamo capito»): non va copiata altrove.

## 2026-10-04
* La stella polare è passata da −0,03R su 130 segnali (ops 0454) a +0,006R su 156, margine ±0,17 (ops 0474), per una giornata sola: il 3 ott 16 trade delle validate, 15 vinti, +0,869R a trade (ops 0479). Il numero oscilla intorno a zero dentro il margine: oggi la regola del 7 ott («motore ≤ 0 con almeno 80 segnali → la modifica va nel gate») non scatterebbe, ieri sì. Il verdetto del 7 ott può dipendere da un giorno buono o cattivo: per questo c'è la conferma del 14.
* Entriamo un po' peggio del segnale: ingresso a +0,038R rispetto alla chiusura della candela del segnale, con 155 secondi di ritardo (mediane, dato D8 raccolto dal 1 ott; ops 0479). È circa metà dei costi stimati a trade (0,081R): non spiega le perdite da solo, ma pesa.
* A 1 ora il gate passa diciotto volte più prove che a 15 minuti: 218 su 9.840 (2,2%, ops 0468) contro 25 su 20.667 (0,12%, ops 0470), in crescita da 141 e 193 nei giri prima. Non sappiamo se è un vantaggio vero o un filtro più facile: proposta G7 (il gate sul prezzo casuale) prima che le prime validate a 1 ora entrino nel paper (dall'8 ott).
* Primo verdetto «contribuisce» nelle funzioni: i quasi-passaggi operati a un quarto (paper esplorativo) fanno +0,385R su 10 trade contro −0,065R delle validate, differenza +0,450 ±0,419 (ops 0465). È al limite del campione minimo (10) e il metro dice 100 trade; ma va nella stessa direzione di T2: oggi la scelta del gate non aggiunge un vantaggio misurabile.
* T2 su 240 trade (ieri 207): a 1 ora i segnali vanno leggermente contro, −0,080 mosse tipiche, margine [−0,184; +0,013] (ops 0471). Ancora «nessun vantaggio misurabile», ma la prima ora è la più vicina a «peggio del caso».

## 2026-10-03
* Lettura ufficiale del 3 ott: le declassate (−0,131R su 70) contro le attive (+0,127R su 33) fanno −0,258R con margine ±0,458R → «non si decide» (ops 0445). Il quarto di puntata ha risparmiato 29,04 USDT, ma non si può dire che scelga trade peggiori.
* Lo «0 promosse» di R1 su 16.000 candidate (ops 0458) è sospetto ma non dimostrato: il gate vero passa lo 0,19% di un mix di 92 strategie (39 casuali nuove, 28 mutazioni dei quasi-passaggi, 25 rivalutate; 44/22.632, ops 0448/0450) e non stampa quante delle 44 siano casuali. Le due date complete sono recenti (17 e 3 set), quindi non è «storia corta». Si decide solo a parità di candidate (R2).
* R1 lavora 2,5 ore a lancio per costruzione (`BUDGET_S`): ieri 315 unità in ~2,4 ore di calcolo, poi fermo fino al lancio di stamattina. A 200 monete restano ~36 ore (ops 0458): la lettura del 10 ott non è raggiungibile senza la restrizione alle monete operate.
* Metà degli stop sono ingressi sbagliati dall'inizio: 51 su 107 (48%) non vanno mai a favore di 0,25R, e dei 7 stop nuovi 5 sono così (ops 0451 vs 0426). Il selettore in ombra non li distingue: p media 0,649 nei vinti contro 0,648 nei persi, correlazione +0,003 su 166 (ops 0445).
* L'ondata di 10 long del 2 ott è a +4,27 USDT sulle 8 chiuse (ops 0445) e la fascia «6+ posizioni nello stesso verso» è l'unica in R positivo (+0,026 su 11, contro −0,100 su 137 e −0,125 su 90). Su questi numeri l'affollamento non è dove si perde; campione piccolo.
* Il motore dopo la validazione resta a −0,03R, ora su 130 segnali ±0,18 (ops 0454; ieri 106 ±0,21): il margine si stringe e il numero non si muove.

## 2026-10-02
* T2: i segnali del paper non hanno un vantaggio misurabile sul caso. Il prezzo dopo 1, 4, 12 e 24
  ore dall'ingresso non si distingue da ingressi a caso sulla stessa moneta e direzione, nelle 12 ore
  dopo (201 trade, 15 giornate; a 4 ore −0,001 mosse tipiche, margine ±0,13, cioè circa ±0,5%; ops
  0437). Per la regola il lavoro sui take profit si ferma (T1 congelata): il problema è l'ingresso o il
  gate (R1).
* Anteprima del fuori campione girata: dopo la scelta del gate il motore fa −0,03R a trade su 106
  segnali, ±0,21 (ops 0429), ieri +0,06 su 89 (ops 0387). La regola del 7-14 ott («motore ≤ 0 con
  almeno 80 segnali → la prossima modifica va nel gate») oggi scatterebbe; il verdetto resta alla data.
* Prima dei costi il paper dal 27 set è quasi a zero: +0,013R a trade su 81, costi 0,078R (ops 0420); e
  il modello dei costi è un po' ottimista rispetto a Binance: commissioni 0,08% contro 0,10%, ~0,012R a
  trade (C5).
* Dal 27 set si perde soprattutto col mercato neutro: −0,317R su 39 trade, contro +0,357R su 25 a
  favore del trend (ops 0420; margine non stampato).

## 2026-10-01
* Il bot esegue quasi come il motore: sugli stessi 79 segnali la differenza è +0,05R con margine
  ±0,16R (ops 0387). Un difetto grosso di esecuzione è quasi escluso; il problema sembra prima del bot.
* Dopo la scelta del gate le validate rendono poco anche nel motore: +0,06R a trade su 89 segnali,
  ±0,18 (ops 0387), contro le +0,18 promesse. È un indizio, non ancora un verdetto (letture 7-14 ott).
* Il paper per ora non si distingue da un prezzo casuale con le stesse uscite: 54% di vinti contro
  54%, 46% di stop contro 46% (ops 0401, K4). Le classi dei referti descrivono la forma delle uscite,
  non una diagnosi.
* Stop giornaliero e freno di serie non avrebbero aiutato: sul gate tolgono soprattutto i rimbalzi
  (stop 3%: −11.615 e drawdown da 11,7% a 20,3%, ops 0405).
* Nessuna funzione ha ancora un contributo dimostrato oltre il margine; l'ombra AI (spenta) avrebbe
  evitato trade a −0,10R contro +0,23R di quelli che approvava, diff −0,33 ±0,36 (ops 0409).
