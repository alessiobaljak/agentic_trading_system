"""Le correzioni dopo il secondo giro di revisione separata del 27 novembre 2026 (`stock/avanti/REVISIONE_AUDIT.md`), su casi costruiti
a mano: conto finto, orologio finto, nessun collegamento ad Alpaca."""
import json

import pandas as pd
import pytest

from stock.avanti import avanti as av
from stock.avanti import conto
from stock.avanti import gamma as ga
from stock.dati import alpaca

NY = "America/New_York"
D, D1 = "2026-11-30", "2026-12-01"
STATO = {"dal": "2026-11-12", "conto_alla_partenza": 200_000.0, "candela_alla_partenza": 100_000.0}


class Risposta:
    def __init__(self, codice, corpo=None):
        self.status_code, self._corpo = codice, corpo
        self.text = json.dumps(corpo) if corpo is not None else ""

    def json(self):
        return self._corpo


def _es(oid, sim, lato, q, p, t="t"):
    return {"symbol": sim, "side": lato, "qty": str(q), "price": str(p), "transaction_time": t, "order_id": oid}


ORDINE = {"simbolo": "AAA", "lato": "buy", "quantita": 100, "stop": 99, "obiettivo": 120, "riferimento": 100, "id": "o1"}


# ---- le richieste: errori passeggeri del server, la scadenza, il 429 -------------------------------------------------

def test_un_503_su_una_lettura_si_ritenta(monkeypatch):
    risposte = [Risposta(503, {"m": "giù"}), Risposta(200, [{"id": "x"}])]
    monkeypatch.setattr(av.requests, "request", lambda *a, **k: risposte.pop(0))
    monkeypatch.setattr(av.time, "sleep", lambda s: None)
    monkeypatch.setattr(alpaca, "_intestazioni", dict)
    assert av._richiesta("GET", "/v2/orders") == [{"id": "x"}]


def test_un_503_su_un_ordine_senza_nome_non_si_ritenta(monkeypatch):
    chiamate = []
    monkeypatch.setattr(av.requests, "request", lambda *a, **k: chiamate.append(a) or Risposta(503, {"m": "giù"}))
    monkeypatch.setattr(av.time, "sleep", lambda s: None)
    monkeypatch.setattr(alpaca, "_intestazioni", dict)
    with pytest.raises(alpaca.ErroreAlpaca, match="503"):
        av._richiesta("POST", "/v2/orders", json={"symbol": "AAA"})
    assert len(chiamate) == 1
    chiamate.clear()
    with pytest.raises(alpaca.ErroreAlpaca, match="503"):
        av._richiesta("DELETE", "/v2/positions/AAA")                            # chiudere una posizione non si ripete
    assert len(chiamate) == 1


def test_un_503_su_un_ordine_con_nome_cerca_per_nome_prima_di_rimandare(monkeypatch):
    chiamate = []

    def rete(metodo, url, **k):
        chiamate.append(metodo)
        if metodo == "POST":
            return Risposta(503, {"m": "giù"})
        return Risposta(200, {"id": "gia", "status": "accepted"})                # il server l'aveva eseguito

    monkeypatch.setattr(av.requests, "request", rete)
    monkeypatch.setattr(av.time, "sleep", lambda s: None)
    monkeypatch.setattr(alpaca, "_intestazioni", dict)
    assert av._richiesta("POST", "/v2/orders", json={"client_order_id": "candela15-x-AAA"})["id"] == "gia"
    assert chiamate.count("POST") == 1


def test_dopo_la_scadenza_un_ordine_non_si_rimanda(monkeypatch):
    chiamate = []

    def rete(metodo, url, **k):
        chiamate.append(metodo)
        if metodo == "POST":
            return Risposta(503, {"m": "giù"})
        return Risposta(404, {"m": "non c'è"})

    monkeypatch.setattr(av.requests, "request", rete)
    monkeypatch.setattr(av.time, "sleep", lambda s: None)
    monkeypatch.setattr(alpaca, "_intestazioni", dict)
    monkeypatch.setattr(av, "ny_adesso", lambda: pd.Timestamp(f"{D} 10:01", tz=NY))
    with pytest.raises(alpaca.ErroreAlpaca, match="tempo scaduto"):
        av._richiesta("POST", "/v2/orders", json={"client_order_id": "candela15-x-AAA"}, scadenza=pd.Timestamp(f"{D} 10:00", tz=NY))
    assert chiamate.count("POST") == 1


