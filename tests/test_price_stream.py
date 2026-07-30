"""PriceStream: accumulo del range, semantica di drenaggio, salute, parsing.

Si testa la LOGICA PURA (nessuna connessione): i messaggi vengono iniettati a mano
con _handle_raw / observe, esattamente come farebbe il WebSocket.
"""
import json
import time

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


def test_stream_path_is_lowercase_aggtrade_list():
    st = _stream()
    assert st._stream_path({"BTCUSDT", "ETHUSDT"}) == \
        "/stream?streams=btcusdt@aggTrade/ethusdt@aggTrade"
