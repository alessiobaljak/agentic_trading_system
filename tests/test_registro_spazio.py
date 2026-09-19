"""IL REGISTRO NON DEVE ARRIVARE AL MURO.

Il registro e' UN SOLO documento Firestore, e dentro ci sono i PASSAGGI ACCUMULATI:
settimane di attesa. Oltre 1 MiB Firestore rifiuta la scrittura, e fino al 19
settembre quella scrittura non aveva rete — il run moriva li' portandosi via le
conferme appena guadagnate, e da fuori il sintomo era solo un numero che smetteva
di salire.

Misura del 19 settembre (ops `gate`, 05:28 UTC): **759 KiB su 879** (86%), in
crescita di ~37 KiB al giorno. Tre giorni.

Tre difese, e questo file le tiene tutte e tre onerose da rompere:

  1. il FORMATO COMPATTO non perde informazione (andata e ritorno identici);
  2. l'alleggerimento e' PREVENTIVO — non si apre mentre si cade;
  3. la scrittura ha una RETE: se viene rifiutata, si riprova con la sola
     contabilita' invece di perdere i passaggi.

E una quarta, implicita ma decisiva: `decode_pairs` legge ANCORA i formati vecchi.
Il registro vivo resta nel formato precedente finche' il primo run col codice nuovo
non lo riscrive, e nel mezzo il bot deve continuare a operare.
"""
import json

import pytest

from bot.core.firebase_client import (decode_pairs, encode_pairs,
                                      encode_registry)
from scripts.optimize import REGISTRY_CORE_FIELDS, scrivi_registro, slim_registry


def _rec(passi: int = 1, **extra) -> dict:
    r = {"pass_count": passi, "fail_count": 0, "symbol": "VETUSDT",
         "strategy": "gen_6d06dca0", "last_seen_at": 1758258123.456789,
         "window_start": 1757000000.5, "passed_in_window": False,
         "generated": True, "last_passed_at": 1758200000.25,
         "last_params": {"rr": 2.0, "atr_mult_stop": 1.5},
         "last_pf": 1.631, "last_win_rate": 0.482,
         "regime_pf": {"bull_trending": {"pf": 1.84, "trades": 22}},
         "holdout": {"ok": True, "pf": 1.7}}
    r.update(extra)
    return r


# --------------------------------------------------------------------------- #
# 1. Il formato compatto non perde niente                                      #
# --------------------------------------------------------------------------- #
def test_andata_e_ritorno_conserva_tutto():
    """Tutto cio' che entra deve uscire identico, tempi a parte. Se questa
    proprieta' cade, il risparmio di spazio diventa una perdita di dati — ed e' il
    genere di perdita che si scopre settimane dopo."""
    pairs = {"VETUSDT|gen_6d06dca0": _rec(2)}
    tornato = decode_pairs(encode_registry(pairs))
    atteso = dict(pairs["VETUSDT|gen_6d06dca0"])
    ottenuto = dict(tornato["VETUSDT|gen_6d06dca0"])
    for campo in ("last_seen_at", "window_start", "last_passed_at"):
        assert ottenuto.pop(campo) == int(atteso.pop(campo))
    assert ottenuto == atteso


def test_symbol_e_strategy_tornano_dalla_chiave():
    """Si tolgono perche' la chiave `COIN|strategia` li contiene gia'. Se non
    tornassero, la dashboard mostrerebbe schede senza nome e `coin_in_maturazione`
    smetterebbe di riconoscere le coin da riammettere nell'universo."""
    enc = encode_registry({"VETUSDT|gen_6d06dca0": _rec()})
    assert '"symbol"' not in enc and '"VETUSDT"' not in enc.split('"k"')[1][:40]
    r = decode_pairs(enc)["VETUSDT|gen_6d06dca0"]
    assert r["symbol"] == "VETUSDT" and r["strategy"] == "gen_6d06dca0"


