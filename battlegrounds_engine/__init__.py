"""Deterministic engine for a four-player tavern auto-battler."""

from .combat import CombatEngine, CombatResult
from .models import Keyword, Minion, PlayerState, TavernTier
from .recruit import RecruitService

__all__ = [
    "CombatEngine",
    "CombatResult",
    "Keyword",
    "Minion",
    "PlayerState",
    "RecruitService",
    "TavernTier",
]

__version__ = "0.1.0"
