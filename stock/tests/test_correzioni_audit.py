"""Le correzioni del percorso degli ordini dopo l'audit del 27 novembre 2026 (`stock/AUDIT_2026-11-27.md`, sezione 3), su casi costruiti
a mano: conto finto, orologio finto, nessun collegamento ad Alpaca."""
import json
from datetime import date

import pandas as pd
import pytest
import requests

from stock.avanti import avanti as av
from stock.avanti import conto
from stock.avanti import gamma as ga
from stock.avanti import miscela as mi
from stock.dati import alpaca

NY = "America/New_York"


class Risposta:
    def __init__(self, codice, corpo=None):
        self.status_code, self._corpo = codice, corpo
        self.text = json.dumps(corpo) if corpo is not None else ""

    def json(self):
        return self._corpo


# ---- le richieste al conto (A8, A14) e la ricerca per nome (A9) ------------------------------------------------------

def test_una_risposta_429_si_ritenta_e_poi_passa(monkeypatch):
    risposte = [Risposta(429, {"m": "troppe"}), Risposta(429, {"m": "troppe"}), Risposta(200, {"ok": 1})]
    monkeypatch.setattr(av.requests, "request", lambda *a, **k: risposte.pop(0))
    monkeypatch.setattr(av.time, "sleep", lambda s: None)
    monkeypatch.setattr(alpaca, "_intestazioni", dict)
    assert av._richiesta("GET", "/v2/account") == {"ok": 1}


def test_un_ordine_con_il_nome_dopo_un_errore_di_rete_non_parte_due_volte(monkeypatch):
    chiamate = []

    def rete(metodo, url, **k):
        chiamate.append((metodo, url))
        if metodo == "POST":
            raise requests.ConnectionError("giù")             # il primo tentativo è arrivato, la risposta no
        return Risposta(200, {"id": "gia", "status": "accepted"})

    monkeypatch.setattr(av.requests, "request", rete)
    monkeypatch.setattr(av.time, "sleep", lambda s: None)
    monkeypatch.setattr(alpaca, "_intestazioni", dict)
    o = av._richiesta("POST", "/v2/orders", json={"symbol": "AAA", "client_order_id": "candela15-2026-11-30-AAA"})
    assert o["id"] == "gia"
    assert sum(1 for m, _ in chiamate if m == "POST") == 1                  # cercato per nome, non rimandato


def test_un_ordine_senza_nome_non_si_ritenta_dopo_un_errore_di_rete(monkeypatch):
    def rete(metodo, url, **k):
        raise requests.ConnectionError("giù")

    monkeypatch.setattr(av.requests, "request", rete)
    monkeypatch.setattr(alpaca, "_intestazioni", dict)
    with pytest.raises(alpaca.ErroreAlpaca, match="non si ritenta"):
        av._richiesta("POST", "/v2/orders", json={"symbol": "AAA"})


def test_la_ricerca_per_nome_distingue_il_404_dagli_altri_errori(monkeypatch):
    monkeypatch.setattr(av.time, "sleep", lambda s: None)
    monkeypatch.setattr(av, "_richiesta", lambda *a, **k: (_ for _ in ()).throw(alpaca.ErroreAlpaca("404 su x: non c'è")))
    assert av._ordine_per_nome("n") is None
    monkeypatch.setattr(av, "_richiesta", lambda *a, **k: (_ for _ in ()).throw(alpaca.ErroreAlpaca("rete su x: Timeout")))
    with pytest.raises(alpaca.ErroreAlpaca):
        av._ordine_per_nome("n")


# ---- il diario: uscite parziali (A6), righe aperte (A1), giorni fuori regola nella tabella (A19) -----------------------

def _es(oid, sim, lato, q, p, t="t"):
    return {"symbol": sim, "side": lato, "qty": str(q), "price": str(p), "transaction_time": t, "order_id": oid}


