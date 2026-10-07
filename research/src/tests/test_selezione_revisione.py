"""Revisione avversaria del Passo 1 (research/src/selezione.py), 7 ott 2026.

Ogni test porta nel nome e nel docstring il difetto che smaschera, con file e riga.
I test marcati «DIFETTO» FALLISCONO finche' il difetto resta: si lasciano cosi'
apposta, sono la prova riproducibile. I test marcati «VERIFICATO» passano e
fissano cio' che la revisione ha controllato e trovato a posto.

Niente rete (fetch finto), niente import da bot/, backtesting/, scripts/.

Correzione del 7 ott 2026, dopo le decisioni sulla revisione: i difetti sono stati
corretti in selezione.py e passo1.py, quindi i test «DIFETTO» ora passano. Quattro
test chiedevano un comportamento diverso da quello deciso e sono stati corretti,
ciascuno con il perche' nel suo docstring: la soglia dei 350 giorni (segnalazione,
non filtro: parametri.yaml e' congelato e non si tocca), la morte a meta' dicembre
(si riconosce dall'ultimo giorno presente letto con il volume, non dai giorni
contati), la ricucitura (al Passo 1 non si cuce da soli: si elencano le sospette e
si chiede allo STOP) e la forma di ``volume_medio_nella_finestra`` (ora ritorna
anche l'ultimo giorno presente).
"""
import calendar
from datetime import date, timedelta
from pathlib import Path

import pytest
import yaml

from research.src import selezione as sel

MS_G = 86_400_000
T2023 = 1_672_531_200_000          # 2023-01-01 00:00 UTC
T2024 = T2023 + 365 * MS_G         # 2024-01-01 00:00 UTC
PREF = "data/futures/um/monthly/klines/BTCUSDT/1d/"
PARAMETRI = Path(__file__).resolve().parents[2] / "config" / "parametri.yaml"


def _cand(simbolo, oggi=True, listing=date(2020, 1, 1), ultimo=date(2023, 12, 31),
          volume=100e6, giorni=365, primo=date(2020, 1, 1), ultimo_giorno=None):
    return sel.Candidata(simbolo=simbolo, negoziata_oggi=oggi, listing=listing,
                         listing_da="exchangeInfo" if oggi else "archivio", primo_mese=primo,
                         ultimo_mese=ultimo, volume_medio_2023=volume, giorni_2023=giorni,
                         ultimo_giorno_2023=ultimo_giorno)


def _riga(ts, quote_volume):
    return [str(ts), "1", "2", "0.5", "1.5", "10", str(int(float(ts)) + MS_G - 1 if str(ts).isdigit() else 0),
            str(quote_volume), "3", "1", "1", "0"]


def _pagina(chiavi, troncata=False, prossimo=None):
    corpo = "".join(f"<Contents><Key>{k}</Key></Contents>" for k in chiavi)
    nm = f"<NextMarker>{prossimo}</NextMarker>" if prossimo else ""
    return (f'<?xml version="1.0"?><ListBucketResult xmlns="http://s3.amazonaws.com/doc/2006-03-01/">'
            f"<Prefix>p</Prefix><IsTruncated>{'true' if troncata else 'false'}</IsTruncated>{nm}{corpo}"
            f"</ListBucketResult>").encode()


def _scelte_dati():
    with open(PARAMETRI, encoding="utf-8") as f:
        return yaml.safe_load(f)["scelte_dati"]


