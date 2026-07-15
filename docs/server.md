# Server Architecture

The server is authoritative for lobby state, recruit commands, combat pairing, combat seeds, hero damage, and player elimination. Clients submit commands and render validated state updates; they never decide gameplay outcomes.

## Session lifecycle

1. A client opens a connection and sends `join_lobby`.
2. The server assigns a stable `player_id` and broadcasts `lobby_state`.
3. Four players select heroes and mark themselves ready.
4. The server starts the recruit phase and sends a complete `recruit_state` snapshot.
5. Valid commands produce ordered `state_delta` messages.
6. When all players end their turns or the timer expires, the server creates two combat pairings.
7. Each pairing receives an independent `combat_start` message with a deterministic seed.
8. After both battles finish, the server broadcasts one comprehensive `leaderboard_update`.
9. The cycle repeats until one player remains.

## Transport contract

Messages use UTF-8 JSON with a required envelope:

```json
{
  "type": "state_delta",
  "message_id": "msg-000042",
  "session_id": "session-001",
  "sequence": 42,
  "payload": {}
}
```

`sequence` must increase monotonically per session. Clients reject duplicates and request a fresh snapshot after a gap.

## Command validation

Every command is checked against the authoritative state:

- player identity and active phase;
- command idempotency key;
- gold, hand, board, and shop constraints;
- valid source and destination positions;
- hero-power cost and per-turn limits;
- current offer identifiers for Discover and Choose One.

Invalid commands return an `error` message without mutating state.

## Deterministic combat

Combat uses a server-provided seed and stable board snapshots. All random choices must originate from one seeded generator. The event log records the seed, ordered events, final survivors, and hero damage so a replay can reproduce the result exactly.

## Reliability and security

- Use heartbeat messages and close stale sessions.
- Apply command rate limits per player.
- Cap message size and reject unknown fields at the boundary.
- Never trust client-provided gold, health, cards, or combat results.
- Persist snapshots at phase boundaries and append combat events to an immutable log.
- Avoid including secrets or internal exception traces in client errors.

## Suggested modules

```text
server/
  app.py               # process lifecycle and connection setup
  lobby.py             # matchmaking and readiness
  session.py           # ordered message processing
  recruit_service.py   # authoritative recruit commands
  round_coordinator.py # pairings and phase transitions
  protocol.py          # schemas and serialization
  persistence.py       # snapshots and replay records
```
