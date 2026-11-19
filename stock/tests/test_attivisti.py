"""Le parti senza rete della prova 42: le righe dell'indice della SEC, l'intestazione di un deposito, il simbolo di allora."""
from datetime import date

from stock.dati import attivisti as a

INDICE = """Form Type   Company Name                                                  CIK         Date Filed  File Name
---------------------------------------------------------------------------------------------------------------------------------
SC 13D      ACME CORP                                                     1234567     2019-01-15  edgar/data/1234567/0000950142-19-000123.txt
SC 13D      STARBOARD VALUE LP                                            1517137     2019-01-15  edgar/data/1517137/0000950142-19-000123.txt
SC 13D/A    ACME CORP                                                     1234567     2019-02-01  edgar/data/1234567/0000950142-19-000999.txt
SC 13G      ACME CORP                                                     1234567     2019-02-02  edgar/data/1234567/0000950142-19-000555.txt
"""

PAGINA = """<html><head><title>0000950142-19-000123-index-headers.html</title></head><body><pre>
&lt;SEC-HEADER&gt;0000950142-19-000123.hdr.sgml : 20190115
&lt;ACCEPTANCE-DATETIME&gt;20190115163012
ACCESSION NUMBER:\t\t0000950142-19-000123
CONFORMED SUBMISSION TYPE:\tSC 13D
PUBLIC DOCUMENT COUNT:\t\t2
FILED AS OF DATE:\t\t20190115
GROUP MEMBERS:\t\tJEFFREY SMITH

SUBJECT COMPANY:\t

\tCOMPANY DATA:\t
\t\tCOMPANY CONFORMED NAME:\t\t\tACME CORP &amp; SONS
\t\tCENTRAL INDEX KEY:\t\t\t0001234567
\t\tSTANDARD INDUSTRIAL CLASSIFICATION:\t[3510]

FILED BY:\t\t

\tCOMPANY DATA:\t
\t\tCOMPANY CONFORMED NAME:\t\t\tSTARBOARD VALUE LP
\t\tCENTRAL INDEX KEY:\t\t\t0001517137
&lt;/SEC-HEADER&gt;
</pre></body></html>"""


def test_righe_dell_indice_solo_i_primi_13d_con_il_numero():
    r = a.righe_13d(INDICE)
    assert [x["cik"] for x in r] == [1234567, 1517137]                     # niente «/A», niente 13G; due righe, lo stesso deposito
    assert {x["numero"] for x in r} == {"0000950142-19-000123"} and r[0]["giorno"] == "2019-01-15" and r[0]["nome"] == "ACME CORP"


def test_intestazione_ora_oggetto_e_chi_deposita():
    d = a.leggi_intestazione(PAGINA)
    assert d["accettazione"] == "20190115163012" and d["tipo"] == "SC 13D"
    assert d["oggetto"] == 1234567 and d["nome_oggetto"] == "ACME CORP & SONS"
    assert d["chi"] == 1517137 and d["nome_chi"] == "STARBOARD VALUE LP"
    assert a.leggi_intestazione("<html>niente</html>")["accettazione"] is None


def test_simbolo_del_periodo_iniziato_per_ultimo_entro_un_anno():
    p = [(date(2016, 1, 10), date(2018, 6, 1), "FB"), (date(2022, 6, 9), date(2024, 12, 2), "META")]
    assert a.simbolo_al(p, date(2017, 3, 1)) == "FB"                       # dentro il periodo
    assert a.simbolo_al(p, date(2019, 3, 1)) == "FB"                       # finito da meno di un anno
    assert a.simbolo_al(p, date(2020, 3, 1)) is None                       # finito da più di un anno
    assert a.simbolo_al(p, date(2022, 6, 9)) is None                       # il periodo nuovo inizia lo stesso giorno: non ancora
    assert a.simbolo_al(p, date(2022, 6, 10)) == "META"
    assert a.simbolo_al([], date(2020, 1, 1)) is None
