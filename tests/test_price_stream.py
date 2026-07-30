"""PriceStream: accumulo del range, semantica di drenaggio, salute, parsing.

Si testa la LOGICA PURA (nessuna connessione): i messaggi vengono iniettati a mano
con _handle_raw / observe, esattamente come farebbe il WebSocket.
"""
import json
import time

from bot.config import settings
from bot.agents.price_stream import PriceStream


def _stream() -> PriceStream:
    return PriceStream(base_url="wss://example.invalid")


def _msg(symbol: str, price: str) -> str:
    return json.dumps({"stream": f"{symbol.lower()}@aggTrade",
                       "data": {"e": "aggTrade", "s": symbol, "p": price}})


# ---- accumulo del range --------------------------------------------------- #
def test_range_accumulates_high_and_low():
    st = _stream()
    for p in (100.0, 103.5, 99.0, 101.0):
        st.observe("BTCUSDT", p)
    assert st.take_range("BTCUSDT") == (103.5, 99.0)


def test_take_range_drains_so_ticks_do_not_overlap():
    """Il drenaggio e' il punto: ogni tick deve vedere la finestra [tick precedente,
    ora]. Se il range non si azzerasse, un picco vecchio riempirebbe TP per sempre."""
    st = _stream()
    st.observe("BTCUSDT", 110.0)
    assert st.take_range("BTCUSDT") == (110.0, 110.0)
    assert st.take_range("BTCUSDT") == (None, None)      # svuotato
    st.observe("BTCUSDT", 101.0)
    assert st.take_range("BTCUSDT") == (101.0, 101.0)    # solo il nuovo


def test_take_range_is_per_symbol():
    st = _stream()
    st.observe("BTCUSDT", 100.0)
    st.observe("ETHUSDT", 50.0)
    assert st.take_range("BTCUSDT") == (100.0, 100.0)
    assert st.take_range("ETHUSDT") == (50.0, 50.0)


def test_reset_drops_prices_seen_before_entry():
    """All'apertura di una posizione il range va buttato: i prezzi visti prima
    dell'ingresso non possono riempire i suoi TP."""
    st = _stream()
    st.observe("BTCUSDT", 999.0)
    st.reset("BTCUSDT")
    assert st.take_range("BTCUSDT") == (None, None)


def test_non_positive_prices_are_ignored():
    st = _stream()
    st.observe("BTCUSDT", 0.0)
    st.observe("BTCUSDT", -5.0)
    assert st.take_range("BTCUSDT") == (None, None)


# ---- parsing dei messaggi ------------------------------------------------- #
def test_handle_raw_parses_combined_stream_message():
    st = _stream()
    st._handle_raw(_msg("BTCUSDT", "123.45"))
    assert st.take_range("BTCUSDT") == (123.45, 123.45)


def test_handle_raw_accepts_bare_payload():
    """Anche lo stream singolo (senza wrapper 'data') deve funzionare."""
    st = _stream()
    st._handle_raw(json.dumps({"e": "aggTrade", "s": "ETHUSDT", "p": "50.5"}))
    assert st.take_range("ETHUSDT") == (50.5, 50.5)


def test_handle_raw_survives_garbage():
    """Un messaggio malformato non deve mai far cadere il thread di rete."""
    st = _stream()
    for bad in ("not json", "{}", '{"data": null}', '{"data": {"s": "X"}}',
                '{"data": {"s": "X", "p": "abc"}}'):
        st._handle_raw(bad)
    assert st.take_range("X") == (None, None)


def test_symbols_are_normalised_uppercase():
    st = _stream()
    st._handle_raw(json.dumps({"data": {"s": "btcusdt", "p": "10"}}))
    assert st.take_range("BTCUSDT") == (10.0, 10.0)


# ---- salute (decide se il bot usa lo stream o ripiega su REST) ------------ #
def test_not_healthy_without_thread_or_symbols():
    st = _stream()
    assert st.is_healthy() is False           # niente simboli, niente thread
    st.set_symbols(["BTCUSDT"])
    assert st.is_healthy() is False           # simboli ma thread non avviato


