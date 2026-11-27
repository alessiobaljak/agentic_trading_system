"""Le correzioni del 27 novembre 2026 dall'audit del 26 novembre: il ciclo del bot (bot/main.py), l'invio a Telegram
(bot/execution/notifier.py) e il monitor di GitHub (scripts/monitor.py).

* salute-3: con lo stato EMERGENCY il bot mandava un Telegram «EMERGENCY CLOSE, 0 posizioni» e tre scritture su Firebase a ogni
  giro (30-40 secondi); ora solo se chiude qualcosa o se l'emergenza e' nuova. `send` guarda la risposta di Telegram.
* ordini-7 e salute-2 (punto 1): l'ordine dei giri e' paper F5, conto vero, paper G1, demo, paper G11, paper G1 neutra, eventi.
* salute-4: con ops/gate_fermo e niente di aperto nel vecchio paper il vecchio sistema non gira piu'.
* salute-6 (il monitor): soglia del battito 900 secondi; il fermo e gli allarmi di demo e conto vero al posto di /risk_state.
"""
from __future__ import annotations

import time
import types

import pytest

from bot import main as bot_main
from bot.core.firebase_client import FirebaseClient
from bot.execution import notifier as notifier_mod
from bot.execution.notifier import TelegramNotifier
from bot.main import TradingBot
from scripts import monitor

NOW = 1_795_737_600.0          # 27 novembre 2026, 00:00 UTC
GIRI = ("paper_f5", "paper_g1", "paper_g11", "paper_g1n", "demo_g1", "conto_vero", "paper_eventi")
#: lo stato di oggi del vecchio sistema (audit, salute-3): EMERGENCY scritta, il pulsante gia' consumato
EMERGENZA_SCRITTA = {"/commands/bot_state": "emergency", "/commands/kill_switch": False}


# --------------------------------------------------------------------------- #
# aiuti                                                                         #
# --------------------------------------------------------------------------- #
class _Telegram:
    """Il notificatore finto: tiene i messaggi; `esito` e' quello che `send` risponde."""

    def __init__(self, esito: bool = True) -> None:
        self.messaggi: list[str] = []
        self.esito = esito

    def send(self, testo: str) -> bool:
        self.messaggi.append(testo)
        return self.esito

    def bot_offline(self) -> None:
        self.send("BOT OFFLINE")


class _Fb(FirebaseClient):
    """Firebase in memoria che tiene i percorsi scritti."""

    def __init__(self, valori: dict | None = None) -> None:
        super().__init__()
        for k, v in (valori or {}).items():
            super().set_rtdb(k, v)
        self.scritte: list[str] = []

    def set_rtdb(self, path, data):
        self.scritte.append(path)
        return super().set_rtdb(path, data)


def _executor(posizioni: dict | None = None, ordini: dict | None = None, chiusi: list | None = None):
    ex = types.SimpleNamespace(dry_run=True, open_positions=dict(posizioni or {}), ordini_limite=dict(ordini or {}))

    def force_close_all(prices, reason):
        out = list(chiusi or []) if ex.open_positions else []
        ex.open_positions.clear()
        ex.ordini_limite.clear()
        return out

    ex.force_close_all = force_close_all
    ex.pop_realized = lambda: []
    return ex


def _bot(fb, executor=None) -> TradingBot:
    """Un TradingBot senza costruttore (troppo pesante), con lo stato che __init__ gli da'."""
    b = TradingBot.__new__(TradingBot)
    b.fb = fb
    b.executor = executor or _executor()
    b.notifier = _Telegram()
    b.price = types.SimpleNamespace(get_mark_price=lambda s: 100.0, get_candles=lambda *a, **k: [])
    b.selected = {}
    b._log_closed = lambda t: None
    b._emergenza_annunciata, b._kill_switch_letto = True, False       # come dopo __init__
    b._vecchio_fermo_stampato, b._orario_vecchio_fermo_at = None, 0.0
    return b


def _ciclo(b: TradingBot, now: float) -> None:
    """Il ciclo di trading fino allo stato (le guardie di stream, Firebase e riconciliazione non fermano)."""
    b._stream_recovery_guard = lambda now: False
    b._firebase_guard = lambda now: 0.0
    b._apply_reconciliation = lambda: False
    b.trading_cycle(now)


EMERGENZA = ("/commands/kill_switch", "/commands/bot_state", "/bot_active")


