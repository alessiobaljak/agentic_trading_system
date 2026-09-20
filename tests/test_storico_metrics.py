"""LO STORICO DI OPEN INTEREST: le trappole del dataset, scritte una volta sola.

Backlog B6. Il dataset «metrics» di data.binance.vision non e' documentato nel
README di Binance, e tre suoi comportamenti sono stati scoperti guardando i file
veri il 20 settembre 2026 — non leggendo una specifica, perche' non esiste:

  * i file recenti NON sono ordinati per orario;
  * i file del 2020/inizio 2021 hanno ogni riga duplicata;
  * esistono solo i giornalieri, e qualche giorno manca del tutto.

Un dato di ricerca letto male non da' errore: da' un backtest plausibile e
sbagliato. Questi test tengono le tre trappole dentro il codice invece che
dentro la memoria di chi l'ha scritto.
"""
import io
import zipfile
from datetime import date, datetime, timezone

import pytest

from backtesting import metrics_loader as ml

INTESTAZIONE = ",".join(ml.COLONNE)


def _riga(hhmm: str, oi: float = 100.0, giorno: str = "2026-09-18") -> str:
    return (f"{giorno} {hhmm}:00,BTCUSDT,{oi},{oi*1000},1.5,2.3,1.4,0.6")


def test_le_righe_escono_ORDINATE_anche_se_il_file_non_lo_e():
    """BTCUSDT 2026-09-18, file vero: parte alle 00:35, passa per le 23:20 e
    finisce alle 22:30. Chi assume l'ordine del file costruisce serie storiche
    che saltano avanti e indietro nel tempo — e un indicatore calcolato cosi'
    non da' errore, da' un numero sbagliato."""
    testo = "\n".join([INTESTAZIONE, _riga("00:35"), _riga("23:20"), _riga("22:30")])
    righe = ml.leggi_csv(testo)
    assert [r["ts"].strftime("%H:%M") for r in righe] == ["00:35", "22:30", "23:20"]


def test_le_righe_DOPPIE_dei_file_vecchi_contano_una_volta():
    """BTCUSDT 2020-09-01, file vero: 576 righe, 288 uniche — ogni riga scritta
    due volte. Contarle entrambe raddoppierebbe il peso di quei giorni in
    qualunque media o conteggio."""
    testo = "\n".join([INTESTAZIONE, _riga("00:00"), _riga("00:00"), _riga("00:05")])
    righe = ml.leggi_csv(testo)
    assert len(righe) == 2


def test_un_cambio_di_colonne_ferma_tutto_invece_di_leggere_a_caso():
    """Il dataset non e' documentato: puo' cambiare senza preavviso. Se le
    colonne si spostassero, leggere in silenzio metterebbe il long/short ratio
    dove ci va l'open interest, e il backtest girerebbe lo stesso."""
    with pytest.raises(ml.FormatoInatteso):
        ml.leggi_csv("a,b,c\n1,2,3")


def test_una_riga_guasta_non_porta_giu_il_giorno():
    testo = "\n".join([INTESTAZIONE, _riga("00:00"), "spazzatura,x,y", _riga("00:05")])
    assert len(ml.leggi_csv(testo)) == 2


def test_i_numeri_arrivano_come_numeri_e_il_tempo_e_in_UTC():
    """Un tempo senza fuso confrontato con uno in UTC esplode a runtime, ma solo
    quando i dati vengono davvero usati: cioe' mesi dopo averli caricati."""
    r = ml.leggi_csv("\n".join([INTESTAZIONE, _riga("00:00", oi=42.5)]))[0]
    assert r["open_interest"] == 42.5
    assert r["ts"] == datetime(2026, 9, 18, 0, 0, tzinfo=timezone.utc)
    assert r["ts"].tzinfo is not None


def test_un_file_vuoto_non_e_un_errore():
    assert ml.leggi_csv("") == []


# --------------------------------------------------------------------------- #
# La rete: elenco, buchi, checksum                                            #
# --------------------------------------------------------------------------- #
_XML = """<?xml version="1.0"?>
<ListBucketResult xmlns="http://s3.amazonaws.com/doc/2006-03-01/">
 <IsTruncated>false</IsTruncated>
 <Contents><Key>data/futures/um/daily/metrics/X/X-metrics-2022-01-01.zip</Key>
  <Size>1000</Size></Contents>
 <Contents><Key>data/futures/um/daily/metrics/X/X-metrics-2022-01-01.zip.CHECKSUM</Key>
  <Size>97</Size></Contents>
 <Contents><Key>data/futures/um/daily/metrics/X/X-metrics-2022-01-03.zip</Key>
  <Size>2000</Size></Contents>
</ListBucketResult>"""


class _Risposta:
    def __init__(self, testo="", contenuto=b"", stato=200):
        self.text, self.content, self.status_code = testo, contenuto, stato

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")


class _Sessione:
    def __init__(self, risposte):
        self.risposte, self.chiamate = risposte, []

    def get(self, url, **kw):
        self.chiamate.append(url)
        for frammento, r in self.risposte.items():
            if frammento in url:
                return r
        return _Risposta(stato=404)


