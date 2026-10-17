"""QUANTO VIVE UNA STRATEGIA VALIDATA — la prova non si distrugge piu'.

Domanda del proprietario, 21 settembre 2026: «il mercato ora e' diverso e lo sara'
sempre, non credo che questa strategia possa valere per i prossimi 3 anni».

Ha ragione, e il sistema in parte lo sa gia': una coppia validata non e' permanente
— due finestre fallite di fila e viene rimossa. Ma a «quanto dura un individuo?»
si poteva solo rispondere «non lo so», perche' il purge stampava una riga nel
journal (che scorre via in poche ore) e poi CANCELLAVA il record. Nel registro
restavano solo i sopravvissuti: lo stesso bias di sopravvivenza che misuriamo sulle
coin delistate, rientrato dalla porta di servizio sulle strategie.

Qui si proteggono le proprieta' che rendono quella misura onesta. La piu'
importante non e' che il diario venga scritto: e' che NON inventi eta'.
"""
import inspect

from scripts import optimize as o


def test_la_data_di_nascita_si_scrive_solo_ATTRAVERSANDO_la_soglia():
    """Il caso che falserebbe tutto: al primo giro col codice nuovo ci sono 56
    coppie gia' validate. Dare a tutte `validated_at = adesso` fabbricherebbe 56
    eta' false, tutte corte, e la vita mediana risulterebbe piu' breve del vero
    proprio nel primo mese di misura — cioe' l'errore sarebbe massimo esattamente
    quando serve la risposta."""
    nuove = []
    rec = {"pass_count": o.MIN_PASSES}
    o._segna_promozione("X|gen_a", rec, prima=o.MIN_PASSES, adesso=1000.0, nuove=nuove)
    assert nuove == [] and "validated_at" not in rec

    rec = {"pass_count": o.MIN_PASSES}
    o._segna_promozione("X|gen_a", rec, prima=o.MIN_PASSES - 1, adesso=1000.0,
                        nuove=nuove)
    assert rec["validated_at"] == 1000.0
    assert len(nuove) == 1 and nuove[0]["tipo"] == "promossa"


def test_chi_non_arriva_alla_soglia_non_e_una_promozione():
    nuove = []
    o._segna_promozione("X|gen_a", {"pass_count": o.MIN_PASSES - 1}, 0, 1000.0, nuove)
    assert nuove == []


def test_una_coppia_senza_data_di_nascita_esce_con_eta_SCONOSCIUTA():
    """«Non lo so» e' l'unica risposta onesta per chi era gia' validata prima che
    questo registro esistesse. Un numero al suo posto entrerebbe nelle mediane e
    le sposterebbe senza che nessuno possa accorgersene."""
    riga = o._riga_vita("X|gen_a", {"pass_count": 3}, "rimossa", adesso=86400.0)
    assert riga["vissuta_giorni"] is None


def test_l_eta_si_misura_dalla_promozione():
    nato = 1_700_000_000.0
    riga = o._riga_vita("X|gen_a", {"pass_count": 3, "validated_at": nato},
                        "rimossa", adesso=nato + 86400 * 7)
    assert riga["vissuta_giorni"] == 7.0


def test_uno_zero_vale_come_data_MANCANTE_non_come_1970():
    """`validated_at = 0` e' il default di un campo non scritto, non una coppia
    validata nel 1970: trattarlo come una data darebbe eta' di ventimila giorni e
    farebbe saltare qualunque mediana."""
    riga = o._riga_vita("X|gen_a", {"pass_count": 3, "validated_at": 0.0},
                        "rimossa", adesso=86400.0 * 7)
    assert riga["vissuta_giorni"] is None


def test_la_riga_dice_se_era_in_deriva():
    """Distingue «il gate l'ha bocciata sulla storia» da «il paper l'aveva gia'
    smentita»: sono due morti diverse e si curano in modo diverso."""
    viva = o._riga_vita("X|g", {"pass_count": 3}, "rimossa", 1.0)
    morta = o._riga_vita("X|g", {"pass_count": 3, "drift_seen_at": 1.0},
                         "rimossa", 1.0)
    assert viva["in_deriva"] is False and morta["in_deriva"] is True


def test_la_riga_si_scrive_PRIMA_della_cancellazione():
    """L'ordine e' tutta la correzione: dopo il `del`, il record non esiste piu' e
    con lui sparisce l'unica prova di quanto era vissuta."""
    src = inspect.getsource(o.update_registry)
    assert src.index("uscite = [_riga_vita(") < src.index("del pairs[k]")


def test_solo_le_VALIDATE_entrano_nel_diario():
    """Il registro contiene migliaia di coppie a zero o un passaggio, purgate di
    continuo. Contarle come «strategie morte» renderebbe la vita mediana un
    numero sul rumore della ricerca, non sulle strategie che operano."""
    src = inspect.getsource(o.update_registry)
    assert '>= MIN_PASSES]' in src.split("uscite = [_riga_vita(")[1][:220]


def test_il_diario_non_puo_far_cadere_una_validazione():
    """Una passata del gate dura piu' di due ore. La memoria di cosa e' successo
    e' un di piu': se Firebase non risponde deve perdersi la riga, non il run."""
    src = inspect.getsource(o.registra_vite)
    assert "try:" in src and "except Exception" in src


def test_il_diario_e_tagliato_come_la_timeline():
    """Il registro su un documento solo ci ha gia' fatto cadere un run da quattro
    ore contro il limite di 1 MiB. Una lista che cresce per sempre e' lo stesso
    difetto con un altro nome."""
    src = inspect.getsource(o.registra_vite)
    assert "righe[-VITE_MAX:]" in src


def test_il_diario_non_scrive_se_non_e_successo_niente():
    """Una `set_doc` a ogni passata riscriverebbe lo stesso documento 16 volte al
    giorno per dire che non e' cambiato nulla."""
    class _Fb:
        def __init__(self):
            self.scritture = 0

        def get_doc(self, *a, **k):
            return {}

        def set_doc(self, *a, **k):
            self.scritture += 1

    fb = _Fb()
    o.registra_vite(fb, [], [])
    assert fb.scritture == 0
    o.registra_vite(fb, [{"key": "X|g", "tipo": "promossa"}], [])
    assert fb.scritture == 1


def test_il_campo_nuovo_sopravvive_al_formato_compatto():
    """Il registro si salva in forma compatta per stare sotto 1 MiB: un campo che
    il codec non conosce verrebbe buttato via in silenzio, e la data di nascita
    sparirebbe al primo salvataggio."""
    from bot.core.firebase_client import decode_pairs, encode_registry

    prima = {"X|gen_a": {"pass_count": 3, "validated_at": 1_700_000_000.0,
                         "symbol": "X", "strategy": "gen_a"}}
    dopo = decode_pairs(encode_registry(prima))
    assert dopo["X|gen_a"]["validated_at"] == 1_700_000_000
