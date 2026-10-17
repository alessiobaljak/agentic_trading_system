"""CHI HA PASSATO IL GATE SI OPERA, ANCHE SE IL VOLUME E' CALATO.

Richiesta del proprietario, 17 settembre, in due parti:

  1. «e' importante che le coppie che iniziano il processo di validazione lo portino
     al termine, non importa se il volume scende»;
  2. «se superano il 3 passaggio, anche se il volume non e' nei nostri standard, il
     paper li deve operare».

Non e' una preferenza estetica: e' coerenza col disegno che il sistema dichiara da
se'. La liquidita' la gestisce il MODELLO DI COSTO (`bot/core/costs.py`), che allarga
lo spread sulle coin sottili; il gate valida ogni coppia CON quei costi dentro. Una
coppia validata ha gia' battuto lo spread della sua coin, tre volte, su dati che lo
includevano.

Scartarla poi in live per «spread troppo largo» vuol dire opporre due volte lo stesso
argomento, e soprattutto far divergere cio' che il gate valida da cio' che il bot
opera. E' la classe di problema piu' costosa di questo progetto — la stessa che ha
prodotto BIRBUSDT (PF 1,51 promesso, 0,16 vissuto).

IL PAVIMENTO CHE RESTA, ed e' l'unico onesto: senza snapshot (coin morta o
delistata) si salta comunque, perche' li' non c'e' un prezzo a cui eseguire. Un
volume basso e' un costo; un mercato che non esiste e' un'altra cosa.
"""
import time

from bot.agents.market_scanner import MarketScanner
from bot.core.models import AssetSnapshot
from scripts.optimize import coin_in_maturazione


def _snap(sym: str = "SOTTILEUSDT", vol: float = 1_000.0) -> AssetSnapshot:
    """Una coin validata ma diventata sottile: volume ben sotto ogni soglia."""
    return AssetSnapshot(symbol=sym, price=1.0, volume_24h=vol, funding_rate=0.0)


# --------------------------------------------------------------------------- #
# 1. Le esclusioni strutturali non valgono per una coppia validata             #
# --------------------------------------------------------------------------- #
def test_a_validated_coin_is_not_excluded_for_spread():
    """ATTENZIONE A COSA PROVA QUESTO TEST, perche' la prima versione provava il
    contrario di quel che credevo.

    Coi valori di default questa esclusione NON SCATTA MAI: il modello di costo si
    ferma a uno spread di 0,00080 e la soglia `ASSET_MAX_SPREAD` e' 0,001. Quindi
    scrivendo il caso di prova col default avrei ottenuto un test verde che non
    verificava niente — l'esclusione non c'era nemmeno prima della deroga.

    Per provare la deroga davvero bisogna abbassare la soglia sotto il pavimento del
    modello. Cosi' il test dice una cosa vera: SE un giorno qualcuno stringesse quel
    parametro (e' un `env`, puo' succedere), le coppie validate resterebbero
    comunque operabili.
    """
    from bot.config import settings

    sottile = _snap()
    originale = settings.ASSET_MAX_SPREAD
    settings.ASSET_MAX_SPREAD = 0.0005      # sotto il pavimento del modello (0.0008)
    try:
        assert any("spread" in r for r in MarketScanner.exclusions(sottile)), (
            "col parametro stretto una coin sottile DEVE essere esclusa, altrimenti "
            "il test non sta provando la deroga")
        assert not any("spread" in r
                       for r in MarketScanner.exclusions(sottile, validata=True))
    finally:
        settings.ASSET_MAX_SPREAD = originale


def test_with_default_settings_the_spread_exclusion_never_fires():
    """Il fatto in se', fissato perche' non si ripeta l'equivoco: con i default il
    modello di costo produce al massimo 0,00080 e la soglia e' 0,001. Chi legge
    `exclusions` e vede il controllo sullo spread puo' crederlo attivo; non lo e'.
    Se un giorno i due numeri si incrociassero, questo test lo dice."""
    from bot.config import settings
    from bot.core.costs import liquidity_spread

    peggiore = liquidity_spread(0.0)        # la fascia piu' sottile del modello
    assert peggiore <= settings.ASSET_MAX_SPREAD, (
        f"ora l'esclusione per spread MORDE (peggior caso {peggiore} > soglia "
        f"{settings.ASSET_MAX_SPREAD}): va deciso se e' voluto")