ORDINE = {"simbolo": "AAA", "lato": "buy", "quantita": 100, "stop": 99, "obiettivo": 120, "riferimento": 100, "id": "o1"}


def test_un_uscita_parziale_conta_solo_la_parte_chiusa():
    r = av.operazioni_del_giorno("2026-11-30", [ORDINE], [_es("o1", "AAA", "buy", 100, 100), _es("g1", "AAA", "sell", 40, 99)],
                                 {"g1": "stop"})[0]
    assert r["uscita"] == "parziale" and r["guadagno"] == pytest.approx(-40.0)
    assert r["proporzione"] == pytest.approx(-0.01) and "resto aperto" in r["nota"]


def test_le_uscite_in_piu_non_contano_oltre_l_ingresso():
    es = [_es("o1", "AAA", "buy", 100, 100), _es("g1", "AAA", "sell", 100, 101), _es("x", "AAA", "sell", 100, 101)]
    r = av.operazioni_del_giorno("2026-11-30", [ORDINE], es, {"g1": "obiettivo"})[0]
    assert r["guadagno"] == pytest.approx(100.0) and "da guardare" in r["nota"]


def test_le_righe_aperte_dei_giorni_prima_fermano_gli_ordini():
    d = pd.DataFrame([{"giorno": "2026-11-27", "simbolo": "AAA", "uscita": "aperta"},
                      {"giorno": "2026-11-27", "simbolo": "BBB", "uscita": "stop"},
                      {"giorno": "2026-11-30", "simbolo": "CCC", "uscita": "aperta"}], columns=av.COLONNE)
    assert av.righe_aperte_prima("2026-11-30", d) == ["2026-11-27 AAA"]


def test_la_tabella_del_riepilogo_non_conta_il_giorno_fuori_regola(monkeypatch, tmp_path):
    monkeypatch.setattr(av, "QUI", tmp_path)
    righe = [{"giorno": g, "simbolo": "AAA", "lato": "buy", "quantita": 10, "ingresso": 100.0, "guadagno": x, "proporzione": x / 1000,
              "commissione_ib": 2.0} for g, x in (("2026-11-10", 50.0), ("2026-11-11", -500.0), ("2026-11-12", 30.0))]
    t = av.scrivi_riepilogo(pd.DataFrame(righe, columns=av.COLONNE))
    assert "| 2026-11-07 | 2 | +80.00 |" in t and "-500" not in t.split("| Settimana")[1]


# ---- dopo le 20:00 niente ordini fuori orario (A7) ------------------------------------------------------------------

def test_dopo_le_20_le_posizioni_aspettano_le_4():
    seduta = {"apertura": pd.Timestamp("2026-11-30 09:30", tz=NY), "chiusura": pd.Timestamp("2026-11-30 16:00", tz=NY)}
    assert av.cosa_fare(pd.Timestamp("2026-11-30 19:30", tz=NY), seduta, True, True, True) == "fuori_orario"
    assert av.cosa_fare(pd.Timestamp("2026-11-30 20:05", tz=NY), seduta, True, True, True).startswith("niente: posizioni aperte dopo")
    assert av.nelle_ore_fuori_seduta(pd.Timestamp("2026-11-30 04:00", tz=NY))
    assert not av.nelle_ore_fuori_seduta(pd.Timestamp("2026-11-30 20:00", tz=NY))


# ---- una posizione della prima candela rimasta di notte (A1) ---------------------------------------------------------

D, D1 = "2026-11-27", "2026-11-30"
STATO = {"dal": "2026-11-12", "conto_alla_partenza": 200_000.0, "candela_alla_partenza": 100_000.0}


