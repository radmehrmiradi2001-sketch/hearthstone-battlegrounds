from __future__ import annotations

from dataclasses import replace

from .models import Minion, PlayerState, TavernTier


class RuleViolation(ValueError):
    """Raised when a player command violates a recruit-phase rule."""


class RecruitService:
    """Apply validated recruit-phase commands to a player state."""

    MINION_COST = 3
    REFRESH_COST = 1
    SELL_VALUE = 1
    UPGRADE_BASE_COST = {
        TavernTier.ONE: 7,
        TavernTier.TWO: 8,
        TavernTier.THREE: 9,
    }

    def buy_minion(self, player: PlayerState, shop_index: int) -> Minion:
        self._require_index(player.shop, shop_index, "shop")
        if player.gold < self.MINION_COST:
            raise RuleViolation("Not enough gold to buy this minion")
        if len(player.hand) >= 10:
            raise RuleViolation("The hand is full")
        player.gold -= self.MINION_COST
        minion = player.shop.pop(shop_index)
        player.hand.append(minion)
        self._resolve_triple(player, minion.card_id)
        return minion

    def play_minion(self, player: PlayerState, hand_index: int, board_index: int | None = None) -> Minion:
        self._require_index(player.hand, hand_index, "hand")
        if len(player.board) >= 7:
            raise RuleViolation("The board is full")
        minion = player.hand.pop(hand_index)
        destination = len(player.board) if board_index is None else board_index
        if not 0 <= destination <= len(player.board):
            raise RuleViolation("Invalid board position")
        player.board.insert(destination, minion)
        return minion

    def sell_minion(self, player: PlayerState, board_index: int) -> Minion:
        self._require_index(player.board, board_index, "board")
        minion = player.board.pop(board_index)
        player.gold = min(10, player.gold + self.SELL_VALUE)
        return minion

    def freeze_shop(self, player: PlayerState, frozen: bool = True) -> None:
        player.shop_frozen = frozen

    def refresh_shop(self, player: PlayerState, replacements: list[Minion]) -> None:
        if player.gold < self.REFRESH_COST:
            raise RuleViolation("Not enough gold to refresh the shop")
        player.gold -= self.REFRESH_COST
        if not player.shop_frozen:
            player.shop = list(replacements)
        player.shop_frozen = False

    def upgrade_tavern(self, player: PlayerState) -> None:
        if player.tavern_tier is TavernTier.FOUR:
            raise RuleViolation("The tavern is already at maximum tier")
        if player.gold < player.tavern_upgrade_cost:
            raise RuleViolation("Not enough gold to upgrade the tavern")
        player.gold -= player.tavern_upgrade_cost
        player.tavern_tier = TavernTier(player.tavern_tier + 1)
        player.tavern_upgrade_cost = self.UPGRADE_BASE_COST.get(player.tavern_tier, 0)

    @staticmethod
    def _require_index(items: list[Minion], index: int, collection_name: str) -> None:
        if not 0 <= index < len(items):
            raise RuleViolation(f"Invalid {collection_name} position: {index}")

    @staticmethod
    def _resolve_triple(player: PlayerState, card_id: str) -> None:
        copies = [minion for minion in [*player.hand, *player.board] if minion.card_id == card_id]
        if len(copies) < 3:
            return
        selected = copies[:3]
        for minion in selected:
            collection = player.hand if minion in player.hand else player.board
            collection.remove(minion)
        base = selected[0]
        golden = replace(
            base,
            name=f"Golden {base.name}",
            attack=base.attack * 2,
            health=base.health * 2,
            golden=True,
        )
        player.hand.append(golden)
