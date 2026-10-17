"""LA SPESA AI, MISURATA E DIVISA PER RAGIONE (29 set 2026).

Il proprietario ha chiesto nel report del mattino «la spesa giornaliera di AI e
per quali ragioni». Fino a oggi c'era solo una stima ricostruita a mano dai log
(backlog D6), con un buco dichiarato: le risposte senza JSON si pagavano e non
lasciavano i token. Questi test difendono le proprieta' che rendono quel numero
credibile:

  * si conta OGNI risposta pagata, anche quella inutilizzabile o troncata;
  * la somma regge fra processi diversi (bot, discovery, runner della domenica);
  * la misura non puo' MAI far fallire la chiamata che misura (fail-open);
  * il report dice da dove viene il numero e cosa NON conta.

Nei test i modelli si chiamano «modello-a», «modello-b»: nessun nome vero.
"""
import contextlib
import inspect
import io
import pathlib
import re
import sys
import types
from datetime import datetime, timedelta, timezone

import pytest

from bot.ai import client as ai_client
from bot.ai import spesa
from bot.config import settings
from bot.core.firebase_client import FirebaseClient
from bot.core.tempo import fuso, giorno_locale

#: 29 set 2026, 10:00 italiane
_TS = datetime(2026, 9, 29, 8, 0, tzinfo=timezone.utc).timestamp()


def _cattura(fn) -> str:
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        fn()
    return buf.getvalue()


def _resp(testo="{}", n_in=100, n_out=50, stop="end_turn", modello="modello-a",
          cache_w=None, cache_r=None, blocchi=None):
    """Una risposta come la restituisce l'SDK: solo i campi che servono."""
    usage = types.SimpleNamespace(input_tokens=n_in, output_tokens=n_out,
                                  cache_creation_input_tokens=cache_w,
                                  cache_read_input_tokens=cache_r)
    content = blocchi if blocchi is not None else [
        types.SimpleNamespace(type="text", text=testo)]
    return types.SimpleNamespace(content=content, usage=usage, stop_reason=stop,
                                 model=modello)


def _anthropic_finto(monkeypatch, resp):
    """Un modulo `anthropic` finto: nessuna rete, nessun SDK necessario."""
    chiamate = []

    class _Messages:
        def create(self, **kw):
            chiamate.append(kw)
            return resp

    class _Client:
        def __init__(self, **kw):
            self.messages = _Messages()

    mod = types.ModuleType("anthropic")
    mod.Anthropic = _Client
    monkeypatch.setitem(sys.modules, "anthropic", mod)
    return chiamate


@pytest.fixture
def fb(monkeypatch):
    """Un client in memoria tutto nuovo, usato anche da `registra` senza `fb`."""
    client = FirebaseClient()
    assert not client.is_live
    monkeypatch.setattr(spesa, "get_firebase", lambda: client)
    return client


@pytest.fixture
def prezzi(monkeypatch):
    """I prezzi di default dichiarati, qualunque cosa ci sia nell'ambiente."""
    monkeypatch.setattr(settings, "AI_PREZZO_INGRESSO_MTOK", 5.0)
    monkeypatch.setattr(settings, "AI_PREZZO_USCITA_MTOK", 25.0)
    monkeypatch.setattr(settings, "AI_CACHE_SCRITTURA_MULT", 1.25)
    monkeypatch.setattr(settings, "AI_CACHE_LETTURA_MULT", 0.1)
    monkeypatch.setattr(settings, "ANTHROPIC_MODEL", "modello-a")
    # l'ombra accesa: una giornata intera deve averla (`ragioni_attese`)
    monkeypatch.setattr(settings, "AI_ENABLED", True)
    monkeypatch.setattr(settings, "AI_SHADOW_ENABLED", True)


# ---- FirebaseClient.incrementa --------------------------------------------- #
def test_incrementa_in_memoria_somma_foglia_per_foglia():
    fb = FirebaseClient()
    fb.incrementa("c", "d", {"a": {"x": 1, "y": {"z": 2}}, "n": 1},
                  imposta={"aggiornato_at": 10.0})
    fb.incrementa("c", "d", {"a": {"x": 3, "y": {"z": 5, "w": 1}}, "n": 1},
                  imposta={"aggiornato_at": 20.0})
    doc = fb.get_doc("c", "d")
    assert doc["a"] == {"x": 4, "y": {"z": 7, "w": 1}}
    assert doc["n"] == 2
    # `imposta` si scrive cosi' com'e': non si somma
    assert doc["aggiornato_at"] == 20.0


