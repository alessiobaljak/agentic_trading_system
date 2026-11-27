"""Le idee della coda nel riepilogo del registro (research/src/registro.py), corrette il 27 novembre 2026 (audit del 26 novembre,
punti_ciechi-7): prima si contava ogni riga numerata del file, anche le regole in testa al registro, e chiusa era solo una voce barrata,
quindi il riepilogo diceva «48 aperte» con la coda quasi vuota. Ora si legge solo la sezione 5 e lo stato scritto a parole."""
from research.src import registro

ESEMPIO = """# Registro

Le regole:
1. **Prima di ogni idea nuova** si guarda qui.
2. **Ogni prova nuova** ha la sua riga prima del calcolo.

## 1. Prove
| n. | descrizione | conto | risultato | verdetto |
|---|---|---|---|---|
| 165 | PC: le chiusure | 1 | −0,2% | no |

Totale nel conto: 9 + 3 = **12**

## 5. Idee in coda
1. ~~Una idea chiusa~~ → prova 16.
2. **Il carry**: non si prova per ora, il funding è basso.
3. **Una idea già provata** (scritta il 22 novembre). → prova 165: **no**.
4. **HLI con il funding di dYdX**: **Sul passato non si fa**: i prezzi sono quelli già usati.
   **Si misura in avanti** dal 2 novembre.
5. **Le liquidazioni vere**: **Ferma**: la chiave la può creare solo il proprietario.
6. **Il canale Telegram** (scalping): si verifica sui prezzi veri.

**Dalla letteratura del 28 ottobre** (un paragrafo fra le voci, non una voce):
7. **Le narrazioni** dei giornali: dopo la 149. [stato: in attesa]
8. ~~**Un'idea barrata con una marca vecchia**~~ [stato: aperta]
9. **Una idea con lo stato
   scritto sulla riga sotto**: **non si fa**.

## 6. Un'altra sezione
10. **Una riga numerata dopo la sezione 5**: non è un'idea.
"""


def _dati(tmp_path, testo=ESEMPIO):
    f = tmp_path / "REGISTRO.md"
    f.write_text(testo, encoding="utf-8")
    return registro.leggi(f)


def test_conta_solo_la_sezione_5(tmp_path):
    """Le regole numerate in testa al registro e le righe numerate di un'altra sezione non sono idee. Prima del 27 novembre le
    regole 1 e 2 del registro vero (righe 9 e 13) comparivano come le prime due «idee aperte»."""
    d = _dati(tmp_path)
    assert [v["n"] for v in d["idee"]] == [1, 2, 3, 4, 5, 6, 7, 8, 9]
    assert all(v["riga"] > d["sezione_idee"] for v in d["idee"])
    assert "Prima di ogni idea nuova" not in [t for _, t in d["idee_aperte"]]


def test_le_aperte_non_sono_le_regole_ne_le_voci_chiuse_a_parole(tmp_path):
    """Il difetto dell'audit con le chiavi di prima: con il codice del 7 novembre qui uscivano 9 «aperte» (le regole 1 e 2, le voci
    chiuse a parole, la riga numerata della sezione 6) e 2 chiuse."""
    d = _dati(tmp_path)
    assert [n for n, _ in d["idee_aperte"]] == [6] and d["idee_chiuse"] == 5


def test_gli_stati_scritti_a_parole(tmp_path):
    """Prima solo la 1 (barrata) era chiusa e le altre otto erano tutte «aperte»."""
    stati = {v["n"]: v["stato"] for v in _dati(tmp_path)["idee"]}
    assert stati == {1: "barrata", 2: "non si fa", 3: "provata", 4: "in avanti", 5: "in attesa", 6: "aperta",
                     7: "in attesa", 8: "barrata", 9: "non si fa"}


def test_sul_passato_non_si_fa_vuol_dire_solo_in_avanti():
    assert registro.stato_della_voce("**HLI**: **Sul passato non si fa**: si misura in avanti dal 2 novembre.") == "in avanti"
    assert registro.stato_della_voce("**X**: sul passato non si fa, e in avanti nemmeno.") == "aperta"
    assert registro.stato_della_voce("**X**: **Non si fa per ora**. Si riprende se la misura in avanti dà un segnale.") == "non si fa"