def _scritture_emergenza(fb: _Fb) -> list[str]:
    return [p for p in fb.scritte if p in EMERGENZA]


# --------------------------------------------------------------------------- #
# 1. salute-3: l'emergenza annunciata una volta                                 #
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize("giro", ["trading_cycle", "vecchio_fermo"])
def test_emergenza_gia_scritta_e_niente_da_chiudere_nessun_messaggio(giro):
    """La prova dell'audit: tre giri senza posizioni davano 3 messaggi e 9 scritture. Ora nessuno dei due."""
    fb = _Fb(EMERGENZA_SCRITTA)
    b = _bot(fb)
    for k in range(3):
        if giro == "trading_cycle":
            _ciclo(b, NOW + 35 * k)
        else:
            b._giro_vecchio_fermo(NOW + 35 * k)
    assert b.notifier.messaggi == []
    assert _scritture_emergenza(fb) == []


def test_pulsante_stop_una_conferma_e_il_flag_si_consuma():
    """Il pulsante STOP della dashboard (KillSwitch.tsx) scrive /commands/kill_switch = true e aspetta che il bot lo rimetta a
    false: una conferma per ogni pressione, anche con l'emergenza gia' in corso e niente da chiudere."""
    fb = _Fb({"/commands/bot_state": "emergency", "/commands/kill_switch": True})
    b = _bot(fb)
    for k in range(3):
        _ciclo(b, NOW + 35 * k)
    assert len(b.notifier.messaggi) == 1 and "EMERGENCY CLOSE" in b.notifier.messaggi[0]
    assert fb.get_rtdb("/commands/kill_switch") is False
    assert fb.get_rtdb("/commands/bot_state") == "emergency" and fb.get_rtdb("/bot_active") is False
    assert _scritture_emergenza(fb) == list(EMERGENZA)
    fb.set_rtdb("/commands/kill_switch", True)        # premuto di nuovo
    for k in range(3, 6):
        b._giro_vecchio_fermo(NOW + 35 * k)
    assert len(b.notifier.messaggi) == 2 and fb.get_rtdb("/commands/kill_switch") is False


def test_emergenza_nuova_mentre_il_bot_gira_si_annuncia_una_volta():
    fb = _Fb({"/commands/bot_state": "normal", "/commands/kill_switch": False})
    b = _bot(fb)
    b.bot_state()                                     # stato normale visto: la prossima emergenza e' nuova
    fb.set_rtdb("/commands/bot_state", "emergency")   # scritta da fuori, senza il pulsante
    for k in range(4):
        b._giro_vecchio_fermo(NOW + 35 * k)
    assert len(b.notifier.messaggi) == 1


def test_con_posizioni_chiuse_il_messaggio_parte_sempre():
    chiuso = types.SimpleNamespace(symbol="XUSDT", pnl=-1.5)
    fb = _Fb(EMERGENZA_SCRITTA)
    b = _bot(fb, _executor(posizioni={"XUSDT": types.SimpleNamespace(entry_price=100.0)}, chiusi=[chiuso]))
    for _ in range(2):                                # come il ciclo: lo stato, poi la chiusura
        assert b.bot_state().value == "emergency"
        b._emergency_close()
    assert len(b.notifier.messaggi) == 1                # il secondo giro non ha piu' niente da chiudere: silenzio
    assert "1 posizioni chiuse" in b.notifier.messaggi[0] and "XUSDT -1.50" in b.notifier.messaggi[0]


def test_un_ordine_limite_annullato_conta_come_chiusura():
    fb = _Fb(EMERGENZA_SCRITTA)
    b = _bot(fb, _executor(ordini={"XUSDT": object()}))
    b._emergency_close()
    assert len(b.notifier.messaggi) == 1


# --------------------------------------------------------------------------- #
# 2. notifier.send: la risposta di Telegram                                     #
# --------------------------------------------------------------------------- #
TOKEN = "999999:TOKEN-DI-PROVA-NON-VERO"


class _Risposta:
    def __init__(self, ok: bool, codice: int, corpo=None, testo: str = "") -> None:
        self.ok, self.status_code, self._corpo, self.text = ok, codice, corpo, testo

    def json(self):
        if isinstance(self._corpo, Exception):
            raise self._corpo
        return self._corpo


