"""Prove chieste dal secondo riesame della quindicesima revisione (26 novembre 2026, problema 202: sei correzioni su quattordici si
potevano togliere senza che un test se ne accorgesse). Scritte dal revisore e dal verificatore, adattate qui con l'asserzione sul
comportamento giusto: annullamento degli ordini rimasti prima di aprire (N1), netto dei lati con arrotondamenti diversi (N2),
ricostruzione con un'operazione aperta che si chiude durante il fermo (195), lezioni del diario unite dopo una ricostruzione rimandata
(N4), cartella dei messaggi predefinita fuori da avanti/ (197 b), risposta persa adottata con i dati dell'esecuzione (197 c).
Nessuna rete."""
import json
import os
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from trader_ai.avvio import Trader
from trader_ai.conto_simulato import ContoSimulato
from trader_ai.messaggio import riga_bilancio
from trader_ai.modello import Esito
from trader_ai.tests.test_avvio import T0, ContoFinto, Orologio, risposta, stop_sul_conto
from trader_ai.tests.test_simulato import MIN, T0_MS, MercatoFinto

RADICE = Path(__file__).resolve().parents[2]


@pytest.mark.parametrize("annullo_ok", [True, False])
def test_annullo_prima_di_aprire(tmp_path, annullo_ok):
    """N1: ordini del trader rimasti senza operazione (uno stop vecchio, senza `da_annullare`): prima di aprire si annullano; se
    l'annullamento lancia un errore (conto simulato) la nuova non si apre."""
    c = ContoFinto()
    o = Orologio(T0)
    c.algo.append({"symbol": "BTCUSDT", "algoId": 7, "clientAlgoId": "tais1", "tipo": "STOP_MARKET", "prezzo": 89900.0})
    if not annullo_ok:
        def annulla_rotto():
            raise RuntimeError("GET /fapi/v1/klines: 429: pausa")
        c.annulla_tutto = annulla_rotto
    tr = Trader(c, lambda s, u: Esito(risposta("apri_lungo", margine_usdt=100, leva=5, stop_prezzo=88000.0), "ok",
                                      {"input_tokens": 1}), tmp_path, o)
    st0 = tr.stato_nuovo()
    st0.update(giorno="2026-11-24", conto_mezzanotte=1000.0, inizio={"giorno": "2026-11-24", "conto": 1000.0})
    tr.salva(st0)
    tr.passo()
    st = tr.carica()
    if annullo_ok:
        assert c.pos is not None and stop_sul_conto(c) == [88000.0]
    else:
        assert c.pos is None and c.ordini == [] and st["ultimo_scarto"].startswith("rifiutata dal conto")


def test_n2_lati_e_netto_con_arrotondamenti_diversi():
    """N2: tre operazioni da -1,004 (risultati arrotondati -1,00, somma -3,00; netto dalle parti -3,012): i lati con la stessa
    regola del netto."""
    ops = [{"chiusa": f"2026-11-25T1{i}:00:00+00:00", "lato": "lungo", "risultato": -1.0, "risultato_prezzo": -1.004, "spese": 0.0,
            "funding": 0.0, "come": "stop iniziale"} for i in range(3)]
    riga = riga_bilancio("oggi", ops)
    assert "netto -3.01 USDT" in riga and "lunghi 3 (0 vinte, 3 perse, -3.01)" in riga


class Orologio_ms:
    def __init__(self, ms):
        self.ms = ms

    def __call__(self):
        return self.ms

    def dt(self):
        return datetime.fromtimestamp(self.ms / 1000, timezone.utc)


def test_ricostruzione_con_operazione_aperta_che_si_chiude_al_riavvio(tmp_path):
    """195: un'operazione aperta nello stato si chiude sul conto durante il fermo; al primo passo della versione 7 la ricostruzione
    non la aggiunge e il passo la registra una volta sola."""
    clock = Orologio_ms(T0_MS)
    m = MercatoFinto()
    c = ContoSimulato(m, tmp_path / "conto_simulato.json", clock)
    c.aggiorna(forza=True)
    m.minuto(T0_MS, 90000, 90050, 89950, 90000)
    m.prezzo = 90000.0
    risposte = [risposta("apri_lungo", margine_usdt=100, leva=5, stop_prezzo=89000.0)]
    tr = Trader(c, lambda s, u: Esito(risposte.pop(0) if risposte else risposta(), "ok", {"input_tokens": 1}), tmp_path, clock.dt)
    clock.ms = T0_MS + 30_000
    tr.passo()                                                          # apertura a mercato
    st = tr.carica()
    assert st["aperta"] and json.loads(c.file.read_text())["posizione"]
    st["versione_memoria"] = 6                                          # come la memoria scritta prima del 26 novembre
    tr.salva(st)
    for i in range(1, 6):                                               # durante il fermo del servizio lo stop scatta
        m.minuto(T0_MS + i * MIN, 89500, 89550, 88800, 88900)
    m.prezzo = 88900.0
    clock.ms = T0_MS + 6 * MIN + 5_000                                  # primo passo della versione 7
    tr.passo()
    ops = tr.carica()["operazioni"]
    assert len(json.loads(c.file.read_text())["chiuse"]) == 1
    assert len(ops) == 1 and not ops[0]["uscita_stimata"]