def test_la_posizione_rimasta_si_chiude_con_il_nome_e_completa_la_riga_del_suo_giorno(monkeypatch, tmp_path):
    monkeypatch.setattr(av, "QUI", tmp_path)
    (tmp_path / "giorni").mkdir()
    (tmp_path / "giorni" / f"{D}.json").write_text(json.dumps({"giorno": D, "ordini": [ORDINE]}))
    pd.DataFrame([{"giorno": D, "simbolo": "AAA", "lato": "buy", "quantita": 100, "ingresso": 100.0, "uscita": "aperta"}],
                 columns=av.COLONNE).to_csv(tmp_path / "diario.csv", index=False)
    posizioni = [{"symbol": "AAA", "qty": "100"}]
    mandati = []
    ordini_alpaca = [{"id": "o1", "client_order_id": f"candela15-{D}-AAA", "symbol": "AAA", "side": "buy", "filled_qty": "100",
                      "filled_avg_price": "100"}]

    def richiesta(metodo, percorso, **k):
        if metodo == "GET" and percorso == "/v2/orders":
            return list(ordini_alpaca)
        if metodo == "GET" and percorso.startswith("/v2/orders/"):
            return {"legs": []}
        raise AssertionError((metodo, percorso))

    def limite(sim, q, giorno, nome=None):
        mandati.append(nome)
        ordini_alpaca.append({"id": "r1", "client_order_id": nome, "symbol": sim, "side": "sell", "filled_qty": "100",
                              "filled_avg_price": "105", "filled_at": f"{D1}T12:05:00Z"})
        return {"id": "r1", "status": "accepted", "_limite": 104.5}

    monkeypatch.setattr(av, "_richiesta", richiesta)
    monkeypatch.setattr(av, "ny_adesso", lambda: pd.Timestamp(f"{D1} 07:00", tz=NY))
    monkeypatch.setattr(av.time, "sleep", lambda s: posizioni.clear())         # dopo un minuto la vendita è eseguita
    monkeypatch.setattr(av, "_cancella_ordini_candela", lambda **k: None)
    monkeypatch.setattr(av, "_posizioni_candela", lambda: list(posizioni))
    monkeypatch.setattr(av, "_ordine_limite_fuori_orario", limite)
    monkeypatch.setattr(av, "esecuzioni_del_giorno", lambda g: [_es("o1", "AAA", "buy", 100, 100.0)] if g == D else [])
    monkeypatch.setattr(av, "_plancia", lambda *a, **k: "plancia")
    assert "ingresso del 2026-11-27" in av.chiudi_rimaste(D1, in_seduta=False)
    assert mandati[0].startswith(f"candela-rim-{D}-AAA-")
    riga = pd.read_csv(tmp_path / "diario.csv").iloc[0]
    assert riga["guadagno"] == pytest.approx(500.0) and riga["uscita"] == "giorno dopo"
    assert av.righe_aperte_prima(D1) == []


def test_il_capitale_di_oggi_conta_solo_i_titoli_entrati_oggi():
    # D1: la chiusura di una rimasta (nome «candela-rim-») e una chiusura a mano di un'altra rimasta (BBB, senza nome) non sono un
    # guadagno di oggi; una posizione rimasta ancora aperta (CCC) conta con il non realizzato, non con tutto il suo valore
    diario = pd.DataFrame([{"giorno": D, "simbolo": "AAA", "lato": "buy", "quantita": 100, "ingresso": 100.0, "uscita_prezzo": 105.0,
                            "guadagno": 500.0, "uscita": "giorno dopo"}], columns=av.COLONNE)
    es = [_es("r1", "AAA", "sell", 100, 105.0), _es("m1", "BBB", "sell", 50, 200.0), _es("e1", "DDD", "buy", 10, 50.0)]
    pos = [{"symbol": "CCC", "qty": "20", "market_value": "2000", "unrealized_pl": "-40"},
           {"symbol": "DDD", "qty": "10", "market_value": "510", "unrealized_pl": "10"}]
    c = conto.classifica([{"id": "r1", "client_order_id": f"candela-rim-{D}-AAA-070000", "symbol": "AAA"},
                          {"id": "e1", "client_order_id": f"candela15-{D1}-DDD", "symbol": "DDD", "filled_qty": "10"}], D1)
    assert c["entrate_candela"] == {"DDD"} and c["rimaste"] == {"r1"} and c["entrata_gamma"] is False
    candela, _ = conto.valori(200_000.0, pos, diario, STATO, oggi=D1, esecuzioni_oggi=es, escludi=c["rimaste"],
                              entrate_oggi=c["entrate_candela"])
    tasse = conto.TASSA_VENDITE * 100 * 105.0
    assert candela == pytest.approx(100_000.0 + 500.0 - tasse + (-500.0 + 510.0) + (-40.0))
    senza, _ = conto.valori(200_000.0, pos, diario.iloc[0:0], STATO, oggi=D1, esecuzioni_oggi=es)
    assert senza > 120_000                                                        # com'era prima: le vendite come guadagno