def _notifier() -> TelegramNotifier:
    n = TelegramNotifier()
    n.token, n.chat_id = TOKEN, "42"
    return n


@pytest.mark.parametrize("codice,descrizione", [
    (400, "Bad Request: can't parse entities"),
    (403, "Forbidden: bot was blocked by the user"),
    (429, "Too Many Requests: retry after 5"),
])
def test_send_un_rifiuto_si_scrive_nel_log_e_torna_falso(monkeypatch, capsys, codice, descrizione):
    corpo = {"ok": False, "error_code": codice, "description": descrizione}
    if codice == 429:
        corpo["parameters"] = {"retry_after": 5}
    monkeypatch.setattr(notifier_mod.requests, "post", lambda *a, **k: _Risposta(False, codice, corpo))
    assert _notifier().send("ciao") is False
    out = capsys.readouterr().out
    assert f"HTTP {codice}" in out and descrizione in out and "rifiutato" in out
    if codice == 429:
        assert "riprovare fra 5 s" in out


def test_send_accettato_torna_vero_e_non_scrive_niente(monkeypatch, capsys):
    monkeypatch.setattr(notifier_mod.requests, "post", lambda *a, **k: _Risposta(True, 200, {"ok": True}))
    assert _notifier().send("ciao") is True
    assert capsys.readouterr().out == ""


def test_send_errore_di_rete_senza_token_nel_log(monkeypatch, capsys):
    def rotto(url, **k):
        raise ConnectionError(f"HTTPSConnectionPool(host='api.telegram.org', port=443): Max retries exceeded with url: "
                              f"{url.split('api.telegram.org')[1]}")
    monkeypatch.setattr(notifier_mod.requests, "post", rotto)
    assert _notifier().send("ciao") is False
    out = capsys.readouterr().out
    assert "invio fallito" in out and "Max retries" in out and TOKEN not in out and "<token>" in out

    def rotto_codificato(url, **k):                   # lo stesso indirizzo, con i due punti scritti come %3A
        raise ConnectionError(f"url: {url.replace(':', '%3A')}")
    monkeypatch.setattr(notifier_mod.requests, "post", rotto_codificato)
    assert _notifier().send("ciao") is False
    out = capsys.readouterr().out
    assert TOKEN.replace(":", "%3A") not in out and TOKEN.split(":")[1] not in out


def test_send_risposta_illeggibile_non_solleva(monkeypatch, capsys):
    monkeypatch.setattr(notifier_mod.requests, "post",
                        lambda *a, **k: _Risposta(False, 502, ValueError("non e' JSON"), testo=f"<html>{TOKEN}</html>"))
    assert _notifier().send("ciao") is False
    out = capsys.readouterr().out
    assert "HTTP 502" in out and TOKEN not in out

    class Strana:
        @property
        def ok(self):
            raise RuntimeError("rotta")
    monkeypatch.setattr(notifier_mod.requests, "post", lambda *a, **k: Strana())
    assert _notifier().send("ciao") is False
    assert "non leggibile" in capsys.readouterr().out


def test_send_spento_torna_falso(capsys):
    n = TelegramNotifier()
    n.token, n.chat_id = "", ""
    assert n.send("ciao") is False
    assert "[telegram:disabled]" in capsys.readouterr().out


# --------------------------------------------------------------------------- #
# 3. il giro: l'ordine dei conti e il vecchio sistema fermo                     #
# --------------------------------------------------------------------------- #
class _Giro:
    def __init__(self, nome: str, ordine: list) -> None:
        self.nome, self.ordine = nome, ordine

    def tick(self, now: float) -> None:
        self.ordine.append(self.nome)


VECCHIO = ("evaluate_pending_trailing", "valuta_pendenti", "_manutenzione_oraria", "_btc_inizio_paper", "refresh_weights",
           "load_weights", "load_params", "load_generated", "_ricarica_registro_se_cambiato", "refresh_regime", "maybe_scan",
           "trading_cycle")