def test_incrementa_non_accetta_cio_che_non_e_un_numero():
    """Un testo o un booleano sommati darebbero un conto senza senso: si rifiuta
    subito (chi chiama la avvolge), e i valori da scrivere vanno in `imposta`."""
    fb = FirebaseClient()
    with pytest.raises(TypeError):
        fb.incrementa("c", "d", {"a": "testo"})
    with pytest.raises(TypeError):
        fb.incrementa("c", "d", {"a": True})
    with pytest.raises(TypeError):
        fb.incrementa("c", "d", {"": 1})


def test_incrementa_non_azzera_una_mappa_con_un_dizionario_vuoto():
    """Su Firestore un `{}` scritto con merge sostituisce la mappa: i conti del
    giorno sparirebbero. I sotto-dizionari vuoti non si mandano."""
    fb = FirebaseClient()
    fb.incrementa("c", "d", {"stop": {"end_turn": 2}})
    fb.incrementa("c", "d", {"stop": {}, "n": 1})
    assert fb.get_doc("c", "d")["stop"] == {"end_turn": 2}


def test_dal_vivo_e_una_scrittura_con_increment_e_zero_letture(monkeypatch):
    """Il percorso vero, senza rete: si guarda COSA viene mandato a Firestore.
    Deve essere un solo `set(merge=True)` con i numeri avvolti in Increment, e
    nessuna lettura (la quota gratuita delle letture e' gia' finita una volta)."""
    scritture = []

    class _Increment:
        def __init__(self, v):
            self.v = v

    _DEFAULT = object()     # come `gapic_v1.method.DEFAULT`: la politica di ritentare

    class _Doc:
        def set(self, dati, merge=False, retry=_DEFAULT, timeout=None):
            scritture.append((dati, merge, timeout, retry))

        def get(self, *a, **k):
            raise AssertionError("incrementa non deve leggere")

    class _Coll:
        def document(self, _id):
            return _Doc()

    class _Fs:
        def collection(self, _c):
            return _Coll()

    finto = types.ModuleType("firebase_admin")
    finto.firestore = types.SimpleNamespace(Increment=_Increment)
    monkeypatch.setitem(sys.modules, "firebase_admin", finto)
    monkeypatch.setitem(sys.modules, "firebase_admin.firestore", finto.firestore)

    fb = FirebaseClient()
    fb._live, fb._fs = True, _Fs()
    prima = fb.letture()["totale"]
    fb.incrementa("ai_spesa", "2026-09-29", {"ragioni": {"ai-shadow": {"n": 1, "out": 7}}},
                  imposta={"aggiornato_at": 5.0})
    assert len(scritture) == 1
    dati, merge, timeout, retry = scritture[0]
    assert merge is True and timeout
    # UN tentativo: niente ritentare di default (fino a 60 s nel ciclo di
    # trading) e niente doppio conteggio se la risposta di un commit riuscito
    # si perde (un Increment non e' idempotente)
    assert retry is None
    foglia = dati["ragioni"]["ai-shadow"]["out"]
    assert isinstance(foglia, _Increment) and foglia.v == 7
    assert dati["aggiornato_at"] == 5.0
    assert fb.letture()["totale"] == prima


# ---- registra -------------------------------------------------------------- #
def test_registra_somma_due_chiamate_e_due_etichette(fb):
    spesa.registra(_resp(n_in=100, n_out=50), "ai-shadow", now=_TS, fb=fb)
    spesa.registra(_resp(n_in=200, n_out=70), "ai-shadow", now=_TS, fb=fb)
    spesa.registra(_resp(n_in=10, n_out=2000, stop="max_tokens"), "ai-universe",
                   now=_TS, fb=fb)
    doc = fb.get_doc("ai_spesa", "2026-09-29")
    ombra = doc["ragioni"]["ai-shadow"]
    assert (ombra["n"], ombra["in"], ombra["out"]) == (2, 300, 120)
    assert ombra["stop"] == {"end_turn": 2}
    assert doc["ragioni"]["ai-universe"]["stop"] == {"max_tokens": 1}
    assert doc["modelli"] == {"modello-a": 3}
    assert doc["ore"] == {"10": 3}           # ora italiana, non UTC
    assert doc["aggiornato_at"] == _TS


def test_il_giorno_e_quello_italiano():
    """Alle 23:30 UTC in Italia e' gia' domani: la spesa va nel giorno che
    legge il proprietario."""
    ts = datetime(2026, 9, 28, 23, 30, tzinfo=timezone.utc).timestamp()
    fb = FirebaseClient()
    spesa.registra(_resp(), "ai-shadow", now=ts, fb=fb)
    assert fb.get_doc("ai_spesa", "2026-09-29") is not None
    assert fb.get_doc("ai_spesa", "2026-09-28") is None


