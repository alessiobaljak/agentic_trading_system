"""La prova 45 sul demo (stock/avanti/gamma.py) e il conto condiviso a tre: le regole pure, su casi costruiti a mano."""
from datetime import date

import pandas as pd
import pytest

from stock.avanti import conto
from stock.avanti import gamma as ga

NY = "America/New_York"


def test_copertura_del_giorno_prima_e_mancante():
    testo = "date,price,dix,gex\n2026-11-19,6000,0.4,-900000.5\n2026-11-20,6010,0.41,1200000\n2026-11-21,6010,0.41,\n"
    assert ga.copertura(testo, date(2026, 11, 19)) == pytest.approx(-900000.5)
    assert ga.copertura(testo, date(2026, 11, 20)) > 0
    assert ga.copertura(testo, date(2026, 11, 21)) is None                  # valore vuoto
    assert ga.copertura(testo, date(2026, 11, 22)) is None                  # giorno che manca


def test_direzione_e_quantita():
    assert ga.direzione(600.0, 603.0) == (pytest.approx(0.005), "buy")
    assert ga.direzione(600.0, 597.0)[1] == "sell"
    assert ga.direzione(600.0, 600.0)[1] is None
    assert ga.quantita(100_000, 550.0) == 178                               # 98'000 / 550 = 178,2: azioni intere


def test_cosa_fare_a_ogni_ora():
    t = lambda h: pd.Timestamp(f"2026-11-24 {h}", tz=NY)
    sed = {"apertura": t("09:30"), "chiusura": t("16:00")}
    f = ga.cosa_fare
    assert f(t("10:40"), sed, False, False, False).startswith("niente: troppo presto")   # più di 4 ore e 30 prima delle 15:30
    assert f(t("11:05"), sed, False, False, False) == "entra"               # in anticipo: aspetta le 15:30
    assert f(t("15:34"), sed, False, False, False) == "entra"
    assert f(t("15:36"), sed, False, False, False) == "tardi"               # più di 5 minuti dopo: il giorno si salta
    assert f(t("16:05"), sed, False, False, False) == "tardi"               # nessun avvio in tempo: si scrive
    assert f(t("15:31"), sed, True, True, False) == "segui"                 # posizione aperta: l'asta, poi il controllo
    assert f(t("16:01"), sed, True, True, False) == "segui"                 # l'asta può essere ancora in arrivo
    assert f(t("16:03"), sed, True, True, False) == "fuori_orario"          # dopo la chiusura ancora aperta: mai la notte
    assert f(t("16:03"), sed, True, False, False) == "diario"
    assert f(t("16:03"), sed, True, False, True).startswith("niente")
    assert f(t("15:40"), sed, True, False, True).startswith("niente")       # deciso senza ordine (copertura sopra zero)
    assert f(t("11:00"), sed, False, True, False) == "chiudi_subito"        # posizione di un altro giorno: via subito
    assert f(t("07:00"), sed, False, True, False) == "fuori_orario"         # prima dell'apertura: ordini fuori orario
    assert f(t("11:00"), None, False, False, False).startswith("niente: oggi la borsa è chiusa")


def test_chiusura_anticipata_ingresso_mezzora_prima():
    t = lambda h: pd.Timestamp(f"2026-11-27 {h}", tz=NY)
    sed = {"apertura": t("09:30"), "chiusura": t("13:00")}
    assert ga.cosa_fare(t("08:40"), sed, False, False, False) == "entra"    # alle 12:30
    assert ga.cosa_fare(t("12:36"), sed, False, False, False) == "tardi"
    assert ga.cosa_fare(t("13:03"), sed, True, True, False) == "fuori_orario"


def _es(order_id, side, qty, price, ora="2026-11-24T20:30:01Z"):
    return {"symbol": "VOO", "order_id": order_id, "side": side, "qty": str(qty), "price": str(price), "transaction_time": ora}


