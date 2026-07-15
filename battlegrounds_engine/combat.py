from __future__ import annotations

from dataclasses import dataclass

import random

from .models import Keyword, Minion, PlayerState


@dataclass(frozen=True, slots=True)
class CombatEvent:
    step: int
    kind: str
    source_player_id: str
    source_instance_id: str | None
    target_instance_id: str | None
    message: str


@dataclass(frozen=True, slots=True)
class CombatResult:
    winner_id: str | None
    loser_id: str | None
    hero_damage: int
    rounds: int
    events: tuple[CombatEvent, ...]

    @property
    def tied(self) -> bool:
        return self.winner_id is None


class CombatEngine:
    """Resolve one battle deterministically from a supplied seed."""

    def resolve(self, first: PlayerState, second: PlayerState, seed: int) -> CombatResult:
        rng = random.Random(seed)
        boards = {
            first.player_id: [minion.clone_for_combat() for minion in first.board],
            second.player_id: [minion.clone_for_combat() for minion in second.board],
        }
        players = {first.player_id: first, second.player_id: second}
        order = self._starting_order(first, second, rng)
        next_attacker = {first.player_id: 0, second.player_id: 0}
        events: list[CombatEvent] = []
        rounds = 0

        while all(self._living(board) for board in boards.values()):
            attacker_id = order[rounds % 2]
            defender_id = order[(rounds + 1) % 2]
            if not self._living(boards[attacker_id]):
                attacker_id, defender_id = defender_id, attacker_id
            attacker = self._next_attacker(boards[attacker_id], next_attacker, attacker_id)
            target = self._choose_target(boards[defender_id], rng)
            self._deal_damage(attacker, target)
            events.append(CombatEvent(
                step=len(events) + 1,
                kind="attack",
                source_player_id=attacker_id,
                source_instance_id=attacker.instance_id,
                target_instance_id=target.instance_id,
                message=f"{attacker.name} attacks {target.name}",
            ))
            self._remove_dead(boards[attacker_id], attacker_id, events)
            self._remove_dead(boards[defender_id], defender_id, events)
            rounds += 1
            if rounds > 500:
                raise RuntimeError("Combat exceeded its safety limit")

        survivors = {player_id: self._living(board) for player_id, board in boards.items()}
        living_ids = [player_id for player_id, board in survivors.items() if board]
        if len(living_ids) != 1:
            return CombatResult(None, None, 0, rounds, tuple(events))
        winner_id = living_ids[0]
        loser_id = second.player_id if winner_id == first.player_id else first.player_id
        damage = int(players[winner_id].tavern_tier) + sum(
            int(minion.tavern_tier) for minion in survivors[winner_id]
        )
        return CombatResult(winner_id, loser_id, damage, rounds, tuple(events))

    @staticmethod
    def _starting_order(first: PlayerState, second: PlayerState, rng: random.Random) -> list[str]:
        if len(first.board) > len(second.board):
            return [first.player_id, second.player_id]
        if len(second.board) > len(first.board):
            return [second.player_id, first.player_id]
        return ([first.player_id, second.player_id] if rng.randrange(2) == 0
                else [second.player_id, first.player_id])

    @staticmethod
    def _living(board: list[Minion]) -> list[Minion]:
        return [minion for minion in board if minion.alive]

    def _next_attacker(
        self, board: list[Minion], cursors: dict[str, int], player_id: str
    ) -> Minion:
        living = self._living(board)
        cursor = cursors[player_id] % len(living)
        cursors[player_id] += 1
        return living[cursor]

    def _choose_target(self, board: list[Minion], rng: random.Random) -> Minion:
        living = self._living(board)
        taunts = [minion for minion in living if Keyword.TAUNT in minion.keywords]
        return rng.choice(taunts or living)

    @staticmethod
    def _deal_damage(attacker: Minion, defender: Minion) -> None:
        attacker_damage, defender_damage = attacker.attack, defender.attack
        if Keyword.DIVINE_SHIELD in defender.keywords and attacker_damage > 0:
            defender.keywords.remove(Keyword.DIVINE_SHIELD)
        else:
            defender.health -= attacker_damage
        if Keyword.DIVINE_SHIELD in attacker.keywords and defender_damage > 0:
            attacker.keywords.remove(Keyword.DIVINE_SHIELD)
        else:
            attacker.health -= defender_damage

    @staticmethod
    def _remove_dead(board: list[Minion], player_id: str, events: list[CombatEvent]) -> None:
        for minion in list(board):
            if minion.alive:
                continue
            board.remove(minion)
            events.append(CombatEvent(
                step=len(events) + 1,
                kind="minion_died",
                source_player_id=player_id,
                source_instance_id=minion.instance_id,
                target_instance_id=None,
                message=f"{minion.name} died",
            ))
