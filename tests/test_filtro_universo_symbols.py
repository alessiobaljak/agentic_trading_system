"""IL FILTRO MONETE DELL'AI NON TOCCA UN ELENCO SCELTO APPOSTA (30 set 2026).

Dal 29 set sera il filtro non viene piu' troncato e ha cominciato a escludere:
alle 06:10 UTC del 30 set, nella passata a 1 ora (che usa --symbols con 30 coin
scelte perche' hanno coppie validate), ne ha tolte 10 su 30 giudicandole dal solo
nome (ops 0365). Nel giro principale la riaggiunta delle coin in maturazione
rimedia; con --symbols no, e le coppie in corso su quelle coin si fermavano.

Si' del proprietario del 30 set: con --symbols il filtro non si chiama. Qui si
difende che con --symbols il filtro non parte e le coin restano tutte, che senza
--symbols parte come prima, e che `main` passa davvero da questa scelta.
"""
import inspect

from bot.ai import universe_filter
from bot.config import settings
from scripts import discover_strategies as d

#: le 10 coin tolte alla passata a 1 ora alle 06:10 UTC del 30 set (ops 0365)
TOLTE_30_SET = ["UBUSDT", "HEMIUSDT", "SKYAIUSDT", "MUBARAKUSDT", "BULLAUSDT",
                "SAHARAUSDT", "AVAAIUSDT", "USELESSUSDT", "HEIUSDT", "TRUMPUSDT"]
COIN_30 = TOLTE_30_SET + [f"C{i}USDT" for i in range(20)]


class _Spia:
    """Un filtro finto che ricorda se e con cosa e' stato chiamato."""

    def __init__(self, togli=()):
        self.chiamate: list = []
        self.togli = set(togli)

    def __call__(self, metrics):
        self.chiamate.append(list(metrics))
        simboli = [m["symbol"] for m in metrics]
        return ([s for s in simboli if s not in self.togli],
                {s: "listing recente" for s in simboli if s in self.togli})


def test_con_symbols_il_filtro_non_viene_chiamato_e_restano_tutte():
    spia = _Spia(togli=TOLTE_30_SET)
    tenute, escluse, applicato = d.filtra_universo(COIN_30, True, spia)
    assert spia.chiamate == []
    assert tenute == COIN_30
    assert escluse == {}
    assert applicato is False


def test_senza_symbols_il_filtro_viene_chiamato_come_prima():
    spia = _Spia(togli=TOLTE_30_SET)
    tenute, escluse, applicato = d.filtra_universo(COIN_30, False, spia)
    assert spia.chiamate == [[{"symbol": s} for s in COIN_30]]
    assert tenute == [s for s in COIN_30 if s not in TOLTE_30_SET]
    assert sorted(escluse) == sorted(TOLTE_30_SET)
    assert applicato is True


def test_la_lista_resa_e_una_copia():
    """Con --symbols la lista torna com'e', ma non e' la stessa lista: chi la
    allunga dopo (riaggiunte, intorno) non deve cambiare quella di chi chiama."""
    coin = ["BTCUSDT", "ETHUSDT"]
    tenute, _, _ = d.filtra_universo(coin, True, _Spia())
    tenute.append("SOLUSDT")
    assert coin == ["BTCUSDT", "ETHUSDT"]


def test_col_filtro_vero_e_una_risposta_che_toglie_10_su_30(monkeypatch):
    """Lo stesso caso del 30 set col filtro vero e l'AI finta: senza --symbols
    toglie le 10 coin (10 su 30 sta sotto la guardia del 50%), con --symbols
    l'AI non viene nemmeno interpellata (nessuna spesa) e restano tutte 30."""
    domande: list = []

    def finta(*a, **k):
        domande.append(k.get("label"))
        return {"escludi": [{"symbol": s, "motivo": "solo il nome"} for s in TOLTE_30_SET]}

    monkeypatch.setattr(settings, "AI_UNIVERSE_FILTER", True)
    monkeypatch.setattr(universe_filter, "available", lambda: True)
    monkeypatch.setattr(universe_filter, "ask_json", finta)

    tenute, escluse, applicato = d.filtra_universo(
        COIN_30, True, universe_filter.filter_universe)
    assert (tenute, escluse, applicato) == (COIN_30, {}, False)
    assert domande == []

    tenute, escluse, applicato = d.filtra_universo(
        COIN_30, False, universe_filter.filter_universe)
    assert len(tenute) == 20 and not set(tenute) & set(TOLTE_30_SET)
    assert sorted(escluse) == sorted(TOLTE_30_SET)
    assert applicato is True
    assert domande == ["ai-universe"]


def test_main_passa_dalla_scelta_con_symbols():
    """`main` non chiama piu' il filtro direttamente: passa da `filtra_universo`
    con «c'e' --symbols» come scelta, e lo dice nel log quando lo salta. Il
    filtro resta comunque PRIMA della riaggiunta delle coin in maturazione
    (lo difende anche `test_universe_rotation`)."""
    src = inspect.getsource(d.main)
    piatto = " ".join(src.split())      # a capo e rientri non contano
    assert "ai_filter_universe(" not in src
    assert ('filtra_universo( full_symbols, bool(getattr(args, "symbols", "")), '
            'ai_filter_universe)') in piatto
    assert "filtro AI dell'universo saltato: elenco scelto apposta" in src
    assert src.index("filtra_universo(") < src.index("coin_in_maturazione")
