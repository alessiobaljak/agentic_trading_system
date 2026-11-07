# Indice della ricerca (massimo 40 righe; lo aggiorna solo la sessione principale)

Leggi questo file per primo; poi solo i file che servono al tuo compito, mai «tutto all'inizio».

## Dove siamo (7 novembre 2026)
- Metodo in vigore: `programma7/METODO.md` (in giornata ed eventi), `programma6/METODO.md` (portafogli giornalieri e settimanali),
  `programma5/REGOLE.md` (a eventi, con la prova in avanti). Decisione del proprietario del 5 novembre: si migliora G1
  (`programma7/MIGLIORARE_G1.md`); un'idea nuova solo con un perché forte.
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
- Sharpe corretto per il numero di prove: `programma6/asticella.py`. Regola del proprietario: da 0,90 in su, ogni anno positivo,
  t sopra 3 (sezione 1 di `REGISTRO.md`).

## Dati (`data/`, 17 GB, fuori da git: mai con Read, solo con script)
- Pannello giornaliero con funding di tutti i perpetui in USDT: `programma6.seconda.pannello()`.
- Candele da 1 minuto delle 100 monete: `programma5.strumenti.motore5.minuti()`; a 1 ora: `programma6.esecuzione.ore_di()`.
- Giorni mancanti nell'archivio di Binance (il 28 ottobre 2026): `programma6/buchi_archivio.py`, `programma5/strumenti/buchi_archivio_minuti.py`.

## Rapporti degli agenti
- `reports/`: rapporti di strategy-researcher. Audit in `audits/`, revisioni del codice in `reviews/`, confronti paper e
  ricerca in `gate2/` (alla radice del repo).