def test_riga_operazione_vendita_uscita_all_asta():
    dec = {"giorno": "2026-11-24", "copertura_del": "2026-11-23", "copertura": "sotto zero", "r": -0.004, "lato": "sell",
           "id_ingresso": "A", "id_asta": "B", "scarto_ingresso_pb": 0.3}
    es = [_es("A", "sell_short", 100, 600.0), _es("A", "sell_short", 60, 600.5),
          _es("B", "buy", 160, 598.0, "2026-11-24T21:00:00Z"), {**_es("X", "buy", 5, 1.0), "symbol": "SPY"}]
    r = ga.riga_operazione("2026-11-24", dec, es)
    p_in = (100 * 600.0 + 60 * 600.5) / 160
    assert r["quantita"] == 160 and r["ingresso"] == pytest.approx(round(p_in, 4))
    assert r["guadagno"] == pytest.approx(round((p_in - 598.0) * 160, 2))   # venduta allo scoperto: guadagna se scende
    assert r["uscita"] == "asta" and r["copertura"] == "sotto zero" and r["simbolo"] == "VOO"
    assert r["commissione_ib"] == pytest.approx(2.0)                        # 160 azioni: il minimo di 1 dollaro per lato


def test_riga_operazione_uscita_a_mercato_e_ingresso_non_eseguito():
    dec = {"giorno": "2026-11-24", "lato": "buy", "id_ingresso": "A", "uscite": {"C": "mercato"},
           "nota": "ordine alla chiusura rifiutato: uscita a mercato"}
    r = ga.riga_operazione("2026-11-24", dec, [_es("A", "buy", 10, 600.0), _es("C", "sell", 10, 601.0)])
    assert r["uscita"] == "mercato" and r["guadagno"] == pytest.approx(10.0) and "rifiutato" in r["nota"]
    assert ga.riga_operazione("2026-11-24", dec, [])["nota"].startswith("ordine alla chiusura")   # nessuna esecuzione: nota


def test_conto_a_tre_la_prima_candela_non_tocca_voo():
    assert conto.della_candela("AAPL") and not conto.della_candela("VOO") and not conto.della_candela("SPY")
    pos = [{"symbol": "VOO", "qty": "-160"}, {"symbol": "SPY", "qty": "37"}, {"symbol": "AAPL", "qty": "20"}]
    pc, pm = conto.separa(pos)
    assert [p["symbol"] for p in pc] == ["AAPL"] and [p["symbol"] for p in pm] == ["SPY"]
    assert [p["symbol"] for p in conto.di_gamma(pos)] == ["VOO"]


def test_conto_a_tre_il_guadagno_della_prova_45_non_va_alla_miscela():
    diario = pd.DataFrame({"giorno": ["2026-11-13"], "guadagno": [100.0]})
    stato = {"dal": "2026-11-12", "conto_alla_partenza": 100_500.0, "candela_alla_partenza": 100_500.0}
    dg = pd.DataFrame({"giorno": ["2026-11-20", "2026-11-23"], "guadagno": [250.0, float("nan")]})   # il 23: copertura sopra zero
    # a fine giornata, tutto chiuso: il conto è salito di 100 (candela) + 250 (prova 45) + 30 (miscela)
    candela, miscela = conto.valori(100_880.0, [], diario, stato, diario_gamma=dg)
    assert candela == pytest.approx(100_600.0)
    assert miscela == pytest.approx(100_030.0)
    assert conto.valore_gamma([], dg) == pytest.approx(100_250.0)
    # oggi, prima che la riga del giorno sia scritta: venduti 160 VOO a 600, ricomprati 100 a 598, gli altri 60 valgono −35.880
    es = [{"symbol": "VOO", "side": "sell_short", "qty": "160", "price": "600"}, {"symbol": "VOO", "side": "buy", "qty": "100", "price": "598"}]
    aperte = [{"symbol": "VOO", "market_value": "-35880", "unrealized_pl": "0"}]
    g = conto.valore_gamma(aperte, dg, oggi="2026-11-24", esecuzioni_oggi=es)
    assert g == pytest.approx(100_250 + 96_000 - 59_800 - 35_880)          # +200 + 120 ancora aperti
    candela, miscela = conto.valori(100_880.0 + 320, aperte, diario, stato, oggi="2026-11-24", esecuzioni_oggi=es, diario_gamma=dg)
    assert candela == pytest.approx(100_600.0) and miscela == pytest.approx(100_030.0)   # le vendite di VOO non sono della candela