def test_il_429_si_ritenta_per_circa_un_minuto(monkeypatch):
    attese = []
    risposte = [Risposta(429, {})] * 4 + [Risposta(200, {"ok": 1})]
    monkeypatch.setattr(av.requests, "request", lambda *a, **k: risposte.pop(0))
    monkeypatch.setattr(av.time, "sleep", attese.append)
    monkeypatch.setattr(alpaca, "_intestazioni", dict)
    assert av._richiesta("GET", "/v2/account") == {"ok": 1}
    assert 50 <= sum(attese) <= 70


# ---- l'ingresso delle 9:45: l'ora si ricontrolla prima di ogni ordine ----------------------------------------------

def test_apri_non_manda_ordini_dopo_le_10_anche_a_meta_del_giro(monkeypatch, tmp_path):
    monkeypatch.setattr(av, "QUI", tmp_path)
    s = {"apertura": pd.Timestamp(f"{D} 09:30", tz=NY), "chiusura": pd.Timestamp(f"{D} 16:00", tz=NY)}
    orologio = [pd.Timestamp(f"{D} 09:45:05", tz=NY)]
    monkeypatch.setattr(av, "seduta_di_oggi", lambda: s)
    monkeypatch.setattr(av, "ny_adesso", lambda: orologio[0])
    monkeypatch.setattr(av, "elenco", lambda: ["AAA", "BBB"])
    monkeypatch.setattr(av, "completa_righe", lambda oggi: [])
    monkeypatch.setattr(av, "_plancia", lambda a=None: "plancia")
    monkeypatch.setattr(conto, "adesso", lambda: {"candela": 100_000.0, "posizioni_candela": []})
    minuti = pd.date_range(f"{D} 09:30", periods=15, freq="1min", tz=NY)
    barre = [{"t": t.tz_convert("UTC").isoformat(), "o": 100 + i * 0.1, "h": 101 + i * 0.1, "l": 99.5, "c": 100.5 + i * 0.1, "v": 1, "n": 1, "vw": 100.0}
             for i, t in enumerate(minuti)]
    monkeypatch.setattr(alpaca, "_get", lambda url, p: {"bars": {"AAA": barre, "BBB": barre}})
    mandati = []

    def post(metodo, percorso, **k):
        mandati.append(k["json"]["symbol"])
        orologio[0] = pd.Timestamp(f"{D} 10:05", tz=NY)          # il primo ordine ha impiegato 20 minuti (Alpaca muta)
        return {"id": "o-AAA", "submitted_at": f"{D}T14:45:06Z"}

    monkeypatch.setattr(av, "_richiesta", post)
    av.apri()
    assert mandati == ["AAA"]
    ordini = json.loads((tmp_path / "giorni" / f"{D}.json").read_text())["ordini"]
    assert ordini[1]["simbolo"] == "BBB" and ordini[1]["nota"].startswith("saltato: troppo tardi")


# ---- le posizioni rimaste: il comando fuori orario e la chiusura che ha dato errore ------------------------------------

def test_il_comando_chiudi_fuori_orario_su_una_rimasta_usa_il_nome_rim(monkeypatch):
    chiamato = []
    monkeypatch.setattr(av, "ny_adesso", lambda: pd.Timestamp(f"{D1} 08:00", tz=NY))
    monkeypatch.setattr(av, "_ordini_dal", lambda g, **k: [])
    monkeypatch.setattr(av, "_posizioni_candela", lambda: [{"symbol": "AAA", "qty": "100"}])
    monkeypatch.setattr(av, "chiudi_rimaste", lambda oggi, in_seduta: chiamato.append(("rim", in_seduta)) or "rim")
    monkeypatch.setattr(av, "chiudi_fuori_orario", lambda: chiamato.append("fo") or "fo")
    assert av.chiudi_fuori_orario_a_mano() == "rim" and chiamato == [("rim", False)]
    monkeypatch.setattr(av, "_ordini_dal", lambda g, **k: [{"client_order_id": f"candela15-{D1}-AAA", "symbol": "AAA", "filled_qty": "100"}])
    chiamato.clear()
    assert av.chiudi_fuori_orario_a_mano() == "fo"                                # entrata oggi: la chiusura di sempre