def test_lezioni_del_diario_unite_dopo_una_ricostruzione_rimandata(tmp_path):
    """N4: la prima ricostruzione salta (conto non letto) e intanto il modello scrive una lezione: al passo dopo i perché vecchi
    del diario si uniscono alla lezione nuova, in ordine di ora e senza doppioni."""
    c = ContoFinto()
    o = Orologio(T0)
    guasto = {"si": True}

    def storia():
        if guasto["si"]:
            raise RuntimeError("rete")
        return {"chiuse": [], "movimenti": [], "funding_applicati": []}
    c.storia = storia
    risposte = [risposta(lezione="lezione nuova")]
    tr = Trader(c, lambda s, u: Esito(risposte.pop(0) if risposte else risposta(), "ok", {"input_tokens": 1}), tmp_path, o)
    vecchi = [{"ora": f"2026-11-23T1{i}:00:00+00:00", "motivo": "candela", "guadagno_giorno": -1.0,
               "risposta": {"azione": "aspetta", "cambio_approccio": True, "perche": f"perché vecchio {i}", "diario": "d"}}
              for i in range(3)]
    tr.diario.parent.mkdir(parents=True, exist_ok=True)
    tr.diario.write_text("".join(json.dumps(x) + "\n" for x in vecchi))
    tr.salva({"operazioni": [], "note": [], "giorno": "2026-11-24", "conto_mezzanotte": 1000.0})
    tr.passo()                                                          # ricostruzione rimandata; il modello scrive una lezione
    st = tr.carica()
    assert st.get("versione_memoria", 0) < 7 and [x["testo"] for x in st["lezioni"]] == ["lezione nuova"]
    guasto["si"] = False
    o.t = T0 + timedelta(minutes=1)
    tr.passo()
    testi = [x["testo"] for x in tr.carica()["lezioni"]]
    assert testi == [f"cambio di approccio: perché vecchio {i}" for i in range(3)] + ["lezione nuova"]


def test_cartella_dei_messaggi_predefinita_fuori_da_avanti():
    """197 b: senza `messaggi`, sulla macchina i messaggi interi stanno fuori da avanti/ (che salva.sh porta nel repository)."""
    amb = {**os.environ, "TRADER_AI_DATI": "/opt/trader-ai-dati/trader_ai/avanti"}
    out = subprocess.run([sys.executable, "-c", "from trader_ai.avvio import Trader; print(Trader(None, None).cartella_messaggi)"],
                         cwd=RADICE, env=amb, capture_output=True, text=True, check=True).stdout.strip()
    assert out == "/opt/trader-ai-dati/trader_ai/messaggi_modello"


def test_risposta_persa_adottata_con_i_dati_dell_esecuzione(tmp_path):
    """197 c: ordine a mercato eseguito ma risposta persa: al passo dopo l'operazione si adotta con l'entrata vera, l'ora di
    esecuzione, 1 R e le spese d'entrata."""
    c = ContoFinto()
    o = Orologio(T0)
    tr = Trader(c, lambda s, u: Esito(risposta("apri_lungo", margine_usdt=100, leva=5, stop_prezzo=88000.0) if not c.ordini
                                      else risposta(), "ok", {"input_tokens": 1}), tmp_path, o)
    vero = c.apri

    def apri_persa(*a, **k):
        vero(*a, **k)
        c.pos["entrata"] = 90050.0                                     # il prezzo vero dell'esecuzione
        raise RuntimeError("POST /fapi/v1/order: rete: Read timed out")
    c.apri = apri_persa
    tr.passo()
    o.t = T0 + timedelta(seconds=30)
    tr.passo()
    a = tr.carica()["aperta"]
    assert stop_sul_conto(c) == [88000.0]                               # la protezione regge
    assert a["entrata"] == 90050.0 and a.get("eseguita") and a.get("R") and a.get("spese_entrata")