def _bot_run(monkeypatch, fermo, posizioni: dict | None = None, valori: dict | None = None) -> TradingBot:
    """Un bot che fa girare `run` davvero, con i pezzi del vecchio sistema e i giri dei paper e dei conti finti."""
    monkeypatch.setattr(bot_main, "ricerca_ferma", fermo if callable(fermo) else (lambda: "fermo" if fermo else None),
                        raising=False)
    b = _bot(_Fb(valori), _executor(posizioni))
    b.reconciler = types.SimpleNamespace(start=lambda: False)
    b.stream = None
    b.ordine, b.chiamate = [], []
    for nome in GIRI:
        setattr(b, nome, _Giro(nome, b.ordine))

    def registra(nome):
        def f(*a, **k):
            b.chiamate.append(nome)
        return f
    for nome in ("_replay_unlogged", "reconcile_equity", "_publish_avvio", "_load_adapt_state"):
        setattr(b, nome, lambda *a, **k: None)
    b._load_selettore = registra("_load_selettore")
    for nome in ("evaluate_pending_trailing", "_manutenzione_oraria", "_btc_inizio_paper", "refresh_weights",
                 "_ricarica_registro_se_cambiato", "refresh_regime", "maybe_scan", "trading_cycle"):
        setattr(b, nome, registra(nome))
    b.adaptation = types.SimpleNamespace(load_weights=registra("load_weights"), load_params=registra("load_params"),
                                         load_generated=registra("load_generated"))
    monkeypatch.setattr(bot_main.rifiutati, "valuta_pendenti", registra("valuta_pendenti"))
    b._timeframes_in_uso = lambda: set()
    b.last_trailing_eval = b.last_orario = b.last_adapt_reload = b.last_regime = b.last_weight_refresh = 0.0
    b._decision_interval_s = 900
    b.regime = None
    b._closed_this_cycle = False
    b._errori_ciclo = []
    return b


def test_l_ordine_dei_giri_ogni_conto_subito_dopo_il_suo_paper(monkeypatch):
    """ordini-7: prima F5, G1, G11, G1 neutra, demo, conto vero, eventi (il demo aspettava G11 e G1 neutra, 9-14 minuti a
    mezzanotte)."""
    b = _bot_run(monkeypatch, fermo=True)
    TradingBot.run(b, max_iterations=1, sleep_s=0)
    assert b.ordine == ["paper_f5", "conto_vero", "paper_g1", "demo_g1", "paper_g11", "paper_g1n", "paper_eventi"]
    b = _bot_run(monkeypatch, fermo=False)            # lo stesso ordine con il vecchio sistema acceso
    TradingBot.run(b, max_iterations=1, sleep_s=0)
    assert b.ordine == ["paper_f5", "conto_vero", "paper_g1", "demo_g1", "paper_g11", "paper_g1n", "paper_eventi"]


def test_ogni_conto_legge_solo_la_decisione_del_paper_che_lo_precede():
    """Il conto vero esegue F5 (il file che il paper di F5 scrive, niente eventi), il demo esegue G1 (il file del paper di G1):
    nessuno dei due legge un file di G11, di G1 neutra o degli eventi del giro in corso."""
    from bot.portafoglio import conto_vero, demo_binance
    from bot.portafoglio.f5 import PaperF5, PaperG1, PaperG11, PaperG1N
    assert conto_vero.FILE_STRATEGIA == PaperF5.FILE_DI_SERIE and conto_vero.STRATEGIA == "F5"
    assert demo_binance.FILE_G1 == PaperG1.FILE_DI_SERIE
    assert conto_vero.ContoVeroG1.eventi_accesi(None) is False and conto_vero.ContoVeroG1.eventi_aperti(None) == {}
    for altro in (PaperG11.FILE_DI_SERIE, PaperG1N.FILE_DI_SERIE):
        assert altro not in (conto_vero.FILE_STRATEGIA, demo_binance.FILE_G1)


def test_vecchio_sistema_fermo_non_fa_girare_niente_del_vecchio(monkeypatch, capsys):
    """salute-4: con ops/gate_fermo niente regime, scansioni, verdetti, pesi, controllo, registro e ciclo di trading; paper,
    demo, conto vero, eventi e battito come prima, a ogni giro."""
    b = _bot_run(monkeypatch, fermo=True)
    TradingBot.run(b, max_iterations=2, sleep_s=0)
    assert b.chiamate == ["_load_selettore"]          # solo all'avvio, come prima
    assert b.ordine.count("demo_g1") == 2 and len(b.ordine) == 2 * len(GIRI)
    assert b.fb.scritte.count("/bot_status/heartbeat") == 2
    assert b.fb.get_rtdb("/bot_status/state") == "running" and b.fb.scritte.count("/bot_status/state") == 1   # una volta l'ora
    out = capsys.readouterr().out
    assert out.count("vecchio sistema FERMO") == 1 and out.count("letture ultime 24 h") == 1


