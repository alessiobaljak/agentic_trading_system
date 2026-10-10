"""Statistica del protocollo di ricerca (sezione 8 di research/PROTOCOLLO.md).

Modulo INDIPENDENTE dal bot: non importa nulla da bot/, backtesting/ o
scripts/. Usa solo la libreria standard e numpy. Tutte le funzioni sono pure:
ricevono numeri, restituiscono numeri, non toccano file ne' stato globale. Ogni
funzione casuale prende un seme esplicito, cosi' lo stesso seme rida' lo
stesso risultato e ogni numero dei report si puo' ricostruire.

Cosa c'e' qui, e perche'
------------------------
* ``bootstrap_blocchi``: il mattone di tutto. I trade di una strategia sono
  ordinati nel tempo e NON sono indipendenti (trade sovrapposti, stesso giorno,
  stesso regime di mercato). Ricampionare un trade alla volta fingerebbe che lo
  siano e darebbe errori standard troppo piccoli. Il bootstrap a blocchi
  ricampiona pezzi contigui di serie, lunghi almeno quanto la dipendenza
  (sezione 8: almeno la durata massima di una posizione, e comunque almeno un
  giorno), cosi' la dipendenza dentro il blocco si conserva.
* ``lunghezza_blocco``: il blocco del bootstrap in numero di trade, dalla
  regola in tempo della sezione 8 (dalla 4.4, uguale per tutte le campagne).
* ``batte_nettamente``: la regola «nettamente» del protocollo dalla versione
  4.4: la media del candidato supera UN numero di baseline oltre la soglia di
  Student in errori standard della differenza, con l'errore del bootstrap
  corretto per il blocco e almeno ``MINIMO_BLOCCHI`` blocchi (sezione 8).
  ``baseline_casuale`` e ``baseline_da_trade`` preparano quel numero per le
  baseline (b) e (a); ``percentile_del_candidato`` da' l'indizio del log.
* ``p_value_vs_baseline``: il p-value che entra nell'asticella dalla 4.4.
* ``differenza_nettamente`` e ``p_value_bootstrap_vs_caso``: le versioni fino
  alla 4.3, a due serie. Restano per rileggere le campagne archiviate; NON sono
  la regola del protocollo dalla 4.4 (confrontare il candidato con UNA sola
  corsa casuale somma il rumore di quella corsa, che la baseline non ha).
* ``p_value_unilaterale``: il mattone dei p-value.
* ``benjamini_hochberg``: l'asticella, con la procedura esatta della sezione 8.
* le metriche in R (profit factor, win rate, drawdown, rendimento per anno),
  ``entrate_casuali`` per costruire la baseline (b) e il tasso del caso,
  ``tasso_del_caso`` e ``criterio_vault``.
* la campagna di gruppo (``research/campagne/GRUPPO/regole.md``, sezioni 5, 6 e
  13), in fondo al modulo: ``TradeDiGruppo`` e ``ordina_trade_di_gruppo`` (i
  trade sommati di tutte le monete in un ordine fisso),
  ``baseline_da_trade_di_gruppo`` e ``baseline_casuale_di_gruppo`` (la (a) e la
  (b) di gruppo, combinate moneta per moneta con i pesi dei trade),
  ``griglia_sfasamenti`` e ``pavimento_sfasamento`` (il pavimento delle strategie
  sfasate, che va a ``contro_baseline`` come ``pavimento_minimo``),
  ``effetto_grappolo`` ed ``estremi_di_gruppo``. Con una moneta sola e
  ``pavimento_minimo`` 0 danno i numeri delle campagne singole.

Convenzioni
-----------
* Le serie sono ``Sequence[float]`` nell'ORDINE DEL TEMPO: il bootstrap a
  blocchi ha senso solo cosi'. Chi chiama ordina i trade per data di uscita.
* I timestamp sono in millisecondi, UTC.
* ``lunghezza_blocco`` e' in numero di elementi (trade), non in tempo: chi chiama
  la ricava dalla durata delle posizioni (es. quanti trade cadono nella
  finestra di dipendenza). Deve essere MINORE della lunghezza della serie:
  con un blocco lungo quanto la serie (o di piu') ogni ricampionamento e' una
  rotazione della serie, la media non cambia mai e l'errore standard viene 0
  per costruzione, non perche' la stima sia precisa. Quel caso e' degenere:
  ``bootstrap_blocchi`` lo rifiuta con ValueError, e le funzioni composte
  (``differenza_nettamente``, ``p_value_bootstrap_vs_caso``) restituiscono il
  risultato piu' prudente e lo segnalano (vedi le loro docstring). Anche con
  pochi blocchi (serie poco piu' lunga del blocco) l'errore e' sottostimato:
  ``n_blocchi`` nel risultato serve a dichiararlo nel report.
"""
from __future__ import annotations

import math
import operator
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Callable, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

import numpy as np

# ---------------------------------------------------------------------------
# Bootstrap a blocchi
# ---------------------------------------------------------------------------


def _come_array(valori: Sequence[float], nome: str) -> np.ndarray:
    """Converte in array float 1-D e rifiuta le serie vuote o con NaN.

    Una serie vuota non ha una media; un NaN la contaminerebbe in silenzio.
    Meglio un errore esplicito che un numero sbagliato in un report.
    """
    arr = np.asarray(list(valori), dtype=float)
    if arr.ndim != 1:
        raise ValueError(f"{nome}: serve una sequenza 1-D, non shape {arr.shape}")
    if arr.size == 0:
        raise ValueError(f"{nome}: la serie e' vuota")
    if np.isnan(arr).any():
        raise ValueError(f"{nome}: la serie contiene NaN")
    return arr


def _indici_blocchi_circolari(n_valori: int, lunghezza_blocco: int, n: int, rng: np.random.Generator) -> np.ndarray:
    """Matrice (n, n_valori) di indici: ogni riga e' un ricampionamento a blocchi.

    Moving block bootstrap circolare: ogni blocco parte da un indice uniforme in
    [0, n_valori) e prende i ``lunghezza_blocco`` elementi successivi, tornando
    all'inizio quando supera la fine. La versione circolare evita che i primi
    e gli ultimi elementi della serie entrino nei blocchi meno spesso degli
    altri (succederebbe con blocchi che non possono "sporgere").

    Si concatenano ceil(n_valori / lunghezza_blocco) blocchi e si tagliano i
    primi n_valori elementi, cosi' ogni campione ha la lunghezza dell'originale.
    """
    n_blocchi = math.ceil(n_valori / lunghezza_blocco)
    partenze = rng.integers(0, n_valori, size=(n, n_blocchi))
    spostamenti = np.arange(lunghezza_blocco)
    indici = (partenze[:, :, None] + spostamenti[None, None, :]) % n_valori
    return indici.reshape(n, n_blocchi * lunghezza_blocco)[:, :n_valori]


def bootstrap_degenere(n_valori: int, lunghezza_blocco: int) -> bool:
    """True se il bootstrap a blocchi NON puo' stimare nulla: blocco >= serie.

    Con un solo blocco circolare ogni ricampionamento e' una rotazione della
    serie: la media e' sempre la stessa e l'errore standard esce 0 per
    costruzione. Un errore 0 a valle vorrebbe dire «qualsiasi differenza e'
    netta» e «p-value al minimo»: il risultato piu' favorevole proprio quando
    non si sa nulla. Per questo il caso va riconosciuto PRIMA di ricampionare.
    Chi chiama puo' usare questa funzione per deciderlo in anticipo (es. per
    dichiarare nel report che un candidato con pochi trade e posizioni lunghe
    non e' valutabile con questo metodo).
    """
    return int(lunghezza_blocco) >= int(n_valori)


def bootstrap_blocchi(
    valori: Sequence[float],
    lunghezza_blocco: int,
    n: int = 2000,
    seme: int = 0,
    statistica: Callable[..., float] = np.mean,
) -> Dict[str, object]:
    """Bootstrap a blocchi circolari (moving block bootstrap) di una statistica.

    Parametri
    ---------
    valori : la serie ordinata nel tempo (es. gli R dei trade per data di uscita).
    lunghezza_blocco : lunghezza del blocco in elementi, almeno 1 e MINORE della
        lunghezza della serie. Blocco >= serie alza ValueError (caso degenere:
        vedi ``bootstrap_degenere``); non viene ridotto in silenzio, perche' una
        riduzione silenziosa darebbe errore 0 e il risultato piu' favorevole
        senza che chi chiama se ne accorga.
    n : numero di ricampionamenti.
    seme : seme del generatore; stesso seme, stesso risultato.
    statistica : funzione da array a numero (default la media). Viene applicata
        riga per riga ai campioni.

    Ritorna un dizionario con:
    * ``media``: la statistica calcolata sulla serie originale (NON la media
      dei campioni: e' il valore osservato, quello che si riporta);
    * ``errore_standard``: deviazione standard (ddof=1) della statistica sui
      campioni; 0 se la serie e' costante o se n < 2;
    * ``intervallo_95``: tupla (2,5° percentile, 97,5° percentile) dei campioni;
    * ``campioni``: l'array dei valori della statistica sui campioni, cosi' chi
      chiama puo' calcolare altro (p-value, differenze) senza ricampionare;
    * ``n_blocchi``: quanti blocchi compongono ogni campione
      (ceil(serie / blocco)). Con pochi blocchi (2-3) l'errore standard e'
      sottostimato, perche' i blocchi circolari di una serie corta si
      somigliano quasi tutti: il numero va nel report, cosi' chi legge sa
      quanto fidarsi.
    """
    arr = _come_array(valori, "valori")
    if n < 1:
        raise ValueError("n deve essere almeno 1")
    lunghezza = int(lunghezza_blocco)
    if lunghezza < 1:
        raise ValueError("lunghezza_blocco deve essere almeno 1")
    if bootstrap_degenere(arr.size, lunghezza):
        raise ValueError(
            f"bootstrap degenere: blocco di {lunghezza} elementi su una serie di {arr.size}; "
            "con un solo blocco ogni ricampionamento e' una rotazione della serie e l'errore "
            "standard esce 0 per costruzione. Servono piu' trade o un blocco piu' corto, e va dichiarato."
        )
    rng = np.random.default_rng(seme)
    indici = _indici_blocchi_circolari(arr.size, lunghezza, n, rng)
    matrice = arr[indici]
    campioni = np.apply_along_axis(statistica, 1, matrice).astype(float)
    errore = float(np.std(campioni, ddof=1)) if campioni.size > 1 else 0.0
    basso, alto = np.percentile(campioni, [2.5, 97.5], method="linear")
    return {
        "media": float(statistica(arr)),
        "errore_standard": errore,
        "intervallo_95": (float(basso), float(alto)),
        "campioni": campioni,
        "n_blocchi": math.ceil(arr.size / lunghezza),
    }


