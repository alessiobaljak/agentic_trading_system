"""LA CACHE DELLE CANDELE — il costo piu' grosso del GATE 1 era rete, non CPU.

La chiave della cache include la data di FINE. Le finestre di validazione cambiano
esattamente quella, quindi ogni finestra era un buco nella cache: quattro anni di
candele riscaricati per duecento coin, ogni volta. Su un timeframe da 15 minuti
sono circa centoquarantamila candele per coin — decine di migliaia di richieste
HTTP per passata, che nessun upgrade di CPU avrebbe accorciato di un secondo.

Due rimedi, testati qui:
  * RIUSO — una serie in cache piu' lunga di quella richiesta si TAGLIA;
  * ESTENSIONE — una piu' corta si allunga scaricando la sola coda mancante.

E soprattutto le condizioni in cui NON si deve fare: una cache corrotta non da'
errore, da' risultati di validazione sbagliati per settimane senza che nessuno se
ne accorga. Per questo ogni controllo qui sotto, fallendo, deve portare a
riscaricare — mai a proseguire con dati dubbi.
"""
import json
import os
from datetime import datetime, timedelta, timezone

import pytest

from backtesting import data_loader as dl
from bot.core.models import Candle


def _series(n: int, start: datetime, step_min: int = 15, px: float = 100.0):
    return [Candle(open_time=start + timedelta(minutes=step_min * i),
                   open=px, high=px + 1, low=px - 1, close=px, volume=10.0)
            for i in range(n)]


T0 = datetime(2024, 1, 1, tzinfo=timezone.utc)


# ---- il taglio: e' qui che un errore diventa look-ahead ------------------- #
def test_cut_is_strict_so_no_future_candle_survives():
    """Una sola candela oltre il confine farebbe vedere alla validazione un pezzo
    di futuro. Il confronto e' stretto: la candela che APRE sul confine e' gia'
    fuori."""
    s = _series(10, T0)
    cut = dl.cut_to(s, T0 + timedelta(minutes=45))
    assert len(cut) == 3
    assert all(c.open_time < T0 + timedelta(minutes=45) for c in cut)


def test_cut_of_everything_is_empty_not_an_error():
    assert dl.cut_to(_series(5, T0), T0) == []


# ---- l'unione: la coda vince sulla sovrapposizione ------------------------ #
def test_the_new_tail_replaces_the_overlap():
    """L'ultima candela di una serie scaricata 'fino a oggi' era ancora in
    formazione: tenerla congelerebbe per sempre un massimo parziale dentro i dati
    di validazione."""
    base = _series(5, T0, px=100.0)
    tail = _series(3, T0 + timedelta(minutes=60), px=200.0)   # riparte dalla 5a
    merged = dl._merge_candles(base, tail)
    assert len(merged) == 7
    assert merged[4].close == 200.0            # rimpiazzata dalla versione nuova


def test_merging_keeps_the_series_ordered():
    merged = dl._merge_candles(_series(5, T0), _series(5, T0 + timedelta(minutes=75)))
    assert all(a.open_time < b.open_time for a, b in zip(merged, merged[1:]))


def test_a_backwards_tail_is_refused():
    """Non monotona = cache inaffidabile. Meglio riscaricare che validare su una
    storia che non e' mai esistita."""
    base = _series(5, T0)
    bad = [Candle(open_time=T0 + timedelta(minutes=60), open=1, high=1, low=1,
                  close=1, volume=1),
           Candle(open_time=T0 + timedelta(minutes=30), open=1, high=1, low=1,
                  close=1, volume=1)]
    assert dl._merge_candles(base, bad) is None


def test_a_tail_with_a_different_timeframe_is_refused():
    """Unire 15m e 1h darebbe una serie che sembra buona e non lo e'."""
    base = _series(5, T0, step_min=15)
    tail = _series(3, T0 + timedelta(minutes=75), step_min=7)
    assert dl._merge_candles(base, tail) is None