def test_senza_gate_fermo_il_vecchio_giro_resta_quello_di_prima(monkeypatch):
    b = _bot_run(monkeypatch, fermo=False)
    TradingBot.run(b, max_iterations=1, sleep_s=0)
    assert b.chiamate == ["_load_selettore", *VECCHIO[:8], "_load_selettore", *VECCHIO[8:]]


def test_con_qualcosa_aperto_nel_vecchio_paper_il_vecchio_giro_continua(monkeypatch):
    """Una posizione del vecchio paper va gestita (stop, take profit): con gate_fermo il giro resta quello di prima."""
    b = _bot_run(monkeypatch, fermo=True, posizioni={"XUSDT": types.SimpleNamespace(entry_price=100.0)})
    TradingBot.run(b, max_iterations=1, sleep_s=0)
    assert "trading_cycle" in b.chiamate and "maybe_scan" in b.chiamate and "refresh_regime" in b.chiamate


def test_un_errore_nel_leggere_l_interruttore_fa_girare_il_vecchio_come_prima(monkeypatch):
    def rotto():
        raise OSError("disco")
    b = _bot_run(monkeypatch, fermo=rotto)
    TradingBot.run(b, max_iterations=1, sleep_s=0)
    assert "trading_cycle" in b.chiamate


def test_vecchio_fermo_il_pulsante_stop_resta_vivo_e_le_richieste_si_azzerano(monkeypatch):
    b = _bot_run(monkeypatch, fermo=True, valori={"/commands/bot_state": "emergency", "/commands/kill_switch": True,
                                                  "/commands/close_position": {"XUSDT": True}})
    TradingBot.run(b, max_iterations=3, sleep_s=0)
    emergenze = [m for m in b.notifier.messaggi if "EMERGENCY CLOSE" in m]
    assert len(emergenze) == 1 and b.fb.get_rtdb("/commands/kill_switch") is False
    assert not b.fb.get_rtdb("/commands/close_position")
    assert "trading_cycle" not in b.chiamate


# --------------------------------------------------------------------------- #
# 4. il monitor di GitHub                                                       #
# --------------------------------------------------------------------------- #
def _monitor(monkeypatch, valori: dict, esito: bool = True, fb: _Fb | None = None) -> tuple[_Fb, _Telegram]:
    fb = fb or _Fb(valori)
    tg = _Telegram(esito)
    monkeypatch.setattr(monitor, "get_firebase", lambda: fb)
    monkeypatch.setattr(monitor, "TelegramNotifier", lambda: tg)
    monitor.main()
    return fb, tg


def test_monitor_soglia_del_battito_900_secondi(monkeypatch):
    assert monitor.HEARTBEAT_MAX_AGE == 900
    _, tg = _monitor(monkeypatch, {"/bot_status/heartbeat": time.time() - 600})      # con 180 s era «BOT OFFLINE»
    assert tg.messaggi == []
    _, tg = _monitor(monkeypatch, {"/bot_status/heartbeat": time.time() - 1000})
    assert tg.messaggi == ["BOT OFFLINE"]


def test_monitor_non_guarda_piu_il_vecchio_risk_state(monkeypatch):
    _, tg = _monitor(monkeypatch, {"/bot_status/heartbeat": time.time() - 30, "/risk_state": {"daily_pnl_pct": -0.08}})
    assert tg.messaggi == []


