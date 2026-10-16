# Messaggio di apertura della sessione di ricerca BTC51 (protocollo 3) — BOZZA

Scritto dal coordinamento il 16 ottobre 2026, da approvare dal proprietario insieme agli esiti del Passo 0. Il
coordinamento lo manda così com'è alla sessione nuova, aperta con il modello `claude-opus-5-5` e ultracode
(controllati con `get_session` dopo la creazione).

---

Leggi research/PROTOCOLLO_3.md per intero, poi research/config/guida_pratica_3.md e research/campagne/BTC51/STATO.md.

Sei la sessione di ricerca del protocollo 3 su BTCUSDT (campagna BTC51): esegui i Passi 1, 2, 3 e 4. Il Passo 0 e
il collaudo del metodo sono già fatti e approvati dal proprietario; i Passi 5-8 li fa il coordinamento.

1. Il branch principale del repository è `claude/brave-albattani-1b12fv`: non lo tocchi e non apri pull request.
   Lavori solo sul branch `research/campagna/BTC51`, già creato: `git fetch origin research/campagna/BTC51` e
   `git checkout -b research/campagna/BTC51 origin/research/campagna/BTC51`. Controlla che l'intestazione di
   PROTOCOLLO_3.md dica «Approvato dal proprietario»: se dice «BOZZA», fermati e avvisa l'utente.
2. Solo quando `git branch --show-current` stampa `research/campagna/BTC51`, scrivi il marcatore
   `research/.sessione` con `{"tipo": "campagna", "simbolo": "BTC51"}` (non è in git). Da lì il guardiano ti
   lascia vedere solo il necessario (sezione 0 del protocollo); la guida pratica spiega come lavorarci.
   Lancia `python3 -m pytest research/src/tests/test_guardiano_btc51.py research/src/tests/test_dati_btc51.py -q -p no:cacheprovider`.
3. Primo commit e `git push -u origin research/campagna/BTC51` nei primi minuti, poi spesso: la macchina di questa
   sessione è temporanea. Se il push fallisce, fermati e avvisa l'utente. I titoli dei commit dicono cosa hai
   fatto, mai i risultati. Mai segreti nei commit: il repository è pubblico.
4. Gli strumenti in `research/src/` sono congelati dal collaudo: non si modificano. Se uno sembra sbagliato, STOP e
   lo scrivi all'utente.
5. Ogni STOP del protocollo lo scrivi all'utente in questa sessione e aspetti qui. Scrivi in italiano, senza sigle.

Comincia con: ESEGUI PASSO 1