def test_la_prova_45_senza_ingresso_di_oggi_conta_la_posizione_con_il_non_realizzato():
    pos = [{"symbol": "VOO", "qty": "160", "market_value": "96000", "unrealized_pl": "-80"}]
    dg = pd.DataFrame([{"giorno": D, "guadagno": float("nan")}])
    assert conto.valore_gamma(pos, dg, D1, [], set(), False) == pytest.approx(100_000 - 80)
    assert conto.valore_gamma(pos, dg, D1, [], set(), None) == pytest.approx(100_000 + 96_000)   # il conto di prima


def test_completa_righe_riscrive_una_riga_aperta_quando_l_uscita_arriva_tardi(monkeypatch, tmp_path):
    monkeypatch.setattr(av, "QUI", tmp_path)
    (tmp_path / "giorni").mkdir()
    (tmp_path / "giorni" / f"{D}.json").write_text(json.dumps({"giorno": D, "ordini": [ORDINE]}))
    pd.DataFrame([{"giorno": D, "simbolo": "AAA", "lato": "buy", "quantita": 100, "ingresso": 100.0, "uscita": "aperta"}],
                 columns=av.COLONNE).to_csv(tmp_path / "diario.csv", index=False)
    # l'ordine fuori orario del 27 si è eseguito dopo il controllo dei 60 secondi: ora c'è fra le esecuzioni del giorno
    monkeypatch.setattr(av, "esecuzioni_del_giorno", lambda g: [_es("o1", "AAA", "buy", 100, 100.0), _es("fo", "AAA", "sell", 100, 99.0)])
    monkeypatch.setattr(av, "_posizioni_candela", list)
    monkeypatch.setattr(av, "_richiesta", lambda m, p, **k: {"legs": [], "client_order_id": f"candela-fo-{D}-AAA-160100"})
    assert av.completa_righe(D1) == [D]
    assert pd.read_csv(tmp_path / "diario.csv").iloc[0]["guadagno"] == pytest.approx(-100.0) and av.righe_aperte_prima(D1) == []


def test_apri_con_una_riga_aperta_si_ferma_con_l_allarme_e_il_lavoro_rosso(monkeypatch, tmp_path):
    monkeypatch.setattr(av, "QUI", tmp_path)
    pd.DataFrame([{"giorno": D, "simbolo": "AAA", "uscita": "aperta"}], columns=av.COLONNE).to_csv(tmp_path / "diario.csv", index=False)
    seduta = {"apertura": pd.Timestamp(f"{D1} 09:30", tz=NY), "chiusura": pd.Timestamp(f"{D1} 16:00", tz=NY)}
    monkeypatch.setattr(av, "seduta_di_oggi", lambda: seduta)
    monkeypatch.setattr(av, "ny_adesso", lambda: pd.Timestamp(f"{D1} 09:45:10", tz=NY))
    monkeypatch.setattr(av, "elenco", lambda: ["AAA"])
    monkeypatch.setattr(av, "completa_righe", lambda oggi: [])
    pubblicati = []
    monkeypatch.setattr(av, "_plancia", lambda a=None: pubblicati.append(a) or "plancia")
    with pytest.raises(alpaca.ErroreAlpaca, match="righe del diario ancora aperte"):
        av.apri()
    assert "contabilita" in pubblicati[0] and pubblicati[0]["contabilita"]["testo"]


