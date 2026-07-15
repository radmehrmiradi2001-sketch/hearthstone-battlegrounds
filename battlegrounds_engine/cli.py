from __future__ import annotations

import argparse
import json

from .combat import CombatEngine
from .models import Keyword, Minion, PlayerState, TavernTier


def demo_player(player_id: str, name: str, hero: str, offset: int) -> PlayerState:
    return PlayerState(
        player_id=player_id,
        display_name=name,
        hero_name=hero,
        tavern_tier=TavernTier.TWO,
        board=[
            Minion(f"demo-{offset}-guard", "Tavern Guardian", 3 + offset, 5,
                   TavernTier.TWO, {Keyword.TAUNT}),
            Minion(f"demo-{offset}-scout", "Clockwork Scout", 4, 3 + offset),
            Minion(f"demo-{offset}-warden", "Shielded Warden", 2, 4,
                   keywords={Keyword.DIVINE_SHIELD}),
        ],
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a deterministic auto-battler demo.")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--json", action="store_true", help="Print machine-readable output.")
    args = parser.parse_args()
    first = demo_player("player-1", "Ranger", "Sylvanas", 0)
    second = demo_player("player-2", "King", "The Lich King", 1)
    result = CombatEngine().resolve(first, second, args.seed)
    payload = {
        "winner_id": result.winner_id,
        "loser_id": result.loser_id,
        "hero_damage": result.hero_damage,
        "rounds": result.rounds,
        "events": [event.message for event in result.events],
    }
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print(f"Winner: {result.winner_id or 'tie'} | Damage: {result.hero_damage} | "
              f"Rounds: {result.rounds}")
        for event in result.events:
            print(f"[{event.step:02}] {event.message}")


if __name__ == "__main__":
    main()
