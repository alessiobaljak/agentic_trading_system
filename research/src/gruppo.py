"""L'esecutore unico dell'esame della campagna di gruppo (Passo 4bis del protocollo).

Testo: ``research/campagne/GRUPPO/regole.md`` (qui sotto «regole.md»), sezione 0,
punto 4, e sezione 13. Ogni numero dell'esame di gruppo (stima dei trade,
baseline, blocco, pavimento, «nettamente», p-value, metriche, verifiche) lo
calcola QUESTO modulo con gli strumenti della sezione 13 (``dati``, ``motore``,
``statistica``), e nessun altro calcolo. La sessione scrive solo le funzioni
che creano la strategia (il contratto qui sotto) e i suoi script di lavoro.

Le funzioni pubbliche
---------------------
* ``conta_trade_di_gruppo`` (sezione 4, punti 2-4): ``motore.conta_trade`` una
  volta per moneta, la somma, il tetto di concentrazione, l'esito (scarto o no).
* ``esame_di_gruppo`` (sezioni 5, 6, 7 e 8.1): test su ogni moneta, trade
  sommati, blocco, (a) e (b) per moneta e combinate, strategie sfasate e
  pavimento, confronti, candidato, metriche, verifiche da riportare; in
  validazione, in una sessione di campagna, controlla prima il via libera.
  Salva i trade sommati e il file di avanzamento.
* ``controllo_positivo`` (sezione 5, punto 10): ingressi che guardano avanti,
  giudicati con l'esame di gruppo senza ritardo e con il ritardo di una barra.
* ``esame_vault`` (sezione 9, e sezione 10, punto 2, per il trasferimento), per
  il coordinamento: il ``criterio_vault`` sui trade sommati con le sfasate del
  vault e il tasso del caso.
* ``asticella_di_gruppo`` (sezione 7, punti 4-5): Benjamini-Hochberg sui
  p-value di validazione dei candidati del gruppo.
* ``controlla_via_libera`` (sezione 7, punto 2), ``parametri_moneta``,
  ``regole_del_gruppo``, ``carica_modulo_variante``,
  ``impronte_degli_strumenti`` e il caricatore ``CaricatoreDisco``.

Il contratto con le funzioni della sessione (sezione 13)
--------------------------------------------------------
Vale allo stesso modo per la sessione di gruppo e per la prova a placebo, con la
sola differenza di ``ingressi_placebo`` (punto 5).

1. **Il modulo della variante** e' UN file ``.py`` (di regola in
   ``research/campagne/GRUPPO/codice/``). ``gruppo.py`` lo esegue per percorso
   dai byte di cui ha calcolato l'impronta SHA-256, DA CAPO PER OGNI PEZZO DI
   LAVORO (una moneta): se il file cambia durante un esame, l'esame si ferma con
   un errore. Puo' importare solo la libreria standard, numpy e
   ``research.src.motore`` (per ``Segnale``): gli import si controllano sul testo
   (``controlla_import_della_variante``), perche' un altro file di ``codice/``
   non sarebbe nell'impronta. Non legge file e non usa la rete. Un dizionario o
   una cache al livello del modulo nascono vuoti per ogni moneta (il modulo e'
   eseguito da capo), quindi non portano dati di una moneta in un'altra (regole.md,
   sezione 3, punto 3); dentro il pezzo di una moneta pero' le esecuzioni si
   susseguono (test, (a), (b)...): la variante non tiene stato fuori dalle sue
   istanze.
2. **Le quattro funzioni**, al livello del modulo, ricevono il contesto ``ctx``
   e i parametri ``p`` (il dizionario JSON della registrazione; ogni chiamata ne
   riceve una copia nuova, ``json.loads(json.dumps(p))``):

   * ``crea_variante(ctx, p)`` -> ``crea()``: senza argomenti, restituisce una
     strategia NUOVA del motore, ``strategia(storia, posizione) -> Segnale |
     "chiudi" | None``, con le regole complete della variante;
   * ``crea_a(ctx, p)`` -> ``crea()``: la strategia della baseline (a), cioe' la
     variante senza la condizione d'ingresso dell'ipotesi e senza filtri:
     stessa direzione, uscita, stop e target, entra a ogni barra in cui e'
     libera, dalla prima barra in cui la variante puo' entrare (sezione 8 del
     protocollo);
   * ``crea_casuale(ctx, p)`` -> ``crea_casuale(ingressi)``: dato l'insieme
     (``frozenset``) degli indici delle barre di segnale, la strategia casuale
     della (b), delle sfasate, del controllo positivo e di ``ingressi_placebo``:
     alla CHIUSURA di quelle barre, se non ha una posizione, emette il segnale
     della variante (stessa direzione, stesso calcolo di stop e target), poi
     esce con la sua uscita; non emette segnali fuori da ``ingressi``;
   * ``crea_segnale(ctx, p)`` -> ``crea_segnale()``: la funzione
     ``segnale(storia) -> Segnale | None`` che calcola il segnale della
     variante SENZA la condizione d'ingresso, None dove non si puo' calcolare
     (riscaldamento): serve a ``motore.barre_vietate_segnale_non_valido``.

   Ogni esecuzione del motore chiama ``crea()`` (o ``crea_casuale(ingressi)``,
   o ``crea_segnale()``) e usa un'istanza nuova (sezione 7 del protocollo).
   ``crea_variante``, ``crea_a``, ``crea_casuale`` e ``crea_segnale`` si
   chiamano una volta per moneta e per pezzo di lavoro. Su ogni moneta, subito
   dopo il test, ``crea_casuale`` con le barre di segnale dei trade del test deve
   rifare gli stessi trade, campo per campo: se no ``ContrattoNonRispettato``
   (la (b) e le sfasate userebbero un'altra uscita senza avviso).
3. **Il contesto** ``ctx`` (``Contesto``) lo costruisce SOLO ``gruppo.py``, uno
   per moneta e per pezzo. Non contiene il simbolo, ne' la posizione j, ne'
   dati di altre monete del gruppo (regole.md, sezione 3, punto 3: niente
   strategie fra monete). Contiene, in sola lettura:

   * ``ctx.timeframe`` (es. ``"1h"``) e ``ctx.ms_per_barra``;
   * ``ctx.btc_chiuse_entro(ts)``: le candele LAST di BTCUSDT dello stesso
     timeframe con ``close_ts <= ts`` (sezione 2, punto 2), dal 2020-01-01;
   * ``ctx.funding_regolato_entro(ts)``: i regolamenti del funding della moneta
     (coppie ``(ts, tasso)``, gli stessi che il motore applica: in un mese
     senza file di funding non ce ne sono, sezione 2, punto 9) con istante
     ``<= ts``.

   Niente sguardo avanti: le due funzioni non vanno mai oltre la chiusura
   dell'ultima barra che la strategia (o la funzione del segnale) ha ricevuto
   dal motore, che ``gruppo.py`` registra a ogni chiamata; un ``ts`` futuro
   restituisce solo cio' che e' gia' chiuso o regolato adesso, e durante la
   creazione (le quattro funzioni, ``crea()``, ``crea_casuale(ingressi)``,
   ``crea_segnale()``: prima di ogni barra) restituiscono una sequenza vuota.
   Restituiscono una vista in sola lettura (``motore.StoriaChiusa``) su una
   lista che contiene solo cio' che e' gia' chiuso, mai la serie intera; ``ts``
   e' un intero in ms. La strategia riceve dal motore, come sempre, le sole
   barre chiuse della moneta (il last allineato al mark).
4. **Cosa fa gruppo.py intorno alle funzioni della sessione**, per ogni moneta:

   * i ``Parametri`` del motore (``parametri_moneta``): commissione, rischio,
     leva, modalita' di margine, margine di mantenimento, margine minimo dalla
     liquidazione e riempimento intra-barra dalla parte comune di
     ``parametri.yaml``, il capitale dalla sezione ``gruppo``
     (``capitale_per_moneta_usdt``), lo slippage dalla fascia della scheda
     (``dati.leggi_scheda_gruppo``), piu' ``moltiplicatore_costi``,
     ``ritardo_barre`` e ``riempimento_intrabarra`` della chiamata, uguali su
     tutte le monete e per test, (a), (b) e sfasate;
   * i dati (``CaricatoreDisco``): last e mark con ``dati.carica_serie_allineate``,
     funding con ``dati.carica_funding``, BTCUSDT con ``dati.carica_candele`` e i
     mesi sotto la liquidita' con ``dati.mesi_sotto_liquidita``;
   * il filtro di liquidita' (sezione 2, punto 7) AVVOLGENDO la strategia della
     variante e della (a): un ``Segnale`` emesso alla chiusura di una barra di un
     mese sotto la soglia diventa ``None`` (la posizione gia' aperta esce con la
     sua uscita). Le stesse barre (``dati.barre_vietate_liquidita``) sono vietate
     agli ingressi della (b) e delle sfasate. E' lo stesso filtro in
     ``conta_trade``, nel test, nella (a) e nel vault.
5. **ingressi_placebo** (sezione 11, punto 1, e sezione 13): senza un marcatore
   di campagna, ``conta_trade_di_gruppo`` ed ``esame_di_gruppo`` accettano, al
   posto di ``crea_variante``, gli ingressi gia' calcolati per moneta:
   {simbolo: istanti (``ts`` di apertura, ms) delle barre di segnale}. La
   strategia della variante e' allora ``crea_casuale(ingressi)`` del modulo (con
   gli indici di quelle barre nella serie della moneta, e il filtro di
   liquidita' come per una variante); un istante che non e' una barra della
   serie si salta e si conta. Con un marcatore di campagna (qualunque simbolo)
   ``ingressi_placebo`` alza ``dati.VietatoInCampagna``. Con ``ingressi_placebo``
   ``esame_di_gruppo`` vuole ``cartella_campagna``, fuori da ``research/campagne/``
   (i numeri della prova non vanno li': regole.md, sezione 11, punto 5).

Il marcatore e il via libera
----------------------------
``gruppo.py`` legge il marcatore come ``dati.py`` (``dati.marcatore_di_campagna``,
nella radice del progetto, mai nella cartella di lavoro o di uscita). Con un
marcatore di campagna (qualunque simbolo):

* ``esame_di_gruppo`` in validazione fa per prima cosa ``controlla_via_libera`` su
  ``<radice del progetto>/research/campagne/GRUPPO/via_libera_validazione.md``,
  qualunque sia ``cartella_campagna`` (regole.md, sezione 7, punto 2.4);
* ``ingressi_placebo`` si rifiuta (sezione 13), e cosi' anche ``monete``,
  ``caricatore`` e una ``radice`` diversa da ``research/`` del progetto: in campagna
  si esamina solo l'elenco ufficiale con i dati della Fase 0 (sezione 0, punto 4);
* ``esame_vault`` si rifiuta (e' del coordinamento);
* le candele di BTCUSDT del timeframe dell'esame devono esserci e coprire la serie
  di ogni moneta (``_controlla_btc``); fuori campagna se ne riporta solo il numero.

Questi controlli stanno nel corpo comune dell'esame (``_esame``), non solo nelle
funzioni pubbliche. Il via libera si controlla com'e' scritto nella sezione 7,
punto 2.3 (il file nomina le cinque impronte e sono quelle dei file sul disco):
ferma gli errori, non uno script scritto apposta per scriversi un via libera.
Il marcatore lo legge il processo che avvia l'esame e lo passa ai pezzi.

Senza marcatore (coordinamento, prova a placebo, test) niente di tutto questo.

Come gira un esame (``esame_di_gruppo``)
----------------------------------------
* Periodi: ``dati.periodi_gruppo`` sui primi mesi delle schede di TUTTE le
  monete del gruppo (con l'elenco ufficiale si controlla che il taglio sia
  quello di ``parametri.yaml``). In costruzione ogni moneta gira dal primo
  giorno dei suoi dati al 2023-01-16; in validazione sulla serie dall'inizio
  della costruzione al 2023-12-31, e contano solo i trade ENTRATI dal
  2023-01-17 (sezione 1, punto 5).
* Fase 1, un pezzo per moneta: il test; per le monete con trade la (a)
  (``baseline_da_trade`` sui SUOI trade, con il SUO blocco), le barre vietate
  della (b) (segnale non valido, mesi sotto la liquidita', in validazione le
  barre prima del 2023-01-17) e la (b) con ``simula_baseline_casuale``, 200
  simulazioni con i semi da 1000·j a 1000·j + 199 (sezione 5, punti 3-4).
* Fase 2, un pezzo per moneta con trade: le strategie sfasate
  (``motore.simula_sfasamento_comune``) con la griglia comune
  (``statistica.griglia_sfasamenti``), che dipende dalla finestra unione e
  dalla durata massima dei trade di TUTTE le monete, quindi si calcola dopo la
  fase 1 (sezione 5, punto 5). Le sfasate vietano le stesse barre della (b)
  (lo si controlla con l'impronta della maschera).
* Combinazioni, solo alla fine e da tutti i pezzi, sempre in ordine dei
  caratteri dei simboli: trade sommati in ``statistica.ordina_trade_di_gruppo``,
  ``motore.metriche_di_gruppo``, ``statistica.lunghezza_blocco``,
  ``baseline_da_trade_di_gruppo``, ``baseline_casuale_di_gruppo``,
  ``pavimento_sfasamento``, ``contro_baseline`` con ``pavimento_minimo``,
  ``percentile_del_candidato``, ``effetto_grappolo``, ``estremi_di_gruppo``,
  ``posizioni_aperte_insieme``.

Processi e avanzamento (sezione 12, punto 6, e sezione 13)
---------------------------------------------------------
* Una moneta per processo: ``processi`` processi (4 di norma) avviati con il
  metodo ``spawn`` (ogni processo importa il codice da capo, niente stato
  ereditato) in un ``concurrent.futures.ProcessPoolExecutor``, le monete piu'
  lunghe per prime; ``processi=1`` lavora nel processo che chiama. Il modulo
  della variante si esegue da capo per ogni pezzo. Ogni pezzo e' deterministico
  e le combinazioni sommano sempre nello stesso ordine: l'esito e' identico bit
  per bit con 1 o 4 processi e con qualunque ordine delle monete. Ogni processo
  controlla di avere lo stesso codice e lo stesso ``parametri.yaml`` del
  processo che ha avviato l'esame. Un processo che muore senza un errore (per
  esempio ucciso dal sistema per memoria finita) ferma l'esame con
  ``ErroreDiMoneta``, invece di lasciarlo fermo per sempre; un ``SystemExit`` del
  codice della variante diventa ``ErroreDiMoneta``.
* **Uno script che chiama ``gruppo.py`` con ``processi`` > 1 deve avere
  ``if __name__ == "__main__":``** intorno alla chiamata: con il metodo ``spawn``
  ogni processo del gruppo rilegge lo script, e senza la guardia proverebbe a
  ripartire l'esame da capo (oggi l'esame si ferma subito con
  ``ErroreDiMoneta``; con il ``Pool`` di prima ripartiva all'infinito).
* Il file di avanzamento ``<cartella_campagna>/avanzamento/<id>_<periodo>.jsonl``
  e' in sola aggiunta: una riga JSON per pezzo finito, con l'impronta
  dell'esame (SHA-256 dei file della sezione 13, del modulo della variante e di
  ``p``, piu' timeframe, periodo, opzioni, monete e origine degli ingressi),
  l'impronta dei dati che il pezzo ha letto (``_impronta_dei_dati``: last, mark,
  funding, mesi sotto la liquidita', slippage, BTCUSDT, periodo; per le sfasate
  anche i loro ingressi) e i secondi di calcolo. Alla ripresa ogni pezzo va
  comunque a un processo, che ricarica i dati: si riprende la riga salvata solo
  se l'impronta dell'esame E quella dei dati sono le stesse, se no si ricalcola
  (dati cambiati, un altro caricatore, un'altra versione). Una riga interrotta
  a meta' si ignora. Anche un pezzo appena calcolato passa dal JSON prima di
  entrare nelle combinazioni: un esame ripreso e uno fatto tutto di fila danno
  gli stessi numeri. ``ripresa`` nel risultato dice quanti pezzi si sono ripresi
  e quanti calcolati.
* I dati di un pezzo nel file sono compatti (si committano, regole.md,
  sezione 8, punto 1): per le sfasate, per ogni s, il numero dei trade e la
  somma esatta (``math.fsum``) dei loro R (``statistica.riassunto_sfasate``);
  M'(s) e n'(s) li calcola ``statistica.medie_sfasate`` (una sola lettura,
  indipendente dall'ordine), in costruzione, in validazione e nel vault.

Scelte documentate
------------------
* I risultati sono dizionari JSON (niente array numpy; chiavi stringa; anni
  come stringhe). I valori non finiti restano float (``t`` = -inf per le
  varianti non valutabili, sezione 8 del protocollo; NaN per un numero che non
  esiste): ``json.dumps`` li scrive ``Infinity``/``NaN`` e ``json.loads`` li rilegge.
* Il drawdown e' positivo, come ``motore.calcola_metriche``.
* La durata massima di un trade in barre e' arrotondata per eccesso (sezione 5,
  punto 5).
* Il buy and hold di gruppo di un anno e' la somma, sulle monete con trade che
  hanno candele in quell'anno, di w_j x il loro rendimento, con gli stessi w_j =
  n_j / N (sezione 5, punto 8: solo contesto); ``peso_presente`` e' la somma dei
  w_j delle monete presenti in quell'anno (meno di 1 negli anni in cui qualche
  moneta non era ancora quotata).
* Una variante non valutabile, anche solo per la (a), ha ``t`` = -inf e
  ``p_value`` 1 (sezione 8 del protocollo) e in validazione
  ``p_value_asticella`` 1 (sezione 7, punto 5); il ``t`` e il ``p_value`` del
  confronto con la (b) restano in ``baseline_b``.
* Le candele di BTCUSDT passate alle funzioni della variante si riportano in
  ``btc`` (numero, prima e ultima).
* La (b) di una moneta su cui gli ingressi casuali non entrano si riconosce
  dal messaggio di ``statistica.entrate_casuali_per_semi`` («impossibile
  piazzare»): la moneta entra nella (b) di gruppo come «ingressi che non
  entrano» e la variante e' non valutabile (sezione 5, punto 4).
* Se il pavimento delle sfasate non e' valutabile (meno di 2 sfasate con
  trade) la variante e' non valutabile: i due confronti si calcolano con
  ``contro_baseline`` su una copia della baseline segnata non valutabile, cosi'
  restano la sola lettura di «non valutabile» (t = -inf, p-value 1). Accanto,
  solo come informazione, c'e' il confronto senza il pavimento delle sfasate
  (``senza_pavimento_sfasate``), che la prova a placebo riporta (sezione 15).
* Nel vault (``esame_vault``) ogni moneta gira dal primo giorno dei suoi dati
  (indicatori caldi, come in validazione) e contano i trade entrati dal
  2024-01-01. I trade delle sfasate del vault arrivano dai processi in forma
  compatta (32 byte per trade) e diventano ``TradeSfasato`` una s alla volta.
  Memoria attesa nel processo principale (stima, non misurata su un vault
  vero): circa 32 byte x trade sfasati, cioe' circa 0,2 GB a 1h con 7.000 trade
  per sfasata e circa 1 GB a 15m con 30.000; in ogni processo del gruppo la
  tabella della (b) di una moneta a 15m su quattro anni arriva a circa 1 GB.
"""

from __future__ import annotations

import ast
import dataclasses
import hashlib
import json
import math
import multiprocessing
import operator
import os
import pickle
import re
import sys
import time
import traceback
import types
from array import array
from bisect import bisect_left, bisect_right
from collections import Counter
from concurrent.futures import FIRST_COMPLETED, ProcessPoolExecutor, wait
from concurrent.futures.process import BrokenProcessPool
from datetime import date, timedelta
from pathlib import Path
from typing import Any, Callable, Dict, Iterator, List, Mapping, Optional, Sequence, Tuple, Union

import numpy as np

from research.src import dati, motore, statistica
from research.src.guardiano import MONETA_RIFERIMENTO, leggi_monete_gruppo
from research.src.motore import Candela, Parametri, Segnale, StoriaChiusa, TradeSfasato

# ---------------------------------------------------------------------------
# Costanti
# ---------------------------------------------------------------------------