def test_la_riga_dei_valori_si_scrive_anche_la_mattina_dopo_ma_non_dopo_l_apertura():
    sedute = [{"apertura": pd.Timestamp(f"{g} 09:30", tz=NY), "chiusura": pd.Timestamp(f"{g} {c}", tz=NY)}
              for g, c in ((D, "13:00"), (D1, "16:00"))]
    assert av.ultima_seduta_da_registrare(pd.Timestamp(f"{D} 19:30", tz=NY), sedute)["giorno"] == D
    assert av.ultima_seduta_da_registrare(pd.Timestamp(f"{D1} 08:15", tz=NY), sedute)["giorno"] == D       # la mattina dopo
    assert av.ultima_seduta_da_registrare(pd.Timestamp(f"{D1} 10:00", tz=NY), sedute) is None              # dopo l'apertura no
    assert av.ultima_seduta_da_registrare(pd.Timestamp(f"{D1} 16:30", tz=NY), sedute)["giorno"] == D1


def test_l_elenco_del_mese_non_si_scrive_con_un_guasto_passeggero(monkeypatch, tmp_path):
    monkeypatch.setattr(av, "QUI", tmp_path)
    pd.DataFrame({"simbolo": [f"T{i:03d}" for i in range(150)]}).to_csv(tmp_path / "sp500_membri.csv", index=False)

    def gruppo(simboli, *a, **k):
        if "T000" in simboli:
            raise alpaca.ErroreAlpaca("503 su /v2/stocks/bars: unavailable")
        return {s: pd.DataFrame({"close": [1.0] * 70, "volume": [1.0] * 70}) for s in simboli}

    def uno(s, *a, **k):
        raise alpaca.ErroreAlpaca("503 su x: giù")

    monkeypatch.setattr(alpaca, "barre_di_piu", gruppo)
    monkeypatch.setattr(alpaca, "barre", uno)
    with pytest.raises(alpaca.ErroreAlpaca, match="non scritto"):
        av.elenco("2026-12")
    assert not (tmp_path / "elenco_2026-12.csv").exists()


def test_miscela_una_ricerca_per_nome_fallita_non_ferma_il_fondo_dopo(monkeypatch):
    mandati = []

    def post(metodo, percorso, **k):
        mandati.append(k["json"]["symbol"])
        if k["json"]["symbol"] == "SPY":
            raise alpaca.ErroreAlpaca("rete su /v2/orders: Timeout")
        return {"status": "accepted"}

    def cerca(nome):
        raise alpaca.ErroreAlpaca("rete su x: Timeout")

    monkeypatch.setattr(av, "_richiesta", post)
    monkeypatch.setattr(av, "_ordine_per_nome", cerca)
    fatti, bene = mi.manda({"SPY": -10, "QQQ": -5}, "day", "fed-giorno-2026-12-09")
    assert mandati == ["SPY", "QQQ"] and not bene and "DA VERIFICARE" in fatti[0]
    monkeypatch.setattr(av, "_richiesta", lambda *a, **k: {"status": "rejected"})
    assert mi.manda({"SPY": 3}, "day", "x")[1] is False                              # trovato per nome ma morto: non conta


def test_prova_45_l_allarme_resta_dopo_il_diario(monkeypatch, tmp_path):
    monkeypatch.setattr(ga, "GIORNI", tmp_path / "gamma_giorni")
    pubblicate = []
    monkeypatch.setattr(ga, "_cancella_ordini_gamma", lambda: None)
    monkeypatch.setattr(ga, "posizione", lambda: -160.0)
    monkeypatch.setattr(ga, "_ordine_fuori_orario", lambda q, g, nome=None: {"id": "fo"})
    monkeypatch.setattr(ga.time, "sleep", lambda s: None)
    monkeypatch.setattr(ga, "scrivi_diario", lambda g: pubblicate.append(None) or "diario")
    monkeypatch.setattr(ga, "pubblica", lambda a=None: pubblicate.append(a) or "plancia")
    with pytest.raises(alpaca.ErroreAlpaca, match="ANCORA APERTA"):
        ga.fuori_orario(D1)
    assert pubblicate[-1] is not None and "VOO ancora aperta" in pubblicate[-1]["testo"]