def test_a_gap_is_tolerated_because_exchanges_have_outages():
    """Un buco e' un fatto del mondo (manutenzione dell'exchange); un passo
    incoerente col resto e' un difetto dei dati. I due casi non vanno confusi."""
    base = _series(5, T0, step_min=15)
    tail = _series(3, T0 + timedelta(minutes=150), step_min=15)   # salta 2 candele
    assert dl._merge_candles(base, tail) is not None


def test_merging_with_nothing_returns_what_there_was():
    base = _series(3, T0)
    assert dl._merge_candles(base, []) == base
    assert dl._merge_candles([], base) == base


# ---- il formato in cache porta con se' la FONTE -------------------------- #
def test_the_source_travels_with_the_series(tmp_path, monkeypatch):
    """Senza, un'estensione incrementale potrebbe allungare candele Binance con
    candele Bybit: prezzi diversi per lo stesso istante, e una storia che non e'
    mai esistita su nessun exchange."""
    monkeypatch.setattr(dl, "_CACHE_DIR", str(tmp_path))
    p = os.path.join(str(tmp_path), "X_15m_2024-01-01_2024-02-01.json")
    dl._cache_write(p, _series(3, T0), "binance")
    assert dl._cache_source(p) == "binance"
    assert len(dl._cache_read(p)) == 3


def test_the_old_bare_list_format_is_still_readable(tmp_path, monkeypatch):
    """I file gia' sul disco della VPS sono liste nude: se smettessero di leggersi,
    il primo run dopo l'aggiornamento riscaricherebbe tutto."""
    monkeypatch.setattr(dl, "_CACHE_DIR", str(tmp_path))
    p = os.path.join(str(tmp_path), "X_15m_2024-01-01_2024-02-01.json")
    with open(p, "w") as f:
        json.dump([[int(T0.timestamp() * 1000), 1, 2, 0.5, 1.5, 10]], f)
    assert len(dl._cache_read(p)) == 1
    assert dl._cache_source(p) == ""        # sconosciuta -> non si estende


def test_an_unknown_source_is_never_extended(tmp_path, monkeypatch):
    """Formato vecchio = fonte ignota. Riscaricare e' l'opzione sicura."""
    monkeypatch.setattr(dl, "_CACHE_DIR", str(tmp_path))
    p = os.path.join(str(tmp_path), "X_15m_2024-01-01_2024-02-01.json")
    with open(p, "w") as f:
        json.dump([[int(T0.timestamp() * 1000), 1, 2, 0.5, 1.5, 10]], f)
    assert dl._cache_source(p) == ""


# ---- trovare le serie riusabili ------------------------------------------ #
def test_reusable_files_are_found_newest_end_first(tmp_path, monkeypatch):
    monkeypatch.setattr(dl, "_CACHE_DIR", str(tmp_path))
    for e in ("2024-02-01", "2024-03-01", "2024-01-15"):
        dl._cache_write(os.path.join(str(tmp_path), f"X_15m_2024-01-01_{e}.json"),
                        _series(2, T0), "binance")
    ends = [e for e, _ in dl._reusable_cache("X", "15m", "2024-01-01")]
    assert ends == ["2024-03-01", "2024-02-01", "2024-01-15"]


def test_a_different_series_is_never_reused(tmp_path, monkeypatch):
    """Simbolo, timeframe e data di inizio diversi = serie diversa. Riusarla
    significherebbe validare una coin sui dati di un'altra."""
    monkeypatch.setattr(dl, "_CACHE_DIR", str(tmp_path))
    dl._cache_write(os.path.join(str(tmp_path), "Y_15m_2024-01-01_2024-02-01.json"),
                    _series(2, T0), "binance")
    dl._cache_write(os.path.join(str(tmp_path), "X_1h_2024-01-01_2024-02-01.json"),
                    _series(2, T0), "binance")
    dl._cache_write(os.path.join(str(tmp_path), "X_15m_2023-01-01_2024-02-01.json"),
                    _series(2, T0), "binance")
    assert dl._reusable_cache("X", "15m", "2024-01-01") == []


