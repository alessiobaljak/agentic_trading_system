# Indice della ricerca (massimo 40 righe; lo aggiorna solo la sessione principale)

Leggi questo file per primo; poi solo i file che servono al tuo compito, mai «tutto all'inizio».

## Dove siamo (12 novembre 2026)
- Metodo in vigore: `programma7/METODO.md` (in giornata ed eventi), `programma6/METODO.md` (portafogli giornalieri e settimanali),
  `programma5/REGOLE.md` (a eventi, con la prova in avanti). Decisione del proprietario del 5 novembre: si migliora G1
  (`programma7/MIGLIORARE_G1.md`, voci 9-13 aperte, le porta avanti strategy-improver); dall'11 novembre la ricerca nuova va avanti
  a ogni giro: strategy-scout propone (`idee/LOG.md`), strategy-researcher esegue (prima in modalità verifica), backtest-auditor
  giudica. Riesame delle prove bocciate di poco: `riesame/ELENCO.md` (fatte la 28 e la 113; restano la 55 e la 96).
- Strategia principale: **G1** (regole `programma7/PRIMA.md`; ricalcolo indipendente `programma7/revisione_g1n/nucleo.py`); nel paper
  del bot con G11, G1N, F5 ed eventi; sul conto demo di Binance a 1.000 USDT dall'8 novembre.
- Vecchio sistema (gate, `bot/strategies/`, `backtesting/`): fermo dal 13 ottobre 2026. Protocolli 1-4 e campagne: chiusi; il vault
  di BTC dal 2024 è stato aperto il 17 ottobre (`vault/APERTURA_3.md`).

## Il registro delle prove
- `REGISTRO.md` (181 KB: non leggerlo tutto): una riga per prova, il conto delle prove, la coda delle idee (sezione 5).
  Interrogalo con `python3 -m research.src.registro --riepilogo` (oppure `--prova N`, `--cerca TESTO`).
- Ogni prova: file di regole committato **prima** del calcolo (`programma7/<NOME>.md`), codice (`<nome>.py`), risultati
  (`RISULTATI_<NOME>.md`, `risultati_<nome>/`).
- Varianti di ogni prova: `trials/<id_prova>.csv`, in sola aggiunta, scritte con `research/src/prove.py` (`registra`); riepilogo con
  `python3 -m research.src.prove --riepilogo`. Mai troncati, archiviati o riassunti.
- Esame approvato dal proprietario (9 e 11 novembre): Sharpe corretto da 0,80 contando le **famiglie di prove simili**
  (`programma6/asticella.py`, `gruppi`), ogni anno positivo, t da 3. Esempio di calcolo: `audits/repro/prova28_2026-11-11.py`.

## Dati (`data/`, 17 GB, fuori da git: mai con Read, solo con script)
- Pannello giornaliero con funding di tutti i perpetui in USDT: `programma6.seconda.pannello()`.
  **Attenzione al funding recente**: dopo l'ultimo file mensile dell'archivio (oggi il 31 ottobre) il pannello mette la media dei 90
  giorni prima, lo stesso numero ogni giorno (`seconda.riempi_funding`): per confronti con il paper o il demo su quei giorni si usa
  `programma6/paper/aggiorna.applica_stima(pan)` (la stima dall'indice del premio). Trovato il 13 novembre con la voce 9 di G1.
- Candele da 1 minuto delle 100 monete: `programma5.strumenti.motore5.minuti()`; a 1 ora: `programma6.esecuzione.ore_di()`.
- L'ultimo giorno pubblicato a metà dall'archivio non entra nel pannello (`seconda.giorni_parziali_in_coda`). Contratti su azioni:
  la ricerca li deve riconoscere dal tipo ufficiale di Binance, non dal nome (backlog P32).
- Giorni mancanti nell'archivio di Binance (il 28 ottobre 2026): `programma6/buchi_archivio.py`, `programma5/strumenti/buchi_archivio_minuti.py`.

## Rapporti degli agenti
- Il rapporto di strategy-researcher è il file dei risultati della prova (`RISULTATI_<NOME>.md`). Audit in `audits/`, revisioni del codice in `reviews/`, confronti paper e
  ricerca in `gate2/` (alla radice del repo).
