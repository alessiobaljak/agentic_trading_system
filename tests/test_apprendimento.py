"""COME IMPARA IL SISTEMA, GIORNO PER GIORNO (29 set 2026).

Richiesta del proprietario: «nel report mattutino voglio avere visibilita' di
come impara e adatta il trailing, e anche delle strategie cosa sta imparando».
Si verifica:
  * la foto del giorno (`impronta_giorno`): contenuto, chiavi ammesse dal RTDB,
    niente None, dimensione < 30 KB con 200 validate;
  * le differenze fra due foto (keep cambiato, declassata nuova e tornata
    piena, panchina entrata/uscita, ipotesi nuova/sparita, freno, cooldown);
  * gli eventi datati fra due istanti (ipotesi, varianti, promosse/rimosse,
    sostituzioni, intorno, declassate, esplorative, freno);
  * la sezione del trailing coi numeri del 29 set (62 verdetti, 25 prematuri
    di cui 4 da rumore, 37 protetti -> «manca 1 protetto»);
  * la foto che manca, detta in chiaro;
  * il comando ops `controllo`: sezioni nuove IN CODA, output di prima
    identico, `--json` com'era, < 12 KB anche con 200 validate;
  * il bot scrive la foto una volta al giorno e non solleva mai;
  * i verdetti portano da ora la loro data.
"""
from __future__ import annotations

import json
import os
from types import SimpleNamespace

import pytest

from bot.config import settings
from bot.core.firebase_client import FirebaseClient, encode_pairs
from bot.learning import apprendimento as ap
from bot.learning import controllo as c
from bot.learning.metrics import proposta_keep, proposta_keep_strategia
from tests.test_controllo import NOW, _fb, _finto_bot, _registro, _trade

# NOW = 25 set 2026 12:00 UTC = 14:00 in Italia: «oggi» 25 set, «ieri» 24 set
OGGI, IERI = "2026-09-25", "2026-09-24"
FIN = ap.finestre(NOW)
T_IERI = FIN["ieri"][0] + 10 * 3600          # 24 set 10:00 ora italiana
T_STANOTTE = FIN["stanotte"][0] + 3600       # 25 set 01:00 ora italiana
T_PRIMA = FIN["ieri"][0] - 3600              # 23 set sera: fuori da entrambe


# --------------------------------------------------------------------------- #
# attrezzi                                                                    #
# --------------------------------------------------------------------------- #
def _trailing(i, verdetto, rumore=False, exit_ts=None, **extra):
    return _trade(1000 + i, 3.0, "trailing_stop", strat=f"gen_t{i % 3}", exit_ts=exit_ts,
                  trailing_verdict=verdetto, trailing_knockout_atr=0.5 if rumore else 2.0,
                  trailing_miss_to_tp=0.7, **extra)


def _trade_del_29_set() -> list[dict]:
    """I numeri misurati il 29 set (ops 0345:74): 62 verdetti, 25 prematuri (4
    da rumore), 37 protetti, e 7 neutri (69 - 62, ops 0345:77)."""
    out = [_trailing(i, "premature", rumore=i < 4, exit_ts=T_PRIMA - i * 3600) for i in range(25)]
    out += [_trailing(100 + i, "protected", exit_ts=T_PRIMA - i * 3600) for i in range(37)]
    out += [_trailing(200 + i, "neutral", exit_ts=T_PRIMA - i * 3600) for i in range(7)]
    return out


def _dati(n_validate=6, trades=None, pesi=None, declassate=(), esplorative=None, drift=None,
          adapt=None, referti=None) -> dict:
    reg = _registro(n_validate)
    pairs = json.loads(reg["pairs"])
    for k in declassate:
        pairs[k]["declassata"] = True
    reg["pairs"] = encode_pairs(pairs)
    return {"registro": reg,
            "weights": {"weights": pesi if pesi is not None else [
                {"strategy": "gen_1", "regime": "sideways", "weight": 0.42},
                {"strategy": "gen_2", "regime": "bull.trending", "weight": 0.9}]},
            "adapt_state": adapt or {"coin_cooldown": {"AUSDT": NOW + 3600},
                                     "strat_cooldown": {"gen_9": NOW + 60, "gen_8": NOW - 60}},
            "drift": drift or {"global": {"verdict": "drift", "live_pf": 0.7, "expected_pf": 2.04}},
            "referti": referti or {"ipotesi": [{"strategia": "gen_1", "tipo": "solo_long",
                                                 "motivo": "short 4/4 persi", "campione": 4}]},
            "esplorative": esplorative,
            "trades": trades if trades is not None else _trade_del_29_set()}


