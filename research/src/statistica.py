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
from datetime import datetime, timezone
from typing import Callable, Dict, List, Sequence, Tuple

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
        "media": float(arr.mean()),
        "errore_standard": float(arr.std(ddof=1) / math.sqrt(arr.size)),
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

    Ritorna ``media``, ``errore_standard``, ``n_trade``, ``n_blocchi`` e
    ``valutabile``: False se i blocchi interi sono meno di MINIMO_BLOCCHI; in
    quel caso l'errore e' infinito e nessun candidato puo' batterla nettamente
    (il giudizio prudente).
    """
    arr = _come_array(r_baseline, "r_baseline")
    b = int(lunghezza_blocco)
    if b < 1:
        raise ValueError("lunghezza_blocco deve essere almeno 1")
    if arr.size // b < MINIMO_BLOCCHI:
        return {"media": float(arr.mean()), "errore_standard": math.inf, "n_trade": int(arr.size),
                "n_blocchi": int(arr.size // b), "valutabile": False}
    errore, k = _errore_media_corretto(arr, b, n, seme)
    return {"media": float(arr.mean()), "errore_standard": errore, "n_trade": int(arr.size),
            "n_blocchi": int(k), "valutabile": True}


def _confronto(r_candidato, lunghezza_blocco, baseline_media, baseline_errore_standard, n, seme) -> Dict[str, object]:
    """Il calcolo comune di ``batte_nettamente`` e ``p_value_vs_baseline``."""
    from scipy.stats import t as student  # scipy e' fra le dipendenze del repo (requirements.txt)

    arr = _come_array(r_candidato, "r_candidato")
    base = float(baseline_media)
    errore_base = float(baseline_errore_standard)
    if math.isnan(base) or math.isinf(base) or math.isnan(errore_base) or errore_base < 0:
        raise ValueError("baseline_media deve essere un numero finito e baseline_errore_standard non negativo")
    b = int(lunghezza_blocco)
    if b < 1:
        raise ValueError("lunghezza_blocco deve essere almeno 1")
    differenza = float(arr.mean()) - base
    k = arr.size // b
    non_valutabile = {
        "differenza": differenza, "errore_standard": math.inf, "margine": math.inf, "soglia": math.inf,
        "gradi_liberta": max(0, k - 1), "netta": False, "t": -math.inf, "p_value": 1.0,
        "errore_candidato": math.inf, "n_blocchi": int(k), "valutabile": False,
    }
    if k < MINIMO_BLOCCHI or math.isinf(errore_base):
        return non_valutabile
    errore_c, _ = _errore_media_corretto(arr, b, n, seme)
    errore = math.sqrt(errore_c ** 2 + errore_base ** 2)
    if errore == 0.0:
        # nessun rumore stimabile (serie costante e baseline senza errore): un
        # errore 0 non e' una precisione infinita, e' una serie che non varia.
        return dict(non_valutabile, errore_candidato=0.0)
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
    }


def batte_nettamente(
    r_candidato: Sequence[float],
    lunghezza_blocco: int,
    baseline_media: float,
    baseline_errore_standard: float,
    n: int = 2000,
    seme: int = 0,
) -> Dict[str, object]:
    """La regola «nettamente» della sezione 8 dalla versione 4.4. Una sola lettura.

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
    return _confronto(r_candidato, lunghezza_blocco, baseline_media, baseline_errore_standard, n, seme)


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
) -> float:
    """p-value unilaterale dell'asticella (sezione 8, dalla versione 4.4).

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
    return float(_confronto(r_candidato, lunghezza_blocco, baseline_media, baseline_errore_standard, n, seme)["p_value"])


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
    log_conf = _log_configurazioni(ammessi, n_trade, distanza)
    if not np.isfinite(log_conf[0, n_trade]):
        massimo = int(np.flatnonzero(np.isfinite(log_conf[0]))[-1])
        raise ValueError(
            f"impossibile piazzare {n_trade} ingressi a distanza {distanza} "
            f"su {n_barre} barre con {int(ammessi.sum())} ammesse: ne entrano al massimo {massimo}"
        )
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