def test_un_record_incoerente_con_la_chiave_si_conserva():
    """La riduzione toglie SOLO cio' che e' davvero ridondante. Se un record avesse
    un symbol diverso dalla sua chiave, indovinare quale dei due e' giusto sarebbe
    peggio che tenerli entrambi."""
    enc = encode_registry({"VETUSDT|gen_a": _rec(symbol="ALTRAUSDT")})
    assert decode_pairs(enc)["VETUSDT|gen_a"]["symbol"] == "ALTRAUSDT"


def test_i_formati_vecchi_si_leggono_ancora():
    """La migrazione non e' istantanea: il registro vivo e' nel formato vecchio
    finche' il primo run col codice nuovo non lo riscrive. Se `decode_pairs`
    smettesse di leggerlo, il bot vedrebbe zero coppie validate e smetterebbe di
    operare — senza un solo errore in log."""
    pairs = {"VETUSDT|gen_a": _rec()}
    assert decode_pairs(encode_pairs(pairs)) == pairs        # stringa, nomi lunghi
    assert decode_pairs(pairs) == pairs                      # mappa nuda
    assert decode_pairs(json.dumps(pairs)) == pairs


def test_il_marcatore_non_e_ambiguo():
    """`v` e `k` al primo livello non possono essere coppie: una chiave di coppia e'
    sempre `SYMBOL|strategia`. Senza questa garanzia il decoder potrebbe scambiare
    un registro normale per uno compatto."""
    normale = {"VETUSDT|gen_a": _rec(), "DOTUSDT|gen_b": _rec()}
    assert all("|" in k for k in decode_pairs(encode_pairs(normale)))


def test_e_piu_piccolo_e_di_molto():
    """Il punto di tutto l'esercizio. Su un registro realistico il formato compatto
    deve stare ben sotto la meta': un guadagno del 10% non varrebbe il rischio di
    cambiare formato a un documento che contiene settimane di attesa."""
    pairs = {f"COIN{i}USDT|gen_{i:08x}":
             _rec(i % 4, symbol=f"COIN{i}USDT", strategy=f"gen_{i:08x}")
             for i in range(400)}
    prima = len(encode_pairs(pairs).encode("utf-8"))
    dopo = len(encode_registry(pairs).encode("utf-8"))
    assert dopo < prima * 0.75, f"risparmio insufficiente: {prima} -> {dopo}"

    # e con l'alleggerimento preventivo sopra (il caso vero: poche validate)
    tutto = len(slim_registry(pairs, list(pairs)[:40]).encode("utf-8"))
    assert tutto < prima * 0.5, f"insieme dovrebbero dimezzarlo: {prima} -> {tutto}"


# --------------------------------------------------------------------------- #
# 2. L'alleggerimento e' PREVENTIVO                                            #
# --------------------------------------------------------------------------- #
def test_alleggerisce_anche_quando_ci_sta_comodamente():
    """LA CORREZIONE DEL 19 SETTEMBRE. Prima si alleggeriva solo oltre la soglia:
    il documento arrivava al muro a velocita' piena e la rete si apriva mentre si
    stava gia' cadendo. Con un tetto larghissimo l'alleggerimento deve avvenire lo
    stesso."""
    pairs = {"VETUSDT|gen_a": _rec(3), "DOTUSDT|gen_b": _rec(1)}
    fuori = decode_pairs(slim_registry(pairs, ["VETUSDT|gen_a"], max_bytes=10**9))
    assert "regime_pf" in fuori["VETUSDT|gen_a"], "la validata tiene tutto"
    assert "regime_pf" not in fuori["DOTUSDT|gen_b"], "la non validata va alleggerita"


