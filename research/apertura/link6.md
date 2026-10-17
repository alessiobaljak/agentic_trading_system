# Messaggio di apertura della sessione di ricerca LINK6 (protocollo 4)

Scritto dal coordinamento il 17 ottobre 2026; si approva con gli esiti del Passo 0. Il coordinamento lo manda così com'è
alla sessione nuova, aperta con il modello `claude-opus-5-5` (controllato con `get_session` dopo la creazione). Non
contiene fatti dal 2024-01-01 né risultati di campagne precedenti (`PROTOCOLLO_4.md`, sezione 3).

---

Leggi research/PROTOCOLLO_4.md per intero, poi research/config/guida_pratica_4.md e research/campagne/LINK6/STATO.md.

Sei la sessione di ricerca del protocollo 4 su LINKUSDT (campagna LINK6): esegui i Passi 1, 2, 3 e 4. Il Passo 0 e il
collaudo del metodo sono già fatti e approvati dal proprietario; le verifiche sulle monete di controllo e i Passi 5-9
li fa il coordinamento.

1. Il branch principale del repository è `claude/brave-albattani-1b12fv`: non lo tocchi e non apri pull request.
   Lavori solo sul branch `research/campagna/LINK6`, già creato: `git fetch origin research/campagna/LINK6` e
   `git checkout -b research/campagna/LINK6 origin/research/campagna/LINK6`. Controlla che l'intestazione di
   PROTOCOLLO_4.md dica «Approvato dal proprietario»: se no, fermati e avvisa l'utente.
2. Solo quando `git branch --show-current` stampa `research/campagna/LINK6`, scrivi il marcatore
   `research/.sessione` con `{"tipo": "campagna", "simbolo": "LINK6"}` (non è in git). Da lì il guardiano ti lascia
   vedere solo il necessario (sezione 12 del protocollo); la guida pratica spiega come lavorarci.
3. Controlla le versioni di Python e numpy (regola 11) e lancia
   `python3 -m pytest research/src/tests/test_guardiano_link6.py research/src/tests/test_dati_link6.py research/src/tests/test_statistica4.py -q -p no:cacheprovider`.
4. Primo commit e `git push -u origin research/campagna/LINK6` nei primi minuti, poi spesso: la macchina di questa
   sessione è temporanea. Se il push fallisce, fermati e avvisa l'utente. I titoli dei commit dicono cosa hai fatto,
   mai i risultati. Mai segreti nei commit: il repository è pubblico.
5. Gli strumenti in `research/src/` sono congelati dal collaudo: non si modificano. Se uno sembra sbagliato, STOP e
   lo scrivi all'utente.
6. Le verifiche sulle monete di controllo le chiedi al coordinamento con il canale della guida pratica (sezione 3bis)
   e aspetti la risposta.
7. Ogni STOP del protocollo lo scrivi all'utente in questa sessione e aspetti qui. Scrivi in italiano, senza sigle.

Comincia con: ESEGUI PASSO 1