# ---- i percorsi degli ordini, con un conto finto e un orologio finto (nessun collegamento ad Alpaca) ------------------------------

class ContoFinto:
    def __init__(self, monkeypatch, ora, qty, stati_asta):
        from stock.avanti import avanti as av
        self.ora = pd.Timestamp(f"2026-11-24 {ora}", tz=NY)
        self.qty, self.stati_asta, self.chiamate, self.giorni, self.aperti = qty, list(stati_asta), [], {}, []
        monkeypatch.setattr(av, "ny_adesso", lambda: self.ora)
        monkeypatch.setattr(ga.time, "sleep", self.dormi)
        monkeypatch.setattr(av, "_richiesta", self.richiesta)
        monkeypatch.setattr(ga, "scrivi_giorno", lambda d: self.giorni.__setitem__(d["giorno"], dict(d)))
        monkeypatch.setattr(ga, "leggi_giorno", lambda g: dict(self.giorni[g]) if g in self.giorni else None)
        monkeypatch.setattr(ga, "scrivi_diario", lambda g: self.chiamate.append(("diario", g)) or "diario")
        monkeypatch.setattr(ga, "pubblica", lambda *a, **k: "plancia")

    def dormi(self, s):
        self.ora += pd.Timedelta(seconds=float(s))

    def stato(self):
        # gli stati dell'asta in ordine di tempo: [(ora, stato), ...]
        attuale = None
        for quando, s in self.stati_asta:
            if self.ora >= pd.Timestamp(f"2026-11-24 {quando}", tz=NY):
                attuale = s
        return attuale

    def richiesta(self, metodo, percorso, **kw):
        self.chiamate.append((metodo, percorso, kw.get("json")))
        if metodo == "GET" and percorso == "/v2/positions":
            return [{"symbol": "VOO", "qty": str(self.qty)}] if self.qty else []
        if metodo == "GET" and percorso.startswith("/v2/orders/"):
            return {"status": self.stato()}
        if metodo == "GET" and percorso == "/v2/orders":
            return list(self.aperti)
        if metodo == "DELETE" and percorso == "/v2/positions/VOO":
            self.qty = 0
            return {"id": "M"}
        if metodo == "POST" and percorso == "/v2/orders":
            corpo = kw["json"]
            if corpo.get("time_in_force") == "cls":
                self.stati_asta.append((f"{self.ora:%H:%M:%S}", "accepted"))
                return {"id": corpo["client_order_id"], "status": "accepted"}
            return {"id": "FO", "status": "accepted"}
        if metodo == "DELETE":
            return {}
        raise AssertionError(f"chiamata non prevista: {metodo} {percorso}")


SEDUTA = {"giorno": date(2026, 11, 24), "apertura": pd.Timestamp("2026-11-24 09:30", tz=NY),
          "chiusura": pd.Timestamp("2026-11-24 16:00", tz=NY)}


def test_asta_scaduta_dopo_le_15_50_si_esce_a_mercato_2_minuti_prima(monkeypatch):
    c = ContoFinto(monkeypatch, "15:51:00", -160, [("00:00", "expired")])
    c.giorni["2026-11-24"] = {"giorno": "2026-11-24", "id_ingresso": "A", "lato": "sell", "id_asta": "B"}
    assert ga.segui(SEDUTA) == "diario"
    uscite = [x for x in c.chiamate if x[0] == "DELETE" and x[1] == "/v2/positions/VOO"]
    assert len(uscite) == 1                                         # una sola uscita, a mercato
    assert not [x for x in c.chiamate if x[0] == "POST"]             # dopo le 15:50 l'asta non si rimanda
    assert "uscita a mercato" in c.giorni["2026-11-24"]["nota"] and c.giorni["2026-11-24"]["uscite"] == {"M": "mercato"}