def test_una_rimasta_con_la_risposta_persa_ma_l_ordine_arrivato_non_e_non_chiusa(monkeypatch, tmp_path):
    monkeypatch.setattr(av, "QUI", tmp_path)
    posizioni = [{"symbol": "AAA", "qty": "100"}]
    monkeypatch.setattr(av, "ny_adesso", lambda: pd.Timestamp(f"{D1} 07:00", tz=NY))
    monkeypatch.setattr(av, "_cancella_ordini_candela", lambda **k: None)
    monkeypatch.setattr(av, "_posizioni_candela", lambda: list(posizioni))
    monkeypatch.setattr(av, "giorno_d_ingresso", lambda s, q, p: D)

    def limite(sim, q, giorno, nome=None):
        raise alpaca.ErroreAlpaca("422 su /v2/orders: client_order_id must be unique")

    monkeypatch.setattr(av, "_ordine_limite_fuori_orario", limite)
    monkeypatch.setattr(av, "_ordine_per_nome", lambda nome: {"id": "r1", "status": "filled", "client_order_id": nome})
    monkeypatch.setattr(av.time, "sleep", lambda s: posizioni.clear())
    monkeypatch.setattr(av, "_plancia", lambda a=None: "plancia")
    scritti = []
    monkeypatch.setattr(av, "scrivi_diario", lambda g: scritti.append(g) or "diario")
    esito = av.chiudi_rimaste(D1, in_seduta=False)
    assert "NON CHIUSO" not in esito and "trovato per nome" in esito and scritti == [D]


# ---- il diario della prima candela: uscite fuori orario per nome, giorni mancanti ------------------------------------

def test_un_uscita_fuori_orario_datata_nel_giorno_dopo_entra_lo_stesso_nella_riga(monkeypatch, tmp_path):
    monkeypatch.setattr(av, "QUI", tmp_path)
    (tmp_path / "giorni").mkdir()
    (tmp_path / "giorni" / f"{D}.json").write_text(json.dumps({"giorno": D, "ordini": [ORDINE]}))
    monkeypatch.setattr(av, "esecuzioni_del_giorno", lambda g: [_es("o1", "AAA", "buy", 100, 100.0)])   # l'uscita non c'è
    fo = {"id": "fo1", "client_order_id": f"candela-fo-{D}-AAA-193000", "symbol": "AAA", "side": "sell", "filled_qty": "100",
          "filled_avg_price": "101", "filled_at": f"{D1}T00:30:00Z"}
    monkeypatch.setattr(av, "_ordini_dal", lambda g, **k: [fo])
    monkeypatch.setattr(av, "_richiesta", lambda m, p, **k: {"legs": []})
    av.scrivi_diario(D)
    riga = pd.read_csv(tmp_path / "diario.csv").iloc[0]
    assert riga["uscita"] == "chiusura" and riga["guadagno"] == pytest.approx(100.0)
    # se invece l'uscita c'è fra le esecuzioni del giorno non si conta due volte
    monkeypatch.setattr(av, "esecuzioni_del_giorno", lambda g: [_es("o1", "AAA", "buy", 100, 100.0), _es("fo1", "AAA", "sell", 100, 101.0)])
    av.scrivi_diario(D)
    assert pd.read_csv(tmp_path / "diario.csv").iloc[0]["guadagno"] == pytest.approx(100.0)


def test_un_giorno_senza_righe_nel_diario_ferma_la_candela_e_si_ricompone(monkeypatch, tmp_path):
    monkeypatch.setattr(av, "QUI", tmp_path)
    (tmp_path / "giorni").mkdir()
    (tmp_path / "giorni" / f"{D}.json").write_text(json.dumps({"giorno": D, "ordini": [ORDINE]}))
    pd.DataFrame(columns=av.COLONNE).to_csv(tmp_path / "diario.csv", index=False)
    assert av.giorni_senza_righe(D1) == [D] and av.giorni_senza_righe(D) == []
    fatti = []
    monkeypatch.setattr(av, "_posizioni_candela", list)
    monkeypatch.setattr(av, "scrivi_diario", lambda g: fatti.append(g))
    assert av.completa_righe(D1) == [D] and fatti == [D]


# ---- il conto: le chiusure «rim» con i file vecchi, la riga segnaposto -----------------------------------------------

