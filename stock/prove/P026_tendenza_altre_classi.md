# Prova 26 — la tendenza sulle altre classi di attivo, come parte nuova della miscela

Regole scritte il 12 novembre 2026 **prima di qualsiasi calcolo e prima di scaricare i prezzi** di questi fondi, committate prima di
lanciare il programma (idee I28 e I30 di `REGISTRO.md`; il proprietario, 11-12 novembre: «non puoi avere una sola strategia», «hai
pensato a come trovarne altre?»). Si conoscevano le prove 1-25: la tendenza a 12 mesi su SPY e QQQ da sola è bocciata (prova 5); la
miscela della prova 25 batte il tenere lo SPY sullo Sharpe (1,08 contro 0,89) ma è fatta solo di azioni americane e nel 2022 perde il
12,4%. Contano come **2 prove** (la parte nuova, e la miscela con la parte nuova): 67 nel conto.

## Perché dovrebbe funzionare

Su quasi tutte le classi di attivo il rendimento degli ultimi 12 mesi indica il segno del mese dopo (Moskowitz, Ooi, Pedersen, «Time
series momentum», *Journal of Financial Economics* 104, 2012), e classi diverse (obbligazioni, oro, materie prime, azioni estere)
salgono e scendono in momenti diversi dalle azioni americane: una parte poco legata alle altre abbassa le oscillazioni dell'insieme
anche se da sola guadagna poco. **Sospetti scritti prima:** la regola è nota a tutti da più di dieci anni; nel 2022 obbligazioni e
azioni sono scese insieme; nel 2016-2024 le obbligazioni lunghe e le azioni dei paesi emergenti hanno reso poco, e una regola che sta
spesso fuori (contanti a zero) può rendere quasi niente; sei fondi scelti da me adesso, non da uno studio.

## La regola (un numero solo, quello dello studio: 12 mesi)

* **I fondi** (scelti prima, i più scambiati della loro classe, tutti quotati da prima del 2016): TLT (titoli di stato americani a 20
  anni e più), IEF (a 7-10 anni), GLD (oro), DBC (materie prime), EFA (azioni dei paesi sviluppati fuori dagli Stati Uniti), EEM
  (azioni dei paesi emergenti).
* **Segnale:** all'ultimo giorno di borsa di ogni mese, per ogni fondo, il rendimento delle ultime 252 sedute con i dividendi. Sopra
  zero: il fondo ha il suo **sesto** del conto (98% investito); altrimenti quel sesto resta in contanti a rendimento zero. Ordini a
  mercato all'apertura del giorno di borsa dopo; ogni mese i sesti si rimettono uguali. Niente vendite allo scoperto, niente leva.
* **Prezzi:** al giorno da Yahoo (apertura e chiusura come scambiate, dividendi applicati dal simulatore a più titoli; nessuno di questi
  fondi ha avuto frazionamenti dal 2015), scaricati dal 2 gennaio 2015 al 31 dicembre 2024 e tenuti fuori dal repository. È un'altra
  fonte rispetto ad Alpaca (le chiavi non sono più nell'ambiente della sessione): si dice, e prima del demo si confronta con Alpaca.
* **Periodo:** decisioni dalla prima fine mese con 252 sedute di storia (gennaio 2016) al 31 dicembre 2024.
* **Costi** (lo scarto di questi fondi non è misurato: fissato prima, per prudenza): metà scarto 2,5 punti base e 1 punto base di
  slittamento per tutti; commissioni Interactive Brokers «fisso»; versione con i costi raddoppiati; capitale 100'000 dollari.

## L'esame: entrare nella miscela (idea I30, fissata qui)

La parte **entra nella miscela** se sono vere **tutte**, sui giorni in comune con la miscela della prova 25 (novembre 2016 → 2024):

1. lo Sharpe annuo della parte con i costi è sopra zero, anche con i costi doppi;
2. la correlazione fra i rendimenti giornalieri della parte e quelli della miscela è sotto 0,3;
3. la **miscela nuova** (tre quarti la miscela della prova 25, un quarto la parte nuova: quattro regole a pesi uguali, rimessi uguali
   ogni giorno) ha lo Sharpe annuo più alto della miscela della prova 25 **e** del tenere lo SPY.

Accanto, da leggere: lo Sharpe corretto per i tentativi della miscela nuova (soglia 0,95: l'8 novembre il proprietario ha detto che
non è un muro), la perdita massima, gli anni (il 2022 in particolare), lo Sharpe di ogni fondo da solo con la regola.

**Se entra:** revisore separato sul codice, poi il **periodo chiuso** (gennaio 2025 → settembre 2026) aperto **una volta** per la sola
parte nuova (la famiglia della tendenza non l'ha mai usato; conta come 1 prova in più): confermata se lì lo Sharpe con i costi è sopra
zero e la correlazione con il tenere lo SPY è sotto 0,5. Confermata, la miscela sul demo parte con quattro regole invece di tre
(`stock/avanti/MISCELA.md`, prima della sua prima operazione). **Se non entra:** bocciata nel registro, la miscela resta com'è.