def test_asta_cancellata_prima_delle_15_50_si_rimanda_e_si_esce_all_asta(monkeypatch):
    c = ContoFinto(monkeypatch, "15:31:00", 160, [("15:30:05", "accepted"), ("15:40:00", "canceled")])

    def chiudi_all_asta(s):
        ContoFinto.dormi(c, s)
        if c.ora >= pd.Timestamp("2026-11-24 16:00:01", tz=NY):
            c.qty = 0
            c.stati_asta.append(("16:00:01", "filled"))
    monkeypatch.setattr(ga.time, "sleep", chiudi_all_asta)
    c.giorni["2026-11-24"] = {"giorno": "2026-11-24", "id_ingresso": "A", "lato": "buy", "id_asta": "B", "tentativi_asta": 1}
    assert ga.segui(SEDUTA) == "diario"
    rimandate = [x for x in c.chiamate if x[0] == "POST" and x[2]["time_in_force"] == "cls"]
    assert len(rimandate) == 1 and rimandate[0][2]["client_order_id"] == "gamma-2026-11-24-asta-2"
    assert not [x for x in c.chiamate if x[0] == "DELETE" and x[1] == "/v2/positions/VOO"]   # nessuna uscita a mercato


def test_fuori_orario_non_manda_un_secondo_ordine_se_l_asta_resta_aperta(monkeypatch):
    from stock.dati import alpaca
    c = ContoFinto(monkeypatch, "16:03:00", 160, [("00:00", "accepted")])
    c.aperti = [{"id": "B", "symbol": "VOO", "client_order_id": "gamma-2026-11-24-asta-1", "status": "accepted"}]
    c.giorni["2026-11-24"] = {"giorno": "2026-11-24", "id_ingresso": "A", "lato": "buy", "id_asta": "B"}
    with pytest.raises(alpaca.ErroreAlpaca, match="ancora aperti"):
        ga.fuori_orario("2026-11-24")
    assert not [x for x in c.chiamate if x[0] == "POST"]             # mai due uscite insieme


def test_posizione_vista_in_ritardo_non_fa_uscire_a_mercato_alle_15_30(monkeypatch):
    c = ContoFinto(monkeypatch, "15:30:05", 160, [])
    letture = {"n": 0}
    vera = c.richiesta

    def in_ritardo(metodo, percorso, **kw):
        if metodo == "GET" and percorso == "/v2/positions":
            letture["n"] += 1
            if letture["n"] == 1:                                    # la prima lettura dopo l'ingresso: ancora vuota
                return []
        return vera(metodo, percorso, **kw)

    def chiudi_all_asta(s):
        ContoFinto.dormi(c, s)
        if c.ora >= pd.Timestamp("2026-11-24 16:00:01", tz=NY) and c.stati_asta:
            c.qty = 0
            c.stati_asta.append(("16:00:01", "filled"))
    from stock.avanti import avanti as av
    monkeypatch.setattr(av, "_richiesta", in_ritardo)
    monkeypatch.setattr(ga.time, "sleep", chiudi_all_asta)
    c.giorni["2026-11-24"] = {"giorno": "2026-11-24", "id_ingresso": "A", "lato": "buy"}
    assert ga.segui(SEDUTA) == "diario"
    assert [x[2]["time_in_force"] for x in c.chiamate if x[0] == "POST"] == ["cls"]            # l'asta, mandata al giro dopo
    assert not [x for x in c.chiamate if x[0] == "DELETE" and x[1] == "/v2/positions/VOO"]   # nessuna uscita a mercato