def test_being_validated_does_not_waive_the_other_exclusions():
    """Funding fuori fascia e quarantena dopo gli stop restano: non c'entrano con la
    liquidita', e nessuno ha chiesto di toglierle."""
    fuori = AssetSnapshot(symbol="AUSDT", price=1.0, volume_24h=5e8,
                          funding_rate=0.01)
    assert any("funding" in r
               for r in MarketScanner.exclusions(fuori, validata=True))
    buona = AssetSnapshot(symbol="AUSDT", price=1.0, volume_24h=5e8, funding_rate=0.0)
    assert any("quarantena" in r for r in MarketScanner.exclusions(
        buona, recent_stops=99, validata=True))


# --------------------------------------------------------------------------- #
# 2. Lo scan non scarta per volume le coin validate                            #
# --------------------------------------------------------------------------- #
def test_the_scan_keeps_a_validated_coin_below_the_volume_floor():
    """Il pavimento `SCAN_MIN_VOLUME_24H` esiste per tenere fuori la spazzatura
    appena quotata. Una coppia validata non e' spazzatura: ha passato il gate tre
    volte, e il gate le ha addebitato lo spread della sua fascia di volume."""
    import inspect
    src = inspect.getsource(MarketScanner.scan)
    assert "sempre_ammesse" in src
    # il salto per volume deve essere subordinato all'appartenenza alle ammesse
    i_filtro = src.index("< min_vol")
    coda = src[i_filtro:i_filtro + 300]
    assert "ammesse" in coda, (
        "il filtro sul volume non consulta le coin ammesse: una validata sottile "
        "verrebbe scartata prima ancora di essere valutata")


def test_the_dead_coin_floor_stays():
    """Un volume basso e' un COSTO; un mercato che non esiste e' un'altra cosa. Senza
    snapshot non c'e' un prezzo a cui eseguire, e un fill inventato renderebbe il
    risultato del paper una finzione — esattamente cio' che il paper esiste per non
    essere."""
    import inspect
    src = inspect.getsource(MarketScanner.scan)
    assert "if snap is None:" in src and "continue" in src


# --------------------------------------------------------------------------- #
# 3. Chi ha iniziato la validazione la porta a termine: nessun tetto            #
# --------------------------------------------------------------------------- #
def test_every_coin_that_started_validating_is_kept_by_default():
    """La prima versione aveva un tetto di 40, poi di 60 sulla coda a una conferma.
    Il proprietario ha chiesto due volte che chi INIZIA il percorso lo finisca: una
    coppia a una conferma ha iniziato. Il tetto resta un parametro, ma spento."""
    ora = time.time()
    pairs = {f"C{i}USDT|gen_{i}": {"symbol": f"C{i}USDT", "generated": True,
                                   "pass_count": 1, "last_passed_at": ora,
                                   "last_seen_at": ora}
             for i in range(300)}
    scelte, diag = coin_in_maturazione(pairs, ora)
    assert len(scelte) == 300
    assert diag["tagliate"] == 0


def test_the_cap_is_still_available_if_a_run_ever_needs_it():
    """Non e' stato rimosso, e' stato spento: se un giorno un giro non chiudesse piu'
    nei tempi, il parametro c'e' e taglia le ultime della coda — mai le vicine al
    traguardo."""
    ora = time.time()
    pairs = {f"U{i}USDT|gen_u{i}": {"symbol": f"U{i}USDT", "generated": True,
                                    "pass_count": 1, "last_passed_at": ora,
                                    "last_seen_at": ora} for i in range(100)}
    pairs.update({f"V{i}USDT|gen_v{i}": {"symbol": f"V{i}USDT", "generated": True,
                                         "pass_count": 2, "last_passed_at": ora,
                                         "last_seen_at": ora} for i in range(10)})
    scelte, diag = coin_in_maturazione(pairs, ora, max_coda=20)
    assert diag["intoccabili"] == 10
    assert diag["tagliate"] == 80
    assert len(scelte) == 30
