# Prova 38 — la stagionalità dello stesso mese: comprate le azioni salite di più nello stesso mese dell'anno scorso, vendute le scese

Regole scritte il 17 novembre 2026 **prima di qualsiasi calcolo** (idea nuova dalla ricerca su GitHub, `IDEE_DA_GITHUB.md`, N7;
aggiunta alla coda come I45 insieme a queste regole). Si conoscevano le prove 1-37: in particolare la 13 (il momento a 12 mesi,
bocciata), la 30 (il premio del comunicato, bocciata), la 31 (stessa forma: metà comprata e metà venduta nell'S&P 500, caduta alla
revisione). Contano come **2 prove** (la strategia da sola, e la miscela con lei): 93 nel conto.

## Perché dovrebbe funzionare

Heston e Sadka, «Seasonality in the cross-section of stock returns», Journal of Financial Economics 87 (2008): un'azione che è andata
bene in un mese di calendario tende ad andare bene nello stesso mese degli anni dopo. Keloharju, Linnainmaa e Nyberg, «Return
seasonalities», Journal of Finance 71 (2016): lo stesso succede in molti mercati e classi di attivo. La replica aperta di Chen e
Zimmermann (segnale `MomSeasonShort`, il solo rendimento dello stesso mese dell'anno prima) dà 1,15% al mese con t 7,6 sul campione
dello studio. È un effetto diverso dal momento (prova 13): conta solo lo stesso mese, non i 12 mesi.

**Sospetti scritti prima (forti):**

* **dopo la pubblicazione** (2008) gli effetti di questo tipo si riducono di molto (Chen e Velikov: in media 4-8 punti base al mese
  dopo costi e pubblicazione); il nostro 2017-2024 è tutto dopo;
* **solo le grandi** (S&P 500), dove gli effetti sono più deboli;
* **il portafoglio cambia quasi tutto ogni mese**: i costi pesano;
* **i bilanci cadono nello stesso mese ogni anno**: una parte della stagionalità può essere il premio del comunicato, che la prova 30
  ha trovato senza vantaggio dopo i costi. Si legge accanto quanta parte dei titoli scelti ha avuto un comunicato nello stesso mese
  dell'anno prima;
* **un anno solo di storia**: lo studio usa anche gli anni 2-20 indietro; con i prezzi di Alpaca dal 2016 si può usare solo l'anno
  prima.

## La regola

* **Quando:** alla chiusura dell'ultimo giorno di borsa di ogni mese, da gennaio 2017 a novembre 2024 (si tiene da febbraio 2017 a
  dicembre 2024); i giorni e la composizione dell'indice sono quelli di `dati/P028_membri.csv.gz`.
* **Chi può entrare:** i membri dell'S&P 500 in quel giorno con il prezzo (rettificato, simbolo di allora, Alpaca) sia alla fine del
  mese prima dello stesso mese dell'anno scorso sia alla fine di quel mese; se sono meno di 100, quel mese niente.
* **Il segnale:** il rendimento del titolo **nello stesso mese di calendario dell'anno prima** (dalla chiusura dell'ultimo giorno del
  mese precedente alla chiusura dell'ultimo giorno del mese; con la regola della prova 28 se il titolo sparisce).
* **La scelta:** i 50 con il segnale più alto si comprano, i 50 con il più basso si vendono allo scoperto (il 20% più alto e il 20%
  più basso, al massimo 50 ciascuno: nell'S&P 500 è circa un decimo, come lo studio); a pari valore in ordine alfabetico.
* **Quanto:** metà del conto nei comprati e metà nei venduti, a pesi uguali (come la prova 31); si ribilancia ogni fine mese.
* **Periodo:** fino al 31 dicembre 2024. Il periodo chiuso non si usa.

## I costi (fissati prima, come la prova 31)

Metà dello scarto misurato di ogni titolo (`dati/ESITO_CONTROLLI_UNIVERSO.md`), slittamento come nelle prove 28-31, commissioni
Interactive Brokers «fisso», **prestito dei venduti allo scoperto 0,5% l'anno**. Versione con tutti i costi raddoppiati.

## L'esame (uguale alle prove 28 e 30-37)

**Da sola:** (1) Sharpe annuo con i costi più alto del tenere lo SPY sugli stessi giorni; (2) Sharpe corretto ≥ 0,95 con tutte le
serie del conto; (3) Sharpe sopra zero con i costi doppi; (4) almeno il 60% dei trimestri in guadagno.

**Per entrare nella miscela** (idea I30 rafforzata): Sharpe con i costi sopra zero, anche con i costi doppi; correlazione con la
miscela della prova 25 sotto 0,3; la miscela nuova (tre quarti la miscela, un quarto la parte nuova) con lo Sharpe più alto della
miscela e del tenere lo SPY; il t dello Sharpe della parte almeno 1,3; la miscela nuova più alta in almeno l'80% di 2000 campionamenti
a blocchi di 20 giorni.

Da leggere accanto (non cambiano l'esito): il rendimento comprati meno venduti mese per mese prima dei costi (media, t, mesi
positivi); quanto cambia il portafoglio ogni mese; la quota di comprati e di venduti con un comunicato sui risultati (8-K 2.02,
`dati/P030_comunicati.csv.gz`) nello stesso mese dell'anno prima, e comprati meno venduti togliendo quelli con un comunicato atteso nel
mese tenuto; l'anno per anno; senza il 2020.

**Se passa uno dei due esami:** revisore separato, poi il periodo chiuso (dal 2 gennaio 2025 al 30 settembre 2026) **una volta**: la
famiglia «stagionalità» non l'ha mai usato.