def test_registra_non_solleva_mai_se_firebase_e_giu():
    class _Rotto:
        def incrementa(self, *a, **k):
            raise RuntimeError("quota finita")

    out = _cattura(lambda: spesa.registra(_resp(), "ai-shadow", fb=_Rotto()))
    assert "[ai-spesa] non registrata" in out and "quota finita" in out


def test_registra_regge_usage_e_cache_mancanti(fb):
    """I campi della cache arrivano None quando la cache non si usa (oggi mai);
    una risposta senza `usage` conta comunque come chiamata."""
    spesa.registra(_resp(cache_w=None, cache_r=None), "ai-shadow", now=_TS, fb=fb)
    senza = types.SimpleNamespace(content=[], usage=None, stop_reason=None, model=None)
    spesa.registra(senza, "ai-autopsia", now=_TS, fb=fb)
    doc = fb.get_doc("ai_spesa", "2026-09-29")
    assert doc["ragioni"]["ai-shadow"]["cache_w"] == 0
    assert doc["ragioni"]["ai-shadow"]["cache_r"] == 0
    aut = doc["ragioni"]["ai-autopsia"]
    assert (aut["n"], aut["in"], aut["out"]) == (1, 0, 0)
    assert aut["stop"] == {"?": 1} and doc["modelli"]["?"] == 1


# ---- ask_json: la risposta pagata si conta anche se inutilizzabile ---------- #
def test_ask_json_registra_anche_la_risposta_senza_json(monkeypatch, fb):
    """IL BUCO MISURATO. `ai-universe` falliva a ogni giro con «risposta senza
    JSON valido» e nel log non restava nemmeno quanto era costato. Ora la
    risposta si conta PRIMA di guardarne il testo, e il log dice token e
    troncamento."""
    monkeypatch.setattr(settings, "ANTHROPIC_API_KEY", "chiave-finta")
    monkeypatch.setattr(settings, "AI_ENABLED", True)
    _anthropic_finto(monkeypatch, _resp(testo='[{"symbol": "BTCUSDT", "tie',
                                        n_in=484, n_out=2000, stop="max_tokens"))
    righe = []
    out = _cattura(lambda: righe.append(
        ai_client.ask_json("s", "u", max_tokens=2000, label="ai-universe")))
    assert righe == [None]
    assert "484+2000 token" in out and "troncata" in out
    doc = fb.get_doc("ai_spesa", giorno_locale(__import__("time").time()))
    voce = doc["ragioni"]["ai-universe"]
    assert (voce["n"], voce["in"], voce["out"]) == (1, 484, 2000)
    assert voce["stop"] == {"max_tokens": 1}
    assert spesa.riepilogo(doc)[0]["troncate"] == 1


def test_ask_json_non_perde_la_risposta_se_la_misura_fallisce(monkeypatch):
    """FAIL-OPEN: Firebase giu' costa una riga di log, non la risposta."""
    class _Rotto:
        def incrementa(self, *a, **k):
            raise RuntimeError("giu'")

    monkeypatch.setattr(spesa, "get_firebase", lambda: _Rotto())
    monkeypatch.setattr(settings, "ANTHROPIC_API_KEY", "chiave-finta")
    monkeypatch.setattr(settings, "AI_ENABLED", True)
    _anthropic_finto(monkeypatch, _resp(testo='{"ok": 1}'))
    risposte = []
    out = _cattura(lambda: risposte.append(ai_client.ask_json("s", "u", label="ai-shadow")))
    assert risposte == [{"ok": 1}]
    assert "[ai-spesa] non registrata" in out


def test_ask_json_non_sostituisce_messages_create_con_un_involucro():
    """La registrazione e' una riga DOPO la chiamata vera: le intestazioni
    condivise restano visibili nel sorgente (test_chiave_workspace)."""
    src = inspect.getsource(ai_client.ask_json)
    assert "default_headers=_headers()" in src
    assert src.index("messages.create") < src.index("registra_spesa(resp, label)")
    assert src.index("registra_spesa(resp, label)") < src.index("_extract_json(")


# ---- il testo dai blocchi che ce l'hanno (ThinkingBlock) -------------------- #
def _con_ragionamento(testo):
    return [types.SimpleNamespace(type="thinking", thinking="ragiono..."),
            types.SimpleNamespace(type="text", text=testo)]


def test_testo_di_salta_i_blocchi_senza_testo():
    assert ai_client.testo_di(_resp(blocchi=_con_ragionamento(" ciao "))) == "ciao"
    assert ai_client.testo_di(types.SimpleNamespace(content=None)) == ""


