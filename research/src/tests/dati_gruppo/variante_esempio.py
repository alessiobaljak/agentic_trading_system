"""Una variante d'esempio per i test di ``research/src/gruppo.py``: il contratto della sua docstring, in pratica.

NON e' una strategia di nessuna campagna e non viene da nessuna fonte: serve solo a provare l'esecutore.

Regola (direzione ``p["direzione"]``, di norma «long»): alla chiusura della barra i, se la chiusura supera il
massimo degli high delle ``n`` barre prima (da i - n a i - 1) — per lo short: scende sotto il minimo dei low —
Segnale con stop a ``stop`` e target a ``target`` (frazioni della chiusura); uscita con «chiudi» dopo ``durata``
barre in posizione, se stop e target non sono scattati prima. Il massimo si aggiorna una barra alla volta (una
deque monotona), cosi' l'esempio gira veloce anche a 1 ora.

Le quattro funzioni del contratto: ``crea_variante``, ``crea_a`` (entra a ogni barra libera da i = n),
``crea_casuale`` (entra alle barre di ``ingressi``) e ``crea_segnale`` (il segnale senza la condizione: None
nel riscaldamento). Tutte ricevono ``ctx`` e ``p`` e non leggono file.

Solo per i test, in ``p``:

* ``sonda``: a ogni chiamata (anche alla creazione) chiede a ``ctx.btc_chiuse_entro`` e a
  ``ctx.funding_regolato_entro`` un istante lontanissimo nel futuro e conta in ``REGISTRO["sonde"]`` se vede
  qualcosa oltre la chiusura dell'ultima barra ricevuta (nella vista o nella lista sotto la vista);
* ``registra_ingressi``: ``crea_casuale`` aggiunge a ``REGISTRO["ingressi"]`` gli ingressi che riceve;
* ``a_ingressi_massimi``: la (a) entra al piu' tante volte (una (a) di pochi trade).
"""

import sys
import types
from collections import deque

from research.src.motore import Segnale


def _registro_condiviso():
    """Il registro dei test, FUORI dal modulo (vale nel processo in cui le funzioni girano).

    ``gruppo.py`` esegue il modulo della variante da capo per ogni pezzo di lavoro: un registro al livello del
    modulo nascerebbe vuoto a ogni moneta e i test non lo vedrebbero. Per questo sta in un modulo a parte in
    ``sys.modules``, comune a tutte le esecuzioni dello stesso processo. NON e' un esempio per la sessione: una
    variante non tiene stato fuori dalle sue istanze (contratto di ``gruppo.py``, punto 1); questo registro non
    cambia l'esito, lo osserva soltanto.
    """
    nome = "_registro_della_variante_esempio"
    contenitore = sys.modules.get(nome)
    if contenitore is None:
        contenitore = types.ModuleType(nome)
        contenitore.REGISTRO = {"ingressi": [], "sonde": {}}
        sys.modules[nome] = contenitore
        _azzera(contenitore.REGISTRO)
    return contenitore.REGISTRO


def _azzera(registro):
    registro["ingressi"].clear()
    registro["sonde"].clear()
    registro["sonde"].update({"chiamate": 0, "violazioni": 0, "non_vuote_btc": 0, "non_vuote_funding": 0,
                              "creazioni": 0, "creazioni_non_vuote": 0})


#: Cio' che le funzioni registrano quando ``p`` lo chiede (vale nel processo in cui girano).
REGISTRO = _registro_condiviso()
#: Un istante oltre ogni dato (anno 33658): chiederlo non deve mai mostrare il futuro.
LONTANO = 10 ** 15


def azzera_registro():
    _azzera(REGISTRO)


def _sonda(ctx, p, adesso):
    """Chiede il futuro al contesto e conta cosa vede (``adesso`` None: alla creazione)."""
    if not p.get("sonda"):
        return
    sonde = REGISTRO["sonde"]
    btc = ctx.btc_chiuse_entro(LONTANO)
    funding = ctx.funding_regolato_entro(LONTANO)
    if adesso is None:
        sonde["creazioni"] += 1
        if len(btc) or len(funding) or len(btc._base) or len(funding._base):
            sonde["creazioni_non_vuote"] += 1
        return
    sonde["chiamate"] += 1
    for vista, istante in ((btc, lambda c: c.close_ts), (funding, lambda f: f[0])):
        ultimi = []
        if len(vista):
            ultimi.append(istante(vista[-1]))
        if len(vista._base):
            ultimi.append(istante(vista._base[-1]))
        if any(x > adesso for x in ultimi):
            sonde["violazioni"] += 1
    if len(btc):
        sonde["non_vuote_btc"] += 1
    if len(funding):
        sonde["non_vuote_funding"] += 1
    # un istante passato da' solo cio' che era chiuso allora
    passato = ctx.btc_chiuse_entro(adesso - 3 * ctx.ms_per_barra)
    if len(passato) and passato[-1].close_ts > adesso - 3 * ctx.ms_per_barra:
        sonde["violazioni"] += 1