def test_con_il_diario_vecchio_la_chiusura_rim_di_oggi_resta_alla_prima_candela():
    diario = pd.DataFrame([{"giorno": D, "simbolo": "AAA", "lato": "buy", "quantita": 100, "ingresso": 100.0, "uscita": "aperta"}],
                          columns=av.COLONNE)
    ordini = [{"id": "r1", "client_order_id": f"candela-rim-{D}-AAA-043000", "symbol": "AAA", "side": "sell", "filled_qty": "100",
               "filled_avg_price": "104.9"}]
    es = [_es("r1", "AAA", "sell", 100, 104.9)]
    c = conto.classifica(ordini, D1)
    candela, miscela = conto.valori(200_000.0 + 490.0, [], diario, STATO, oggi=D1, esecuzioni_oggi=es, escludi=c["rimaste"],
                                    entrate_oggi=c["entrate_candela"], ordini_oggi=ordini)
    assert candela == pytest.approx(100_490.0) and miscela == pytest.approx(100_000.0)
    # con il diario già completato non si conta due volte
    fatto = diario.assign(uscita="giorno dopo", uscita_prezzo=104.9, guadagno=490.0)
    candela2, _ = conto.valori(200_000.0 + 490.0, [], fatto, STATO, oggi=D1, esecuzioni_oggi=es, escludi=c["rimaste"],
                               entrate_oggi=c["entrate_candela"], ordini_oggi=ordini)
    assert candela2 == pytest.approx(100_490.0 - conto.TASSA_VENDITE * 100 * 104.9)


def test_la_riga_segnaposto_della_prova_45_non_toglie_il_flusso_di_oggi():
    dg = pd.DataFrame([{"giorno": D1, "simbolo": "VOO", "quantita": float("nan"), "guadagno": float("nan"),
                        "nota": f"chiusa la posizione rimasta del {D}"}])
    # oggi: entrate 160 a 600, uscite 60 a 605 a mercato; restano 100 (valore 60'500, non realizzato 500): il guadagno di oggi è 800
    pos = [{"symbol": "VOO", "qty": "100", "market_value": "60500", "unrealized_pl": "500"}]
    es = [_es("in", "VOO", "buy", 160, 600.0), _es("m1", "VOO", "sell", 60, 605.0)]
    assert conto.valore_gamma(pos, dg, D1, es, set(), True) == pytest.approx(100_000 + 800)


def test_i_valori_non_si_scrivono_con_una_riga_aperta_del_giorno(monkeypatch, tmp_path):
    monkeypatch.setattr(conto, "QUI", tmp_path)
    monkeypatch.setattr(conto, "VALORI", tmp_path / "valori.csv")
    monkeypatch.setattr(conto, "DIARIO_GAMMA", tmp_path / "gamma_diario.csv")
    pd.DataFrame([{"giorno": D, "uscita": "aperta", "guadagno": float("nan")}]).to_csv(tmp_path / "gamma_diario.csv", index=False)
    pd.DataFrame(columns=av.COLONNE).to_csv(tmp_path / "diario.csv", index=False)
    monkeypatch.setattr(av, "_richiesta", lambda m, p, **k: [])
    monkeypatch.setattr(ga, "riga_mancante", lambda g: False)
    assert "righe aperte" in conto.registra(D)
    # una riga ferma da più giorni non blocca per sempre
    pd.DataFrame([{"giorno": "2026-11-20", "uscita": "aperta", "guadagno": float("nan")}]).to_csv(tmp_path / "gamma_diario.csv",
                                                                                                    index=False)
    monkeypatch.setattr(conto, "adesso", lambda: {"posizioni_candela": [], "posizioni_gamma": [], "posizioni_miscela": [],
                                                  "conto": 200_000.0, "candela": 100_000.0, "miscela": 100_000.0, "gamma": 100_000.0})
    assert conto.registra(D).startswith(f"valori del {D}:")


def test_la_fotografia_del_conto_si_rilegge_se_le_posizioni_cambiano(monkeypatch, tmp_path):
    monkeypatch.setattr(conto, "QUI", tmp_path)
    monkeypatch.setattr(conto, "STATO", tmp_path / "stato.json")
    monkeypatch.setattr(conto, "DIARIO_GAMMA", tmp_path / "gamma_diario.csv")
    (tmp_path / "stato.json").write_text(json.dumps(STATO))
    letture = [[{"symbol": "AAA", "qty": "100", "market_value": "10000", "unrealized_pl": "0"}], [], [], []]
    esecuzioni = [[_es("o1", "AAA", "buy", 100, 100.0)], [_es("o1", "AAA", "buy", 100, 100.0), _es("s1", "AAA", "sell", 100, 98.0)]]

    def richiesta(m, p, **k):
        return {"equity": "199800"} if p == "/v2/account" else letture.pop(0)

    monkeypatch.setattr(av, "_richiesta", richiesta)
    monkeypatch.setattr(av, "ny_adesso", lambda: pd.Timestamp(f"{D} 14:00", tz=NY))
    monkeypatch.setattr(av, "esecuzioni_del_giorno", lambda g: esecuzioni.pop(0))
    monkeypatch.setattr(av, "_ordini_dal", lambda g, **k: [{"id": "o1", "client_order_id": f"candela15-{D}-AAA", "symbol": "AAA",
                                                            "filled_qty": "100", "legs": [{"id": "s1"}, {"id": "t1"}]}])
    v = conto.adesso()
    assert v["candela"] == pytest.approx(100_000.0 - 200.0)                     # lo stop contato una volta sola