# ---- i valori di fine giornata alla chiusura ufficiale (A10) ---------------------------------------------------------

def test_la_correzione_alla_chiusura_ufficiale():
    pos = [{"symbol": "SPY", "qty": "10", "current_price": "601"}, {"symbol": "QQQ", "qty": "4", "current_price": "500"}]
    assert conto.correzione_alla_chiusura(pos, {"SPY": 600.0, "QQQ": 502.0}) == pytest.approx(-10 + 8)
    assert conto.correzione_alla_chiusura(pos, {"SPY": 600.0}) is None


def test_i_valori_aspettano_venti_minuti_dopo_la_fine(monkeypatch, tmp_path):
    monkeypatch.setattr(conto, "VALORI", tmp_path / "valori.csv")
    monkeypatch.setattr(av, "ny_adesso", lambda: pd.Timestamp("2026-11-30 16:05", tz=NY))
    esito = conto.registra("2026-11-30", pd.Timestamp("2026-11-30 16:00", tz=NY))
    assert "si aspettano le chiusure ufficiali" in esito


def test_le_tasse_sulle_vendite_vanno_a_chi_vende():
    d = pd.DataFrame([{"lato": "buy", "quantita": 100, "ingresso": 50.0, "uscita_prezzo": 60.0, "guadagno": 1000.0},
                      {"lato": "sell", "quantita": 10, "ingresso": 100.0, "uscita_prezzo": 90.0, "guadagno": 100.0},
                      {"lato": "buy", "quantita": 5, "ingresso": 10.0, "uscita_prezzo": float("nan"), "guadagno": float("nan")}])
    assert conto.tasse_vendite(d) == pytest.approx(conto.TASSA_VENDITE * (100 * 60.0 + 10 * 100.0))


# ---- la miscela: settimana e mese dall'ultima decisione salvata (A4), gruppi che falliscono (A3) ---------------------------

def test_se_salta_la_sera_di_venerdi_la_calma_si_decide_lunedi():
    # giovedì 26 nov la sera decide per venerdì 27 (settimana 48); la sera di venerdì salta; lunedì 30 la prossima è martedì 1 dic
    st = {"settimana_calma": mi.settimana(date(2026, 11, 27)), "mese_ampiezza": "2026-11"}
    dec = mi.decisioni(date(2026, 11, 30), date(2026, 12, 1), st)
    assert dec["calma"] and dec["ampiezza"]                                     # il 30 è anche l'ultimo giorno del mese
    assert dec["note"] == ["calma decisa in ritardo: la sera di fine settimana era saltata"]      # solo la calma è in ritardo
    # se salta anche la sera del 30, il 1° dicembre si decide l'ampiezza in ritardo
    assert mi.decisioni(date(2026, 12, 1), date(2026, 12, 2), {"settimana_calma": mi.settimana(date(2026, 12, 1)),
                                                               "mese_ampiezza": "2026-11"})["note"] == [
        "ampiezza decisa in ritardo: la sera di fine mese era saltata"]
    st2 = {"settimana_calma": mi.settimana(date(2026, 12, 1)), "mese_ampiezza": "2026-12"}
    assert not any((d := mi.decisioni(date(2026, 12, 1), date(2026, 12, 2), st2))[k] for k in ("calma", "ampiezza")) and not d["note"]
    # senza le chiavi nello stato vale la regola di prima: venerdì sera per lunedì sì, mercoledì sera per giovedì no
    assert mi.decisioni(date(2026, 11, 27), date(2026, 11, 30), {})["calma"]
    assert not mi.decisioni(date(2026, 11, 25), date(2026, 11, 27), {})["calma"]