# =========================================================================== #
# (1) punto nel tempo                                                          #
# =========================================================================== #
def test_DIFETTO_alta_scheda_moneta_rivela_se_la_moneta_e_delistata_oggi():
    """selezione.py riga 326: la scheda stampa ``listing_da``. In passo1.py (righe 54-59)
    ``archivio`` si assegna SOLO a un contratto assente dall'exchangeInfo di oggi, cioe'
    delistato: chi legge «(archivio)» sa che la moneta oggi non e' negoziata. E' proprio
    l'informazione che la regola 4.1 e il docstring della scheda vietano. Il test
    ``test_scheda_moneta_senza_informazioni_dopo_il_2023`` non lo vede perche' cerca
    solo le stringhe «2024» e «delist»."""
    viva = sel.scheda_moneta(_cand("AUSDT", oggi=True, volume=300e6))
    morta = sel.scheda_moneta(_cand("AUSDT", oggi=False, ultimo=date(2024, 6, 30), volume=300e6))
    assert "archivio" not in morta and "exchangeInfo" not in viva
    # stessa moneta, stessi dati al 2023-12-31: la scheda dev'essere identica
    assert viva == morta


def test_VERIFICATO_ordine_e_taglio_non_dipendono_da_niente_del_2024():
    """L'ordine e il taglio alle prime N cambiano solo con volume 2023 e simbolo:
    delisting nel vault, ``negoziata_oggi`` e ``ultimo_mese`` oltre il 2023 non contano."""
    base = [_cand("AUSDT", volume=300e6), _cand("BUSDT", volume=900e6), _cand("CUSDT", volume=200e6)]
    r1 = sel.seleziona(base, n=2)
    variato = [_cand("AUSDT", volume=300e6, oggi=False, ultimo=date(2026, 9, 30)),
               _cand("BUSDT", volume=900e6, oggi=False, ultimo=date(2024, 1, 31)),
               _cand("CUSDT", volume=200e6, ultimo=date(2025, 3, 31))]
    r2 = sel.seleziona(variato, n=2)
    assert [c.simbolo for c in r1["campagna"]] == [c.simbolo for c in r2["campagna"]] == ["BUSDT", "AUSDT"]


def test_VERIFICATO_finestra_del_volume_e_solo_il_2023_ai_bordi():
    """2022-12-31 23:59:59.999 fuori, 2023-01-01 00:00 dentro, 2023-12-31 23:59:59.999
    dentro, 2024-01-01 00:00 fuori; i microsecondi si normalizzano prima del confronto."""
    # (corretto il 7 ott: la funzione ora ritorna anche l'ultimo giorno presente, in ms,
    # per il filtro «fine dati al giorno»; la finestra e' la stessa)
    giorni = [(T2023 - 1, 1e12), (T2023, 10.0), (T2024 - 1, 30.0), (T2024, 1e12)]
    assert sel.volume_medio_nella_finestra(giorni) == (20.0, 2, T2024 - MS_G)
    righe = [_riga(T2023 * 1000, 10.0), _riga(T2024 * 1000, 99.0)]     # microsecondi
    assert sel.volume_medio_nella_finestra(sel.volume_quote_giornaliero(righe)) == (10.0, 1, T2023)


# =========================================================================== #
# (2) filtri contro il protocollo e parametri.yaml                             #
# =========================================================================== #
def test_VERIFICATO_costanti_uguali_a_parametri_yaml():
    """Le costanti copiate a mano in selezione.py coincidono con scelte_dati."""
    p = _scelte_dati()
    assert sel.LIQUIDITA_MINIMA == p["liquidita_minima_usdt_giorno"]
    assert sel.NUMERO_MONETE_CAMPAGNA == p["numero_monete_campagna"]
    assert sel.INIZIO_FINESTRA_VOLUME == p["finestra_volume"]["inizio"]
    assert sel.FINE_FINESTRA_VOLUME == p["finestra_volume"]["fine"]
    assert sel.LIMITE_LISTING == date(2024 - p["storia_minima_anni"], 1, 1)
    assert list(sel.FASCE_SLIPPAGE) == [(f["volume_minimo"], f["slippage"]) for f in p["slippage_per_lato"]]