def differenza_nettamente(
    a: Sequence[float],
    b: Sequence[float],
    lunghezza_blocco: int,
    n: int = 2000,
    seme: int = 0,
) -> Dict[str, object]:
    """La regola «nettamente» FINO ALLA 4.3: differenza fra due serie oltre 2 errori standard.

    Dalla versione 4.4 la regola del protocollo e' ``batte_nettamente``: questa
    funzione resta solo per rileggere le campagne archiviate. Usata contro UNA
    corsa casuale (per esempio la mediana delle simulazioni) somma l'errore
    standard di quella corsa, che e' grande quanto quello del candidato, mentre
    la baseline (b) e' la media di centinaia di corse e quasi non ha errore: il
    margine viene circa 1,4 volte piu' largo del dovuto.

    ``a`` e' il candidato, ``b`` la baseline (stesso effetto senza condizione,
    entrata casuale, buy and hold a trade...). Le due serie si ricampionano
    INDIPENDENTEMENTE, ciascuna col proprio bootstrap a blocchi (semi diversi:
    ``seme`` per a e ``seme + 1`` per b, cosi' non usano gli stessi blocchi): le
    due serie possono avere lunghezze diverse e non c'e' un accoppiamento trade
    per trade. L'errore standard della differenza e' allora la radice della
    somma dei quadrati dei due errori standard.

    Ritorna: ``differenza`` (media a - media b), ``errore_standard``,
    ``margine`` (2 errori standard), ``netta`` (|differenza| > margine),
    ``segno`` (+1, -1 o 0) e ``degenere`` (bool). Con due serie uguali la
    differenza e' 0 e ``netta`` e' False qualunque sia l'errore.

    Caso degenere (``degenere`` True): se il blocco e' lungo almeno quanto una
    delle due serie il bootstrap non stima nulla (vedi ``bootstrap_degenere``).
    Qui NON si alza un errore, perche' «nettamente» e' un giudizio e il
    giudizio prudente esiste: la differenza NON e' netta. Si restituisce
    ``errore_standard`` e ``margine`` infiniti (nessuna informazione sulla
    precisione), ``netta`` False e ``degenere`` True, cosi' il report puo'
    scrivere «non valutabile: pochi trade rispetto alla durata delle
    posizioni» invece di «non netta». La ``differenza`` osservata si calcola
    comunque, perche' e' un fatto, non una stima.
    """
    arr_a = _come_array(a, "a")
    arr_b = _come_array(b, "b")
    differenza = float(np.mean(arr_a)) - float(np.mean(arr_b))
    if bootstrap_degenere(arr_a.size, lunghezza_blocco) or bootstrap_degenere(arr_b.size, lunghezza_blocco):
        return {
            "differenza": differenza,
            "errore_standard": math.inf,
            "margine": math.inf,
            "netta": False,
            "segno": int(np.sign(differenza)),
            "degenere": True,
        }
    boot_a = bootstrap_blocchi(arr_a, lunghezza_blocco, n=n, seme=seme)
    boot_b = bootstrap_blocchi(arr_b, lunghezza_blocco, n=n, seme=seme + 1)
    errore = math.sqrt(float(boot_a["errore_standard"]) ** 2 + float(boot_b["errore_standard"]) ** 2)
    margine = 2.0 * errore
    return {
        "differenza": differenza,
        "errore_standard": errore,
        "margine": margine,
        "netta": bool(abs(differenza) > margine),
        "segno": int(np.sign(differenza)),
        "degenere": False,
    }


GIORNO_MS = 86_400_000


def lunghezza_blocco(ts_entrata: Sequence[int], ts_uscita: Sequence[int], minimo_ms: int = GIORNO_MS) -> int:
    """Il blocco del bootstrap in NUMERO DI TRADE, dalla regola in tempo della sezione 8.

    La sezione 8 dice: il blocco e' lungo almeno quanto la durata massima di una
    posizione, e comunque almeno un giorno. Il bootstrap pero' lavora su trade,
    non su ore: fino alla 4.3 ogni campagna faceva la conversione a modo suo.
    Dalla 4.4 la conversione e' questa, uguale per tutti:

    * finestra = max(durata massima fra i trade (uscita - entrata), ``minimo_ms``);
    * blocco = il massimo numero di trade che ESCONO dentro una qualunque
      finestra di quella lunghezza, [t, t + finestra), con t l'uscita di un trade;
      almeno 1.

    Cosi' i trade che possono dipendere l'uno dall'altro (sovrapposti, dello
    stesso giorno) finiscono nello stesso blocco. Si calcola sui trade di cui si
    stima l'errore (il candidato, oppure la serie della baseline (a)), nel
    periodo che si sta giudicando. Timestamp in millisecondi.
    """
    entrate = [int(x) for x in ts_entrata]
    uscite = [int(x) for x in ts_uscita]
    if not entrate or len(entrate) != len(uscite):
        raise ValueError("servono entrate e uscite non vuote e della stessa lunghezza")
    if any(u < e for e, u in zip(entrate, uscite)):
        raise ValueError("un trade esce prima di entrare")
    finestra = max(max(u - e for e, u in zip(entrate, uscite)), int(minimo_ms))
    if finestra <= 0:
        raise ValueError("la finestra deve essere positiva")
    ordinate = sorted(uscite)
    blocco = 1
    j = 0
    for i, t in enumerate(ordinate):
        while j < len(ordinate) and ordinate[j] < t + finestra:
            j += 1
        blocco = max(blocco, j - i)
    return blocco


#: sotto questo numero di blocchi interi il bootstrap a blocchi non stima l'errore:
#: il candidato e' «non valutabile» (sezione 8, dalla 4.4; ``parametri.yaml``,
#: ``minimo_blocchi_bootstrap``). Con 2 blocchi l'errore crolla e un candidato
#: senza vantaggio risulterebbe «netto» una volta su tre.
MINIMO_BLOCCHI = 3

#: «oltre 2 errori standard» con una normale e' la coda del 2,275%: la soglia
#: della sezione 8 e' il quantile 0,97725 della t di Student con i gradi di
#: liberta' dei blocchi, che con molti blocchi torna a 2.
LIVELLO_NETTAMENTE = 0.97725


def baseline_casuale(r_medi_simulazioni: Sequence[float]) -> Dict[str, object]:
    """La baseline (b) come UN numero: media degli R medi delle simulazioni casuali.

    Le simulazioni sono strategie a entrate casuali con la stessa uscita, la
    stessa direzione e lo stesso periodo del candidato: le esegue
    ``motore.simula_baseline_casuale`` (sezione 8, dalla 4.4), che restituisce
    gia' questo dizionario. Il numero di simulazioni e' ``simulazioni_baseline_casuale``
    di ``parametri.yaml``.

    Ritorna:
    * ``media``: la media degli R medi, cioe' il numero da battere;
    * ``errore_standard``: l'errore di QUELLA media, deviazione standard degli R
      medi (ddof=1) divisa per la radice del numero di simulazioni. Con 200
      simulazioni e' circa un quattordicesimo dell'errore di una corsa sola;
    * ``errore_minimo_candidato``: la deviazione standard degli R medi delle
      simulazioni, cioe' l'errore della media di una strategia senza vantaggio
      con gli stessi trade: e' il pavimento dell'errore del candidato in
      ``contro_baseline``;
    * ``tipo`` = "b";
    * ``n_simulazioni``, ``percentile_90`` (riferimento: il ``criterio_vault`` usa
      il 90° percentile delle ``simulazioni_caso`` del vault, non queste) e
      ``valori`` (per ``percentile_del_candidato``, che si riporta come indizio,
      mai come prova).

    Servono almeno 2 simulazioni (con una sola l'errore della media non si stima).
    """
    arr = _come_array(r_medi_simulazioni, "r_medi_simulazioni")
    if arr.size < 2:
        raise ValueError("servono almeno 2 simulazioni per stimare l'errore della media")
    return {
        "tipo": "b",
        "media": float(arr.mean()),
        "errore_standard": float(arr.std(ddof=1) / math.sqrt(arr.size)),
        # la dispersione degli R medi delle simulazioni e' l'errore di una
        # strategia SENZA vantaggio con gli stessi trade: l'errore del candidato
        # non si stima mai sotto questo pavimento (vedi ``contro_baseline``)
        "errore_minimo_candidato": float(arr.std(ddof=1)),
        "n_simulazioni": int(arr.size),
        "percentile_90": float(np.percentile(arr, 90, method="linear")),
        "valori": arr,
    }


def percentile_del_candidato(r_medio_candidato: float, r_medi_simulazioni: Sequence[float]) -> float:
    """Quota, per 100, delle simulazioni con R medio STRETTAMENTE minore del candidato.

    E' il «percentile fra le simulazioni casuali» che il log riporta (sezione 6)
    come indizio, mai come prova: le simulazioni hanno trade meno dipendenti fra
    loro di quelli del candidato, e il percentile li conta come indipendenti.
    """
    arr = _come_array(r_medi_simulazioni, "r_medi_simulazioni")
    return float(100.0 * np.count_nonzero(arr < float(r_medio_candidato)) / arr.size)


def _errore_media_corretto(arr: np.ndarray, lunghezza_blocco: int, n: int, seme: int) -> Tuple[float, int]:
    """Errore standard della media dal bootstrap a blocchi, corretto, e i blocchi interi.

    Il bootstrap a blocchi circolari sottostima la varianza della media di un
    fattore circa (1 - b/n) (b blocco, n trade): l'errore si moltiplica per
    radice(n / (n - b)). Senza la correzione, con blocchi lunghi, un candidato
    senza vantaggio risultava «netto» fino a tre volte piu' spesso del dichiarato.
    Chi chiama ha gia' controllato che i blocchi interi siano almeno MINIMO_BLOCCHI.
    """
    b = int(lunghezza_blocco)
    boot = bootstrap_blocchi(arr, b, n=n, seme=seme)
    errore = float(boot["errore_standard"])
    # una serie costante da' in virgola mobile 1e-16, non 0
    if errore <= 1e-12 * max(1.0, abs(float(arr.mean()))):
        errore = 0.0
    return errore * math.sqrt(arr.size / (arr.size - b)), arr.size // b