# ---- la prova 45: riga aperta senza posizione, righe di prima aperte, il comando «chiudi» -----------------------------

def test_prova_45_una_riga_aperta_senza_posizione_non_e_scritta(monkeypatch, tmp_path):
    monkeypatch.setattr(ga, "DIARIO", tmp_path / "gamma_diario.csv")
    monkeypatch.setattr(ga, "GIORNI", tmp_path / "gamma_giorni")
    (tmp_path / "gamma_giorni").mkdir()
    (tmp_path / "gamma_giorni" / f"{D}.json").write_text(json.dumps({"giorno": D, "id_ingresso": "in"}))
    pd.DataFrame([{"giorno": D, "simbolo": "VOO", "quantita": 160, "uscita": "aperta"}], columns=ga.COLONNE).to_csv(
        tmp_path / "gamma_diario.csv", index=False)
    monkeypatch.setattr(ga, "posizione", lambda: 0.0)
    assert ga.diario_scritto(D) is False
    monkeypatch.setattr(ga, "posizione", lambda: 160.0)
    assert ga.diario_scritto(D) is True


def test_prova_45_non_entra_con_una_riga_di_prima_aperta(monkeypatch, tmp_path):
    monkeypatch.setattr(ga, "DIARIO", tmp_path / "gamma_diario.csv")
    monkeypatch.setattr(ga, "GIORNI", tmp_path / "gamma_giorni")
    pd.DataFrame([{"giorno": D, "simbolo": "VOO", "quantita": 160, "uscita": "aperta"}], columns=ga.COLONNE).to_csv(
        tmp_path / "gamma_diario.csv", index=False)
    oggi = {"giorno": pd.Timestamp(D1).date(), "apertura": pd.Timestamp(f"{D1} 09:30", tz=NY),
            "chiusura": pd.Timestamp(f"{D1} 16:00", tz=NY)}
    ieri = {"giorno": pd.Timestamp(D).date(), "chiusura": pd.Timestamp(f"{D} 16:00", tz=NY)}
    monkeypatch.setattr(av, "ny_adesso", lambda: pd.Timestamp(f"{D1} 15:30:05", tz=NY))
    monkeypatch.setattr(ga, "scarica_copertura", lambda: "")
    monkeypatch.setattr(ga, "copertura", lambda t, g: -1.0)
    monkeypatch.setattr(ga, "chiusura_di_ieri", lambda i: 600.0)
    monkeypatch.setattr(ga, "chiusura_del_segnale", lambda i: 601.0)
    monkeypatch.setattr(ga, "posizione", lambda: 0.0)
    pubblicate = []
    monkeypatch.setattr(ga, "pubblica", lambda a=None: pubblicate.append(a) or "plancia")
    monkeypatch.setattr(ga, "manda", lambda *a, **k: pytest.fail("nessun ordine"))
    assert "righe del diario ancora aperte" in ga.entra(oggi, ieri)
    assert pubblicate[-1] and D in pubblicate[-1]["testo"]


def test_prova_45_una_riga_con_l_ingresso_non_eseguito_non_si_riscrive_a_ogni_avvio(monkeypatch, tmp_path):
    monkeypatch.setattr(ga, "DIARIO", tmp_path / "gamma_diario.csv")
    monkeypatch.setattr(ga, "GIORNI", tmp_path / "gamma_giorni")
    (tmp_path / "gamma_giorni").mkdir()
    (tmp_path / "gamma_giorni" / f"{D}.json").write_text(json.dumps({"giorno": D, "id_ingresso": "in", "lato": "buy",
                                                                     "nota": "ingresso rejected: eseguite 0 su 160"}))
    pd.DataFrame([{"giorno": D, "simbolo": "VOO", "nota": "ingresso rejected: eseguite 0 su 160"}], columns=ga.COLONNE).to_csv(
        tmp_path / "gamma_diario.csv", index=False)
    monkeypatch.setattr(ga, "posizione", lambda: 0.0)
    monkeypatch.setattr(av, "esecuzioni_del_giorno", lambda g: pytest.fail("non si rilegge"))
    assert ga.completa_righe(D1) == []