#: La radice del progetto (la cartella che contiene research/), calcolata da questo file:
#: da qui si legge l'elenco ufficiale delle monete (``guardiano.leggi_monete_gruppo``).
RADICE_PROGETTO = Path(__file__).resolve().parents[2]
#: I due periodi che ``esame_di_gruppo`` giudica (regole.md, sezione 5); il vault ha ``esame_vault``.
PERIODI = ("costruzione", "validazione")
#: Il file del via libera (regole.md, sezione 7, punto 2), relativo alla radice del progetto.
VIA_LIBERA = Path("research") / "campagne" / "GRUPPO" / "via_libera_validazione.md"
#: Le candele di BTCUSDT per ``ctx.btc_chiuse_entro`` partono da qui: l'archivio mensile
#: dei futures comincia a gennaio 2020 (``parametri.yaml``, ``periodi.in_sample.nota``).
INIZIO_ARCHIVIO = date(2020, 1, 1)
#: «la quota delle monete con almeno 10 trade il cui R medio supera la propria b_j»
#: (regole.md, sezione 6, punto 2: soglia di processo scritta solo li', sezione 0, punto 5).
TRADE_MINIMI_PER_LA_QUOTA_SOPRA_B = 10
#: Le quattro funzioni del contratto (docstring del modulo, punto 2).
FUNZIONI_DEL_CONTRATTO = ("crea_variante", "crea_a", "crea_casuale", "crea_segnale")
#: Versione del formato delle righe di avanzamento: una riga di un altro formato non si riusa.
#: 2 (10 ottobre 2026): ogni riga ha l'impronta dei dati della moneta (``impronta_dati``).
FORMATO_AVANZAMENTO = 2
#: Gli import che il modulo della variante puo' fare oltre alla libreria standard (contratto, punto 1).
IMPORT_AMMESSI = ("numpy", "research.src.motore")
#: I campi di un trade del motore che l'esame conserva (file dei trade e avanzamento).
CAMPI_TRADE = ("direzione", "ts_entrata", "ts_uscita", "entrata", "uscita", "stop", "target", "quantita",
               "esito", "r", "pnl", "funding_pagato", "ridotto", "violazione_liquidazione")
GIORNO_MS = statistica.GIORNO_MS
SALTI = ("fuori_finestra", "buco", "vietata", "posizione_aperta")

#: I file della sezione 13 che il via libera e l'impronta dell'esame nominano (regole.md,
#: sezione 7, punto 2, e sezione 11, punto 1), con il percorso del file davvero in uso.
_FILE_DEL_CODICE: Dict[str, Path] = {
    "research/src/gruppo.py": Path(__file__).resolve(),
    "research/src/statistica.py": Path(statistica.__file__).resolve(),
    "research/src/motore.py": Path(motore.__file__).resolve(),
    "research/src/dati.py": Path(dati.__file__).resolve(),
}
NOME_PARAMETRI = "research/config/parametri.yaml"
#: I cinque file del via libera, nell'ordine di regole.md, sezione 11, punto 1.
FILE_DEL_VIA_LIBERA = tuple(_FILE_DEL_CODICE) + (NOME_PARAMETRI,)


def _sha256_file(percorso: Path) -> str:
    """SHA-256 esadecimale di un file (regole.md, sezione 7, punto 2: «sha256sum»)."""
    sha = hashlib.sha256()
    with open(percorso, "rb") as flusso:
        for blocco in iter(lambda: flusso.read(1 << 20), b""):
            sha.update(blocco)
    return sha.hexdigest()


#: Le impronte dei quattro file .py prese all'import di questo modulo: il codice che gira
#: e' quello in memoria, e un esame lo confronta con i file sul disco e fra i processi.
_IMPRONTE_DEL_CODICE_IN_MEMORIA: Dict[str, str] = {nome: _sha256_file(p) for nome, p in _FILE_DEL_CODICE.items()}


class ViaLiberaNonValida(Exception):
    """La validazione non puo' partire: il via libera manca o non torna (regole.md, sezione 7, punto 2)."""


class ContrattoNonRispettato(TypeError):
    """Il modulo della variante non rispetta il contratto della docstring del modulo (regole.md, sezione 13)."""


class ErroreDiMoneta(RuntimeError):
    """Un pezzo di lavoro di una moneta e' fallito: il messaggio dice quale pezzo, quale moneta e perche' (regole.md, sezione 2, punto 9)."""


# ---------------------------------------------------------------------------
# Parametri congelati (parametri.yaml: parte comune e sezione gruppo)
# ---------------------------------------------------------------------------


def _voce(albero: Mapping, *nomi: str) -> Any:
    """Il valore ``albero[nomi[0]][nomi[1]]...`` di ``parametri.yaml``; ValueError se manca (regole.md, sezione 0, punto 5)."""
    valore: Any = albero
    for nome in nomi:
        if not isinstance(valore, Mapping) or nome not in valore:
            raise ValueError(f"parametri.yaml: manca {'.'.join(nomi)}")
        valore = valore[nome]
    return valore


def _numero(valore: Any, dove: str, intero: bool = False) -> Union[int, float]:
    """Un numero finito e positivo di ``parametri.yaml`` (un booleano non e' un numero; regole.md, sezione 0, punto 5)."""
    if isinstance(valore, bool) or not isinstance(valore, (int, float)) or not math.isfinite(valore) or valore <= 0:
        raise ValueError(f"parametri.yaml, {dove}: atteso un numero positivo, trovato {valore!r}")
    if intero:
        if int(valore) != valore:
            raise ValueError(f"parametri.yaml, {dove}: atteso un intero, trovato {valore!r}")
        return int(valore)
    return float(valore)


def regole_del_gruppo(percorso: Optional[Union[str, Path]] = None) -> Dict[str, object]:
    """I numeri dell'esame di gruppo letti da ``parametri.yaml`` (regole.md, sezione 0, punto 5, e sezione 13).

    Si legge il file del progetto (``dati.PERCORSO_PARAMETRI``, lo stesso del via
    libera); ``percorso`` serve solo ai test. Il file si legge UNA volta in
    byte: ``impronta`` e' quella dei byte da cui escono i numeri.

    Parte comune: ``commissione_per_lato`` (``fatti.commissione_taker_per_lato``),
    ``rischio_per_trade``, ``leva_max``, ``modalita_margine`` (la proposta
    approvata), ``tasso_margine_mantenimento`` (``fatti.regole_dimensione_bot``),
    ``margine_minimo_da_liquidazione``, ``riempimento_intrabarra``,
    ``timeframe_ammessi``, ``bootstrap_ricampionamenti`` e ``bootstrap_seme``,
    ``pf_minimo_vault`` e ``percentile_caso_vault`` (``regole_esame``).
    Sezione ``gruppo``: ``capitale_per_moneta``, ``trade_minimi``,
    ``quota_massima_moneta``, ``simulazioni_baseline_casuale``, ``passo_semi``
    (il 1000 di «1000*j + s»), ``sfasamenti_pavimento``, ``fittizie_vault``,
    ``margine_sfasamento_giorni``, ``anni_trade_minimi``,
    ``trade_migliori_tolti``, ``giorni_migliori_tolti``,
    ``monete_migliori_tolte``, ``asticella_q``, ``taglio_costruzione``,
    ``inizio_validazione`` e ``numero_monete``. ValueError se una chiave manca o
    non ha la forma attesa.
    """
    import yaml  # qui: serve solo a questa funzione

    file = Path(percorso) if percorso is not None else Path(dati.PERCORSO_PARAMETRI)
    contenuto = file.read_bytes()
    albero = yaml.safe_load(contenuto)
    if not isinstance(albero, Mapping):
        raise ValueError(f"{file}: atteso un dizionario YAML")
    gruppo = _voce(albero, "gruppo")
    semi = str(_voce(gruppo, "semi_baseline_casuale"))
    trovato = re.match(r"\s*(\d+)\s*\*\s*j\s*\+\s*s\b", semi)
    if not trovato:
        raise ValueError(f"parametri.yaml, gruppo.semi_baseline_casuale: forma «N*j + s» attesa, trovato {semi!r}")
    modalita = _voce(albero, "fatti", "regole_dimensione_bot", "modalita_margine_proposta")
    riempimento = _voce(albero, "regole_esame", "riempimento_intrabarra")
    if modalita not in ("isolated", "cross") or riempimento not in ("stop_prima", "target_prima"):
        raise ValueError(f"parametri.yaml: modalita' di margine {modalita!r} o riempimento {riempimento!r} sconosciuti")
    trade_minimi = _voce(gruppo, "trade_minimi")
    fase4 = _voce(gruppo, "fase4")
    seme = _voce(albero, "regole_esame", "bootstrap", "seme")
    if isinstance(seme, bool) or not isinstance(seme, int) or seme < 0:
        raise ValueError(f"parametri.yaml, regole_esame.bootstrap.seme: atteso un intero >= 0, trovato {seme!r}")
    taglio = _voce(gruppo, "taglio_costruzione")
    inizio_validazione = _voce(gruppo, "inizio_validazione")
    if not isinstance(taglio, date) or not isinstance(inizio_validazione, date):
        raise ValueError("parametri.yaml: gruppo.taglio_costruzione e gruppo.inizio_validazione devono essere date")
    quota = _numero(_voce(gruppo, "quota_massima_moneta"), "gruppo.quota_massima_moneta")
    if quota > 1:
        raise ValueError(f"parametri.yaml, gruppo.quota_massima_moneta: {quota} oltre 1")
    dimensione = ("fatti", "regole_dimensione_bot")
    return {
        "impronta": hashlib.sha256(contenuto).hexdigest(),
        "commissione_per_lato": _numero(_voce(albero, "fatti", "commissione_taker_per_lato", "valore"),
                                        "fatti.commissione_taker_per_lato.valore"),
        "rischio_per_trade": _numero(_voce(albero, *dimensione, "rischio_per_trade"),
                                     "fatti.regole_dimensione_bot.rischio_per_trade"),
        "leva_max": _numero(_voce(albero, *dimensione, "leva_max"), "fatti.regole_dimensione_bot.leva_max"),
        "modalita_margine": modalita,
        "tasso_margine_mantenimento": _numero(_voce(albero, *dimensione, "tasso_margine_mantenimento"),
                                              "fatti.regole_dimensione_bot.tasso_margine_mantenimento"),
        "margine_minimo_da_liquidazione": _numero(_voce(albero, "regole_esame", "margine_minimo_da_liquidazione"),
                                                  "regole_esame.margine_minimo_da_liquidazione"),
        "riempimento_intrabarra": riempimento,
        "timeframe_ammessi": [str(t) for t in _voce(albero, "regole_esame", "timeframe_ammessi")],
        "bootstrap_ricampionamenti": _numero(_voce(albero, "regole_esame", "bootstrap", "ricampionamenti"),
                                             "regole_esame.bootstrap.ricampionamenti", intero=True),
        "bootstrap_seme": seme,
        "pf_minimo_vault": _numero(_voce(albero, "regole_esame", "criterio_vault", "profit_factor_minimo"),
                                   "regole_esame.criterio_vault.profit_factor_minimo"),
        "percentile_caso_vault": _numero(_voce(albero, "regole_esame", "criterio_vault",
                                               "r_medio_sopra_percentile_caso"),
                                         "regole_esame.criterio_vault.r_medio_sopra_percentile_caso"),
        "capitale_per_moneta": _numero(_voce(gruppo, "capitale_per_moneta_usdt"), "gruppo.capitale_per_moneta_usdt"),
        "trade_minimi": {periodo: _numero(_voce(trade_minimi, periodo), f"gruppo.trade_minimi.{periodo}", intero=True)
                         for periodo in ("costruzione", "validazione", "vault")},
        "quota_massima_moneta": quota,
        "simulazioni_baseline_casuale": _numero(_voce(gruppo, "simulazioni_baseline_casuale"),
                                                "gruppo.simulazioni_baseline_casuale", intero=True),
        "passo_semi": int(trovato.group(1)),
        "sfasamenti_pavimento": _numero(_voce(gruppo, "sfasamenti_pavimento"), "gruppo.sfasamenti_pavimento",
                                        intero=True),
        "fittizie_vault": _numero(_voce(gruppo, "fittizie_vault"), "gruppo.fittizie_vault", intero=True),
        "margine_sfasamento_giorni": _numero(_voce(gruppo, "margine_sfasamento_giorni"),
                                             "gruppo.margine_sfasamento_giorni", intero=True),
        "anni_trade_minimi": _numero(_voce(fase4, "anni_trade_minimi"), "gruppo.fase4.anni_trade_minimi", intero=True),
        "trade_migliori_tolti": _numero(_voce(fase4, "trade_migliori_tolti"), "gruppo.fase4.trade_migliori_tolti",
                                        intero=True),
        "giorni_migliori_tolti": _numero(_voce(fase4, "giorni_migliori_tolti"), "gruppo.fase4.giorni_migliori_tolti",
                                         intero=True),
        "monete_migliori_tolte": _numero(_voce(fase4, "monete_migliori_tolte"), "gruppo.fase4.monete_migliori_tolte",
                                         intero=True),
        "asticella_q": _numero(_voce(gruppo, "asticella", "q"), "gruppo.asticella.q"),
        "taglio_costruzione": taglio,
        "inizio_validazione": inizio_validazione,
        "numero_monete": _numero(_voce(gruppo, "numero_monete"), "gruppo.numero_monete", intero=True),
    }


def _opzioni_del_motore(regole: Mapping, moltiplicatore_costi: float, ritardo_barre: int,
                        riempimento_intrabarra: Optional[str]) -> Dict[str, object]:
    """Le tre opzioni della chiamata che cambiano i ``Parametri`` (regole.md, sezione 6, punto 2, e sezione 13: costi doppi, ritardo, regola intra-barra)."""
    if isinstance(moltiplicatore_costi, bool) or not isinstance(moltiplicatore_costi, (int, float)) \
            or not math.isfinite(moltiplicatore_costi) or moltiplicatore_costi <= 0:
        raise ValueError(f"moltiplicatore_costi deve essere un numero positivo, non {moltiplicatore_costi!r}")
    if isinstance(ritardo_barre, bool) or operator.index(ritardo_barre) < 0:
        raise ValueError(f"ritardo_barre deve essere un intero >= 0, non {ritardo_barre!r}")
    riempimento = regole["riempimento_intrabarra"] if riempimento_intrabarra is None else riempimento_intrabarra
    if riempimento not in ("stop_prima", "target_prima"):
        raise ValueError(f"riempimento_intrabarra sconosciuto: {riempimento!r}")
    return {"moltiplicatore_costi": float(moltiplicatore_costi), "ritardo_barre": operator.index(ritardo_barre),
            "riempimento_intrabarra": riempimento}


def _parametri(regole: Mapping, slippage_per_lato: float, opzioni: Mapping) -> Parametri:
    """I ``Parametri`` di una moneta (regole.md, sezione 2, punto 8, e sezione 13; sezione 7 del protocollo)."""
    slippage = float(slippage_per_lato)
    if not math.isfinite(slippage) or slippage < 0:
        raise ValueError(f"slippage per lato non valido: {slippage_per_lato!r}")
    return Parametri(
        commissione_per_lato=regole["commissione_per_lato"],
        slippage_per_lato=slippage,
        rischio_per_trade=regole["rischio_per_trade"],
        leva_max=regole["leva_max"],
        modalita_margine=regole["modalita_margine"],
        tasso_margine_mantenimento=regole["tasso_margine_mantenimento"],
        margine_minimo_da_liquidazione=regole["margine_minimo_da_liquidazione"],
        capitale_iniziale=regole["capitale_per_moneta"],
        riempimento_intrabarra=opzioni["riempimento_intrabarra"],
        moltiplicatore_costi=opzioni["moltiplicatore_costi"],
        ritardo_barre=opzioni["ritardo_barre"],
    )


def parametri_moneta(slippage_per_lato: float, *, moltiplicatore_costi: float = 1.0, ritardo_barre: int = 0,
                     riempimento_intrabarra: Optional[str] = None) -> Parametri:
    """I ``Parametri`` del motore per una moneta del gruppo (regole.md, sezione 2, punto 8, e sezione 13).

    Parte comune di ``parametri.yaml`` (commissione, rischio, leva, modalita' di
    margine, margine di mantenimento, margine minimo dalla liquidazione,
    riempimento intra-barra), capitale della sezione ``gruppo`` (1.000 USDT per
    moneta), ``slippage_per_lato`` dalla fascia della scheda
    (``dati.leggi_scheda_gruppo``), piu' le tre opzioni delle verifiche della Fase 4
    (costi doppi, ritardo di una barra, regola intra-barra opposta).
    """
    regole = regole_del_gruppo()
    return _parametri(regole, slippage_per_lato,
                      _opzioni_del_motore(regole, moltiplicatore_costi, ritardo_barre, riempimento_intrabarra))


# ---------------------------------------------------------------------------
# Impronte, marcatore e via libera
# ---------------------------------------------------------------------------


def impronte_degli_strumenti() -> Dict[str, str]:
    """Le impronte SHA-256 dei cinque file della sezione 13 (regole.md, sezione 7, punto 2, e sezione 11, punto 1).

    {percorso dalla radice del repository: impronta} per ``FILE_DEL_VIA_LIBERA``:
    i quattro moduli come erano quando questo modulo e' stato importato (il
    codice che gira) e ``parametri.yaml`` come e' adesso sul disco.
    """
    impronte = dict(_IMPRONTE_DEL_CODICE_IN_MEMORIA)
    impronte[NOME_PARAMETRI] = _sha256_file(Path(dati.PERCORSO_PARAMETRI))
    return impronte


def _in_campagna() -> bool:
    """True se c'e' un marcatore di campagna, letto come lo legge ``dati`` (regole.md, sezione 13, «Il marcatore»).

    Un marcatore rotto alza ``dati.VietatoInCampagna``: si sistema, non si ignora.
    """
    return dati.marcatore_di_campagna() is not None


def _controlla_argomenti_in_campagna(chi: str, monete, caricatore, radice) -> None:
    """In una sessione di campagna si esamina solo l'elenco ufficiale, con i dati del progetto (regole.md, sezione 0, punto 4, e sezione 13).

    ``monete`` e ``caricatore`` servono ai test, alla prova a placebo e al
    coordinamento: con un marcatore di campagna (letto come lo legge ``dati``)
    restano quelli predefiniti (l'elenco di ``guardiano.leggi_monete_gruppo`` e
    ``CaricatoreDisco``), e ``radice`` e' la cartella ``research/`` del progetto
    (``dati.RADICE_DEFAULT``); se no ``dati.VietatoInCampagna``. Cosi' una variante
    non si giudica su una parte delle monete ne' su dati diversi da quelli della
    Fase 0. I test della sessione girano senza marcatore (la loro fixture punta
    ``dati.RADICE_PROGETTO`` a una cartella vuota).
    """
    if not _in_campagna():
        return
    altri = [nome for nome, valore in (("monete", monete), ("caricatore", caricatore)) if valore is not None]
    if Path(radice).resolve() != Path(dati.RADICE_DEFAULT).resolve():
        altri.append("radice")
    if altri:
        raise dati.VietatoInCampagna(
            f"{chi}: in una sessione di campagna non si passano {', '.join(altri)}: l'esame di gruppo gira su tutte le "
            "monete di monete.csv con i dati del progetto (regole.md, sezione 0, punto 4)")


def controlla_via_libera(percorso: Optional[Union[str, Path]] = None) -> Dict[str, str]:
    """Il controllo del via libera prima della validazione (regole.md, sezione 7, punto 2, e sezione 11, punto 2).

    ``percorso``: di norma ``<radice del progetto>/research/campagne/GRUPPO/
    via_libera_validazione.md`` (la radice di ``dati.RADICE_PROGETTO``, dove sta il
    marcatore), qualunque sia la cartella di uscita dell'esame. Il file deve
    nominare tutti e cinque i file ``FILE_DEL_VIA_LIBERA`` con una riga nel
    formato di ``sha256sum`` (``<impronta>  <percorso dalla radice del
    repository>``, ammesso anche ``*`` davanti al percorso, o l'ordine inverso);
    le altre righe (per esempio quella dell'esito) non contano. Ogni impronta
    deve essere quella del file sul disco e quella del codice in memoria (un
    file cambiato dopo l'import di questo modulo e' un codice diverso da quello
    del via libera).

    Restituisce {percorso: impronta}. Alza ``ViaLiberaNonValida`` con il motivo se
    il file manca, se un file non e' nominato (meno di cinque impronte), se e'
    nominato due volte con impronte diverse o se un'impronta non torna.
    """
    file = Path(percorso) if percorso is not None else Path(dati.RADICE_PROGETTO) / VIA_LIBERA
    if not file.is_file():
        raise ViaLiberaNonValida(
            f"manca {file}: la validazione non parte senza il via libera del coordinamento "
            "(regole.md, sezione 7, punto 2)")
    trovate: Dict[str, str] = {}
    for riga in file.read_text(encoding="utf-8").splitlines():
        campi = [c.strip("`") for c in riga.split()]
        while campi and campi[0] in ("-", "*"):
            campi = campi[1:]
        if len(campi) != 2:
            continue
        a, b = campi[0], campi[1].lstrip("*")
        if re.fullmatch(r"[0-9a-fA-F]{64}", a) and b in FILE_DEL_VIA_LIBERA:
            nome, impronta = b, a.lower()
        elif re.fullmatch(r"[0-9a-fA-F]{64}", b) and a in FILE_DEL_VIA_LIBERA:
            nome, impronta = a, b.lower()
        else:
            continue
        if trovate.get(nome, impronta) != impronta:
            raise ViaLiberaNonValida(f"{file}: {nome} ha due impronte diverse")
        trovate[nome] = impronta
    mancanti = [nome for nome in FILE_DEL_VIA_LIBERA if nome not in trovate]
    if mancanti:
        raise ViaLiberaNonValida(f"{file}: non nomina l'impronta di {', '.join(mancanti)} "
                                 "(servono tutte e cinque: regole.md, sezione 7, punto 2)")
    sul_disco = {nome: _sha256_file(p) for nome, p in _FILE_DEL_CODICE.items()}
    sul_disco[NOME_PARAMETRI] = _sha256_file(Path(dati.PERCORSO_PARAMETRI))
    diverse = [nome for nome in FILE_DEL_VIA_LIBERA if trovate[nome] != sul_disco[nome]]
    if diverse:
        raise ViaLiberaNonValida(
            f"{file}: le impronte di {', '.join(diverse)} non sono quelle dei file sul disco: il via libera vale solo "
            "per i file della prova a placebo (regole.md, sezione 7, punto 2, e sezione 11, punto 2)")
    in_memoria = [nome for nome, impronta in _IMPRONTE_DEL_CODICE_IN_MEMORIA.items() if impronta != sul_disco[nome]]
    if in_memoria:
        raise ViaLiberaNonValida(
            f"{', '.join(in_memoria)} e' cambiato dopo l'import di gruppo.py: il codice in memoria non e' quello "
            "del via libera (riavviare l'interprete)")
    return trovate


