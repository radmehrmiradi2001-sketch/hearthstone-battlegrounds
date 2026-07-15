from __future__ import annotations

from dataclasses import dataclass, field, replace
from enum import Enum, IntEnum
from uuid import uuid4


class Keyword(str, Enum):
    TAUNT = "taunt"
    DIVINE_SHIELD = "divine_shield"
    REBORN = "reborn"
    WINDFURY = "windfury"


class TavernTier(IntEnum):
    ONE = 1
    TWO = 2
    THREE = 3
    FOUR = 4


@dataclass(slots=True)
class Minion:
    card_id: str
    name: str
    attack: int
    health: int
    tavern_tier: TavernTier = TavernTier.ONE
    keywords: set[Keyword] = field(default_factory=set)
    instance_id: str = field(default_factory=lambda: str(uuid4()))
    golden: bool = False

    def __post_init__(self) -> None:
        if self.attack < 0 or self.health < 1:
            raise ValueError("A minion requires non-negative attack and positive health")

    @property
    def alive(self) -> bool:
        return self.health > 0

    def clone_for_combat(self) -> Minion:
        return replace(self, keywords=set(self.keywords), instance_id=str(uuid4()))


@dataclass(slots=True)
class PlayerState:
    player_id: str
    display_name: str
    hero_name: str
    health: int = 40
    gold: int = 3
    turn: int = 1
    tavern_tier: TavernTier = TavernTier.ONE
    tavern_upgrade_cost: int = 5
    board: list[Minion] = field(default_factory=list)
    hand: list[Minion] = field(default_factory=list)
    shop: list[Minion] = field(default_factory=list)
    shop_frozen: bool = False
    eliminated: bool = False

    def validate(self) -> None:
        if len(self.board) > 7:
            raise ValueError("The board cannot contain more than seven minions")
        if len(self.hand) > 10:
            raise ValueError("The hand cannot contain more than ten cards")
        if not 0 <= self.gold <= 10:
            raise ValueError("Gold must be between zero and ten")

    def begin_turn(self) -> None:
        self.turn += 1
        self.gold = min(10, self.turn + 2)
        self.tavern_upgrade_cost = max(self.minimum_upgrade_cost, self.tavern_upgrade_cost - 1)

    @property
    def minimum_upgrade_cost(self) -> int:
        return {TavernTier.ONE: 2, TavernTier.TWO: 4, TavernTier.THREE: 5}.get(
            self.tavern_tier, 0
        )