def test_prova_45_il_comando_chiudi_non_tocca_la_posizione_di_oggi(monkeypatch):
    monkeypatch.setattr(av, "ny_adesso", lambda: pd.Timestamp(f"{D1} 08:00", tz=NY))
    monkeypatch.setattr(ga, "posizione", lambda: 160.0)
    monkeypatch.setattr(av, "_ordini_dal", lambda g, **k: [{"client_order_id": f"gamma-{D1}-in", "symbol": "VOO", "filled_qty": "160"}])
    monkeypatch.setattr(ga, "chiudi_rimasta", lambda *a, **k: pytest.fail("non si chiude"))
    assert "entrata oggi" in ga.chiudi_a_mano()
    monkeypatch.setattr(av, "_ordini_dal", lambda g, **k: [])
    monkeypatch.setattr(ga, "sedute", lambda: [{"giorno": pd.Timestamp(D1).date(), "apertura": pd.Timestamp(f"{D1} 09:30", tz=NY),
                                                "chiusura": pd.Timestamp(f"{D1} 16:00", tz=NY)}])
    monkeypatch.setattr(ga, "chiudi_rimasta", lambda oggi, in_seduta: f"rim {in_seduta}")
    assert ga.chiudi_a_mano() == "rim False"                                    # alle 8:00: fuori orario, con il nome «gamma-rim-»


# ---- terzo giro: le uscite fuori orario di un altro giorno, la riga segnaposto, i giorni senza righe, la chiusura con un 503 ----

def test_una_vendita_fuori_orario_di_ieri_datata_oggi_non_e_guadagno_di_oggi():
    # Alpaca data in UTC: la vendita delle 19:30 di ieri (ordine di ieri) è fra le esecuzioni di oggi; oggi AAA è rientrata
    es = [_es("fo-ieri", "AAA", "sell", 100, 98.0), _es("in", "AAA", "buy", 97, 101.0)]
    ordini = [{"id": "in", "client_order_id": f"candela15-{D1}-AAA", "symbol": "AAA", "filled_qty": "97", "legs": [{"id": "s"}]}]
    pos = [{"symbol": "AAA", "qty": "97", "market_value": "9797", "unrealized_pl": "0"}]
    c = conto.classifica(ordini, D1)
    candela, _ = conto.valori(200_000.0, pos, pd.DataFrame(columns=av.COLONNE), STATO, oggi=D1, esecuzioni_oggi=es,
                              escludi=c["rimaste"], entrate_oggi=c["entrate_candela"], ordini_oggi=ordini)
    assert candela == pytest.approx(100_000.0 + 9797 - 97 * 101.0)


def test_il_diario_di_oggi_toglie_la_vendita_fuori_orario_di_ieri(monkeypatch, tmp_path):
    monkeypatch.setattr(av, "QUI", tmp_path)
    (tmp_path / "giorni").mkdir()
    (tmp_path / "giorni" / f"{D1}.json").write_text(json.dumps({"giorno": D1, "ordini": [{**ORDINE, "quantita": 40}]}))
    es = [_es("fo-ieri", "AAA", "sell", 50, 209.0), _es("o1", "AAA", "buy", 40, 205.0), _es("g1", "AAA", "sell", 40, 207.0)]
    monkeypatch.setattr(av, "esecuzioni_del_giorno", lambda g: es)
    monkeypatch.setattr(av, "_ordini_dal", lambda g, **k: [])

    def richiesta(m, p, **k):
        if p == "/v2/orders/o1":
            return {"legs": [{"id": "g1", "type": "limit"}]}
        return {"client_order_id": f"candela-fo-{D}-AAA-193000"}

    monkeypatch.setattr(av, "_richiesta", richiesta)
    av.scrivi_diario(D1)
    riga = pd.read_csv(tmp_path / "diario.csv").iloc[0]
    assert riga["guadagno"] == pytest.approx(80.0) and str(riga["nota"]) in ("", "nan")