def test_la_narrativa_della_domenica_regge_un_modello_che_ragiona(monkeypatch):
    """MISURATO sul runner GitHub del 27 set: «'ThinkingBlock' object has no
    attribute 'text'» — token pagati, narrativa persa, ogni domenica."""
    from bot.learning import learning_loop

    class _Domenica(datetime):
        @classmethod
        def now(cls, tz=None):
            return datetime(2026, 9, 27, 7, 15, tzinfo=timezone.utc)

    monkeypatch.setattr(learning_loop, "datetime", _Domenica)
    monkeypatch.setattr(settings, "ANTHROPIC_API_KEY", "chiave-finta")
    _anthropic_finto(monkeypatch, _resp(blocchi=_con_ragionamento("Settimana tranquilla.")))
    ll = learning_loop.LearningLoop.__new__(learning_loop.LearningLoop)
    ll.fb = FirebaseClient()
    report = types.SimpleNamespace(model_dump_json=lambda: "{}")
    assert ll._maybe_narrative(report) == "Settimana tranquilla."
    docs = ll.fb.query_collection("ai_spesa")
    assert docs and docs[0]["ragioni"]["ai-learning"]["n"] == 1


def test_la_narrativa_vuota_si_dice_e_non_si_salva(monkeypatch):
    from bot.learning import learning_loop

    class _Domenica(datetime):
        @classmethod
        def now(cls, tz=None):
            return datetime(2026, 9, 27, 7, 15, tzinfo=timezone.utc)

    monkeypatch.setattr(learning_loop, "datetime", _Domenica)
    monkeypatch.setattr(settings, "ANTHROPIC_API_KEY", "chiave-finta")
    solo_ragionamento = [types.SimpleNamespace(type="thinking", thinking="...")]
    _anthropic_finto(monkeypatch, _resp(blocchi=solo_ragionamento, stop="max_tokens"))
    ll = learning_loop.LearningLoop.__new__(learning_loop.LearningLoop)
    ll.fb = FirebaseClient()
    esito = []
    out = _cattura(lambda: esito.append(
        ll._maybe_narrative(types.SimpleNamespace(model_dump_json=lambda: "{}"))))
    assert esito == [None]
    assert "narrativa vuota" in out and "max_tokens" in out


def test_l_orchestratore_col_modello_regge_un_blocco_di_ragionamento(monkeypatch, fb):
    from bot.orchestrator import orchestrator as orch

    monkeypatch.setattr(orch, "build_user_message", lambda *a, **k: "x")
    monkeypatch.setattr(settings, "ANTHROPIC_API_KEY", "chiave-finta")
    _anthropic_finto(monkeypatch, _resp(blocchi=_con_ragionamento(
        '{"asset": "BTCUSDT", "strategy": "breakout", "direction": "long", '
        '"size_multiplier": 0.5, "confidence": 70}')))
    o = orch.Orchestrator.__new__(orch.Orchestrator)
    segnali = [{"symbol": "ETHUSDT", "strategy": "x", "direction": "long",
                "adjusted_confidence": 10, "confidence": 10}]
    d = o._decide_llm([], segnali, None, None, [], [])
    assert d is not None and d.asset == "BTCUSDT"   # non il ripiego deterministico
    doc = fb.query_collection("ai_spesa")[0]
    assert doc["ragioni"]["ai-orchestratore"]["n"] == 1


# ---- ogni punto che chiama il modello e' contato, con un perche' ------------ #
def test_le_prove_della_chiave_si_contano():
    from scripts import connectivity_check, verify_keys

    assert 'registra(resp, "ai-connettivita")' in inspect.getsource(
        connectivity_check.info_others)
    assert 'registra(r, "ai-verifica")' in inspect.getsource(verify_keys.check_anthropic)


def test_ogni_etichetta_usata_ha_un_perche():
    """Un'etichetta nuova senza frase uscirebbe nel report col nome tecnico: si
    vede subito qui invece che sul telefono del proprietario."""
    etichette = set()
    for f in list(pathlib.Path("bot").glob("**/*.py")) + list(pathlib.Path("scripts").glob("*.py")):
        testo = f.read_text(encoding="utf-8")
        etichette |= set(re.findall(r'label="(ai-[a-z-]+)"', testo))
        etichette |= set(re.findall(r'registra\(\w+, "(ai-[a-z-]+)"', testo))
    assert {"ai-shadow", "ai-hypotheses", "ai-universe", "ai-learning"} <= etichette
    assert etichette <= set(spesa.RAGIONI), etichette - set(spesa.RAGIONI)
    assert spesa.perche("ai-sconosciuta") == "ai-sconosciuta"