def test_DIFETTO_media_filtro_di_copertura_350_giorni_non_e_in_parametri_yaml():
    """selezione.py righe 61-63 e 192-193: un quinto filtro («almeno 350 giorni di dati
    nel 2023») con una soglia che non sta ne' nella sezione 3.3 del protocollo ne' in
    ``scelte_dati`` di parametri.yaml, che la sezione 3 dichiara congelato e approvato.
    Una moneta con 340 giorni e 100 M USDT/giorno la esclude il codice, non il protocollo.

    Corretto il 7 ott: il test chiedeva di DICHIARARE la soglia in parametri.yaml, ma il
    file e' congelato e non si tocca. La decisione e' l'altra via: la soglia non e' piu'
    un filtro (nessun motivo di esclusione), resta solo come soglia di attenzione
    (``SOGLIA_COPERTURA_2023``) con cui ``seleziona`` elenca le idonee con copertura
    incompleta perche' il coordinamento le mostri allo STOP. Quindi qui si verifica che
    nessun valore di scelte_dati venga usato come minimo di giorni, che 340 giorni non
    escludano, e che la copertura venga segnalata."""
    valori = []

    def _raccogli(x):
        if isinstance(x, dict):
            for v in x.values():
                _raccogli(v)
        elif isinstance(x, list):
            for v in x:
                _raccogli(v)
        else:
            valori.append(x)
    _raccogli(_scelte_dati())
    assert sel.SOGLIA_COPERTURA_2023 not in valori, "una soglia di giorni nei parametri congelati? allora e' un filtro"
    assert not hasattr(sel, "GIORNI_MINIMI_2023")
    assert sel.valuta(_cand("OKUSDT", giorni=340)).motivi_esclusione == []
    assert sel.valuta(_cand("OKUSDT", giorni=1)).motivi_esclusione == []
    r = sel.seleziona([_cand("OKUSDT", giorni=340), _cand("FULLUSDT", giorni=365)], n=2)
    assert r["conteggi"]["idonee"] == 2 and r["copertura_incompleta"] == ["OKUSDT"]
    assert r["conteggi"]["idonee_con_copertura_incompleta"] == 1


def test_DIFETTO_bassa_storia_minima_guarda_il_listing_e_non_i_dati():
    """selezione.py righe 183-186: ``valuta`` non legge mai ``primo_mese``. Il protocollo
    (Passo 1, punto 2) chiede «almeno storia_minima_anni di DATI prima del 2024-01-01»:
    un contratto con onboardDate 2021-06 ma primo file nell'archivio 2022-06 passa con un
    anno e mezzo di dati."""
    c = sel.valuta(_cand("LATEUSDT", listing=date(2021, 6, 1), primo=date(2022, 6, 1)))
    assert c.motivi_esclusione, "passa il filtro della storia con 19 mesi di dati"


def test_DIFETTO_bassa_morta_a_meta_dicembre_2023_entra_in_campagna_senza_vault():
    """selezione.py righe 187-188: la fine dei dati e' al mese. Un contratto con il file
    2023-12 ma morto il 17 dicembre (351 giorni nel 2023, non negoziato oggi) passa tutti
    i filtri ed entra in campagna con zero giorni di vault; il protocollo fa entrare «i
    contratti delistati DOPO il 2023». La soglia dei 350 giorni lo ferma solo se e' morto
    prima del 16 dicembre.

    Corretto il 7 ott: la decisione riconosce la morte a meta' dicembre dall'ULTIMO
    GIORNO presente nel 2023 (``ultimo_giorno_2023``, che passo1 riempie leggendo le
    candele insieme al volume), non dal numero di giorni contati, che non e' un filtro.
    Il test quindi passa l'ultimo giorno, come fa passo1."""
    c = sel.valuta(_cand("DECUSDT", oggi=False, ultimo=date(2023, 12, 31), giorni=351,
                         ultimo_giorno=date(2023, 12, 17)))
    assert c.motivi_esclusione, "entra in campagna una moneta che non ha un giorno di vault"
    assert any(m.startswith("dati che finiscono il 2023-12-17") for m in c.motivi_esclusione)
    # con l'ultima candela del 31 dicembre passa, viva o delistata che sia
    assert sel.valuta(_cand("OKUSDT", oggi=False, ultimo_giorno=date(2023, 12, 31))).motivi_esclusione == []