def test_not_healthy_when_messages_are_stale():
    """Connessione in piedi ma silenziosa da troppo tempo = non affidabile:
    meglio ripiegare sulle candele che fidarsi di dati vecchi."""
    st = PriceStream(base_url="wss://example.invalid", stale_after_s=5.0)
    st._symbols = {"BTCUSDT"}
    st._thread = type("T", (), {"is_alive": lambda self: True})()
    st.observe("BTCUSDT", 100.0)
    assert st.is_healthy() is True
    st._last_msg_ts = time.time() - 10.0      # ultimo messaggio 10s fa, soglia 5s
    assert st.is_healthy() is False


# ---- gestione dell'insieme dei simboli ----------------------------------- #
def test_set_symbols_bumps_generation_to_force_reconnect():
    """Cambiare i simboli deve far riconnettere con la nuova lista."""
    st = _stream()
    st.set_symbols(["btcusdt"])
    gen = st._generation
    st.set_symbols(["BTCUSDT", "ETHUSDT"])
    assert st._generation > gen
    assert st._symbols == {"BTCUSDT", "ETHUSDT"}


def test_set_symbols_is_noop_when_unchanged():
    """Nessun riconnesso inutile se l'insieme e' lo stesso (anche con case diverso)."""
    st = _stream()
    st.set_symbols(["BTCUSDT"])
    gen = st._generation
    st.set_symbols(["btcusdt"])
    assert st._generation == gen


def test_set_symbols_forgets_ranges_of_dropped_symbols():
    st = _stream()
    st.set_symbols(["BTCUSDT", "ETHUSDT"])
    st.observe("ETHUSDT", 50.0)
    st.set_symbols(["BTCUSDT"])               # ETH non piu' seguito
    assert st.take_range("ETHUSDT") == (None, None)


def test_stream_path_uses_configured_type_lowercase():
    st = _stream()
    assert st._stream_path({"BTCUSDT", "ETHUSDT"}) == \
        "/stream?streams=btcusdt@bookTicker/ethusdt@bookTicker"


def test_stream_path_follows_config_override(monkeypatch):
    monkeypatch.setattr(settings, "EXEC_STREAM_TYPE", "aggTrade")
    st = _stream()
    assert st._stream_path({"BTCUSDT"}) == "/stream?streams=btcusdt@aggTrade"


# ---- estrazione del prezzo per tipo di evento ----------------------------- #
def test_bookticker_uses_mid_price():
    """bookTicker -> MID (bid+ask)/2. Non il lato: lo spread e' gia' un costo a parte
    in bot/core/costs.py, prenderlo qui lo conteggerebbe due volte."""
    st = _stream()
    st._handle_raw(json.dumps({"data": {"e": "bookTicker", "s": "BTCUSDT",
                                        "b": "64003.80", "a": "64003.90"}}))
    hi, lo = st.take_range("BTCUSDT")
    assert hi == lo
    assert abs(hi - 64003.85) < 1e-6      # tolleranza: e' aritmetica in virgola mobile


def test_aggtrade_still_parsed_by_price_field():
    """Retrocompatibilita': dove gli stream di trade funzionano, si usa 'p'."""
    st = _stream()
    st._handle_raw(json.dumps({"data": {"e": "aggTrade", "s": "ETHUSDT", "p": "50.25"}}))
    assert st.take_range("ETHUSDT") == (50.25, 50.25)


def test_aggtrade_field_a_is_not_mistaken_for_ask():
    """TRAPPOLA: in aggTrade 'a' e' l'ID del trade, in bookTicker e' il prezzo ask.
    Discriminando su 'e' non si puo' confondere un id con un prezzo."""
    st = _stream()
    st._handle_raw(json.dumps({"data": {"e": "aggTrade", "s": "BTCUSDT",
                                        "a": 4025482234, "p": "63988.35"}}))
    assert st.take_range("BTCUSDT") == (63988.35, 63988.35)


