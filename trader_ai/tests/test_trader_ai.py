"""Test del trader AI (REGOLE.md, versione 3) con il modello finto: tetto di spesa, obiettivo del giorno, limiti, chiamata
ogni 15 minuti e a ogni chiusura, indicatori, messaggio, nessun dato dell'altra sessione."""
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from trader_ai.costi import Budget, costo_dollari, costo_massimo
from trader_ai.giro import decidi
from trader_ai.indicatori import atr, ema, riassunto, rsi
from trader_ai.limiti import Conto, Posizione, controlla, obiettivo_raggiunto
from trader_ai.messaggio import blocco_memoria, costruisci, taglia
from trader_ai.modello import Esito, ModelloFinto
from trader_ai.schema import Risposta
from trader_ai.sveglia import motivo

ORA = datetime(2026, 11, 24, 10, 0, tzinfo=timezone.utc)
P = 90000.0


def conto(**kw):
    base = dict(conto=1000.0, disponibile=1000.0, conto_mezzanotte=1000.0)
    base.update(kw)
    return Conto(**base)


def r(azione="aspetta", **kw):
    base = dict(approccio="t", cambio_approccio=False, diario="")
    base.update(kw)
    return Risposta(azione=azione, **base)


def aspetta():
    return Esito(r(), "ok", {"input_tokens": 6000, "output_tokens": 2000})


# --- tetto di spesa -------------------------------------------------------------------------------------------------

def test_costo_dai_token_dichiarati():
    assert costo_dollari({"input_tokens": 1_000_000}) == pytest.approx(4.0)
    assert costo_dollari({"output_tokens": 1_000_000}) == pytest.approx(20.0)
    assert costo_dollari({"cache_read_input_tokens": 1_000_000}) == pytest.approx(0.2)


def test_tetto_ferma_le_chiamate_fino_a_mezzanotte_utc(tmp_path):
    b = Budget(tmp_path / "spesa.json")
    chiamate = []

    def finto():
        chiamate.append(1)
        return Esito(r(), "ok", {"input_tokens": 200_000, "output_tokens": 20_000})  # 1,20 dollari

    for i in range(10):
        decidi(ORA + timedelta(minutes=15 * i), "t", b, conto(), P, finto, costo_massimo=1.25)
    assert len(chiamate) == 4 and b.speso(ORA) <= 5.0
    assert decidi(ORA + timedelta(hours=5), "t", b, conto(), P, finto, 1.25).stato == "tetto"
    domani = datetime(2026, 11, 25, 0, 0, tzinfo=timezone.utc)
    assert decidi(domani, "t", b, conto(), P, finto, 1.25).stato == "ok"


def test_il_tetto_non_si_sfora_mai_anche_con_chiamate_al_massimo(tmp_path):
    b = Budget(tmp_path / "s.json")
    caratteri = 30_000
    cm = costo_massimo(caratteri)
    massimo_vero = {"cache_creation_input_tokens": int(caratteri / 2), "output_tokens": 16000}
    assert costo_dollari(massimo_vero) <= cm + 1e-9
    for i in range(500):
        decidi(ORA + timedelta(minutes=i), "t", b, conto(), P, lambda: Esito(None, "fuori_schema", massimo_vero), cm)
    assert b.speso(ORA) <= 5.0 and b.rimasto(ORA) < cm


# --- obiettivo del giorno -------------------------------------------------------------------------------------------

def test_obiettivo_del_3_per_cento_chiude_e_non_chiama(tmp_path):
    assert not obiettivo_raggiunto(conto(conto=1029.99))
    assert obiettivo_raggiunto(conto(conto=1030.0))
    assert not obiettivo_raggiunto(conto(conto=1059.0, conto_mezzanotte=1040.0))   # il 3% di 1.040 è 31,20
    chiamato = []
    ris = decidi(ORA, "t", Budget(tmp_path / "s.json"), conto(conto=1050.0), P, lambda: chiamato.append(1), 0.5)
    assert ris.stato == "obiettivo" and not chiamato


def test_nessuna_perdita_massima_si_continua_anche_in_forte_perdita(tmp_path):
    ris = decidi(ORA, "t", Budget(tmp_path / "s.json"), conto(conto=300.0, disponibile=300.0), P, aspetta, 0.5)
    assert ris.stato == "ok"


# --- limiti ---------------------------------------------------------------------------------------------------------