# =========================================================================== #
# (3) la media del volume e le righe corrotte                                  #
# =========================================================================== #
def test_DIFETTO_media_riga_corrotta_nan_rende_la_moneta_idonea_e_rompe_il_csv():
    """selezione.py righe 152-157: ``float("nan")`` non solleva, quindi una riga corrotta
    entra; la media diventa NaN; ``valuta`` (riga 194) non la esclude perche' ``nan <
    soglia`` e' falso; in ``seleziona`` l'ordine con NaN non e' definito; poi
    ``fascia_slippage`` e' None (assert in ``scheda_moneta``) e ``riga_csv`` (riga 299)
    solleva ValueError su ``round(nan)``: il Passo 1 si ferma o pubblica una lista storta."""
    righe = [_riga(T2023, 100.0), _riga(T2023 + MS_G, "nan")]
    giorni = sel.volume_quote_giornaliero(righe)
    assert giorni == [(T2023, 100.0)], "la riga con quote volume 'nan' va scartata"


def test_DIFETTO_media_candidata_con_volume_nan_non_viene_esclusa():
    c = sel.valuta(_cand("NANUSDT", volume=float("nan")))
    assert c.motivi_esclusione, "volume NaN e nessun motivo di esclusione"


def test_DIFETTO_media_riga_corrotta_volume_negativo_o_infinito_accettata():
    """``float("-5e9")`` e ``float("inf")`` passano: un volume negativo abbassa la media di
    tutto l'anno, uno infinito mette la moneta prima di BTC e poi ``round(inf)`` in
    ``riga_csv`` solleva OverflowError."""
    assert sel.volume_quote_giornaliero([_riga(T2023, "-5e9")]) == []
    assert sel.volume_quote_giornaliero([_riga(T2023, "inf")]) == []


def test_DIFETTO_bassa_open_time_infinito_fa_saltare_tutta_la_lettura():
    """selezione.py riga 155: si catturano solo TypeError e ValueError; ``int(float("inf"))``
    solleva OverflowError e l'intero file del mese salta invece della sola riga."""
    righe = [_riga(T2023, 100.0), ["inf", "1", "2", "0.5", "1.5", "10", "0", "5"]]
    assert sel.volume_quote_giornaliero(righe) == [(T2023, 100.0)]


def test_DIFETTO_bassa_doppione_dello_stesso_giorno_con_ms_diverso_conta_due_giorni():
    """selezione.py righe 171-176: il doppione si riconosce solo a timestamp IDENTICO,
    non per giorno UTC. Due righe dello stesso giorno (00:00:00.000 e 00:00:00.001) sono
    due «giorni»: ``giorni_2023`` puo' superare 365 e la media raddoppia il peso di quel
    giorno; il filtro di copertura non ha un tetto."""
    giorni = [(T2023, 100.0), (T2023 + 1, 300.0)]
    media, n, _ = sel.volume_medio_nella_finestra(giorni)      # (7 ott: terzo valore = ultimo giorno)
    assert n == 1, f"un giorno contato {n} volte"


def test_VERIFICATO_doppione_identico_fuori_finestra_e_buco_di_dati():
    # (corretto il 7 ott: terzo valore = ultimo giorno presente, in ms)
    giorni = [(T2023 + i * MS_G, 50.0) for i in range(0, 20, 2)]       # un giorno si' e uno no
    assert sel.volume_medio_nella_finestra(giorni + [(T2023, 50.0)]) == (50.0, 10, T2023 + 18 * MS_G)