def test_kline_uses_current_close():
    st = _stream()
    st._handle_raw(json.dumps({"data": {"e": "kline", "s": "BTCUSDT",
                                        "k": {"c": "100.5"}}}))
    assert st.take_range("BTCUSDT") == (100.5, 100.5)


def test_bookticker_without_both_sides_is_skipped_with_reason():
    st = _stream()
    st._handle_raw(json.dumps({"data": {"e": "bookTicker", "s": "BTCUSDT", "b": "10"}}))
    assert st.take_range("BTCUSDT") == (None, None)
    assert "bid/ask" in (st.stats()["last_skip"] or "")


def test_unknown_event_is_skipped_with_diagnostic():
    st = _stream()
    st._handle_raw(json.dumps({"data": {"e": "misteryEvent", "s": "BTCUSDT", "x": 1}}))
    assert st.take_range("BTCUSDT") == (None, None)
    skip = st.stats()["last_skip"] or ""
    assert "nessun prezzo riconoscibile" in skip and "misteryEvent" in skip


# ---- percorso ordinato (zigzag) ------------------------------------------- #
def _st_path(**kw) -> PriceStream:
    return PriceStream(base_url="wss://example.invalid",
                       min_move_frac=kw.get("min_move_frac", 0.0),
                       max_path_points=kw.get("max_path_points", 800))


def test_path_extends_monotone_run_without_adding_points():
    """Una salita continua e' UN solo movimento: si tiene l'estremo raggiunto, non
    ogni singolo trade (altrimenti la memoria crescerebbe senza motivo)."""
    st = _st_path()
    for p in (100.0, 100.5, 101.0, 103.0):
        st.observe("BTCUSDT", p)
    path, hi, lo, trunc = st.take("BTCUSDT")
    assert path == [100.0, 103.0]
    assert (hi, lo) == (103.0, 100.0)
    assert trunc is False


def test_path_records_reversals_in_order():
    """Ogni inversione e' un punto: la sequenza dei livelli attraversati e' preservata."""
    st = _st_path()
    for p in (100.0, 103.0, 97.0, 105.0):
        st.observe("BTCUSDT", p)
    path, _, _, _ = st.take("BTCUSDT")
    assert path == [100.0, 103.0, 97.0, 105.0]


def test_path_preserves_order_of_two_levels():
    """Il caso che conta: 100 -> 103 -> 97 e 100 -> 97 -> 103 devono restare DISTINTI
    (stesso range, ordine opposto -> esito del trade opposto)."""
    a, b = _st_path(), _st_path()
    for p in (100.0, 103.0, 97.0):
        a.observe("X", p)
    for p in (100.0, 97.0, 103.0):
        b.observe("X", p)
    assert a.take("X")[0] == [100.0, 103.0, 97.0]
    assert b.take("X")[0] == [100.0, 97.0, 103.0]


def test_micro_reversals_are_filtered_as_noise():
    """Il rimbalzo bid/ask (inversioni minuscole) non deve gonfiare il percorso."""
    st = _st_path(min_move_frac=0.001)         # 0.1%
    st.observe("BTCUSDT", 100.0)
    st.observe("BTCUSDT", 103.0)
    st.observe("BTCUSDT", 102.99)              # -0.01%: rumore, ignorato
    st.observe("BTCUSDT", 102.98)
    path, hi, lo, _ = st.take("BTCUSDT")
    assert path == [100.0, 103.0]
    assert lo == 100.0 and hi == 103.0         # il range vero non perde nulla


def test_second_point_always_recorded_to_establish_direction():
    """Con un solo punto non esiste ancora un verso: il secondo punto va SEMPRE
    registrato (e' lui a definire la direzione), filtro o non filtro."""
    st = _st_path(min_move_frac=0.5)           # filtro assurdo (50%)
    st.observe("BTCUSDT", 100.0)
    st.observe("BTCUSDT", 100.01)
    assert st.take("BTCUSDT")[0] == [100.0, 100.01]