def test_prova_45_la_riga_segnaposto_di_un_giorno_con_l_ingresso_si_rifa(monkeypatch, tmp_path):
    monkeypatch.setattr(ga, "DIARIO", tmp_path / "gamma_diario.csv")
    monkeypatch.setattr(ga, "GIORNI", tmp_path / "gamma_giorni")
    (tmp_path / "gamma_giorni").mkdir()
    (tmp_path / "gamma_giorni" / f"{D}.json").write_text(json.dumps({"giorno": D, "id_ingresso": "in", "lato": "buy", "id_asta": "a"}))
    pd.DataFrame([{"giorno": D, "simbolo": "VOO", "nota": "chiusa la posizione rimasta del 2026-11-27"}], columns=ga.COLONNE).to_csv(
        tmp_path / "gamma_diario.csv", index=False)
    assert ga.riga_mancante(D)
    monkeypatch.setattr(ga, "posizione", lambda: 0.0)
    monkeypatch.setattr(av, "esecuzioni_del_giorno", lambda g: [_es("in", "VOO", "buy", 160, 600.0), _es("a", "VOO", "sell", 160, 603.3)])
    monkeypatch.setattr(av, "_ordini_dal", lambda g, **k: [])
    assert ga.completa_righe(D1) == [D]
    assert pd.read_csv(tmp_path / "gamma_diario.csv").iloc[0]["guadagno"] == pytest.approx(528.0) and not ga.riga_mancante(D)


def test_i_valori_non_si_scrivono_con_un_giorno_senza_righe(monkeypatch, tmp_path):
    monkeypatch.setattr(conto, "QUI", tmp_path)
    monkeypatch.setattr(conto, "VALORI", tmp_path / "valori.csv")
    monkeypatch.setattr(conto, "DIARIO_GAMMA", tmp_path / "gamma_diario.csv")
    monkeypatch.setattr(av, "QUI", tmp_path)
    (tmp_path / "giorni").mkdir()
    (tmp_path / "giorni" / f"{D}.json").write_text(json.dumps({"giorno": D, "ordini": [ORDINE]}))
    pd.DataFrame(columns=av.COLONNE).to_csv(tmp_path / "diario.csv", index=False)
    monkeypatch.setattr(av, "_richiesta", lambda m, p, **k: [])
    monkeypatch.setattr(ga, "riga_mancante", lambda g: False)
    assert "non ha ancora le righe" in conto.registra(D)
    monkeypatch.setattr(ga, "riga_mancante", lambda g: g == D)
    (tmp_path / "giorni" / f"{D}.json").unlink()
    assert "non ha ancora le righe" in conto.registra(D)


# ---- i test che il revisore delle regressioni ha chiesto (terzo giro) -------------------------------------------------

def test_un_429_su_un_ingresso_dopo_le_10_non_si_rimanda(monkeypatch):
    chiamate = []
    orologio = [pd.Timestamp(f"{D} 09:59:50", tz=NY)]

    def rete(metodo, url, **k):
        chiamate.append(orologio[0])
        return Risposta(429, {"m": "troppe"})

    def dormi(x):
        orologio[0] += pd.Timedelta(seconds=x)

    monkeypatch.setattr(av.requests, "request", rete)
    monkeypatch.setattr(av.time, "sleep", dormi)
    monkeypatch.setattr(alpaca, "_intestazioni", dict)
    monkeypatch.setattr(av, "ny_adesso", lambda: orologio[0])
    with pytest.raises(alpaca.ErroreAlpaca, match="tempo scaduto"):
        av._richiesta("POST", "/v2/orders", json={"client_order_id": f"candela15-{D}-AAA"}, scadenza=pd.Timestamp(f"{D} 10:00", tz=NY))
    assert chiamate and max(chiamate) <= pd.Timestamp(f"{D} 10:00", tz=NY)          # nessun invio dopo le 10:00