def test_monitor_fermo_e_allarmi_una_volta_sola(monkeypatch):
    valori = {"/bot_status/heartbeat": time.time() - 30,
              "/demo_binance/fermo": {"motivo": "stop del conto a -35%", "ora": NOW - 3600, "chiuse": 4},
              "/demo_binance/allarmi/limiti_binance": {"ora": NOW - 60, "testo": "Binance limita le richieste <429>"},
              "/conto_vero/allarmi/creazione": {"ora": NOW - 120, "testo": "git non risponde"}}
    fb, tg = _monitor(monkeypatch, valori)
    assert len(tg.messaggi) == 3
    fermo = next(m for m in tg.messaggi if "FERMO" in m)
    assert "Demo FERMO" in fermo and "stop del conto a -35%" in fermo and "4 posizioni chiuse" in fermo
    assert any("&lt;429&gt;" in m for m in tg.messaggi)                    # il testo e' scappato per l'HTML di Telegram
    assert any("Allarme del conto vero" in m and "git non risponde" in m for m in tg.messaggi)
    # il giro dopo: gli stessi allarmi, anche riscritti con un'altra ora, non ripartono
    fb.set_rtdb("/demo_binance/allarmi/limiti_binance", {"ora": NOW, "testo": "Binance limita le richieste di nuovo"})
    _, tg = _monitor(monkeypatch, {}, fb=fb)
    assert tg.messaggi == []
    # l'allarme si spegne e si riaccende: riparte; un fermo nuovo (un'altra ora) riparte
    fb.set_rtdb("/demo_binance/allarmi/limiti_binance", None)
    _, tg = _monitor(monkeypatch, {}, fb=fb)
    assert tg.messaggi == [] and "demo_binance-allarmi-limiti_binance" not in fb.get_rtdb(monitor.NODO_AVVISATI)
    fb.set_rtdb("/demo_binance/allarmi/limiti_binance", {"ora": NOW, "testo": "ancora"})
    fb.set_rtdb("/demo_binance/fermo", {"motivo": "pulsante «chiudi tutto»", "ora": NOW - 10, "chiuse": 0})
    _, tg = _monitor(monkeypatch, {}, fb=fb)
    assert len(tg.messaggi) == 2


def test_monitor_un_invio_non_riuscito_si_riprova(monkeypatch):
    valori = {"/bot_status/heartbeat": time.time() - 30,
              "/demo_binance/allarme": {"ora": NOW, "testo": "fermo ma il conto non e' vuoto"}}
    fb, tg = _monitor(monkeypatch, valori, esito=False)
    assert len(tg.messaggi) == 1 and not fb.get_rtdb(monitor.NODO_AVVISATI)
    _, tg = _monitor(monkeypatch, {}, fb=fb)
    assert len(tg.messaggi) == 1 and fb.get_rtdb(monitor.NODO_AVVISATI) == {"demo_binance-allarme": "acceso"}


def test_monitor_non_rimanda_cio_che_il_bot_ha_gia_mandato(monkeypatch):
    """Dal 27 novembre il demo e il conto vero mandano i loro allarmi al telefono da se' e lo segnano con `telefono` nel nodo
    (bot/portafoglio/demo_binance.py): il monitor non li rimanda, ma manda quelli senza il segno (bot con il codice di prima)."""
    valori = {"/bot_status/heartbeat": time.time() - 30,
              "/demo_binance/fermo": {"motivo": "stop del conto a -35%", "ora": NOW - 3600, "telefono": NOW - 3590},
              "/demo_binance/allarme": {"ora": NOW, "testo": "fermo ma il conto non e' vuoto", "telefono": NOW - 3000},
              "/conto_vero/allarmi/ordini_vietati": {"ora": NOW, "testo": "versione non approvata", "telefono": NOW},
              "/demo_binance/allarmi/limiti_binance": {"ora": NOW, "testo": "Binance limita le richieste"}}
    fb, tg = _monitor(monkeypatch, valori)
    assert len(tg.messaggi) == 1 and "limiti binance" in tg.messaggi[0]
    assert set(fb.get_rtdb(monitor.NODO_AVVISATI)) == {"demo_binance-fermo", "demo_binance-allarme",
                                                       "conto_vero-allarmi-ordini_vietati", "demo_binance-allarmi-limiti_binance"}
    _, tg = _monitor(monkeypatch, {}, fb=fb)
    assert tg.messaggi == []


def test_monitor_in_manutenzione_non_manda_niente(monkeypatch):
    _, tg = _monitor(monkeypatch, {"/commands/maintenance": True, "/demo_binance/fermo": {"motivo": "x", "ora": NOW}})
    assert tg.messaggi == []


