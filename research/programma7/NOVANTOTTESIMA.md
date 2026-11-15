# Prova 160 — G1 con una quota fissa di funding coperto su Bitcoin ed Ether (miscela a quote fisse), idea 145

Regole scritte il 15 novembre 2026 (giro delle 08:17) dallo strategy-scout, **prima di ogni calcolo**: nessun risultato di miscela guardato.
La prova la esegue strategy-researcher, il giudizio lo dà backtest-auditor. Il numero 160 è libero (ultima nel registro: 159). Non
spegne e non sostituisce niente: G1 resta com'è. Usa solo serie già calcolate: nessun dato nuovo da scaricare.

## Il perché forte
* **Richiesta del proprietario (14 novembre):** guadagni regolari, mettendo insieme quello che già abbiamo. Nel registro (`--cerca miscela`,
  `--cerca rischio uguale`, `--cerca combin`) le miscele provate sono tutte fra strategie di direzione (F5, M7, K2, N3, M8, prove 15-33); **mai
  G1 con il funding coperto** (prova 157): due guadagni di natura diversa (G1 prende il funding scegliendo le monete, con rischio di prezzo
  fra i due lati; il coperto prende il funding di Bitcoin ed Ether senza rischio di prezzo, discesa massima giornaliera sotto lo 0,5%).
  Correlazione dei rendimenti giornalieri fra le due: da misurare (la attesa è bassa); non si guarda prima.
* **Ragione economica e fonte:** il vantaggio di mettere insieme due fonti di rendimento poco correlate è la diversificazione di Markowitz
  (*Journal of Finance* 1952); qui il guadagno atteso non è lo Sharpe in sé (la parte coperta è piccola) ma **la discesa massima più bassa e
  i mesi più regolari** per il capitale piccolo del demo.
* **Avviso onesto:** il funding coperto da solo è FAIL della revisione per il margine (il rischio vero, borsa, liquidazione e USDT, non è
  misurato dal passato) e dal 2022 rende circa +4% l'anno (prova 157: la revisione). Una quota piccola non può alzare di molto il
  rendimento: se la discesa massima non scende di almeno 5 punti la miscela non serve. Probabilità media. Sotto i 500 USDT l'allocatore
  prevede una strategia sola (`allocazione/REGOLE.md`, sezione 3), quindi il risultato serve per quando il conto sarà più grande; si dice.

## Dati e periodo
* G1: rendimenti giornalieri netti **con lo stop** di `research/programma7/risultati_novantaseiesima/giorni_G1_con_stop.csv.gz` (stessa serie
  di G1 della prova 120, con funding vero); coperto: `research/programma7/risultati_novantacinquesima/giorni_B.csv.gz` (la lenta, B, quella
  che vale per le regole della prova 157; rendimenti per capitale). Verificare che le colonne e le date coincidano (se i nomi sono diversi, il
  ricercatore lo scrive nel rapporto, senza cambiare le regole).
* Periodo: i giorni in comune delle due serie, fino al 4 ottobre 2026 (`an.FINE`). Anni parziali segnati.

## La miscela (fissata qui)
* Pesi sul capitale: G1 con peso w e coperto con 1 − w, **riequilibrati ogni primo del mese** alla mezzanotte UTC (nel mese i pesi vanno alla
  deriva). Costo del riequilibrio: commissione a mercato 0,05% sul valore spostato, più lo scarto 0,01% (BTC, ETH) per la parte coperta e
  0,02% sulle altre monete per la parte di G1; in più la serie G1 e quella del coperto sono già nette delle loro spese.
* **Varianti (al massimo 2):** A: 80% G1 + 20% coperto. B: 60% G1 + 40% coperto. Nessun altro peso, nessuna variante dopo i risultati.
  Conta 2 prove (famiglia di G1: probabile, correlazione sopra il `TAGLIO`; si segna).

## L'esame (regole approvate dal proprietario il 9 novembre)
Passa se: netto dopo i costi positivo; **ogni anno positivo** (2021 e 2026 parziali, si segnano); t almeno 3; Sharpe corretto almeno 0,80 per
famiglie (`corretto_famiglie`, `programma6/asticella.py`; esempio `audits/repro/prova28_2026-11-11.py`, voce 11). **Per essere utile
(scritto prima):** (1) la discesa massima giornaliera della miscela almeno 5 punti sotto quella di G1 sugli stessi giorni; (2) lo Sharpe
della miscela non sotto quello di G1 di più di 0,05; (3) i mesi di calendario negativi in meno di G1 (conta dei mesi positivi su totale,
scritta). Se (1)-(3) non valgono la miscela è «non utile» anche se passa l'esame. Il rendimento l'anno (più basso di G1) si scrive accanto
in USDT su 1.000.
**Controlli descrittivi, non varianti:** correlazione giornaliera e settimanale G1-coperto; rendimento per anno; peggiori 10 giornate di G1
e cosa faceva il coperto; senza riequilibrio (pesi fissi ogni giorno, con costo zero) per vedere quanto pesano le spese.

## Cosa si consegna
Rapporto `research/programma7/RISULTATI_NOVANTOTTESIMA.md`, serie giornaliere in `research/programma7/risultati_novantottesima/`, script
`research/programma7/novantottesima.py`, registro delle varianti in `research/trials/novantottesima.csv` (non si tronca). Non si
modificano G1, il coperto, il paper né il demo.

## Riga per il registro (testo)
160: MX: G1 con una quota fissa di funding coperto su Bitcoin ed Ether (la lenta della prova 157), riequilibrata ogni primo del mese: A 80/20, B 60/40; esame scritto più «utile» (discesa massima di almeno 5 punti più bassa, Sharpe non sotto di più di 0,05, meno mesi negativi); idea 145 (`NOVANTOTTESIMA.md`)

## Nota della sessione principale del 15 novembre 2026, prima di ogni calcolo: la prova è in attesa
La serie del funding coperto indicata sopra (`risultati_novantacinquesima/giorni_B.csv.gz`) è il calcolo pubblicato della prova 157, che
backtest-auditor ha bocciato per il margine del perpetuo (`audits/reports/2026-11-15-PROVA157.md`: con il margine vero il conto sarebbe
stato liquidato; il guadagno vero è più basso). Usarla gonfierebbe la miscela. **La prova 160 non si calcola** finché il funding coperto
non è rifatto come prova nuova con una regola di margine scritta prima (decisione chiesta al proprietario il 15 novembre); allora la
miscela userà quella serie, con queste regole e senza altri cambi. Il numero 160 resta riservato.

**Aggiornamento del 15 novembre, sera**: il proprietario ha chiesto di rifare il funding coperto con il margine giusto: è la prova 161
(`NOVANTANOVESIMA.md`). Quando la 161 avrà le sue serie, la miscela userà la serie «161 B» (90 giorni, la lenta, come scritto sopra per la
157) al posto di quella della 157, con queste regole e senza altri cambi.