def _canonico(valore: object) -> str:
    """JSON canonico (chiavi ordinate, niente spazi, niente valori non finiti) per le impronte."""
    return json.dumps(valore, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False)


def _sha256_testo(testo: str) -> str:
    return hashlib.sha256(testo.encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------------
# Il modulo della variante (contratto, punto 1)
# ---------------------------------------------------------------------------

_MODULI_VARIANTE: Dict[Tuple[str, str], types.ModuleType] = {}


def _import_ammesso(nome: str) -> bool:
    """True per un modulo della libreria standard, di numpy o ``research.src.motore`` (contratto, punto 1)."""
    if nome.split(".", 1)[0] in sys.stdlib_module_names:
        return True
    return any(nome == ammesso or nome.startswith(ammesso + ".") for ammesso in IMPORT_AMMESSI)


def controlla_import_della_variante(sorgente: Union[str, bytes], file: Union[str, Path] = "<variante>") -> None:
    """Gli import del modulo della variante: solo libreria standard, numpy e ``research.src.motore`` (regole.md, sezione 13; docstring del modulo, punto 1).

    Si leggono dal testo (``ast``), anche quelli dentro le funzioni. Un altro
    file di codice importato (per esempio ``codice/comune.py``) non sarebbe
    nell'impronta della variante: la ripresa riuserebbe pezzi calcolati con il
    codice vecchio e l'impronta nel log non direbbe piu' quali regole sono
    congelate. ``ContrattoNonRispettato`` con l'elenco degli import vietati,
    compresi quelli relativi (``from . import x``). Non si vede un import fatto
    a runtime (``__import__``, ``importlib``): come il guardiano, e' una barriera
    contro la distrazione, non contro un codice scritto per aggirarla.
    """
    albero = ast.parse(sorgente, filename=str(file))
    vietati: List[str] = []
    for nodo in ast.walk(albero):
        if isinstance(nodo, ast.Import):
            vietati.extend(f"import {alias.name}" for alias in nodo.names if not _import_ammesso(alias.name))
        elif isinstance(nodo, ast.ImportFrom):
            modulo = nodo.module or ""
            if nodo.level:
                vietati.append(f"from {'.' * nodo.level}{modulo} import ...")
            elif not _import_ammesso(modulo):
                # «from research.src import motore» importa research.src.motore
                vietati.extend(f"from {modulo} import {alias.name}" for alias in nodo.names
                               if not _import_ammesso(f"{modulo}.{alias.name}"))
    if vietati:
        raise ContrattoNonRispettato(
            f"{file}: import non ammessi nel modulo della variante: {', '.join(vietati)} (solo libreria standard, "
            "numpy e research.src.motore: un altro file di codice non sarebbe nell'impronta; docstring di "
            "research/src/gruppo.py, punto 1)")


def _leggi_variante(percorso: Union[str, Path], impronta: Optional[str]) -> Tuple[Path, bytes, str]:
    """Il file della variante, i suoi byte e il loro SHA-256; RuntimeError se ``impronta`` non torna."""
    file = Path(percorso).resolve()
    sorgente = file.read_bytes()
    trovata = hashlib.sha256(sorgente).hexdigest()
    if impronta is not None and trovata != impronta:
        raise RuntimeError(f"il modulo della variante {file} e' cambiato durante l'esame "
                           f"(impronta {trovata[:16]}..., attesa {impronta[:16]}...)")
    return file, sorgente, trovata


def _esegui_variante(file: Path, sorgente: bytes, trovata: str) -> types.ModuleType:
    """Esegue da capo i byte della variante in un modulo nuovo e ne controlla import e funzioni del contratto."""
    controlla_import_della_variante(sorgente, file)
    nome = "_variante_di_gruppo_" + _sha256_testo(f"{file}\n{trovata}")[:20]
    modulo = types.ModuleType(nome)
    modulo.__file__ = str(file)
    sys.modules[nome] = modulo
    try:
        exec(compile(sorgente, str(file), "exec"), modulo.__dict__)
    except BaseException:
        sys.modules.pop(nome, None)
        raise
    mancanti = [f for f in FUNZIONI_DEL_CONTRATTO if not callable(getattr(modulo, f, None))]
    if mancanti:
        sys.modules.pop(nome, None)
        raise ContrattoNonRispettato(
            f"{file}: mancano le funzioni del contratto {', '.join(mancanti)} (crea_variante(ctx, p), crea_a(ctx, p), "
            "crea_casuale(ctx, p), crea_segnale(ctx, p): docstring di research/src/gruppo.py)")
    return modulo


def carica_modulo_variante(percorso: Union[str, Path], impronta: Optional[str] = None) -> types.ModuleType:
    """Importa per percorso il modulo della variante e ne controlla il contratto (regole.md, sezione 13; docstring del modulo, punti 1-2).

    Il modulo si esegue dai byte letti qui, di cui si calcola lo SHA-256: se
    ``impronta`` e' data e non torna, RuntimeError (il file e' cambiato durante
    l'esame). Gli import devono essere quelli ammessi
    (``controlla_import_della_variante``) e le quattro funzioni
    ``FUNZIONI_DEL_CONTRATTO`` devono esistere ed essere chiamabili, altrimenti
    ``ContrattoNonRispettato``. Un modulo gia' importato in questo processo con
    lo stesso percorso e la stessa impronta si riusa: serve al controllo del
    contratto all'avvio di un esame. I pezzi di lavoro NON usano questo modulo:
    ognuno esegue i byte da capo (``_modulo_del_pezzo``), cosi' uno stato al
    livello del modulo non passa da una moneta all'altra (sezione 3, punto 3).
    """
    file, sorgente, trovata = _leggi_variante(percorso, impronta)
    chiave = (str(file), trovata)
    if chiave in _MODULI_VARIANTE:
        return _MODULI_VARIANTE[chiave]
    modulo = _esegui_variante(file, sorgente, trovata)
    _MODULI_VARIANTE[chiave] = modulo
    return modulo


def _modulo_del_pezzo(percorso: Union[str, Path], impronta: str) -> types.ModuleType:
    """Il modulo della variante eseguito da capo per UN pezzo di lavoro (una moneta), dai byte con l'impronta dell'esame (regole.md, sezione 3, punto 3, e sezione 13).

    Un dizionario o una ``lru_cache`` al livello del modulo nascono vuoti per ogni
    moneta: i dati di una moneta non arrivano a un'altra, e l'esito non dipende
    dal numero di processi ne' da come si distribuiscono le monete. Costa
    l'esecuzione del file, millisecondi. Non chiude il caso di uno stato appeso
    apposta a un altro modulo importato.
    """
    file, sorgente, trovata = _leggi_variante(percorso, impronta)
    return _esegui_variante(file, sorgente, trovata)


# ---------------------------------------------------------------------------
# Il contesto (contratto, punto 3): niente simbolo, niente futuro
# ---------------------------------------------------------------------------


class _Orologio:
    """L'«adesso» di una moneta: la chiusura dell'ultima barra passata alla strategia (None prima di ogni barra)."""

    __slots__ = ("adesso",)

    def __init__(self) -> None:
        self.adesso: Optional[int] = None


class Contesto:
    """Il contesto che ``gruppo.py`` passa alle funzioni della variante (regole.md, sezione 3, punto 3, e sezione 13).

    In sola lettura: ``timeframe``, ``ms_per_barra``, ``btc_chiuse_entro(ts)`` e
    ``funding_regolato_entro(ts)`` (docstring del modulo, punto 3). Non c'e' il
    simbolo, non c'e' la posizione j, non ci sono dati di altre monete.
    """

    __slots__ = ("timeframe", "ms_per_barra", "btc_chiuse_entro", "funding_regolato_entro")

    def __init__(self, timeframe: str, ms_per_barra: int, btc_chiuse_entro: Callable[[int], Sequence[Candela]],
                 funding_regolato_entro: Callable[[int], Sequence[Tuple[int, float]]]) -> None:
        object.__setattr__(self, "timeframe", timeframe)
        object.__setattr__(self, "ms_per_barra", ms_per_barra)
        object.__setattr__(self, "btc_chiuse_entro", btc_chiuse_entro)
        object.__setattr__(self, "funding_regolato_entro", funding_regolato_entro)

    def __setattr__(self, nome: str, valore: object) -> None:
        raise AttributeError("il contesto della variante e' in sola lettura")

    def __delattr__(self, nome: str) -> None:
        raise AttributeError("il contesto della variante e' in sola lettura")

    def __repr__(self) -> str:
        return f"Contesto(timeframe={self.timeframe!r}, ms_per_barra={self.ms_per_barra})"


def _accesso_entro(elementi: Sequence, istanti: Sequence[int], orologio: _Orologio) -> Callable[[int], StoriaChiusa]:
    """La funzione ``entro(ts)`` del contesto: gli ``elementi`` con istante ``<= min(ts, adesso)`` (regole.md, sezione 3, punto 3, e sezione 13).

    ``istanti`` e' crescente (uno per elemento). La vista restituita e' una
    ``motore.StoriaChiusa`` su una lista che contiene SOLO gli elementi gia'
    chiusi adesso (come fa ``motore.esegui`` con le barre): cresce quando
    l'orologio avanza e si accorcia quando riparte (un'esecuzione nuova).
    """
    visibili: List = []

    def entro(ts: int) -> StoriaChiusa:
        limite = operator.index(ts)
        adesso = orologio.adesso
        n_adesso = 0 if adesso is None else bisect_right(istanti, adesso)
        if len(visibili) > n_adesso:
            del visibili[n_adesso:]
        elif len(visibili) < n_adesso:
            visibili.extend(elementi[len(visibili):n_adesso])
        k = 0 if adesso is None else bisect_right(istanti, min(limite, adesso))
        return StoriaChiusa(visibili, k)

    return entro


def _crea_contesto(timeframe: str, ms_per_barra: int, btc: Sequence[Candela], funding: Sequence[Tuple[int, float]],
                   orologio: _Orologio) -> Contesto:
    """Il ``Contesto`` di una moneta, con l'orologio che le strategie avvolte aggiornano (regole.md, sezione 13)."""
    btc = list(btc)
    chiusure = [c.close_ts for c in btc]
    if any(b <= a for a, b in zip(chiusure, chiusure[1:])):
        raise ValueError("candele di BTCUSDT non in ordine strettamente crescente")
    funding = sorted((int(t), float(tasso)) for t, tasso in funding)
    return Contesto(timeframe, ms_per_barra,
                    _accesso_entro(btc, chiusure, orologio),
                    _accesso_entro(funding, [t for t, _ in funding], orologio))


def _strategia_avvolta(strategia: Callable, orologio: _Orologio, vietata: Optional[bytearray]) -> Callable:
    """La strategia della sessione con l'orologio del contesto e, se ``vietata`` c'e', il filtro di liquidita' (regole.md, sezione 2, punto 7).

    Prima di ogni chiamata l'«adesso» diventa la chiusura dell'ultima barra
    della storia; un ``Segnale`` alla chiusura di una barra con ``vietata[i]``
    diventa None (gli ingressi del motore partono solo da un Segnale; un
    «chiudi» passa sempre: la posizione aperta esce con la sua uscita).
    """
    if not callable(strategia):
        raise ContrattoNonRispettato("la fabbrica deve restituire una strategia(storia, posizione)")

    def avvolta(storia, posizione):
        orologio.adesso = storia[-1].close_ts
        decisione = strategia(storia, posizione)
        if vietata is not None and isinstance(decisione, Segnale) and vietata[len(storia) - 1]:
            return None
        return decisione

    return avvolta


class _Fabbriche:
    """Le fabbriche che il motore chiama, costruite dalle quattro funzioni della sessione (contratto, punti 2-5)."""

    def __init__(self, modulo: types.ModuleType, ctx: Contesto, orologio: _Orologio, p_json: str,
                 vietate_liquidita: bytearray) -> None:
        self._orologio = orologio
        self._liquidita = vietate_liquidita
        self.ingressi_variante: Optional[frozenset] = None  # ingressi_placebo o controllo positivo
        fabbriche = []
        for nome in FUNZIONI_DEL_CONTRATTO:
            orologio.adesso = None
            fabbrica = getattr(modulo, nome)(ctx, json.loads(p_json))
            if not callable(fabbrica):
                raise ContrattoNonRispettato(f"{nome}(ctx, p) deve restituire una funzione (docstring di gruppo.py)")
            fabbriche.append(fabbrica)
        self._variante, self._a, self._casuale, self._segnale = fabbriche

    def variante(self) -> Callable:
        """``crea()`` della variante (o ``crea_casuale`` dei suoi ingressi dati), con il filtro di liquidita'."""
        self._orologio.adesso = None
        if self.ingressi_variante is not None:
            strategia = self._casuale(self.ingressi_variante)
        else:
            strategia = self._variante()
        return _strategia_avvolta(strategia, self._orologio, self._liquidita)

    def a(self) -> Callable:
        """``crea()`` della (a), con il filtro di liquidita'."""
        self._orologio.adesso = None
        return _strategia_avvolta(self._a(), self._orologio, self._liquidita)

    def casuale(self, ingressi: frozenset) -> Callable:
        """``crea_casuale(ingressi)`` della (b) e delle sfasate: le barre vietate le escludono gia' gli ingressi."""
        self._orologio.adesso = None
        return _strategia_avvolta(self._casuale(ingressi), self._orologio, None)

    def segnale(self) -> Callable:
        """``crea_segnale()``, con l'orologio del contesto."""
        self._orologio.adesso = None
        funzione = self._segnale()
        if not callable(funzione):
            raise ContrattoNonRispettato("crea_segnale() deve restituire una funzione segnale(storia)")
        orologio = self._orologio

        def segnale(storia):
            orologio.adesso = storia[-1].close_ts
            return funzione(storia)

        return segnale


# ---------------------------------------------------------------------------
# I dati di una moneta
# ---------------------------------------------------------------------------


@dataclasses.dataclass(frozen=True)
class CaricatoreDisco:
    """Il caricatore dei dati dal disco, con le sole funzioni di ``dati`` (regole.md, sezione 2, punti 3, 7 e 8, e sezione 13).

    Un caricatore e' un oggetto (che si passa fra processi con pickle) con tre
    metodi, gli stessi che un test o il coordinamento possono iniettare:

    * ``scheda(simbolo)`` -> {``primo_mese``: date, ``slippage_per_lato``: float}
      (``dati.leggi_scheda_gruppo``);
    * ``serie(simbolo, timeframe, inizio, fine)`` -> {``candele``: last,
      ``candele_mark``: mark sugli stessi ts (``dati.carica_serie_allineate``),
      ``funding``: [(ts, tasso)] (``dati.carica_funding``),
      ``mesi_sotto_liquidita``: [(anno, mese)] (``dati.mesi_sotto_liquidita``)},
      piu', facoltativo, ``barre_tolte``: {``last``, ``mark``} (le barre tolte
      dall'allineamento, i «dettagli del feed» della sezione 6, punto 2.6);
    * ``btc(timeframe, inizio, fine)`` -> le candele last di BTCUSDT
      (``dati.carica_candele``).

    Il caricatore non scarica nulla: i file si scaricano in Fase 0. Il blocco del
    vault, i rifiuti in campagna e le date li controlla ``dati``.
    """

    radice: str = str(dati.RADICE_DEFAULT)

    def scheda(self, simbolo: str) -> Dict[str, object]:
        scheda = dati.leggi_scheda_gruppo(simbolo, Path(self.radice))
        return {"primo_mese": scheda["primo_mese"], "slippage_per_lato": scheda["slippage_per_lato"]}

    def serie(self, simbolo: str, timeframe: str, inizio: date, fine: date) -> Dict[str, object]:
        radice = Path(self.radice)
        allineate = dati.carica_serie_allineate(simbolo, timeframe, inizio, fine, radice)
        return {
            "candele": allineate["candele"],
            "candele_mark": allineate["candele_mark"],
            "funding": dati.carica_funding(simbolo, inizio, fine, radice),
            "mesi_sotto_liquidita": dati.mesi_sotto_liquidita(simbolo, inizio, fine, radice),
            "barre_tolte": {"last": allineate["n_tolte_last"], "mark": allineate["n_tolte_mark"]},
        }

    def btc(self, timeframe: str, inizio: date, fine: date) -> List[Candela]:
        return dati.carica_candele(MONETA_RIFERIMENTO, timeframe, inizio, fine, Path(self.radice))


def _controlla_candele(nome: str, candele: Sequence[Candela], da_ms: int, a_ms: int) -> List[Candela]:
    """Le candele di un caricatore: ``Candela``, ts crescenti, tutte dentro [da_ms, a_ms) (niente dati fuori dal periodo)."""
    lista = list(candele)
    for c in lista:
        if not isinstance(c, Candela):
            raise TypeError(f"{nome}: il caricatore deve dare Candela, non {type(c).__name__}")
        if c.ts < da_ms or c.close_ts >= a_ms:
            raise ValueError(f"{nome}: la candela {c.ts} e' fuori dal periodo richiesto: il caricatore non puo' dare "
                             "dati oltre la fine del periodo (sezione 8 del protocollo)")
    if any(b.ts <= a.ts for a, b in zip(lista, lista[1:])):
        raise ValueError(f"{nome}: ts non strettamente crescenti")
    return lista


def _carica_moneta(caricatore, simbolo: str, timeframe: str, inizio: date, fine: date) -> Dict[str, object]:
    """I dati di una moneta dal caricatore, controllati: dentro il periodo, mark allineato, funding ordinato."""
    serie = caricatore.serie(simbolo, timeframe, inizio, fine)
    da_ms, a_ms = dati.ms_da_data(inizio), dati.ms_da_data(fine + timedelta(days=1))
    candele = _controlla_candele(f"{simbolo} last", serie["candele"], da_ms, a_ms)
    mark = _controlla_candele(f"{simbolo} mark", serie["candele_mark"], da_ms, a_ms)
    if [c.ts for c in mark] != [c.ts for c in candele]:
        raise ValueError(f"{simbolo}: last e mark non hanno gli stessi ts (dati.carica_serie_allineate)")
    funding = sorted((int(t), float(tasso)) for t, tasso in serie["funding"])
    if funding and (funding[0][0] < da_ms or funding[-1][0] >= a_ms):
        raise ValueError(f"{simbolo}: funding fuori dal periodo richiesto")
    mesi = sorted({(int(a), int(m)) for a, m in serie["mesi_sotto_liquidita"]})
    tolte = serie.get("barre_tolte")
    return {"candele": candele, "candele_mark": mark, "funding": funding, "mesi_sotto_liquidita": mesi,
            "barre_tolte": None if tolte is None else {"last": int(tolte["last"]), "mark": int(tolte["mark"])}}


_BTC_IN_MEMORIA: Dict[Tuple[bytes, str, str], Tuple[List[Candela], str]] = {}


def _byte_delle_candele(candele: Sequence[Candela]) -> bytes:
    """Le candele come byte (ts, close_ts in int64; open, high, low, close, volume in float64), per le impronte dei dati."""
    if not candele:
        return b""
    interi = np.array([(c.ts, c.close_ts) for c in candele], dtype=np.int64)
    reali = np.array([(c.open, c.high, c.low, c.close, c.volume) for c in candele], dtype=np.float64)
    return interi.tobytes() + reali.tobytes()


def _btc(caricatore, timeframe: str, fine: date) -> Tuple[List[Candela], str]:
    """Le candele di BTCUSDT dal 2020-01-01 alla fine del periodo e la loro impronta, una volta per processo (regole.md, sezione 3, punto 3)."""
    chiave = (pickle.dumps(caricatore), timeframe, fine.isoformat())
    if chiave not in _BTC_IN_MEMORIA:
        candele = _controlla_candele(MONETA_RIFERIMENTO, caricatore.btc(timeframe, INIZIO_ARCHIVIO, fine),
                                     dati.ms_da_data(INIZIO_ARCHIVIO), dati.ms_da_data(fine + timedelta(days=1)))
        _BTC_IN_MEMORIA.clear()
        _BTC_IN_MEMORIA[chiave] = (candele, hashlib.sha256(_byte_delle_candele(candele)).hexdigest())
    return _BTC_IN_MEMORIA[chiave]


def _controlla_btc(btc: Sequence[Candela], candele: Sequence[Candela], simbolo: str,
                   in_campagna: bool) -> Dict[str, object]:
    """Quante candele di BTCUSDT arrivano alle funzioni della variante, e da quando a quando (regole.md, sezione 2, punto 2, e sezione 3, punto 3).

    Si riportano sempre (``candele``, ``prima_ts``, ``ultima_close_ts``). In una
    sessione di campagna l'esame si ferma (ValueError) se non ce n'e' nessuna o se
    non coprono la serie della moneta (la prima apre dopo la prima barra della
    moneta, o l'ultima chiude prima dell'ultima): una variante che usa BTC come
    filtro sarebbe giudicata su un'altra regola senza che nessuno lo veda. Senza
    marcatore (la prova a placebo, i test) solo il conteggio.
    """
    info = {"candele": len(btc), "prima_ts": btc[0].ts if btc else None,
            "ultima_close_ts": btc[-1].close_ts if btc else None}
    if in_campagna and candele:
        if not btc:
            raise ValueError(f"{simbolo}: nessuna candela di {MONETA_RIFERIMENTO} del timeframe dell'esame: vanno "
                             "scaricate in Fase 0 (regole.md, sezione 2, punto 2)")
        if btc[0].ts > candele[0].ts or btc[-1].close_ts < candele[-1].close_ts:
            raise ValueError(f"{simbolo}: le candele di {MONETA_RIFERIMENTO} ({btc[0].ts}-{btc[-1].close_ts}) non "
                             f"coprono la serie della moneta ({candele[0].ts}-{candele[-1].close_ts}) "
                             "(regole.md, sezione 2, punto 2)")
    return info


def _impronta_dei_dati(compito: Mapping, slippage: float, serie: Mapping, impronta_btc: str) -> str:
    """L'impronta di tutto cio' che un pezzo legge dal caricatore per la sua moneta (regole.md, sezione 13: ripresa automatica).

    SHA-256 di simbolo, periodo, slippage della scheda, last, mark, funding, mesi
    sotto la liquidita', barre tolte e candele di BTCUSDT. Va nella riga di
    avanzamento del pezzo: alla ripresa il pezzo si riusa solo se i dati di
    adesso hanno la stessa impronta (altrimenti si ricalcola), cosi' una ripresa
    con lo stesso id non tiene in silenzio pezzi calcolati su dati diversi.
    """
    sha = hashlib.sha256()
    sha.update(_canonico({
        "simbolo": compito["simbolo"], "timeframe": compito["timeframe"], "inizio": compito["inizio"],
        "fine": compito["fine"], "inizio_conteggio_ts": compito.get("inizio_conteggio_ts"),
        "slippage_per_lato": float(slippage), "mesi_sotto_liquidita": [list(m) for m in serie["mesi_sotto_liquidita"]],
        "barre_tolte": serie["barre_tolte"], "n": [len(serie["candele"]), len(serie["candele_mark"]),
                                                  len(serie["funding"])], "btc": impronta_btc,
    }).encode("utf-8"))
    sha.update(_byte_delle_candele(serie["candele"]))
    sha.update(_byte_delle_candele(serie["candele_mark"]))
    if serie["funding"]:
        sha.update(np.array([t for t, _ in serie["funding"]], dtype=np.int64).tobytes())
        sha.update(np.array([tasso for _, tasso in serie["funding"]], dtype=np.float64).tobytes())
    return sha.hexdigest()


def _bandierine(n: int, intervalli: Sequence[Sequence[int]]) -> bytearray:
    """Un byte per barra, 1 se la barra e' in uno degli intervalli (inizio incluso, fine esclusa)."""
    bandierine = bytearray(n)
    for inizio, fine in intervalli:
        lo, hi = max(0, int(inizio)), min(n, int(fine))
        if hi > lo:
            bandierine[lo:hi] = b"\x01" * (hi - lo)
    return bandierine


def _in_json(valore: object) -> object:
    """Lo stesso valore fatto solo di dict (chiavi stringa), list, str, int, float, bool e None."""
    if isinstance(valore, Mapping):
        return {(k if isinstance(k, str) else str(k)): _in_json(v) for k, v in valore.items()}
    if isinstance(valore, (list, tuple)):
        return [_in_json(v) for v in valore]
    if isinstance(valore, np.ndarray):
        return [_in_json(v) for v in valore.tolist()]
    if isinstance(valore, np.generic):
        return valore.item()
    if isinstance(valore, date):
        return valore.isoformat()
    if isinstance(valore, Path):
        return str(valore)
    if valore is None or isinstance(valore, (bool, int, float, str)):
        return valore
    raise TypeError(f"valore non rappresentabile in JSON: {type(valore).__name__}")


# ---------------------------------------------------------------------------
# I pezzi di lavoro di una moneta (un processo per moneta)
# ---------------------------------------------------------------------------


class _Preparato:
    """Cio' che serve ai pezzi di una moneta: dati, parametri, fabbriche avvolte, barre vietate."""

    def __init__(self, candele, mark, funding, mesi_sotto, intervalli_liquidita, parametri, fabbriche,
                 indice_conteggio, barre_tolte) -> None:
        self.candele: List[Candela] = candele
        self.mark: List[Candela] = mark
        self.funding: List[Tuple[int, float]] = funding
        self.mesi_sotto: List[Tuple[int, int]] = mesi_sotto
        self.intervalli_liquidita: List[Tuple[int, int]] = intervalli_liquidita
        self.parametri: Parametri = parametri
        self.fabbriche: _Fabbriche = fabbriche
        self.indice_conteggio: int = indice_conteggio
        self.barre_tolte = barre_tolte
        self.ingressi_variante: Optional[Dict[str, int]] = None
        self.btc: Dict[str, object] = {}
        self.impronta_dati: str = ""
        self._vietate: Optional[Dict[str, object]] = None

    def barre_vietate(self) -> Dict[str, object]:
        """Le barre vietate agli ingressi della (b) e delle sfasate (regole.md, sezione 5, punto 4, e sezione 2, punto 7).

        Segnale non valido o non calcolabile (``motore.barre_vietate_segnale_non_valido``,
        riscaldamento compreso), mesi sotto la liquidita' (``dati.barre_vietate_liquidita``,
        le stesse barre del filtro della variante) e, in validazione e nel vault,
        tutte le barre prima del periodo. L'ultima barra la vieta il motore.
        ``impronta`` e' lo SHA-256 della maschera: la (b) e le sfasate di una moneta
        devono avere la stessa.
        """
        if self._vietate is None:
            segnale = [tuple(x) for x in motore.barre_vietate_segnale_non_valido(
                self.candele, self.fabbriche.segnale, self.parametri)]
            prima = [(0, self.indice_conteggio)] if self.indice_conteggio > 0 else []
            intervalli = segnale + list(self.intervalli_liquidita) + prima
            maschera = _bandierine(len(self.candele), intervalli)
            self._vietate = {
                "intervalli": intervalli,
                "maschera": maschera,
                "segnale_non_valido": sum(b - a for a, b in segnale),
                "liquidita": sum(b - a for a, b in self.intervalli_liquidita),
                "prima_del_periodo": self.indice_conteggio,
                "totale": sum(maschera),
                "impronta": hashlib.sha256(bytes(maschera)).hexdigest(),
            }
        return self._vietate


def _controlla_impronte_nel_processo(compito: Mapping) -> None:
    """Il processo che lavora ha lo stesso codice e gli stessi parametri del processo che ha avviato l'esame."""
    attese = compito["impronte"]
    diverse = [nome for nome, impronta in _IMPRONTE_DEL_CODICE_IN_MEMORIA.items() if attese.get(nome) != impronta]
    if _sha256_file(Path(dati.PERCORSO_PARAMETRI)) != attese.get(NOME_PARAMETRI):
        diverse.append(NOME_PARAMETRI)
    if diverse:
        raise RuntimeError(f"il codice di questo processo non e' quello dell'esame: cambiati {', '.join(diverse)}")


def _prepara(compito: Mapping) -> _Preparato:
    """Carica i dati della moneta e costruisce contesto, fabbriche e ingressi dati (contratto, punti 3-5).

    Il modulo della variante si esegue da capo per il pezzo (``_modulo_del_pezzo``).
    ``impronta_dati`` (``_impronta_dei_dati``) e ``btc`` (``_controlla_btc``) vanno
    nel pezzo.
    """
    modulo = _modulo_del_pezzo(compito["modulo"], compito["impronta_variante"])
    caricatore = compito["caricatore"]
    simbolo = compito["simbolo"]
    scheda = caricatore.scheda(simbolo)
    parametri = _parametri(compito["regole"], scheda["slippage_per_lato"], compito["opzioni"])
    inizio, fine = date.fromisoformat(compito["inizio"]), date.fromisoformat(compito["fine"])
    serie = _carica_moneta(caricatore, simbolo, compito["timeframe"], inizio, fine)
    candele = serie["candele"]
    btc, impronta_btc = _btc(caricatore, compito["timeframe"], fine)
    info_btc = _controlla_btc(btc, candele, simbolo, bool(compito.get("in_campagna")))
    orologio = _Orologio()
    ctx = _crea_contesto(compito["timeframe"], compito["ms_per_barra"], btc, serie["funding"], orologio)
    intervalli = [tuple(x) for x in dati.barre_vietate_liquidita(candele, serie["mesi_sotto_liquidita"])]
    fabbriche = _Fabbriche(modulo, ctx, orologio, compito["p_json"], _bandierine(len(candele), intervalli))
    conteggio = compito.get("inizio_conteggio_ts")
    indice = 0 if conteggio is None else bisect_left([c.ts for c in candele], conteggio)
    prep = _Preparato(candele, serie["candele_mark"], serie["funding"], serie["mesi_sotto_liquidita"], intervalli,
                      parametri, fabbriche, indice, serie["barre_tolte"])
    prep.btc = info_btc
    prep.impronta_dati = _impronta_dei_dati(compito, parametri.slippage_per_lato, serie, impronta_btc)

    sorgente = compito["sorgente"]
    if sorgente["tipo"] == "placebo":
        indice_per_ts = {c.ts: i for i, c in enumerate(candele)}
        indici = [indice_per_ts.get(int(ts)) for ts in sorgente["ts"]]
        fabbriche.ingressi_variante = frozenset(i for i in indici if i is not None)
        prep.ingressi_variante = {"dati": len(indici), "senza_barra": sum(1 for i in indici if i is None)}
    elif sorgente["tipo"] == "guarda_avanti":
        # Il solo calcolo in cui una strategia del gruppo usa una barra non chiusa: la legge gruppo.py, qui
        # (regole.md, sezione 5, punto 10). Segnale alla barra i se la chiusura di i + 1 e' sopra (long) o
        # sotto (short) quella di i, fuori dalle barre vietate delle varianti.
        maschera = prep.barre_vietate()["maschera"]
        lato = 1 if sorgente["direzione"] == "long" else -1
        fabbriche.ingressi_variante = frozenset(
            i for i in range(len(candele) - 1)
            if not maschera[i] and lato * (candele[i + 1].close - candele[i].close) > 0)
        prep.ingressi_variante = {"dati": len(fabbriche.ingressi_variante), "senza_barra": 0}
    elif sorgente["tipo"] != "modulo":
        raise ValueError(f"origine degli ingressi sconosciuta: {sorgente['tipo']!r}")
    return prep


def _pezzo_conta(compito: Mapping, prep: _Preparato) -> Tuple[Dict[str, object], Dict[str, float]]:
    """``motore.conta_trade`` su una moneta, con il filtro di liquidita' (regole.md, sezione 4, punto 2)."""
    conta = motore.conta_trade(prep.candele, prep.fabbriche.variante, compito["fine_costruzione_ts"],
                               prep.parametri, None, prep.mark, prep.funding)
    conta["mesi_sotto_liquidita"] = len(prep.mesi_sotto)
    conta["barre_vietate_liquidita"] = sum(b - a for a, b in prep.intervalli_liquidita)
    conta["btc"] = prep.btc
    if prep.ingressi_variante is not None:
        conta["ingressi_dati"] = prep.ingressi_variante
    return conta, {}


def _riga(trade: motore.Trade) -> List[object]:
    return [getattr(trade, campo) for campo in CAMPI_TRADE]


def _indici_di_segnale(trade: Sequence[motore.Trade], candele: Sequence[Candela], ritardo: int) -> List[int]:
    """L'indice della barra di segnale di ogni trade: 1 + ``ritardo_barre`` barre prima della barra d'ingresso, nella serie (motore, «ingresso all'apertura della barra i + 1 + ritardo»)."""
    indice_per_ts = {c.ts: i for i, c in enumerate(candele)}
    indici = []
    for t in trade:
        i = indice_per_ts[t.ts_entrata] - 1 - ritardo
        if i < 0:
            raise RuntimeError(f"il trade entrato a {t.ts_entrata} non ha una barra di segnale nella serie")
        indici.append(i)
    return indici


def _controlla_casuale(prep: _Preparato, risultato: motore.Risultato) -> Dict[str, int]:
    """La strategia casuale della sessione rifa' i trade del candidato dalle sue barre di segnale (regole.md, sezione 5, punti 4 e 5; contratto, punto 2).

    La (b), le sfasate, il controllo positivo e ``ingressi_placebo`` usano tutti
    ``crea_casuale``: «emette il segnale della variante ed esce con la sua
    uscita». Qui la si esegue una volta, sulla stessa serie del test, con gli
    ingressi alle barre di segnale di TUTTI i trade del test (anche quelli prima
    del periodo, in validazione e nel vault: cosi' il capitale segue lo stesso
    percorso). Deve dare gli stessi trade, campo per campo (entrata, uscita,
    esito, quantita', R, pnl...); se no ``ContrattoNonRispettato``: una (b) o un
    pavimento delle sfasate con un'altra uscita cambierebbero l'esame senza avviso.
    """
    if not risultato.trades:
        return {"trade_rifatti": 0}
    indici = _indici_di_segnale(risultato.trades, prep.candele, prep.parametri.ritardo_barre)
    rifatto = motore.esegui(prep.candele, None, prep.mark, prep.funding, prep.fabbriche.casuale(frozenset(indici)),
                            prep.parametri)
    if rifatto.trades != risultato.trades:
        diversi = sum(1 for a, b in zip(rifatto.trades, risultato.trades) if a != b) + \
            abs(len(rifatto.trades) - len(risultato.trades))
        raise ContrattoNonRispettato(
            f"crea_casuale con le barre di segnale dei {len(risultato.trades)} trade del test da' "
            f"{len(rifatto.trades)} trade, {diversi} diversi: deve emettere il segnale della variante e uscire con la "
            "sua uscita (docstring di research/src/gruppo.py, punto 2; regole.md, sezione 5, punti 4-5)")
    return {"trade_rifatti": len(rifatto.trades)}


def _pezzo_fase1(compito: Mapping, prep: _Preparato) -> Tuple[Dict[str, object], Dict[str, float]]:
    """La fase 1 di una moneta: test, controllo della strategia casuale, (a), barre vietate e (b) (regole.md, sezione 5, punti 1, 3 e 4; sezione 1, punto 5)."""
    secondi: Dict[str, float] = {}
    regole = compito["regole"]
    ms = compito["ms_per_barra"]
    candele = prep.candele
    conteggio = compito.get("inizio_conteggio_ts")

    t0 = time.perf_counter()
    risultato = motore.esegui(candele, None, prep.mark, prep.funding, prep.fabbriche.variante(), prep.parametri)
    trade = [t for t in risultato.trades if conteggio is None or t.ts_entrata >= conteggio]
    ts_segnali = [candele[i].ts for i in _indici_di_segnale(trade, candele, prep.parametri.ritardo_barre)]
    secondi["test"] = time.perf_counter() - t0
    t0 = time.perf_counter()
    coerenza = _controlla_casuale(prep, risultato)
    secondi["controllo_casuale"] = time.perf_counter() - t0

    pezzo: Dict[str, object] = {
        "simbolo": compito["simbolo"],
        "j": compito["j"],
        "slippage_per_lato": prep.parametri.slippage_per_lato,
        "barre": len(candele),
        "barre_nel_periodo": len(candele) - prep.indice_conteggio,
        "prima_barra_ts": candele[0].ts if candele else None,
        "ultima_barra_ts": candele[-1].ts if candele else None,
        "barre_tolte": prep.barre_tolte,
        "mesi_sotto_liquidita": [list(m) for m in prep.mesi_sotto],
        "ingressi_dati": prep.ingressi_variante,
        "btc": prep.btc,
        "controllo_casuale": coerenza,
        "trade": {"campi": list(CAMPI_TRADE), "righe": [_riga(t) for t in trade]},
        "ts_segnali": ts_segnali,
        "durata_massima_ms": max((t.ts_uscita - t.ts_entrata for t in trade), default=0),
        "conteggi": {
            "trade_prima_del_periodo": len(risultato.trades) - len(trade),
            "segnali_non_validi": risultato.n_segnali_non_validi,
            "segnali_senza_barra": risultato.n_segnali_senza_barra,
            "capitale_esaurito": risultato.n_segnali_capitale_esaurito,
            "buchi_dati": risultato.n_buchi_dati,
            "funding_in_buco": risultato.n_funding_in_buco,
        },
        "a": None,
        "b": None,
        "vietate": None,
    }

    # (c) buy and hold per anno, sul periodo (sezione 5, punto 8: solo contesto)
    per_anno: Dict[int, List[Candela]] = {}
    for c in candele[prep.indice_conteggio:]:
        per_anno.setdefault(dati.mese_utc(c.ts)[0], []).append(c)
    pezzo["buy_and_hold"] = {str(anno): {"long": motore.buy_and_hold(cc, prep.parametri, "long"),
                                         "short": motore.buy_and_hold(cc, prep.parametri, "short")}
                             for anno, cc in sorted(per_anno.items())}
    if not trade:
        return pezzo, secondi

    # (a) della moneta: i SUOI trade, il SUO blocco (sezione 5, punto 3)
    if compito["con_a"]:
        t0 = time.perf_counter()
        ris_a = motore.esegui(candele, None, prep.mark, prep.funding, prep.fabbriche.a(), prep.parametri)
        trade_a = [t for t in ris_a.trades if conteggio is None or t.ts_entrata >= conteggio]
        if trade_a:
            blocco_a = statistica.lunghezza_blocco([t.ts_entrata for t in trade_a], [t.ts_uscita for t in trade_a])
            base_a = statistica.baseline_da_trade([t.r for t in trade_a], blocco_a,
                                                  n=regole["bootstrap_ricampionamenti"], seme=regole["bootstrap_seme"])
            pezzo["a"] = {"base": base_a, "blocco": blocco_a, "n_trade": len(trade_a)}
        else:
            pezzo["a"] = {"base": None, "blocco": None, "n_trade": 0}
        secondi["a"] = time.perf_counter() - t0

    # barre vietate e (b) della moneta (sezione 5, punto 4)
    t0 = time.perf_counter()
    vietate = prep.barre_vietate()
    pezzo["vietate"] = {k: v for k, v in vietate.items() if k not in ("intervalli", "maschera")}
    secondi["vietate"] = time.perf_counter() - t0
    t0 = time.perf_counter()
    durata_media = motore.durata_media_barre(trade, ms)
    primo_seme = regole["passo_semi"] * compito["j"]
    try:
        sim = motore.simula_baseline_casuale(
            candele, prep.fabbriche.casuale, len(trade), durata_media, prep.parametri, None, prep.mark, prep.funding,
            vietate["intervalli"], n_simulazioni=regole["simulazioni_baseline_casuale"], primo_seme=primo_seme,
            rifiuta_poche_simulazioni=False)
    except ValueError as errore:
        if not str(errore).startswith("impossibile piazzare"):
            raise
        pezzo["b"] = {"entrano": False, "messaggio": str(errore), "durata_media": durata_media,
                      "primo_seme": primo_seme}
    else:
        per_seme = sim["r_medio_per_seme"]
        con_trade = iter(sim["trade_per_simulazione"])
        trade_per_seme = [0 if r is None else next(con_trade) for r in per_seme]
        pezzo["b"] = {
            "entrano": True,
            "durata_media": durata_media,
            "primo_seme": primo_seme,
            "r_medio_per_seme": per_seme,
            "trade_per_seme": trade_per_seme,
            "simulazioni_vuote": sim["simulazioni_vuote"],
            "segnali_non_validi_medi": float(np.mean(sim["segnali_non_validi_per_simulazione"])),
            "segnali_senza_barra_medi": float(np.mean(sim["segnali_senza_barra_per_simulazione"])),
        }
    secondi["b"] = time.perf_counter() - t0
    return pezzo, secondi


def _pezzo_sfasate(compito: Mapping, prep: _Preparato) -> Tuple[Dict[str, object], Dict[str, float]]:
    """Le strategie sfasate di una moneta (regole.md, sezione 5, punto 5, e sezione 9, punto 3).

    In costruzione e in validazione il pezzo tiene solo ``per_s``
    (``statistica.riassunto_sfasate``: [n_j(s), somma esatta degli R] per ogni s),
    che va nel file di avanzamento. Nel vault (``trade_completi``) servono anche
    i trade di ogni s, per le metriche di ogni sfasata: si restituiscono in forma
    compatta (``trade_compatti``: per ogni s il numero dei trade e, in fila per
    tutte le s, quattro ``array`` di interi e reali: ts d'entrata, ts d'uscita, R,
    pnl; 32 byte per trade invece di circa 280 di una lista di Python).
    """
    secondi: Dict[str, float] = {}
    t0 = time.perf_counter()
    vietate = prep.barre_vietate()
    if vietate["impronta"] != compito["impronta_vietate"]:
        raise RuntimeError("le barre vietate delle sfasate non sono quelle della (b) della stessa moneta")
    secondi["vietate"] = time.perf_counter() - t0
    t0 = time.perf_counter()
    ris = motore.simula_sfasamento_comune(
        prep.candele, prep.fabbriche.casuale, compito["ts_segnali"], tuple(compito["finestra_unione"]),
        tuple(compito["finestra_moneta"]), compito["ms_per_barra"], compito["sfasamenti"], prep.parametri,
        None, prep.mark, prep.funding, vietate["intervalli"])
    secondi["sfasate"] = time.perf_counter() - t0
    per_s = ris["per_sfasamento"]
    pezzo: Dict[str, object] = {
        "simbolo": compito["simbolo"],
        "L": ris["L"],
        "n_segnali": ris["n_segnali"],
        "segnali_fuori_dalla_finestra_unione": ris["segnali_fuori_dalla_finestra_unione"],
        "segnali_coincidenti": ris["segnali_coincidenti"],
        "saltati_totali": ris["saltati_totali"],
        "ingressi_totali": sum(x["ingressi"] for x in per_s),
        "segnali_non_validi": sum(x["segnali_non_validi"] for x in per_s),
        "segnali_senza_barra": sum(x["segnali_senza_barra"] for x in per_s),
        "capitale_esaurito": sum(x["capitale_esaurito"] for x in per_s),
    }
    if compito["trade_completi"]:
        trade_in_fila = [t for x in per_s for t in x["trade"]]
        pezzo["trade_compatti"] = {
            "conteggi": array("q", [len(x["trade"]) for x in per_s]),
            "ts_entrata": array("q", [t.ts_entrata for t in trade_in_fila]),
            "ts_uscita": array("q", [t.ts_uscita for t in trade_in_fila]),
            "r": array("d", [t.r for t in trade_in_fila]),
            "pnl": array("d", [t.pnl for t in trade_in_fila]),
        }
    else:
        pezzo["per_s"] = statistica.riassunto_sfasate([[t.r for t in x["trade"]] for x in per_s])
    return pezzo, secondi


def _trade_compatti_per_s(compatti: Mapping[str, array]) -> Iterator[List[TradeSfasato]]:
    """I trade di ogni s dalla forma compatta di ``_pezzo_sfasate`` (vault), uno s alla volta, come ``motore.TradeSfasato``."""
    inizio = 0
    for quanti in compatti["conteggi"]:
        fine = inizio + quanti
        yield [TradeSfasato(compatti["ts_entrata"][k], compatti["ts_uscita"][k], compatti["r"][k], compatti["pnl"][k])
               for k in range(inizio, fine)]
        inizio = fine


#: Gli ingressi specifici di un pezzo delle sfasate che entrano nella sua impronta (oltre ai dati della moneta).
_INGRESSI_DELLE_SFASATE = ("ts_segnali", "finestra_unione", "finestra_moneta", "sfasamenti", "impronta_vietate",
                           "trade_completi")


def _impronta_del_pezzo(compito: Mapping, prep: _Preparato) -> str:
    """L'impronta di cio' che il pezzo legge: i dati della moneta e, per le sfasate, i loro ingressi (regole.md, sezione 13)."""
    specifici = {k: compito[k] for k in _INGRESSI_DELLE_SFASATE if k in compito} if compito["tipo"] == "sfasate" else {}
    return _sha256_testo(_canonico({"dati": prep.impronta_dati, "pezzo": compito["tipo"], "ingressi": specifici}))


def _lavora(compito: Mapping) -> Dict[str, object]:
    """Esegue un pezzo di lavoro (in questo processo o in un processo del gruppo) e dice quale.

    Per la fase 1 e le sfasate, se ``compito["riusabili"]`` contiene l'impronta di
    cio' che il pezzo legge adesso (``_impronta_del_pezzo``), il pezzo non si
    ricalcola: torna solo ``riuso`` con quell'impronta, e chi chiama prende la
    riga salvata. Ogni errore, anche un ``SystemExit`` del codice della variante,
    diventa ``ErroreDiMoneta`` con il nome del pezzo (un ``SystemExit`` in un
    processo del gruppo, se no, chiuderebbe chi ha avviato l'esame).
    """
    inizio = time.perf_counter()
    tipo, simbolo = compito["tipo"], compito["simbolo"]
    impronta: Optional[str] = None
    try:
        _controlla_impronte_nel_processo(compito)
        if tipo not in ("conta", "fase1", "sfasate"):
            raise ValueError(f"pezzo sconosciuto: {tipo!r}")
        prep = _prepara(compito)
        tempo_dati = time.perf_counter() - inizio
        if tipo == "conta":
            pezzo, secondi = _pezzo_conta(compito, prep)
        else:
            impronta = _impronta_del_pezzo(compito, prep)
            if impronta in compito.get("riusabili", ()):
                return {"tipo": tipo, "simbolo": simbolo, "dati": None, "riuso": impronta, "impronta_dati": impronta,
                        "secondi": {"dati": round(tempo_dati, 3), "totale": round(time.perf_counter() - inizio, 3)}}
            pezzo, secondi = (_pezzo_fase1 if tipo == "fase1" else _pezzo_sfasate)(compito, prep)
        secondi["dati"] = tempo_dati
    except (Exception, SystemExit) as errore:
        raise ErroreDiMoneta(f"{tipo} di {simbolo}: {type(errore).__name__}: {errore}\n"
                             f"{traceback.format_exc()}") from errore
    secondi["totale"] = time.perf_counter() - inizio
    return {"tipo": tipo, "simbolo": simbolo, "dati": pezzo, "riuso": None, "impronta_dati": impronta,
            "secondi": {k: round(v, 3) for k, v in secondi.items()}}


def _ferma_i_processi(esecutore: ProcessPoolExecutor) -> None:
    """Chiude subito i processi del gruppo (dopo un errore): i pezzi in corso non servono piu'."""
    for processo in list((getattr(esecutore, "_processes", None) or {}).values()):
        try:
            processo.terminate()
        except Exception:  # un processo gia' finito
            pass


def _esegui_compiti(compiti: Sequence[Mapping], processi: int) -> Iterator[Dict[str, object]]:
    """I pezzi, uno per moneta: in questo processo con ``processi`` = 1, altrimenti in un gruppo di processi ``spawn`` (regole.md, sezione 12, punto 6, e sezione 13).

    I risultati arrivano nell'ordine in cui finiscono; chi li usa li rimette in
    ordine dei simboli. I pezzi partono nell'ordine di ``compiti`` (le monete piu'
    lunghe per prime). Un errore in un pezzo ferma tutto (e i processi del gruppo
    si chiudono): i pezzi gia' arrivati sono gia' stati salvati.

    Il gruppo e' un ``concurrent.futures.ProcessPoolExecutor``: se un processo
    muore senza un errore (memoria finita e processo ucciso dal sistema,
    ``os._exit``, un processo che non riesce a partire, per esempio perche' lo
    script che chiama ``gruppo.py`` non ha ``if __name__ == "__main__":``) l'esame
    non resta fermo per sempre: ``ErroreDiMoneta`` con i pezzi che erano in corso.
    """
    if not compiti:
        return
    if processi == 1:
        for compito in compiti:
            yield _lavora(compito)
        return
    contesto = multiprocessing.get_context("spawn")
    esecutore = ProcessPoolExecutor(max_workers=min(processi, len(compiti)), mp_context=contesto)
    finito = False
    try:
        in_attesa = {esecutore.submit(_lavora, compito): compito for compito in compiti}
        while in_attesa:
            fatti, _ = wait(in_attesa, return_when=FIRST_COMPLETED)
            for futuro in fatti:
                compito = in_attesa.pop(futuro)
                try:
                    risultato = futuro.result()
                except BrokenProcessPool as errore:
                    pezzi = sorted({f"{c['tipo']} di {c['simbolo']}" for c in [compito, *in_attesa.values()]})
                    raise ErroreDiMoneta(
                        "un processo del gruppo e' morto senza un errore (memoria finita, os._exit, sys.exit fuori "
                        "da un pezzo, uno script senza `if __name__ == \"__main__\":`...); pezzi non finiti: "
                        f"{', '.join(pezzi)}") from errore
                yield risultato
        finito = True
    finally:
        if not finito:
            _ferma_i_processi(esecutore)
        esecutore.shutdown(wait=True, cancel_futures=True)


# ---------------------------------------------------------------------------
# Il file di avanzamento (regole.md, sezione 8, punto 1, e sezione 13)
# ---------------------------------------------------------------------------


def _canonico_libero(valore: object) -> str:
    """JSON con chiavi ordinate che ammette i valori non finiti (per confrontare due pezzi)."""
    return json.dumps(valore, sort_keys=True, separators=(",", ":"))


class _Avanzamento:
    """Il file di avanzamento in sola aggiunta: una riga JSON per pezzo finito, con l'impronta dell'esame e quella dei dati del pezzo (regole.md, sezione 13).

    Alla lettura tiene solo le righe con lo stesso formato e la stessa impronta
    dell'esame; una riga illeggibile (un'interruzione a meta' scrittura) si salta,
    e prima di aggiungere si chiude con un a capo. Ogni riga porta anche
    ``impronta_dati`` (``_impronta_del_pezzo``: i dati che il pezzo ha letto): una
    riga si riusa solo se il processo che ricarica i dati di adesso trova la
    stessa impronta. Due righe dello stesso pezzo, della stessa impronta e degli
    stessi dati con numeri diversi sono un errore: il calcolo non sarebbe
    deterministico. I pezzi passano sempre dal JSON, anche quelli appena fatti.
    """

    def __init__(self, percorso: Path, intestazione: Mapping[str, str]) -> None:
        self.percorso = percorso
        self.intestazione = dict(intestazione)
        self._pezzi: Dict[Tuple[str, str, str, str], Dict[str, object]] = {}
        self.righe_di_altre_impronte = 0
        self.righe_illeggibili = 0
        self.pezzi_ripresi = 0
        self.pezzi_calcolati = 0
        if percorso.is_file():
            self._leggi()

    def _leggi(self) -> None:
        for riga in self.percorso.read_bytes().decode("utf-8", errors="replace").split("\n"):
            if not riga.strip():
                continue
            try:
                voce = json.loads(riga)
            except json.JSONDecodeError:
                self.righe_illeggibili += 1
                continue
            if not isinstance(voce, dict) or voce.get("formato") != FORMATO_AVANZAMENTO \
                    or voce.get("impronta") != self.intestazione["impronta"]:
                self.righe_di_altre_impronte += 1
                continue
            chiave = (voce["pezzo"], voce["simbolo"], voce.get("condizione", ""), str(voce.get("impronta_dati")))
            if chiave in self._pezzi:
                if _canonico_libero(self._pezzi[chiave]) != _canonico_libero(voce["dati"]):
                    raise RuntimeError(f"{self.percorso}: due righe diverse per {chiave} con la stessa impronta")
                continue
            self._pezzi[chiave] = voce["dati"]

    def impronte_salvate(self, pezzo: str, simbolo: str, condizione: str = "") -> List[str]:
        """Le impronte dei dati delle righe salvate di questo pezzo (quelle che un processo puo' chiedere di riusare)."""
        return sorted(k[3] for k in self._pezzi if k[:3] == (pezzo, simbolo, condizione))

    def dati(self, pezzo: str, simbolo: str, condizione: str, impronta_dati: str) -> Dict[str, object]:
        """La riga salvata del pezzo con quei dati (KeyError se non c'e')."""
        valore = self._pezzi[(pezzo, simbolo, condizione, impronta_dati)]
        self.pezzi_ripresi += 1
        return valore

    def aggiungi(self, pezzo: str, simbolo: str, dati_pezzo: Mapping, secondi: Mapping,
                 condizione: str = "", impronta_dati: str = "") -> Dict[str, object]:
        voce = dict(self.intestazione)
        voce.update({"formato": FORMATO_AVANZAMENTO, "pezzo": pezzo, "simbolo": simbolo, "condizione": condizione,
                     "impronta_dati": impronta_dati, "dati": _in_json(dati_pezzo), "secondi": dict(secondi)})
        riga = json.dumps(voce, sort_keys=True, ensure_ascii=False)
        riletti = json.loads(riga)["dati"]
        self.percorso.parent.mkdir(parents=True, exist_ok=True)
        with open(self.percorso, "ab") as flusso:
            if flusso.tell() > 0:
                with open(self.percorso, "rb") as lettura:
                    lettura.seek(-1, os.SEEK_END)
                    if lettura.read(1) != b"\n":
                        flusso.write(b"\n")
            flusso.write(riga.encode("utf-8") + b"\n")
            flusso.flush()
            os.fsync(flusso.fileno())
        self._pezzi[(pezzo, simbolo, condizione, impronta_dati)] = riletti
        self.pezzi_calcolati += 1
        return riletti

    def prendi(self, risultato: Mapping, condizione: str = "") -> Dict[str, object]:
        """Il pezzo che un processo ha restituito: la riga salvata se e' un riuso, se no la riga nuova (aggiunta al file)."""
        if risultato["riuso"] is not None:
            return self.dati(risultato["tipo"], risultato["simbolo"], condizione, risultato["riuso"])
        return self.aggiungi(risultato["tipo"], risultato["simbolo"], risultato["dati"], risultato["secondi"],
                             condizione, risultato["impronta_dati"])


# ---------------------------------------------------------------------------
# Monete, periodi, compiti
# ---------------------------------------------------------------------------


def _monete_con_posizione(monete: Optional[Union[Sequence[str], Mapping[str, int]]]) -> Tuple[Dict[str, int], bool]:
    """{simbolo: j} e se l'elenco e' quello ufficiale (regole.md, sezione 1, punto 1, e sezione 10, punto 2).

    Senza ``monete``: ``guardiano.leggi_monete_gruppo`` (l'elenco con l'impronta
    approvata, la sola fonte), j = posizione nel file. Un test, la prova a
    placebo o il trasferimento (``esame_vault``) possono passare una sequenza
    (j = posizione) o un dizionario {simbolo: j}.
    """
    if monete is None:
        elenco = leggi_monete_gruppo(str(RADICE_PROGETTO))
        return {s: j for j, s in enumerate(elenco)}, True
    coppie = list(monete.items()) if isinstance(monete, Mapping) else [(s, j) for j, s in enumerate(monete)]
    if not coppie:
        raise ValueError("nessuna moneta")
    risultato: Dict[str, int] = {}
    for simbolo, j in coppie:
        if not isinstance(simbolo, str) or not re.fullmatch(r"[A-Z0-9]+", simbolo):
            raise ValueError(f"simbolo non valido: {simbolo!r}")
        if isinstance(j, bool) or operator.index(j) < 0:
            raise ValueError(f"posizione non valida per {simbolo}: {j!r}")
        if simbolo in risultato:
            raise ValueError(f"{simbolo} compare due volte")
        risultato[simbolo] = operator.index(j)
    if len(set(risultato.values())) != len(risultato):
        raise ValueError("due monete con la stessa posizione j")
    return {s: risultato[s] for s in sorted(risultato)}, False


def _periodi(caricatore, monete: Mapping[str, int], ufficiali: bool, regole: Mapping) -> Dict[str, object]:
    """``dati.periodi_gruppo`` sui primi mesi delle schede (regole.md, sezione 1, punto 3); con l'elenco ufficiale il taglio deve essere quello di ``parametri.yaml``."""
    primi = {s: caricatore.scheda(s)["primo_mese"] for s in monete}
    periodi = dati.periodi_gruppo(primi)
    if ufficiali:
        if len(monete) != regole["numero_monete"]:
            raise ValueError(f"{len(monete)} monete nell'elenco, {regole['numero_monete']} in parametri.yaml")
        if periodi["fine_costruzione"] != regole["taglio_costruzione"] \
                or periodi["inizio_validazione"] != regole["inizio_validazione"]:
            raise ValueError(
                f"dati.periodi_gruppo da' il taglio {periodi['fine_costruzione']}, parametri.yaml "
                f"{regole['taglio_costruzione']}: STOP, si chiede all'utente (regole.md, sezione 0, punto 5)")
    return periodi


def _sorgente(ingressi_placebo: Optional[Mapping[str, Sequence[int]]], monete: Mapping[str, int]) -> Dict[str, object]:
    """L'origine degli ingressi della variante: il modulo, oppure ``ingressi_placebo`` (regole.md, sezione 13, «Il marcatore»).

    ``ingressi_placebo`` si rifiuta con un marcatore di campagna (qualunque
    simbolo): ``dati.VietatoInCampagna``.
    """
    if ingressi_placebo is None:
        return {"tipo": "modulo"}
    if _in_campagna():
        raise dati.VietatoInCampagna(
            "ingressi_placebo: vietato in una sessione di campagna (regole.md, sezione 13, «Il marcatore»)")
    if not isinstance(ingressi_placebo, Mapping):
        raise TypeError("ingressi_placebo: serve {simbolo: istanti delle barre di segnale}")
    sconosciute = sorted(set(ingressi_placebo) - set(monete))
    if sconosciute:
        raise ValueError(f"ingressi_placebo: monete fuori dall'elenco {sconosciute}")
    per_moneta: Dict[str, List[int]] = {}
    for simbolo in sorted(monete):
        istanti = []
        for ts in ingressi_placebo.get(simbolo, ()):
            if isinstance(ts, bool):
                raise ValueError(f"ingressi_placebo di {simbolo}: {ts!r} non e' un istante")
            istanti.append(operator.index(ts))
        if len(set(istanti)) != len(istanti):
            raise ValueError(f"ingressi_placebo di {simbolo}: istanti ripetuti")
        per_moneta[simbolo] = sorted(istanti)
    return {"tipo": "placebo", "per_moneta": per_moneta, "impronta": _sha256_testo(_canonico(per_moneta))}


def _sorgente_della_moneta(sorgente: Mapping, simbolo: str) -> Dict[str, object]:
    """La parte dell'origine degli ingressi che va al processo di una moneta."""
    if sorgente["tipo"] == "placebo":
        return {"tipo": "placebo", "ts": sorgente["per_moneta"][simbolo]}
    return {k: v for k, v in sorgente.items() if k != "per_moneta"}


def _descrizione_sorgente(sorgente: Mapping) -> Dict[str, object]:
    """L'origine degli ingressi nell'impronta e nel risultato (senza gli istanti, che sono nell'impronta)."""
    return {k: v for k, v in sorgente.items() if k != "per_moneta"}


def _impronta_dell_esame(compito_base: Mapping, monete: Mapping[str, int], extra: Mapping) -> Dict[str, str]:
    """Le impronte dell'esame: del codice (sezione 13 e variante), di ``p`` e dell'esame intero (regole.md, sezione 13)."""
    codice = _sha256_testo(_canonico({"strumenti": compito_base["impronte"],
                                      "variante": compito_base["impronta_variante"]}))
    parametri = _sha256_testo(compito_base["p_json"])
    esame = _sha256_testo(_canonico({
        "formato": FORMATO_AVANZAMENTO, "codice": codice, "parametri": parametri,
        "timeframe": compito_base["timeframe"], "opzioni": compito_base["opzioni"],
        "monete": sorted([s, j] for s, j in monete.items()), **extra}))
    return {"impronta": esame, "impronta_codice": codice, "impronta_parametri": parametri}


def _compito_base(modulo: Union[str, Path], p: Mapping, timeframe: str, regole: Mapping, opzioni: Mapping,
                  caricatore) -> Dict[str, object]:
    """La parte comune dei compiti: variante, parametri, timeframe, opzioni, caricatore, impronte."""
    if not isinstance(p, Mapping):
        raise TypeError("p deve essere un dizionario JSON")
    try:
        p_json = json.dumps(p, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)
    except (TypeError, ValueError) as errore:
        raise ValueError(f"p deve essere un dizionario JSON (numeri finiti): {errore}") from None
    if timeframe not in regole["timeframe_ammessi"]:
        raise ValueError(f"timeframe {timeframe!r} non ammesso: {regole['timeframe_ammessi']}")
    percorso = Path(modulo).resolve()
    impronta_variante = hashlib.sha256(percorso.read_bytes()).hexdigest()
    carica_modulo_variante(percorso, impronta_variante)  # il contratto si controlla subito
    impronte = impronte_degli_strumenti()
    if impronte[NOME_PARAMETRI] != regole["impronta"]:
        raise RuntimeError("parametri.yaml e' cambiato durante la lettura")
    return {
        "modulo": str(percorso), "impronta_variante": impronta_variante, "impronte": impronte, "regole": regole,
        "p_json": p_json, "timeframe": timeframe, "ms_per_barra": dati.durata_intervallo(timeframe),
        "opzioni": dict(opzioni), "caricatore": caricatore,
        # il marcatore lo legge il processo che avvia l'esame, una volta: i processi del gruppo non lo rileggono
        "in_campagna": _in_campagna(),
    }


def _controlla_processi(processi: int) -> int:
    if isinstance(processi, bool) or operator.index(processi) < 1:
        raise ValueError(f"processi deve essere un intero >= 1, non {processi!r}")
    return operator.index(processi)


# ---------------------------------------------------------------------------
# conta_trade_di_gruppo (regole.md, sezione 4)
# ---------------------------------------------------------------------------


def conta_trade_di_gruppo(
    modulo: Union[str, Path],
    p: Mapping,
    timeframe: str,
    *,
    moltiplicatore_costi: float = 1.0,
    ritardo_barre: int = 0,
    riempimento_intrabarra: Optional[str] = None,
    processi: int = 4,
    radice: Union[str, Path] = dati.RADICE_DEFAULT,
    monete: Optional[Union[Sequence[str], Mapping[str, int]]] = None,
    caricatore=None,
    ingressi_placebo: Optional[Mapping[str, Sequence[int]]] = None,
) -> Dict[str, object]:
    """La stima dei trade di gruppo prima di registrare una variante (regole.md, sezione 4, punti 2-4).

    ``motore.conta_trade`` una volta per moneta, sulle regole esatte che si
    registrano (``modulo`` e ``p``), con gli stessi parametri, funding, serie e
    filtro di liquidita' del test, sui dati di costruzione e con la fine della
    costruzione del gruppo (``fine_costruzione_ts``). Solo conteggi: niente R,
    niente pnl. ``moltiplicatore_costi``, ``ritardo_barre`` e
    ``riempimento_intrabarra`` servono ai casi della Fase 4; ``ingressi_placebo``
    alla prova a placebo (docstring del modulo, punto 5).

    Ritorna: ``trade_stimati`` (la somma), ``trade_stimati_per_moneta``
    ({simbolo: trade}, tutte le monete), ``monete_con_trade``,
    ``quota_moneta_piu_presente`` e ``moneta_piu_presente`` (None senza trade),
    ``esito`` («scarto» se la somma e' sotto ``gruppo.trade_minimi.costruzione``
    (700) o se una moneta ha piu' di ``gruppo.quota_massima_moneta`` (10%) dei
    trade, altrimenti «registrabile»), ``motivi`` dello scarto, ``minimo`` e
    ``quota_massima`` usati, ``stima_trade_validazione`` (sezione 4, punto 4: la
    somma su ogni moneta di trade di costruzione x giorni di validazione /
    giorni di costruzione della moneta, una STIMA da dichiarare come tale) e
    ``per_moneta`` (il dizionario di ``conta_trade`` di ogni moneta, piu' i mesi e
    le barre sotto la liquidita').
    """
    _controlla_argomenti_in_campagna("conta_trade_di_gruppo", monete, caricatore, radice)
    processi = _controlla_processi(processi)
    regole = regole_del_gruppo()
    opzioni = _opzioni_del_motore(regole, moltiplicatore_costi, ritardo_barre, riempimento_intrabarra)
    caricatore = CaricatoreDisco(str(radice)) if caricatore is None else caricatore
    base = _compito_base(modulo, p, timeframe, regole, opzioni, caricatore)
    posizioni, ufficiali = _monete_con_posizione(monete)
    sorgente = _sorgente(ingressi_placebo, posizioni)
    periodi = _periodi(caricatore, posizioni, ufficiali, regole)
    date_monete = periodi["monete"]
    compiti = [dict(base, tipo="conta", simbolo=s, j=posizioni[s], sorgente=_sorgente_della_moneta(sorgente, s),
                    inizio=date_monete[s]["inizio"].isoformat(), fine=periodi["fine_costruzione"].isoformat(),
                    inizio_conteggio_ts=None, fine_costruzione_ts=periodi["fine_costruzione_ts"])
               for s in sorted(posizioni, key=lambda s: (-date_monete[s]["giorni"], s))]
    per_moneta: Dict[str, Dict[str, object]] = {}
    for risultato in _esegui_compiti(compiti, processi):
        per_moneta[risultato["simbolo"]] = _in_json(risultato["dati"])
    per_moneta = {s: per_moneta[s] for s in sorted(per_moneta)}
    conteggi = {s: int(v["trade"]) for s, v in per_moneta.items()}
    totale = sum(conteggi.values())
    minimo = regole["trade_minimi"]["costruzione"]
    quota_massima = regole["quota_massima_moneta"]
    motivi = []
    if totale < minimo:
        motivi.append(f"trade stimati {totale} sotto {minimo}")
    quota, piu_presente = None, None
    if totale > 0:
        piu_presente = min(conteggi, key=lambda s: (-conteggi[s], s))
        quota = conteggi[piu_presente] / totale
        if quota > quota_massima:
            motivi.append(f"{piu_presente} ha il {quota:.1%} dei trade stimati, oltre il {quota_massima:.0%}")
    stima_validazione = math.fsum(
        conteggi[s] * date_monete[s]["giorni_validazione"] / date_monete[s]["giorni_costruzione"]
        for s in sorted(conteggi))
    return _in_json({
        "trade_stimati": totale,
        "trade_stimati_per_moneta": conteggi,
        "monete_con_trade": sum(1 for v in conteggi.values() if v > 0),
        "quota_moneta_piu_presente": quota,
        "moneta_piu_presente": piu_presente,
        "esito": "scarto" if motivi else "registrabile",
        "motivi": motivi,
        "minimo": minimo,
        "quota_massima": quota_massima,
        "stima_trade_validazione": stima_validazione,
        "timeframe": timeframe,
        "parametri": json.loads(base["p_json"]),
        "opzioni": opzioni,
        "ingressi": _descrizione_sorgente(sorgente),
        "fine_costruzione": periodi["fine_costruzione"],
        "per_moneta": per_moneta,
    })


# ---------------------------------------------------------------------------
# Le combinazioni (solo alla fine, da tutti i pezzi)
# ---------------------------------------------------------------------------


def _trade_della_moneta(pezzo: Mapping) -> List[Dict[str, object]]:
    campi = pezzo["trade"]["campi"]
    return [dict(zip(campi, riga)) for riga in pezzo["trade"]["righe"]]


def _trade_sommati(pezzi1: Mapping[str, Mapping]) -> Tuple[List[statistica.TradeDiGruppo], List[Dict[str, object]]]:
    """I trade di tutte le monete nell'ordine fisso (regole.md, sezione 5, punto 1) e, nello stesso ordine, i trade completi."""
    completi: Dict[Tuple[str, int], Dict[str, object]] = {}
    di_gruppo = []
    for simbolo in sorted(pezzi1):
        for t in _trade_della_moneta(pezzi1[simbolo]):
            di_gruppo.append(statistica.TradeDiGruppo(simbolo, int(t["ts_entrata"]), int(t["ts_uscita"]),
                                                      float(t["r"]), float(t["pnl"])))
            completi[(simbolo, int(t["ts_entrata"]))] = dict(t, simbolo=simbolo)
    ordinati = statistica.ordina_trade_di_gruppo(di_gruppo)
    return ordinati, [completi[(t.simbolo, t.ts_entrata)] for t in ordinati]


def _griglia(periodo: str, con_trade: Sequence[str], pezzi1: Mapping[str, Mapping], periodi: Optional[Mapping],
             ms: int, regole: Mapping, numero: int) -> Dict[str, object]:
    """Finestra unione, L, margine e sfasamenti comuni a tutte le monete (regole.md, sezione 5, punto 5, e sezione 9, punto 3)."""
    if periodo == "costruzione":
        inizio = min(periodi["monete"][s]["inizio_ts"] for s in con_trade)
        fine = periodi["fine_costruzione_ts"]
    elif periodo == "validazione":
        inizio = periodi["inizio_validazione_ts"]
        fine = dati.ms_da_data(periodi["fine_validazione"] + timedelta(days=1)) - 1
    else:
        inizio = dati.ms_da_data(dati.INIZIO_VAULT)
        fine = dati.ms_da_data(dati.FINE_VAULT + timedelta(days=1)) - 1
    durata = fine + 1 - inizio
    if durata % ms:
        raise ValueError(f"la finestra unione non e' un numero intero di barre da {ms} ms")
    barre = durata // ms
    giorni_ms = regole["margine_sfasamento_giorni"] * GIORNO_MS
    if giorni_ms % ms:
        raise ValueError(f"{regole['margine_sfasamento_giorni']} giorni non sono un numero intero di barre")
    durata_massima_ms = max(int(pezzi1[s]["durata_massima_ms"]) for s in con_trade)
    durata_massima_barre = -(-durata_massima_ms // ms)
    griglia = statistica.griglia_sfasamenti(barre, max(giorni_ms // ms, durata_massima_barre), numero)
    griglia.update({"finestra_unione": [inizio, fine], "durata_massima_barre": durata_massima_barre})
    griglia["impronta"] = _sha256_testo(_canonico({"finestra": [inizio, fine], "ms": ms,
                                                   "sfasamenti": griglia["sfasamenti"]}))
    return griglia


def _confronto(r: Sequence[float], blocco: int, baseline: Mapping, pavimento: Mapping, regole: Mapping) -> Dict[str, object]:
    """``statistica.contro_baseline`` con il pavimento delle sfasate (regole.md, sezione 5, punto 6), piu' la lettura senza quel pavimento, solo informativa (sezione 15)."""
    n, seme = regole["bootstrap_ricampionamenti"], regole["bootstrap_seme"]
    if pavimento["valutabile"]:
        risultato = statistica.contro_baseline(r, blocco, dict(baseline), n=n, seme=seme,
                                               pavimento_minimo=pavimento["pavimento"], dettagli=True)
        motivo = None
    else:
        # meno di 2 sfasate con trade: la variante e' non valutabile (sezione 5, punto 5)
        risultato = statistica.contro_baseline(r, blocco, dict(baseline, valutabile=False), n=n, seme=seme,
                                               dettagli=True)
        motivo = "pavimento delle sfasate non valutabile (meno di 2 sfasate con trade)"
    senza = statistica.contro_baseline(r, blocco, dict(baseline), n=n, seme=seme)
    risultato = dict(risultato)
    risultato["errore_differenza"] = risultato.pop("errore_standard")
    if motivo is None and not risultato["valutabile"]:
        motivo = baseline.get("motivo") or "meno di 3 blocchi interi o candidato senza rumore stimabile"
    risultato["motivo_non_valutabile"] = motivo
    risultato["senza_pavimento_sfasate"] = {
        chiave: senza[chiave] for chiave in ("differenza", "errore_standard", "errore_candidato", "errore_minimo",
                                             "t", "soglia", "netta", "p_value", "valutabile")}
    return risultato


def _metriche(pezzi1: Mapping[str, Mapping], con_trade: Sequence[str], monete_nel_periodo: int,
              regole: Mapping) -> Dict[str, object]:
    """``motore.metriche_di_gruppo`` sui trade sommati (regole.md, sezione 8, punto 1, e sezione 9, punto 2)."""
    return motore.metriche_di_gruppo(
        {s: [{"ts_entrata": t["ts_entrata"], "ts_uscita": t["ts_uscita"], "r": t["r"], "pnl": t["pnl"]}
             for t in _trade_della_moneta(pezzi1[s])] for s in con_trade},
        monete_nel_periodo, regole["capitale_per_moneta"], regole["trade_migliori_tolti"])


def _stabilita(ordinati: Sequence[statistica.TradeDiGruppo], metriche: Mapping, b_per_moneta: Mapping,
               regole: Mapping) -> Dict[str, object]:
    """La stabilita' della Fase 4 (regole.md, sezione 6, punto 2.4).

    Negli anni di costruzione (anno d'uscita) con almeno ``anni_trade_minimi``
    (100) trade sommati, l'R medio dei trade usciti nell'anno (la chiave
    ``r_medio_per_anno`` di ``motore.metriche_di_gruppo``) deve superare la B
    ripesata sui trade di quell'anno, Σ r_j · b_j / Σ r_j con r_j i trade
    dell'anno della moneta j (la stessa funzione degli estremi,
    ``statistica.b_ripesata``). Superata se gli anni sopra sono piu' della meta'
    degli anni che contano (e ce n'e' almeno uno).
    """
    per_anno: Dict[int, List[statistica.TradeDiGruppo]] = {}
    for t in ordinati:
        per_anno.setdefault(dati.mese_utc(t.ts_uscita)[0], []).append(t)
    anni: Dict[str, Dict[str, object]] = {}
    for anno, trade in sorted(per_anno.items()):
        if len(trade) < regole["anni_trade_minimi"]:
            continue
        b_ripesata = statistica.b_ripesata(trade, b_per_moneta)
        r_medio = metriche["r_medio_per_anno"][anno]
        anni[str(anno)] = {"trade": len(trade), "r_medio": r_medio, "b_ripesata": b_ripesata,
                           "sopra": bool(r_medio > b_ripesata)}
    sopra = sum(1 for v in anni.values() if v["sopra"])
    return {"anni": anni, "anni_che_contano": len(anni), "anni_sopra": sopra,
            "trade_minimi_per_anno": regole["anni_trade_minimi"],
            "superata": bool(anni) and 2 * sopra > len(anni)}


def _combina_esame(pezzi1: Mapping[str, Mapping], pezzi2: Mapping[str, Mapping], griglia: Optional[Mapping],
                   posizioni: Mapping[str, int], periodo: str, ms: int, regole: Mapping,
                   con_baseline_a: bool) -> Tuple[Dict[str, object], List[Dict[str, object]]]:
    """Tutte le combinazioni dell'esame, dai pezzi (regole.md, sezioni 5, 6.2, 7 e 8.1)."""
    ordinati, trade_in_ordine = _trade_sommati(pezzi1)
    n_j = {s: len(pezzi1[s]["trade"]["righe"]) for s in sorted(pezzi1)}
    con_trade = [s for s in sorted(n_j) if n_j[s] > 0]
    totale = len(ordinati)
    monete_nel_periodo = sum(1 for s in pezzi1 if pezzi1[s]["barre_nel_periodo"] > 0)
    metriche = _metriche(pezzi1, con_trade, monete_nel_periodo, regole)
    minimo = regole["trade_minimi"][periodo]

    ris: Dict[str, object] = {
        "trade_minimi": {"minimo": minimo, "superati": totale >= minimo},
        "monete_nel_gruppo": len(posizioni),
        "monete_nel_periodo": monete_nel_periodo,
        "monete_con_trade": len(con_trade),
        "quota_moneta_piu_presente": None,
        "moneta_piu_presente": None,
        "metriche": dict(metriche, trade=metriche["n_trade"]),
    }
    if con_trade:
        piu = min(con_trade, key=lambda s: (-n_j[s], s))
        ris["moneta_piu_presente"], ris["quota_moneta_piu_presente"] = piu, n_j[piu] / totale

    # tabella per moneta (sezione 8, punto 2, e sezione 13)
    per_moneta: Dict[str, Dict[str, object]] = {}
    for s in sorted(pezzi1):
        pezzo = pezzi1[s]
        trade_s = _trade_della_moneta(pezzo)
        a, b = pezzo.get("a"), pezzo.get("b")
        per_moneta[s] = {
            "j": posizioni[s],
            "trade": n_j[s],
            "r_medio": metriche["per_moneta"][s]["r_medio"] if n_j[s] else None,
            "pnl": math.fsum(float(t["pnl"]) for t in trade_s),
            "peso": n_j[s] / totale if totale else 0.0,
            "long": sum(1 for t in trade_s if t["direzione"] == "long"),
            "short": sum(1 for t in trade_s if t["direzione"] == "short"),
            "ridotti": sum(1 for t in trade_s if t["ridotto"]),
            "violazioni_liquidazione": sum(1 for t in trade_s if t["violazione_liquidazione"]),
            "slippage_per_lato": pezzo["slippage_per_lato"],
            "barre": pezzo["barre"],
            "barre_nel_periodo": pezzo["barre_nel_periodo"],
            "barre_tolte_allineamento": pezzo["barre_tolte"],
            "mesi_sotto_liquidita": len(pezzo["mesi_sotto_liquidita"]),
            "ingressi_dati": pezzo["ingressi_dati"],
            "conteggi": pezzo["conteggi"],
            "barre_vietate": pezzo.get("vietate"),
            "a": None if not a or a["base"] is None else {
                "media": a["base"]["media"], "errore_standard": a["base"]["errore_standard"],
                "deviazione_standard": a["base"]["deviazione_standard"], "n_trade": a["n_trade"],
                "blocco": a["blocco"], "n_blocchi": a["base"]["n_blocchi"], "valutabile": a["base"]["valutabile"]},
            "b_j": None,
            "b_simulazioni_con_trade": None if not b or not b["entrano"] else sum(
                1 for x in b["r_medio_per_seme"] if x is not None),
            "b_durata_media": None if not b else b["durata_media"],
            "b_ingressi_entrano": None if not b else b["entrano"],
            "sfasate": None if s not in pezzi2 else {
                k: pezzi2[s][k] for k in ("n_segnali", "segnali_fuori_dalla_finestra_unione", "segnali_coincidenti",
                                          "saltati_totali", "ingressi_totali")},
            "controllo_casuale": pezzo["controllo_casuale"],
        }
    ris["per_moneta"] = per_moneta
    ris["btc"] = _btc_dai_pezzi(pezzi1)
    ris["liquidazione"] = {"violazioni": sum(v["violazioni_liquidazione"] for v in per_moneta.values()),
                           "trade_ridotti": sum(v["ridotti"] for v in per_moneta.values())}

    if totale == 0:
        ris.update({"valutabile": False, "motivi_non_valutabile": ["il candidato non ha trade nel periodo"],
                    "t": -math.inf, "p_value": 1.0, "percentile_caso": None, "baseline_a": None, "baseline_b": None,
                    "pavimento_sfasate": None, "blocco": None, "n_blocchi": 0, "uscite_massime_in_un_giorno": 0,
                    "durata_massima_ms": 0, "durata_massima_barre": 0, "effetto_grappolo": None, "estremi": None,
                    "stabilita": None, "quota_monete_sopra_b_j": None,
                    "posizioni_aperte_insieme": {"long": 0, "short": 0, "totale": 0}, "buy_and_hold_per_anno": {}})
        if periodo == "costruzione":
            ris["candidato"] = None if not con_baseline_a else False
        else:
            ris["validazione"] = {"trade_minimi_superati": False, "r_medio_positivo": False, "p_value_asticella": 1.0}
        return ris, trade_in_ordine

    r = [t.r for t in ordinati]
    blocco = statistica.lunghezza_blocco([t.ts_entrata for t in ordinati], [t.ts_uscita for t in ordinati])
    durata_massima_ms = max(t.ts_uscita - t.ts_entrata for t in ordinati)
    ris.update({
        "blocco": blocco,
        "n_blocchi": totale // blocco,
        "uscite_massime_in_un_giorno": max(Counter(t.ts_uscita // GIORNO_MS for t in ordinati).values()),
        "durata_massima_ms": durata_massima_ms,
        "durata_massima_barre": -(-durata_massima_ms // ms),
        "posizioni_aperte_insieme": motore.posizioni_aperte_insieme(trade_in_ordine),
    })

    # (b) di gruppo (sezione 5, punto 4)
    base_b = statistica.baseline_casuale_di_gruppo(
        {s: (pezzi1[s]["b"]["r_medio_per_seme"] if pezzi1[s]["b"]["entrano"] else None) for s in con_trade},
        {s: n_j[s] for s in con_trade})
    # pavimento delle sfasate (sezione 5, punto 5)
    m_sfasate, n_sfasate = statistica.medie_sfasate({s: pezzi2[s]["per_s"] for s in pezzi2}, griglia["numero"])
    pavimento = statistica.pavimento_sfasamento(m_sfasate, n_sfasate, totale)
    ris["pavimento_sfasate"] = dict(pavimento, **{
        "L": griglia["barre_finestra"], "margine": griglia["margine"], "margine_richiesto": griglia["margine_richiesto"],
        "durata_massima_barre": griglia["durata_massima_barre"], "sfasamenti_richiesti": griglia["sfasamenti_richiesti"],
        "numero": griglia["numero"], "tutti_gli_interi": griglia["tutti_gli_interi"],
        "finestra_unione": griglia["finestra_unione"],
        "saltati_totali": {motivo: sum(pezzi2[s]["saltati_totali"][motivo] for s in sorted(pezzi2)) for motivo in SALTI},
        "segnali_fuori_dalla_finestra_unione": sum(pezzi2[s]["segnali_fuori_dalla_finestra_unione"]
                                                   for s in sorted(pezzi2)),
        "segnali_coincidenti": sum(pezzi2[s]["segnali_coincidenti"] for s in sorted(pezzi2)),
        "ingressi_totali": sum(pezzi2[s]["ingressi_totali"] for s in sorted(pezzi2)),
    })

    # confronti (sezione 5, punto 6)
    conf_b = _confronto(r, blocco, base_b, pavimento, regole)
    trade_per_m = []
    for i in range(base_b["simulazioni_per_moneta"]):
        presenti = [pezzi1[s]["b"]["trade_per_seme"][i] for s in con_trade
                    if pezzi1[s]["b"]["entrano"] and pezzi1[s]["b"]["r_medio_per_seme"][i] is not None]
        if presenti:
            trade_per_m.append(sum(presenti))
    vietate = [pezzi1[s]["vietate"] for s in con_trade]
    barre = sum(pezzi1[s]["barre"] for s in con_trade)
    scartati = [pezzi1[s]["b"]["segnali_non_validi_medi"] + pezzi1[s]["b"]["segnali_senza_barra_medi"]
                for s in con_trade if pezzi1[s]["b"]["entrano"]]
    ris["baseline_b"] = dict({k: v for k, v in base_b.items() if k != "valori"}, **conf_b, **{
        "trade_per_simulazione_medio": float(np.mean(trade_per_m)) if trade_per_m else None,
        "semi": {"formula": f"{regole['passo_semi']}*j + s", "simulazioni_per_moneta":
                 regole["simulazioni_baseline_casuale"],
                 "primo_per_moneta": {s: pezzi1[s]["b"]["primo_seme"] for s in con_trade}},
        "pavimento_sfasate": pavimento["pavimento"],
        "quota_barre_vietate_segnale_non_valido": sum(v["segnale_non_valido"] for v in vietate) / barre,
        "segnali_scartati_per_simulazione_medi": float(np.mean(scartati)) if scartati else None,
    })
    valori_m = np.asarray(base_b["valori"], dtype=float)
    ris["percentile_caso"] = (statistica.percentile_del_candidato(metriche["r_medio"], valori_m)
                              if valori_m.size else None)
    ris["baseline_b"]["percentile_caso"] = ris["percentile_caso"]

    motivi = []
    if not conf_b["valutabile"]:
        motivi.append("confronto con la (b) non valutabile: " + str(conf_b["motivo_non_valutabile"]))
    conf_a = None
    ris["baseline_a"] = None
    if con_baseline_a:
        base_a = statistica.baseline_da_trade_di_gruppo(
            {s: pezzi1[s]["a"]["base"] for s in con_trade}, {s: n_j[s] for s in con_trade})
        conf_a = _confronto(r, blocco, base_a, pavimento, regole)
        ris["baseline_a"] = dict({k: v for k, v in base_a.items() if k != "per_moneta"}, **conf_a,
                                 pavimento_sfasate=pavimento["pavimento"])
        if not conf_a["valutabile"]:
            motivi.append("confronto con la (a) non valutabile: " + str(conf_a["motivo_non_valutabile"]))
    if not pavimento["valutabile"]:
        motivi.append("pavimento delle sfasate non valutabile: meno di 2 sfasate con trade")
    ris["valutabile"] = not motivi
    ris["motivi_non_valutabile"] = motivi
    # Una variante non valutabile (anche solo per la (a)) ha t = -inf e p-value 1: e' in fondo all'ordine dei
    # ritocchi (sezione 8 del protocollo) ed entra nell'asticella con p-value 1 (regole.md, sezione 7, punto 5).
    # Il t e il p-value del confronto con la (b) restano in ``baseline_b``.
    ris["t"] = conf_b["t"] if ris["valutabile"] else -math.inf
    ris["p_value"] = conf_b["p_value"] if ris["valutabile"] else 1.0
    ris["effetto_grappolo"] = statistica.effetto_grappolo(conf_b["errore_candidato_senza_pavimento"], r)

    # b_j, stabilita', estremi, quota delle monete sopra la propria b_j (sezione 6, punto 2)
    b_per_moneta = base_b["b_per_moneta"]
    for s in con_trade:
        per_moneta[s]["b_j"] = b_per_moneta.get(s)
    b_numero = base_b["media"]
    if base_b["valutabile"] and math.isfinite(b_numero):
        ris["stabilita"] = _stabilita(ordinati, metriche, b_per_moneta, regole)
        ris["estremi"] = statistica.estremi_di_gruppo(
            ordinati, b_numero, b_per_moneta, regole["trade_migliori_tolti"], regole["giorni_migliori_tolti"],
            regole["monete_migliori_tolte"])
        con_dieci = [s for s in con_trade if n_j[s] >= TRADE_MINIMI_PER_LA_QUOTA_SOPRA_B
                     and b_per_moneta.get(s) is not None]
        sopra_b = [s for s in con_dieci if per_moneta[s]["r_medio"] > b_per_moneta[s]]
        ris["quota_monete_sopra_b_j"] = {"monete_con_almeno_10_trade": len(con_dieci), "sopra_b_j": len(sopra_b),
                                         "quota": len(sopra_b) / len(con_dieci) if con_dieci else None}
    else:
        ris["stabilita"] = ris["estremi"] = ris["quota_monete_sopra_b_j"] = None

    ris["buy_and_hold_per_anno"] = _buy_and_hold_di_gruppo(pezzi1, con_trade, n_j, totale)

    # candidato e validazione (sezione 5, punto 7; sezione 7, punti 4-5)
    r_medio = metriche["r_medio"]
    if periodo == "costruzione":
        ris["candidato"] = None if conf_a is None else bool(
            ris["valutabile"] and conf_a["netta"] and conf_b["netta"] and r_medio > 0)
    else:
        sopra_minimo = totale >= minimo
        ris["validazione"] = {
            "trade_minimi_superati": sopra_minimo,
            "r_medio_positivo": r_medio > 0,
            # 1 per chi ha meno di 300 trade o e' non valutabile (sezione 7, punto 5)
            "p_value_asticella": ris["p_value"] if (ris["valutabile"] and sopra_minimo) else 1.0,
        }
    return ris, trade_in_ordine


def _buy_and_hold_di_gruppo(pezzi1: Mapping[str, Mapping], con_trade: Sequence[str], n_j: Mapping[str, int],
                            totale: int) -> Dict[str, Dict[str, float]]:
    """La (c): buy and hold per anno, long e short, di ogni moneta con trade, combinato con gli stessi pesi w_j = n_j / N (regole.md, sezione 5, punto 8).

    Solo contesto. In un anno in cui una moneta con trade non ha candele (non era
    ancora quotata) il suo termine non c'e': il buy and hold dell'anno e' la somma
    dei w_j · rendimento delle monete presenti, e ``peso_presente`` (la somma dei
    loro w_j) dice quanta parte dei pesi c'e'. Le somme vanno in ordine dei
    caratteri dei simboli.
    """
    bh: Dict[str, Dict[str, float]] = {}
    for anno in sorted({anno for s in con_trade for anno in pezzi1[s]["buy_and_hold"]}):
        presenti = [s for s in sorted(con_trade) if anno in pezzi1[s]["buy_and_hold"]]
        voce = {lato: math.fsum((n_j[s] / totale) * pezzi1[s]["buy_and_hold"][anno][lato] for s in presenti)
                for lato in ("long", "short")}
        voce["peso_presente"] = math.fsum(n_j[s] / totale for s in presenti)
        voce["monete_presenti"] = len(presenti)
        bh[anno] = voce
    return bh


def _btc_dai_pezzi(pezzi1: Mapping[str, Mapping]) -> Optional[Dict[str, object]]:
    """Le candele di BTCUSDT passate alle funzioni della variante (regole.md, sezione 3, punto 3): le stesse per ogni moneta dell'esame."""
    viste = {_canonico_libero(pezzi1[s]["btc"]) for s in pezzi1}
    if len(viste) > 1:
        raise RuntimeError("i pezzi hanno visto candele di BTCUSDT diverse: i dati sono cambiati durante l'esame")
    return dict(pezzi1[sorted(pezzi1)[0]]["btc"]) if pezzi1 else None


def _scrivi_trade(percorso: Path, trade: Sequence[Mapping]) -> None:
    """I trade sommati in JSONL, nell'ordine fisso (regole.md, sezione 6, punto 1, e sezione 8, punto 1), scritti in modo atomico."""
    percorso.parent.mkdir(parents=True, exist_ok=True)
    temporaneo = percorso.with_name(percorso.name + ".parziale")
    with open(temporaneo, "w", encoding="utf-8") as flusso:
        for t in trade:
            voce = {"simbolo": t["simbolo"]}
            voce.update({campo: t[campo] for campo in CAMPI_TRADE})
            flusso.write(json.dumps(voce, ensure_ascii=False) + "\n")
    os.replace(temporaneo, percorso)


# ---------------------------------------------------------------------------
# esame_di_gruppo (regole.md, sezioni 5-8)
# ---------------------------------------------------------------------------


def _controlla_cartella_del_placebo(cartella_campagna, radice) -> Path:
    """La cartella di uscita della prova a placebo: obbligatoria e fuori da ``research/campagne/`` (regole.md, sezione 11, punti 1 e 5).

    I numeri della prova non vanno mai in ``campagne/`` (ne' sul branch
    principale ne' su quello della campagna): con ``ingressi_placebo`` la
    cartella si passa sempre (di norma sotto ``research/taratura/placebo_gruppo/``
    del branch di coordinamento, o una cartella di lavoro) e non puo' stare sotto
    ``<research del progetto>/campagne/`` ne' sotto ``<radice>/campagne/``.
    ValueError se no.
    """
    if cartella_campagna is None:
        raise ValueError("ingressi_placebo: serve cartella_campagna (i numeri della prova a placebo non vanno in "
                         "campagne/GRUPPO/, regole.md, sezione 11, punto 5)")
    cartella = Path(cartella_campagna).resolve()
    for vietata in {(Path(dati.RADICE_DEFAULT) / "campagne").resolve(), (Path(radice) / "campagne").resolve()}:
        if cartella == vietata or vietata in cartella.parents:
            raise ValueError(f"ingressi_placebo: la cartella di uscita {cartella} e' sotto {vietata}: i numeri della "
                             "prova a placebo non vanno in campagne/ (regole.md, sezione 11, punto 5)")
    return cartella


def _esame(modulo, p, timeframe: str, periodo: str, id: str, *, moltiplicatore_costi, ritardo_barre,
           riempimento_intrabarra, con_baseline_a: bool, processi: int, radice, cartella_campagna, monete,
           caricatore, sorgente_richiesta, chi: str = "esame_di_gruppo") -> Dict[str, object]:
    """Il corpo di ``esame_di_gruppo`` e di ``controllo_positivo`` (regole.md, sezioni 5, 6.2, 7, 8.1 e 5.10).

    I controlli della sessione di campagna stanno QUI, prima di toccare i dati,
    cosi' valgono per ogni strada che porta all'esame (sezione 7, punto 2.4, e
    sezione 13): in validazione il via libera; ``monete``, ``caricatore`` e una
    ``radice`` diversa rifiutati; ingressi che non vengono dal modulo
    (``ingressi_placebo``) rifiutati, salvo quelli del controllo positivo, che
    calcola ``gruppo.py``.
    """
    if periodo not in PERIODI:
        raise ValueError(f"periodo deve essere uno di {PERIODI}, non {periodo!r}")
    if periodo == "validazione" and _in_campagna():
        controlla_via_libera()  # prima di tutto (sezione 7, punto 2.4)
    _controlla_argomenti_in_campagna(chi, monete, caricatore, radice)
    if not isinstance(id, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]*", id) or ".." in id:
        raise ValueError(f"id non valido: {id!r}")
    processi = _controlla_processi(processi)
    regole = regole_del_gruppo()
    opzioni = _opzioni_del_motore(regole, moltiplicatore_costi, ritardo_barre, riempimento_intrabarra)
    caricatore = CaricatoreDisco(str(radice)) if caricatore is None else caricatore
    posizioni, ufficiali = _monete_con_posizione(monete)
    sorgente = sorgente_richiesta(posizioni)
    if sorgente["tipo"] not in ("modulo", "guarda_avanti") and _in_campagna():
        raise dati.VietatoInCampagna(f"{chi}: ingressi {sorgente['tipo']!r} vietati in una sessione di campagna "
                                     "(regole.md, sezione 13, «Il marcatore»)")
    if sorgente["tipo"] == "placebo":
        cartella = _controlla_cartella_del_placebo(cartella_campagna, radice)
    else:
        cartella = Path(cartella_campagna) if cartella_campagna is not None else Path(radice) / "campagne" / "GRUPPO"
    base = _compito_base(modulo, p, timeframe, regole, opzioni, caricatore)
    periodi = _periodi(caricatore, posizioni, ufficiali, regole)
    ms = base["ms_per_barra"]
    impronte = _impronta_dell_esame(base, posizioni, {"periodo": periodo, "con_baseline_a": bool(con_baseline_a),
                                                      "ingressi": _descrizione_sorgente(sorgente)})
    file_avanzamento = cartella / "avanzamento" / f"{id}_{periodo}.jsonl"
    avanzamento = _Avanzamento(file_avanzamento, impronte)
    date_monete = periodi["monete"]
    in_ordine = sorted(posizioni, key=lambda s: (-date_monete[s]["giorni"], s))
    fine = periodi["fine_costruzione"] if periodo == "costruzione" else periodi["fine_validazione"]
    conteggio = None if periodo == "costruzione" else periodi["inizio_validazione_ts"]

    def compito_moneta(simbolo: str, tipo: str, **altro) -> Dict[str, object]:
        return dict(base, tipo=tipo, simbolo=simbolo, j=posizioni[simbolo], periodo=periodo,
                    sorgente=_sorgente_della_moneta(sorgente, simbolo),
                    inizio=date_monete[simbolo]["inizio"].isoformat(), fine=fine.isoformat(),
                    inizio_conteggio_ts=conteggio, con_a=bool(con_baseline_a), **altro)

    # fase 1: test, (a), (b) di ogni moneta. Ogni moneta va comunque a un processo, che ricarica i suoi dati: se
    # hanno l'impronta di una riga salvata il pezzo si riprende da li', se no si ricalcola (sezione 13).
    pezzi1: Dict[str, Dict[str, object]] = {}
    compiti = [compito_moneta(simbolo, "fase1", riusabili=avanzamento.impronte_salvate("fase1", simbolo))
               for simbolo in in_ordine]
    for risultato in _esegui_compiti(compiti, processi):
        pezzi1[risultato["simbolo"]] = avanzamento.prendi(risultato)
    pezzi1 = {s: pezzi1[s] for s in sorted(pezzi1)}

    # fase 2: le sfasate delle monete con trade, con la griglia comune
    con_trade = [s for s in sorted(pezzi1) if pezzi1[s]["trade"]["righe"]]
    pezzi2: Dict[str, Dict[str, object]] = {}
    griglia = None
    if con_trade:
        griglia = _griglia(periodo, con_trade, pezzi1, periodi, ms, regole, regole["sfasamenti_pavimento"])
        compiti = []
        for simbolo in [s for s in in_ordine if s in con_trade]:
            finestra_moneta = ([date_monete[simbolo]["inizio_ts"], periodi["fine_costruzione_ts"]]
                               if periodo == "costruzione" else griglia["finestra_unione"])
            compiti.append(compito_moneta(
                simbolo, "sfasate", ts_segnali=pezzi1[simbolo]["ts_segnali"],
                finestra_unione=griglia["finestra_unione"], finestra_moneta=finestra_moneta,
                sfasamenti=griglia["sfasamenti"], impronta_vietate=pezzi1[simbolo]["vietate"]["impronta"],
                trade_completi=False,
                riusabili=avanzamento.impronte_salvate("sfasate", simbolo, griglia["impronta"])))
        for risultato in _esegui_compiti(compiti, processi):
            pezzi2[risultato["simbolo"]] = avanzamento.prendi(risultato, griglia["impronta"])
        pezzi2 = {s: pezzi2[s] for s in sorted(pezzi2)}

    combinato, trade_in_ordine = _combina_esame(pezzi1, pezzi2, griglia, posizioni, periodo, ms, regole,
                                                bool(con_baseline_a))
    file_trade = cartella / "trade" / f"{id}_{periodo}.jsonl"
    _scrivi_trade(file_trade, trade_in_ordine)
    risultato = {
        "id": id,
        "periodo": periodo,
        "timeframe": timeframe,
        "parametri": json.loads(base["p_json"]),
        "opzioni": dict(opzioni, con_baseline_a=bool(con_baseline_a)),
        "ingressi": _descrizione_sorgente(sorgente),
        "date": {"fine_costruzione": periodi["fine_costruzione"], "inizio_validazione": periodi["inizio_validazione"],
                 "fine_validazione": periodi["fine_validazione"], "giorni_validazione": periodi["giorni_validazione"]},
        "impronte": {"esame": impronte["impronta"], "codice": impronte["impronta_codice"],
                     "parametri": impronte["impronta_parametri"], "variante": base["impronta_variante"],
                     "strumenti": base["impronte"]},
        "file": {"trade": str(file_trade), "avanzamento": str(file_avanzamento)},
        "ripresa": {"pezzi_ripresi": avanzamento.pezzi_ripresi, "pezzi_calcolati": avanzamento.pezzi_calcolati,
                    "righe_di_altre_impronte": avanzamento.righe_di_altre_impronte,
                    "righe_illeggibili": avanzamento.righe_illeggibili},
    }
    risultato.update(combinato)
    return _in_json(risultato)


def esame_di_gruppo(
    modulo: Union[str, Path],
    p: Mapping,
    timeframe: str,
    periodo: str,
    id: str,
    *,
    moltiplicatore_costi: float = 1.0,
    ritardo_barre: int = 0,
    riempimento_intrabarra: Optional[str] = None,
    con_baseline_a: bool = True,
    processi: int = 4,
    radice: Union[str, Path] = dati.RADICE_DEFAULT,
    cartella_campagna: Optional[Union[str, Path]] = None,
    monete: Optional[Union[Sequence[str], Mapping[str, int]]] = None,
    caricatore=None,
    ingressi_placebo: Optional[Mapping[str, Sequence[int]]] = None,
) -> Dict[str, object]:
    """L'esame di una variante sui trade sommati di tutte le monete (regole.md, sezioni 5, 6.2, 7 e 8.1).

    ``modulo``: il file della variante (contratto nella docstring del modulo);
    ``p``: i suoi parametri; ``timeframe``; ``periodo``: «costruzione» o
    «validazione»; ``id``: l'identificativo del test (``GRUPPO-NNN``; una
    verifica della Fase 4 usa un id suo, per esempio ``GRUPPO-007-costi2``,
    perche' file dei trade e di avanzamento sono per id e periodo).
    ``moltiplicatore_costi``, ``ritardo_barre`` e ``riempimento_intrabarra``
    (predefinito quello di ``parametri.yaml``) sono le verifiche della Fase 4,
    applicate a test, (a), (b) e sfasate; ``con_baseline_a=False`` salta la (a),
    che le verifiche non usano. ``processi``: processi in parallelo (una moneta
    per processo). ``radice``: la cartella ``research/`` dei dati;
    ``cartella_campagna``: di norma ``<radice>/campagne/GRUPPO``. ``monete`` e
    ``caricatore`` servono ai test e alla prova a placebo (``_monete_con_posizione``
    e ``CaricatoreDisco``); ``ingressi_placebo`` solo alla prova a placebo
    (docstring del modulo, punto 5), e allora ``cartella_campagna`` e' obbligatoria
    e fuori da ``research/campagne/`` (sezione 11, punto 5).

    In validazione, con un marcatore di campagna, PRIMA di tutto
    ``controlla_via_libera`` (sezione 7, punto 2.4): senza il via libera o con
    un'impronta diversa alza ``ViaLiberaNonValida`` e non tocca nulla, qualunque
    sia ``cartella_campagna``. Senza marcatore il controllo non c'e'. Questi
    controlli, e i rifiuti degli argomenti dei test in campagna, li fa il corpo
    comune dell'esame (``_esame``).

    Salva i trade sommati in ``<cartella_campagna>/trade/<id>_<periodo>.jsonl``
    (una riga per trade, nell'ordine fisso, con ``simbolo`` e ``CAMPI_TRADE``) e
    l'avanzamento in ``<cartella_campagna>/avanzamento/<id>_<periodo>.jsonl``.

    Ritorna un dizionario JSON (sezione 8, punto 1), fra cui: ``metriche``
    (``motore.metriche_di_gruppo``, con ``trade`` = ``n_trade``), ``per_moneta``
    (la tabella, con b_j), ``blocco``, ``n_blocchi``,
    ``uscite_massime_in_un_giorno``, ``durata_massima_ms`` e ``_barre``,
    ``effetto_grappolo``, ``baseline_a`` e ``baseline_b`` (i numeri della
    baseline di gruppo e il confronto di ``contro_baseline`` con il pavimento
    delle sfasate; l'errore della differenza e' ``errore_differenza``;
    ``senza_pavimento_sfasate`` solo come informazione), ``pavimento_sfasate``,
    ``percentile_caso``, ``t`` e ``p_value`` (contro la (b)), ``valutabile`` e
    ``motivi_non_valutabile`` (una variante non valutabile ha ``t`` = -inf e
    ``p_value`` 1), ``candidato`` (costruzione: batte nettamente (a) e
    (b) e R medio > 0; None senza la (a)) oppure ``validazione`` (trade minimi,
    R medio positivo, ``p_value_asticella``), ``stabilita``, ``estremi``,
    ``quota_monete_sopra_b_j``, ``posizioni_aperte_insieme``,
    ``buy_and_hold_per_anno`` (con ``peso_presente``), ``liquidazione`` (violazioni
    e trade ridotti), ``monete_con_trade``, ``quota_moneta_piu_presente``, ``btc``
    (le candele di BTCUSDT passate alla variante), le impronte, i file e
    ``ripresa`` (pezzi ripresi dall'avanzamento e pezzi calcolati).
    """
    return _esame(modulo, p, timeframe, periodo, id, moltiplicatore_costi=moltiplicatore_costi,
                  ritardo_barre=ritardo_barre, riempimento_intrabarra=riempimento_intrabarra,
                  con_baseline_a=con_baseline_a, processi=processi, radice=radice,
                  cartella_campagna=cartella_campagna, monete=monete, caricatore=caricatore,
                  sorgente_richiesta=lambda posizioni: _sorgente(ingressi_placebo, posizioni), chi="esame_di_gruppo")


# ---------------------------------------------------------------------------
# controllo_positivo (regole.md, sezione 5, punto 10)
# ---------------------------------------------------------------------------


def controllo_positivo(
    modulo: Union[str, Path],
    p: Mapping,
    timeframe: str,
    direzione: str,
    *,
    id: str = "GRUPPO-controllo-positivo",
    processi: int = 4,
    radice: Union[str, Path] = dati.RADICE_DEFAULT,
    cartella_campagna: Optional[Union[str, Path]] = None,
    monete: Optional[Union[Sequence[str], Mapping[str, int]]] = None,
    caricatore=None,
) -> Dict[str, object]:
    """Il controllo positivo degli strumenti, prima della prima variante (regole.md, sezione 5, punto 10; ``lezioni/metodo.md``).

    ``modulo`` e ``p``: il modulo della sessione con l'uscita che usera'
    (contratto: le sue ``crea_casuale``, ``crea_a`` e ``crea_segnale``; la sua
    ``crea_variante`` qui non si usa). Su ogni moneta del periodo di costruzione
    ``gruppo.py`` calcola da se' gli ingressi che guardano avanti: la barra i e'
    un segnale se la chiusura della barra i + 1 e' sopra (``direzione`` «long»)
    o sotto («short») la chiusura della barra i, fuori dalle barre vietate delle
    varianti (segnale non valido, mesi sotto la liquidita'). E' l'unico calcolo in
    cui una strategia del gruppo usa barre non chiuse, e quelle barre le legge
    solo ``gruppo.py``. Gli ingressi vanno a ``crea_casuale(ingressi)``, lo stesso
    percorso della (b) e delle sfasate, e si giudicano con l'esame di gruppo
    (``esame_di_gruppo`` intero, con (a), (b) e pavimento), senza ritardo e con il
    ritardo di una barra (id ``<id>`` e ``<id>-ritardo1``).

    Passa se senza ritardo il candidato batte nettamente la (a) e la (b) di
    gruppo e se con il ritardo il ``t`` contro la (b) ricalcolata scende sotto la
    meta' di quello senza ritardo. Se non passa e' un errore degli strumenti
    (STOP). ValueError se i trade non hanno tutti la ``direzione`` data (il
    modulo non e' quello giusto).
    """
    _controlla_argomenti_in_campagna("controllo_positivo", monete, caricatore, radice)
    if direzione not in ("long", "short"):
        raise ValueError(f"direzione deve essere long o short, non {direzione!r}")
    sorgente = {"tipo": "guarda_avanti", "direzione": direzione}
    esami = {}
    for nome, ritardo, identificativo in (("senza_ritardo", 0, id), ("con_ritardo", 1, f"{id}-ritardo1")):
        esami[nome] = _esame(modulo, p, timeframe, "costruzione", identificativo, moltiplicatore_costi=1.0,
                             ritardo_barre=ritardo, riempimento_intrabarra=None, con_baseline_a=True,
                             processi=processi, radice=radice, cartella_campagna=cartella_campagna, monete=monete,
                             caricatore=caricatore, sorgente_richiesta=lambda posizioni: dict(sorgente),
                             chi="controllo_positivo")
        contrari = sum(v["short" if direzione == "long" else "long"] for v in esami[nome]["per_moneta"].values())
        if contrari:
            raise ValueError(f"controllo positivo {direzione}: {contrari} trade nell'altra direzione: il modulo non "
                             "ha la direzione dichiarata")
    senza, con = esami["senza_ritardo"], esami["con_ritardo"]
    batte = bool(senza["valutabile"] and senza["baseline_a"]["netta"] and senza["baseline_b"]["netta"])
    crolla = bool(math.isfinite(senza["t"]) and con["t"] < senza["t"] / 2)
    return _in_json({
        "direzione": direzione,
        "timeframe": timeframe,
        "passa": batte and crolla,
        "condizioni": {"batte_nettamente_a_e_b_senza_ritardo": batte,
                       "t_con_ritardo_sotto_meta_di_quello_senza": crolla},
        "t_senza_ritardo": senza["t"],
        "t_con_ritardo": con["t"],
        "esami": esami,
    })


# ---------------------------------------------------------------------------
# asticella_di_gruppo (regole.md, sezione 7, punti 4-5)
# ---------------------------------------------------------------------------


def asticella_di_gruppo(risultati_validazione: Sequence[Mapping]) -> Dict[str, object]:
    """L'asticella del gruppo: Benjamini-Hochberg al 10% sui candidati del gruppo (regole.md, sezione 7, punti 4-5).

    ``risultati_validazione``: i dizionari di ``esame_di_gruppo`` in validazione di
    TUTTI i candidati di gruppo che hanno girato in validazione (m = quanti sono;
    la m del gruppo non si unisce a quella delle monete singole). Il p-value di
    ognuno e' ``validazione.p_value_asticella`` (il ``p_value`` di
    ``contro_baseline`` contro la (b) di validazione con il pavimento delle
    sfasate; 1 per chi ha meno di 300 trade o e' non valutabile). Va al vault chi
    ha almeno 300 trade sommati, passa l'asticella e ha l'R medio dopo i costi
    positivo (sezione 7, punto 4). Esito provvisorio: lo conferma il coordinamento.
    """
    regole = regole_del_gruppo()
    voci = []
    for risultato in risultati_validazione:
        if risultato.get("periodo") != "validazione" or "validazione" not in risultato:
            raise ValueError("asticella_di_gruppo vuole i risultati di esame_di_gruppo in validazione")
        voci.append(risultato)
    p_values = [float(v["validazione"]["p_value_asticella"]) for v in voci]
    passano = statistica.benjamini_hochberg(p_values, regole["asticella_q"])
    candidati = []
    for voce, p_value, passa in zip(voci, p_values, passano):
        val = voce["validazione"]
        candidati.append({"id": voce.get("id"), "p_value_asticella": p_value, "passa_asticella": bool(passa),
                          "trade_minimi_superati": bool(val["trade_minimi_superati"]),
                          "r_medio_positivo": bool(val["r_medio_positivo"]),
                          "va_al_vault": bool(passa and val["trade_minimi_superati"] and val["r_medio_positivo"])})
    return {"m": len(voci), "q": regole["asticella_q"], "candidati": candidati, "provvisorio": True}


# ---------------------------------------------------------------------------
# esame_vault (regole.md, sezione 9, e sezione 10, punto 2), per il coordinamento
# ---------------------------------------------------------------------------


def esame_vault(
    modulo: Union[str, Path],
    p: Mapping,
    timeframe: str,
    *,
    processi: int = 4,
    radice: Union[str, Path] = dati.RADICE_DEFAULT,
    monete: Optional[Union[Sequence[str], Mapping[str, int]]] = None,
    caricatore=None,
    file_trade: Optional[Union[str, Path]] = None,
) -> Dict[str, object]:
    """Il candidato di gruppo sul vault, una volta sola (regole.md, sezione 9; sezione 10, punto 2; Passo 5 del protocollo). Solo per il coordinamento.

    Gira solo a vault aperto: lo garantisce il caricatore (``dati`` alza
    ``VaultChiuso`` per dati oltre il 2023-12-31 senza ``vault/APERTURA.md``).
    ``monete``: di norma l'elenco del gruppo; per il trasferimento le monete fuori
    dal gruppo, {simbolo: j} con j la posizione nel loro elenco in ordine dei
    caratteri, e un ``caricatore`` che da' la fascia di slippage giusta. Ogni
    moneta gira sulla serie dal primo giorno dei suoi dati (``scheda``) al
    2026-09-30 o al suo ultimo giorno con candele, con 1.000 USDT, il filtro di
    liquidita' della sezione 2, punto 7 (sui file giornalieri del vault, con le
    stesse barre vietate alla (b) e alle sfasate); contano i trade ENTRATI dal
    2024-01-01 (indicatori caldi, come in validazione). Una moneta che smette di
    avere candele resta nella somma fino al suo ultimo giorno (sezione 10, punto 1.2).

    * Le sfasate del vault (sezione 9, punto 3): gli ingressi del candidato nel
      vault spostati tutti dello stesso intervallo, in cerchio sulla finestra del
      vault (``griglia_sfasamenti`` con S = ``gruppo.fittizie_vault``, a 1d meno);
      la finestra di una moneta finisce con il suo ultimo giorno con candele.
    * Il ``criterio_vault`` sui trade sommati (sezione 9, punto 2) con le metriche
      di ``motore.metriche_di_gruppo``: profit factor almeno 1,10, almeno 300 trade,
      risultato totale positivo, R medio sopra il 90° percentile degli R medi
      delle sfasate con almeno un trade.
    * Il tasso del caso (sezione 9, punto 4): la quota delle sfasate che passano
      le stesse condizioni (``criterio_vault`` con ``trade_minimi`` = 0 sulle loro
      metriche, piu' i 300 trade del candidato, che valgono per tutte); quelle
      senza trade restano nel denominatore e non passano.
    * Solo da riportare (sezione 9, punto 5): la (b) di gruppo del vault (semi
      1000·j + s, 200 per moneta) e il confronto con il pavimento delle sfasate;
      la distribuzione di n'(s) / N e le sfasate senza trade; la quota della
      moneta piu' presente; la tabella per moneta; le monete che smettono di
      avere candele.

    Senza file di avanzamento: i trade delle 1.000 sfasate sarebbero troppi per
    un file da conservare. ``file_trade``, se dato, riceve i trade sommati. Con un
    marcatore di campagna alza ``dati.VietatoInCampagna``: il vault e' del
    coordinamento.
    """
    if _in_campagna():
        raise dati.VietatoInCampagna("esame_vault: e' del coordinamento, mai di una sessione di campagna "
                                     "(regole.md, sezione 9)")
    processi = _controlla_processi(processi)
    regole = regole_del_gruppo()
    opzioni = _opzioni_del_motore(regole, 1.0, 0, None)
    caricatore = CaricatoreDisco(str(radice)) if caricatore is None else caricatore
    base = _compito_base(modulo, p, timeframe, regole, opzioni, caricatore)
    posizioni, _ufficiali = _monete_con_posizione(monete)
    ms = base["ms_per_barra"]
    primi = {s: caricatore.scheda(s)["primo_mese"] for s in posizioni}
    inizio_vault_ts = dati.ms_da_data(dati.INIZIO_VAULT)
    fine_vault_ts = dati.ms_da_data(dati.FINE_VAULT + timedelta(days=1)) - 1
    in_ordine = sorted(posizioni, key=lambda s: (primi[s], s))

    def compito_moneta(simbolo: str, tipo: str, **altro) -> Dict[str, object]:
        return dict(base, tipo=tipo, simbolo=simbolo, j=posizioni[simbolo], periodo="vault",
                    sorgente={"tipo": "modulo"}, inizio=primi[simbolo].isoformat(),
                    fine=dati.FINE_VAULT.isoformat(), inizio_conteggio_ts=inizio_vault_ts, con_a=False, **altro)

    pezzi1: Dict[str, Dict[str, object]] = {}
    for risultato in _esegui_compiti([compito_moneta(s, "fase1") for s in in_ordine], processi):
        pezzi1[risultato["simbolo"]] = json.loads(json.dumps(_in_json(risultato["dati"])))
    pezzi1 = {s: pezzi1[s] for s in sorted(pezzi1)}
    ordinati, trade_in_ordine = _trade_sommati(pezzi1)
    n_j = {s: len(pezzi1[s]["trade"]["righe"]) for s in pezzi1}
    con_trade = [s for s in sorted(n_j) if n_j[s] > 0]
    totale = len(ordinati)
    nel_periodo = sorted(s for s in pezzi1 if pezzi1[s]["barre_nel_periodo"] > 0)
    metriche = _metriche(pezzi1, con_trade, len(nel_periodo), regole)
    if file_trade is not None:
        _scrivi_trade(Path(file_trade), trade_in_ordine)

    # l'ultimo giorno con candele di ogni moneta (sezione 10, punto 1.2)
    fine_giorno = {s: int(pezzi1[s]["ultima_barra_ts"]) // GIORNO_MS * GIORNO_MS + GIORNO_MS - 1 for s in nel_periodo}
    smettono = {s: (date(1970, 1, 1) + timedelta(days=fine_giorno[s] // GIORNO_MS)).isoformat()
                for s in nel_periodo if fine_giorno[s] < fine_vault_ts}
    trade_minimi = regole["trade_minimi"]["vault"]
    pf_minimo = regole["pf_minimo_vault"]
    risultato: Dict[str, object] = {
        "periodo": "vault",
        "timeframe": timeframe,
        "parametri": json.loads(base["p_json"]),
        "impronte": {"variante": base["impronta_variante"], "strumenti": base["impronte"],
                     "parametri": _sha256_testo(base["p_json"])},
        "metriche": dict(metriche, trade=metriche["n_trade"]),
        "monete_nel_gruppo": len(posizioni),
        "monete_nel_periodo": len(nel_periodo),
        "monete_con_trade": len(con_trade),
        "monete_che_smettono": smettono,
        "quota_moneta_piu_presente": None,
        "moneta_piu_presente": None,
        "btc": _btc_dai_pezzi(pezzi1),
        "per_moneta": {s: {"j": posizioni[s], "trade": n_j[s],
                           "r_medio": metriche["per_moneta"][s]["r_medio"] if n_j[s] else None,
                           "pnl": math.fsum(float(t["pnl"]) for t in _trade_della_moneta(pezzi1[s])),
                           "barre_nel_periodo": pezzi1[s]["barre_nel_periodo"],
                           "mesi_sotto_liquidita": len(pezzi1[s]["mesi_sotto_liquidita"]),
                           "barre_vietate": pezzi1[s]["vietate"],
                           "violazioni_liquidazione": sum(1 for t in _trade_della_moneta(pezzi1[s])
                                                          if t["violazione_liquidazione"])}
                       for s in sorted(pezzi1)},
    }
    if con_trade:
        piu = min(con_trade, key=lambda s: (-n_j[s], s))
        risultato["moneta_piu_presente"], risultato["quota_moneta_piu_presente"] = piu, n_j[piu] / totale
    if totale == 0:
        criterio = statistica.criterio_vault(metriche, math.inf, trade_minimi=trade_minimi, pf_minimo=pf_minimo)
        risultato.update({"criterio": criterio, "passa": False, "tasso_del_caso": None, "sfasate": None,
                          "baseline_b": None, "percentile_90_sfasate": None})
        return _in_json(risultato)

    griglia = _griglia("vault", con_trade, pezzi1, None, ms, regole, regole["fittizie_vault"])
    compiti = [compito_moneta(s, "sfasate", ts_segnali=pezzi1[s]["ts_segnali"],
                              finestra_unione=griglia["finestra_unione"],
                              finestra_moneta=[inizio_vault_ts, min(fine_giorno[s], fine_vault_ts)],
                              sfasamenti=griglia["sfasamenti"], impronta_vietate=pezzi1[s]["vietate"]["impronta"],
                              trade_completi=True)
               for s in in_ordine if s in con_trade]
    pezzi2: Dict[str, Dict[str, object]] = {}
    for r_pezzo in _esegui_compiti(compiti, processi):
        pezzi2[r_pezzo["simbolo"]] = r_pezzo["dati"]
    numero = griglia["numero"]
    # una s alla volta: i TradeSfasato di una sfasata esistono solo mentre se ne calcolano le metriche
    metriche_s = []
    riassunti: Dict[str, List[List[object]]] = {s: [] for s in sorted(pezzi2)}
    per_s = {s: _trade_compatti_per_s(pezzi2[s]["trade_compatti"]) for s in sorted(pezzi2)}
    for _ in range(numero):
        trade_s = {s: next(per_s[s]) for s in sorted(pezzi2)}
        for s, trade in trade_s.items():
            riassunti[s].extend(statistica.riassunto_sfasate([[t.r for t in trade]]))
        metriche_s.append(motore.metriche_di_gruppo({s: v for s, v in trade_s.items() if v}, len(nel_periodo),
                                                    regole["capitale_per_moneta"], regole["trade_migliori_tolti"]))
    # il criterio di ogni sfasata sulle sue metriche (sezione 9, punto 4); il pavimento con la lettura comune
    # di M'(s) (statistica.medie_sfasate, sezione 5, punto 5)
    m_sfasate, n_sfasate = statistica.medie_sfasate(riassunti, numero)
    con_trade_s = [m["r_medio"] for m in metriche_s if m["n_trade"] > 0]
    percentile_90 = (statistica.percentile(con_trade_s, regole["percentile_caso_vault"]) if con_trade_s
                     else math.inf)
    criterio = statistica.criterio_vault(metriche, percentile_90, trade_minimi=trade_minimi, pf_minimo=pf_minimo)
    trade_ok = totale >= trade_minimi
    esiti = []
    dettaglio = []
    for d, met in zip(griglia["sfasamenti"], metriche_s):
        passa = bool(met["n_trade"] > 0 and trade_ok and statistica.criterio_vault(
            met, percentile_90, trade_minimi=0, pf_minimo=pf_minimo)["esito"])
        esiti.append(passa)
        dettaglio.append({"d": d, "n_trade": met["n_trade"], "r_medio": met["r_medio"] if met["n_trade"] else None,
                          "profit_factor": met["profit_factor"], "rendimento_totale": met["rendimento_totale"],
                          "passa": passa})
    pavimento = statistica.pavimento_sfasamento(m_sfasate, n_sfasate, totale)
    risultato.update({
        "criterio": criterio,
        "passa": bool(criterio["esito"]),
        "percentile_90_sfasate": percentile_90,
        "tasso_del_caso": statistica.tasso_del_caso(esiti),
        "sfasate": dict({k: v for k, v in pavimento.items() if k not in ("pavimento", "valutabile", "media_r_sfasate")},
                        **{"passate": sum(esiti), "L": griglia["barre_finestra"], "margine": griglia["margine"],
                           "sfasamenti_richiesti": griglia["sfasamenti_richiesti"],
                           "tutti_gli_interi": griglia["tutti_gli_interi"],
                           "saltati_totali": {motivo: sum(pezzi2[s]["saltati_totali"][motivo] for s in sorted(pezzi2))
                                              for motivo in SALTI},
                           "segnali_coincidenti": sum(pezzi2[s]["segnali_coincidenti"] for s in sorted(pezzi2)),
                           "dettaglio": dettaglio}),
    })
    # (b) di gruppo del vault e confronto, solo da riportare (sezione 9, punto 5)
    r = [t.r for t in ordinati]
    blocco = statistica.lunghezza_blocco([t.ts_entrata for t in ordinati], [t.ts_uscita for t in ordinati])
    base_b = statistica.baseline_casuale_di_gruppo(
        {s: (pezzi1[s]["b"]["r_medio_per_seme"] if pezzi1[s]["b"]["entrano"] else None) for s in con_trade},
        {s: n_j[s] for s in con_trade})
    conf_b = _confronto(r, blocco, base_b, pavimento, regole)
    risultato["baseline_b"] = dict({k: v for k, v in base_b.items() if k != "valori"}, **conf_b,
                                   pavimento_sfasate=pavimento["pavimento"], blocco=blocco)
    return _in_json(risultato)