# --------------------------------------------------------------------------- #
# 5. revisione del 27 novembre 2026 (reviews/reports/2026-11-27-bot.md e         #
#    2026-11-27-stato_e_segreti-bis.md): il DRY_RUN del processo (218) e gli     #
#    allarmi che il bot tiene fuori dal telefono di proposito (212)              #
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize("dry", [True, False])
def test_218_vecchio_fermo_il_dry_run_del_processo_si_scrive_all_avvio_e_ogni_ora(monkeypatch, dry):
    """Con il vecchio sistema fermo `refresh_regime` non gira, e prima /bot_status/dry_run restava quello del processo di prima
    (la prova del revisore: tre giri con DRY_RUN falso, lo stato diceva ancora «DRY_RUN: True» senza avviso). Ora lo scrivono
    `_publish_avvio` a ogni avvio e il giro da fermo una volta l'ora, con il valore di settings.DRY_RUN (qui finto dal test: il
    bot non lo cambia mai)."""
    from scripts import state_snapshot
    prima = {"/bot_status/state": "running", "/bot_status/dry_run": not dry, "/bot_status/heartbeat": 1.0}
    b = _bot_run(monkeypatch, fermo=True, valori=prima)
    b._publish_avvio = types.MethodType(TradingBot._publish_avvio, b)          # quello vero (in _bot_run e' finto)
    b._avviato_at = NOW
    monkeypatch.setattr(bot_main, "pubblica_versione", lambda bot: None)
    monkeypatch.setattr(bot_main.settings, "DRY_RUN", dry, raising=False)
    TradingBot.run(b, max_iterations=3, sleep_s=0)
    assert b.chiamate == ["_load_selettore"]                                     # il vecchio sistema non ha girato
    assert b.fb.get_rtdb("/bot_status/dry_run") is dry
    assert b.fb.scritte.count("/bot_status/dry_run") == 2                        # all'avvio e al primo giro dell'ora
    assert b.fb.scritte.index("/bot_status/dry_run") < b.fb.scritte.index("/bot_status/avviato_at")
    riga = next(r for r in state_snapshot.sezione_del_bot(b.fb) if r.startswith("- DRY_RUN"))
    if dry:
        assert riga == "- DRY_RUN: True"
    else:
        assert riga.startswith("- DRY_RUN: False") and "non vero" in riga                # in cima allo stato, con l'avviso


def test_218_il_giro_da_fermo_riscrive_state_e_dry_run_una_volta_l_ora():
    fb = _Fb()
    b = _bot(fb)
    for k in range(5):                                                           # 0, 20, 40, 60, 80 minuti
        b._giro_vecchio_fermo(NOW + 1200 * k)
    assert fb.scritte.count("/bot_status/dry_run") == 2 == fb.scritte.count("/bot_status/state")
    assert fb.get_rtdb("/bot_status/dry_run") is bot_main.settings.DRY_RUN is True        # i test girano con DRY_RUN vero


def _nodi(fb: _Fb, valori: dict) -> None:
    for k, v in valori.items():
        fb.set_rtdb(k, v)


def test_212_monitor_non_manda_il_429_che_il_bot_tiene_solo_su_firebase(monkeypatch):
    """Il bot non manda al telefono il 429 di Binance (bot/portafoglio/demo_binance.py, salute-6): nemmeno il monitor. Il 418 senza
    `telefono` si' (bot con il codice di prima, o un blocco che il bot non ha mandato), e anche il nodo dei limiti senza codice."""
    fb = _Fb({"/demo_binance/allarmi/limiti_binance": {"ora": NOW, "testo": "Binance limita le richieste (protezioni)",
                                                       "riprende": NOW + 60, "codice": 429}})
    tg = _Telegram()
    for k in range(2):                                                           # a ogni giro: mai
        assert monitor.avvisa_allarmi(fb, tg, now=NOW + 900 * k) == 0
    assert tg.messaggi == [] and not fb.get_rtdb(monitor.NODO_AVVISATI)          # e non si segna fra gli avvisati
    fb.set_rtdb("/demo_binance/allarmi/limiti_binance", {"ora": NOW + 1800, "testo": "indirizzo bloccato da Binance (418)",
                                                         "codice": 418})
    assert monitor.avvisa_allarmi(fb, tg, now=NOW + 1800) == 1                    # lo stesso nodo diventato un 418: parte
    assert "bloccato" in tg.messaggi[0]
    fb2, tg2 = _Fb({"/conto_vero/allarmi/limiti_binance": {"ora": NOW, "testo": "limiti"}}), _Telegram()
    assert monitor.avvisa_allarmi(fb2, tg2, now=NOW) == 1                         # senza codice non si sa: parte
    fb3, tg3 = _Fb({"/demo_binance/allarmi/pesi": {"ora": NOW, "testo": "pesi", "codice": 429}}), _Telegram()
    assert monitor.avvisa_allarmi(fb3, tg3, now=NOW) == 1                         # il 429 vale solo per limiti_binance


