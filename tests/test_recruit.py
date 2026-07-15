import pytest

from battlegrounds_engine.models import Minion, PlayerState
from battlegrounds_engine.recruit import RecruitService, RuleViolation


def minion(card_id: str = "card-1") -> Minion:
    return Minion(card_id, "Test Minion", 2, 2)


def test_buy_moves_minion_and_spends_gold() -> None:
    player = PlayerState("p1", "Player", "Hero", shop=[minion()])
    RecruitService().buy_minion(player, 0)
    assert player.gold == 0
    assert len(player.hand) == 1
    assert player.shop == []


def test_buy_rejects_insufficient_gold() -> None:
    player = PlayerState("p1", "Player", "Hero", gold=2, shop=[minion()])
    with pytest.raises(RuleViolation, match="Not enough gold"):
        RecruitService().buy_minion(player, 0)


def test_three_copies_create_a_golden_minion() -> None:
    player = PlayerState("p1", "Player", "Hero", gold=3,
                         hand=[minion("same"), minion("same")], shop=[minion("same")])
    RecruitService().buy_minion(player, 0)
    assert len(player.hand) == 1
    assert player.hand[0].golden
    assert (player.hand[0].attack, player.hand[0].health) == (4, 4)
