"""La regola del proprietario dell'8 novembre 2026: nessuna strategia del paper o del demo si spegne o si perde.

«Non voglio che nessuna delle strategie ora in paper o in demo vada persa, devono rimanere tutte in corso: queste sono le uniche su
cui stiamo testando live e che potrebbero andare con soldi veri.» Questo test fallisce se si toglie l'interruttore di una di loro o
se il bot smette di crearla o di farla girare. Spegnerne una si fa solo con l'ok del proprietario, cambiando anche questo test.
"""
from pathlib import Path

from bot.portafoglio.demo_binance import INTERRUTTORE as DEMO
from bot.portafoglio.eventi import INTERRUTTORE as EVENTI
from bot.portafoglio.f5 import PaperF5, PaperG1, PaperG11, PaperG1N

RADICE = Path(__file__).resolve().parents[1]

# strategia -> (interruttore in ops/, attributo del bot)
IN_CORSO = {
    "G1 sul conto demo di Binance": ("demo_binance_acceso", "demo_g1"),
    "G1 nel paper": ("paper_g1_acceso", "paper_g1"),
    "G1 neutra al mercato (paper)": ("paper_g1n_acceso", "paper_g1n"),
    "G11 (paper)": ("paper_g11_acceso", "paper_g11"),
    "F5, il lunedi' (paper)": ("paper_f5_acceso", "paper_f5"),
    "Eventi (paper)": ("paper_eventi_acceso", "paper_eventi"),
}


def test_gli_interruttori_ci_sono_tutti():
    mancanti = [nome for nome, (file, _) in IN_CORSO.items() if not (RADICE / "ops" / file).is_file()]
    assert not mancanti, f"strategie spente (manca l'interruttore in ops/): {mancanti}"


def test_ogni_strategia_legge_il_suo_interruttore():
    letti = {p.name for p in (DEMO, EVENTI, PaperF5.INTERRUTTORE_DI_SERIE, PaperG1.INTERRUTTORE_DI_SERIE,
                              PaperG11.INTERRUTTORE_DI_SERIE, PaperG1N.INTERRUTTORE_DI_SERIE)}
    assert letti == {file for file, _ in IN_CORSO.values()}


def test_il_bot_le_crea_e_le_fa_girare_tutte():
    testo = (RADICE / "bot" / "main.py").read_text(encoding="utf-8")
    for nome, (_, attributo) in IN_CORSO.items():
        assert f"self.{attributo} = " in testo, f"{nome}: il bot non la crea piu'"
        assert f"self.{attributo}.tick(" in testo, f"{nome}: il bot non la fa piu' girare"