def baseline_da_trade(r_baseline: Sequence[float], lunghezza_blocco: int, n: int = 2000, seme: int = 0) -> Dict[str, object]:
    """La baseline (a) come UN numero: R medio dei trade della baseline e il suo errore.

    La baseline (a) e' la variante senza la condizione d'ingresso dell'ipotesi
    (sezione 8): una sola serie di trade, ordinata per uscita, non senza rumore.
    Il suo errore si stima come quello del candidato (bootstrap a blocchi con la
    correzione del blocco), con il blocco calcolato da ``lunghezza_blocco`` sui
    SUOI trade.

    Ritorna ``tipo`` = "a", ``media``, ``errore_standard``, ``n_trade``,
    ``n_blocchi``, ``deviazione_standard`` (degli R dei suoi trade: divisa per la
    radice dei trade del candidato da' il pavimento dell'errore del candidato in
    ``contro_baseline``) e ``valutabile``: False se i blocchi interi sono meno di
    MINIMO_BLOCCHI; in quel caso l'errore e' infinito e nessun candidato puo'
    batterla nettamente (il giudizio prudente).
    """
    arr = _come_array(r_baseline, "r_baseline")
    b = int(lunghezza_blocco)
    if b < 1:
        raise ValueError("lunghezza_blocco deve essere almeno 1")
    deviazione = float(arr.std(ddof=1)) if arr.size > 1 else 0.0
    if arr.size // b < MINIMO_BLOCCHI:
        return {"tipo": "a", "media": float(arr.mean()), "errore_standard": math.inf, "n_trade": int(arr.size),
                "n_blocchi": int(arr.size // b), "deviazione_standard": deviazione, "valutabile": False}
    errore, k = _errore_media_corretto(arr, b, n, seme)
    return {"tipo": "a", "media": float(arr.mean()), "errore_standard": errore, "n_trade": int(arr.size),
            "n_blocchi": int(k), "deviazione_standard": deviazione, "valutabile": True}


def _esito_non_valutabile(differenza: float, k: int) -> Dict[str, object]:
    """Il risultato di un confronto NON VALUTABILE (sezione 8): non netto, t = -inf, p-value 1."""
    return {
        "differenza": differenza, "errore_standard": math.inf, "margine": math.inf, "soglia": math.inf,
        "gradi_liberta": max(0, k - 1), "netta": False, "t": -math.inf, "p_value": 1.0,
        "errore_candidato": math.inf, "n_blocchi": int(k), "valutabile": False,
    }


def _confronto(r_candidato, lunghezza_blocco, baseline_media, baseline_errore_standard, n, seme,
               errore_minimo_candidato: float = 0.0) -> Dict[str, object]:
    """Il calcolo comune di ``batte_nettamente``, ``p_value_vs_baseline`` e ``contro_baseline``."""
    return _confronto_dettagliato(r_candidato, lunghezza_blocco, baseline_media, baseline_errore_standard, n, seme,
                                  errore_minimo_candidato)[0]


def _confronto_dettagliato(r_candidato, lunghezza_blocco, baseline_media, baseline_errore_standard, n, seme,
                           errore_minimo_candidato: float = 0.0) -> Tuple[Dict[str, object], object]:
    """``_confronto`` piu' l'errore del candidato PRIMA del pavimento (None se non calcolato).

    Il dizionario e' quello di sempre (``batte_nettamente`` lo restituisce cosi'
    com'e'). Il secondo valore serve solo a ``contro_baseline``, per l'effetto
    grappolo della campagna di gruppo (``campagne/GRUPPO/regole.md``, sezione 5,
    punto 9): l'errore del bootstrap gia' corretto per il blocco, prima di
    qualunque pavimento. None quando il bootstrap non e' stato fatto (meno di
    ``MINIMO_BLOCCHI`` blocchi interi, o baseline con errore infinito).
    """
    from scipy.stats import t as student  # scipy e' fra le dipendenze del repo (requirements.txt)

    arr = _come_array(r_candidato, "r_candidato")
    base = float(baseline_media)
    errore_base = float(baseline_errore_standard)
    if math.isnan(base) or math.isinf(base) or math.isnan(errore_base) or errore_base < 0:
        raise ValueError("baseline_media deve essere un numero finito e baseline_errore_standard non negativo")
    pavimento = float(errore_minimo_candidato)
    if not math.isfinite(pavimento) or pavimento < 0:
        raise ValueError("errore_minimo_candidato deve essere un numero finito non negativo")
    if not np.isfinite(arr).all():
        raise ValueError("r_candidato contiene valori non finiti")
    b = int(lunghezza_blocco)
    if b < 1:
        raise ValueError("lunghezza_blocco deve essere almeno 1")
    differenza = float(arr.mean()) - base
    k = arr.size // b
    non_valutabile = _esito_non_valutabile(differenza, k)
    if k < MINIMO_BLOCCHI or math.isinf(errore_base):
        return non_valutabile, None
    errore_c, _ = _errore_media_corretto(arr, b, n, seme)
    errore_senza_pavimento = errore_c
    # Il pavimento: con R asimmetrici (molti piccoli guadagni, rare grandi
    # perdite) i ricampionamenti con meno perdite hanno insieme media alta ed
    # errore piccolo, e una serie di soli vincenti ha errore 0. L'errore del
    # candidato non scende mai sotto quello di una strategia senza vantaggio con
    # gli stessi trade (revisione del 7 ott 2026).
    errore_c = max(errore_c, pavimento)
    errore = math.sqrt(errore_c ** 2 + errore_base ** 2)
    if errore_c == 0.0:
        # nessun rumore stimabile nel candidato (serie costante, nessun
        # pavimento): un errore 0 non e' una precisione infinita, e' una serie
        # che non varia.
        return dict(non_valutabile, errore_candidato=0.0), errore_senza_pavimento
    gradi = k - 1
    soglia = float(student.ppf(LIVELLO_NETTAMENTE, gradi))
    t = differenza / errore
    return {
        "differenza": differenza,
        "errore_standard": errore,
        "margine": soglia * errore,
        "soglia": soglia,
        "gradi_liberta": int(gradi),
        "netta": bool(t > soglia),
        "t": float(t),
        "p_value": float(student.sf(t, gradi)),
        "errore_candidato": errore_c,
        "n_blocchi": int(k),
        "valutabile": True,
    }, errore_senza_pavimento


def batte_nettamente(
    r_candidato: Sequence[float],
    lunghezza_blocco: int,
    baseline_media: float,
    baseline_errore_standard: float,
    n: int = 2000,
    seme: int = 0,
    errore_minimo_candidato: float = 0.0,
) -> Dict[str, object]:
    """La regola «nettamente» della sezione 8 dalla versione 4.4. Una sola lettura.

    Nelle campagne si usa attraverso ``contro_baseline``, che prende il numero
    della baseline, il suo errore e il pavimento dell'errore del candidato dal
    dizionario di ``baseline_casuale`` o ``baseline_da_trade``: cosi' nessuno li
    passa a mano sbagliando.

    Il candidato (i suoi R, ORDINATI PER USCITA) batte nettamente una baseline se
    la differenza fra il suo R medio e il NUMERO della baseline supera la soglia
    in errori standard della differenza:

        differenza = media(r_candidato) - baseline_media
        errore     = radice(e_c^2 + baseline_errore_standard^2)
        t          = differenza / errore
        netta      = t > soglia        (solo verso l'alto)

    * ``e_c`` e' l'errore della media del candidato dal bootstrap a blocchi
      (``lunghezza_blocco`` trade per blocco, da ``lunghezza_blocco()``),
      moltiplicato per radice(n / (n - b)): il bootstrap a blocchi sottostima la
      varianza della media di circa (1 - b/n);
    * ``soglia`` e' il quantile 0,97725 della t di Student con k - 1 gradi di
      liberta', dove k = n // b e' il numero di blocchi interi: con molti blocchi
      vale circa 2 («oltre 2 errori standard», la coda del 2,275%), con pochi e'
      piu' alta perche' l'errore stesso e' stimato male;
    * sotto ``MINIMO_BLOCCHI`` blocchi interi, o con l'errore della baseline
      infinito, o senza alcun rumore stimabile, il candidato e' NON VALUTABILE:
      ``valutabile`` False, ``netta`` False, ``t`` = -inf (in fondo all'ordine dei
      ritocchi, regola 6), ``p_value`` 1.

    ``baseline_errore_standard`` e' obbligatorio: per la (b) e' quello di
    ``baseline_casuale`` (piccolo), per la (a) quello di ``baseline_da_trade``.
    ``n`` e ``seme`` sono quelli di ``parametri.yaml`` (2000 e 0) e non si
    cambiano per rilanciare. Il buy and hold (baseline (c)) non passa da qui.

    Perche' cosi' e non con due serie (``differenza_nettamente``, fino alla 4.3):
    la (b) e' la MEDIA di 200 strategie casuali e il suo errore e' piccolo;
    confrontare il candidato con UNA corsa casuale aggiungeva il rumore di quella
    corsa. Ma toglierlo e basta avrebbe lasciato scoperti i difetti del bootstrap
    (blocchi lunghi, pochi blocchi) che quel rumore in piu' copriva per caso: la
    correzione del blocco e la soglia di Student li coprono apposta.

    Ritorna ``differenza``, ``errore_standard``, ``margine`` (soglia x errore),
    ``soglia``, ``gradi_liberta``, ``netta``, ``t``, ``p_value`` (lo stesso di
    ``p_value_vs_baseline``: netta vuol dire p_value < 0,02275), ``errore_candidato``
    (gia' corretto), ``n_blocchi`` e ``valutabile``.
    """
    return _confronto(r_candidato, lunghezza_blocco, baseline_media, baseline_errore_standard, n, seme,
                      errore_minimo_candidato)


def _pavimento_minimo_valido(pavimento_minimo: object) -> float:
    """Il ``pavimento_minimo`` di ``contro_baseline`` come float finito e non negativo, o ValueError.

    None (il pavimento delle sfasate non valutabile, ``campagne/GRUPPO/regole.md``,
    sezione 5, punto 5) non e' un pavimento: la variante e' non valutabile, e lo
    decide chi chiama prima del confronto.
    """
    if pavimento_minimo is None or isinstance(pavimento_minimo, bool):
        raise ValueError("pavimento_minimo: serve un numero finito non negativo (un pavimento delle sfasate "
                         "non valutabile rende non valutabile la variante, regole.md sezione 5 punto 5)")
    valore = float(pavimento_minimo)
    if not math.isfinite(valore) or valore < 0:
        raise ValueError(f"pavimento_minimo deve essere un numero finito non negativo, non {pavimento_minimo!r}")
    return valore


def contro_baseline(
    r_candidato: Sequence[float],
    lunghezza_blocco: int,
    baseline: Dict[str, object],
    n: int = 2000,
    seme: int = 0,
    pavimento_minimo: float = 0.0,
) -> Dict[str, object]:
    """Il confronto della sezione 8 con una baseline gia' calcolata. E' QUESTO che si usa.

    ``baseline`` e' il dizionario di ``baseline_casuale`` (o di
    ``motore.simula_baseline_casuale``, che lo restituisce) per la (b), oppure di
    ``baseline_da_trade`` per la (a). Da li' si prendono il numero, il suo errore
    e il pavimento dell'errore del candidato:
    * (b): la deviazione standard degli R medi delle simulazioni
      (``errore_minimo_candidato``);
    * (a): la deviazione standard degli R della (a) divisa per la radice del
      numero di trade del candidato.
    Una (a) non valutabile rende non valutabile anche il confronto (errore
    infinito). Ritorna il risultato di ``batte_nettamente`` (``netta``, ``t``,
    ``soglia``, ``p_value``, ``valutabile``...) piu' ``baseline_media``,
    ``baseline_errore_standard`` ed ``errore_minimo``.

    Campagna di gruppo (``campagne/GRUPPO/regole.md``, sezione 5, punto 6).
    ``pavimento_minimo`` e' il pavimento delle strategie sfasate
    (``pavimento_sfasamento``): il pavimento usato e' il PIU' ALTO fra quello della
    baseline e ``pavimento_minimo``. Con 0 (il predefinito, le campagne singole)
    il pavimento e' quello della baseline e ogni chiave di prima ha lo stesso
    valore, bit per bit. ``baseline`` puo' essere anche il dizionario di
    ``baseline_da_trade_di_gruppo`` (tipo "a") o di ``baseline_casuale_di_gruppo``
    (tipo "b"): una baseline con ``valutabile`` False rende il confronto non
    valutabile anche quando il suo numero non esiste (NaN), senza eccezioni.

    Chiavi in piu' rispetto a prima, solo informative:
    * ``errore_minimo_baseline``: il pavimento della baseline;
    * ``pavimento_minimo``: quello passato;
    * ``origine_pavimento``: "baseline" se il pavimento usato (``errore_minimo``)
      e' quello della baseline (anche a pari valore), "pavimento_minimo" se e'
      quello passato;
    * ``errore_candidato_senza_pavimento``: l'errore della media del candidato dal
      bootstrap a blocchi, gia' corretto per il blocco, PRIMA di qualunque
      pavimento (serve all'effetto grappolo della sezione 5, punto 9, di
      regole.md: ``effetto_grappolo``); None con meno di ``MINIMO_BLOCCHI``
      blocchi interi. E' lo stesso bootstrap (stesso seme) del confronto.
    """
    tipo = baseline.get("tipo")
    arr = _come_array(r_candidato, "r_candidato")
    minimo = _pavimento_minimo_valido(pavimento_minimo)
    if tipo == "b":
        pavimento_baseline = float(baseline["errore_minimo_candidato"])
    elif tipo == "a":
        pavimento_baseline = float(baseline["deviazione_standard"]) / math.sqrt(arr.size)
    else:
        raise ValueError("baseline: serve il dizionario di baseline_casuale (tipo b) o di baseline_da_trade (tipo a)")
    media = float(baseline["media"])
    errore_base = float(baseline["errore_standard"])
    # Il pavimento usato e' il piu' alto dei due; a pari valore, quello della
    # baseline. Con minimo = 0 resta quello della baseline, cosi' com'era.
    if minimo > pavimento_baseline or (math.isnan(pavimento_baseline) and minimo > 0):
        pavimento, origine = minimo, "pavimento_minimo"
    else:
        pavimento, origine = pavimento_baseline, "baseline"
    baseline_non_valutabile = baseline.get("valutabile") is False
    if baseline_non_valutabile and not (math.isfinite(media) and math.isfinite(pavimento_baseline)):
        # Solo le baseline di gruppo non valutabili arrivano qui (numero o
        # pavimento che non esistono): il confronto e' non valutabile.
        if not np.isfinite(arr).all():
            raise ValueError("r_candidato contiene valori non finiti")
        b = int(lunghezza_blocco)
        if b < 1:
            raise ValueError("lunghezza_blocco deve essere almeno 1")
        ris, errore_senza_pavimento = _esito_non_valutabile(float(arr.mean()) - media, arr.size // b), None
    else:
        if not math.isfinite(pavimento_baseline) or pavimento_baseline < 0:
            raise ValueError("errore_minimo_candidato deve essere un numero finito non negativo")
        # una baseline non valutabile ha errore infinito (cosi' gia' la (a) delle campagne singole)
        ris, errore_senza_pavimento = _confronto_dettagliato(
            arr, lunghezza_blocco, media, math.inf if baseline_non_valutabile else errore_base, n, seme, pavimento)
    if errore_senza_pavimento is None and arr.size // int(lunghezza_blocco) >= MINIMO_BLOCCHI:
        # il confronto e' non valutabile per la baseline, ma l'errore del candidato si stima
        errore_senza_pavimento, _ = _errore_media_corretto(arr, int(lunghezza_blocco), n, seme)
    ris.update({"baseline_media": media,
                "baseline_errore_standard": errore_base,
                "errore_minimo": pavimento,
                "errore_minimo_baseline": pavimento_baseline,
                "pavimento_minimo": minimo,
                "origine_pavimento": origine,
                "errore_candidato_senza_pavimento": errore_senza_pavimento})
    return ris


# ---------------------------------------------------------------------------
# p-value e asticella
# ---------------------------------------------------------------------------


def p_value_unilaterale(osservato: float, distribuzione_nulla: Sequence[float]) -> float:
    """Quota della distribuzione nulla >= osservato, con la correzione (k+1)/(n+1).

    La correzione (Phipson & Smyth) evita un p-value di 0 quando nessun valore
    simulato raggiunge l'osservato: con n simulazioni non si puo' affermare che
    la probabilita' sia sotto 1/(n+1), e un p-value esattamente 0 passerebbe
    qualunque asticella. Con la distribuzione nulla vuota ritorna 1.0 (non si
    sa nulla, quindi non si rifiuta nulla).
    """
    nulla = np.asarray(list(distribuzione_nulla), dtype=float)
    n = nulla.size
    if n == 0:
        return 1.0
    k = int(np.count_nonzero(nulla >= osservato))
    return (k + 1) / (n + 1)


def p_value_bootstrap_vs_caso(
    r_candidato: Sequence[float],
    r_caso: Sequence[float],
    lunghezza_blocco: int,
    n: int = 2000,
    seme: int = 0,
) -> float:
    """p-value unilaterale FINO ALLA 4.3: il candidato contro UNA serie di trade casuali.

    Dalla versione 4.4 il p-value dell'asticella e' ``p_value_vs_baseline``
    (contro la MEDIA delle simulazioni casuali): questa funzione resta solo per
    rileggere le campagne archiviate.

    Era il p-value dell'asticella (sezione 8 fino alla 4.3): «la probabilita' di ottenere per
    caso un R medio cosi' superiore a quello dell'entrata casuale con la stessa
    uscita, stimata con bootstrap a blocchi sui trade di validazione».

    Scelta documentata. Non si fa un test di permutazione (mescolare le etichette
    candidato/caso distruggerebbe l'ordine temporale che il bootstrap a blocchi
    vuole preservare) ma un bootstrap della differenza delle medie: si
    ricampionano a blocchi, indipendentemente, i trade del candidato e quelli
    dell'entrata casuale (semi ``seme`` e ``seme + 1``, come in
    ``differenza_nettamente``), si calcola per ogni ricampionamento la
    differenza media(candidato) - media(caso), e il p-value e' la quota dei
    ricampionamenti in cui la differenza e' <= 0, con la correzione
    (k+1)/(n+1) di ``p_value_unilaterale``. Se il vantaggio osservato e' solido,
    quasi nessun ricampionamento lo cancella e p e' piccolo; se le due serie
    sono simili, circa meta' dei ricampionamenti lo cancella e p e' circa 0,5.
    Il minimo raggiungibile e' 1/(n+1): con n=2000 e' circa 0,0005.

    Caso degenere. Se il blocco e' lungo almeno quanto una delle due serie
    (vedi ``bootstrap_degenere``) il bootstrap non stima nulla: tutte le
    differenze ricampionate sarebbero uguali a quella osservata e il p-value
    uscirebbe 1/(n+1), il MINIMO, anche per un vantaggio di un miliardesimo di
    R. Qui si restituisce invece ``1.0``: nessuna evidenza misurabile che il
    candidato batta il caso, quindi il candidato non passa l'asticella. Un
    p-value esattamente 1.0 e' il segnale per il report («non valutabile:
    pochi trade rispetto alla durata delle posizioni»); chi vuole saperlo
    prima chiama ``bootstrap_degenere``.
    """
    arr_cand = _come_array(r_candidato, "r_candidato")
    arr_caso = _come_array(r_caso, "r_caso")
    if bootstrap_degenere(arr_cand.size, lunghezza_blocco) or bootstrap_degenere(arr_caso.size, lunghezza_blocco):
        return 1.0
    boot_cand = bootstrap_blocchi(arr_cand, lunghezza_blocco, n=n, seme=seme)
    boot_caso = bootstrap_blocchi(arr_caso, lunghezza_blocco, n=n, seme=seme + 1)
    differenze = np.asarray(boot_cand["campioni"]) - np.asarray(boot_caso["campioni"])
    # quota dei campioni con differenza <= 0 == quota di (-differenza) >= 0
    return p_value_unilaterale(0.0, -differenze)


def p_value_vs_baseline(
    r_candidato: Sequence[float],
    lunghezza_blocco: int,
    baseline_media: float,
    baseline_errore_standard: float,
    n: int = 2000,
    seme: int = 0,
    errore_minimo_candidato: float = 0.0,
) -> float:
    """p-value unilaterale dell'asticella (sezione 8, dalla versione 4.4).

    Nelle campagne si legge da ``contro_baseline(...)["p_value"]`` con la (b)
    calcolata sul periodo di validazione.

    «La probabilita' di ottenere per caso un R medio cosi' superiore a quello
    dell'entrata casuale con la stessa uscita», sui trade di validazione: e' lo
    stesso calcolo di ``batte_nettamente`` (stesso errore corretto, stessi gradi
    di liberta'), letto come coda superiore della t di Student. Per costruzione
    un candidato «netto» ha p-value sotto 0,02275, e viceversa: le due regole non
    possono dire cose diverse sugli stessi trade.

    Non valutabile (meno di ``MINIMO_BLOCCHI`` blocchi interi, errore della
    baseline infinito, nessun rumore stimabile): 1.0, cioe' nessuna evidenza
    misurabile; il candidato non passa l'asticella.
    """
    return float(_confronto(r_candidato, lunghezza_blocco, baseline_media, baseline_errore_standard, n, seme,
                            errore_minimo_candidato)["p_value"])


def benjamini_hochberg(p_values: Sequence[float], q: float = 0.10) -> List[bool]:
    """Asticella di Benjamini-Hochberg, procedura esatta della sezione 8.

    Ordina p(1) <= p(2) <= ... <= p(m); trova il k piu' grande per cui
    p(k) <= (k / m) * q; passano i candidati da 1 a k nell'ordine dei p-value
    (NON solo quelli che soddisfano la disuguaglianza uno per uno: e' il
    classico "step-up", un p-value sopra la soglia puo' passare se uno piu'
    grande di lui la soddisfa). Se nessun k la soddisfa non passa nessuno.

    Ritorna una lista di bool nell'ORDINE ORIGINALE dei p-value. Lista vuota
    -> lista vuota. I p-value devono stare in [0, 1].

    Parita' esatta sulla soglia. Il protocollo dice «p(k) <= (k/m) x 0,10»: un
    p-value ESATTAMENTE pari alla soglia passa. In virgola mobile pero'
    ``rango / m * q`` puo' uscire un pelo sotto il valore esatto (es.
    7/10*0.1 = 0.06999999999999999) e un p-value di 0.07 verrebbe respinto per
    un errore di arrotondamento, non per la statistica. Per questo il
    confronto ammette una tolleranza relativa di 1e-9: e' enormemente piu'
    piccola della granularita' di qualunque p-value del modulo (1/(n+1), cioe'
    circa 5e-4 con n=2000), quindi non puo' far passare un p-value davvero
    sopra la soglia; serve solo a non perdere la parita'.
    """
    p = [float(x) for x in p_values]
    m = len(p)
    if m == 0:
        return []
    if any(not (0.0 <= x <= 1.0) for x in p):
        raise ValueError("ogni p-value deve stare in [0, 1]")
    if not (0.0 < q <= 1.0):
        raise ValueError("q deve stare in (0, 1]")
    ordine = sorted(range(m), key=lambda i: p[i])
    k_max = 0
    for rango, i in enumerate(ordine, start=1):
        soglia = rango / m * q
        if p[i] <= soglia or math.isclose(p[i], soglia, rel_tol=1e-9, abs_tol=1e-12):
            k_max = rango
    passano = [False] * m
    for rango, i in enumerate(ordine, start=1):
        if rango <= k_max:
            passano[i] = True
    return passano


def percentile(valori: Sequence[float], q: float) -> float:
    """Il q-esimo percentile (q in [0, 100]) con interpolazione lineare di numpy.

    E' il metodo "linear" (il default di numpy, lo stesso di Excel PERCENTILE.INC):
    serve a dire nei report quale definizione si e' usata, perche' su serie
    corte i vari metodi danno numeri diversi. Usato per il 90° percentile
    delle entrate casuali nel ``criterio_vault``.
    """
    arr = _come_array(valori, "valori")
    return float(np.percentile(arr, q, method="linear"))


# ---------------------------------------------------------------------------
# Metriche da trade
# ---------------------------------------------------------------------------


def profit_factor(pnl: Sequence[float]) -> float:
    """Somma dei guadagni / somma delle perdite in valore assoluto.

    Casi limite: nessuna perdita -> inf (se c'e' almeno un guadagno); nessun
    guadagno -> 0 (anche se non ci sono perdite: una strategia senza guadagni
    non deve mai passare l'asticella di profit factor). Vuoto -> 0.
    """
    arr = np.asarray(list(pnl), dtype=float)
    guadagni = float(arr[arr > 0].sum()) if arr.size else 0.0
    perdite = float(-arr[arr < 0].sum()) if arr.size else 0.0
    if perdite > 0:
        return guadagni / perdite
    return math.inf if guadagni > 0 else 0.0


def win_rate(pnl: Sequence[float]) -> float:
    """Quota dei trade con pnl > 0 (uno zero conta come non vinto). Vuoto -> 0."""
    arr = np.asarray(list(pnl), dtype=float)
    if arr.size == 0:
        return 0.0
    return float(np.count_nonzero(arr > 0) / arr.size)


def drawdown_max_da_curva(curva: Sequence[float]) -> float:
    """Massima caduta dal picco precedente, come frazione del picco.

    Si considera solo un picco positivo (una curva di capitale non dovrebbe
    mai essere <= 0; se lo fosse la frazione non avrebbe senso). Vuoto -> 0.
    Esempio: 100, 120, 90, 130 -> il peggio e' da 120 a 90 = 0,25.
    """
    arr = np.asarray(list(curva), dtype=float)
    if arr.size == 0:
        return 0.0
    picchi = np.maximum.accumulate(arr)
    validi = picchi > 0
    if not validi.any():
        return 0.0
    cadute = (picchi[validi] - arr[validi]) / picchi[validi]
    return float(max(0.0, cadute.max()))


def _anno(ts_ms: int) -> int:
    return datetime.fromtimestamp(ts_ms / 1000, tz=timezone.utc).year


def rendimento_per_anno(curva: Sequence[Tuple[int, float]]) -> Dict[int, float]:
    """Rendimento di ogni anno (frazione) da una curva di capitale (ts ms, valore).

    Per ogni anno: ultimo valore dell'anno / valore di riferimento - 1, dove il
    riferimento e' l'ULTIMO valore dell'anno precedente presente nella curva
    (il capitale con cui l'anno e' iniziato) oppure, per il primo anno, il
    primo valore della curva. Cosi' i rendimenti dei vari anni si compongono
    nel rendimento totale e il primo anno non parte da zero. La curva viene
    ordinata per timestamp. Riferimento <= 0 -> 0 per quell'anno. Vuoto -> {}.
    """
    punti = sorted((int(ts), float(v)) for ts, v in curva)
    if not punti:
        return {}
    risultato: Dict[int, float] = {}
    riferimento = punti[0][1]
    anno_corrente = _anno(punti[0][0])
    ultimo = riferimento
    for ts, valore in punti:
        anno = _anno(ts)
        if anno != anno_corrente:
            risultato[anno_corrente] = ultimo / riferimento - 1.0 if riferimento > 0 else 0.0
            riferimento = ultimo
            anno_corrente = anno
        ultimo = valore
    risultato[anno_corrente] = ultimo / riferimento - 1.0 if riferimento > 0 else 0.0
    return risultato


# ---------------------------------------------------------------------------
# Entrate casuali, tasso del caso, criterio del vault
# ---------------------------------------------------------------------------


def entrate_casuali(
    n_barre: int,
    n_trade: int,
    durata_media_barre: int,
    seme: int,
    barre_vietate: Sequence[Tuple[int, int]] = (),
) -> List[int]:
    """Indici di ingresso casuali, senza sovrapposizione, riproducibili col seme.

    Serve a costruire la baseline (b) della sezione 8 e il tasso del caso: la
    strategia casuale la costruisce chi chiama (ingresso all'indice ritornato,
    stessa uscita e stessa direzione del candidato). Qui si scelgono solo gli
    indici.

    Regole:
    * ogni indice sta in [0, n_barre);
    * due ingressi distano almeno ``durata_media_barre`` barre (almeno 1), cosi'
      le posizioni fittizie non si sovrappongono in media come non si
      sovrappongono quelle del candidato;
    * nessun ingresso cade in una finestra vietata: ``barre_vietate`` e' una
      sequenza di coppie (inizio, fine) con inizio INCLUSO e fine ESCLUSA, come
      gli intervalli di Python (serve per il riscaldamento degli indicatori,
      buchi nei dati, periodi che il candidato non poteva usare).

    Metodo: estrazione ESATTAMENTE uniforme fra tutte le configurazioni valide
    (tutti gli insiemi di ``n_trade`` indici ammessi a distanza >= ``distanza``
    hanno la stessa probabilita'). Si contano prima, con una tabella di
    programmazione dinamica, le configurazioni possibili a partire da ogni
    barra con ogni numero di ingressi ancora da piazzare
    (``_log_configurazioni``); poi si scorre la serie da sinistra a destra e
    in ogni barra ammessa si decide se entrare con probabilita' pari alla
    quota di configurazioni che entrano li'. Due conseguenze volute:
    * se una configurazione esiste si trova SEMPRE, con qualunque seme (il
      vecchio metodo greedy su permutazione casuale falliva con alcuni semi
      quando i trade erano fitti, es. 80 trade a distanza 10 su 1000 barre:
      riusciva con 10 semi su 50, e il tasso del caso perdeva simulazioni
      proprio per i candidati che stanno a lungo in posizione);
    * nessun bias sistematico verso un punto della serie: la distribuzione e'
      uniforme per costruzione, quindi le entrate non portano informazione.
    La tabella dei conteggi e' in scala logaritmica perche' il numero di
    configurazioni esplode (binomiali di decine di migliaia di barre).

    Ritorna la lista ORDINATA degli indici. Se NESSUNA configurazione esiste
    (troppi trade per la distanza, o troppe barre vietate) alza ValueError
    dicendo quanti ingressi entrano al massimo: in quel caso il confronto del
    protocollo (stesso numero di trade del candidato) non e' costruibile e va
    dichiarato.
    """
    if n_barre <= 0:
        raise ValueError("n_barre deve essere positivo")
    if n_trade < 0:
        raise ValueError("n_trade non puo' essere negativo")
    distanza = max(1, int(durata_media_barre))
    ammessi = np.ones(n_barre, dtype=bool)
    for inizio, fine in barre_vietate:
        lo = max(0, int(inizio))
        hi = min(n_barre, int(fine))
        if hi > lo:
            ammessi[lo:hi] = False
    if n_trade == 0:
        return []
    return entrate_casuali_per_semi(n_barre, n_trade, durata_media_barre, [seme], barre_vietate)[0]


def entrate_casuali_per_semi(
    n_barre: int,
    n_trade: int,
    durata_media_barre: int,
    semi: Sequence[int],
    barre_vietate: Sequence[Tuple[int, int]] = (),
) -> List[List[int]]:
    """Come ``entrate_casuali``, per piu' semi, costruendo la tabella UNA volta.

    La tabella delle configurazioni dipende solo da barre ammesse, numero di
    trade e distanza, non dal seme: ricostruirla per ognuna delle 200
    simulazioni della baseline (b) era il 60-80% del suo tempo (a 15 minuti,
    decine di minuti per una (b)). Per ogni seme l'estrazione e' identica a
    quella di ``entrate_casuali`` con lo stesso seme: stessi indici.
    """
    if n_barre <= 0:
        raise ValueError("n_barre deve essere positivo")
    if n_trade < 0:
        raise ValueError("n_trade non puo' essere negativo")
    distanza = max(1, int(durata_media_barre))
    ammessi = np.ones(n_barre, dtype=bool)
    for inizio, fine in barre_vietate:
        lo = max(0, int(inizio))
        hi = min(n_barre, int(fine))
        if hi > lo:
            ammessi[lo:hi] = False
    if n_trade == 0:
        return [[] for _ in semi]
    log_conf = _log_configurazioni(ammessi, n_trade, distanza)
    if not np.isfinite(log_conf[0, n_trade]):
        massimo = int(np.flatnonzero(np.isfinite(log_conf[0]))[-1])
        raise ValueError(
            f"impossibile piazzare {n_trade} ingressi a distanza {distanza} "
            f"su {n_barre} barre con {int(ammessi.sum())} ammesse: ne entrano al massimo {massimo}"
        )
    return [_estrai(ammessi, log_conf, n_trade, distanza, n_barre, seme) for seme in semi]


def _estrai(ammessi: np.ndarray, log_conf: np.ndarray, n_trade: int, distanza: int, n_barre: int, seme: int) -> List[int]:
    """L'estrazione uniforme di ``entrate_casuali`` per un seme, dalla tabella gia' fatta."""
    rng = np.random.default_rng(seme)
    # un'estrazione uniforme per barra, tirate tutte insieme: stesso seme,
    # stessi numeri, stessa configurazione.
    estrazioni = rng.random(n_barre)
    scelti: List[int] = []
    i = 0
    restano = n_trade
    while restano > 0:
        if ammessi[i]:
            # quota delle configurazioni (da qui in poi, con `restano` ingressi)
            # che entrano proprio in questa barra
            quota = math.exp(log_conf[i + distanza, restano - 1] - log_conf[i, restano])
            if estrazioni[i] < quota:
                scelti.append(i)
                restano -= 1
                i += distanza
                continue
        i += 1
    return scelti


def _log_configurazioni(ammessi: np.ndarray, n_trade: int, distanza: int) -> np.ndarray:
    """Tabella T[i, j] = log del numero di modi di piazzare j ingressi fra le barre >= i.

    Regola: alla barra i o NON si entra (i modi sono quelli da i+1 con j
    ingressi) oppure, se la barra e' ammessa, si entra (e i j-1 ingressi
    restanti stanno da i+distanza in poi). T[i, 0] = log(1) = 0 per ogni i
    (zero ingressi si piazzano in un solo modo); T[i, j>0] = -inf oltre la
    fine. La tabella ha ``distanza`` righe in piu' in fondo cosi' l'indice
    i+distanza non esce mai. Scala logaritmica con ``logaddexp`` perche' i
    conteggi superano in fretta il massimo rappresentabile in virgola mobile.
    """
    n = ammessi.size
    tabella = np.full((n + distanza + 1, n_trade + 1), -np.inf)
    tabella[:, 0] = 0.0
    for i in range(n - 1, -1, -1):
        if ammessi[i]:
            tabella[i, 1:] = np.logaddexp(tabella[i + 1, 1:], tabella[i + distanza, :-1])
        else:
            tabella[i, 1:] = tabella[i + 1, 1:]
    return tabella


def tasso_del_caso(esiti: Sequence[bool]) -> float:
    """Quota delle strategie fittizie che passano il criterio del vault. Vuoto -> 0."""
    lista = [bool(e) for e in esiti]
    if not lista:
        return 0.0
    return sum(lista) / len(lista)


def criterio_vault(
    metriche: Dict[str, object],
    r_caso_percentile_90: float,
    trade_minimi: int = 30,
    pf_minimo: float = 1.10,
) -> Dict[str, object]:
    """Il ``criterio_vault`` della sezione 3: quattro condizioni, tutte insieme.

    ``metriche`` e' il dizionario del motore (chiavi ``profit_factor``,
    ``n_trade``, ``rendimento_totale``, ``r_medio``; una chiave mancante alza
    KeyError, meglio che passare per sbaglio). ``r_caso_percentile_90`` e' il
    90° percentile degli R medi delle entrate casuali con la stessa uscita,
    sul periodo del vault (``percentile(r_medi_caso, 90)``).

    Ritorna ``esito`` (True solo se passano tutte) e ``condizioni`` con le
    quattro separate, cosi' nel report si vede QUALE e' caduta:
    * ``profit_factor``: profit factor dopo costi >= pf_minimo;
    * ``trade_minimi``: n_trade >= trade_minimi;
    * ``rendimento_positivo``: rendimento totale > 0;
    * ``sopra_il_caso``: R medio > r_caso_percentile_90.
    Riporta anche i valori usati, per il report.
    """
    pf = float(metriche["profit_factor"])
    n_trade = int(metriche["n_trade"])
    rendimento = float(metriche["rendimento_totale"])
    r_medio = float(metriche["r_medio"])
    condizioni = {
        "profit_factor": bool(pf >= pf_minimo),
        "trade_minimi": bool(n_trade >= trade_minimi),
        "rendimento_positivo": bool(rendimento > 0.0),
        "sopra_il_caso": bool(r_medio > float(r_caso_percentile_90)),
    }
    return {
        "esito": all(condizioni.values()),
        "condizioni": condizioni,
        "valori": {
            "profit_factor": pf,
            "n_trade": n_trade,
            "rendimento_totale": rendimento,
            "r_medio": r_medio,
            "r_caso_percentile_90": float(r_caso_percentile_90),
            "pf_minimo": float(pf_minimo),
            "trade_minimi": int(trade_minimi),
        },
    }


def monete_richieste_trasferimento(n_monete: int, p_caso: float, livello: float = 0.05, minimo: int = 2) -> int:
    """Su quante monete un candidato deve passare per «trasferirsi» (Passo 6, dalla 4.5).

    Il piu' piccolo k, mai sotto ``minimo`` (``trasferimento_monete_minime``), per cui la
    probabilita' di almeno k passaggi PER CASO su ``n_monete`` monete e' sotto ``livello``
    (``trasferimento.livello_caso``), con ``p_caso`` la probabilita' che una strategia senza
    vantaggio passi su una moneta (il piu' alto fra ``trasferimento.caso_per_moneta_minimo`` e
    la «netta per caso» della prova a placebo). Binomiale: le monete correlate sono gia' state
    fuse in una prima di contare ``n_monete``. Con una soglia fissa a 2, su 80 monete con
    l'1% a moneta, 2 passaggi escono per caso il 19% delle volte.

    Se nemmeno k = n_monete basta (poche monete), restituisce un numero piu' grande di
    n_monete (mai sotto ``minimo``): il trasferimento non si puo' dimostrare e l'esito e'
    «non si sa».
    """
    from scipy.stats import binom

    n = int(n_monete)
    p = float(p_caso)
    if n < 0 or not (0.0 <= p <= 1.0) or not (0.0 < livello < 1.0):
        raise ValueError("servono n_monete >= 0, p_caso in [0, 1] e livello in (0, 1)")
    for k in range(max(int(minimo), 1), n + 1):
        if float(binom.sf(k - 1, n, p)) < livello:  # sf(k-1) = P(X >= k)
            return k
    return max(int(minimo), n + 1)


# ---------------------------------------------------------------------------
# Campagna di gruppo (Passo 4bis del protocollo: research/campagne/GRUPPO/regole.md)
# ---------------------------------------------------------------------------
#
# Le funzioni qui sotto sono le sole che fanno i calcoli statistici dell'esame
# di gruppo (regole.md, sezione 0, punto 4, e sezione 13); le chiama
# ``research/src/gruppo.py``. Sono pure e senza numeri casuali. Due scelte
# valgono per tutte:
# * ogni somma su piu' monete si fa nell'ordine dei caratteri dei simboli,
#   qualunque sia l'ordine in cui le monete arrivano: il risultato e' lo stesso
#   bit per bit con le monete in qualunque ordine (e con qualunque numero di
#   processi che le ha calcolate);
# * i pesi si calcolano prima (n_j / somma degli n) e poi si moltiplicano:
#   con una moneta sola il peso e' esattamente 1, e ogni numero e' quello del
#   percorso delle campagne singole, bit per bit (regole.md, sezione 13, test
#   obbligatori).


@dataclass(frozen=True)
class TradeDiGruppo:
    """Un trade della campagna di gruppo: la moneta e i soli numeri dell'esame (regole.md, sezione 5, punto 1).

    * ``simbolo``: la moneta, come in ``campagne/GRUPPO/monete.csv`` (es. ``"AAVEUSDT"``);
    * ``ts_entrata``, ``ts_uscita``: istanti in millisecondi UTC, quelli di
      ``motore.Trade`` (un'uscita dentro una barra ha l'istante di chiusura della
      barra, sezione 7 del protocollo);
    * ``r``: l'R del trade dopo i costi (``motore.Trade.r``);
    * ``pnl``: il risultato netto in USDT sul capitale della moneta
      (``motore.Trade.pnl``), per profit factor e risultato totale (regole.md,
      sezione 9, punto 2).

    Immutabile. Da un ``motore.Trade`` ``t`` della moneta ``s``:
    ``TradeDiGruppo(s, t.ts_entrata, t.ts_uscita, t.r, t.pnl)`` (questo modulo non
    importa il motore). In JSON con ``dataclasses.asdict``; si rilegge con
    ``TradeDiGruppo(**voce)``. Non ha un ordine proprio (``sorted`` alza
    TypeError): l'ordine dei trade sommati e' solo quello di
    ``ordina_trade_di_gruppo``.
    """

    simbolo: str
    ts_entrata: int
    ts_uscita: int
    r: float
    pnl: float


def _chiave_ordine_di_gruppo(trade: object) -> Tuple[int, str, int]:
    """La chiave dell'ordine fisso di regole.md, sezione 5, punto 1: (uscita, simbolo, entrata)."""
    return (operator.index(trade.ts_uscita), trade.simbolo, operator.index(trade.ts_entrata))


def ordina_trade_di_gruppo(trade: Iterable[object]) -> List[object]:
    """I trade sommati di tutte le monete nell'ordine fisso di regole.md, sezione 5, punto 1.

    L'ordine e': per istante d'uscita, poi per simbolo in ordine dei caratteri
    (i punti di codice: prima le cifre, poi le lettere, come in ``monete.csv``),
    poi per istante d'entrata. E' l'ordine «per uscita» della sezione 8 del
    protocollo, reso totale fra monete diverse: il bootstrap a blocchi, il blocco
    e ogni media sui trade sommati si calcolano in quest'ordine, che non dipende
    dall'ordine in cui le monete sono state calcolate.

    ``trade``: oggetti con gli attributi ``simbolo`` (str non vuota),
    ``ts_entrata`` e ``ts_uscita`` (interi, ms), di norma ``TradeDiGruppo``.
    Ritorna una lista nuova con gli stessi oggetti. ValueError se un trade esce
    prima di entrare o se due trade della stessa moneta entrano nello stesso
    istante: il motore tiene una posizione alla volta per moneta, quindi sarebbe
    un errore nei dati, e con due trade a pari chiave l'ordine dipenderebbe da
    quello d'arrivo. Con una moneta sola e' l'ordine del motore (per uscita).
    """
    lista = list(trade)
    viste = set()
    for t in lista:
        simbolo = t.simbolo
        if not isinstance(simbolo, str) or not simbolo:
            raise ValueError(f"simbolo non valido: {simbolo!r}")
        entrata, uscita = operator.index(t.ts_entrata), operator.index(t.ts_uscita)
        if uscita < entrata:
            raise ValueError(f"un trade di {simbolo} esce ({uscita}) prima di entrare ({entrata})")
        if (simbolo, entrata) in viste:
            raise ValueError(f"due trade di {simbolo} entrano nello stesso istante ({entrata}): "
                             "il motore tiene una posizione alla volta per moneta")
        viste.add((simbolo, entrata))
    return sorted(lista, key=_chiave_ordine_di_gruppo)


def _somma_in_ordine(termini: Sequence[float]) -> float:
    """Somma da sinistra a destra partendo dal primo termine (cosi' con un termine solo e' quel termine)."""
    totale = float(termini[0])
    for x in termini[1:]:
        totale += float(x)
    return totale


def _trade_candidato_positivi(trade_candidato_per_moneta: Mapping[str, int]) -> Dict[str, int]:
    """{simbolo: n_j} delle sole monete con n_j > 0, in ordine dei caratteri. ValueError se N = 0.

    Una moneta senza trade del candidato pesa zero e non ha baseline (regole.md,
    sezione 5, punto 3).
    """
    positivi: Dict[str, int] = {}
    for simbolo in sorted(trade_candidato_per_moneta):
        if not isinstance(simbolo, str) or not simbolo:
            raise ValueError(f"simbolo non valido: {simbolo!r}")
        valore = trade_candidato_per_moneta[simbolo]
        if isinstance(valore, bool):
            raise ValueError(f"trade del candidato su {simbolo}: serve un intero, non {valore!r}")
        n_j = operator.index(valore)
        if n_j < 0:
            raise ValueError(f"trade del candidato su {simbolo}: {n_j} e' negativo")
        if n_j > 0:
            positivi[simbolo] = n_j
    if not positivi:
        raise ValueError("il candidato non ha trade su nessuna moneta (N = 0): niente da confrontare")
    return positivi


def _controlla_monete(per_moneta: Mapping[str, object], trade_candidato_per_moneta: Mapping[str, int],
                      positivi: Dict[str, int], nome: str) -> None:
    """ValueError se ``per_moneta`` nomina monete sconosciute o manca una moneta con n_j > 0."""
    sconosciute = sorted(set(per_moneta) - set(trade_candidato_per_moneta))
    if sconosciute:
        raise ValueError(f"{nome}: monete senza il numero di trade del candidato: {sconosciute}")
    mancanti = [s for s in positivi if s not in per_moneta]
    if mancanti:
        raise ValueError(f"{nome}: mancano le monete con trade del candidato {mancanti}")


def baseline_da_trade_di_gruppo(
    baseline_per_moneta: Mapping[str, Optional[Dict[str, object]]],
    trade_candidato_per_moneta: Mapping[str, int],
) -> Dict[str, object]:
    """La baseline (a) di gruppo come UN numero (regole.md, sezione 5, punto 3).

    ``baseline_per_moneta``: {simbolo: dizionario di ``baseline_da_trade``} della (a)
    di ogni moneta j con n_j > 0, calcolato sui SUOI trade con il blocco di
    ``lunghezza_blocco`` sui suoi trade; None se la (a) di quella moneta non ha
    trade (``baseline_da_trade`` non si puo' chiamare). ``trade_candidato_per_moneta``:
    {simbolo: n_j}, i trade del candidato su ogni moneta nel periodo; le monete con
    n_j = 0 pesano zero e non hanno (a) (se il loro dizionario c'e', si ignora).
    N = somma degli n_j, w_j = n_j / N.

    * numero: A = somma di w_j · A_j (A_j la ``media`` della (a) della moneta);
    * errore: somma di w_j · e_j, con e_j l'``errore_standard`` della (a) della
      moneta, oppure la sua ``deviazione_standard`` (dev_j) se la (a) ha meno di
      ``MINIMO_BLOCCHI`` (3) blocchi interi; le monete trattate come se si
      muovessero insieme, un errore che non sottostima;
    * deviazione standard combinata: radice(somma di n_j · dev_j² / N), calcolata
      come radice(somma di w_j · dev_j²); cosi' il pavimento della (a) in
      ``contro_baseline`` (deviazione / radice(N)) vale radice(somma di n_j · dev_j²) / N.

    Se la (a) di una moneta con n_j > 0 ha meno di 2 trade (o e' None) la
    variante e' non valutabile: ``valutabile`` False ed ``errore_standard``
    infinito, come la (a) non valutabile delle campagne singole, cosi'
    ``contro_baseline`` da' un confronto non valutabile; se una (a) e' None il
    numero e la deviazione non esistono (NaN).

    Ritorna un dizionario di tipo "a", da passare cosi' com'e' a
    ``contro_baseline``: ``tipo``, ``media``, ``errore_standard``,
    ``deviazione_standard``, ``valutabile``, ``motivo`` (None o la frase del
    perche' non e' valutabile), ``n_trade`` (i trade delle (a), sommati),
    ``n_trade_candidato`` (N), ``n_monete`` (quelle con n_j > 0), ``pesi``
    ({simbolo: w_j}), ``monete_errore_da_deviazione``,
    ``monete_con_meno_di_2_trade`` e ``per_moneta`` ({simbolo: numeri della moneta,
    con ``errore_usato`` = e_j}, None per una (a) senza trade).

    Con una moneta sola il peso e' 1 e, se la sua (a) ha almeno 3 blocchi
    interi, numero, errore e deviazione sono quelli di ``baseline_da_trade`` bit
    per bit. Con meno di 3 blocchi le due regole sono diverse per scelta di
    regole.md (qui e_j = dev_j e il confronto si fa; nelle campagne singole la (a)
    e' non valutabile).
    """
    positivi = _trade_candidato_positivi(trade_candidato_per_moneta)
    _controlla_monete(baseline_per_moneta, trade_candidato_per_moneta, positivi, "baseline_per_moneta")
    n_totale = sum(positivi.values())
    pesi = {s: n_j / n_totale for s, n_j in positivi.items()}
    per_moneta: Dict[str, Optional[Dict[str, object]]] = {}
    poche: List[str] = []
    da_deviazione: List[str] = []
    termini_media: List[float] = []
    termini_errore: List[float] = []
    termini_varianza: List[float] = []
    numero_mancante = False
    trade_baseline = 0
    for simbolo, n_j in positivi.items():
        base = baseline_per_moneta[simbolo]
        if base is None:
            poche.append(simbolo)
            per_moneta[simbolo] = None
            numero_mancante = True
            continue
        if base.get("tipo") != "a":
            raise ValueError(f"baseline di {simbolo}: serve il dizionario di baseline_da_trade (tipo a)")
        media_j = float(base["media"])
        deviazione_j = float(base["deviazione_standard"])
        errore_j = float(base["errore_standard"])
        trade_j = operator.index(base["n_trade"])
        blocchi_j = operator.index(base["n_blocchi"])
        if not math.isfinite(media_j) or not math.isfinite(deviazione_j) or deviazione_j < 0 or trade_j < 1:
            raise ValueError(f"baseline di {simbolo}: numeri non validi (media {media_j}, deviazione "
                             f"{deviazione_j}, trade {trade_j})")
        errore_da_deviazione = blocchi_j < MINIMO_BLOCCHI
        errore_usato = deviazione_j if errore_da_deviazione else errore_j
        if not math.isfinite(errore_usato) or errore_usato < 0:
            raise ValueError(f"baseline di {simbolo}: errore non valido ({errore_usato}) con {blocchi_j} blocchi")
        if errore_da_deviazione:
            da_deviazione.append(simbolo)
        if trade_j < 2:
            poche.append(simbolo)
        trade_baseline += trade_j
        w_j = pesi[simbolo]
        termini_media.append(w_j * media_j)
        termini_errore.append(w_j * errore_usato)
        termini_varianza.append(w_j * (deviazione_j * deviazione_j))
        per_moneta[simbolo] = {
            "n_trade_candidato": n_j, "peso": w_j, "media": media_j, "errore_standard": errore_j,
            "errore_usato": errore_usato, "deviazione_standard": deviazione_j, "n_trade": trade_j,
            "n_blocchi": blocchi_j, "errore_da_deviazione": errore_da_deviazione,
        }
    valutabile = not poche
    return {
        "tipo": "a",
        "media": math.nan if numero_mancante else _somma_in_ordine(termini_media),
        "errore_standard": _somma_in_ordine(termini_errore) if valutabile else math.inf,
        "deviazione_standard": math.nan if numero_mancante else math.sqrt(_somma_in_ordine(termini_varianza)),
        "valutabile": valutabile,
        "motivo": None if valutabile else f"la (a) ha meno di 2 trade su: {', '.join(poche)}",
        "n_trade": trade_baseline,
        "n_trade_candidato": n_totale,
        "n_monete": len(positivi),
        "pesi": pesi,
        "monete_errore_da_deviazione": da_deviazione,
        "monete_con_meno_di_2_trade": poche,
        "per_moneta": per_moneta,
    }


def baseline_casuale_di_gruppo(
    r_medio_per_seme_per_moneta: Mapping[str, Optional[Sequence[Optional[float]]]],
    trade_candidato_per_moneta: Mapping[str, int],
) -> Dict[str, object]:
    """La baseline (b) di gruppo come UN numero (regole.md, sezione 5, punto 4).

    ``r_medio_per_seme_per_moneta``: {simbolo: lista ``r_medio_per_seme`` di
    ``motore.simula_baseline_casuale`` della moneta j}, cioe' m_j(s) per s da 0 a
    S - 1 (di regola S = 200, semi 1000·j + s) con None per le simulazioni senza
    trade; None al posto della lista se sulla moneta gli ingressi casuali non
    entrano (``entrate_casuali`` alza). Le liste devono avere tutte la stessa
    lunghezza S. ``trade_candidato_per_moneta``: {simbolo: n_j}; le monete con
    n_j = 0 non hanno (b) (se la loro lista c'e', si ignora).

    * M(s) = somma di n_j · m_j(s) / somma di n_j, con le due somme sulle sole
      monete che hanno trade nella loro simulazione s e i pesi n_j del candidato;
      una M(s) senza nessuna moneta con trade non esiste e si conta
      (``m_mancanti``); quelle fatte su una parte delle monete si contano in
      ``m_parziali``;
    * numero B = media delle M(s); errore = deviazione standard delle M(s) (ddof 1)
      / radice(numero delle M(s)); pavimento della (b)
      (``errore_minimo_candidato``) = deviazione standard delle M(s);
      ``percentile_90`` e ``valori`` (le M(s), per ``percentile_del_candidato``,
      che si riporta sempre come indizio): sono le chiavi di ``baseline_casuale``
      calcolata sulle M(s), con la stessa funzione;
    * b_j = media delle m_j(s) con trade (``b_per_moneta``, per gli estremi della
      Fase 4: ``estremi_di_gruppo``).

    Non valutabile (``valutabile`` False, ``errore_standard`` infinito, e i numeri
    che non esistono NaN) se su una moneta con n_j > 0 gli ingressi non entrano,
    se una moneta con n_j > 0 ha meno di 2 simulazioni con trade, o se restano
    meno di 2 M(s). ``contro_baseline`` lo legge come un confronto non valutabile.

    Ritorna il dizionario di tipo "b" di ``baseline_casuale`` (da passare cosi'
    com'e' a ``contro_baseline``) piu' ``valutabile``, ``motivo``,
    ``n_trade_candidato`` (N), ``n_monete``, ``pesi`` ({simbolo: n_j / N}),
    ``b_per_moneta`` ({simbolo: b_j o None}), ``simulazioni_per_moneta`` (S),
    ``simulazioni_con_trade_per_moneta``, ``m_mancanti``, ``m_parziali``,
    ``monete_senza_ingressi`` e ``monete_con_meno_di_2_simulazioni``.

    Con una moneta sola M(s) = m(s) bit per bit (peso 1) e tutti i numeri sono
    quelli di ``baseline_casuale`` sulle simulazioni con trade, cioe' della (b)
    delle campagne singole.
    """
    positivi = _trade_candidato_positivi(trade_candidato_per_moneta)
    _controlla_monete(r_medio_per_seme_per_moneta, trade_candidato_per_moneta, positivi,
                      "r_medio_per_seme_per_moneta")
    n_totale = sum(positivi.values())
    liste: Dict[str, List[Optional[float]]] = {}
    senza_ingressi: List[str] = []
    for simbolo in positivi:
        valori = r_medio_per_seme_per_moneta[simbolo]
        if valori is None:
            senza_ingressi.append(simbolo)
            continue
        lista: List[Optional[float]] = []
        for x in valori:
            if x is None:
                lista.append(None)
                continue
            v = float(x)
            if not math.isfinite(v):
                raise ValueError(f"r_medio_per_seme di {simbolo}: valore non finito {x!r} (le vuote sono None)")
            lista.append(v)
        liste[simbolo] = lista
    lunghezze = sorted({len(lista) for lista in liste.values()})
    if len(lunghezze) > 1:
        raise ValueError(f"r_medio_per_seme: le monete hanno numeri di simulazioni diversi {lunghezze}")
    n_semi = lunghezze[0] if lunghezze else 0

    b_per_moneta: Dict[str, Optional[float]] = {}
    con_trade: Dict[str, int] = {}
    for simbolo in positivi:
        presenti = [x for x in liste.get(simbolo, []) if x is not None]
        con_trade[simbolo] = len(presenti)
        b_per_moneta[simbolo] = float(np.asarray(presenti, dtype=float).mean()) if presenti else None
    poche = [s for s in positivi if s in liste and con_trade[s] < 2]

    valori_m: List[float] = []
    mancanti = 0
    parziali = 0
    for s in range(n_semi):
        presenti_s = [(simbolo, lista[s]) for simbolo, lista in liste.items() if lista[s] is not None]
        if not presenti_s:
            mancanti += 1
            continue
        if len(presenti_s) < len(positivi):
            parziali += 1
        totale_s = sum(positivi[simbolo] for simbolo, _ in presenti_s)
        valori_m.append(_somma_in_ordine([(positivi[simbolo] / totale_s) * m for simbolo, m in presenti_s]))

    motivi: List[str] = []
    if senza_ingressi:
        motivi.append(f"gli ingressi casuali non entrano su: {', '.join(senza_ingressi)}")
    if poche:
        motivi.append(f"meno di 2 simulazioni con trade su: {', '.join(poche)}")
    if len(valori_m) < 2:
        motivi.append(f"solo {len(valori_m)} M(s) su {n_semi}")
    valutabile = not motivi

    if len(valori_m) >= 2:
        risultato = baseline_casuale(valori_m)
    else:
        arr = np.asarray(valori_m, dtype=float)
        risultato = {
            "tipo": "b",
            "media": float(arr.mean()) if arr.size else math.nan,
            "errore_standard": math.inf,
            "errore_minimo_candidato": math.nan,
            "n_simulazioni": int(arr.size),
            "percentile_90": float(np.percentile(arr, 90, method="linear")) if arr.size else math.nan,
            "valori": arr,
        }
    if not valutabile:
        risultato["errore_standard"] = math.inf
    risultato.update({
        "valutabile": valutabile,
        "motivo": "; ".join(motivi) if motivi else None,
        "n_trade_candidato": n_totale,
        "n_monete": len(positivi),
        "pesi": {s: n_j / n_totale for s, n_j in positivi.items()},
        "b_per_moneta": b_per_moneta,
        "simulazioni_per_moneta": n_semi,
        "simulazioni_con_trade_per_moneta": con_trade,
        "m_mancanti": mancanti,
        "m_parziali": parziali,
        "monete_senza_ingressi": senza_ingressi,
        "monete_con_meno_di_2_simulazioni": poche,
    })
    return risultato


def pavimento_sfasamento(
    r_medio_sfasate: Sequence[Optional[float]],
    trade_sfasate: Sequence[int],
    n_trade_candidato: int,
) -> Dict[str, object]:
    """Il pavimento delle strategie sfasate (regole.md, sezione 5, punto 5).

    ``r_medio_sfasate``: M'(s), l'R medio dei trade sommati (tutte le monete)
    della strategia sfasata s, None per una sfasata senza trade;
    ``trade_sfasate``: n'(s), il numero dei suoi trade; ``n_trade_candidato``: N,
    i trade sommati del candidato. Le due liste vanno nell'ordine di s e hanno
    la stessa lunghezza; M'(s) e' None se e solo se n'(s) = 0 (ValueError se no).

    pavimento = deviazione standard (ddof 1) dei valori
    (M'(s) - media delle M') · radice(n'(s) / N), sulle sole s con almeno un
    trade (la media delle M' e' la media semplice su quelle s). La radice corregge
    per i trade saltati: e' esatta con trade indipendenti, con i grappoli e'
    un'approssimazione che la prova a placebo della sezione 11 di regole.md
    controlla.

    Con meno di 2 sfasate con trade la variante e' non valutabile: ``pavimento``
    None e ``valutabile`` False. Il pavimento va a ``contro_baseline`` come
    ``pavimento_minimo`` (sezione 5, punto 6), che rifiuta None.

    Ritorna ``pavimento``, ``valutabile``, ``media_r_sfasate`` (None senza sfasate
    con trade), ``sfasate``, ``sfasate_con_trade``, ``sfasate_senza_trade`` e la
    distribuzione di n'(s) / N su tutte le s (``quota_trade_minima``,
    ``quota_trade_mediana``, ``quota_trade_massima``; None senza sfasate).
    """
    medie = list(r_medio_sfasate)
    quanti = [operator.index(x) for x in trade_sfasate]
    if len(medie) != len(quanti):
        raise ValueError(f"r_medio_sfasate ({len(medie)}) e trade_sfasate ({len(quanti)}) hanno lunghezze diverse")
    if isinstance(n_trade_candidato, bool):
        raise ValueError("n_trade_candidato: serve un intero")
    n_totale = operator.index(n_trade_candidato)
    if n_totale < 1:
        raise ValueError("n_trade_candidato deve essere almeno 1")
    coppie: List[Tuple[float, int]] = []
    for s, (m, k) in enumerate(zip(medie, quanti)):
        if k < 0:
            raise ValueError(f"sfasata {s}: numero di trade negativo ({k})")
        if k == 0:
            if m is not None:
                raise ValueError(f"sfasata {s}: senza trade ma con R medio {m!r} (dev'essere None)")
            continue
        if m is None:
            raise ValueError(f"sfasata {s}: {k} trade ma R medio None")
        v = float(m)
        if not math.isfinite(v):
            raise ValueError(f"sfasata {s}: R medio non finito {m!r}")
        coppie.append((v, k))
    quote = np.asarray(quanti, dtype=float) / n_totale
    info: Dict[str, object] = {
        "sfasate": len(medie),
        "sfasate_con_trade": len(coppie),
        "sfasate_senza_trade": len(medie) - len(coppie),
        "quota_trade_minima": float(quote.min()) if quote.size else None,
        "quota_trade_mediana": float(np.median(quote)) if quote.size else None,
        "quota_trade_massima": float(quote.max()) if quote.size else None,
    }
    if len(coppie) < 2:
        media = coppie[0][0] if coppie else None
        return dict({"pavimento": None, "valutabile": False, "media_r_sfasate": media}, **info)
    arr_m = np.asarray([m for m, _ in coppie], dtype=float)
    arr_k = np.asarray([k for _, k in coppie], dtype=float)
    media = float(arr_m.mean())
    valori = (arr_m - media) * np.sqrt(arr_k / n_totale)
    return dict({"pavimento": float(np.std(valori, ddof=1)), "valutabile": True, "media_r_sfasate": media}, **info)


def griglia_sfasamenti(barre_finestra: int, margine: int, numero_sfasamenti: int) -> Dict[str, object]:
    """Gli sfasamenti d_s delle strategie sfasate, in barre (regole.md, sezione 5, punto 5, e sezione 9, punto 3).

    ``barre_finestra``: L, le barre del timeframe della variante nella finestra
    del periodo, contate sul calendario (buchi compresi). ``margine``: il piu'
    alto fra 30 giorni e la durata massima dei trade del candidato nel periodo, in
    barre (lo calcola chi chiama); qui si porta a L // 4 se e' piu' alto.
    ``numero_sfasamenti``: S (200 per il pavimento, 1.000 per le sfasate del vault).

    d_s = margine + arrotondamento di s · (L - 2 · margine) / (S - 1), con le meta'
    verso l'alto, per s da 0 a S - 1 (con interi: niente virgola mobile, e non
    l'arrotondamento «al pari» di ``round``). Cosi' d_0 = margine e
    d_(S-1) = L - margine. Se L - 2 · margine + 1 e' meno di S, gli sfasamenti
    sono tutti gli interi da margine a L - margine, una volta ciascuno, e si
    dichiara quanti sono (``numero``; ``tutti_gli_interi`` True). Esempio: il
    vault a 1d ha L = 1004; con margine 30 e S = 1000 gli sfasamenti sono i 945
    interi da 30 a 974.

    ValueError se S < 2, se L < 1, se il margine e' negativo, o se il margine
    usato viene 0 (L < 4): uno sfasamento di 0 o di L barre sarebbe il candidato
    stesso.

    Ritorna ``sfasamenti`` (lista di interi, nell'ordine di s), ``numero``,
    ``margine`` (quello usato), ``margine_richiesto``, ``barre_finestra``,
    ``sfasamenti_richiesti`` e ``tutti_gli_interi``.
    """
    for nome, valore in (("barre_finestra", barre_finestra), ("margine", margine),
                         ("numero_sfasamenti", numero_sfasamenti)):
        if isinstance(valore, bool):
            raise ValueError(f"{nome}: serve un intero, non {valore!r}")
    n_barre = operator.index(barre_finestra)
    richiesto = operator.index(margine)
    n_sfasamenti = operator.index(numero_sfasamenti)
    if n_sfasamenti < 2:
        raise ValueError("servono almeno 2 sfasamenti")
    if n_barre < 1:
        raise ValueError("la finestra deve avere almeno una barra")
    if richiesto < 0:
        raise ValueError("il margine non puo' essere negativo")
    usato = min(richiesto, n_barre // 4)
    if usato < 1:
        raise ValueError(f"margine {usato} su una finestra di {n_barre} barre: uno sfasamento di 0 o di L barre "
                         "sarebbe il candidato stesso")
    ampiezza = n_barre - 2 * usato
    if ampiezza + 1 < n_sfasamenti:
        sfasamenti = list(range(usato, n_barre - usato + 1))
        tutti = True
    else:
        denominatore = n_sfasamenti - 1
        # arrotondamento con le meta' verso l'alto di x = s · ampiezza / denominatore:
        # floor(x + 1/2) = (2 · s · ampiezza + denominatore) // (2 · denominatore)
        sfasamenti = [usato + (2 * s * ampiezza + denominatore) // (2 * denominatore) for s in range(n_sfasamenti)]
        tutti = False
    return {
        "sfasamenti": sfasamenti,
        "numero": len(sfasamenti),
        "margine": usato,
        "margine_richiesto": richiesto,
        "barre_finestra": n_barre,
        "sfasamenti_richiesti": n_sfasamenti,
        "tutti_gli_interi": tutti,
    }


def effetto_grappolo(errore_candidato_prima_del_pavimento: Optional[float], r: Sequence[float]) -> Optional[float]:
    """L'effetto grappolo (regole.md, sezione 5, punto 9): errore² · N / varianza degli R.

    ``errore_candidato_prima_del_pavimento``: l'errore della media del candidato
    dal bootstrap a blocchi sui trade sommati, gia' corretto per il blocco e
    preso PRIMA di qualunque pavimento: la chiave
    ``errore_candidato_senza_pavimento`` di ``contro_baseline`` (stesso bootstrap,
    stesso seme). ``r``: gli R dei trade sommati (N = quanti sono); varianza con
    ddof 1.

    Dice quante volte i trade sommati valgono meno di trade indipendenti: con
    trade indipendenti l'errore² e' circa varianza / N e l'effetto e' circa 1.
    Solo informazione, mai prova. None quando non si calcola: errore None o
    infinito (meno di 3 blocchi interi), meno di 2 trade, R tutti uguali
    (varianza 0: in virgola mobile la varianza di una serie costante puo' uscire
    1e-33 invece di 0, e l'effetto un numero enorme senza senso).
    ValueError se l'errore e' negativo o NaN.
    """
    arr = _come_array(r, "r")
    if errore_candidato_prima_del_pavimento is None:
        return None
    errore = float(errore_candidato_prima_del_pavimento)
    if math.isnan(errore) or errore < 0:
        raise ValueError(f"errore del candidato non valido: {errore_candidato_prima_del_pavimento!r}")
    if math.isinf(errore) or arr.size < 2 or bool(np.all(arr == arr[0])):
        return None
    varianza = float(arr.var(ddof=1))
    return errore * errore * arr.size / varianza


def _giorno_utc(ts_ms: int) -> int:
    """Il giorno UTC di un istante in ms, come numero di giorni dal 1970-01-01."""
    return operator.index(ts_ms) // GIORNO_MS


def _data_del_giorno(giorno: int) -> str:
    """Il giorno UTC (giorni dal 1970-01-01) come AAAA-MM-GG."""
    return datetime.fromtimestamp(giorno * 86_400, tz=timezone.utc).date().isoformat()


def _b_ripesata(trade: Sequence[object], b_per_moneta: Mapping[str, Optional[float]]) -> Optional[float]:
    """Σ r_j · b_j / Σ r_j, con r_j i trade di ``trade`` della moneta j (regole.md, sezione 6, punto 2.5)."""
    if not trade:
        return None
    conteggi: Dict[str, int] = {}
    for t in trade:
        conteggi[t.simbolo] = conteggi.get(t.simbolo, 0) + 1
    totale = len(trade)
    termini: List[float] = []
    for simbolo in sorted(conteggi):
        b_j = b_per_moneta.get(simbolo)
        if b_j is None:
            raise ValueError(f"b_per_moneta: manca la b_j di {simbolo}, che ha trade")
        valore = float(b_j)
        if not math.isfinite(valore):
            raise ValueError(f"b_per_moneta: b_j di {simbolo} non finita ({b_j!r})")
        termini.append((conteggi[simbolo] / totale) * valore)
    return _somma_in_ordine(termini)


def _r_medio(trade: Sequence[object]) -> Optional[float]:
    """La media semplice degli R, nell'ordine dato; None senza trade."""
    if not trade:
        return None
    return float(np.asarray([float(t.r) for t in trade], dtype=float).mean())


def estremi_di_gruppo(
    trade: Iterable[object],
    b_gruppo: float,
    b_per_moneta: Mapping[str, Optional[float]],
    trade_migliori: int = 30,
    giorni_migliori: int = 3,
    monete_migliori: int = 3,
) -> Dict[str, object]:
    """Le tre prove sugli estremi della Fase 4 di gruppo, tutte da superare (regole.md, sezione 6, punto 2.5).

    ``trade``: i trade sommati del candidato in costruzione (``TradeDiGruppo`` o
    oggetti con ``simbolo``, ``ts_entrata``, ``ts_uscita``, ``r``); si mettono
    nell'ordine di ``ordina_trade_di_gruppo``, quindi l'ordine d'arrivo non conta.
    ``b_gruppo``: B, il numero della (b) di gruppo (``baseline_casuale_di_gruppo``).
    ``b_per_moneta``: le b_j della stessa (b) (``b_per_moneta``), gia' calcolate:
    nessuna simulazione nuova. ``trade_migliori``, ``giorni_migliori`` e
    ``monete_migliori`` sono quelli di ``parametri.yaml`` (sezione ``gruppo``,
    ``fase4``: 30, 3 e 3).

    * ``senza_trade_migliori``: senza i 30 trade con l'R piu' alto, l'R medio dei
      trade rimasti supera B (strettamente);
    * ``senza_giorni_migliori``: senza tutti i trade USCITI nei 3 giorni UTC con la
      somma di R piu' alta, l'R medio dei rimasti supera la B ripesata sui trade
      rimasti;
    * ``senza_monete_migliori``: senza tutti i trade delle 3 monete con la somma di
      R piu' alta, l'R medio dei rimasti supera la B ripesata sulle monete rimaste.

    La B ripesata e' Σ r_j · b_j / Σ r_j, con r_j i trade rimasti della moneta j.
    Se non resta nessun trade la prova non e' superata. Le somme di R per giorno e
    per moneta sono esatte (``math.fsum``). A pari somma si toglie prima il giorno
    piu' vecchio e la moneta che viene prima in ordine dei caratteri (scelta
    documentata: il testo non lo dice; con R reali le parita' esatte sono rare).
    A pari R fra i trade migliori non serve una regola: l'R medio dei rimasti e'
    lo stesso qualunque trade si tolga.

    Ritorna le tre chiavi, ognuna con ``superata`` (bool), ``trade_tolti``,
    ``trade_rimasti``, ``r_medio`` (None senza trade rimasti) e la soglia (``b``
    per la prima, ``b_ripesata`` per le altre due, None senza trade rimasti); in
    piu' ``giorni_tolti`` (AAAA-MM-GG) e ``somme_r_giorni_tolti``,
    ``monete_tolte`` e ``somme_r_monete_tolte``; e ``tutte_superate``.
    """
    ordinati = ordina_trade_di_gruppo(trade)
    if not ordinati:
        raise ValueError("estremi_di_gruppo: servono i trade del candidato")
    r = _come_array([t.r for t in ordinati], "r")
    if not np.isfinite(r).all():
        raise ValueError("estremi_di_gruppo: R non finiti fra i trade")
    soglia_b = float(b_gruppo)
    if not math.isfinite(soglia_b):
        raise ValueError(f"b_gruppo non finita: {b_gruppo!r}")
    quanti: Dict[str, int] = {}
    for nome, valore in (("trade_migliori", trade_migliori), ("giorni_migliori", giorni_migliori),
                         ("monete_migliori", monete_migliori)):
        if isinstance(valore, bool) or operator.index(valore) < 0:
            raise ValueError(f"{nome} deve essere un intero non negativo")
        quanti[nome] = operator.index(valore)

    # Prova sui trade: via i trade con l'R piu' alto (a pari R, il primo nell'ordine fisso).
    migliori = set(sorted(range(len(ordinati)), key=lambda i: (-r[i], i))[:quanti["trade_migliori"]])
    rimasti = [t for i, t in enumerate(ordinati) if i not in migliori]
    r_medio = _r_medio(rimasti)
    senza_trade = {
        "superata": bool(r_medio is not None and r_medio > soglia_b),
        "trade_tolti": len(migliori),
        "trade_rimasti": len(rimasti),
        "r_medio": r_medio,
        "b": soglia_b,
    }

    # Prova sui giorni: via i trade usciti nei giorni UTC con la somma di R piu' alta.
    r_per_giorno: Dict[int, List[float]] = {}
    for t in ordinati:
        r_per_giorno.setdefault(_giorno_utc(t.ts_uscita), []).append(float(t.r))
    somme_giorni = {g: math.fsum(valori) for g, valori in r_per_giorno.items()}
    giorni_tolti = sorted(somme_giorni, key=lambda g: (-somme_giorni[g], g))[:quanti["giorni_migliori"]]
    via_giorni = set(giorni_tolti)
    rimasti = [t for t in ordinati if _giorno_utc(t.ts_uscita) not in via_giorni]
    r_medio = _r_medio(rimasti)
    b_ripesata = _b_ripesata(rimasti, b_per_moneta)
    senza_giorni = {
        "superata": bool(r_medio is not None and r_medio > b_ripesata),
        "giorni_tolti": [_data_del_giorno(g) for g in giorni_tolti],
        "somme_r_giorni_tolti": [somme_giorni[g] for g in giorni_tolti],
        "trade_tolti": len(ordinati) - len(rimasti),
        "trade_rimasti": len(rimasti),
        "r_medio": r_medio,
        "b_ripesata": b_ripesata,
    }

    # Prova sulle monete: via tutti i trade delle monete con la somma di R piu' alta.
    r_per_moneta: Dict[str, List[float]] = {}
    for t in ordinati:
        r_per_moneta.setdefault(t.simbolo, []).append(float(t.r))
    somme_monete = {s: math.fsum(valori) for s, valori in r_per_moneta.items()}
    monete_tolte = sorted(somme_monete, key=lambda s: (-somme_monete[s], s))[:quanti["monete_migliori"]]
    via_monete = set(monete_tolte)
    rimasti = [t for t in ordinati if t.simbolo not in via_monete]
    r_medio = _r_medio(rimasti)
    b_ripesata = _b_ripesata(rimasti, b_per_moneta)
    senza_monete = {
        "superata": bool(r_medio is not None and r_medio > b_ripesata),
        "monete_tolte": monete_tolte,
        "somme_r_monete_tolte": [somme_monete[s] for s in monete_tolte],
        "trade_tolti": len(ordinati) - len(rimasti),
        "trade_rimasti": len(rimasti),
        "r_medio": r_medio,
        "b_ripesata": b_ripesata,
    }
    return {
        "senza_trade_migliori": senza_trade,
        "senza_giorni_migliori": senza_giorni,
        "senza_monete_migliori": senza_monete,
        "tutte_superate": bool(senza_trade["superata"] and senza_giorni["superata"] and senza_monete["superata"]),
    }