@pytest.mark.parametrize("dec, parola", [
    (r("apri_lungo", margine_usdt=100, leva=11, stop_prezzo=P * 0.99), "leva"),
    (r("apri_lungo", margine_usdt=100, leva=5), "manca lo stop"),
    (r("apri_lungo", margine_usdt=100, leva=5, stop_prezzo=P * 1.01), "parte sbagliata"),
    (r("apri_corto", margine_usdt=100, leva=5, stop_prezzo=P * 0.99), "parte sbagliata"),
    (r("apri_lungo", margine_usdt=100, leva=10, stop_prezzo=P * 0.90), "liquidazione"),
    (r("apri_lungo", margine_usdt=2000, leva=2, stop_prezzo=P * 0.99), "disponibile"),
    (r("apri_lungo", margine_usdt=5, leva=2, stop_prezzo=P * 0.99), "minimo"),
    (r("apri_lungo", margine_usdt=100, leva=2, stop_prezzo=P * 0.99, obiettivo_prezzo=P * 0.98), "obiettivo"),
    (r("chiudi"), "nessuna operazione"),
    (r("modifica", stop_prezzo=P * 0.99), "nessuna operazione"),
])
def test_decisioni_fuori_regola_scartate(dec, parola):
    assert parola in controlla(dec, conto(), P)


def test_aperture_valide_e_una_sola_operazione():
    ok = r("apri_lungo", margine_usdt=1000, leva=10, stop_prezzo=P * 0.95, obiettivo_prezzo=P * 1.02)
    assert controlla(ok, conto(), P) is None
    pos = Posizione("lungo", 0.1, 89000, 10, 85000, liquidazione=81000)
    assert "già un'operazione" in controlla(ok, conto(posizione=pos), P)
    assert controlla(r("modifica", stop_prezzo=88000), conto(posizione=pos), P) is None
    assert "liquidazione" in controlla(r("modifica", stop_prezzo=80000), conto(posizione=pos), P)
    assert controlla(r("chiudi"), conto(posizione=pos), P) is None


def test_modello_finto_non_passa_mai_fuori_regola():
    finto = ModelloFinto(seme=3)
    for i in range(500):
        dec = finto.chiama(P, ha_posizione=False).risposta
        if controlla(dec, conto(), P) is None and dec.azione.startswith("apri"):
            assert 1 <= dec.leva <= 10 and dec.margine_usdt <= 1000 and dec.margine_usdt * dec.leva >= 100
            assert abs(P - dec.stop_prezzo) / P <= 0.9 / dec.leva


def test_decisione_scartata_nessuna_operazione_e_diario(tmp_path):
    finto = lambda: Esito(r("apri_lungo", margine_usdt=100, leva=50, stop_prezzo=P * 0.99), "ok", {"input_tokens": 10})
    ris = decidi(ORA, "t", Budget(tmp_path / "s.json"), conto(), P, finto, 0.5, tmp_path / "d.jsonl")
    assert ris.accettata is None and "leva" in ris.scarto
    assert '"scarto"' in (tmp_path / "d.jsonl").read_text()


# --- quando chiamare ------------------------------------------------------------------------------------------------

def test_chiamata_a_ogni_candela_da_15_minuti_e_a_ogni_chiusura():
    t0 = ORA + timedelta(minutes=1)                                  # 10:01
    assert motivo(t0, None) == "primo avvio"
    assert motivo(ORA + timedelta(minutes=14), t0) is None           # 10:14, stessa candela
    assert motivo(ORA + timedelta(minutes=15), t0) == "candela da 15 minuti chiusa"
    assert motivo(ORA + timedelta(minutes=3), t0, "stop").startswith("operazione chiusa")


# --- indicatori e messaggio -----------------------------------------------------------------------------------------

def _candele(n, passo=5):
    out = []
    for i in range(n):
        c = 100 + i * 0.5 + (i % 3)
        out.append({"apertura": c - 0.2, "massimo": c + 1, "minimo": c - 1, "chiusura": c, "volume": 10 + i % 5,
                    "chiusa": ORA - timedelta(minutes=passo * (n - i))})
    return out


def test_indicatori_ragionevoli():
    assert ema([1, 1, 1], 3) == [1, 1, 1]
    assert rsi(list(range(30))) == 100.0
    assert rsi([10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0, -1, -2, -3, -4, -5]) == pytest.approx(0.0)
    c = _candele(100)
    assert 1.5 < atr(c) < 3.5
    ind = riassunto(c)
    assert ind["bollinger_bassa"] < ind["bollinger_media"] < ind["bollinger_alta"]
    assert ind["rsi14"] > 50 and ind["vwap_giorno"] is not None


