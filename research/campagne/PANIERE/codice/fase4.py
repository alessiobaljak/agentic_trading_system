"""Fase 4 delle regole del gruppo (sezione 6, punto 2) per i candidati, sui trade sommati di costruzione.

Per ogni candidato, in serie, ogni verifica registrata PRIMA (voce «registrazione», tipo_test «verifica», verifica_di)
e il risultato dopo (il dizionario di gruppo.esame_di_gruppo copiato così com'è):
* costi doppi (moltiplicatore_costi 2), ritardo di una barra (ritardo_barre 1), regola intra-barra opposta
  (riempimento_intrabarra «target_prima»: senza target non dovrebbe cambiare nulla, si dichiara);
* robustezza: ogni parametro numerico a round(0,8 x) e round(1,2 x) (interi con le metà verso l'alto; se resta uguale,
  -1 e +1), uno alla volta; ogni caso contato prima con conta_trade_di_gruppo: sotto 700 o oltre il tetto del 10% si
  dichiara e non si esamina.
Riprende da solo: una verifica con il risultato nel log si salta, una registrata senza risultato si esamina.
Uso: fase4.py <id del candidato> [...]
"""

import copy
import json
import math
import sys
from pathlib import Path

RADICE = Path(__file__).resolve().parents[4]
CODICE = Path(__file__).resolve().parent
sys.path.insert(0, str(RADICE))
sys.path.insert(0, str(CODICE))

from research.src import gruppo  # noqa: E402
import registro  # noqa: E402

INTERI = {"monete_in_ritardo", "giorni_deviazione", "giorni_minimi_deviazione", "barre_uscita", "barre_atr",
          "barre_massime"}
NUMERICI = ["k", "monete_in_ritardo", "giorni_deviazione", "giorni_minimi_deviazione", "barre_uscita",
            "multiplo_atr", "barre_atr", "barre_massime"]


def arrotonda(x):
    return int(math.floor(x + 0.5))


def spostamenti(nome, valore):
    if nome in INTERI:
        giu, su = arrotonda(0.8 * valore), arrotonda(1.2 * valore)
        if giu == valore:
            giu = valore - 1
        if su == valore:
            su = valore + 1
        return [giu, su]
    return [round(0.8 * valore, 10), round(1.2 * valore, 10)]


def registrazione_di(id_candidato):
    for v in registro.voci():
        if v["id"] == id_candidato and v["tipo"] == "registrazione":
            return v
    raise KeyError(id_candidato)


def gia_fatta(nome_verifica):
    voci = registro.voci()
    reg = [v for v in voci if v["tipo"] == "registrazione" and v.get("nome_verifica") == nome_verifica]
    if not reg:
        return None, False
    id_v = reg[-1]["id"]
    fatto = reg[-1].get("non_conta") or any(v["id"] == id_v and v["tipo"] == "risultato" for v in voci)
    return id_v, bool(fatto)


def esegui(id_candidato, reg, nome_verifica, p, opzioni, previsione, criterio, conta_prima):
    id_v, fatto = gia_fatta(nome_verifica)
    if fatto:
        print(nome_verifica, "già fatta", id_v)
        return
    modulo = CODICE / Path(reg["modulo"]).name
    if id_v is None:
        campi = {"tipo": "registrazione", "tipo_test": "verifica", "verifica_di": id_candidato,
                 "nome_verifica": nome_verifica, "timeframe": "1d", "direzione": p["direzione"], "parametri": p,
                 "opzioni": opzioni, "periodo": "costruzione", "previsione": previsione,
                 "criterio_successo": criterio, "modulo": reg["modulo"]}
        if conta_prima:
            conta = gruppo.conta_trade_di_gruppo(modulo, p, "1d")
            campi.update({"trade_stimati": conta["trade_stimati"], "monete_con_trade": conta["monete_con_trade"],
                          "quota_moneta_piu_presente": conta["quota_moneta_piu_presente"]})
            if conta["esito"] == "scarto":
                campi.update({"non_conta": True, "motivi": conta["motivi"],
                              "testo": "caso della robustezza fuori dai minimi: si dichiara e non conta"})
                voce = registro.aggiungi(campi)
                print(nome_verifica, "non conta", voce["id"], conta["motivi"])
                return
        else:
            campi["trade_stimati"] = reg["trade_stimati"]
        id_v = registro.prossimo_id()
        registro.aggiungi(campi, id_voce=id_v)
    esame = gruppo.esame_di_gruppo(modulo, p, "1d", "costruzione", id_v, **opzioni)
    registro.aggiungi(dict({"tipo": "risultato", "verifica_di": id_candidato, "nome_verifica": nome_verifica}, **esame),
                      id_voce=id_v)
    print(nome_verifica, "risultato", id_v, "t contro (b)", esame.get("baseline_b", {}).get("t"),
          "netta", esame.get("baseline_b", {}).get("netta"), "R", esame.get("metriche", {}).get("r_medio"))


def main():
    for id_candidato in sys.argv[1:]:
        reg = registrazione_di(id_candidato)
        p = reg["parametri"]
        esegui(id_candidato, reg, f"{id_candidato} costi doppi", p, {"moltiplicatore_costi": 2.0},
               "R medio scende di circa 0,01 (il costo di un giro è circa 0,007 R); t contro la (b) a costi doppi di "
               "poco sotto quello a costi normali; netta con probabilità 80%",
               "batte nettamente la (b) ricalcolata a costi doppi e R medio a costi doppi > 0", False)
        esegui(id_candidato, reg, f"{id_candidato} ritardo di una barra", p, {"ritardo_barre": 1},
               "t contro la (b) col ritardo fra -0,5 e 2,5: il recupero comincia dal giorno d'ingresso (Fase 3: +0,08 R "
               "alla prima chiusura), quindi può scendere molto; resta sopra la metà con probabilità 45%",
               "t contro la (b) ricalcolata col ritardo positivo e almeno la metà di quello senza ritardo", False)
        esegui(id_candidato, reg, f"{id_candidato} regola intra-barra opposta", p,
               {"riempimento_intrabarra": "target_prima"},
               "nessuna differenza: le varianti non hanno target",
               "si dichiara la differenza", False)
        for nome in NUMERICI:
            if nome not in p:
                continue
            for nuovo in spostamenti(nome, p[nome]):
                q = copy.deepcopy(p)
                q[nome] = nuovo
                if q["giorni_minimi_deviazione"] > q["giorni_deviazione"]:
                    q["giorni_minimi_deviazione"] = q["giorni_deviazione"]
                esegui(id_candidato, reg, f"{id_candidato} robustezza {nome} {nuovo}", q, {},
                       "t contro la (b) positivo; netta in circa metà dei casi; i casi di barre_massime non toccano "
                       "nulla (l'uscita a 3 barre arriva prima) e reggono per costruzione",
                       "nei casi che contano t contro la (b) ricalcolata positivo, e netta in almeno metà", True)
    print("fatto")


if __name__ == "__main__":
    main()
