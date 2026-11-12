"""Audit G1 (12 nov 2026): riesegue `revisione_g1n/parita_bot.main` con il codice del bot di oggi, scrivendo in audits/repro/."""
from pathlib import Path
from research.programma7.revisione_g1n import parita_bot as pb
pb.QUI = Path(__file__).parent / "parita_g1_2026-11-12"
pb.main()