# --------------------------------------------------------------------------- #
# 1. la foto del giorno                                                        #
# --------------------------------------------------------------------------- #
def _chiavi(obj):
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield k
            yield from _chiavi(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from _chiavi(v)


def _valori(obj):
    if isinstance(obj, dict):
        for v in obj.values():
            yield from _valori(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from _valori(v)
    else:
        yield obj


def test_impronta_giorno_contiene_tutto_quello_che_serve():
    esp = {"pairs": encode_pairs({"XUSDT|gen_e": {"since": NOW - 3600}})}
    foto = ap.impronta_giorno(_dati(declassate=["C2USDT|gen_2"], esplorative=esp), NOW)
    assert foto["at"] == NOW and foto["giorno"] == OGGI and foto["versione"] == 1
    v = foto["validate"]
    assert len(v) == 6
    assert v["C0USDT|gen_0"] == {"declassata": False, "keep": 0.25, "scala": "1/2/3", "be": True}
    assert v["C1USDT|gen_1"] == {"declassata": False, "scala": "1.5/3/5", "be": True}   # keep: default
    assert v["C2USDT|gen_2"]["declassata"] is True
    # tutti i pesi, a 2 decimali, con la chiave ripulita per il RTDB
    assert foto["pesi"] == {"gen_1|sideways": 0.42, "gen_2|bull_trending": 0.9}
    assert foto["cooldown"] == {"coin": ["AUSDT"], "strategie": ["gen_9"]}   # gen_8 e' scaduto
    assert foto["freno"] == {"attivo": True, "pf_vissuto": 0.7, "pf_atteso": 2.04}
    assert foto["ipotesi"] == ["gen_1|solo_long"] and foto["esplorative"] == ["XUSDT|gen_e"]
    t = foto["trailing"]
    assert (t["verdetti"], t["prematuri"], t["rumore"], t["protetti"], t["neutri"]) == (62, 25, 4, 37, 7)
    assert "proposta" not in t                                   # 59,7%: nessuna proposta
    # il RTDB rifiuta . $ # [ ] / nelle chiavi, e un None non si scrive
    assert not any(ch in str(k) for k in _chiavi(foto) for ch in ".$#[]/")
    assert None not in list(_valori(foto))


def test_impronta_giorno_resta_sotto_30_kb_con_200_validate():
    pesi = [{"strategy": f"gen_{i}", "regime": r, "weight": 0.3 + (i % 7) / 10}
            for i in range(60) for r in ("sideways", "bull_trending", "bear_trending", "volatile")]
    foto = ap.impronta_giorno(_dati(n_validate=200, pesi=pesi), NOW)
    assert len(foto["validate"]) == 200 and len(foto["pesi"]) == 240
    assert len(json.dumps(foto)) < 30_000


# --------------------------------------------------------------------------- #
# 2. le differenze fra due foto                                                 #
# --------------------------------------------------------------------------- #
def _foto(**kw) -> dict:
    base = {"at": NOW - 86400, "giorno": IERI,
            "validate": {"AUSDT|gen_a": {"keep": 0.75, "scala": "1.5/3/5", "be": True, "declassata": False},
                         "BUSDT|gen_b": {"declassata": True},
                         "CUSDT|gen_c": {"keep": 0.5, "declassata": False}},
            "pesi": {"gen_a|sideways": 0.3, "gen_b|bull_trending": 0.8},
            "cooldown": {"coin": ["AUSDT"]}, "freno": {"attivo": False},
            "ipotesi": ["gen_a|solo_long"], "esplorative": ["XUSDT|gen_e"],
            "trailing": {"verdetti": 62, "proposta": 0.75}}
    base.update(kw)
    return base


def test_differenze_fra_due_foto():
    prima = _foto()
    dopo = _foto(at=NOW, giorno=OGGI,
                 validate={"AUSDT|gen_a": {"keep": 0.5, "scala": "1.5/3/5", "be": True, "declassata": False},
                           "BUSDT|gen_b": {"declassata": False},
                           "CUSDT|gen_c": {"keep": 0.5, "declassata": True},
                           "DUSDT|gen_d": {"declassata": False}},
                 pesi={"gen_a|sideways": 0.55, "gen_b|bull_trending": 0.45},
                 cooldown={"strategie": ["gen_z"]}, freno={"attivo": True},
                 ipotesi=["gen_b|conferma_trend"], esplorative=[],
                 trailing={"verdetti": 63})                       # la proposta 0,75 e' sparita
    d = ap.differenze(prima, dopo)
    assert d["coppie"] == [{"coppia": "AUSDT|gen_a", "keep": (0.75, 0.5)}]
    assert d["comuni"] == 3 and d["validate_entrate"] == ["DUSDT|gen_d"] and d["validate_uscite"] == []
    assert d["declassate_nuove"] == ["CUSDT|gen_c"] and d["tornate_piene"] == ["BUSDT|gen_b"]
    assert d["panchina_entrate"] == [("gen_b|bull_trending", 0.45)]
    assert d["panchina_uscite"] == [("gen_a|sideways", 0.55)]
    assert d["cooldown_iniziati"] == ["strategia gen_z"] and d["cooldown_finiti"] == ["coin AUSDT"]
    assert d["freno"] == "acceso"
    assert d["ipotesi_nuove"] == ["gen_b|conferma_trend"] and d["ipotesi_sparite"] == ["gen_a|solo_long"]
    assert d["esplorative_uscite"] == ["XUSDT|gen_e"]
    assert d["proposta"] == (0.75, None)
    # nessun cambiamento: tutto vuoto; una foto che manca: None, non un confronto inventato
    vuota = ap.differenze(prima, dict(prima))
    assert vuota["coppie"] == [] and vuota["freno"] is None and vuota["proposta"] is None
    assert ap.differenze(None, prima) is None and ap.differenze(prima, {}) is None


def test_la_riga_coppia_per_coppia_si_taglia_a_8():
    prima = _foto(validate={f"C{i}USDT|gen_{i}": {"keep": 0.5, "declassata": False} for i in range(20)})
    dopo = _foto(validate={f"C{i}USDT|gen_{i}": {"keep": 0.65, "declassata": False} for i in range(20)})
    righe = ap._righe_cambi("ieri", ap.differenze(prima, dopo), "")
    # «su 20 in comune» si leggeva «solo 20 in comune»: si dice cosa e' cambiato
    assert "20 coppie su 20 hanno cambiato keep, scala o break-even" in righe[0]
    nessuna = ap._righe_cambi("ieri", ap.differenze(prima, prima), "")
    assert "nessuna delle 20 coppie presenti in entrambe le foto ha cambiato" in nessuna[0]
    assert sum(1 for r in righe if "keep 0,5 -> 0,65" in r) == 8
    assert righe[-1].strip() == "e altre 12"


# --------------------------------------------------------------------------- #
# 3. gli eventi fra due istanti                                                 #
# --------------------------------------------------------------------------- #
def test_eventi_fra_due_istanti():
    storia = {"voci": {
        "gen_a|solo_long": {"strategia": "gen_a", "tipo": "solo_long", "nata_at": T_IERI,
                            "variante_id": "gen_a2", "variante_at": T_IERI + 60, "bocciata_at": T_STANOTTE},
        "gen_b|conferma_trend": {"strategia": "gen_b", "tipo": "conferma_trend", "nata_at": T_PRIMA,
                                 "variante_id": "gen_b2", "passata_at": T_IERI, "validata_at": T_IERI}}}
    vite = {"events": [{"key": "AUSDT|gen_b2", "tipo": "promossa", "at": T_IERI, "ipotesi": "conferma_trend"},
                       {"key": "ZUSDT|gen_z", "tipo": "rimossa", "at": T_IERI, "vissuta_giorni": 3.24},
                       {"key": "OLDUSDT|gen_o", "tipo": "promossa", "at": T_PRIMA}]}
    pairs = {"AUSDT|gen_b": {"sostituita_da": "gen_b2", "sostituita_at": T_IERI},
             "BUSDT|gen_f": {"nata_intorno_at": T_IERI, "genitore": "gen_m"},
             "CUSDT|gen_d": {"declassata": True, "declassata_at": T_IERI},
             "DUSDT|gen_x": {"declassata": True, "declassata_at": T_PRIMA}}
    esp = {"pairs": encode_pairs({"EUSDT|gen_e": {"since": T_IERI}, "FUSDT|gen_f": {"since": T_PRIMA}}),
           "storia": encode_pairs({"GUSDT|gen_g": {"since": T_PRIMA, "fine": T_IERI, "esito": "validata"},
                                   "HUSDT|gen_h": {"since": T_IERI, "fine": T_IERI + 5, "esito": "scartata"}})}
    drift = {"global": {"verdict": "drift", "dal": T_IERI + 7200}}
    referti = {"ipotesi": [{"strategia": "gen_a", "tipo": "solo_long", "motivo": "short 4/4 persi"}]}
    t0, t1, _g = FIN["ieri"]
    ev = ap.eventi_fra(t0, t1, storia=storia, vite=vite, registro={"pairs": encode_pairs(pairs)},
                       esplorative=esp, drift=drift, referti=referti)
    assert ev["ipotesi_nate"] == [{"chiave": "gen_a|solo_long", "strategia": "gen_a", "tipo": "solo_long",
                                   "motivo": "short 4/4 persi"}]
    assert [x["variante"] for x in ev["varianti"]["create"]] == ["gen_a2"]
    assert [x["variante"] for x in ev["varianti"]["passate"]] == ["gen_b2"]
    assert [x["variante"] for x in ev["varianti"]["validate"]] == ["gen_b2"]
    assert ev["varianti"]["bocciate"] == []                        # e' stanotte, non ieri
    assert [e["key"] for e in ev["promosse"]] == ["AUSDT|gen_b2"] and [e["key"] for e in ev["rimosse"]] == ["ZUSDT|gen_z"]
    assert ev["sostituzioni"] == [{"madre": "AUSDT|gen_b", "figlia": "AUSDT|gen_b2"}]
    assert ev["intorno"] == [{"figlia": "BUSDT|gen_f", "genitore": "gen_m"}]
    assert ev["declassate"] == ["CUSDT|gen_d"]
    assert ev["esplorative"] == {"entrate": ["EUSDT|gen_e", "HUSDT|gen_h"], "promosse": ["GUSDT|gen_g"],
                                 "scartate": ["HUSDT|gen_h"]}
    assert ev["freno_acceso_at"] == T_IERI + 7200
    # stanotte: solo la bocciatura
    s0, s1, _g = FIN["stanotte"]
    ev2 = ap.eventi_fra(s0, s1, storia=storia, vite=vite, registro={"pairs": encode_pairs(pairs)},
                        esplorative=esp, drift=drift, referti=referti)
    assert [x["variante"] for x in ev2["varianti"]["bocciate"]] == ["gen_a2"]
    assert not ev2["ipotesi_nate"] and not ev2["promosse"] and ev2["freno_acceso_at"] is None
    righe = ap._righe_eventi(ev, None, "manca la foto del 24 set")
    testo = "\n".join(righe)
    assert "ipotesi nate dai referti 1: gen_a solo_long «short 4/4 persi»" in testo
    # UN evento, UNA riga: la figlia che prende il posto della madre e' la stessa
    # promozione del diario, non tre cose successe
    assert ("validate promosse 1: AUSDT|gen_b2 (ipotesi conferma_trend; prende il posto di gen_b, "
            "che smette di essere operata); rimosse 1: ZUSDT|gen_z (vissuta 3,2 giorni)") in testo
    assert "sostituzioni madre -> figlia" not in testo
    # la figlia dell'intorno che il diario non ha fra le promosse resta, a parte
    assert "figlie nuove 1: BUSDT|gen_f (figlia dell'intorno di gen_m)" in testo
    # le varianti col nome dell'idea, non solo con l'id della variante
    assert ("varianti dalle ipotesi: create 1: gen_a solo_long (variante gen_a2); passate 1: "
            "gen_b conferma_trend (variante gen_b2); validate 1: gen_b conferma_trend (variante "
            "gen_b2, promossa: vedi sotto)") in testo
    assert "freno globale acceso alle" in testo and "non disponibili, manca la foto del 24 set" in testo
    # tutto fermo: una riga sola lo dice
    vuoto = ap.eventi_fra(T_PRIMA - 10, T_PRIMA - 5)
    assert ap._righe_eventi(vuoto, ap.differenze(_foto(), _foto()), "")[0].strip().startswith("nulla di nuovo")


# --------------------------------------------------------------------------- #
# 4. il trailing coi numeri del 29 set                                          #
# --------------------------------------------------------------------------- #
def test_quanto_manca_segue_la_regola_di_metrics():
    g = ap.quanto_manca_globale(62, 25, 37)
    assert g["proposta"] is None and g["mancano_protetti"] == 1 and g["mancano_prematuri"] == 31
    assert proposta_keep(63, 25, 38) == 0.75 and proposta_keep(62, 25, 37) is None
    assert proposta_keep(62 + 31, 25 + 31, 37) == 0.25 and proposta_keep(62 + 30, 25 + 30, 37) is None
    # a tappeto: il numero detto e' sempre il minimo che accende la regola
    for n in range(0, 30):
        for prot in range(0, n + 1):
            prem = n - prot
            g = ap.quanto_manca_globale(n, prem, prot)
            if g["proposta"] is not None:
                y = g["spegne_con"]
                contro = (prem + y, prot) if g["proposta"] == 0.75 else (prem, prot + y)
                assert proposta_keep(n + y, *contro) is None
                meno = (prem + y - 1, prot) if g["proposta"] == 0.75 else (prem, prot + y - 1)
                assert proposta_keep(n + y - 1, *meno) == g["proposta"]
                continue
            x = g["mancano_protetti"]
            assert proposta_keep(n + x, prem, prot + x) == 0.75
            if x:
                assert proposta_keep(n + x - 1, prem, prot + x - 1) != 0.75


def test_le_strategie_piu_vicine_alla_proposta():
    def t(i, gid, v, rumore=False):
        return _trade(i, 1.0, "trailing_stop", strat=gid, trailing_verdict=v,
                      trailing_knockout_atr=0.5 if rumore else 2.0)
    trades = ([t(i, "gen_a", "protected") for i in range(4)]
              + [t(10 + i, "gen_b", "protected") for i in range(3)] + [t(20, "gen_b", "premature")]
              + [t(30 + i, "gen_c", "premature", rumore=i == 0) for i in range(2)] + [t(40, "gen_c", "protected")]
              + [t(50 + i, "gen_p", "protected") for i in range(5)])
    v = ap.vicine_per_strategia(trades)
    assert [x["strategia"] for x in v["propongono"]] == ["gen_p"] and v["propongono"][0]["keep"] == 0.75
    assert [(x["strategia"], x["verso"], x["mancano"]) for x in v["vicine"]] == [
        ("gen_a", 0.75, 1), ("gen_b", 0.75, 1), ("gen_c", 0.25, 2)]
    # il numero detto accende davvero la regola della strategia
    extra = [t(60 + i, "gen_c", "premature", rumore=True) for i in range(2)]
    assert proposta_keep_strategia([x for x in trades if x["strategy"] == "gen_c"] + extra) == 0.25
    assert proposta_keep_strategia([x for x in trades if x["strategy"] == "gen_c"] + extra[:1]) is None


def test_sezione_trailing_coi_numeri_del_29_settembre():
    dati = _dati(n_validate=6)
    dati["gate"] = {"meta": {"generato_at": NOW - 3600},
                    "giro": {"computed_at": NOW - 3600,
                             "paper_propone": {"scala": "1/1.25/1.75", "keep": None, "verdetti_trailing": 62,
                                               "keep_strategie": 0}}}
    righe = ap.sezione_trailing(dati, NOW)
    testo = "\n".join(righe)
    assert righe[0].startswith("COME IMPARA IL TRAILING (il keep e' la parte del guadagno che il trailing blocca")
    assert ("uscite del trailing sulle candele da 15 minuti (le sole che contano per le proposte): "
            if settings.ORCHESTRATOR_TIMEFRAME == "15m" else "uscite del trailing sulle candele da ") in testo
    assert "62 verdetti = 25 prematuri (4 da rumore) + 37 protetti; in piu' 7 neutri" in testo
    assert ("«da rumore» se lo stop e' scattato su un ritorno indietro piu' piccolo del movimento "
            "medio di una candela") in testo
    assert "nelle 24 ore dopo" in testo and "96 barre" not in testo and "ATR" not in testo
    assert ("37 protetti su 62 verdetti = 59,7% (serve il 60%): nessuna proposta. Manca 1 protetto "
            "per proporre 0,75 (oppure 31 prematuri per 0,25)") in testo
    # senza uscite dopo un incasso parziale ne' verdetti dopo gli stop, le righe non ci sono
    assert "incasso parziale" not in testo and "dopo gli stop" not in testo
    assert "incongruenza nota" not in testo                  # rimandava a una voce che non c'era
    assert "scala dei target di incasso dal vissuto (multipli del rischio iniziale" in testo
    assert "ultimo giro del gate" in testo and "1/1.25/1.75" in testo
    assert "keep imparato dal bot da solo" in testo
    assert "c) COSA HA SCELTO IL GATE per le 6 validate che il bot opera" in testo
    assert "Dalle proposte del paper (0,25 e 0,75 esistono solo cosi'): 2" in testo
    assert "cambiato ieri: non disponibile (manca la foto del 24 set)" in testo
    assert "gruppi NON confrontabili: coppie diverse; misura, non regola" in testo
    # i verdetti senza data si contano col giorno di uscita, e lo si dice
    nuovi = [_trailing(900, "protected", exit_ts=T_IERI),
             _trailing(901, "premature", exit_ts=T_PRIMA, trailing_verdict_at=T_IERI + 60)]
    testo = "\n".join(ap.sezione_trailing(_dati(trades=nuovi), NOW))
    assert ("nuovi ieri (24 set): trailing 1 prematuro, 1 protetto, 0 neutri (1 senza data: contati "
            "nel giorno di uscita del trade, il verdetto puo' essere del giorno dopo)") in testo
    assert "nuovi stanotte (25 set): nessuno" in testo


def test_funziona_raggruppa_per_keep_in_uso():
    dal = ap.finestre(NOW)["ieri"][0]
    trades = [
        _trade(1, 4.0, "trailing_stop", exit_ts=NOW - 3600, profit_lock_keep=0.75, orig_stop=98.0,
               trailing_verdict="protected", trailing_miss_to_tp=0.6,
               post_mortem={"lock_mai_armato": False}),
        _trade(2, -2.0, "stop_loss", exit_ts=NOW - 7200, profit_lock_keep=0.75, orig_stop=98.0),
        _trade(3, 2.0, "trailing_stop", exit_ts=NOW - 7200, profit_lock_keep=0.5, orig_stop=98.0,
               trailing_verdict="premature", trailing_miss_to_tp=0.8),
        _trade(4, 9.0, "manual", exit_ts=NOW - 7200, profit_lock_keep=0.5),        # esito esterno: fuori
        _trade(5, 9.0, "trailing_stop", exit_ts=dal - 10, profit_lock_keep=0.5),   # prima del dal: fuori
        _trade(6, 9.0, "take_profit", exit_ts=NOW - 7200),                         # senza keep: fuori
    ]
    g = {x["keep"]: x for x in ap.keep_in_uso(trades, dal=dal)}
    assert set(g) == {0.5, 0.75}
    assert g[0.75]["trade"] == 2 and g[0.75]["armato"] == 1 and g[0.75]["con_referto"] == 2
    assert g[0.75]["protetti"] == 1 and g[0.75]["r_medio"] == pytest.approx((2.0 - 1.0) / 2)
    assert g[0.5]["trade"] == 1 and g[0.5]["prematuri"] == 1 and g[0.5]["tavolo"] == 0.8
    # detto a parole: «lock armato 1 su 2» non diceva su cosa
    testo = "\n".join(ap.sezione_trailing(_dati(trades=trades), NOW))
    assert "keep 0,75: 2 trade · trailing armato in 1 dei 2 trade con referto (50,0%)" in testo


# --------------------------------------------------------------------------- #
# 5. la foto che manca                                                          #
# --------------------------------------------------------------------------- #
def test_la_foto_che_manca_e_detta_in_chiaro():
    oggi = _foto(at=FIN["stanotte"][0] + 300, giorno=OGGI)
    ieri = _foto(at=FIN["ieri"][0] + 240)
    assert "foto di ieri 24 set 00:04, foto di oggi 25 set 00:05" in "\n".join(ap.righe_foto(NOW, oggi, ieri))
    solo_oggi = "\n".join(ap.righe_foto(NOW, oggi, None))
    assert ("manca la foto del 24 set (bot fermo tutto il giorno o foto non riuscita): confronto "
            "«ieri» fra stati non disponibile; la storia parte dal 25 set") in solo_oggi
    # c'e' una foto piu' vecchia: non si dice che la storia parte oggi
    con_vecchia = "\n".join(ap.righe_foto(NOW, oggi, None, ("2026-09-22", 1.0)))
    assert "l'ultima foto prima di oggi e' del 22 set" in con_vecchia
    assert "la storia parte" not in con_vecchia
    # RTDB muto: le foto non lette non «mancano»
    muto = "\n".join(ap.righe_foto(NOW, None, None, None, rtdb_muto=True))
    assert "RTDB non raggiungibile: foto non lette" in muto
    assert "mancano le foto" not in muto and "non e' ancora partita" not in muto
    assert "manca la foto di oggi (25 set)" in "\n".join(ap.righe_foto(NOW, None, ieri))
    niente = "\n".join(ap.righe_foto(NOW, None, None))
    assert "mancano le foto del 24 set e del 25 set" in niente and "la storia non e' ancora partita" in niente
    assert "l'ultima e' del 20 set" in "\n".join(ap.righe_foto(NOW, None, None, ("2026-09-20", 1.0)))
    testo = "\n".join(ap.sezione_strategie(_dati(), NOW, storia={}, vite={}, foto_oggi=oggi))
    assert "IERI (24 set, giornata intera ora italiana):" in testo
    assert "non disponibili, manca la foto del 24 set" in testo


def test_giorni_da_cancellare():
    assert ap.giorni_da_cancellare("2026-09-26", "2026-09-25") == ["2026-08-21"]
    assert ap.giorni_da_cancellare("2026-09-26", "2026-09-23") == ["2026-08-21", "2026-08-20", "2026-08-19"]
    assert len(ap.giorni_da_cancellare("2026-09-26", None)) == ap.FOTO_SPAZZATA_GIORNI
    assert ap.giorni_da_cancellare("2026-09-26", "2026-01-01")[-1] == "2026-08-15"   # mai piu' di 7
    assert ap.giorni_da_cancellare("rotto", None) == []


def test_la_copia_della_soglia_scala_e_uguale_alla_discovery():
    from scripts.discover_strategies import SCALA_STRATEGIA_MIN_TRADES, scale_per_strategia
    assert ap.SCALA_STRATEGIA_MIN_TRADES == SCALA_STRATEGIA_MIN_TRADES
    trades = [_trade(i, 1.0, strat=f"gen_{i % 3}", mfe_r=0.5 + 0.2 * i) for i in range(20)]
    attese = {k: "/".join(f"{m:g}" for m in v) for k, v in scale_per_strategia(trades).items()}
    assert ap.scale_proprie(trades) == attese and attese


# --------------------------------------------------------------------------- #
# 6. il comando ops `controllo`                                                 #
# --------------------------------------------------------------------------- #
def _fb_pieno(n_validate: int = 200) -> FirebaseClient:
    """Il Firebase del controllo con in piu' il caso peggiore: 200 validate,
    foto di ieri e di oggi con ogni coppia cambiata, 50 ipotesi e 50 promosse ieri."""
    fb = _fb()
    fb.set_doc("strategy_registry", "validated", _registro(n_validate))
    dati = c.carica_dati(fb, NOW)
    oggi = ap.impronta_giorno(dati, FIN["stanotte"][0] + 300)
    ieri = json.loads(json.dumps(oggi))
    ieri["at"], ieri["giorno"] = FIN["ieri"][0] + 240, IERI
    for k, v in ieri["validate"].items():
        v["keep"] = 0.75
        v["declassata"] = True
    ieri["pesi"] = {k: 0.9 for k in oggi["pesi"]}
    fb.set_rtdb(f"/learning_giorni/{OGGI}", oggi)
    fb.set_rtdb(f"/learning_giorni/{IERI}", ieri)
    fb.set_doc("learning", "ipotesi_storia", {"voci": {
        f"gen_{i}|solo_long": {"strategia": f"gen_{i}", "tipo": "solo_long", "nata_at": T_IERI,
                               "variante_id": f"gen_{i}v", "variante_at": T_IERI, "bocciata_at": T_STANOTTE}
        for i in range(50)}})
    fb.set_doc("gate_history", "lifecycle", {"events": [
        {"key": f"C{i}USDT|gen_{i}", "tipo": "promossa" if i % 2 else "rimossa", "at": T_IERI,
         "ipotesi": "solo_long", "vissuta_giorni": 2.5} for i in range(50)]})
    return fb


def test_il_comando_ops_aggiunge_le_sezioni_in_coda_e_lascia_uguale_il_resto(monkeypatch, capsys):
    from scripts import controllo as cli
    fb = _fb_pieno()
    monkeypatch.setattr("bot.core.firebase_client.get_firebase", lambda: fb)
    monkeypatch.setattr(c.time, "time", lambda: NOW)
    originale = cli.stampa_apprendimento
    monkeypatch.setattr(cli, "stampa_apprendimento", lambda *a, **k: None)
    capsys.readouterr()                                    # la riga d'avvio del client in memoria
    assert cli.main([]) == 0
    vecchio = capsys.readouterr().out
    monkeypatch.setattr(cli, "stampa_apprendimento", originale)
    assert cli.main([]) == 0
    nuovo = capsys.readouterr().out
    assert nuovo.startswith(vecchio)                       # l'output di prima, identico e in testa
    coda = nuovo[len(vecchio):]
    for titolo in ("STORIA DEL LEARNING", "COME IMPARA IL TRAILING", "COSA IMPARANO LE STRATEGIE",
                   "a) COSA HA VISTO IL PAPER", "b) COSA PROPONE IL PAPER AL GATE",
                   "c) COSA HA SCELTO IL GATE", "d) FUNZIONA?", "IERI (24 set", "STANOTTE (25 set",
                   "PER STRATEGIA"):
        assert titolo in coda, titolo
    assert "foto di ieri 24 set 00:04, foto di oggi 25 set 00:05" in coda
    assert ("cambiato ieri (foto 24 set 00:04 -> foto 25 set 00:05): 200 coppie su 200 hanno "
            "cambiato keep, scala o break-even") in coda
    assert "e altre 192" in coda and "tornate piene 200:" in coda
    assert "ipotesi nate dai referti 50:" in coda and "e altre 47" in coda
    # il caso peggiore sta nel canale: tutto l'output < 12 KB, le due sezioni ~7 KB
    assert len(nuovo.encode("utf-8")) < 12_000, len(nuovo.encode("utf-8"))
    assert len(coda.encode("utf-8")) < 8_000, len(coda.encode("utf-8"))
    # --json resta com'era: solo il documento
    assert cli.main(["--json"]) == 0
    js = capsys.readouterr().out
    assert "COME IMPARA IL TRAILING" not in js and "STORIA DEL LEARNING" not in js
    assert json.loads(js.split("\n[firebase]")[0])["meta"]["generato_da"] == "ops"


def test_il_comando_ops_regge_letture_che_falliscono(monkeypatch, capsys):
    from scripts import controllo as cli
    fb = _fb()
    vero_get_doc = fb.get_doc

    def get_doc(coll, doc_id, *a, **k):
        if (coll, doc_id) in (("learning", "ipotesi_storia"), ("gate_history", "lifecycle")):
            raise RuntimeError("quota esaurita")
        return vero_get_doc(coll, doc_id, *a, **k)
    monkeypatch.setattr(fb, "get_doc", get_doc)
    monkeypatch.setattr("bot.core.firebase_client.get_firebase", lambda: fb)
    monkeypatch.setattr(c.time, "time", lambda: NOW)
    assert cli.main([]) == 0
    out = capsys.readouterr().out
    assert "COME IMPARA IL TRAILING" in out and "PER STRATEGIA" in out
    assert "[lettura fallita] learning/ipotesi_storia: quota esaurita" in out
    assert "storia delle ipotesi (learning/ipotesi_storia) non disponibile" in out
    assert "mancano le foto del 24 set e del 25 set" in out


def test_una_sezione_che_esplode_non_porta_via_l_altra(monkeypatch, capsys):
    from scripts import controllo as cli
    fb = _fb()
    monkeypatch.setattr("bot.core.firebase_client.get_firebase", lambda: fb)
    monkeypatch.setattr(c.time, "time", lambda: NOW)
    monkeypatch.setattr(ap, "sezione_trailing", lambda *a, **k: 1 / 0)
    assert cli.main([]) == 0
    out = capsys.readouterr().out
    assert "COME IMPARA IL TRAILING\n  sezione non calcolata: ZeroDivisionError" in out
    assert "COSA IMPARANO LE STRATEGIE" in out


# --------------------------------------------------------------------------- #
# 7. il bot scrive la foto una volta al giorno                                  #
# --------------------------------------------------------------------------- #
class _Conta:
    """Un FirebaseClient in memoria che conta le scritture sotto /learning_giorni."""

    def __init__(self, fb):
        self.fb, self.scritte, self.cancellate = fb, [], []

    def __getattr__(self, nome):
        return getattr(self.fb, nome)

    def set_rtdb(self, path, data):
        if path.startswith(ap.FOTO_BASE):
            (self.cancellate if data is None else self.scritte).append(path)
        return self.fb.set_rtdb(path, data)


def test_il_bot_scrive_la_foto_una_volta_al_giorno(capsys):
    from bot.main import TradingBot
    fb = _Conta(_fb())
    bot = _finto_bot(fb)
    TradingBot._publish_controllo(bot, [], now=NOW)
    foto = fb.get_rtdb(f"/learning_giorni/{OGGI}")
    assert foto["giorno"] == OGGI and len(foto["validate"]) == 160 and foto["at"] == NOW
    assert bot._foto_learning == {"giorno": OGGI, "verificato": True}
    assert fb.scritte == [f"/learning_giorni/{OGGI}"] and len(fb.cancellate) == ap.FOTO_SPAZZATA_GIORNI
    assert f"[learning] foto del {OGGI} scritta: 160 validate" in capsys.readouterr().out
    # un'ora dopo, stesso giorno: il controllo si pubblica, la foto no
    TradingBot._publish_controllo(bot, [], now=NOW + 3600)
    assert fb.scritte == [f"/learning_giorni/{OGGI}"]
    # il giorno dopo: nuova foto e si cancella quella di 36 giorni prima
    TradingBot._publish_controllo(bot, [], now=NOW + 86400)
    assert fb.scritte[-1] == "/learning_giorni/2026-09-26"
    assert fb.cancellate[-1] == "/learning_giorni/2026-08-21"
    # riavvio: la foto di oggi c'e' gia' (foglia `at`) -> non si riscrive
    fb2 = _Conta(fb.fb)
    bot2 = _finto_bot(fb2)
    TradingBot._publish_controllo(bot2, [], now=NOW + 86400 + 7200)
    assert fb2.scritte == [] and bot2._foto_learning == {"giorno": "2026-09-26", "verificato": True}


def test_la_foto_non_solleva_mai_e_riprova_se_il_database_non_risponde(capsys):
    from bot.main import foto_learning_giorno
    dati = _dati()

    def giu(*a, **k):
        raise RuntimeError("RTDB giu'")
    rotto = SimpleNamespace(get_rtdb=giu, set_rtdb=giu)
    stato = foto_learning_giorno(rotto, dati, NOW, None)
    assert stato.get("giorno") is None
    assert "[learning] foto del giorno saltata: RTDB giu'" in capsys.readouterr().out
    # database vivo che non accetta la scrittura: il giorno NON si segna, si riprova all'ora dopo
    tentativi = []
    muto = SimpleNamespace(is_live=True, get_rtdb=lambda p: None,
                           set_rtdb=lambda p, d: tentativi.append(p) or False)
    stato = foto_learning_giorno(muto, dati, NOW, None)
    # `verificato` torna falso: al tentativo dopo si rilegge la foglia `at` (la
    # lettura di prima puo' essere venuta dallo specchio vuoto)
    assert stato == {"giorno": None, "verificato": False} and tentativi == [f"/learning_giorni/{OGGI}"]
    assert "non scritta (RTDB non risponde): si riprova fra un'ora" in capsys.readouterr().out
    stato = foto_learning_giorno(muto, dati, NOW + 3600, stato)
    assert len(tentativi) == 2
    # dati rotti: la funzione pura esplode, il bot no
    assert foto_learning_giorno(FirebaseClient(), {"registro": 5, "weights": {"weights": [1]}}, NOW,
                                None) is not None


# --------------------------------------------------------------------------- #
# 8. i verdetti portano la loro data                                            #
# --------------------------------------------------------------------------- #
def test_i_verdetti_portano_da_ora_la_loro_data():
    from tests.test_memoria_trade_misure import _bot_verdetti, _c, _stop_trade
    ex = 1_800_000_000.0
    b = _bot_verdetti(_stop_trade("15m", ex),
                      [_c(ex, 99.0, 97.9), _c(ex + 900, 98.0, 95.8), _c(ex + 1800, 99.0, 98.0)])
    b.evaluate_pending_trailing(ex + 3600)
    assert b.visto["doc"]["post_stop_verdict"] == "inversione"
    assert b.visto["doc"]["post_stop_verdict_at"] == ex + 3600
    t = _stop_trade("1h", ex)
    t["exit_reason"], t["exit_price"] = "trailing_stop", 104.0
    b = _bot_verdetti(t, [_c(ex - 3600, 105.0, 99.0), _c(ex, 104.5, 103.9), _c(ex + 3600, 106.0, 103.0),
                          _c(ex + 40 * 3600, 110.5, 105.0)])
    b.evaluate_pending_trailing(ex + 41 * 3600)
    assert b.visto["doc"]["trailing_verdict"] == "premature"
    assert b.visto["doc"]["trailing_verdict_at"] == ex + 41 * 3600


def test_verdetti_nuovi_usano_la_data_e_ripiegano_sull_uscita():
    trades = [
        _trailing(1, "premature", exit_ts=T_PRIMA, trailing_verdict_at=T_IERI),     # data vera: ieri
        _trailing(2, "protected", exit_ts=T_IERI),                                  # senza data: uscita
        _trade(3, -2.0, "stop_loss", exit_ts=T_PRIMA, post_stop_verdict="rumore",
               post_stop_verdict_at=T_STANOTTE),
        _trade(4, 5.0, "scale_out", exit_ts=T_IERI, trailing_verdict="neutral", trailing_verdict_at=T_IERI),
        _trade(5, 5.0, "take_profit", exit_ts=T_IERI, trailing_verdict="premature"),   # non e' un'uscita trailing
    ]
    t0, t1, _g = FIN["ieri"]
    n = ap.verdetti_nuovi(trades, t0, t1)
    assert n["trailing_stop"] == {"premature": 1, "protected": 1} and n["scale_out"] == {"neutral": 1}
    assert n["stimati"] == 1 and not n["stop_loss"]
    s0, s1, _g = FIN["stanotte"]
    assert ap.verdetti_nuovi(trades, s0, s1)["stop_loss"] == {"rumore": 1}


# --------------------------------------------------------------------------- #
# 10. i rilievi dei revisori del 29 set                                          #
# --------------------------------------------------------------------------- #
def test_la_soglia_della_panchina_e_quella_del_controllo():
    """Una copia a mano poteva divergere senza che nessun test lo dicesse."""
    assert ap.SOGLIA_PANCHINA is c.SOGLIA_PANCHINA


def test_un_peso_appena_sotto_la_soglia_resta_in_panchina_nella_foto():
    """0,4962 arrotondato a 2 decimali faceva 0,5: il report diceva «esce dalla
    panchina» mentre il bot (che decide sul peso vero) ce la teneva."""
    def foto(w, now):
        return ap.impronta_giorno({"weights": {"weights": [
            {"strategy": "gen_1", "regime": "sideways", "weight": w},
            {"strategy": "gen_2", "regime": "sideways", "weight": 0.123456}]}}, now)
    ieri, oggi = foto(0.45, NOW - 86400), foto(0.4962, NOW)
    assert oggi["pesi"]["gen_1|sideways"] < ap.SOGLIA_PANCHINA
    assert oggi["pesi"]["gen_2|sideways"] == 0.1235                 # 4 decimali, come il controllo
    d = ap.differenze(ieri, oggi)
    assert d["panchina_uscite"] == [] and d["panchina_entrate"] == []
    quasi = foto(0.49996, NOW)["pesi"]["gen_1|sideways"]
    assert quasi < ap.SOGLIA_PANCHINA                               # mai arrotondato oltre la soglia
    assert c.panchina({"weights": [{"strategy": "gen_1", "regime": "sideways",
                                    "weight": 0.4962}]})["in_panchina_n"] == 1


def test_i_verdetti_nuovi_di_altri_timeframe_sono_a_parte():
    """La riga a) conta solo il timeframe del bot: anche i «nuovi» lo fanno."""
    altro = "1h" if settings.ORCHESTRATOR_TIMEFRAME != "1h" else "4h"
    trades = [_trailing(1, "premature", exit_ts=T_PRIMA, trailing_verdict_at=T_STANOTTE, timeframe=altro)]
    s0, s1, g = FIN["stanotte"]
    n = ap.verdetti_nuovi(trades, s0, s1)
    assert not n["trailing_stop"] and n["altri_tf"] == {"premature": 1}
    assert ap.riassunto_verdetti(trades)["verdetti"] == 0
    riga = ap._riga_nuovi("stanotte", g, n)
    assert "+1 trailing su altri timeframe (non contano per le proposte)" in riga
    assert "trailing 1 prematuro" not in riga


def test_la_nota_sui_verdetti_senza_data_si_scrive_una_volta():
    trades = [_trailing(1, "protected", exit_ts=T_IERI), _trailing(2, "protected", exit_ts=T_STANOTTE)]
    testo = "\n".join(ap.sezione_trailing(_dati(trades=trades), NOW))
    assert testo.count("contati nel giorno di uscita del trade") == 1
    assert "(1 senza data, come sopra)" in testo


def test_incasso_parziale_e_dopo_gli_stop_solo_se_ci_sono():
    trades = _trade_del_29_set() + [
        _trade(700, 5.0, "scale_out", exit_ts=T_PRIMA, trailing_verdict="premature"),
        _trade(701, -2.0, "stop_loss", exit_ts=T_PRIMA, post_stop_verdict="inversione")]
    testo = "\n".join(ap.sezione_trailing(_dati(trades=trades), NOW))
    assert ("uscite dopo un incasso parziale (preso almeno il primo target, resto chiuso dallo "
            "stop): 1 verdetti") in testo
    assert "NON usati dalle proposte (se contarli non e' deciso)" in testo
    assert all(len(r) <= 220 for r in testo.splitlines()), max(testo.splitlines(), key=len)
    assert "dopo gli stop: 0 rumore" in testo and "entro la finestra" in testo


def test_la_distribuzione_non_nasconde_l_unica_voce_che_avanza():
    from collections import Counter
    conta = Counter({"non scelta": 160, "1/1.5/2.5": 14, "1/2/3": 11, "1.5/3/5": 8,
                     "1/1.25/1.75 (dal vissuto)": 6})
    testo = ap._distribuzione(conta, 3)
    assert "1/1.25/1.75 (dal vissuto) ×6" in testo and "altre" not in testo
    assert testo.startswith("non scelta ×160")                     # non occupa un posto
    conta["x"] = 1
    conta["y"] = 1
    assert "altre 2 (×2)" in ap._distribuzione(conta, 4)


def test_la_scala_dal_vissuto_si_vede_per_nome():
    dati = _dati(n_validate=6)
    reg = dati["registro"]
    pairs = json.loads(reg["pairs"])
    pairs["C0USDT|gen_0"]["last_params"]["scale_r_mults"] = [1.0, 1.25, 1.75]
    reg["pairs"] = encode_pairs(pairs)
    testo = "\n".join(ap.sezione_trailing(dati, NOW))
    assert "1/1.25/1.75 (dal vissuto) ×1" in testo and "dal vissuto in tutto: 1" in testo
    assert "stop spostato al prezzo d'ingresso dopo il primo incasso (break-even)" in testo


def test_le_piu_vicine_una_per_riga():
    testo = ap.sezione_trailing(_dati(), NOW)
    i = next(n for n, r in enumerate(testo) if "keep per strategia" in r)
    if testo[i].endswith("Le piu' vicine:"):
        assert testo[i + 1].startswith("       gen_") and "per 0," in testo[i + 1]
    # sul telefono: nessuna riga oltre ~5 righe di schermo (erano fino a 312 caratteri)
    assert all(len(r) <= 220 for r in testo), max(testo, key=len)


def test_letture_mancanti_riconosce_le_fonti_della_foto():
    dati = {"errori_lettura": ["fs:strategy_weights/current: 503 Service Unavailable",
                               "fs:ai_shadow: quota", "rtdb:/adapt_state: giu'"]}
    assert ap.letture_mancanti(dati) == ["fs:strategy_weights/current", "rtdb:/adapt_state"]
    assert ap.letture_mancanti({}) == [] and ap.letture_mancanti(None) == []


class _Flaky:
    """Firestore che fallisce le letture di pesi, referti ed esplorative."""

    def __init__(self, fb, rotte=(("strategy_weights", "current"), ("learning", "referti"),
                                  ("strategy_registry", "esplorative"))):
        self.fb, self.rotte, self.giu = fb, set(rotte), True

    def __getattr__(self, nome):
        return getattr(self.fb, nome)

    def get_doc(self, coll, doc_id, *a, **k):
        if self.giu and (coll, doc_id) in self.rotte:
            raise RuntimeError("503 Service Unavailable")
        return self.fb.get_doc(coll, doc_id, *a, **k)


def test_la_foto_non_si_scrive_con_letture_fallite_e_si_riprova(capsys):
    """RILIEVO: una foto coi buchi (pesi, referti, esplorative a vuoto) faceva
    inventare al report due mattine di cambi, e non si rifaceva piu'."""
    from bot.main import foto_learning_giorno
    fb = _Flaky(_fb())
    stato = foto_learning_giorno(fb, c.carica_dati(fb, NOW), NOW, None)
    assert stato.get("giorno") is None and fb.get_rtdb(f"{ap.FOTO_BASE}/{OGGI}") is None
    out = capsys.readouterr().out
    assert "foto del 2026-09-25 rimandata: letture fallite (fs:strategy_weights/current" in out
    # un'ora dopo le letture tornano: la foto si scrive, intera
    fb.giu = False
    stato = foto_learning_giorno(fb, c.carica_dati(fb, NOW + 3600), NOW + 3600, stato)
    foto = fb.get_rtdb(f"{ap.FOTO_BASE}/{OGGI}")
    assert stato["giorno"] == OGGI and foto["pesi"] and foto["at"] == NOW + 3600
    assert fb.get_rtdb(ap.FOTO_INDICE) == {OGGI: NOW + 3600}       # l'indice accanto alla foto


def test_il_report_non_confronta_uno_stato_di_adesso_coi_buchi(monkeypatch, capsys):
    from scripts import controllo as cli
    fb = _Flaky(_fb_pieno())
    monkeypatch.setattr("bot.core.firebase_client.get_firebase", lambda: fb)
    monkeypatch.setattr(c.time, "time", lambda: NOW)
    assert cli.main([]) == 0
    out = capsys.readouterr().out
    assert ("cambiato stanotte: non disponibile (stato di adesso incompleto: letture fallite "
            "(fs:strategy_weights/current") in out
    assert "ipotesi non piu' nei referti" not in out.split("STANOTTE (")[1]
    assert "cambiato ieri (foto 24 set 00:04 -> foto 25 set 00:05)" in out   # fra due foto: si'


class _RtdbGiu:
    """Client vivo col RTDB che non risponde: `get_rtdb` non solleva (ridà lo
    specchio, vuoto) e ogni chiamata sarebbe una richiesta ritentata."""
    is_live = True

    def __init__(self, fb):
        self.fb, self.rt = fb, []

    def __getattr__(self, nome):
        return getattr(self.fb, nome)

    def get_rtdb(self, path):
        self.rt.append(path)
        return None

    def degraded_for(self, now=None):
        return 300.0


def test_col_rtdb_muto_il_report_non_legge_le_foto_e_non_dice_che_mancano(capsys):
    from scripts import controllo as cli
    fb = _RtdbGiu(_fb())
    dati: dict = {}
    doc = c.esegui(fb, "ops", settings_da_bot=False, now=NOW, dati_out=dati)
    prima = len(fb.rt)
    cli.stampa_apprendimento(fb, dati, doc)
    out = capsys.readouterr().out
    assert len(fb.rt) == prima                          # nessuna lettura RTDB in piu'
    assert "RTDB non raggiungibile: foto non lette" in out
    assert "la storia non e' ancora partita" not in out and "mancano le foto" not in out


def test_l_ultima_foto_si_trova_con_una_lettura_dell_indice(capsys):
    """Prima: fino a 34 GET in fila. Ora l'indice {giorno: at} scritto dal bot."""
    from scripts import controllo as cli
    base = _fb()
    base.set_rtdb(f"{ap.FOTO_BASE}/{OGGI}", _foto(at=FIN["stanotte"][0] + 300, giorno=OGGI))
    base.set_rtdb(f"{ap.FOTO_INDICE}/2026-09-21", FIN["ieri"][0] - 3 * 86400)
    base.set_rtdb(f"{ap.FOTO_INDICE}/{OGGI}", FIN["stanotte"][0] + 300)

    class _Conta:
        def __init__(self, fb):
            self.fb, self.rt = fb, []

        def __getattr__(self, nome):
            return getattr(self.fb, nome)

        def get_rtdb(self, path):
            self.rt.append(path)
            return self.fb.get_rtdb(path)
    fb = _Conta(base)
    assert cli._ultima_foto(fb, NOW) == ("2026-09-21", FIN["ieri"][0] - 3 * 86400)
    assert fb.rt == [ap.FOTO_INDICE]
    dati: dict = {}
    doc = c.esegui(fb, "ops", settings_da_bot=False, now=NOW, dati_out=dati)
    cli.stampa_apprendimento(fb, dati, doc)
    out = capsys.readouterr().out
    assert "manca la foto del 24 set" in out and "l'ultima foto prima di oggi e' del 21 set" in out
    assert ap.ultima_dall_indice({}, OGGI) is None and ap.ultima_dall_indice(None, OGGI) is None


def test_riavvio_col_rtdb_giu_non_riscrive_la_foto_delle_00_05(capsys):
    """RILIEVO: al riavvio col RTDB giu' la foglia `at` letta dallo specchio
    (vuoto) diceva «foto assente»; un'ora dopo la foto delle 00:05 veniva
    riscritta con lo stato delle 15:00."""
    from bot.main import foto_learning_giorno
    at_vero = FIN["stanotte"][0] + 300
    remoto = {f"{ap.FOTO_BASE}/{OGGI}": {"at": at_vero, "giorno": OGGI}}

    class _Fb:
        is_live = True
        giu = True

        def get_rtdb(self, path):
            if self.giu:
                return None
            if path.endswith("/at"):
                return (remoto.get(path.rsplit("/", 1)[0]) or {}).get("at")
            return remoto.get(path)

        def set_rtdb(self, path, dati):
            if self.giu:
                return False
            remoto[path] = dati
            return True
    fb = _Fb()
    stato = foto_learning_giorno(fb, _dati(), NOW, None)           # 14:00, RTDB giu'
    assert stato == {"giorno": None, "verificato": False}
    fb.giu = False
    stato = foto_learning_giorno(fb, _dati(), NOW + 3600, stato)   # 15:00, RTDB tornato
    assert remoto[f"{ap.FOTO_BASE}/{OGGI}"]["at"] == at_vero        # non riscritta
    assert stato == {"giorno": OGGI, "verificato": True}
    # col client vero (che sa dire se il RTDB e' muto) non si tenta nemmeno
    tentativi = []

    class _Degradato(_Fb):
        def degraded_for(self, now=None):
            return 120.0 if self.giu else 0.0

        def set_rtdb(self, path, dati):
            tentativi.append(path)
            return super().set_rtdb(path, dati)
    fb2 = _Degradato()
    stato = foto_learning_giorno(fb2, _dati(), NOW, None)
    assert tentativi == [] and stato == {"giorno": None, "verificato": False}
    assert "rimandata: RTDB non risponde" in capsys.readouterr().out


# --------------------------------------------------------------------------- #
# 9. niente identificativi di modelli nei file nuovi                            #
# --------------------------------------------------------------------------- #
def test_nessun_identificativo_di_modello_nei_file_nuovi():
    radice = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    vietato = "claude" + "-"
    for rel in ("bot/learning/apprendimento.py", "tests/test_apprendimento.py"):
        with open(os.path.join(radice, rel), encoding="utf-8") as f:
            assert vietato not in f.read().lower(), rel


def test_default_repo_come_li_legge_il_report():
    # le righe dicono i default: se cambiassero, il report li cambia da solo
    testo = "\n".join(ap.sezione_trailing(_dati(), NOW))
    assert f"(default {ap._k(settings.PROFIT_LOCK_KEEP)})" in testo