def test_only_one_file_per_series_survives(tmp_path, monkeypatch):
    """Ogni data di fine crea un file con l'INTERA storia dentro: senza pulizia il
    riuso della cache si pagherebbe in gigabyte di copie quasi identiche."""
    monkeypatch.setattr(dl, "_CACHE_DIR", str(tmp_path))
    keep = os.path.join(str(tmp_path), "X_15m_2024-01-01_2024-03-01.json")
    for e in ("2024-02-01", "2024-03-01", "2024-01-15"):
        dl._cache_write(os.path.join(str(tmp_path), f"X_15m_2024-01-01_{e}.json"),
                        _series(2, T0), "binance")
    dl._drop_older("X", "15m", "2024-01-01", keep)
    assert [e for e, _ in dl._reusable_cache("X", "15m", "2024-01-01")] == ["2024-03-01"]


# ---- il percorso completo ------------------------------------------------- #
def test_a_longer_cache_is_reused_without_touching_the_network(tmp_path, monkeypatch):
    """Il caso delle finestre di validazione: stessa serie, data di fine PRECEDENTE.
    Prima era un buco nella cache e quattro anni di download."""
    monkeypatch.setattr(dl, "_CACHE_DIR", str(tmp_path))
    monkeypatch.setattr(dl, "_PRUNED", True)
    long_series = _series(400, T0)                      # ~4 giorni di 15m
    dl._cache_write(os.path.join(str(tmp_path), "X_15m_2024-01-01_2024-01-05.json"),
                    long_series, "binance")

    def _boom(*a, **k):
        raise AssertionError("nessuna chiamata di rete deve partire")

    monkeypatch.setattr(dl, "_binance", _boom)
    monkeypatch.setattr(dl, "_bybit", _boom)
    monkeypatch.setattr(dl, "_okx", _boom)
    out = dl.load_candles("X", "15m", "2024-01-01", "2024-01-03", allow_synthetic=False)
    assert out and all(c.open_time < datetime(2024, 1, 3, tzinfo=timezone.utc)
                       for c in out)


def test_a_shorter_cache_is_extended_by_the_missing_tail_only(tmp_path, monkeypatch):
    """Il caso del run ogni 8 ore: serviva qualche candela nuova e si riscaricava
    l'intera storia."""
    monkeypatch.setattr(dl, "_CACHE_DIR", str(tmp_path))
    monkeypatch.setattr(dl, "_PRUNED", True)
    base = _series(200, T0)
    dl._cache_write(os.path.join(str(tmp_path), "X_15m_2024-01-01_2024-01-03.json"),
                    base, "binance")
    asked: list = []

    def _fake_binance(symbol, interval, start_ms, end_ms):
        asked.append(start_ms)
        first = datetime.fromtimestamp(start_ms / 1000, tz=timezone.utc)
        return _series(300, first)

    monkeypatch.setattr(dl, "_binance", _fake_binance)
    out = dl.load_candles("X", "15m", "2024-01-01", "2024-01-05", allow_synthetic=False)
    assert out is not None and len(out) > len(base)
    # ha chiesto SOLO dalla fine della cache in poi, non dall'inizio della storia
    assert asked and asked[0] > int(T0.timestamp() * 1000)


def test_an_exact_cache_hit_still_wins(tmp_path, monkeypatch):
    monkeypatch.setattr(dl, "_CACHE_DIR", str(tmp_path))
    monkeypatch.setattr(dl, "_PRUNED", True)
    dl._cache_write(os.path.join(str(tmp_path), "X_15m_2024-01-01_2024-01-03.json"),
                    _series(200, T0), "binance")

    def _boom(*a, **k):
        raise AssertionError("nessuna rete")

    monkeypatch.setattr(dl, "_binance", _boom)
    assert len(dl.load_candles("X", "15m", "2024-01-01", "2024-01-03",
                               allow_synthetic=False)) == 200