def test_un_gruppo_che_fallisce_si_riprova_un_titolo_alla_volta(monkeypatch):
    def gruppo(simboli, *a, **k):
        raise alpaca.ErroreAlpaca("422 su /v2/stocks/bars: invalid symbol: ZZZZ")

    def uno(s, *a, **k):
        if s == "ZZZZ":
            raise alpaca.ErroreAlpaca("422 su /v2/stocks/bars: invalid symbol")
        return pd.DataFrame({"close": [1.0]})

    monkeypatch.setattr(alpaca, "barre_di_piu", gruppo)
    monkeypatch.setattr(alpaca, "barre", uno)
    out = av.barre_a_gruppi(["AAA", "ZZZZ", "BBB"], "1Day", None, None)
    assert sorted(out) == ["AAA", "BBB"]


# ---- la prova 45: uscite di altri giorni, parziali, nome dell'ordine fuori orario (A1, A6, A8, A17) -----------------------

def test_prova_45_un_uscita_di_un_altro_giorno_non_e_un_uscita_di_oggi():
    dec = {"id_ingresso": "in", "lato": "buy", "nota": ""}
    es = [_es("in", "VOO", "buy", 160, 600.0), _es("vecchia", "VOO", "sell", 150, 598.0), _es("asta", "VOO", "sell", 160, 601.0)]
    r = ga.riga_operazione("2026-11-30", dec, es, escludi={"vecchia"})
    assert r["guadagno"] == pytest.approx(160.0) and "da guardare" not in r["nota"]
    r2 = ga.riga_operazione("2026-11-30", dec, es[:2])
    assert r2["uscita"] == "parziale" and r2["guadagno"] == pytest.approx(-300.0)


def test_prova_45_l_ordine_fuori_orario_ha_un_nome_e_i_giorni_senza_operazione_si_pubblicano(monkeypatch, tmp_path):
    corpi = []
    monkeypatch.setattr(ga, "ultimo_prezzo", lambda s: 600.0)
    monkeypatch.setattr(av, "_richiesta", lambda m, p, **k: corpi.append(k["json"]) or {"id": "fo"})
    monkeypatch.setattr(av, "ny_adesso", lambda: pd.Timestamp("2026-11-30 16:30", tz=NY))
    ga._ordine_fuori_orario(-160, "2026-11-30")
    assert corpi[0]["client_order_id"] == "gamma-2026-11-30-fo-163000" and corpi[0]["side"] == "buy"
    pubblicate = []
    monkeypatch.setattr(ga, "GIORNI", tmp_path / "gamma_giorni")
    monkeypatch.setattr(ga, "DIARIO", tmp_path / "gamma_diario.csv")
    monkeypatch.setattr(ga, "pubblica", lambda *a, **k: pubblicate.append(1) or "plancia")
    ga.decidi_senza_ordine({"giorno": "2026-11-30", "copertura_del": "2026-11-27", "copertura": "sopra zero"}, "niente: copertura sopra zero")
    assert pubblicate == [1]


# ---- i membri dell'S&P 500 (A3) ---------------------------------------------------------------------------------------

def test_i_membri_si_leggono_dalla_tabella_e_una_lettura_strana_non_passa():
    from stock.avanti import membri
    lettere = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    simboli = [a + b for a in lettere for b in lettere][:500] + ["BRK.B", "BF-B"]
    righe = "".join(f"<tr><td>{s}</td><td>x</td></tr>" for s in simboli)
    html = f"<table><tr><th>Symbol</th><th>Security</th></tr>{righe}</table>"
    letti = membri.dalla_pagina(html)
    assert len(letti) == 502 and "BRK.B" in letti and "BF.B" in letti
    with pytest.raises(ValueError):
        membri.dalla_pagina("<table><tr><th>Symbol</th></tr><tr><td>AAPL</td></tr></table>")