# ---- conti e testo del report ---------------------------------------------- #
def test_costo_usd_ai_prezzi_configurati(prezzi):
    assert spesa.costo_usd(1_000_000, 0) == pytest.approx(5.0)
    assert spesa.costo_usd(0, 1_000_000) == pytest.approx(25.0)
    assert spesa.costo_usd(0, 0, cache_w=1_000_000) == pytest.approx(6.25)
    assert spesa.costo_usd(0, 0, cache_r=1_000_000) == pytest.approx(0.5)
    # un giro di ipotesi dei log del 29 set (ops 0345): 2029 letti + 3020 scritti
    assert spesa.costo_usd(2029, 3020) == pytest.approx(0.0856, abs=1e-4)


def _voce(n, n_in, n_out, troncate=0):
    stop = {"end_turn": n - troncate}
    if troncate:
        stop["max_tokens"] = troncate
    return {"n": n, "in": n_in, "out": n_out, "cache_w": 0, "cache_r": 0, "stop": stop}


def test_righe_spesa_ieri_per_ragione_in_ordine_di_costo(prezzi):
    docs = {"2026-09-28": {"ragioni": {"ai-shadow": _voce(40, 32000, 19500),
                                       "ai-hypotheses": _voce(12, 23500, 41300)},
                           "modelli": {"modello-a": 52}, "ore": {"00": 5}},
            "2026-09-27": {"ragioni": {"ai-shadow": _voce(10, 8000, 5000)},
                           "ore": {"01": 2}}}
    righe = spesa.righe_spesa(docs, "2026-09-29", "2026-09-28", "08:05")
    testo = "\n".join(righe)
    assert "prezzo configurato 5/25 $ per milione" in righe[0]
    assert "console Anthropic" in righe[0]
    assert "ieri (28 set, giornata intera ora italiana): 1,80 $ in 52 chiamate" in testo
    i_ip = testo.index("(ai-hypotheses)")
    i_om = testo.index("(ai-shadow)")
    assert i_ip < i_om, "la ragione piu' cara viene prima"
    assert "idee di strategie nuove da far provare al gate (ai-hypotheses): 12 chiamate" in testo
    assert "% della spesa di ieri" in testo and "% del giorno" not in testo
    assert "oggi fino alle 08:05 ora italiana: nessuna chiamata registrata" in testo
    assert "media" in testo and "su 2 giorni con dati" in testo and "al mese" in testo
    assert "non contati" in testo and "@claude" in testo and "0,0002 $" in testo
    assert "⚠️" not in testo
    assert len(testo.encode("utf-8")) < 2048


def test_righe_spesa_avvisa_su_troncamenti_e_modello_diverso(prezzi):
    docs = {"2026-09-28": {"ragioni": {"ai-universe": _voce(8, 16000, 16000, troncate=8)},
                           "modelli": {"modello-a": 7, "modello-b": 1}},
            "2026-09-29": {"ragioni": {"ai-universe": _voce(2, 4000, 4000, troncate=2)},
                           "modelli": {"modello-a": 2}}}
    testo = "\n".join(spesa.righe_spesa(docs, "2026-09-29", "2026-09-28", "08:05"))
    assert "risposte tagliate a meta'" in testo
    assert ("filtro delle monete su cui cercare (ai-universe): ieri 8 su 8 · oggi 2 su 2 → "
            "pagate e buttate") in testo
    # documento senza modelli per ragione (scritto prima del 29 set sera): la
    # riga dice il modello, non puo' dire chi
    assert ("1 chiamata fra ieri e oggi ha usato il modello «modello-b» invece di quello "
            "della VPS «modello-a»") in testo
    assert "oggi fino alle 08:05 ora italiana: 0,12 $ in 2 chiamate" in testo


def test_una_versione_con_data_dello_stesso_modello_non_e_un_allarme(prezzi):
    docs = {"2026-09-28": {"ragioni": {"ai-shadow": _voce(1, 10, 10)},
                           "modelli": {"modello-a-20260901": 1}}}
    testo = "\n".join(spesa.righe_spesa(docs, "2026-09-29", "2026-09-28", "08:05"))
    assert "ha risposto anche" not in testo


def test_senza_dati_lo_dice_e_rimanda_alla_stima_D6(prezzi):
    testo = "\n".join(spesa.righe_spesa({}, "2026-09-29", "2026-09-28", "08:05"))
    assert "ieri (28 set): nessuna chiamata registrata" in testo
    assert "stima D6" in testo and "2,75 $" in testo