def test_212_monitor_non_manda_cio_che_il_bot_salta_per_il_limite_di_uno_all_ora(monkeypatch):
    """Il bot manda lo stesso allarme al massimo una volta all'ora: un allarme che si spegne e si riaccende entro l'ora resta senza
    `telefono` di proposito. Il monitor che ha visto l'invio del bot non lo manda; dopo l'ora, o senza averlo visto, si'."""
    from bot.portafoglio import demo_binance
    assert monitor.STESSO_TIPO_S == demo_binance.AVVISO_STESSO_TIPO_S
    fb, tg = _Fb(), _Telegram()
    _nodi(fb, {"/demo_binance/allarmi/pesi": {"ora": NOW, "testo": "pesi fuori dai limiti", "telefono": NOW}})
    assert monitor.avvisa_allarmi(fb, tg, now=NOW + 60) == 0                      # mandato dal bot: si ricorda quando
    assert fb.get_rtdb(monitor.NODO_TELEFONO_DEL_BOT) == {"demo_binance-allarmi-pesi": NOW}
    fb.set_rtdb("/demo_binance/allarmi/pesi", None)                              # si spegne...
    assert monitor.avvisa_allarmi(fb, tg, now=NOW + 900) == 0
    assert not fb.get_rtdb(monitor.NODO_AVVISATI)
    fb.set_rtdb("/demo_binance/allarmi/pesi", {"ora": NOW + 1500, "testo": "pesi fuori dai limiti"})   # ...si riaccende entro l'ora
    assert monitor.avvisa_allarmi(fb, tg, now=NOW + 1800) == 0 and tg.messaggi == []
    assert fb.get_rtdb(monitor.NODO_AVVISATI) == {"demo_binance-allarmi-pesi": "acceso"}   # segnato come quelli del bot
    assert monitor.avvisa_allarmi(fb, tg, now=NOW + 7200) == 0                    # e non riparte ai giri dopo
    # spento e riacceso oltre l'ora dall'invio del bot: il bot l'avrebbe mandato; senza `telefono` lo manda il monitor
    fb.set_rtdb("/demo_binance/allarmi/pesi", None)
    monitor.avvisa_allarmi(fb, tg, now=NOW + 7300)
    fb.set_rtdb("/demo_binance/allarmi/pesi", {"ora": NOW + 7400, "testo": "pesi fuori dai limiti"})
    assert monitor.avvisa_allarmi(fb, tg, now=NOW + 7500) == 1
    # un fermo nuovo entro l'ora dal fermo mandato dal bot, senza `telefono`: non si manda
    fb.set_rtdb("/demo_binance/fermo", {"motivo": "stop sul conto", "ora": NOW, "telefono": NOW})
    monitor.avvisa_allarmi(fb, tg, now=NOW + 7600)
    fb.set_rtdb("/demo_binance/fermo", {"motivo": "stop sul conto", "ora": NOW + 1200})
    assert monitor.avvisa_allarmi(fb, tg, now=NOW + 7700) == 0 and len(tg.messaggi) == 1
    # la memoria degli invii del bot dura due giorni, poi esce
    assert set(fb.get_rtdb(monitor.NODO_TELEFONO_DEL_BOT)) == {"demo_binance-allarmi-pesi", "demo_binance-fermo"}
    fb.set_rtdb("/demo_binance/fermo", None)
    fb.set_rtdb("/demo_binance/allarmi/pesi", None)
    monitor.avvisa_allarmi(fb, tg, now=NOW + 3 * 86400)
    assert not fb.get_rtdb(monitor.NODO_TELEFONO_DEL_BOT)


def test_212_monitor_senza_aver_visto_l_invio_del_bot_manda():
    """Il limite: se l'allarme si e' acceso e spento fra due giri del monitor, il monitor non sa dell'invio del bot e manda quello
    riacceso (un messaggio in piu', dalla parte sicura)."""
    fb, tg = _Fb({"/demo_binance/allarmi/pesi": {"ora": NOW + 1500, "testo": "pesi fuori dai limiti"}}), _Telegram()
    assert monitor.avvisa_allarmi(fb, tg, now=NOW + 1800) == 1
