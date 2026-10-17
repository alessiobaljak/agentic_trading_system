"""
Layer — MOTORE DI APPRENDIMENTO E ADATTAMENTO (il cuore del sistema).

  * trade_logger : registra ogni trade chiuso con TUTTO il contesto.
  * metrics      : calcola metriche di performance segmentate + pesi dinamici.
  * learning_loop: job notturno che produce il memory_report e i pesi.
  * adaptation   : applica i pesi alle decisioni (con baseline anti-overfitting).
"""
from bot.learning.adaptation import AdaptationEngine
from bot.learning.trade_logger import TradeLogger

__all__ = ["AdaptationEngine", "TradeLogger"]