def test_nessuna_candela_dopo_l_ora_della_chiamata():
    c = _candele(10) + [{"apertura": 1, "massimo": 1, "minimo": 1, "chiusura": 777777.0, "volume": 1,
                         "chiusa": ORA + timedelta(minutes=5)}]
    assert len(taglia(c, ORA)) == 10
    _, utente = costruisci(ORA, "t", 4.0, "BTCUSDT", {"5m": c}, {"prezzo": 100.0}, conto(), "m")
    assert "777777" not in utente


def test_messaggio_dice_obiettivo_memoria_e_scarto():
    mem = blocco_memoria([{"aperta": "11-24 09:00", "lato": "lungo", "leva": 5, "entrata": 90000, "uscita": 89500,
                           "come": "stop", "risultato": -27.8, "approccio": "rottura"}], "rottura", ["nota"], "leva 50")
    system, utente = costruisci(ORA, "candela", 4.2, "BTCUSDT", {"5m": _candele(60), "15m": _candele(60, 15),
                                "30m": _candele(60, 30)}, {"prezzo": 130.0, "funding": 0.0001}, conto(conto=1020), mem)
    assert "3%" in system and "adatti" in system
    assert "mancano 10.00" in utente and "SCARTATA" in utente and "rottura" in utente and "4.20 dollari" in utente
    assert all(f"candele {x}" in utente for x in ("5m", "15m", "30m"))


def test_niente_dati_ne_codice_dell_altra_sessione():
    cartella = Path(__file__).resolve().parents[1]
    for f in cartella.rglob("*.py"):
        if "tests" in f.parts:
            continue
        testo = f.read_text()
        assert not re.search(r"^\s*(from|import)\s+(research|bot|stock)\b", testo, re.M), f
        assert "research/" not in testo and "G1" not in testo, f
    istruzioni = (cartella / "istruzioni.md").read_text()
    assert "G1" not in istruzioni and "ricerca" not in istruzioni.lower()


# --- chiamata vera con un client finto (senza chiave) ---------------------------------------------------------------

class _Usage:
    def model_dump(self):
        return {"input_tokens": 100, "output_tokens": 50}


class _R:
    def __init__(self, stop_reason, parsed):
        self.stop_reason, self.parsed_output, self.usage = stop_reason, parsed, _Usage()


class _Client:
    def __init__(self, risposta):
        self.risposta, self.chiamate = risposta, []
        esterno = self

        class _M:
            def parse(self, **kw):
                esterno.chiamate.append(kw)
                return esterno.risposta
        self.messages = _M()


def test_chiama_usa_il_modello_scelto_e_gestisce_rifiuto_e_troncata():
    from trader_ai.modello import chiama
    ok = r()
    c = _Client(_R("end_turn", ok))
    e = chiama(c, "s", "u")
    assert e.stato == "ok" and e.risposta is ok and e.usage["output_tokens"] == 50
    kw = c.chiamate[0]
    assert kw["model"] == "claude-opus-5-5" and kw["output_format"] is Risposta and kw["max_tokens"] == 16000
    assert "fallbacks" not in kw
    assert chiama(_Client(_R("refusal", None)), "s", "u").stato == "rifiuto"
    assert chiama(_Client(_R("max_tokens", None)), "s", "u").stato == "troncata"


def test_bilancio_di_oggi_dice_direzioni_vinte_perse_e_prezzo():
    from trader_ai.messaggio import bilancio_di_oggi
    ops = [{"chiusa": "2026-11-25T08:30:00", "lato": "corto", "risultato": -9.6},
           {"chiusa": "2026-11-25T14:09:00", "lato": "corto", "risultato": 2.5},
           {"chiusa": "2026-11-25T20:00:00", "lato": "lungo", "risultato": -4.0},
           {"chiusa": "2026-11-24T20:00:00", "lato": "lungo", "risultato": 50.0}]
    b = bilancio_di_oggi(ops, "2026-11-25", 58890.0, 60120.0)
    assert "3 operazioni chiuse" in b and "corto: 2 operazioni, 1 vinte e 1 perse" in b and "+2.09%" in b
    piene = [{**o, "aperta": "x", "leva": 5, "entrata": 1.0, "uscita": 1.0, "come": "stop", "approccio": "a"} for o in ops]
    _, utente = costruisci(ORA, "t", 4.0, "BTCUSDT", {}, {"prezzo": 1.0}, conto(), blocco_memoria(piene, "x", [], None, b))
    assert "bilancio di oggi" in utente


def test_istruzioni_obiettivo_obbligatorio():
    from trader_ai.messaggio import ISTRUZIONI
    t = ISTRUZIONI.read_text()
    assert "OBBLIGATORIO" in t and "Non è un tetto" in t and "IMPARA" in t
