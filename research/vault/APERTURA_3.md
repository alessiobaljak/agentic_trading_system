# Apertura del vault del protocollo 3 (Passo 5)

Scritto dal coordinamento il 17 ottobre 2026 alle 16:23 UTC (18:23 ora italiana), sul branch principale.

- **Comando del proprietario:** «APRI IL VAULT 3», scritto dal proprietario nella sessione di ricerca BTC51 e
  registrato da quella sessione nel suo log, copiato esatto (`research/campagne/BTC51/log.jsonl` sul branch
  `research/campagna/BTC51`, note delle 16:21:41 e 16:22:10 UTC, commit 946ccadb e 739a1853). Al coordinamento il
  proprietario ha scritto alle 18:17 ora italiana: «ho aperto direttamente io il vault nella campagna». La sessione di
  ricerca non ha creato questo file e non ha scaricato, caricato o letto dati del vault (stesse note).
- **Prerequisiti:** consegna completa (`consegna.md`, commit 1b222fb5 del 17 ottobre, 15:44 UTC, controllata dal
  coordinamento alle 15:46 UTC).
- **Periodo:** dal 2024-01-01 00:00 al 2026-09-30 23:59 UTC. Il vault si apre una volta sola.

## Candidati

Uno solo: **V-020** della campagna BTC51 (1h, long; filtro F6 giorni feriali; ingresso E11 funding regolato sotto
0,00%; ingresso a mercato; stop S1 a 2 ATR(14); uscita U2 dopo 24 candele).

Impronte SHA-256 dei file del candidato al commit della consegna 1b222fb5, uguali a quelle del Passo 3
(`validazione.md`, tabella del punto 1):

| File (in `research/campagne/BTC51/`) | SHA-256 |
|---|---|
| `candidati/V-020/regole.md` | `7eb2cc234a8dc6a64d09bb310c46968309e3b6b0532559cb95a0f28b39d129f7` |
| `codice/lotto_2.json` | `dfb3695b8b2d0aebe3236beab610f07f7bc394df00a2c86fed49f5e4fdfa8232` |
| `codice/lotto.py` | `455b5ca3a16e9c308b0de5625ea1943cf31abb342de3f063f1c5bf13d714a91f` |
| `codice/registro.py` | `fe3d7a140092fc887e0abd8042c40896c4402cc1ead5c15606f5bd72dc08b1ab` |

Strumenti: le 9 impronte del quarto giro del collaudo (`research/collaudo_3/esiti/giro4/impronte.json`), uguali sul
branch principale e su quello della ricerca (`python3 research/vault/passo5_btc51.py verifica`, «tutto_uguale»).

## Come si esegue

`research/vault/passo5_btc51.py`, committato prima di scaricare i dati del vault. Prima dell'apertura lo stesso
programma ha rifatto costruzione e validazione di V-020 e ha dato i numeri della sessione di ricerca: 180 trade,
+0,2227 R, p-value 0,01698 (17 su 1.001); 80 trade, +0,1666 R, profit factor 1,290, +0,0643 R a costi doppi.

Una sola esecuzione (`esegui`), che si rifiuta se `BTC51_giro_iniziato.json` esiste già; condizioni della sezione
10.3 e asticella di Benjamini-Hochberg al 10% della sezione 10.4. Risultati in `research/vault/BTC51_risultati.md`.

## Aggiunta del 17 ottobre, 16:36 UTC

Il proprietario ha scritto la frase esatta «APRI IL VAULT 3» anche al coordinamento, alle 18:36 ora italiana (dopo
che la sessione di ricerca gli aveva detto di scriverla qui). A quel punto il vault era già aperto (16:23 UTC) ed
eseguito una volta (16:24 UTC, `BTC51_giro_iniziato.json`): la frase conferma l'apertura, non apre un secondo giro.
Il vault si apre una volta sola e V-020 non si riesegue.