def test_il_primo_giorno_misurato_a_meta_non_entra_nella_media(prezzi):
    """Il contatore nasce a meta' giornata: quella mezza giornata, contata come
    intera, dimezzerebbe la media della prima settimana."""
    docs = {"2026-09-26": {},
            "2026-09-27": {"ragioni": {"ai-shadow": _voce(5, 1000, 1000)}, "ore": {"15": 5}},
            "2026-09-28": {"ragioni": {"ai-shadow": _voce(40, 40000, 40000)}, "ore": {"00": 40}}}
    testo = "\n".join(spesa.righe_spesa(docs, "2026-09-29", "2026-09-28", "08:05"))
    assert "su 1 giorno con dati" in testo
    assert "escluso 27 set: misurato solo in parte" in testo
    solo_ieri = {"2026-09-27": {}, "2026-09-28": docs["2026-09-27"]}
    testo = "\n".join(spesa.righe_spesa(solo_ieri, "2026-09-29", "2026-09-28", "08:05"))
    assert "giornata NON intera: prima chiamata contata alle 15" in testo


def test_un_giorno_senza_l_ombra_non_e_intero_ne_entra_nella_media(prezzi):
    """RILIEVO del 29 set. La ricerca conta dal primo pull dell'agente ops, il
    bot (l'ombra, ~0,80 $ al giorno per la D6) solo dopo il riavvio: nei giorni
    in mezzo il conto e' piu' basso di circa il 30% pur sembrando una giornata
    piena. Si dice, e quel giorno resta fuori dalla media."""
    docs = {"2026-09-27": {},
            "2026-09-28": {"ragioni": {"ai-hypotheses": _voce(16, 144000, 51000),
                                       "ai-autopsia": _voce(16, 176000, 18000)},
                           "ore": {"00": 2, "03": 4}}}
    testo = "\n".join(spesa.righe_spesa(docs, "2026-09-29", "2026-09-28", "08:05"))
    assert "giornata NON intera: manca l'ombra (ai-shadow)" in testo
    assert "riavviato col contatore" in testo
    assert "escluso 28 set: misurato solo in parte" in testo and "stima D6" in testo
    # ombra spenta per scelta: nessuna ragione attesa, il giorno e' intero
    testo = "\n".join(spesa.righe_spesa(docs, "2026-09-29", "2026-09-28", "08:05", attese=()))
    assert "giornata intera ora italiana" in testo and "manca l'ombra" not in testo


def test_il_giorno_parziale_resta_fuori_anche_una_settimana_dopo(prezzi):
    """RILIEVO del 29 set: col solo `oggi + 7` il piu' vecchio dei 7 non aveva il
    giorno prima fra quelli letti, e il primo giorno del contatore (nato alle
    15) entrava nella media del report di una settimana dopo (-10%)."""
    from datetime import date

    def doc(ora, n):
        return {"ragioni": {"ai-shadow": _voce(n, 10000 * n, 500 * n)}, "ore": {ora: n}}
    oggi = date(2026, 10, 6)
    giorni = [(oggi - timedelta(days=i)).isoformat() for i in range(9)]   # come stato_spesa
    docs = {g: ({} if g < "2026-09-29" else doc("15" if g == "2026-09-29" else "00",
                                                    10 if g == "2026-09-29" else 30))
            for g in giorni}
    testo = "\n".join(spesa.righe_spesa(docs, giorni[0], giorni[1], "08:00"))
    assert "escluso 29 set: misurato solo in parte" in testo
    assert "su 6 giorni con dati" in testo
    pieno = spesa.costo_usd(300000, 15000)
    assert f"media {spesa._usd(pieno)} al giorno" in testo


def test_troncate_apposta_non_sono_un_allarme(prezzi):
    """Le prove della chiave chiedono 5 token APPOSTA: finire lo spazio e' l'esito
    atteso. Il riassunto della domenica, se tagliato, resta (monco)."""
    docs = {"2026-09-28": {"ragioni": {"ai-connettivita": _voce(1, 8, 5, troncate=1),
                                       "ai-verifica": _voce(1, 8, 5, troncate=1)}}}
    testo = "\n".join(spesa.righe_spesa(docs, "2026-09-29", "2026-09-28", "08:05"))
    assert "tagliate a meta'" not in testo and "⚠️" not in testo
    docs = {"2026-09-28": {"ragioni": {"ai-learning": _voce(1, 3000, 400, troncate=1)}}}
    testo = "\n".join(spesa.righe_spesa(docs, "2026-09-29", "2026-09-28", "08:05"))
    assert "riassunto settimanale della domenica (ai-learning): ieri 1 su 1 → testo salvato ma monco" in testo