# =========================================================================== #
# (4) fasce di slippage ai confini e (9) fine_mese                             #
# =========================================================================== #
def test_VERIFICATO_fasce_ai_confini_coerenti_con_lo_yaml():
    for soglia, slippage in sel.FASCE_SLIPPAGE:
        assert sel.fascia_slippage(soglia) == slippage
        assert sel.fascia_slippage(soglia - 1) != slippage
    assert sel.fascia_slippage(sel.LIQUIDITA_MINIMA) == 0.0010
    assert sel.fascia_slippage(sel.LIQUIDITA_MINIMA - 0.01) is None
    # chi passa il filtro di liquidita' ha sempre una fascia (nessuna idonea senza slippage)
    assert sel.valuta(_cand("EDGEUSDT", volume=sel.LIQUIDITA_MINIMA)).motivi_esclusione == []


def test_VERIFICATO_fine_mese_tutti_i_mesi_bisestile_e_dicembre():
    for anno in (2023, 2024, 2100, 2000):
        for mese in range(1, 13):
            assert sel.fine_mese(anno, mese) == date(anno, mese, calendar.monthrange(anno, mese)[1])


# =========================================================================== #
# (5) ordinamento e (6) conteggi della sopravvivenza                           #
# =========================================================================== #
def test_DIFETTO_bassa_stesso_simbolo_due_volte_occupa_due_posti_di_campagna():
    """selezione.py righe 204-208: nessun controllo sui doppioni di simbolo. Se le
    candidate arrivano da due liste (exchangeInfo e archivio) senza fusione, la stessa
    moneta prende due dei 20 posti."""
    r = sel.seleziona([_cand("AUSDT"), _cand("AUSDT"), _cand("BUSDT", volume=50e6)], n=2)
    simboli = [c.simbolo for c in r["campagna"]]
    assert len(set(simboli)) == len(simboli), simboli


def test_VERIFICATO_conteggi_sovrapposti_una_moneta_esclusa_per_due_motivi_conta_due_volte():
    """Non e' un errore ma NON e' dichiarato: le categorie ``escluse_per_*`` si sovrappongono
    (``any`` per motivo), quindi la loro somma supera ``len(escluse)``. Questo test lo fissa
    nero su bianco."""
    r = sel.seleziona([_cand("XUSDT", listing=date(2023, 1, 1), volume=1e6)], n=1)
    k = r["conteggi"]
    assert k["escluse_per_listing"] == 1 and k["escluse_per_volume"] == 1
    assert k["escluse_per_listing"] + k["escluse_per_volume"] > len(r["escluse"])


def test_DIFETTO_bassa_listing_sconosciuta_contata_come_listing_tardivo():
    """selezione.py riga 220: la categoria si riconosce dalla parola «listing» nel motivo,
    e «data di listing sconosciuta» la contiene. Nel conteggio del bias di sopravvivenza
    un contratto SENZA data finisce fra quelli «listati dopo il 2022»."""
    r = sel.seleziona([_cand("NOLISTUSDT", listing=None)], n=1)
    assert r["conteggi"]["escluse_per_listing"] == 0


def test_DIFETTO_media_valuta_cancella_i_motivi_scritti_dal_chiamante():
    """selezione.py riga 196: ``valuta`` SOSTITUISCE ``motivi_esclusione`` invece di
    aggiungere. passo1.py (riga 102) scrive «errore nello scarico del 2023: ...» e poi
    chiama ``seleziona``: il motivo sparisce e resta «nessun volume nel 2023», che e'
    falso (il volume non si e' potuto leggere). Il ciclo ``for ... pass`` di passo1.py
    (righe 108-109) che dovrebbe conservarlo non fa nulla."""
    c = _cand("ERRUSDT", volume=None, giorni=0)
    c.motivi_esclusione = ["errore nello scarico del 2023: zip rotto"]
    sel.valuta(c)
    assert any("errore nello scarico" in m for m in c.motivi_esclusione), c.motivi_esclusione


# =========================================================================== #
# (1 bis) la ricucitura delle serie richiesta dal Passo 1                      #
# =========================================================================== #
def test_DIFETTO_media_manca_la_serie_collegata_nel_csv_e_nel_modello():
    """Passo 1, punto 1 e 2 del protocollo: «ricuci i cambi di contratto ... salvale con
    simbolo, serie collegata, ...». ``Candidata`` ha un solo ``simbolo`` e ``COLONNE_CSV``
    (riga 284) non ha una colonna per la serie collegata: il modulo non puo' nemmeno
    rappresentare una ridenominazione."""
    assert any("serie" in colonna for colonna in sel.COLONNE_CSV), sel.COLONNE_CSV