def test_l_elenco_ignora_i_CHECKSUM_e_tiene_le_dimensioni():
    """I `.CHECKSUM` stanno accanto agli zip: contarli raddoppierebbe i giorni e
    falserebbe il peso su disco, che e' proprio il numero per cui esiste questa
    misura."""
    s = _Sessione({"s3-ap-northeast-1": _Risposta(testo=_XML)})
    mappa = ml.elenco_giorni("X", sessione=s)
    assert mappa == {date(2022, 1, 1): 1000, date(2022, 1, 3): 2000}


def test_i_giorni_mancanti_si_vedono():
    """Un buco non e' un guasto da nascondere: e' il dato da guardare PRIMA di
    costruirci sopra una feature."""
    assert ml.buchi({date(2022, 1, 1), date(2022, 1, 3)},
                    date(2022, 1, 1), date(2022, 1, 3)) == [date(2022, 1, 2)]


def _zip_di(testo: str) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        z.writestr("X-metrics-2022-01-01.csv", testo)
    return buf.getvalue()


def test_un_giorno_assente_torna_None_invece_di_esplodere(tmp_path):
    """Il dataset non e' documentato e qualche giorno manca: un 404 deve essere
    un giorno in meno, non un giro di ricerca perso."""
    s = _Sessione({})
    assert ml.scarica_giorno("X", date(2022, 1, 2), str(tmp_path), sessione=s) is None


def test_un_download_corrotto_viene_FERMATO_dal_checksum(tmp_path):
    """Uno zip troncato si apre lo stesso e da' meno righe: senza checksum
    sarebbe un buco invisibile dentro i dati, non un errore."""
    dati = _zip_di(INTESTAZIONE)
    s = _Sessione({".zip.CHECKSUM": _Risposta(testo="0" * 64 + "  X.zip"),
                   ".zip": _Risposta(contenuto=dati)})
    with pytest.raises(RuntimeError, match="checksum"):
        ml.scarica_giorno("X", date(2022, 1, 1), str(tmp_path), sessione=s)
    assert not list(tmp_path.iterdir()), "un file non verificato non resta in cache"


def test_la_cache_evita_di_riscaricare(tmp_path):
    """1750 giorni per 25 coppie: senza cache ogni prova ripaga l'intero
    download."""
    import hashlib
    dati = _zip_di("\n".join([INTESTAZIONE, _riga("00:00")]))
    s = _Sessione({".zip.CHECKSUM": _Risposta(
        testo=hashlib.sha256(dati).hexdigest() + "  X.zip"),
        ".zip": _Risposta(contenuto=dati)})
    for _ in range(2):
        assert ml.scarica_giorno("X", date(2022, 1, 1), str(tmp_path),
                                 sessione=s) == dati
    assert sum(1 for u in s.chiamate if u.endswith(".zip")) == 1


def test_si_usa_l_origine_S3_non_l_hostname():
    """`data.binance.vision` come hostname non sempre risponde; l'origine S3 si'
    — e' gia' la scelta di `scripts/survivorship_report.py`."""
    assert ml.S3.startswith("https://s3-")
    assert ml.url_zip("X", date(2022, 1, 1)).startswith(ml.S3)


def test_solo_i_file_GIORNALIERI():
    """I mensili non esistono per questo dataset (ci sono per le klines): chi
    li cercasse otterrebbe 404 su tutto e concluderebbe che la fonte e' morta."""
    assert "/daily/" in ml.PREFIX and "monthly" not in ml.PREFIX


# --------------------------------------------------------------------------- #
# La sonda misura e basta                                                     #
# --------------------------------------------------------------------------- #
def test_la_sonda_non_scrive_niente():
    """Il paper sta correndo verso i 40 trade: una misura che cambia lo stato
    butterebbe via l'esperimento che sta misurando."""
    import inspect

    from scripts import binance_metrics_probe as p

    src = inspect.getsource(p)
    for vietato in ("set_doc(", "set_rtdb(", "delete("):
        assert vietato not in src, f"la sonda scrive: {vietato}"


def test_la_sonda_dice_quante_coppie_hanno_dati_dal_2022():
    """E' la domanda numero uno del backlog B6: 23 delle 25 coppie validate sono
    coin recenti, e se lo storico non arriva al 2022 la feature non si puo'
    validare sulla stessa finestra del gate."""
    import inspect

    from scripts import binance_metrics_probe as p

    src = inspect.getsource(p.main)
    assert "coppie con dati dall'inizio della finestra" in src
    assert "PESO SUL DISCO" in src


def test_la_finestra_finisce_IERI_non_oggi():
    """PRIMO GIRO, 20 settembre: la sonda ha detto «25 coppie su 25 con giorni
    mancanti». Nessuna ne aveva: il file di un giorno esce il giorno dopo, e
    l'unico buco era la data di fine scelta male. Un allarme inventato dal
    proprio metro e' peggio di nessun allarme."""
    import inspect

    from scripts import binance_metrics_probe as p

    src = inspect.getsource(p.main)
    assert "timedelta(days=1)" in src
    assert 'default=ieri.isoformat()' in src
