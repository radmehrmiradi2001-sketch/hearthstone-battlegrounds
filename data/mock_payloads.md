# Protocol Payload Reference

These examples define the client/server boundary. Identifiers are opaque strings, positions are zero-based, and all state-changing commands require an idempotency key.

## Recruit state

```json
{
  "type": "recruit_state",
  "message_id": "msg-001",
  "sequence": 1,
  "payload": {
    "turn": 1,
    "player": {
      "player_id": "player-1",
      "health": 40,
      "gold": 3,
      "tavern_tier": 1,
      "tavern_upgrade_cost": 5,
      "shop_frozen": false,
      "hand": [],
      "board": []
    },
    "shop": []
  }
}
```

## Buy command

```json
{
  "type": "command",
  "payload": {
    "action": "buy_minion",
    "shop_position": 1,
    "idempotency_key": "command-001"
  }
}
```

## State delta

```json
{
  "type": "state_delta",
  "message_id": "msg-002",
  "sequence": 2,
  "payload": {
    "gold": 0,
    "shop_remove": {"position": 1},
    "hand_add": {"position": 0, "instance_id": "minion-101", "card_id": "CARD_001"}
  }
}
```

## Combat start

```json
{
  "type": "combat_start",
  "message_id": "msg-030",
  "sequence": 30,
  "payload": {
    "combat_id": "combat-008",
    "seed": 8675309,
    "first_player_id": "player-1",
    "second_player_id": "player-3",
    "first_board": [],
    "second_board": []
  }
}
```

## Combat event

```json
{
  "type": "combat_event",
  "message_id": "msg-031",
  "sequence": 31,
  "payload": {
    "combat_id": "combat-008",
    "step": 1,
    "kind": "attack",
    "source_instance_id": "minion-101",
    "target_instance_id": "minion-204",
    "message": "Tavern Guardian attacks Clockwork Scout"
  }
}
```

## Combat result

```json
{
  "type": "combat_result",
  "message_id": "msg-050",
  "sequence": 50,
  "payload": {
    "combat_id": "combat-008",
    "winner_id": "player-1",
    "loser_id": "player-3",
    "hero_damage": 5,
    "rounds": 9
  }
}
```

## Leaderboard update

```json
{
  "type": "leaderboard_update",
  "payload": {
    "players": [
      {"player_id": "player-1", "health": 40, "tavern_tier": 2, "eliminated": false},
      {"player_id": "player-2", "health": 33, "tavern_tier": 2, "eliminated": false},
      {"player_id": "player-3", "health": 28, "tavern_tier": 1, "eliminated": false},
      {"player_id": "player-4", "health": 0, "tavern_tier": 3, "eliminated": true}
    ]
  }
}
```

## Choice offer

```json
{
  "type": "discover_offer",
  "payload": {
    "offer_id": "offer-009",
    "options": [
      {"choice_id": "choice-a", "card_id": "CARD_A"},
      {"choice_id": "choice-b", "card_id": "CARD_B"},
      {"choice_id": "choice-c", "card_id": "CARD_C"}
    ]
  }
}
```

## Error

```json
{
  "type": "error",
  "payload": {
    "code": "INSUFFICIENT_GOLD",
    "message": "Not enough gold to complete this command.",
    "command_id": "command-001",
    "recoverable": true
  }
}
```

Clients must ignore unknown optional fields, reject missing required fields, and request a full snapshot when sequence continuity is lost.
