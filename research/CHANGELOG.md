# Registro delle correzioni a codice e dati della ricerca

Una riga per correzione: data, cosa, perché, campagne che potrebbe toccare. Solo in aggiunta.

| Data | Cosa | Perché | Campagne toccate |
|---|---|---|---|
| 2026-10-06 | Passo 0: nascono `src/motore.py`, `src/dati.py`, `src/statistica.py`, `src/guardiano.py` con i loro test | preparazione degli strumenti prima di qualunque campagna | nessuna |
| 2026-10-06 | Revisione avversaria del Passo 0: 36 difetti confermati e corretti (motore 14: gap in apertura, funding nella candela di chiusura, liquidazione con gap, buchi nella serie; dati 5: candela a cavallo del 2024, APERTURA.md vuoto, fine del vault; statistica 3: bootstrap degenere, entrate casuali, parità di Benjamini-Hochberg; guardiano 10: marcatore scrivibile, link simbolici, espansioni della shell, comandi che leggono tutto, variabili d'ambiente, git su altri branch; fatti 4: riferimenti) | prima di qualunque campagna | nessuna |
| 2026-10-07 | `src/tests/test_selezione_revisione.py` importava `yaml` senza che `pyyaml` fosse fra le dipendenze del repo: `pytest -q` dalla radice moriva in raccolta e i test di GitHub erano rossi dalle 07:38 (12 esecuzioni). Aggiunto `pyyaml` a `requirements.txt`, il test si salta se manca, la CI copre anche `research/src/tests` | correzione di strumenti, non di regole | BTCUSDT (branch aggiornato con l'unione del principale, nessuna lettura del contenuto); coordinamento |