def test_la_contabilita_sopravvive_a_ogni_alleggerimento():
    """I campi del nucleo sono quelli senza cui si perdono i passaggi. Devono
    restare sia nell'alleggerimento normale sia in quello d'emergenza."""
    pairs = {"DOTUSDT|gen_b": _rec(2)}
    for tetto in (10**9, 1):          # comodo, e poi impossibile
        r = decode_pairs(slim_registry(pairs, [], max_bytes=tetto))["DOTUSDT|gen_b"]
        for campo in ("pass_count", "window_start", "passed_in_window",
                      "generated", "last_passed_at", "last_seen_at"):
            assert campo in r, f"{campo} perso col tetto {tetto}"


def test_in_emergenza_si_alleggeriscono_anche_le_validate():
    """Perdere il PF sulle schede della dashboard e' cosmetico; perdere un passaggio
    sono settimane. Non e' un pareggio, e la scelta dev'essere quella."""
    pairs = {"VETUSDT|gen_a": _rec(3)}
    r = decode_pairs(slim_registry(pairs, ["VETUSDT|gen_a"], max_bytes=1))["VETUSDT|gen_a"]
    assert "regime_pf" not in r
    assert r["pass_count"] == 3 and "last_params" in r


def test_il_nucleo_e_un_sottoinsieme_di_cio_che_si_scrive():
    """Se un campo del nucleo non fosse mai scritto, l'alleggerimento lo
    'proteggerebbe' senza che esista: una garanzia finta."""
    assert {"pass_count", "window_start", "generated"} <= REGISTRY_CORE_FIELDS


# --------------------------------------------------------------------------- #
# 3. La scrittura ha una rete                                                  #
# --------------------------------------------------------------------------- #
class _FbRifiuta:
    """Firestore che rifiuta la PRIMA scrittura, come fa oltre il limite di 1 MiB."""

    def __init__(self):
        self.scritture = []

    def set_doc(self, coll, doc, payload):
        self.scritture.append(payload)
        if len(self.scritture) == 1:
            raise RuntimeError("document exceeds maximum size of 1048576 bytes")


def test_una_scrittura_rifiutata_non_perde_i_passaggi():
    """IL CUORE. Prima del 19 settembre questa eccezione usciva da `update_registry`
    e il run moriva: le conferme guadagnate in quel giro sparivano, in silenzio."""
    fb = _FbRifiuta()
    pairs = {"VETUSDT|gen_a": _rec(3), "DOTUSDT|gen_b": _rec(2)}
    assert scrivi_registro(fb, {"pairs": encode_registry(pairs), "validated": []}, pairs)
    assert len(fb.scritture) == 2, "il secondo tentativo non e' stato fatto"
    salvate = decode_pairs(fb.scritture[-1]["pairs"])
    assert salvate["VETUSDT|gen_a"]["pass_count"] == 3
    assert salvate["DOTUSDT|gen_b"]["pass_count"] == 2


def test_se_fallisce_anche_il_ripiego_l_errore_sale():
    """Se anche la forma minima viene rifiutata, il problema non e' lo spazio.
    Ingoiare l'eccezione qui significherebbe un run che dice 'fatto' e non ha
    scritto niente — il modo piu' caro di sbagliare in questo progetto."""
    class _SempreNo(_FbRifiuta):
        def set_doc(self, coll, doc, payload):
            raise RuntimeError("permission denied")

    with pytest.raises(RuntimeError):
        scrivi_registro(_SempreNo(), {"pairs": "{}"}, {"VETUSDT|gen_a": _rec()})


def test_la_discovery_non_rigonfia_cio_che_optimize_ha_alleggerito():
    """La discovery riscrive il registro DOPO optimize. Finche' usava `encode_pairs`
    grezzo, l'ultimo a scrivere disfaceva il lavoro del primo: la rete c'era e non
    serviva a niente."""
    import inspect

    from scripts import discover_strategies as d

    src = inspect.getsource(d.merge_into_registry)
    assert "slim_registry(pairs, validated)" in src
    assert "scrivi_registro(" in src
    assert 'doc["pairs"] = encode_pairs' not in src