def test_stesso_modello_solo_a_meno_della_data():
    """RILIEVO del 29 set: il confronto per prefisso scambiava per lo stesso
    listino due modelli diversi della stessa famiglia."""
    assert spesa._stesso_modello("modello-a-20260901", "modello-a")
    assert spesa._stesso_modello("modello-a", "modello-a-20260901")
    assert spesa._stesso_modello("modello-a-latest", "modello-a")
    assert not spesa._stesso_modello("modello-a", "modello-a-8")
    assert not spesa._stesso_modello("modello-a-8", "modello-a")
    docs = {"2026-09-28": {"ragioni": {"ai-shadow": _voce(1, 10, 10)},
                           "modelli": {"modello-a": 1}}}
    testo = "\n".join(spesa.righe_spesa(docs, "2026-09-29", "2026-09-28", "08:05",
                                        modello_atteso="modello-a-8"))
    assert "«modello-a»" in testo and "«modello-a-8»" in testo


def test_il_modello_diverso_dice_chi_e_il_rimedio_giusto(prezzi, fb):
    """RILIEVO del 29 set. Il runner GitHub prende il modello dal segreto
    ANTHROPIC_MODEL: il rimedio e' quel segreto, NON i prezzi della VPS. Sotto
    1 centesimo non e' un allarme, solo una riga che lo dice."""
    ts = datetime(2026, 9, 28, 10, 0, tzinfo=timezone.utc).timestamp()
    spesa.registra(_resp(n_in=8, n_out=5, modello="modello-b", stop="max_tokens"),
                   "ai-connettivita", now=ts, fb=fb)
    spesa.registra(_resp(n_in=100, n_out=50), "ai-shadow", now=ts, fb=fb)
    doc = fb.get_doc("ai_spesa", "2026-09-28")
    assert doc["ragioni"]["ai-connettivita"]["modelli"] == {"modello-b": 1}
    assert doc["ragioni"]["ai-shadow"]["modelli"] == {"modello-a": 1}
    testo = "\n".join(spesa.righe_spesa({"2026-09-28": doc}, "2026-09-29", "2026-09-28", "08:05"))
    assert ("➖ 1 chiamata fra ieri e oggi per «prova di collegamento della chiave» "
            "(ai-connettivita, circa 0,0002 $) ha usato il modello «modello-b»") in testo
    assert "probabile runner GitHub: segreto ANTHROPIC_MODEL" in testo and "⚠️" not in testo
    # la domenica, piu' cara: ⚠️ col rimedio del runner
    domenica = {"ragioni": {"ai-learning": {**_voce(1, 30000, 400), "modelli": {"modello-b": 1}}}}
    testo = "\n".join(spesa.righe_spesa({"2026-09-28": domenica}, "2026-09-29", "2026-09-28", "08:05"))
    assert "⚠️ 1 chiamata fra ieri e oggi per «riassunto settimanale della domenica»" in testo
    assert "si imposta quel segreto, NON si cambiano i prezzi AI_PREZZO_*" in testo
    # sulla VPS: il rimedio sono i prezzi
    vps = {"ragioni": {"ai-shadow": {**_voce(40, 32000, 19500), "modelli": {"modello-b": 40}}}}
    testo = "\n".join(spesa.righe_spesa({"2026-09-28": vps}, "2026-09-29", "2026-09-28", "08:05"))
    assert "⚠️ 40 chiamate fra ieri e oggi per «ombra" in testo
    assert "vanno aggiornati i prezzi AI_PREZZO_* nel .env della VPS" in testo


# ---- scripts/ai_status.stato_spesa ----------------------------------------- #
class _Fb:
    """Come il finto di test_stato_ai: `get_doc(coll, doc)` senza parole chiave."""

    def __init__(self, docs=None):
        self.docs = docs or {}
        self.letti = []

    def get_doc(self, coll, doc):
        self.letti.append((coll, doc))
        return self.docs.get((coll, doc), {})


def test_stato_spesa_legge_nove_giorni_e_stampa_la_sezione(prezzi):
    from scripts import ai_status

    oggi = datetime.now(fuso()).date()
    ieri = (oggi - timedelta(days=1)).isoformat()
    fb = _Fb({("ai_spesa", ieri): {"ragioni": {"ai-shadow": _voce(40, 32000, 19500)},
                                   "modelli": {"modello-a": 40}, "ore": {"00": 40}}})
    out = _cattura(lambda: ai_status.stato_spesa(fb))
    # 9: oggi, i 7 della media e il giorno prima del piu' vecchio (solo per
    # giudicare se quello e' misurato per intero)
    assert len(fb.letti) == 9 and {c for c, _ in fb.letti} == {"ai_spesa"}
    assert fb.letti[0][1] == oggi.isoformat() and fb.letti[1][1] == ieri
    assert "SPESA AI" in out
    assert "ombra: cosa farebbe l'AI al posto del bot, solo misura (ai-shadow): 40 chiamate" in out


