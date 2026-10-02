# Cosa abbiamo capito — una sezione per giorno

La stella polare (CLAUDE.md, 1 ott 2026): ogni giorno il sistema deve essere un passo più vicino
all'obiettivo, e non solo in profitto: conta ciò che abbiamo CAPITO (come perdiamo, perché entriamo
in ritardo, perché il trailing chiude presto, quali idee funzionano dopo il gate). Ogni mattina il
controllo giornaliero aggiunge qui IN CIMA una sezione `## AAAA-MM-GG` con 2-5 punti, ognuno con il
numero e la sua fonte; se non c'è niente di nuovo lo scrive. La macchina pubblica l'ultima sezione
nel report giornaliero in dashboard (sezione «Cosa abbiamo capito»): non va copiata altrove.

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