def test_DIFETTO_media_contratto_rinominato_nel_2023_sparisce_dalla_selezione():
    """Senza ricucitura un contratto rinominato a meta' 2023 e' DUE candidate: la vecchia
    esclusa per «dati che finiscono prima del 2023-12», la nuova per listing dopo il 2022.
    La serie, che ha 3 anni e mezzo di dati e 500 M USDT/giorno, non entra; la meta'
    vecchia gonfia pure i conteggi dei delistati.

    Corretto il 7 ott: il test chiedeva la cucitura automatica (una sola idonea). La
    decisione e' che al Passo 1 il codice NON cuce da solo: il protocollo dice «se non
    sei sicuro di un collegamento, STOP e chiedi», e un codice non puo' sapere se OLD e
    NEW sono la stessa moneta o due monete diverse. Quindi ``seleziona`` elenca le
    sospette (sparite nel 2022-2023, nate nel 2022-2023) e il coordinamento le mostra
    allo STOP; ``serie_collegata`` resta il simbolo finche' l'utente non decide. Le due
    meta' restano escluse, ma non spariscono in silenzio."""
    vecchia = _cand("OLDUSDT", oggi=False, ultimo=date(2023, 5, 31), volume=500e6, giorni=151)
    nuova = _cand("NEWUSDT", listing=date(2023, 6, 1), primo=date(2023, 6, 1), volume=500e6, giorni=214)
    r = sel.seleziona([vecchia, nuova], n=1)
    assert r["conteggi"]["idonee"] == 0, [c.motivi_esclusione for c in r["escluse"]]
    assert r["sospette_ridenominazioni"] == {"sparite_2022_2023": ["OLDUSDT"], "listate_2022_2023": ["NEWUSDT"]}
    assert vecchia.serie_collegata == "OLDUSDT" and nuova.serie_collegata == "NEWUSDT"


# =========================================================================== #
# (7) l'indice dei file                                                         #
# =========================================================================== #
def test_DIFETTO_media_indice_troncato_con_marker_fermo_restituisce_una_lista_parziale():
    """selezione.py riga 275: con ``prossimo == marker`` si esce in silenzio con la lista
    parziale (e doppia: il test ufficiale accetta ``["a.zip", "a.zip"]``). Un elenco a
    meta' sposta ``ultimo_mese`` (filtro «fine dati») o ``primo_mese`` (listing dei
    delistati) senza che nessuno lo sappia. ``dati.elenca_simboli_archivio`` nello stesso
    caso solleva."""
    def fetch(url):
        return _pagina([PREF + "BTCUSDT-1d-2020-01.zip"], troncata=True, prossimo="z")
    with pytest.raises(RuntimeError):
        sel.elenca_file_archivio("BTCUSDT", fetch=fetch)


def test_DIFETTO_media_indice_con_marker_che_torna_indietro_gira_100_pagine_e_non_solleva():
    """selezione.py righe 269-278: un marker che va all'indietro passa il controllo
    ``prossimo == marker``; dopo MAX_PAGINE_INDICE pagine ancora troncate si esce senza
    errore con 100 chiavi ripetute."""
    chiamate = []

    def fetch(url):
        chiamate.append(url)
        if "marker=z" in url:
            return _pagina([PREF + "BTCUSDT-1d-2020-02.zip"], troncata=True, prossimo="y")
        return _pagina([PREF + "BTCUSDT-1d-2020-01.zip"], troncata=True, prossimo="z")
    with pytest.raises(RuntimeError):
        sel.elenca_file_archivio("BTCUSDT", fetch=fetch)
    assert len(chiamate) < 100