def test_stato_spesa_regge_firebase_giu():
    from scripts import ai_status

    class _Rotto:
        def get_doc(self, *a, **k):
            raise RuntimeError("giu'")

    out = _cattura(lambda: ai_status.stato_spesa(_Rotto()))
    assert "SPESA AI" in out and "nessuna chiamata registrata" in out


def test_la_sezione_sta_dopo_le_prove_e_prima_della_chiusura():
    from scripts import ai_status

    src = inspect.getsource(ai_status.main)
    assert src.index("stato_prove(fb)") < src.index("stato_spesa(fb)")
    assert src.index("stato_spesa(fb)") < src.rindex('print("=" * 62)')


def test_il_report_non_registra_il_proprio_ping():
    """ai_status e' di sola lettura (test_stato_ai): il suo ping non si conta,
    e la sezione lo dichiara invece di scriverlo. Vietate anche la scrittura
    arrivata con la spesa (`incrementa`) e `ask_json`, che ora registra."""
    from scripts import ai_status

    src = inspect.getsource(ai_status)
    for vietato in ("registra(", "registra_spesa", "incrementa(", "ask_json(",
                    "set_doc(", "set_rtdb("):
        assert vietato not in src, vietato


def _chiamate_al_modello(radice: pathlib.Path):
    """(file, funzione, registra?) per ogni funzione di bot/ e scripts/ che
    chiama `<...>.messages.create(...)`, letta dall'albero del sorgente (la
    chiamata puo' andare a capo: una ricerca di testo la perderebbe)."""
    import ast

    file = sorted(radice.glob("bot/**/*.py")) + sorted(radice.glob("scripts/*.py"))
    for f in file:
        albero = ast.parse(f.read_text(encoding="utf-8"))
        for fn in ast.walk(albero):
            if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            chiamate = [n for n in ast.walk(fn) if isinstance(n, ast.Call)]
            crea = any(isinstance(c.func, ast.Attribute) and c.func.attr == "create"
                       and isinstance(c.func.value, ast.Attribute) and c.func.value.attr == "messages"
                       for c in chiamate)
            if not crea:
                continue
            nomi = {getattr(c.func, "id", None) or getattr(c.func, "attr", None) for c in chiamate}
            yield (str(f.relative_to(radice)), fn.name,
                   any(str(n).startswith("registra") for n in nomi if n))


def test_ogni_chiamata_al_modello_passa_dal_conto():
    """RILIEVO del 29 set: «ogni chiamata finisce nel conto» era difeso punto per
    punto. Un `messages.create` nuovo senza `registra` nella stessa funzione
    farebbe sottostimare la spesa senza dirlo: qui si vede subito.
    UNICA ECCEZIONE dichiarata: il ping di `scripts/ai_status.prova_chiave`, che
    e' di sola lettura e lo dice nella sezione (~0,0002 $ al giorno)."""
    radice = pathlib.Path(__file__).resolve().parent.parent
    trovate = list(_chiamate_al_modello(radice))
    assert len(trovate) >= 5, trovate           # la ricerca vede davvero le chiamate
    senza = sorted(f"{f}:{fn}" for f, fn, ok in trovate if not ok)
    assert senza == ["scripts/ai_status.py:prova_chiave"], senza


# ---- nessun nome di modello nei file nuovi --------------------------------- #
def test_nessun_identificativo_di_modello_nei_file_nuovi():
    ago = "claude" + "-"
    for f in ("bot/ai/spesa.py", "tests/test_ai_spesa.py"):
        testo = pathlib.Path(f).read_text(encoding="utf-8").lower()
        assert ago not in testo, f


def test_filtro_monete_e_ombra_spenti_di_default():
    """30 set 2026, si' del proprietario: filtro monete AI e ombra AI spenti di
    default (bot/config.py); si riaccendono solo con l'env esplicito."""
    import importlib, os
    import bot.config as cfg
    assert 'os.getenv("AI_UNIVERSE_FILTER", "false")' in open(cfg.__file__).read()
    assert 'os.getenv("AI_SHADOW_ENABLED", "false")' in open(cfg.__file__).read()