def test_le_parole_strette_non_chiudono_le_idee_aperte():
    """Le parole di tutti i giorni non sono stati: un'idea aperta non deve sparire dalla coda per una frase della sua descrizione."""
    for testo in ("**Gli ordini limite in attesa** nel libro: comprare dove si ammassano.",
                  "**Le monete non ancora quotate** su Binance: ci si aspetta un rialzo.",
                  "**Il rimbalzo**: comprare quando il prezzo si riprende dopo una cascata.",
                  "**X**: non si prova sul passato, solo con dati nuovi.",
                  "**Il mercato fermo**: quando il prezzo è fermo per giorni.",
                  "**Binance ha sospeso i prelievi**: un evento da provare."):
        assert registro.stato_della_voce(testo) == "aperta", testo


def test_la_marca_vale_piu_delle_parole_ma_non_della_barra():
    assert registro.stato_della_voce("**X**: non si fa per ora. [stato: in attesa]") == "in attesa"
    assert registro.stato_della_voce("**X**: si misura in avanti. **[stato: aperta]**") == "aperta"
    assert registro.stato_della_voce("**X** [stato: in avanti] poi chiusa [stato: non si fa]") == "non si fa"   # l'ultima
    assert registro.stato_della_voce("[stato: aperta] ~~X~~ → prova 12") == "barrata"
    assert registro.stato_della_voce("**X**: [stato: chissà]") == "aperta"            # una marca sconosciuta non conta


def test_il_titolo_e_la_riga(tmp_path):
    d = _dati(tmp_path)
    v = {v["n"]: v for v in d["idee"]}
    assert v[6]["titolo"] == "Il canale Telegram" and v[7]["titolo"] == "Le narrazioni"
    assert ESEMPIO.splitlines()[v[6]["riga"] - 1].startswith("6. ")
    assert d["idee_aperte"] == [(6, "Il canale Telegram")] and d["idee_chiuse"] == 5


def test_il_riepilogo_stampa_gli_stati_e_le_aperte(tmp_path):
    righe = registro.riepilogo(_dati(tmp_path))
    testo = "\n".join(righe)
    assert "9 voci, 2 barrate, 1 provata, 2 non si fa, 1 in avanti, 2 in attesa, 1 aperta" in testo
    assert "  provate ma non barrate: 3" in righe and "  non si fa: 2, 9" in righe and "  in attesa: 5, 7" in righe
    assert "idee aperte (1):" in righe and any(r.startswith("  6. Il canale Telegram (riga") for r in righe)
    assert len(righe) <= 20


def test_con_molte_aperte_resta_entro_20_righe(tmp_path):
    voci = "\n".join(f"{n}. **Idea {n}**: da scrivere." for n in range(1, 41))
    righe = registro.riepilogo(_dati(tmp_path, f"# R\n\n## 5. Idee in coda\n{voci}\n"))
    assert len(righe) == 20 and "40 aperte" in righe[1]
    assert righe[-1].startswith("  … e le altre: ") and righe[-1].endswith(", 40")


def test_senza_sezione_5_lo_dice(tmp_path):
    d = _dati(tmp_path, "# R\n\n1. **Una regola**\n")
    assert d["idee"] == [] and d["sezione_idee"] is None
    assert any("non trovata" in r for r in registro.riepilogo(d))


def test_registro_vero_le_idee_sono_solo_della_sezione_5():
    d = registro.leggi()
    regole = ("Prima di ogni idea nuova", "Ogni prova nuova")            # le regole 1 e 2 in testa al registro (righe 9 e 13)
    assert not [t for _, t in d["idee_aperte"] if t in regole]
    assert d["sezione_idee"] and d["idee"]
    assert all(v["riga"] > d["sezione_idee"] for v in d["idee"])
    assert not [v for v in d["idee"] if v["titolo"] in regole]
    assert sum(d["stati"].values()) == len(d["idee"]) and set(d["stati"]) <= set(registro.STATI)
    assert len(registro.riepilogo(d)) <= 20


def test_cerca_trova_anche_le_idee_della_coda(tmp_path, capsys, monkeypatch):
    """Dal 27 novembre 2026 --cerca legge anche la sezione 5: tre scout su tre non vedevano le idee già in coda."""
    from research.src import registro
    f = tmp_path / "REGISTRO.md"
    f.write_text("| 1 | X1: **una prova sul funding** | — | no |\n\n## 5. Idee in coda\n\n"
                 "7. **Il contrario dei trader con più leva di Hyperliquid**: da provare.\n"
                 "8. ~~**Una idea chiusa**~~ → prova 1.\n", encoding="utf-8")
    monkeypatch.setattr(registro, "REGISTRO", f)
    registro.main(["--cerca", "hyperliquid"])
    out = capsys.readouterr().out
    assert "(trovate 0)" in out and "idea 7 (aperta" in out and "(idee trovate 1)" in out
