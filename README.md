# Battlegrounds Simulator

A deterministic, four-player tavern auto-battler foundation built for reliable gameplay experiments, replayable combat, and clean client/server integration.

> This is an independent educational project inspired by the auto-battler genre. Existing reference artwork and design notes remain available for classroom use.

## What is implemented

- Typed domain models for players, minions, tavern tiers, and combat keywords
- Recruit-phase commands for buying, playing, selling, freezing, refreshing, and upgrading
- Board, hand, gold, and position validation with clear rule errors
- Automatic triple detection and Golden minion creation
- Seeded, deterministic combat with alternating attacks
- Taunt targeting, Divine Shield, simultaneous damage, death events, ties, and hero damage
- Structured combat events suitable for replay timelines or network transport
- Runnable demonstration CLI and automated tests

The original design specification, mock payload notes, team template, and artwork are preserved in `docs/`, `data/`, `teams/`, and `bgknowhow-main/`.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"

battlegrounds-sim --seed 42
pytest
ruff check .
```

For JSON output that can feed a UI or replay viewer:

```bash
battlegrounds-sim --seed 42 --json
```

## Architecture

```text
battlegrounds_engine/
  models.py       # Validated domain entities and terminology
  recruit.py      # Recruit-phase command rules
  combat.py       # Deterministic combat resolution and events
  cli.py          # Runnable simulation demo
tests/            # Recruit and combat regression tests
data/             # Existing payload contracts and fixtures
docs/             # Existing product and interface specifications
```

The engine deliberately contains no rendering or socket code. A Pygame, web, or network client can consume the same `PlayerState` and `CombatEvent` contracts without coupling gameplay rules to presentation.

## Core terminology

Names follow game-domain intent instead of UI implementation details:

- `PlayerState` — authoritative state for one lobby participant
- `RecruitService` — validated recruit-phase command handler
- `CombatEngine` — deterministic battle resolver
- `CombatEvent` — immutable replay or transport record
- `RuleViolation` — expected invalid player command
- `instance_id` — unique board entity; `card_id` identifies the card definition

## Roadmap

1. Load card definitions from versioned JSON schemas.
2. Add Battlecry, Deathrattle, Reborn, summon queues, and hero powers.
3. Introduce a four-player round coordinator with ghost snapshots.
4. Connect the existing mock payload contracts to a WebSocket gateway.
5. Build a replay viewer before adding a full interactive client.

## Contributing

Create a feature branch and submit changes through a pull request. Keep rule changes covered by deterministic tests, and never mix gameplay decisions into rendering components.

The full client gameplay specification is available at [docs/frontend_playbook.md](docs/frontend_playbook.md).
