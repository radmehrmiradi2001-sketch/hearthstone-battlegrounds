from battlegrounds_engine.combat import CombatEngine
from battlegrounds_engine.models import Keyword, Minion, PlayerState


def player(player_id: str, minions: list[Minion]) -> PlayerState:
    return PlayerState(player_id, player_id, "Hero", board=minions)


def test_stronger_board_wins_and_deals_damage() -> None:
    winner = player("winner", [Minion("strong", "Strong", 10, 10)])
    loser = player("loser", [Minion("weak", "Weak", 1, 1)])
    result = CombatEngine().resolve(winner, loser, seed=7)
    assert result.winner_id == "winner"
    assert result.hero_damage == 2


def test_taunt_is_targeted_first() -> None:
    attacker = player("attacker", [
        Minion("a", "Attacker", 10, 10),
        Minion("a2", "Support One", 1, 2),
        Minion("a3", "Support Two", 1, 2),
    ])
    defender = player("defender", [
        Minion("safe", "Safe", 1, 1),
        Minion("taunt", "Taunt", 1, 1, keywords={Keyword.TAUNT}),
    ])
    result = CombatEngine().resolve(attacker, defender, seed=3)
    first_attack = next(event for event in result.events if event.kind == "attack")
    assert "Taunt" in first_attack.message


def test_same_seed_produces_same_event_sequence() -> None:
    def run() -> list[str]:
        left = player("left", [Minion("l1", "L1", 3, 3), Minion("l2", "L2", 2, 2)])
        right = player("right", [Minion("r1", "R1", 3, 3), Minion("r2", "R2", 2, 2)])
        return [event.message for event in CombatEngine().resolve(left, right, seed=99).events]

    assert run() == run()