def test_range_brackets_every_price_even_if_filtered_from_path():
    """RETE DI SICUREZZA. Un'inversione filtrata non entra nel percorso, ma resta
    COMPRESA nel range [lo, hi]: il controllo sull'aggregato la cogliera' comunque,
    quindi nessun livello attraversato puo' sfuggire del tutto."""
    st = _st_path(min_move_frac=0.05)          # filtro aggressivo (5%)
    for p in (100.0, 110.0, 105.0, 108.0):
        st.observe("BTCUSDT", p)
    path, hi, lo, _ = st.take("BTCUSDT")
    assert 105.0 not in path                   # scartata dal percorso...
    assert lo <= 105.0 <= hi                   # ...ma il range la comprende


def test_path_truncation_is_flagged():
    """Oltre il tetto di punti il percorso non cresce e lo segnala: la coda resta
    coperta dal range, ma il chiamante deve sapere che l'ordine non e' completo."""
    st = _st_path(max_path_points=4)
    for i in range(50):
        st.observe("BTCUSDT", 100.0 + (i % 2) * 5)   # oscilla -> tante inversioni
    path, hi, lo, trunc = st.take("BTCUSDT")
    assert len(path) <= 4
    assert trunc is True
    assert (hi, lo) == (105.0, 100.0)                # gli estremi restano corretti


def test_take_drains_the_path_too():
    st = _st_path()
    st.observe("BTCUSDT", 100.0)
    st.observe("BTCUSDT", 105.0)
    assert st.take("BTCUSDT")[0] == [100.0, 105.0]
    assert st.take("BTCUSDT") == ([], None, None, False)


def test_reset_clears_the_path():
    st = _st_path()
    st.observe("BTCUSDT", 100.0)
    st.observe("BTCUSDT", 105.0)
    st.reset("BTCUSDT")
    assert st.take("BTCUSDT") == ([], None, None, False)


# ---- REGRESSIONE: il filtro anti-rumore non deve cancellare attraversamenti - #
def test_default_config_preserves_small_reversals():
    """Con la config di DEFAULT una micro-inversione DEVE restare nel percorso.

    Il difetto originale: soglia 0.02% = $12.80 su BTC. Un tuffo di pochi dollari sotto
    uno stop a BREAK-EVEN (che sta esattamente all'entry) veniva cancellato, il replay
    non lo vedeva, proseguiva e incassava un TP mai raggiunto -> errore OTTIMISTA."""
    st = PriceStream(base_url="wss://x")          # nessun override: usa i default reali
    for p in (64000.0, 64010.0, 64008.0, 64020.0):  # inversione di soli 2 dollari
        st.observe("BTCUSDT", p)
    path, _, _, _ = st.take("BTCUSDT")
    assert path == [64000.0, 64010.0, 64008.0, 64020.0]


def test_default_config_keeps_break_even_dip_visible():
    """Scenario reale: stop a break-even a 64000, il prezzo lo perfora di 3$ e risale.
    Il percorso deve contenere il punto SOTTO il livello, altrimenti l'ordine e' perso."""
    st = PriceStream(base_url="wss://x")
    for p in (64050.0, 63997.0, 64900.0):
        st.observe("BTCUSDT", p)
    path, _, _, _ = st.take("BTCUSDT")
    assert min(path) == 63997.0                   # il tuffo sotto il BE e' visibile
    assert path.index(63997.0) < path.index(64900.0)   # e viene PRIMA del rally


def test_identical_consecutive_prices_are_deduplicated():
    """bookTicker ripete spesso lo stesso mid: nessun punto inutile."""
    st = PriceStream(base_url="wss://x")
    for p in (100.0, 100.0, 100.0):
        st.observe("X", p)
    assert st.take("X")[0] == [100.0]


def test_monotone_run_still_compresses_with_no_filter():
    """Anche senza filtro, una corsa in un solo verso resta 2 punti: la compressione
    che serve (memoria) non dipende dalla soglia."""
    st = PriceStream(base_url="wss://x")
    for p in (100.0, 101.0, 102.0, 103.0, 104.0):
        st.observe("X", p)
    assert st.take("X")[0] == [100.0, 104.0]