def test_una_rimasta_alle_15_59_20_si_chiude_con_il_limite_fuori_orario(monkeypatch):
    s = {"apertura": pd.Timestamp(f"{D1} 09:30", tz=NY), "chiusura": pd.Timestamp(f"{D1} 16:00", tz=NY)}
    posizioni = [{"symbol": "AAA", "qty": "100"}]
    limiti, mercato = [], []
    monkeypatch.setattr(av, "seduta_di_oggi", lambda: s)
    monkeypatch.setattr(av, "ny_adesso", lambda: pd.Timestamp(f"{D1} 15:59:20", tz=NY))
    monkeypatch.setattr(av, "_cancella_ordini_candela", lambda **k: None)
    monkeypatch.setattr(av, "_posizioni_candela", lambda: list(posizioni))
    monkeypatch.setattr(av, "giorno_d_ingresso", lambda sim, q, p: D)
    monkeypatch.setattr(av, "_ordine_limite_fuori_orario", lambda sim, q, g, nome=None: limiti.append(nome) or {"_limite": 1.0})
    monkeypatch.setattr(av, "_richiesta", lambda *a, **k: mercato.append(a) or {})
    monkeypatch.setattr(av.time, "sleep", lambda x: posizioni.clear())
    monkeypatch.setattr(av, "_plancia", lambda a=None: "plancia")
    monkeypatch.setattr(av, "scrivi_diario", lambda g: "diario")
    av.chiudi_rimaste(D1, in_seduta=True)
    assert mercato == [] and limiti[0].startswith(f"candela-rim-{D}-AAA-")


def test_prova_45_la_chiusura_rim_di_oggi_resta_alla_prova_con_il_diario_vecchio():
    dg = pd.DataFrame([{"giorno": D, "simbolo": "VOO", "lato": "buy", "quantita": 160, "ingresso": 600.0, "uscita": "aperta"}],
                      columns=ga.COLONNE)
    ordini = [{"id": "r1", "client_order_id": f"gamma-rim-{D}-084000", "symbol": "VOO", "side": "sell", "filled_qty": "160",
               "filled_avg_price": "606.675"}]
    c = conto.classifica(ordini, D1)
    v = conto.valore_gamma([], dg, D1, [_es("r1", "VOO", "sell", 160, 606.675)], c["rimaste"], c["entrata_gamma"], ordini)
    assert v == pytest.approx(100_000 + 1_068)


def test_prova_45_la_vendita_fuori_orario_di_ieri_datata_oggi_non_e_flusso_di_oggi():
    ordini = [{"id": "in", "client_order_id": f"gamma-{D1}-in", "symbol": "VOO", "filled_qty": "160"}]
    es = [_es("fo-ieri", "VOO", "sell", 160, 600.0), _es("in", "VOO", "buy", 160, 601.0)]
    pos = [{"symbol": "VOO", "qty": "160", "market_value": "96320", "unrealized_pl": "160"}]
    v = conto.valore_gamma(pos, pd.DataFrame(columns=ga.COLONNE), D1, es, set(), True, ordini)
    assert v == pytest.approx(100_000 + 96_320 - 160 * 601.0)


def test_il_comando_chiudi_fuori_orario_passa_dalla_scelta_delle_rimaste():
    import inspect
    assert '"chiudi_fuori_orario": chiudi_fuori_orario_a_mano' in inspect.getsource(av)
    assert '"chiudi": chiudi_a_mano' in inspect.getsource(ga)


# ---- la seduta prima dal calendario (28 novembre 2026) ---------------------------------------------------------------

def test_la_seduta_prima_di_registra_viene_dal_calendario():
    sedute = [{"apertura": pd.Timestamp(f"{g} 09:30", tz=NY), "chiusura": pd.Timestamp(f"{g} 16:00", tz=NY)}
              for g in ("2026-11-25", "2026-11-28")]                            # in mezzo la festa (finta) del 26-27
    g = av.ultima_seduta_da_registrare(pd.Timestamp("2026-11-28 17:00", tz=NY), sedute)
    assert g["giorno"] == "2026-11-28" and g["prima"] == "2026-11-25"


def test_registra_guarda_la_seduta_prima_del_calendario(monkeypatch, tmp_path):
    monkeypatch.setattr(conto, "QUI", tmp_path)
    monkeypatch.setattr(conto, "VALORI", tmp_path / "valori.csv")
    monkeypatch.setattr(conto, "DIARIO_GAMMA", tmp_path / "gamma_diario.csv")
    # la riga aperta è del 25 novembre; il 26 è festa: con il giorno feriale prima (il 26) non si vedrebbe
    pd.DataFrame([{"giorno": "2026-11-25", "uscita": "aperta", "guadagno": float("nan")}]).to_csv(tmp_path / "gamma_diario.csv",
                                                                                                    index=False)
    pd.DataFrame(columns=av.COLONNE).to_csv(tmp_path / "diario.csv", index=False)
    monkeypatch.setattr(av, "_richiesta", lambda m, p, **k: [])
    monkeypatch.setattr(ga, "riga_mancante", lambda g: False)
    assert "righe aperte" in conto.registra("2026-11-27", prima="2026-11-25")