def test_DIFETTO_media_pagina_troncata_senza_chiavi_ne_marker_restituisce_lista_parziale():
    """selezione.py riga 255-256 e 275: pagina 2 troncata ma vuota -> ``prossimo`` None ->
    si esce con le sole chiavi della pagina 1, senza errore."""
    def fetch(url):
        if "marker=" in url:
            return _pagina([], troncata=True)
        return _pagina([PREF + "BTCUSDT-1d-2020-01.zip"], troncata=True)
    with pytest.raises(RuntimeError):
        sel.elenca_file_archivio("BTCUSDT", fetch=fetch)


def test_DIFETTO_bassa_chiavi_fuori_dal_prefisso_entrano_nei_mesi():
    """selezione.py riga 278: nessun controllo ``startswith(prefisso)`` (che
    ``dati.elenca_simboli_archivio`` invece fa). Una chiave di un'altra cartella diventa
    un mese del simbolo: qui ETHUSDT 2019-12 sposta il primo mese di BTCUSDT."""
    altrove = "data/futures/um/monthly/klines/ETHUSDT/1d/ETHUSDT-1d-2019-12.zip"

    def fetch(url):
        return _pagina([altrove, PREF + "BTCUSDT-1d-2020-01.zip"])
    nomi = sel.elenca_file_archivio("BTCUSDT", fetch=fetch)
    assert sel.primo_e_ultimo_mese(nomi)[0] == date(2020, 1, 1), nomi


def test_DIFETTO_bassa_prefisso_del_funding_ha_il_livello_dell_intervallo_che_non_esiste():
    """selezione.py riga 266: il prefisso mette sempre ``/{intervallo}/``, ma per
    ``fundingRate`` l'archivio non ha quel livello (vedi ``dati.url_mese``): l'elenco e'
    sempre vuoto. Fuori dal bisogno del Passo 1 (solo klines 1d), ma la firma lo ammette."""
    urls = []

    def fetch(url):
        urls.append(url)
        return _pagina([])
    sel.elenca_file_archivio("BTCUSDT", intervallo=None, fetch=fetch, tipo="fundingRate")
    assert urls and "/fundingRate/BTCUSDT/" in urls[0] and "/None/" not in urls[0], urls[0]


def test_VERIFICATO_checksum_ignorati_e_prefisso_per_simbolo_non_prende_i_trimestrali():
    chiavi = ["BTCUSDT-1d-2023-01.zip.CHECKSUM", "BTCUSDT-1d-2023-01.zip"]
    assert sel.mesi_dai_nomi(chiavi) == [(2023, 1)]
    # il prefisso finisce con ``BTCUSDT/1d/``: la cartella ``BTCUSDT_210326/1d/`` non ci sta sotto
    url = sel.url_indice_file(PREF)
    assert url.endswith("klines/BTCUSDT/1d/") and not "BTCUSDT_210326/".startswith("BTCUSDT/")


# =========================================================================== #
# (8) il listing dedotto dal primo file                                         #
# =========================================================================== #
def test_VERIFICATO_primo_del_mese_non_cambia_il_filtro_della_storia():
    """L'approssimazione «listing = primo giorno del primo mese» (dichiarata nel docstring
    del modulo, righe 23-26) non sposta mai la decisione: il limite 2022-01-01 cade su un
    confine di mese e l'archivio parte dal 2020-01, prima del limite."""
    giorno = date(2021, 10, 1)
    while giorno <= date(2022, 3, 31):
        vero = sel.valuta(_cand("XUSDT", listing=giorno)).motivi_esclusione
        approssimato = sel.valuta(_cand("XUSDT", listing=giorno.replace(day=1))).motivi_esclusione
        assert bool(vero) == bool(approssimato), giorno
        giorno += timedelta(days=1)
    # un contratto piu' vecchio dell'archivio compare come 2020-01-01: passa, e deve passare
    assert sel.valuta(_cand("BTCUSDT", oggi=False, listing=date(2020, 1, 1))).motivi_esclusione == []