def _segnale(chiusura, p):
    if p.get("direzione", "long") == "long":
        return Segnale("long", stop=chiusura * (1 - p["stop"]), target=chiusura * (1 + p["target"]))
    return Segnale("short", stop=chiusura * (1 + p["stop"]), target=chiusura * (1 - p["target"]))


def _uscita(stato, i, posizione, durata):
    """L'uscita comune: «chiudi» dopo ``durata`` barre in posizione."""
    if stato["entrata"] is None:
        stato["entrata"] = i
    if i - stato["entrata"] >= durata - 1:
        return "chiudi"
    return None


def barre_di_rottura(candele, p):
    """Gli indici delle barre in cui la condizione d'ingresso vale (con o senza posizione): per i test di ``ingressi_placebo``."""
    n, lungo = int(p["n"]), p.get("direzione", "long") == "long"
    indici = []
    for i in range(n, len(candele)):
        finestra = candele[i - n:i]
        if lungo and candele[i].close > max(c.high for c in finestra):
            indici.append(i)
        if not lungo and candele[i].close < min(c.low for c in finestra):
            indici.append(i)
    return indici


def crea_variante(ctx, p):
    n, durata, lungo = int(p["n"]), int(p["durata"]), p.get("direzione", "long") == "long"
    _sonda(ctx, p, None)

    def crea():
        _sonda(ctx, p, None)
        estremi = deque()  # (indice, high o low), monotona: in testa l'estremo della finestra
        stato = {"entrata": None}

        def strategia(storia, posizione):
            i = len(storia) - 1
            barra = storia[-1]
            _sonda(ctx, p, barra.close_ts)
            while estremi and estremi[0][0] < i - n:
                estremi.popleft()
            riferimento = estremi[0][1] if (estremi and i >= n) else None
            valore = barra.high if lungo else barra.low
            while estremi and (estremi[-1][1] <= valore if lungo else estremi[-1][1] >= valore):
                estremi.pop()
            estremi.append((i, valore))
            if posizione is None:
                stato["entrata"] = None
                if riferimento is not None and (barra.close > riferimento if lungo else barra.close < riferimento):
                    return _segnale(barra.close, p)
                return None
            return _uscita(stato, i, posizione, durata)

        return strategia

    return crea


def crea_a(ctx, p):
    n, durata = int(p["n"]), int(p["durata"])
    massimo = p.get("a_ingressi_massimi")
    _sonda(ctx, p, None)

    def crea():
        _sonda(ctx, p, None)
        stato = {"entrata": None, "segnali": 0}

        def strategia(storia, posizione):
            i = len(storia) - 1
            _sonda(ctx, p, storia[-1].close_ts)
            if posizione is None:
                stato["entrata"] = None
                if i >= n and (massimo is None or stato["segnali"] < massimo):
                    stato["segnali"] += 1
                    return _segnale(storia[-1].close, p)
                return None
            return _uscita(stato, i, posizione, durata)

        return strategia

    return crea


def crea_casuale(ctx, p):
    durata = int(p["durata"])
    _sonda(ctx, p, None)

    def crea(ingressi):
        _sonda(ctx, p, None)
        if p.get("registra_ingressi"):
            REGISTRO["ingressi"].append(sorted(ingressi))
        stato = {"entrata": None}

        def strategia(storia, posizione):
            i = len(storia) - 1
            _sonda(ctx, p, storia[-1].close_ts)
            if posizione is None:
                stato["entrata"] = None
                if i in ingressi:
                    return _segnale(storia[-1].close, p)
                return None
            return _uscita(stato, i, posizione, durata)

        return strategia

    return crea


def crea_segnale(ctx, p):
    n = int(p["n"])
    _sonda(ctx, p, None)

    def crea():
        _sonda(ctx, p, None)

        def segnale(storia):
            _sonda(ctx, p, storia[-1].close_ts)
            if len(storia) - 1 < n:
                return None
            return _segnale(storia[-1].close, p)

        return segnale

    return crea
